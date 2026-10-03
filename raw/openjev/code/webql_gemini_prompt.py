#!/usr/bin/env python
"""Page relevance on the keenable bench with EXACTLY Gemini's input: the rendered sem_extract.jinja prompt (instructions built with
the operator's spec_instruction/_list_instruction, output JSON schema, the input row as JSON with content cut at 70k chars, schema
reminder, rules) is the premise; one hypothesis per spec ("<key> is not null: the document states it"); doc score = max over specs.
Zero-shot P(entailment) and a 5-fold-CV MLP on the latent. Ported from keenable_webql/operators/sem_extract.py + prompts/sem_extract.jinja.
    python webql_gemini_prompt.py --ckpt /mnt/qwen_nli_ckpt/qwen3.5-35b-a3b-nli --out results/webql_geminiprompt_35b.json
"""
import argparse, json
from datetime import date
import numpy as np, torch
from webql_bench import auroc, best_acc
from webql_mlp import LatScorer
from latent_mlp import fit, predict

QUOTE_SPAN = "the full sentence or complete table line around the supporting phrase"
CONTEXT_QUOTES = ("plus, as separate verbatim quotes, the page-level context: the table's header row or caption when the supporting quote is a "
                  "table row, and the page title, section heading, or introductory sentence stating what the page or table is about")
EVIDENCE_QUOTES = ("a list of one or more supporting quotes, each copied verbatim, character for character, from the '{column}' text, spanning "
                   + QUOTE_SPAN + ", " + CONTEXT_QUOTES)
EVIDENCE_INSTRUCTION = "'evidence' — " + EVIDENCE_QUOTES
PER_FIELD = "per_field"


def ev_prop(spec, subject, absent):
    return {"type": ["array", "null"], "items": {"type": "string"},
            "description": f"one or more quotes copied verbatim from the '{spec['column']}' text that support {subject}, each spanning {QUOTE_SPAN}, {CONTEXT_QUOTES}; null when {absent}"}


def obj_props(spec):
    p = {}
    for name, desc in spec["fields"]:
        p[name] = {"type": ["string", "number", "boolean", "null"], "description": desc}
        if spec["evidence"] == PER_FIELD:
            p[f"{name}_evidence"] = ev_prop(spec, f"this object's '{name}' value", f"'{name}' is null")
    if spec["evidence"] and spec["evidence"] != PER_FIELD:
        p["evidence"] = ev_prop(spec, "this object's values", "the object's values are all null")
    return p


def spec_prop(spec):
    d = spec["description"]
    if spec["func"] == "SEM_EXTRACT_ALL":
        if spec["fields"]:
            item = {"type": "object", "properties": obj_props(spec)}
        else:
            item = {"type": ["string", "number", "boolean"], "description": d}
            if spec["evidence"]:
                item = {"type": "object", "properties": {"value": item, "evidence": ev_prop(spec, "this value", "this value is null")}}
        return {"type": ["array", "null"], "description": f"every distinct {d} the text states; null when it states none", "items": item}
    if spec["fields"]:
        null_when = "null when the text states none of these fields"
        if d:
            null_when = f"{d}; {null_when} or the description does not apply"
        return {"type": ["object", "null"], "description": null_when, "properties": obj_props(spec)}
    vp = {"type": ["string", "number", "boolean", "null"], "description": d}
    if not spec["evidence"]:
        return vp
    return {"type": "object", "properties": {"value": vp, "evidence": ev_prop(spec, "the value", "the value is null")}}


def field_keys(spec):
    return "; ".join(f"'{n}': {d}" for n, d in spec["fields"])


def fields_ev_clause(spec, subject):
    if spec["evidence"] == PER_FIELD:
        return (f"; {subject} also carries one '<field>_evidence' key per non-null field, placed right after the field it supports and supporting"
                f" that field's value alone — {EVIDENCE_QUOTES.format(column=spec['column'])}")
    if spec["evidence"]:
        return f"; {subject} ends with {EVIDENCE_INSTRUCTION.format(column=spec['column'])}"
    return ""


