---
type: Concept
title: Pi Orbs Schedules, Voice, and MCP Integrations
description: Pi Orbs integrates scheduled bot messages, realtime voice, signed MCP events, and sandboxed MCP Apps through distinct paths.
tags: [pi-orbs]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: '2026-11-14T15:54:17Z' }
sources:
  - id: pi-orbs
    resource: ../raw/pi-orbs/README.md
    scope: ../raw/pi-orbs/
    kind: code
    revision: 6a2ab3b507504045bedf7a6837047d62c2c8f42d
    title: Pi Orbs
---

**Reported:** [Pi Orbs](pi-orbs-overview.md) supports optional scheduled messages and voice, plus distinct MCP inbound-event and interactive-app paths. These integrations have different credentials, transports and delivery semantics.[^pi-orbs]

## Schedules

The `schedule_message` tool creates a cron-job.org job to POST content to a per-bot tokenized webhook; delivery becomes a normal user message, not a peer steer. Schedules support five-field cron and a time zone, or a one-shot ISO time; the documented one-shot expiration is three minutes after its scheduled minute. Repeated identical tool calls return the stored job ID. On bot deletion, remote jobs are deleted first; a failure keeps the bot to avoid leaving jobs behind.[^pi-orbs]

## Voice and MCP

Voice requires an optional Grok or OpenAI realtime key. The local client mints a short-lived provider token for the browser; the voice agent has `search_messages`, `send_task`, and `stop_voice` tools. Voice transcripts are stored on the client for the call, not as a second bot thread.[^pi-orbs]

MCP event webhooks accept a tokenized URL and Standard Webhooks signature, deliver signed non-verification events as follow-up inputs, and can be disconnected per bot. MCP Apps instead fetch a declared `ui://` resource and render it in a sandboxed iframe on a separate local origin. These are separate integration paths, not interchangeable mechanisms.[^pi-orbs]

## Coverage and limits

Architecture and README were inspected; integration implementation, tests, `docs/evals/mcp-apps.md`, dependencies and remaining package material are pending. This is a project report, not verified operation. The local simulator substitutes in-memory behavior and does not exercise real providers.[^pi-orbs]

## Relationships

- [Security boundaries](pi-orbs-security.md) describes credential handling and webhook authentication.
- [Bot coordination](pi-orbs-coordination.md) distinguishes peer steers from normal scheduled messages.

[^pi-orbs]: `docs/architecture.md` §§ Voice, Scheduled messages, Bots and `/home/sprite/work`, Cross-bot steering; `README.md` § The interface.
