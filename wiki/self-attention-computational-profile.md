---
type: Concept
title: Self-attention computational profile
description: Full self-attention offers constant sequential depth and direct token-to-token paths at quadratic full-sequence cost, while restricted attention trades cost for longer paths.
tags: [self-attention, complexity, parallelism, long-context]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-13T16:13:58Z }
sources:
  - id: flashattention-2022
    resource: ../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex
    title: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
---

# Self-attention computational profile

For a full sequence of length $n$ and representation width $d$, a full self-attention layer costs $O(n^2d)$, requires $O(1)$ sequential operations, and directly connects any pair of positions with maximum path length $O(1)$. This favors parallel training and short dependency paths, but its quadratic token interaction is the central scaling cost for long sequences.[^vaswani-transformer-2017]

## Layer comparison

The paper compares layer types along three separate axes rather than treating “efficiency” as one quantity:[^vaswani-transformer-2017]

| Layer type | Complexity per layer | Sequential operations | Maximum path length |
|---|---:|---:|---:|
| Full self-attention | $O(n^2d)$ | $O(1)$ | $O(1)$ |
| Recurrent | $O(nd^2)$ | $O(n)$ | $O(n)$ |
| Convolutional | $O(knd^2)$ | $O(1)$ | $O(\log_k n)$ |
| Restricted self-attention | $O(rnd)$ | $O(1)$ | $O(n/r)$ |

Here $k$ is convolution kernel width and $r$ is the attended neighborhood size. Full self-attention is cheaper than a recurrent layer under these formulas when $n<d$, a condition the paper says commonly held for the sentence representations in its machine-translation setting.[^vaswani-transformer-2017]

## Trade-off

- **Parallelism:** known positions can be processed together because a layer has no recurrence across token positions.
- **Dependency path:** one layer can directly connect distant positions, shortening forward and backward signal paths.
- **Quadratic interaction:** every query compares with every key, so full-sequence cost grows quadratically in token count.
- **Restriction:** limiting attention to neighborhoods lowers complexity to $O(rnd)$ but increases the maximum path between distant positions to $O(n/r)$.[^vaswani-transformer-2017]

These are asymptotic, per-layer comparisons for processing a sequence, not a complete account of wall-clock performance or autoregressive decoding. Implementations, memory traffic, batching, caching, and hardware can change practical behavior; the original paper does not analyze modern KV-cached decoding.[^vaswani-transformer-2017]

## Relationships

- **Motivates:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md).
- **Applies to:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) when attention spans the full sequence.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which bounds recurrent decode state by giving up exact token-addressable softmax attention.
- **Optimized by:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md), which reduces full attention's intermediate-memory traffic while retaining its quadratic arithmetic.[^flashattention-2022]

[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762v7, bundled [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially `why_self_attention.tex`.

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 2, 8, and 13.

[^flashattention-2022]: Tri Dao et al., “FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness,” NeurIPS 2022, bundled [LaTeX source](../raw/arXiv-2205.14135v2/streaming_attention_neurips_2022.tex), Sections 1–4.
