---
type: Concept
title: ALiBi attention with linear biases
description: ALiBi adds fixed head-specific linear distance penalties to causal-attention logits, creating a recency prior that can extend positional behavior beyond the training length without positional embeddings.
tags: [alibi, positional-encoding, attention, transformer, long-context, causal-language-modeling]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:41:40Z }
sources:
  - id: alibi-summary
    resource: ../raw/ALiBi.md
    title: "ALiBi overview (Vietnamese summary)"
---

# ALiBi attention with linear biases

Attention with Linear Biases (ALiBi) replaces token positional embeddings in a causal Transformer with fixed, head-specific linear penalties on attention logits by query–key distance. The resulting recency prior is translation-invariant over sequence position and can be evaluated at lengths beyond training, but it neither guarantees retained long-range quality nor changes dense attention’s quadratic cost.[^alibi-summary]

## Mechanism

For a head $h$, causal attention changes the usual scaled dot-product logit to:

$$
s_{ij}^{(h)} = \frac{q_i^{(h)\top} k_j^{(h)}}{\sqrt{d_k}} - m_h(i-j), \qquad j \leq i,
$$

where $m_h > 0$ is a fixed slope and future keys remain causally masked. Thus a key farther in the past receives a larger negative bias, while sufficiently strong content compatibility can still outweigh that bias; ALiBi is a soft recency preference, not a local-attention mask.[^alibi-summary]

Slopes differ across heads and are exponentially distributed: large slopes specialize heads toward nearby context, whereas small slopes leave heads more able to attend farther back. In unnormalized softmax weights, the linear logit term multiplies content compatibility by $\exp(-m_h d)$, so the mechanism can also be understood as head-specific exponential distance decay.[^alibi-summary]

## Length extrapolation and cost

Because the bias depends only on relative distance rather than an absolute position index, the same rule applies after shifting both query and key positions. It can therefore be computed for distances not observed during training without new position embeddings or interpolation. This mechanical extrapolation does not establish stable perplexity, retrieval, or reasoning quality at arbitrary lengths; distant evidence is increasingly disadvantaged by the bias.[^alibi-summary]

The cited study reports that a roughly 1.3B-parameter model trained at 1,024 tokens and evaluated at 2,048 obtained perplexity comparable to a sinusoidal-position baseline trained at 2,048, with reported training-time and memory reductions of about 11% in that setup. These results are experiment-specific rather than a guarantee for every model or target length.[^alibi-summary]

ALiBi modifies logits only. Full dense attention still has $O(L^2)$ score computation and memory pressure with sequence length, although an implementation can fuse or otherwise avoid materializing the bias matrix.[^alibi-summary]

## Trade-offs

ALiBi has no learned positional parameters and is simple to add to a decoder-only attention implementation. Its monotonic recency prior is useful when nearby context is often most relevant, but can be limiting for tasks that require reliable retrieval of extremely distant tokens. The supplied overview describes the original formulation as focused on causal language models; bidirectional use requires an appropriate bias design rather than directly assuming the causal matrix.[^alibi-summary]

## Relationships

- **Alternative to:** [Rotary position embedding (RoPE)](rotary-position-embedding.md). ALiBi adds distance-dependent logits, whereas RoPE rotates queries and keys before their dot product.[^alibi-summary]
- **Used by:** [BLOOM open multilingual language model](bloom-open-multilingual-language-model.md), whose supplied overview reports ALiBi in its causal architecture.[^alibi-summary]
- **Uses:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) as the attention computation whose logits it biases.
- **Constrained by:** [Self-attention computational profile](self-attention-computational-profile.md): it retains dense self-attention’s quadratic sequence-length scaling.[^alibi-summary]

[^alibi-summary]: “ALiBi overview” (Vietnamese summary), [raw source](../raw/ALiBi.md), Sections 1–18. This is secondary-source evidence linking to Press, Smith, and Lewis, “Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation” (arXiv:2108.12409) and its implementation repository; those primary materials have not been independently ingested here.
