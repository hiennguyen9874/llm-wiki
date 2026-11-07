---
type: Concept
title: ai-memory wiki storage, OKF mapping, typed edges and temporal queries
description: How ai-memory stores pages (tiers, kinds, versioning, git checkpoints), maps frontmatter to OKF v0.2, models typed edges, and answers as_of queries.
tags: [agent-memory, ai-memory, okf, wiki, storage, temporal]
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
  - id: okf
    resource: ../raw/ai-memory/docs/okf.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: OKF design and field mapping
  - id: typed-edges
    resource: ../raw/ai-memory/docs/typed-edges.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Typed edges
  - id: temporal
    resource: ../raw/ai-memory/docs/temporal.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Temporal (as_of) queries
  - id: wiki-migrations
    resource: ../raw/ai-memory/docs/wiki-migrations.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Wiki migrations
  - id: core-code
    resource: ../raw/ai-memory/crates/ai-memory-core/src/okf.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-core okf.rs / page.rs
  - id: wiki-code
    resource: ../raw/ai-memory/crates/ai-memory-wiki/src/markdown.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-wiki markdown.rs / git.rs
---

# ai-memory wiki storage, OKF mapping, typed edges and temporal queries

ai-memory's memory is a git-versioned directory of markdown pages; each page has JSON-like YAML frontmatter and a body, and the SQLite index is rebuilt from the files.[^readme] The wiki is natively an Open Knowledge Format (OKF) v0.2 bundle: a single function conforms every written page's frontmatter to OKF.[^okf][^core-code] This is the same OKF family that this repository's own `AGENTS.md` contract uses for its wiki (see [overview](ai-memory-overview.md)).

Evidence class: **Observed** (static inspection of docs and code) unless noted; nothing executed.

## Page model

- Frontmatter keys: `tier` (strictly `working|episodic|semantic|procedural`), `pinned`, `kind` (`rule|decision|gotcha|procedure|fact`), `slot_kind` (`state|invariant`), `entities`/`tags`, `expires_at`, `relations`.[^wiki-code][^core-code]
- Tiers are a single `pages.tier` column, not separate tables.[^core-code]
- The parser accepts only a leading `---` fence (LF or CRLF, BOM stripped).[^wiki-code]
- Identity is `(workspace_id, project_id, path)`; `portable_page_key` is lowercase + NFC.[^core-code]

## Versioning and git

Writing new content supersedes the old row in one transaction (`is_latest=0`, `valid_to` set); an identical body hash, frontmatter (ignoring `generated.at`) and title/tier/pinned is a no-op returning the same page id.[^core-code] Each write also creates a libgit2 checkpoint (author `ai-memory <ai-memory@local>`, object fsync via a dedicated git config), so history is recoverable with `restore-page`.[^wiki-code]

## OKF v0.2 mapping

`conform_frontmatter` fills `type` (from path family or `kind`/`slot_kind`), `description` ← `summary`, `stale_after` ← `expires_at` (date-only → end of UTC day), `sources` ← `session_id`/`agent` (`process:<agent>`), and `generated.by` ← `generated_by_model` else `process:ai-memory/<ver>`; `generated.at` is stamped only on real change.[^core-code][^okf] Wiki-structure migrations are tracked in a `wiki_migrations` table with a downgrade guard (`NewerWikiFormat`); the registry currently holds one migration, `OkfConformance`.[^wiki-migrations][^wiki-code]

## Typed edges

A closed vocabulary — `causes`, `fixes`, `contradicts` — is declared in frontmatter `relations:` and stored in `links.link_type` (default `references`), so no schema change was needed. Unknown keys are skipped with a warning; targets share wikilink grammar (`path`, `project:path`, `workspace/project:path`, `_global:path`) and gain `.md` when extension-less. Edges ride the retrieval graph without relation-specific weight; `contradicts` feeds `memory_lint`.[^typed-edges][^core-code]

## Temporal (`as_of`) queries — "bi-temporal-lite"

Only **ingestion time** is modelled. Link grain uses `entity_page_links.valid_from/superseded_at`; page grain uses `pages.valid_from/valid_to` (V62, backfilled in chunks at boot). An `as_of` search fuses an entity-timeline stream with a version-filtered FTS stream using RRF (k = 60); it has no vector, graph or raw-observation legs, works on a single project only, and refuses `global`/`scopes`.[^temporal] Entities derive from frontmatter `entities` plus `tags`.[^temporal][^core-code]

## Relationships

- Part of [ai-memory architecture](ai-memory-architecture.md); ranking behaviour in [Retrieval pipeline](ai-memory-retrieval-pipeline.md).
- Aging rewrites pages via supersession: [Consolidation and aging](ai-memory-consolidation-and-aging.md).
- Documentation drift on OKF `kind` mapping: [Source map and discrepancies](ai-memory-source-map-and-doc-discrepancies.md).

[^readme]: `../raw/ai-memory/README.md` — "Why ai-memory" (plain markdown), "Architecture".
[^okf]: `../raw/ai-memory/docs/okf.md` — "Field mapping" section.
[^typed-edges]: `../raw/ai-memory/docs/typed-edges.md` — whole document (vocabulary, storage, retrieval effect).
[^temporal]: `../raw/ai-memory/docs/temporal.md` — whole document (grain, RRF fusion, limits).
[^wiki-migrations]: `../raw/ai-memory/docs/wiki-migrations.md` — framework description.
[^core-code]: `../raw/ai-memory/crates/ai-memory-core/src/okf.rs::conform_frontmatter, OKF_VERSION, strip_generated_at, derive_type`; `src/page.rs::Tier, Relation, frontmatter_entity_names`; `src/ids.rs::portable_page_key`; store `ops.rs::upsert_page_in_tx`; `migrations/V62__page_ingestion_windows.sql`.
[^wiki-code]: `../raw/ai-memory/crates/ai-memory-wiki/src/markdown.rs::parse, extract_relation_links`; `src/git.rs::COMMIT_AUTHOR_*, FSYNC_OBJECT_FILES`; `src/wiki.rs::page_metadata`; `src/migrations/runner.rs`, `mod.rs::registry`.
