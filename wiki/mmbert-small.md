---
type: Concept
title: mmBERT-small
description: A 140M-parameter ModernBERT-based multilingual masked-language encoder covering 1,800+ languages, with an 8,192-token context window and 256,000-token Gemma 2 vocabulary.
tags: [encoder, multilingual, masked-language-modeling, embedding, retrieval, modernbert]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:33:53Z }
sources:
  - id: mmbert-small-card
    resource: ../raw/mmBERT-small.md
    title: mmBERT-small model card
---

# mmBERT-small

mmBERT-small is a 140M-parameter multilingual bidirectional encoder trained with masked-language modeling. It uses a ModernBERT-based architecture and is presented for classification, embeddings, and retrieval, but the source supplies no benchmark score table for the small checkpoint. [^mmbert-small-card]

## Benchmarks

The model card claims that the mmBERT family outperforms prior multilingual encoders such as XLM-R on classification, embedding, and retrieval tasks. However, it reports no benchmark names, scores, evaluation configurations, comparisons, or small-checkpoint-specific results. That claim therefore cannot be used to compare mmBERT-small quantitatively from this source. [^mmbert-small-card]

## Model size and architecture

- **Parameters:** 140M total parameters, including 42M non-embedding parameters. [^mmbert-small-card]
- **Transformer configuration:** 22 layers, 384 hidden size, 1,152 intermediate size, and 6 attention heads. [^mmbert-small-card]
- **Context and tokenizer:** 8,192-token maximum sequence length; 256,000-token vocabulary using the Gemma 2 tokenizer. [^mmbert-small-card]
- **Encoder design:** ModernBERT-based bidirectional attention with a masked-language-modeling objective. The card also names Flash Attention 2 and unpadding as architecture/implementation features. [^mmbert-small-card]

## Language support

The card describes mmBERT-small as covering **1,800+ languages**. Its frontmatter enumerates 1,811 distinct language codes, while its decay-training description says all **1,833 languages** were included. The source does not explain the discrepancy, specify which count applies to the released checkpoint, or provide per-language quality measures. [^mmbert-small-card]

## Training data

The card describes a public multilingual corpus of **3T+ tokens** assembled from filtered DCLM (English), FineWeb2 and FineWeb2-HQ, MegaWika/Wikipedia, StarCoder and ProLong code, ArXiv and PeS2o academic material, and StackExchange. [^mmbert-small-card]

| Training phase | Stated coverage | Stated volume |
|---|---|---:|
| Pre-training P1 | 60 languages; foundational data | 2.3T tokens |
| Pre-training P2 | Extension data | Not stated |
| Pre-training P3 | Final pre-training data | Not stated |
| Mid-training | 110 languages; context extension to 8K | 600B tokens |
| Decay phase | 1,833 languages; premium-quality data | 100B tokens |

Training progressively adds languages (60, then 110, then all stated decay languages). The source also describes reducing the mask ratio from 30% to 15% to 5% and changing temperature sampling from τ=0.7 to τ=0.3 across phases. It does not give mixture proportions by data source or language, collection dates, licenses, filtering details, or an independent corpus audit. [^mmbert-small-card]

[^mmbert-small-card]: [mmBERT-small model card](../raw/mmBERT-small.md). All model, architecture, coverage, training-data, and performance claims are reported by the model card.
