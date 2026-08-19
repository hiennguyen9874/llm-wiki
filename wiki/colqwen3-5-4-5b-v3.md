---
type: Concept
title: ColQwen3.5-4.5B-v3
description: A 4.5B-parameter Qwen3.5-based visual document retrieval model using ColBERT-style late interaction and multilingual training data.
tags: [embedding, visual-document-retrieval, late-interaction, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:12:13Z }
sources:
  - id: colqwen35v3-card
    resource: ../raw/ColQwen3.5-4.5B-v3.md
    title: ColQwen3.5-4.5B-v3 model card
---

# ColQwen3.5-4.5B-v3

ColQwen3.5-4.5B-v3 is a BF16 visual-document retrieval model built on Qwen3.5-4B. It represents queries and document images as multi-vector embeddings and ranks them with ColBERT-style late interaction (MaxSim); the source describes it as a 4.5B-parameter model. [^colqwen35v3-card]

## Model architecture and size

- **Base model:** Qwen/Qwen3.5-4B vision-language model. [^colqwen35v3-card]
- **Retrieval architecture:** ColBERT-style late interaction / multi-vector embedding for visual document retrieval. The supplied usage scores query and document embeddings with MaxSim. [^colqwen35v3-card]
- **Reported model size:** 4.5B parameters; the captured ViDoRe V3 table reports 4.6B parameters and 8,660 MB memory. [^colqwen35v3-card]
- **Precision and adaptation:** BF16 with LoRA (`r=16`, `alpha=64`). [^colqwen35v3-card]
- **Embedding dimension:** the trained projection head and model configuration use 320 dimensions. The source cautions that a 128-dimension leaderboard column is a `colpali-engine` class-default artifact, not the model's actual output dimension. [^colqwen35v3-card]

## Language support

The model card lists English, French, German, Spanish, and Chinese. Its training data also includes an approximately 270K-pair multilingual set described as covering five languages; the source does not identify those five languages in the training-data section. [^colqwen35v3-card]

## Training data and procedure

The source reports approximately 776K training pairs from these datasets: [^colqwen35v3-card]

| Dataset | Reported pairs | Notes |
|---|---:|---|
| `vidore/colpali_train_set` | 127K | — |
| `openbmb/VisRAG-Ret-Train-Synthetic-data` | 239K | Synthetic retrieval data |
| `openbmb/VisRAG-Ret-Train-In-domain-data` | 123K | In-domain retrieval data |
| `llamaindex/vdr-multilingual-train` | ~270K | Five languages |
| `vidore/tatdqa_train` | ~13K | Finance |
| `Metric-AI/tabfquad_train_set` | ~1.5K | Tables |

Training comprised multi-objective hyperparameter search over ViDoRe V1+V3, three one-epoch full-training runs (seeds 42, 123, and 456), full-state-dictionary seed averaging, then a per-layer evolutionary model-soup merge with V2. The selected configuration used a cosine schedule, learning rate `4.57e-5`, 8% warmup, batch size 32, two hard negatives per sample, 0.197 dropout, and 0.02 weight decay. [^colqwen35v3-card]

## Benchmarks

### ViDoRe V3

On the source's captured ViDoRe V3 leaderboard snapshot (dated 2026-04-20), the model is ranked **#6** by Mean (Task), with nDCG@10 of **61.46** Mean (Task), **61.56** Mean (Public), and **61.06** Mean (Private). The same snapshot reports it as top three among 4B-class models. These rank-dependent figures can change as the live leaderboard receives submissions. [^colqwen35v3-card]

### ViDoRe V1+V2

The supplied V1+V2 nDCG@5 table ranks the model **#4**, with an average of **83.7**. Its listed scores include 91.9 on ArxivQA, 66.6 on DocVQA, 93.6 on InfoVQA, 95.9 on TabFQuAD, and 84.0 on TatDQA. The source identifies ESG and Econ as comparatively weak V2 areas and reports that the model is slightly below Ops-ColQwen3 and Nemotron variants on the V1+V2 average. [^colqwen35v3-card]

[^colqwen35v3-card]: [ColQwen3.5-4.5B-v3 model card](../raw/ColQwen3.5-4.5B-v3.md). Benchmarks and implementation details are reported by the model card; live leaderboard standings are time-sensitive.
