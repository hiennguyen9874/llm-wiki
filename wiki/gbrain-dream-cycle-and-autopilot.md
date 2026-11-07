---
type: Concept
title: GBrain dream cycle and autopilot
description: The 31-phase maintenance cycle behind gbrain dream, autopilot and the autopilot-cycle job, including locking, scheduling, health checks and quiet hours.
tags: [agent-memory, gbrain, dream-cycle, autopilot, maintenance]
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
  - id: cycle-ts
    resource: ../raw/gbrain/src/core/cycle.ts
    kind: code
    revision: 27f8b9d
    title: Dream cycle runner
  - id: phase-table
    resource: ../raw/gbrain/src/core/cycle/phase-table.ts
    kind: code
    revision: 27f8b9d
    title: Cycle phase table
  - id: autopilot-ts
    resource: ../raw/gbrain/src/commands/autopilot.ts
    kind: code
    revision: 27f8b9d
    title: autopilot command
  - id: cron-schedule
    resource: ../raw/gbrain/docs/guides/cron-schedule.md
    kind: code
    revision: 27f8b9d
    title: Cron schedule guide
  - id: dream-patterns
    resource: ../raw/gbrain/docs/guides/dream-patterns.md
    kind: code
    revision: 27f8b9d
    title: Dream patterns guide
  - id: facts-drain
    resource: ../raw/gbrain/docs/guides/facts-drain.md
    kind: code
    revision: 27f8b9d
    title: Facts drain guide
---

GBrain's "dream cycle" is the overnight maintenance loop the README describes as dedup, citation repair, salience scoring, contradiction finding and next-day prep.[^readme] In code it is one primitive, `runCycle()` in `src/core/cycle.ts`, called three ways: `gbrain dream` (one-shot, intended for nightly cron), `gbrain autopilot` (daemon) and the `autopilot-cycle` [Minions](gbrain-minions-job-queue.md) handler.[^cycle-ts]

## Phases (Observed: `ALL_PHASES`, 31 entries; order is load-bearing)

`lint, backlinks, sync, fence_repair, content_repair, unindexed_files, synthesize, extract, extract_facts, extract_atoms, resolve_symbol_edges, patterns, synthesize_concepts, recompute_emotional_weight, consolidate, propose_takes, grade_takes, calibration_profile, edge_contradictions, claim_conflicts, drift, standing_questions, chronicle, facts_drain, conversation_facts_backfill, enrich_thin, skillopt, embed, orphans, schema-suggest, purge`.

Per-phase comments note that `drift` and `skillopt` default OFF (skillopt caps: $0.50 per skill, $2.00 per brain). `phase-table.ts` classifies each phase for managed brains as `writes | no_coordinated_write | managed_skip`.[^cycle-ts][^phase-table] These phases touch the [memory model](gbrain-memory-model.md) (`consolidate`, `propose_takes`, `grade_takes`, `claim_conflicts`), [sync](gbrain-sync-and-ingestion.md) (`sync`, `purge`), [skills tooling](gbrain-skills-and-resolver.md) (`skillopt`) and [embeddings](gbrain-embeddings-and-providers.md) (`embed`).

## Locking and scheduling

- **Lock:** Postgres row in `gbrain_cycle_locks` (30 min TTL, works through PgBouncer); PGLite or no-engine runs use `~/.gbrain/cycle.lock`. Read-only phase selections skip the lock. A parallel `gbrain dream` beside autopilot shares the brain-wide `gbrain-cycle` lease and the loser skips phases as `maintenance_lock_busy` (Reported).[^cycle-ts][^cron-schedule]
- **Schedule:** the `autopilot --interval` flag defaults to 300 s (Observed); docs describe an adaptive 150–600 s tick (Reported). Autopilot submits one `autopilot-cycle` job per interval with an idempotency key so slow cycles do not stack.[^autopilot-ts]
- **Health/remediation (files Observed, semantics Reported):** bounded `getHealth()` reads where a server-side timeout means "degraded", not a failed cycle; a full-cycle freshness floor of 60 minutes; `gbrain autopilot --status` exit codes 0/1/2 are the cron signal; self-upgrade lives in the same daemon and respects quiet hours.[^autopilot-ts]
- **Quiet hours** are gated at job claim time; see [Minions](gbrain-minions-job-queue.md).

## Notable behaviors

- **Facts drain:** extraction queues one `facts-absorb` job per eligible page write; drained by the Postgres worker, a PGLite serve or the `facts_drain` phase, with $1.00 per run and $5.00 per day caps; drained jobs return to the queue without burning an attempt (Reported).[^facts-drain]
- **Never-lost work:** connector and pattern phases persist `grounding_appends.<source>` as the only copy of unverified timeline entries (Reported). `appended_unverified` is documented as deprecated "two releases after this one" — an undated relative marker still present at this version.[^dream-patterns]
- **Cron discipline:** every cron or daemon call must go through one wrapper exporting `GBRAIN_HOME`, to avoid no-brain, second-host and stale-DB failure classes (Reported).[^cron-schedule]

## Doc drift

`cron-schedule.md` lists only "lint, backlinks, extract, sync, embed, synthesize" in a different order; the code runs 31 phases with `sync` third and `extract` eighth (Observed by subagent). See [discrepancies](gbrain-doc-code-discrepancies.md).

## Relationships

- Runs on: [Minions](gbrain-minions-job-queue.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "What it does (the loop)" ("Cron-driven enrichment runs while you sleep") and intro.
[^cycle-ts]: `src/core/cycle.ts` lines 1–46 (callers, lock), 128 (`ALL_PHASES`), 1931 (`runCycle`); `src/core/minions/handlers/autopilot-cycle.ts:1-25`.
[^phase-table]: `src/core/cycle/phase-table.ts` lines 1–70.
[^autopilot-ts]: `src/commands/autopilot.ts` lines 1–11, 1338; `autopilot-health.ts`, `autopilot-remediation-policy.ts` headers.
[^cron-schedule]: `docs/guides/cron-schedule.md` (phase list; `maintenance_lock_busy`; `GBRAIN_HOME` wrapper).
[^dream-patterns]: `docs/guides/dream-patterns.md` (deprecation note on `appended_unverified`).
[^facts-drain]: `docs/guides/facts-drain.md`.
