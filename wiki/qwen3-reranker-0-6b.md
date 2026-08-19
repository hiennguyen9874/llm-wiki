---
type: Concept
title: Qwen3-Reranker-0.6B
description: A 0.6B-parameter, 28-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval and instruction-following results.
tags: [reranking, retrieval, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:52:34Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Reranker-0.6B

Qwen3-Reranker-0.6B is a 28-layer, 0.6B-parameter Qwen3 point-wise reranker with a 32K-token context limit and customizable instructions. [^qwen3-embedding-report-latex]

## Scoring and training

The model receives an instruction, query, and document in a Qwen chat template and frames relevance as predicting `yes` or `no`; its score is the softmax-normalized likelihood of `yes` relative to those two next-token likelihoods. It is trained with supervised fine-tuning on those binary labels and then uses SLERP checkpoint merging. Unlike the embedding models, reranker training omits the weakly supervised pre-training stage; the report does not disclose reranker-specific dataset sizes. [^qwen3-embedding-report-latex]

## Reported evaluation

These report-authored scores use top-100 candidates retrieved by Qwen3-Embedding-0.6B, so they measure reranking in that specified candidate-generation setting rather than end-to-end retrieval.

| Evaluation | Score |
|---|---:|
| MTEB English retrieval | 65.80 |
| C-MTEB retrieval | 71.31 |
| MMTEB retrieval | 66.36 |
| MLDR | 67.28 |
| MTEB Code | 73.42 |
| FollowIR | 5.41 |

The report says the 0.6B reranker improves the embedding retriever on the English, Chinese, multilingual, MLDR, and FollowIR evaluations, but not on MTEB Code. [^qwen3-embedding-report-latex]

[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. Architecture, procedure, and evaluation claims are report-authored.
