---
type: Concept
title: Rotary position embedding (RoPE)
description: RoPE encodes absolute token positions by rotating query and key coordinate pairs, causing their attention dot product to depend on relative position.
tags: [rope, positional-encoding, attention, transformer, long-context]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:39:20+07:00 }
sources:
  - id: rope-summary
    resource: ../raw/RoPE.md
    title: "RoPE overview (Vietnamese summary)"
---

# Rotary position embedding (RoPE)

Rotary position embedding (RoPE), introduced with RoFormer, encodes a token’s absolute position by rotating pairs of query and key coordinates by position-dependent angles. When a query at position $m$ is compared with a key at position $n$, the rotations combine so the dot product depends on $n-m$; thus relative-position information enters the attention score without adding a separate positional vector to the token representation.[^rope-summary]

## Mechanism

For a two-dimensional coordinate pair, RoPE applies the rotation $R(m\theta)$ at position $m$. Rotation is orthogonal, so it preserves vector norm. Across an even-dimensional attention head, RoPE rotates each coordinate pair with its own frequency, conventionally $\theta_i = 10000^{-2i/d}$ for pair $i$ in a head of dimension $d$.[^rope-summary]

If unrotated query and key vectors are $q_m$ and $k_n$, the source derives:

$$
(R_m q_m)^\top(R_n k_n) = q_m^\top R_{n-m} k_n.
$$

The sign of the relative offset follows the query/key rotation convention, but the key property is dependence on their difference rather than their independent absolute positions. Shifting both positions by the same amount leaves that difference unchanged.[^rope-summary]

## Use in attention

RoPE is applied after forming the query and key projections and before computing their scaled dot-product attention scores. It is ordinarily applied per attention head and usually not to value vectors, because position dependence is needed in $QK^\top$ rather than in the values being aggregated.[^rope-summary]

Efficient implementations avoid materializing rotation matrices. Given aligned sine and cosine caches, they compute the rotation as $x\odot\cos\phi + \operatorname{rotate\_half}(x)\odot\sin\phi$. Implementations must consistently use either interleaved coordinate pairs or a split-half pairing convention; the source cautions that a checkpoint and rotary implementation using different conventions cannot simply be mixed.[^rope-summary]

## Context-length boundary

Fixed sine and cosine formulas can be evaluated at positions beyond those seen in training, but that mechanical property does not ensure useful long-context extrapolation. At much longer positions, phase patterns can fall outside the training distribution and retrieval quality can degrade. The overview identifies position interpolation, frequency/base changes, per-frequency scaling, and long-sequence fine-tuning as later RoPE-based context-extension techniques, not features of the original RoFormer method.[^rope-summary]

The source also characterizes RoPE’s multi-frequency sum as having a soft long-distance-decay tendency through phase cancellation. This is not a monotonic distance penalty or a guarantee that a distant query–key pair receives a low score.[^rope-summary]

## Relationships

- **Alternative to:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), whose original design adds sinusoidal positional vectors to token embeddings; RoPE instead rotates projected queries and keys.[^rope-summary]
- **Contrasts with:** [BLOOM open multilingual language model](bloom-open-multilingual-language-model.md), which the available summary describes as using additive ALiBi attention biases rather than RoPE.
- **Used by:** [LLaMA efficient pre-trained language models](llama-efficient-pre-trained-language-models.md), whose available summary reports rotary positional embeddings in its decoder-only architecture.

[^rope-summary]: “RoPE overview” (Vietnamese summary), [raw source](../raw/RoPE.md), Sections 1–17. This is secondary-source evidence linking to Su et al., “RoFormer: Enhanced Transformer with Rotary Position Embedding” (arXiv:2104.09864); the primary paper has not been independently ingested here.
