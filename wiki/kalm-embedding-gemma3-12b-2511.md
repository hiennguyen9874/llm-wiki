---
type: Concept
title: KaLM-Embedding-Gemma3-12B-2511
description: An 11.76B-parameter Gemma 3-derived embedding model with 3,840-dimensional last-token-pooled Matryoshka outputs and self-reported top MMTEB rank as of November 2025.
tags: [embedding, retrieval, gemma, matryoshka, multilingual]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:27:54Z }
sources:
  - id: kalm-gemma3-12b-card
    resource: ../raw/KaLM-Embedding-Gemma3-12B-2511.md
    title: KaLM-Embedding-Gemma3-12B-2511 model card
---

# KaLM-Embedding-Gemma3-12B-2511

KaLM-Embedding-Gemma3-12B-2511 is an 11.76B-parameter text-embedding model derived from `google/gemma-3-12b-pt`. It outputs 3,840-dimensional, last-token-pooled embeddings with Matryoshka truncation options; its model card self-reports first place in an MMTEB comparison current to November 2025. [^kalm-gemma3-12b-card]

## Benchmarks

The model card reports a **72.32 Mean (Task)** and **62.51 Mean (TaskType)** MMTEB score, ranked first by Borda count in its comparison table. It leads the listed models in bitext mining (83.76), classification (77.88), multilabel classification (33.03), and retrieval (75.66). [^kalm-gemma3-12b-card]

| Metric | Score |
|---|---:|
| Bitext mining | 83.76 |
| Classification | 77.88 |
| Clustering | 55.77 |
| Instruction reranking | 5.49 |
| Multilabel classification | 33.03 |
| Pair classification | 84.73 |
| Reranking | 67.27 |
| Retrieval | 75.66 |
| STS | 79.02 |

These results and the state-of-the-art claim are self-reported. The source does not identify the precise MMTEB release, task set, evaluation protocol, or hardware, so they are not independently verifiable from this model card. [^kalm-gemma3-12b-card]

## Model size and architecture

- **Size:** 11.76B parameters. [^kalm-gemma3-12b-card]
- **Base model:** `google/gemma-3-12b-pt`. The card's vLLM instructions distinguish `Gemma3TextModel` from `Gemma3ForCausalLM` configurations and require the latter's `CausalLM` revision for vLLM loading. [^kalm-gemma3-12b-card]
- **Embedding head:** last-token pooling produces 3,840-dimensional vectors. [^kalm-gemma3-12b-card]
- **Matryoshka representation learning:** supports 3,840, 2,048, 1,024, 512, 256, 128, and 64 dimensions. [^kalm-gemma3-12b-card]
- **Input limit:** 32,000 tokens. [^kalm-gemma3-12b-card]

The source does not disclose the layer count, hidden size, attention configuration, tokenizer, normalization behavior, or parameter breakdown; the architecture cannot be characterized more specifically from this evidence. [^kalm-gemma3-12b-card]

## Language support

The source supplies neither a language list nor a multilingual-support claim. Its MMTEB comparison includes bitext-mining results, but that does not establish which languages the model supports or its quality by language. [^kalm-gemma3-12b-card]

## Training data

The model card metadata names `KaLM-Embedding/KaLM-embedding-finetuning-data` as a dataset. It does not describe that dataset's contents, languages, size, collection method, licenses, splits, filtering, mixture proportions, or whether further data was used. No training procedure is provided. These omissions limit provenance and coverage assessment. [^kalm-gemma3-12b-card]

[^kalm-gemma3-12b-card]: [KaLM-Embedding-Gemma3-12B-2511 model card](../raw/KaLM-Embedding-Gemma3-12B-2511.md). Model, benchmark, architecture, language, and training-data claims are reported by the model card.
