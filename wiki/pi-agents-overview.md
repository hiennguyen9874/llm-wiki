---
type: Concept
title: Pi Agents Overview and Recovery
description: A Pi extension for named, session-owned agents backed by Pi Durable, with separate storage and bounded recovery guarantees.
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

Pi Agents is a Pi extension that delegates work to named agents and graphs in the Pi process, using [Pi Durable](pi-durable-overview.md) to persist their work. Agents have separate conversations, models and working directories; their jobs need to stand alone because they do not see the parent conversation. **Reported:** the package installs with `pi install npm:pi-agents` and uses the user's Pi logins and models.[^pi-agents]

## Recovery and storage

**Reported:** agents belong to the initiating Pi session; quitting, crashing or switching sessions pauses them until that session resumes. Finished graph nodes do not rerun. Interrupted model calls consume a retry; repeated crash loops end work rather than restarting forever. Tool effects may repeat, while tools deemed unsafe to repeat report interruption. Pending results can arrive more than once after a crash if Pi had not saved them. `--no-session` agents are in-memory and cannot recover from storage failure.[^pi-agents]

Storage is separate from Pi's session file under `~/.pi/agent/pi-agents/sessions/<session-id>/`. **Reported:** optional `piAgents.retentionDays` deletes inactive stores at startup, excluding the current store and stores held by other running Pi processes; absent that setting, stores remain indefinitely. Deletion permanently removes their agents.[^pi-agents]

## Tools and trust

**Reported:** agents can use standard Pi tools and shared MCP or extension tools. MCP and configured extensions run in a separate headless tool twin, with the user's MCP configuration and sign-ins; the twin has no UI and sees an empty conversation. Project settings and MCP configuration require project trust. A profile tool allowlist does not restrict the shared MCP and extension tools described in usage.[^pi-agents]

## Coverage and limitations

**Observed:** package metadata identifies version 0.40.1, MIT licensing, Node >=22.19.0 and a dependency on Pi Durable 1.5.1. README and documentation on usage, graphs, messaging, profiles, configuration, architecture, and hooks were inspected. Source implementation (72 files), tests (45 files), remaining design, CI, release history and demo assets are pending; binary GIFs are illustrative and not inspected. No code or tests were executed. Documentation claims are reported rather than independently verified; this page and sibling concepts remain draft pending implementation reconciliation. A pattern-based credential scan found no matches in screened text types; it is not a complete privacy audit.[^pi-agents]

## Relationships

- **Uses:** [Pi Durable](pi-durable-overview.md) for the underlying harness.[^pi-agents]
- **Uses:** [Pi Agents Graphs](pi-agents-graphs.md) for delegated groups and [Pi Agents Messaging](pi-agents-messaging.md) for peer coordination.[^pi-agents]
- **Uses:** [Pi Agents Configuration and Hooks](pi-agents-configuration.md) for profiles, tool sharing and extension integration.[^pi-agents]

[^pi-agents]: `README.md` § Installation, Architecture, Documentation; `package.json` keys `version`, `license`, `engines`, `dependencies`; `docs/usage.md` §§ Glossary, Tools available to agents; `docs/architecture.md` §§ Durability, Storage; `docs/configuration.md` §§ Extension tools, Storage retention.
