---
type: Concept
title: LightRAG concurrency and durability contracts
description: Single- versus multi-process shared state, keyed locks, file publication fences, and strict-read migration constraints.
tags: [operations, concurrency, persistence]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:47:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a
    title: LightRAG repository
---

**Observed:** LightRAG's concurrency boundary is not just per-request asyncio concurrency: it includes workspace reservations, manager-backed cross-process state, keyed graph locks, and file-publication fences. **Synthesis:** consistency depends on using the expected process initialization and mutation protocols; independently starting writers against the same data is not equivalent to joining a shared manager topology.[^lightrag-aaebfe1]

## Shared-state topology

`initialize_share_data(workers, global_concurrency_limits)` chooses a multiprocessing manager, shared dictionaries, holder table and ingress/scan hubs for multiple workers; one worker uses asyncio locks and ordinary dictionaries. The initialized guard makes later initialization calls no-ops rather than upgrading topology. **Synthesis:** initializing single-process state first and subsequently asking for multiple workers does not establish cross-process coordination.[^lightrag-aaebfe1]

`get_final_namespace` combines workspace and namespace with `:`; an empty-string workspace preserves legacy bare namespaces, while absent workspace and namespace are rejected. Per-namespace caches are reset during initialization/finalization to avoid retaining workspace state. Pipeline status includes busy/destructive/scanning reservations, pending enqueue tokens, and ownership fields—not merely a single busy boolean.[^lightrag-aaebfe1]

## Lock responsibilities

**Observed:**

| Primitive | Intended boundary |
| --- | --- |
| `UnifiedLock` | Async or multiprocessing/holder-record locks behind one interface; blocking manager acquisition is executor-offloaded |
| `KeyedUnifiedLock` | Sorted multi-key acquisition, partial-acquisition rollback including cancellation |
| `KeyedHolderTable` | Atomic server-side holder acquire/release records |
| `NamespaceLock` | Per-coroutine reusable context via `ContextVar`; double acquisition is rejected |
| Data-init lock | Storage initialization and one-shot migration serialization |
| NetworkX single-writer capability | Admin mutation serialization for a process-resident graph |

Dead-owner reclamation considers PID liveness and process identity/start-time information; uncertain identity does not automatically authorize reclamation. Optional `psutil` availability affects probing. These are observed implementation controls, not fault-injection-tested guarantees.[^lightrag-aaebfe1]

## File-backed publication

**Observed:** fingerprint contracts require sampling before reading, treating unreadable stat separately from absence, and respecting publication order for multi-file stores. NetworkX declares single-writer requirements and supports discarding uncommitted graph mutations. JSON KV's update flag means shared data still needs flushing, not that disk is a newer independent copy. `write_seq` introduces ordering beyond whole-second timestamps for redo-log replay.[^lightrag-aaebfe1]

**Reported:** `FileBackedSnapshotContract` documents FAISS index and metadata as two independently renamed files, not a cross-file atomic transaction. A mismatched publication may leave orphan vectors or dropped metadata rows. `NetworkXSingleWriterContract` explains why a lock around serialization alone does not replace the full write gate. **Limit:** this ingest did not audit `file_atomic.py` or simulate torn publication, process death, or cross-worker interleavings.[^lightrag-aaebfe1]

## Migration and cache fences

**Observed:** startup `check_and_migrate_data` runs under the data-init lock, seeds chunk tracking, then backfills document entity/relation recovery anchors. Its existence check samples up to five processed documents rather than proving complete coverage. Strict reads matter: silently omitting corrupt status rows can make a partial migration appear finished on future starts. Chunk-tracking backfill raises on failed graph reads rather than certifying an empty result. SDK creation paths have a separate retryable pre-creation migration check.[^lightrag-aaebfe1]

**Observed:** `_query_done` commits `text_chunks` under an extraction-cache fence before publishing the LLM-cache namespace. A declined/failed chunk commit skips that cache commit. **Synthesis:** query completion can include durability coordination; cached extraction records should not become published without reachable chunk metadata.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Storage capability gates](lightrag-storage.md).
- **Used by:** [Ingestion and deletion](lightrag-ingestion.md) and [query/citation/cache handling](lightrag-query-contracts.md).
- **Related:** [Embedding recovery](lightrag-embedding-recovery.md) requires stopping all writers, not just respecting request-level locks.

## Evidence limits

Targeted static reading, with design-document assertions explicitly Reported. Ingress/scan hub bodies, all atomic-file helpers, full backend transactions, dead-process recovery, and concurrent execution remain unverified; see [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/kg/shared_storage.py::initialize_share_data, get_final_namespace, UnifiedLock, KeyedUnifiedLock, KeyedHolderTable, NamespaceLock, initialize_pipeline_status, get_data_init_lock, finalize_share_data`; `kg/file_fingerprint.py` publication contract; `kg/write_seq.py`; `kg/networkx_impl.py::requires_single_writer, discard_uncommitted_mutations`; `kg/json_kv_impl.py` update-flag contract; `storage_migrations.py::check_and_migrate_data, _migrate_chunk_tracking_before_creation`; `lightrag.py::LightRAG._query_done`; `tests/test_storage_migrations_strict_read.py` assertions inspected, not run; `docs/design/FileBackedSnapshotContract.md` FAISS publication; `docs/design/NetworkXSingleWriterContract.md` commit gate.
