---
type: Concept
title: Ling-3.0-tiny hybrid architecture
description: Ling-3.0-tiny is a reported 7.9B-total hybrid-linear MoE with a 3:1 KDA–Gated-MLA stack, 128 routed experts plus one shared expert, and 1.3B textual-card active parameters per token.
tags: [ling-3-0-tiny, hybrid-attention, kimi-delta-attention, mixture-of-experts, multi-token-prediction]
status: stable
created: 2026-08-25
generated: { by: llm-wiki-agent/1, at: 2026-08-25T16:21:40Z }
sources:
  - id: ling3-tiny-card-2026
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny.md
    title: Ling-3.0-tiny model card
  - id: ling3-tiny-architecture-2026
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny-architecture.png
    title: Ling-3.0-tiny architecture diagram
---

# Ling-3.0-tiny hybrid architecture

Ling-3.0-tiny is a reported 7.9B-total hybrid-linear MoE that repeats three Kimi Delta Attention (KDA) layers and one Gated Multi-head Latent Attention (MLA) layer. The model card reports 1.3B activated parameters per token; the included diagram rounds that figure to 1.4B.[^ling3-tiny-card-2026][^ling3-tiny-architecture-2026]

## Backbone and sparse capacity

The diagram depicts six 3:1 groups, corresponding to 18 KDA and six Gated MLA layers, with pre-normalized residual paths around both the sequence mixer and FFN. It labels a 1,536-dimensional embedding, a roughly 157K-token vocabulary, and RoPE. The first block uses a dense FFN of hidden size 4,608; later FFNs are MoE blocks.[^ling3-tiny-architecture-2026]

The card says each MoE block contains 128 routed experts and one shared expert, activating eight routed experts plus the shared expert for each token. It does not disclose router scoring, expert dimensions, capacity controls, load-balancing implementation, latent-attention dimensions, or KDA equations. The diagram labels auxiliary-loss-free load balancing (ALF-LB), but this alone does not establish a specific routing-bias algorithm or its behavior.[^ling3-tiny-card-2026][^ling3-tiny-architecture-2026]

## Context and prediction objective

The diagram advertises one-million-token supported content length, linear-time KDA mixing, and next-token plus multi-token-prediction (MTP) objectives. The supplied SGLang recipe instead configures 256K YaRN context; its Ollama example sets an 8K default context. The bundle provides neither an extension method nor a one-million-token launch or evaluation recipe, so the figure's context claim is not independently operationalized here.[^ling3-tiny-card-2026][^ling3-tiny-architecture-2026]

## Relationships

- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) through the KDA majority path.[^ling3-tiny-card-2026]
- **Uses:** [Multi-head Latent Attention](multi-head-latent-attention.md) in every fourth sequence-mixing layer.[^ling3-tiny-card-2026]
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) through top-8 routed capacity and a shared expert.[^ling3-tiny-card-2026]
- **Declares:** [Sequential multi-token prediction](sequential-multi-token-prediction.md), but the source does not specify MTP depth, loss weight, or implementation.[^ling3-tiny-architecture-2026]
- **Evaluated by:** [Ling-3.0-tiny evaluation, serving, and evidence limits](ling-3-0-tiny-evaluation-serving-and-evidence-limits.md).

## Evidence limits

This vendor model card and figure disclose high-level topology and selected dimensions, not weights, training data, a checkpoint configuration, implementation code, or ablations. Architectural labels and the 1M context claim should therefore not be read as independently reproduced capability; the 1.3B versus 1.4B active-parameter discrepancy is retained as a source-level rounding or reporting difference.[^ling3-tiny-card-2026][^ling3-tiny-architecture-2026]

[^ling3-tiny-card-2026]: InclusionAI, “Ling-3.0-tiny,” [model card](../raw/Ling-3.0-tiny/Ling-3.0-tiny.md), Introduction, Model Overview, and Quickstart.

[^ling3-tiny-architecture-2026]: InclusionAI, “Ling-3.0-tiny Architecture,” [included diagram](../raw/Ling-3.0-tiny/Ling-3.0-tiny-architecture.png).