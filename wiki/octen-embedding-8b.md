---
type: Concept
title: Octen-Embedding-8B
description: A Qwen3-Embedding-8B-derived multilingual text embedding model reported as 7.6B in its family table and 8B in Model Details, with 4,096-dimensional outputs and a self-reported 0.8045 RTEB Mean (Task).
tags: [embedding, retrieval, multilingual, qwen, lora]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:39:40Z }
sources:
  - id: octen-8b-card
    resource: ../raw/Octen-Embedding-8B.md
    title: Octen-Embedding-8B model card
---

# Octen-Embedding-8B

Octen-Embedding-8B is a text embedding model fine-tuned from Qwen/Qwen3-Embedding-8B using LoRA. It produces 4,096-dimensional embeddings and is positioned for multilingual semantic search and retrieval. The source reports conflicting model sizes: 7.6B in its family table and 8B in Model Details. [^octen-8b-card]

## Benchmarks

The model card reports **0.7953 RTEB Public**, **0.8157 RTEB Private**, and **0.8045 RTEB Mean (Task)** for Octen-Embedding-8B. It claims the model ranked #1 on the RTEB leaderboard as of January 12, 2026. These are self-reported results; the card does not provide task-level scores or evaluation-protocol details. [^octen-8b-card]

| Model | RTEB Public | RTEB Private | RTEB Mean (Task) |
|---|---:|---:|---:|
| Octen-Embedding-8B | 0.7953 | 0.8157 | 0.8045 |
| Qwen3-Embedding-8B | 0.7310 | 0.7838 | 0.7547 |

## Model size and architecture

- **Size discrepancy:** the model-family table gives **7.6B** parameters, while Model Details gives **8B**; the source does not reconcile the two figures. [^octen-8b-card]
- **Base model and adaptation:** fine-tuned from `Qwen/Qwen3-Embedding-8B` using LoRA. The card does not specify LoRA rank, target modules, trainable-parameter count, or training hyperparameters. [^octen-8b-card]
- **Inputs and outputs:** 4,096-dimensional embeddings. The supplied Transformers example takes the final-token hidden state and L2-normalizes it; the card does not otherwise describe pooling or embedding-head architecture. [^octen-8b-card]
- **Context-length discrepancy:** the highlights, model-family table, and RTEB table list 32,768 maximum tokens, whereas Model Details lists 40,960 maximum sequence length; the source does not reconcile them. [^octen-8b-card]
- **Undisclosed architecture:** the source does not provide layer count, hidden size, attention design, tokenizer details, or a parameter breakdown. [^octen-8b-card]

## Language support

The card claims support for **100+ languages**, specifically naming English and Chinese in its metadata, and says support includes programming languages. It describes multilingual, cross-lingual, and code retrieval capability, but does not enumerate the supported languages or give per-language benchmark results. [^octen-8b-card]

## Training data

The model card does not identify any training datasets, corpus sizes, mixture proportions, collection dates, licenses, filtering procedures, synthetic-data use, or domain-specific sample counts. It only names LoRA fine-tuning as the training method. Therefore, its claims of expertise in legal, finance, healthcare, and code retrieval cannot be tied to disclosed training data from this source. [^octen-8b-card]

[^octen-8b-card]: [Octen-Embedding-8B model card](../raw/Octen-Embedding-8B.md). Model, training, language, and benchmark claims are reported by the model card.
