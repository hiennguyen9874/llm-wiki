---
type: Concept
title: Pi Agents Graphs and Delegation
description: How Pi Agents groups, dependency graphs, recursive spawning, waits, and failure handling compose delegated work.
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

**Reported:** each `agent_spawn` starts one group of 1–12 agents with one owned result. Named `after` edges carry final messages between agents; independent nodes run in parallel, and only nodes without dependents contribute to the group result. Singleton group IDs and agent IDs differ: address the agent by its ID, wait for or stop the group by its group ID.[^pi-agents]

## Failure and waiting

**Reported:** a dependent starts with available answers and notices failures; it is skipped only if none of its dependencies answered. Groups ordinarily run to completion despite failures; `failFast: true` stops remaining agents on failure. Edges have no schemas, conditions or loops. Both Pi and agents must call `agent_wait` directly, not through codemode, so a script cannot discard or truncate a result before model receipt. Peer messages do not wake a wait; use asynchronous results when children need clarification.[^pi-agents]

## Recursive delegation

**Reported:** a spawning agent receives its own group's result, either asynchronously as `[results]` input or as a direct wait result, never both. It may allow children to spawn, up to three agent levels below Pi. Each spawning agent can start at most 24 children over its lifetime, without replenishment; at most 16 spawned agents have unfinished initial jobs in a session, including dependency-waiting nodes. The optional working-agent cap also applies to later turns. Stopping an agent stops its descendants, while interruption leaves them working.[^pi-agents]

**Limit:** documentation only; implementation and tests have not been inspected or run. See [overview](pi-agents-overview.md) for source coverage and recovery constraints.

## Relationships

- **Uses:** [Pi Agents Messaging](pi-agents-messaging.md) for peer coordination and follow-ups.[^pi-agents]
- **Depends on:** [Pi Agents Overview and Recovery](pi-agents-overview.md) for session ownership and recovery.[^pi-agents]

[^pi-agents]: `docs/graphs.md` §§ Graphs, Agents that spawn agents; `docs/usage.md` § Tools; `docs/configuration.md` § Working agents.
