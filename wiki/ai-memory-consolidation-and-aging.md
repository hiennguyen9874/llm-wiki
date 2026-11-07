---
type: Concept
title: ai-memory consolidation, aging and dream
description: How ai-memory turns sessions into pages (zero-LLM by default), and its decay formula, compaction, dedup, contradiction flagging, belief strength and opt-in dream pass.
tags: [agent-memory, ai-memory, consolidation, decay, aging]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: aging-design
    resource: ../raw/ai-memory/docs/design-memory-aging.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Memory aging design
  - id: decay-code
    resource: ../raw/ai-memory/crates/ai-memory-store/src/decay.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-store decay.rs
  - id: consolidate-code
    resource: ../raw/ai-memory/crates/ai-memory-consolidate/src/lib.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-consolidate crate (consolidator, sweep, dream, lint)
  - id: hooks-synth
    resource: ../raw/ai-memory/crates/ai-memory-hooks/src/synth.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Session page synthesis
---

# ai-memory consolidation, aging and dream

Consolidation turns captured observations into readable pages; aging decides which pages fade, compact or merge. The defining design choice: the default path needs **no LLM**, and anything that rewrites or drops content is opt-in and reversible by supersession.[^readme][^aging-design]

Evidence class: **Observed** for formulas and defaults (the decay constants were rechecked directly in `decay.rs` this session); other mechanics are **Observed by delegated inspection**; effectiveness is **Unverified**. `stale_after` is set because defaults shift across releases.

## Session → page

- **Zero-LLM default:** SessionEnd always writes a deterministic `sessions/<id>.md` from a bounded digest (first prompt as title, files touched, tool counts, a 500-line observation list = 250 head + 250 tail).[^hooks-synth]
- **LLM path (opt-in):** `consolidate_on_session_end` (default false) or manual `memory_consolidate`; emits 1–5 page updates of kinds Rule/Decision/Gotcha/Procedure/Fact. A `kind: rule` is routed to `_rules/<slug>.md`. Admission preflight runs before spending a completion; identical sha256 short-circuits; writes are new versions via supersession; budget 100k in / 32k out; ≤3 retries with `Retry-After` capped at 32 s.[^consolidate-code]
- Pre-compaction writes a rule-based checkpoint first and queues the provider job durably.[^consolidate-code]

## Decay formula and defaults

Retention is `salience · e^(−λΔt) + σ · ln(1+access) · e^(−μ · days_since_access) · breadth`, with defaults λ = 0.02 (≈35-day half-life), σ = 0.6, μ = 0.04, `salience_default` 1.0, `cold_threshold` 0.20, `hard_delete_after_days` 180; salience clamped to 0.25–2.0 in 0.25 steps (helpful/not-helpful step it; stale/wrong floor it).[^decay-code] Only `Tier::Episodic` pages decay; pinned pages are exempt; semantic/procedural are skipped; TTL `expires_at` hard-deletes regardless and runs first.[^consolidate-code] Opening, searching or link-reaching a page counts as access (async bump, ≤1 per page/operator per 60 s).[^consolidate-code][^readme]

## Sweep order

TTL + cold set → read-only dedup plan → per page compact or evict → dedup batch write → hard-delete tombstones older than 180 d → optional observation prune → optional ledger prune.[^consolidate-code]

## Opt-in aging features (all off by default)

| Feature | Behaviour |
| --- | --- |
| Compaction (`compact_cold_episodic`) | keep L0 `abstract:`, L1 first paragraph, L2 regex-kept tokens (file paths, error codes, decisions); `compacted_at` marker is terminal |
| Dedup (`dedup_cold_clusters`) | cosine DBSCAN over the cold set (`min_pts=2`, adaptive eps clamped at 0.15); survivor = highest retention; others superseded with a merge note; needs an embedder |
| Entropy filter (A4) | min 16 chars, 2.0 bits/char, repetition > 0.7 |
| Dream (`[dream] enabled`) | needs provider **and** embedder; idle window 300 s; cancels on activity; ≤8 clusters/run; dry-run first; sources superseded, never deleted |

[^consolidate-code][^aging-design] Contradiction flagging reports cosine similarity in a 0.4–0.75 band as an advisory `similarity_candidate` separately from explicit `contradiction` findings; it is O(N²) capped at 60 cold pages.[^consolidate-code]

**Belief strength** is a read-time confidence in [0, 0.95] from distinct sessions, recency and live `contradicts` edges; exposed in `explain`/`status`; the ranking weight `belief_authority_weight` defaults to 0.0.[^consolidate-code] **Curator** (`cold_episodic`, `stale_slot`, `duplicate_title`, `dangling_cross_project_link`) is report-only.[^consolidate-code]

The README reports compaction and dedup as reversible through retained git and page history; `restore-page` can recover retained versions. This is not a general guarantee of indefinite retention: the sweep also has TTL and hard-deletion paths (see [Data handling](ai-memory-data-handling-and-lifecycle-ops.md)).[^readme][^consolidate-code]

## Relationships

- Pages are written per [Wiki storage](ai-memory-wiki-storage-and-okf.md); ranking effect via [Retrieval pipeline](ai-memory-retrieval-pipeline.md).
- Adds proposals on top: [Auto-improvement](ai-memory-auto-improvement.md). Providers: [LLM and embedding providers](ai-memory-llm-and-embedding-providers.md).
- Docs drift (ARCHITECTURE tier table says procedural decays; code decays only episodic): [Source map and discrepancies](ai-memory-source-map-and-doc-discrepancies.md).

[^readme]: `../raw/ai-memory/README.md` — "It ages memory without an LLM", "It can also 'dream', if you let it".
[^aging-design]: `../raw/ai-memory/docs/design-memory-aging.md` — design record (A2/A3/A4/B1–B4 items); its migration-number and path references are stale.
[^decay-code]: `../raw/ai-memory/crates/ai-memory-store/src/decay.rs::DecayParams::default` (lines ~92–104: `lambda: 0.02, sigma: 0.6, mu: 0.04`), `lambda_from_half_life_days`.
[^consolidate-code]: `../raw/ai-memory/crates/ai-memory-consolidate/src/{consolidator.rs,sweep.rs,compaction.rs,cold_cluster.rs,dream.rs,lint.rs,curator.rs,entropy_filter.rs}` — e.g. `sweep.rs::is_decayable`, `consolidator.rs` retry/budget constants, `lint.rs` similarity band constants; read by a delegated agent (line numbers not recorded here).
[^hooks-synth]: `../raw/ai-memory/crates/ai-memory-hooks/src/synth.rs::synthesize_session_page`.
