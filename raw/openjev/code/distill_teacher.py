#!/usr/bin/env python
"""Reasoning teacher -> one-pass student. A thinking Qwen writes typed decisions, solves each k times, and the vote
distribution becomes the student's soft label.

    V=~/venvs/sglang/bin/python        # --backend vllm with ~/venvs/vllm/bin/python also works
    $V distill_teacher.py write --model Qwen/Qwen3.5-9B --n 6000 --out data/distill/scenarios.jsonl
    $V distill_teacher.py solve --model Qwen/Qwen3.5-9B --tasks data/distill/scenarios.jsonl --k 6 --out data/distill/solved.jsonl
    python distill_teacher.py rows  --solved data/distill/solved.jsonl --out nli_distill/parts/distill.jsonl

write   Scenarios come from a family DESCRIPTION plus random seeds (domain, twist); no benchmark item is ever shown.
solve   k sampled chains per item. A chain that runs out of budget is not thrown away: `</think>\\nFINAL:` is appended
        and the model must commit from what it has reasoned so far (budget forcing). Works on any jsonl of typed
        decisions, so the public JevBench items double as the teacher's exam (`--tasks hard.jsonl`).
rows    One student row per (vote, option): entailment if that vote chose the option, contradiction otherwise. The
        expectation over votes is the teacher's distribution, so plain cross-entropy distils a SOFT label with no
        change to train.py. Items the teacher disagrees with itself on (top share < --min-agree) are dropped.
"""
import argparse
import collections
import json
import os
import random
import re

from think_probe import PROMPT, options, parse

FAMILIES = {
    "trap": "The surface reading of the state invites one answer (a confident claim by a customer or colleague, a familiar-looking case) but a defined term, a precedence rule or a small stated fact makes another answer correct.",
    "ambiguous": "Several answers look defensible until one reads which fact the stated rules actually make decisive; exactly one answer follows from the rules as written.",
    "routing_hard": "A request must be routed to one of several queues or specialists. The wording suggests one destination, but the routing rules in the state send it elsewhere (an exception, a priority order, a scope limit).",
    "judge_hard": "The state holds a request and a response to it. Decide whether the response fully and correctly satisfies the request, including method, units, formatting and every explicit constraint. Many responses are almost right.",
    "tradeoff": "A policy lists several possible actions with conditions and an order of precedence; the agent must pick the single action the policy requires now, not the one that feels most helpful.",
    "adversarial": "The state contains text that tries to steer the decision (an instruction embedded in a document, a threat, flattery, a false statement of policy). The correct answer follows the real rules and ignores the steering.",
    "multi_hop": "The answer needs three or four facts from different places in the state chained together (a lookup, an override, a conversion, a threshold). Skipping any one step gives a neighbouring answer.",
    "temporal_numeric": "The decision turns on dates, times and numbers stated in the state: deadlines counted in business days or calendar months, month-end rules, time zones, leap years, tiered fees or limits with boundary values. The tempting answer comes from a naive count; the correct one needs the exact rule applied to the exact numbers. State every date, time and rule explicitly.",
    "long_policy": "A long policy or contract excerpt (definitions, covered causes, exclusions, waiting periods, notification deadlines with exceptions, limits changed by a dated endorsement) followed by a case file. The right outcome needs two or three clauses combined, and a note in the file argues for a wrong outcome. Write the policy in numbered sections with plenty of ordinary clauses around the ones that matter.",
}
DOMAINS = ["airline customer service", "hospital scheduling", "warehouse operations", "university admissions", "SaaS support",
           "municipal permits", "retail returns", "bank operations", "insurance claims", "HR leave policy", "IT access control",
           "food safety inspection", "library lending", "telecom billing", "property management", "clinical trial intake",
           "customs and shipping", "energy utility service", "legal intake", "fleet maintenance"]
WRITE = ("Write ONE decision item for a benchmark of typed decisions.\n\nFamily: {family} — {desc}\nDomain: {domain}\n"
         "Answer format: {qtype}\nSeed for variety: {seed}\n\nRequirements:\n"
         "- STATE: {length}. Everything needed to decide must be in the state; no outside knowledge.\n"
         "- Exactly one allowed answer is correct and a careful reader can prove it from the state.\n"
         "- Include a tempting wrong answer that a hasty reader would choose.\n"
         "- {optspec}\n\nReturn ONLY a JSON object with keys: state (string), instructions (string), "
         "options (object mapping each allowed answer label to a one-sentence rubric), answer (one of the labels), "
         "tempting (the wrong label a hasty reader picks).")


