---
type: Concept
title: F2LLM-v2-14B
description: A 13.99B-parameter F2LLM-v2 embedding model with 5,120-dimensional EOS-pooled Matryoshka embeddings and author-reported results on 17 MTEB benchmarks.
tags: [embedding, retrieval, multilingual, instruction-tuned]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T08:58:31Z }
sources:
  - id: f2llm-v2-14b-card
    resource: ../raw/F2LLM-v2-14B.md
    title: F2LLM-v2-14B model card
  - id: f2llm-v2-report
    resource: ../raw/2603.19223_F2LLM-v2/main.tex
    title: F2LLM-v2 technical-report LaTeX source
---

# F2LLM-v2-14B

F2LLM-v2-14B is the largest member of the [F2LLM-v2](f2llm-v2.md) multilingual embedding family. Its model card provides the inference interface, while the technical report specifies its 13.99B-parameter architecture, training procedure, and author-reported MTEB results. [^f2llm-v2-14b-card] [^f2llm-v2-report]

## Benchmarks

The technical report evaluates the model on 17 MTEB benchmarks totaling 430 tasks. It reports scores of 68.74 on Multilingual MTEB, 73.08 on English, 80.75 on Code, and 71.72 in the table's unqualified average column; its leaderboard ranks were accessed on 2026-03-19. The table gives the model rank 1 on Code, European, Scandinavian, Indic, German, Polish, Japanese, Dutch, Persian, and Vietnamese. [^f2llm-v2-report]

The source prose instead says the model is state of the art on 11 benchmarks. Because its table identifies only ten first-place ranks, the claimed count cannot be reconciled from the report. [^f2llm-v2-report]

## Model size and architecture

- **Size and family:** The report gives 13,990M total parameters, comprising 778M embedding and 13,212M non-embedding parameters. [^f2llm-v2-report]
- **Architecture:** A Qwen3-based dense decoder Transformer with 40 layers, hidden size 5,120, 40 attention heads, 8 KV heads, and 128-dimensional heads; it uses the final EOS hidden state as the sequence representation. [^f2llm-v2-report]
- **Embedding interface:** The card's Sentence Transformers and Transformers examples return L2-normalized 5,120-dimensional vectors. The Transformers example selects the final non-padding (EOS) hidden state; retrieval-query examples use an instruction and documents use no prompt. [^f2llm-v2-14b-card]
- **MRL:** The report applies Matryoshka Representation Learning with a minimum dimension of 8, allowing truncated representations. [^f2llm-v2-report]
- **Unspecified:** Neither supplied source establishes tokenizer details, context length, hardware, token count, or training duration.

## Language support and training data

The report states that the 60M-sample corpus is collected from 157 public sources and covers 282 natural languages and more than 40 programming languages. It reports 16.1M English samples (28.7%) and 4.3M Chinese samples (7.7%), alongside a long tail of languages; this qualifies the card's claim of support for more than 200 languages, but does not independently establish quality or downstream proficiency per language. [^f2llm-v2-report] [^f2llm-v2-14b-card]

The 14B model is trained in the two reported stages: first on 27M samples from seven large retrieval datasets without instructional prefixes, then on an 18M mixture capped at 80,000 queries per source with task-specific instructions. It is one of the models trained without the report's additional embedding-distillation loss because of stated resource constraints. [^f2llm-v2-report]

## Release

The card says that training data, code, base and instruct models, and intermediate checkpoints are released. [^f2llm-v2-14b-card]

## Relationships

- **Part of:** [F2LLM-v2](f2llm-v2.md).

[^f2llm-v2-14b-card]: [F2LLM-v2-14B model card](../raw/F2LLM-v2-14B.md). Model-card interface and release claims are reported by the card.
[^f2llm-v2-report]: [F2LLM-v2 technical-report LaTeX source](../raw/2603.19223_F2LLM-v2/main.tex). Architecture, training, and benchmark results are author-reported.
