---
type: Concept
title: ai-memory managed workstreams (ai-memory run)
description: How ai-memory run provides cross-harness session continuity through leases, a ledger, a private local history dossier, and degraded-offline recovery.
tags: [agent-memory, ai-memory, workstreams, continuity, harness]
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
  - id: managed-workstreams
    resource: ../raw/ai-memory/docs/managed-workstreams.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Managed workstreams
  - id: managed-harness
    resource: ../raw/ai-memory/docs/managed-harness-contributions.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Managed harness contributions
  - id: workstream-code
    resource: ../raw/ai-memory/crates/ai-memory-workstream/src/lib.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-workstream crate
---

# ai-memory managed workstreams (`ai-memory run`)

A **managed workstream** is an optional continuity layer: launching a harness through `ai-memory run <harness>` links it to a shared workstream, so quitting Claude Code and running `ai-memory run codex` gives Codex the shared workstream plus a private, temporary local projection of Claude's visible native history for details the bounded startup packet omitted.[^readme] Direct harness launches behave as before.[^readme]

Evidence class: **Observed** (docs and crate sources, delegated static inspection); nothing executed.

## Run lifecycle

- Opens a **90-second renewable lease**; one writer per workstream.[^managed-workstreams]
- Per run: resolve scope and repository/worktree fingerprint, set `AI_MEMORY_RUN_ID`, link the native session in SessionStart, deliver only unseen portable events; on exit read the native transcript read-only with deterministic ids and cursors (1 MiB per-record cap, with a loss annotation).[^managed-workstreams]
- `--force-unlock` atomically replaces the lease, only for the same authenticated operator, and never signals the native process.[^managed-workstreams][^readme]
- Subcommands: `run`, `continue` (newest managed checkout), `resume` (picker; `--search`, `--all`, `--limit`), `workstreams`, `workstream-search`, `recover`.[^readme]

## Harness switching and privacy

On a real harness switch the receiving agent is told to consult `AI_MEMORY_PREVIOUS_SESSION_HISTORY`, naming a private temp Markdown projection built from a checkout-validated, read-only adapter; it disappears when the child exits and is local to the launcher machine. The server receives only harness and session identity, never transcript path or body. A switch on another machine gets the portable ledger and handoff but not the native transcript.[^readme][^managed-workstreams] This path needs host client 3.1.0 or newer; a stale binary earlier in `PATH` can shadow the update.[^readme]

## Degraded offline launches

If the server is unreachable, `run` warns and launches with local capture spooling, skipping leases and journaling bounded metadata; `ai-memory recover` replays after the server returns. `--require-server` fails closed instead.[^readme][^managed-workstreams]

## Newer unended session notice

Without the managed launcher a quota-cut harness leaves no handoff; the next session start carries a one-line notice naming a newer unended session, readable via `memory_read_session_observations`, also surfaced as `recent_sessions` ordering in `memory_briefing` and `newer_unended_session` in `memory_handoff_list`.[^readme]

## Adding a harness

An acceptance bar and protocol for managed resume, transcript import and startup-context delivery is defined for contributors.[^managed-harness] Harness adapters live in the workstream crate (`harness.rs`).[^workstream-code]

## Relationships

- Uses the handoff ledger: [Handoffs and messaging](ai-memory-handoffs-and-messaging.md).
- Installed and wired through [Harness integrations and CLI](ai-memory-harness-integrations-and-cli.md).
- Raw segments are stored under `raw/workstreams/` in the data dir ([architecture](ai-memory-architecture.md)).

[^readme]: `../raw/ai-memory/README.md` — "Why ai-memory" (carry the session), "If in doubt, start your harness with `ai-memory run`" and following paragraphs.
[^managed-workstreams]: `../raw/ai-memory/docs/managed-workstreams.md` — "What happens on each run", "Lease recovery", "Native identity privacy", "Degraded offline launches", "Privacy and storage boundaries".
[^managed-harness]: `../raw/ai-memory/docs/managed-harness-contributions.md` — protocol and acceptance bar.
[^workstream-code]: `../raw/ai-memory/crates/ai-memory-workstream/src/lib.rs`, `src/harness.rs` (read by delegated agent; symbol-level locators not recorded).
