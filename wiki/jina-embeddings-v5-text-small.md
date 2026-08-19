---
type: Concept
title: Jina Embeddings v5 Text Small
description: A 677M-parameter Qwen3-0.6B-based multilingual text embedding model with 1,024-dimensional, last-token-pooled Matryoshka vectors and a 32,768-token input limit.
tags: [embedding, retrieval, multilingual, matryoshka, qwen, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: jina-v5-small-card
    resource: ../raw/jina-embeddings-v5-text-small.md
    title: jina-embeddings-v5-text-small model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# Jina Embeddings v5 Text Small

Jina Embeddings v5 Text Small is a 677M-parameter multilingual text embedding model built on Qwen3-0.6B-Base. It supports retrieval, text matching, clustering, and classification, using 1,024-dimensional last-token-pooled vectors that can be Matryoshka-truncated. The model card states a 32,768-token maximum sequence length. [^jina-v5-small-card]

## Benchmarks

The model card reports averages of **71.7 on MTEB English v2** and **67.7 on MMTEB**. It claims these are the highest scores among multilingual embedding models below 1B parameters. The supplied source gives no task-level scores, evaluation configurations, comparison table, or independent evaluation; the scores and rank claim are therefore self-reported. [^jina-v5-small-card]

A supplied leaderboard CSV ranks the model **5th of 45** with Mean (Task) **67.00** and Mean (TaskType) **58.90**. Its task-category scores are below; the CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 69.71 | 71.32 | 53.41 | 1.35 | 41.97 | 82.93 | 65.66 | 64.88 | 78.85 |

## Contradictions

The model card reports **67.7 on MMTEB**, while the supplied CSV reports **67.00 Mean (Task)** for a similarly named multilingual MTEB benchmark. Neither artifact provides enough evaluation detail to determine whether these are the same configuration, so the values are not directly reconciled. [^jina-v5-small-card] [^mteb-multilingual-v2-summary]

## Model size and architecture

- **Size:** 677M parameters. [^jina-v5-small-card]
- **Backbone:** Qwen/Qwen3-0.6B-Base. [^jina-v5-small-card]
- **Training architecture:** embedding distillation from Qwen3-Embedding-4B combined with task-specific contrastive losses. [^jina-v5-small-card]
- **Output:** 1,024-dimensional vectors using last-token pooling; Matryoshka dimensions are 32, 64, 128, 256, 512, 768, and 1,024. [^jina-v5-small-card]
- **Tasks:** `retrieval`, `text-matching`, `clustering`, and `classification`. [^jina-v5-small-card]

## Language support

The card states support for **119+ languages** and describes the model as multilingual. It neither enumerates the languages nor defines the support criterion or provides per-language results, so support quality for any particular language is not established by this source. Usage examples include Arabic, Chinese, English, French, German, Greek, Hindi, Italian, Japanese, and Korean. [^jina-v5-small-card]

## Training data and procedure

The model card identifies the teacher model and task-specific contrastive-loss training, but does not disclose training data: it provides no corpus names, size or token count, language mix, collection dates, licenses, filtering, or mixture proportions. It refers readers to an external technical report for training details; that report is outside the supplied source artifact. [^jina-v5-small-card]

## Relationships

- **Related to:** [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md), a smaller model in the same v5 text family. [^jina-v5-small-card]

[^jina-v5-small-card]: [jina-embeddings-v5-text-small model card](../raw/jina-embeddings-v5-text-small.md). Benchmark, architecture, language, and training statements are reported by the model card; linked external technical-report material was not inspected.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
