---
type: Concept
title: PagedAttention KV-cache serving
description: PagedAttention maps each sequence’s logical KV-cache blocks to non-contiguous GPU blocks, enabling demand allocation, prefix sharing, and dynamic batching without changing exact causal attention.
tags: [pagedattention, vllm, kv-cache, llm-serving, decoding, continuous-batching]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:53:10Z }
sources:
  - id: pagedattention-summary
    resource: ../raw/PagedAttention.md
    title: "PagedAttention and vLLM in LLM serving (Vietnamese summary)"
---

# PagedAttention KV-cache serving

PagedAttention stores a sequence’s growing key/value (KV) cache as fixed-size logical blocks mapped through a block table to arbitrary physical GPU blocks. vLLM can therefore allocate cache on demand rather than reserve one contiguous region per request, share common-prefix blocks between related sequences, and admit or retire requests during decoding. It changes cache management and the serving kernel’s memory access, not the exact causal-attention computation or its context-length scaling.[^pagedattention-summary]

## Block-mapped cache

For $L$ layers, $H_{KV}$ KV heads, head dimension $d_h$, and $s$ bytes per element, the cache needed per token is approximately:

$$
2LH_{KV}d_hs.
$$

The factor two represents keys and values. In conventional multi-head attention, $H_{KV}d_h$ is typically the model width; multi-query and grouped-query attention reduce this quantity by reducing the number of KV heads.[^pagedattention-summary]

PagedAttention groups token positions into fixed-size logical KV blocks, then maps each logical block to any free physical block with a per-sequence block table. An attention kernel follows this indirection while streaming K/V blocks and combining their contributions, so the logical sequence can remain contiguous even when its physical cache is not.[^pagedattention-summary]

Demand allocation avoids reservation for an unknown output length and eliminates the need for a large contiguous region. External fragmentation is consequently avoided at the block level; internal waste is limited to the final partly filled block, at most $B-1$ token positions for block size $B$.[^pagedattention-summary]

## Sharing and scheduling

Multiple sequences with the same prompt may point to the same physical prefix blocks. Physical blocks use reference counts; if one sequence must write a shared incomplete block, copy-on-write allocates and copies a new block before redirecting that sequence. This supports parallel sampling, beam search, and other shared-prefix workloads without duplicating the entire prompt cache.[^pagedattention-summary]

The flexible block pool also supports continuous batching: finished sequences leave a decode batch and newly admitted requests receive available blocks without requiring a contiguous cache allocation. Under memory pressure, a serving system can preempt a sequence by swapping its cache blocks to host memory or discarding them and recomputing the prompt cache later; the preferred choice depends on recomputation cost and interconnect bandwidth.[^pagedattention-summary]

## Performance boundary

PagedAttention does not make one-token decode attention constant time: each new token still attends over the prior context, so K/V reads and attention work grow with context length. Its principal benefit is system throughput—more concurrent sequences, less cache duplication and reservation waste, and more flexible scheduling—rather than a guaranteed latency reduction for an isolated request.[^pagedattention-summary]

The source reports roughly $2$–$4\times$ higher throughput at comparable latency than FasterTransformer and simulated Orca baselines in the 2023 paper’s tested setups. This is historical, configuration-specific evidence, not a performance guarantee for current vLLM or other serving engines.[^pagedattention-summary]

Block tables introduce an extra memory indirection and require specialized paged-attention kernels. Block size trades metadata and allocation overhead against final-block fragmentation, while copy-on-write can require copying a partly filled shared block.[^pagedattention-summary]

## Relationships

- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) unchanged mathematically while changing where cached K/V tensors reside during causal decoding.[^pagedattention-summary]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which lowers cache bytes and reads per token by reducing KV-head count.[^pagedattention-summary]
- **Contrasts with:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md): PagedAttention manages non-contiguous decode cache, whereas FlashAttention tiles attention computation to reduce intermediate HBM traffic.[^pagedattention-summary]
- **Preserves the scaling described by:** [Self-attention computational profile](self-attention-computational-profile.md); it improves cache allocation and serving concurrency rather than replacing full attention with a subquadratic formulation.[^pagedattention-summary]

[^pagedattention-summary]: “PagedAttention and vLLM in LLM serving” (Vietnamese summary), [raw source](../raw/PagedAttention.md), Sections 1–12. It summarizes Kwon et al., “Efficient Memory Management for Large Language Model Serving with PagedAttention” (SOSP 2023) and current vLLM documentation; those external primary sources have not been independently ingested here.
