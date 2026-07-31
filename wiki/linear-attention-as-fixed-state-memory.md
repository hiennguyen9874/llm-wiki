---
type: Concept
title: Linear attention as fixed-state memory
description: Linear attention trades token-addressable KV storage for a fixed-size associative state, reducing decode-state growth while introducing capacity interference.
tags: [attention, associative-memory, linear-attention, inference]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:06:35Z }
sources:
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
---

# Linear attention as fixed-state memory

Linear attention replaces a sequence-growing, token-addressable KV cache with a fixed-size associative state. This bounds recurrent decode state, but several key-value associations share the same matrix and can interfere once its effective capacity is exceeded.[^gpt2-kimi3-2026]

## Mechanism

Softmax attention forms query-key interactions before applying its nonlinearity, so its usual formulation cannot simply reassociate the products. Linear attention instead transforms queries and keys separately with a feature map, allowing an update of the form $S_t = S_{t-1} + \phi(k_t)^T v_t$ and a read from $\phi(q_t)S_t$, with an additional normalization state when required.[^gpt2-kimi3-2026]

The resulting state has dimensions determined by head width rather than sequence length. By contrast, a conventional KV cache retains keys and values for each prior token and therefore grows linearly with context length.[^gpt2-kimi3-2026]

## Trade-off

- **Bounded recurrent state:** decode memory does not grow with token count.
- **Loss of isolated slots:** earlier associations are superposed rather than individually retained.
- **Capacity interference:** purely additive updates eventually combine conflicting associations without an eviction policy.
- **Kernel approximation:** feature-map attention is less expressive than exact softmax attention; practical quality depends on the architecture and workload.[^gpt2-kimi3-2026]

Training, prefill, and decode complexity should be distinguished. Avoid treating every implementation of softmax attention as performing quadratic work at every decode step: KV caching and fused attention kernels change the practical cost, while the cache still grows with sequence length.[^gpt2-kimi3-2026]

## Relationships

- **Improved by:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), which adds targeted replacement and learned decay to a fixed-size state.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) through Kimi Delta Attention.

## Evidence limits

This concept is compiled from one secondary explainer rather than the cited primary papers or implementation. The mechanism is useful as a conceptual model, but equations, complexity details, and empirical comparisons remain unverified here.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).
