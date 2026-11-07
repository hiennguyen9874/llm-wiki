---
type: Concept
title: GBrain sync, ingestion, enrichment and open loops
description: How GBrain syncs Markdown repos into its index (with soft deletes), ingests from native source kinds and connectors, enriches entities, and tracks open loops from email.
tags: [agent-memory, gbrain, sync, ingestion, connectors, open-loops]
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
  - id: sync-ts
    resource: ../raw/gbrain/src/core/sync.ts
    kind: code
    revision: 27f8b9d
    title: Sync manifest builder
  - id: sync-reconcile
    resource: ../raw/gbrain/src/core/sync-reconcile.ts
    kind: code
    revision: 27f8b9d
    title: Sync reconciliation
  - id: commit-notifier
    resource: ../raw/gbrain/src/core/commit-notifier.ts
    kind: code
    revision: 27f8b9d
    title: Commit notifier
  - id: live-sync
    resource: ../raw/gbrain/docs/guides/live-sync.md
    kind: code
    revision: 27f8b9d
    title: Live sync guide
  - id: import-file
    resource: ../raw/gbrain/src/core/import-file.ts
    kind: code
    revision: 27f8b9d
    title: Per-file import writer
  - id: data-ingestion
    resource: ../raw/gbrain/docs/guides/data-ingestion.md
    kind: code
    revision: 27f8b9d
    title: Data ingestion guide
  - id: meeting-slack
    resource: ../raw/gbrain/docs/guides/meeting-and-slack-sources.md
    kind: code
    revision: 27f8b9d
    title: Meeting and Slack sources
  - id: github-source
    resource: ../raw/gbrain/docs/guides/github-source.md
    kind: code
    revision: 27f8b9d
    title: GitHub source guide
  - id: google-connect
    resource: ../raw/gbrain/docs/guides/google-connect.md
    kind: code
    revision: 27f8b9d
    title: Google connect guide
  - id: open-loops
    resource: ../raw/gbrain/docs/guides/open-loops.md
    kind: code
    revision: 27f8b9d
    title: Open loops guide
  - id: enrichment-doc
    resource: ../raw/gbrain/docs/guides/enrichment-pipeline.md
    kind: code
    revision: 27f8b9d
    title: Enrichment pipeline guide
  - id: ingestion-daemon
    resource: ../raw/gbrain/src/core/ingestion/daemon.ts
    kind: code
    revision: 27f8b9d
    title: Ingestion daemon
---

GBrain's knowledge flows in two ways: **sync** of Markdown brain repos (git is the canonical store; the database index follows it) and **ingestion** of other material through native source kinds, connectors, capture and webhooks. Enrichment and open-loop detection then build entities and commitments on top. The README's starting advice is to begin with an explicit fact or a notes folder and opt into connectors, capture and enrichment separately.[^readme] The data model it fills is in [data model](gbrain-data-model-and-system-of-record.md); background execution is in [Minions](gbrain-minions-job-queue.md) and the [dream cycle](gbrain-dream-cycle-and-autopilot.md).

## Sync model (Observed unless noted)

- **Pipeline:** `git diff --name-status -M LAST..HEAD` → `buildSyncManifest()` (add/modify/delete/rename) → `isSyncable()` → `pathToSlug()`. Rename detection can be downgraded with reasons such as `id_conflict`, `title_not_unique`, `no_identity_signal`. Strategies: `markdown | code | auto`.[^sync-ts]
- **Git deletes are soft deletes:** a delete sets `pages.deleted_at`; "every soft delete promises a 72-hour restore"; the `purge` phase removes tombstones after `purge.retention_hours` (default 72). A mass-delete valve (`sync.max_deletes` 500, `sync.max_delete_ratio` 0.01 above 50 deletes) needs `GBRAIN_ALLOW_MASS_RECONCILE=1` to bypass (the valve defaults are Reported).[^sync-reconcile]
- **Modes (Reported):** classic incremental by `last_commit`; a managed level-triggered pass (pins HEAD, batches ≤ 10,000, ≤ 4 rounds, never pulls); `--full` reconcile; `--dry-run`; outcomes `synced | resumable | blocked` with ~18 reason codes.[^live-sync]
- **On-commit sync** (off by default, `sync.on_commit`): one host-wide owner via `sync_notifier_leases` with a fencing token (or PGLite serve IPC `sync_nudge`); `fs.watch` accelerates but a 3 s `rev-parse` poll is truth; 400 ms trailing quiet window; per-source states `due | running | retry (5 s/15 s/1 m/5 m) | operator_blocked`; never pulls.[^commit-notifier]
- **Import writer:** `import-file.ts` screens content, applies a write gate, repairs fences, chunks (recursive text chunker; tree-sitter AST chunking for TS/TSX/JS/Python/Ruby/Go with WASM fallback), reuses stored embeddings where inputs match, and installs page-state projections.[^import-file]