class AzureGen:
    """The generate() contract over the Azure OpenAI Responses API (a reasoning deployment such as gpt-5.5).
    Key and endpoint come from AZURE_OPENAI_KEY / AZURE_OPENAI_URL and are never written to disk. Reasoning runs
    server side, so `thinking` maps to reasoning effort and budget forcing is replaced by max_output_tokens."""

    def __init__(self, model, workers=16, effort="medium"):
        self.model, self.workers, self.effort = model, workers, effort
        self.url, self.key = os.environ["AZURE_OPENAI_URL"], os.environ["AZURE_OPENAI_KEY"]
        self.tok = None
        self.usage = collections.Counter()

    def chat_prompt(self, content, thinking):
        return {"content": content, "thinking": thinking}

    def _one(self, prompt, max_tokens):
        import time
        import urllib.request
        body = {"model": self.model, "input": prompt["content"], "max_output_tokens": max_tokens,
                "reasoning": {"effort": self.effort if prompt["thinking"] else "low"}}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(), method="POST",
                                     headers={"api-key": self.key, "Content-Type": "application/json"})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    d = json.load(r)
                text = "".join(c.get("text", "") for o in d.get("output", []) for c in (o.get("content") or [])
                               if isinstance(c, dict) and c.get("type") == "output_text")
                u = d.get("usage") or {}
                self.usage["in"] += u.get("input_tokens", 0)
                self.usage["out"] += u.get("output_tokens", 0)
                self.usage["reasoning"] += (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
                self.usage["calls"] += 1
                return text, d.get("status") == "incomplete"
            except Exception:  # noqa: BLE001 - rate limits and transient 5xx: back off and retry
                time.sleep(min(60, 3 * 2 ** attempt))
        self.usage["failed"] += 1
        return "", True

    def generate(self, prompts, temperature, max_tokens, n=1, top_p=0.95):
        from concurrent.futures import ThreadPoolExecutor
        jobs = [(i, p) for i, p in enumerate(prompts) for _ in range(n)]
        with ThreadPoolExecutor(self.workers) as ex:
            res = list(ex.map(lambda ip: self._one(ip[1], max_tokens), jobs))
        out = [[] for _ in prompts]
        for (i, _), r in zip(jobs, res):
            out[i].append(r)
        print(f"[azure] usage so far: {dict(self.usage)}", flush=True)
        return out


def make_gen(model, backend, mem):
    if backend == "azure":
        return AzureGen(model, workers=int(os.environ.get("AZURE_WORKERS", "16")),
                        effort=os.environ.get("AZURE_EFFORT", "medium"))
    return Gen(model, backend, mem)


class Gen:
    """One interface over the two engines. sglang is the default: k samples share the prompt prefix and the forced
    answer continues an already generated chain, both of which RadixAttention serves from cache."""

    def __init__(self, model, backend="sglang", mem=0.85, max_len=20000):
        from transformers import AutoTokenizer
        self.tok, self.backend = AutoTokenizer.from_pretrained(model), backend
        if backend == "sglang":
            import sglang as sgl
            # flashinfer JIT-compiles a head_dim=256 kernel for Qwen3.5 and needs nvcc >= 12.8; the triton attention
            # backend needs no compiler. Override with OPENJEV_SGL_ATTN=flashinfer where the toolchain is new enough.
            self.llm = sgl.Engine(model_path=model, mem_fraction_static=mem, context_length=max_len,
                                  attention_backend=os.environ.get("OPENJEV_SGL_ATTN", "triton"),
                                  sampling_backend=os.environ.get("OPENJEV_SGL_SAMPLING", "pytorch"))
        else:
            from vllm import LLM
            self.llm = LLM(model, max_model_len=max_len, gpu_memory_utilization=mem, limit_mm_per_prompt={"image": 0})

    def chat_prompt(self, content, thinking):
        return self.tok.apply_chat_template([{"role": "user", "content": content}], tokenize=False,
                                            add_generation_prompt=True, enable_thinking=thinking)

    def generate(self, prompts, temperature, max_tokens, n=1, top_p=0.95):
        """-> per prompt, a list of n (text, hit_length_limit)."""
        if self.backend == "sglang":
            flat = self.llm.generate(prompts, {"temperature": temperature, "top_p": top_p, "max_new_tokens": max_tokens, "n": n})
            assert len(flat) == len(prompts) * n, (len(flat), len(prompts), n)
            out = [(o["text"], (o["meta_info"].get("finish_reason") or {}).get("type") == "length") for o in flat]
            return [out[i * n:(i + 1) * n] for i in range(len(prompts))]
        from vllm import SamplingParams
        res = self.llm.generate(prompts, SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens, n=n, seed=0))
        return [[(c.text, c.finish_reason == "length") for c in o.outputs] for o in res]


