---
type: Concept
title: Empirical language-model loss scaling laws
description: Kaplan et al. report power-law cross-entropy scaling with non-embedding parameters, dataset tokens, and batch-adjusted training compute for decoder-only Transformer language models.
tags: [scaling-laws, language-modeling, training-compute, datasets, transformers]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:36:58Z }
sources:
  - id: kaplan-scaling-laws-2020-v1
    resource: ../raw/arXiv-2001.08361v1/main.tex
    title: Scaling Laws for Neural Language Models
---

# Empirical language-model loss scaling laws

Kaplan et al. find that the cross-entropy loss of their decoder-only Transformer language models follows fitted power laws in non-embedding parameter count $N$, dataset size $D$, and batch-adjusted minimum compute $C_{\min}$ across their measured ranges. The result is empirical and tokenization- and dataset-dependent, not a claim of universal exponents.[^kaplan-scaling-laws-2020-v1]

## Experimental setting

The study trains autoregressive Transformers on WebText2 with a 50,257-token byte-pair vocabulary and a 1,024-token context. It varies model size from 768 to 1.5 billion non-embedding parameters and data from 22 million to 23 billion tokens; its principal metric is test cross-entropy in nats per token.[^kaplan-scaling-laws-2020-v1]

At fixed non-embedding parameter count, changing depth, width, attention heads, or feed-forward width over the investigated range changed loss only mildly. Excluding embedding parameters made the model-size trend more consistent across model shapes.[^kaplan-scaling-laws-2020-v1]

## Fitted relationships

When the other factors are not limiting, the paper summarizes its fits as:

$$
L(N) = (N_c/N)^{\alpha_N},\qquad
L(D) = (D_c/D)^{\alpha_D},\qquad
L(C_{\min}) = (C_c^{\min}/C_{\min})^{\alpha_C^{\min}}.
$$

For this source version’s WebText2 setting, the summary fit reports $\alpha_N=0.076$, $\alpha_D=0.095$, and $\alpha_C^{\min}=0.050$. The numerical scales and their units depend on the tokenizer and vocabulary, so the paper does not treat them as fundamental constants.[^kaplan-scaling-laws-2020-v1]

For simultaneous finite model and dataset size, the authors fit:

$$
L(N,D)=\left[\left(\frac{N_c}{N}\right)^{\alpha_N/\alpha_D}+\frac{D_c}{D}\right]^{\alpha_D}.
$$

This fit implies a data requirement approximately proportional to $N^{0.74}$ to hold the overfitting penalty fixed in the investigated regime. On held-out distributions, the authors report loss improvements that track in-distribution validation loss with a roughly constant offset.[^kaplan-scaling-laws-2020-v1]

## Training and batch-size interpretation

The paper estimates non-embedding training compute as $C \approx 6NBS$, for batch size $B$ in tokens and parameter-update count $S$. It defines $C_{\min}$ as the compute that would be needed at a batch size far below the critical batch size, distinguishing it from compute measured at an arbitrary fixed batch size.[^kaplan-scaling-laws-2020-v1]

Its measured critical batch size is fit as $B_{\mathrm{crit}}(L) = B_*/L^{1/\alpha_B}$ with $\alpha_B\approx0.21$. This is a reported fit for these experiments, rather than a batch-size rule guaranteed for other architectures, data, optimizers, or target losses.[^kaplan-scaling-laws-2020-v1]

## Evidence limits

The source reports empirical fits rather than a derivation. It explicitly cautions that the laws must eventually flatten because language has non-zero entropy; the small-data regime fit poorly, very large-loss extrapolations of critical batch size were uncertain, regularization was not systematically varied, and the compute estimate omits context-length-dependent terms. No later scaling-law source has been reconciled in this wiki yet.[^kaplan-scaling-laws-2020-v1]

## Relationships

- **Studies:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) in its decoder-only form.
- **Basis for:** [Kaplan compute-optimal training allocation](kaplan-compute-optimal-training-allocation.md), which derives a training prescription from these fitted laws.

[^kaplan-scaling-laws-2020-v1]: Jared Kaplan et al., “Scaling Laws for Neural Language Models,” arXiv:2001.08361v1, bundled [LaTeX source](../raw/arXiv-2001.08361v1/main.tex), especially Sections 1–6 and Appendix A.
