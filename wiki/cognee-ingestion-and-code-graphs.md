---
type: Concept
title: Cognee ingestion and code graphs
description: How Cognee stages and indexes content, builds knowledge graphs, and extracts repository structure.
tags: [agent-memory, cognee, ingestion]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:06:51Z' }
stale_after: 2027-02-06
sources:
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
---

**Observed:** Cognee separates staging via `add` from graph construction via `cognify`; the ordinary `remember` path orchestrates both. The cognify implementation provides an early indexing pipeline and a subsequent extraction pipeline, allowing chunk-level retrieval before graph extraction finishes when early indexing is enabled.[^cognee]

## Data flow

- **Observed:** the indexing task list classifies and chunks documents and stores embedded chunks without an LLM task. The graph task list can reuse indexed chunks, extracts graph and summaries, then writes graph/vector data; optional provenance recording follows.[^cognee]
- **Reported by implementation documentation:** indexing and cognify have separate run records and rollback boundaries; extraction failure can leave already indexed chunks searchable. This failure behavior was not executed.[^cognee]
- **Observed:** code graph tasks invoke an external `enola` executable and parse snapshot artifacts; no Enola implementation is vendored in that task package. Code repository partitioning skips hidden paths and symlinks; this is not a substitute for a security review of ingested repositories.[^cognee]

## Relationships

- **Feeds:** [Cognee retrieval](cognee-retrieval.md) with chunk and graph representations.
- **Part of:** [Cognee overview](cognee-overview.md); inspection scope is in the [source map](cognee-source-map.md).

[^cognee]: Revision `525b1d1`, `cognee/api/v1/remember/remember.py::_remember_inner`, `cognee/api/v1/add/add.py::add`, `cognee/api/v1/cognify/cognify.py::get_default_tasks`, `::get_indexing_tasks`, `cognee/modules/cognify/memory_pipelines.py::run_memory_pipelines`, `cognee/tasks/code_graph/__init__.py`, `cognee/tasks/code_graph/code_repo.py::partition_repo_files`.
