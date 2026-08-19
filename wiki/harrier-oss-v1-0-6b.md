---
type: Concept
title: harrier-oss-v1-0.6b
description: A 0.6B-parameter multilingual decoder-only embedding model with 1,024-dimensional, last-token-pooled normalized outputs and a reported 69.0 Multilingual MTEB v2 score.
tags: [embedding, retrieval, multilingual, decoder-only, harrier, microsoft]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: harrier-oss-v1-0-6b-card
    resource: ../raw/harrier-oss-v1-0.6b.md
    title: harrier-oss-v1 model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# harrier-oss-v1-0.6b

harrier-oss-v1-0.6b is Microsoft's 0.6B-parameter multilingual text-embedding model. It is a decoder-only model that produces 1,024-dimensional dense embeddings with last-token pooling and L2 normalization, accepts up to 32,768 tokens, and is intended for retrieval, clustering, semantic similarity, classification, bitext mining, and reranking. [^harrier-oss-v1-0-6b-card]

## Benchmarks

The model card reports a **69.0** score on Multilingual MTEB v2. It characterizes the harrier-oss-v1 family as state of the art on that benchmark at release; it does not provide the evaluation date, task-level scores, metric definition, or evaluation configuration in the card. [^harrier-oss-v1-0-6b-card]

A supplied leaderboard CSV ranks this model **2nd of 45** with Mean (Task) **69.01** and Mean (TaskType) **59.00**. Its task-category scores are below; the CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 82.85 | 73.88 | 54.00 | 0.81 | 26.37 | 82.07 | 63.16 | 70.75 | 77.09 |

| harrier-oss-v1 variant | Parameters | Embedding dimension | Max tokens | Multilingual MTEB v2 score |
|---|---:|---:|---:|---:|
| 270m | 270M | 640 | 32,768 | 66.5 |
| 0.6b | 0.6B | 1,024 | 32,768 | 69.0 |
| 27b | 27B | 5,376 | 32,768 | 74.3 |

## Model size and architecture

- **Size and output:** 0.6B parameters and 1,024-dimensional embeddings; the maximum input length is 32,768 tokens. [^harrier-oss-v1-0-6b-card]
- **Architecture:** decoder-only; embeddings are the final non-padding token's hidden state (last-token pooling), then L2-normalized. [^harrier-oss-v1-0-6b-card]
- **Query formatting:** the card says queries require a one-sentence task instruction and documents do not; omitting the query instruction degrades performance. [^harrier-oss-v1-0-6b-card]

## Language support

The card declares multilingual support and lists 93 language codes in addition to `multilingual`: `af`, `am`, `ar`, `as`, `az`, `be`, `bg`, `bn`, `br`, `bs`, `ca`, `cs`, `cy`, `da`, `de`, `el`, `en`, `eo`, `es`, `et`, `eu`, `fa`, `fi`, `fr`, `fy`, `ga`, `gd`, `gl`, `gu`, `ha`, `he`, `hi`, `hr`, `hu`, `hy`, `id`, `is`, `it`, `ja`, `jv`, `ka`, `kk`, `km`, `kn`, `ko`, `ku`, `ky`, `la`, `lo`, `lt`, `lv`, `mg`, `mk`, `ml`, `mn`, `mr`, `ms`, `my`, `ne`, `nl`, `no`, `om`, `or`, `pa`, `pl`, `ps`, `pt`, `ro`, `ru`, `sa`, `sd`, `si`, `sk`, `sl`, `so`, `sq`, `sr`, `su`, `sv`, `sw`, `ta`, `te`, `th`, `tl`, `tr`, `ug`, `uk`, `ur`, `uz`, `vi`, `xh`, `yi`, and `zh`. The prose describes the list as non-exhaustive, so this is a declared coverage list rather than a quality guarantee for each language. [^harrier-oss-v1-0-6b-card]

## Training data and procedure

All harrier-oss-v1 models were trained with contrastive-learning objectives on a large-scale mixture of multilingual datasets covering diverse tasks. The 0.6B variant was additionally trained through knowledge distillation from larger embedding models. [^harrier-oss-v1-0-6b-card]

The card does not name the training datasets or teachers, or report corpus size, language/task mixture, sampling, filtering, licenses, training duration, or hyperparameters; it therefore does not support a more specific training-data account. [^harrier-oss-v1-0-6b-card]

[^harrier-oss-v1-0-6b-card]: [harrier-oss-v1 model card](../raw/harrier-oss-v1-0.6b.md). Architecture, capability, benchmark, language, and training claims are reported by the model card.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
