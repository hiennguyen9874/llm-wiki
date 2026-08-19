---
type: Concept
title: Jina Embeddings v4
description: A Qwen2.5-VL-3B-Instruct-based multimodal, multilingual embedding model offering dense and late-interaction retrieval outputs with task-selectable adapters.
tags: [embedding, retrieval, multimodal, multilingual, late-interaction, qwen, jina]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:24:30Z }
sources:
  - id: jina-v4-card
    resource: ../raw/jina-embeddings-v4.md
    title: Jina Embeddings v4 model card
---

# Jina Embeddings v4

Jina Embeddings v4 is a multimodal, multilingual embedding model built on Qwen2.5-VL-3B-Instruct. It embeds text, images, and visual documents for dense single-vector or late-interaction multi-vector retrieval, with inference-selectable adapters for retrieval, text matching, and code tasks. [^jina-v4-card]

## Benchmarks

The model card announces **Jina VDR**, a multilingual, multi-domain benchmark for visual-document retrieval, alongside the model. It does not report Jina Embeddings v4 scores, rankings, metrics, evaluation protocol, or comparisons on that benchmark or any other benchmark. It directs readers to an external technical report for benchmarks; that report is not part of this source artifact, so benchmark performance is not established here. [^jina-v4-card]

## Model size and architecture

- **Base model:** Qwen/Qwen2.5-VL-3B-Instruct. The card does not separately report Jina Embeddings v4's total parameter count, so the base model's 3B designation should not be treated as a precise adapted-model parameter count. [^jina-v4-card]
- **Modalities and retrieval forms:** unified embeddings for text, images, and visual documents; dense single-vector and late-interaction multi-vector output. [^jina-v4-card]
- **Task adaptation:** adapters for `retrieval`, `text-matching`, and `code` can be selected at inference. Separate vLLM variants merge the corresponding adapter into the base Qwen2.5-VL weights. [^jina-v4-card]
- **Vectors:** dense output is 2,048 dimensions by default and supports Matryoshka truncation to 1,024, 512, 256, or 128 dimensions. Multi-vector output is 128 dimensions. [^jina-v4-card]
- **Other reported configuration:** BF16 model dtype, mean pooling, FlashAttention2, and a 32,768-token maximum sequence length. [^jina-v4-card]

## Language support

The card claims support for **30+ languages** and describes the model as multilingual. It does not enumerate the languages, define the support criterion, or provide per-language results; support for a particular language therefore cannot be determined from this source. [^jina-v4-card]

## Training data and procedure

The model card provides no training-corpus composition, size, datasets, collection dates, licenses, filtering, mixture proportions, or training procedure. It refers readers to the external technical report for training details, which is outside the supplied evidence. [^jina-v4-card]

[^jina-v4-card]: [Jina Embeddings v4 model card](../raw/jina-embeddings-v4.md). Architecture, capability, language, benchmark, and training-data statements are reported by the model card; it delegates detailed training and benchmark evidence to an external technical report.