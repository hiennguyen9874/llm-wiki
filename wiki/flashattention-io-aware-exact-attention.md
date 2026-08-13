---
type: Concept
title: FlashAttention IO-aware exact attention
description: FlashAttention computes exact softmax attention tile by tile with online normalization, avoiding materialization of quadratic score and probability matrices in HBM.
tags: [flashattention, attention, gpu, memory-io, online-softmax, kernel-fusion]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-13T16:13:58Z }
sources:
  - id: flashattention-2022
    resource: ../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex
    title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
---

# FlashAttention IO-aware exact attention

FlashAttention is an IO-aware GPU implementation of scaled dot-product attention: it processes query, key, and value tiles in fast on-chip memory, maintains online softmax statistics, and writes only the final output and small per-row state rather than full $N\times N$ score or probability matrices to HBM. It preserves the full softmax-attention computation up to ordinary finite-precision and reduction-order differences; it is not a sparse, low-rank, or other algorithmic approximation.[^flashattention-2022]

## Tiled online computation

For a query tile $Q_i$, FlashAttention streams key/value tiles $(K_j,V_j)$ through SRAM. For each score tile,

$$
S_{ij}=Q_iK_j^T/\sqrt{d},
$$

it applies any mask, updates the running row maximum $m$, normalized exponential sum $l$, and output accumulator $o$, then discards the score tile. When a new tile changes the row maximum from $m_{old}$ to $m_{new}$, prior $l$ and $o$ are rescaled by $e^{m_{old}-m_{new}}$ before adding the new tile's contributions. The final output is $o/l$.[^flashattention-2022]

This online normalization makes blockwise processing numerically stable without retaining the complete score row. Causal tiles wholly above the diagonal can be skipped, while partially overlapping tiles receive the causal mask.[^flashattention-2022]

## Memory, IO, and backward-pass trade-off

Full attention still performs $O(N^2d)$ arithmetic. FlashAttention's principal change is avoiding $O(N^2)$ intermediate score and softmax tensors, retaining the output and per-row softmax statistics instead. The paper proves $O(N)$ additional memory beyond inputs and output for its tiled forward algorithm.[^flashattention-2022]

For head dimension $d$ and SRAM capacity $M$, the paper analyzes standard attention as requiring $\Theta(Nd + N^2)$ HBM accesses and FlashAttention as requiring $\Theta(N^2d^2/M)$, for $d \le M \le Nd$. It supplies a lower bound only in the stated sense: no exact algorithm can asymptotically improve on that HBM-access expression for *all* SRAM sizes in that range. This IO result does not reduce the quadratic attention arithmetic.[^flashattention-2022]

In training, the forward pass retains output and small row-wise normalization information rather than the full softmax matrix. The backward pass reloads tiles and recomputes scores and probabilities; with dropout, it saves and replays pseudo-random-generator state rather than a quadratic mask. This selectively exchanges computation for less HBM traffic and activation memory.[^flashattention-2022]

## Block-sparse extension

The paper also defines block-sparse FlashAttention: a predefined block mask skips disallowed score blocks, so it is an approximation when the mask omits token pairs. If $s$ is the fraction of nonzero blocks, its stated IO complexity is $\Theta(Nd + N^2d^2s/M)$. The reported speedup and quality results for this variant depend on the chosen sparsity pattern and workloads; they do not establish that it preserves full-attention outputs.[^flashattention-2022]

## Evidence boundary

This ingestion reviewed the paper’s LaTeX source, included algorithm and experiment files, and result tables. It does not derive additional numeric claims from the bundled benchmark-figure PDFs or images.

## Relationships

- **Implements:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) without changing its attention formula.[^flashattention-2022]
- **Optimizes:** [Self-attention computational profile](self-attention-computational-profile.md)'s full attention by reducing intermediate-memory traffic, not its quadratic arithmetic.[^flashattention-2022]
- **Elaborated by:** [FlashAttention: tiled attention và online softmax cho người mới](flashattention-tiled-attention-beginners-guide.md), which adds beginner-first derivation, reference code, and correctness tests.
- **Extended by:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md).

[^flashattention-2022]: Tri Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness,” NeurIPS 2022, bundled [LaTeX source](../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex), Sections 1–5 and Appendix A.
