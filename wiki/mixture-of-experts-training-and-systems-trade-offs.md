---
type: Concept
title: Mixture-of-Experts training and systems trade-offs
description: Practical MoE training requires bounded per-expert token capacity, load balancing, numerically stable routing, and distributed dispatch; these controls trade efficiency against padding, communication, and dropped tokens.
tags: [mixture-of-experts, sparse-models, distributed-training, load-balancing]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
  - id: muon-overview-2026
    resource: ../raw/MuonOptimizer.md
    title: Muon Optimizer overview (Vietnamese summary)
  - id: deepseekmoe-2024
    resource: ../raw/arXiv-2401.06066v1/main.tex
    title: "DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# Mixture-of-Experts training and systems trade-offs

Sparse expert models reduce the dominant expert-FFN computation per token, but practical training and serving are constrained by expert imbalance, fixed capacity, routing stability, all-to-all communication, and the need to retain all weights. MoE efficiency therefore depends on routing and systems design, not active-parameter counts alone.[^moe-overview-2026]

## Capacity and balance

Implementations give each expert a bounded token capacity, approximately $C=(T/N)\times\text{capacity factor}$ for $T$ batch tokens and $N$ experts. Tokens assigned beyond an expert’s capacity skip its expert computation and continue through the residual path; raising the capacity factor reduces such overflows but increases padding, memory, communication, and wasted work.[^moe-overview-2026]

Without a balancing objective, a router can concentrate traffic on a small number of experts, causing overflow while leaving others undertrained. The Switch overview describes an auxiliary loss $\alpha N\sum_i f_iP_i$, combining each expert’s realized routing fraction $f_i$ with its mean router probability $P_i$, to encourage balanced use. It balances traffic but does not require experts to learn identical functions.[^moe-overview-2026]

## Distributed execution and stability

Expert parallelism shards experts across accelerators. Tokens are grouped by selected expert, exchanged with all-to-all communication for expert computation, then exchanged back to restore token order. This dispatch can become the bottleneck even when sparse FFN FLOPs are low.[^moe-overview-2026]

The overview reports three Switch-specific stability measures: compute router logits and softmax in float32 while retaining lower precision elsewhere; reduce initialization scale to roughly one tenth of the dense default; and apply stronger expert dropout during fine-tuning to limit overfitting. These are reported engineering findings, not universal hyperparameter prescriptions.[^moe-overview-2026]

## Two-level balance in DeepSeekMoE

DeepSeekMoE supplies primary evidence for distinguishing collapse prevention from device utilization. Its expert-level auxiliary loss combines each routed expert’s realized selection fraction and mean routing probability. Its device-level loss aggregates those terms over the experts assigned to a device, so it balances device computation without demanding uniform traffic for every expert. In its 2B and 16B configurations, all experts in a layer occupy one device, so the authors use only a small expert-level factor and no token dropping; the preliminary 145B run distributes routed experts over four devices and applies both losses.[^deepseekmoe-2024]

This does not establish that the formulation is generally preferable: the no-drop setup and layer-local placement change the capacity and communication conditions relative to broadly sharded MoE deployments.[^deepseekmoe-2024]

## Device-limited routing and token dropping

DeepSeek-V2 adds a device fan-out limit before top-$k$ expert selection: each token first chooses at most $M$ devices with high-affinity experts, then selects routed experts only within that subset. It applies expert-, device-, and receiving-communication balance losses, and at training time drops the lowest-affinity assignments on over-capacity devices while retaining all assignments for approximately 10% of sequences. This bounds communication and device work in that setup, but dropped assignments and the chosen $M$, balance factors, placement, and capacity rule remain quality and utilization choices.[^deepseek-v2-2024]

## Auxiliary-loss-free batch balance

DeepSeek-V3 supplies primary evidence for a different balance control: adaptive per-expert routing biases. Its router selects top-$k$ experts using affinity plus bias but retains unmodified affinity for the selected experts’ output weights; after each step, the bias falls for overloaded experts and rises for underloaded ones. A small sequence-wise auxiliary loss remains, while the primary balance target is the aggregate batch. The authors report stronger specialization patterns and mostly improved small- and large-scale ablation results relative to their purely auxiliary-loss-based variants, but not universal metric gains.[^deepseek-v3-2024]

## Extreme sparsity and rank-level balance

Kimi K3 provides a primary-source case with 896 routed experts and top-16 selection. Its Stable LatentMoE reduces routed width, inserts normalization before returning to model width, bounds both activation branches, and updates routing biases from target-load quantiles. Its MoonEP runtime separately replicates experts dynamically so each expert-parallel rank receives equal aggregate token work and static computation shapes. Router balance and rank balance are complementary: neither alone removes weight memory, dispatch traffic, or within-rank expert skew.[^kimi-k3-2026]

## Operational limits

- All expert weights, checkpoints, and model-loading costs remain proportional to total parameters.
- Small batches relative to the expert count yield poor utilization, many empty capacity slots, and unstable balance.
- Fine-tuning data may not exercise every expert sufficiently, and router drift or expert overfitting can impair downstream transfer.
- Attention, embeddings, dense layers, KV cache, router work, padding, and networking are excluded or only partly represented by an active-expert parameter count.[^moe-overview-2026]
- The Muon overview reports Moonlight, a 2.24B-active/15.29B-total-parameter MoE trained with Muon; this optimizer result does not remove the routing, dispatch, or total-weight-memory constraints above.[^muon-overview-2026]

## Relationships

- **Operationalizes:** [Switch Transformer sparse routing](switch-transformer-sparse-routing.md) through capacity limits, balancing, precision policy, and expert parallelism.
- **Applies to:** [DeepSeekMoE expert specialization](deepseekmoe-expert-specialization.md), which adds fine-grained top-$k$ routing and an always-on shared path; its paper supplies primary evidence for its balance objectives.
- **Operationalized by:** [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md) through device-limited routing, three balance objectives, and training-time token dropping.
- **Specialized by:** [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md), used by [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md) for batch-wise router-bias control.[^deepseek-v3-2024]
- **Specialized by:** [Stable LatentMoE and Quantile Balancing](stable-latentmoe-and-quantile-balancing.md), with primary evidence for compact experts and quantile routing.
- **Operationalized by:** [Kimi K3 lifecycle infrastructure](kimi-k3-lifecycle-infrastructure.md), including dynamic redundant experts and static rank-level shapes.
- **Related optimizer evidence:** [Muon LLM training scaling and operational trade-offs](muon-llm-training-scaling-and-operational-trade-offs.md) describes the supplied Moonlight result and the distributed cost of full-matrix orthogonalization.

## Evidence limits

This page compiles a secondary Vietnamese overview that cites the Switch Transformer paper. The primary paper and implementation evidence were not bundled, so the formulas, thresholds, and reported training behavior remain attributed to the overview.[^moe-overview-2026]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), citing Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022).

[^muon-overview-2026]: “Muon Optimizer overview (Vietnamese summary),” [raw source](../raw/MuonOptimizer.md), Section 11; it cites “Muon is Scalable for LLM Training” (arXiv:2502.16982).

[^deepseekmoe-2024]: Dai et al., “DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models” (2024), [source](../raw/arXiv-2401.06066v1/main.tex), Section 3.3 and Sections 4–6.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.3 and 5.2.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.2 and 3.1.

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 2.1 and 5.4.
