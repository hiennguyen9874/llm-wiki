---
type: Concept
title: Linear attention as fixed-state memory
description: Linear attention trades token-addressable KV storage for a fixed-size associative state, reducing decode-state growth while introducing capacity interference.
tags: [attention, associative-memory, linear-attention, inference]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:14:44Z }
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Linear attention as fixed-state memory

Linear attention replaces a sequence-growing, token-addressable KV cache with a fixed-size associative state. This bounds recurrent decode state, but several key-value associations share the same matrix and can interfere once its effective capacity is exceeded.[^fast-weight-programmers-2021][^gpt2-kimi3-2026][^kimi-linear-2025]

## Mechanism

Softmax attention forms query-key interactions before applying its nonlinearity, so its usual formulation cannot simply reassociate the products. Linear attention instead transforms queries and keys separately with a feature map, allowing an update of the form $S_t = S_{t-1} + \phi(k_t)^T v_t$ and a read from $\phi(q_t)S_t$, with an additional normalization state when required.[^gpt2-kimi3-2026]

The resulting state has dimensions determined by head width rather than sequence length. The 2021 paper formalizes this as a fast-weight matrix updated by an outer product of value and mapped key, plus a feature accumulator for normalized attention; a query reads the matrix with its mapped feature vector. By contrast, a conventional KV cache retains keys and values for each prior token and therefore grows linearly with context length. The Kimi Linear report instantiates this with a $d_k\times d_v$ state per KDA head and switches from chunkwise prefill to recurrent generation.[^fast-weight-programmers-2021][^gpt2-kimi3-2026][^kimi-linear-2025]

## Trade-off

- **Bounded recurrent state:** decode memory does not grow with token count.
- **Loss of isolated slots:** earlier associations are superposed rather than individually retained.
- **Capacity interference:** purely additive updates eventually combine conflicting associations without an eviction policy. For interference-free exact retrieval in the paper's associative-memory analysis, mapped keys must be orthogonal, so there can be no more than $d_{\mathrm{dot}}$ such associations; this is a representational limit, not a universal measured failure threshold.[^fast-weight-programmers-2021]
- **Kernel approximation:** feature-map attention is less expressive than exact softmax attention; practical quality depends on the architecture and workload.[^gpt2-kimi3-2026]

Training, prefill, and decode complexity should be distinguished. Avoid treating every implementation of softmax attention as performing quadratic work at every decode step: KV caching and fused attention kernels change the practical cost, while the cache still grows with sequence length.[^gpt2-kimi3-2026]

## Relationships

- **Improved by:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), which adds targeted replacement and learned decay to a fixed-size state.
- **Used by:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), which combines fixed-state KDA layers with periodic global attention.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) through KDA, paired with periodic global MLA because fixed recurrent state is not token-addressable.[^kimi-k3-2026]
- **Generalized by:** [Structured State Space Duality](structured-state-space-duality.md), which replaces linear attention's all-ones causal mask with a data-dependent semiseparable mask.[^dao-gu-2024]

## Evidence limits

The fixed-state mechanism, its fast-weight formulation, and its capacity analysis are supported by primary papers; the broader memory framing also draws on the secondary explainer. Fixed state guarantees bounded state dimensions, not lossless memory, constant end-to-end latency, or quality parity with softmax attention. Kimi K3 still retains sequence-growing MLA cache, so end-to-end outcomes remain architecture-, kernel-, context-, and workload-dependent.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 1–3 and 6.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.1 and 5.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 4–6.
