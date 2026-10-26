---
type: Concept
title: WeKnora MCP server surfaces
description: Built-in scoped Streamable HTTP endpoints, the CLI stdio catalog, and the deprecated Python server are distinct MCP products.
tags: [ml, weknora, mcp, integrations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2026-12-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora exposes multiple MCP implementations with different transports, tool catalogs, and credentials. **Observed:** the built-in Go app server publishes workspace-scoped HTTP endpoints; the CLI offers a separate curated stdio server; the Python package remains present but is explicitly deprecated. A single “MCP version” or tool count would conflate different artifacts.[^weknora]

## Built-in endpoint server

`internal/mcpserver/server.go` uses endpoint-aware visibility filtering **and** call-time tool guards. HTTP routes `/mcp/:endpoint_id` are mounted with their own authentication before global app auth; stateless transport supports requests reaching different replicas. The endpoint model stores a token hash/hint, KB and tool allowlists, enabled state, and a default per-minute limit of 60.[^weknora]

**Observed catalog:** twelve tools across retrieval, chat, wiki, and ingestion: KB listing, search, grep, document listing/reading, ask, wiki search/read/index, and document add/update/delete. Write groups default off. Scope helpers reauthorize allowlisted KBs and drop stale/foreign IDs; filtering tools out of discovery is not the only enforcement step.[^weknora]

## Other server implementations

- [CLI](weknora-cli-sdk.md): curated ten-tool stdio catalog with accumulated tool results.
- Python `mcp-server/`: package version 1.1.1, with stdio/SSE/HTTP transport support; network transport requires separate server authentication, and upload-path helpers constrain local files to configured roots. Its README announces deprecation and future removal.[^weknora]

**Observed naming difference, not a proven contradiction:** the Go built-in server self-identifies as 1.0.0, while the Python package is 1.1.1 and historical README release notes mention a different earlier tool count. These version labels do not establish one linear server upgrade path. Python tool bodies were only partly inspected.[^weknora]

## Relationships

- Publishes [knowledge retrieval](weknora-hybrid-retrieval.md) and [wiki pages](weknora-wiki-compilation.md).
- Depends on [workspace/machine-principal security](weknora-security.md).
- Distinct from WeKnora acting as an **MCP client** inside its agent; outbound MCP/OAuth implementation remains pending.
- Other external delivery surfaces: [embed/IM channels and harness integration](weknora-publishing-channels.md).

## Coverage limits

Server setup, endpoint auth/scope/model, catalog symbols, and selected Python transport/path code were inspected. No MCP handshake, tool call, OAuth flow, rate-limit test, upload test, or proxy deployment ran. Actual replicated limiter behavior and complete per-tool scope enforcement remain pending; see the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `internal/mcpserver/server.go` server constants, filters and guard middleware; `mcpserver/scope.go::allowedKnowledgeBases`; `internal/types/mcp_endpoint.go::MCPEndpoint`; `types/mcp_endpoint_tools.go` catalog/group defaults; `internal/router/routes_mcp_endpoint.go::RegisterMCPServerRoutes`; `internal/middleware/mcp_endpoint_auth.go::MCPEndpointAuth`; `cli/internal/mcp/tools.go`, `server.go::RunStdio`; `mcp-server/README.md`, opening deprecation notice; `mcp-server/pyproject.toml`; `mcp-server/weknora_mcp_server.py` configuration, network authentication, transports, and `main`; `mcp-server/upload_paths.py::resolve_upload_file_path`. Package entry: [README](../raw/WeKnora/README.md), “Clients and Integrations” and v0.8.2 “Built-in MCP Server.”
