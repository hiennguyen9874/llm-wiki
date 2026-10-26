---
type: Concept
title: Ragas dataset stacks and sample schemas
description: Backend-bound Dataset and Experiment tables coexist with legacy EvaluationDataset samples and are not interchangeable.
tags: [rag, evaluation, schemas]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:20:38Z }
stale_after: 2027-01-24
sources:
  - id: ragas-298b682
    resource: ../raw/ragas/README.md
    scope: ../raw/ragas/
    kind: code
    revision: 298b682
    title: Ragas repository
---

**Observed:** Ragas exposes two different dataset abstractions: `dataset.py::DataTable` underlies the backend-bound `Dataset` and `Experiment`, whereas `dataset_schema.py::EvaluationDataset` contains typed evaluation samples and supports the legacy evaluator. HuggingFace `datasets.Dataset` is a third class accepted by that evaluator, not an alias for `ragas.Dataset`.[^ragas-298b682]

## Choosing a data model

| Model | Shape | Intended consumer |
| --- | --- | --- |
| `DataTable` / `Dataset` | Named table of dicts or Pydantic rows, backend object | Experiment row functions |
| `Experiment` | DataTable distinguished by `DATATABLE_TYPE` | Backend's experiment namespace |
| `EvaluationDataset` | `SingleTurnSample` or `MultiTurnSample` collection | `evaluate` / `aevaluate` |
| HuggingFace Dataset | Columnar data converted by evaluator | Legacy input compatibility |

`DataTable` resolves backend instances or registry names, can load with an optional model, and explicitly saves via its backend. Constructor-supplied data is assigned directly; do not assume uniform validation simply from providing a model. `train_test_split` creates fresh in-memory-backed outputs; an experiment inheriting one of these backends remains in memory unless storage is explicitly selected.[^ragas-298b682]

## Evaluation fields and validation

All `SingleTurnSample` fields default to `None`, including user input, response, retrieved contexts and reference. This differs from migration-guide comments calling user input/response required. `MultiTurnSample.user_input` is required and its validator checks message/tool ordering. Legacy metric-specific required columns and compatible sample types are checked by `validation.py`, not by making all sample fields mandatory.[^ragas-298b682]

Legacy HuggingFace input conversion maps historical `question`, `contexts`, `answer`, `ground_truth` names to `user_input`, `retrieved_contexts`, `response`, `reference`. This compatibility layer does not make backend-bound Dataset a valid legacy-evaluator input. **Synthesis:** select the runner first, then its matching dataset and metric APIs; do not infer interchangeability from similar class names.[^ragas-298b682]

## Relationships

- Uses [persistence backends](ragas-backends.md) for new-style tables.
- Used by [experiments](ragas-experiments.md) or [legacy evaluation](ragas-legacy-evaluation.md), depending on the data abstraction.

## Limits

Empty collections, mixed schemas and serialized message-content round trips were not executed. Model-specific coercion, particularly after CSV string loading, must be tested with the caller's actual schema.

[^ragas-298b682]: Ragas `298b682`, `src/ragas/dataset.py::DataTable.__init__/_resolve_backend/load/save/train_test_split`; `src/ragas/dataset_schema.py::SingleTurnSample/MultiTurnSample/RagasDataset/EvaluationDataset`; `src/ragas/validation.py::validate_required_columns/validate_supported_metrics`; `src/ragas/utils.py::convert_v1_to_v2_dataset`; `docs/howtos/migrations/migrate_from_v03_to_v04.md::Updated Schema`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
