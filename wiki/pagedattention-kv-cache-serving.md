---
type: Concept
title: PagedAttention KV-cache serving
description: PagedAttention maps a sequence's logical KV-cache blocks to non-contiguous physical blocks, enabling demand allocation and block sharing for high-throughput autoregressive LLM serving.
tags: [pagedattention, vllm, kv-cache, llm-serving, decoding, continuous-batching]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-10T14:50:04Z }
sources:
  - id: pagedattention-2023
    resource: ../raw/arXiv-2309.06180v1/main.tex
    title: "Efficient Memory Management for Large Language Model Serving with PagedAttention"
  - id: flashinfer-2025
    resource: ../raw/arXiv-2501.01005v2/main.tex
    title: "FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving"
---

# PagedAttention KV-cache serving

PagedAttention stores an autoregressive sequence's growing key/value (KV) cache as fixed-size logical blocks, whose block-table entries can point to arbitrary physical GPU blocks. Its attention kernel reads the mapped blocks while retaining the usual causal-attention result. vLLM uses this indirection to allocate cache only as a request grows, share complete prefix blocks, and avoid requiring a contiguous per-request allocation.[^pagedattention-2023]

## Block-mapped cache

For a block size $B$, each logical block holds the K/V vectors for $B$ consecutive token positions. A block engine divides a reserved GPU-memory region into same-sized physical blocks, while each request's block table maps its ordered logical blocks to those physical blocks and records how much of its final block is filled. The kernel visits the mapped K/V blocks separately when computing attention; thus logical continuity does not require physical contiguity.[^pagedattention-2023]

Unlike a contiguous allocation sized to a request's maximum possible length, vLLM allocates a physical block only when a new logical block is needed. A request can waste only the unused positions in its final block, while fixed-size physical blocks avoid the variable-size external fragmentation described for the paper's baselines.[^pagedattention-2023]

## Sharing and recovery

Multiple sequences may map their common prefix blocks to the same physical blocks. Physical blocks carry reference counts. If a sequence needs to append into a shared, partly filled block, vLLM makes a block-granularity copy before writing (copy-on-write); complete shared blocks need not be copied. The paper applies this to parallel sampling, beam search, and provider-managed shared prefixes.[^pagedattention-2023]

Under memory pressure, the paper's vLLM design gang-preempts all sequences in a request's sequence group. It either swaps their blocks to CPU memory or later recomputes the cache by treating the prior generated sequence as prompt input. This all-or-nothing policy follows from decode attention requiring a sequence's complete cache; which recovery method is preferable depends on block size, data-transfer bandwidth, and GPU compute.[^pagedattention-2023]

## Serving boundary

PagedAttention changes cache layout and the serving kernel, not the model's causal-attention semantics. It does not make decode attention constant-time: each new query still reads and attends over the cached history. Its benefit is more effective cache capacity, sharing, and request concurrency; a specialized kernel must pay for block-table indirection and non-contiguous accesses.[^pagedattention-2023]

The paper's evaluation and its author-implemented baselines are summarized in [PagedAttention evaluation and serving trade-offs](pagedattention-evaluation-and-serving-trade-offs.md). Those historical measurements do not establish performance for later vLLM releases, models, hardware, or workloads.[^pagedattention-2023]

## Relationships

- **Manages the decode cache of:** [KV caching](kv-caching.md), mapping its growing logical K/V sequence to non-contiguous physical blocks.[^pagedattention-2023]
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) with a block-addressed cache representation.[^pagedattention-2023]
- **Complemented by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces KV-head count and hence cache bytes, whereas PagedAttention reduces allocation waste and permits sharing.[^pagedattention-2023]
- **Contrasts with:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md): PagedAttention manages non-contiguous decode cache, whereas FlashAttention tiles attention computation to reduce intermediate-memory traffic.[^pagedattention-2023]
- **Implemented by:** [FlashInfer attention engine](flashinfer-attention-engine.md), whose BSR abstraction represents page-table cache access alongside other sparse layouts; it is an attention-engine integration, not a replacement for PagedAttention’s allocation and sharing policy.[^flashinfer-2025]
- **Evaluated by:** [PagedAttention evaluation and serving trade-offs](pagedattention-evaluation-and-serving-trade-offs.md).[^pagedattention-2023]

[^pagedattention-2023]: Kwon et al., “Efficient Memory Management for Large Language Model Serving with PagedAttention,” SOSP 2023, [source](../raw/arXiv-2309.06180v1/main.tex), Sections 1–5 and 7–8.

[^flashinfer-2025]: Zihao Ye et al., “FlashInfer: Efficient and Customizable Attention Engine for LLM Inference Serving,” arXiv:2501.01005v2, [bundled LaTeX source](../raw/arXiv-2501.01005v2/main.tex), Sections 1 and 3.1.
