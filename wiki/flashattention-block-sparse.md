---
type: Concept
title: Block-Sparse FlashAttention
description: Block-masked FlashAttention variant that skips zero blocks for sparsity-proportional IO and runtime gains to 64K context.
tags: [attention, flashattention, sparse-attention, io-aware, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T14:00:00Z }
sources:
  - id: fa-block
    resource: ../raw/arXiv-2205.14135v2/src/extension.tex
    title: 'Extension: Block-Sparse FlashAttention'
  - id: fa-theory
    resource: ../raw/arXiv-2205.14135v2/src/theory.tex
    title: 'Analysis: IO Complexity of FlashAttention'
  - id: fa-exp
    resource: ../raw/arXiv-2205.14135v2/src/experiments.tex
    title: FlashAttention Experiments
---

Block-sparse FlashAttention is the approximate extension in the original FlashAttention paper that applies a predefined block-sparsity mask inside the same tiled, IO-aware loop and skips fully zero blocks, reducing HBM traffic roughly in proportion to sparsity and reaching 64K context[^fa-block].

## Mask formalism

Given `Q,K,V in R^(N×d)` and mask `Mtilde in {0,1}^(N×N)`, it computes `S=QK^T`, `P=softmax(S ⊙ 1_Mtilde)`, `O=PV`, where masked-out entries are `-inf`[^fa-block].

The mask must have block form: for block sizes `B_r,B_c`, `Mtilde_{k,l}=M_{i,j}` with `i=floor(k/B_r)`, `j=floor(l/B_c)` for a coarser `M in {0,1}^(N/B_r × N/B_c)`[^fa-block].

## Algorithm change

The algorithm is identical to dense FlashAttention except zero blocks are skipped rather than loaded and computed[^fa-block].

This makes block-sparse FlashAttention a primitive for realizing approximate attention without reintroducing the memory-access overhead that made many prior sparse methods wall-clock slow[^fa-block].

## IO complexity

For SRAM size `M` with `d ≤ M ≤ Nd` and nonzero-block fraction `s`, block-sparse FlashAttention needs `Θ(Nd + N^2 d^2 M^-1 s)` HBM accesses[^fa-block].

The `s` factor applies directly to the dominant term; with typical settings such as `s=N^-1/2` or `s=N^-1 log N`, this becomes roughly `Θ(N√N)` or `Θ(N log N)` IO complexity[^fa-block].

The paper validates that runtime improves proportionally with sparsity[^fa-theory].

## Sparsity pattern used

Downstream experiments use a fixed butterfly sparsity pattern, chosen because prior work showed it can approximate arbitrary sparsity patterns[^fa-block].

## Empirical position

- Long-Range Arena: block-sparse FlashAttention keeps dense-level accuracy (59.6 vs 59.8 dense vs 59.3 Transformer) with 2.8× speedup over standard attention, faster than all tested approximate baselines[^fa-exp].
- Path-X (16K): 56.0 accuracy; Path-256 (64K): 63.1 accuracy, the first reported better-than-chance sequence-model result on Path-256[^fa-exp].
- Attention microbenchmarks: block-sparse FlashAttention is faster than all tested exact, sparse, and approximate implementations across sequence lengths, while sharing dense FlashAttention's linear memory footprint[^fa-exp].

For dense training numbers, long-document gains, and kernel benchmarks, see [FlashAttention Original Paper Evaluation](flashattention-paper-evaluation.md).

## Relationships

- Uses [FlashAttention Exact IO-Aware Attention](flashattention.md) — synthesis: reuses tiling, online softmax, recomputation, and fused kernels, adding only mask-aware block skipping.
- Contrasts with [LongCat Sparse Attention](longcat-sparse-attention.md) — synthesis: block-sparse FlashAttention uses a fixed butterfly block mask; LongCat adds streaming-aware, cross-layer, and hierarchical indexing.
- Contrasts with [FlexAttention Programmable Attention Kernels](flex-attention.md) — synthesis: block-sparse FlashAttention is a fixed block-sparse kernel; FlexAttention compiles arbitrary score and mask variants.

## Coverage limits

- Compiled from `src/extension.tex`, `src/theory.tex`, and `src/experiments.tex` plus table captions; figure PDFs (`figs/flashattn_micros.pdf`, `figs/benchmarks.tex`) were not visually rendered.
- Full per-baseline timing and memory tables under `tables/` were excluded as non-durable; summary claims above are the durable synthesis.
- No secrets, credentials, or PII were found in the compiled tex sources.

[^fa-block]: Extension: Block-Sparse FlashAttention — `../raw/arXiv-2205.14135v2/src/extension.tex`.
[^fa-theory]: Analysis: IO Complexity of FlashAttention — `../raw/arXiv-2205.14135v2/src/theory.tex`.
[^fa-exp]: FlashAttention Experiments — `../raw/arXiv-2205.14135v2/src/experiments.tex`.
