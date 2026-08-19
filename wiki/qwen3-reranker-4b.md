---
type: Concept
title: Qwen3-Reranker-4B
description: A 4B-parameter, 36-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval and instruction-following results.
tags: [reranking, retrieval, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:52:34Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Reranker-4B

Qwen3-Reranker-4B is a 36-layer, 4B-parameter Qwen3 point-wise reranker with a 32K-token context limit and customizable instructions. [^qwen3-embedding-report-latex]

## Scoring and training

For each instruction, query, and document, the model uses a chat-formatted binary relevance prompt and scores the normalized relative likelihood of the next token `yes` over `yes` and `no`. The report describes supervised fine-tuning with a binary label loss followed by SLERP merging of fine-tuning checkpoints. It explicitly excludes weakly supervised pre-training from reranker training and gives no reranker-specific data size. [^qwen3-embedding-report-latex]

## Reported evaluation

These are report-authored scores after reranking the top 100 candidates produced by Qwen3-Embedding-0.6B; they are not end-to-end retrieval scores.

| Evaluation | Score |
|---|---:|
| MTEB English retrieval | 69.76 |
| C-MTEB retrieval | 75.94 |
| MMTEB retrieval | 72.74 |
| MLDR | 69.97 |
| MTEB Code | 81.20 |
| FollowIR | 14.84 |

Among the three reported Qwen3 rerankers, the 4B model has the highest English-retrieval and FollowIR scores. [^qwen3-embedding-report-latex]

[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, procedure, and evaluation claims are report-authored.
