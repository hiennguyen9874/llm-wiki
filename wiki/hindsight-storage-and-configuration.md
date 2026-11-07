---
type: Concept
title: Hindsight storage and configuration
description: Hindsight's PostgreSQL/Oracle storage, vector and text-search extensions, schema, and the hierarchical HINDSIGHT_API_* configuration system with key defaults.
tags: [agent-memory, hindsight, storage, configuration, postgres]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: storage-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/storage.md
    kind: documentation
    revision: eb963cb
    title: Storage developer doc
  - id: config-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/configuration.mdx
    kind: documentation
    revision: eb963cb
    title: Configuration developer doc
  - id: config-code
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/config.py
    kind: code
    revision: eb963cb
    title: HindsightConfig
---

Hindsight stores everything in PostgreSQL with pgvector (or Oracle AI Database 23ai at documented full parity) and deliberately has no storage abstraction layer beyond those two backends. Configuration is resolved per request through a global → tenant → bank hierarchy over ~530 `HINDSIGHT_API_*` environment constants.[^readme][^storage-doc][^config-code]

## Storage

- **Requirements:** PostgreSQL 15+, pgvector ≥ 0.5.0; uses HNSW, tsvector/GIN, JSONB and recursive CTEs. Tested managed services: RDS, Cloud SQL, Azure, Supabase, Neon (Reported).[^storage-doc]
- **Embedded dev DB:** `pg0` (default `HINDSIGHT_API_DATABASE_URL=pg0`), port 5555 in dev, data in `~/.hindsight/pg0/`; requires the `embedded-db` extra, so the slim base install does not provide it (Observed).[^storage-doc][^config-code]
- **Vector extension** (`HINDSIGHT_API_VECTOR_EXTENSION`): `pgvector` (HNSW cosine, default), `pgvectorscale`/`pg_diskann`, `vchord`, `scann` (AlloyDB). Embedding dimension default 384.[^config-code]
- **Text search** (`HINDSIGHT_API_TEXT_SEARCH_EXTENSION`): `native`, `vchord`, `pg_textsearch`, `pgroonga`, `pg_search`.[^config-code]
- **Oracle:** native `VECTOR(384, FLOAT32)`, Oracle Text, `memory_units` LIST-partitioned by `bank_id`, schema-based tenant isolation; observation near-duplicate reconciliation is skipped on Oracle (Observed/Reported).[^config-code][^storage-doc]
- **Schema:** 116 Alembic revisions; core tables include `banks, documents, chunks, memory_units, memory_links, entities, unit_entities, entity_cooccurrences, mental_models(+history/versions), knowledge_pages, directives, async_operations, webhooks, audit_log, llm_requests` and others (Observed; summarized, not fully read).[^config-code]

## Configuration

- **Hierarchy:** global env → tenant (`TenantExtension.get_tenant_config`) → bank (`banks.config` JSONB), resolved per request by `config_resolver.py::ConfigResolver`; only fields in `_CONFIGURABLE_FIELDS` are bank-overridable.[^config-code]
- **Adding config:** `HindsightConfig` constants plus docs table plus `.env.example` (see [Contributor workflow](hindsight-contributor-workflow.md)).

| Key | Default |
| --- | --- |
| `HINDSIGHT_API_DATABASE_BACKEND` / `_DATABASE_URL` / `_DATABASE_SCHEMA` | `postgresql` / `pg0` / `public` |
| `HINDSIGHT_API_HOST` / `_PORT` / `_WORKERS` | `0.0.0.0` / `8888` / `1` |
| `HINDSIGHT_API_LLM_PROVIDER` / `_LLM_MODEL` | `openai` / `gpt-4o-mini` |
| `RETAIN_CHUNK_SIZE` / `RETAIN_EXTRACTION_MODE` / `RETAIN_MAX_COMPLETION_TOKENS` | 3000 / `concise` / 64000 |
| `RECALL_MAX_TOKENS` (internal) / `REFLECT_MAX_ITERATIONS` / `REFLECT_WALL_TIMEOUT` | 2048 / 10 / 300 s |
| `WORKER_ENABLED` / `WORKER_POLL_INTERVAL_MS` / `WORKER_MAX_SLOTS` | true / 500 / 10 |
| `MCP_ENABLED` | true |
| `EMBEDDINGS_LOCAL_MODEL` / `EMBEDDINGS_MAX_INPUT_TOKENS` | `BAAI/bge-small-en-v1.5` / 8192 |

Values from `config.py` (Observed) and `configuration.mdx` (Reported); the docs page also covers multi-LLM failover/round-robin, file storage (Postgres/S3/GCS/Azure), file parsers (markitdown default, iris, llama_parse), audit logging, LLM request tracing, reverse-proxy base path and background maintenance.[^config-code][^config-doc]

## Relationships

Consumed by every pipeline: [Retain](hindsight-retain-pipeline.md), [Recall](hindsight-recall-pipeline.md), [Reflect](hindsight-reflect-agent.md). Provider choices: [Providers](hindsight-llm-embedding-providers.md). Deployment: [Deployment and CI](hindsight-deployment-and-ci.md). Per-tenant override hook: [Extensions](hindsight-extensions-defense-webhooks.md).

## Limits

Docs say performance is read-optimized (recall 100–600 ms, reflect 800–3000 ms, retain 500–2000 ms per batch; Reported, `performance.md`). A vendor blog cites Postgres p99 rising from 0.5 s to 5.3 s between small and ~210k memories to motivate the proprietary Memlake engine (Reported, vendor).

[^readme]: `README.md` § "Running in Production" (Storage, Configuration rows).
[^storage-doc]: `hindsight-docs/docs/developer/storage.md`; `performance.md`; `blog/2026-10-13-memlake.md`.
[^config-doc]: `hindsight-docs/docs/developer/configuration.mdx` (section list; defaults).
[^config-code]: `hindsight-api-slim/hindsight_api/config.py::HindsightConfig`, `config_resolver.py::ConfigResolver`, `engine/schema.py`, `alembic/versions/`, `engine/db/oracle.py`, `engine/sql/postgresql.py`.
