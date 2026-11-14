---
type: Concept
title: Pi Agents Messaging Guarantees
description: Peer message reach, ordering, delivery, interruption, and limits in a Pi Agents session.
tags: [pi-agents]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: '2026-11-14T15:47:01Z' }
sources:
  - id: pi-agents
    resource: ../raw/pi-agents/README.md
    scope: ../raw/pi-agents/
    kind: code
    revision: 99d64403214c6b61797080e82cf7dc0c43e70f65
    title: pi-agents 0.40.1
---

**Reported:** agents send one-way peer messages via `agent_send`; by default a message steers active work, `followUp` waits for the current work, and `interrupt` stops it first. Reach is limited to peers, a spawning agent, and one's own children as documented; agents cannot message the parent Pi model or agents in another session. A reply requires a separate message. Peer messages appear in the user transcript but not in Pi's model context.[^pi-agents]

## Delivery and caveats

**Reported:** a send binds the recipient's identity and enters its conversation once, including across crashes; a fresh send with identical text is a different message. Sends from one sender to one recipient are accepted in order, but a steer may be placed before an earlier follow-up; parallel sends in one model step have no mutual ordering. Messages may be queued, delivered, or dropped on interruption or stop; delivery does not prove the recipient handled them.[^pi-agents]

An interrupt and its message are not atomic: a stopped send can leave the recipient interrupted without the message. Messages do not wake `agent_wait`, and there are no send budgets or hop limits. Exactly-once message delivery is not exactly-once external effects. `/messages` shows the latest 1,000 session messages.[^pi-agents]

**Limit:** these are documentation claims, not independently tested; implementation and tests remain pending. See [overview](pi-agents-overview.md) for package coverage.

## Relationships

- **Uses:** [Pi Agents Graphs and Delegation](pi-agents-graphs.md) for groups and spawned-agent reach.[^pi-agents]
- **Depends on:** [Pi Agents Overview and Recovery](pi-agents-overview.md) for recovery and external-effect limits.[^pi-agents]

[^pi-agents]: `docs/messaging.md` §§ Using messages, Guarantees, Limitations; `docs/architecture.md` § Durability.
