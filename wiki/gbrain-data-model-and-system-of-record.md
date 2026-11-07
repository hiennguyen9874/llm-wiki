---
type: Concept
title: GBrain data model and system of record
description: GBrain's brain-vs-source axes, core tables, page anatomy (frontmatter, compiled truth, facts fence, timeline), size ceilings, schema packs and what is canonical Markdown versus DB-only.
tags: [agent-memory, gbrain, data-model, schema-packs]
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
  - id: schema-sql
    resource: ../raw/gbrain/src/schema.sql
    kind: code
    revision: 27f8b9d
    title: Fresh-install SQL schema
  - id: page-anatomy
    resource: ../raw/gbrain/docs/guides/page-anatomy.md
    kind: code
    revision: 27f8b9d
    title: Anatomy of a page
  - id: brains-and-sources
    resource: ../raw/gbrain/docs/architecture/brains-and-sources.md
    kind: code
    revision: 27f8b9d
    title: Brains and sources
  - id: system-of-record
    resource: ../raw/gbrain/docs/architecture/system-of-record.md
    kind: code
    revision: 27f8b9d
    title: System of record
  - id: schema-packs
    resource: ../raw/gbrain/docs/architecture/schema-packs.md
    kind: code
    revision: 27f8b9d
    title: Schema packs
  - id: type-taxonomy
    resource: ../raw/gbrain/docs/architecture/type-taxonomy.md
    kind: code
    revision: 27f8b9d
    title: Type taxonomy
  - id: page-size-policy
    resource: ../raw/gbrain/src/core/page-size-policy.ts
    kind: code
    revision: 27f8b9d
    title: Page size policy
  - id: page-body-limits
    resource: ../raw/gbrain/src/core/page-body/limits.ts
    kind: code
    revision: 27f8b9d
    title: Segmented page-body limits
---

GBrain's unit of knowledge is a Markdown page (path becomes slug) holding frontmatter, a rewritable *compiled truth*, an optional facts fence and an append-only *timeline*. Pages live in **sources** (named content repos) inside a **brain** (one database). For file-backed knowledge, the Markdown repo is the system of record and the database is a rebuildable index; some state is DB-only by design.[^page-anatomy][^system-of-record][^brains-and-sources] The engines that host this schema are in [architecture and engines](gbrain-architecture-and-engines.md); how pages become facts and takes is in the [memory model](gbrain-memory-model.md).

## Brain vs source (Reported)

- **Brain** = which database (PGLite file, self-hosted Postgres, Supabase); each has its own pages, chunks, OAuth surface and lifecycle. Routed by `--brain`, `GBRAIN_BRAIN_ID` or `.gbrain-mount`; mounts listed in `~/.gbrain/mounts.json`.
- **Source** = a named repo inside one brain; every `pages` row has `source_id`, and slug uniqueness is `(source_id, slug)`. Routed by `--source`, `GBRAIN_SOURCE`, `.gbrain-source` or a `sources.local_path` match.
- Rule of thumb: a different *data owner* means a different brain; same owner but different repo or topic means a different source. `schema.sql` confirms the `sources` table and the `pages_source_slug_key UNIQUE (source_id, slug)` constraint (Observed).[^brains-and-sources][^schema-sql]

## Core tables (Observed in `schema.sql`)

- `sources` (id, name, `local_path`, `last_commit`, `config` JSONB, chunker version, archive fields).
- `pages`: `source_id`, `slug`, `type`, `page_kind` ∈ markdown/code/image, `title`, `compiled_truth`, `timeline`, `frontmatter` JSONB, `content_hash`, `deleted_at` (soft delete), `effective_date`, `generation`, unique `(source_id, slug)`. About 17 further columns arrive from migrations, not the inline DDL, so reading only `schema.sql` gives an incomplete picture of the live table.
- `content_chunks`: `embedding vector(1536)` in the baseline DDL, `embedding_image vector(1024)`, `search_vector tsvector`, code-symbol columns. The seeded `config` rows still say `text-embedding-3-large` / 1536 while the code default for new installs is Voyage 1024; see [embeddings](gbrain-embeddings-and-providers.md).
- `links` (typed edges, `link_type`, `link_source`, `link_kind` plain/typed_ner), `tags`, `timeline_entries`, `page_versions`, `raw_data`, `ingest_log`, `config`.
- Auth and ops: `access_tokens`, `oauth_*`, `mcp_request_log`, `op_checkpoints`; derivation ledgers `derived_generation*`; purge ledgers `fact_purges`, `take_purges`, `page_purges`.[^schema-sql]

