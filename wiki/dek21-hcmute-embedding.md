---
type: Concept
title: DEk21_hcmute_embedding
description: A Vietnamese legal-text embedding model built from a RoBERTa sentence-transformer with 768-dimensional Matryoshka embeddings and mean pooling.
tags: [embedding, retrieval, vietnamese, legal, sentence-transformers, matryoshka]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:21:23Z }
sources:
  - id: dek21-card
    resource: ../raw/huydang-dek21-embedding.md
    title: DEk21_hcmute_embedding model card
---

# DEk21_hcmute_embedding

DEk21_hcmute_embedding is a Vietnamese sentence-transformer embedding model for legal-question and legal-context retrieval. It returns 768-dimensional cosine-comparable vectors and uses Matryoshka training for lower-dimensional truncation; its model card does not report a parameter count. [^dek21-card]

## Benchmarks

The card reports an information-retrieval evaluation on `another-symato/VMTEB-Zalo-legel-retrieval-wseg`, using Sentence Transformers' `InformationRetrievalEvaluator`. In its comparison table, the base `huyydangg/DEk21_hcmute_embedding` dense model scores **0.752173 nDCG@3**, **0.769259 nDCG@5**, **0.785101 nDCG@10**, **0.724740 MRR@3**, **0.734427 MRR@5**, and **0.741076 MRR@10**. A separately named `_wseg` variant leads the table with 0.917742 nDCG@10 and 0.894266 MRR@10; those results should not be attributed to the base model. [^dek21-card]

The card also reports cosine retrieval metrics at truncated output dimensions, but labels the evaluation datasets only as `dim_768`, `dim_512`, `dim_256`, `dim_128`, and `dim_64`. At 768 dimensions, it reports 0.693788 nDCG@10, 0.656815 MRR@10, and 0.810999 Recall@10; at 64 dimensions, the corresponding results are 0.657121, 0.621218, and 0.771753. The card does not identify that dataset or give its evaluation protocol, so these figures are not directly comparable to the named VMTEB evaluation. [^dek21-card]

## Model size and architecture

- **Parameter count:** not disclosed in the supplied card. [^dek21-card]
- **Encoder:** a Sentence Transformers pipeline with a `RobertaModel` transformer and mean-token pooling; CLS, max, mean-square-root-length, weighted-mean, and last-token pooling are disabled. [^dek21-card]
- **Base model:** metadata names `bkai-foundation-models/vietnamese-bi-encoder`; the usage guidance describes the model as PhoBERT-based. [^dek21-card]
- **Inputs and outputs:** maximum sequence length is 256 tokens; the native embedding size is 768 dimensions; cosine similarity is the stated similarity function. [^dek21-card]
- **Efficiency:** Matryoshka loss enables embeddings to be truncated. The supplied results cover 64, 128, 256, 512, and 768 dimensions. [^dek21-card]

## Language support

The model card declares **Vietnamese** as its language. It recommends Vietnamese word segmentation with `pyvi` before encoding because PhoBERT was pretrained on segmented Vietnamese text with multi-word expressions joined by underscores. The source makes no claim of support for other languages. [^dek21-card]

## Training data and procedure

The model was trained on an in-house corpus of approximately **100,000** examples pairing legal questions with related contexts. The card characterizes the model as focused on RAG and production efficiency, but does not identify the corpus source, collection period, data license, train/evaluation split, filtering, or exact mixture. [^dek21-card]

Metadata names `MultipleNegativesRankingLoss` and `MatryoshkaLoss`; the source says Matryoshka training is intended to preserve retrieval quality when embeddings are shortened. It supplies no hyperparameters, training duration, hardware details, or negative-mining procedure. [^dek21-card]

[^dek21-card]: [DEk21_hcmute_embedding model card](../raw/huydang-dek21-embedding.md). Architecture, training, language, and benchmark claims are self-reported by the model card.
