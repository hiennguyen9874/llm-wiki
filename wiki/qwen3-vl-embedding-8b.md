---
type: Concept
title: Qwen3-VL-Embedding-8B
description: An 8B-parameter, 36-layer Qwen3-VL-based multimodal embedding model with 32K context, 64–4,096-dimensional outputs, 30+ language support, and reported MMEB-V2 and MMTEB results.
tags: [embedding, retrieval, multimodal, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:09:50Z }
sources:
  - id: qwen3-vl-embedding-8b-card
    resource: ../raw/Qwen3-VL-Embedding-8B.md
    title: Qwen3-VL-Embedding-8B model card
  - id: qwen3-vl-retrieval-report
    resource: ../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex
    title: "Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking"
---

# Qwen3-VL-Embedding-8B

Qwen3-VL-Embedding-8B is an instruction-aware multimodal embedding model built from Qwen3-VL-8B-Instruct. It maps text, images, screenshots, videos, and mixed-modality inputs into a shared vector space for retrieval, clustering, and cross-modal similarity. The model card reports the strongest aggregate MMEB-V2 result among its listed models, but does not disclose the embedding model's training datasets or training procedure.[^qwen3-vl-embedding-8b-card]

## Model size and architecture

- **Parameters and depth:** 8B parameters and 36 layers.[^qwen3-vl-embedding-8b-card]
- **Base model and pooling:** initialized from Qwen3-VL-8B-Instruct and used as a causal-attention bi-encoder. The instruction is a system message, the instance is a user message, and the last hidden state of an appended `<|endoftext|>` token is the dense representation; relevance uses cosine similarity.[^qwen3-vl-retrieval-report]
- **Inputs:** text, images, screenshots, videos, and arbitrary multimodal combinations such as text plus image or video.[^qwen3-vl-embedding-8b-card]
- **Context and output:** 32K sequence length and embeddings up to 4,096 dimensions. Matryoshka representation learning permits user-selected dimensions from 64 through 4,096.[^qwen3-vl-embedding-8b-card]
- **Adaptation:** supports task-specific instructions and post-processing quantization of output embeddings. The card reports that instructions generally improve downstream results by 1–5%, based on its own evaluation.[^qwen3-vl-embedding-8b-card]

## Language support

The model card claims support for more than 30 languages, inherited from Qwen3-VL, but does not enumerate them or provide per-language results. It recommends English task instructions in multilingual use because most instructions used during training were originally written in English.[^qwen3-vl-embedding-8b-card]

## Training

The technical report describes public, proprietary in-house, and synthetic multimodal relevance data without disclosing total sample counts or the source allocation. Synthetic image and video tasks span classification, question answering, retrieval, and moment retrieval. Seed assets are quality-filtered, labeled and annotated with Qwen3-VL-32B, filtered for visual-text alignment using GME similarity, category-rebalanced, and refined through recall plus positive and hard-negative filtering.[^qwen3-vl-retrieval-report]

Training uses LoRA and three stages: large-scale synthetic InfoNCE pre-training; task-specific contrastive learning on mined public, proprietary, and sampled synthetic data; and score-distribution distillation from Qwen3-VL-Reranker followed by model merging to balance retrieval against classification and QA. Retrieval, classification, and semantic textual similarity use adapted InfoNCE, explicit-label contrastive, and CoSent objectives respectively. Matryoshka losses train variable-dimensional prefixes, while LSQ-based quantization-aware training targets low-precision embeddings.[^qwen3-vl-retrieval-report]

## Reported benchmarks

These results are author-reported rather than independent reproductions. The model card covers 78 MMEB-V2 datasets and says all models except IFM-TTE were re-evaluated on an updated VisDoc OOD split. The technical report reports 77.8 overall rather than the card’s 77.9 and uses different category aggregates; these should be treated as source/version differences. The report’s claim that 77.8 was first on the leaderboard is time-bound to its January 2026 evaluation.[^qwen3-vl-embedding-8b-card][^qwen3-vl-retrieval-report]

The report’s evaluation constrains context to 16,384 tokens, images to 1,800 tokens, and videos to 15,000 tokens and 64 frames, below the declared 32K model maximum.[^qwen3-vl-retrieval-report]

| Benchmark | Aggregate | Qwen3-VL-Embedding-8B | Qwen3-VL-Embedding-2B |
|---|---|---:|---:|
| MMEB-V2 (78 datasets) | All | **77.9** | 73.4 |
| MMEB-V2 | Image Overall | 80.1 | 75.0 |
| MMEB-V2 | Video Overall | 66.1 | 61.1 |
| MMEB-V2 | VisDoc Overall | 83.3 | 80.2 |
| MMTEB | Mean (Task) | 67.88 | 63.87 |
| MMTEB | Mean (Type) | 58.88 | 55.84 |

On the supplied MMEB-V2 table, Qwen3-VL-Embedding-8B leads every listed model in the aggregate score at 77.9, one point above Seed-1.6-embedding-1215 at 76.9. Its category results are not uniformly best: Seed leads Video Overall at 67.7, while the Qwen model leads Image Overall at 80.1 and VisDoc Overall at 83.3. On the supplied MMTEB table, its 67.88 Mean (Task) trails the text-only Qwen3-Embedding-8B (70.58), Qwen3-Embedding-4B (69.45), and Gemini Embedding (68.37), so the card does not establish text-only benchmark leadership.[^qwen3-vl-embedding-8b-card]

## Relationships

- **Shares family with:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md), the smaller 28-layer variant with a maximum 2,048-dimensional output.
- **Trained with supervision from:** the Qwen3-VL reranker family during retrieval-focused distillation; see [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md) and [Qwen3-VL-Reranker-2B](qwen3-vl-reranker-2b.md).

[^qwen3-vl-embedding-8b-card]: [Qwen3-VL-Embedding-8B model card](../raw/Qwen3-VL-Embedding-8B.md). Architecture, language, instruction-effect, and benchmark claims are author-reported.
[^qwen3-vl-retrieval-report]: [Qwen3-VL retrieval technical report](../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex). Architecture, training, and evaluation claims are author-reported; proprietary training data prevents full auditability.
