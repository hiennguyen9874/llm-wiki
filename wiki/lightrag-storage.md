---
type: Concept
title: LightRAG storage backends and workspace isolation
description: Four storage contracts, backend selection, capability gates, workspace mappings, and filtered-vector-search constraints.
tags: [rag, operations, storage]
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

**Observed:** LightRAG separates KV, vector, graph, and document-status persistence behind four independently selectable contracts. Default implementations are `JsonKVStorage`, `NanoVectorDBStorage`, `NetworkXStorage`, and `JsonDocStatusStorage`. **Reported:** the README reserves these RAM-resident, file-persisted defaults for small-scale testing/evaluation and recommends PostgreSQL for production. **Synthesis:** supporting a backend name does not establish equivalent isolation, transactionality, or migration behavior across all four contracts.[^lightrag-aaebfe1]

## Selection and capability gates

**Observed:** `STORAGE_IMPLEMENTATIONS` lists allowed names and minimum methods; `STORAGE_ENV_REQUIREMENTS` lists required environment names; `STORAGES` maps names to modules. `LightRAG.__post_init__` validates all four selections before constructing stores. `get_storage_class` imports defaults directly and lazily resolves other modules relative to `lightrag`. Environment checks establish presence, not validity: an exported empty value passes the shallow gate. The abstract storage classes require more than the registry's minimum method lists.[^lightrag-aaebfe1]

Important capabilities are explicit:

- `supports_strict_point_reads` distinguishes complete-or-raise reads from relaxed reads; unsupported strict reads raise `StorageCapabilityError` rather than authorizing deletion from incomplete evidence.
- `requires_single_writer` is true for NetworkX and drives higher-level admin write serialization.
- `requires_embedding_func` defaults true; `NoopVectorDBStorage` opts out, accepts writes without persisting vectors, and raises on queries.
- Buffer-discard APIs distinguish unsupported (`None`) from supported-but-empty (`0`). Deferred-operation support varies by backend; callers cannot infer rollback from a common method name.[^lightrag-aaebfe1]

## Isolation map

**Observed, selected implementation regions:**

| Backend | Workspace boundary |
| --- | --- |
| JSON / Nano / FAISS / NetworkX | Workspace subdirectory; empty workspace uses working directory directly |
| Redis | Key prefix |
| OpenSearch | Sanitized workspace/namespace index name, with collision checks |
| Milvus | Workspace/namespace/model-specific collection |
| Qdrant | Workspace-salted point IDs plus `workspace_id` payload filters in shared collections |
| PostgreSQL KV / status / vectors | Workspace row column; vector table also carries model suffix |
| PostgreSQL AGE graph | Workspace/namespace graph name |
| PostgreSQL table graph | Workspace/namespace/id keys in shared relational tables |
| Neo4j / Memgraph | Workspace node label, default `base` |
| MongoDB | Workspace-prefixed collections |

Backend-specific workspace environment overrides can take precedence over the passed workspace. **Synthesis:** stale overrides are data-visibility hazards; workspace labels are storage routing, not independently verified user authorization.[^lightrag-aaebfe1]

## Backend-specific constraints

- **Observed:** Redis provides KV/status, not graph/vector; startup rejects all-keys eviction policies that could silently evict durable document records.
- **Observed/reported:** Mongo vector search requires Atlas-compatible vector search; ordinary metadata/graph operations and label-search fallback should not be conflated with that requirement.
- **Observed:** OpenSearch normalizes index names and refuses detected workspace collisions rather than silently sharing an index. Neo4j/Memgraph escape workspace labels using doubled backticks.
- **Observed:** PostgreSQL offers AGE-backed and relational graph implementations. The AGE adapter has an unsupported-version gate; the source comments report a crash risk from AGE 1.8.0 onward. This ingest did not reproduce that crash.
- **Reported:** the pinned `PgVectorFilteredSearch` design note describes global ANN candidate generation followed by workspace filtering, causing sparse-workspace under-recall. It documents transaction-local `hnsw.iterative_scan = strict_order` mitigation and says this is not a guarantee or a tenant-local structural fix. Its measurements were not rerun here.[^lightrag-aaebfe1]

## Documentation reconciliation

**Reported:** environment/API documentation restricts workspace names to letters, digits, and underscore. **Observed:** `validate_workspace` rejects path separators and `.`/`..`, deliberately accepting dots and other characters. The implementation gate is therefore broader than the documented convention; downstream normalization can still create backend-specific collisions. Registry remnants for AGE/Chroma imports do not make them normally selectable: they are absent from allowed implementation lists.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Concurrency and durability](lightrag-concurrency.md) for shared state, commit fences, and migration serialization.
- **Uses:** [Embedding-space recovery](lightrag-embedding-recovery.md) for model compatibility and vector rebuilds.
- **Used by:** [Architecture](lightrag-architecture.md), [ingestion](lightrag-ingestion.md), and [retrieval](lightrag-retrieval.md).

## Evidence limits

Targeted static reading of backend naming, capability and migration regions, not full query-path or database integration testing. Large backend bodies, cursor/batch behavior, remote services, and many assertions remain pending in the [source map](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/kg/__init__.py::STORAGE_IMPLEMENTATIONS, STORAGE_ENV_REQUIREMENTS, STORAGES, verify_storage_implementation`; `kg/factory.py::get_storage_class`; `lightrag.py::LightRAG.__post_init__`; `base.py::BaseVectorStorage, BaseGraphStorage, DocStatusStorage` and strict-read/buffer-discard contracts; `utils.py::check_storage_env_vars, validate_workspace`; `kg/{json_kv_impl,json_doc_status_impl,nano_vector_db_impl,faiss_impl,networkx_impl,redis_impl,milvus_impl,qdrant_impl,postgres_impl,pgtable_impl,neo4j_impl,memgraph_impl,mongo_impl,opensearch_impl,noop_vector_db_impl}.py` workspace initialization and capability fields; `redis_impl.py` eviction guard (189–250); `postgres_impl.py` AGE version gate (1200–1290); `docs/design/PgVectorFilteredSearch.md` problem, mitigation and limits; README “Selecting Backend Storage”; `env.example` workspace constraints; `docs/LightRAG-API-Server.md` storage/workspace sections.
