---
type: Concept
title: DeepSeek-V4.1-Flash Architecture
description: CED encoder-decoder with CSA2 cross-layer KV/index reuse, Single-Pass mHC, Engram memory, DSpark drafting, and FP4 KV for 552B multimodal Flash.
tags: [deepseek-v4.1, ced, sparse-attention, mhc, engram, dspark, quantization, multimodal]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v41-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: 'DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression'
---

DeepSeek-V4.1-Flash is a 552B-backbone plus 196B-Engram multimodal MoE with a 20-layer causal encoder followed by a 20-layer decoder, activating 8B parameters per token during prefill and 16B during decode with up to 1M-token context[^v41-report].

## Causal Encoder-Decoder

For global attention the bottom L/2 layers act as causal encoder; decoder global KV is projected from `H_{L/2}` with layer-dependent `W_l^{KV}` and `W_l^Z` rather than from each decoder hidden state[^v41-report].

SWA stays layer-wise in every layer, so decoder SWA still needs reconstruction. Prefill complexity falls from `O(NL)` to approximately `O(NL/2)` for `N >> n_win`, nearly halving prefill for input-heavy agentic workloads[^v41-report].

## Compressed Sparse Attention 2

CSA2 jointly compresses entry size, sequence dimension, and layer dimension. Relative to DeepSeek-V4 CSA it removes overlapping 2m-source compression entries and absolute positional embeddings, and projects indexer K from main KV instead of a separate hidden-state path[^v41-report].

Each layer computes its own Q and SWA KV; main KV, indexer K, and Top-K indices follow one static mode[^v41-report]:

- **Full:** compute main KV, indexer Q, indexer K, and fresh Top-K.
- **Reindex:** reuse most recent main KV plus indexer K, compute own indexer Q and fresh Top-K.
- **Reuse:** reuse most recent main KV and latest Top-K against it; no indexer scoring.

Configured sizes: first two layers SWA-only; remaining 18 encoder layers use compression `m=2` in three groups of six as 1 Full plus 5 Reuse; 20 decoder layers use `m=1` in five groups of four, first group 1 Full plus 3 Reuse and other four groups 1 Reindex plus 3 Reuse[^v41-report]. Indexer has 32 query heads of dimension 128 with Top-K 512; main attention has 64 query heads of dimension 512, query compression 1280, 8 output-projection groups of dimension 1024, and SWA window 128[^v41-report].

## Hierarchical Sparse Indexer

Decoder-only training-aware restriction for later indexers. The first Full decoder layer scores all visible positions for its own Top-512, scores blocks by maximum position score, and publishes up to 2,048 blocks of 8 positions as a 16,384-position candidate pool[^v41-report].

Later Reindex layers score only that pool and pick their own Top-512; Reuse layers do no scoring. Per-query cost for deeper indexers is therefore bounded for fixed pool size, while the first Full pass remains full-range[^v41-report].

## Single-Pass mHC

With `n=4` residual streams, the original three-kernel mHC needs `(4n+4)d` activation traffic versus a `(2n+2)d` ideal map. Folding norms into projections allows a two-pass `(3n+2)d` form, but input mixing still waits on coefficients from the same block[^v41-report].

Single-Pass mHC consumes the previous block's mixing coefficient `A_{l-1}` instead of `A_l`, removing that dependency. Deployment fuses residual update, input mixing, coefficient prediction, pre-norm, and FP8 conversion into one Mega-mHC kernel attaining `(2n+2)d` traffic, halving the original implementation; pretraining retains the multi-kernel form[^v41-report].

## Engram

Two modules at layers 1 and 14 hold 196B total, each with N-gram orders {2,3,4}, 8 hash heads, 2048 embedding dimensions per order, approximately 16M-entry distinct-prime tables, and FP8 tables plus key/value projections[^v41-report]. Short causal convolution is omitted; embeddings use momentum plus Sinkhorn balancing and deterministic addressing enables background RDMA prefetch with first-module prefetch overlapping the first block[^v41-report].

## DSpark

Three-block sliding-window-128 drafter computes base logits for five draft positions in parallel, with a Markov head for draft dependencies and a confidence head predicting per-position acceptance for survival-aware verification-length scheduling against profiled throughput curves[^v41-report].

Unlike DeepSeek-V3 MTP, DSpark trains separately after backbone pretraining with the backbone frozen, then continues alongside post-training without gradients into the backbone, keeping it aligned for serving and rollout generation[^v41-report].

## FP4 main KV

Main KV uses E2M1 with one E4M3 scale per 16 channels, following NVFP4 but omitting the second-level global scale. Supported magnitude reaches 448x6=2688 versus observed maxima around 10 and a ~22.6 RMS/RoPE bound, so omission causes no measured loss and simplifies layout[^v41-report].

Quantization applies after RoPE with the same format for RoPE and non-RoPE parts; SWA KV stays FP8 due to sensitivity. Training uses QAT in post-training; dequantization before attention preserves cross-hardware compatibility without native support for that format. This nearly halves main-KV storage versus DeepSeek-V4 FP8[^v41-report].

## Multimodal and MoE setup

DeepSeek-ViT has 32 layers, hidden 1024, 16 heads, patch 14, 2D-RoPE, linear patch projection, RMSNorm, SwiGLU, plus 3x3 pixel-unshuffle for 9x token reduction supporting roughly 1344x1344 inputs; a two-layer 5120-dim MLP projects to the language backbone[^v41-report].

Image and text tokens use separate expert-bias sets under auxiliary-loss-free balancing, retaining original scores for weighting and updating biases independently per modality[^v41-report].

All 40 Transformer blocks use DeepSeekMoE with 1 shared plus 384 routed experts of intermediate size 2304, 6 active per token, and clamped SwiGLU at threshold 10[^v41-report].

## Relationships

- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — serving-side companion with shared KV/candidate/selection, Engram host layouts, bounded replay flags, and fusion kernels.
- Related to [DeepSeek-V4.1-Flash Reference Inference Implementation](deepseek-v41-reference-inference.md) — readable TP conversion plus autoregressive runtime implementing this architecture's sparse attention, Engram, DSpark forward, and vision path.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — training-side companion with shared-state parallelism and FP4/FP8 QAT discipline.
- Uses [DeepSeek-V4.1-Flash Systems](deepseek-v41-systems.md) — deployment and distributed-training realization of CED, CSA2, Engram, and FP4 KV.
- Uses [DeepSeek-V4.1-Flash Training and Evaluation](deepseek-v41-training.md) — data, optimizer, and benchmark context for this architecture.
- Related to [DeepSeek-V4 Architecture](deepseek-v4-architecture.md) — predecessor tech-report source for CSA, mHC, and Muon that CSA2 and Single-Pass mHC extend.

## Coverage limits

- Figure images under `raw/DeepSeek_V41_Tech_Report/images/` were not visually inspected; structural claims follow prose, tables, and equations.
- Numerical config values are report snapshots, not independent verification.

[^v41-report]: DeepSeek-V4.1-Flash tech report — `../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md`, Sections 2.1-2.4 plus Figure 3 architecture and Section 4.2.1 model setups.
