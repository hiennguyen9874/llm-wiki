---
type: Concept
title: Transformer sequence transduction architecture
description: The original Transformer replaces sequence-aligned recurrence and convolution with stacked self-attention, cross-attention, and position-wise feed-forward layers.
tags: [transformer, sequence-transduction, encoder-decoder, self-attention]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:18:25Z }
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
---

# Transformer sequence transduction architecture

The original Transformer is an autoregressive encoder–decoder architecture that replaces sequence-aligned recurrence and convolution with attention and position-wise computation. The encoder builds contextual representations with bidirectional self-attention; the decoder combines causal self-attention with attention over encoder outputs. Because attention itself has no sequence-order bias, positional encodings are added to token embeddings.[^vaswani-transformer-2017]

## Architecture

The base model stacks six encoder and six decoder layers with model width $d_{model}=512$.[^vaswani-transformer-2017]

- **Encoder layer:** multi-head self-attention followed by a position-wise feed-forward network.
- **Decoder layer:** masked multi-head self-attention, encoder–decoder cross-attention, then a position-wise feed-forward network.
- **Residual path:** every sublayer uses the post-normalization form $LayerNorm(x + Sublayer(x))$.
- **Feed-forward sublayer:** the same two-layer ReLU network is applied independently at every token position, with inner width 2048 in the base model.
- **Autoregressive constraint:** decoder self-attention masks future positions, and decoder inputs are shifted right.

The model uses learned token embeddings and shares weights between source embeddings, target embeddings, and the pre-softmax projection. It adds fixed sinusoidal positional encodings whose wavelengths form a geometric progression; learned positional embeddings gave nearly identical development results in the reported ablation.[^vaswani-transformer-2017]

## Functional decomposition

The architecture separates three kinds of work:

1. [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) retrieves and mixes information across token positions.
2. Position-wise feed-forward networks transform each position independently.
3. Residual connections and layer normalization carry and stabilize representations across depth.

This decomposition enables all positions in a known training sequence to be processed in parallel, although autoregressive generation still emits output tokens sequentially.[^vaswani-transformer-2017]

## Reported evidence

On WMT 2014 English–German, the paper reports 27.3 BLEU for the base model and 28.4 for the big model. The base model trained for 100,000 steps (about 12 hours) and the big model for 300,000 steps (3.5 days), each on eight NVIDIA P100 GPUs. A four-layer variant also transferred to English constituency parsing, reaching 91.3 F1 with WSJ-only training and 92.7 in the reported semi-supervised setting.[^vaswani-transformer-2017]

These are historical results under the paper’s datasets, preprocessing, checkpoint averaging, and beam-search setup; they do not establish current state of the art.

## Contradictions

The v7 source is internally inconsistent about WMT 2014 English–French: its abstract and results table report 41.8 BLEU for the big model, while the results prose reports 41.0. This page does not resolve the discrepancy.[^vaswani-transformer-2017]

## Relationships

- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) for encoder self-attention, causal decoder self-attention, and encoder–decoder cross-attention.
- **Enabled by:** [Self-attention computational profile](self-attention-computational-profile.md), particularly constant sequential depth per full-sequence layer during training.

[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762v7, bundled [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), including `model_architecture.tex`, `why_self_attention.tex`, `training.tex`, and `results.tex`.
