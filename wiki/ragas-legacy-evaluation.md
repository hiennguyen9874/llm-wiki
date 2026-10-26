---
type: Concept
title: Ragas legacy evaluation and executor
description: Deprecated evaluate and aevaluate retain sample validation, metric fan-out, ordered scores, cancellation, and optional cost tracing.
tags: [rag, operations, evaluation, concurrency]
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

**Observed:** deprecated `evaluate()` and `aevaluate()` remain public. They accept legacy EvaluationDataset or convert HuggingFace datasets, validate legacy metrics, supply missing model resources, fan out per sample/metric through Executor, and construct EvaluationResult. This is a different execution contract from `@experiment`.[^ragas-298b682]

## Data and control flow

- Optional column remapping and v1-to-v2 field conversion precede typed samples.
- Default metrics are answer relevancy, context precision, faithfulness and context recall.
- Missing metric LLM/embedding resources are initialized; injected resources are restored in `finally`.
- Single-turn and multi-turn scoring are dispatched by dataset sample type. Scores are reassembled into per-row metric dictionaries.
- EvaluationResult supports aggregate representations and tabular export; cost/token helpers depend on installing a token-usage parser/callback, not merely running a score.

The evaluator rejects metrics outside its legacy base-class contract. Collection/custom metrics that return structured MetricResult should not be assumed compatible merely because their names match.[^ragas-298b682]

## Executor and run configuration

Executor assigns submission indices, supports optional batches, restores submission order, and converts caught job failures to NaN when `raise_exceptions=False`. Cancellation is cooperative via an event and pending-task handling; `return_executor=True` exposes the execution handle. RunConfig defaults include timeout 180 seconds, max_retries 10, max_wait 60, max_workers 16 and seed 42. Retry helpers use exponential randomized waiting; configuration does not imply every library operation universally receives retries.[^ragas-298b682]

`evaluate` has notebook/nested-loop handling, including `allow_nest_asyncio`; `aevaluate` provides the async entry. **Synthesis:** prefer explicit async composition inside existing event loops and test the application's loop policy rather than treating monkey-patching as universally compatible.[^ragas-298b682]

## Relationships and limits

- Depends on [legacy sample schemas](ragas-datasets.md) and the [legacy metric contract](ragas-metric-contracts.md).
- Supersession is only a source-reported migration direction toward [experiments](ragas-experiments.md), not removal of the old API in this snapshot.
- Executor/async-evaluation tests were inspected for intent, not run. No rate-limit, cancellation, timeout, notebook, cost or provider behavior was reproduced.

[^ragas-298b682]: Ragas `298b68274234c060deacab3cf5fb52aa3a20e885`, `src/ragas/evaluation.py::aevaluate/evaluate`; `src/ragas/executor.py::Executor`; `src/ragas/async_utils.py::apply_nest_asyncio/as_completed/run`; `src/ragas/run_config.py::RunConfig/add_retry/add_async_retry`; `src/ragas/dataset_schema.py::EvaluationResult`; `tests/unit/test_executor.py`; `tests/unit/test_async_evaluation.py`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
