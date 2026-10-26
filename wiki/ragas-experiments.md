---
type: Concept
title: Ragas experiment runner and versioning
description: Experiment row functions run in completion order with backend inheritance, dropped failures, and optional repository-mutating versioning.
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
    revision: 298b68274234
    title: Ragas repository
---

**Observed:** `@experiment()` wraps a sync or async row function. Calling that wrapper invokes one row function; `.arun(dataset)` is the dataset runner. It schedules all row coroutines with `asyncio.as_completed`, appends non-None results in completion order, warns and omits failed rows, then saves an Experiment through the selected backend.[^ragas-298b682]

## Execution and persistence contract

1. Choose supplied name or generate a memorable name; apply decorator name prefix.
2. Select backend: run argument, decorator default, then input dataset backend.
3. Create the result Experiment with optional output model.
4. Invoke the row function for every input, forwarding extra arguments.
5. Append successful non-None results as they complete; exceptions print warnings.
6. Save through `DataTable.save` and return the result table.

No RunConfig, semaphore, per-row timeout or automatic retry is wired into this runner. Sync row functions are called directly, not automatically offloaded to a thread. **Synthesis:** enforce provider rate limits and blocking-work isolation in caller code; retain input IDs in outputs because result positions do not preserve input order. Failed/None rows need separate accounting to avoid survivor-biased aggregates.[^ragas-298b682]

The experiment test suite contains a case expecting two outputs for three inputs when one raises, confirming this as observed test intent, not an executed test result.[^ragas-298b682]

## Documentation reconciliation

The migration guide's `await run_evaluation(dataset)` calls the row function once with the dataset object; `.arun(dataset)` performs row iteration. The experimentation guide's blanket timestamped-CSV statement is too broad: format and durability depend on backend, and save names come from explicit/generated experiment names. An in-memory backend does not become filesystem persistence on save.[^ragas-298b682]

## Git side effects

`version_experiment` is an explicit helper, not automatic pure metadata capture. It stages tracked changes by default, optionally all files, commits if dirty, otherwise uses HEAD, and optionally creates a `ragas/<experiment_name>` branch. It requires GitPython. **Synthesis:** review the caller's repository/index and naming before invocation; this compilation never invoked it.[^ragas-298b682]

## Relationships

- Uses [dataset tables](ragas-datasets.md) and [backend persistence](ragas-backends.md).
- Contrasts with [legacy evaluation](ragas-legacy-evaluation.md), whose Executor/RunConfig controls do not automatically carry over.

[^ragas-298b682]: Ragas `298b68274234`, `src/ragas/experiment.py::ExperimentWrapper.__call__/arun/experiment/version_experiment`; `src/ragas/dataset.py::DataTable.save`; `tests/unit/test_experiment.py::TestExperimentDecorator`; `docs/concepts/experimentation.md::Result Storage`; `docs/howtos/migrations/migrate_from_v03_to_v04.md::Evaluation to Experiment`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
