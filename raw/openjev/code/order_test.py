#!/usr/bin/env python
"""Option-order invariance and run-to-run determinism of the jev decision wrapper, on the public JevBench items.

    OPENJEV_DEVICE=cuda python order_test.py --model ckpt/qwen3.5-0.8b-nli-v2s --tasks easy.jsonl original.jsonl hard.jsonl

For every item: the same question with options in the given order, reversed, and shuffled, plus the given order a
second time. Reports label flips and the largest change in any option's probability.
"""
import argparse
import json
import random

from openjev_decide import OpenJev, RUBRIC_MARK
from think_probe import options


def ask(jev, task, order):
    opts = options(task)
    q = {"type": "choice", "options": order,
         "instructions": task["question"]["instructions"] + RUBRIC_MARK + json.dumps({k: opts[k] for k in order})}
    state = task["state"] if isinstance(task["state"], str) else json.dumps(task["state"], ensure_ascii=False)
    return jev.decide(state, [q])[0]["probabilities"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tasks", nargs="+", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    jev = OpenJev.from_pretrained(args.model)
    rng = random.Random(0)
    stats = {k: {"flips": 0, "max_dp": 0.0, "sum_dp": 0.0} for k in ("rerun", "reversed", "shuffled")}
    n = 0
    for path in args.tasks:
        for line in open(path):
            t = json.loads(line)
            base = list(options(t))
            if len(base) < 2:
                continue
            ref = ask(jev, t, base)
            shuf = base[:]
            rng.shuffle(shuf)
            for name, order in (("rerun", base), ("reversed", base[::-1]), ("shuffled", shuf)):
                p = ask(jev, t, order)
                dp = max(abs(p[k] - ref[k]) for k in base)
                s = stats[name]
                s["flips"] += max(p, key=p.get) != max(ref, key=ref.get)
                s["max_dp"] = max(s["max_dp"], dp); s["sum_dp"] += dp
            n += 1
    for s in stats.values():
        s["mean_dp"] = s.pop("sum_dp") / n
    res = {"model": args.model, "n_items": n, **stats}
    print(json.dumps(res, indent=1))
    if args.out:
        json.dump(res, open(args.out, "w"), indent=1)


if __name__ == "__main__":
    main()
