---
type: Concept
title: F2LLM-v2
description: An eight-size, Qwen3-based multilingual embedding family trained on a reported 60 million samples in 282 natural and 40+ programming languages.
tags: [embedding, retrieval, multilingual, instruction-tuned, matryoshka]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:58:31Z }
sources:
  - id: f2llm-v2-report
    resource: ../raw/2603.19223_F2LLM-v2/main.tex
    title: F2LLM-v2 technical-report LaTeX source
---

# F2LLM-v2

F2LLM-v2 is a reported family of eight Qwen3-based decoder embedding models, from 80M to 14B parameters. The authors report training it on 60 million samples from 157 public sources, covering 282 natural languages and more than 40 programming languages; the family uses EOS-token representations, Matryoshka Representation Learning (MRL), and a two-stage contrastive-training pipeline. [^f2llm-v2-report]

## Models and representation

| Model size | Total parameters | Hidden size | Layers | Full embedding dimension |
|---|---:|---:|---:|---:|
| 80M | 80M | 320 | 8 | 320 |
| 160M | 159M | 640 | 9 | 640 |
| 330M | 334M | 896 | 16 | 896 |
| 0.6B | 596M | 1,024 | 28 | 1,024 |
| 1.7B | 1,721M | 2,048 | 28 | 2,048 |
| 4B | 4,022M | 2,560 | 36 | 2,560 |
| 8B | 7,568M | 4,096 | 36 | 4,096 |
| 14B | 13,990M | 5,120 | 40 | 5,120 |

The 0.6B through 14B models directly correspond to Qwen3 LLMs; the 80M, 160M, and 330M variants are pruned from the 0.6B model. MRL is applied in both training stages with a minimum dimension of 8, so embeddings can be truncated. [^f2llm-v2-report]

## Data and training

The reported corpus consolidates heterogeneous source data into retrieval, clustering, and two-way-classification formats. Retrieval tuples use in-batch negatives and supplied hard negatives mined with Qwen3-Embedding-8B; clustering and two-way classification use hard negatives only to avoid in-batch false negatives. The corpus is numerically dominated by English (16.1M samples; 28.7%) and Chinese (4.3M; 7.7%), while also including a long tail of languages and code. [^f2llm-v2-report]

- **Stage 1:** Five models from 0.6B through 14B are trained without instructional prefixes on 27M samples from seven broad, large retrieval datasets.
- **Stage 2:** A mixture capped at 80,000 queries per source produces 18M samples. Queries receive task-specific instructions; in symmetric tasks, 30% of documents and negatives also receive instructions.
- **Pruning and distillation:** The three sub-0.6B variants are pruned in width, MLP size, and layers after stage 1. During training, students minimize MSE to their teacher's embeddings over queries, documents, and negatives; the authors also apply this loss to 0.6B and 1.7B in stage 2. [^f2llm-v2-report]

On the authors' 350-task ablation subset, distillation raises reported averages from 53.37 to 58.04 (80M), 56.27 to 60.53 (160M), 62.77 to 64.55 (330M), 65.87 to 66.72 (0.6B), and 68.58 to 69.13 (1.7B). [^f2llm-v2-report]

## Evaluation

The report evaluates the family on 17 MTEB benchmarks comprising 430 tasks across ten task types. It reports that the 14B model scores 68.74 on Multilingual MTEB and 71.72 in the table's unqualified average column; its 4B, 1.7B, 0.6B, 330M, and 160M scores on Multilingual are 67.06, 65.21, 62.74, 60.84, and 57.98, respectively. The leaderboard ranks in the table were accessed on 2026-03-19. [^f2llm-v2-report]

## Contradictions

- The report prose says the 14B model is state of the art on 11 of 17 benchmarks, but its results table assigns it rank 1 on ten: Code, European, Scandinavian, Indic, German, Polish, Japanese, Dutch, Persian, and Vietnamese. The source does not explain the discrepancy. [^f2llm-v2-report]

## Relationships

- **Includes:** [F2LLM-v2-14B](f2llm-v2-14b.md), the family member with an independently supplied model card.

[^f2llm-v2-report]: [F2LLM-v2 technical-report LaTeX source](../raw/2603.19223_F2LLM-v2/main.tex). Training, architecture, and performance are author-reported; this source does not independently verify them.
