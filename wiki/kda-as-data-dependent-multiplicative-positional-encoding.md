---
type: Synthesis
title: KDA as data-dependent multiplicative positional encoding
description: KDA can be interpreted as transporting writes through learned, data-dependent transition products, supplying order and recency signals that let Kimi K3 use NoPE in its text-backbone MLA layers.
tags: [kda, positional-encoding, rope, kimi-k3, linear-attention]
status: stable
created: 2026-09-03
generated: { by: llm-wiki-agent/1, at: 2026-09-03T08:19:15Z }
sources:
  - id: why-k3-no-rope-note
    resource: ../raw/why-K3-doesnt-need-RoPE.md
    title: "Why Kimi K3 doesn't need RoPE (user-supplied note)"
  - id: why-k3-no-rope-diagram
    resource: ../raw/why-K3-doesnt-need-RoPE.jpeg
    title: "Why Kimi K3 doesn't need RoPE (user-supplied diagram)"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# KDA as data-dependent multiplicative positional encoding

Kimi Delta Attention (KDA) can be read as a data-dependent multiplicative positional mechanism: a write made at position $i$ is transformed by the ordered product of later recurrent transitions before a query at $t$ reads it. Unlike RoPE, this product is generally neither a fixed function of $t-i$ nor orthogonal. In Kimi K3, this position-sensitive recurrent mixing lets the periodic text-backbone MLA layers use NoPE; it does not make KDA and RoPE identical operators.[^kimi-linear-2025][^kimi-k3-2026]

## Transition-product view

For a fixed per-step rotation $R$, a RoPE score can be written as

$$
q_t^\top R^{t-i}k_i
= q_t^\top\left(\prod_{j=i+1}^{t}R\right)k_i.
$$

This is the transition form of RoPE's familiar cancellation of two absolute rotations, $R_t^\top R_i=R_{i-t}$ up to sign convention. The resulting transform depends only on relative offset, and orthogonality preserves query/key norms.[^why-k3-no-rope-diagram]

KDA instead uses a learned transition such as

$$
H_j=(I-\beta_j k_jk_j^\top)\operatorname{Diag}(\alpha_j),
$$

under the state-orientation convention used here. Expanding the recurrent state makes a write from position $i$ reach a later query through an ordered product $\prod_{j=i+1}^{t}H_j$. The path therefore carries order and recency information through the intervening keys, write strengths, and channel-wise decays rather than through a fixed frequency schedule.[^kimi-linear-2025][^why-k3-no-rope-note][^why-k3-no-rope-diagram]

This gives a third interpretation alongside the usual views of delta memory as key-addressed read/write and as online regression against retrieval error. It is an interpretation of the induced sequence-mixing weights, not a claim that KDA computes softmax attention internally.[^why-k3-no-rope-note][^kimi-linear-2025]

## Why orthogonality is not required

RoPE applies independent absolute transforms to queries and keys, so orthogonality is what lets their dot product collapse cleanly to one relative transform. KDA directly accumulates the interval transition in its recurrent state; it does not need to factor that path into two independent absolute-position transforms.[^why-k3-no-rope-note][^why-k3-no-rope-diagram]

The rank-one factor is therefore best called **Householder-style** or a **generalized Householder transform**. For unit $k$, $I-2kk^\top$ is an orthogonal Householder reflection, but $I-\beta kk^\top$ is generally non-orthogonal for learned $\beta$, and channel-wise decay makes the full KDA transition non-orthogonal except in special cases. Thus the informal statement that “Householder matrices satisfy RoPE's requirements” applies only to the orthogonal reflection case, not to KDA's general learned transition.[^why-k3-no-rope-diagram][^kimi-linear-2025]

## Why Kimi K3 can use NoPE MLA

Kimi K3 places three KDA layers before each periodic global MLA layer and applies no explicit positional encoding to MLA queries or keys. The primary report assigns position-sensitive and recency-aware mixing to the intervening KDA layers and unrestricted global content interaction to MLA. It also argues that this avoids RoPE-frequency retuning during context extension.[^kimi-k3-2026]

The claim is architectural: **the hybrid text backbone delegates positional handling to KDA**. It does not establish that:

- any standalone NoPE attention layer automatically recovers position;
- KDA is a drop-in replacement for RoPE in arbitrary architectures;
- non-orthogonal transitions universally extrapolate better than RoPE; or
- K3's recurrent state preserves every earlier token exactly.

K3 still uses periodic token-addressable MLA whose cache grows with context, while KDA remains a finite-dimensional associative state. The supplied note and diagram are useful secondary explanations; the Kimi Linear and Kimi K3 reports are the stronger evidence for the mechanism and model design.[^why-k3-no-rope-note][^why-k3-no-rope-diagram][^kimi-linear-2025][^kimi-k3-2026]

## Relationships

- **Interprets:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through ordered products of learned recurrent transitions.
- **Contrasts with:** [Rotary position embedding (RoPE)](rotary-position-embedding.md), whose fixed orthogonal rotations reduce to a translation-invariant relative offset.
- **Used by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), which combines position-sensitive KDA with periodic NoPE MLA.
- **Inherited from:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), where the KDA–NoPE division of labor was introduced.

## Evidence limits

The user-supplied note and diagram provide no author, publication date, or external citations and are treated as informal secondary explanation. Their central transition-product framing is corroborated by the Kimi Linear report, and K3's NoPE assignment is corroborated by the Kimi K3 report. The sources support a mechanistic interpretation and an architecture choice, not an isolated causal ablation proving that this positional treatment alone explains K3's long-context quality.

[^why-k3-no-rope-note]: “Why Kimi K3 doesn't need RoPE,” user-supplied note, [raw source](../raw/why-K3-doesnt-need-RoPE.md). Informal secondary explanation; author and date are not supplied.

[^why-k3-no-rope-diagram]: “Why Kimi K3 doesn't need RoPE,” user-supplied diagram, [raw image](../raw/why-K3-doesnt-need-RoPE.jpeg). Informal secondary explanation; author and date are not supplied.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 2 and 6, especially the gated-delta transition-product interpretation and NoPE discussion.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.1 and 3.1.
