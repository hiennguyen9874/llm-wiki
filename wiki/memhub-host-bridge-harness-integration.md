---
type: Concept
title: MemHub host bridge and per-harness integration
description: How MemHub installs MCP, hooks and skills into AI harnesses (Claude Code, Cursor, Codex, OpenCode, Qwen Code, Pi, Hermes, OpenClaw, WorkBuddy, DeepSeek) and the mechanics and risks of each.
tags: [memhub, mcp, hooks, harness, integration]
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

# MemHub host bridge and per-harness integration

Each harness has two independent switches: **one-click insert** (MemHub → harness recall) and **sync switch** (harness → MemHub ingest) (`memhub/docs/harness-support/README.md` "同步开关的统一精确语义").[^hy-memory] MCP exposes exactly three tools — `MemHub_recall`, `MemHub_write`, `MemHub_diagnostic_trace` — through a stdio server that reads broker discovery from `ONE_MEMORY_BROKER_DISCOVERY` and credentials from `ONE_MEMORY_HOST_CREDENTIAL_FILE` and routes through `broker-client.ts` (`packages/host-bridge/src/mcp-toolset.ts`, `mcp.ts`; `docs/contracts/one-memory-recall-install-v1.md` §5).[^hy-memory]

## Installer mechanics

`recall-installer.ts` unifies installs: a `RecallHostLayout` (`hostId`, `configPath|null`, `format` of `json|toml|yaml|dsh|opencode|openclaw|codebuddy-plugin|none`, `channel` `mcp|cli`, `skillPath|null`, `journalPath`, `containmentRoot`) feeds `planRecallInstall → previewRecallInstall` (fingerprint hunks) `→ applyRecallInstall → verifyRecallInstall`, with `rollbackRecallInstall`, `planRecallUninstall/applyRecallUninstall` and `inspectRemnants`. Installers never force-delete user-edited files: they revoke first and ask for manual review (`packages/host-bridge/src/recall-installer.ts`; harness docs).[^hy-memory] Capture hooks live in `capture-hooks.ts` (`cursor`: beforeSubmitPrompt/afterAgentResponse; `claude-code`: UserPromptSubmit/Stop/SubagentStop; `codex`: UserPromptSubmit/Stop), all wrapped by `failOpenHookCommand` so a hook failure never blocks the host. Hook and Hermes provider assets are built by `scripts/build-hook-assets.mjs` and `build-hermes-provider-assets.mjs` (copies `plugins/hermes/hy_memory/*`, rejecting symlinks).[^hy-memory]

## Per harness (from `memhub/docs/harness-support/*.md`)

| Harness | Mechanism | Notes |
|---|---|---|
| Claude Code | MCP in `~/.claude.json` + skill + 3 hook groups | |
| Cursor | `~/.cursor/mcp.json` + skill + 2 hooks | |
| Codex | `~/.codex/config.toml [mcp_servers.one-memory]` + skill + 2 hooks | |
| OpenCode | `mcp.one-memory` + capture plugin; no skill | two overlapping ingest paths (DB scan + plugin) |
| Qwen Code | `~/.qwen/settings.json` + skill; no hooks | `QWEN_HOME` split between Core import and Desktop layout |
| Pi | no MCP; CLI skill + extension + credential file | web copy still says unsupported |
| Hermes | native Python `MemoryProvider` prefetch + MCP + skill, `memory.provider: hy_memory` | see [plugins](hy-memory-plugins-openclaw-hermes.md) |
| OpenClaw | **frozen**: product paths reject it | low-level installer still writes config and can't roll back — footgun if called directly |
| WorkBuddy | real `.codebuddy-plugin` with marketplace + cache copies, three registries | registry hashes conservative; unrelated edits can make auto-uninstall refuse |
| DeepSeek Harness | per-profile hosts `deepseek-harness:<profile>` with `cordis.patch.yml` managed blocks | one UI switch covers all profiles |

## Gotchas

A probe is not proof of hot reload — harnesses must be fully restarted; a stale or mismatched host runtime blocks install/permission mutations (`runtime-cli.ts` `host_install_preview_stale`, `host_runtime_component_mismatch`).[^hy-memory]

## Relationships

- Part of: [MemHub architecture](memhub-product-architecture.md), [apps and packages](memhub-apps-and-packages.md).
- Reads from the harnesses via: [import adapters](memhub-import-adapters-and-live-sync.md).
- Permission semantics: [privacy and permissions](memhub-privacy-and-permissions.md).

## Coverage and limits

Static inspection (delegated); no installer was run against a real harness, so documented install paths are Reported-from-docs plus Observed-in-code, not Reproduced.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
