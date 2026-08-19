---
type: Concept
title: Octen-Embedding-4B
description: A 4B-parameter Qwen3-Embedding-4B-derived multilingual text embedding model with 2,560-dimensional outputs, LoRA fine-tuning, and self-reported 0.7834 RTEB Mean (Task).
tags: [embedding, retrieval, multilingual, qwen, lora]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:38:40Z }
sources:
  - id: octen-4b-card
    resource: ../raw/Octen-Embedding-4B.md
    title: Octen-Embedding-4B model card
---

# Octen-Embedding-4B

Octen-Embedding-4B is a 4B-parameter text embedding model fine-tuned from Qwen/Qwen3-Embedding-4B. It produces 2,560-dimensional embeddings and is positioned for multilingual semantic search and retrieval. [^octen-4b-card]

## Benchmarks

The model card reports **0.7747 RTEB Public**, **0.7942 RTEB Private**, and **0.7834 RTEB Mean (Task)** for Octen-Embedding-4B. These results are self-reported; the card does not provide task-level scores or evaluation-protocol details. [^octen-4b-card]

| Model | RTEB Public | RTEB Private | RTEB Mean (Task) |
|---|---:|---:|---:|
| Octen-Embedding-4B | 0.7747 | 0.7942 | 0.7834 |
| Qwen3-Embedding-4B | Not reported | 0.7711 | Not reported |

The card calls the 4B model “best in 4B category,” but does not define the comparison set or ranking methodology. Its claimed RTEB #1 ranking applies to the separate Octen-Embedding-8B model, not this model. [^octen-4b-card]

## Model size and architecture

- **Size:** 4B parameters. [^octen-4b-card]
- **Base model and adaptation:** fine-tuned from `Qwen/Qwen3-Embedding-4B` using LoRA. The card does not specify LoRA rank, target modules, trainable-parameter count, or training hyperparameters. [^octen-4b-card]
- **Inputs and outputs:** 2,560-dimensional embeddings. The supplied Transformers example takes the final-token hidden state and L2-normalizes it; the card does not otherwise describe pooling or embedding-head architecture. [^octen-4b-card]
- **Context-length discrepancy:** the model-family and RTEB tables list 32,768 maximum tokens, whereas Model Details lists 40,960 maximum sequence length; the source does not reconcile them. [^octen-4b-card]
- **Undisclosed architecture:** the source does not provide layer count, hidden size, attention design, tokenizer details, or a parameter breakdown. [^octen-4b-card]

## Language support

The card claims support for **100+ languages**, specifically naming English and Chinese in its metadata, and says support includes programming languages. It describes multilingual, cross-lingual, and code retrieval capability, but does not enumerate the supported languages or give per-language benchmark results. [^octen-4b-card]

## Training data

The model card does not identify any training datasets, corpus sizes, mixture proportions, collection dates, licenses, filtering procedures, synthetic-data use, or domain-specific sample counts. It only names LoRA fine-tuning as the training method. Therefore, its claims of expertise in legal, finance, healthcare, and code retrieval cannot be tied to disclosed training data from this source. [^octen-4b-card]

[^octen-4b-card]: [Octen-Embedding-4B model card](../raw/Octen-Embedding-4B.md). Model, training, language, and benchmark claims are reported by the model card.
