---
type: Concept
title: Multi-query and grouped-query attention
description: MQA shares one key/value head across many query heads to reduce autoregressive decode KV-cache traffic, while GQA uses an intermediate number of KV heads to trade some of that efficiency for representational capacity.
tags: [attention, multi-query-attention, grouped-query-attention, kv-cache, decoding, inference]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:08:42Z }
sources:
  - id: mqa-summary
    resource: ../raw/MQA.md
    title: "MQA overview (Vietnamese summary)"
  - id: gqa-summary
    resource: ../raw/GQA.md
    title: "GQA overview (Vietnamese summary)"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
---

# Multi-query and grouped-query attention

Multi-query attention (MQA) retains multiple query heads but shares a single key head and value head among them. It therefore reduces the stored and repeatedly read KV cache during token-by-token decoding by roughly the number of query heads relative to multi-head attention (MHA), while constraining heads to use shared key and value representations. Grouped-query attention (GQA) generalizes the trade-off by using an intermediate number of KV heads.[^mqa-summary]

## Head layout

For $H_Q$ query heads, conventional MHA uses $H_{KV}=H_Q$ key and value heads. MQA instead uses:

$$
H_Q=H,\qquad H_K=H_V=H_{KV}=1.
$$

Each query head retains its own query projection, so heads can produce different attention distributions over the shared keys. But they retrieve from the same value vectors and compare against the same key representation, reducing the independent key/value subspaces available under MHA.[^mqa-summary]

GQA chooses $1 < H_{KV} < H_Q$ and assigns groups of query heads to shared KV heads. If $R=H_Q/H_{KV}$, query head $i$ uses KV head $\lfloor i/R\rfloor$; its query projection and attention distribution remain distinct from the other query heads in that group. Thus MHA and MQA are the endpoints of the same head-count choice: $H_{KV}=H_Q$ for MHA and $H_{KV}=1$ for MQA.[^gqa-summary]

## Decode memory and performance boundary

For batch $B$, layers $L$, cached sequence length $S$, KV-head width $d_h$, and element width $p$ bytes, the K/V-cache storage is approximately:

$$
2BLSH_{KV}d_hp.
$$

Consequently, MQA reduces idealized K/V tensor storage—and the K/V data read per decode step—by a factor of $H_Q$ versus MHA, excluding allocation overhead, padding, metadata, and temporary buffers. The source identifies this memory-bandwidth reduction as MQA’s primary benefit during autoregressive decoding: each new-token query must read the growing cache, whereas prompt prefill can use more compute-efficient matrix operations.[^mqa-summary]

MQA also reduces K/V projections and their parameters, but does not eliminate the per-query-head attention-score work. It should therefore not be interpreted as a universal $H_Q$-fold latency improvement: hardware, batch size, context length, kernel support, and other serving bottlenecks determine observed speedup. The source reports a TPUv2 experiment where decoder incremental latency fell from 46 to 3.8 microseconds per token, a configuration-specific result.[^mqa-summary]

In the reported T5-XXL setup, uptrained GQA with eight KV heads scored 47.1 versus 47.2 for MHA-XXL and 46.6 for MQA-XXL, with reported inference times of 0.28, 1.51, and 0.24 seconds respectively. This makes the roughly $5.4\times$ GQA-versus-MHA speedup specific to that TPUv4 benchmark and its parallelization, rather than a general performance guarantee.[^gqa-summary]

## Quality trade-off

Sharing K/V limits each head’s ability to learn independent key and value representations. In the source’s reported WMT14 English–German experiment, MQA had broadly comparable BLEU to MHA; its Billion Word result had slightly worse development perplexity. Those results support a small degradation in those tested configurations, not an assurance of equivalent quality for all models or tasks.[^mqa-summary]

The reported GQA-8 result supports GQA as a practical compromise that can approach MHA quality with much of MQA’s decode efficiency, but does not establish equivalent quality for every model, task, context length, or KV-head count. The source also describes an MHA-checkpoint conversion followed by limited continued pretraining; see [GQA checkpoint conversion and uptraining](gqa-checkpoint-conversion-and-uptraining.md).[^gqa-summary]

## DeepSeek-V2 comparison

In the DeepSeek-V2 authors’ matched 7B dense ablation, MHA led GQA with eight groups and MQA on BBH, MMLU, C-Eval, and CMMLU. This is a model-specific result that supports a quality–cache trade-off; it neither overrides the T5 uptraining evidence summarized above nor establishes a universal ranking. The same report proposes MLA as a different low-rank route to smaller cache state.[^deepseek-v2-2024]

## Relationships

- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md), which caches a joint low-rank KV latent plus a rotary key rather than sharing whole K/V heads.[^deepseek-v2-2024]
- **Modifies:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) by sharing K/V projections across query heads rather than giving each head separate projections.[^mqa-summary]
- **Addresses:** the KV-cache-read bottleneck described in [FlashAttention implementation evolution](flashattention-implementation-evolution.md) for one-token decoding; it is an architectural cache-layout trade-off rather than an exact-attention kernel optimization.[^mqa-summary]
- **Adapted by:** [GQA checkpoint conversion and uptraining](gqa-checkpoint-conversion-and-uptraining.md), which averages MHA K/V projections within each target group and continues pretraining.[^gqa-summary]

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 1–14. This is secondary-source evidence citing Shazeer, “Fast Transformer Decoding: One Write-Head is All You Need” (2019), Vaswani et al. (2017), and Ainslie et al., “GQA” (2023); those primary papers have not been independently ingested here.

[^gqa-summary]: “GQA overview” (Vietnamese summary), [raw source](../raw/GQA.md), Sections 3–18. This is secondary-source evidence summarizing Ainslie et al., “GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints” (2023); the primary paper has not been independently ingested here.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and Appendix C.
