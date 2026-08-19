---
type: Concept
title: EmbeddingGemma 300M
description: A 300M-parameter Gemma 3-based multilingual text embedding model with 768-dimensional Matryoshka embeddings and on-device deployment focus.
tags: [embedding, retrieval, multilingual, matryoshka, gemma]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: embeddinggemma-card
    resource: ../raw/embeddinggemma-300m.md
    title: EmbeddingGemma model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# EmbeddingGemma 300M

EmbeddingGemma is Google's 300M-parameter open text-embedding model. Built from Gemma 3 with T5Gemma initialization, it produces 768-dimensional embeddings that can be truncated to 512, 256, or 128 dimensions through Matryoshka Representation Learning (MRL); its model card emphasizes deployment on resource-constrained devices. [^embeddinggemma-card]

## Benchmarks

The model card reports the following MTEB scores for the full-precision checkpoint. It provides the benchmark versions and aggregate metrics, but not task-level results or evaluation protocol details. [^embeddinggemma-card]

| Benchmark | 768d Mean (Task) | 768d Mean (TaskType) | 128d Mean (Task) | 128d Mean (TaskType) |
|---|---:|---:|---:|---:|
| MTEB Multilingual v2 | 61.15 | 54.31 | 58.23 | 51.77 |
| MTEB English v2 | 69.67 | 65.11 | 66.66 | 62.70 |
| MTEB Code v1 | 68.76 | 68.76 | 62.96 | 62.96 |

At 768 dimensions, the card's quantization-aware-training checkpoints score 60.62–60.93 Mean (Task) on MTEB Multilingual v2, 69.31–69.49 on English v2, and 67.99–68.70 on Code v1, across Q4_0, Q8_0, and mixed-precision configurations. These are self-reported scores; the card's claim of superiority to comparable-sized open models is not independently established by the source. [^embeddinggemma-card]

A supplied leaderboard CSV ranks the model **18th of 45**, reporting the same 768d aggregates—Mean (Task) **61.15** and Mean (TaskType) **54.31**—and the task-category scores below. The CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 64.40 | 60.90 | 51.17 | 5.61 | 24.82 | 81.40 | 63.25 | 62.49 | 74.73 |

## Model size and architecture

- **Size:** 300M parameters. [^embeddinggemma-card]
- **Backbone:** built from Gemma 3, initialized from T5Gemma; the card does not disclose layer count, hidden size, attention configuration, tokenizer, or parameter breakdown. [^embeddinggemma-card]
- **Input and output:** accepts text up to 2,048 tokens and outputs 768-dimensional vectors. MRL permits truncation to 512, 256, or 128 dimensions followed by re-normalization. [^embeddinggemma-card]
- **Runtime constraint:** activations do not support `float16`; the card recommends `float32` or `bfloat16`. [^embeddinggemma-card]

## Language support

The model was trained on text in **100+ spoken languages**, including web documents in over 100 languages. The source does not enumerate languages or provide per-language evaluation results, so the extent of support for any specific language is not established. [^embeddinggemma-card]

## Training data

The card reports approximately **320B tokens** drawn from web documents, code and technical documents, and synthetic/task-specific data. The latter includes curated data for information retrieval, classification, and sentiment analysis. It reports multi-stage CSAM filtering, automated filtering of certain personal and sensitive information, and additional quality and safety filtering. [^embeddinggemma-card]

The source does not name constituent datasets, give mixture proportions, describe collection dates or licenses, or specify the amount of synthetic versus non-synthetic material; those omissions limit assessment of corpus coverage and provenance. [^embeddinggemma-card]

[^embeddinggemma-card]: [EmbeddingGemma model card](../raw/embeddinggemma-300m.md). Model, training, language, and benchmark claims are reported by the model card.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
