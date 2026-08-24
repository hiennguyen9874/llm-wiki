---
type: Concept
title: Gated DeltaNet-2 decoupled delta rule and training
description: Gated DeltaNet-2 separates KDA’s scalar active edit into channel-wise key-side erase and value-side write gates while retaining channel-wise decay and chunkwise training.
tags: [associative-memory, deltanet, gating, linear-attention, parallelism]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:20:33Z }
sources:
  - id: gated-deltanet-2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
---

# Gated DeltaNet-2 decoupled delta rule and training

Gated DeltaNet-2 keeps Kimi Delta Attention’s (KDA) channel-wise decay but replaces its one scalar delta strength with independent channel-wise erase and write gates. The erase gate selects the key-side direction used to read and remove old content; the write gate selects value channels to commit. Tying both gates recovers KDA, and additionally tying decay recovers Gated DeltaNet.[^gated-deltanet-2-2026]

## Asymmetric gated delta update

For state $S_t\in\mathbb{R}^{d_k\times d_v}$, key $k_t$, value $v_t$, channel-wise decay $\alpha_t$, erase gate $b_t\in[0,1]^{d_k}$, and write gate $w_t\in[0,1]^{d_v}$, define $D_t=\operatorname{Diag}(\alpha_t)$, $e_t=b_t\odot k_t$, and $z_t=w_t\odot v_t$. The stated recurrence is

$$
S_t=(I-k_te_t^\top)D_tS_{t-1}+k_tz_t^\top.
$$

Equivalently, it decays the state, reads it along $e_t$, and adds $k_t(z_t-(D_tS_{t-1})^\top e_t)^\top$. The asymmetric rank-one factor preserves the ordinary key as the write direction while making the erase read direction channel-selective. The source gives separate sigmoid projections for $b_t$ and $w_t$ and a negative log-decay projection for $\alpha_t$.[^gated-deltanet-2-2026]

Setting $b_t=\beta_t\mathbf{1}_{d_k}$ and $w_t=\beta_t\mathbf{1}_{d_v}$ yields the KDA update. Setting $\alpha_t=\alpha_t^{\mathrm{scalar}}\mathbf{1}_{d_k}$ as well yields scalar-decay Gated DeltaNet. These are algebraic reductions of the stated recurrence, not empirical equivalence claims for independently trained models.[^gated-deltanet-2-2026]

## Chunkwise implementation

The authors absorb cumulative channel-wise decay into asymmetric normalized factors $\bar k_r=\gamma_r^{-1}\odot k_r$ and $\bar e_r=\gamma_r\odot(b_r\odot k_r)$, where $\gamma_r$ is the within-chunk cumulative decay. A strictly lower triangular matrix built from $\bar e\bar k^\top$ has a shared WY inverse for erase-side and write-side auxiliaries. Thus token interactions within a fixed-size chunk are dense products and triangular solves, while the state remains recurrent across chunks.[^gated-deltanet-2-2026]

Unlike a scalar gate, the vector gates cannot be applied as a post-scale in the backward pass: the relevant auxiliary products contain $w\odot V$ and $\gamma\odot b\odot K$ inside their dot products. The appendix states a chunk size of 64, fp32 log-decay/state and matrix accumulators, and a recurrent fp32-state decoding kernel. Its reported forward/backward checks compare the chunked kernels with a tokenwise reference; those are author implementation claims, not an independently executed verification here.[^gated-deltanet-2-2026]

## Block and hybrid placement

The token mixer projects $Q/K/V$, applies short causal convolution and SiLU, and L2-normalizes $Q$ and $K$. Independent branches produce decay, erase, and write gates; the recurrent output then receives RMS normalization, a SiLU output gate, and output projection. The recurrent-only family stacks this mixer with MLPs. The hybrid repeated cell is Gated DeltaNet-2, MLP, sliding-window attention (SWA), MLP: fixed state carries compressed long history while SWA provides bounded, exact local token interaction.[^gated-deltanet-2-2026]

## Relationships

- **Extends:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) by separating active erase and write controls.
- **Generalizes:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) and KDA through tied-gate reductions.
- **Depends on:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), whose superposed associations motivate more selective memory editing.
- **Evaluated by:** [Gated DeltaNet-2 evaluation and hybrid trade-offs](gated-deltanet-2-evaluation-and-hybrid-trade-offs.md).

## Evidence limits

The recurrence, reductions, derivation, implementation choices, and correctness checks are primary-source author statements. The derivation establishes equivalence of the stated recurrent and chunkwise forms, but not general numerical robustness, semantic interpretation of gate values, or performance on other model scales, kernels, precisions, and hardware.

[^gated-deltanet-2-2026]: Ali Hatamizadeh, Yejin Choi, and Jan Kautz, “Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention,” supplied LaTeX source, [source](../raw/2605.22791_GatedDeltaNet-2/main.tex), Sections 2–3 and Appendices A–C.
