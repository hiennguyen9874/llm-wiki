---
type: Concept
title: Durable Pi Device API and Streams
description: The reported v1 device API for message admission, creation receipts, streaming snapshots, shared state, and durable jobs.
tags: [pi-durable, api, networking]
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

The [Durable Pi network](durable-pi-network.md) documents a v1 HTTP and SSE API shared by its web hub, TUI, and scripts. The following are **reported** API contracts; server implementation and behavior were not verified in this ingest.[^durable-pi]

## Admission and recovery

- All `/v1/*` routes require the device token, using bearer authorization or `X-DPI-Token`; `/healthz` is open. Names can address sessions and agents; ambiguous names return 409.[^durable-pi]
- Message sends require `requestId`; retries with the same ID are reported to be admitted once. Session, agent and fork creation separately accept an `Idempotency-Key`; the API says receipts are kept at least 24 hours and reusing a key on a different route is invalid. These are admission and creation guarantees, not exactly-once guarantees for external effects.[^durable-pi]
- A send chooses follow-up, steer, or reject when busy; follow-up is the default. Optional waiting is capped at 300,000 ms. API errors distinguish busy, stale-state conflict, ambiguous names and unavailable sessions.[^durable-pi]

## Streaming and state

SSE streams begin with `hello`, then a snapshot, then deltas; reconnect starts from a fresh snapshot rather than replaying old frames. A 15-second ping, 45-second silence rule, and 2 MB slow-viewer disconnection are documented. SDK reducers interpret frames; closing a stream does not stop the agent.[^durable-pi]

The API documents device-wide shared JSON state with revision checks and path operations, and named durable jobs with checkpointed phases. `release-check` gathers evidence with a subagent, waits for approval, then publishes and verifies. A background job belongs to the conversation; when called with `wait: true`, the call owns it and interruption stops it.[^durable-pi]

## Coverage limit

The API and SDK README were inspected as documentation; implementation, security enforcement, tests and edge cases remain pending. Reported defaults and contracts are revision-specific and may change.[^durable-pi]

[^durable-pi]: `apps/dpi-backend/API.md` §§ Conventions, Routes, Durable jobs, Streams; `apps/dpi-sdk/README.md` §§ Layout, Use it; root `README.md` §§ One shared App State, Where it can still fail, revision `37165c619573dbaf425463038bbffecfe576beec`.
