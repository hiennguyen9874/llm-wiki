---
type: Concept
title: Kaplan compute-optimal training allocation
description: Under Kaplan et al.’s fitted laws, compute-efficient training scales model size much faster than serial training steps and stops well before convergence.
tags: [scaling-laws, compute-optimal-training, training-compute, early-stopping, batch-size]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:36:58Z }
sources:
  - id: kaplan-scaling-laws-2020-v1
    resource: ../raw/arXiv-2001.08361v1/main.tex
    title: Scaling Laws for Neural Language Models
---

# Kaplan compute-optimal training allocation

Given the empirical fits in Kaplan et al., minimizing loss at a fixed training-compute budget favors a much larger model, a larger batch, and only a weak increase in serial optimization steps. In this source’s terminology, the optimum is deliberately short of convergence rather than a recommendation to train any model to convergence.[^kaplan-scaling-laws-2020-v1]

## Allocation rule

Using compute adjusted to $C_{\min}$—the estimated compute at batch size well below the critical batch size—the paper reports:

$$
N_{\mathrm{opt}}\propto C_{\min}^{0.73},\qquad
B\propto C_{\min}^{0.24},\qquad
S_{\min}\propto C_{\min}^{0.03}.
$$

Thus, under these fitted laws, most additional compute goes to parameter count; most of the modest growth in processed data is realized through batch size rather than more serial updates.[^kaplan-scaling-laws-2020-v1]

The analytical derivation combines the paper’s model-size, training-step, and critical-batch-size fits. It predicts $\alpha_C^{\min}=1/(1/\alpha_S+1/\alpha_B+1/\alpha_N)\approx0.054$, close to the reported direct fit of roughly $0.050$ for loss versus $C_{\min}$.[^kaplan-scaling-laws-2020-v1]

## Early stopping and efficiency

At the compute-efficient frontier, the derivation places loss about $\alpha_N/\alpha_S\approx10\%$ above the converged loss for the selected model. The paper therefore characterizes the optimum as training a very large model significantly short of convergence, with greater sample efficiency than smaller models trained longer.[^kaplan-scaling-laws-2020-v1]

For a model and finite dataset, the paper also gives a lower-bound-style estimate for when early stopping should occur from the gap between the finite-data loss and infinite-data converged loss. It presents this as a rough estimate, not an exact stopping rule.[^kaplan-scaling-laws-2020-v1]

## Limits and scope

These exponents and the resulting allocation are conditional on the paper’s decoder-only Transformer experiments, WebText2 data, optimizer choices, fixed 1,024-token context, and its $C\approx6NBS$ compute model. The paper itself predicts that its compute and data trends eventually become inconsistent and must fail before or around their intersection; it gives the numerical intersection only as a highly uncertain conjecture. This concept records the 2020 source’s prescription, not a current universal training rule.[^kaplan-scaling-laws-2020-v1]

## Relationships

- **Depends on:** [Empirical language-model loss scaling laws](empirical-language-model-loss-scaling-laws.md), whose fitted exponents supply this allocation.
- **Applies to:** decoder-only instances of [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) in the reported experiments.

[^kaplan-scaling-laws-2020-v1]: Jared Kaplan et al., “Scaling Laws for Neural Language Models,” arXiv:2001.08361v1, bundled [LaTeX source](../raw/arXiv-2001.08361v1/main.tex), especially Sections 4–6 and Appendix A.
