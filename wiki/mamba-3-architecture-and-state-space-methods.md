---
type: Concept
title: Mamba-3 architecture and state-space methods
description: Mamba-3 extends Mamba-2’s scalar-transition SSD with an exponential-trapezoidal recurrence, data-dependent rotary complex transitions, and an optional MIMO state update.
tags: [mamba, mamba-3, ssm, recurrence, rope, inference]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T02:15:43Z }
sources:
  - id: lahoti-et-al-2026
    resource: ../raw/2603.15569_Mamba-3/structure.tex
    title: "Mamba-3: Improved Sequence Modeling using State Space Principles"
---

# Mamba-3 architecture and state-space methods

Mamba-3 is a Mamba-2-derived fixed-state sequence mixer that changes the SSM input discretization, makes the transition complex-valued through data-dependent rotations, and optionally turns each head’s SISO update into a rank-$R$ MIMO update. Its recurrent state remains bounded by architecture dimensions rather than context length; these changes do not restore arbitrary token-addressable retrieval.[^lahoti-et-al-2026]

## Exponential-trapezoidal recurrence

For scalar real decay $A_t$, input $B_tx_t$, and data-dependent $\lambda_t\in[0,1]$, the stated recurrence is

$$
h_t=\alpha_t h_{t-1}+\beta_t B_{t-1}x_{t-1}+\gamma_tB_tx_t,
$$

where $\alpha_t=e^{\Delta_tA_t}$, $\beta_t=(1-\lambda_t)\Delta_t e^{\Delta_tA_t}$, and $\gamma_t=\lambda_t\Delta_t$. Setting $\lambda_t=1$ recovers the exponential-Euler update used by the Mamba-1/2 implementation; $\lambda_t=\tfrac12$ gives the usual endpoint-average trapezoid weighting. The paper describes a local $O(\Delta_t^3)$ state-input-integral error only when $\lambda_t=\tfrac12+O(\Delta_t)$ under smoothness and stability assumptions; its learned default does **not** enforce that condition, so this is not an accuracy guarantee for the trained model.[^lahoti-et-al-2026]

The added prior-input term is equivalently a data-dependent width-two convolution on the *state input* $B_tx_t$, followed by decay. In the SSD form, its mask factors into the usual 1-semiseparable decay mask and a two-band convolutional mask. This differs from Mamba-2’s external short causal convolution; Mamba-3 adds normalized, head-specific/channel-wise $B$ and $C$ biases and omits that external convolution in its reported pure-model block.[^lahoti-et-al-2026]

## Complex transition implemented as rotary projections

A complex diagonal transition $A_t+i\theta_t$ is equivalent in real coordinates to scalar decay times block-diagonal $2\times2$ rotations with angles $\Delta_t\theta_t$. Because these rotations commute and are orthogonal, the paper moves their cumulative inverse rotations into $B$ and $C$. The resulting implementation is a data-dependent rotary transform of those projections while the recurrent state uses a scalar transition.[^lahoti-et-al-2026]

This equivalence is conditional on the stated scalar real decay and commuting block rotations; it should not be conflated with ordinary RoPE’s fixed position-frequency schedule. The authors use this change to represent rotational state dynamics that real non-negative scalar transitions cannot express, and evaluate it separately on synthetic state-tracking tasks.[^lahoti-et-al-2026]

## MIMO variant and block design

For state $H_t\in\mathbb{R}^{N\times P}$, MIMO rank $R$ replaces vector $B,C$ and input $x$ with rank-$R$ forms, so the write/emission use matrix products rather than only outer products. The state shape is retained while decode FLOPs and arithmetic intensity grow approximately with $R$ when $R\ll N,P$. The paper uses $R=4$ and obtains the rank-expanded per-head input, gate, and output through lightweight learned scaling/projection rather than widening every projection by $R$; it reduces MLP width to parameter-match its SISO models.[^lahoti-et-al-2026]

MIMO can be expressed as $R^2$ SISO interactions for parallel training, but the authors’ chunked algorithm targets about an $R$-fold training-FLOP increase by reducing chunk length by $R$. Decode still incurs more computation, so similar latency is a hardware- and kernel-dependent result rather than an asymptotic invariant.[^lahoti-et-al-2026]

The surrounding reported block follows a Llama-style pre-norm stack with alternating Mamba-3 and SwiGLU blocks. It applies RMS normalization to $B,C$ (BCNorm/QKNorm); the authors remove Mamba-2’s post-gate normalization in pure models but report that an added norm can help hybrid long-context retrieval.[^lahoti-et-al-2026]

## Relationships

- **Extends:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) with a three-term recurrence, complex rotations, BCNorm/biases, and optional inference-oriented MIMO.
- **Uses:** [Structured State Space Duality](structured-state-space-duality.md); the exponential-trapezoidal mask extends scalar SSD with a two-band state-input factor.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md). Both bound recurrent state, but the paper derives these changes from the SSM/discretization view rather than an associative-memory objective.
- **Evaluated by:** [Mamba-3 evaluation and inference trade-offs](mamba-3-evaluation-and-inference-trade-offs.md).

## Evidence limits

The recurrence, equivalences, block description, complexity accounting, and ablations are primary-paper claims. Their mathematical equivalences establish stated recurrences, not numerical stability, broad language-model quality, or end-to-end serving speed. The architecture still compresses earlier context into fixed state; periodic attention in the paper’s hybrids supplies the token-level access that a pure recurrence lacks.

[^lahoti-et-al-2026]: Aakash Lahoti et al., “Mamba-3: Improved Sequence Modeling using State Space Principles,” supplied LaTeX source, [source](../raw/2603.15569_Mamba-3/structure.tex), Sections 2–3 and Appendices A–C.
