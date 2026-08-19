---
type: Concept
title: Qwen3-Reranker-8B
description: An Apache-2.0 8B-parameter, 36-layer Qwen3 point-wise reranker with 32K-token context, 100+ language support, configurable instructions, and reported June 2025 retrieval results.
tags: [reranking, retrieval, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:12:28Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
  - id: qwen3-reranker-model-card
    resource: ../raw/Qwen3-Reranker-8B.md
    title: Qwen3-Reranker-8B model card
---

# Qwen3-Reranker-8B

Qwen3-Reranker-8B is a 36-layer, 8B-parameter Qwen3 point-wise reranker with a 32K-token context limit, support for 100+ languages, and customizable instructions. It is released under Apache-2.0. [^qwen3-embedding-report-latex] [^qwen3-reranker-model-card]

## Scoring and training

The model receives instruction, query, and document together in a Qwen chat template. It treats relevance as binary classification and scores the softmax-normalized next-token likelihood of `yes` relative to `yes` and `no`. The report describes supervised fine-tuning and SLERP checkpoint merging, while explicitly stating that reranking skips the embedding family’s weak-supervision pre-training stage. Reranker-specific dataset sizes are not disclosed. [^qwen3-embedding-report-latex]

## Implementation and scoring

The model card provides Sentence Transformers `CrossEncoder` usage and requires `transformers>=4.51.0` for its Transformers example. In Sentence Transformers, `predict` returns raw logit differences by default; applying a sigmoid produces 0–1 scores. The supplied lower-level example instead calculates a normalized probability from the `yes` and `no` token logits. [^qwen3-reranker-model-card]

Its default prompt name is `query`, which supplies the instruction “Given a web search query, retrieve relevant passages that answer the query.” The model card recommends task-specific instructions and reports an approximately 1%–5% retrieval-performance decrease when an instruction is omitted. Although the model overview declares a 32K context length, its Transformers example configures `max_length` as 8,192. [^qwen3-reranker-model-card]

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
[^qwen3-reranker-model-card]: [Qwen3-Reranker-8B model card](../raw/Qwen3-Reranker-8B.md). Model-card claims are publisher-authored.
