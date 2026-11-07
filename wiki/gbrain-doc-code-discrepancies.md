---
type: Concept
title: GBrain doc/code discrepancies
description: Consolidated list of places where GBrain's documentation, comments and code disagree or are stale at revision 27f8b9d, with which side the evidence favors.
tags: [agent-memory, gbrain, discrepancies, staleness]
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
  - id: engines-doc
    resource: ../raw/gbrain/docs/ENGINES.md
    kind: code
    revision: 27f8b9d
    title: Engines design document
  - id: defaults-ts
    resource: ../raw/gbrain/src/core/ai/defaults.ts
    kind: code
    revision: 27f8b9d
    title: AI defaults
  - id: surface-ts
    resource: ../raw/gbrain/src/mcp/surface.ts
    kind: code
    revision: 27f8b9d
    title: MCP surfaces
  - id: manifest
    resource: ../raw/gbrain/skills/manifest.json
    kind: code
    revision: 27f8b9d
    title: Skills manifest
  - id: cron-schedule
    resource: ../raw/gbrain/docs/guides/cron-schedule.md
    kind: code
    revision: 27f8b9d
    title: Cron schedule guide
  - id: belief-ledger-design
    resource: ../raw/gbrain/docs/designs/BELIEF_LEDGER.md
    kind: code
    revision: 27f8b9d
    title: Belief ledger design
  - id: schema-packs
    resource: ../raw/gbrain/docs/architecture/schema-packs.md
    kind: code
    revision: 27f8b9d
    title: Schema packs
  - id: retrieval-doc
    resource: ../raw/gbrain/docs/architecture/RETRIEVAL.md
    kind: code
    revision: 27f8b9d
    title: Retrieval architecture
  - id: shell-jobs-doc
    resource: ../raw/gbrain/docs/guides/minions-shell-jobs.md
    kind: code
    revision: 27f8b9d
    title: Minions shell jobs guide
---

At this snapshot the GBrain repository is large and fast-moving, and its prose docs lag its code in many small ways. This page collects the discrepancies found during ingest so a reader can weigh a claim before relying on it. Unless stated, each item was found by a subagent reading both sides; items the curator re-checked directly are marked **(curator-checked)**. In every case the *code* is the better evidence for current behavior, and where only docs exist the claim stays Reported. These are preliminary static observations: documentation and implementation can reflect different contexts, and apparent contradictions warrant investigation before selecting a winner.

## Counts and defaults

| Item | Doc/comment says | Code says | Page |
| --- | --- | --- | --- |
| Embedding dimension default comment in `ai/dims.ts` | 1536 (OpenAI default) | `DEFAULT_EMBEDDING_DIMENSIONS = 1024`, model `voyage:voyage-4` **(curator-checked)** | [embeddings](gbrain-embeddings-and-providers.md) |
| Reranker default in the provider guide's init section | `voyage:rerank-2.5` | `voyage:rerank-3-lite` **(curator-checked)** | [embeddings](gbrain-embeddings-and-providers.md) |
| Rerank price range in `RETRIEVAL.md` | ~$0.025–0.05/M | $0.02 (lite) and $0.05 | [embeddings](gbrain-embeddings-and-providers.md) |
| `BrainEngine` size | "100+ methods" | 187 signatures | [architecture](gbrain-architecture-and-engines.md) |
| Operation count | "100+ operations" | 194 manifest entries, 171 non-`localOnly` | [CLI and MCP](gbrain-cli-and-mcp-surface.md) |
| Starter MCP surface size | `surface.ts` header says "~20-op" | 41 members; generated catalog says ~41 [^surface-ts] | [CLI and MCP](gbrain-cli-and-mcp-surface.md) |
| Skill count | "50+" in `GBRAIN_SKILLPACK.md`; "~100" in a task brief | 75 **(curator-checked)** | [skills](gbrain-skills-and-resolver.md) |
| `skills/manifest.json` version | `0.32.3.0` | project `VERSION` is `0.60.593.0` | [skills](gbrain-skills-and-resolver.md) |
| Autopilot interval | adaptive 150–600 s in docs | CLI default flat 300 s | [dream cycle](gbrain-dream-cycle-and-autopilot.md) |
| Dream phase list in `cron-schedule.md` | 6 phases, `extract` before `sync` | 31 phases, `sync` third, `extract` eighth | [dream cycle](gbrain-dream-cycle-and-autopilot.md) |

## Scale and storage guidance

PGLite capacity is stated four ways: under 1,000 files (`ENGINES.md`), "1000+ files → Supabase" (`CLAUDE.md`, topologies), a 7K+ page power-user tier, and "up to ~50K pages" (README). The only measured hard bound is the PGLite HNSW refusal near 300k chunks of 1,024 dims. `ENGINES.md` also omits the 24 MiB ingress and 1 MiB segmentation thresholds from its page-size comparison.[^engines-doc][^readme] See [architecture](gbrain-architecture-and-engines.md) and [data model](gbrain-data-model-and-system-of-record.md).

