---
type: Concept
title: Durable Pi Agent Network
description: A device-owned durable agent network with a backend per machine, a local hub, and web, terminal, and API clients.
tags: [pi-durable, durable-agents, networking]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:45:19Z }
stale_after: 2027-02-14
sources:
  - id: durable-pi
    resource: ../raw/durable-pi/README.md
    scope: ../raw/durable-pi/
    kind: code
    revision: 37165c619573dbaf425463038bbffecfe576beec
    title: Durable Pi
---

Durable Pi is a separate application built on [Pi Durable](pi-durable-overview.md): its documentation describes a backend on each device that owns its agents and SQLite databases, while a hub, terminal client, and direct HTTP clients watch and steer them. Closing a client does not itself stop the work; the backend and its persistent storage are the relevant recovery boundary. These are **reported** design and behavior claims, not independently tested here.[^durable-pi]

## Architecture and operations

- A device hosts `dpi-backend`; a session is one harness and one `agent.sqlite`; an agent is a conversation within that session, including Main, forks, and subagents. The device also keeps a catalog and shared application state. The hub stores device addresses and tokens, proxies authenticated requests, and multiplexes browser streams; the TUI connects directly. The SDK supplies the shared wire contract, clients, and reducers.[^durable-pi]
- Device definitions distinguish local, SSH, exe.dev, and pre-existing URL targets. The documentation describes provisioning, service setup, registration, deploy, rotation and—in the exe.dev case—confirmed destruction. These operations have real machine and network side effects; none were executed here.[^durable-pi]
- The documented security boundary is substantial: a device token gives its holder the backend user's shell and filesystem access; start directories are not a sandbox. SSH devices use plain HTTP on the LAN by default; exe.dev's HTTPS proxy is public and relies on the token. The hub stores all tokens and should remain loopback-bound. The optional command guard sends bash commands to a third party and fails open, so it is not a sandbox.[^durable-pi]
- Message admission IDs do not guarantee exactly-once external effects. Replay-safe operations can rerun; unsafe interrupted tools return an interrupted result. See [replay safety](pi-durable-replay-safety.md).[^durable-pi]

## Evidence and coverage

**Reported:** documentation describes the design and its own test results; no installation, test, deployment, or crash recovery was run. The root README, backend README and API, SDK README, and proactive demo README were inspected in part. Implementation, tests, dependency manifests, deployment recipes, UI and TUI docs, bundled upstream documentation, video, and images remain pending; this draft is not a complete repository coverage ledger. The README identifies MIT licensing and pins pi-durable 1.0.3. The Git revision identifies the inspected checkout, not an independent verification of its behavior.[^durable-pi]

## Relationships

- **Uses** [Pi Durable](pi-durable-overview.md) for durable execution.
- **Exposes** the [device API and streaming model](durable-pi-device-api.md).
- **Includes** a separate [proactive incident demo](durable-pi-proactive-demo.md).

[^durable-pi]: Durable Pi, `README.md` §§ The Durable Agent Network, Configure your network, How it's built, Where it can still fail, License; `apps/dpi-backend/README.md` §§ Configuration, Deploy to other devices, Layout, Guarantees and boundaries; `apps/dpi-sdk/README.md` § Layout, at revision `37165c619573dbaf425463038bbffecfe576beec`.
