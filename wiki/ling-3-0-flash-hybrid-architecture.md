---
type: Concept
title: Ling-3.0-flash hybrid architecture
description: Ling-3.0-flash is a reported 124B-total/5.1B-active hybrid-linear MoE that repeats five Kimi Delta Attention layers and one Gated MLA layer, with 512 routed experts and a stated 256K training schedule.
tags: [ling-3-0-flash, hybrid-attention, kimi-delta-attention, mixture-of-experts, multi-token-prediction]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:19:01Z }
sources:
  - id: ling3-card-2026
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash.md
    title: Ling-3.0-flash model card
  - id: ling3-architecture-2026
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash-architecture.png
    title: Ling-3.0-flash architecture diagram
---

# Ling-3.0-flash hybrid architecture

Ling-3.0-flash is a reported 124B-total, 5.1B-active hybrid-linear MoE. Its 42 sequence-mixing layers are arranged as seven repetitions of five Kimi Delta Attention (KDA) layers and one Gated Multi-head Latent Attention (MLA) layer, combining mostly fixed-state recurrent mixing with periodic token-addressable attention.[^ling3-card-2026][^ling3-architecture-2026]

## Backbone and sparse capacity

The card specifies 35 KDA and seven Gated MLA layers, 32 attention heads, hidden width 2,560, and a 157,184-token vocabulary. The first two blocks use dense FFNs; the remaining capacity uses 512 routed experts plus one shared expert, activating eight routed experts per token. This is 1/64 routed-expert activation, consistent with the card's sparse-MoE description.[^ling3-card-2026][^ling3-architecture-2026]

The diagram shows a pre-normalized residual structure around each sequence mixer and MoE. Its KDA inset labels learned decay and delta-update controls, while its Gated MLA inset routes a gated residual branch around latent attention. The supplied card and diagram do not disclose the KDA equations, latent dimensions, router algorithm, load-balancing update, or a code implementation, so they do not establish behavior beyond this architectural labeling.[^ling3-architecture-2026]

## Context, position, and prediction objective

The source lists a context-training progression from 8K to 32K to 256K and recommends a 256K YaRN serving context. It also depicts RoPE and declares next-token prediction plus multi-token prediction (MTP) as training objectives.[^ling3-card-2026][^ling3-architecture-2026]

The architecture diagram separately labels a supported content length of one million tokens. That conflicts with the card's stated 256K training schedule and 256K serving example; the supplied bundle does not explain the extension method or give a one-million-token launch recipe. This wiki therefore treats 1M as an unresolved diagram claim, not an established operational context limit.[^ling3-card-2026][^ling3-architecture-2026]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through the KDA majority path.[^ling3-card-2026]
- **Uses:** [Multi-head Latent Attention](multi-head-latent-attention.md) in every sixth sequence-mixing layer.[^ling3-card-2026]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through top-8 routed capacity and a shared expert.[^ling3-card-2026]
- **Declares:** [Sequential multi-token prediction](sequential-multi-token-prediction.md), with no supplied detail about depth, loss weight, or training implementation.[^ling3-architecture-2026]
- **Evaluated by:** [Ling-3.0-flash evaluation, serving, and evidence limits](ling-3-0-flash-evaluation-serving-and-evidence-limits.md).

## Evidence limits

This is a vendor model card and diagram, not a technical report, checkpoint configuration, or reference implementation. They specify the high-level layer counts and dimensions but provide no pre-training data, ablations, training recipe, model weights, or independently reproducible long-context evidence. The separate 1M and 256K context statements remain unresolved within the source bundle.[^ling3-card-2026][^ling3-architecture-2026]

[^ling3-card-2026]: InclusionAI, “Ling-3.0-flash,” [model card](../raw/Ling-3.0-flash/Ling-3.0-flash.md), Introduction, Model Overview, and Quickstart.

[^ling3-architecture-2026]: InclusionAI, “Ling-3.0-flash Architecture,” [included diagram](../raw/Ling-3.0-flash/Ling-3.0-flash-architecture.png).