## Ingestion sources

- **Native source kinds** (`sources add --kind`): `github` (issues, PRs, comments, reviews, CI; webhook, poll and full reconcile; requires a fine-grained token in `GH_TOKEN`; shares the mass-delete guard), `google` (Gmail, Calendar, Contacts; read-only scopes; bring-your-own OAuth client; tokens in a 0600 credentials file), `meetings` (Fireflies first; one page per meeting; private pages for unattended meetings), `slack` (one page per channel per day) — all Reported in their guides, kinds Observed in `sources-lifecycle-args.ts`.[^github-source][^google-connect][^meeting-slack]
- **Other paths:** `gbrain capture` (`--file`, `--stdin`), an `/ingest` webhook, an `~/.gbrain/inbox/` folder source, and `gbrain transcripts ingest` for coding-agent and chat exports with pattern-based redaction.[^data-ingestion]
- **Connector subsystem and daemon (Observed by subagent):** `src/core/connectors/` with `chatgpt` and `claude` providers and a `connector-sync` job (35-minute DB lock, `connectors.<p>.auto_sync` rechecked at start). The ingestion daemon supervises pluggable sources (file watcher, inbox, cron, learning), validates at the boundary, dedups on a 24 h content hash, rate-limits per source (100 events / 10 s) and enqueues `ingest_capture` jobs; webhooks live in `serve --http`, not the daemon.[^ingestion-daemon]
- Integration recipes (email, calendar, X, meetings, voice) are catalogued in [recipes, plugins and bootstrap](gbrain-recipes-plugins-and-bootstrap.md).

## Enrichment and entity detection (Reported)

`gbrain enrich` batches enrichment with three spend tiers (Tier 1 is 10–15 API calls across web, Twitter, LinkedIn, research, funding, meetings and contacts), stores raw responses under `sources.{provider}.fetched_at`, never overwrites a human assessment and re-enriches at most weekly. Entity detection is opt-in capture plus `gbrain extract` and NER link extraction (see [knowledge graph](gbrain-knowledge-graph.md)).[^enrichment-doc]

## Open loops (`gbrain waiting`) — Reported, files Observed

- A deterministic thread-state machine with no LLM: `unanswered_inbound` (≥ 24 h, you in To:) and `unanswered_outbound` (≥ 72 h, your question), self-closing on reply; loops close by state transition and are never deleted.
- A one-call-per-thread LLM commitment extractor (default on for google sources, last 30 days only, kill switch `loops.extraction_enabled`) projects into an `open_loops` row, a `facts` row of kind `commitment` and a typed thread→person edge (`owes_to` / `awaiting_reply_from`).
- Precision gates exclude noise senders, list mail, bulk Gmail categories, CC-only mail and calendar system mail (detected by iCalendar `METHOD`), with mute-by-sender or thread.[^open-loops]

## Dangerous operations

`GBRAIN_ALLOW_MASS_RECONCILE=1`, `gbrain delete --purge`, `sources reconcile` (Reported).[^live-sync]

## Relationships

- Writes into: [data model](gbrain-data-model-and-system-of-record.md), [memory model](gbrain-memory-model.md) (facts from extraction).
- Executed by: [Minions](gbrain-minions-job-queue.md), [dream cycle](gbrain-dream-cycle-and-autopilot.md).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "How to get data in", "Integrations", "What it does (the loop)".
[^sync-ts]: `src/core/sync.ts` lines 1–11, 27–55.
[^sync-reconcile]: `src/core/sync-reconcile.ts` lines 59–73, 117–154; `src/core/uncommitted-deletions.ts:73`; mass-delete defaults from `docs/guides/sync-unblock-runbook.md:389` via subagent.
[^live-sync]: `docs/guides/live-sync.md` (managed pass, outcomes, reason codes); `docs/guides/on-commit-sync.md`.
[^commit-notifier]: `src/core/commit-notifier.ts` lines 1–20.
[^import-file]: `src/core/import-file.ts` lines 1–45; `src/core/chunkers/recursive.ts:1-16`, `code.ts:1-14`.
[^data-ingestion]: `docs/guides/data-ingestion.md`.
[^meeting-slack]: `docs/guides/meeting-and-slack-sources.md`.
[^github-source]: `docs/guides/github-source.md`.
[^google-connect]: `docs/guides/google-connect.md` (head).
[^open-loops]: `docs/guides/open-loops.md`; `src/core/google/{loop-detect,loops-extract}.ts`, `src/core/loops/*`.
[^enrichment-doc]: `docs/guides/enrichment-pipeline.md`; `docs/guides/entity-detection.md`.
[^ingestion-daemon]: `src/core/ingestion/daemon.ts` lines 1–20; `src/core/minions/handlers/connector-sync.ts:1-30`.
