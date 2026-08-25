---
type: Concept
title: LongCat Sparse Attention
description: LongCat Sparse Attention combines streaming-aware fixed regions, distilled cross-layer index reuse, and training-free hierarchical selection to address DSA’s scattered KV reads and indexer overhead while retaining token-addressable KV state.
tags: [attention, sparse-attention, longcat, long-context, multi-head-latent-attention, inference]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:13:08Z }
sources:
  - id: longcat-lsa-2026
    resource: ../raw/2608.01662_LongCatSparseAttention/longcat.tex
    title: "LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing"
---

# LongCat Sparse Attention

LongCat Sparse Attention (LSA) is a DSA extension that keeps token-level MLA KV entries but co-designs selection and kernels around three separate bottlenecks: scattered selected-KV access, repeated indexing across depth, and global token-level top-k selection. It therefore reduces attention-read and indexer work, not the total per-token KV-cache footprint.[^longcat-lsa-2026]

## Streaming-aware indexing

LSA makes the selected set the union of a fixed attention-sink region, a local sliding window, and dynamically selected non-streaming tokens. In its reported default $K=2048$ configuration, 16 sink tokens and a 1,024-token window are fixed, leaving 1,008 dynamically indexed positions. The contiguous fixed portions let its Hybrid Sparse Attention kernel overlap window and scattered sparse branches and reduce backward `scatter_add` write conflicts; the indexer need not score those fixed positions.[^longcat-lsa-2026]

The source reports that sink plus window captured an average 83.1% of attention mass in its 69B model analysis. This is an empirical, model-and-workload-specific rationale for its approximately half-fixed budget, not a guarantee that a fixed window is suitable for every model or workload.[^longcat-lsa-2026]

## Cross-layer indexing

LSA groups consecutive layers. The first owner layer runs the indexer; reuse layers consume its selected set. Rather than naively sharing selections, the owner indexer is trained against the distillation losses for every layer in its group. The reported default $N=2$ halves indexing passes; an ablation says $N=4$ harmed 128K retrieval even with a doubled top-k budget, while $N=2$ remained comparable to the cited baselines.[^longcat-lsa-2026]

The same approach is applied to a three-step multi-token-prediction module: its first draft step supplies an index shared by all three steps, trained with their joint distillation target. The reported mean acceptance length was 3.11 versus 3.15 for dense MLA on four listed tasks.[^longcat-lsa-2026]

## Hierarchical indexing

Hierarchical Indexing (HI) is an inference-only approximation. It first ranks pages from mean-pooled sub-block key representations, then applies token-level scoring only within the selected pages. With page size $P$, candidate-page count $M$, and the source's selection-cost accounting, its two top-k stages cost $O(L/P + MP)$ per query rather than a flat $O(L)$ selection over $L$ tokens.[^longcat-lsa-2026]

The selected reported configuration uses $P=128$, mean-pooling sub-block size $B=8$, and $M=1024$ recalled pages (128K candidate tokens), disables HI in the first four indexers, and enables it at contexts of at least 256K. HI needs no retraining, but coarse recall can exclude tokens that the fine stage cannot restore.[^longcat-lsa-2026]

## Relationships

- **Extends:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) with memory-locality, depth-reuse, and coarse-to-fine index-selection mechanisms.[^longcat-lsa-2026]
- **Specializes:** [Multi-head Latent Attention](multi-head-latent-attention.md) by retaining MLA entries but selecting a sparse subset for core attention.[^longcat-lsa-2026]
- **Implemented by:** [LongCat-Flash-Lite-Sparse attention architecture](longcat-flash-lite-sparse-attention-architecture.md).
- **Underpins:** [LongCat-2.0 sparse-attention and embedding architecture](longcat-2-0-sparse-attention-and-embedding-architecture.md), according to the report; its model-level details remain card-bounded.[^longcat-lsa-2026]
- **Evaluated by:** [LongCat Sparse Attention systems trade-offs and evidence](longcat-sparse-attention-systems-trade-offs-and-evidence.md).

## Evidence limits

Mechanism, measurements, and ablations are from a Meituan LongCat Team technical report. The source includes its central figure PDFs, which were inspected; it does not provide model code, kernel code, data, configurations sufficient for reproduction, or independent evaluation. Reported hardware results therefore establish author-measured behavior under the stated setups, not portable serving or training guarantees.[^longcat-lsa-2026]

[^longcat-lsa-2026]: Wen Zan et al., “LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing,” 2026, [source](../raw/2608.01662_LongCatSparseAttention/longcat.tex), Sections 1–4 and 6; inspected [framework](../raw/2608.01662_LongCatSparseAttention/figs/fig_framework.pdf), [streaming-mass](../raw/2608.01662_LongCatSparseAttention/figs/fig_streaming_mass.pdf), and CLI-ablation figures.
