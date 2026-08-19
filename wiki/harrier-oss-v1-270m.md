---
type: Concept
title: harrier-oss-v1-270m
description: A 270M-parameter multilingual decoder-only embedding model with 640-dimensional, last-token-pooled normalized outputs and a reported 66.5 Multilingual MTEB v2 score.
tags: [embedding, retrieval, multilingual, decoder-only, harrier, microsoft]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: harrier-oss-v1-270m-card
    resource: ../raw/harrier-oss-v1-270m.md
    title: harrier-oss-v1 model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# harrier-oss-v1-270m

harrier-oss-v1-270m is Microsoft's 270M-parameter multilingual text-embedding model. It is a decoder-only model that produces 640-dimensional dense embeddings with last-token pooling and L2 normalization, accepts up to 32,768 tokens, and is intended for retrieval, clustering, semantic similarity, classification, bitext mining, and reranking. [^harrier-oss-v1-270m-card]

## Benchmarks

The model card reports a **66.5** score on Multilingual MTEB v2. It characterizes the harrier-oss-v1 family as state of the art on that benchmark at release; it does not provide the evaluation date, task-level scores, metric definition, or evaluation configuration in the card. [^harrier-oss-v1-270m-card]

A supplied leaderboard CSV ranks this model **8th of 45** with Mean (Task) **66.55** and Mean (TaskType) **56.90**. Its task-category scores are below; the CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 81.54 | 70.84 | 52.51 | -0.47 | 23.97 | 80.12 | 61.90 | 66.38 | 75.35 |

| harrier-oss-v1 variant | Parameters | Embedding dimension | Max tokens | Multilingual MTEB v2 score |
|---|---:|---:|---:|---:|
| 270m | 270M | 640 | 32,768 | 66.5 |
| 0.6b | 0.6B | 1,024 | 32,768 | 69.0 |
| 27b | 27B | 5,376 | 32,768 | 74.3 |

## Model size and architecture

- **Size and output:** 270M parameters and 640-dimensional embeddings; the maximum input length is 32,768 tokens. [^harrier-oss-v1-270m-card]
- **Architecture:** decoder-only; embeddings are the final non-padding token's hidden state (last-token pooling), then L2-normalized. [^harrier-oss-v1-270m-card]
- **Query formatting:** the card says queries require a one-sentence task instruction and documents do not; omitting the query instruction degrades performance. [^harrier-oss-v1-270m-card]

## Language support

The card declares multilingual support and lists 93 language codes in addition to `multilingual`: `af`, `am`, `ar`, `as`, `az`, `be`, `bg`, `bn`, `br`, `bs`, `ca`, `cs`, `cy`, `da`, `de`, `el`, `en`, `eo`, `es`, `et`, `eu`, `fa`, `fi`, `fr`, `fy`, `ga`, `gd`, `gl`, `gu`, `ha`, `he`, `hi`, `hr`, `hu`, `hy`, `id`, `is`, `it`, `ja`, `jv`, `ka`, `kk`, `km`, `kn`, `ko`, `ku`, `ky`, `la`, `lo`, `lt`, `lv`, `mg`, `mk`, `ml`, `mn`, `mr`, `ms`, `my`, `ne`, `nl`, `no`, `om`, `or`, `pa`, `pl`, `ps`, `pt`, `ro`, `ru`, `sa`, `sd`, `si`, `sk`, `sl`, `so`, `sq`, `sr`, `su`, `sv`, `sw`, `ta`, `te`, `th`, `tl`, `tr`, `ug`, `uk`, `ur`, `uz`, `vi`, `xh`, `yi`, and `zh`. The prose describes the list as non-exhaustive, so this is a declared coverage list rather than a quality guarantee for each language. [^harrier-oss-v1-270m-card]

## Training data and procedure

All harrier-oss-v1 models were trained with contrastive-learning objectives on a large-scale mixture of multilingual datasets covering diverse tasks. The 270M variant was additionally trained through knowledge distillation from larger embedding models. [^harrier-oss-v1-270m-card]

The card does not name the training datasets or teachers, or report corpus size, language/task mixture, sampling, filtering, licenses, training duration, or hyperparameters; it therefore does not support a more specific training-data account. [^harrier-oss-v1-270m-card]

[^harrier-oss-v1-270m-card]: [harrier-oss-v1 model card](../raw/harrier-oss-v1-270m.md). Architecture, capability, benchmark, language, and training claims are reported by the model card.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