## Page anatomy (Reported, matching schema columns)

1. **Frontmatter:** `type`, `title`, `tags`, `aliases`, email(s), `visibility`, `status`, effective-date keys, plus gbrain-stamped `subtype`, `trust_tier`, `ingested_at`, `source_kind`, `ingested_via`.
2. **Compiled truth:** prose between frontmatter and the `<!-- timeline -->` sentinel; rewritten as understanding changes.
3. **Facts fence** between `<!--- gbrain:facts:begin -->` and `:end -->` with 10 written columns (claim, kind, confidence, visibility, notability, valid_from/until, source, context) and 5 optional (`claim_metric`, `claim_value`, `claim_unit`, `claim_period`, `attributed_to`).
4. **Timeline** below the sentinel as `- **YYYY-MM-DD** | Source — Summary` bullets; a takes fence holds holder (`who`) and weight.[^page-anatomy]

## System of record (Reported)

Three categories: **FS-canonical** (takes, facts, links, timeline, tags, `emotional_weight`, synthesis evidence), **derived from FS** (`pages`, `content_chunks`, `page_versions`), and **DB-only by design** (`raw_data`, OAuth/access tokens, `mcp_request_log`, the Minions queue, `op_checkpoint_paths`, the withdrawal ledger, belief ledger `belief_events`). A Markdown rebuild therefore starts with empty belief history; DB-only pages, unresolved facts and operational state need a database backup (README: "Markdown export is not a full database backup"). A CI guard `check:system-of-record` is wired in `package.json` (Observed).[^system-of-record][^readme]

## Size ceilings (Observed)

- `PAGE_MAX_BYTES` = 24 MiB inline ceiling for any ingress; `PAGE_INLINE_MAX_BYTES` = 1 MiB (segmented-storage threshold); `CODE_FILE_MAX_BYTES` = 5,000,000.
- Segmented ceilings: Postgres 256 MiB, PGLite 128 MiB; lead segment `BODY_LEAD_BYTES` 64 KiB. `ENGINES.md` mentions only the 128/256 MiB figures, so the 24 MiB and 1 MiB gates are easy to miss.[^page-size-policy][^page-body-limits]

## Schema packs and types (Reported)

A pack declares directories, page types, path→type inference and link verbs. Bundled: `gbrain-base-v2` (the 15-type default: 14 canonical plus `note`: person, company, media, tweet, social-digest, analysis, atom, concept, source, deal, email, slack, writing, project, note), `gbrain-base` (legacy 24 types), `gbrain-recommended` (13 extra directories) and lens packs (`gbrain-creator`, `-investor`, `-engineer`, `-everything`). Resolution is a seven-tier chain (call flag → env → per-source DB key → brain DB key → `gbrain.yml` → `~/.gbrain/config.json` → default). The tier-7 default is documented as `gbrain-base`, not v2, which conflicts with the README's "(default)" label for v2. `gbrain schema detect → suggest → review-candidates` proposes custom types from a filesystem; `gbrain jobs submit unify-types` migrates base → base-v2 (dry-run by default).[^schema-packs][^type-taxonomy][^readme]

## Relationships

- Used by: [retrieval](gbrain-retrieval-pipeline.md), [knowledge graph](gbrain-knowledge-graph.md), [sync and ingestion](gbrain-sync-and-ingestion.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Your brain's shape (schema packs)", "Architecture" ("Canonical files preserve file-backed knowledge"), "Troubleshooting".
[^schema-sql]: `src/schema.sql`: `sources` (~line 26), `pages` (~99; unique constraint ~172; migration-column comment ~173–180), `content_chunks` (~354), `links` (~549), `config` seed (~720).
[^page-anatomy]: `docs/guides/page-anatomy.md` (frontmatter, compiled truth, facts fence, timeline).
[^brains-and-sources]: `docs/architecture/brains-and-sources.md` "Brains (the DB axis)", "Rule of thumb".
[^system-of-record]: `docs/architecture/system-of-record.md` "The three categories"; `package.json` script `check:system-of-record`.
[^schema-packs]: `docs/architecture/schema-packs.md` "What ships in the box", "Resolution chain (7 tiers)".
[^type-taxonomy]: `docs/architecture/type-taxonomy.md` (14 canonical types plus `note`; subtype allowlist).
[^page-size-policy]: `src/core/page-size-policy.ts` lines 16, 26, 35.
[^page-body-limits]: `src/core/page-body/limits.ts` lines 44–57.
