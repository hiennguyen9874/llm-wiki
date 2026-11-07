---
type: Concept
title: Hy Memory storage backends, snapshot and re-embedding
description: Vector, graph, cache and history store abstractions in the SDK, plus offline data-plane snapshot/restore and the re-embedding workflow.
tags: [agent-memory, hy-memory, storage, chroma, kuzu, reembed]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory storage backends, snapshot and re-embedding

The SDK uses a three-engine layout — vector store, graph store, cache — plus a separate history store and (for working/coding) local SQLite stores, each behind a provider abstraction with no silent fallback on unknown providers (`hy_memory/data/__init__.py` docstring; `data/vector_store.py::create_vector_store`).[^hy-memory]

## Backends

- **Vector**: `VectorStoreBase` → Chroma (default), Qdrant, FAISS. `physical_collection_name(base, dims)` appends `_{dims}` so different embedding widths never share a collection (`data/vector_store_base.py`). Payload fields include isolation key, layer, status, `memory_at`, `valid_from/until`, `supersedes`, `is_latest`, `meta_tags`.[^hy-memory]
- **Graph** (ultra, optional in pro): `GraphStoreBase` → embedded Kuzu (default) or Neo4j (also used for `memgraph`). Kuzu node tables `User, Topic, HierarchyTopic, Entity, VdbRef, Memory`; rel tables `HAS_MEMORY, TAGGED_WITH, MEMBER_OF, SUBTOPIC_OF, MENTIONS, RELATED_TO, DERIVED_FROM, CROSS_ABSTRACTS_TO, TEMPORAL_NEXT` (`data/graph_store_kuzu.py:137-250`). Kuzu runs on a single-thread executor and must not be widened (`graph_store_kuzu.py:40-45`).[^hy-memory]
- **Cache**: SQLite (default) or MySQL with date-partitioned tables; tables `memory_operations_v2, pipeline_logs_v2, write_outcomes, system_metrics, episode_state` (`data/cache_sqlite.py:48-115`; `cache_mysql.py`).[^hy-memory]
- **History**: separate SQLite `memory_history` table (`data/history_store.py`).[^hy-memory]
- **Not real**: `data/kv_store.py` is legacy (docs say Redis unsupported) and `data/rdb.py` is a placeholder whose methods raise `NotImplementedError` (`env_reference.md` Cache row; `rdb.py`).[^hy-memory]
- **Working/coding metadata**: local SQLite, see [Working and coding memory](hy-memory-working-coding-memory.md) (`README.md::Storage Backends`).[^hy-memory]
- Known limits: Chroma cannot express null-aware time filters, so `created_after` is post-filtered, and Chroma has no BM25 channel so hybrid recall degrades to vector-only (`vector_store_base.py::passes_created_after`; `env_reference.md` Vector Store note).[^hy-memory]

## Snapshot and restore

`snapshot_local_data_plane(source, target, writers_stopped)` refuses unless writers are stopped, rejects symlinks, refuses an existing target, and verifies every copied file by size and SHA-256. `restore_local_data_plane` stages to a temp dir, keeps a `.pre-restore` copy and rolls back on `OSError`. Local paths only; remote providers must provide their own export (`hy_memory/snapshot.py`, module docstring).[^hy-memory]

## Re-embedding

`hy_memory/reembed.py` re-embeds into a new embedding space identified by `(model, dims)`: `plan_reembed` → `reembed_vector_space` (batch 64, `max_inflight=2`, `skip_existing`, cancellable with finished batches preserved) → `verify_reembed`. Source is never written; every vector width is checked (`EmbeddingDimensionMismatchError`). It supports **Chroma only** (`VectorSpace.from_config`) and covers six collections (`memory, entities, coding_keys(_cv), working_facts(_cv)`). Graph re-embedding builds a fresh Kuzu DB at the target because Kuzu cannot `SET` an indexed column (`plan_graph_reembed`, `reembed_graph`, `verify_graph_reembed`).[^hy-memory] Introduced in 2.0.10 (`CHANGELOG.md::2.0.10`). MemHub drives it for [embedding-space switching](memhub-embedding-space-switching.md).[^hy-memory]

## Relationships

- Part of: [SDK API and config](hy-memory-sdk-api-and-config.md).
- Used by: [Chat retrieval](hy-memory-chat-retrieval-pipeline.md); [MemHub embedding switching](memhub-embedding-space-switching.md) (uses reembed and snapshot).

## Coverage and limits

Static inspection (delegated); the Qdrant, FAISS and Neo4j adapters were not read in detail. Backend parity was not tested here.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
