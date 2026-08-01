---
type: Concept
title: Auxiliary-loss-free MoE load balancing
description: Auxiliary-loss-free balancing adjusts per-expert routing biases from observed batch load, separating top-k assignment control from the affinity weights used to combine expert outputs.
tags: [mixture-of-experts, load-balancing, routing, distributed-training]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:38:26Z }
sources:
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: "DeepSeek-V3 Technical Report"
---

# Auxiliary-loss-free MoE load balancing

DeepSeek-V3’s auxiliary-loss-free balancing changes which experts enter top-$k$ routing by adding an adaptive per-expert bias to router affinity, but computes the selected experts’ output weights from the unmodified affinity. After each training step, it lowers a bias for an overloaded expert and raises one for an underloaded expert, pursuing batch-wise balance without putting the main balance pressure into the model loss.[^deepseek-v3-2024]

## Routing and bias update

For routed expert $i$ and token $t$, the V3 router obtains sigmoid affinity $s_{i,t}$. It selects the top-$k$ experts under $s_{i,t}+b_i$, but normalizes the original $s_{i,t}$ values to obtain the mixture weights. Thus the bias changes assignment eligibility rather than directly scaling an expert’s FFN contribution.[^deepseek-v3-2024]

At each step, observed expert load determines a fixed-size update: an overloaded expert’s $b_i$ decreases by $\gamma$, while an underloaded expert’s increases by $\gamma$. The V3 run uses $\gamma=0.001$ for its first 14.3T tokens and zero for its final 500B. It also retains an extremely small sequence-wise balance loss ($\alpha=0.0001$) to prevent extreme imbalance within individual sequences.[^deepseek-v3-2024]

## Scope and reported evidence

The report contrasts this batch-wise method with a sequence-wise auxiliary loss: batch-level balance permits domains within a sequence to concentrate on different experts, which the authors associate with stronger specialization patterns. In listed small and large MoE ablations, the auxiliary-loss-free variants improve most reported benchmarks over purely auxiliary-loss-based variants, but not every metric.[^deepseek-v3-2024]

Batch-wise balance does not itself guarantee safe inference utilization. V3 combines node-limited routing, large distributed micro-batches, and redundant experts at serving time; the report separately identifies domain-shift load imbalance as an inference concern.[^deepseek-v3-2024]

## Relationships

- **Specializes:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) with dynamic router biases rather than a primary auxiliary-loss signal.
- **Used by:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md).
- **Implemented by:** [DeepSeek-V3 training systems and FP8](deepseek-v3-training-systems-and-fp8.md) through node-limited routing and redundant-expert deployment.

## Evidence limits

The mechanism and ablations are author-reported. The comparison changes the balancing strategy in specified 15.7B and 228.7B models, but it does not establish the method’s performance or stability across data mixtures, expert counts, batch sizes, hardware, or production request distributions.[^deepseek-v3-2024]

[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” arXiv:2412.19437v2, [source](../raw/arXiv-2412.19437v2/main.tex), Sections 2.1, 3.2, 5.4, and Appendix B.
