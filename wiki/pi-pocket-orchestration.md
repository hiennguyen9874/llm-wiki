---
type: Concept
title: Pi Pocket Linked Sessions and Durable Automation
description: How Pi Pocket coordinates linked agent sessions, durable schedules and watches, including replay and delivery limits.
tags: [pi-pocket, orchestration, durable-agents]
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

[Pi Pocket](pi-pocket-overview.md) uses [Pi Durable tasks](pi-durable-tasks.md) for scheduled work and coordinates separate conversations through linked sessions. **Reported:** a linked session is an ordinary session, not an owned subagent or an access grant; it copies agent settings but not history, and normally works in the source folder unless another folder is supplied. Agent Teams uses this experimental API and is off by default.[^pi-pocket]

## Linked sessions

The `host.linkedSessions` API can start, message, stop, archive and list linked sessions. Operations normally act for the person Pi works for in the source and are subject to source and target access, turn, plan and spend checks; conversation-bound human routes instead bind the authenticated person. A linked session cannot start another, and the top session's budget covers its team. There is no session or message count limit since 0.19.0, so the project advises setting a budget.[^pi-pocket]

**Reported replay design:** callers provide a stable key per logical call. A persisted receipt allows retries to find a prior result; the start receipt is committed with the new session, while message request IDs derive from the same key. Retention is limited (30 days and the newest 1,000 records according to the architecture guide), not an indefinite exactly-once guarantee. Since 0.28.0, messages steer by default at the next tool-round pause unless `steer: false`; the API returns on admission, not on an answer.[^pi-pocket]

The originating session normally receives an automatic final report from a linked session; however, the architecture guide explicitly says the end-of-run listener runs in process after the ending commit, so a crash between those events can lose the report. This qualifies the feature guide's normal-operation description. Fenced inter-session content remains untrusted; see [security boundaries](pi-pocket-security.md).[^pi-pocket]

## Scheduled and external work

The project reports scheduled messages and PR/repository watches as durable tasks that sleep until deadlines. Scheduled messages whose time passed during downtime are sent on restart; repeating schedules skip an occurrence if the preceding message is still queued. PR and repository watch sends use task-and-count request IDs, with the message checkpointed before sending. These are source-reported designs, not independently reproduced guarantees.[^pi-pocket]

## Evidence and limits

Based on the README, feature tour, architecture guide and linked-session extension documentation; none of the workflows or tests was executed, and implementation was not systematically checked. The [package coverage ledger](pi-pocket-overview.md#evidence-and-coverage) records pending work.[^pi-pocket]

[^pi-pocket]: Pi Pocket revision `5d009fa4d1e2b69db54f05e04f750a6f2e591bb1`: `docs/architecture.md` §§Durable truth and what memory keeps, Linked sessions, Work from outside the app; `docs/extensions/linked-sessions.md` §§What a linked session is, Starts from a human page, Send a message, A session's final answer comes back by itself, Limits of a team, Replays; `docs/features.md` §Scheduled messages.
