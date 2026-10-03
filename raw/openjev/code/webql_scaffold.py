#!/usr/bin/env python
"""Page-relevance scaffold for openjev: chunk the document, score every (chunk, hypothesis) pair, aggregate by voting.
Hypotheses: one per spec ("The document states <spec>") and one per field ("The document states <field desc>").
Chunk sizes x aggregators x hypothesis sets -> AUROC / best accuracy for gold non-null vs all-null.

    python webql_scaffold.py --ckpt ckpt/qwen3.5-4b-nli --data data/sem_extract_bench.jsonl --out results/webql_scaffold_4b.json
"""
import argparse, json
import numpy as np
from webql_bench import Scorer, auroc, best_acc, spec_hypothesis


def chunks(content, size, overlap):
    step = max(1, size - overlap)
    out = [content[i:i + size] for i in range(0, max(1, len(content) - overlap), step)]
    return out or [content]


def hyps_for(spec, mode):
    d = spec["description"].strip()
    if mode == "spec":
        return [spec_hypothesis(spec)]
    if mode == "fields":
        return [f"The document states {desc}." for _, desc in (spec.get("fields") or [])] or [f"The document states {d}."]
    return [spec_hypothesis(spec)] + [f"The document states {desc}." for _, desc in (spec.get("fields") or [])]


AGG = {
    "max": lambda p: p.max(),
    "mean": lambda p: p.mean(),
    "top3_mean": lambda p: np.sort(p)[-3:].mean(),
    "vote_frac_0.5": lambda p: (p > 0.5).mean(),
    "vote_any_0.5": lambda p: float((p > 0.5).any()),
    "noisy_or": lambda p: 1 - np.prod(1 - p),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="ckpt/qwen3.5-4b-nli")
    ap.add_argument("--data", default="data/sem_extract_bench.jsonl")
    ap.add_argument("--out", default="results/webql_scaffold_4b.json")
    ap.add_argument("--sizes", nargs="+", type=int, default=[500, 1500, 3000])
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data)]
    labels = [int(any(v is not None for v in r["gold"].values())) for r in rows]
    scorer = Scorer(args.ckpt, bs=32, max_len=1024)
    res = {"n_docs": len(rows), "n_all_null": int(len(rows) - sum(labels)), "configs": {}}
    for size in args.sizes:
        overlap = size // 4
        for hmode in ["spec", "fields", "both"]:
            pairs, jobs = [], []
            for ri, r in enumerate(rows):
                cs = chunks(r["input"].get("content") or "", size, overlap)
                for si, spec in enumerate(r["extract"]):
                    for hi, h in enumerate(hyps_for(spec, hmode)):
                        for ci, c in enumerate(cs):
                            pairs.append((c, h)); jobs.append((ri, si, hi))
            p = scorer.p_entail(pairs)
            per = {}
            for (ri, si, hi), v in zip(jobs, p):
                per.setdefault(ri, {}).setdefault((si, hi), []).append(float(v))
            for agg_name, agg in AGG.items():
                # per hypothesis aggregate over chunks; doc score = max over hypotheses (any field present => relevant)
                # plus a "mean over hypotheses" variant
                for hagg_name, hagg in [("max_hyp", max), ("mean_hyp", lambda xs: float(np.mean(xs)))]:
                    scores = [hagg([agg(np.array(v)) for v in per[ri].values()]) for ri in range(len(rows))]
                    key = f"size{size}/{hmode}/{agg_name}/{hagg_name}"
                    res["configs"][key] = {"auroc": auroc(scores, labels), "best_acc": best_acc(scores, labels)}
            print(f"size {size} hyps {hmode}: {len(pairs)} pairs; best so far:",
                  max(res["configs"].items(), key=lambda kv: kv[1]["auroc"]), flush=True)
    json.dump(res, open(args.out, "w"), indent=2)
    top = sorted(res["configs"].items(), key=lambda kv: -kv[1]["auroc"])[:12]
    print("\n| config | AUROC | best acc |\n|---|---|---|")
    for k, v in top:
        print(f"| {k} | {v['auroc']:.3f} | {v['best_acc']:.3f} |")


if __name__ == "__main__":
    main()
