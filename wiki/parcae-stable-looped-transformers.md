---
type: Concept
title: Parcae stable looped transformers
description: Parcae constrains recurrent input-state dynamics, normalizes the prelude output, and samples depth per sequence to stabilize middle-looped language-model training.
tags: [dynamical-systems, recurrent-depth, stability, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T04:08:40Z }
sources:
  - id: prairie2026parcae
    resource: ../raw/arXiv-2604.12946v1/main.tex
    title: "Parcae: Scaling Laws For Stable Looped Language Models"
---

# Parcae stable looped transformers

Parcae is a prelude–recurrent-core–coda language model designed to prevent recurrent residual-state explosion. It treats the recurrent update as a nonlinear dynamical system, constrains a linearized state-transition component to be stable, normalizes the fixed input injected into every recurrence, and samples recurrence depth per sequence. Source experiments report more robust convergence and better parameter- and data-matched quality than tested recurrent-depth and fixed-depth baselines, but the fixed-depth comparison does not match training or inference FLOPs.[^prairie2026parcae]

## Stable recurrent update

- The source writes the recurrent state as $h_{t+1}=\bar A h_t+\bar B e+\overline{\mathcal R}(h_t,e)$, where $e$ is the prelude representation and $\overline{\mathcal R}$ contains the nonlinear transformer operations. Dropping the nonlinear term gives the linear time-invariant surrogate used for stability analysis.[^prairie2026parcae]
- Parcae parameterizes the continuous transition as $A=\operatorname{Diag}(-\exp(\mathtt{log\_A}))$ and discretizes it as $\bar A=\exp(\Delta A)$. This makes the diagonal transition eigenvalues lie between zero and one; $\bar B=\Delta B$ remains unconstrained.[^prairie2026parcae]
- A layer normalization on the prelude output gives $e=\operatorname{LN}(P(s))$. The source introduced this after a 1.3B run developed late loss spikes: checkpoint diagnostics attributed the initial recurrent-state jump to the injected prelude representation rather than to $\bar A$, $\bar B$, or the recurrent transformer blocks.[^prairie2026parcae]

The stability condition is derived for a linearized surrogate, not the complete nonlinear transformer. The experiments support the intervention within the tested architecture, but do not prove that constraining $\bar A$ is sufficient for arbitrary looped networks.[^prairie2026parcae]

## Variable-depth training

- Rather than drawing one depth for an entire microbatch, Parcae samples depth per sequence to better estimate the objective’s expectation over depth. In a reported 350M run this removed visible loss spikes and added 1.8% pretraining wall-clock overhead; the evidence is source-run rather than independently replicated.[^prairie2026parcae]
- The training algorithm samples total forward recurrence from the intended depth distribution and separately truncates gradient-visible steps. This corrects an identified shifted-distribution mismatch in the compared RDM recipe and improved evaluation away from the mean training depth in a 100M ablation.[^prairie2026parcae]
- Main experiments set gradient-visible mean depth to $\lceil\mu_{\mathrm{rec}}/2\rceil$. An appendix ablation suggests that holding backward depth fixed while increasing forward recurrence can erase expected gains, so forward and backward depth are coupled design variables rather than interchangeable compute controls.[^prairie2026parcae]

## Reported evidence and limits

- Across a learning-rate sweep from $2\times10^{-4}$ to $10^{-3}$, the tested Parcae setup converged in all five runs, residual-normalized RDMs in two, and pre-normalized RDMs in one. Divergent unconstrained runs developed transition values above the source’s stability threshold together with exploding recurrent-state norms.[^prairie2026parcae]
- Against 100M and 350M parameter- and data-matched RDMs, Parcae reports up to 6.2% lower held-out perplexity, 9.1% lower WikiText perplexity, and up to 1.8 points higher mean downstream score.[^prairie2026parcae]
- Against source-trained fixed-depth Transformers from 140M to 1.3B parameters, all trained with the same data at each size, Parcae at eight recurrences reports 4.3–9.2% lower validation perplexity and gains up to 2.99 Core and 1.18 Core-Extended points. The authors tuned the Transformer/RDM baselines but reused those learning rates without tuning Parcae; conversely, recurrence gives Parcae more compute, so these results establish parameter/data efficiency under the source recipe, not compute-matched superiority.[^prairie2026parcae]
- The largest run has 1.3B parameters and 104B training tokens. The manuscript reports no independent replication or released implementation, and explicitly leaves larger parameter/FLOP scales, deeper recurrence, alternate discretizations, and full-rank dynamics open.[^prairie2026parcae]

## Relationships

- Enables: [Parcae recurrence scaling laws](parcae-recurrence-scaling-laws.md) — the stabilized architecture is the experimental vehicle for the source’s compute-scaling study.
- Related to: [DeepLoop residual scaling for looped transformers](deeploop-residual-scaling-for-looped-transformers.md) — both target recurrent-depth stability, but Parcae constrains explicit input/state dynamics while DeepLoop changes residual scaling and initialization.
- Related to: [Controlled looped-model architecture ablations](controlled-looped-model-architecture-ablations.md) — Parcae also uses a prelude–recurrent-core–coda layout with persistent input injection, while adding dynamical-system constraints and training changes.

[^prairie2026parcae]: Prairie et al., *Parcae: Scaling Laws For Stable Looped Language Models*, source manuscript, abstract; §§2–5; appendices “Per-sequence Sampling Reduces Loss Spikes,” “Sampling of Truncated Recurrence,” “Selecting $\mu_\text{rec}$ and $\mu_\text{bwd}$,” and “Ablation of Prelude Normalization” (arXiv:2604.12946v1, 2026).
