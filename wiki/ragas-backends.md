---
type: Concept
title: Ragas persistence backends
description: Plugin-discovered CSV, JSONL, in-memory and Google Sheets backends have distinct durability and type-preservation constraints.
tags: [operations, rag, persistence]
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

**Observed:** backend-bound datasets and experiments share BaseBackend's six load/save/list methods while retaining separate namespaces. A singleton registry discovers `ragas.backends` package entry points and aliases. Shipped entries are `local/csv`, `local/jsonl`, `inmemory`, and optional `gdrive`.[^ragas-298b682]

## Storage tradeoffs

| Backend | Mechanism | Consequential constraints |
| --- | --- | --- |
| Local CSV | `<root>/datasets|experiments/<name>.csv` | First row defines headers; raw loads return strings; no nested-value codec; save overwrites |
| Local JSONL | Parallel `.jsonl` layout | Recursive dates serialize to ISO; date-looking strings heuristically regain date/datetime types; malformed lines warn and skip |
| In-memory | Separate dict stores with deepcopy on save/load | No filesystem durability; instance lifetime matters |
| Google Drive | Sheets in dataset/experiment Drive subfolders | Network/auth at initialization; A:Z range assumptions; stringification and heuristic type restoration |

`data_model` is backend context, not a guarantee that every adapter preserves typed rows. Registry discovery failures are logged; missing optional dependencies can affect availability. **Synthesis:** prefer JSONL over raw CSV when nested contexts/messages must survive round trips, but test date-shaped strings and malformed-line handling before relying on exact preservation.[^ragas-298b682]

## Google boundary

GDriveBackend expects `folder_id`, not the `root_dir` argument shown in one dataset guide. It supports service-account or OAuth credentials, environment-configured paths and a token cache. Its declared scopes include full Drive and spreadsheets access, not a demonstrated folder-only capability. See [security boundaries](ragas-security.md) before using sensitive evaluation data.[^ragas-298b682]

## Relationships and limits

- Used by [experiment tables](ragas-experiments.md) and [new-style datasets](ragas-datasets.md), not an automatic persistence layer for legacy EvaluationDataset.
- Split datasets use fresh in-memory backends; explicitly override storage for durable split-run results.
- Representative backend tests were inspected, with some assertions only located by symbol/name. No local round-trip or real cloud API test ran; atomicity, concurrent writers, permission handling and recovery are unverified.

[^ragas-298b682]: Ragas `298b682`, `pyproject.toml::project.entry-points.ragas.backends`; `src/ragas/backends/base.py::BaseBackend`; `src/ragas/backends/registry.py::BackendRegistry.discover_backends`; `src/ragas/backends/local_csv.py::LocalCSVBackend._load/_save`; `src/ragas/backends/local_jsonl.py::LocalJSONLBackend._serialize_datetime/_deserialize_datetime/_load`; `src/ragas/backends/inmemory.py::InMemoryBackend`; `src/ragas/backends/gdrive_backend.py::GDriveBackend`; `src/ragas/dataset.py::DataTable.train_test_split`; `docs/concepts/datasets.md::Cloud Storage`. Static inspection only unless explicitly stated otherwise; coverage and remaining limits: [source map](ragas-source-map.md).
