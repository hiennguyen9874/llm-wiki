---
type: Concept
title: Granite Embedding 311M Multilingual R2
description: A 311M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 768-dimensional Matryoshka embeddings and a 32,768-token context window.
tags: [embedding, retrieval, multilingual, code, modernbert, granite]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:47:55Z }
sources:
  - id: granite-311m-r2-card
    resource: ../raw/granite-embedding-311m-multilingual-r2.md
    title: Granite-Embedding-311M-Multilingual-R2 model card
  - id: mteb-multilingual-v2-summary
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    title: MTEB Multilingual v2 summary CSV
---

# Granite Embedding 311M Multilingual R2

Granite Embedding 311M Multilingual R2 is IBM's 311M-parameter dense ModernBERT bi-encoder for multilingual text and code retrieval. It produces 768-dimensional, CLS-pooled embeddings from inputs up to 32,768 tokens; the supplied model card reports 65.2 on Multilingual MTEB Retrieval (18 tasks). [^granite-311m-r2-card]

## Benchmarks

The model card reports the following average scores (higher is better). Throughput was measured on a single NVIDIA H100 GPU with batches of 1,024 sequences at 512 tokens; it does not provide task-level results or further evaluation protocol details. [^granite-311m-r2-card]

| Benchmark | Score |
|---|---:|
| Multilingual MTEB Retrieval (18 tasks) | 65.2 |
| MTEB English Retrieval v2 (10 tasks) | 52.6 |
| MTEB Code v1 (12 tasks) | 63.8 |
| LongEmbed (6 tasks) | 71.7 |
| Reasoning as Retrieval, RaR-b (17 tasks) | 28.0 |
| Average across listed benchmarks | 56.3 |
| Throughput | 1,828 documents/s |

The card calls the 65.2 multilingual-retrieval result a 13-point improvement over Granite Embedding 278M Multilingual (52.2), and the 56.3 average a 14.5-point improvement over that predecessor. It also describes the model as top-three in the under-500M multilingual class across the listed retrieval, code, long-document, and reasoning benchmarks. These are self-reported comparative claims, not independently verified here. [^granite-311m-r2-card]

The card's separate Matryoshka table labels a seemingly corresponding “ML MTEB Retrieval” metric as 63.9 at 768 dimensions (and 63.9, 63.8, 63.5, and 62.5 at 512, 384, 256, and 128 dimensions). It does not explain why this conflicts with the 65.2 main-table score, so the benchmark figures should not be treated as directly reconciled. [^granite-311m-r2-card]

A supplied leaderboard CSV ranks the model **44th of 45** with Mean (Task) **55.96** and Mean (TaskType) **49.35**. Its Retrieval score (**65.21**) is consistent to rounding with the card's 65.2 main-table score, but the CSV does not document evaluation configuration or metric definitions. [^mteb-multilingual-v2-summary]

| Bitext mining | Classification | Clustering | Instruction reranking | Multilabel classification | Pair classification | Reranking | Retrieval | STS |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 57.92 | 53.34 | 44.42 | -2.42 | 18.50 | 76.11 | 61.99 | 65.21 | 69.05 |

## Model size and architecture

- **Size and output:** approximately 311M parameters; 768-dimensional embeddings, optionally truncated with Matryoshka Representation Learning to 512, 384, 256, or 128 dimensions. [^granite-311m-r2-card]
- **Encoder:** a dense ModernBERT bi-encoder with 22 transformer layers, 12 attention heads, a 1,152-dimensional intermediate size, GeGLU activations, and CLS pooling. [^granite-311m-r2-card]
- **Sequence and tokenizer:** supports inputs up to 32,768 tokens and uses a 262,152-token multilingual vocabulary. [^granite-311m-r2-card]
- **ModernBERT features:** alternating attention lengths, rotary position embeddings, Flash Attention 2.0 support, and streamlined removal of unnecessary bias terms. [^granite-311m-r2-card]

## Language and code support

The underlying encoder was pretrained on text in **more than 200 languages**. The card distinguishes that broad pretraining coverage from **enhanced retrieval support** for 52 languages—Albanian, Arabic, Azerbaijani, Bengali, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Georgian, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kazakh, Khmer, Korean, Latvian, Lithuanian, Malay, Marathi, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Telugu, Thai, Turkish, Ukrainian, Urdu, Uzbek, and Vietnamese—which receive explicit retrieval-pair and cross-lingual training. [^granite-311m-r2-card]

It is also trained for cross-lingual code retrieval in Python, Go, Java, JavaScript, PHP, Ruby, SQL, C, and C++. The card cautions that lower-resource languages outside the enhanced-support set may have weaker retrieval quality through cross-lingual transfer. [^granite-311m-r2-card]

## Training data and procedure

The card reports four training-data sources: unsupervised title–body pairs scraped from the web; publicly available paired data under permissive, enterprise-friendly licenses; IBM-internal paired data for technical domains; and IBM-generated multilingual synthetic data, including long-document pairs. It describes the data as subject to technical, business, and governance clearance review, and says base-language-model training data was filtered for hate, abuse, and profanity, while noting that filtering effectiveness may vary by language family. [^granite-311m-r2-card]

The source says the training data is commercially friendly and elsewhere characterizes it as permissively licensed open-source data plus select proprietary data. It does not name datasets, give corpus size, mixture proportions, collection dates, or a license-by-source inventory. [^granite-311m-r2-card]

Training combined multi-teacher knowledge distillation, contrastive fine-tuning, model merging, and Matryoshka Representation Learning. The tokenizer was derived from Google's Gemma 3 tokenizer and further trained on multilingual text and code spanning more than 200 languages. [^granite-311m-r2-card]

[^granite-311m-r2-card]: [Granite-Embedding-311M-Multilingual-R2 model card](../raw/granite-embedding-311m-multilingual-r2.md). Architecture, training, language, and benchmark claims are reported by the model card.
[^mteb-multilingual-v2-summary]: [MTEB Multilingual v2 summary CSV](../raw/MTEB_Multilingual_v2_summary.csv). Supplied leaderboard scores; the artifact does not document its evaluation protocol.
