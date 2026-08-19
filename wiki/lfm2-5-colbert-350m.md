---
type: Concept
title: LFM2.5-ColBERT-350M
description: A 353M-parameter multilingual late-interaction retriever built from LFM2.5-350M-Base, producing 128-dimensional token vectors scored with MaxSim.
tags: [embedding, retrieval, late-interaction, colbert, multilingual, liquid]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:29:08+07:00 }
sources:
  - id: lfm25-colbert-card
    resource: ../raw/LFM2.5-ColBERT-350M.md
    title: LFM2.5-ColBERT-350M model card
---

# LFM2.5-ColBERT-350M

LFM2.5-ColBERT-350M is Liquid AI's approximately 353M-parameter multilingual late-interaction retrieval model. Built on LFM2.5-350M-Base with bidirectional patches, it emits 128-dimensional vectors per token and scores query–document pairs with MaxSim; the model card targets retrieval across 11 languages. [^lfm25-colbert-card]

## Benchmarks

The model card reports the following aggregate retrieval results. They are vendor-reported results, not independently reproduced here; apart from the metric, dataset, and language breakdown, the card provides no evaluation protocol details. [^lfm25-colbert-card]

| Benchmark | Metric | Reported average | Comparative result in listed table |
|---|---|---:|---|
| NanoBEIR Multilingual Extended | NDCG@10 | 0.605 | Highest average among the listed models |
| MKQA-11 | Recall@20 | 0.694 | Highest average among the listed models |

For NanoBEIR Multilingual Extended, the reported NDCG@10 values are Arabic 0.551, German 0.606, English 0.687, Spanish 0.607, French 0.622, Italian 0.606, Japanese 0.614, Korean 0.590, Norwegian 0.570, Portuguese 0.613, and Swedish 0.586. For MKQA-11, the reported Recall@20 values are Arabic 0.608, German 0.709, English 0.748, Spanish 0.711, French 0.715, Italian 0.707, Japanese 0.703, Korean 0.640, Norwegian 0.689, Portuguese 0.703, and Swedish 0.700. [^lfm25-colbert-card]

## Model size and architecture

- **Size and base:** approximately 353M parameters, based on LFM2.5-350M-Base plus bidirectional patches. It is described as one of the first bidirectional LFM-family members. [^lfm25-colbert-card]
- **Late interaction:** ColBERT-style multi-vector retrieval: one 128-dimensional vector per token, with query and document vectors compared using MaxSim. This improves retrieval accuracy and generalization relative to the source's dense sibling, at the cost of a larger index. [^lfm25-colbert-card]
- **Encoder and projection:** 17 layers (10 convolutional, 6 attention, and 1 dense); a `Lfm2BidirectionalModel` transformer followed by a bias-free identity dense projection from 1,024 to 128 dimensions. [^lfm25-colbert-card]
- **Limits and precision:** 512-token documents, 32-token queries, BF16 training precision, and a 64,402-token vocabulary. [^lfm25-colbert-card]

## Language support

The model card lists support for English, Spanish, German, French, Italian, Portuguese, Arabic, Swedish, Norwegian, Japanese, and Korean, and describes the retrieval use case as multilingual and cross-lingual search. [^lfm25-colbert-card]

## Training data and disclosure limit

The supplied model card does **not** name training datasets, corpus size, data mixture, licenses, collection dates, or a training procedure. It links to an external Liquid AI blog post for the bidirectional architecture and training recipe, but that material is not present in `raw/` and was not compiled. Training-data claims therefore cannot be established from this source. [^lfm25-colbert-card]

[^lfm25-colbert-card]: [LFM2.5-ColBERT-350M model card](../raw/LFM2.5-ColBERT-350M.md). Model, benchmark, and language claims are reported by the vendor model card.
