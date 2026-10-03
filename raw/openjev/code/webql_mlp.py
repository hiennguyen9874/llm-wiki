#!/usr/bin/env python
"""keenable-webql sem_extract bench with the latent + MLP recipe (frozen jev backbone, small MLP, soft BCE), 5-fold CV over documents.
A) page relevance: doc latent = max-pool over block latents (+ max P(ent)); label = gold non-null.
B) block selection: per-block latent; label = block holds a gold verbatim quote; recall@k of gold blocks vs zero-shot / lexical.
    python webql_mlp.py --ckpt /mnt/qwen_nli_ckpt/qwen3.5-35b-a3b-nli --out results/webql_mlp_35b.json
"""
import argparse, json
from collections import Counter
import numpy as np, torch
from webql_bench import Scorer, auroc, best_acc, spec_hypothesis, blocks_of, quote_blocks, iter_quotes, terms, WORD_RE
from latent_mlp import fit, predict


class LatScorer(Scorer):
    @torch.no_grad()
    def latents(self, pairs):
        X, P = [], []
        backbone = getattr(self.model, self.model.base_model_prefix)
        for i in range(0, len(pairs), self.bs):
            chunk = pairs[i:i + self.bs]
            texts = [self.template.format(premise=p, hypothesis=h) for p, h in chunk]
            enc = self.tok(texts, truncation=True, max_length=self.max_len, padding=True, return_tensors="pt").to("cuda")
            h = backbone(**enc).last_hidden_state
            last = enc["attention_mask"].sum(1) - 1
            pooled = h[torch.arange(h.shape[0], device=h.device), last]
            X.append(pooled.float().cpu().numpy().astype(np.float16))
            P.append(torch.softmax(self.model.score(pooled).float(), -1)[:, 1].cpu().numpy())
        return np.concatenate(X), np.concatenate(P)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--data", default="data/sem_extract_bench.jsonl")
    ap.add_argument("--out", required=True); ap.add_argument("--folds", type=int, default=5); ap.add_argument("--eps", type=float, default=0.1)
    ap.add_argument("--ks", nargs="+", type=int, default=[4, 8, 12, 24]); ap.add_argument("--bs", type=int, default=16)
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data)]
    sc = LatScorer(args.ckpt, bs=args.bs)
    pairs, jobs, per_row = [], [], []
    for ri, r in enumerate(rows):
        blocks = blocks_of(r["input"].get("content") or "")
        per_row.append(blocks)
        hyp = spec_hypothesis(r["extract"][0])  # first spec (1150/1200 docs have exactly one)
        for bi, b in enumerate(blocks):
            jobs.append((ri, bi)); pairs.append((b, hyp))
    print(len(pairs), "pairs", flush=True)
    X, P = sc.latents(pairs)
    d = X.shape[1]
    jobs = np.array(jobs)
    # per-doc structures
    doc_idx = {ri: np.flatnonzero(jobs[:, 0] == ri) for ri in range(len(rows))}
    labels = np.array([int(any(v is not None for v in r["gold"].values())) for r in rows])
    docX = np.stack([np.concatenate([X[doc_idx[ri]].astype(np.float32).max(0), [P[doc_idx[ri]].max()]]) if len(doc_idx[ri]) else np.zeros(d + 1, np.float32) for ri in range(len(rows))])
    gold_blocks = [quote_blocks(r["input"].get("content") or "", list(iter_quotes(r["gold"]))) for r in rows]
    block_y = np.zeros(len(pairs), np.int64)
    for ri in range(len(rows)):
        for j in doc_idx[ri]:
            block_y[j] = int(jobs[j, 1] in gold_blocks[ri])
    rng = np.random.RandomState(0); perm = rng.permutation(len(rows)); folds = np.array_split(perm, args.folds)
    ns = argparse.Namespace(hidden=512, dropout=0.1, lr=1e-3, wd=1e-2, bs=256, epochs=60, patience=8, eps=args.eps, seed=0)
    page_scores = np.zeros(len(rows)); block_scores = np.zeros(len(pairs))
    for f, test_docs in enumerate(folds):
        test_set = set(test_docs.tolist()); train_docs = np.array([i for i in range(len(rows)) if i not in test_set])
        # A) page-level MLP (val = 10% of train docs, grouped by doc id trivially)
        va = train_docs[: len(train_docs) // 10]; tr = train_docs[len(train_docs) // 10:]
        m, st, _, _ = fit(docX[tr], labels[tr], tr, docX[va], labels[va], va, ns)
        page_scores[test_docs] = predict(m, st, docX[test_docs])
        # B) block-level MLP on docs that have evidence
        trb = np.concatenate([doc_idx[i] for i in tr if gold_blocks[i]]); vab = np.concatenate([doc_idx[i] for i in va if gold_blocks[i]])
        teb = np.concatenate([doc_idx[i] for i in test_docs])
        m, st, _, _ = fit(X[trb].astype(np.float32), block_y[trb], jobs[trb, 0], X[vab].astype(np.float32), block_y[vab], jobs[vab, 0], ns)
        block_scores[teb] = predict(m, st, X[teb].astype(np.float32))
        print(f"fold {f} done", flush=True)
    res = {"n_docs": len(rows), "page_relevance": {
        "mlp_auroc": auroc(page_scores, labels), "mlp_best_acc": best_acc(page_scores, labels),
        "zeroshot_auroc": auroc(docX[:, -1], labels), "zeroshot_best_acc": best_acc(docX[:, -1], labels)},
        "evidence_block_recall": {}}
    for k in args.ks:
        rec = {"mlp": [], "zeroshot": [], "lex": [], "mlp_prefix": []}
        for ri, r in enumerate(rows):
            gb = gold_blocks[ri]
            if not gb or not len(doc_idx[ri]):
                continue
            idx = doc_idx[ri]; bis = jobs[idx, 1]
            q = set().union(*(terms(s["description"] + " " + " ".join(dd for _, dd in s.get("fields") or [])) for s in r["extract"]))
            lex = np.array([sum(Counter(WORD_RE.findall(b.lower())).get(w, 0) for w in q) for b in per_row[ri]])
            for name, s in [("mlp", block_scores[idx]), ("zeroshot", P[idx]), ("lex", lex)]:
                top = set(bis[np.argsort(-s, kind="stable")[:k]].tolist()); rec[name].append(len(gb & top) / len(gb))
            pre = set(range(min(4, len(bis)))); order = [b for b in bis[np.argsort(-block_scores[idx], kind="stable")].tolist() if b not in pre]
            rec["mlp_prefix"].append(len(gb & (pre | set(order[:max(0, k - len(pre))]))) / len(gb))
        res["evidence_block_recall"][str(k)] = {n: float(np.mean(v)) for n, v in rec.items()}
    json.dump(res, open(args.out, "w"), indent=2); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
