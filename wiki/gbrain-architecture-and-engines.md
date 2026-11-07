---
type: Concept
title: GBrain architecture and engines
description: How GBrain's single operation registry, BrainEngine contract, PGLite and Postgres engines, topologies, thin client, canonical writers and generations fit together.
tags: [agent-memory, gbrain, architecture, storage-engine]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: engine-ts
    resource: ../raw/gbrain/src/core/engine.ts
    kind: code
    revision: 27f8b9d
    title: BrainEngine interface
  - id: operations-ts
    resource: ../raw/gbrain/src/core/operations.ts
    kind: code
    revision: 27f8b9d
    title: Operation registry
  - id: engines-doc
    resource: ../raw/gbrain/docs/ENGINES.md
    kind: code
    revision: 27f8b9d
    title: Engines design document
  - id: topologies
    resource: ../raw/gbrain/docs/architecture/topologies.md
    kind: code
    revision: 27f8b9d
    title: Topologies
  - id: thin-client
    resource: ../raw/gbrain/docs/architecture/thin-client.md
    kind: code
    revision: 27f8b9d
    title: Thin client
  - id: canonical-writers
    resource: ../raw/gbrain/docs/architecture/canonical-writers.md
    kind: code
    revision: 27f8b9d
    title: Canonical writers
  - id: generations
    resource: ../raw/gbrain/docs/architecture/generations.md
    kind: code
    revision: 27f8b9d
    title: Derivation generations
  - id: pglite-lock
    resource: ../raw/gbrain/src/core/pglite-lock.ts
    kind: code
    revision: 27f8b9d
    title: PGLite lock
  - id: serve-sync
    resource: ../raw/gbrain/docs/architecture/serve-sync-concurrency.md
    kind: code
    revision: 27f8b9d
    title: Serve and sync concurrency
---

GBrain is built around one spine: a contract-first **operation registry** (`src/core/operations.ts`) that generates both the CLI and the MCP tool surface, running against a **`BrainEngine`** interface with two interchangeable implementations — embedded **PGLite** (Postgres 17 compiled to WASM, the default) and **Postgres + pgvector** (Supabase or self-hosted) for shared or large brains. Embedding generation and chunking live outside the engine; the engine only stores and searches.[^operations-ts][^engine-ts][^engines-doc] The README presents the same shape: Markdown repos → sync/parse → engine → CLI or MCP → hybrid retrieval and typed graph traversal → synthesis.[^readme] For the data side see [data model and system of record](gbrain-data-model-and-system-of-record.md); for search see [retrieval pipeline](gbrain-retrieval-pipeline.md).

## Operation registry and call path

- `operations.ts` is the single array of operations; a handler-free manifest (`operation-manifest.generated.ts`) mirrors it for fast `tools/list`. Each operation declares params, handler, scope, `localOnly` and output redaction. Observed by subagent: the manifest has 194 entries, 23 `localOnly`, leaving 171 remotely callable (this matches the generated tool catalog; the curator re-counted the 23 `localOnly` markers). See [CLI and MCP surface](gbrain-cli-and-mcp-surface.md).[^operations-ts]
- Wiring (Observed): `cli.ts` / `mcp/server.ts` → `operations.ts` → `OperationContext{engine, config, logger, remote, auth}` → `engine-factory.createEngine` → `engine-construct.constructEngine` (dynamic import) → `BrainEngine` → `engine-sql/<domain>.ts` → a `SqlExecutor` with a PGLite or Postgres dialect → `src/schema.sql`.[^operations-ts][^engine-ts]

## The BrainEngine contract

- `export interface BrainEngine` carries `kind: 'postgres' | 'pglite'`; a subagent counted 187 method signatures covering lifecycle, pages, search, chunks/embeddings, graph, tags, timeline, files, facts/takes, stats and config. It is slug-keyed, not ID-keyed (Observed count; slug-keying Reported by `ENGINES.md`).[^engine-ts][^engines-doc]
- Shared SQL lives once per domain in `src/core/engine-sql/` (25 modules); the executor contract exposes capabilities such as `maxBindParamsPerStatement` (Reported).[^engines-doc]

## PGLite vs Postgres

