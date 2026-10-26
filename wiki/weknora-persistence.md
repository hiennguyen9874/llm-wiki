---
type: Concept
title: WeKnora domain persistence and migrations
description: Workspace-scoped knowledge, chunks, conversations, store bindings, and separate PostgreSQL/SQLite migration histories.
tags: [ml, weknora, persistence]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora models a workspace as a tenant containing knowledge bases, documents, chunks, conversations, and named infrastructure bindings. **Observed:** GORM types and tenant-scoped repository predicates supply the persistence model, while PostgreSQL and SQLite use separate versioned migration directories. This is a schema-level account, not a certification of isolation across every repository method.[^weknora]

## Durable entities

| Entity | Inspected responsibility |
| --- | --- |
| `Tenant` | Workspace configuration, retrieval engines, storage quota/usage, memory and parser settings |
| `KnowledgeBase` | `document`, `faq`, or `wiki`; chunking, extraction, image, question, tagging, and wiki configuration |
| `Knowledge` | Document lifecycle, parse status, outstanding enrichment subtasks, soft deletion |
| `Chunk` | Mutable content, original `SourceContent`, content revision/index status, parent/related chunk structure, image metadata |
| `Session` / `Message` | Ownership, last-request state, answer references, tool steps, mentions and attachments |
| `VectorStore` | Named per-workspace connection configuration; not the same as the application's database |

**Observed:** `KnowledgeBase.VectorStoreID` is create-only in its GORM tag; storage backend binding is separate. Declared parse states are `pending`, `processing`, `finalizing`, `completed`, `failed`, `deleting`, and `cancelled`; finalizing means primary parsing is complete but enrichment remains. `repository/knowledge.go::GetKnowledgeByID` explicitly filters both tenant and document ID.[^weknora]

## Storage distinctions

**Observed:** managed `VectorStore` engine types deliberately exclude PostgreSQL and SQLite because those use the application-database/environment-store path. Thus the README's broad retrieval-backend list does **not** mean every backend is selectable as a named database-managed instance. This distinction matters when following [retrieval routing](weknora-hybrid-retrieval.md).[^weknora]

`internal/database/migration.go::RunMigrationsWithOptions` chooses `migrations/versioned` for PostgreSQL and `migrations/sqlite` for SQLite. Startup also has idempotent legacy storage-binding fixups. The initial PostgreSQL migration defines the core tenant/model/KB/document/session/message/chunk tables; subsequent migrations were inventoried but not fully reviewed.[^weknora]

## Contradictions

- **Observed historical schema/code tension:** `migrations/versioned/000000_init.up.sql` uses document parse-status default `unprocessed`, whereas current `types/knowledge.go::ParseStatusPending` is `pending`. Whether later migrations normalize that default is **unverified**; neither initial SQL nor current constants alone establish the effective deployed schema.[^weknora]

## Relationships

- Initialized by [backend bootstrap](weknora-backend-architecture.md).
- Supplies document lifecycle state to [task queues](weknora-task-queues.md).
- Wiki page history has additional [atomic revision and rewrite guards](weknora-wiki-compilation.md).

## Coverage limits

Only representative entity fields, a tenant-filtered repository method, initial schema, and migration dispatch were inspected. Later migrations, all foreign-key/constraint behavior, full repository authorization coverage, and data migration execution remain pending; see the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `internal/types/tenant.go::Tenant`, `GetDefaultRetrieverEngines`; `internal/types/knowledgebase.go::KnowledgeBase`; `internal/types/knowledge.go::Knowledge`, `ParseStatusPending` and parse-state constants; `internal/types/chunk.go::Chunk`; `internal/types/session.go::Session`; `internal/types/message.go::Message`; `internal/types/vectorstore.go::VectorStore`, `validEngineTypes`; `internal/application/repository/knowledge.go::GetKnowledgeByID`; `internal/database/migration.go::RunMigrationsWithOptions`; `internal/container/container.go::initDatabase`, `resolveStorageProviderPending`, `migrateLegacyStorageBackends`; `migrations/versioned/000000_init.up.sql`, core table definitions and `knowledges.parse_status`. Package entry: [README](../raw/WeKnora/README.md), “Supported backends.”
