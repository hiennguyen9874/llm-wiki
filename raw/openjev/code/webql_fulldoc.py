#!/usr/bin/env python
"""Page relevance with the FULL document as premise (one pair per doc, up to --max-len tokens), jev backbone frozen:
zero-shot P(entailment) and a 5-fold-CV MLP on the document latent. Label = gold non-null.
    python webql_fulldoc.py --ckpt /mnt/qwen_nli_ckpt/qwen3.5-35b-a3b-nli --out results/webql_fulldoc_35b.json
"""
import argparse, json
import numpy as np, torch
from webql_bench import auroc, best_acc, spec_hypothesis
from webql_mlp import LatScorer
from latent_mlp import fit, predict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--data", default="data/sem_extract_bench.jsonl")
    ap.add_argument("--out", required=True); ap.add_argument("--max-len", type=int, default=8192); ap.add_argument("--max-chars", type=int, default=40000)
    ap.add_argument("--bs", type=int, default=2); ap.add_argument("--folds", type=int, default=5); ap.add_argument("--eps", type=float, default=0.1)
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data)]
    sc = LatScorer(args.ckpt, bs=args.bs, max_len=args.max_len)
    sc.tok.truncation_side = "left"  # long docs: drop the beginning of the premise, never the hypothesis at the end
    # premise = whole document; hypothesis about the (first) spec. Truncation cuts the END, so put the hypothesis first via template
    # order? The template is Premise/Hypothesis; to keep the hypothesis inside the window we cap the premise by chars.
    pairs = [((r["input"].get("content") or "")[: args.max_chars], spec_hypothesis(r["extract"][0])) for r in rows]
    labels = np.array([int(any(v is not None for v in r["gold"].values())) for r in rows])
    lens = [len(sc.tok(sc.template.format(premise=p, hypothesis=h))["input_ids"]) for p, h in pairs[:50]]
    print(f"{len(pairs)} docs; token length of first 50: median {int(np.median(lens))} max {max(lens)}", flush=True)
    X, P = sc.latents(pairs)
    X = X.astype(np.float32)
    rng = np.random.RandomState(0); perm = rng.permutation(len(rows)); folds = np.array_split(perm, args.folds)
    ns = argparse.Namespace(hidden=512, dropout=0.1, lr=1e-3, wd=1e-2, bs=128, epochs=60, patience=8, eps=args.eps, seed=0)
    scores = np.zeros(len(rows))
    for f, te in enumerate(folds):
        tr_all = np.array([i for i in range(len(rows)) if i not in set(te.tolist())]); va, tr = tr_all[: len(tr_all) // 10], tr_all[len(tr_all) // 10:]
        m, st, _, _ = fit(X[tr], labels[tr], tr, X[va], labels[va], va, ns)
        scores[te] = predict(m, st, X[te])
    res = {"n_docs": len(rows), "max_len_tokens": args.max_len,
           "zeroshot_auroc": auroc(P, labels), "zeroshot_best_acc": best_acc(P, labels),
           "mlp_auroc": auroc(scores, labels), "mlp_best_acc": best_acc(scores, labels)}
    json.dump(res, open(args.out, "w"), indent=2); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
