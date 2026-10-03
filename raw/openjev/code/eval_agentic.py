#!/usr/bin/env python
"""Agentic evaluation for jev cross-encoders: BFCL v4 and held-out Mind2Web websites. Nothing here is trained on.

    python eval_agentic.py --models ckpt/qwen3.5-0.8b-nli-v2s-agent --out results/v2s/agentic.json

Tasks (score = P(entailment)):
  bfcl_relevance   BFCL v4 irrelevance + live_relevance: premise = request + the available functions, hypothesis =
                   "One of the available functions can serve this request." Gold: relevance yes / irrelevance no.
                   AUROC + balanced accuracy at 0.5.
  bfcl_call        BFCL v4 multiple / live_multiple: the gold call against the other functions in the same item,
                   phrased as "The correct call is f(args)". Rank-1 accuracy over the candidate calls.
  taubench         tau2-bench simulation results (sierra-research/tau2-bench, data/tau2/results/final): premise =
                   domain policy + conversation. Two labels come with each simulation — the 0/1 task reward, and
                   each `nl_assertion` ("Agent does not cancel insurance or offer a refund.") with met / not met.
                   telecom is the headline: tau-bench v1 (the training source) has no telecom domain, so the policy,
                   the tools and the tasks are all unseen. retail / airline are reported too, but their v1 policies
                   were in training, so only the traces are new there.
  mind2web         the websites data_mix.py `agentic2` held out (mind2web_heldout_websites.json): pick the next
                   action among the step's own actions. Rank-1 accuracy, plus "is the task finished" accuracy.
"""
import argparse
import json
import os
import random
import urllib.request
from collections import defaultdict

import numpy as np

from eval import ENT, NLIScorer
from eval_extra import Window, auroc, bacc, fetch

BFCL = ("https://raw.githubusercontent.com/ShishirPatil/gorilla/main/berkeley-function-call-leaderboard/"
        "bfcl_eval/data/")
RELEVANT = "One of the available functions can serve this request."


def load_bfcl(name, cache, answers=False):
    url = BFCL + (f"possible_answer/{name}" if answers else name)
    path = fetch(url, cache)
    return [json.loads(line) for line in open(path) if line.strip()]


def user_text(item):
    msgs = item["question"][0] if item["question"] and isinstance(item["question"][0], list) else item["question"]
    return "\n".join(m.get("content", "") for m in msgs if m.get("role") == "user")


def fn_text(fn, limit=400):
    params = (fn.get("parameters") or {}).get("properties") or {}
    args = ", ".join(f"{k}: {(v or {}).get('type', '?')}" for k, v in list(params.items())[:8])
    return f"{fn.get('name')}({args}) — {(fn.get('description') or '')[:limit]}"


def eval_bfcl_relevance(w, args):
    rows = []
    for name, gold in (("BFCL_v4_irrelevance.json", 0), ("BFCL_v4_live_relevance.json", 1)):
        for it in load_bfcl(name, args.cache):
            funcs = "\n".join(fn_text(f) for f in (it.get("function") or [])[:20])
            rows.append((f"User request: {user_text(it)}\n\nAvailable functions:\n{funcs}", gold))
    if args.limit:
        rows = random.Random(0).sample(rows, min(args.limit * 4, len(rows)))
    p = w.probs([(prem, RELEVANT) for prem, _ in rows])[:, ENT]
    y = [g for _, g in rows]
    return {"n": len(y), "pos_rate": float(np.mean(y)), "auroc": auroc(y, p), "bacc@0.5": bacc(y, p)}


def call_text(name, params):
    args = ", ".join(f"{k}={json.dumps(v[0] if isinstance(v, list) and v else v, ensure_ascii=False)}"
                     for k, v in (params or {}).items())
    return f"The correct call is {name}({args})."


