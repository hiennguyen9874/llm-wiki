---
type: Concept
title: Pi Agents Configuration, Profiles, and Hooks
description: Reusable agent profiles, concurrency and tool sharing, and extension hooks for durable agent requests.
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

**Reported:** agent profiles are Markdown files with YAML settings and system-prompt instructions. User profiles live in `~/.pi/agent/agents`; trusted project profiles in `.pi/agents` override namesakes. Fields include required `name` and `description`, model, thinking, tools, skills, `spawn`, and `maxTurns`; explicit spawn arguments override the profile. Spawn defaults to false and the turn limit is absent by default.[^pi-agents]

## Runtime settings

**Reported:** `piAgents.twinExtensions` specifies extension packages to load in a headless tool twin alongside configured MCP servers. `piAgents.maxWorkingAgents` limits simultaneous work across groups; an agent yields its slot during a direct child wait. No additional working-agent cap applies by default, and the fixed spawning limits are separate. Restart Pi after changes to these settings or MCP sign-ins.[^pi-agents]

## Extension hooks

**Reported:** co-loaded extensions discover hooks synchronously through `pi-agents:hooks:discover`. `onAgentCreate` snapshots JSON state per top-level spawn; children inherit it, and later parent changes affect future top-level spawns. State is persisted unencrypted, must not contain secrets, and is limited to 8 KiB combined per agent. `onAgentRequest` can replace requests and fails the request on errors; `beforeAgentRequest` can hold requests, but callback errors are reported and the call proceeds unless the extension itself handles them to fail closed. Hooks run in namespace order and have documented exclusions, including parent and classifier/image requests.[^pi-agents]

**Limit:** documentation only; source implementation and tests have not been inspected or executed. See [overview](pi-agents-overview.md) for package coverage and trust boundaries.

## Relationships

- **Configures:** [Pi Agents Overview and Recovery](pi-agents-overview.md), including its tool twin.[^pi-agents]
- **Constrains:** [Pi Agents Graphs and Delegation](pi-agents-graphs.md) through the optional working-agent cap.[^pi-agents]

[^pi-agents]: `docs/profiles.md` § Agent profiles; `docs/configuration.md` §§ Extension tools, Working agents; `docs/hooks.md` §§ Register hooks, Capture state, Transform requests, Hold requests.
