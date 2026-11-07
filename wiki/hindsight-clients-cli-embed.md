---
type: Concept
title: Hindsight clients, CLI, embed daemon and dev tooling
description: Hindsight's Python/TypeScript/Go/Rust SDKs and how they are generated, the Rust CLI, the hindsight-embed local daemon, and hindsight-dev tooling.
tags: [agent-memory, hindsight, sdk, cli, tooling]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: py-client
    resource: ../raw/hindsight/hindsight-clients/python/pyproject.toml
    kind: code
    revision: eb963cb
    title: Python client manifest
  - id: cli
    resource: ../raw/hindsight/hindsight-cli/Cargo.toml
    kind: code
    revision: eb963cb
    title: hindsight-cli manifest
  - id: embed
    resource: ../raw/hindsight/hindsight-embed/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-embed manifest
  - id: dev
    resource: ../raw/hindsight/hindsight-dev/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-dev manifest
---

Every Hindsight client is derived from one OpenAPI 3.1 spec (`hindsight-docs/static/openapi.json`, version 1.2.0) emitted from the FastAPI app by `hindsight-dev/hindsight_dev/generate_openapi.py`; hand-written wrappers sit on top of generated code in Python and TypeScript.[^py-client][^dev] Install lines in the README: `pip install hindsight-client`, `npm install @vectorize-io/hindsight-client`, `go get github.com/vectorize-io/hindsight/hindsight-clients/go`, and a `get-cli` installer.[^readme]

## SDKs (Observed)

| Client | Package / version | Generation | Hand-written layer |
| --- | --- | --- | --- |
| Python | `hindsight-client` 1.2.0 (≥3.10) | openapi-generator v7.10.0 (asyncio) into `hindsight_client_api/` | `hindsight_client/hindsight_client.py::Hindsight`, sync wrappers over `a*` async twins; retries only idempotent calls (recall/reflect) on 429/503 honouring `Retry-After` |
| TypeScript | `@vectorize-io/hindsight-client` 1.2.0 | `@hey-api/openapi-ts` 0.97.3 | `src/index.ts::HindsightClient`; CJS+ESM via tsup; Deno-tested |
| Go | module `github.com/vectorize-io/hindsight/hindsight-clients/go` | Entirely generated (openapi-generator v7.10.0) plus sed patches | `hindsight_client.go` helpers |
| Rust | `hindsight-client` 0.1.0 | `progenitor` 0.11 at build time in `build.rs` | `src/lib.rs` helpers (user-agent aware client) |

`scripts/generate-clients.sh` pins the generator and applies post-generation patches; clients are regenerated only at release.[^py-client] The `release.sh` script does not bump the Rust client (still 0.1.0), and some client READMEs and config files are stale (Go README says 1.0.0, Rust README references removed methods) — Observed.[^dev]

## CLI (`hindsight`)

Rust (`hindsight-cli` 1.2.0, clap, ratatui TUI) built on the Rust client. Commands: `bank`, `memory` (retain/recall/reflect/…), `document`, `entity`, `tag`, `chunk`, `operation`, `mental-model`, `knowledge-base`, `directive`, `webhook`, `audit`, `fs`, `health`, `metrics`, `explore` (TUI), `ui`, `configure`, `profile`. Config precedence: `HINDSIGHT_API_URL`/`HINDSIGHT_API_KEY` → named profile `~/.hindsight/cli-profiles/<name>.toml` → `~/.hindsight/config` → `http://localhost:8888`. `fs mount` mirrors a bank's [knowledge pages](hindsight-consolidation-and-mental-models.md) as local Markdown refreshed every 30 s (read-only unless `--writable`).[^cli]

## hindsight-embed

A thin local front end that auto-manages a detached `hindsight-api` daemon on `127.0.0.1:8888` with embedded Postgres (`pg0://hindsight-embed-<profile>`), forwards unknown commands to the `hindsight` CLI, and offers profiles, `daemon`, `ui` and `control` commands. Named profiles hash into ports 8889–9888. Idle auto-exit defaults to **disabled** (`HINDSIGHT_EMBED_DAEMON_IDLE_TIMEOUT=0`), contradicting the package README's 5-minute claim (curator-verified). The control center is token-gated (`X-Hindsight-Control-Token`) and loopback-bound.[^embed]

## hindsight-dev

Console scripts for `generate-openapi`, `generate-bank-template-schema`, `generate-changelog` (LLM-written release notes), `sync-cookbook`, `generate-llms-full`, `check-openapi-compatibility`, `client-coverage-check` / `cli-coverage-check` (assert wrappers expose every spec field), and perf/micro benchmarks (`perf-test`, `entity-resolver-bench`, …); LoComo/LongMemEval runners were moved to the external AMB project.[^dev]

## Relationships

Clients call the [API surface](hindsight-api-surface.md); the [control plane](hindsight-control-plane.md) uses the TypeScript client; [integrations](hindsight-integrations.md) wrap these clients; release flow in [Contributor workflow](hindsight-contributor-workflow.md).

[^readme]: `README.md` § "Quick Start → Connect a client".
[^py-client]: `hindsight-clients/python/pyproject.toml`, `hindsight_client/hindsight_client.py`; `hindsight-clients/typescript/{package.json,openapi-ts.config.ts}`; `hindsight-clients/go/`; `hindsight-clients/rust/{Cargo.toml,build.rs}`; `scripts/generate-clients.sh`.
[^cli]: `hindsight-cli/Cargo.toml`, `src/main.rs::Commands`, `src/config.rs`, `src/commands/fs/`.
[^embed]: `hindsight-embed/pyproject.toml`, `hindsight_embed/cli.py`, `daemon_embed_manager.py::DEFAULT_DAEMON_IDLE_TIMEOUT`, `profile_manager.py`, `control_center/server.py`; `README.md` line 13.
[^dev]: `hindsight-dev/pyproject.toml` `[project.scripts]`; `hindsight_dev/generate_openapi.py`, `client_coverage_check.py`; `scripts/release.sh`.
