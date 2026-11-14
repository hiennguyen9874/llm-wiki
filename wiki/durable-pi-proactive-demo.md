---
type: Concept
title: Durable Pi Proactive Incident Demo
description: A simulated incident pipeline combining per-row classification, coded thresholds, an agent investigation, and checkpointed human-approved deployment.
tags: [pi-durable, incident-response, durable-agents]
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

The [Durable Pi](durable-pi-network.md) proactive demo is a simulated checkout incident: a classifier judges individual log rows, ordinary code applies thresholds, and a durable agent investigates and prepares a fix before requesting human deploy approval. It demonstrates a division of responsibility, not proof that production incidents can be safely automated in the same way. All behavior and results below are **reported** by the demo documentation, not reproduced here.[^durable-pi]

## Pipeline and recovery

1. A mock Cloud Logging stream runs checkout code and introduces a bad revision; the watcher classifies each row. By default, three incident verdicts with one fingerprint in 120 seconds trigger an incident; eight suspicious verdicts can also trigger one.[^durable-pi]
2. Incident creation is described as one durable commit creating the incident document and conversation. The agent works in an incident branch; tools enforce stage order, and `submit_fix` checks that changed tests fail on main and the full suite passes on the branch before committing.[^durable-pi]
3. Deployment is a tool-owned durable task with approval, rollout and verification phases. Decline or interruption prevents that deploy; after approval the simulated stream rolls out the revision and checks checkout results. The README reports restart during approval retains the task, and that a reused brief request ID prevents duplicate briefs.[^durable-pi]
4. During a prolonged classifier outage the incident opens only after recovery; old rows beyond the default 300-second backlog are skipped. The demo has no login and runs bash; its documented default is loopback binding.[^durable-pi]

The source reports two measured runs on 2026-10-05, with deploy approval reached around 25–30 seconds; these are narrow demo measurements, not independently verified performance claims. Demo implementation, tests and external services remain uninspected or unexecuted.[^durable-pi]

[^durable-pi]: `apps/proactive-dpi-demo/README.md` §§ Demo timeline, How it works, Durability, verified 2026-10-05; root `README.md` §§ The hook: a proactive durable agent, Where it can still fail, revision `37165c619573dbaf425463038bbffecfe576beec`.
