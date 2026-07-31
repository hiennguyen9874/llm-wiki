---
type: Concept
title: Delta-rule and gated associative memory
description: Delta-rule memory corrects selected key-value associations, while learned decay adds broader eviction and per-channel capacity control.
tags: [associative-memory, deltanet, gating, linear-attention]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:06:35Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
---

# Delta-rule and gated associative memory

The delta rule turns a purely additive associative state into a memory that can correct what a key currently retrieves. Gating complements this targeted replacement with decay, giving a fixed-capacity memory both a write policy and an eviction mechanism.[^gpt2-kimi3-2026]

## Delta update

For a current key, the memory first reads the value already stored at that direction. It then writes only a learned fraction of the error between the desired and retrieved values:

1. Read the old association: $v_{old} = k_t S_{t-1}$.
2. Form the correction: $u_t = \beta_t(v_t-v_{old})$.
3. Update the state with the correction's outer product.

This can replace a specific association rather than adding indefinitely, but it does not by itself provide broad forgetting during a context change.[^gpt2-kimi3-2026]

## Gated decay

Gated DeltaNet adds a data-dependent scalar decay $\alpha_t$ to the previous state. Setting it near one preserves memory; setting it near zero clears old state broadly. Kimi Delta Attention generalizes this idea with per-channel decay, allowing different state dimensions to retain or forget information at different rates.[^gpt2-kimi3-2026]

These mechanisms serve different roles:

- **Delta correction** selectively rewrites the association addressed by the current key.
- **Decay** frees capacity across multiple associations.
- **Fine-grained decay** gives channels different retention horizons.

## Parallel training

A token-by-token delta recurrence is inefficient for prefill and training. The described DeltaNet formulation reparameterizes the recurrence with generalized Householder transitions and processes fixed-size chunks: interactions within a chunk use causal score matrices, while information from previous chunks is carried in the recurrent state. Chunk size therefore mediates a hardware-utilization trade-off rather than changing the underlying bounded-state goal.[^gpt2-kimi3-2026]

## Relationships

- **Depends on:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), whose additive-state interference motivates corrective updates.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), which combines Kimi Delta Attention with periodic softmax retrieval.

## Evidence limits

The update progression and Kimi-specific interpretation come from one secondary explainer. Primary-paper equations, implementation orientation conventions, and performance claims were not independently verified, so this concept remains draft.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).
