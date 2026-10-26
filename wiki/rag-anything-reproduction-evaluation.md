---
type: Concept
title: RAG-Anything reproduction and evaluation
description: The repository's indexing, querying, and LLM-judge scripts require external data and schema reconciliation before reproducible evaluation.
tags: [ml, rag, evaluation, reproducibility]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:43:55Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb352b90d40a9884a5ad235d98ac72e
    title: RAG-Anything repository
---

**Observed:** `reproduce/` contains separate indexing, query, and LLM-judge scripts rather than a fully connected experiment runner. Its query output does not match the evaluator's default discovery convention or structured-RAG input schema. **Synthesis:** this package provides experiment scaffolding, not a directly reproduced benchmark result. This concept remains draft because external corpora, execution, and protocol reconciliation are outstanding.[^rag-anything-3a14ecb]

## Observed three-stage protocol

| Stage | Configuration and artifact |
| --- | --- |
| `reproduce/index.py::process_with_rag` | Text/vision via `gpt-4o-mini`, embeddings `text-embedding-3-large` with dimension 3072; parser/method config; ingest forces `source="modelscope"`, `backend="pipeline"`, `device="cuda:0"` |
| `reproduce/query.py::process_with_rag` | Creates LightRAG with LLM cache disabled and a rerank callback; reads `<foldername>_qa.jsonl` beside the document; calls `mode="mix"`, `response_type="One Sentence"`, `vlm_enhanced=False` |
| `reproduce/llm_answer_evaluator.py` | LLM judge `gpt-4o-mini`, temperature 0.1, max 1000 output tokens, 15-second timeout, three attempts; supports structured-RAG result files or a separate flat-QA directory route |

**Observed:** query output is `qa_results_mix_mm.json`, an array with `question`, generated `answer`, and `correct_answer`. VLM query enhancement is explicitly disabled, so this script does not evaluate retrieved-image VLM answering even though ingestion may have indexed visual descriptions. `ENABLE_RERANK` appears in the example environment but the script always constructs a rerank callback.[^rag-anything-3a14ecb]

## Input/output mismatch

**Observed:** the evaluator's default QA-directory scan searches only `qa_results_naive_mm*.json`; it therefore misses the query script's `qa_results_mix_mm.json`. Its `--rag-results-file` path expects per-method objects such as `hybrid_result`/`mix_result`/`naive_result`, plus `doc_id` and `expected_answer`; simply passing the flat query output is not an equivalent connection.[^rag-anything-3a14ecb]

**Synthesis, unexecuted reconciliation options:** explicitly adapt the output to the structured per-method schema, or make a disposable copy matching the QA scan naming and use its flat-QA route. The latter labels the method `qa` and infers `doc_id` from the first directory PDF or directory name; it should not silently be presented as a native `mix` evaluation. Never alter immutable raw source/data to hide the mismatch.[^rag-anything-3a14ecb]

## Metrics and resume semantics

**Observed:** accuracy-only grading is binary accuracy. Comprehensive prompts additionally request relevance, completeness, faithfulness, clarity, consistency, and overall score on 0–1 scales. Reports aggregate method accuracy and comparisons; output includes evaluation JSON, summary CSV, and a log. These are judge-generated grades, not independently checked ground truth.[^rag-anything-3a14ecb]

**Observed:** resume keys use `(doc_id, question, method)` and skip successful entries with a non-null accuracy. Saves use temporary-file replacement and per-item persistence. **Synthesis:** changing an answer without changing that identity can reuse a stale grade. The max-evaluations cap is applied per input file, so capped aggregates require explicit sampling/accounting to compare fairly.[^rag-anything-3a14ecb]

## Reproducibility and negative findings

- **Observed:** the default `reproduce/data` corpus directory is absent. Questions, reference answers, PDFs, dataset splits, and sampling provenance cannot be reconstructed from these scripts alone.
- **Observed:** indexing assumes a CUDA device and model-download source; exceptions are logged/caught rather than reliably propagated into a failing process exit. **Synthesis:** exit success is not sufficient evidence of indexed data.
- **Observed:** the judge has nonzero temperature, with no repeated-judge/seed protocol established in the inspected paths. **Synthesis:** single-model grades are nondeterministic and vulnerable to judge bias; the answering/judging model family overlaps.
- **Observed:** no measured benchmark scores, hardware/compute run record, or independent reproduction was established by this ingest. The README links a technical report, but that external paper was not retrieved or compiled here.
- **Unverified:** live provider/embedding/rerank compatibility, evaluation parsing reliability, model quality, and every numerical result that would require running the protocol.[^rag-anything-3a14ecb]

## Relationships

- **Uses:** [Document ingestion](rag-anything-ingestion.md) for index creation.
- **Uses:** [Query and retrieval](rag-anything-query-retrieval.md), specifically its text-only answer path in the supplied query script.
- **Depends on:** [Runtime operations](rag-anything-stack-operations.md) for CUDA/models/providers/environment.
- **Uses:** [Source map](rag-anything-source-map.md) for missing-data and partial-evaluator coverage limits.

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb352b90d40a9884a5ad235d98ac72e`: `reproduce/index.py::process_with_rag` (92 onward, model functions/embedding configuration and final ingestion call); `reproduce/query.py::process_with_rag` (92 onward; rerank/LightRAG setup, JSONL reading, query and output writing 190–285); `reproduce/env.example`; `reproduce/llm_answer_evaluator.py` grading prompts (46–158), evaluation/model call (286–530), structured result reader (approximately 870–980), atomic saves (1009), report (1058–1188), resume (1489–1580), flat QA reader and directory discovery (1581–1715), CLI/main (1738–1876); default data path checked against package inventory; README “Citation” links the external technical report. Evaluator inspection was targeted, not a complete line-by-line audit; no experiment was run.
