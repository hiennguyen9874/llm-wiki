---
type: Concept
title: Hybrid environments for tool-use trajectory synthesis
description: A proposed tool-use data pipeline combines live services, local reconstructed APIs, and model-simulated tools, then evolves verifier-backed tasks along an explicit difficulty taxonomy.
tags: [agent-training, synthetic-data, tool-use, trajectory-synthesis, verification]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:42:05Z }
sources:
  - id: nanbeige2026compactagent
    resource: ../raw/arXiv-2607.22083v2/main.tex
    title: "Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model"
---

# Hybrid environments for tool-use trajectory synthesis

Nanbeige4.2's authors propose tool-use trajectory synthesis in hybrid environments: live MCP services preserve dynamic behavior, Python-reconstructed tools operate over locally persisted real-world data, and model-simulated tools cover impractical runtime dependencies. A task agent produces a verifier and evolves tasks based on solver outcomes across dimensions such as chain depth, retrieval difficulty, and parameter inference; this is a reported pipeline, not a validated guarantee of environmental realism or task quality.[^nanbeige2026compactagent]

## Method

- The process collects thousands of MCP tool specifications, assesses composability, and groups compatible tools into bundles. An environment-synthesis agent uses web search and Bash to collect relevant data into a local database and reconstruct callable Python interfaces.[^nanbeige2026compactagent]
- The three stated environment types are live online MCP services for time-sensitive outputs, local Python tools over collected data, and model-simulated virtual tools for dependencies that are hard to reproduce. The source frames this as a diversity--realism trade-off rather than claiming equivalence among types.[^nanbeige2026compactagent]
- A task-synthesis agent generates a natural-language task and Python verifier. Solver attempts identify reliably solved tasks; their trajectories feed a task-evolution loop that raises selected difficulty dimensions. A compact, held-out rapid-validation suite is intended to be disjoint from training data and track iteration effects.[^nanbeige2026compactagent]

## Trust boundary

The manuscript does not quantify the fidelity of reconstructed or simulated tools to live systems, contamination of web-collected data, verifier correctness, or whether the adaptive loop produces harder tasks without changing task validity. Live services also make trajectories and results time-dependent.[^nanbeige2026compactagent]

## Relationships

- Related to: [Execution-grounded repository-to-trajectory synthesis](execution-grounded-repository-to-trajectory-synthesis.md) — both use verification and outcome-driven task evolution, but this approach targets tool bundles rather than repository patches.
- Related to: [Artifact-centric office workflow task synthesis](artifact-centric-office-workflow-task-synthesis.md) — both build closed-loop agent data, with different primary task substrates.
- Used by: [Nanbeige4.2 compact looped agent model](nanbeige4-2-compact-looped-agent-model.md) — the model report identifies complex tool-use data as a post-training component.

[^nanbeige2026compactagent]: Nanbeige LLM Lab and Boss Zhipin, *Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model*, source manuscript, abstract, §§1--4, appendix, and figures (arXiv:2607.22083v2, 2026).