def spec_instr(spec, key):
    col, d = spec["column"], spec["description"]
    if spec["func"] == "SEM_EXTRACT_ALL":
        if spec["fields"]:
            return (f"- {key}: an array with one object per {d} (from the '{col}' field), each with keys {field_keys(spec)};"
                    " cover every distinct one the text states, null when it states none" + fields_ev_clause(spec, "each object"))
        s = f"- {key}: an array of values — every distinct {d} the '{col}' text states; null when it states none"
        if spec["evidence"]:
            s += f"; each array item is an object with 'value', then {EVIDENCE_INSTRUCTION.format(column=col)}"
        return s
    if spec["fields"]:
        scope, null_when = "", "the text states none of them"
        if d:
            scope = f"; object description: {d}"; null_when += " or the description does not apply"
        return f"- {key}: an object with keys {field_keys(spec)} (from the '{col}' field){scope}; null when {null_when}" + fields_ev_clause(spec, "the object")
    s = f"- {key}: {d} (from the '{col}' field)"
    if spec["evidence"]:
        s += f"; return an object with 'value', then {EVIDENCE_INSTRUCTION.format(column=col)}"
    return s


RULES = """Process the input document above. Extract the requested fields, matching the output schema. Return a single JSON object.

Rules:
1. CRITICAL: Extract values ONLY from the INPUT DOCUMENT above. Never fill in a value from your own knowledge or memory — if the document does not state it, the value is null, even when you know or could guess the real-world answer.
2. When a field requests an array, include one entry for every distinct value or entity the document states — never merge distinct entities or add entries the document does not state. Use null for the whole array when the document states none, never an empty array.
3. When the document does not give a field's value, omit the key or use null — never placeholders like "Unknown", "N/A", or "None".
4. When extracting names of entities (products, companies, people, places), use their most common canonical name, and keep a qualifier that tells the entity apart from a sibling — a model, edition, version, year, region, or size. Drop only packaging and listing noise (pack sizes, seller suffixes) that names the same entity. A naming format stated in the schema description wins.
5. IMPORTANT: Follow the format requirements in the schema descriptions exactly — each row is processed independently, so consistent formatting depends on it. Never wrap string values in extra quotes.
6. A field's value must come from text about the exact entity, model, region, and period the field names. When the document states values only for similar entities (another model code, another year, another region), the value is null. A sentence that names the entity and the value together ("Google DeepMind principal researcher Pei Sun", "Zoph joined Google DeepMind as VP of research") states that value for that entity. For an array entry, fill every field from each sentence that names the same entity, including the sentence its name came from.
7. When the value sits in a table whose columns are years or periods, match the cell to the exact column header requested; re-check the header before answering."""
RULES_EV = """
8. When a field requests 'evidence' — or any key ending in '_evidence' — return a list of supporting quotes copied verbatim from the INPUT DOCUMENT — never paraphrase, translate, or fix typos. Quote the full sentence or complete table line, plus a neighbouring sentence when it adds context — not just the bare phrase. A quote that is not in the document word for word is discarded.
9. An evidence list must stand alone: the reader sees only the quotes, not the document. Add separate verbatim context quotes: the page title, and the nearest section heading or introductory sentence when it states what the page or table is about; a quote that names the entity when the supporting sentence uses only a pronoun or generic reference ("it", "the Company"); the table's header row or caption when a supporting quote is a table row, so values keep their column meaning.
10. When a requested field is a date, or the value holds only for a stated time period, include the sentence carrying that date exactly as printed.
11. When the requested field concerns ordering or recency ("latest", "most recent", "newest", "first", "top"), the quotes must include the marker that proves the position — the section heading (e.g. "Latest papers"), the sort label, or a neighbouring dated entry, each as its own short verbatim quote. The target entry alone proves nothing about its order."""


