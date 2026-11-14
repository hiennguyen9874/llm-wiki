---
type: Concept
title: Eta Personal Agent Architecture
description: Eta combines a desktop agent, self-hosted Bot, and mobile companion around a shared agent core, with separate local and cloud state.
tags: [eta, agents]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:53:01Z }
sources:
  - id: eta
    resource: ../raw/eta/README.md
    scope: ../raw/eta/
    kind: code
    revision: fc520e4ef2a2ec8a23613e39a2a5181330673856
    title: Eta repository
---

Eta is a personal agent distributed across an Electron desktop app, a self-hosted HTTP/SSE Bot, and a mobile companion; its shared core includes durable threads, projects, scheduling, sandboxing and approvals. **Reported:** the agent runtime is built on Pi. Desktop and Bot retain separate projects, histories and credentials; closing Desktop does not stop remote work.[^eta]

## Operation and delegation

**Reported:** desktop skills are discovered from personal and project directories, with project skills taking precedence. The main agent can delegate to independent or history-forked subagents; orchestrator mode assigns tool execution to children. Code mode is the default and composes enabled tools in JavaScript, while standard mode calls them directly; both share permissions and sandbox controls. Local schedules require Eta running and the computer awake; Bot schedules continue on the server.[^eta]

## Coverage and limits

**Observed:** this initial synthesis inspected the root README, package manifest, Desktop and sandbox user guides, and Bot README. The repository also contains desktop, mobile, website, core, agent and computer-use code, CI, tests, documents, release assets and a separate `.repos` reference checkout. Their material contents, the mobile guide, translations, dependency closure and execution are pending; binary/decorative assets and the lockfile were not examined. Claims above are documentation reports, not verified behavior. Version 0.1.169 and Node >=22.18.0 come from the root manifest; the Bot guide separately asks for Node 24. MIT is stated in the root README. The safety scan was heuristic and excluded `.repos` and binary/large files.[^eta]

## Relationships

- **Uses:** Pi is reported as the agent runtime; this does not establish which version or whether Eta uses [Pi Durable](pi-durable-overview.md).[^eta]
- **Related:** [Eta Bot](eta-bot.md) describes remote operation; [Eta security](eta-security.md) covers execution permissions.

[^eta]: `README.md` §§ Getting started, Packages, Development, License; `package.json` keys `version`, `engines`; `docs/user/desktop.md` §§ Skills, Subagents, Scheduled tasks; `apps/bot/README.md` §§ introduction, Desktop connection.
