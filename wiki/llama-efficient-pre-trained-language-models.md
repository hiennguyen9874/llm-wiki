---
type: Concept
title: LLaMA efficient pre-trained language models
description: LLaMA is Meta AI’s reported 7B-to-65B decoder-only base-model family, which combines a data-intensive training allocation with RMSNorm, SwiGLU, and RoPE to pursue strong capability at lower inference cost.
tags: [llama, meta, causal-language-modeling, pre-training, efficient-training, open-weights]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:20:06+07:00 }
sources:
  - id: llama-summary
    resource: ../raw/LLaMA.md
    title: "LLaMA overview (Vietnamese summary)"
---

# LLaMA efficient pre-trained language models

LLaMA (Large Language Model Meta AI) is Meta AI’s reported family of 7B, 13B, 33B, and 65B parameter decoder-only causal language models. The supplied summary presents its central result as an efficiency trade-off: training smaller models on substantially more tokens can preserve competitive reported benchmark performance while reducing inference-time model size and cost.[^llama-summary]

## Family and training allocation

The reported parameter counts are 6.7B, 13.0B, 32.5B, and 65.2B. LLaMA-7B and -13B train on 1.0T tokens, while -33B and -65B train on 1.4T; the post-tokenization corpus totals about 1.4T tokens. Most data is used once, with Wikipedia and books used about twice.[^llama-summary]

The summary describes this allocation as motivated by the Chinchilla result that a smaller model trained on more data can be preferable under a fixed training-compute budget. It further frames LLaMA’s practical objective as performance under an inference budget, rather than pretraining FLOPs alone.[^llama-summary]

The reported mixture is 67% English CommonCrawl, 15% C4, 4.5% each GitHub, Wikipedia, and Gutenberg/Books3, 2.5% arXiv, and 2% Stack Exchange. The source says the inputs were publicly accessible, but explicitly cautions that accessibility does not establish a clean copyright or rights status, including for Books3.[^llama-summary]

Reported preprocessing includes deduplication, language and web-quality filtering, restricted-license GitHub selection (Apache, BSD, or MIT), boilerplate and low-quality-code removal, direct LaTeX processing for arXiv, and book-overlap filtering. The tokenizer is a 32,000-token SentencePiece BPE model with split digits and byte fallback.[^llama-summary]

## Architecture and optimization recipe

LLaMA uses next-token prediction with a decoder-only Transformer. The source reports pre-normalization with RMSNorm, SwiGLU feed-forward layers, and rotary positional embeddings (RoPE), rather than learned absolute position embeddings. This is a combination of prior architectural choices, not a wholly new Transformer design.[^llama-summary]

All variants reportedly use an approximately 4M-token global batch. Training uses AdamW with $\beta_1=0.9$, $\beta_2=0.95$, 0.1 weight decay, 1.0 gradient clipping, 2,000 warm-up steps, and cosine learning-rate decay to 10% of the peak rate. The summary also reports memory-efficient causal attention, activation checkpointing, model and sequence parallelism, and overlapped GPU computation and communication.[^llama-summary]

For LLaMA-65B, the source reports training on 2,048 A100 80GB GPUs at roughly 380 tokens/second/GPU for about 21 days. These are reported system measurements, not an independently reproduced cost estimate.[^llama-summary]

## Reported efficiency result

The summary reports that LLaMA-13B exceeded GPT-3 175B on most—not all—benchmarks in the cited comparison tables, and that LLaMA-65B was competitive with Chinchilla-70B and PaLM-540B. These are benchmark- and prompt-dependent results; they do not establish general superiority across tasks or deployment settings.[^llama-summary]

## Relationships

- **Informed by:** [Chinchilla compute-optimal training allocation](chinchilla-compute-optimal-training-allocation.md), whose data-intensive fixed-compute framing the summary identifies as a motivation for LLaMA.[^llama-summary]
- **Compared with:** [GPT-3 scaled causal language model](gpt-3-scaled-causal-language-model.md) in the source’s reported benchmark results.[^llama-summary]
- **Limited by:** [LLaMA evaluation, alignment, and limitations](llama-evaluation-alignment-and-limitations.md).

[^llama-summary]: “LLaMA overview” (Vietnamese summary), [raw source](../raw/LLaMA.md), Sections 1–5, 7, 9–10. This is secondary-source evidence that links to arXiv:2302.13971 and a Llama 2 publication; neither primary source has been independently ingested here.
