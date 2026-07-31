---
type: Concept
title: GPT-2 WebText pre-training and architecture
description: GPT-2 scales a causal Transformer language model on WebText with byte-level BPE, a 1,024-token context, pre-layer normalization, and depth-scaled residual initialization.
tags: [gpt-2, causal-language-modeling, webtext, tokenization, transformer]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:33:02Z }
sources:
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
---

# GPT-2 WebText pre-training and architecture

GPT-2 is a causal Transformer language model trained on WebText, a curated web-text corpus. Relative to the earlier GPT configuration, the report uses byte-level BPE, expands the context window to 1,024 tokens, adopts pre-layer normalization, and scales residual-layer weights at initialization to account for depth.[^radford-gpt-2-2019]

## WebText corpus

WebText was built from the text of outbound Reddit links that received at least three karma, using Dragnet and Newspaper content extractors. The preliminary version used in the report excludes links created after December 2017; after de-duplication and heuristic cleaning, it contains slightly more than 8 million documents and 40 GB of text. Wikipedia documents were removed to reduce overlap with common evaluation datasets.[^radford-gpt-2-2019]

Reddit karma is a heuristic for user interest, not a general quality guarantee. The corpus construction and cutoff also make reported benchmark results contingent on possible web-data overlap.[^radford-gpt-2-2019]

## Input representation and model changes

The model uses a byte-level variant of BPE with a 256-byte base vocabulary. To avoid allocating merges to punctuation variants of the same word, BPE is prevented from merging across character categories, except for spaces; the resulting vocabulary has 50,257 tokens. This representation can assign probabilities to any Unicode string without an out-of-vocabulary token.[^radford-gpt-2-2019]

GPT-2 otherwise largely follows the earlier GPT decoder-only Transformer, with these reported changes:[^radford-gpt-2-2019]

- Layer normalization moves to the input of each sub-block, and another layer normalization follows the final self-attention block.
- Residual-layer weights at initialization are scaled by $1/\sqrt{N}$, where $N$ is the number of residual layers.
- Context length rises from 512 to 1,024 tokens and the batch size is 512.

The report trains approximately log-uniformly spaced model sizes: 117M parameters (12 layers, width 768), 345M (24, 1024), 762M (36, 1280), and 1.542B (48, 1600). Learning rates were manually tuned for perplexity on a 5% held-out WebText sample; the authors report that all sizes still underfit WebText.[^radford-gpt-2-2019]

## Relationships

- **Extends:** [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md)'s decoder-only causal language-model approach.
- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md)'s masked self-attention stack, but not its encoder or encoder-decoder attention.
- **Evaluated by:** [GPT-2 zero-shot multitask evaluation and overlap auditing](gpt-2-zero-shot-multitask-evaluation-and-overlap-auditing.md).

[^radford-gpt-2-2019]: Alec Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), bundled [PDF](../raw/gpt2.pdf), especially Sections 2.1–2.3 and Table 2.