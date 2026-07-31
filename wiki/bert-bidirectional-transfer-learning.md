---
type: Concept
title: BERT bidirectional transfer learning
description: BERT pre-trains a bidirectional Transformer encoder, then fine-tunes all of its parameters with a small task-specific output layer.
tags: [bert, transfer-learning, transformer-encoder, fine-tuning]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:22:53Z }
sources:
  - id: devlin-bert-2018
    resource: ../raw/arXiv-1810.04805v2/main.tex
    title: BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
---

# BERT bidirectional transfer learning

BERT couples pre-training on unlabeled text with end-to-end fine-tuning for each labeled task. Its Transformer encoder lets every token attend to both left and right context during encoding; the same pre-trained parameters initialize each downstream model, which adds only the appropriate output layer.[^devlin-bert-2018]

## Encoder and input interface

BERT is a multi-layer bidirectional Transformer encoder. The paper reports BERT Base ($L=12$, $H=768$, $A=12$, 110M parameters) and BERT Large ($L=24$, $H=1024$, $A=16$, 340M parameters); its feed-forward width is $4H$.[^devlin-bert-2018]

A token input is the sum of WordPiece token, position, and segment embeddings. A sequence begins with `[CLS]`; sentence pairs are joined by `[SEP]` and distinguished with learned A/B segment embeddings. The final `[CLS]` state is the aggregate representation for classification, while final token states support token-level outputs.[^devlin-bert-2018]

## Transfer pattern

For every downstream task, all pre-trained parameters are fine-tuned. Classification attaches a linear classifier to `[CLS]`; token labeling and extractive question answering attach outputs to token states. A packed question–passage or text pair can therefore interact through the encoder’s bidirectional self-attention rather than requiring a separate cross-attention stage.[^devlin-bert-2018]

The source reports task-dependent fine-tuning with batch sizes 16 or 32, Adam learning rates in $\{2,3,5\}\times10^{-5}$, and 2–4 epochs; these are reported experimental settings, not a general prescription.[^devlin-bert-2018]

## Reported evidence and limits

In its contemporary evaluations, BERT Large reported a GLUE leaderboard score of 80.5, SQuAD v1.1 test F1 of 93.2 using an ensemble with TriviaQA fine-tuning, and SQuAD v2.0 test F1 of 83.1 for a single model.[^devlin-bert-2018] These are historical, benchmark- and setup-specific results, not evidence of current state of the art.

## Relationships

- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md)’s encoder-style self-attention stack, without its autoregressive decoder.
- **Pre-trained by:** [BERT masked-language and next-sentence pre-training](bert-masked-language-and-next-sentence-pre-training.md).

[^devlin-bert-2018]: Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova, “BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,” arXiv:1810.04805v2, bundled [LaTeX source](../raw/arXiv-1810.04805v2/main.tex), including its included sections, tables, and figure PDFs.
