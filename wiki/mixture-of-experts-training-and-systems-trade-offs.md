---
type: Concept
title: Mixture-of-Experts training and systems trade-offs
description: Practical MoE training requires bounded per-expert token capacity, load balancing, numerically stable routing, and distributed dispatch; these controls trade efficiency against padding, communication, and dropped tokens.
tags: [mixture-of-experts, sparse-models, distributed-training, load-balancing]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:19:23Z }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
---

# Mixture-of-Experts training and systems trade-offs

Sparse expert models reduce the dominant expert-FFN computation per token, but practical training and serving are constrained by expert imbalance, fixed capacity, routing stability, all-to-all communication, and the need to retain all weights. MoE efficiency therefore depends on routing and systems design, not active-parameter counts alone.[^moe-overview-2026]

## Capacity and balance

Implementations give each expert a bounded token capacity, approximately $C=(T/N)\times\text{capacity factor}$ for $T$ batch tokens and $N$ experts. Tokens assigned beyond an expert’s capacity skip its expert computation and continue through the residual path; raising the capacity factor reduces such overflows but increases padding, memory, communication, and wasted work.[^moe-overview-2026]

Without a balancing objective, a router can concentrate traffic on a small number of experts, causing overflow while leaving others undertrained. The Switch overview describes an auxiliary loss $\alpha N\sum_i f_iP_i$, combining each expert’s realized routing fraction $f_i$ with its mean router probability $P_i$, to encourage balanced use. It balances traffic but does not require experts to learn identical functions.[^moe-overview-2026]

## Distributed execution and stability

Expert parallelism shards experts across accelerators. Tokens are grouped by selected expert, exchanged with all-to-all communication for expert computation, then exchanged back to restore token order. This dispatch can become the bottleneck even when sparse FFN FLOPs are low.[^moe-overview-2026]

The overview reports three Switch-specific stability measures: compute router logits and softmax in float32 while retaining lower precision elsewhere; reduce initialization scale to roughly one tenth of the dense default; and apply stronger expert dropout during fine-tuning to limit overfitting. These are reported engineering findings, not universal hyperparameter prescriptions.[^moe-overview-2026]

## Operational limits

- All expert weights, checkpoints, and model-loading costs remain proportional to total parameters.
- Small batches relative to the expert count yield poor utilization, many empty capacity slots, and unstable balance.
- Fine-tuning data may not exercise every expert sufficiently, and router drift or expert overfitting can impair downstream transfer.
- Attention, embeddings, dense layers, KV cache, router work, padding, and networking are excluded or only partly represented by an active-expert parameter count.[^moe-overview-2026]

## Relationships

- **Operationalizes:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md) through capacity limits, balancing, precision policy, and expert parallelism.
- **Applies to:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md), which adds fine-grained top-$k$ routing and an always-on shared path; its reported results and systems behavior require primary-source verification.
- **Applies to:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), whose supplied overview describes routed latent-space experts; its system behavior requires primary-source verification.

## Evidence limits

This page compiles a secondary Vietnamese overview that cites the Switch Transformer paper. The primary paper and implementation evidence were not bundled, so the formulas, thresholds, and reported training behavior remain attributed to the overview.[^moe-overview-2026]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), citing Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022).
