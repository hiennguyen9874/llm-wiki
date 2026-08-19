---
type: Concept
title: Vintern-Embedding-1B
description: A reported 0.9B-parameter Vietnamese, English, and Chinese multimodal multi-vector embedding model built on Vintern-1B-v3_5 and trained on more than 1.5M VQA and text-QA pairs.
tags: [embedding, retrieval, multimodal, late-interaction, vietnamese, chinese, english]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:42:36Z }
sources:
  - id: vintern-embedding-1b-card
    resource: ../raw/Vintern-Embedding-1B.md
    title: Vintern-Embedding-1B model card
---

# Vintern-Embedding-1B

Vintern-Embedding-1B is a reported 0.9B-parameter multimodal, multi-vector embedding model built on `5CD-AI/Vintern-1B-v3_5`. The model card describes text-to-visual and text-to-text retrieval, and reports training on more than 1.5 million VQA and pure-text QA question–document pairs. [^vintern-embedding-1b-card]

## Benchmarks

All results below are self-reported by the model card; it supplies benchmark tables but no evaluation configuration or independent validation. [^vintern-embedding-1b-card]

| Benchmark | Reported Vintern-Embedding-1B result | Comparison context stated in the card |
|---|---:|---|
| GreenNode Table Markdown Retrieval (Vietnamese) | MAP@5 57.01; MRR@5 57.01; NDCG@5 59.17; Recall@5 65.65; Mean 59.71 | The table's highest listed Mean; its comparators include multilingual, Vietnamese, and GreenNode embedding models. |
| GreenNode Zalo Legal Text Retrieval (Vietnamese) | MAP@5 68.90; MRR@5 69.06; NDCG@5 72.32; Recall@5 82.29; Mean 73.14 | Below the table's M3-GN-VN-Mixed Mean of 74.95 and M3-Embedding Mean of 74.67; above its other listed models. |
| ViDoRe Benchmark | Average Score 82.85 | Above the listed ColVintern-1B score of 78.8; below all listed 2.2B–8.3B alternatives. |

For the ViDoRe table, the reported domain scores are 75.37 (ArxivQA), 51.79 (DocVQA), 86.20 (InfoVQA), 97.52 (Artificial Intelligence), 93.19 (Energy), 93.97 (Government), 97.09 (Healthcare Industry), and 67.72 (TAT-DQA). [^vintern-embedding-1b-card]

## Model size and architecture

- **Size:** approximately 0.9B parameters. [^vintern-embedding-1b-card]
- **Base model:** `5CD-AI/Vintern-1B-v3_5`. [^vintern-embedding-1b-card]
- **Retrieval architecture:** multimodal multi-vector embeddings for text queries against images or text documents. The supplied inference uses `score_multi_vector` to compare query vectors with image and text-document vectors. [^vintern-embedding-1b-card]
- **Unspecified details:** the source does not state the embedding dimension, pooling or late-interaction mechanism, vision encoder, context limit, or fine-tuning procedure. [^vintern-embedding-1b-card]

## Language support

The card metadata lists Vietnamese (`vi`), English (`en`), and Chinese (`zh`). Its narrative specifically identifies English and Vietnamese retrieval applications; it does not provide per-language performance, support criteria, or an explicit Chinese capability description. [^vintern-embedding-1b-card]

## Training data

The card reports more than **1.5 million high-quality question–document pairs** spanning Visual Question Answering (VQA) and pure-text QA. It characterizes the set as large and diverse but does not name the datasets, give modality or language proportions, describe data collection, filtering, licensing, decontamination, or disclose a training recipe. [^vintern-embedding-1b-card]

[^vintern-embedding-1b-card]: [Vintern-Embedding-1B model card](../raw/Vintern-Embedding-1B.md). Model size, architecture, languages, training-data total, and benchmark results are reported by the model card.
