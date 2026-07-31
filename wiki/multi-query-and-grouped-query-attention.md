---
type: Concept
title: Multi-query and grouped-query attention
description: MQA shares one key/value head across many query heads to reduce autoregressive decode KV-cache traffic, while GQA uses an intermediate number of KV heads to trade some of that efficiency for representational capacity.
tags: [attention, multi-query-attention, grouped-query-attention, kv-cache, decoding, inference]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:44:26+07:00 }
sources:
  - id: mqa-summary
    resource: ../raw/MQA.md
    title: "MQA overview (Vietnamese summary)"
---

# Multi-query and grouped-query attention

Multi-query attention (MQA) retains multiple query heads but shares a single key head and value head among them. It therefore reduces the stored and repeatedly read KV cache during token-by-token decoding by roughly the number of query heads relative to multi-head attention (MHA), while constraining heads to use shared key and value representations. Grouped-query attention (GQA) generalizes the trade-off by using an intermediate number of KV heads.[^mqa-summary]

## Head layout

For $H_Q$ query heads, conventional MHA uses $H_{KV}=H_Q$ key and value heads. MQA instead uses:

$$
H_Q=H,\qquad H_K=H_V=H_{KV}=1.
$$

Each query head retains its own query projection, so heads can produce different attention distributions over the shared keys. But they retrieve from the same value vectors and compare against the same key representation, reducing the independent key/value subspaces available under MHA.[^mqa-summary]

GQA chooses $1 < H_{KV} < H_Q$ and assigns groups of query heads to shared KV heads. Thus MHA and MQA are the endpoints of the same head-count choice: $H_{KV}=H_Q$ for MHA and $H_{KV}=1$ for MQA.[^mqa-summary]

## Decode memory and performance boundary

For batch $B$, layers $L$, cached sequence length $S$, KV-head width $d_h$, and element width $p$ bytes, the K/V-cache storage is approximately:

$$
2BLSH_{KV}d_hp.
$$

Consequently, MQA reduces idealized K/V tensor storage—and the K/V data read per decode step—by a factor of $H_Q$ versus MHA, excluding allocation overhead, padding, metadata, and temporary buffers. The source identifies this memory-bandwidth reduction as MQA’s primary benefit during autoregressive decoding: each new-token query must read the growing cache, whereas prompt prefill can use more compute-efficient matrix operations.[^mqa-summary]

MQA also reduces K/V projections and their parameters, but does not eliminate the per-query-head attention-score work. It should therefore not be interpreted as a universal $H_Q$-fold latency improvement: hardware, batch size, context length, kernel support, and other serving bottlenecks determine observed speedup. The source reports a TPUv2 experiment where decoder incremental latency fell from 46 to 3.8 microseconds per token, a configuration-specific result.[^mqa-summary]

## Quality trade-off

Sharing K/V limits each head’s ability to learn independent key and value representations. In the source’s reported WMT14 English–German experiment, MQA had broadly comparable BLEU to MHA; its Billion Word result had slightly worse development perplexity. Those results support a small degradation in those tested configurations, not an assurance of equivalent quality for all models or tasks.[^mqa-summary]

The summary presents GQA as a practical compromise that can approach MHA quality with much of MQA’s decode efficiency. It attributes to the cited GQA work an MHA-to-MQA/GQA checkpoint conversion procedure using approximately 5% of original pretraining compute in that work’s setting; this is a reported, setup-dependent training result.[^mqa-summary]

## Relationships

- **Modifies:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) by sharing K/V projections across query heads rather than giving each head separate projections.[^mqa-summary]
- **Addresses:** the KV-cache-read bottleneck described in [FlashAttention implementation evolution](flashattention-implementation-evolution.md) for one-token decoding; it is an architectural cache-layout trade-off rather than an exact-attention kernel optimization.[^mqa-summary]

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 1–14. This is secondary-source evidence citing Shazeer, “Fast Transformer Decoding: One Write-Head is All You Need” (2019), Vaswani et al. (2017), and Ainslie et al., “GQA” (2023); those primary papers have not been independently ingested here.
