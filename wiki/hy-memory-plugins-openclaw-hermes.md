---
type: Concept
title: Hy Memory plugins — OpenClaw and Hermes
description: How the OpenClaw TypeScript plugin and the Hermes Python memory provider integrate with Hy Memory, including tools, scope, auto recall/capture, managed mode, and known drifts.
tags: [agent-memory, hy-memory, plugins, openclaw, hermes]
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

# Hy Memory plugins — OpenClaw and Hermes

`plugins/` is an integration-only layer; memory logic stays in the Python SDK. Both plugins talk to the Python SDK over local HTTP, a stated difference from Mem0's TS SDK approach (`plugins/README.md` "布局", "与 Mem0 的差异").[^hy-memory] `hook/` and `mcp/` directories are reserved.[^hy-memory]

## OpenClaw (TypeScript, npm `openclaw-hy-memory`)

- **Tools**: `memory_search`, `memory_add`, `memory_get`, `memory_update`, `memory_delete` (`openclaw.plugin.json` `contracts.tools`; `tools/index.ts::registerAllTools`). `memory-list.ts` exists but isn't registered and the `index.ts` header says "6 core tools" (stale); `memory_get`'s description references `memory_list`, which the model cannot call (Observed).[^hy-memory]
- **Transport**: `HttpProvider` calls `/api/v1/*` with a 120 s timeout and `GET /healthz`; grouped search results are flattened (`provider.ts::normalizeSearchMemories`). See [server routes](hy-memory-sdk-api-and-config.md).[^hy-memory]
- **Scope**: `userId` (default OS username), `agentId` (`default_agent`), `sessionId` (`default_session`); tools may override per call; `memory_add` with `text` routes to `addExtracted` (skip extraction), with `messages` to `add` (`config.ts`; `tools/memory-add.ts`).[^hy-memory]
- **Auto-recall** (`before_prompt_build`, `autoRecall`): skips prompts <5 chars or containing `HEARTBEAT`; prepends a `<relevant-memories>` block with evolution chains oldest→newest. **Auto-capture** (`agent_end`/`session_end`, `autoCapture`): writes every `memoryWriteTurnWindow` turns with a per-session cursor, strips injected memory blocks to avoid recursion, requires ≥10 chars and a user message; always uses static `cfg.sessionId`, so per-conversation session isolation is not applied (`index.ts`).[^hy-memory]
- **Server lifecycle**: on `gateway_start` it creates a venv at `~/.openclaw/hy-memory-venv`, pip-installs `hy-memory[extras]` from `HY_MEMORY_PYPI_INDEX_URL`, and spawns `python -m hy_memory.server`; unset `HY_MEMORY_SDK_VERSION` means the latest PyPI release is installed and re-upgraded each start; stuck port owners are SIGKILLed (`python-env.ts`; `index.ts::ensureVenv`, `killStuckProcessOnPort`). Install needs `--dangerously-force-unsafe-install` because it spawns Python (`plugins/openclaw/README.md` Quick Start).[^hy-memory]
- **Config → env** (`config.ts::buildServerEnv`): `MEMORY_MODE`, Kuzu in ultra, `MEMORY_CACHE_BACKEND=sqlite`, `MEMORY_PIPELINE_TRACE_ENABLED=false`, forced `MEMORY_EMBEDDER_EXTRA_BODY={"encoding_format":"float"}`.[^hy-memory]
- **CLI**: `openclaw hy-memory status|search|add|list|inspect|delete|reset|init|import-from-openclaw`; the wizard rewrites `~/.openclaw/openclaw.json`; import uses a sha256 ledger `.hy-memory-import.json`, needs a reachable server except `--dry-run`, and skips `memory/dreaming/**` (`cli/init-wizard.ts`, `cli/import-core.ts`; README "Migrating").[^hy-memory]
- **Drift**: README/schema say `topK: 10`, `searchThreshold: 0.3` but `config.ts` defaults are 5 and 0.4 (the parser wins); versions differ — package 1.1.10, plugin manifest 0.1.0 (Observed).[^hy-memory]

## Hermes (Python provider, `plugin.yaml` 0.2.0)

- Registers `HyMemoryProvider` via `ctx.register_memory_provider`; stdlib only — no SDK import, DB or server (`plugins/hermes/hy_memory/__init__.py`; README intro).[^hy-memory]
- **Two modes**: MemHub-managed (private `connection.json`, `transport: memhub-broker`) is **recall-only** — `_broker_request` rejects non-`context` operations with `writes_suppressed`, `hy_memory_add` is not exposed, `auto_capture` forced off; otherwise operator-managed direct mode requires `HY_MEMORY_USER_ID`/`HY_MEMORY_AGENT_ID` (`provider.py::__init__`, `_load_broker_configuration`).[^hy-memory]
- Broker checks: discovery must be `127.0.0.1`, `one-memory-recall-broker`, `status: running`; token matches `omhg_v1_[A-Za-z0-9_-]{43}`; health `instance_id` must match (`provider.py`).[^hy-memory]
- Recall: `queue_prefetch` warms a search, `prefetch` consumes it next turn, dedups injected `memory_id`s per session (sha256 bucket in `$HERMES_HOME/.one-memory/hy-memory-seen.json`, 0600), escapes `<`/`>` and wraps in `<memhub_memory_context>`. Hardening: no redirects, total-deadline reader, bounded bodies, HTTPS required for non-loopback direct URLs.[^hy-memory]
- Requires a full Hermes restart after install/removal; an orphaned provider fails safe (README §Security notes the bare SDK server has no auth).[^hy-memory]

## Relationships

- Uses: [SDK API and HTTP server](hy-memory-sdk-api-and-config.md).
- Installed by MemHub: [host bridge](memhub-host-bridge-harness-integration.md).
- Tests/CI: [releases, CI and quality](hy-memory-release-ci-and-quality.md).

## Coverage and limits

Static inspection (delegated); plugin tests were not run. OpenClaw's host API semantics (hooks, `before_prompt_build`) are taken from the plugin code only.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
