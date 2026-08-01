---
type: Concept
title: Stable LatentMoE and Quantile Balancing
description: Stable LatentMoE routes tokens through compact experts and stabilizes extreme sparsity with routed-branch normalization, bounded SiTU-GLU activations, and quantile-based load-balancing biases.
tags: [mixture-of-experts, latentmoe, load-balancing, quantile-balancing]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Stable LatentMoE and Quantile Balancing

Stable LatentMoE separates full model width from routed-expert width: shared experts process full-width tokens, while routed experts operate in a compact latent space. Kimi K3 uses two shared experts and selects 16 of 896 routed experts per token at latent width 3,584, making a large expert pool affordable while introducing activation- and balancing-stability problems that require explicit controls.[^kimi-k3-2026]

## Routed latent path

A down-projection maps a token from model width $d$ to latent width $\ell$; top-$k$ compact experts process it; their weighted aggregate is RMS-normalized before an up-projection returns it to model width. Shared experts remain full-width and always active. The normalization limits selected-expert scale variation before the routed and shared paths are combined.[^kimi-k3-2026]

## Bounded activation

SiTU-GLU smoothly caps both multiplicative branches of SwiGLU:

$$
[\beta_1\tanh(g/\beta_1)\sigma(g)]\odot[\beta_2\tanh(u/\beta_2)].
$$

With K3’s $\beta_1=4$ and $\beta_2=25$, each output coordinate is bounded in magnitude by 100. The scaled $\tanh$ is locally linear, so the activation matches SwiGLU to first order near zero while avoiding two unbounded factors. This controls low-precision overflow risk but saturation can still reduce gradients at large magnitude.[^kimi-k3-2026]

## Quantile Balancing

Routing applies an expert-specific bias only to top-$k$ selection, not to the normalized mixture weights. Quantile Balancing (QB) updates each bias from the score margin quantile corresponding to the target load $mk/n$. This is the exact coordinate minimizer of the dual balanced-assignment objective under the report’s no-tie and integral-load assumptions, rather than a fixed-size sign step based only on whether an expert is over- or underloaded.[^kimi-k3-2026]

The next-step bias for expert $j$ is estimated from the $(1-k/n)$ quantile of its score margins against token cutoffs, then all biases are mean-centered. At scale, per-expert histograms pool margin counts across ranks with one integer all-reduce; the estimate’s error is bounded by the bin width. K3 reports 1,000 bins and no measurable residual imbalance, but does not provide a cross-system benchmark establishing universal superiority.[^kimi-k3-2026]

## Operational boundary

QB balances router assignments, while MoonEP separately guarantees equal aggregate token work per expert-parallel rank by dynamically replicating experts. These mechanisms solve different levels of imbalance: learning and expert utilization versus distributed execution and static shapes.[^kimi-k3-2026]

## Relationships

- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md).
- **Operationalized by:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md) through MoonEP and dedicated latent-MoE kernels.

## Evidence limits

The paper reports improved validation loss from routed-branch normalization and stable large-scale optimization from the combined design, but it does not isolate every component at 2.8T scale. Exact QB balance is a property of its assignment formulation; histogram approximation, delayed updates, ties, and changing training distributions make realized routing an empirical systems result.[^kimi-k3-2026]

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.3 and Appendix B–C.
