---
type: Concept
title: Qwen3-Reranker-8B
description: An 8B-parameter, 36-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval results.
tags: [reranking, retrieval, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:52:34Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Reranker-8B

Qwen3-Reranker-8B is a 36-layer, 8B-parameter Qwen3 point-wise reranker with a 32K-token context limit and customizable instructions. [^qwen3-embedding-report-latex]

## Scoring and training

The model receives instruction, query, and document together in a Qwen chat template. It treats relevance as binary classification and scores the softmax-normalized next-token likelihood of `yes` relative to `yes` and `no`. The report describes supervised fine-tuning and SLERP checkpoint merging, while explicitly stating that reranking skips the embedding family’s weak-supervision pre-training stage. Reranker-specific dataset sizes are not disclosed. [^qwen3-embedding-report-latex]

## Reported evaluation

The report reranks the top 100 candidates returned by Qwen3-Embedding-0.6B; the following are therefore reranking-pipeline scores, not end-to-end retrieval scores.

| Evaluation | Score |
|---|---:|
| MTEB English retrieval | 69.02 |
| C-MTEB retrieval | 77.45 |
| MMTEB retrieval | 72.94 |
| MLDR | 70.19 |
| MTEB Code | 81.22 |
| FollowIR | 8.05 |

Among the three reported Qwen3 rerankers, the 8B model has the highest scores on C-MTEB retrieval, MMTEB retrieval, MLDR, and MTEB Code. [^qwen3-embedding-report-latex]

[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, procedure, and evaluation claims are report-authored.
