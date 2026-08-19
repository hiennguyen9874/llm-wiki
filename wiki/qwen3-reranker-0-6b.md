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
  - id: qwen3-reranker-model-card
    resource: ../raw/Qwen3-Reranker-0.6B.md
    title: Qwen3-Reranker-0.6B model card
---

# Qwen3-Reranker-0.6B

Qwen3-Reranker-0.6B is a 28-layer, 0.6B-parameter Qwen3 point-wise reranker with a 32K-token context limit, support for 100+ languages, and customizable instructions. It is released under Apache-2.0. [^qwen3-embedding-report-latex] [^qwen3-reranker-model-card]

## Scoring and training

The model receives an instruction, query, and document in a Qwen chat template and frames relevance as predicting `yes` or `no`; its score is the softmax-normalized likelihood of `yes` relative to those two next-token likelihoods. It is trained with supervised fine-tuning on those binary labels and then uses SLERP checkpoint merging. Unlike the embedding models, reranker training omits the weakly supervised pre-training stage; the report does not disclose reranker-specific dataset sizes. [^qwen3-embedding-report-latex]

## Implementation and scoring

The model card provides Sentence Transformers `CrossEncoder` usage, requiring `transformers>=4.51.0` for its Transformers example and `vllm>=0.8.5` for its vLLM example. In Sentence Transformers, `predict` returns raw logit differences by default; applying a sigmoid produces 0–1 scores. The supplied lower-level examples instead calculate a normalized probability from the `yes` and `no` token logits. [^qwen3-reranker-model-card]

Its default prompt name is `query`, which supplies the instruction “Given a web search query, retrieve relevant passages that answer the query.” The model card recommends task-specific instructions and reports an approximately 1%–5% retrieval-performance decrease when an instruction is omitted. Although the model overview declares a 32K context length, its Transformers and vLLM examples configure `max_length` as 8,192. [^qwen3-reranker-model-card]

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
[^qwen3-reranker-model-card]: [Qwen3-Reranker-0.6B model card](../raw/Qwen3-Reranker-0.6B.md). Model-card claims are publisher-authored.
