---
type: Concept
title: Gated DeltaNet architecture and chunkwise training
description: Gated DeltaNet adds scalar learned decay to DeltaNet’s corrective recurrence and extends its WY/UT chunkwise algorithm for hardware-efficient training.
tags: [deltanet, gating, linear-attention, mamba, parallelism]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-27T03:11:23Z }
sources:
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
---

# Gated DeltaNet architecture and chunkwise training

Gated DeltaNet combines a scalar learned forgetting gate with DeltaNet’s key-addressed corrective update. Its chunkwise extension applies decay-aware scaling to the prior DeltaNet WY/UT construction, retaining recurrent state between chunks while expressing most within-chunk work as matrix multiplication.[^gated-deltanet-2025]

## Gated delta rule

For state $S_t$, normalized key $k_t$, value $v_t$, write strength $\beta_t$, and scalar decay $\alpha_t\in(0,1)$, the reported recurrence is

$$
S_t=S_{t-1}\bigl(\alpha_t(I-\beta_tk_tk_t^\top)\bigr)+\beta_tv_tk_t^\top.
$$

The rank-one term revises the association selected by the current key, while scalar $\alpha_t$ decays the entire state. Thus the gate can broadly clear accumulated memory, unlike ungated DeltaNet, but it does not give different state channels independent retention rates.[^gated-deltanet-2025]

The authors also present this recurrence as test-time SGD on a key--value regression loss with adaptive weight decay. That is an interpretation of the update and online-learning objective, not evidence that every learned gate performs useful semantic forgetting.[^gated-deltanet-2025]

## Block and hybrid designs

The basic model retains a Llama-style token-mixer/MLP stack, replacing self-attention with the gated delta rule. Query and key paths use linear projection, short convolution, SiLU, and L2 normalization; the value path omits L2 normalization. The $\alpha$ and $\beta$ parameters use linear projections, and the mixer output is normalized, gated, and projected.[^gated-deltanet-2025]

Two reported hybrids reintroduce token-addressable local context:

- **H1:** alternates Gated DeltaNet and sliding-window-attention blocks.
- **H2:** repeats Mamba2, Gated DeltaNet, and sliding-window-attention blocks.
- **Qwen3.8-Flash-Next:** repeats three Gated DeltaNet layers and one global-attention layer. Its variant uses a bounded sigmoid output gate and zero-centered RMSNorm; the report retains RoPE in global attention because a NoPE ablation later produced more endless generation after post-training despite similar pre-training behavior.[^qwen38-next-report]

These are hybrid architectures, not evidence that the fixed-state recurrence alone provides the hybrid models’ retrieval behavior.[^gated-deltanet-2025][^qwen38-next-report]

## Decay-aware chunkwise algorithm

Within a chunk, the algorithm uses cumulative products of $\alpha$ to rescale queries, keys, the carried state, and the DeltaNet WY factors. A lower-triangular decay-masked UT transform produces the pseudo-values used for causal intra-chunk interactions. The resulting output and next-state computation use batched matrix operations, while the final state still flows recurrently from one chunk to the next.[^gated-deltanet-2025]

This is an exact re-expression of the stated gated recurrence. It preserves the same broad hardware strategy as Parallel DeltaNet, but scalar decay distinguishes it from Mamba-2’s scalar-transition SSD and from channel-wise gated variants such as KDA.[^gated-deltanet-2025]

## Relationships

- **Implements:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) as a scalar-decay corrective memory.
- **Extends:** [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md) with decay-aware WY/UT factors.
- **Contrasts with:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md), whose scalar decay has no key-conditioned rank-one correction.
- **Evaluated by:** [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md).

## Evidence limits

The recurrence, block details, derivation, and hybrids are primary-source author claims. The chunkwise derivation establishes equivalence to the stated update, not universal numerical stability or end-to-end speed; those depend on precision, kernels, head size, sequence length, and hardware.

[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–4, Figure 1, and Appendix A.

[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Section 2.1.1.
