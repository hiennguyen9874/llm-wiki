---
type: Concept
title: DeepSeek-V4.1-Flash Systems
description: Persistent KV management, SWA bounded replay, EPD disaggregation, fused kernels, and distributed training infrastructure for DeepSeek-V4.1-Flash.
tags: [deepseek-v4.1, kv-cache, prefix-caching, disaggregation, kernels, distributed-training]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v41-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: 'DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression'
---

DeepSeek-V4.1-Flash reduces global HBM-resident KV to 890 bytes per token, about 1/4 of DeepSeek-V4-Flash and 1/437 of DeepSeek-V1, and persistent SSD/host KV to about 1/8 of V4-Flash through no-SWA persistence plus 1/4 global compression. Single-token decode FLOPs stay nearly constant from 4K to 1M, rising only about 1/4 over that 256x range[^v41-report].

## Persistent KV management

V4 stores global KV fully with LRU and caches SWA KV at prompt-end and output-end positions; SWA is nearly half of persistent capacity despite storing only `n_win` entries at those points, with a 72-hour SSD retention target. SWA reuse is minute-scale within an active session and dead afterward, mismatching long retention[^v41-report].

V4.1 therefore[^v41-report]:

- Removes SWA KV from persistent cache; keeps global KV with at least 72-hour lifetime.
- Holds SWA KV in a distributed memory pool from 10% of each machine's host DRAM with minute-scale TTL and immediate recycling, sized for concurrent active sessions rather than long history.
- Accepts global-hit plus SWA-miss and recovers via bounded replay over `n_win` tokens instead of exact `L x n_win` replay.

Exact V4 Zero-SWA recomputation over `L x n_win` tokens proved prohibitive in production, motivating the approximate fallback[^v41-report].

## SWA Bounded Replay

Exact reconstruction needs `L x n_win` tokens because SWA dependencies accumulate across layers. Bounded replay replays only the most recent `n_win` tokens and truncates SWA to the replay segment: a query at `i` replaying from `s` attends to SWA keys in `[max(s,i-W+1),i]`[^v41-report].

Encoder replay makes prefix caching depend only on global KV. On a hit it replays the cached prefix's final 128 tokens together with the uncached suffix, regenerating only SWA KV while reusing cached global KV without recomputation or overwrite[^v41-report].

Decoder replay bounds CED prefill. Decoder global KV comes from final encoder states, but decoder SWA needs each decoder layer's own states. Instead of running `L/2` decoder layers over `(L/2) x n_win` prompt tokens when a short suffix follows a long cached prefix, every prefill replays the prompt's final `n_win` tokens through decoder layers under the same truncation and uses the result only for decoding, not caching[^v41-report].

Both forms are approximate and not mathematically identical to full prefill; report experiments find negligible quality impact, with replay also simulated during post-training for adaptation[^v41-report].

## Inference execution

Deployment uses Encoder-Prefill-Decode disaggregation so vision encoding, prefill, and decode scale and overlap independently. Most Reuse-mode layers execute in 15 kernels during prefill and 11 during decode through FlashMLA fused-RoPE-attention-RoPE-cast, Mega-Gate, Mega-mHC, Mega-MoE DeepGEMM, TileKernels, and DeepSelect TopK fusion[^v41-report].

Host memory separates long-lived global KV from short-lived encoder SWA KV, matching the bounded-replay split[^v41-report].

## Multimodal training infrastructure

Contrastive vision pretraining overlaps all-gathers with compute: visual features gather during text forward and text features during text backward, hiding both transfers[^v41-report].

The vision encoder replicates outside the LLM parameter tree with three phases per step — vision forward, LLM forward/backward, vision backward — preserving text-only parallel strategy in the LLM phase. Ultra-long image-dense sequences shard images across CP ranks with load balancing and load each image once; loading stays hidden when per-token raw bytes versus compute satisfy `rho < (B_IO/B_GPU) C`, independent of sequence length and cluster size[^v41-report]. RL rollout transfers images incrementally and caches CPU decode plus preprocessing outputs on distributed storage for reuse[^v41-report].

## CSA2 distributed-training support

Layers sharing main KV, indexer K, or indices may sit on different pipeline stages. Support uses shadow indexers with one logical parameter owner plus consistent lightweight replicas, pipeline payload extensions carrying intermediates and sparse routing over existing P2P paths partitioned with context parallelism, and micro-batch shared-state lifetime management retained through forward, recomputation, and backward then promptly released[^v41-report].

## Engram systems

Tables partition by row across engram-parallel groups trading memory against lookup communication scope, with optimizer states further sharded. Lookup indices depend only on inputs, so prefetch starts for the whole local batch before pipeline microbatches; prefetch and gradient returns overlap vision forward/backward. Embeddings store and fetch in FP8 directly into GEMM; Sinkhorn row/column scaling vectors persist across iterations with fused row-normalize plus partial-column-statistics kernels. During RL rollouts tables stay GPU-resident to reduce host pressure and fragmentation-induced OOMs[^v41-report].

## Relationships

- Uses [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) — CED, CSA2, Engram, and FP4 designs realized by these systems.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — SGLang flags and measurements for encoder/decoder bounded replay and Engram host offload.
- Related to [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — prefix-reuse boundary changed by encoder replay without a window checkpoint.
- Related to [SGLang HiSparse Hierarchical Sparse-Attention Memory](sglang-hisparse.md) — separate HBM-capacity tradeoff from Engram host offload.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — colocated rollout/training counterpart to this report's training infrastructure.
- Related to [DeepSeek-V4.1-Flash Reference Inference Implementation](deepseek-v41-reference-inference.md) — minimal single-process counterpart without disaggregation, prefix cache, or speculative-verify loop.

## Coverage limits

- Figure images were not visually inspected; byte, ratio, kernel-count, and DRAM-percentage claims follow prose.
- Throughput, TTL, and retention numbers are workload-dependent deployment snapshots, not universal guarantees.

[^v41-report]: DeepSeek-V4.1-Flash tech report — `../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md`, Sections 2.5, 3.1-3.2 and Introduction/Figure 1-2 KV and FLOPs claims.
