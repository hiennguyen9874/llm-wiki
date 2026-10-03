#!/usr/bin/env python
"""Merge results/*.json into one markdown table (model x task). Usage: python summarize.py > results/summary.md"""
import glob, json, collections

NAMES = {
    "ckpt/qwen3.5-0.8b-nli": "Qwen3.5-0.8B full FT",
    "ckpt/qwen3.5-2b-nli": "Qwen3.5-2B full FT",
    "ckpt/qwen3.5-4b-nli": "Qwen3.5-4B full FT",
    "ckpt/qwen3.5-2b-nli-headonly": "Qwen3.5-2B head-only",
    "dleemiller/ModernCE-large-nli": "ModernCE-large-nli (ref)",
}
MC = ["gpqa", "mmlu", "arc_easy", "arc_challenge", "winogrande", "chess"]

res = collections.defaultdict(dict)
for f in sorted(glob.glob("results/*.json")):
    if "train_" in f or "smoke" in f or "fewshot" in f:  # few-shot runs use an MMLU subsample; see README
        continue
    for m, r in json.load(open(f)).items():
        res[m].update(r)

order = [m for m in NAMES if m in res] + [m for m in res if m not in NAMES]
f3 = lambda x: f"{x:.3f}"

print("### NLI sanity (accuracy)\n")
print("| model | MNLI-m | MNLI-mm |\n|---|---|---|")
for m in order:
    mn = res[m].get("mnli")
    if mn:
        print(f"| {NAMES.get(m, m)} | {f3(mn['validation_matched']['acc'])} | {f3(mn['validation_mismatched']['acc'])} |")

print("\n### Multiple choice, rerank without reference (blog #3): premise = question, pick argmax P(entailment)\n")
print("| model | " + " | ".join(MC) + " |\n|---|" + "---|" * len(MC))
rb = {t: next((res[m][t]["random_baseline"] for m in order if t in res[m] and "random_baseline" in res[m][t]), None) for t in MC}
print("| random | " + " | ".join(f3(rb[t]) if rb[t] is not None else "-" for t in MC) + " |")
for m in order:
    print(f"| {NAMES.get(m, m)} | " + " | ".join(f3(res[m][t]["rerank_acc"]) if t in res[m] else "-" for t in MC) + " |")

print("\n### Multiple choice, grading with reference (blog #6): premise = question + gold, entailment <=> option is gold (acc / F1)\n")
print("| model | " + " | ".join(MC) + " |\n|---|" + "---|" * len(MC))
for m in order:
    print(f"| {NAMES.get(m, m)} | " + " | ".join(f"{f3(res[m][t]['grade_acc'])} / {f3(res[m][t]['grade_f1'])}" if t in res[m] else "-" for t in MC) + " |")

print("\n### GSM8K (200 test questions, candidates from Qwen3.5-4B: greedy + 4 samples)\n")
print("| model | greedy | pass@1 | maj@4 | NLI rerank@4 | oracle@4 | grade acc / F1 |\n|---|---|---|---|---|---|---|")
for m in order:
    g = res[m].get("gsm8k")
    if g:
        print(f"| {NAMES.get(m, m)} | {f3(g['greedy_acc'])} | {f3(g['sample_pass1'])} | {f3(g['maj@4'])} | {f3(g['nli_rerank@4'])} | {f3(g['oracle@4'])} | {f3(g['grade_acc'])} / {f3(g['grade_f1'])} |")
