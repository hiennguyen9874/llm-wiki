---
type: Concept
title: Nemotron-3-Embed-8B-BF16
description: An approximately 8B-parameter Ministral-3-8B-based multilingual text embedding encoder with 4,096-dimensional mean-pooled outputs and self-reported 78.46 RTEB NDCG@10.
tags: [embedding, retrieval, multilingual, nemotron, nvidia, ministral]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:36:06Z }
sources:
  - id: nemotron-3-embed-8b-card
    resource: ../raw/Nemotron-3-Embed-8B.md
    title: Nemotron-3-Embed-8B-BF16 model card
---

# Nemotron-3-Embed-8B-BF16

Nemotron-3-Embed-8B-BF16 is NVIDIA's multilingual dense text-embedding model for retrieval and semantic similarity. It is an approximately 8B-parameter, `Ministral-3-8B-Instruct-2512`-based transformer encoder that applies bidirectional attention and average pooling to produce L2-normalized 4,096-dimensional embeddings. [^nemotron-3-embed-8b-card]

## Benchmarks

The model card reports chunk-retrieval average NDCG@10 scores with the model sequence length set to 4,096 tokens. It evaluates the model on 16 public Retrieval Embedding Benchmark (RTEB) tasks, MMTEB Retrieval datasets, and OCR-extracted text from eight ViDoRe-V3 datasets. These are model-card-reported results, not independently reproduced measurements. [^nemotron-3-embed-8b-card]

| Benchmark | NDCG@10 |
|---|---:|
| RTEB 16 | 78.46 |
| ViDoRe-V3 text | 60.60 |
| MMTEB (Retrieval) | 75.45 |

The model card also claims state-of-the-art performance on the multilingual RTEB leaderboard as of July 16, 2026. That is a time-bound, self-reported leaderboard assertion. [^nemotron-3-embed-8b-card]

## Model size and architecture

- **Parameters:** approximately 8B. [^nemotron-3-embed-8b-card]
- **Backbone:** `mistralai/Ministral-3-8B-Instruct-2512`, adapted as an encoder model. [^nemotron-3-embed-8b-card]
- **Encoder and pooling:** Transformer with bidirectional attention masking; average pooling over token-level representations. [^nemotron-3-embed-8b-card]
- **Dimensions and context:** hidden size and output dimension are 4,096; maximum input length is 32,768 tokens. Embeddings can be prefix-sliced to smaller dimensions and L2-renormalized. [^nemotron-3-embed-8b-card]

## Language support

The card describes the model as multilingual with multilingual and cross-lingual retrieval capability. It was evaluated across 34 languages: English, Arabic, Assamese, Bengali, Bulgarian, Chinese, Danish, Dutch, Finnish, French, German, Hindi, Hinglish, Indonesian, Italian, Japanese, Korean, Malay, Marathi, Nepali, Norwegian, Persian, Portuguese, Romanian, Russian, Spanish, Swahili, Swedish, Tamil, Telugu, Thai, Ukrainian, Urdu, and Vietnamese. Evaluation coverage does not guarantee equivalent quality in every language. [^nemotron-3-embed-8b-card]

## Training data

The model card reports more than **50M text training samples**. Training used publicly available, commercially permissible datasets plus synthetic data; collection and labeling are characterized as a hybrid of human, automated, and synthetic methods. [^nemotron-3-embed-8b-card]

Named public sources include MIRACL, MLDR, HotpotQA, NQ, SQuAD, Stack Exchange, HoVer, TAT-QA, FinQA, PubMedQA, MedQuAD, JaQuAD, CoIR retrieval datasets, SWE-bench, MLQA, SpartQA, Winogrande, TempReason, PAQ, Wikipedia, CCNews, S2ORC, and Reddit. FinePdfs, CentralActs, BRIGHT, and MultiHiertt were seed datasets for synthetic pairs. [^nemotron-3-embed-8b-card]

Synthetic query–document pairs were generated from scratch or from seed data using listed Qwen, Gemma, GPT-OSS, and NVIDIA Nemotron generative models. The source does not disclose mixture proportions, language distribution, filtering procedures, or a license-by-dataset inventory. [^nemotron-3-embed-8b-card]

[^nemotron-3-embed-8b-card]: [Nemotron-3-Embed-8B-BF16 model card](../raw/Nemotron-3-Embed-8B.md). Architecture, training-data, language, and benchmark claims are reported by the model card; linked external datasets and benchmark materials were not independently inspected.
