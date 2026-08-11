---
type: Concept
title: FlashAttention IO-aware exact attention
description: FlashAttention computes exact softmax attention tile by tile with online normalization, avoiding materialization of quadratic score and probability matrices in HBM.
tags: [flashattention, attention, gpu, memory-io, online-softmax, kernel-fusion]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:35:10Z }
sources:
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
---

# FlashAttention IO-aware exact attention

FlashAttention is an IO-aware GPU implementation of scaled dot-product attention: it processes query, key, and value tiles in fast on-chip memory, maintains online softmax statistics, and writes only the final output and small per-row state rather than full $N\times N$ score or probability matrices to HBM. It preserves the full softmax-attention computation up to ordinary finite-precision and reduction-order differences; it is not a sparse, low-rank, or other algorithmic approximation.[^flashattention-summary]

## Tiled online computation

For a query tile $Q_i$, FlashAttention streams key/value tiles $(K_j,V_j)$ through SRAM. For each score tile,

$$
S_{ij}=Q_iK_j^T/\sqrt{d},
$$

it applies any mask, updates the running row maximum $m$, normalized exponential sum $l$, and output accumulator $o$, then discards the score tile. When a new tile changes the row maximum from $m_{old}$ to $m_{new}$, prior $l$ and $o$ are rescaled by $e^{m_{old}-m_{new}}$ before adding the new tile's contributions. The final output is $o/l$.[^flashattention-summary]

This online normalization makes blockwise processing numerically stable without retaining the complete score row. Causal tiles wholly above the diagonal can be skipped, while partially overlapping tiles receive the causal mask.[^flashattention-summary]

## Memory and backward-pass trade-off

Full attention still performs $O(N^2d)$ arithmetic. FlashAttention's principal change is avoiding $O(N^2)$ intermediate score and softmax tensors, leaving output and row-wise statistics whose sequence-length dependence is near $O(Nd)$ for the described attention intermediates.[^flashattention-summary]

In training, the forward pass retains output and small row-wise normalization information instead of the full softmax matrix. The backward pass reloads tiles and recomputes needed scores and probabilities. This selectively exchanges additional computation for less HBM traffic and activation memory.[^flashattention-summary]

## Relationships

- **Implements:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) without changing its attention formula.[^flashattention-summary]
- **Optimizes:** [Self-attention computational profile](self-attention-computational-profile.md)'s full attention by reducing intermediate-memory traffic, not its quadratic arithmetic.[^flashattention-summary]
- **Elaborated by:** [FlashAttention: tiled attention và online softmax cho người mới](flashattention-tiled-attention-beginners-guide.md), which adds beginner-first derivation, reference code, and correctness tests.
- **Extended by:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md).

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 1–11. This is secondary-source evidence summarizing Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness” (NeurIPS 2022); the primary paper has not been independently ingested here.