| | PGLite | Postgres + pgvector |
| --- | --- | --- |
| Implementation | `pglite-engine.ts`, in-process WASM, data at `~/.gbrain/brain.pglite` | `postgres-engine.ts`, vendored and patched `postgres` driver |
| Best for | personal brains | shared, large or multi-machine brains |
| Concurrency | single writer; kernel lock authoritative | normal multi-connection |
| Daemon/queue | cannot host the Minions daemon | can |

Scale guidance is inconsistent across docs (under 1,000 files, 7K+ pages, ~50K pages); the only hard measured bound found is PGLite's HNSW refusal at roughly 300k chunks of 1,024 dimensions (Reported). See [discrepancies](gbrain-doc-code-discrepancies.md).[^engines-doc][^readme]

**PGLite failure modes (Observed):** `PgliteBusyError` (`pglite_busy`, retryable; reasons `timeout|live_serve|legacy_owner_unverified`), `LegacyOwnerUnverifiedError` (not retryable; needs `gbrain pglite-repair --legacy-lock --dry-run`), `LiveServeLockError`. The kernel lock is authoritative; `.gbrain-lock` is diagnostic.[^pglite-lock] On PGLite, `sync` is delegated to the resident `serve` over authenticated IPC; `--no-delegate` does not allow opening an owned datastore; the stall watchdog `GBRAIN_SYNC_STALL_ABORT_SECONDS` defaults to 900 (Reported).[^serve-sync]

## Topologies and the thin client (Reported)

Three shapes keyed on which `~/.gbrain/config.json` (`GBRAIN_HOME`) is active: (1) single brain; (2) **cross-machine thin client** — `gbrain init --mcp-only` stores a `remote_mcp` block instead of a DB connection and `isThinClient(cfg)` is checked before `connectEngine`, so the empty local PGLite is never opened and local-only commands refuse; (3) split-engine per-worktree code engines. Shapes 2 and 3 stack.[^topologies][^thin-client]

## Canonical writers and generations (Reported)

- **Canonical writers:** managed persistence is an explicit activation boundary. Page bodies, frontmatter, visibility, tags, aliases, facts, takes, timeline and source identity require coordinator authority, enforced by SQL triggers that fail closed with `writer_coordinator_required`. A checked-in writer census (`canonical-writers.tsv`) plus a test rejects new write references; the native worktree lock plus database ownership rows grant authority while registry files and markers only refuse.[^canonical-writers]
- **Generations:** `publishGeneration` replaces the item set one input owns, recorded in `derived_generation*` ledger tables; at most one `live` and one `held` row per key, and held results write nothing. The tables exist in `schema.sql` (Observed); the doc's migration numbers v265/v266 are self-described placeholders.[^generations]

## Relationships

- Uses: [data model](gbrain-data-model-and-system-of-record.md) (schema and system of record), [retrieval](gbrain-retrieval-pipeline.md) (search runs above the engine).
- Feeds: [CLI and MCP surface](gbrain-cli-and-mcp-surface.md), [Minions](gbrain-minions-job-queue.md) (Postgres-native queue).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Architecture" (mermaid flowchart; "Two engines, one contract").
[^engine-ts]: `src/core/engine.ts::BrainEngine` (declaration at ~line 826; `kind` at ~828), counted by subagent.
[^operations-ts]: `src/core/operations.ts` (single registry); `src/core/ops/contract.ts` `Operation`; `src/core/operation-manifest.generated.ts`; `engine-factory.ts`, `engine-construct.ts:13,17`.
[^engines-doc]: `docs/ENGINES.md` "The interface", "Key design choices", "PGLiteEngine", "PGLite vector index ceiling", "When to use PGLite vs Postgres" (line ~572).
[^topologies]: `docs/architecture/topologies.md` (three shapes).
[^thin-client]: `docs/architecture/thin-client.md` (`remote_mcp`, `isThinClient`, `THIN_CLIENT_REFUSE_HINTS`).
[^canonical-writers]: `docs/architecture/canonical-writers.md`; `docs/ENGINES.md` "Writer-protocol fences"; migration v278 per subagent.
[^generations]: `docs/architecture/generations.md` "The ledger", "Publishing"; `src/schema.sql` lines ~1984–2044 (`derived_generation*`).
[^pglite-lock]: `src/core/pglite-lock.ts` lines 17–50.
[^serve-sync]: `docs/architecture/serve-sync-concurrency.md`.
