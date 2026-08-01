---
type: Concept
title: Parallel DeltaNet chunkwise training
description: Parallel DeltaNet expresses delta-rule state transitions with compact Householder products and a chunkwise triangular transform, exposing GPU-friendly matrix multiplications without materializing every matrix state.
tags: [deltanet, linear-attention, parallelism, training]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:24:41Z }
sources:
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
---

# Parallel DeltaNet chunkwise training

Parallel DeltaNet makes the corrective DeltaNet recurrence practical to train at language-model scale by representing rank-one state transitions compactly within chunks, then expressing most intra-chunk work as matrix multiplication. It retains recurrent state across chunks and direct recurrent decoding; it is not a fully sequence-parallel DeltaNet algorithm.[^parallel-deltanet-2024]

## From correction to a compact additive form

For state $S_t$, key $k_t$, value $v_t$, and learned write strength $\beta_t$, DeltaNet updates

$$
S_t=S_{t-1}(I-\beta_t k_tk_t^\top)+\beta_t v_tk_t^\top.
$$

The rank-one factor subtracts the value currently retrieved by $k_t$ before writing toward $v_t$. The paper rewrites the resulting state as an additive sum of pseudo-values $u_i k_i^\top$, where each $u_i$ is the scaled residual between $v_i$ and the prior state’s retrieval. Products of the rank-one transitions admit a compact WY/Householder-style representation, so constructing the required vectors does not require materializing a full $d\times d$ state at every token.[^parallel-deltanet-2024]

## Chunkwise algorithm

For each length-$C$ chunk, the method represents the within-chunk transition and write contribution as low-rank sums. A lower-triangular UT transform solves for the corresponding $W$ and $U$ matrices from the chunk’s keys, values, and $\beta$s. The output and the transition to the next chunk can then use the same broad pattern as chunkwise linear attention: a carried state supplies inter-chunk context, while causal intra-chunk interactions use batched matrix products.[^parallel-deltanet-2024]

This removes the need to store all token-level matrix states and reduces sequential depth from sequence length to the number of chunks (absent an additional chunk-level scan). The implementation recomputes chunk-level states during backpropagation to save GPU memory. It is exact for the stated recurrence, rather than an approximation to its forward computation.[^parallel-deltanet-2024]

## Hardware boundary

The paper’s H100 kernel comparison reports chunkwise-versus-recurrent speedups from $5.5\times$ (length 2,048, head width 64) to $13.7\times$ (length 2,048, width 256); longer tested sequences also increase the reported gain. These are kernel measurements against its recurrent implementation, not end-to-end claims against every attention or recurrent model.[^parallel-deltanet-2024]

The method avoids a fully parallel DeltaNet form because its triangular transform would require a sequence-length matrix inverse with cubic scaling without further changes. Its state-to-state dependencies also remain costlier than GLA’s elementwise recurrence: the authors report lower DeltaNet training speed than GLA and identify head/state-size scaling as a practical constraint.[^parallel-deltanet-2024]

## Relationships

- **Parallelizes:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md)’s targeted corrective update for efficient training.
- **Adapts:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md)’s chunkwise separation of intra-chunk parallel work and cross-chunk state propagation.
- **Contrasts with:** [Structured State Space Duality](structured-state-space-duality.md), whose scalar transitions give a semiseparable masked-attention form; Parallel DeltaNet instead handles key-conditioned rank-one matrix transitions.
- **Evaluated by:** [DeltaNet evaluation and hybrid-attention trade-offs](deltanet-evaluation-and-hybrid-attention-trade-offs.md).

## Evidence limits

The algebra, pseudocode, and kernel measurements are author-reported primary-source evidence. The speedups depend on the specified H100, sequence length, head width, kernel implementations, and the fixed product of batch size and length used in that comparison. They do not establish universal training throughput, quality, or long-context behavior.

[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–3, Table 1, and appendices on the WY/UT derivations and pseudocode.
