---
type: Concept
title: KV caching
description: KV caching stores each token's computed key and value vectors during autoregressive generation so every decode step computes only the newest token's projections, trading away O(n²) redundant work for cache memory that grows with context length.
tags: [kv-cache, inference, decoding, prefill, ttft, attention, llm-serving]
status: draft
created: 2026-08-10
generated: { by: llm-wiki-agent/1, at: 2026-08-10T13:54:53Z }
sources:
  - id: kv-caching-explained
    resource: ../raw/KVCachinginLLMsClearlyExplained.md
    title: "KV Caching in LLMs, Clearly Explained"
---

# KV caching

KV caching is the serving-side mechanism that makes token-by-token generation fast: a decoder stores each token's key and value vectors after computing them once, so each subsequent step computes projections only for the newest token and runs attention against the full cached history. Without it, every step would recompute identical K/V vectors for all prior tokens, wasting $O(n)$ work per step and $O(n^2)$ over a generation. The source reports that this makes LLM inference roughly $5\times$ faster in practice, at the cost of GPU memory that grows with context length and concurrency.[^kv-caching-explained]

## Why recomputation is redundant

A causal transformer processes all input tokens and produces a hidden state per token; these are projected into vocabulary space as logits. Only the logits from the last token matter for choosing the next token: the model samples from them, appends the chosen token to the input, and repeats. To produce that next token, only the hidden state of the most recent token is needed; every earlier hidden state is an intermediate byproduct of the forward pass.[^kv-caching-explained]

Inside each layer, every token has a query (Q), key (K), and value (V) vector, and attention multiplies queries against keys for scores, then weights the values. The last token's row of $QK^T$ uses its own query against all key vectors in the sequence, and its attention output uses the same query against all key and value vectors. So even though only the final token's hidden state is ultimately needed, every attention layer requires that token's Q and the K/V of everything before it.[^kv-caching-explained]

The redundancy follows directly: generating token 50 needs the K/V of tokens 1–50, and generating token 51 needs the K/V of tokens 1–51. The K/V vectors of tokens 1–49 were already computed in the previous step, with the same inputs and therefore the same outputs, yet a naive loop recomputes them from scratch every step. That is $O(n)$ redundant work per step, hence $O(n^2)$ wasted compute over an entire generation.[^kv-caching-explained]

## The mechanism

Instead of recomputing all K/V at every step, store them:

1. Compute Q, K, and V for only the newest token.
2. Append the new K and V to the cache.
3. Retrieve all previous K/V from the cache.
4. Run attention using the new Q against the full cached K and V.

Each step adds exactly one new K and one new V per layer; everything else comes from memory. The expensive K/V projections therefore happen once per token rather than once per step. Attention itself still scales with sequence length, because every new query attends over all cached keys and values.[^kv-caching-explained]

## Prefill and time-to-first-token

The first token is slow because of the prefill phase: the model processes the entire prompt in one forward pass, computing and caching K/V vectors for every token. This is the most compute-intensive part of the request. Once the cache is warm, each subsequent token needs only a single forward pass with one token, which is fast. The initial delay is called time-to-first-token (TTFT); longer prompts mean longer prefills and longer waits. The source lists chunked prefill, speculative decoding, and prompt caching as distinct TTFT optimizations, while noting the dynamic is always the same: building the cache is expensive, reading from it is cheap.[^kv-caching-explained]

## Memory trade-off

KV caching trades compute for memory. Every layer stores K/V vectors for every token: the source's illustrative Qwen 2.5 72B example (80 layers, 32K context, hidden dim 8192) consumes several gigabytes of GPU memory per request, and at hundreds of concurrent requests the aggregate cache often exceeds the model weights themselves.[^kv-caching-explained]

This pressure motivates architectural K/V sharing: grouped-query attention (GQA) and multi-query attention (MQA) share key/value heads across query heads, cutting cache memory with minimal quality loss. It also explains why doubling context length is hard: doubling the window doubles the KV cache per request and reduces how many concurrent users fit in memory.[^kv-caching-explained]

The source reports roughly $5\times$ faster inference in practice and states that every mainstream LLM serving stack (vLLM, TGI, TensorRT-LLM) builds on the idea.[^kv-caching-explained]

## Relationships

- **Motivates:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md), which shrinks the per-token cache produced by this mechanism through retention, quantization, or lossy aggregation.[^kv-caching-explained]
- **Motivates:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md) and [Multi-head Latent Attention](multi-head-latent-attention.md), which reduce cache memory by sharing K/V heads or caching a low-rank latent instead.[^kv-caching-explained]
- **Managed by:** [PagedAttention KV-cache serving](pagedattention-kv-cache-serving.md), which maps the growing logical cache to non-contiguous physical blocks for serving.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which replaces the growing, token-addressable KV cache with a fixed-size state instead of caching exact K/V.
- **Contextualizes:** [FlashAttention implementation evolution](flashattention-implementation-evolution.md), whose kernels fit compute-heavy prefill while one-token decode is bounded by KV-cache reads.
- **Preserves the scaling described by:** [Self-attention computational profile](self-attention-computational-profile.md): decode attention still attends over the full cached history each step.

## Evidence limits

This concept is compiled from a single self-contained explainer. The raw file records no author, publication date, or URL, so the source identity is the file itself. The "$5\times$ speedup," the Qwen 2.5 72B memory figures, and the claim that cache often exceeds model weights at high concurrency are source-reported illustrations rather than independently measured results; the underlying serving stacks (vLLM, TGI, TensorRT-LLM) have not been independently ingested here.

[^kv-caching-explained]: “KV Caching in LLMs, Clearly Explained,” [raw source](../raw/KVCachinginLLMsClearlyExplained.md), Parts 1–6 and tl;dr. The article itself is secondary orientation material and does not cite primary papers for the stated speedup or memory figures.
