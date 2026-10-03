---
type: Concept
title: 'Jev-Evaluated Agent Memory: Beacon Pattern'
description: How Beacon captures cross-harness agent history and uses Jev to promote only high-signal corrections into reusable skills.
tags: [jev, agents, memory, skills]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:45:00Z }
sources:
  - id: avichawla-beacon-2026-09-21
    resource: ../raw/2101966536798040332/index.md
    scope: ../raw/2101966536798040332/
    kind: post
    title: 'Post by @_avichawla on X'
---

# Jev-Evaluated Agent Memory: Beacon Pattern

Synthesis: Beacon continuously captures agent sessions across coding harnesses and uses Jev as a cheap evaluator to decide which runs are worth learning from, promoting only high-signal workflows, corrections, and debugging patterns into reusable skills available to other agents[^avichawla-beacon-2026-09-21].

## What Beacon does

- Beacon by @asymptotelabs continuously captures agent history across harnesses including Claude Code, Codex, Cursor, OpenCode, and 20+ more, per the post's harness list[^avichawla-beacon-2026-09-21].
- It turns the highest-signal workflows, corrections, and debugging patterns into reusable skills, with the GitHub repo linked via `https://t.co/7n0b9guyQI` in the post[^avichawla-beacon-2026-09-21].
- The post frames this as a self-improving memory layer that puts Jev's evaluation signal to work, and characterizes Jev as making it dramatically cheaper to evaluate what actually happened inside an agent run[^avichawla-beacon-2026-09-21].

## Preserve versus learn

- Beacon preserves the complete session history, but preserving a run and learning from it are treated as two different things[^avichawla-beacon-2026-09-21].
- Most coding-agent sessions contain routine exploration, failed commands, and fixes that only apply to one task; the trace can remain available for inspection without turning every detail into guidance for future agents[^avichawla-beacon-2026-09-21].
- **Synthesis**: store everything, promote selectively — retention is not endorsement.

## Evaluation and promotion policy

- Jev scores each run for evidence, reuse potential, and human correction signals[^avichawla-beacon-2026-09-21].
- An application policy then decides whether to promote, review, or discard the run[^avichawla-beacon-2026-09-21].
- Only the approved lesson becomes available to other coding agents working on the project[^avichawla-beacon-2026-09-21].

## Demonstrated correction loop

- The recording shows Claude receiving a coding task, modifying the implementation, and running the tests[^avichawla-beacon-2026-09-21].
- The human then provides an edge-case correction, so Claude updates the code and adds regression coverage[^avichawla-beacon-2026-09-21].
- Beacon automatically captures the complete session and Jev evaluates whether the correction contains a reusable engineering lesson[^avichawla-beacon-2026-09-21].

## Cross-harness reuse

- Because the skill layer works across harnesses, Claude Code sessions can teach Codex and Cursor debugging can improve OpenCode, per the post's examples[^avichawla-beacon-2026-09-21].
- The intended effect is that a problem solved by one agent should not need to be learned from scratch by another[^avichawla-beacon-2026-09-21].

## Relationships

- Uses [Jev Decision Model](jev-decision-model.md) as the cheap run evaluator for evidence, reuse, and correction signals.
- Uses [Jev API Patterns](jev-api-patterns.md) invocation shapes for scoring runs, subject to live-docs verification.
- Informs [Classifier Selection](classifier-selection.md) agent-harness uses by giving a concrete judge-and-promote memory implementation beyond routing and pre-screening.
- Complements [Conservative Jev Routing for Coding Agents](conservative-jev-routing.md), which governs model switching, whereas this pattern governs what gets remembered.

## Coverage limits

- Single third-party enthusiast post by @_avichawla about Beacon by @asymptotelabs; all Beacon behavior is **reported**, not reproduced here[^avichawla-beacon-2026-09-21].
- No Jev scoring rubric, thresholds, skill format, approval UX, or measurements were included; do not implement numeric cutoffs from this source[^avichawla-beacon-2026-09-21].
- Linked GitHub repo behind `https://t.co/7n0b9guyQI`, the embedded recording, and the mentioned hands-on Jev decision-path guide were not resolved or inspected[^avichawla-beacon-2026-09-21].
- No credentials, keys, tokens, or non-public PII were found in the source; handles are public attribution.

[^avichawla-beacon-2026-09-21]: @_avichawla, “Post by @_avichawla on X,” X, published 2026-09-21, canonical local entry `../raw/2101966536798040332/index.md`, upstream `https://x.com/_avichawla/status/2101966536798040332`. Locators in text: opening Jev-evaluation claim; Beacon harness list (Claude Code, Codex, Cursor, OpenCode, 20+ more) and `https://t.co/7n0b9guyQI` repo link; preserve-versus-learn paragraph; Jev scoring (evidence, reuse potential, human correction) and promote/review/discard policy; recording walkthrough (Claude task, tests, edge-case correction, regression coverage, capture, evaluate, approve); cross-harness transfer examples.
