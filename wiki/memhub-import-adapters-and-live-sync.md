---
type: Concept
title: MemHub source adapters, import and live sync
description: The SourceAdapter protocol, registered host sources, cursor rules, polling-plus-watch live sync, hook capture handoff, and source authorization checks.
tags: [memhub, import, adapters, live-sync, capture]
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

# MemHub source adapters, import and live sync

MemHub ingests host transcripts through a uniform `SourceAdapter` protocol, keeps them in sync by polling with an optional file-watch trigger, and offers a hook-capture path for hosts that can push turns (`memhub/docs/contracts/source-adapter-v1.md`; `apps/core/src/one_memory/imports/`).[^hy-memory]

## Adapter protocol

`SourceAdapter` exposes `descriptor`, `detect()`, `scan(options)` yielding `ScannedEvidence | ScanFailure | ScanSkip | ScanProgressEvent` (`imports/adapters.py`; contract "输入与输出").[^hy-memory] Cursors are per-file, opaque `file_key` + checkpoint + observed size/mtime, and advance only after the record commits. Capability flags (`can_append`, `can_observe_edits/deletes`, `can_reconcile_complete_set`) derive an honesty label `additions_only` vs `full_dynamic` (`SourceCapabilities.sync_completeness`). Absent or unreadable data is never treated as deletion.[^hy-memory]

## Registered sources

WorkBuddy, Cursor (unified), Claude Code, Codex, Pi, QwenWork, Qwen Code, Hermes, DeepSeek Harness, OpenCode, OpenClaw, plus manual exports `chatgpt-export`, `claude-export`, `generic-export`, `memory-content-export` (`imports/sources/registry.py::build_source_catalog`; `imports/sources/exported.py`). Each source carries a verification level (`FIXTURE_ONLY` vs `REAL_REPLAYED`) in `imports/host_packages.py`.[^hy-memory]

## Live sync and capture

- Polling supervisor with a persisted incremental cursor (default 60 s, floor 5 s); `watchfiles` is a pure trigger of the same supervisor, never a second ingest path (`imports/live_sync.py::PollingLiveSyncSupervisor`; `imports/live_watch.py`).[^hy-memory]
- `memhub capture <host>` is a short-lived hook process that never opens the main DB: it posts hook JSON to loopback `/api/v1/live-capture/{source}` (1.5 s budget) and silently drops on timeout; the Unreleased changelog notes no double-write when hook and file sync both see a turn (`capture_handoff.py` docstring; `CHANGELOG.md::Unreleased`).[^hy-memory]

## Authorization

`source_grants` rows hold authorised root/identity/revocation; `config.json` holds per-source `sync_enabled` desired-state written atomically by Core. File access re-verifies realpath, symlinks, regular-file type and size budget, and rejects sensitive roots (`imports/grants.py::SourceGrantStore`; `memory_server/config_state.py`; `imports/access.py::AuthorizedSourceFile.admit`; `docs/ARCHITECTURE.md` "Source authorization and synchronization").[^hy-memory] See [privacy and permissions](memhub-privacy-and-permissions.md).

## Relationships

- Feeds: [modes and write queue](memhub-memory-modes-and-write-queue.md).
- Installed per host by: [host bridge](memhub-host-bridge-harness-integration.md).
- Part of: [MemHub architecture](memhub-product-architecture.md).

## Coverage and limits

Static inspection (delegated). Per-source readers under `imports/sources/` were enumerated, not individually read; real-host replay status per source was not verified.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
