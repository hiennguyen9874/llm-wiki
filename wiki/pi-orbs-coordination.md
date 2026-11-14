---
type: Concept
title: Pi Orbs Bot Coordination and State
description: Pi Orbs isolates bot conversations while using steer submissions and a bounded ledger for cross-bot coordination.
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

**Reported:** [Pi Orbs](pi-orbs-overview.md) gives each bot a separate Pi Durable conversation but a common workspace and model; bots coordinate through peer steers rather than sharing threads.[^pi-orbs]

## Steering and limits

The server submits peer content to the target with `whenBusy: "steer"`: an idle target starts a turn, while a busy target receives the input after the current tool round. The request ID is tied to the tool call to avoid duplicate admissions on replay. A ledger retains the latest 1,000 peer rows. Peer inputs are stored as user entries in the target conversation but presented as peer lines rather than human messages; exports can still include the underlying peer input. A human-started chain begins at hop 1; hop 3 and a second onward steer from the same incoming peer message are refused.[^pi-orbs]

**Reported:** a bot can create at most eight others and the roster can hold 24; each bot has private prompt memory and can be configured with a name, instructions and look. One selected Main Bot receives approximately hourly check-ins. Conversation exports contain text transcripts, not tool traces, and do not support import. Local simulator behavior is an in-memory stand-in, not harness execution.[^pi-orbs]

## Coverage and limits

These are project documentation claims, not independently verified runtime guarantees. `docs/architecture.md` and README were read; peer implementation was only searched selectively, and implementation, tests and remaining package materials are pending. No code was executed.

## Relationships

- Uses [Pi Durable conversations](pi-durable-conversations.md) for the reported steer submission primitive.
- Shares the environment described in [Pi Orbs architecture](pi-orbs-overview.md).

[^pi-orbs]: `docs/architecture.md` §§ Bots and `/home/sprite/work`, Cross-bot steering, Search, templates, memory, secrets, review, and the Main Bot; `README.md` § The interface.
