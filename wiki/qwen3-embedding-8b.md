---
type: Concept
title: Qwen3-Embedding-8B
description: An 8B-parameter Qwen3-based multilingual text embedding model with 36 layers, causal-attention EOS pooling, 4,096-dimensional Matryoshka embeddings, and reported leading June 2025 MTEB results.
tags: [embedding, retrieval, multilingual, matryoshka, qwen]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T15:52:34Z }
sources:
  - id: qwen3-embedding-8b-card
    resource: ../raw/Qwen3-Embedding-8B.md
    title: Qwen3-Embedding-8B model card
  - id: qwen3-embedding-report-latex
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    title: Qwen3 Embedding technical report LaTeX source (arXiv:2506.05176)
---

# Qwen3-Embedding-8B

Qwen3-Embedding-8B is an 8B-parameter text embedding model initialized from the dense Qwen3 foundation-model family. It has 36 layers, a 32,000-token context length, and up to 4,096-dimensional instruction-aware Matryoshka embeddings. The model card states support for 100+ languages, including programming languages. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]

## Benchmarks

The technical report evaluates the embedding series on 216 tasks: 131 MTEB Multilingual, 41 MTEB English v2, 32 C-MTEB, and 12 MTEB Code tasks. It describes the broader MMTEB suite as covering 500+ evaluation tasks and 250+ languages; that is benchmark coverage, not a model-support guarantee. [^qwen3-embedding-report-latex]

For Qwen3-Embedding-8B, the report gives the following results. These are report-authored evaluations or leaderboard snapshots, not independently reproduced here.

| Benchmark | Mean (Task) | Mean (Type) | Notes |
|---|---:|---:|---|
| MTEB Multilingual | 70.58 | 61.69 | Comparison values retrieved from the online leaderboard on 2025-06-04. |
| MTEB English v2 | 75.22 | 68.70 | Reported comparison. |
| C-MTEB | 73.83 | 75.00 | The model card rounds the task mean to 73.84. |
| MTEB Code v1 | 80.68 | — | nDCG@10 across 12 tasks. |

The model card calls its 70.58 MTEB Multilingual result No. 1 as of 2025-06-05, whereas the report's comparison table is dated 2025-06-04 and the card's own table says compared-model scores were retrieved on 2025-05-24. The underlying score agrees, but the source dates are not fully consistent. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]

## Model size and architecture

- **Backbone and size:** dense Qwen3 foundation-model family, **8B** parameters and **36 layers**. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]
- **Embedding path:** a causal-attention LLM appends an EOS token; the embedding is the final-layer hidden state at that token. Inputs are L2-normalized in the supplied implementation before cosine-similarity scoring. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]
- **Shape and input limit:** 32K context; maximum 4,096 output dimensions. Matryoshka representation learning permits user-selected dimensions from 32 to 4,096. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]
- **Instruction handling:** queries concatenate a task instruction and query; documents are left unchanged. The card says instructions generally improve downstream tasks by 1–5% in its evaluation. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]

## Language support

The model card claims support for **100+ languages**, including programming languages, and positions the model for multilingual, cross-lingual, and code retrieval. It does not list supported languages or define a per-language quality threshold. The technical report states that synthetic retrieval data use Qwen3's multilingual pretraining corpus, but does not disclose that corpus's language distribution. [^qwen3-embedding-8b-card] [^qwen3-embedding-report-latex]

## Training data and procedure

The technical report describes a **series-level** two-stage recipe; it does not assign separate dataset sizes to the 8B model. First, the authors use Qwen3-32B to synthesize roughly **150M** multi-task weak-supervision pairs, including retrieval, bitext mining, classification, and semantic-textual-similarity data. Retrieval synthesis draws documents from Qwen3's multilingual pretraining corpus and varies role, query type, length, difficulty, and language. [^qwen3-embedding-report-latex]

Second, supervised fine-tuning combines about **7M** labeled pairs with about **12M** high-quality synthetic pairs selected using a cosine-similarity threshold above 0.7. Named labeled-data sources are MS MARCO, NQ, HotpotQA, NLI, DuReader, T2-Ranking, SimCLUE, MIRACL, MLDR, Mr.TyDi, Multi-CPR, and CodeSearchNet. The embedding objective is an InfoNCE-derived contrastive loss with hard negatives and false-negative masking; the final procedure merges fine-tuning checkpoints using spherical linear interpolation (SLERP). [^qwen3-embedding-report-latex]

The source does not disclose the Qwen3 pretraining-corpus composition, data licenses, collection dates, source proportions, synthetic prompts, or per-model/per-language data allocation. [^qwen3-embedding-report-latex]

[^qwen3-embedding-8b-card]: [Qwen3-Embedding-8B model card](../raw/Qwen3-Embedding-8B.md). Model-card claims and benchmark snapshot.
[^qwen3-embedding-report-latex]: [Qwen3 Embedding technical report LaTeX source](../raw/2506.05176_Qwen3Embedding/main.tex), arXiv:2506.05176. The entry point and its local inputs contain the report's series-level architecture, training, and evaluation claims.