def render(record, limit=70000, today=None):
    specs, keys = record["extract"], list(record["gold"].keys())  # gold keys == llm output keys, same order
    schema = {"type": "object", "properties": {k: spec_prop(s) for k, s in zip(keys, specs)}}
    schema_str = json.dumps(schema, indent=2)
    instr = "Extract the following fields:\n" + "\n".join(spec_instr(s, k) for k, s in zip(keys, specs))
    cols = sorted({s["column"] for s in specs} | {"url", "title", "published_at", "query"})
    row = {c: record["input"].get(c) for c in cols}
    row = {k: (v[:limit] if isinstance(v, str) and len(v) > limit else v) for k, v in row.items()}
    ev = any(s["evidence"] for s in specs)
    return (f"Today is {today or date.today().isoformat()}.\n\n### INSTRUCTIONS\n{instr}\n\n### OUTPUT SCHEMA\n{schema_str}\n\n### INPUT DOCUMENT\n"
            f"{json.dumps(row, ensure_ascii=False)}\n\n### OUTPUT SCHEMA (reminder)\n{schema_str}\n\n{RULES}{RULES_EV if ev else ''}"), keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True); ap.add_argument("--data", default="data/sem_extract_bench.jsonl"); ap.add_argument("--out", required=True)
    ap.add_argument("--max-len", type=int, default=32768); ap.add_argument("--bs", type=int, default=1); ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--eps", type=float, default=0.1); ap.add_argument("--today", default="2026-09-17")
    args = ap.parse_args()
    rows = [json.loads(l) for l in open(args.data)]
    sc = LatScorer(args.ckpt, bs=args.bs, max_len=args.max_len); sc.tok.truncation_side = "left"
    pairs, jobs = [], []
    for ri, r in enumerate(rows):
        prem, keys = render(r, today=args.today)
        for k in keys:
            pairs.append((prem, f"The output for '{k}' is not null: the input document states it.")); jobs.append(ri)
    jobs = np.array(jobs)
    lens = [len(sc.tok(sc.template.format(premise=p, hypothesis=h))["input_ids"]) for p, h in pairs[:100]]
    print(f"{len(pairs)} pairs; prompt tokens (first 100): median {int(np.median(lens))} p90 {int(np.percentile(lens, 90))} max {max(lens)}", flush=True)
    X, P = sc.latents(pairs); X = X.astype(np.float32)
    labels = np.array([int(any(v is not None for v in r["gold"].values())) for r in rows])
    doc_idx = {ri: np.flatnonzero(jobs == ri) for ri in range(len(rows))}
    zs = np.array([P[doc_idx[ri]].max() for ri in range(len(rows))])
    docX = np.stack([np.concatenate([X[doc_idx[ri]].max(0), [zs[ri]]]) for ri in range(len(rows))])
    rng = np.random.RandomState(0); folds = np.array_split(rng.permutation(len(rows)), args.folds)
    ns = argparse.Namespace(hidden=512, dropout=0.1, lr=1e-3, wd=1e-2, bs=128, epochs=60, patience=8, eps=args.eps, seed=0)
    scores = np.zeros(len(rows))
    for te in folds:
        tr_all = np.array([i for i in range(len(rows)) if i not in set(te.tolist())]); va, tr = tr_all[: len(tr_all) // 10], tr_all[len(tr_all) // 10:]
        m, st, _, _ = fit(docX[tr], labels[tr], tr, docX[va], labels[va], va, ns); scores[te] = predict(m, st, docX[te])
    res = {"n_docs": len(rows), "prompt": "sem_extract.jinja render (Gemini input)", "max_len_tokens": args.max_len,
           "zeroshot_auroc": auroc(zs, labels), "zeroshot_best_acc": best_acc(zs, labels), "mlp_auroc": auroc(scores, labels), "mlp_best_acc": best_acc(scores, labels)}
    json.dump(res, open(args.out, "w"), indent=2); print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
