---
type: Concept
title: DeepSeek-V4 hybrid architecture and pretraining
description: DeepSeek-V4 is a preview MoE family that combines compressed sparse and heavily compressed attention, manifold-constrained residual connections, Muon, and DeepSeekMoE to natively support a reported one-million-token context.
tags: [deepseek-v4, mixture-of-experts, long-context, pretraining, hybrid-attention]
status: draft
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T00:00:00Z }
sources:
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# DeepSeek-V4 hybrid architecture and pretraining

DeepSeek-V4 is DeepSeek-AI’s preview MoE model family for one-million-token contexts. The report describes a 1.6T-total/49B-active Pro model trained on 33T tokens and a 284B-total/13B-active Flash model trained on 32T tokens; both interleave compressed sparse attention (CSA) and heavily compressed attention (HCA), retain DeepSeekMoE and one-depth multi-token prediction, add manifold-constrained Hyper-Connections (mHC), and use Muon for most matrix parameters.[^deepseek-v4-2026]

## Model design

Pro has 61 layers and width 7,168; Flash has 43 layers and width 4,096. Both use MoE in every Transformer block, with hash routing in their first three MoE layers, one shared expert, six activated routed experts, and auxiliary-loss-free batch balancing plus a small sequence-wise balance loss. The report changes router affinity from sigmoid to $\sqrt{\operatorname{Softplus}(\cdot)}$ and removes V3’s routing-target-node constraint; these are V4 configuration choices, not isolated causal results.[^deepseek-v4-2026]

For attention, CSA compresses groups of four tokens then sparsely selects compressed entries, while HCA densely attends over entries compressed at a factor of 128; both add a 128-token uncompressed sliding-window branch. The authors report that at a 1M-token context, Pro requires 27% of DeepSeek-V3.2’s estimated single-token FP8-equivalent FLOPs and 10% of its KV cache; Flash requires 10% and 7%, respectively. These estimates are architecture-specific and do not establish end-to-end serving latency or quality parity.[^deepseek-v4-2026]

## Data and training

The report describes a more-than-32T-token corpus with math, code, web, multilingual, and curated long-document data. Training starts at 4K sequence length and progressively extends through 16K and 64K to 1M; sparse attention is introduced after an initial dense-attention phase. It retains a 128K vocabulary, token splitting, and fill-in-the-middle, but adopts sample-level attention masking.[^deepseek-v4-2026]

The authors report two empirical stability measures: temporarily calculate routing assignments from historical parameters after a loss spike (Anticipatory Routing), and clamp SwiGLU’s linear branch to $[-10,10]$ and gate branch above at 10. Their mechanisms are not yet theoretically explained by the report.[^deepseek-v4-2026]

## Relationships

- **Uses:** [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) for its long-context attention layers.
- **Uses:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) to expand and stabilize the residual stream.
- **Uses:** [Muon orthogonalized-momentum optimizer](muon-orthogonalized-momentum-optimizer.md) for most non-exempt parameter matrices.
- **Extends:** [DeepSeek-V3 architecture and pretraining](deepseek-v3-architecture-and-pretraining.md) with different attention, residual, routing, optimizer, and context designs.
- **Implemented by:** [DeepSeek-V4 training and serving infrastructure](deepseek-v4-training-and-serving-infrastructure.md).
- **Extended by:** [DeepSeek-V4 post-training and evaluation limits](deepseek-v4-post-training-and-evaluation-limits.md).

## Evidence limits

Architecture, corpus, stability, cost, and efficiency claims are from an author technical report. The data mixture, full implementations, ablations separating components, and independent long-context or systems measurements are not available here.[^deepseek-v4-2026]

[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” arXiv:2606.19348v1, [source](../raw/arXiv-2606.19348v1/main.tex), Sections 1–3 and 5.
