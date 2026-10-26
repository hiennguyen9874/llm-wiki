---
type: Concept
title: "OpenRAG Python and TypeScript SDKs"
description: "SDK authentication, frontend-origin routing, language-specific streaming interfaces, and integration parity limits."
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

**Observed:** the Python and TypeScript `openrag-sdk` packages wrap versioned chat, search, documents, settings, and knowledge-filter APIs. Both default to `http://localhost:3000` and construct `/api/v1/...` requests through the Next.js proxy; a bare backend URL is not automatically equivalent.[^openrag-repo]

## Authentication and runtime

- Explicit `api_key`/`apiKey` overrides `OPENRAG_API_KEY`; normal key transport is `X-API-Key`.
- Python requires Python ≥3.11 and uses async httpx; it allows extra authentication headers for gateway-managed identity and otherwise raises when credentials are absent.
- TypeScript requires Node ≥22 and uses fetch.
- Snapshot SDK versions are `0.4.0.dev0` (Python) and `0.4.0-dev0` (TypeScript), distinct from the application package version.[^openrag-repo]

## Streaming interfaces

| Python | TypeScript |
| --- | --- |
| `chat.create(stream=True)` returns an async event iterator | Streaming events are async iterable |
| `chat.stream(...)` provides a context-managed `ChatStream` | `ChatStream` supports `AsyncIterable` and `Disposable` |
| Aggregates text, sources, chat ID and final text | Provides corresponding streaming aggregation |

Both parse public SSE `data:` frames; malformed JSON frames are skipped. Streams are single-consumption objects. Their public `content/sources/done` contract differs from the browser's internal NDJSON. **Synthesis:** applications needing reliable completion should check for final completion/ID rather than relying on accumulated text alone.[^openrag-repo]

## Error, timeout, and pagination differences

Python maps status codes to typed exceptions and reads server error payloads. The TypeScript `_handleError` path produces generic status-derived messages rather than awaiting the server body. Its request timeout timer is cleared after the fetch response is obtained, so it does not bound the full streaming body lifetime. These are static implementation differences, not measured failure behavior.[^openrag-repo]

Python's document API documents the 500-file cap of `get_all_files` and recommends cursor-based listing for larger sets. A TypeScript client-side page-size fallback does not alter the server endpoint's hard cap. Consult [public API pagination](openrag-public-api.md) rather than assuming “all” means unbounded.[^openrag-repo]

## Relationships

- Uses [public API](openrag-public-api.md), [chat SSE](openrag-chat-streaming.md), and [security](openrag-auth-security.md).
- Preferred over directly calling exported Langflow snippets, which omit OpenRAG runtime configuration (**Reported** documentation).
- Alternative to [MCP](openrag-mcp.md) for programmatic clients, and required for file ingestion when MCP multipart conversion is excluded.[^openrag-repo]

## Coverage limits

Client/chat implementations were inspected more deeply than all search/filter/model helper modules. No packages were installed and no SDK tests or network requests ran. Published package contents/version compatibility were not checked; this page describes repository code only. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `sdks/python/{pyproject.toml,README.md}`; `sdks/python/openrag_sdk/{client,chat,documents}.py::{OpenRAGClient,ChatStream,_request,_handle_error}`; `sdks/typescript/package.json`; `sdks/typescript/src/{client,chat,documents,index}.ts::{OpenRAGClient,ChatStream,_request,_handleError}`; `src/api/v1/files.py::get_all_files`; `docs/docs/core-components/chat.mdx` § Integrate OpenRAG chat into an application.
