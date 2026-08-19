---
type: Concept
title: Jina Embeddings v5 Text Nano
description: A 239M-parameter EuroBERT-210M-based multilingual text embedding model with 768-dimensional last-token-pooled, Matryoshka-truncatable vectors.
tags: [embedding, retrieval, multilingual, matryoshka, eurobert, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: jina-v5-nano-card
    resource: ../raw/jina-embeddings-v5-text-nano.md
    title: jina-embeddings-v5-text-nano model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# Jina Embeddings v5 Text Nano

Jina Embeddings v5 Text Nano is a 239M-parameter multilingual text embedding model based on EuroBERT-210M. It supports retrieval, text matching, clustering, and classification, producing 768-dimensional last-token-pooled vectors that can be Matryoshka-truncated to smaller dimensions. [^jina-v5-nano-card]

## Benchmarks

The model card reports an average score of **71.0 on MTEB English v2** and **65.5 on MMTEB**. It claims these results match or exceed other sub-500M embedding models, naming KaLM-mini-v2.5 (494M) and Gemma-300M (308M) as comparisons. The supplied source does not provide task-level scores, evaluation configurations, or an independent comparison, so the aggregate scores and comparative claim are self-reported. [^jina-v5-nano-card]

A supplied leaderboard CSV ranks the model **11th of 45** with Mean (Task) **65.52** and Mean (TaskType) **57.66**. Its task-category scores are below; the CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 67.70 | 69.18 | 52.73 | 0.05 | 41.31 | 81.94 | 64.63 | 63.26 | 78.17 |

## Model size and architecture

- **Size:** 239M parameters. [^jina-v5-nano-card]
- **Backbone:** EuroBERT/EuroBERT-210M. [^jina-v5-nano-card]
- **Training architecture:** embedding distillation from Qwen3-Embedding-4B combined with task-specific contrastive losses. [^jina-v5-nano-card]
- **Output:** 768-dimensional vectors using last-token pooling; Matryoshka dimensions are 32, 64, 128, 256, 512, and 768. [^jina-v5-nano-card]
- **Tasks:** `retrieval`, `text-matching`, `clustering`, and `classification`. [^jina-v5-nano-card]

## Language support

The card describes the model as multilingual but does not state a language count, enumerate languages, define its support criterion, or report per-language results. Its usage examples cover Arabic, Chinese, English, French, German, Greek, Hindi, Italian, Japanese, and Korean, but examples alone do not establish the scope or quality of language support. [^jina-v5-nano-card]

## Training data and procedure

The card identifies the teacher model (Qwen3-Embedding-4B) and the use of task-specific contrastive losses, but it does not disclose the training data: no corpus names, size or token count, language mix, collection dates, licenses, filtering, or mixture proportions are provided. It directs readers to an external technical report for training details; that report is outside the supplied source artifact. [^jina-v5-nano-card]

## Source inconsistency

The overview says the model supports text up to **32K tokens**, while the configuration table lists a **maximum sequence length of 8,192**. The supplied source does not explain the discrepancy, so the supported input limit is unresolved. [^jina-v5-nano-card]

[^jina-v5-nano-card]: [jina-embeddings-v5-text-nano model card](../raw/jina-embeddings-v5-text-nano.md). Benchmark, model, language, and training statements are reported by the model card.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.