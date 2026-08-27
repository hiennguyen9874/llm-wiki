---
type: Concept
title: Qwen Gated Residual
description: Qwen Gated Residual carries four widened residual streams while using data-dependent element-wise read gates and per-stream scalar write gates around each attention and MoE branch.
tags: [residual-connections, qwen, hyper-connections, training-stability]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-27T03:11:23Z }
sources:
  - id: qwen38-next-card
    resource: ../raw/Qwen3.8-Flash-Next/README.md
    title: Qwen3.8-Flash-Next model card
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next checkpoint configuration
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: Qwen4-Exp Transformers modeling implementation
  - id: qwen38-next-figure
    resource: ../raw/Qwen3.8-Flash-Next/architecture.png
    title: Qwen3.8-Flash-Next architecture diagram
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
---

# Qwen Gated Residual

Qwen Gated Residual expands the language model's residual state into four width-2,560 streams. Before each token-mixer or MoE branch, a normalized, low-rank, data-dependent read gate reduces those streams to one ordinary-width branch input; after the branch, four learned scalar write gates inject its output back into the widened state. The checkpoint uses rank 320 for the read-gate bottleneck.[^qwen38-next-card][^qwen38-next-config][^qwen38-next-modeling]

## Read and write path

For widened state $X\in\mathbb{R}^{4d}$, the implementation applies grouped RMS normalization, maps $4d\rightarrow320\rightarrow4d$ with SiLU then sigmoid, multiplies the resulting element-wise gates by the normalized streams, and averages across the four streams to obtain the width-$d$ branch input. A separate projection produces four write coefficients as $2\sigma(\cdot)$; the branch output is multiplied by each coefficient and added to the unchanged widened state. Attention and MoE each have their own Gated Residual module, and a final read-only mixer reduces the four streams before the prediction head.[^qwen38-next-modeling][^qwen38-next-figure]

This design gives the read path feature-level control and the write path branch-level control while preserving a direct carried state.[^qwen38-next-modeling]

## Ablations, path analysis, and systems trade-offs

On matched 25B-A3B MoE runs, widening with static mHC-style operators raises the nine-benchmark average from 50.91 to 52.49; making read/write data-dependent raises it to 54.47 despite only a 0.002 loss reduction, and GR reaches 54.66. The report finds channel-wise read gates useful, scalar write gates sufficient, and the full branch-mixing matrix unhelpful. In a separate loss comparison, Full Attention Residual plus GatedNorm reaches 1.758 versus 1.762 for GR, so GR is not uniformly superior on loss; it avoids Attention Residual's growing depth cache.[^qwen38-next-report]

An exact decomposition on one matched 20-layer pair attributes GR's difference mainly to amplified adjacent and very long paths at the expense of mid-range paths. Across five GR checkpoints, one of four exchangeable branches becomes long-range; early GDN outputs are preserved and later softmax-attention layers are prominent readers. This is mechanistic evidence for those probed checkpoints, not proof that every trained GR model specializes identically.[^qwen38-next-report]

Reading only the two highest-gated branches looked nearly neutral in pre-training but degraded after post-training, so it was rejected. Storing all four residual branches in FP8 reportedly halves residual-state traffic versus BF16 with almost no quality loss; fused read and write kernels traverse the widened state once in each direction per block. No deployable kernel or independent measurement accompanies those claims.[^qwen38-next-report]

## Relationship to Hyper-Connections

Gated Residual is a widened hyper-connection-style residual path, but the released code does **not** implement the doubly stochastic channel-to-channel residual matrix or Sinkhorn normalization that defines [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md). Its carried residual is identity plus gated branch injection, so mHC's spectral argument should not be transferred to this mechanism without separate evidence.[^qwen38-next-modeling]

## Relationships

- **Used by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md) around every token mixer and MoE branch.
- **Contrasts with:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md), which explicitly constrains residual mixing to the Birkhoff polytope.
- **Extends:** ordinary residual accumulation in [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md).
- **Compared in:** [So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path](residual-path-architecture-comparison.md).

## Evidence limits

The architecture diagram, configuration, reference forward pass, and technical report establish the mechanism, dimensions, and author-run ablations. The report provides point estimates and selected training curves but no repeated-seed uncertainty, deployable GR kernel, or independent replication; post-training and FP8 claims therefore remain author-reported.[^qwen38-next-report][^qwen38-next-modeling]

[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Section 2.2, Tables 5–6, and Figure 7.

[^qwen38-next-card]: Qwen Team, “Qwen3.8-Flash-Next,” [model card](../raw/Qwen3.8-Flash-Next/README.md), Highlights and Model Overview.

[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [config](../raw/Qwen3.8-Flash-Next/config.json), Gated Residual fields.

[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), `Qwen4ExpTextGatedResidual`, decoder-layer, and text-model classes.

[^qwen38-next-figure]: Qwen Team, “Qwen3.8-Flash-Next Architecture,” [included diagram](../raw/Qwen3.8-Flash-Next/architecture.png).

[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), Gated Residual section.
