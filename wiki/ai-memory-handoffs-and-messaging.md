---
type: Concept
title: ai-memory handoffs and agent messaging
description: The claim-once handoff protocol between agent sessions, the offer-not-claim option, and the directed claim-once agent-to-agent message inbox.
tags: [agent-memory, ai-memory, handoff, messaging, protocol]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/ai-memory/README.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: ai-memory README
  - id: handoff-design
    resource: ../raw/ai-memory/docs/design-handoff-offer-not-claim.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Handoff offer-not-claim design
  - id: agent-messaging
    resource: ../raw/ai-memory/docs/agent-messaging.md
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Agent messaging
  - id: hooks-router
    resource: ../raw/ai-memory/crates/ai-memory-hooks/src/router.rs
    scope: ../raw/ai-memory/
    kind: code
    revision: 26fa9cf
    title: Hook router (handoff claim logic)
---

# ai-memory handoffs and agent messaging

A **handoff** is a typed baton one session leaves for the next: where work stopped, what failed, what is open. Each handoff has an owner and is **claimed exactly once**.[^readme] A separate **agent message** inbox provides directed, claim-once messages between agents across projects.[^agent-messaging]

Evidence class: **Observed** (docs and `router.rs`, delegated static inspection); nothing executed. The user-facing promises are also **Reported** by the README.

## Handoff protocol

- **Claim-once:** state `open` is guarded on both sides, lookup is owner-filtered, live batons are held for a 10-minute quiet period (`LIVE_BATON_QUIET_PERIOD`), and the claim and the managed-ledger claim commit in one transaction after rendering.[^hooks-router]
- **MCP tools:** `memory_handoff_begin`, `memory_handoff_list`, `memory_handoff_accept`, `memory_handoff_cancel`.[^hooks-router][^readme]
- **Offer-not-claim:** with `[handoff] claim_on_session_start=false`, session start renders a notice naming the exact `handoff_id` for `memory_handoff_accept` and never claims.[^handoff-design][^hooks-router]
- **Cut-off sessions:** a metadata-only continuity notice (agent, id, age) names a newer session that never ended; see [Managed workstreams](ai-memory-managed-workstreams.md).[^hooks-router]
- `AI_MEMORY_AUTO_HANDOFF=off` suppresses handoff *creation*, not delivery; the design doc's `AI_MEMORY_HANDOFF=off` / `run --no-handoff` options are described as not pursued and do not exist in the CLI (Observed via delegated check of `cli.rs`).[^handoff-design]

## Agent messaging

Four MCP tools — `memory_message_send`, `_list`, `_pop`, `_cancel` — implement a directed claim-once inbox, ≤256 pending per inbox, unknown recipient fails closed, and send/pop/cancel refuse a server-inferred scope. Popped bodies are fenced as untrusted with a `security_notice`. The on-start notice is count-only; mid-session notice is opt-in through `[messaging] inbox_notice_on_prompt` and `mcp-bridge --channel inbox`. The web UI has an agent inbox where an operator can queue requests.[^agent-messaging][^readme]

## Relationships

- Captured by hooks: [Capture and hooks](ai-memory-capture-and-hooks.md); exposed as [MCP tools](ai-memory-mcp-tools-and-http-surfaces.md).
- Scope for messages comes from [Project identity](ai-memory-project-identity-and-profile.md).
- Untrusted-body fencing relates to [Auth and security](ai-memory-auth-and-security.md).

[^readme]: `../raw/ai-memory/README.md` — "Why ai-memory" (handoffs are a typed protocol); "Everyday use" (web agent inbox); `memory_briefing` / `memory_handoff_list` notes.
[^handoff-design]: `../raw/ai-memory/docs/design-handoff-offer-not-claim.md` — status banner and "options not pursued".
[^agent-messaging]: `../raw/ai-memory/docs/agent-messaging.md` — tools, limits, notices, web inbox sections.
[^hooks-router]: `../raw/ai-memory/crates/ai-memory-hooks/src/router.rs::fetch_and_accept_handoff_at, LIVE_BATON_QUIET_PERIOD, render_handoff_notice, render_continuity_notice`.
