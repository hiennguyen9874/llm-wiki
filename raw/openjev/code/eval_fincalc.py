#!/usr/bin/env python
"""Financial arithmetic for jev cross-encoders: FinCalc-NLI test split. Nothing here is trained on.

    python eval_fincalc.py --models ckpt/qwen3.5-4b-nli-v5 ckpt/qwen3.5-4b-nli --out results/fincalc_4b.json

FinCalc-NLI (anespo28/fincalc-nli, MIT, synthetic): premise = evidence with the inputs and distractor figures
(another company, the prior year, policy lines), hypothesis = a derived figure (LTV, DSCR, interest cover, net
leverage, EBITDA margin, CET1, NPL ratio, NPL coverage, annual interest, net debt), a covenant pass/breach, or a
plain lookup. Labels are computed in code. The test split uses names and templates disjoint from train, and one
formula (NPL coverage) that train never shows.

Reported: 3-way accuracy (argmax), per mistake kind (slip, inverted ratio, wrong entity, unit error, flipped
covenant, missing input, ...) and per metric.
"""
import argparse
import json
from collections import defaultdict

import numpy as np

from eval import NLIScorer

REPO = "anespo28/fincalc-nli"


def load(n):
    from datasets import load_dataset
    ds = load_dataset(REPO, data_files={"test": "test.jsonl"}, split="test")
    return ds.shuffle(seed=0).select(range(min(n, len(ds)))) if n else ds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=0, help="subsample the 4,000-item test split (0 = all)")
    ap.add_argument("--bs", type=int, default=32)
    a = ap.parse_args()
    ds = load(a.n)
    pairs = list(zip(ds["premise"], ds["hypothesis"]))
    gold = np.array(ds["label"])  # already in jev order: 0 contradiction, 1 entailment, 2 neutral
    res = {}
    for path in a.models:
        pred = NLIScorer(path, bs=a.bs).predict(pairs).argmax(1)
        by = defaultdict(list)
        for k, m, ok in zip(ds["kind"], ds["metric"], pred == gold):
            by["kind:" + k].append(ok)
            by["metric:" + m].append(ok)
        res[path] = {"n": len(pairs), "accuracy": round(float((pred == gold).mean()), 4),
                     **{k: round(float(np.mean(v)), 4) for k, v in sorted(by.items())}}
        print(path, json.dumps(res[path]), flush=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
