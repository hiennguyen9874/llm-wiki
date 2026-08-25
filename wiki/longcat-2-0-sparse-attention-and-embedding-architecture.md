---
type: Concept
title: LongCat-2.0 sparse-attention and embedding architecture
description: LongCat-2.0 is a reported 1.6T-total/48B-active MoE that pairs streaming-aware, cross-layer, and hierarchical sparse attention with 135B N-gram embedding parameters for long-context and agentic workloads.
tags: [longcat, mixture-of-experts, sparse-attention, n-gram-embeddings, multi-token-prediction, long-context]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:13:08Z }
sources:
  - id: longcat-2-card-2026
    resource: ../raw/LongCat-2.0.md
    title: LongCat-2.0 model card
  - id: longcat-lsa-2026
    resource: ../raw/2608.01662_LongCatSparseAttention/longcat.tex
    title: "LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing"
---

# LongCat-2.0 sparse-attention and embedding architecture

LongCat-2.0 is Meituan’s reported 1.6-trillion-parameter MoE language model with about 48B activated parameters per token. Its model card combines LongCat Sparse Attention (LSA)—streaming-aware, cross-layer, and hierarchical indexing—with 135B N-gram embedding parameters, and attributes its long-horizon capability to LSA, hundreds of billions of one-million-context training tokens, and post-training.[^longcat-2-card-2026]

## Sparse-attention indexer

The card presents LSA as an answer to the output discontinuity and quadratic scoring bottleneck it attributes to DeepSeek Sparse Attention’s Lightning Indexer. It names three orthogonal changes:[^longcat-2-card-2026]

- **Streaming-aware Indexing (SI)** allocates selection budget between contiguous accesses and dynamically selected tokens. The stated systems intent is coalesced HBM access and predictable sequential reads rather than fragmented gathers.
- **Cross-Layer Indexing (CLI)** reuses one indexing pass for several adjacent layers; cross-layer distillation is said to make the reuse possible during training. The described target-model schedule shares an index every two layers.
- **Hierarchical Indexing (HI)** first recalls blocks by approximate block-level scoring, then selects tokens within those blocks, reducing the per-query candidate set for fine scoring.

The card says these strategies also apply to a three-step Multi-Token Prediction (MTP) module for speculative decoding. In that reported arrangement, all three MTP draft steps share one indexer pass. The technical report independently describes the same three-step arrangement, but only says LSA underpins LongCat-2.0 (1.6T-A48B); it does not document that model's N-gram embedding allocation or full configuration.[^longcat-2-card-2026][^longcat-lsa-2026]

## N-gram embedding capacity

LongCat-2.0 inherits N-gram Embedding from LongCat-Flash-Lite and assigns 135B parameters to it. The card characterizes these parameters as sparse dimensions orthogonal to its MoE, and asserts that MoE sparsity has passed a “sweet spot” while the N-gram share should remain within an optimum range. It does not disclose the lookup formulation, table layout, tokenizer coupling, ablation protocol, or the claimed optimum; this is model-card evidence for the allocation and design rationale, not an independently established scaling law.[^longcat-2-card-2026]

## Training and context claims

The card reports pre-training on more than 35T tokens, with hundreds of billions of tokens at a one-million-token context length. It also reports that the full training run and large-scale deployment used AI ASIC superpods, consumed millions of accelerator-days, and experienced no rollbacks or irrecoverable loss spikes. No model configuration, data composition, training schedule, hardware definition, loss trace, or reproducible systems measurement is bundled with this source.[^longcat-2-card-2026]

## Relationships

- **Implements:** [LongCat Sparse Attention](longcat-sparse-attention.md), whose technical report identifies LSA as underpinning LongCat-2.0; complete model-level details remain card-bounded.[^longcat-lsa-2026]
- **Related sparse-attention design:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md). LongCat explicitly positions LSA against the indexer bottlenecks it attributes to DSA; the implementations and measurements are not directly comparable from this card alone.[^longcat-2-card-2026]
- **Uses:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md) as a distinct sparse-capacity mechanism alongside MoE.[^longcat-2-card-2026]
- **Uses:** [Sequential multi-token prediction](sequential-multi-token-prediction.md) in a reported three-step speculative-drafting arrangement.[^longcat-2-card-2026]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md); total and active parameter counts alone do not establish its training or serving cost.[^longcat-2-card-2026]
- **Evaluated and released by:** [LongCat-2.0 evaluation, deployment, and release limits](longcat-2-0-evaluation-deployment-and-release-limits.md).

## Evidence limits

All architecture, training, context, and systems statements come from the vendor model card. The linked technical blog, source code/configuration, training data, weights, and benchmark-chart SVG are outside this raw artifact; its two locally referenced `figures/` SVGs were absent. The prose and numeric benchmark table were available, but no claims unique to the missing graphics were compiled.[^longcat-2-card-2026]

[^longcat-2-card-2026]: Meituan LongCat team, “LongCat-2.0,” [model card](../raw/LongCat-2.0.md), Model Introduction, Key Features, Evaluation Results, Deployment, Chat Template, License Agreement, and Usage Considerations.

[^longcat-lsa-2026]: Wen Zan et al., “LongCat Sparse Attention: Taming the Lightning via Streaming-aware Hierarchical Cross-Layer Indexing,” 2026, [source](../raw/2608.01662_LongCatSparseAttention/longcat.tex), Abstract and Sections 1 and 3.
