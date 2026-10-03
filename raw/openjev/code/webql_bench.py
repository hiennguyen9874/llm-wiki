#!/usr/bin/env python
"""openjev (zero-shot NLI cross-encoder) on the keenable-webql sem_extract benchmark, for the two places where a
Gemini-Flash-lite call (or a lexical heuristic) decides something before extraction:

A) page relevance (SEM_MATCH-style): does this document state the requested field(s) at all?
   Truth: gold is all-null (291 of 1200) vs has values. openjev score = max over 500-char blocks of P(entailment |
   block, "The document states <spec>"). Compared with the lexical term-overlap score (find_best_fragment's scorer)
   and with the Gemini run's own null decision from benchmarks/results.
B) paragraph selection (find_best_fragment-style): rank the 500-char blocks and check whether the blocks holding
   the gold verbatim evidence quotes are in the top-k. openjev ranking vs lexical ranking vs the blocks Gemini's
   returned evidence quotes fall into.

    python webql_bench.py --ckpt ckpt/qwen3.5-4b-nli --data data/sem_extract_bench.jsonl --gemini data/sem_extract_bench_gemini-3.5-flash-lite.jsonl --out results/webql_bench.json
"""
import argparse
import json
import math
import re
from collections import Counter

import numpy as np
import torch

BLOCK = 500
WORD_RE = re.compile(r"\w{2,}", re.UNICODE)
STOP = set("the a an of in on for to and or with by from at as is are was were be this that these those which who what "
           "when where how any all each per its it their his her list value values number name names date year".split())


def terms(s):
    out = set()
    for w in WORD_RE.findall(s.lower()):
        out.add(w)
        if "_" in w:
            out.update(p for p in w.split("_") if len(p) >= 2)
    return out - STOP


def iter_quotes(v):
    if isinstance(v, dict):
        for k, x in v.items():
            if k == "evidence" or k.endswith("_evidence"):
                if isinstance(x, list):
                    yield from (q for q in x if isinstance(q, str) and q)
            else:
                yield from iter_quotes(x)
    elif isinstance(v, list):
        for x in v:
            yield from iter_quotes(x)


def spec_hypothesis(spec):
    d = spec["description"].strip()
    if spec.get("fields"):
        fields = "; ".join(f"{n}: {desc}" for n, desc in spec["fields"])
        return f"The document states {d} with {fields}."
    return f"The document states {d}."


def blocks_of(content):
    return [content[i:i + BLOCK] for i in range(0, len(content), BLOCK)]


