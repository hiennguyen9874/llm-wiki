---
type: Concept
title: MemHub memory modes, durable write queue and nightly evolve
description: How MemHub maps lite/pro/ultra onto SDK writes, schedules durable extraction jobs by event time with fairness rules, and runs nightly System 2 evolve.
tags: [memhub, memory-modes, write-queue, evolve, scheduling]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# MemHub memory modes, durable write queue and nightly evolve

MemHub turns the SDK's `lite|pro|ultra` into user-visible memory modes, writes through a durable queue (one job = one `add()`), and schedules System 2 evolve nightly in `ultra` (`memhub/docs/contracts/memory-mode-evolve-v1.md` §§1–6; `memhub/docs/ARCHITECTURE.md` "Write path").[^hy-memory]

## Modes

| Mode | Conversation becomes | Search reads |
|---|---|---|
| `lite` | embedded L1 raw batches, no model call | plain vector RAG over raw (active + shadow) |
| `pro` (default) | raw, then model extraction (System 1); raw → shadow | extracted facts/profile/intentions |
| `ultra` | pro + graph projection; nightly System 2 | pro lanes + schema/graph lanes |

(`memory-mode-evolve-v1.md` §1; `memory_server/config_state.py::ConfigDocument`.)[^hy-memory] Mode is read at claim time, not enqueue time; in-flight batches finish in their starting mode; switching never migrates or deletes; ultra→lower stops evolve; →ultra backfills graph facts once per user. "Sedimentation off" pauses only generation-model extraction, and lite is admitted without an active model (`memory-mode-evolve-v1.md` §2; `api.py::_sedimentation_claim_enabled`). Hand-added content in lite is saved raw and not backfilled after switching up.[^hy-memory] Raw retention is absolute: every mode keeps SDK L1 raw, one raw per complete turn, human user/assistant turns only, never tool output (`memhub/MEMORY.md` principles 4–5).[^hy-memory] See SDK semantics in [chat write path](hy-memory-chat-hierarchy-and-write-path.md).

## Durable queue and scheduling

- One queue row = one final conversation chunk with a frozen message payload; terminal success reaps the body but keeps IDs (`docs/contracts/memory-event-time-scheduling-v1.md` "Immutable job input and branches"; `memory_server/durable_queue.py::DurableWriteDrain`).[^hy-memory]
- Fixed 10-minute event-time windows anchored at the oldest eligible `event_at`; cross-harness concurrency inside a window, one job per harness; a **first-import barrier** blocks model claims until accepted history jobs are terminal, so many pending jobs with zero model calls is intentional (`memory-event-time-scheduling-v1.md`; `docs/PRODUCT_LOG_TROUBLESHOOTING.md` §4C).[^hy-memory]
- Fairness: 24 h fresh window, 90-day default extraction window (presets 3m/6m/1y/all), 4 fresh : 1 backlog share, one running job per conversation, per-harness caps, live lane first (`apps/core/src/one_memory/memory_queue.py` docstring, `free_to_run`).[^hy-memory]
- Clients are cached by (profile, revision, mode, features); a change retires stale handles while in-flight work finishes on the old key; feature flags are global, config-only and default-preserving (`memory-features-v1.md` §3).[^hy-memory]

## Nightly evolve

Evolve is ultra-only (`client.evolve` refuses other modes); MemHub owns locking, receipts and scheduling: async run, one per user, `EVOLVE_MAX_ROUNDS=20`, schedule checked every 300 s, default 03:00 local with catch-up after sleep, state persisted as counts/codes only in `evolve-state.json`. Users are enumerated from Core's own records because the SDK cannot list users (`apps/core/src/one_memory/memory_evolution.py` docstring; `memory-mode-evolve-v1.md` §§5–6). Mechanics of the evolve itself: [System 2](hy-memory-system2-evolution.md).[^hy-memory]

## Relationships

- Part of: [MemHub architecture](memhub-product-architecture.md).
- Uses: [System 2 evolution](hy-memory-system2-evolution.md); fed by [import adapters](memhub-import-adapters-and-live-sync.md).
- Blocked by: [embedding switches](memhub-embedding-space-switching.md) (model writes pause during a switch).

## Coverage and limits

Static inspection (delegated). Queue behaviour was derived from contracts and module docstrings; no runtime or load test.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
