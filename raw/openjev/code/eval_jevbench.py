#!/usr/bin/env python
"""JevBench (github.com/fstandhartinger/jevbench) public items with a jev NLI cross-encoder.

    python eval_jevbench.py --models ckpt/qwen3.5-0.8b-nli-v2s --out results/v2s/jevbench.json

Only the public items exist outside the benchmark (easy 48, standard 72 = `original`, hard 111; judge and held-out
items are private), so the numbers are PUBLIC-ITEM accuracy and not the JevBench Score. For a like-for-like
comparison the leaderboard systems are re-scored on exactly these items from JevBench's per-task artifact.

Every option becomes one hypothesis over the state; the option distribution is P(entailment) normalised over the
options (native, one forward pass per option, nothing generated):
    choice  "The answer to "<instructions>" is <label>: <criterion>."
    noul    two options, yes/no, phrased with the item's true/false criteria
    score   one hypothesis per level, phrased with the level description
"""
import argparse
import json
import os
import time
from collections import defaultdict

import numpy as np

from eval import ENT, NLIScorer
from eval_extra import Window, fetch

REPO = "https://raw.githubusercontent.com/fstandhartinger/jevbench/main/"
TIERS = {"easy": "datasets/public/easy.jsonl", "standard": "datasets/public/original.jsonl",
         "hard": "datasets/public/hard.jsonl"}
PER_TASK = "results/v1.2/jevbench-v1.2-per-task.json"


def options(task):
    q = task["question"]
    instr, crit = q["instructions"].strip(), q.get("criteria")
    if q["type"] == "noul":
        crit = crit or {}
        return [("no", f'The answer to "{instr}" is no: {crit.get("false", "no")}'),
                ("yes", f'The answer to "{instr}" is yes: {crit.get("true", "yes")}')]
    if q["type"] == "score":
        return [(str(i), f'The answer to "{instr}" is level {i}: {c}') for i, c in enumerate(crit)]
    return [(lab, f'The answer to "{instr}" is {lab}: {(crit or {}).get(lab) or lab}') for lab in task["labels"]]


def ece(conf, correct, bins=10):
    conf, correct = np.asarray(conf), np.asarray(correct, dtype=float)
    idx = np.minimum((conf * bins).astype(int), bins - 1)
    return float(sum(abs(correct[idx == b].mean() - conf[idx == b].mean()) * (idx == b).mean()
                     for b in range(bins) if (idx == b).any()))


def run_model(w, tasks):
    pairs, owner = [], []
    for i, (_, t) in enumerate(tasks):
        state = t["state"] if isinstance(t["state"], str) else json.dumps(t["state"], ensure_ascii=False)
        for lab, hyp in options(t):
            pairs.append((state, hyp)); owner.append((i, lab))
    t0 = time.perf_counter()
    pe = w.probs(pairs)[:, ENT]
    wall = time.perf_counter() - t0
    dist = defaultdict(dict)
    for (i, lab), p in zip(owner, pe):
        dist[i][lab] = float(p)
    per_task, by = {}, defaultdict(list)
    for i, (tier, t) in enumerate(tasks):
        z = sum(dist[i].values()) or 1.0
        probs = {k: v / z for k, v in dist[i].items()}
        pred = max(probs, key=probs.get)
        ok = pred == str(t["expected"])
        per_task[t["id"]] = {"pred": pred, "ok": ok, "conf": probs[pred]}
        by[tier].append((ok, probs[pred], t["family"]))
    res = {"wall_s": wall, "n_forward": len(pairs)}
    for tier, rows in by.items():
        fam = defaultdict(list)
        for ok, _, f in rows:
            fam[f].append(ok)
        res[tier] = {"n": len(rows), "accuracy": float(np.mean([r[0] for r in rows])),
                     "ece": ece([r[1] for r in rows], [r[0] for r in rows]),
                     "by_family": {f: float(np.mean(v)) for f, v in sorted(fam.items())}}
    res["all_public"] = float(np.mean([r[0] for rows in by.values() for r in rows]))
    return res, per_task


def leaderboard(cache, ids):
    d = json.load(open(fetch(REPO + PER_TASK, cache)))
    tier_of = {t["id"]: t["tier"] for t in d["tasks"]}
    out = {}
    for name, s in d["systems"].items():
        pt = s.get("public_tasks") or {}
        by = defaultdict(list)
        for tid in ids:
            if tid in pt:
                by[tier_of[tid]].append(pt[tid][0] == "c")
        if by:
            out[name] = {**{t: float(np.mean(v)) for t, v in by.items()},
                         "all_public": float(np.mean([x for v in by.values() for x in v])),
                         "n": sum(len(v) for v in by.values()), "display": s.get("display")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=8192)
    ap.add_argument("--cache", default="data/extra_cache/jevbench")
    args = ap.parse_args()
    tasks = [(tier, json.loads(line)) for tier, path in TIERS.items()
             for line in open(fetch(REPO + path, args.cache)) if line.strip()]
    res = json.load(open(args.out)) if os.path.exists(args.out) else {}
    res["_leaderboard_on_public_items"] = leaderboard(args.cache, [t["id"] for _, t in tasks])
    for m in args.models:
        w = Window(NLIScorer(m, bs=args.bs, max_len=args.max_len), args.max_len)
        res[m], per_task = run_model(w, tasks)
        res[m]["per_task"] = per_task
        print(m, json.dumps({k: v for k, v in res[m].items() if k != "per_task"})[:800], flush=True)
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump(res, open(args.out, "w"), indent=2)
        del w
        import torch
        torch.cuda.empty_cache()
    print("\n| system | easy | standard | hard | all public |\n|---|---|---|---|---|")
    rows = [(k, v) for k, v in res["_leaderboard_on_public_items"].items()]
    rows += [(m, {t: res[m][t]["accuracy"] for t in TIERS} | {"all_public": res[m]["all_public"]}) for m in args.models]
    for k, v in sorted(rows, key=lambda kv: -kv[1]["all_public"]):
        print(f"| {k} | " + " | ".join(f"{v.get(t, float('nan')):.3f}" for t in TIERS) + f" | {v['all_public']:.3f} |")


if __name__ == "__main__":
    main()
