---
type: Concept
title: Deterministic parameter-free projection for linear attention
description: DPFP maps keys and queries to a larger positive feature space through deterministic ReLU-product features, trading additional fixed-state width for a higher associative-memory capacity bound.
tags: [associative-memory, dpfp, linear-attention]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:29Z }
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
---

# Deterministic parameter-free projection for linear attention

Deterministic parameter-free projection (DPFP) is a positive feature map for linear attention that expands the dot-product space without learned or random projection weights. It was proposed to increase the finite associative memory's capacity bound while avoiding the sampling variance and implementation complexity of random-feature softmax approximations.[^fast-weight-programmers-2021]

## Construction

For input $x\in\mathbb{R}^{d_{\mathrm{key}}}$, DPFP concatenates $x$ and $-x$, applies ReLU, and forms products of components separated by offsets $\nu\in\{1,\ldots,\nu_{\max}\}$. Its output is non-negative and has dimension $d_{\mathrm{dot}}=2d_{\mathrm{key}}\nu_{\max}$. The offset count $\nu_{\max}$ is therefore a direct fixed-state-width and capacity control.[^fast-weight-programmers-2021]

The products create sparse conjunction features: in the paper's two-dimensional illustration, each sign region activates a distinct component. This encourages mapped keys from different regions to be orthogonal, which reduces crosstalk in the outer-product associative state.[^fast-weight-programmers-2021]

## Capacity and trade-offs

Increasing $d_{\mathrm{dot}}$ raises the number of mutually orthogonal mapped keys that the paper's interference-free retrieval analysis can accommodate. It does not create unbounded or exact-softmax memory: superposed associations can still interfere, and larger feature maps increase the fixed per-head state and computation.[^fast-weight-programmers-2021]

Compared with FAVOR+, DPFP is deterministic and parameter-free rather than using sampled random features. The paper reports that, on WMT14 English–German at $d_{\mathrm{dot}}=256$, DPFP reached 26.9 test BLEU versus 26.8 for the tested Linear Transformer and 25.3 for Performer; at 512 dimensions, DPFP's 27.1 trailed the tested Performer and standard Transformer at 27.7. These author-run results support a task- and width-specific trade-off, not a general ordering.[^fast-weight-programmers-2021]

## Relationships

- **Extends:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) by expanding its feature-space capacity bound while retaining a sequence-length-independent state.
- **Complements:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md); the paper reports that the corrective delta update improved its DPFP language-model configuration even outside the designed overcapacity setting.[^fast-weight-programmers-2021]

## Evidence limits

DPFP's construction, capacity motivation, and reported synthetic, translation, and language-model experiments come from one primary paper. Its capacity argument assumes interference-free retrieval through orthogonal mapped keys; it is not a calibrated capacity estimate for arbitrary trained models or natural-language workloads. The reported evaluations are not independently replicated here.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 4–6 and Appendices C–D.
