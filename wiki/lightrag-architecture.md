---
type: Concept
title: LightRAG architecture and technology stack
description: Python facade and mixins, FastAPI and React delivery, storage namespaces, role routing, and explicit runtime lifecycle.
tags: [rag, architecture, technology]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG is a Python graph-and-vector RAG library with a FastAPI service, React WebUI, provider adapters, interchangeable storage, and in-tree document parsing/multimodal analysis. The final dataclass facade composes model-role, storage-migration and pipeline mixins. **Synthesis:** its central abstraction is a workspace-scoped retrieval engine and mutation pipeline, rather than a general-purpose agent-workflow canvas.[^lightrag-aaebfe1]

## Component map

| Boundary | Responsibility |
| --- | --- |
| `lightrag.py::LightRAG` | Public query/insert/admin APIs, store composition, flush and recovery gates |
| `pipeline.py::_PipelineMixin` | Enqueue, admission/reservations, parse/analyze/process queues, status transitions |
| `operate.py` | Extraction, merging, graph rebuilding, retrieval/context construction |
| `llm_roles.py::_RoleLLMMixin` | Role-specific callables, limits, runtime configuration |
| `storage_migrations.py::_StorageMigrationMixin` | Startup/pre-creation data backfills |
| `parser/`, `chunker/`, `sidecar/` | File conversion, chunk strategies, structured parser interchange |
| `kg/` | Storage adapters and shared-process coordination |
| `api/` | FastAPI, request/auth/limit dependencies, document/query/graph/Ollama routes |
| `lightrag_webui/` | Dual-entry admin and query-only browser app |

**Observed:** the package lazily exports `LightRAG`, `QueryParam`, `RoleLLMConfig`, `RoleSpec`, and `ROLES`. Server startup assembles configured adapters through `create_app`/`initialize_rag`; SDK callers can inject functions. The server and SDK expose overlapping but non-identical ingestion contracts.[^lightrag-aaebfe1]

## Stack and persisted planes

**Observed:** distribution `lightrag-hku` uses setuptools, Python ≥3.10 and MIT licensing. Core dependencies include asyncio-oriented HTTP/model utilities, NumPy, NetworkX, NanoVectorDB, Pydantic, tiktoken, tenacity and dotenv/configuration helpers. Optional extras add API, provider/storage, evaluation and tracing packages. React 19/Vite 8/Zustand 5, Tailwind, axios and Sigma/graphology comprise inspected frontend dependencies; Bun builds/tests the browser bundle.[^lightrag-aaebfe1]

Four independent storage axes cover KV, vectors, graph and document status. Twelve composed namespaces include full documents, text chunks, LLM cache, full-entity/full-relation recovery anchors, entity/relation chunk tracking, three vector indexes, the graph and document status. **Synthesis:** recovery metadata is part of the write protocol, not disposable derived logging.[^lightrag-aaebfe1]

## Lifecycle and data flow

**Observed:** storage initialization/finalization is explicit; deprecated automatic lifecycle management defaults off. File processing flows enqueue → parse → multimodal analyze → chunk/embed/extract/merge → flush → terminal status. `DocStatus` includes pending, parsing, analyzing, processing, processed and failed; the old preprocessed state is deprecated. Querying reads graph/vector/chunk stores, prepares a bounded context, then optionally generates an answer through the query role.[^lightrag-aaebfe1]

**Observed:** multi-worker shared state uses a parent-owned manager topology, while default graph/vector implementations keep process-resident snapshots with local persistence. **Synthesis:** a multi-process worker setting is not evidence of safe independent multi-pod writers; deployment and backend consistency constraints must be considered together.[^lightrag-aaebfe1]

## Relationships

- **Uses:** [Ingestion](lightrag-ingestion.md), [chunking](lightrag-chunking.md), [extraction](lightrag-extraction.md), and [deletion/recovery](lightrag-deletion.md).
- **Uses:** [Storage](lightrag-storage.md), [model roles](lightrag-models.md), and [concurrency contracts](lightrag-concurrency.md).
- **Exposes:** [Retrieval](lightrag-retrieval.md) through [API/UI](lightrag-api-ui.md).
- **Related:** [RAG-Anything architecture](rag-anything-architecture.md) is a separate pinned multimodal orchestrator; LightRAG's reported integration does not establish supersession or drop-in compatibility.

## Evidence limits

Static architecture inspection only. The source map records targeted, not exhaustive, backend/parser/provider/test coverage. No server, frontend build, database, worker pool, or model was run.[^lightrag-aaebfe1]

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `lightrag/lightrag.py::LightRAG, __post_init__, initialize_storages, finalize_storages, _index_storages`; `pipeline.py::_PipelineMixin, _run_pipeline_batch`; `base.py::DocStatus`; `llm_roles.py::_RoleLLMMixin`; `storage_migrations.py::_StorageMigrationMixin`; `lightrag/__init__.py` lazy exports; `api/lightrag_server.py::create_app, initialize_rag`; `kg/shared_storage.py::initialize_share_data`; `pyproject.toml` project/dependencies/extras/scripts; `LICENSE`; `lightrag_webui/package.json`; README “Multimodal Capability Upgrades”.
