---
type: Concept
title: Jina Embeddings v5 Text Nano
description: A 239M-parameter EuroBERT-210M-based multilingual text embedding model with 768-dimensional last-token-pooled, Matryoshka-truncatable vectors.
tags: [embedding, retrieval, multilingual, matryoshka, eurobert, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:55:57Z }
sources:
  - id: jina-v5-nano-card
    resource: ../raw/jina-embeddings-v5-text-nano.md
    title: jina-embeddings-v5-text-nano model card
  - id: jina-v5-text-report
    resource: ../raw/2602.15547_jina-embeddings-v5-text/paper.tex
    title: Jina Embeddings v5 Text: Task-Targeted Embedding Distillation
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

## Technical-report evaluation

The technical report reports **71.0 Average (Task)** on MTEB English v2 and **65.5 Average (Task)** on MMTEB for Nano. Its MMTEB task-type scores are bitext mining 67.7, classification 69.2, clustering 52.7, instruction reranking 0.0, multilabel classification 41.3, pair classification 81.9, reranking 64.6, retrieval 63.3, and STS 78.2. These are author-reported results; the report identifies some comparator scores as partly self-evaluated and provides no independent replication. [^jina-v5-text-report]

## Model size and architecture

- **Size:** 239M parameters. The technical report decomposes this into a 212M-parameter base and four 6.7M-parameter LoRA adapters. [^jina-v5-nano-card] [^jina-v5-text-report]
- **Backbone:** EuroBERT-210M. [^jina-v5-nano-card] [^jina-v5-text-report]
- **Training architecture:** embedding distillation from Qwen3-Embedding-4B combined with task-specific training. [^jina-v5-nano-card] [^jina-v5-text-report]
- **Output:** 768-dimensional vectors using last-token pooling; Matryoshka dimensions are 32, 64, 128, 256, 512, and 768. [^jina-v5-nano-card]
- **Context limit:** 8,192 tokens in the technical-report model table. [^jina-v5-text-report]
- **Tasks:** `retrieval`, `text-matching`, `clustering`, and `classification`, selected through task-specific LoRA adapters. [^jina-v5-nano-card] [^jina-v5-text-report]

## Language support

The card describes the model as multilingual but does not state a language count, enumerate languages, define its support criterion, or report per-language results. Its usage examples cover Arabic, Chinese, English, French, German, Greek, Hindi, Italian, Japanese, and Korean, but examples alone do not establish the scope or quality of language support. [^jina-v5-nano-card]

## Training data and procedure

The technical report documents two stages. First, Nano is distilled from Qwen3-Embedding-4B by projecting the 768-dimensional student embeddings into the teacher space and minimizing cosine distance for query/document pairs. General-purpose training uses pairs from more than 300 datasets in more than 30 languages for 50,000 steps. The report does not identify the complete corpus mixture, sizes, licenses, filtering, or sampling proportions. [^jina-v5-text-report]

Second, the distillation-trained backbone is frozen and separate rank-32 LoRA adapters are trained for retrieval, text matching, clustering, and classification. Retrieval combines InfoNCE with hard negatives, distillation, and global orthogonal regularization; text matching alternates between CoSENT for graded labels and InfoNCE plus distillation; clustering uses a topic-identification teacher instruction; and classification uses bidirectional contrastive learning with relational distillation. [^jina-v5-text-report]

## Contradictions

The Nano model card overview says it supports text up to **32K tokens**, but both its configuration table and the technical-report model table specify an **8,192-token** maximum. The sources do not explain whether 32K refers to another configuration, so its supported limit remains unresolved. [^jina-v5-nano-card] [^jina-v5-text-report]

## Relationships

- **Uses:** [Qwen3-Embedding-4B](qwen3-embedding-4b.md) as the first-stage distillation teacher. [^jina-v5-text-report]
- **Related to:** [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md), the larger v5 text model trained with the same two-stage regimen. [^jina-v5-text-report]

[^jina-v5-nano-card]: [jina-embeddings-v5-text-nano model card](../raw/jina-embeddings-v5-text-nano.md). Benchmark, model, language, and training statements are reported by the model card.
[^jina-v5-text-report]: [Jina Embeddings v5 Text: Task-Targeted Embedding Distillation](../raw/2602.15547_jina-embeddings-v5-text/paper.tex). Author technical report; training and evaluation claims are reported by its authors and were not independently reproduced.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.