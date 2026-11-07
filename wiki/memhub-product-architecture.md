---
type: Concept
title: MemHub product architecture and data plane
description: MemHub's single-Runtime process model, SDK-vs-management data authorities, API surfaces, contracts catalog, and operational gotchas.
tags: [memhub, architecture, runtime, data-plane, api]
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

# MemHub product architecture and data plane

MemHub is a local-first shared-memory product: it compiles AI conversations the user authorises into one local memory and re-exposes it to separately authorised AI tools (`memhub/README.md` "MemHub", "核心原则").[^hy-memory] Hy Memory is the engine; "MemHub" is the product name, while `one-memory` survives in module names, compatibility paths and the default data home `~/.one-memory` (`memhub/docs/ARCHITECTURE.md` preamble; `memhub/PRIVACY.md`).[^hy-memory] MemHub 1.0.6 (build 45) pins `hy-memory==2.0.14` (`memhub/apps/core/src/one_memory/hy_runtime_config.py::HY_MEMORY_VERSION`; `memhub/README.md`).[^hy-memory]

## Process model

One installation = one managed Runtime, one data home, one OS service identity; App, CLI and Web are clients (`memhub/docs/contracts/runtime-unification.md` "Components").[^hy-memory] The long-running Runtime is Node (`runtime.cjs serve`) and owns one Python Core child, one loopback Recall Broker/Host Gateway sidecar, receipts/tokens/lock files and Core restart supervision. macOS uses a LaunchAgent (no Electron needed to run), Linux a systemd user unit, with owner receipt `app` or `cli` (`memhub/docs/ARCHITECTURE.md` "Runtime process shape", "Service ownership").[^hy-memory] Core is FastAPI and acts as management plane (grants, model profiles, durable write queue, config, diagnostics) and refuses to serve until the SDK data-plane migration has cut over (`apps/core/src/one_memory/api.py` startup raising `SdkMigrationRequired`; `docs/contracts/sdk-data-plane-migration-v1.md`).[^hy-memory]

## Two data authorities

Memory entities, raw turns, vectors, graph, coding stores and SDK caches belong to the SDK under `<data_dir>/hy-memory/governed-v2`; the management DB `one-memory.sqlite3` holds only grants, sync desired-state, model profiles, queue/leases, receipts and `memory_id` references. All memory I/O goes through the public `HyMemoryClient`, with a direct-store exception for graph projection/admin (`docs/ARCHITECTURE.md` "Storage", "HY SDK client boundary"; `memhub/MEMORY.md` principles 1–3; `hy_sdk_runtime.py::build_sdk_config`).[^hy-memory] The management SQLite is WAL with `BEGIN IMMEDIATE` because multiple writers meet by design; contention, WAL switching and connection leaks were observed failures (`apps/core/src/one_memory/database.py`).[^hy-memory] Legacy `memory_governance.py` and `memory_visibility.py` serve only pre-cutover data (Observed; replaced by retired stores after cutover).[^hy-memory]

Write chain: `memory_write_jobs → SDK add() → memory_id receipt`; one queue row = one final conversation chunk = one `add()` (see [modes and write queue](memhub-memory-modes-and-write-queue.md)).[^hy-memory]

## API surfaces

Local HTTP with bearer token or UI session cookie plus origin checks; broker identities validated from signed envelope headers; unknown external endpoints fail closed (`auth.py::local_api_guard`; `external_memory_access.py::require_external_endpoint`).[^hy-memory]

- Writes: `POST /api/v2/memory-writes` (+ receipt), `POST /api/v2/memories`, hook `POST /api/v1/live-capture/{source}`.
- Reads: `/api/v2/home-projection`, `/memory-library`, `/memories/graph`, `/user-profile`, `/memories/{id}`, `/raw`, `POST /api/v2/memories/ask(/stream)`, `POST /api/v1/recall`, `POST /api/v2/context/search`.
- Management: sources/grants/import jobs/live sync, model profiles, embedding spaces/switches, settings (memory-mode, memory-features, evolve-schedule, …), `POST /api/v2/evolve`, diagnostics, backup, health.

(`api.py` route table; `memory_server/routes.py`; `memhub/MEMORY.md` Write/Search sections.)[^hy-memory] CLI and MCP surfaces: see [apps and packages](memhub-apps-and-packages.md) and [host bridge](memhub-host-bridge-harness-integration.md).

## Contracts catalog (`memhub/docs/contracts/`)

`runtime-unification` (one Runtime/home/identity); `sdk-data-plane-migration-v1` (offline startup migration, copies no memory, reattaches collections, readback-verifies); `memory-mode-evolve-v1`; `memory-features-v1` (opt-in SDK retrieval/extraction flags, config-only); `memory-event-time-scheduling-v1`; `source-adapter-v1`; `embedding-switch-v1`; `home-mode-projection-v1` (Web home authority, excerpt privacy); `host-context-transport-v1` and `unified-context-read-v1` (legacy Context v1 for pre-cutover hosts); `one-memory-recall-install-v1` (MCP stdio + discovery file, exactly three tools); `diagnostic-logging` (`DiagnosticEventV1` JSONL).[^hy-memory]

## Constraints and gotchas

- **No model ⇒ no recallable history**: raw is written only inside SDK `add`, and the drain requires an active generation model; a raw-only write path is proposed but unimplemented (`memhub/docs/TODO-raw-recall-without-model.md` "Problem").[^hy-memory]
- Platform: Windows unsupported; macOS x64 not shipped in 1.0.6; no auto-updater; preview release (`docs/INSTALLATION.md` platform table; `README.md` "发行与平台合同"). Desktop packaging configs mention Windows NSIS (see [apps](memhub-apps-and-packages.md)).[^hy-memory]
- Ultra hard-fails without Kuzu; graph width mismatch is inspected at startup (`memory-mode-evolve-v1.md` §1; `hy_graph_admin.py`).[^hy-memory]
- Never infer deletion from absence (vanished host files, missing grants) (`ARCHITECTURE.md` "Engineering Rules").[^hy-memory]
- Matters/session-inbox/change-outbox are deleted placeholders, dropped on upgrade (`ARCHITECTURE.md`).[^hy-memory]

## Relationships

- Builds on: [SDK API and config](hy-memory-sdk-api-and-config.md).
- Detailed in: [modes and write queue](memhub-memory-modes-and-write-queue.md), [import adapters](memhub-import-adapters-and-live-sync.md), [embedding switching](memhub-embedding-space-switching.md), [privacy and permissions](memhub-privacy-and-permissions.md).
- Part of: [Hy Memory overview](hy-memory-overview.md).

## Coverage and limits

Static inspection (delegated). `apps/core/src/one_memory/` has ~559 files in the Core tree; modules were read at docstring/route level, not exhaustively. Contract documents were summarised one line each, not reproduced. Version numbers (build 45, 2.0.14) may change quickly (`stale_after` not set; re-check against a newer revision).

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
