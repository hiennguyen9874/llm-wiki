---
type: Concept
title: txtai persistence and index lifecycle
description: Identifiers, SQL content joins, mutation and initialization boundaries, serialization, archives, and cloud persistence.
tags: [rag, operations, txtai, persistence]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac4
    title: txtai repository
---

**Observed:** txtai separates vector positions from external document identifiers and optional relational content. Saving an embeddings database persists configuration plus component-specific artifacts; SQL/content backends join vector candidates with text, metadata, and encoded objects. **Synthesis:** this is a composed storage lifecycle, not a demonstrated atomic transaction across every index, graph, and database.[^txtai-repo]

## Identifiers, content, and mutations

With content disabled, `IndexIds` maps internal vector positions to user identifiers. With content enabled, relational sections map `indexid` to document IDs/text/tags, with separate JSON document and binary object tables. SQLite is the default for `content: true`; DuckDB and SQLAlchemy-client configurations are alternatives. Encoders store/decode objects such as PIL images; object-only rows can be decoded and re-vectorized during reindex.[^txtai-repo]

`index` constructs/rebuilds components; `upsert` deletes matching IDs before inserting replacement data. `delete` fans out across configured stores. Backend mutation support differs, so ANN choice constrains lifecycle operations. `Documents` can stage input in an internally enabled temporary pickle stream; this is distinct from permitting arbitrary external pickle artifacts.[^txtai-repo]

**Observed destructive boundary:** `Client.createtables` clears `sections`, `documents`, and `objects` after creating schema. It is called through **fresh `RDBMS.initialize` with no active connection**, not every client connection: `RDBMS.load` opens a session without calling `createtables`. Starting a new index against an existing client database/schema therefore warrants explicit review; loading an existing persisted index must not be conflated with initialization.[^txtai-repo]

## SQL query integration

`similar(...)` clauses are parsed into placeholders; retrieval produces candidate IDs/scores, and RDBMS embeds them via temporary batch/score tables. Multiple similarity contributions are averaged per internal ID. Unless explicitly overridden, similarity queries order by descending score. Metadata, grouping, ordering, and pagination remain relational operations.[^txtai-repo]

The SQL parser rejects multiple statements and supports bind parameters, but assembled query clauses and configured functions/expressions are powerful executable/query capabilities. **Synthesis:** this is a query surface over accessible content, not row-level authorization or a sanitizer for arbitrary caller-selected expressions. Bind values rather than interpolating application data, and restrict exposed query capability where necessary.[^txtai-repo]

Pagination candidate budgeting has constraints: numeric limit/offset recognition and leading score-desc order influence how much ANN data is fetched; parameterized limits are not necessarily usable for candidate sizing. DuckDB runtime failures can abort its current transaction; inspected code reports unsaved-change loss rather than proving savepoint recovery.[^txtai-repo]

## Save/load, archives, and cloud

| Artifact | Role |
| --- | --- |
| `config.json` / legacy `config` | Configuration; JSON preferred, gated pickle compatibility |
| `embeddings`, `lsa`, `ids` | Native ANN, reduction, and no-content identifier state |
| `documents`, `scoring` | Content backend and sparse metadata/postings |
| `indexes/<name>`, `graph` | Child indexes and graph-specific state |

Components use native library formats or MessagePack/SQLite where appropriate; remote relational state is not necessarily a portable directory snapshot. `save/load` can wrap compressed archives and cloud providers. Hugging Face Hub and libcloud storage are available; object-storage downloads validate destination containment. Documentation restricts cloud storage to compressed indexes.[^txtai-repo]

Legacy serializers can fall back to gated pickle; enabling `ALLOW_PICKLE` changes artifact trust. Tar/Zip paths validate extraction targets, but the inspected code does not impose comprehensive expansion-size budgets. See [security](txtai-security.md) before importing external indexes or archives.[^txtai-repo]

## Relationships and limits

- **Supports:** [Retrieval](txtai-retrieval.md), [graph state](txtai-graph.md), and [RAG text context](txtai-rag.md).
- **Used by:** [Application/API](txtai-api.md); serving write/reindex flags are additional gates, not storage transactions.
- **Part of:** [txtai](txtai.md); [source map](txtai-source-map.md) identifies remaining backend and durability coverage.

No persistence round-trip, failure injection, migration, concurrent-write, remote-database, cloud upload/download, or archive extraction was executed. No general crash-consistency guarantee is established.

[^txtai-repo]: Revision `738aac4`: `src/python/txtai/embeddings/base.py::Embeddings.index, upsert, delete, reindex, save, load`; `embeddings/index/indexids.py::IndexIds`; `embeddings/index/transform.py::Transform.load, stream`; `embeddings/index/documents.py::Documents`; `database/factory.py::DatabaseFactory`; `database/schema/statement.py::Statement`; `database/rdbms.py::RDBMS.load, initialize, session, reindex, embed, scores, query`; `database/client.py::Client.createtables, connect`; `database/duckdb.py::DuckDB`; `database/sql/base.py` statement parsing; `database/encoder/image.py::ImageEncoder`; `embeddings/index/configuration.py::Configuration`; `serialize/serializer.py::Serializer`, `serialize/pickle.py::Pickle.allow`; `archive/tar.py::Tar.unpack`, `archive/zip.py::Zip.unpack`; `cloud/factory.py::CloudFactory`, `cloud/storage.py::ObjectStorage.load`, `cloud/hub.py::HuggingFaceHub`; `docs/embeddings/format.md`, `docs/embeddings/indexing.md` cloud storage restriction. Short module paths are relative to `src/python/txtai/`.
