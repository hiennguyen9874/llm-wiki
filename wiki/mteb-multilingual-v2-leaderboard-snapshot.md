---
type: Benchmark
title: MTEB Multilingual v2 leaderboard snapshot
description: A 45-model CSV ranking snapshot for MTEB Multilingual v2, led by Qwen3-Embedding-4B at 69.45 Mean (Task).
tags: [benchmark, embedding, multilingual, mteb, leaderboard]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# MTEB Multilingual v2 leaderboard snapshot

This CSV snapshot ranks 45 embedding models on MTEB Multilingual v2. Qwen/Qwen3-Embedding-4B is rank 1 (69.45 Mean (Task)), followed by microsoft/harrier-oss-v1-0.6b at rank 2 (69.01) and codefuse-ai/F2LLM-v2-4B at rank 3 (67.06). The artifact does not identify its publisher, capture date, ranking method, evaluation configuration, metric definitions, task set, or model-inclusion criteria, so it supports comparison within this supplied snapshot—not a general or time-stable performance claim. [^mteb-multilingual-v2-summary]

## Ranking

| Rank | Model | Mean (Task) | Mean (TaskType) |
|---:|---|---:|---:|
| 1 | Qwen/Qwen3-Embedding-4B | 69.45 | 60.86 |
| 2 | microsoft/harrier-oss-v1-0.6b | 69.01 | 59.00 |
| 3 | codefuse-ai/F2LLM-v2-4B | 67.06 | 58.25 |
| 4 | jinaai/jina-embeddings-v5-omni-small | 67.00 | 58.90 |
| 5 | jinaai/jina-embeddings-v5-text-small | 67.00 | 58.90 |
| 6 | codefuse-ai/F2LLM-v2-1.7B | 65.21 | 56.78 |
| 7 | BidirLM/BidirLM-Omni-2.5B-Embedding | 63.50 | 55.48 |
| 8 | microsoft/harrier-oss-v1-270m | 66.55 | 56.90 |
| 9 | Qwen/Qwen3-Embedding-0.6B | 64.34 | 56.01 |
| 10 | jinaai/jina-embeddings-v5-omni-nano | 65.52 | 57.66 |
| 11 | jinaai/jina-embeddings-v5-text-nano | 65.52 | 57.66 |
| 12 | BidirLM/BidirLM-1.7B-Embedding | 63.54 | 55.39 |
| 13 | ICT-TIME-and-Querit/ICT-TIME-and-Querit-embedding-v1 | 63.78 | 55.02 |
| 14 | intfloat/multilingual-e5-large-instruct | 63.22 | 55.09 |
| 15 | BidirLM/BidirLM-1B-Embedding | 63.21 | 54.84 |
| 16 | ICT-TIME-and-Querit/BOOM_4B_v1 | 63.52 | 54.81 |
| 17 | codefuse-ai/F2LLM-v2-0.6B | 62.74 | 55.02 |
| 18 | google/embeddinggemma-300m | 61.15 | 54.31 |
| 19 | Alibaba-NLP/gte-Qwen2-1.5B-instruct | — | 62.51 |
| 20 | Lajavaness/bilingual-embedding-large | — | 73.55 |
| 21 | BidirLM/BidirLM-0.6B-Embedding | 60.42 | 52.85 |
| 22 | codefuse-ai/F2LLM-v2-330M | 60.84 | 53.27 |
| 23 | NovaSearch/stella_en_1.5B_v5 | 56.53 | 49.96 |
| 24 | NovaSearch/jasper_en_vision_language_v1 | — | 60.63 |
| 25 | OrdalieTech/Solon-embeddings-large-0.1 | — | 76.10 |
| 26 | jinaai/jina-embeddings-v3 | 58.37 | 50.66 |
| 27 | BAAI/bge-m3 | — | 60.35 |
| 28 | intfloat/multilingual-e5-large | — | 73.81 |
| 29 | Alibaba-NLP/gte-multilingual-base | — | 71.79 |
| 30 | HIT-TMG/KaLM-embedding-multilingual-mini-v1 | — | 64.77 |
| 31 | Lajavaness/bilingual-embedding-base | — | 69.98 |
| 32 | nomic-ai/nomic-embed-text-v2-moe | 57.64 | 49.57 |
| 33 | hotchpotch/bekko-embedding-v1-a25m | 58.36 | 51.12 |
| 34 | HIT-TMG/KaLM-embedding-multilingual-mini-instruct-v1 | — | 64.22 |
| 35 | manu/bge-m3-custom-fr | — | 72.16 |
| 36 | codefuse-ai/F2LLM-v2-160M | 57.98 | 50.61 |
| 37 | Snowflake/snowflake-arctic-embed-l-v2.0 | 57.03 | 49.95 |
| 38 | Lajavaness/bilingual-embedding-small | — | 69.48 |
| 39 | BidirLM/BidirLM-270M-Embedding | 56.81 | 49.30 |
| 40 | zeroentropy/zembed-1 | 56.58 | 49.96 |
| 41 | hotchpotch/bekko-embedding-v1-a8m | 56.73 | 50.05 |
| 42 | intfloat/multilingual-e5-base | 57.02 | 49.82 |
| 43 | intfloat/multilingual-e5-small | — | 69.40 |
| 44 | ibm-granite/granite-embedding-311m-multilingual-r2 | 55.96 | 49.35 |
| 45 | deepvk/USER-bge-m3 | — | — |

An em dash represents `NA` or an empty value in the CSV. The table's non-monotonic ranks among rows with missing Mean (Task) values show that the ranking cannot be reconstructed from the two displayed aggregates alone. [^mteb-multilingual-v2-summary]

## Covered concepts

The snapshot supplies task-category scores for [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md), [harrier-oss-v1-270m](harrier-oss-v1-270m.md), [Jina Embeddings v5 Text Small](jina-embeddings-v5-text-small.md), [Jina Embeddings v5 Text Nano](jina-embeddings-v5-text-nano.md), [EmbeddingGemma 300M](embeddinggemma-300m.md), and [Granite Embedding 311M Multilingual R2](granite-embedding-311m-multilingual-r2.md). It does not provide enough model-card detail to create standalone concepts for the other listed models.

[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). This is an unauthenticated supplied ranking artifact; model metadata and scores are reproduced as reported.