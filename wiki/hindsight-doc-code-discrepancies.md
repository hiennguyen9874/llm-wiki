---
type: Concept
title: Hindsight documentation vs code discrepancies
description: Catalogue of places where Hindsight READMEs, docs and comments disagree with the code or each other, with verification status and how to treat each.
tags: [agent-memory, hindsight, discrepancies, trust]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
stale_after: 2027-02-06
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: api-slim-readme
    resource: ../raw/hindsight/hindsight-api-slim/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-api-slim README
  - id: api-pyproject
    resource: ../raw/hindsight/hindsight-api-slim/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-api-slim package manifest
  - id: memory-engine
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/memory_engine.py
    kind: code
    revision: eb963cb
    title: MemoryEngine
  - id: embed-readme
    resource: ../raw/hindsight/hindsight-embed/README.md
    kind: documentation
    revision: eb963cb
    title: hindsight-embed README
  - id: workspace
    resource: ../raw/hindsight/pyproject.toml
    kind: code
    revision: eb963cb
    title: Root uv workspace manifest
---

When using Hindsight material, prefer code over README prose where they differ. This page records the mismatches found in the 1.2.0 snapshot; items marked **verified** were rechecked directly by the curator, the rest are subagent observations.

## Contradictions

Each row lists both claims; "Treat as" is a synthesis judgement, not a source claim.

| # | Claim A | Claim B | Status | Treat as |
| --- | --- | --- | --- | --- |
| 1 | License is MIT: `license = "MIT"` in the manifest and root `LICENSE`[^api-pyproject] | `hindsight-api-slim/README.md` line 137 (and `hindsight-api/README.md`) say "Apache 2.0"; OpenAPI metadata in `api/http.py` says "Apache 2.0"[^api-slim-readme] | verified | MIT governs the repo; sub-docs are stale. Decision-model weights are separately Apache 2.0/MIT licensed |
| 2 | `hindsight-embed/README.md` line 13: daemon exits after 5 minutes idle[^embed-readme] | `daemon_embed_manager.py::DEFAULT_DAEMON_IDLE_TIMEOUT = 0` (disabled)[^embed-readme] | verified | Code wins: no auto-shutdown unless configured |
| 3 | Code comments say recall "Diversif[ies] … MMR" in `memory_engine.py`[^memory-engine] | No MMR implementation exists; grep finds only those docstrings | verified | Recall has no MMR step ([Recall](hindsight-recall-pipeline.md)) |
| 4 | README advertises "opinions" shaped by disposition[^readme] | `memory_engine.py` filters the removed `opinion` fact type for backward compatibility; disposition only affects reflect prompt phrasing[^memory-engine] | verified (filter); prompt effect subagent-observed | Valid types are world, experience, observation ([Reflect](hindsight-reflect-agent.md)) |
| 5 | Root workspace lists `hindsight-mcp-server`[^workspace] | No such directory in this checkout | verified | Dangling workspace member |
| 6 | `hindsight-api-slim/README.md` shows a Python API (`MemoryEngine().create_memory_bank(...)`, `retain(memory_bank_id=…)`)[^api-slim-readme] | Real surface: `ensure_bank_profile`, `retain_async`, `recall_async`, `reflect_async` with `bank_id=` and a required `request_context`[^memory-engine] | subagent-observed | Do not copy the slim README example |
| 7 | READMEs describe `hindsight-local-mcp` as a stdio MCP server[^api-slim-readme] | `mcp_local.py` starts the full API on :8888 with `pg0://hindsight-mcp` and serves MCP over HTTP | subagent-observed | Treat as HTTP ([API surface](hindsight-api-surface.md)) |
| 8 | `hindsight-all-slim/README.md` shows `pip install hindsight-all` / `from hindsight import …` | `hindsight-all-slim` has `packages = []` and no `hindsight/` module | subagent-observed | Use `hindsight-all` for the module |
| 9 | `config.py` comment on `DEFAULT_WEBHOOK_EVENT_TYPES` says "default = all supported events" | Value is only `"consolidation.completed"` | subagent-observed | Subscribe to other events explicitly ([Webhooks](hindsight-extensions-defense-webhooks.md)) |
| 10 | Integrations hub README row "Claude Code Skills" links to `./chat` | `chat/` documents the Vercel Chat SDK; no `claude-code` directory exists | subagent-observed | Use [Coding agents](hindsight-coding-agents.md) |
| 11 | Stale client artifacts: Go README says 1.0.0/API 0.4.11; Rust README lists removed methods; Python generator config says `packageVersion: 0.0.7` vs 1.2.0 | Manifests show 1.2.0 (Python/TS) and 0.1.0 (Rust) | subagent-observed | Trust manifests ([Clients](hindsight-clients-cli-embed.md)) |

## Other trust notes

- The internal name "TEMPR" for the retrieval stack appears in READMEs, figures and one tool docstring but in no code symbol (subagent-observed).
- `pg0` embedded DB is the documented default but needs the `embedded-db` extra, absent from the slim base install ([Storage](hindsight-storage-and-configuration.md)).
- The README's benchmark chart is dated January 2026 and vendor-published ([Benchmarks](hindsight-benchmarks-and-testing.md)).[^readme]

[^readme]: `README.md` § "Memory Types", "Memory Performance & Accuracy".
[^api-slim-readme]: `hindsight-api-slim/README.md` (license line 137; Python usage example; local MCP description); `hindsight-api/README.md` line 145.
[^api-pyproject]: `hindsight-api-slim/pyproject.toml` line 9; root `LICENSE`.
[^memory-engine]: `hindsight-api-slim/hindsight_api/engine/memory_engine.py` lines ~9515, ~9610–9611, ~10015; `api/http.py` line ~4529; `mcp_local.py`; `config.py` line ~2339.
[^embed-readme]: `hindsight-embed/README.md` line 13; `hindsight-embed/hindsight_embed/daemon_embed_manager.py` line 74.
[^workspace]: `pyproject.toml` line 2.
