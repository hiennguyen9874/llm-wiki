---
type: Concept
title: UltraRAG benchmarking and evaluation
description: Dataset loading and alignment, answer-quality metrics, retrieval evaluation, and reproducibility limits.
tags: [ml, ultrarag, evaluation, benchmarks]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f134099405b8b483edbbad95274080
    title: UltraRAG repository
---

**Observed:** UltraRAG separates benchmark ingestion from evaluation. The benchmark server produces aligned question/answer fields for a pipeline; the evaluation server computes answer metrics or TREC-style retrieval metrics. This supports controlled comparisons, but the existence of standardized tools is not evidence of reproduced benchmark scores.[^ultrarag]

## Dataset loading and alignment

`benchmark.get_data` accepts JSONL, JSON, and Parquet, with a configurable `key_map`, shuffle flag, seed, and limit. Committed defaults include `shuffle: false`, seed `42`, and limit `-1`; zero is rejected. Rows missing any mapped key are dropped together, so questions, reference answers, and other mapped fields stay aligned when selecting/shuffling records. A regression test specifically addresses key-map alignment. Sample NQ data carries `id`, `question`, `golden_answers`, and metadata fields; it is a small example, not benchmark-wide coverage.[^ultrarag]

## Metrics and pipeline wiring

The committed answer-metric list includes `acc`, `f1`, `em`, `coverem`, `stringem`, and ROUGE-1/2/L. These are repository-defined metric identifiers; do not infer identical normalization or scoring conventions to another benchmark from a shared metric name. The shared normalizer handles booleans, underscores, case, punctuation, and articles. `acc` is substring containment. Binary match metrics accept any matching reference, while F1 and ROUGE take maxima over references; **`stringem` instead returns the fraction of gold answers that match**, not a maximum. `evaluate` zips predictions with references without enforcing equal length, so mismatches silently truncate. `evaluate_trec` and `evaluate_trec_pvalue` use retrieval-evaluation machinery, including a permutation-test path. Evaluation dependencies are an optional extra. The p-value path uses a two-sided sign-flip permutation procedure with `10000` default resamples and unseeded `random.getrandbits`; repeated runs are not guaranteed identical. It reports significance using `p < 0.05`.[^ultrarag]

Pipeline remapping matters: examples map the evaluator's `pred_ls` input to another answer variable such as `ans_ls`. A successfully generated answer is not automatically the field being evaluated. Inspect the generated I/O and chosen normalization before comparing methods.[^ultrarag]

## Reproducibility and interpretation

- **Observed:** tests exist for normalization and benchmark alignment; their source was inspected, not executed.
- **Reported:** the README describes standardized evaluation and baseline reproduction as framework benefits. This ingestion did not independently reproduce those benefits.
- **Observed:** `docs/architecture.png` contains an illustrative Vanilla LLM versus Vanilla RAG chart for HotPotQA, 2Wiki, MuSiQue, and Bamboogle. Its image alone supplies no model, split, metric definition, variance, or run protocol; chart values are therefore not compiled as benchmark results.
- **Synthesis:** reproducible comparisons require pinned data/model snapshots, matching field maps and prompt/output extraction, and explicit treatment of non-demo `<error>` sentinels versus demo streaming error text/partial answers, in addition to a fixed code revision.[^ultrarag]

No benchmark dataset beyond bundled samples was downloaded, no metrics were executed, and no statistical result was independently checked.[^ultrarag]

## Relationships

- **Depends on:** [generation output semantics](ultrarag-generation.md), especially error handling.
- **Uses:** [pipeline remapping](ultrarag-pipelines.md) to bind predictions and references.
- **Uses:** [research workflow examples](ultrarag-research-workflows.md) as comparison configurations, not verified result artifacts.

[^ultrarag]: Revision `185e2032d9f134099405b8b483edbbad95274080`: `servers/benchmark/src/benchmark.py::get_data`; `servers/benchmark/parameter.yaml`; `data/sample_nq_10.jsonl` field schema; `servers/evaluation/src/evaluation.py::normalize_text`, `compute_metrics`, `evaluate`, `evaluate_trec`, `evaluate_trec_pvalue`; `servers/evaluation/parameter.yaml` metric list; `tests/servers/benchmark/test_key_map_alignment.py`; `tests/servers/evaluation/test_normalize_text.py`; `examples/experiments/{evaluate_results,eval_trec,eval_trec_pvalue,rag_loop}.yaml`; `pyproject.toml` evaluation extra; `README.md` Key Highlights; `docs/architecture.png` right-hand Experimental Results panel (visually inspected, protocol unavailable).
