---
type: Concept
title: LongCat-Flash-Lite-Sparse attention architecture
description: LongCat-Flash-Lite-Sparse is a reported 69B-total/~3B-active non-thinking MoE that replaces its dense predecessor’s MLA with streaming-aware, cross-layer, and hierarchical sparse attention for a native one-million-token context.
tags: [longcat, mixture-of-experts, sparse-attention, multi-head-latent-attention, long-context]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:13:08Z }
sources:
  - id: longcat-flash-lite-sparse-card-2026
    resource: ../raw/LongCat-Flash-Lite-Sparse.md
    title: LongCat-Flash-Lite-Sparse model card
  - id: longcat-lsa-2026
    resource: ../raw/2608.01662_LongCatSparseAttention/longcat.tex
    title: "LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing"
---

# LongCat-Flash-Lite-Sparse attention architecture

LongCat-Flash-Lite-Sparse is Meituan’s reported non-thinking MoE model with 69B total parameters and about 3B activated per token. Relative to [LongCat-Flash-Lite N-gram-embedding architecture](longcat-flash-lite-ngram-embedding-architecture.md), the card says it replaces dense Multi-head Latent Attention (MLA) with LongCat Sparse Attention (LSA), enabling a native context of up to one million tokens.[^longcat-flash-lite-sparse-card-2026]

## LongCat Sparse Attention

The card describes LSA as an extension of DeepSeek Sparse Attention with three complementary indexing mechanisms:[^longcat-flash-lite-sparse-card-2026]

- **Streaming-Aware Indexing (SI)** reserves part of the selection budget for a fixed sink and local sliding window, leaving the remainder for dynamic sparse selection. The stated goal is more contiguous, predictable KV reads and better HBM access efficiency than fragmented gathering.
- **Cross-Layer Indexing (CLI)** lets consecutive layers reuse one indexing result. The card attributes this reuse to cross-layer distillation during training.
- **Hierarchical Indexing (HI)** first recalls candidate blocks with coarse scores, then selects tokens within them using fine-grained scores. The claimed purpose is to reduce the candidate space and indexing overhead; the card says it can be enabled at inference without additional training.

The card supplies no algorithm, index budget, layer-sharing interval, distillation objective, kernel implementation, latency decomposition, or ablation. The later LongCat technical report specifies a $K=2048$ budget with 16 sink and 1,024 sliding-window tokens, CLI groups of two model attention layers and three MTP steps, and training-free HI at long context; it identifies the model as an LSA-based 69B-total/3B-active release.[^longcat-flash-lite-sparse-card-2026][^longcat-lsa-2026]

## Context extension

The card reports an enriched long-context corpus and a progressive extension schedule to 1,024K tokens, yielding native support for contexts up to 1M tokens. The technical report specifies five stages (32K, 64K, 128K, 256K, and 1M), introduces three-step MTP at 32K, and converts the main and MTP modules from dense MLA to SI/CLI at 128K; HI remains inference-only. It still does not disclose the corpus, token counts, positional treatment, or a reliability boundary within the advertised window.[^longcat-flash-lite-sparse-card-2026][^longcat-lsa-2026]

## Relationships

- **Implements:** [LongCat Sparse Attention](longcat-sparse-attention.md) in the reported released model.[^longcat-lsa-2026]
- **Extends:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) with streaming-aware, cross-layer, and hierarchical indexing; implementation and efficiency claims remain source- and configuration-specific.[^longcat-flash-lite-sparse-card-2026][^longcat-lsa-2026]
- **Replaces in this model:** [Multi-head Latent Attention](multi-head-latent-attention.md), which the card identifies as the dense predecessor’s attention mechanism.[^longcat-flash-lite-sparse-card-2026]
- **Evaluated and released by:** [LongCat-Flash-Lite-Sparse evaluation, deployment, and release limits](longcat-flash-lite-sparse-evaluation-deployment-and-release-limits.md).

## Evidence limits

The model-card claims are vendor-authored. A later local technical report supplies method and selected training detail, but no model or kernel code, weights, configurations sufficient for reproduction, training data, or independent evaluation was examined.[^longcat-flash-lite-sparse-card-2026][^longcat-lsa-2026]

[^longcat-flash-lite-sparse-card-2026]: Meituan LongCat team, “LongCat-Flash-Lite-Sparse,” [model card](../raw/LongCat-Flash-Lite-Sparse.md), Model Introduction and Key Features.

[^longcat-lsa-2026]: Wen Zan et al., “LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing,” 2026, [source](../raw/2608.01662_LongCatSparseAttention/longcat.tex), Sections 3 and 6.