def eval_bfcl_call(w, args):
    res = {}
    for name in ("BFCL_v4_multiple.json", "BFCL_v4_live_multiple.json"):
        items = {it["id"]: it for it in load_bfcl(name, args.cache)}
        golds = {g["id"]: g for g in load_bfcl(name, args.cache, answers=True)}
        pairs, owner, gold_idx = [], [], {}
        ids = list(items)
        if args.limit:
            ids = random.Random(0).sample(ids, min(args.limit, len(ids)))
        for i, tid in enumerate(ids):
            it, g = items[tid], golds.get(tid)
            if not g or not g.get("ground_truth"):
                continue
            truth = g["ground_truth"][0]
            gold_name = next(iter(truth))
            funcs = it.get("function") or []
            names = [f.get("name") for f in funcs]
            if gold_name not in names or len(names) < 2:
                continue
            prem = f"User request: {user_text(it)}\n\nAvailable functions:\n" + "\n".join(fn_text(f) for f in funcs[:20])
            gold_idx[i] = len(pairs)
            pairs.append((prem, call_text(gold_name, truth[gold_name]))); owner.append(i)
            for other in [n for n in names if n != gold_name][:4]:
                pairs.append((prem, call_text(other, truth[gold_name]))); owner.append(i)
        if not pairs:
            continue
        p = w.probs(pairs)[:, ENT]
        by = defaultdict(list)
        for j, i in enumerate(owner):
            by[i].append((j, p[j]))
        hits = [max(v, key=lambda x: x[1])[0] == gold_idx[i] for i, v in by.items() if i in gold_idx]
        res[name.replace("BFCL_v4_", "").replace(".json", "")] = {"n": len(hits), "rank1_acc": float(np.mean(hits))}
    return res


def eval_mind2web(w, args):
    from datasets import load_dataset
    held = set(json.load(open(args.m2w_heldout))) if os.path.exists(args.m2w_heldout) else set()
    ds = load_dataset("osunlp/Mind2Web", split="train")
    steps, done_rows = [], []
    for ex in ds:
        if held and ex["website"] not in held:
            continue
        reprs = ex["action_reprs"]
        for i, act in enumerate(reprs):
            history = " -> ".join(reprs[max(0, i - 3):i]) or "(nothing yet)"
            prem = (f"Goal: {ex['confirmed_task']}\nWebsite: {ex['website']}\nActions so far: {history}")
            others = [a for a in reprs if a != act]
            if len(others) < 3:
                continue
            cands = [act] + random.Random(i).sample(others, 3)
            steps.append((prem, cands))
            done_rows.append((prem, int(i + 1 == len(reprs))))
    if args.limit:
        keep = random.Random(0).sample(range(len(steps)), min(args.limit * 3, len(steps)))
        steps = [steps[i] for i in keep]; done_rows = [done_rows[i] for i in keep]
    pairs, owner, gold_at = [], [], {}
    for i, (prem, cands) in enumerate(steps):
        gold_at[i] = len(pairs)  # cands[0] is the gold action
        for c in cands:
            pairs.append((prem, f"The next action is: {c}")); owner.append(i)
    p = w.probs(pairs)[:, ENT]
    best = defaultdict(lambda: (-1.0, -1))
    for j, i in enumerate(owner):
        if p[j] > best[i][0]:
            best[i] = (float(p[j]), j)
    hits = [best[i][1] == gold_at[i] for i in range(len(steps))]
    pd = w.probs([(prem, "This is the last action needed to complete the task.") for prem, _ in done_rows])[:, ENT]
    y = [g for _, g in done_rows]
    return {"websites_held_out": sorted(held), "n_steps": len(steps), "next_action_rank1": float(np.mean(hits)),
            "task_finished_auroc": auroc(y, pd), "task_finished_bacc@0.5": bacc(y, pd)}


TAU2 = ("https://raw.githubusercontent.com/sierra-research/tau2-bench/main/data/tau2/results/final/"
        "{model}_{domain}_default_gpt-4.1-2025-04-14_4trials.json")
