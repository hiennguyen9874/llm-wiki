---
type: Concept
title: Supervised pre-training at language-model scale
description: Supervised pre-training applies an SFT-style target-only loss at pretraining-scale batch sizes, contexts, and token budgets; Loopie's authors report retained general metrics and improving reasoning metrics in one deployment.
tags: [instruction-tuning, post-training, supervised-learning, training]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:38:21Z }
sources:
  - id: gao2026loopie
    resource: ../raw/arXiv-2607.16051v2/neurips_2023.tex
    title: "Loop the Loopies!"
---

# Supervised pre-training at language-model scale

Supervised pre-training (SPT) retains supervised fine-tuning's target-token-only cross-entropy loss while using pretraining-scale optimization. In the Loopie deployment, this meant 1,024-example global batches, 131K-token contexts, and 2T training tokens; the authors report that both general and reasoning metrics continued improving, but provide no comprehensive causal ablation establishing which scale, data, or optimization factor produced the result.[^gao2026loopie]

## Definition and reported setup

- For a supervised example composed of context $c$ and target $y$, SPT masks context and padding positions and applies cross-entropy only to $y$, exactly as SFT does. It differs from ordinary pretraining, which applies loss to every non-padding token; it differs from conventional SFT by optimization scale rather than loss form.[^gao2026loopie]
- The reported SPT configuration uses global batch size 1,024 and sequence length 131,072, totaling at least 128M nominal token positions per update. It trains Loopie for 2T tokens over roughly 10 epochs, with AdamW and a warmup-then-stable $10^{-5}$ learning rate.[^gao2026loopie]
- The source positions SPT between neither SFT nor pretraining objectives: it shares SFT's loss-bearing positions and pretraining's batch, context, and token-budget regime. It hypothesizes that broad gradient aggregation and long contexts mitigate repeated-SFT specialization, rather than proving that mechanism.[^gao2026loopie]

## Reported observations and limits

- In the authors' training curves, SPT loss decreased smoothly without an epoch-boundary cliff; their reported reasoning metrics, ARC-Challenge, and MMLU continued to improve over the 2T-token run. These are source-run trends, not a controlled comparison across all relevant training variables.[^gao2026loopie]
- The paper contrasts SPT with a representative conventional SFT regime (batch sizes 32--128, 8K--32K contexts, and 10B--100B tokens) and reports that SFT improved reasoning metrics but degraded its pretraining metrics, while pretraining improved the latter with approximately unchanged reasoning. This is a contextual comparison, not a general benchmark of SPT against optimally tuned alternatives.[^gao2026loopie]
- The authors explicitly state that compute limits prevented a sufficiently comprehensive SPT ablation. Thus, the evidence does not isolate SPT from the training-data mixture, base model, hyperparameters, or Loopie's architecture, nor establish that it prevents catastrophic forgetting generally.[^gao2026loopie]

## Relationships

- Used by: [Loopie layer-loop compute-matched MoE scaling](loopie-layer-loop-compute-matched-moe-scaling.md) — the reported Loopie Thinking pipeline applies SPT after high-quality annealing and before math/code reinforcement learning.

[^gao2026loopie]: Gao et al., *Loop the Loopies!*, source manuscript, §3.4, appendix, and §5 (arXiv:2607.16051v2, 2026).