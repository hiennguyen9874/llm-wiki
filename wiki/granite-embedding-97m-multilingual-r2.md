---
type: Concept
title: Granite Embedding 97M Multilingual R2
description: A 97M-parameter ModernBERT bi-encoder for multilingual text and code retrieval, with 384-dimensional embeddings and a 32,768-token context window.
tags: [embedding, retrieval, multilingual, code, modernbert, granite]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:16:34Z }
sources:
  - id: granite-97m-r2-card
    resource: ../raw/Granite-Embedding-97M-Multilingual-R2.md
    title: Granite-Embedding-97M-Multilingual-R2 model card
---

# Granite Embedding 97M Multilingual R2

Granite Embedding 97M Multilingual R2 is IBM's 97M-parameter dense bi-encoder for multilingual text and code retrieval. It produces 384-dimensional, CLS-pooled embeddings from inputs up to 32,768 tokens; the supplied model card reports 60.3 on Multilingual MTEB Retrieval (18 tasks). [^granite-97m-r2-card]

## Benchmarks

The model card reports the following average benchmark scores (higher is better) and throughput. Throughput was measured on one NVIDIA H100 using a 512-token sliding-window setup; the card does not provide task-level results or further evaluation protocol details. [^granite-97m-r2-card]

| Benchmark | Score |
|---|---:|
| Multilingual MTEB Retrieval (18 tasks) | 60.3 |
| MTEB English Retrieval v2 (10 tasks) | 50.1 |
| MTEB Code v1 (12 tasks) | 60.4 |
| LongEmbed (6 tasks) | 65.5 |
| Reasoning as Retrieval, RaR-b (17 tasks) | 24.9 |
| Average across listed benchmarks | 52.2 |
| Throughput | 2,534 documents/s |

For context, the card compares this model's 60.3 multilingual-retrieval score with 48.1 for Granite Embedding 107M Multilingual, 52.2 for Granite Embedding 278M Multilingual, and 65.2 for the 311M Multilingual R2 model. It characterizes 60.3 as the highest score among open multilingual embedding models below 100M parameters and a 9.4-point lead over `multilingual-e5-small`; these comparative and leadership claims are self-reported, not independently verified here. [^granite-97m-r2-card]

## Model size and architecture

- **Size and output:** approximately 97M parameters and 384-dimensional vectors; it is about one-third the size of the 311M-parameter R2 counterpart. [^granite-97m-r2-card]
- **Encoder:** a dense ModernBERT bi-encoder with 12 transformer layers, 12 attention heads, a 1,536-dimensional intermediate layer, SiLU activations, and CLS pooling. [^granite-97m-r2-card]
- **Sequence and tokenizer:** supports sequences up to 32,768 tokens and uses a purpose-trained 180,000-token multilingual vocabulary. [^granite-97m-r2-card]
- **ModernBERT features:** alternating attention lengths, rotary position embeddings, and Flash Attention 2.0 support. [^granite-97m-r2-card]
- **Derivation:** the model was produced by pruning the 22-layer, 311M R2 model to 12 layers and reducing its vocabulary from 262,152 to 180,000 tokens, then continuing training. [^granite-97m-r2-card]

## Language and code support

The underlying encoder was pretrained on text in **more than 200 languages**. The card distinguishes this broad coverage from **enhanced retrieval support** for 52 languages—Arabic, Azerbaijani, Bengali, Bulgarian, Catalan, Chinese, Croatian, Czech, Danish, Dutch, English, Estonian, Finnish, French, Georgian, German, Greek, Hebrew, Hindi, Hungarian, Icelandic, Indonesian, Italian, Japanese, Kazakh, Khmer, Korean, Latvian, Lithuanian, Malay, Marathi, Norwegian, Persian, Polish, Portuguese, Romanian, Russian, Serbian, Slovak, Slovenian, Spanish, Swahili, Swedish, Tagalog, Telugu, Thai, Turkish, Ukrainian, Urdu, Uzbek, and Vietnamese—which receive explicit retrieval-pair and cross-lingual training. [^granite-97m-r2-card]

It is also trained for cross-lingual code retrieval in Python, Go, Java, JavaScript, PHP, Ruby, SQL, C, and C++. The source warns that lower-resource languages outside the enhanced-support set may have weaker retrieval quality through cross-lingual transfer, particularly in this smaller model. [^granite-97m-r2-card]

## Training data and procedure

The model card reports four training-data sources: unsupervised title–body pairs scraped from the web; publicly available paired data under permissive, enterprise-friendly licenses; IBM-internal paired data for technical domains; and IBM-generated multilingual synthetic data, including long-document pairs. It describes the corpus as commercially friendly and subject to technical, business, and governance data-clearance review; elsewhere it characterizes the data as permissively licensed open source plus select proprietary data. [^granite-97m-r2-card]

The card does not name the datasets, state corpus size or mixture proportions, identify collection dates, or provide a license-by-source inventory. It says base-language-model training data was filtered for hate, abuse, and profanity, while noting that filtering effectiveness can vary by language family. [^granite-97m-r2-card]

Training combined multi-teacher knowledge distillation with contrastive fine-tuning after pruning. The tokenizer was trained on code and text data spanning more than 200 languages. [^granite-97m-r2-card]

[^granite-97m-r2-card]: [Granite-Embedding-97M-Multilingual-R2 model card](../raw/Granite-Embedding-97M-Multilingual-R2.md). Architecture, training, language, and benchmark claims are reported by the model card.
