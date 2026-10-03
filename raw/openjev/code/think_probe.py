#!/usr/bin/env python
"""Does reasoning help a small generative Qwen on typed decisions? No training: base model, thinking on, one sample.

    python think_probe.py --model Qwen/Qwen3.5-0.8B --tasks hard.jsonl --shard 0/3 --out results/think_0.8b_0.jsonl

Decides whether a GRPO "slow path" is worth building: if thinking alone lifts the hard tier well above the one-pass
cross-encoder, RL on the verifiable generators (hard_gen.py) has headroom; if not, it has to create the skill itself.
Each record keeps the raw completion, so answers can be re-parsed later.
"""
import argparse
import json
import os
import re
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROMPT = ("You are given a STATE and a QUESTION with a fixed set of allowed answers. Work through the facts and rules "
          "step by step, then finish with one line of the form\nFINAL: <one allowed answer, copied exactly>\n\n"
          "STATE:\n{state}\n\nQUESTION: {instr}\n\nALLOWED ANSWERS:\n{opts}")


def options(task):
    q, crit = task["question"], task["question"].get("criteria")
    if q["type"] == "noul":
        crit = crit or {}
        return {"yes": crit.get("true", "yes"), "no": crit.get("false", "no")}
    if q["type"] == "score":
        return {str(i): c for i, c in enumerate(crit)}
    return {k: (crit or {}).get(k) or k for k in task["labels"]}


def parse(text, labels):
    tail = text.split("</think>")[-1]
    m = re.findall(r"FINAL:\s*[`'\"]?([^\n`'\"]+)", tail)
    cand = (m[-1] if m else tail[-80:]).strip().strip(".").lower()
    for lab in sorted(labels, key=len, reverse=True):
        if cand == lab.lower() or cand.startswith(lab.lower()):
            return lab
    return next((lab for lab in sorted(labels, key=len, reverse=True) if lab.lower() in cand), None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--max-new", type=int, default=1536)
    ap.add_argument("--no-think", action="store_true")
    ap.add_argument("--dtype", default=os.environ.get("OPENJEV_DTYPE", "bfloat16"))
    args = ap.parse_args()
    k, n = map(int, args.shard.split("/"))
    tasks = [json.loads(l) for l in open(args.tasks) if l.strip()][k::n]
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype)).cuda().eval()
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for t in tasks:
            opts = options(t)
            state = t["state"] if isinstance(t["state"], str) else json.dumps(t["state"], ensure_ascii=False)
            msg = PROMPT.format(state=state, instr=t["question"]["instructions"],
                                opts="\n".join(f"- {k}: {v}" for k, v in opts.items()))
            ids = tok.apply_chat_template([{"role": "user", "content": msg}], add_generation_prompt=True,
                                          enable_thinking=not args.no_think, return_tensors="pt", return_dict=True).to("cuda")
            t0 = time.perf_counter()
            with torch.no_grad():
                out = model.generate(**ids, max_new_tokens=args.max_new, do_sample=False)
            text = tok.decode(out[0, ids["input_ids"].shape[1]:], skip_special_tokens=True)
            pred = parse(text, list(opts))
            rec = {"id": t["id"], "family": t["family"], "expected": str(t["expected"]), "pred": pred,
                   "correct": pred == str(t["expected"]), "new_tokens": int(out.shape[1] - ids["input_ids"].shape[1]),
                   "latency_s": round(time.perf_counter() - t0, 2), "completion": text}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            print(t["id"], t["family"], rec["correct"], rec["new_tokens"], f"{rec['latency_s']}s", flush=True)


if __name__ == "__main__":
    main()
