---
type: Concept
title: Memos API and MCP interfaces
description: Structured API routing, live events and the OpenAPI-derived MCP adapter in Memos.
tags: [note-taking, memos, api, mcp]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:10:00Z' }
sources:
  - id: memos
    resource: ../raw/memos/README.md
    scope: ../raw/memos/
    kind: code
    revision: 88a20fe
    title: Memos repository
---

**Observed:** Memos registers Connect and gRPC-Gateway handlers for instance, auth, user, memo, Space, attachment, AI and identity-provider services. Both transports use a shared authorizer; unresolved gateway procedures are treated as protected. The router also serves `/api/sse` and returns HTTP 410 for removed `/api/v1/` and `memos.api.v1` routes.[^memos]

## MCP

At `/mcp`, a stateless Streamable HTTP server creates a curated tool catalog from the embedded OpenAPI specification. Tool calls are validated and forwarded in-process to the existing API handler with the caller's authorization header. It provides tools rather than a separate data store; therefore API resource authorization remains relevant. The implementation disables the SDK's localhost protection and instead uses its own Origin/Host check; its efficacy was not dynamically tested.[^memos]

See [security](memos-security.md), [overview](memos-overview.md), and [source coverage](memos-source-map.md).

[^memos]: `server/api/api.go::NewHandler`; `server/mcp/service.go::NewMCPService`, `newMCPToolHandler`, `RegisterRoutes`; `server/mcp/README.md` §§ Startup flow, Request flow.
