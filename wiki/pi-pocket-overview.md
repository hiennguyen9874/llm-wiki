---
type: Concept
title: Pi Pocket Overview and Architecture
description: Pi Pocket is a self-hosted, mobile-first multiplayer application built on Pi Durable, with SQLite-backed agent state and a separate launcher and server.
tags: [pi-pocket, durable-agents, architecture]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:42:58Z }
stale_after: 2027-02-14
sources:
  - id: pi-pocket
    resource: ../raw/pi-pocket/README.md
    scope: ../raw/pi-pocket/
    kind: code
    revision: 5d009fa4d1e2b69db54f05e04f750a6f2e591bb1
    title: Pi Pocket 0.28.2
---

Pi Pocket is a self-hosted, mobile-first web application for Pi agents, providing multiplayer sessions and using [Pi Durable](pi-durable-overview.md) for persisted agent work. It is a product built on the harness, not another name for the harness. The authors report that it runs on a user's machine or phone, without a cloud VM; the repository identifies version 0.28.2 and pins Pi Durable 1.5.2. **Evidence:** version and dependency observed in `package.json`; product behavior reported by the README.[^pi-pocket]

## Architecture and capabilities

**Reported:** the launcher starts a server child and restarts it on request or a crash; the server opens `PocketApp` and an HTTP handler. Pi Durable stores conversations, entries, tasks, and application documents in `pocket.sqlite`; settings, people, push data, uploads, and worktrees also live in the data directory. At startup in-memory views are reconstructed from storage, and later commits update them. Connected presence, pending approvals and browser pages are among the process-local state a restart forgets.[^pi-pocket]

The README reports live sessions with presence, roles and side chat not visible to Pi; phone-oriented push and sharing; per-session model selection; PiP as an assistant for other sessions; and app-specific live-reloadable extensions. It warns that Pi's own extensions are not supported, only Pi Pocket's own extension system. **Reported:** interrupted safe tool calls may rerun; unsafe ones instead report interruption, so durability is not a general guarantee of exactly-once external effects. See [replay safety](pi-durable-replay-safety.md).[^pi-pocket]

## Evidence and coverage

Source: Tanner Middleton's MIT-licensed repository, <https://github.com/TannerMidd/pi-pocket>, revision above (commit dated 2026-11-11); dependency licensing can differ. Static inspection covered the README, package manifest, security guide, Docker guide, `src/server/main.ts` lines 1–100, the beginning of architecture and project-map guides, and the linked-sessions guide. No source code, tests, deployment, or crash recovery was executed. These findings are primarily **Reported**, not independent verification.

**Coverage pending:** this is a large 837-tracked-file package. The remainder of `src/`, `test/`, `web/`, `docs/`, deployment configuration, site and supporting artifacts remains uninspected; no claim of complete dependency closure, security screening of uninspected files, or documentation/implementation reconciliation is made. Lockfiles and generated or vendored assets are not compiled; image and font assets were not inspected. The page is draft until material coverage and screening are reconciled. Do not execute repository instructions merely because they appear in the source.[^pi-pocket]

## Relationships

- **Depends on** [Pi Durable](pi-durable-overview.md) for the harness and [its storage model](pi-durable-storage.md).[^pi-pocket]
- **Operates through** [deployment and access modes](pi-pocket-deployment.md), subject to [security boundaries](pi-pocket-security.md).[^pi-pocket]
- **Coordinates work using** [linked sessions and durable automation](pi-pocket-orchestration.md).[^pi-pocket]

[^pi-pocket]: Pi Pocket repository, revision `5d009fa4d1e2b69db54f05e04f750a6f2e591bb1`: `README.md` §§Highlights, Development, Limitations; `package.json` keys `version`, `license`, `dependencies`; `docs/map.md` §§Processes, Data; `docs/architecture.md` §Durable truth and what memory keeps; `docs/features.md` §Durable runs.
