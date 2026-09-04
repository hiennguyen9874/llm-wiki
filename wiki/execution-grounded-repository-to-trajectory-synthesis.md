---
type: Concept
title: Execution-grounded repository-to-trajectory synthesis
description: A proposed agent-training pipeline reconstructs repositories as executable tasks, validates reference patches with fail-to-pass and pass-to-pass tests, diversifies successful trajectories across scaffolds, and feeds recurring failures back into mining.
tags: [agent-training, code-agents, data-curation, synthetic-data, verification]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:42:05Z }
sources:
  - id: nanbeige2026compactagent
    resource: ../raw/arXiv-2607.22083v2/main.tex
    title: "Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model"
---

# Execution-grounded repository-to-trajectory synthesis

Nanbeige4.2's authors describe converting historical repository patches into containerized, executable agent tasks: agents see the parent-commit repository while reference patches and grading tests remain hidden; a verifier checks target and regression behavior; successful work from heterogeneous scaffolds is filtered into training trajectories. Recurrent failures are used as cues for further repository and patch mining, but the source does not independently establish the value of each stage.[^nanbeige2026compactagent]

## Construction and validation

- Repository and patch selection is guided by diversity and by failure categories observed on seed tasks. The pipeline reconstructs dependencies and test infrastructure from the parent commit in an isolated container, then synthesizes a task while withholding the patch and task-specific grading tests from the agent.[^nanbeige2026compactagent]
- Fail-to-pass tests must fail on the base repository and pass after the reference patch; pass-to-pass tests must pass in both states. The authors also audit the agreement among task description, hidden tests, and patch, revising recoverable tasks and discarding flaky, broken, or underspecified ones.[^nanbeige2026compactagent]
- Claude Code, OpenHands, SWE-agent, and Codex-based drivers generate trajectories in the sandbox. Only patches passing target and regression tests are retained; turn-level filtering removes incorrect tool calls, non-terminating loops, redundant actions, and context truncations while preserving essential debugging and recovery steps.[^nanbeige2026compactagent]

## Trust boundary

Executable tests provide evidence for the specified behavioral contract, not for untested requirements, security, or general code quality. The source gives no task count, acceptance rate, data-leakage analysis, or comparison showing that multi-scaffold generation or failure-guided mining improves generalization.[^nanbeige2026compactagent]

## Relationships

- Related to: [Hybrid environments for tool-use trajectory synthesis](hybrid-environments-for-tool-use-trajectory-synthesis.md) — both create executable environments and evolve task distributions from agent outcomes, but this method uses repository patches and tests.
- Used by: [Nanbeige4.2 compact looped agent model](nanbeige4-2-compact-looped-agent-model.md) — the source identifies this as its agentic software-engineering data pipeline.

[^nanbeige2026compactagent]: Nanbeige LLM Lab and Boss Zhipin, *Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model*, source manuscript, abstract, §§1--4, appendix, and figures (arXiv:2607.22083v2, 2026).