def quote_blocks(content, quotes):
    hit = set()
    for q in quotes:
        start = content.find(q)
        if start < 0:
            continue
        for b in range(start // BLOCK, (start + len(q) - 1) // BLOCK + 1):
            hit.add(b)
    return hit


def auroc(scores, labels):
    s, y = np.asarray(scores, float), np.asarray(labels, int)
    if y.sum() == 0 or (1 - y).sum() == 0:
        return float("nan")
    order = np.argsort(s)
    ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    # average ranks for ties
    for v in np.unique(s):
        m = s == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    return float((ranks[y == 1].sum() - y.sum() * (y.sum() + 1) / 2) / (y.sum() * (1 - y).sum()))


def best_acc(scores, labels):
    s, y = np.asarray(scores, float), np.asarray(labels, int)
    best = 0.0
    for t in np.unique(s):
        best = max(best, float(((s >= t).astype(int) == y).mean()))
    return best


class Scorer:
    def __init__(self, ckpt, bs=48, max_len=512):
        from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(ckpt); self.tok.padding_side = "right"
        cls = AutoModelForSequenceClassification
        if getattr(AutoConfig.from_pretrained(ckpt), "model_type", "") == "qwen3_5_moe":
            from modeling_qwen35_moe_seqcls import Qwen3_5MoeForSequenceClassification as cls
        self.model = cls.from_pretrained(ckpt, dtype=torch.bfloat16).cuda().eval()
        self.model.config.get_text_config().pad_token_id = self.tok.pad_token_id
        self.template = self.model.config.nli_template
        self.bs, self.max_len = bs, max_len

    @torch.no_grad()
    def p_entail(self, pairs):
        out = []
        for i in range(0, len(pairs), self.bs):
            chunk = pairs[i:i + self.bs]
            texts = [self.template.format(premise=p, hypothesis=h) for p, h in chunk]
            enc = self.tok(texts, truncation=True, max_length=self.max_len, padding=True, return_tensors="pt").to("cuda")
            logits = self.model(**enc).logits.float()
            out.append(torch.softmax(logits, -1)[:, 1].cpu().numpy())
        return np.concatenate(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="ckpt/qwen3.5-4b-nli")
    ap.add_argument("--data", default="data/sem_extract_bench.jsonl")
    ap.add_argument("--gemini", default=None, help="benchmarks/results/sem_extract_bench_gemini-3.5-flash-lite.jsonl")
    ap.add_argument("--out", default="results/webql_bench.json")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ks", nargs="+", type=int, default=[4, 8, 12, 24])
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data)]
    if args.limit:
        rows = rows[:args.limit]
    gem = {}
    if args.gemini:
        for l in open(args.gemini):
            r = json.loads(l)
            gem[r.get("id")] = r
    scorer = Scorer(args.ckpt)

    # ------------------------------------------------------------------ build all (block, hypothesis) pairs
    jobs = []  # (row_idx, spec_idx, block_idx)
    pairs = []
    per_row = []
    for ri, r in enumerate(rows):
        content = r["input"].get("content") or ""
        blocks = blocks_of(content)
        per_row.append(blocks)
        for si, spec in enumerate(r["extract"]):
            hyp = spec_hypothesis(spec)
            for bi, b in enumerate(blocks):
                jobs.append((ri, si, bi)); pairs.append((b, hyp))
    print(f"{len(rows)} docs, {len(pairs)} (block, hypothesis) pairs", flush=True)
    p = scorer.p_entail(pairs)
    nli = {}
    for (ri, si, bi), v in zip(jobs, p):
        nli.setdefault((ri, si), {})[bi] = float(v)

    # ------------------------------------------------------------------ A) page relevance
    A = {"nli": [], "lex": [], "label": [], "gem_pred_nonnull": [], "gem_ok": []}
    # ------------------------------------------------------------------ B) evidence block recall
    B = {k: {"nli": [], "lex": [], "nli_prefix": [], "lex_prefix": []} for k in args.ks}
    gem_recall, n_gem_docs = [], 0
    for ri, r in enumerate(rows):
        content = r["input"].get("content") or ""
        blocks = per_row[ri]
        if not blocks:
            continue
        gold_nonnull = any(v is not None for v in r["gold"].values())
        doc_nli = max(max(nli[(ri, si)].values()) for si in range(len(r["extract"])))
        q = set().union(*(terms(spec["description"] + " " + " ".join(d for _, d in spec.get("fields") or [])) for spec in r["extract"]))
        lex_scores = [sum(Counter(WORD_RE.findall(b.lower())).get(w, 0) for w in q) for b in blocks]
        A["nli"].append(doc_nli); A["lex"].append(max(lex_scores)); A["label"].append(int(gold_nonnull))
        g = gem.get(r["id"])
        if g is not None:
            outputs = g.get("outputs") or g.get("output") or {}
            pred_nonnull = any(v is not None for k, v in outputs.items() if not (k == "evidence" or k.endswith("_evidence"))) if isinstance(outputs, dict) else False
            A["gem_pred_nonnull"].append(int(pred_nonnull)); A["gem_ok"].append(int(pred_nonnull == gold_nonnull))
        # evidence blocks
        gold_blocks = quote_blocks(content, list(iter_quotes(r["gold"])))
        if gold_blocks:
            nb = len(blocks)
            nli_rank = np.argsort([-max(nli[(ri, si)][bi] for si in range(len(r["extract"]))) for bi in range(nb)], kind="stable")
            lex_rank = np.argsort([-s for s in lex_scores], kind="stable")
            prefix = list(range(min(4, nb)))  # find_best_fragment always keeps the first 2000 chars
            for k in args.ks:
                for name, rank in [("nli", nli_rank), ("lex", lex_rank)]:
                    top = set(rank[:k].tolist())
                    B[k][name].append(len(gold_blocks & top) / len(gold_blocks))
                    topp = set(prefix) | set([i for i in rank.tolist() if i not in prefix][:max(0, k - len(prefix))])
                    B[k][name + "_prefix"].append(len(gold_blocks & topp) / len(gold_blocks))
            if g is not None:
                gq = list(iter_quotes(g.get("outputs") or g.get("output") or {}))
                gb = quote_blocks(content, gq)
                gem_recall.append(len(gold_blocks & gb) / len(gold_blocks)); n_gem_docs += 1

    res = {"n_docs": len(A["label"]), "n_pairs": len(pairs), "n_all_null": int(len(A["label"]) - sum(A["label"])),
           "page_relevance": {
               "openjev_auroc": auroc(A["nli"], A["label"]), "openjev_best_acc": best_acc(A["nli"], A["label"]),
               "lexical_auroc": auroc(A["lex"], A["label"]), "lexical_best_acc": best_acc(A["lex"], A["label"]),
               "majority_acc": float(max(np.mean(A["label"]), 1 - np.mean(A["label"]))),
               "gemini_nonnull_acc": float(np.mean(A["gem_ok"])) if A["gem_ok"] else None,
               "gemini_n": len(A["gem_ok"])},
           "evidence_block_recall": {str(k): {n: float(np.mean(v)) for n, v in B[k].items()} for k in args.ks},
           "evidence_docs": len(B[args.ks[0]]["nli"]),
           "gemini_evidence_recall": float(np.mean(gem_recall)) if gem_recall else None,
           "avg_blocks_per_doc": float(np.mean([len(b) for b in per_row]))}
    json.dump(res, open(args.out, "w"), indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
