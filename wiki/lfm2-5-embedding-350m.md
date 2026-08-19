---
type: Concept
title: LFM2.5-Embedding-350M
description: A 354M-parameter multilingual dense bi-encoder built from LFM2.5-350M-Base, producing one 1,024-dimensional CLS vector per input and scored with cosine similarity.
tags: [embedding, retrieval, dense-retrieval, bi-encoder, multilingual, liquid]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:30:07+07:00 }
sources:
  - id: lfm25-embedding-card
    resource: ../raw/LFM2.5-Embedding-350M.md
    title: LFM2.5-Embedding-350M model card
---

# LFM2.5-Embedding-350M

LFM2.5-Embedding-350M is Liquid AI's approximately 354M-parameter multilingual dense retrieval bi-encoder. It is built on LFM2.5-350M-Base with bidirectional patches, emits one 1,024-dimensional CLS vector per input, and uses cosine similarity for retrieval across 11 stated languages. [^lfm25-embedding-card]

## Benchmarks

The vendor model card reports aggregate results on multilingual and cross-lingual retrieval benchmarks; these results have not been independently reproduced here, and the card does not supply evaluation-protocol details beyond the metrics, datasets, and language breakdowns. [^lfm25-embedding-card]

| Benchmark | Metric | Reported average | Comparison in displayed table |
|---|---|---:|---|
| NanoBEIR Multilingual Extended | NDCG@10 | 0.577 | Highest displayed dense-model average; the source's 0.605 late-interaction sibling is higher overall |
| MKQA-11 | Recall@20 | 0.691 | Highest displayed dense-model average; the source's 0.694 late-interaction sibling is higher overall |

For NanoBEIR, the reported NDCG@10 values are Arabic 0.529, German 0.581, English 0.644, Spanish 0.581, French 0.592, Italian 0.583, Japanese 0.575, Korean 0.563, Norwegian 0.557, Portuguese 0.581, and Swedish 0.566. For MKQA-11, the reported Recall@20 values are Arabic 0.610, German 0.709, English 0.738, Spanish 0.708, French 0.715, Italian 0.703, Japanese 0.685, Korean 0.630, Norwegian 0.691, Portuguese 0.710, and Swedish 0.708. [^lfm25-embedding-card]

## Contradictions

The card says bold text identifies the best bi-encoder for each language, but several bolded dense-model values are not the largest displayed dense value: NanoBEIR English is 0.644 versus Qwen3-Embedding-0.6B's 0.649, and MKQA-11 Norwegian is 0.691 versus gte-multilingual-base's 0.698. This page preserves the numerical values and does not treat the per-language highlighting as verified ranking evidence. [^lfm25-embedding-card]

## Model size and architecture

- **Size and base:** approximately 354M parameters; LFM2.5-350M-Base with bidirectional patches. The card describes it as a bidirectional LFM-family member. [^lfm25-embedding-card]
- **Retriever:** dense bi-encoder with one vector per document, intended to keep indexes smaller than the related late-interaction model. [^lfm25-embedding-card]
- **Encoder and output:** 17 layers (10 convolutional, 6 attention, and 1 pooling layer), represented as a `Lfm2BidirectionalModel` followed by CLS pooling; it produces a 1,024-dimensional CLS vector. [^lfm25-embedding-card]
- **Retrieval interface:** cosine similarity; asymmetric `query: ` and `document: ` prompts. [^lfm25-embedding-card]
- **Limits and precision:** 512-token document length, 65,536-token vocabulary, and BF16 training precision. [^lfm25-embedding-card]

## Language support

The model card lists English, Spanish, German, French, Italian, Portuguese, Arabic, Swedish, Norwegian, Japanese, and Korean. It targets multilingual and cross-lingual retrieval. [^lfm25-embedding-card]

## Training data and disclosure limit

The supplied model card does **not** name training datasets, corpus size, data mixture, licenses, collection dates, or a training procedure. It links externally to a Liquid AI blog post for the bidirectional architecture and training recipe, but that material is not included in `raw/` and was not compiled. Training-data claims therefore cannot be established from this source. [^lfm25-embedding-card]

[^lfm25-embedding-card]: [LFM2.5-Embedding-350M model card](../raw/LFM2.5-Embedding-350M.md). Model, benchmark, and language claims are reported by the vendor model card.
