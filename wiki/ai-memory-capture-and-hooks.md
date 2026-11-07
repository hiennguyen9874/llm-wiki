---
type: Concept
title: ai-memory capture, hooks and privacy boundary
description: How ai-memory silently captures agent lifecycle events via fire-and-forget hooks, spools them offline, sanitizes them at a typed boundary, and applies per-repository capture policy.
tags: [agent-memory, ai-memory, capture, hooks, privacy]
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
  - id: hooks-lib
    resource: ../raw/ai-memory/hooks/_lib.sh
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Shared POSIX hook library
  - id: hooks-code
    resource: ../raw/ai-memory/crates/ai-memory-hooks/src/capture_policy.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-hooks crate (capture_policy.rs, router.rs)
  - id: marker-file
    resource: ../raw/ai-memory/docs/marker-file.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Marker file and capture exclusions
  - id: external-lifecycle
    resource: ../raw/ai-memory/docs/external-lifecycle.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: External lifecycle producers
  - id: security
    resource: ../raw/ai-memory/SECURITY.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: SECURITY.md
  - id: managed-workstreams
    resource: ../raw/ai-memory/docs/managed-workstreams.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Managed workstreams
---

# ai-memory capture, hooks and privacy boundary

Capture is the first stage of ai-memory's pipeline: per-harness lifecycle hooks send every event to the local server, which sanitizes it before storage.[^readme] Hooks are deliberately non-blocking and always exit successfully so they never stall the agent.[^hooks-lib]

Evidence class: **Observed** (static inspection of `hooks/_lib.sh` and hook crate sources, delegated), nothing executed. Security-posture statements are **Reported** by `SECURITY.md`.

## Event flow

- **Events** (Claude Code example): SessionStart, UserPromptSubmit, PreToolUse, PostToolUse (+ PostToolUseFailure mapped to `post-tool-use`), PreCompact, Stop, SessionEnd, SubagentStart/Stop — 9 scripts for 10 triggers.[^hooks-lib]
- **Transport:** POST to `http://127.0.0.1:49374/hook?event=…&agent=…` with marker-derived query params; 0.2 s POST budget, 1.0 s synchronous `GET /handoff` at session start for the baton; hooks `exit 0` / return `{}` always.[^hooks-lib]
- **Compaction:** a SessionStart with `source: "compact"` claims no handoff.[^hooks-lib]
- **Native path:** `ai-memory hook` spools instantly and drains from a detached `hook-drain`; the Zero harness drains in-process because its sandbox kills detached children.[^hooks-code]

## Offline spool

Failed posts land in `<data_dir>/hook-spool/<ms>-<pid>-<seq>.json` (file mode 0600, dir 0700, tmp+rename). An `ingest_key` is minted before the first POST so replays dedup. 2xx or terminal 4xx retires an entry; 408/425/429 stop the pass. Bounds: 8 failed passes, 7 days, 10,000 files.[^managed-workstreams] The spool holds **pre-strip** bodies, so a filesystem copy (unlike `ai-memory backup`) can include unsanitized text.[^security] The server-side sanitizer runs before raw workstream segments are written.[^managed-workstreams]

## Privacy boundary

`ai_memory_core::sanitize::Sanitizer` and the `Sanitized<T>` wrapper form the typed boundary; it redacts vendor keys, PEM blocks, URL credentials and `*_TOKEN=` shapes, with per-match allowlisting and private keys never exempt. The server sanitizer runs before both FTS rows and the immutable raw workstream segments.[^hooks-code][^security] Assistant-output capture needs a double opt-in and is scrubbed client-side and server-side; operator `extra_patterns` apply only server-side.[^security] A recent fix stopped the `api_key` rule from matching inside ordinary identifiers (e.g. corrupting `task-release-…`).[^security]

## Capture policy

`[capture] ignore_paths` (strict, ≤128 patterns, an invalid marker fails closed) yields Keep / Drop / MetadataOnly decisions; recognized search/list tools drop under an active policy, shell/unknown tools are best-effort lexical. Allowlist mode gates every event *before* spool, so an unmarked repository emits nothing.[^hooks-code][^marker-file] Capture ownership can be delegated to an orchestrator with `AI_MEMORY_CAPTURE_OWNER`, with batch ingestion and stable retry identity for external producers.[^external-lifecycle]

## Relationships

- Feeds [Consolidation and aging](ai-memory-consolidation-and-aging.md) (session pages) and [Handoffs and messaging](ai-memory-handoffs-and-messaging.md).
- Installed via [Harness integrations and CLI](ai-memory-harness-integrations-and-cli.md); project routing in [Project identity and profile](ai-memory-project-identity-and-profile.md).
- Wider threat model: [Auth and security](ai-memory-auth-and-security.md), [Data handling](ai-memory-data-handling-and-lifecycle-ops.md).

[^readme]: `../raw/ai-memory/README.md` — "It captures the work itself, silently"; "How it works".
[^hooks-lib]: `../raw/ai-memory/hooks/_lib.sh::ai_memory_post_hook, ai_memory_get_handoff, ai_memory_is_compaction_start, ai_memory_spool_event, ai_memory_drain_spool, ai_memory_url_with_ingest_key`; `hooks/claude-code/*.sh`.
[^hooks-code]: `../raw/ai-memory/crates/ai-memory-hooks/src/capture_policy.rs::CapturePolicy::inspect, repository_admits_capture`; `crates/ai-memory-core/src/sanitize.rs` module doc; `crates/ai-memory-cli/src/commands/hook.rs` module doc.
[^marker-file]: `../raw/ai-memory/docs/marker-file.md` — "Capture exclusions".
[^external-lifecycle]: `../raw/ai-memory/docs/external-lifecycle.md` — capture suppression and batch ingestion sections.
[^security]: `../raw/ai-memory/SECURITY.md` — "Assistant/Stop capture…" and hook-spool notes (pre-strip bodies, 0600/0700).
[^managed-workstreams]: `../raw/ai-memory/docs/managed-workstreams.md` — "Degraded offline launches" (spool bounds) and "Privacy and storage boundaries".
