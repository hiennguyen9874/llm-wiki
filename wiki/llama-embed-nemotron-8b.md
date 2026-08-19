---
type: Concept
title: Llama-Embed-Nemotron-8B
description: A 7.50B-parameter Llama-3.1-8B-derived multilingual text embedding model with bidirectional attention, 4,096-dimensional outputs, and self-reported top MMTEB multilingual-v2 Borda rank in October 2025.
tags: [embedding, retrieval, multilingual, llama, nemotron, nvidia]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:31:10+07:00 }
sources:
  - id: llama-embed-nemotron-8b-card
    resource: ../raw/llama-embed-nemotron-8b.md
    title: llama-embed-nemotron-8b model card
---

# Llama-Embed-Nemotron-8B

Llama-Embed-Nemotron-8B is NVIDIA's text embedding model for retrieval, reranking, semantic similarity, and classification. It is a fine-tuned, 7.50B-parameter Llama-3.1-8B decoder adapted with bidirectional attention for bi-encoder embedding; the model card positions it for multilingual and cross-lingual retrieval and reports top rank on the October 21, 2025 MMTEB multilingual-v2 leaderboard. [^llama-embed-nemotron-8b-card]

## Benchmarks

The model card reports evaluation on **131 tasks** from the `MTEB(Multilingual, v2)` MMTEB split. It characterizes that benchmark as spanning 1,038 languages, 9 task types, and 20 domains. This is benchmark coverage, not a demonstrated list of model-supported languages. [^llama-embed-nemotron-8b-card]

As of October 21, 2025, the card reports the following MMTEB leaderboard results. The ranking uses Borda votes across tasks, which the card says favors broadly strong task performance. These scores and the rank are self-reported leaderboard snapshots, not independently reproduced here. [^llama-embed-nemotron-8b-card]

| Borda rank | Model | Borda votes | Mean task score |
|---:|---|---:|---:|
| 1 | Llama-Embed-Nemotron-8B | 39,573 | 69.46 |
| 2 | gemini-embedding-001 | 39,368 | 68.37 |
| 3 | Qwen3-Embedding-8B | 39,364 | 70.58 |

The card therefore reports Llama-Embed-Nemotron-8B as first by Borda rank, though Qwen3-Embedding-8B has the higher mean task score in that table. [^llama-embed-nemotron-8b-card]

## Model size and architecture

- **Parameters:** 7,504,924,672 (about 7.50B), despite the 8B family/model name. [^llama-embed-nemotron-8b-card]
- **Backbone:** `meta-llama/Llama-3.1-8B`, fine-tuned from a Transformer decoder with bidirectional attention. [^llama-embed-nemotron-8b-card]
- **Embedding architecture:** bi-encoder: queries and passages are independently encoded, with contrastive learning used to raise query–positive similarity and lower similarity to sampled negatives. [^llama-embed-nemotron-8b-card]
- **Shape:** 32 hidden layers, 4,096 hidden/embedding dimensions, and 4,096-dimensional output vectors. [^llama-embed-nemotron-8b-card]
- **Input limit:** up to 32,768 tokens for either queries or documents. [^llama-embed-nemotron-8b-card]
- **Instruction handling:** retrieval queries use an `Instruct: {task_instruction}\nQuery: {query}` template; documents receive no special template. [^llama-embed-nemotron-8b-card]

## Language support

The model card describes the model as **multilingual** and intended for multilingual and cross-lingual text retrieval, including RAG where queries and documents may use different languages. It does not enumerate supported languages, define the support level, or give language-level results. The stated capability should therefore not be read as a guarantee for any particular language. [^llama-embed-nemotron-8b-card]

## Training data and procedure

The card reports **16.4M query–passage pairs** from public and synthetically generated text datasets, collected and labeled through a hybrid of human, automated, and synthetic processes. Its training-data size field gives only a broad range of **1B to 10T tokens**. [^llama-embed-nemotron-8b-card]

It links the `nvidia/embed-nemotron-dataset-v1` training dataset, describes it as a curated mix of public and synthetic data, and links a technical report and training code. Those linked artifacts are outside the supplied raw source and were not inspected, so this wiki cannot establish dataset names beyond the linked dataset, source proportions, languages, licensing for individual data sources, filtering, or the synthetic-data-generation procedure. [^llama-embed-nemotron-8b-card]

[^llama-embed-nemotron-8b-card]: [llama-embed-nemotron-8b model card](../raw/llama-embed-nemotron-8b.md). Architecture, training, language, and benchmark statements are reported by the model card; externally linked dataset, technical-report, and code materials were not inspected.