## Schema packs and types

- The README labels `gbrain-base-v2` as the default, while the 7-tier resolution chain's last tier is documented as `gbrain-base`.
- The per-source pack key is written `schema_pack:source:<id>` in the tier table and `schema_pack.source.<id>` elsewhere in the same file; code and key-file docs use the dot form.
- "14 canonical types", "14 plus `note`" and "15 types" are used interchangeably.[^schema-packs]
- `schema.sql` omits ~17 `pages` columns and ~10 `content_chunks` columns that migrations add, and seeds `text-embedding-3-large` / 1536 while new installs default to Voyage 1024.[^defaults-ts]

## Status lines and design docs

- `BELIEF_LEDGER.md` says "design, not built", yet `src/core/belief/` (20 modules), migration v249 and `gbrain beliefs` exist.[^belief-ledger-design]
- `calibration-quality-gate-spec.md` calls itself "largely unshipped" and no `falsifiability` identifier exists in `src/` — here the doc is correct.
- `generations.md` migration numbers v265/v266 are self-described placeholders.
- `compiled-truth.md` pseudocode (`timeline-add`, `put … { compiled_truth }`) does not match `put_page`'s full-`content` signature.
- `takes resolve` help text lists three `--quality` values while the DB and mutation code accept `unresolvable` too.

## Operations and process

- Shell-job gating: one guide says the handler is "disabled at worker startup", the other "always registered, guarded"; semantics agree.[^shell-jobs-doc]
- Two unrelated "quiet hours" mechanisms share one name (Minions claim-time gate; harness file-spool).
- `RETRIEVAL.md` carries a self-correction: the old P@5 49.1% headline is "do not cite".[^retrieval-doc]
- `cache_enabled: true` in every mode bundle versus semantic caching being disabled in practice.
- `docs/tutorials/company-brain.md` heading "Two scoping models" lists three; port examples differ (3131 vs 8787).
- `DESIGN.md` is the admin UI design system, not an architecture doc.
- `dbg-tmp.ts` is a stray root script with a machine-specific path; the CHANGELOG has duplicate version headings.

## Skills and docs hygiene

Six skills have bare `brain_first: exempt`; `RESOLVER.md` embeds a generated block despite the README saying no machine-managed block exists; the deprecated `twilio-voice-brain` recipe is still linked as current from `GBRAIN_SKILLPACK.md`; two identity-template sets coexist; production-brain figures differ across `README.md`, `ORIGIN.md` and `GBRAIN_SKILLPACK.md`.[^manifest][^cron-schedule]

## Time-sensitive markers to re-check on a new revision

`skillopt --loop` removal on/after 2026-12-03; `appended_unverified` deprecation "two releases after this one"; benchmark numbers from v0.48.4.0; the 41-op starter surface and 194-op full surface; default embedding and reranker models.

## Relationships

- Qualifies claims in: [architecture](gbrain-architecture-and-engines.md), [retrieval](gbrain-retrieval-pipeline.md), [embeddings](gbrain-embeddings-and-providers.md), [CLI and MCP](gbrain-cli-and-mcp-surface.md), [skills](gbrain-skills-and-resolver.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` line ~329 ("personal brains up to ~50K pages") and the `gbrain-base-v2 (default)` bullet.
[^engines-doc]: `docs/ENGINES.md` line ~572 ("< 1,000 files") and the PGLite-vs-Postgres comparison table.
[^defaults-ts]: `src/core/ai/defaults.ts` lines 15–19; `src/core/ai/dims.ts` comment and `src/core/embedding-pricing.ts:52-55` via subagent.
[^surface-ts]: `src/mcp/surface.ts` header comment ("~20-op daily-driver set") versus `STARTER_OPS`.
[^manifest]: `skills/manifest.json#version`; `skills/_AGENT_README.md`; `docs/GBRAIN_SKILLPACK.md`.
[^cron-schedule]: `docs/guides/cron-schedule.md` phase list and interval wording; `src/core/cycle.ts::ALL_PHASES`.
[^belief-ledger-design]: `docs/designs/BELIEF_LEDGER.md:3`; `docs/architecture/key-files/belief-ledger.md`.
[^schema-packs]: `docs/architecture/schema-packs.md` lines ~70 and ~156 (key spelling), "What ships in the box".
[^retrieval-doc]: `docs/architecture/RETRIEVAL.md` "The benchmark" ("do not cite").
[^shell-jobs-doc]: `docs/guides/minions-shell-jobs.md` versus `docs/guides/minions-deployment.md` precondition 4.
