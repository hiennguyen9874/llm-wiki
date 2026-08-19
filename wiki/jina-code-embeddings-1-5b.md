---
type: Concept
title: Jina Code Embeddings 1.5B
description: A Qwen2.5-Coder-1.5B-based code-retrieval embedding model with 1,536-dimensional last-token-pooled vectors, 32,768-token inputs, and stated support for 15+ programming languages.
tags: [embedding, retrieval, code, jina, qwen, multilingual]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:23:33+07:00 }
sources:
  - id: jina-code-embeddings-1-5b-card
    resource: ../raw/jina-code-embeddings-1.5b.md
    title: Jina Code Embeddings 1.5B model card
---

# Jina Code Embeddings 1.5B

Jina Code Embeddings 1.5B is a code-retrieval embedding model built on Qwen2.5-Coder-1.5B. It targets text-to-code, code-to-code, code-to-text, code-to-completion retrieval, and technical question answering, producing 1,536-dimensional last-token-pooled dense vectors from inputs up to 32,768 tokens. [^jina-code-embeddings-1-5b-card]

## Benchmarks

The supplied model card does not report benchmark names, scores, metrics, baselines, or evaluation configurations. It directs readers to an external technical report for training details and benchmarks, but that report is not included in this source; no benchmark-performance claim is compiled here. [^jina-code-embeddings-1-5b-card]

## Model size and architecture

- **Size and base model:** built on Qwen/Qwen2.5-Coder-1.5B; the card presents the model as a 1.5B variant. [^jina-code-embeddings-1-5b-card]
- **Embedding output:** 1,536-dimensional dense embeddings by default, with Matryoshka truncation dimensions of 128, 256, 512, 1,024, and 1,536. The card characterizes truncation to 128 dimensions as having minimal performance loss, without supplying measurements. [^jina-code-embeddings-1-5b-card]
- **Encoding design:** last-token pooling; BFloat16 model dtype; maximum sequence length of 32,768 tokens; and FlashAttention2 attention support. [^jina-code-embeddings-1-5b-card]
- **Task conditioning:** inference-time instruction prefixes are specified for `nl2code`, `code2code`, `code2nl`, `code2completion`, and technical QA. [^jina-code-embeddings-1-5b-card]

## Language support

The card states support for **15+ programming languages** and describes applicability across web development, software development, machine learning, data science, and educational coding problems. It does not enumerate those languages, define the support criterion, report per-language quality, or claim support for a particular set of natural languages. [^jina-code-embeddings-1-5b-card]

## Training data and procedure

The supplied card contains no training-corpus description, named datasets, data volume, source licenses, programming-language mixture, filtering, deduplication, training objectives, or fine-tuning procedure. It refers readers to an external technical report for training details, which is outside the ingested source; training-data characteristics therefore remain unknown here. [^jina-code-embeddings-1-5b-card]

[^jina-code-embeddings-1-5b-card]: [Jina Code Embeddings 1.5B model card](../raw/jina-code-embeddings-1.5b.md). Architecture, capability, language, and coverage-limit statements are derived from the supplied model card.
