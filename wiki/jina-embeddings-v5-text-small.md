---
type: Concept
title: Jina Embeddings v5 Text Small
description: A 677M-parameter Qwen3-0.6B-based multilingual text embedding model with 1,024-dimensional, last-token-pooled Matryoshka vectors and a 32,768-token input limit.
tags: [embedding, retrieval, multilingual, matryoshka, qwen, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T20:04:02+07:00 }
sources:
  - id: jina-v5-small-card
    resource: ../raw/jina-embeddings-v5-text-small.md
    title: jina-embeddings-v5-text-small model card
  - id: jina-v5-text-report
    resource: ../raw/2602.15547_jina-embeddings-v5-text/paper.tex
    title: Jina Embeddings v5 Text: Task-Targeted Embedding Distillation
  - id: jina-v5-omni-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    title: jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers
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

## Technical-report evaluation

The technical report gives **71.7 Average (Task)** on MTEB English v2 and **67.0 Average (Task)** on MTEB Multilingual v2 (MMTEB) for Small. It reports the following MMTEB task-type scores: bitext mining 69.7, classification 71.3, clustering 53.4, instruction reranking 1.3, multilabel classification 42.0, pair classification 82.9, reranking 65.7, retrieval 64.9, and STS 78.9. These are author-reported results; the report says some comparison scores are partly self-evaluated and does not provide independent replication. [^jina-v5-text-report]

## Contradictions

The model card reports **67.7 on MMTEB**, whereas both the technical report and the supplied CSV report **67.0 Mean (Task)** for a similarly named multilingual MTEB benchmark. The supplied sources do not identify the cause of the difference, so the values are not directly reconciled. [^jina-v5-small-card] [^jina-v5-text-report] [^mteb-multilingual-v2-summary]

## Model size and architecture

- **Size:** 677M parameters. [^jina-v5-small-card]
- **Backbone:** Qwen/Qwen3-0.6B-Base. [^jina-v5-small-card]
- **Training architecture:** embedding distillation from Qwen3-Embedding-4B combined with task-specific contrastive losses. [^jina-v5-small-card]
- **Output:** 1,024-dimensional vectors using last-token pooling; Matryoshka dimensions are 32, 64, 128, 256, 512, 768, and 1,024. [^jina-v5-small-card]
- **Tasks:** `retrieval`, `text-matching`, `clustering`, and `classification`. [^jina-v5-small-card]

## Language support

The card states support for **119+ languages** and describes the model as multilingual. It neither enumerates the languages nor defines the support criterion or provides per-language results, so support quality for any particular language is not established by this source. Usage examples include Arabic, Chinese, English, French, German, Greek, Hindi, Italian, Japanese, and Korean. [^jina-v5-small-card]

## Training data and procedure

The technical report documents two stages. First, the model is distilled from Qwen3-Embedding-4B: a linear head projects its 1,024-dimensional student vectors into the teacher space, and cosine distance aligns query and document vectors. General-purpose training uses text pairs from more than 300 datasets in more than 30 languages for 50,000 steps; Small then receives 6,500 long-context steps on synthetic high-noise documents and natural long texts paired with LLM-generated queries. The report does not name the full training mixture, give corpus sizes, licenses, or filtering details. [^jina-v5-text-report]

Second, frozen backbone weights receive separate rank-32 LoRA adapters for retrieval, text matching, clustering, and classification. Retrieval combines InfoNCE with hard negatives, distillation, and global orthogonal regularization; the report’s ablation attributes its best tested MTEB/RTEB retrieval scores (64.50/66.45) to that combination. Text matching uses CoSENT when graded similarity labels are available, otherwise InfoNCE plus distillation. Clustering distills with a topic-identification teacher instruction, and classification uses bidirectional contrastive learning plus relational distillation. [^jina-v5-text-report]

The report states that Matryoshka retrieval performance drops markedly below 256 dimensions. In its binary-quantization ablation, the full retrieval objective lost 1.90 MTEB and 2.51 RTEB points, versus 3.08 and 3.92 without the orthogonal regularizer. These are report-specific experimental results, not an independently replicated deployment guarantee. [^jina-v5-text-report]

## Relationships

- **Uses:** [Qwen3-Embedding-4B](qwen3-embedding-4b.md) as the first-stage distillation teacher. [^jina-v5-text-report]
- **Related to:** [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md), the smaller v5 text model trained with the same two-stage regimen. [^jina-v5-text-report]
- **Extended by:** [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md) through [GELATO](gelato.md), without changing this model's text-encoder weights. [^jina-v5-omni-report]

[^jina-v5-small-card]: [jina-embeddings-v5-text-small model card](../raw/jina-embeddings-v5-text-small.md). Benchmark, architecture, language, and training statements are reported by the model card.
[^jina-v5-text-report]: [Jina Embeddings v5 Text: Task-Targeted Embedding Distillation](../raw/2602.15547_jina-embeddings-v5-text/paper.tex). Author technical report; training and evaluation claims are reported by its authors and were not independently reproduced.
[^jina-v5-omni-report]: [jina-embeddings-v5-omni: Geometry-preserving Embeddings via Locked Aligned Towers](../raw/2605.08384_jina-embeddings-v5-omni/main.tex). Author technical report; its architecture claim was not independently reproduced.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
