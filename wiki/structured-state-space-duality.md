---
type: Concept
title: Structured State Space Duality
description: SSD expresses selective state-space models as semiseparable matrix transformations and identifies a scalar-transition subset with structured masked attention.
tags: [attention, linear-attention, mamba, semiseparable-matrices, ssm]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:14:44Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Structured State Space Duality

Structured State Space Duality (SSD) casts a selective state-space model as multiplication by a causal semiseparable matrix. Its scalar-identity-transition case is exactly a form of structured masked kernel attention: it has both an efficient recurrent form and a quadratic, attention-like form.[^dao-gu-2024]

## Matrix and attention forms

An SSM recurrence $h_t=A_th_{t-1}+B_tx_t$, $y_t=C_t^\top h_t$ induces a causal matrix $M$ with entries $M_{ji}=C_j^\top A_{j:i}B_i$. The authors identify this as a sequentially semiseparable representation: every on-or-below-diagonal submatrix has rank at most the state size $N$. This provides a compressed $O(TN)$ representation and recurrent matrix-vector multiplication for a length-$T$ sequence.[^dao-gu-2024]

For the SSD specialization, each transition is a scalar times the identity. Its quadratic form is

$$
Y=(L\circ QK^\top)V,\qquad L_{ij}=\prod_{r=j+1}^{i}a_r\ \text{ for } i\ge j,
$$

where the input-dependent scalar transitions produce a causal 1-semiseparable mask $L$. Reordering the same contraction yields a recurrence. Thus SSD shares linear attention's feature expansion and contraction but replaces its all-ones causal mask with a data-dependent decay/selection mask.[^dao-gu-2024]

The paper further proves that a structured-masked-attention instance with bounded-order autoregression must use a semiseparable mask. This does not make SSD equivalent to standard softmax attention: softmax has no finite feature-map reassociation of this form.[^dao-gu-2024]

## Block SSD algorithm

The reported SSD algorithm partitions the semiseparable matrix into chunks. It evaluates diagonal blocks with the quadratic dual, factors off-diagonal blocks through the recurrent state, and scans only the chunk-level state transitions. With state size, head width, and chunk length all $N$, the authors give $O(TN^2)$ training FLOPs, $O(TN)$ activation memory, $O(N^2)$ recurrent inference memory, and $O(N^2)$ inference FLOPs per head; the dominant work is matrix multiplication.[^dao-gu-2024]

This combines bounded SSM-style recurrent state with attention-like hardware utilization, but its restriction from diagonal transitions to scalar-identity transitions trades some SSM expressivity for that computation pattern.[^dao-gu-2024]

## Relationships

- **Generalizes:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) from an all-ones causal mask to structured masks with fast multiplication.
- **Contrasts with:** [Self-attention computational profile](self-attention-computational-profile.md): full softmax attention retains token-addressable interactions, whereas SSD compresses history into fixed-size state.
- **Used by:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) as its sequence-mixing layer.

## Evidence limits

The duality, complexity claims, and algorithm are primary-paper results. Wall-clock gains depend on the implementation, state size, sequence length, precision, and accelerator; the matrix formulation does not establish quality parity with softmax attention or every selective SSM.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 2–6 and Appendix algorithms.