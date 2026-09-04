---
type: Concept
title: Depth-recurrent transformers for compositional generalization
description: A sub-million-parameter study combines final-step-only supervision, identity-biased gated recurrence, and task-specific interfaces to test latent-depth scaling on controlled compositional tasks.
tags: [compositional-generalization, depth-recurrence, latent-reasoning, parameter-sharing, transformers]
status: stable
created: 2026-09-04
generated: { by: llm-wiki-agent/1, at: 2026-09-04T03:25:27Z }
sources:
  - id: chen2026depth
    resource: ../raw/arXiv-2603.21676v1/main.tex
    title: "Thinking Deeper, Not Longer: Depth-Recurrent Transformers for Compositional Generalization"
---

# Depth-recurrent transformers for compositional generalization

This study evaluates a shared Transformer block iterated in latent space for an externally selected number of steps, rather than generating additional chain-of-thought tokens. In controlled synthetic tasks, its final-step-only objective, identity-biased gate, and (for two tasks) LayerScale yielded stable unrolling and some OOD compositional generalization; the evidence is limited to manually designed interfaces and models below 1M parameters.[^chen2026depth]

## Architecture and training

- A task-specific encoder produces a full sequence state, then one pre-LayerNorm Transformer block is reused for $T$ recurrence steps; a task-specific head reads the final state. Learned depth embeddings distinguish iterations. $T$ is an externally specified inference-compute budget, so it raises compute depth without adding output tokens or parameters.[^chen2026depth]
- Training applies cross-entropy only at the final recurrence step ("silent thinking") and samples $T$ uniformly from a task-specific range. The source argues this avoids rewarding early heuristic answers; it does not provide a general theoretical result.[^chen2026depth]
- A GRU-like per-channel gate mixes the candidate and prior states. Its bias is initialized to $-2$, so the initial gate retains about 88% of the prior state. LayerScale, initialized to $10^{-4}$ after attention and FFN sublayers, is used for the Boolean and relational-text tasks; it is omitted for graph reachability.[^chen2026depth]
- The interfaces deliberately vary structural priors: adjacency-masked attention for graph reachability, RoPE with unconstrained bidirectional attention for nested Boolean expressions, and shuffled relational sentences with standard sequence attention for family-relation composition.[^chen2026depth]

## Reported compositional-generalization evidence

- For adjacency-masked graph reachability, trained on 1--5 hops and 5--8 steps, the model reached 100% through 8-hop OOD queries when given enough recurrence steps, but was near chance at 10 and 12 hops. The heatmap shows a sharp one-hop-per-step frontier, consistent with the hard mask's message-passing constraint.[^chen2026depth]
- For nested Boolean expressions, trained to nesting depth 8 and 4--16 steps, it retained at least 90% accuracy through OOD depth 14. The reported heatmap stayed around 90% or higher at 20--24 recurrence steps, rather than degrading with those extra tested steps.[^chen2026depth]
- For shuffled relational text, trained on chain depths 2--5 and 1--12 steps, additional steps improved depth-5 accuracy from 63.8% at one step to 81.7% at 12; OOD depths 6 and 7 reached 69% and 67%, respectively, at 12--20 steps. OOD depths 8 and 9 remained near chance despite modest gains, so this is limited extrapolation rather than reliable long-chain routing.[^chen2026depth]

## Intermediate-supervision ablation

On graph reachability, the paper reports that averaging loss across all recurrence steps gave about 73% accuracy for 12-hop paths after one step but about 50% accuracy with sufficient steps. Final-step-only training gave about 50% at one step and perfect accuracy through 8 hops with sufficient steps.[^chen2026depth]

Because the adjacency mask restricts one recurrence step to one graph hop, the authors interpret the one-step result as a graph-distribution heuristic rather than path propagation, and attribute the later collapse to capacity spent on that shortcut. This is a single-task ablation; it supports caution about per-step answer supervision under this data generator and architecture, not the claim that intermediate supervision is generally harmful.[^chen2026depth]

## Trust boundary and limitations

The source's "computational frontier" and claims of autonomous latent routing are empirical descriptions of three constructed tasks, not demonstrations on pretrained LLMs or open-ended language reasoning. The authors explicitly note the sub-million-parameter scale, manually designed interfaces, and absence of formal generalization guarantees.[^chen2026depth]

## Relationships

- Related to: [Virtual logical depth scaling](virtual-logical-depth-scaling.md) — both investigate tied layer reuse as a way to raise computation depth at fixed parameter count, but this source focuses on controlled OOD tasks and stability mechanisms.
- Related to: [Recurrence and parametric knowledge manipulation](recurrence-and-parametric-knowledge-manipulation.md) — both report synthetic compositional-task benefits from recurrence, with distinct architectures and evaluation designs.
- Qualifies: [Probing depth-recurrent latent chain-of-thought](probing-depth-recurrent-latent-chain-of-thought.md) — this source measures final-task success rather than establishing that its recurrent states constitute interpretable or faithful latent chain-of-thought.

[^chen2026depth]: Chen, *Thinking Deeper, Not Longer: Depth-Recurrent Transformers for Compositional Generalization*, source manuscript, abstract, §§2--5, and appendices (arXiv:2603.21676v1, 2026).