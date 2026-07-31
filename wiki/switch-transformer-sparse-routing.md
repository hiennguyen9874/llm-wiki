---
type: Concept
title: Switch Transformer sparse routing
description: Switch Transformer replaces selected dense Transformer FFNs with many experts and routes each token to one expert, separating total parameter capacity from most per-token FFN computation.
tags: [mixture-of-experts, switch-transformer, sparse-models, routing]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:15:46Z }
sources:
  - id: moe-overview-2026
    resource: ../raw/MixtureofExperts.md
    title: "Switch Transformer and Mixture of Experts in LLMs (Vietnamese overview)"
---

# Switch Transformer sparse routing

Switch Transformer replaces selected dense position-wise FFNs with a bank of independently parameterized FFN experts. A router assigns each token to its highest-probability expert (top-1 routing), so expert parameter capacity can grow without proportionally increasing the main FFN computation for that token.[^moe-overview-2026]

## Routing mechanism

For token state $x$, the router projects to one logit per expert, applies softmax, selects $i^*=\arg\max_i p_i(x)$, and scales that expert’s output by its selected probability: $y=p_{i^*}(x)E_{i^*}(x)$. The discrete assignment is not differentiated through directly, but the selected gate probability is differentiable with respect to router weights.[^moe-overview-2026]

An expert remains an ordinary FFN with its own weights. Routing is per token, so neighboring tokens can select different experts; the overview also reports that Switch layers may be interleaved with dense FFN layers rather than replacing every FFN.[^moe-overview-2026]

## Capacity versus active computation

With $N$ experts of $P$ parameters each, expert capacity is approximately $NP$, while top-1 expert parameters active for a token are approximately $P$. This distinction makes total parameters, active parameters, and FLOPs per token different quantities. It does **not** make the inactive weights or MoE overhead free: routing, dispatch, padding, inter-device communication, and weight storage remain material costs.[^moe-overview-2026]

Top-1 routing avoids the duplicated expert computation and token dispatch of top-$k$ routing for $k>1$. The overview attributes reported quality–training-time gains to this simplification, but those gains are experiment- and hardware-specific rather than a general forward-pass speedup.[^moe-overview-2026]

## Relationships

- **Replaces a component of:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), substituting a routed expert bank for selected position-wise FFNs.
- **Contrasts with:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), whose supplied overview reports top-16 routed experts rather than Switch’s top-1 choice.

## Evidence limits

This page compiles a secondary Vietnamese overview that cites the Switch Transformer and sparsely gated MoE papers. Those primary papers were not bundled in the repository, so mathematical details and reported results here remain attributed to the overview.[^moe-overview-2026]

[^moe-overview-2026]: “Switch Transformer và Mixture of Experts trong LLM,” [raw source](../raw/MixtureofExperts.md), citing Fedus, Zoph, and Shazeer, “Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity” (2021/2022), and Shazeer et al., “Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer” (2017).