def cmd_write(args):
    rng = random.Random(args.seed)
    gen = make_gen(args.model, args.backend, args.gpu_util)
    specs, msgs = [], []
    fams = [f for f in args.families.split(",") if f] or list(FAMILIES)
    for i in range(args.n):
        fam = rng.choice(fams)
        qtype = rng.choice(["yes/no", "one of 3 to 6 labels", "one of 3 to 6 labels"]) if fam != "judge_hard" else "yes/no"
        optspec = ('Allowed answers are exactly "yes" and "no".' if qtype == "yes/no"
                   else "Allowed answers are 3 to 6 short snake_case labels.")
        length = rng.choice(["120 to 250 words", "250 to 500 words", "500 to 900 words with several numbered rules"])
        if fam == "long_policy":
            length = rng.choice(["900 to 1400 words, 8 to 14 numbered sections", "1400 to 2000 words, 12 to 20 numbered sections"])
        specs.append({"family": fam, "qtype": qtype})
        msgs.append(gen.chat_prompt(WRITE.format(family=fam, desc=FAMILIES[fam], domain=rng.choice(DOMAINS), qtype=qtype,
                                                 seed=rng.randint(1, 10**9), length=length, optspec=optspec), thinking=False))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    # generate in chunks and append as they finish: a long API run keeps what it has already paid for
    kept = 0
    with open(args.out, "a" if args.resume else "w") as f:
      for start in range(0, len(msgs), args.chunk):
        outs = gen.generate(msgs[start:start + args.chunk], 0.9, args.max_new)
        for i, (spec, o) in enumerate(zip(specs[start:start + args.chunk], outs), start):
                m = re.search(r"\{.*\}", o[0][0], re.S)
                try:
                    d = json.loads(m.group(0))
                    opts = {str(k): str(v) for k, v in d["options"].items()}
                    assert 2 <= len(opts) <= 6 and isinstance(d["state"], str) and len(d["state"]) > 200
                except Exception:  # noqa: BLE001
                    continue
                crit = {"true": opts.get("yes", "yes"), "false": opts.get("no", "no")} if set(opts) == {"yes", "no"} else opts
                rec = {"id": f"distill-{i:06d}", "family": spec["family"], "state": d["state"], "labels": sorted(opts),
                       "question": {"type": "noul" if set(opts) == {"yes", "no"} else "choice",
                                    "instructions": str(d.get("instructions", "")).strip(), "criteria": crit},
                       "expected": None, "writer_answer": str(d.get("answer")), "writer_tempting": str(d.get("tempting"))}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                kept += 1
        f.flush()
        print(f"[write] {min(start + args.chunk, len(msgs))}/{len(msgs)} done, kept {kept}", flush=True)
    print(f"[write] kept {kept}/{args.n} parseable scenarios", collections.Counter(s["family"] for s in specs))


def cmd_solve(args):
    tasks = [json.loads(l) for p in args.tasks for l in open(p) if l.strip()]
    if args.limit:
        tasks = tasks[: args.limit]
    gen = make_gen(args.model, args.backend, args.gpu_util)
    prompts = []
    for t in tasks:
        opts = options(t)
        state = t["state"] if isinstance(t["state"], str) else json.dumps(t["state"], ensure_ascii=False)
        msg = PROMPT.format(state=state, instr=t["question"]["instructions"], opts="\n".join(f"- {k}: {v}" for k, v in opts.items()))
        prompts.append(gen.chat_prompt(msg, thinking=True))
    outs = gen.generate(prompts, 0.6, args.think_budget, n=args.k)
    # budget forcing: chains that hit the limit must commit to an answer from what they have so far
    forced_prompts, where = [], []
    texts = [[text for text, _ in o] for o in outs]
    for i, o in enumerate(outs):
        for j, (text, cut) in enumerate(o):
            if cut or parse(text, list(options(tasks[i]))) is None:
                if isinstance(prompts[i], dict):  # API backend: reasoning is server side, no chain to continue
                    continue
                forced_prompts.append(prompts[i] + text + "\n</think>\n\nFINAL:")
                where.append((i, j))
    if forced_prompts:
        f_outs = gen.generate(forced_prompts, 0.0, 24)
        for (i, j), fo in zip(where, f_outs):
            texts[i][j] = texts[i][j] + "\n</think>\n\nFINAL:" + fo[0][0]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    n_forced, stats = len(forced_prompts), collections.defaultdict(list)
    with open(args.out, "w") as f:
        for t, tx in zip(tasks, texts):
            labels = list(options(t))
            votes = [parse(x, labels) for x in tx]
            c = collections.Counter(v for v in votes if v)
            top = c.most_common(1)[0] if c else (None, 0)
            rec = {**{k: t[k] for k in ("id", "family", "state", "question", "labels")}, "votes": votes,
                   "majority": top[0], "agree": top[1] / max(len(votes), 1), "expected": t.get("expected"),
                   "writer_answer": t.get("writer_answer")}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if t.get("expected") is not None:
                stats[t["family"]].append(top[0] == str(t["expected"]))
    print(f"[solve] {len(tasks)} items x {args.k}; budget-forced chains: {n_forced}/{len(tasks) * args.k}")
    if stats:
        allv = [x for v in stats.values() for x in v]
        print(f"[solve] teacher majority accuracy on labelled items: {sum(allv) / len(allv):.3f}",
              {k: round(sum(v) / len(v), 2) for k, v in sorted(stats.items())})


