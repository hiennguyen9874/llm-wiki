---
type: Concept
title: Qwen3-Reranker-4B
description: A 4B-parameter, 36-layer Qwen3 point-wise reranker with a 32K-token context limit and reported June 2025 retrieval and instruction-following results.
tags: [reranking, retrieval, multilingual, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T13:11:19Z }
sources:
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
  - id: qwen3-reranker-model-card
    resource: ../raw/Qwen3-Reranker-4B.md
    title: Qwen3-Reranker-4B model card
---

# Qwen3-Reranker-4B

Qwen3-Reranker-4B is a 36-layer, 4B-parameter Qwen3 point-wise reranker with a 32K-token context limit, support for 100+ languages, and customizable instructions. It is released under Apache-2.0. [^qwen3-embedding-report-latex] [^qwen3-reranker-model-card]

## Scoring and training

For each instruction, query, and document, the model uses a chat-formatted binary relevance prompt and scores the normalized relative likelihood of the next token `yes` over `yes` and `no`. The report describes supervised fine-tuning with a binary label loss followed by SLERP merging of fine-tuning checkpoints. It explicitly excludes weakly supervised pre-training from reranker training and gives no reranker-specific data size. [^qwen3-embedding-report-latex]

## Implementation and scoring

The model card provides Sentence Transformers `CrossEncoder` usage, requiring `transformers>=4.51.0` for its Transformers example and `vllm>=0.8.5` for its vLLM example. In Sentence Transformers, `predict` returns raw logit differences by default; applying a sigmoid produces 0–1 scores. The supplied lower-level examples instead calculate a normalized probability from the `yes` and `no` token logits. [^qwen3-reranker-model-card]

Its default prompt name is `query`, which supplies the instruction “Given a web search query, retrieve relevant passages that answer the query.” The model card recommends task-specific instructions and reports an approximately 1%–5% retrieval-performance decrease when an instruction is omitted. Although the model overview declares a 32K context length, its Transformers and vLLM examples configure `max_length` as 8,192. [^qwen3-reranker-model-card]

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
[^qwen3-reranker-model-card]: [Qwen3-Reranker-4B model card](../raw/Qwen3-Reranker-4B.md). Model-card claims are publisher-authored.
