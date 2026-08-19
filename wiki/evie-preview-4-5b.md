---
type: Concept
title: EVIE-Preview-4.5B
description: A 4.54B-parameter Qwen3.5-based multilingual visual-document retriever producing native 128-dimensional token embeddings for MaxSim late interaction.
tags: [embedding, visual-document-retrieval, multimodal, late-interaction, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T09:53:52Z }
sources:
  - id: evie-card
    resource: ../raw/EVIE-Preview-4.5B.md
    title: EVIE-Preview-4.5B model card
---

# EVIE-Preview-4.5B

EVIE-Preview-4.5B is a multilingual visual-document retrieval model built on Qwen3.5-4B. It encodes text queries and document images into native 128-dimensional token vectors and scores them with MaxSim late interaction. The model card reports 4.54B parameters and first-place results on its presented ViDoRe V3 and combined V1+V2 tables. [^evie-card]

## Benchmarks

The model card reports the following public ViDoRe results; these are author-reported measurements and rank claims rather than independently verified standings. Comparison rows in the V3 table are vendor-published scores. [^evie-card]

| Benchmark | Metric | Configuration | Reported score | Reported standing |
|---|---|---|---:|---|
| ViDoRe V3 public | nDCG@10 | 768 visual tokens/page | 64.56 | — |
| ViDoRe V3 public | nDCG@10 | 1,792 visual tokens/page | 65.36 | #1 |
| ViDoRe V1 | nDCG@5 | 10 tasks | 91.73 | — |
| ViDoRe V2 | nDCG@5 | 4 tasks | 70.87 | — |
| ViDoRe V1+V2 | nDCG@5 | 14 tasks | 85.77 | #1 |

The model was trained with 768 visual tokens per page. The card characterizes the 1,792-token V3 result as test-time extrapolation using the same checkpoint; it reports a gain of 0.80 nDCG@10 and improvement in seven of eight domains. V3 covers eight public domains and six query languages. [^evie-card]

## Model size

- **Parameters:** 4.54B. [^evie-card]
- **Checkpoint:** 8.5 GB in BF16. [^evie-card]
- **Token-vector dimension:** native 128D. [^evie-card]
- **Visual-token budgets:** 768 (training/default) and 1,792 (test-time extrapolation). [^evie-card]

## Model architecture

- **Backbone:** Qwen/Qwen3.5-4B vision-language model, described as using interleaved GatedDeltaNet linear-attention and full-attention layers. [^evie-card]
- **Attention behavior:** full-attention layers are made bidirectional for retrieval; GatedDeltaNet layers remain recurrent. [^evie-card]
- **Projection:** contextual query and document token states are projected directly to 128-dimensional representations. [^evie-card]
- **Retrieval:** ColQwen3_5/ColPali-style multi-vector encoding with token-level MaxSim late interaction between text-query tokens and visual-document tokens. [^evie-card]
- **Document representation:** dynamic vision encoding supports page images containing charts, tables, reports, filings, and scanned forms. [^evie-card]

## Language support

The card explicitly states query support for **English, French, German, Italian, Spanish, Portuguese, and Chinese**. It also says these queries can retrieve Japanese-language pages, but does not claim Japanese query support. The ViDoRe V3 evaluation is described as using six query languages; the source does not identify which six in the benchmark section. [^evie-card]

## Training data

The model card reports approximately **0.8 million high-quality image-query pairs** spanning multilingual documents, technical reports, complex financial tables, infographics, and document visual-question-answering material. It does not identify the component datasets, language distribution, collection dates, licenses, or mixture proportions. Although the card frontmatter names ViDoRe benchmark datasets, it does not state that they were training sources; they should therefore be treated as evaluation resources rather than confirmed training data. [^evie-card]

For hard-negative preparation, a large multimodal judge re-evaluated mined candidates: answer-bearing candidates became positives, partially relevant or ambiguous candidates were excluded from the loss, and only strictly irrelevant pages remained negatives. Multi-positive examples were group-weighted by `1/positive_count`; rows with empty queries, corrupted images, or degraded text were dropped. [^evie-card]

## Relationships

- **Built on:** Qwen3.5-4B, also used as the backbone of [ColQwen3.5-4.5B-v3](colqwen3-5-4-5b-v3.md); both are visual-document retrievers using late interaction, but their reported projection dimensions and training recipes differ. [^evie-card]

[^evie-card]: [EVIE-Preview-4.5B model card](../raw/EVIE-Preview-4.5B.md). Model size, architecture, language support, training data, benchmark scores, and rank claims are reported by the model card and have not been independently verified here.
