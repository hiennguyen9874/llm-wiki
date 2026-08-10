---
type: Concept
title: FlashAttention implementation evolution
description: FlashAttention-2 and -3 retain tiled exact attention while improving GPU work partitioning and, on Hopper, asynchronous low-precision execution; benefits are greatest for long-prompt prefill rather than one-token decode.
tags: [flashattention, gpu-kernels, prefill, decoding, kv-cache, hopper]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:35:10Z }
sources:
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
  - id: flashattention-2-summary
    resource: ../raw/FlashAttention-2.md
    title: "FlashAttention-2 overview (Vietnamese summary)"
---

# FlashAttention implementation evolution

FlashAttention-2 and FlashAttention-3 retain tiled, exact softmax attention while targeting progressively better hardware utilization: FlashAttention-2 changes work partitioning and sequence parallelism, and FlashAttention-3 targets NVIDIA Hopper with asynchronous, warp-specialized execution and low-precision support. These kernels most directly benefit long-sequence training and prompt prefill; one-token autoregressive decode is often constrained instead by KV-cache reads.[^flashattention-summary]

## Kernel evolution

FlashAttention fuses score computation, scaling, masking, softmax, dropout, and value aggregation so intermediate tensors mostly remain in registers or shared memory rather than making separate HBM round trips.[^flashattention-summary]

FlashAttention-2 shifts more of the main loop toward Tensor-Core matrix multiplies by maintaining an unnormalized output accumulator and deferring division by the softmax normalizer until all key/value tiles have been processed. It also skips causal tiles wholly outside the allowed triangle, reducing masked work.[^flashattention-2-summary]

Rather than making concurrency depend mainly on batch and head count, FlashAttention-2 assigns separate query-row tiles within each head to thread blocks. For a query length $N$ and query-tile height $B_r$, this creates roughly $B\,H\,\lceil N/B_r\rceil$ blocks, which can improve occupancy for long sequences with small batches.[^flashattention-2-summary]

Within a thread block, its split-Q partition gives each warp independent query rows while sharing the key/value tile. This avoids the inter-warp reduction, shared-memory traffic, and synchronization associated with a split-K arrangement in which warps produce partial results for the same query rows.[^flashattention-2-summary]

The source reports approximately $2\times$ kernel speedup over the first version in tested configurations, 50–73% of theoretical A100 peak FLOPs/s, and up to 225 TFLOPs/s per A100 in a reported end-to-end GPT-style training configuration. These are configuration-specific benchmark results, not device-independent guarantees.[^flashattention-2-summary]

FlashAttention-3 is described as a Hopper-oriented redesign using warp specialization, asynchronous transfer/compute pipelining, interleaving GEMM with softmax work, and FP8 support with block quantization and error-reduction techniques. The source reports roughly $1.5$–$2\times$ speedup over FlashAttention-2 on tested H100 configurations; this is a benchmark result, not a device-independent guarantee.[^flashattention-summary]

## Operational boundary

During training, reduced attention activations can enable longer sequences or larger batches, but total memory remains affected by model weights, other activations, gradients, optimizer state, and hardware-specific kernels.[^flashattention-summary]

During inference prefill, many prompt tokens attend together, making FlashAttention especially applicable. In token-by-token decode, the query length is usually one and reading the accumulated KV cache can dominate; paged KV caches, multi- or grouped-query attention, KV-cache quantization, and continuous batching address distinct serving bottlenecks.[^flashattention-summary]

FlashAttention makes full attention more efficient but does not remove its $O(N^2)$ sequence-length arithmetic. Very long contexts may still require restricted or sparse attention, chunking, distributed sequence techniques, retrieval, or architectures with different attention/state trade-offs.[^flashattention-summary]

## Relationships

- **Contextualized by:** [KV caching](kv-caching.md), which explains why prefill is compute-heavy and one-token decode is bounded by KV-cache reads.[^flashattention-summary]
- **Extends:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md) with hardware-aware scheduling and data-movement refinements.[^flashattention-summary]
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which changes the retrieval formulation and state-growth behavior rather than optimizing exact full-attention kernels.[^flashattention-summary]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces KV-cache traffic in one-token decoding by sharing K/V heads rather than changing the exact-attention kernel.[^mqa-summary]

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 11–16 and 18. It cites Dao et al.'s FlashAttention (2022), FlashAttention-2 (2023), FlashAttention-3 (2024), and the official implementation repository; none has been independently ingested here.

[^flashattention-2-summary]: “FlashAttention-2 overview” (Vietnamese summary), [raw source](../raw/FlashAttention-2.md), Sections 3–11. This secondary source cites Dao, “FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning” (2023/ICLR 2024); the primary paper has not been independently ingested here.

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 3–7 and 13. This is secondary-source evidence; its cited primary MQA and GQA papers have not been independently ingested here.
