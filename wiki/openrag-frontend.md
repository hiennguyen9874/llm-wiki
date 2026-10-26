---
type: Concept
title: "OpenRAG frontend and request proxy"
description: "Browser feature surfaces, Next.js proxy and build constraints, permission affordances, and frontend test boundaries."
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
    revision: 6fc819d3ec10ee3d0dedc842d244ec2b63fd9791
    title: OpenRAG repository
---

**Observed:** OpenRAG's Next.js App Router frontend implements chat, knowledge browsing, settings/connectors, onboarding, and authentication screens. A same-origin catch-all API proxy forwards browser traffic to the Python backend; the UI primarily uses internal session-cookie routes rather than the public SDK API.[^openrag-repo]

## Stack and build contract

Declared dependencies include Next.js `^16.4.0`, React `^19.2.7`, TypeScript `^6.0.3`, Node ≥22, Tailwind 4, Radix primitives, TanStack Query 5, Zustand 5, Axios, AG Grid, React Markdown, and Docling UI components. Version ranges are not a lockfile audit. The frontend image uses a Node 24 build base.[^openrag-repo]

`next.config.ts` disables image optimization to avoid Sharp/libvips and sets `typescript.ignoreBuildErrors=true`; `typecheck` is a separate script. **Synthesis:** a successful Next build alone cannot establish type correctness. `OPENRAG_FRONTEND_BASE_PATH` is compiled into the browser bundle and needs build-time configuration. `NEXT_DIST_DIR` supports independent dev build directories; the configured experimental proxy timeout is 300,000 ms.[^openrag-repo]

## Request path

1. Axios uses `${frontendBasePath}/api`, sends credentials, and resolves non-2xx responses for explicit handling. Unauthorized redirect selection rejects cross-origin targets.
2. `app/api/[...path]/route.ts::proxyRequest` forwards GET/POST/PUT/DELETE/PATCH to the configured backend host/port/protocol, removes proxy-sensitive headers, and adds a request ID. Multipart bodies are buffered; response streams pass through. Cookies are re-appended explicitly.
3. `/mcp/:path*` rewrites through `/api/mcp/:path*`, enabling the public frontend-origin MCP URL.
4. Basic `/health` is liveness-only; collective health probes backend/Langflow, and separate metrics instrumentation can listen on port 9090.[^openrag-repo]

## User-visible feature surfaces

- Chat: streaming text, function-call inspection, citation/chunk/file previews, nudges, token usage, context-file uploads, and partial-answer recovery affordances. The actual browser wire format is NDJSON, not public SSE.
- Knowledge: AG Grid selection/bulk deletion, filename search and sorting, saved knowledge filters, chunk views, task notifications, provider/Docling health banners, and ingest-review/preview affordances. Grid offset pages map to backend `after_key` cursors.
- Settings: provider, agent, ingestion, connector, and API-key sections with permission-aware navigation and brand/run-mode differences.
- `usePermissions` is explicitly an affordance layer: backend gates remain authoritative. Hidden controls are not a security boundary.[^openrag-repo]

## Relationships

- Uses [backend architecture](openrag-backend-architecture.md), [chat transport](openrag-chat-streaming.md), and [security](openrag-auth-security.md).
- Proxies [public API](openrag-public-api.md) and [MCP](openrag-mcp.md) traffic for external clients as well as internal browser routes.
- Checked by configured tooling described in [testing](openrag-testing.md).

## Coverage limits

Large chat/knowledge pages were inspected by imports and selected handlers, not line-by-line. Onboarding state machines, preview internals, component accessibility, markdown sanitization, telemetry behavior, and connector UI policy were not comprehensively audited. No browser or rendering tests were run. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d3ec10ee3d0dedc842d244ec2b63fd9791`: `frontend/package.json::{dependencies,devDependencies,engines,scripts,overrides}`; `frontend/next.config.ts`; `Dockerfile.frontend`; `frontend/lib/api-client.ts::apiClient`; `frontend/app/api/[...path]/route.ts::proxyRequest`; `frontend/app/health/{route.ts,collective_health/route.ts}`; `frontend/instrumentation.node.ts::registerNodeInstrumentation`; `frontend/hooks/{useChatStreaming.ts,use-permissions.ts}`; `frontend/app/{chat,knowledge}/page.tsx` selected handlers/imports; `frontend/app/settings/_components/settings-nav.tsx::TABS`; `frontend/lib/{brand,constants}.ts`.
