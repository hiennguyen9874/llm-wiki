---
type: Concept
title: Qwen3-Embedding-4B
description: A 4B-parameter Qwen3 multilingual text embedding model with 36 layers, a 32K-token context limit, 2,560-dimensional Matryoshka embeddings, and reported leading June 2025 MMTEB results.
tags: [embedding, retrieval, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:52:34Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Embedding-4B

Qwen3-Embedding-4B is a Qwen3-based multilingual text embedding model with 36 layers, a 32K-token context limit, and 2,560-dimensional instruction-aware Matryoshka embeddings. [^qwen3-embedding-report-latex]

## Architecture and use

The model appends an EOS token under causal attention and uses its final-layer hidden state as the embedding. A query prepends or concatenates the task instruction, whereas a document is embedded without an instruction. The report designates the model as Matryoshka-representation-learning capable, but does not list its supported truncation sizes. [^qwen3-embedding-report-latex]

## Training

The report gives a family-level, not per-model, procedure: pre-train on about 150M Qwen3-32B-generated weak-supervision pairs spanning retrieval, bitext mining, classification, and semantic textual similarity; fine-tune on about 7M labeled and 12M filtered synthetic pairs; then merge fine-tuning checkpoints with SLERP. Its embedding objective is an InfoNCE-derived contrastive loss with hard negatives and false-negative masking. [^qwen3-embedding-report-latex]

## Reported evaluation

These are report-authored results, not independent reproductions. The reported evaluation contains 216 tasks across MTEB Multilingual, MTEB English v2, C-MTEB, and MTEB Code.

| Benchmark | Mean (Task) | Mean (Type) |
|---|---:|---:|
| MTEB Multilingual | 69.45 | 60.86 |
| MTEB English v2 | 74.60 | 68.09 |
| C-MTEB | 72.26 | 73.50 |
| MTEB Code v1 | 80.06 | — |

The report’s multilingual comparison table lists Qwen3-Embedding-4B ahead of its selected baselines on both aggregate measures, with compared-model leaderboard values retrieved on 2025-06-04. [^qwen3-embedding-report-latex]

[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, training, and evaluation claims are report-authored.
