---
type: Concept
title: Qwen Sparse Attention
description: Qwen Sparse Attention ranks fixed-size micro-blocks with a lightweight MQA indexer, then applies causal GQA only to tokens in the selected blocks.
tags: [attention, sparse-attention, qwen, long-context, grouped-query-attention]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-26T15:18:15Z }
sources:
  - id: qwen38-next-card
    resource: ../raw/Qwen3.8-Flash-Next/README.md
    title: Qwen3.8-Flash-Next model card
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next checkpoint configuration
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: Qwen4-Exp Transformers modeling implementation
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
  - id: qwen38-next-attention-figure
    resource: ../raw/Qwen3.8-Flash-Next/Attention.png
    title: Qwen Sparse Attention diagram
---

# Qwen Sparse Attention

Qwen Sparse Attention (QSA) uses a separate low-width indexer to score contiguous micro-blocks, expands the selected blocks back to token indices, and restricts the main causal grouped-query attention (GQA) to those tokens. In Qwen3.8-Flash-Next, each four-token block is represented by the mean of its index keys; the indexer selects at most 512 complete blocks, corresponding to a 2,048-token budget, while retaining the visible incomplete tail.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Indexing and attention path

The released implementation projects each hidden state to four 128-dimensional query heads and one shared 128-dimensional key head. It RMS-normalizes both paths, applies the model's partial RoPE, averages raw keys within each complete four-token block, and scores each block by summing ReLU-clipped query–block-key dot products across the four query heads. Top-ranked blocks are expanded to all constituent tokens and overlaid on the ordinary causal mask.[^qwen38-next-modeling]

The main attention path is distinct from the indexer: it uses 24 query heads and two KV heads of width 256, Q/K normalization, 64 rotary dimensions, and a learned sigmoid output gate. The supplied diagram makes this separation explicit: a compressed lightweight indexer produces top-k block indices for sparse core attention, while the main attention has separate Q/K/V projections and a sigmoid-gated output.[^qwen38-next-attention-figure] Thus the indexer reduces the set read by the expensive attention operation, but the implementation still caches per-token main-attention K/V and indexer keys for QSA layers.[^qwen38-next-config][^qwen38-next-modeling]

## Complexity and systems boundary

For context length $N$, block size $r=4$, and selected-block count $K\le512$, the disclosed design scores roughly $N/r$ pooled keys per query and performs main attention over at most $Kr=2{,}048$ selected complete-block tokens, plus a tail shorter than $r$. This reduces the main-attention work relative to dense attention, but does not make indexing free or bound the QSA cache independently of context.[^qwen38-next-modeling]

The release blog reports that an optimized QSA attention kernel reaches up to 7.6× prefill and 4.9× decode speedups at one million tokens. It also reports 8.6× Qwen3.7-Plus prefill throughput at that context under an online-serving setup with a 90% prefix-cache hit rate. These are vendor measurements with a favorable cache-reuse assumption, not results reproduced by the supplied reference code.[^qwen38-next-blog]

The supplied Python implementation loops over batches and query positions to construct the selection mask and declares no FlashAttention or FlexAttention support for the text model. It is therefore a semantic reference path, not evidence of those optimized long-context gains; production efficiency depends on specialized serving kernels.[^qwen38-next-blog][^qwen38-next-modeling]

## Relationships

- **Used by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md) every fourth language layer.
- **Contrasts with:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md), whose disclosed indexer selects individual token-level MLA entries rather than fixed four-token blocks.
- **Related to:** [LongCat Sparse Attention](longcat-sparse-attention.md), another sparse long-context design with different streaming, cross-layer, and hierarchical selection rules.

## Evidence limits

The model card, blog, diagram, and reference code establish the selection concept and checkpoint dimensions. The separately supplied technical report was not part of this two-source ingest, and the blog provides no kernel configuration, hardware, absolute latency, or dense-attention quality ablation sufficient to reproduce or independently attribute its speed claims.[^qwen38-next-blog][^qwen38-next-modeling]

[^qwen38-next-card]: Qwen Team, “Qwen3.8-Flash-Next,” [model card](../raw/Qwen3.8-Flash-Next/README.md), Highlights and Model Overview.

[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [config](../raw/Qwen3.8-Flash-Next/config.json), `text_config`.

[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), `Qwen4ExpTextQSAIndexer` and `Qwen4ExpTextAttention`.

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), Attention section.

[^qwen38-next-attention-figure]: Qwen Team, “Qwen Sparse Attention,” [included diagram](../raw/Qwen3.8-Flash-Next/Attention.png).
