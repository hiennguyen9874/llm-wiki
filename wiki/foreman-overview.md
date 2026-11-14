---
type: Concept
title: Foreman Semantic Supervision Overview
description: Foreman separates coding-agent work from decision-model supervision, responsibility checks, and deterministic intervention policy.
tags: [foreman, agents, supervision]
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

**Reported:** Foreman is a Python asyncio supervisor for coding agents. A worker performs engineering while a separate loop observes evidence, asks decision models typed questions, and applies Python policy to proposed interventions. Its usefulness depends on evidence, thresholds, checks, and models; the architecture is not proof of correctness.[^foreman]

## Managed workers

The source reports one coding worker at a time, with a separate verifier worker when verification is needed. The default Codex App Server backend can steer an active turn; Codex exec, OpenCode, Hermes, and Deep Agents backends lack this live-steering capability and fall back to stop/retry. Jev is the default decision provider; OpenAI Decisions is another adapter.[^foreman]

A cycle collects bounded observations, groups checks by evidence selection, obtains model assessments, lets responsibilities propose directives, and has policy select a permitted action. State and events are persisted. Model probabilities are inputs to a policy, not independent verification of the job.[^foreman]

## Relationships and coverage

- Uses [responsibilities and routing](foreman-responsibilities.md) and [bounded evidence](foreman-evidence.md).
- Supports externally started sessions through [attached hooks and the Pi bridge](foreman-attached-hooks.md).

**Coverage limit:** Initial documentation-led compilation: inspected `README.md` through the responsibilities section, `pyproject.toml`, `docs/runtime.md`, `docs/routing.md`, `docs/evidence.md`, `docs/hooks.md`, and `integrations/pi/README.md`. The remaining README, other docs and integrations, implementation, configuration, CI, and tests remain pending. The icon is decorative; lockfiles are dependency snapshots. No source code, tests, or external services were executed. Claims are project reports, not independent verification. The package reports version 0.5.1, Python >=3.11, and MIT license in its manifest.[^foreman]

[^foreman]: `README.md` §§ What is Foreman?, The factory floor, Responsibilities and checks; `docs/runtime.md` §§ Components, One assessment cycle; `pyproject.toml` `[project]`.
