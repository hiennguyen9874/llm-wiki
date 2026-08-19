---
type: Concept
title: Qwen3-Embedding-4B
description: An Apache-2.0 4B-parameter Qwen3 multilingual text embedding model with 36 layers, 32K-token context, and 32–2,560-dimensional instruction-aware Matryoshka outputs.
tags: [embedding, retrieval, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T14:23:16Z }
sources:
  - id: qwen3-embedding-card
    resource: ../raw/Qwen3-Embedding-4B.md
    title: Qwen3-Embedding-4B model card
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Embedding-4B

Qwen3-Embedding-4B is an Apache-2.0, Qwen3-based 4B-parameter multilingual text embedding model. It has 36 layers, a 32K-token context limit, and instruction-aware Matryoshka outputs configurable from 32 to 2,560 dimensions; the model card states support for 100+ languages, including programming languages. [^qwen3-embedding-card] [^qwen3-embedding-report-latex]

## Architecture and use

The model appends an EOS token under causal attention and uses its final-layer hidden state as the embedding. A query prepends or concatenates the task instruction, whereas a document is embedded without an instruction. The report designates the model as Matryoshka-representation-learning capable, while the model card specifies the supported output-dimension range as 32–2,560. [^qwen3-embedding-report-latex] [^qwen3-embedding-card]

For retrieval, the supplied examples apply a one-sentence task instruction to queries only, normalize the resulting vectors, and use cosine similarity (or a normalized dot product); the card recommends task-specific instructions, preferably written in English for multilingual use. It reports a roughly 1–5% retrieval-performance decrease when query instructions are omitted, an author evaluation rather than an independent result. [^qwen3-embedding-card]

## Implementation and deployment

The model card requires `transformers>=4.51.0`; its Sentence Transformers example additionally requires `sentence-transformers>=2.7.0`, and its vLLM example requires `vllm>=0.8.5`. It shows Sentence Transformers, bare Transformers, vLLM embedding, and Text Embeddings Inference (TEI) interfaces. FlashAttention 2 with left padding is recommended for acceleration and memory savings; the TEI example names NVIDIA-GPU and CPU images. [^qwen3-embedding-card]

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

[^qwen3-embedding-card]: [Qwen3-Embedding-4B model card](../raw/Qwen3-Embedding-4B.md). Author-reported license, capability, implementation, deployment, and benchmark claims.
[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, training, and evaluation claims are report-authored.
