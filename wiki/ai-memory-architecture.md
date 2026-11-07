---
type: Concept
title: ai-memory architecture and crates
description: Data flow, 11-crate layout, SQLite single-writer storage, data directory and the cross-cutting invariants of ai-memory 3.4.2.
tags: [agent-memory, ai-memory, architecture, rust, sqlite]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: architecture
    resource: ../raw/ai-memory/docs/ARCHITECTURE.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ARCHITECTURE.md
  - id: cargo
    resource: ../raw/ai-memory/Cargo.toml
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Workspace Cargo.toml
  - id: store-code
    resource: ../raw/ai-memory/crates/ai-memory-store/src/lib.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-store crate (lib.rs, writer.rs, migrations.rs)
  - id: repo-agents
    resource: ../raw/ai-memory/AGENTS.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Repository AGENTS.md (contributor contract)
  - id: changelog
    resource: ../raw/ai-memory/CHANGELOG.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: CHANGELOG.md
---

# ai-memory architecture and crates

ai-memory is one Rust binary that runs an MCP/HTTP server and owns one data directory. Hooks POST observations; the server serializes all writes through a single SQLite writer, compiles session observations into markdown pages, and serves retrieval from derived indexes.[^readme][^architecture] Markdown files are primary and SQLite is derived, with no cross-resource transaction between them.[^architecture]

Evidence class: **Observed** by delegated static inspection of docs and crate sources at the pinned revision (see [Source map](ai-memory-source-map-and-doc-discrepancies.md)); no code was executed.

## Data directory

`<data_dir>/` holds `wiki/` (git-versioned markdown source of truth), `raw/` (immutable sanitized managed-workstream transcript segments), `db/` (SQLite incl. FTS5, entities, embeddings), `models/` (local embedding models) and `logs/`; the CLI default is `dirs::data_local_dir()/ai-memory` (≈ `~/.local/share/ai-memory` on Linux).[^readme][^architecture] The DB file is `db/memory.sqlite`.[^store-code]

## Crate layout (workspace of 11 members + `evals`)

The workspace sets `resolver = "3"`, `unsafe_code = "forbid"`, `missing_docs = "warn"`.[^cargo] The crate graph is acyclic.[^architecture]

| Crate | Responsibility |
| --- | --- |
| `ai-memory-core` | Domain vocabulary, no IO: ids/`PagePath`, `Tier`, OKF conformance, `Sanitizer`/`Sanitized<T>`, actor, handoff, message, user, workstream types[^store-code] |
| `ai-memory-store` | SQLite layer: `Store`, single `WriterHandle`, `ReaderPool`, refinery migrations, decay, belief, ops, reader, scope, project authz, FTS query building[^store-code] |
| `ai-memory-wiki` | Markdown source of truth: atomic writes, frontmatter, libgit2 checkpoints, file watcher, admission webhooks, backup, wiki migrations |
| `ai-memory-llm` | LLM and embedding providers, fallback, local embedder |
| `ai-memory-consolidate` | Consolidator, sweep/decay, lint, curator, dream, auto-improve |
| `ai-memory-hooks` | Hook router, capture policy, session synthesis, handoff rendering |
| `ai-memory-mcp` | MCP server (27 `memory_*` tools), auth, admin routes |
| `ai-memory-web` | Built-in web UI, `/api/v1`, management UI |
| `ai-memory-workstream` | Managed-workstream and harness adapters |
| `ai-memory-cli` | The `ai-memory` binary and all subcommands |
| `ai-memory-test-support` | Test helpers |

Layering is described in `docs/ARCHITECTURE.md`; per-crate responsibilities beyond `core`/`store` come from that doc and crate listings (**Reported** by the doc, listings **Observed**).[^architecture]

## Storage mechanics

- **Writer actor:** one dedicated OS thread owns the writer `Connection`; callers send commands over an `mpsc` channel of 1024 with `oneshot` replies. Readers use a read-only pool capped at 4 connections.[^store-code]
- **SQLite pragmas:** WAL, `journal_size_limit` 64 MiB, `synchronous=NORMAL`, `busy_timeout` 5000 ms, immediate transactions.[^store-code]
- **Migrations:** 101 embedded `refinery` migrations, head **V101** (`V101__handoff_manual_flag.sql`); divergent or missing history aborts, a schema-ahead DB yields `DataSchemaAhead` (verified by listing the migrations directory: 101 files).[^store-code]
- **Core tables** from `V01__init.sql`: `workspaces`, `projects`, `pages` (versioned), `sessions`, `observations`, `links`, `audit_log`; later additions include entities (V38), page windows (V62), `page_evidence` (V63), `agent_messages` (V64), `query_page_signals` (V98), `observations.file_path` (V99).[^store-code]
- **FTS5:** external-content `pages_fts` with tokenizer `unicode61 remove_diacritics 2 tokenchars '_-'`, plus generated `*_parts` columns so hyphen/underscore components match, and CJK bigram companion indexes (V100). V100 reportedly doubles FTS size.[^store-code][^changelog]
- Vectors are packed and scanned in Rust; `sqlite-vec` is not a dependency (see discrepancies).

## Cross-cutting invariants (from ARCHITECTURE.md)

Markdown primary / SQLite derived; a single-writer actor; indexes commit with the data; identity is the 3-tuple `(workspace_id, project_id, path)`; `Sanitized<NewObservation>` is the only constructor path for observations (privacy as a typed boundary); embeddings carry `{provider, model, dim}`; atomic tmp+rename+fsync file writes; a zero-LLM default path.[^architecture] The contributor contract (`AGENTS.md`, "Cross-cutting invariants (do not violate)") numbers at least 16 — additionally one config-read path, hooks fire-and-forget and bounded, JSON-schema-only LLM outputs, a live-process check before direct-disk lifecycle ops, an absolute canonical data dir, no global singletons, provider auth resolved before construction, and multi-session/multi-user access as a core concern (read directly this session; see also [Distribution, CI and companions](ai-memory-distribution-ci-and-companions.md)).[^repo-agents]

## Relationships

- Storage format details: [Wiki storage, OKF, typed edges, temporal](ai-memory-wiki-storage-and-okf.md).
- Ranking over these indexes: [Retrieval pipeline](ai-memory-retrieval-pipeline.md).
- Decay constants and sweeps: [Consolidation and aging](ai-memory-consolidation-and-aging.md).
- Overview: [ai-memory overview](ai-memory-overview.md).

[^readme]: `../raw/ai-memory/README.md` — "Architecture" (data dir tree and retrieval summary).
[^architecture]: `../raw/ai-memory/docs/ARCHITECTURE.md` — "Data flow", "Storage architecture", "Crate layout", "Cross-cutting invariants", "MCP tool surface (27 tools)".
[^cargo]: `../raw/ai-memory/Cargo.toml::[workspace]`, `[workspace.lints]`, `[workspace.package]`.
[^store-code]: `../raw/ai-memory/crates/ai-memory-store/src/lib.rs::Store::open, DB_FILENAME, READER_POOL_SOFT_CAP`; `src/writer.rs` module doc (writer actor, channel 1024); `src/migrations.rs::run`; `migrations/V01__init.sql`, `V100` (FTS parts); `crates/ai-memory-core/src/lib.rs` module docs; `crates/ai-memory-wiki/src/lib.rs`.
[^repo-agents]: `../raw/ai-memory/AGENTS.md` — "Cross-cutting invariants (do not violate)" (numbered list 1–16, from about line 479).
[^changelog]: `../raw/ai-memory/CHANGELOG.md` — `[Unreleased]` and recent release notes on the V100 index migration (read by a delegated agent; heading-level locator only, exact line unavailable).
