---
type: Concept
title: Foreman Attached Hooks and Pi Integration
description: Foreman supervises externally started coding sessions through local hook adapters, including a Pi and Pi Durable bridge.
tags: [foreman, pi-durable, hooks]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:50:51Z }
sources:
  - id: foreman
    resource: ../raw/foreman/README.md
    scope: ../raw/foreman/
    kind: code
    revision: c3142ef636617f32f772140125aa310d81ceece9
    title: Foreman
---

**Reported:** Unlike `foreman run`, `foreman hook` attaches supervision to an externally started session via a single-event JSON filter. Codex, Deep Agents, Pi, and Pi Durable adapters normalize native events into shared supervision. Attached state is stored outside the target repository and session identity combines client and native session ID.[^foreman]

## Pi and Pi Durable

The TypeScript bridge forwards events to the Python `foreman` executable; it makes no model calls itself. The guide reports testing against `@earendil-works/pi-coding-agent` and `@earendil-works/pi-durable` 1.0.4, Node 22.19+, and core 0.4.4 or newer. A Durable host needs subprocess support; this bridge does not run in a Cloudflare Worker.[^foreman]

Pi can refuse an input, block tools, add feedback and request one continuation. For [Pi Durable hooks](pi-durable-extensions-hooks-agents.md), the bridge routes actual submitted entries with stable IDs; a before-tool steering request becomes a block because that hook cannot inject context. Halt uses the public abort API because ordinary generation-hook exceptions are swallowed. Other tools in a parallel batch may already be executing; sequential tool execution is recommended for strict boundaries.[^foreman]

Work and event IDs protect routing and completion-response replay within a bounded, expiring session; they do **not** guarantee exactly-once model or tool execution. The documented default session inactivity TTL is seven days.[^foreman]

## Coverage

Only `docs/hooks.md` and `integrations/pi/README.md` were inspected for this page; bridge code, adapter implementations, tests and other integrations remain pending. Compatibility and safety behavior are reported, not reproduced.[^foreman]

[^foreman]: `docs/hooks.md` §§ Client adapters, Event flow, Local state; `integrations/pi/README.md` §§ Installation, Pi coding agent, Pi Durable, Process contract and tests.
