---
type: Concept
title: Qwen3-VL-Embedding-2B
description: A 2B-parameter, 28-layer Qwen3-VL-based multimodal embedding model with 32K context, 64–2,048-dimensional outputs, 30+ language support, and reported MMEB-V2 and MMTEB results.
tags: [embedding, retrieval, multimodal, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:09:50Z }
sources:
  - id: qwen3-vl-embedding-2b-card
    resource: ../raw/Qwen3-VL-Embedding-2B.md
    title: Qwen3-VL-Embedding-2B model card
  - id: qwen3-vl-retrieval-report
    resource: ../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex
    title: "Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking"
---

# Qwen3-VL-Embedding-2B

Qwen3-VL-Embedding-2B is an instruction-aware multimodal embedding model built from Qwen3-VL-2B-Instruct. It maps text, images, screenshots, videos, and mixed-modality inputs into a shared vector space for retrieval, clustering, and cross-modal similarity. The model card reports strong multimodal results for its 2B size, but does not disclose its embedding-training datasets or training procedure.[^qwen3-vl-embedding-2b-card]

## Model size and architecture

- **Parameters and depth:** 2B parameters and 28 layers.[^qwen3-vl-embedding-2b-card]
- **Base model and pooling:** initialized from Qwen3-VL-2B-Instruct and used as a causal-attention bi-encoder. The instruction is a system message, the instance is a user message, and the last hidden state of an appended `<|endoftext|>` token is the dense representation; relevance uses cosine similarity.[^qwen3-vl-retrieval-report]
- **Inputs:** text, images, screenshots, videos, and arbitrary multimodal combinations such as text plus image or video.[^qwen3-vl-embedding-2b-card]
- **Context and output:** 32K sequence length and embeddings up to 2,048 dimensions. Matryoshka representation learning permits user-selected dimensions from 64 through 2,048.[^qwen3-vl-embedding-2b-card]
- **Adaptation:** supports task-specific instructions and post-processing quantization of output embeddings. The card reports that instructions generally improve downstream results by 1–5%, based on its own evaluation.[^qwen3-vl-embedding-2b-card]

## Language support

The model card claims support for more than 30 languages, inherited from Qwen3-VL, but does not enumerate them or provide per-language coverage. It recommends English task instructions in multilingual use because most instructions used during training were written in English.[^qwen3-vl-embedding-2b-card]

## Training

The technical report describes a mixture of public, proprietary in-house, and synthetic multimodal relevance data, but does not disclose total sample counts or the public/proprietary allocation. Synthetic image and video tasks cover classification, question answering, retrieval, and moment retrieval. Seed assets are filtered for visual quality and cross-modal alignment, labeled and annotated with Qwen3-VL-32B, rebalanced by category, then refined through embedding recall, positive filtering, and hard-negative selection.[^qwen3-vl-retrieval-report]

Training uses LoRA and three stages: (1) InfoNCE contrastive pre-training on large-scale synthetic data; (2) task-specific contrastive learning on mined public, proprietary, and sampled synthetic data; and (3) distribution distillation from Qwen3-VL-Reranker followed by model merging to recover classification and QA performance lost during retrieval-focused distillation. Objectives vary by task: retrieval uses InfoNCE, classification contrasts only explicit incorrect labels, and semantic textual similarity uses CoSent. Matryoshka losses train embedding prefixes, while LSQ-based quantization-aware training targets full-precision, int8, and binary deployment robustness.[^qwen3-vl-retrieval-report]

In the report’s 2B stage ablation, MMEB-v2 rises from 66.6 at initial pre-training (`s0`) to 73.2 after the final merge (`s3`). Distillation (`s2`) improves retrieval-oriented categories but lowers classification and QA, motivating the merge with `s1`.[^qwen3-vl-retrieval-report]

## Efficiency findings

On author-run MSMARCO and VL3-Syn experiments with the 2B model, reducing text embeddings from 1,024 to 512 dimensions reportedly cuts storage in half and doubles retrieval speed for a 1.4% performance decrease. Int8 quantization has negligible reported degradation, while binary quantization degrades retrieval more sharply, especially at smaller dimensions.[^qwen3-vl-retrieval-report]

## Reported benchmarks

These are author-reported results, not independent reproductions. The model card says all models except IFM-TTE were re-evaluated on an updated VisDoc OOD split. The technical report instead reports 73.2 overall for this model under its stated MMEB-v2 setup; this differs from the card’s 73.4 and should be treated as a source/version difference rather than silently reconciled.[^qwen3-vl-embedding-2b-card][^qwen3-vl-retrieval-report]

The report also says evaluation used a 16,384-token context cap, up to 1,800 image tokens, and up to 15,000 video tokens across at most 64 frames. These evaluation limits are lower than the model’s declared 32K maximum.[^qwen3-vl-retrieval-report]

| Benchmark | Aggregate | Qwen3-VL-Embedding-2B | Qwen3-VL-Embedding-8B |
|---|---|---:|---:|
| MMEB-V2 (78 datasets) | All | 73.2 | 77.8 |
| MMEB-V2 | Image Overall | 75.0 | 80.1 |
| MMEB-V2 | Video Overall | 61.9 | 67.1 |
| MMEB-V2 | VisDoc Overall | 79.2 | 82.4 |
| MMTEB | Mean (Task) | 63.87 | 67.88 |
| MMTEB | Mean (Type) | 55.84 | 58.88 |

On the supplied MMEB-V2 comparison, the 2B model scores 73.2 overall: below Qwen3-VL-Embedding-8B (77.8), Seed-1.6-embedding-1215 (76.9), and IFM-TTE (74.1), while above the other listed baselines. It exceeds the listed 8B RzenEmbed and Ops-MM-embedding-v1 overall despite using fewer reported parameters. On the supplied MMTEB table, its 63.87 Mean (Task) trails Qwen3-Embedding-0.6B (64.33), illustrating that the multimodal model card does not establish leadership for text-only embedding.[^qwen3-vl-embedding-2b-card]

## Relationships

- **Provides candidates to:** [Qwen3-VL-Reranker-2B](qwen3-vl-reranker-2b.md) and [Qwen3-VL-Reranker-8B](qwen3-vl-reranker-8b.md) in the report’s top-100 reranking evaluation.
- **Shares family with:** [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md).

[^qwen3-vl-embedding-2b-card]: [Qwen3-VL-Embedding-2B model card](../raw/Qwen3-VL-Embedding-2B.md). Architecture, language, instruction-effect, and benchmark claims are author-reported.
[^qwen3-vl-retrieval-report]: [Qwen3-VL retrieval technical report](../raw/2601.04720_Qwen3-VL-Embedding_Qwen3-VL-Reranker/colm2024_conference.tex). Architecture, training, ablation, and evaluation claims are author-reported; proprietary training data prevents full auditability.
