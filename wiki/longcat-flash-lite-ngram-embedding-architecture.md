---
type: Concept
title: LongCat-Flash-Lite N-gram-embedding architecture
description: LongCat-Flash-Lite is a reported 68.5B-total MoE with 2.9B–4.5B active parameters, 31.4B projected hashed N-gram-embedding parameters, and a 256K YaRN context claim.
tags: [longcat, mixture-of-experts, n-gram-embeddings, long-context, yarn]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:09:50Z }
sources:
  - id: longcat-flash-lite-card-2026
    resource: ../raw/LongCat-Flash-Lite.md
    title: LongCat-Flash-Lite model card
  - id: longcat-flash-lite-sparse-card-2026
    resource: ../raw/LongCat-Flash-Lite-Sparse.md
    title: LongCat-Flash-Lite-Sparse model card
  - id: longcat-embedding-scaling-2026
    resource: ../raw/2601.21204_ScalingEmbeddingsOutperformsScalingExpertsinLanguageModels/longcat.tex
    title: "Scaling Embeddings Outperforms Scaling Experts in Language Models"
---

# LongCat-Flash-Lite N-gram-embedding architecture

LongCat-Flash-Lite is Meituan’s reported 68.5B-total-parameter MoE language model with 2.9B–4.5B activated parameters per token. Its technical report specifies 31.4B N-gram-embedding parameters (46% of total), 14 shortcut layers, and YaRN training intended to support sequences up to 256K tokens.[^longcat-embedding-scaling-2026]

## N-gram embedding capacity

The technical report specifies a base embedding plus suffix N-gram branches. Each branch uses $K$ hash-addressed sub-tables and a projection for each sub-table, then averages their projected lookups with the base-token embedding. Its hash is a polynomial rolling function of the token IDs modulo the selected table size; the report does not disclose the production model’s chosen $N$, $K$, exact table sizes, or table layout.[^longcat-embedding-scaling-2026]

Each shortcut layer has 256 FFN experts plus 128 zero-experts, and each token selects 12 experts. The source says it uses a LongCat-Flash training recipe: 11T tokens at 8K sequence length, 1.5T mid-training tokens extending length to 128K, then supervised fine-tuning; YaRN is introduced at the 32K stage. It does not provide data composition, a configuration/checkpoint, or source implementation.[^longcat-embedding-scaling-2026]

## Context claim

The card says YaRN provides a 256K context length. It does not disclose the base context, extension training, positional configuration, corpus, evaluation method, or quality/reliability profile across that window.[^longcat-flash-lite-card-2026]

## Relationships

- **Uses:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md) as a reported sparse capacity mechanism distinct from MoE computation.[^longcat-flash-lite-card-2026]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); total and active parameters alone do not establish loading, routing, or serving cost.[^longcat-flash-lite-card-2026]
- **Dense predecessor of:** [LongCat-Flash-Lite-Sparse attention architecture](longcat-flash-lite-sparse-attention-architecture.md), whose model card identifies it as the MLA-based baseline replaced by LongCat Sparse Attention.[^longcat-flash-lite-sparse-card-2026]
- **Evaluated and released by:** [LongCat-Flash-Lite evaluation, deployment, and release limits](longcat-flash-lite-evaluation-deployment-and-release-limits.md).

## Evidence limits

The vendor technical report and its figure attachments were inspected, but it remains an author-authored disclosure. The raw bundle has no model configuration, weights, training-data composition, source code, cache or kernel implementation, benchmark harness, or reproducible ablation materials. The linked SGLang pull request was not inspected.[^longcat-embedding-scaling-2026][^longcat-flash-lite-card-2026]

[^longcat-flash-lite-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite,” [model card](../raw/LongCat-Flash-Lite.md), Model Introduction and Key Features.

[^longcat-flash-lite-sparse-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite-Sparse,” [model card](../raw/LongCat-Flash-Lite-Sparse.md), Model Introduction.
