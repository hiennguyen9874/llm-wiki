---
type: Concept
title: Scaled dot-product and multi-head attention
description: Scaled dot-product attention retrieves weighted values from query–key compatibility, while multiple projected heads retrieve from distinct representation subspaces in parallel.
tags: [attention, softmax-attention, multi-head-attention, retrieval]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:35:10Z }
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: "FlashAttention overview (Vietnamese summary)"
---

# Scaled dot-product and multi-head attention

Attention maps a query and key–value pairs to a weighted sum of values. Scaled dot-product attention computes all query–key compatibilities with matrix multiplication, scales them before softmax, and uses the resulting weights to retrieve values. Multi-head attention repeats this operation over separately learned projections so different heads can retrieve from different positions and representation subspaces.[^vaswani-transformer-2017]

## Scaled dot-product attention

For query, key, and value matrices $Q$, $K$, and $V$:

$$
Attention(Q,K,V)=softmax\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

The $1/\sqrt{d_k}$ factor controls logit magnitude. Under the paper’s simplifying assumption that query and key components are independent with mean zero and variance one, their dot product has variance $d_k$; without scaling, larger key dimensions can push softmax into regions with very small gradients.[^vaswani-transformer-2017]

An optional pre-softmax mask sets forbidden compatibilities to $-\infty$. The Transformer decoder uses this to prevent each position from attending to future output positions.[^vaswani-transformer-2017]

## Multi-head attention

Each head applies attention to distinct learned projections:

$$
head_i=Attention(QW_i^Q,KW_i^K,VW_i^V)
$$

$$
MultiHead(Q,K,V)=Concat(head_1,\ldots,head_h)W^O
$$

The base Transformer uses eight heads with $d_k=d_v=64$ and $d_{model}=512$. Splitting the model dimension across heads keeps total cost similar to one full-width head while avoiding a single weighted average as the only retrieval channel. In the paper’s development ablation, one head underperformed the best tested multi-head setting, but quality also declined with too many heads.[^vaswani-transformer-2017]

## Three retrieval patterns

- **Encoder self-attention:** queries, keys, and values come from the prior encoder layer; every position can retrieve from every input position.
- **Causal decoder self-attention:** all three come from the prior decoder layer, with future positions masked.
- **Encoder–decoder cross-attention:** decoder states provide queries, while encoder outputs provide keys and values.[^vaswani-transformer-2017]

## Relationships

- **Used by:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md).
- **Has profile:** [Self-attention computational profile](self-attention-computational-profile.md) when used as full self-attention over a sequence.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), which changes the attention formulation to permit a bounded recurrent state rather than retaining token-addressable interactions.
- **Implemented by:** [FlashAttention IO-aware exact attention](flashattention-io-aware-exact-attention.md), which preserves this formula while changing GPU data movement and evaluation order.[^flashattention-summary]
- **Modified by:** [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), which shares K/V projections across query heads to reduce decode-time cache traffic.[^mqa-summary]

[^vaswani-transformer-2017]: Ashish Vaswani et al., “Attention Is All You Need,” arXiv:1706.03762v7, bundled [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially `model_architecture.tex` and its referenced attention diagrams.

[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [raw source](../raw/FlashAttention.md), Sections 1–8. This is secondary-source evidence; its cited primary FlashAttention paper has not been independently ingested here.

[^mqa-summary]: “MQA overview” (Vietnamese summary), [raw source](../raw/MQA.md), Sections 1–6 and 10. This is secondary-source evidence; its cited primary MQA and GQA papers have not been independently ingested here.
