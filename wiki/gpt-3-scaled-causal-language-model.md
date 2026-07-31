---
type: Concept
title: GPT-3 scaled causal language model
description: GPT-3 scales the GPT-2-style causal Transformer to 175B parameters, a 2,048-token context, 300B training tokens, and a quality-weighted web-and-books corpus.
tags: [gpt-3, causal-language-modeling, pre-training, sparse-attention, training-data]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:42:00Z }
sources:
  - id: brown-gpt-3-2020-v4
    resource: ../raw/arXiv-2005.14165v4/main.tex
    title: Language Models are Few-Shot Learners
---

# GPT-3 scaled causal language model

GPT-3 is the 175B-parameter member of a family of eight autoregressive Transformers trained to test scaling and in-context behavior. It retains the GPT-2-style causal architecture and tokenizer, adds alternating dense and locally banded sparse-attention layers, and uses a 2,048-token context window.[^brown-gpt-3-2020-v4]

## Model family and training

The reported family ranges from 125M to 175B parameters. The 175B model has 96 layers, width 12,288, 96 attention heads of dimension 128, a 3.2M-token batch, and a peak learning rate of $6.0\times10^{-5}$; every family member trains for 300B tokens.[^brown-gpt-3-2020-v4]

Training uses Adam ($\beta_1=0.9$, $\beta_2=0.95$, $\epsilon=10^{-8}$), global gradient clipping at 1.0, weight decay 0.1, a 375M-token linear warmup, and cosine learning-rate decay to 10% of its initial value over 260B tokens. Batches grow from 32K tokens over the first 4–12B tokens; documents are packed into full context windows and separated by an end-of-text token without special attention masking.[^brown-gpt-3-2020-v4]

## Data mixture and processing

The 300B-token training mixture is 60% filtered Common Crawl (410B available tokens), 22% WebText2 (19B), 8% Books1 (12B), 8% Books2 (55B), and 3% Wikipedia (3B). Sampling intentionally oversamples the smaller, selected corpora, so WebText2 and Wikipedia are seen about 2.9 and 3.4 times respectively while Common Crawl and Books2 are sampled less than once.[^brown-gpt-3-2020-v4]

The source filters Common Crawl by a logistic-regression quality score trained to distinguish curated reference data from raw crawl, then stochastically favors high-scoring documents. It fuzzily deduplicates with MinHashLSH within corpora and removes WebText-like content from Common Crawl, reducing the data by about 10% on average. These quality proxies and the web-derived corpus do not establish that the resulting data is representative, unbiased, or free of benchmark leakage.[^brown-gpt-3-2020-v4]

## Relationships

- **Extends:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) with a larger context, data mixture, scale, and alternating sparse-attention pattern.
- **Applies:** [Kaplan compute-optimal training allocation](kaplan-compute-optimal-training-allocation.md)'s then-current prescription to favor larger models trained on comparatively fewer tokens.
- **Evaluated by:** [GPT-3 in-context learning evaluation and results](gpt-3-in-context-learning-evaluation-and-results.md) and [GPT-3 benchmark contamination audit](gpt-3-benchmark-contamination-audit.md).

[^brown-gpt-3-2020-v4]: Tom B. Brown et al., “Language Models are Few-Shot Learners,” arXiv:2005.14165v4 (2020), bundled [LaTeX source](../raw/arXiv-2005.14165v4/main.tex), especially Sections 2.1–2.3, Appendix A–B, and Tables 1–2.
