---
type: Concept
title: Looped World Models
description: LoopWM is a proposed action-conditioned latent world-model architecture that reuses a transformer dynamics block across inner-loop refinement iterations and can defer decoding during multi-action rollouts.
tags: [world-models, looped-transformers, latent-dynamics, adaptive-computation, deferred-decoding]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:54:29Z }
sources:
  - id: loopwm-2026
    resource: ../raw/arXiv-2606.18208v1/draft.tex
    title: "Looped World Models"
  - id: loopwm-human-eval-2026
    resource: ../raw/arXiv-2606.18208v1/human_eval_combined.pdf
    title: "Human evaluation results on Danmaku Chan"
---

# Looped World Models

Looped World Models (LoopWM) are a proposed latent-dynamics world-model architecture. For each environment transition, the model combines the previous latent state, an observation embedding, and an action embedding, then applies a parameter-shared transformer block for multiple inner-loop iterations before prediction heads decode observation, reward, and continuation targets.[^loopwm-2026]

## Architecture

A prelude Transformer produces a normalized conditioning signal from the previous state, observation, and action. The recurrent block then applies shared Transformer parameters for $T$ iterations, so increasing effective depth does not add block parameters. A separately parameterized coda maps the final recurrent state to the latent state consumed by lightweight prediction heads.[^loopwm-2026]

The source writes each recurrent update as

$$
h^{(t+1)}=\bar A h^{(t)}+\bar B e+\bar{\mathcal R}(h^{(t)},e).
$$

It parameterizes the diagonal state-retention term as $A=\operatorname{diag}(-\exp(\mathbf a))$ and $\bar A=\exp(\Delta A)$, making every diagonal entry of $\bar A$ lie in $(0,1)$. This establishes contraction of that *linear retention term*, while layer normalization bounds the conditioning input magnitude.[^loopwm-2026]

## Variable depth and deferred decoding

Training samples the inner-loop count per sequence from a Poisson distribution and truncates backpropagation through loop iterations. The proposed inference gate may halt when a sigmoid score over the current hidden state exceeds a threshold; entropy regularization is intended to prevent trivial always-stop or never-stop behavior.[^loopwm-2026]

The source also proposes **deferred decoding** for a $K$-action rollout: advance the latent state for each action without invoking the observation, reward, and continuation heads, then decode only the terminal state. Its suggested training recipe combines terminal prediction loss, alignment of intermediate latent states to frozen encoder embeddings, a soft trajectory-change budget, and a curriculum that increases $K$.[^loopwm-2026]

## Relationships

- **Applies:** [Test-time compute allocation](test-time-compute-allocation.md) to inner-loop depth in action-conditioned world-model transitions.
- **Related to:** [Structured State Space Duality](structured-state-space-duality.md), which also uses a state transition but derives a different sequence-layer duality and does not establish LoopWM's proposed architecture.
- **Evaluated by:** [LoopWM evaluation and evidence limits](loopwm-evaluation-and-evidence-limits.md).

## Evidence limits

This is an incomplete, internally inconsistent manuscript rather than a reproducible implementation. The source supplies no code, hyperparameters, training-data specification, ablations isolating looping, deferred decoding, spectral retention, or early exit, and no measurements of adaptive-exit behavior or actual parameter/FLOP efficiency.[^loopwm-2026]

Its statement that the full nonlinear recurrence is "provably stable" over arbitrary rollout lengths does not follow from the displayed contraction of $\bar A$ alone: the nonlinear residual $\bar{\mathcal R}$ is not bounded or Lipschitz-constrained in the provided formulation. Treat the source as establishing the parameterization of the linear retention term, not a proof of bounded full-model rollouts.[^loopwm-2026]

The referenced one-page PDF instead reports human evaluation of "Danmaku Chan" for a "Baseline VLM" and "LWM," whereas its figure caption in the manuscript describes automatic danmaku results and the surrounding paper concerns ScienceWorld and AlfWorld. This artifact cannot support LoopWM evaluation claims and indicates a source-integrity problem.[^loopwm-human-eval-2026][^loopwm-2026]

[^loopwm-2026]: FaceMind Research Asia, “Looped World Models,” arXiv:2606.18208v1, [source](../raw/arXiv-2606.18208v1/draft.tex), abstract; Sections 1–3; included `method.tex`, `deferred.tex`, and `limitations.tex`.

[^loopwm-human-eval-2026]: “Human evaluation results on Danmaku Chan,” [source PDF](../raw/arXiv-2606.18208v1/human_eval_combined.pdf), one rendered page, inspected 2026-08-01.
