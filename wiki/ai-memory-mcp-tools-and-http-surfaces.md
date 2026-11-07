---
type: Concept
title: ai-memory MCP tools and HTTP surfaces
description: The 27 memory_* MCP tools, the /web and /api/v1 HTTP surfaces, opt-in serve flags, and localization of the web UI.
tags: [agent-memory, ai-memory, mcp, http, web-ui, api]
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
  - id: mcp-server
    resource: ../raw/ai-memory/crates/ai-memory-mcp/src/server.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: MCP server.rs (tool_router)
  - id: web-code
    resource: ../raw/ai-memory/crates/ai-memory-web/src/routes/api.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory-web routes (api.rs, mount.rs)
  - id: frontend-api
    resource: ../raw/ai-memory/docs/frontend-api.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Frontend API
  - id: management-ui
    resource: ../raw/ai-memory/docs/management-ui.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Management UI
  - id: localization
    resource: ../raw/ai-memory/docs/localization.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Interface localization
---

# ai-memory MCP tools and HTTP surfaces

ai-memory exposes its memory to agents through an MCP server with **27 `memory_*` tools** and to humans and frontends through an opt-in read-mostly web UI and a JSON API.[^mcp-server][^readme] The count is **Observed**: `grep -n '#\[tool('` on `server.rs` returns 28 lines, of which 27 are real attributes and one (line 13990) is a doc comment mentioning the attribute.

Evidence class: **Observed** by delegated static inspection; nothing executed.

## MCP tools

- **Query/read:** `memory_query`, `memory_recent`, `memory_read_page`, `memory_read_session_observations`, `memory_status`, `memory_briefing` (structured JSON), `memory_explore` (LLM prose digest).
- **Write:** `memory_write_page`, `memory_write_pages_batch` (1–100 pages, 1 MiB/page, 8 MiB total), `memory_patch_page`, `memory_resolve_write_target`, `memory_delete_page`, `memory_restore_page`.
- **Maintenance:** `memory_feedback` (helpful / not_helpful / stale / wrong), `memory_lint`, `memory_forget_sweep`, `memory_consolidate`, `memory_auto_improve`, `memory_install_self_routing`.
- **Coordination:** `memory_handoff_begin|list|accept|cancel`, `memory_message_send|list|pop|cancel` (see [Handoffs and messaging](ai-memory-handoffs-and-messaging.md)).[^mcp-server]

`memory_query` parameters: `query`, `limit` (default 10, clamp 1–100), `kind`, `tier`, `path_prefix`, `tag`, `project`, `workspace`, `scopes[]`, `global`, `include_expired`, `include_superseded`, `pin_first`, `explain`, `as_of`, `answer`, `reasoning` (`minimal…max`). Details in [Retrieval pipeline](ai-memory-retrieval-pipeline.md).[^mcp-server]

## HTTP surfaces

- **Core routes:** `/mcp` (stateless by default), `/hook`, `/auth/*`, `/identity`, `/admin/*`, `/management/v1/*`.[^web-code]
- **`/web`** (built-in server-rendered UI, askama): project index, docs, search, pending, workstreams overview, health, cross-project `/graph` and per-project graph, page/history/session/agent views, agent `/inbox` with POST routes for composing messages.[^web-code]
- **`/api/v1`** (read-only JSON): docs, workspaces, projects, pages, `search` (GET/POST), history, recent, briefing, overviews, handoffs, sessions, observations, graphs.[^web-code][^frontend-api]

## Opt-in flags (all off by default)

`--enable-web`, `--enable-api` (API only, no UI), `--web-ui-dir` (custom SPA; needs `--enable-web`), `--web-slug`, `--base-path`, `--enable-management-ui` (needs the `management-ui` cargo feature **and** the runtime flag, HTTP transport only), `--enable-session-management`, `--enable-self-service-keys`. Enabling the management UI also mounts the latter two.[^web-code][^management-ui][^readme]

## Localization

English and Brazilian Portuguese via five Fluent catalogs; the web UI negotiates per request (cookie `ai_memory_language` beats `Accept-Language`), while `/api/v1` JSON, MCP payloads, stored pages and logs are not localized.[^localization]

## Relationships

- Authorization of these routes: [Auth and security](ai-memory-auth-and-security.md).
- Built from crates described in [Architecture](ai-memory-architecture.md).

[^readme]: `../raw/ai-memory/README.md` — "Everyday use" (web view, `/web/graph`, `/api/v1`), "Teams and multiple machines" (opt-in HTTP surfaces).
[^mcp-server]: `../raw/ai-memory/crates/ai-memory-mcp/src/server.rs::tool_router, QueryArgs`; 27 `#[tool(` attributes between lines 3173 and 8020 (checked directly with grep this session); `docs/ARCHITECTURE.md` "MCP tool surface (27 tools)" agrees.
[^web-code]: `../raw/ai-memory/crates/ai-memory-web/src/routes/api.rs::build`, `src/mount.rs`, `src/routes/{inbox,graph,workstreams}.rs`; `crates/ai-memory-cli/src/commands/serve.rs` (flag wiring).
[^frontend-api]: `../raw/ai-memory/docs/frontend-api.md` — API endpoint sections (§4.x).
[^management-ui]: `../raw/ai-memory/docs/management-ui.md` — feature gates and public-deployment notes.
[^localization]: `../raw/ai-memory/docs/localization.md`; `crates/ai-memory-web/src/localization.rs`.