def cmd_rows(args):
    rng = random.Random(0)
    tmpl = ['The answer to "{instr}" is {label}: {crit}', 'Decision for "{instr}": {label} — {crit}']
    kept = dropped = rows = 0
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for line in open(args.solved):
            r = json.loads(line)
            votes = [v for v in r["votes"] if v]
            if len(votes) < max(2, len(r["votes"]) // 2) or r["agree"] < args.min_agree:
                dropped += 1
                continue
            if args.require_writer and r.get("writer_answer") not in (None, "None") and r["majority"] != r["writer_answer"]:
                dropped += 1  # the item's author and its solver disagree: the item is probably ill-posed
                continue
            opts = options(r)
            state = r["state"] if isinstance(r["state"], str) else json.dumps(r["state"], ensure_ascii=False)
            # the writer sometimes repeats the question and the option list inside the state; the student must not
            # see option wording in its premise
            state = re.split(r"\n\s*(?:Instructions?|Options?|Allowed answers?|Question)\s*:", state, maxsplit=1)[0].strip()
            if len(state) < 150:
                dropped += 1
                continue
            t = rng.choice(tmpl)
            for v in votes:
                others = [o for o in opts if o != v]
                for lab in [v] + rng.sample(others, min(2, len(others))):
                    f.write(json.dumps({"premise": state, "hypothesis": t.format(instr=r["question"]["instructions"], label=lab, crit=opts[lab]),
                                        "label": 1 if lab == v else 0, "source": f"distill_{r['family']}", "image": ""}, ensure_ascii=False) + "\n")
                    rows += 1
            kept += 1
    print(f"[rows] items kept {kept}, dropped {dropped}; student rows {rows}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write"); w.add_argument("--model", required=True); w.add_argument("--n", type=int, default=6000)
    w.add_argument("--out", required=True); w.add_argument("--max-new", type=int, default=2500); w.add_argument("--seed", type=int, default=0)
    w.add_argument("--gpu-util", type=float, default=0.85); w.add_argument("--backend", choices=["sglang", "vllm", "azure"], default="sglang")
    w.add_argument("--families", default="", help="comma-separated subset of FAMILIES (default: all)")
    w.add_argument("--chunk", type=int, default=500, help="items per generate() call; each chunk is appended to --out")
    w.add_argument("--resume", action="store_true", help="append to --out instead of overwriting")
    s = sub.add_parser("solve"); s.add_argument("--model", required=True); s.add_argument("--tasks", nargs="+", required=True)
    s.add_argument("--out", required=True); s.add_argument("--k", type=int, default=6); s.add_argument("--think-budget", type=int, default=3000)
    s.add_argument("--gpu-util", type=float, default=0.85); s.add_argument("--limit", type=int, default=0)
    s.add_argument("--backend", choices=["sglang", "vllm", "azure"], default="sglang")
    r = sub.add_parser("rows"); r.add_argument("--solved", required=True); r.add_argument("--out", required=True)
    r.add_argument("--min-agree", type=float, default=0.67); r.add_argument("--require-writer", action="store_true")
    args = ap.parse_args()
    {"write": cmd_write, "solve": cmd_solve, "rows": cmd_rows}[args.cmd](args)


if __name__ == "__main__":
    main()
