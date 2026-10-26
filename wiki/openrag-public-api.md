---
type: Concept
title: "OpenRAG public API"
description: "Versioned integration endpoints, permission requirements, file pagination, mode-specific routes, and internal/proxy API distinctions."
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

**Observed:** the versioned OpenRAG API serves chat, search, document ingestion/tasks, file listing, knowledge filters, settings/models, and selected service status. It uses API-key or gateway-derived identity and permission dependencies, unlike the session-oriented browser surface. RBAC permission checks only enforce fine-grained grants when enabled.[^openrag-repo]

## Main integration routes

| Route family | Purpose / permission boundary |
| --- | --- |
| `POST /v1/chat` | Chat, `chat:use` |
| `GET /v1/chat`, `GET /v1/chat/{chat_id}` | Own conversation read |
| `DELETE /v1/chat/{chat_id}` | Own conversation deletion |
| `POST /v1/search` | Search, `search:use` |
| `POST /v1/documents/ingest` | Multipart upload, `knowledge:upload` |
| `DELETE /v1/documents` | Own/anonymous knowledge deletion permissions |
| `/v1/tasks/*` | Task status and enhanced structured failure information |
| `/v1/files/get_all`, `/v2/files`, `/v2/files/search` | Knowledge file listing/search |
| `/v1/knowledge-filters*` | Saved subsets, distinct create/read/edit permissions |
| `GET/POST /v1/settings` | Provider read versus configuration write |

Chat-only permissions do not imply permission to list/read conversations. Status and component-log routes are registered only in OSS mode, so other modes can return route absence rather than a permission error. Literal task subpaths register before parameterized routes to avoid shadowing.[^openrag-repo]

## Pagination and filters

`/v1/files/get_all` uses a server-side cap of **500**, despite the name. V2 listing uses `page_size=25` by default, maximum 500, `sort_order=asc|desc`, and an `after_key` JSON cursor; `page` is for display, not the pagination mechanism. Larger collections require cursor traversal.[^openrag-repo]

Filter resolution combines a saved `filter_id` with per-field inline overrides. Filters scope search/retrieval but do not replace ownership/DLS checks. Document deletion accepts a filename or a filter's explicit data-source names, rejecting wildcard-based deletion on that filter path.[^openrag-repo]

## Do not conflate API surfaces

- Browser `/langflow` streams NDJSON with `prompt`, `conversation_id`, and `previous_response_id`; public chat uses SSE with `message` and `chat_id`.
- `/v1/models`, `/v1/chat/completions`, and `/v1/embeddings` also serve Langflow model-proxy plumbing with dedicated token dependencies. Their OpenAI-compatible shape does not make them unrestricted public agent tools.
- SDKs default to the frontend origin and call `/api/v1/...`; direct backend routes are `/v1/...`. Base URL and prefix handling must match the selected client.[^openrag-repo]

## Relationships

- Depends on [security](openrag-auth-security.md); used by [SDKs](openrag-sdks.md) and selectively auto-exposed by [MCP](openrag-mcp.md).
- Uses [chat contract](openrag-chat-streaming.md), [retrieval](openrag-hybrid-retrieval.md), and [ingestion](openrag-document-ingestion.md).

## Coverage limits

This is a route-family map, not a complete OpenAPI/schema reproduction. Endpoint error paths, gateway compatibility, all role combinations, and v2 cursor correctness were not exercised. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `src/app/routes/{public_v1,public_v2,internal}.py` registration functions; `src/dependencies.py::{require_api_key_permission,require_api_key_any_permission}`; `src/api/v1/{chat,search,documents,files,knowledge_filters,llm}.py`; `src/api/v1/_filter_resolution.py`; `src/api/v2/files.py` query parameters; `src/mcp_http/server.py::COMPONENT_CUSTOMIZATIONS`; `sdks/python/openrag_sdk/client.py::DEFAULT_BASE_URL` and request paths.
