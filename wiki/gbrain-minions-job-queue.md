---
type: Concept
title: GBrain Minions job queue
description: How GBrain's Postgres-native Minions queue stores jobs, moves them through states, survives worker crashes, runs shell jobs and gates quiet hours.
tags: [agent-memory, gbrain, job-queue, minions, operations]
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
  - id: queue-ts
    resource: ../raw/gbrain/src/core/minions/queue.ts
    kind: code
    revision: 27f8b9d
    title: MinionQueue
  - id: types-ts
    resource: ../raw/gbrain/src/core/minions/types.ts
    kind: code
    revision: 27f8b9d
    title: Minions types
  - id: worker-ts
    resource: ../raw/gbrain/src/core/minions/worker.ts
    kind: code
    revision: 27f8b9d
    title: MinionWorker
  - id: deployment-doc
    resource: ../raw/gbrain/docs/guides/minions-deployment.md
    kind: code
    revision: 27f8b9d
    title: Minions deployment guide
  - id: shell-jobs-doc
    resource: ../raw/gbrain/docs/guides/minions-shell-jobs.md
    kind: code
    revision: 27f8b9d
    title: Minions shell jobs guide
  - id: runbook
    resource: ../raw/gbrain/docs/guides/queue-operations-runbook.md
    kind: code
    revision: 27f8b9d
    title: Queue operations runbook
  - id: quiet-hours-ts
    resource: ../raw/gbrain/src/core/minions/quiet-hours.ts
    kind: code
    revision: 27f8b9d
    title: Minions quiet hours gate
---

Minions is GBrain's Postgres-native, BullMQ-inspired job queue (`MinionQueue` plus `MinionWorker`). It runs autopilot cycles, connector syncs, embedding backfills, shell jobs and sub-agent runs, and the README presents `gbrain agent run` as exposing the brain surface to a sub-agent "through the Minions queue, with crash-safe two-phase persistence".[^queue-ts][^readme] PGLite cannot host the worker daemon because of its exclusive file lock, so a durable queue implies Postgres or a resident `serve` (Reported).[^shell-jobs-doc]

## Storage and states

- Tables `minion_jobs` (params JSONB, `lock_until`, `delay_until`, `parent_job_id`), `minion_inbox`, attachments and `subagent_tool_executions` (a two-phase tool ledger).[^queue-ts]
- States (Observed in `types.ts`): `waiting | active | completed | failed | delayed | dead | cancelled`, plus SQL-only `waiting-children` and `paused`. Terminal set: completed, failed, dead, cancelled. Handler errors: `UnrecoverableError` goes straight to `dead`; also `JobDeferredError` and `RateLeaseUnavailableError`. Deletion is only allowed from terminal states.[^types-ts][^queue-ts]

## Workers and crash safety

- **Worker:** an in-process promise pool of `concurrency`, a per-job `AbortController` and a lock-renewal timer (Observed).[^worker-ts] `gbrain jobs supervisor` is the canonical wrapper: PID file, exponential restart 1 s→60 s, 35 s drain then SIGKILL, distinct exit codes (worker exit 16 = `configuration_blocked`). `--job-isolation process` runs each job in a child process; `--max-rss` caps worker and child trees (Reported).[^deployment-doc]
- **Leases:** lock token plus `lock_until`; reclaim after expiry with a 15 s grace; a failed lock renewal triggers a fenced "verify-before-evict" re-check rather than assuming loss; a stall sweeper reclaims; wall-clock eviction at 2× `timeout_ms`; a DB-liveness probe returns `pool_starved | server_unreachable | unknown`. In process-isolation mode the child reports one atomic outcome file and the lock token fences its queue writes into no-ops (Observed in code structure; semantics Reported).[^queue-ts][^runbook]
- **Lanes:** long jobs (`autopilot-cycle`, `autopilot-global-maintenance`, `embed-backfill`, `connector-sync`, `extract`) are confined to `N − minions.short_job_reserved_slots` at concurrency ≥ 2 (Reported).
- **Admission control:** params coalescing, a waiting TTL (default 48 h for `subagent`), optional waiting quota and a divergence check (ratio 2, min-waiting 50) in `admission.ts` (file Observed; semantics Reported).[^deployment-doc]
- **Wedge handling (Reported):** a worker alive but claiming nothing self-heals through a DB-probe self-exit (~3 min) or supervisor restart after 15 minutes without completions, with a loop breaker of 3 wedge restarts per 30 minutes.[^runbook]

## Shell jobs (Reported)

The `shell` handler runs `{cmd, cwd}` with a minimal environment allowlist (`PATH, HOME, USER, LANG, TZ, NODE_ENV`) and a JSONL audit log. Two independent gates apply: MCP/remote callers can never submit shell jobs, and the worker must be started with `--allow-shell-jobs` or `GBRAIN_ALLOW_SHELL_JOBS=1` or the job dies unrecoverably. `inherit: ["database_url"]` stores names only and resolves at child spawn. There is no filesystem sandbox, so `cwd` is the trust boundary. The two docs word the registration differently ("disabled at worker startup" vs "always registered, guarded"); semantics agree.[^shell-jobs-doc][^deployment-doc]

## Quiet hours

The Minions gate is evaluated at **claim** time (`allow | skip | defer`), uses an IANA timezone and is a pure function (Observed). A separate harness-side spool pattern in `quiet-hours.md` shares the name but is a different mechanism.[^quiet-hours-ts]

## Dangerous operations

`gbrain jobs delete <id>` (last resort), shell jobs, and process isolation sized for `concurrency` instead of `(concurrency+1) × cap` memory (Reported).[^runbook]

## Relationships

- Hosts: [dream cycle and autopilot](gbrain-dream-cycle-and-autopilot.md), connector syncs in [sync and ingestion](gbrain-sync-and-ingestion.md).
- Depends on: [architecture and engines](gbrain-architecture-and-engines.md) (Postgres engine).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Two ways to query your brain" (`gbrain agent run`).
[^queue-ts]: `src/core/minions/queue.ts` lines 1–9, 60–72, 99–120, 754, 1738, 1894, 2260, 2273; `src/core/minions/transcript.ts:6`.
[^types-ts]: `src/core/minions/types.ts` lines 20–27, 351.
[^worker-ts]: `src/core/minions/worker.ts` lines 1–15.
[^deployment-doc]: `docs/guides/minions-deployment.md` (supervisor, isolation, lanes, admission, preconditions).
[^shell-jobs-doc]: `docs/guides/minions-shell-jobs.md` lines 12–15 and gating sections.
[^runbook]: `docs/guides/queue-operations-runbook.md` ("Lock-renewal", wedge, divergence sections).
[^quiet-hours-ts]: `src/core/minions/quiet-hours.ts` lines 1–16.
