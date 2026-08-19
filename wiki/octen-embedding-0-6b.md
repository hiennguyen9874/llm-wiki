---
type: Concept
title: Octen-Embedding-0.6B
description: A 0.6B-parameter Qwen3-Embedding-0.6B-derived multilingual text embedding model with 1,024-dimensional outputs, a 32,768-token context limit, and a self-reported 0.7241 RTEB public score.
tags: [embedding, retrieval, multilingual, qwen, lora]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:37:54Z }
sources:
  - id: octen-0-6b-card
    resource: ../raw/Octen-Embedding-0.6B.md
    title: Octen-Embedding-0.6B model card
---

# Octen-Embedding-0.6B

Octen-Embedding-0.6B is a 0.6B-parameter text embedding model fine-tuned from Qwen/Qwen3-Embedding-0.6B. It produces 1,024-dimensional embeddings, accepts up to 32,768 tokens, and is positioned for multilingual semantic search and retrieval. [^octen-0-6b-card]

## Benchmarks

The model card reports an **RTEB public Mean score of 0.7241** for Octen-Embedding-0.6B. It reports no private-dataset or Mean (Task) score for this model, so a full RTEB comparison is unavailable from the source. [^octen-0-6b-card]

| Model | RTEB Public | RTEB Private | RTEB Mean (Task) |
|---|---:|---:|---:|
| Octen-Embedding-0.6B | 0.7241 | Not reported | Not reported |
| Qwen3-Embedding-0.6B | Not reported | 0.7117 | Not reported |

The same table reports the larger Octen-Embedding-8B at 0.7953 public, 0.8157 private, and 0.8045 Mean (Task), with a claimed #1 RTEB ranking as of January 12, 2026. That ranking applies to the 8B model, not the 0.6B model. All benchmark results and ranking claims are self-reported by the model card. [^octen-0-6b-card]

## Model size and architecture

- **Size:** 0.6B parameters. [^octen-0-6b-card]
- **Base model and adaptation:** fine-tuned from `Qwen/Qwen3-Embedding-0.6B` using LoRA. The card does not specify LoRA rank, target modules, trainable-parameter count, or training hyperparameters. [^octen-0-6b-card]
- **Inputs and outputs:** 32,768-token maximum context and 1,024-dimensional embeddings. The supplied Transformers example takes the final-token hidden state and L2-normalizes it; the card does not otherwise describe pooling or embedding-head architecture. [^octen-0-6b-card]
- **Undisclosed architecture:** the source does not provide layer count, hidden size, attention design, tokenizer details, or a parameter breakdown. [^octen-0-6b-card]

## Language support

The card claims support for **100+ languages**, specifically naming English and Chinese in its metadata, and says support includes programming languages. It describes multilingual, cross-lingual, and code retrieval capability, but does not enumerate the supported languages or give per-language benchmark results. [^octen-0-6b-card]

## Training data

The model card does not identify any training datasets, corpus sizes, mixture proportions, collection dates, licenses, filtering procedures, synthetic-data use, or domain-specific sample counts. It only names LoRA fine-tuning as the training method. Therefore, its claims of expertise in legal, finance, healthcare, and code retrieval cannot be tied to disclosed training data from this source. [^octen-0-6b-card]

[^octen-0-6b-card]: [Octen-Embedding-0.6B model card](../raw/Octen-Embedding-0.6B.md). Model, training, language, and benchmark claims are reported by the model card.
