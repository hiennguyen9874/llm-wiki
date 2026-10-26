---
type: Concept
title: Ragas retrieval and answer-quality metrics
description: RAG judges measure context support, generated-question relevance, ranked precision, attribution recall and reference-based correctness with distinct limits.
tags: [rag, ml, evaluation, metrics]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b68274234c060deacab3cf5fb52aa3a20e885
    title: Ragas repository
---

**Observed:** Ragas' RAG metric families operationalize different comparisons: answer versus contexts, question versus generated questions, contexts versus a reference, and response versus reference claims. **Synthesis:** a score must be interpreted with its input requirements, prompt/model choice and empty-output behavior; faithfulness is context-consistency, not independent factual truth.[^ragas-298b682]

## Collections implementations inspected

| Metric | Mechanism | Important limit/default |
| --- | --- | --- |
| Faithfulness | Decompose response into statements, NLI verdicts against joined contexts, supported/total ratio | No generated statements yields NaN; judge does not check world truth |
| AnswerRelevancy | Generate questions from response, compare their embeddings with input question | Strictness 3; mean cosine with all-noncommittal zero gate; no generated questions yields 0 |
| ContextPrecisionWithReference | One context usefulness judgment per ranked context; average precision over binary hits | Requires reference; ContextPrecision alias points here |
| ContextPrecisionWithoutReference | Similar ranking judgment using response instead of reference | ContextUtilization aliases this family |
| ContextRecall | Attribute reference statements to joined retrieved contexts | Attribution ratio; empty classification yields NaN |
| FactualCorrectness | Claim decomposition and NLI in response/reference directions; precision/recall/F-beta | Defaults f1, beta 1, low atomicity/coverage; rounds to two decimals |
| AnswerCorrectness | Weighted factuality and embedding similarity | Not identical to claim-only correctness; similarity can be disabled by weight |
| NoiseSensitivity | Compare reference/response statements against contexts and classify incorrect context-supported claims | Relevant/irrelevant modes; lower is better |

ResponseGroundedness and ContextRelevance use two judge prompts and normalize averaged 0/1/2 ratings, with retry/NaN handling. A reference is itself evidence supplied by the caller, not an independent truth oracle. Repeating an incorrect retrieved passage may satisfy a context-support prompt; actual verdicts remain model-dependent.[^ragas-298b682]

## Migration and experiment interpretation

Legacy and collections implementations are not guaranteed numeric equivalents: for example, empty generated questions yield NaN in legacy response relevancy but 0 in the inspected collections metric. Legacy also exposes ID-based and non-LLM context precision/recall variants not simply replaced by like-named collection classes. Migration e2e tests inspect tolerances rather than proving exact parity, and were not run here.[^ragas-298b682]

**Synthesis:** compare retrieval changes under a fixed schema, metric implementation, judge model, prompt examples, embedding model, aggregation and invalid-score policy. Retain per-row failures rather than silently combining empty/NaN/None outputs. This compilation provides no measured model-quality, cost or latency result.

## Relationships and limits

- Depends on [metric API selection](ragas-metric-contracts.md) and [model/prompt configuration](ragas-model-adapters.md).
- Uses contexts/reference fields from [dataset schemas](ragas-datasets.md); generated references from [testset synthesis](ragas-testset-generation.md) still require quality review.
- Entity-recall, summary and some rubric prompt bodies received only signature/symbol-level inspection; no exhaustive metric catalogue verification.

[^ragas-298b682]: Ragas `298b68274234c060deacab3cf5fb52aa3a20e885`, `src/ragas/metrics/collections/faithfulness/metric.py::Faithfulness.ascore/_compute_score` and `util.py::NLIStatementPrompt`; `collections/answer_relevancy/metric.py::AnswerRelevancy.ascore`; `collections/context_precision/metric.py::ContextPrecisionWithReference/ContextPrecisionWithoutReference/ContextPrecision/ContextUtilization`; `collections/context_recall/metric.py::ContextRecall.ascore`; `collections/factual_correctness/metric.py::FactualCorrectness.ascore`; `collections/answer_correctness/metric.py::AnswerCorrectness.ascore`; `collections/noise_sensitivity/metric.py::NoiseSensitivity`; `collections/response_groundedness/metric.py`; `collections/context_relevance/metric.py` (all collection paths relative to `src/ragas/metrics/`); `src/ragas/metrics/_answer_relevance.py::ResponseRelevancy`; `tests/e2e/metrics_migration/`; `docs/concepts/metrics/available_metrics/faithfulness.md`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
