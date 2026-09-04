---
type: Concept
title: Difficulty-aware reasoning length control
description: A proposed RL reward penalizes a correct response's excess over its fixed problem-specific length budget in proportion to the rollout group's current correctness, while alternating constrained and free-expansion phases.
tags: [reinforcement-learning, reasoning, reward-modeling, training]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:42:05Z }
sources:
  - id: nanbeige2026compactagent
    resource: ../raw/arXiv-2607.22083v2/main.tex
    title: "Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model"
---

# Difficulty-aware reasoning length control

The Nanbeige4.2 report proposes a reasoning-RL reward that subtracts a continuous length penalty only above a fixed per-problem budget, scaled by the current rollout group's fully-correct fraction. By alternating constrained and no-penalty phases, it aims to compress reasoning for reliably solved problems without suppressing exploration on harder ones; the report does not isolate this objective in an ablation.[^nanbeige2026compactagent]

## Objective

- For each problem, the fixed budget is the median length of successful historical rollouts from preceding checkpoints. A response within budget receives no length penalty.[^nanbeige2026compactagent]
- In constrained phases, the source defines $r_i=r_i^{base}-\alpha p_q[(L_i-b_q)/(L_{max}-b_q)]_0^1$, where $p_q$ is the group's fully-correct fraction. Thus excess length is penalized more on problems the group currently solves reliably; free-expansion phases disable the penalty.[^nanbeige2026compactagent]
- The authors note that, for binary task rewards and $\alpha<1$, subtracting rather than gating the penalty preserves a preference for correct over incorrect responses regardless of length. This is a property of the stated reward construction, not evidence that optimization achieves the intended behavior.[^nanbeige2026compactagent]

## Reported context and limitations

In the source's aggregate before/after-RL figure, six selected benchmarks all show higher reported accuracy with fewer average output tokens; because the full RL pipeline also includes RLHF and agentic RL, the figure does not attribute those changes to length control.[^nanbeige2026compactagent]

Budgets derived from historical successful rollouts can encode earlier model inefficiency or a narrow solution style. The source does not report sensitivity to budget quality, phase schedules, $\alpha$, reward hacking, or task difficulty calibration.[^nanbeige2026compactagent]

## Relationships

- Used by: [Nanbeige4.2 compact looped agent model](nanbeige4-2-compact-looped-agent-model.md) — the source places this reasoning-RL stage after two-stage RLHF and before agentic RL.

[^nanbeige2026compactagent]: Nanbeige LLM Lab and Boss Zhipin, *Nanbeige4.2-3B: Unlocking Agentic Capabilities in a Compact Model*, source manuscript, abstract, §§1--4, appendix, and figures (arXiv:2607.22083v2, 2026).