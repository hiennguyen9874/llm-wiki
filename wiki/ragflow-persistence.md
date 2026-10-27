---
type: Concept
title: "RAGFlow persistence and engines"
description: "Metadata, document search, object storage, cache/leases, and task queues are separate configurable persistence planes."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow persistence and engines

**Observed:** RAGFlow separates relational metadata, searchable chunks, object bytes, cache/leases, and asynchronous messages. These are distinct backend contracts: configuring a search engine does not automatically select a relational DB or object store. The inspected metadata path uses GORM with MySQL-compatible persistence; document engines are selected independently.[^ragflow]

## Persistence planes

| Plane | Observed implementation/selection | Boundary |
| --- | --- | --- |
| Metadata | MySQL or OceanBase's MySQL protocol | `ParseDatabaseConfig`; not a general PostgreSQL metadata option |
| Searchable documents/chunks | Elasticsearch, Infinity, OceanBase, SeekDB, SereneDB, Vastbase | `InitDocEngine` switch; engine parity not established |
| File/image objects | MinIO, S3, OSS, GCS | `Factory.initStorage`; Azure/OpenDAL enum/config presence is not runtime support |
| Cache, coordination, leases | Kvrocks via Redis client | Fail-fast initialization in ordinary main |
| Async task delivery | NATS JetStream | Only accepted message-queue type in `InitMessageQueue` |
| Dataset compile scheduling | MySQL records plus NATS events/wake-ups | Scheduling state is not solely owned by JetStream |

These are code-observed choices; third-party clients listed in `go.mod` are not additional supported config options.[^ragflow]

## Search schema and scope

`DocEngine` defines chunk and metadata operations, search, kNN score retrieval, SQL-style operations, and metadata filter pushdown. In the inspected Elasticsearch implementation, chunk indices are tenant-scoped (`ragflow_<tenantID>`), while `kb_id` filters dataset membership. Metadata indices use `ragflow_doc_meta_<tenantID>`; templates distinguish those namespaces. **Synthesis:** a tenant index is not equivalent to per-dataset physical isolation.[^ragflow]

## Schema evolution and compatibility

`BaseModel` carries both epoch-millisecond timestamps and date columns to retain legacy schema shapes. Migration handling compares version markers and separates manual fixups from ORM automation. Existing index names may differ from historic Python conventions; inspect migration ownership before proposing schema renames. No live-schema migration was attempted.[^ragflow]

## Configuration precedence and risks

Document-engine choice takes environment `DOC_ENGINE` over `general.doc_engine`. Storage factory support is narrower than the enum and commented config surface. Kvrocks connection failure is fatal in ordinary bootstrap even though agent option wiring contains an in-memory fallback branch; that branch is not a promise that cold startup tolerates missing Kvrocks.[^ragflow]

## Relationships

- **Used by:** [server architecture](ragflow-architecture.md), [ingestion](ragflow-ingestion.md), and [retrieval](ragflow-retrieval.md).
- **Used by:** [knowledge compilation](ragflow-knowledge-compilation.md) for products, scheduling, and navigation projections.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `internal/server/config/database_config.go::ParseDatabaseConfig`; `internal/engine/global.go::InitDocEngine / InitMessageQueue`; `internal/engine/engine.go::DocEngine / MessageQueue`; `internal/storage/storage_factory.go::initStorage`; `internal/storage/types.go::StorageType`; `internal/engine/kvrocks/redis.go::Init`; `cmd/ragflow_server.go::main`; `internal/server/api/server.go::buildAgentRunOptions`; `internal/engine/nats/knowledgecompile.go::knowledge.compile.events / notify.kc.workers`; `internal/engine/elasticsearch/chunk.go::CreateChunkStore`; `internal/engine/elasticsearch/client.go::index template installation`; `internal/engine/elasticsearch/common.go::ragflow_doc_meta_`; `internal/entity/base.go::BaseModel / BeforeCreate`; `internal/dao/database.go::InitDB`; `internal/server/config/general_config.go::DocEngineType`.
