---
type: Concept
title: WeKnora embed, IM, and harness publishing channels
description: Embedded-agent sessions, callback-driven messaging, and a read-only DeepSeek Harness plugin expose different external trust boundaries.
tags: [ml, weknora, integrations, channels]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2026-12-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd5855fc4ded5c981a92dcb82a455246
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora publishes agent/knowledge access through iframe widgets, messaging adapters, and a coding-agent plugin, with separate authentication and state lifetimes. **Synthesis:** these are not just alternate skins over a logged-in browser session; each introduces a distinct principal, credential, and recovery boundary.[^weknora]

## Embed sessions

**Observed:** the embed channel model carries an agent binding, origin restrictions, rate limits, and a publish token excluded from JSON serialization. Defaults declare 30 requests/minute and 10,000/day. Secure session exchange uses Redis-backed tokens with a 30-minute TTL; without Redis that exchange is unavailable. Session-handle signatures bind the channel/session context through HMAC.[^weknora]

The public widget mounts an iframe and schedules token refresh; the embed SPA has its own entry and bridge for host context, locale, and session state. Public embed routes have their own auth/rate limits before global authentication. Selected handler/router symbols describe stripping visitor-supplied resource/model overrides, but the complete payload and origin enforcement paths remain pending. Unlike ordinary authenticated agent chat, the inspected web transport does not reconnect embed streams automatically.[^weknora]

## IM adapters

`internal/im/adapter.go` declares incoming/quoted-message types, callback verification, and user-versus-thread session modes. Session identity incorporates platform/chat/workspace context rather than just message text. Adapter packages cover WeCom, Feishu, Slack, Telegram, DingTalk, Mattermost, WeChat, QQBot, and Yunzhijia; Lark is also described in the README's product support table.[^weknora]

**Observed:** callback routes precede global auth and therefore rely on per-adapter verification. Channel administration uses role guards, summaries omit credential fields, and DingTalk is restricted to Stream transport. Adapter existence and a verification interface do not prove each platform signature handler is correct.[^weknora]

## DeepSeek Harness integration

**Observed:** `packages/dsh-weknora` declares package version 0.1.0, Node >=20.11, and four read-only tools: list knowledge bases, search, read document, and ask. Its client distinguishes public resource URLs from handle-based access and refuses a partial assembled answer without a terminal complete event. **Reported:** its documented compatibility target is older than this server snapshot; current harness interoperability was not run.[^weknora]

## Relationships

- Shares [frontend/SSE transport](weknora-frontend-streaming.md) and [backend agent runtime](weknora-agent-runtime.md).
- Depends on [authentication, principal scope, and outbound policy](weknora-security.md).
- Alternative publishing protocol: [MCP servers](weknora-mcp-servers.md).

## Coverage limits

Models, selected embed/session/widget logic, adapter contracts, route guards, and plugin source sections were inspected. Per-platform callback implementations, embed exchange/origin enforcement end to end, webhook delivery, plugin tools, browser bridge, and external platform APIs remain pending. No conversation, webhook, IM callback, or harness test ran. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `internal/types/embed_channel.go::EmbedChannel`; `internal/application/service/embed_session.go::embedSessionTTL`, `SignEmbedSessionHandle`, `VerifyEmbedSessionHandle`; `internal/middleware/embed_auth.go`; `internal/router/routes_agent.go::RegisterEmbedPublicRoutes`, `RegisterIMRoutes`, `RegisterIMChannelRoutes`; `internal/handler/embed_channel.go` payload-patching symbol inventory; `frontend/public/weknora-widget.js::scheduleRefresh`; `frontend/src/embed-main.ts`; `frontend/src/composables/useEmbedBridge.ts`; `frontend/src/api/chat/streame.ts::canReconnect`; `internal/im/adapter.go`, `types.go`, `channel_security.go::validateChannelTransport`; `packages/dsh-weknora/package.json`; `packages/dsh-weknora/src/index.ts::apply`, `config.ts::resolveConfig`, `client.ts::assembleStream`; plugin README compatibility section. Package entry: [README](../raw/WeKnora/README.md), “Channels and integrations” and “Clients and Integrations.”
