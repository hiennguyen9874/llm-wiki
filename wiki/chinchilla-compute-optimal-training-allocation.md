---
type: Concept
title: Chinchilla compute-optimal training allocation
description: Chinchilla’s fitted loss law reallocates fixed pretraining compute nearly evenly between dense-model parameters and training tokens, yielding an approximate 20-token-per-parameter heuristic.
tags: [chinchilla, scaling-laws, compute-optimal-training, training-compute, pre-training]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:12:13+07:00 }
sources:
  - id: chinchilla-summary
    resource: ../raw/Chinchilla.md
    title: Chinchilla overview (summary)
---

# Chinchilla compute-optimal training allocation

The Chinchilla analysis models final language-model loss as separate finite-capacity and finite-data terms. At fixed dense-Transformer pretraining compute, its empirical fit allocates additional compute approximately equally to parameter count and training-token count—unlike the earlier Kaplan prescription that strongly favored parameters.[^chinchilla-summary]

## Fixed-compute formulation

For parameter count $N$, training tokens $D$, and training compute $C$, the source uses the dense-Transformer approximation:

$$
C \approx 6ND.
$$

It fits final loss with:

$$
\hat L(N,D)=E+\frac{A}{N^\alpha}+\frac{B}{D^\beta},
$$

where $E$ is irreducible loss and the two declining terms represent finite model capacity and finite training data. Under the fixed-compute constraint, the optimum has $N_{\mathrm{opt}}\propto C^{\beta/(\alpha+\beta)}$ and $D_{\mathrm{opt}}\propto C^{\alpha/(\alpha+\beta)}$.[^chinchilla-summary]

## Empirical allocation

Three reported estimation methods place the parameter/token exponents near one half: $(0.50, 0.50)$, $(0.49, 0.51)$, and $(0.46, 0.54)$. The summary therefore gives the practical scaling rule $N_{\mathrm{opt}}\propto C^{0.5}$ and $D_{\mathrm{opt}}\propto C^{0.5}$: multiplying compute by four approximately doubles both quantities.[^chinchilla-summary]

A commonly cited rule of thumb from this fit is $D_{\mathrm{opt}}\approx20N$, with $D$ in tokens and $N$ in parameters. It is an empirical heuristic, not a physical constant: architecture, tokenizer, data quality and distribution, optimizer, schedule, parameter-count convention, and the fitted compute range can change it.[^chinchilla-summary]

## Scope and limits

The source reports that the scaling analysis covered more than 400 runs from roughly 70M to over 16B parameters, then extrapolated to the 70B-parameter Chinchilla model. It also notes that the power-law assumption, mostly sub-epoch training, unmodeled data quality, and possible benchmark contamination limit generalization.[^chinchilla-summary]

This allocation optimizes loss under a fixed *pretraining* FLOP budget. It does not directly optimize lifetime cost: when inference volume dominates, spending more once on training a smaller model on more tokens can reduce per-token serving cost. Here, “overtraining” relative to Chinchilla means exceeding the training-token allocation for that restricted objective; it does not by itself imply overfitting.[^chinchilla-summary]

## Relationships

- **Contradicts:** [Kaplan compute-optimal training allocation](kaplan-compute-optimal-training-allocation.md) on how fixed training compute should be divided: the earlier fitted prescription emphasizes model size, whereas this source’s fit is near-balanced.
- **Characterizes:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md) as comparatively undertrained by its approximate token-per-parameter heuristic.

[^chinchilla-summary]: “Chinchilla overview (summary),” [raw source](../raw/Chinchilla.md), Sections 1–8 and 12–13. This is a secondary Vietnamese-language summary that cites the Chinchilla paper and related webpages; the primary paper has not been independently ingested here.
