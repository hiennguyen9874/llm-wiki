---
type: Concept
title: "RAGFlow frontend and API integration"
description: "React/Vite feature routing, query/service/request layers, Go proxy routes, agent canvas state, and browser SSE transports."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:16:02Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa024356711dc86de2e231afb0e4bf1
    title: RAGFlow repository snapshot
---

# RAGFlow frontend and API integration

**Observed:** the browser application uses React/TypeScript/Vite with TanStack Query, Zustand, XYFlow, Tailwind/Radix UI and rich-text/graph integrations. It exposes datasets/documents/chunks, chats/search, agent canvases, memories, skills, files, settings and admin feature routes. UI route presence does not prove backend entitlement or end-to-end feature completeness.[^ragflow]

## Request architecture

Agent hooks call service registrations backed by a shared Axios instance. `registerNextServer` translates URL/method records into clients. The shared request interceptor converts keys to snake_case, injects tenant parameters and authorization unless explicitly skipped; response handling covers authentication redirects and selected API/error shapes. Query-key factories centralize cache identity.[^ragflow]

## Streaming is an intentional transport exception

Generic SSE uses native fetch, an AbortController, TextDecoderStream and EventSourceParserStream; it accepts done sentinels and normalizes event data. Chat completion streaming also uses fetch because browser Axios does not expose `Response.body`. The agent chat hook consumes typed workflow, node, message, user-input, waiting-for-user and node-log events; canvas UI state uses Zustand/Immer with XYFlow node/edge changes.[^ragflow]

## Development routing and backend boundaries

Vite proxies `/api/v1/admin` to Go admin port 9381 and `/api` plus `/v1` to Go API port 9380; the dev server defaults to 9222 unless `PORT` is set. The inspected frontend targets the Go backend, not a selectable Python/Go implementation. Endpoint constants retain both `/v1` and `/api/v1` shapes.[^ragflow]

Backend router groups separate unauthenticated, beta-token and session-authorized routes. Agent run uses SSE, while the separate MCP listener has its own transport requirements. **Synthesis:** browser visibility, tenant parameters and frontend auth redirects are not substitutes for backend authorization checks.[^ragflow]

## Relationships

- **Uses:** [agent workflows](ragflow-agent-workflows.md) and [citation/reference payloads](ragflow-citations.md).
- **Depends on:** [server architecture](ragflow-architecture.md) and [operations](ragflow-operations.md) for proxy/runtime alignment.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa024356711dc86de2e231afb0e4bf1`; locators: `web/package.json::dependencies / devDependencies`; `web/src/routes.tsx::Routes / createBrowserRouter`; `web/src/hooks/use-agent-request.ts::AgentKeys / agent hooks`; `web/src/services/agent-service.ts::registerNextServer client`; `web/src/utils/register-server.ts::registerNextServer`; `web/src/utils/next-request.ts::axios.create / request and response interceptors`; `web/src/hooks/use-send-message.ts::useSendMessageBySSE`; `web/src/services/chat-completion-stream.ts::requestChatCompletionStream`; `web/src/pages/agent/chat/use-send-agent-message.ts::SSE integration`; `web/src/pages/agent/store.ts::Zustand store`; `web/vite.config.ts::server.port / server.proxy`; `web/src/utils/api.ts::webAPI / restAPIv1`; `internal/router/router.go::Setup`; `internal/handler/agent.go::RunAgent`; `internal/server/api/server.go::MCP HTTP server`.
