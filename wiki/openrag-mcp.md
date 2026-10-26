---
type: Concept
title: "OpenRAG built-in MCP server"
description: "Streamable-HTTP MCP route conversion, required authentication headers, explicit exclusions, and retired-package documentation drift."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

**Observed:** OpenRAG mounts a FastMCP streamable-HTTP server at `/mcp`, generated from selected FastAPI routes after registration. The parent explicitly manages the mounted app's lifespan. This built-in service is the documented replacement for the retired standalone `openrag-mcp` package.[^openrag-repo]

## Exposure model

`create_mcp_server` converts versioned routes into tools, including GETs: code comments explain that many agent clients invoke tools but do not surface MCP resources. Customized names include `openrag_chat`, `openrag_search`, file/knowledge-filter tools, settings, and enhanced task status.[^openrag-repo]

Ordered exclusions precede broad includes:

1. `GET /v1/models` and `POST /v1/chat/completions|/v1/embeddings` are excluded model-proxy plumbing.
2. `POST /v1/documents/ingest` is excluded: the implementation comment reports FastMCP does not reconstruct the required multipart upload. Use HTTP/SDK instead.
3. Remaining `/v1/*` methods and GET `/v2/files*` become tools; other paths are excluded.[^openrag-repo]

**Synthesis:** this is a broad inherited API capability surface, including mutation/deletion tools, not a read-only knowledge search server. Permissions and gateway exposure remain consequential.[^openrag-repo]

## Authentication and frontend routing

The server module documents that FastMCP's internal proxy strips `Authorization`; use `X-API-Key` for OpenRAG keys. Gateway-managed IBM identity uses a forwarded `X-OpenRAG-API-JWT` after edge authentication; the edge must not trust an arbitrary client-supplied identity header. The external gateway mechanism is **Reported by code comments**, not independently exercised.[^openrag-repo]

The frontend rewrites `/mcp/*` through its API proxy, so `http://localhost:3000/mcp` is the documented user-facing origin while a direct backend deployment can mount the same service on port 8000.[^openrag-repo]

## Contradictions and retirement

- `sdks/mcp/README.md` lists ingestion and suggests `Authorization: Bearer`; current route maps exclude multipart ingestion and the server module warns the header is stripped. Treat the README as a conflicting claim, not proof the advertised methods work.
- The root README also broadly advertises document ingestion among MCP capabilities; the current explicit exclusion is the implementation evidence.
- The standalone package metadata marks it retired/inactive. Its `__init__.py` imports `openrag_mcp.server`, but that module is absent in the inspected tree. **Synthesis:** that import is unresolved in this snapshot; it was not executed. This ingest does not infer a package-release or effective retirement date beyond the pinned snapshot.[^openrag-repo]

## Relationships

- Uses [public API](openrag-public-api.md) and [security](openrag-auth-security.md).
- Reached through the [frontend proxy](openrag-frontend.md).
- Distinct from internal Langflow URL-tool MCP in [workflows](openrag-langflow-workflows.md); uses [SDK/HTTP ingestion](openrag-sdks.md) rather than multipart tools.

## Coverage limits

No MCP client, transport session, header-forwarding test, or retired-package import was run. FastMCP dependency internals were not independently audited. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `src/mcp_http/server.py::{create_mcp_server,COMPONENT_CUSTOMIZATIONS}` and authentication module docstring; `src/app/routes/mcp.py::mount_mcp`; `frontend/next.config.ts::rewrites`; `frontend/app/api/[...path]/route.ts::proxyRequest`; `sdks/mcp/{README.md,pyproject.toml,src/openrag_mcp/__init__.py}`; `README.md` § Model Context Protocol; `docs/docs/reference/api-sdk-overview.mdx`.
