---
type: Concept
title: ai-memory data handling, retention and lifecycle operations
description: What ai-memory stores, its opt-in network egress paths, retention and deletion semantics, and the safety matrix for purge, merge, backup, restore, reset and reindex.
tags: [agent-memory, ai-memory, privacy, operations, backup]
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
  - id: data-handling
    resource: ../raw/ai-memory/DATA_HANDLING.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: DATA_HANDLING.md
  - id: lifecycle-ops
    resource: ../raw/ai-memory/docs/lifecycle-ops.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Lifecycle operations
  - id: backup-agents
    resource: ../raw/ai-memory/docs/design-backup-agent-assets.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Agent-asset backup design
---

# ai-memory data handling, retention and lifecycle operations

By default ai-memory is **local-only with no telemetry**: one data directory (git-backed markdown + SQLite), no background update check, and no encryption at rest (OS permissions only).[^data-handling] The single default network call is the first-start download of the ~87 MB `all-MiniLM-L6-v2` local embedding files from `huggingface.co`, sha256-pinned, with no stored content sent.[^data-handling]

Evidence class: **Reported** by the project's data and ops docs (static reading, delegated). `stale_after` is set because defaults and destructive-command behaviour change by release. Nothing executed.

## Opt-in egress paths

Cloud `embedding_provider` (sends every page; switching later backfills the existing corpus); `llm_provider`/`llm_fallbacks` (observations and page text for consolidation, lint, dream, profile, auto-improve); `capture_assistant` (double opt-in, global); `AI_MEMORY_RERANKER=llm` (unsanitized live query plus titles/snippets); `[[admission_webhooks]]` (path, frontmatter, full body). Embedding, LLM and webhook payloads are **not** sanitized. `ai-memory upgrade` contacts api.github.com; OIDC logins contact issuer endpoints.[^data-handling]

## Retention and deletion

Decay evicts cold episodic pages (`cold_threshold` 0.20; hard delete after 180 days; see [Consolidation and aging](ai-memory-consolidation-and-aging.md)); `expires_at` TTL pages outrank `pinned`; observations are kept by default (`observation_retention_days = 0`). There is no data-subject-request tooling; a configured provider (not the self-hosted default) creates a processor relationship.[^data-handling] Purges are **logical deletes**: `--compact` rebuilds FTS, runs `VACUUM` and `wal_checkpoint(TRUNCATE)` but "is not forensic erasure" — bytes remain in git history and older backups.[^lifecycle-ops]

## Safety matrix (abridged)

| Operation | Server running? | Effect | Reversible |
| --- | --- | --- | --- |
| `purge-project --confirm` | yes | wipes one project (+ cross-project collateral observations); 409 on a live run lease | no |
| `purge-session --confirm` | yes | wipes one session's rows, handoffs, page versions, embeddings | no |
| `merge-project` | yes | dry run by default; `--confirm` is lossless | no |
| `move-project --confirm` | yes | copy+purge merge needs `--allow-lossy-merge` | no |
| `rename-project` / `rename-workspace` | yes | column-only | yes |
| `move-session` | yes | dry run without `--confirm` | yes |
| `backup --to` | yes | online SQLite backup | n/a |
| `restore-page` / `memory_restore_page` | yes | restores one page version | yes |
| `restore --from` | **no, stop server** | overwrites the data dir (staged + verified) | no |
| `reset --confirm` | **no** | wipes all data | no |
| `reindex` | **no** | refuses a non-empty DB | only with DB backup |

`dry_run` always wins over `confirm`; `restore` drops wiki-git hooks/alternates/nested repos.[^lifecycle-ops] Direct-disk operations (`reset`, `restore`, `reindex`, `uninstall --purge-data`) look for a process named `ai-memory`, which is why the Nix package leaves the binary unwrapped.[^readme]

## Host agent-asset backup

`ai-memory backup-agents -o agent-assets.tar.gz` archives host-side harness configuration; `restore-agents` inspects first and only `--apply` writes (timestamped copies). Redaction limits, archive bounds and an active-content warning are specified in the design doc.[^readme][^backup-agents]

## Relationships

- Threat model and auth: [Auth and security](ai-memory-auth-and-security.md).
- Hook spool holding pre-strip bodies: [Capture and hooks](ai-memory-capture-and-hooks.md).
- CLI commands: [Harness integrations and CLI](ai-memory-harness-integrations-and-cli.md).

[^readme]: `../raw/ai-memory/README.md` — "Everyday use" (backup-agents), "NixOS" (live-process guard rationale).
[^data-handling]: `../raw/ai-memory/DATA_HANDLING.md` — "Default: local, no telemetry, one model download", "The opt-in paths…", retention and GDPR sections.
[^lifecycle-ops]: `../raw/ai-memory/docs/lifecycle-ops.md` — "TL;DR - safety matrix", deletion semantics.
[^backup-agents]: `../raw/ai-memory/docs/design-backup-agent-assets.md` — supported paths, redaction limits, archive bounds (read by delegated agent at head level only).
