---
type: Concept
title: Hindsight API surface, services and packaging
description: Hindsight's server entry points (REST, MCP, worker, admin CLI), async operations, and how the api, api-slim, all, all-slim and all-npm packages differ.
tags: [agent-memory, hindsight, api, mcp, packaging]
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
  - id: api-pyproject
    resource: ../raw/hindsight/hindsight-api-slim/pyproject.toml
    kind: code
    revision: eb963cb
    title: hindsight-api-slim package manifest
  - id: mcp-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/mcp-server.md
    kind: documentation
    revision: eb963cb
    title: MCP server developer doc
  - id: admin-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/admin-cli.md
    kind: documentation
    revision: eb963cb
    title: Admin CLI developer doc
  - id: services-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/services.md
    kind: documentation
    revision: eb963cb
    title: Services developer doc
---

The server is a FastAPI app (`hindsight_api.api.create_app`) exposing ~120 REST routes under `/v1/default/banks/{bank_id}/…` and a Model Context Protocol endpoint per bank, with a separate worker process that drains a Postgres-backed task queue.[^api-pyproject][^mcp-doc]

## Console scripts (Observed)

`hindsight-api` (`hindsight_api.main:main`, port 8888), `hindsight-worker` (`worker.main:main`), `hindsight-local-mcp` (`mcp_local:main`), `hindsight-admin` (`admin.cli:main`).[^api-pyproject]

## REST

Resource families: `memories/recall`, `memories` (retain), `reflect`, `consolidate`, `observations`, `mental-models`, `knowledge-base/*`, `directives`, `entities`, `graph`, `documents`, `operations`, `webhooks`, `audit-logs`, `config`, `stats`, `transfer/export|import`, plus `/v1/version` and `/metrics` (Observed). Health: `/health/live` (no DB), `/health/ready` (checks DB) (Reported).[^api-pyproject][^services-doc]

## MCP

- Every server ships a built-in MCP endpoint per bank, exposing retain, recall and reflect as tools.[^readme] Enabled by default at `/mcp/{bank_id}/`; open by default, Bearer auth via `HINDSIGHT_API_MCP_AUTH_TOKEN` or a tenant extension. Bank resolution order: URL path > `X-Bank-Id` > `HINDSIGHT_MCP_BANK_ID` (default `default`).[^mcp-doc]
- Single-bank mode exposes 27 tools, multi-bank `/mcp/` 30 (adds `list_banks`, `create_bank`, `get_bank_stats`); tools are annotated `readOnlyHint` / `destructiveHint` (Reported). Tool implementations are in `mcp_tools.py` (retain, recall, reflect, bank/document/mental-model/knowledge-base/directive CRUD, operations).[^mcp-doc][^api-pyproject]
- `hindsight-local-mcp` is documented as stdio but is implemented as a launcher that starts the full API on :8888 with `pg0://hindsight-mcp`; see [discrepancies](hindsight-doc-code-discrepancies.md).

## Worker and async operations

`async_operations` is the work queue (types include `retain`, `consolidation`, `refresh_mental_model`, `webhook_delivery`, `export_bank`, `import_bank`); `WorkerPoller` claims batches, executes tasks and shuts down gracefully. API (`:8888`, stateless) and worker (`:8889`, same image) scale separately with Postgres as broker (`HINDSIGHT_API_WORKER_*`). Observed in `worker/poller.py`; Reported in `services.md`.[^services-doc][^api-pyproject]

## Admin CLI (`hindsight-admin`)

`run-db-migration`, `repair-bank`, `rename-bank`, `reembed` (in-place embedding model switch; mixed vectors degrade recall, 503 guard until `--finish`), `backup`/`restore` (zip with REPEATABLE READ snapshot; restore deletes the target schema), `export-bank`/`import-bank`, `decommission-worker(s)`, `worker-status`, `cloud login`.[^admin-doc]

## Package variants (Observed)

| Package | Content |
| --- | --- |
| `hindsight-api-slim` | The actual code; base deps only; extras `local-ml`, `local-llm`, `local-onnx`, `embedded-db`, `oracle`, `all` |
| `hindsight-api` | Ships no code; depends on `hindsight-api-slim[all]` and re-declares the four scripts |
| `hindsight-all` | `api-slim[all]` + `hindsight-client` + `hindsight-embed`; Python `hindsight` module (`HindsightServer`, `HindsightClient`, `HindsightEmbedded`) |
| `hindsight-all-slim` | Same deps without extras; no module of its own |
| `hindsight-all-npm` | `@vectorize-io/hindsight-all` (Node ≥ 22); manages a local `hindsight-embed` daemon; ships no HTTP client |

[^api-pyproject]: `hindsight-api-slim/pyproject.toml` `[project.scripts]`, extras; `hindsight_api/api/http.py::create_app`, `api/mcp.py`, `mcp_tools.py`, `worker/poller.py::WorkerPoller`; `hindsight-api/pyproject.toml`; `hindsight-all*/` manifests.
[^mcp-doc]: `hindsight-docs/docs/developer/mcp-server.md` (modes, auth, bank resolution, tool annotations).
[^admin-doc]: `hindsight-docs/docs/developer/admin-cli.md`.
[^services-doc]: `hindsight-docs/docs/developer/services.md`; `monitoring.md` (health endpoints).
[^readme]: `README.md` § "MCP Server", "Python Embedded".
