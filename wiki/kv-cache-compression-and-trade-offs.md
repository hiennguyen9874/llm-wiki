---
type: Concept
title: KV-cache compression and trade-offs
description: KV-cache compression reduces decode-state memory through token retention, lower-precision representation, or lossy aggregation, with quality, bandwidth, and kernel overhead determining whether a smaller cache improves serving.
tags: [kv-cache, compression, quantization, inference, decoding, llm-serving]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: kv-cache-compression-summary
    resource: ../raw/KVCacheCompressionOptimization.md
    title: "KV Cache Compression & Optimization"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# KV-cache compression and trade-offs

A decoder’s KV cache avoids recomputing prior keys and values, but its storage grows linearly with cached tokens and active batch size. Compression either retains fewer token KV pairs, stores them at lower precision, or replaces them with lossy aggregates; a useful deployment choice must preserve task quality while reducing memory traffic enough to repay selection, conversion, and kernel costs.[^kv-cache-compression-summary]

## Memory pressure

For $L$ layers, batch size $B$, cached length $S$, $H_{KV}$ KV heads of width $d_h$, and $p$ bytes per value, KV storage is approximately:

$$
M_{KV}=2LBSH_{KV}d_hp.
$$

The factor two is for keys and values. Thus cache bytes grow linearly with context length and batch size, not exponentially; weights, temporary activations, allocator overhead, and concurrent requests add to the practical memory requirement.[^kv-cache-compression-summary]

## Compression mechanisms

### Retention and eviction

Token-selection methods retain a bounded subset of KV pairs. A simple policy keeps a recent sliding window; sink-token policies also retain selected prompt-initial tokens. Attention-informed policies retain tokens with high accumulated attention (heavy hitters) or select prompt tokens from an observation window near the end of prefill. Per-head or per-layer budgets can reserve more capacity for heads whose attention retrieves distant context.[^kv-cache-compression-summary]

These policies can bound memory more strongly than numeric compression, but permanent eviction cannot recover a token that becomes relevant later. A retained recent window and retrieval-sensitive head budgets are therefore quality safeguards rather than guarantees, especially for long-context retrieval and code workloads.[^kv-cache-compression-summary]

### Lower-precision and aggregate representations

Quantization retains all token positions while encoding K/V elements with fewer bits, commonly with scales and zero points. Its ideal storage reduction is roughly proportional to the FP16-to-target bit-width ratio, but metadata, alignment, residual high-precision blocks, dequantization, and packing reduce the realized saving. Key quantization can be more quality-sensitive than value quantization because key error perturbs attention logits before softmax; this motivates asymmetric K/V precision or grouping.[^kv-cache-compression-summary]

Merging similar token KV pairs, low-rank approximations, and sparse coding instead replace multiple values or a dense representation with a smaller lossy representation. They may retain more information than hard eviction, but introduce grouping, projection, reconstruction, or specialized-kernel work; position-dependent representations can further complicate token merging.[^kv-cache-compression-summary]

Multi-head Latent Attention is an architectural low-rank alternative: it caches a joint KV latent and a small decoupled rotary key rather than independently materialized K/V heads. In DeepSeek-V2’s controlled ablations, this reduced cache elements substantially relative to MHA while retaining token-addressable softmax attention; it is still model- and dimension-specific, and cache state grows with token count.[^deepseek-v2-2024]

## Compressed attention state in DeepSeek-V4

DeepSeek-V4 supplies primary evidence for an architectural aggregation variant: CSA and HCA replace groups of token KV entries with learned compressed entries, but retain a sliding-window cache and uncompressed tail state until a compression block completes. Its serving layout separates this fixed-size per-request state from compressed cache blocks, and can store completed compressed-prefix entries on disk; restoring a prefix still requires handling the incomplete tail and optionally reconstructing sliding-window state. This is a V4-specific lossy attention design, not ordinary post-hoc cache quantization.[^deepseek-v4-2026]

## Deployment boundary

A smaller cache does not by itself make decoding faster. Quantization, sparse selection, irregular gathers, metadata access, decompression, and CPU–GPU migration can lower kernel efficiency or add latency. Evaluate memory reduction alongside prefill latency, time to first token, time per output token, throughput/goodput under a latency objective, and long-context task quality—not only the nominal compression ratio.[^kv-cache-compression-summary]

Compression is complementary to architectural and serving-layout choices. Multi-query and grouped-query attention reduce the number of KV heads produced by the model, while PagedAttention reduces allocation waste and enables sharing without making an individual token representation smaller. In practice, the source recommends composing such compatible mechanisms conservatively, with irreversible eviction applied only after measuring the target workload.[^kv-cache-compression-summary]

## Relationships

- **Builds on:** [KV caching](kv-caching.md), whose per-token cache this page compresses rather than replaces.[^kv-cache-compression-summary]
- **Complements:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which reduces KV-head count rather than compressing an already-produced cache.[^kv-cache-compression-summary]
- **Complements:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md), which improves cache allocation, prefix reuse, and batching rather than reducing the per-token KV representation.[^kv-cache-compression-summary]
- **Implemented architecturally by:** [Multi-head Latent Attention](multi-head-latent-attention.md), which stores a jointly compressed KV latent rather than sharing or evicting conventional K/V heads.[^deepseek-v2-2024]
- **Addresses:** the decode-time KV-read bottleneck identified in [FlashAttention implementation evolution](flashattention-implementation-evolution.md).[^kv-cache-compression-summary]
- **Specialized by:** [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md), which makes learned aggregation part of V4 attention layers.[^deepseek-v4-2026]
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which replaces token-addressable softmax KV storage with a fixed-size state instead of compressing it.[^kv-cache-compression-summary]

## Evidence limits

This concept is compiled from a Vietnamese secondary summary that links two KV-cache surveys; neither linked survey nor the named method papers has been independently ingested. The taxonomy and implementation cautions are useful orientation, but method-specific quality and speed claims require primary-source and target-system validation.

[^kv-cache-compression-summary]: “KV Cache Compression & Optimization,” [raw source](../raw/KVCacheCompressionOptimization.md), Sections 1–14. The source frames its synthesis around Liu et al., “KV Cache Compression for Inference Efficiency in LLMs: A Review” (2025), and “A Survey on Large Language Model Acceleration based on KV Cache Management” (2024/2025); those linked sources have not been independently inspected here.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.1 and Appendix D.

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Sections 2.3 and 4.5–4.6.
