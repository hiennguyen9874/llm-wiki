#!/usr/bin/env python
"""Keenable WebQL null detection (benchmarks/sem_extract_null_detection.py) with a jev NLI cross-encoder.

Binary task on the 1,200 sem_extract_bench pages: does the page state at least one of the requested values?
Gold "no data" = the 291 all-null examples. The request is rebuilt exactly as keenable-webql builds it for Jev:

  * field instructions from `_spec_instruction` (SEM_EXTRACT / SEM_EXTRACT_ALL wording, evidence clauses included);
  * the `jev_prefilter` question/true/false texts, includes_match=False;
  * content truncated to 70,000 chars, then windowed with 2,000-char overlap, max probability over windows.
    Jev windows at 35,000 chars; ours defaults to 24,000 (--window-chars) so a window fits the 8k-token encoder
    without silent truncation. Same pages, same gold, same question — only the window size differs.

Two framings (--hyp):
  claim (default) one plain claim per spec, "The document states <description> with <fields>." — the phrasing the
        openjev WebQL runs used; p_has_data = P(entailment), max over specs and windows.
  jev   Jev's own true/false criteria as the two hypotheses, with the field instructions appended;
        p_has_data = P(ent | true) / (P(ent | true) + P(ent | false)). Closer to the Jev wire format, but the text
        is an instruction rather than a statement, which a cross-encoder reads badly.

    python webql_null.py --models ckpt/qwen3.5-0.8b-nli-v2s-jev --data data/sem_extract_bench.jsonl \
        --jev data/sem_extract_null_detection_jev-latest.jsonl --out results/v2s/webql_null.json
"""
import argparse
import json
import os
import time

import numpy as np

from eval import ENT, NLIScorer

TRUNCATE = 70_000
WINDOW, OVERLAP = 24_000, 2_000
QUOTE_SPAN = "the full sentence or complete table line around the supporting phrase"
CONTEXT_QUOTES = ("plus, as separate verbatim quotes, the page-level context: the table's header"
                  " row or caption when the supporting quote is a table row, and the page title,"
                  " section heading, or introductory sentence stating what the page or table is"
                  " about")
EVIDENCE_QUOTES = ("a list of one or more supporting quotes, each copied verbatim,"
                   " character for character, from the '{column}' text, spanning " + QUOTE_SPAN + ", " + CONTEXT_QUOTES)
EVIDENCE_INSTRUCTION = "'evidence' — " + EVIDENCE_QUOTES
# The Jev question ("Does the document state at least one of the requested values...") is not a statement, so it
# cannot be a hypothesis; its two criteria are, and the field list rides along with each of them.
TRUE = "The document explicitly states at least one requested value for the described entity."
FALSE = ("The document does not contain the requested data: the values are absent, the description does not apply"
         " to this document, or only unrelated data is present.")


def field_keys(spec):
    return "; ".join(f"'{name}': {description}" for name, description in spec["fields"])


def fields_evidence_clause(spec, subject):
    col = spec["column"]
    if spec.get("evidence") == "per_field":
        return (f"; {subject} also carries one '<field>_evidence' key per non-null field, placed right after the"
                f" field it supports and supporting that field's value alone — {EVIDENCE_QUOTES.format(column=col)}")
    if spec.get("evidence"):
        return f"; {subject} ends with {EVIDENCE_INSTRUCTION.format(column=col)}"
    return ""


def spec_instruction(spec, key):
    """keenable_webql.operators.sem_extract._spec_instruction, rebuilt from the dataset's parsed `extract` block."""
    col, desc = spec["column"], spec["description"]
    if spec["func"] == "SEM_EXTRACT_ALL":
        if spec["fields"]:
            return (f"- {key}: an array with one object per {desc} (from the '{col}' field), each with keys"
                    f" {field_keys(spec)}; cover every distinct one the text states, null when it states none"
                    + fields_evidence_clause(spec, "each object"))
        out = f"- {key}: an array of values — every distinct {desc} the '{col}' text states; null when it states none"
        if spec.get("evidence"):
            out += f"; each array item is an object with 'value', then {EVIDENCE_INSTRUCTION.format(column=col)}"
        return out
    if spec["fields"]:
        scope, null_when = "", "the text states none of them"
        if desc:
            scope = f"; object description: {desc}"
            null_when += " or the description does not apply"
        return (f"- {key}: an object with keys {field_keys(spec)} (from the '{col}' field){scope};"
                f" null when {null_when}" + fields_evidence_clause(spec, "the object"))
    out = f"- {key}: {desc} (from the '{col}' field)"
    if spec.get("evidence"):
        out += f"; return an object with 'value', then {EVIDENCE_INSTRUCTION.format(column=col)}"
    return out


def is_evidence_key(k):
    return k == "evidence" or k.endswith("_evidence")


def value_units(value):
    if value is None:
        return 0
    if isinstance(value, dict):
        return sum(value_units(v) for k, v in value.items() if not is_evidence_key(k))
    if isinstance(value, list):
        return sum(value_units(v) for v in value)
    return 1


def windows(text, size=WINDOW):
    if len(text) <= size:
        return [text]
    step = size - OVERLAP
    return [text[s:s + size] for s in range(0, max(len(text) - OVERLAP, 1), step)]


def spec_claim(spec):
    """Plain statement form of a spec (openjev's webql_bench.spec_hypothesis)."""
    d = spec["description"].strip()
    if spec.get("fields"):
        fields = "; ".join(f"{n}: {desc}" for n, desc in spec["fields"])
        return f"The document states {d} with {fields}."
    return f"The document states {d}."


