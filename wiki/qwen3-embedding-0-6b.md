---
type: Concept
title: Qwen3-Embedding-0.6B
description: A 0.6B-parameter Qwen3 multilingual text embedding model with 28 layers, a 32K-token context limit, 1,024-dimensional Matryoshka embeddings, and reported June 2025 MMTEB results.
tags: [embedding, retrieval, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T14:22:22Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
  - id: qwen3-embedding-0-6b-card
    resource: ../raw/Qwen3-Embedding-0.6B.md
    title: Qwen3-Embedding-0.6B model card
---

# Qwen3-Embedding-0.6B

Qwen3-Embedding-0.6B is the smallest Qwen3-based embedding model in the report’s 0.6B/4B/8B family. It has 28 layers, a 32K-token context limit, and 1,024-dimensional instruction-aware Matryoshka embeddings. [^qwen3-embedding-report-latex]

## Architecture and use

The decoder-only Qwen3 backbone uses causal attention. An EOS token is appended to the input, and the last-layer state at that token is the embedding. Queries concatenate a task instruction with the query, while documents are embedded unchanged. The model card specifies selectable output dimensions from 32 through 1,024, declares 100+ supported languages (including programming languages), and lists Apache-2.0 licensing. [^qwen3-embedding-report-latex] [^qwen3-embedding-0-6b-card]

## Deployment

The card documents use through Sentence Transformers (requiring `transformers>=4.51.0` and `sentence-transformers>=2.7.0`), raw Transformers, vLLM (`vllm>=0.8.5`), and Text Embeddings Inference. Its examples use L2-normalized last-token-pooled vectors and dot products for cosine similarity. It recommends task-specific English query instructions; the authors report an approximately 1–5% retrieval-performance drop in most retrieval scenarios when query instructions are omitted. This is author-reported guidance, not an independent measurement. [^qwen3-embedding-0-6b-card]

## Training

The report describes a family-level recipe rather than per-size training allocations: approximately 150M synthetic weak-supervision pairs are used before supervised fine-tuning on about 7M labeled and 12M filtered synthetic pairs. Synthetic data cover retrieval, bitext mining, classification, and semantic textual similarity; Qwen3-32B generates them. The embedding objective is an InfoNCE-derived contrastive loss with hard negatives and false-negative masking, and the final model merges fine-tuning checkpoints with SLERP. [^qwen3-embedding-report-latex]

## Reported evaluation

The following are report-authored results, not independent reproductions. The report evaluates 216 tasks across MTEB Multilingual, MTEB English v2, C-MTEB, and MTEB Code.

| Benchmark | Mean (Task) | Mean (Type) |
|---|---:|---:|
| MTEB Multilingual | 64.33 | 56.00 |
| MTEB English v2 | 70.70 | 64.88 |
| C-MTEB | 66.33 | 67.44 |
| MTEB Code v1 | 75.41 | — |

An ablation reports that the final 0.6B model outperforms variants trained only on synthetic data, without synthetic-data pre-training, or without model merging on all four aggregates. This supports the authors’ conclusion about the utility of those recipe components, but does not isolate their causal effects. [^qwen3-embedding-report-latex]

[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, training, and evaluation claims are report-authored.

[^qwen3-embedding-0-6b-card]: [Qwen3-Embedding-0.6B model card](../raw/Qwen3-Embedding-0.6B.md). Licensing, support, deployment, and performance guidance are provider-authored.
