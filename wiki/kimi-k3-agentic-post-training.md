---
type: Concept
title: Kimi K3 agentic post-training
description: Kimi K3 post-training combines agentic SFT, nine domain-and-effort RL experts, partial rollouts, budget controls, and multi-teacher on-policy distillation into one deployment-aware policy.
tags: [kimi-k3, reinforcement-learning, agents, distillation]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Kimi K3 agentic post-training

Kimi K3’s post-training pipeline establishes tool use with supervised fine-tuning, trains nine policies across three domains and three reasoning-effort levels, then consolidates them through multi-teacher on-policy distillation. Training targets long-horizon loops of reasoning, acting, observing, verification, and recovery rather than only single-turn answer quality.[^kimi-k3-2026]

## Three-stage pipeline

1. **Agentic SFT:** Prior Kimi models synthesize trajectories that undergo staged verification and human annotation. XTML serializes reasoning, responses, typed parallel tool calls, results, and request options.
2. **Specialized RL:** General tasks, general agents, and coding agents are each trained at low, high, and max effort, producing nine expert policies.
3. **Multi-teacher on-policy distillation:** For each sampled domain and effort, the corresponding teacher supplies a clipped per-token log-ratio reward to the unified student’s own rollout.[^kimi-k3-2026]

The report says top-$k$ distribution distillation offered no clear convergence or final-quality advantage in its setting. Its dense log-ratio reward integrates with the same RL infrastructure, but teacher consolidation can still inherit specialist errors and interference.[^kimi-k3-2026]

## Long-horizon RL controls

Partial rollout pauses generation when a fraction $\lambda$ of active trajectories finish rather than waiting for every straggler. Paused trajectories resume in later iterations, which raises policy staleness; the report relies on per-token regularization to keep updates local enough to tolerate this off-policy data.[^kimi-k3-2026]

Reasoning-effort RL estimates a per-problem baseline budget and assigns reward $-1$ when a trajectory exceeds a domain-specific multiplier. The multiplier is annealed from max to high and low effort. Agentic budgets count cumulative model output, including reasoning and tool arguments; this controls generated tokens, not total environment or verifier cost.[^kimi-k3-2026]

For non-verifiable tasks, an agentic generative reward model reads the outcome, creates a rubric, scores candidates, and records scores. An analogous length threshold makes overlong candidates automatically lose to reduce verbosity reward hacking. This makes evaluation procedure explicit but does not remove judge bias or rubric gaming.[^kimi-k3-2026]

## Environments and task synthesis

A configurable white-box harness composes tool interfaces, prompts, context management, skills, memories, and subagents so training is not tied to one scaffold. Environments include web research, professional knowledge work, software engineering, kernel optimization, visual tool use, persistent assistants, autonomous execution, and web development.[^kimi-k3-2026]

Task sourcing uses a self-evolving hierarchical knowledge graph. Agents recursively expand coarse concepts into finer nodes, search existing nodes before adding duplicates, retrieve public materials from sampled related concepts and ancestors, and synthesize tasks of selected types. This controls topical granularity and coverage, but the paper does not disclose graph-quality metrics or source-governance safeguards.[^kimi-k3-2026]

Autonomous Execution Tasks expose goals, constraints, tools, budgets, and verifier interfaces without reference trajectories. Rewards inspect final environment state; public verifiers provide feedback while hidden verifiers and submission limits reduce overfitting and reward hacking.[^kimi-k3-2026]

## Deployment-aware training

Quantization-aware training begins at SFT: routed expert weights use MXFP4 and activations MXFP8, while non-expert components remain at higher precision. Rollout and optimization use the same scheme to avoid train–inference precision mismatch.[^kimi-k3-2026]

A pre-trained multi-token-prediction layer is fine-tuned as an EAGLE-3-style draft. The target is frozen; the draft fuses early, middle, and final AttnRes block features and directly minimizes negative log speculative acceptance rather than KL divergence.[^kimi-k3-2026]

## Relationships

- **Post-trains:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Allocates:** [Test-time compute allocation](test-time-compute-allocation.md) through effort-conditioned policies and budget penalties.
- **Uses:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) for persistent rollout and sandbox state.
- **Deploys with:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md).

## Evidence limits

The report shows capability improving as RL FLOPs and average tool-call steps increase, but the interventions co-vary and do not prove that longer trajectories alone cause improvement. Many task suites, judges, and environments are internal; human guidance, synthesis sources, and reward-model bias limit reproducibility.[^kimi-k3-2026]

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Section 4 and Appendix F.