def build(record, window=WINDOW, hyp="claim"):
    """(premise windows, [hypothesis]) — the Jev criteria pair, or one plain claim per spec."""
    keys = [k for k in record["gold"] if not is_evidence_key(k)]
    specs = record["extract"]
    instr = "\n".join(spec_instruction(s, keys[i] if i < len(keys) else f"field{i}") for i, s in enumerate(specs))
    hyps = [spec_claim(s) for s in specs] if hyp == "claim" else [
        f"{TRUE}\nRequested fields:\n{instr}", f"{FALSE}\nRequested fields:\n{instr}"]
    cols = sorted({s["column"] for s in specs})
    state = {c: record["input"].get(c) for c in cols}
    state = {k: (v[:TRUNCATE] if isinstance(v, str) and len(v) > TRUNCATE else v) for k, v in state.items()}
    main = max((k for k, v in state.items() if isinstance(v, str)), key=lambda k: len(state[k]), default=None)
    head = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)[:2000]}" for k, v in state.items() if k != main)
    body = state.get(main) or ""
    return [f"{head}\n{main}:\n{w}".strip() for w in windows(body, window)], hyps


def metrics(gold_has_data, p, thr):
    pred = np.asarray(p) >= thr
    g = np.asarray(gold_has_data, dtype=bool)
    tp, tn = int((g & pred).sum()), int((~g & ~pred).sum())
    fp, fn = int((~g & pred).sum()), int((g & ~pred).sum())
    r = lambda a, b: round(a / b, 4) if b else None  # noqa: E731
    return {"accuracy": r(tp + tn, len(g)), "null_recall": r(tn, tn + fp), "null_precision": r(tn, tn + fn),
            "null_f1": r(2 * tn, 2 * tn + fn + fp), "data_recall": r(tp, tp + fn),
            "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn}}


def report(gold, p):
    from sklearn.metrics import roc_auc_score
    thrs = [round(t, 2) for t in np.arange(0.05, 1.0, 0.05)]
    at = {str(t): metrics(gold, p, t) for t in thrs}
    best = max(thrs, key=lambda t: at[str(t)]["null_f1"] or 0)
    return {"n": len(gold), "roc_auc": round(float(roc_auc_score(gold, p)), 4),
            "at_0.3": metrics(gold, p, 0.3), "at_0.5": metrics(gold, p, 0.5),
            "best_threshold": best, "at_best": at[str(best)], "sweep": at}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--data", default="data/sem_extract_bench.jsonl")
    ap.add_argument("--jev", default=None, help="jev-latest run jsonl, re-scored here for reference")
    ap.add_argument("--out", required=True)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--max-len", type=int, default=8192)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--window-chars", type=int, default=WINDOW)
    ap.add_argument("--hyp", choices=["claim", "jev"], default="claim")
    args = ap.parse_args()

    records = [json.loads(l) for l in open(args.data) if l.strip()]
    if args.limit:
        records = records[: args.limit]
    gold = [value_units(r["gold"]) > 0 for r in records]
    prepared = [build(r, args.window_chars, args.hyp) for r in records]
    print(f"{len(records)} pages, {sum(len(w) for w, _ in prepared)} windows, {sum(gold)} with data", flush=True)

    res = json.load(open(args.out)) if os.path.exists(args.out) else {}
    if args.jev:
        by_id = {json.loads(l)["id"]: json.loads(l) for l in open(args.jev) if l.strip()}
        rows = [(g, by_id[r["id"]]["p_has_data"]) for r, g in zip(records, gold) if r["id"] in by_id]
        res["jev-1.13.0 (reference run)"] = report([g for g, _ in rows], [p for _, p in rows])

    for m in args.models:
        scorer = NLIScorer(m, bs=args.bs, max_len=args.max_len)
        pairs, owner = [], []
        for i, (wins, hyps) in enumerate(prepared):
            for w in wins:
                for h in hyps:
                    pairs.append((w, h)); owner.append(i)
        t0 = time.perf_counter()
        pe = scorer.predict(pairs)[:, ENT]
        wall = time.perf_counter() - t0
        p = np.zeros(len(records))
        if args.hyp == "jev":  # pairs come in (true, false) order per window
            for (i, t), f in zip(list(zip(owner, pe))[::2], pe[1::2]):
                p[i] = max(p[i], t / max(t + f, 1e-9))
        else:
            for i, v in zip(owner, pe):
                p[i] = max(p[i], v)
        res[m] = report(gold, p)
        res[m]["wall_s"] = round(wall, 1)
        res[m]["pages_per_s"] = round(len(records) / wall, 2)
        res[m]["p_has_data"] = {r["id"]: float(x) for r, x in zip(records, p)}
        print(m, json.dumps({k: v for k, v in res[m].items() if k not in ("sweep", "p_has_data")})[:600], flush=True)
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        json.dump(res, open(args.out, "w"), indent=2)
        del scorer
        import torch
        torch.cuda.empty_cache()

    print("\n| system | ROC AUC | acc@best | null F1@best | data recall | thr |\n|---|---|---|---|---|---|")
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["roc_auc"]):
        b = v["at_best"]
        print(f"| {k} | {v['roc_auc']} | {b['accuracy']} | {b['null_f1']} | {b['data_recall']} | {v['best_threshold']} |")


if __name__ == "__main__":
    main()
