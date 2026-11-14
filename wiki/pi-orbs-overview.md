---
type: Concept
title: Pi Orbs Architecture and Deployment
description: Pi Orbs deploys named Pi Durable bots on one Fly.io Sprite from a local client, with shared workspace and model.
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

Pi Orbs is a client-installed system for named Pi bots, each with its own conversation, sharing one Fly.io Sprite, model, and working directory. **Reported:** the local client creates the Sprite and pushes the server; the server hosts conversations using [Pi Durable](pi-durable-overview.md).[^pi-orbs]

## Operation and persistence

**Reported:** `npx pi-orbs` starts a local browser UI at `127.0.0.1:8787`; setup requests a Sprites token, connector and model. The deployed server listens on port 8080, uses `/home/sprite/work` as the common working directory, stores its harness SQLite database and roster under `/home/sprite/app/data`, and exposes a public `/version`. Pushing a new build recreates the service while preserving data and work directories. Destroying the Sprite removes its disk and bots.[^pi-orbs]

The package manifest **observed** at this revision declares version 0.3.0, MIT license, Node >=20, and separate client/server builds. Documentation reports that local server execution and server tests require Node 22 for `node:sqlite`; the simulator works on Node 20. `npm run dev:local` is an in-memory simulation, not a live harness or deployment.[^pi-orbs]

## Coverage and limits

Inspected README, architecture and security documentation, root and server manifests; implementation was searched selectively, not audited. Remaining client/server modules, tests, CI, release history, E2E, supporting docs and dependencies are pending. Generated cache, lockfile dependency detail, marketing media and decorative images were inventoried but not interpreted. No source code or tests were executed. Claims above are project reports unless marked observed; configuration and service behavior are time-sensitive.

## Relationships

- Uses [Pi Durable](pi-durable-overview.md) for the reported conversation harness.
- [Bot coordination](pi-orbs-coordination.md), [security](pi-orbs-security.md), and [integrations](pi-orbs-integrations.md) describe distinct operational boundaries.

[^pi-orbs]: `README.md` §§ Try, From a checkout, Test; `docs/architecture.md` §§ Client and server, Bots and `/home/sprite/work`, Troubleshooting; `package.json` and `server/package.json`.
