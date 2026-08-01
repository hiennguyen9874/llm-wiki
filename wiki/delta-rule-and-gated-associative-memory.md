---
type: Concept
title: Delta-rule and gated associative memory
description: Delta-rule memory corrects selected key-value associations, while learned decay adds broader eviction and per-channel capacity control.
tags: [associative-memory, deltanet, gating, linear-attention]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:24:41Z }
sources:
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
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
---

# Delta-rule and gated associative memory

The delta rule turns a purely additive associative state into a memory that corrects what a key currently retrieves. Learned decay complements this targeted replacement with broader eviction; Kimi Delta Attention (KDA) makes that decay channel-wise, giving a fixed-capacity memory distinct write, correction, and per-feature retention controls.[^fast-weight-programmers-2021][^kimi-linear-2025]

## Delta update

For a mapped key $\phi(k_t)$, the 2021 fast-weight formulation first reads $\bar v_t=W_{t-1}\phi(k_t)$, then applies $W_t=W_{t-1}+\beta_t(v_t-\bar v_t)\otimes\phi(k_t)$, where the model produces $\beta_t\in[0,1]$. With orthogonal keys, this rewrites the addressed association while leaving unrelated ones unchanged, unlike a global decay gate. The paper also normalizes mapped keys and queries by their component sums to balance the write and removal terms; its alternative accumulating attention normalization can grow with sequence length and did not provide that balance.[^fast-weight-programmers-2021]

DeltaNet performs online gradient descent on the reconstruction loss $\tfrac12\|S^\top k_t-v_t\|^2$. With learned step size $\beta_t$, its state update is:

$$
S_t=(I-\beta_t k_tk_t^\top)S_{t-1}+\beta_tk_tv_t^\top.
$$

Equivalently, the memory reads the association currently selected by $k_t$ and writes a fraction of the error toward $v_t$. This corrects a selected association instead of adding indefinitely, but does not itself broadly remove obsolete memories.[^kimi-linear-2025]

## Gated decay and KDA

Gated DeltaNet multiplies the corrective transition by a learned scalar decay $\alpha_t$. KDA replaces that head-wise scalar with a diagonal channel-wise gate:

$$
S_t=(I-\beta_tk_tk_t^\top)\operatorname{Diag}(\alpha_t)S_{t-1}+\beta_tk_tv_t^\top.
$$

Different key channels can therefore learn different retention rates. The report also interprets the cumulative, data-dependent transitions as multiplicative positional behavior: unlike RoPE’s fixed orthogonal rotations, KDA’s transitions combine learned decay with key-conditioned correction. This is a model interpretation, not proof that KDA universally extrapolates better than RoPE.[^kimi-linear-2025]

The mechanisms have distinct roles:

- **Delta correction** selectively rewrites the association addressed by the current key.
- **Decay** frees capacity beyond that selected association.
- **Channel-wise decay** gives state features different, input-dependent retention horizons.

## Constrained DPLR transition

KDA is a constrained diagonal-plus-low-rank (DPLR) transition. Its diagonal is $\operatorname{Diag}(\alpha_t)$, while the rank-one factors share the current key rather than being independently parameterized. This preserves fine-grained decay while letting the implementation factor the decay and apply a Householder-style correction. The authors report that this constraint removes secondary chunking and matrix multiplications required by their general DPLR formulation; their kernel benchmark approaches a $2\times$ speedup at long tested lengths, but does not establish an advantage over every DPLR implementation.[^kimi-linear-2025]

## Parallel training and recurrent decoding

KDA compresses products of rank-one transitions within each chunk using a WY representation, then applies a UT transform so most work becomes matrix multiplication. Interactions inside a chunk are parallel, state crosses chunk boundaries recurrently, and autoregressive decoding uses the direct recurrent update. For chunk size $C$, head width $d_h$, and sequence length $T$, the report gives $6Td_h^2+3TCd_h+TC^2$ attention FLOPs per KDA head, versus the dominant $2T^2d_h$ term for global attention.[^kimi-linear-2025]

The earlier Parallel DeltaNet paper applies the same broad compact-WY and triangular-transform strategy to the ungated DeltaNet recurrence, avoiding token-level matrix-state materialization while retaining chunk-boundary recurrence. Its dedicated training and evaluation evidence is recorded separately.[^parallel-deltanet-2024]

## Relationships

- **Depends on:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md), whose additive-state interference motivates corrective updates.
- **Parallelized by:** [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md), which targets the ungated corrective recurrence.
- **Used by:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), which interleaves KDA with periodic global attention.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), whose primary report retains the recurrence while lower-bounding log-decay for BF16 Tensor Core tiles and adding a full-rank output gate.[^kimi-k3-2026]

## Evidence limits

The original learned-step delta update and its associative-memory comparison are documented in the 2021 primary paper; the KDA recurrence, derivation, pseudocode, and kernel measurements are documented in the Kimi Linear report, while Kimi K3 independently specifies its modified decay and output gate. The derivations support recurrent–chunkwise equivalence, while empirical expressivity and speed remain dependent on model, kernel, precision, and hardware.

[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–3 and appendices.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 4.2 and Appendix A–B.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 2–3, 6, and the chunkwise derivation and pseudocode appendices.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Section 2.1.
