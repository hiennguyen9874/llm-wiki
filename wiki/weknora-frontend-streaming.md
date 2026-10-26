---
type: Concept
title: WeKnora frontend and streaming chat state
description: Vue/Vite/Pinia clients, shared SSE state reconstruction, reconnect limits, and desktop/mobile delivery differences.
tags: [ml, weknora, frontend, streaming]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora's main UI and embed UI share a streaming-event vocabulary but have different entry points, authentication, and recovery behavior. **Observed:** the frontend reconstructs answer, reasoning, tool, approval, and completion state from SSE events; correctness depends on event/message identity and stale-request suppression, not simply on keeping an HTTP connection alive.[^weknora]

## Stack and state

**Observed dependency declarations:** Vue `^3.5.34`, Vite `^7.3.5`, Pinia `^3.0.4`, vue-router `^4.5.0`, TypeScript `~6.0.3`, TDesign `^1.19.2`, and fetch-event-source `^2.0.1`. These are manifest ranges, not measured installed runtime versions. Vite builds main and embed HTML entries; runtime public configuration and API base-path derivation are separate from build-time settings.[^weknora]

`createCachedResource` and the versioned request coordinator support shared chat resource snapshots, in-flight coalescing, explicit refresh after writes, and invalidation that rejects stale responses. Agent catalog snapshots are locale-sensitive. This is a selected state-layer account; visual rendering was not inspected in a browser.[^weknora]

## SSE transport and replay

`frontend/src/api/chat/streame.ts::useStream` sends authentication, tenant, request ID, and language context; handshake authentication failure can trigger one shared refresh/replay. A stream-generation counter prevents an old stream from mutating or aborting its replacement.[^weknora]

**Observed reconnect conditions:** an ordinary authenticated agent stream must already know the assistant message ID and not have completed; embed streams are excluded. Recovery attaches to the session continuation endpoint, with at most eight attempts and capped exponential backoff. A 30-second client idle timer watches all frames; inspected server stream code emits heartbeats every ten seconds.[^weknora]

`useChatStreamHandler` demultiplexes answer/thinking/progress, tool calls/results, command output, approvals, suspension, OAuth, artifacts, compaction, steering, and terminal events. Answer fragments are keyed by event ID; replacement retracts the matching contribution instead of blindly appending duplicate text. Completion hydrates artifacts and usage before leaving reply state.[^weknora]

## Delivery-shell differences

- **Observed:** Wails desktop starts a Lite backend with local listener selection and persistent local signing/JWT files.
- **Observed:** the Mini Program requests an SSE response through `wx.request`, then parses/concatenates answer chunks after the response resolves; that path is not incremental browser-style rendering.
- Browser tokens use local storage, while the Mini Program stores API settings in wx storage. These are sensitive-data storage design facts; no token values are retained here.[^weknora]

## Relationships

- Consumes events from the [backend](weknora-backend-architecture.md) and [agent runtime](weknora-agent-runtime.md).
- Parallel consumer to the [CLI and Go SDK](weknora-cli-sdk.md), not a frontend built on the CLI.
- Embed authentication belongs to [publishing channels](weknora-publishing-channels.md).

## Coverage limits

Transport, selected state/event code, manifest/build setup, and delivery-shell interfaces were inspected. View rendering, accessibility, layout, complete event handling, desktop platform behavior, and browser security were not tested. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `frontend/package.json`; `frontend/vite.config.ts::build.rollupOptions.input`; `frontend/public/config.js`; `frontend/src/main.ts::bootstrap`; `frontend/src/utils/api-base.ts::getApiBaseUrl`; `frontend/src/stores/resourceCache.ts::createCachedResource`; `stores/versionedRequest.ts::createVersionedRequestCoordinator`; `stores/chatResources.ts::useChatResourcesStore`; `frontend/src/api/chat/streame.ts::useStream`, `canReconnect`; `frontend/src/utils/authRefresh.ts::refreshAccessTokenShared`; `frontend/src/composables/useChatStreamHandler.ts` dispatch/answer/complete sections; `internal/handler/session/stream.go` heartbeat/replay code; `cmd/desktop/main.go`, `signing_key.go`; `miniprogram/utils/request.js`, `utils/sse.js`, `utils/config.js`, `pages/chat/chat.js::ask`. Package entry: [README](../raw/WeKnora/README.md), “Product Tour” and “Clients and Integrations.”