TAU2_RUNS = [("gpt-4.1-2025-04-14", d) for d in ("telecom", "airline", "retail")]
TAU_DONE = "The agent followed the domain policy and resolved the user's request."


def tau2_text(messages, policy, policy_chars=6000, trace_chars=6000):
    lines = []
    for m in messages:
        role = m.get("role")
        for c in (m.get("tool_calls") or []):
            fn = c.get("function") or c
            lines.append(f"{role} calls {fn.get('name')}({str(fn.get('arguments'))[:200]})")
        text = (m.get("content") or "").strip()
        if text:
            lines.append(f"{role}: {text[:400]}")
    return f"Domain policy:\n{policy[:policy_chars]}\n\nConversation:\n" + "\n".join(lines)[-trace_chars:]


def eval_taubench(w, args):
    res = {}
    for model, domain in TAU2_RUNS:
        try:
            path = fetch(TAU2.format(model=model, domain=domain), args.cache)
            data = json.load(open(path))
        except Exception as e:  # noqa: BLE001
            res[domain] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            continue
        # airline/retail ship policy.md; telecom splits its policy into main_policy.md + the tech-support manual
        policy = ""
        for fn in ("policy.md", "main_policy.md", "tech_support_workflow.md"):
            try:
                policy += open(fetch(f"https://raw.githubusercontent.com/sierra-research/tau2-bench/main/"
                                     f"data/tau2/domains/{domain}/{fn}", args.cache)).read() + "\n"
            except Exception:  # noqa: BLE001 - a domain has one layout or the other, never both
                continue
        sims = data.get("simulations") or []
        if args.limit:
            sims = random.Random(0).sample(sims, min(args.limit, len(sims)))
        traj_pairs, traj_y, as_pairs, as_y = [], [], [], []
        for s in sims:
            info = s.get("reward_info") or {}
            prem = tau2_text(s.get("messages") or [], policy)
            traj_pairs.append((prem, TAU_DONE)); traj_y.append(int(float(info.get("reward", 0)) >= 1.0))
            for a in (info.get("nl_assertions") or []):
                text = (a.get("nl_assertion") or "").strip()
                if text:
                    as_pairs.append((prem, text)); as_y.append(int(bool(a.get("met"))))
        out = {"n_sims": len(sims)}
        if traj_pairs:
            p = w.probs(traj_pairs)[:, ENT]
            out["task_success"] = {"n": len(traj_y), "pos_rate": float(np.mean(traj_y)),
                                   "auroc": auroc(traj_y, p), "bacc@0.5": bacc(traj_y, p)}
        if as_pairs:
            p = w.probs(as_pairs)[:, ENT]
            out["nl_assertions"] = {"n": len(as_y), "pos_rate": float(np.mean(as_y)),
                                    "auroc": auroc(as_y, p), "bacc@0.5": bacc(as_y, p)}
        res[domain] = out
    return res


TASKS = {"taubench": eval_taubench, "bfcl_relevance": eval_bfcl_relevance, "bfcl_call": eval_bfcl_call, "mind2web": eval_mind2web}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", nargs="+", default=list(TASKS))
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cache", default="data/extra_cache/bfcl")
    ap.add_argument("--m2w-heldout", default=os.path.expanduser("~/qwen_nli/nli_stage4/mind2web_heldout_websites.json"))
    args = ap.parse_args()
    res = json.load(open(args.out)) if os.path.exists(args.out) else {}
    for m in args.models:
        w = Window(NLIScorer(m, bs=args.bs, max_len=args.max_len), args.max_len)
        res.setdefault(m, {})
        for t in args.tasks:
            print(f"== {m} :: {t}", flush=True)
            try:
                res[m][t] = TASKS[t](w, args)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                res[m][t] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            print(json.dumps(res[m][t])[:400], flush=True)
            os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
            json.dump(res, open(args.out, "w"), indent=2)
        del w
        import torch
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
