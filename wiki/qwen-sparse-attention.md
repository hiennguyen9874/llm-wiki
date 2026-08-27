---
type: Concept
title: Qwen Sparse Attention
description: Qwen Sparse Attention ranks fixed-size micro-blocks with a lightweight MQA indexer, then applies causal GQA only to tokens in the selected blocks.
tags: [attention, sparse-attention, qwen, long-context, grouped-query-attention]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-27T03:11:23Z }
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
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
---

# Qwen Sparse Attention

Qwen Sparse Attention (QSA) uses a separate low-width indexer to score contiguous micro-blocks, expands the selected blocks back to token indices, and restricts the main causal grouped-query attention (GQA) to those tokens. In Qwen3.8-Flash-Next, each four-token block is represented by the mean of its index keys; the indexer selects at most 512 complete blocks, corresponding to a 2,048-token budget, while retaining the visible incomplete tail.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Indexing and attention path

The released implementation projects each hidden state to four 128-dimensional query heads and one shared 128-dimensional key head. It averages raw keys within each complete four-token block, RMS-normalizes the queries and pooled keys, applies the model's partial RoPE, and scores each block by summing ReLU-clipped query–block-key dot products across the four query heads. Top-ranked blocks are expanded to all constituent tokens and overlaid on the ordinary causal mask.[^qwen38-next-modeling]

The main attention path is distinct from the indexer: it uses 24 query heads and two KV heads of width 256, Q/K normalization, 64 rotary dimensions, and a learned sigmoid output gate. The supplied diagram makes this separation explicit: a compressed lightweight indexer produces top-k block indices for sparse core attention, while the main attention has separate Q/K/V projections and a sigmoid-gated output.[^qwen38-next-attention-figure] Thus the indexer reduces the set read by the expensive attention operation, but the implementation still caches per-token main-attention K/V and indexer keys for QSA layers.[^qwen38-next-config][^qwen38-next-modeling]

## Complexity and systems boundary

For context length $N$, block size $r=4$, and selected-block count $K\le512$, the disclosed design scores roughly $N/r$ pooled keys per query and performs main attention over at most $Kr=2{,}048$ selected complete-block tokens, plus a tail shorter than $r$. This reduces the main-attention work relative to dense attention, but does not make indexing free or bound the QSA cache independently of context.[^qwen38-next-modeling]

The release blog reports that an optimized QSA attention kernel reaches up to 7.6× prefill and 4.9× decode speedups at one million tokens. It also reports 8.6× Qwen3.7-Plus prefill throughput at that context under an online-serving setup with a 90% prefix-cache hit rate. These are vendor measurements with a favorable cache-reuse assumption, not results reproduced by the supplied reference code.[^qwen38-next-blog]

The supplied Python implementation loops over batches and query positions to construct the selection mask and declares no FlashAttention or FlexAttention support for the text model. It is therefore a semantic reference path, not evidence of those optimized long-context gains; production efficiency depends on specialized serving kernels.[^qwen38-next-blog][^qwen38-next-modeling]

## Training and reported evaluation

QSA is introduced during 256K continued pre-training. The report describes 1,000 indexer-only dense-distillation steps (about 2B tokens), followed by 8,000 joint sparse-training steps (about 200B tokens). The teacher's token attention is max-pooled to blocks for KL distillation; after sparse selection, the backbone and indexer adapt jointly. Direct sparse use after distillation reportedly drops RULER performance, while joint training recovers it.[^qwen38-next-report]

In author-run comparisons, QSA raises the eight-task short-context average from 75.9 to 76.8 and the macro-average over RULER/MRCR settings from 78.76 to 80.93. At one million tokens, RULER rises from 90.08 to 93.00 and MRCR from 20.71 to 26.44. Four-step MTP accepted length is effectively unchanged (4.06 versus 4.07 average) when QSA indices are reused across draft steps. These point estimates lack repeated-seed uncertainty.[^qwen38-next-report]

The report's kernel comparison includes indexer plus sparse core attention and uses FlashInfer paged GQA as the dense baseline. It reports QSA speedups beginning around 64K and reaching 7.6× prefill and 4.9× decode at one million tokens. These are attention-module measurements under specified chunked-prefill and batched-MTP decode workloads, not end-to-end serving throughput.[^qwen38-next-report]

## Relationships

- **Used by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md) every fourth language layer.
- **Contrasts with:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md), whose disclosed indexer selects individual token-level MLA entries rather than fixed four-token blocks.
- **Related to:** [LongCat Sparse Attention](longcat-sparse-attention.md), another sparse long-context design with different streaming, cross-layer, and hierarchical selection rules.

## Evidence limits

The model card, blog, report, diagram, and reference code establish the selection concept, training procedure, checkpoint dimensions, and author-run ablations. The report does not provide code for the fused QSA kernel, absolute latency tables, repeated-seed uncertainty, or independent replication; its speed and quality results remain workload- and implementation-bound.[^qwen38-next-report][^qwen38-next-modeling]

[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Section 2.1.2, Tables 2–4, and Figures 3–6.

[^qwen38-next-card]: Qwen Team, “Qwen3.8-Flash-Next,” [model card](../raw/Qwen3.8-Flash-Next/README.md), Highlights and Model Overview.

[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [config](../raw/Qwen3.8-Flash-Next/config.json), `text_config`.

[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), `Qwen4ExpTextQSAIndexer` and `Qwen4ExpTextAttention`.

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), Attention section.

[^qwen38-next-attention-figure]: Qwen Team, “Qwen Sparse Attention,” [included diagram](../raw/Qwen3.8-Flash-Next/Attention.png).
