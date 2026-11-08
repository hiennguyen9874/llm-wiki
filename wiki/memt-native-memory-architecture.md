---
type: Concept
title: MemT-1.0 native memory architecture
description: Dynamic local state, trained hyper memory, stable updates, dense Mixture-of-Storage routing, and backbone-specific geometry in MemT-1.0.
tags: [agent-memory, native-memory, llm]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: '2026-11-08T02:52:52Z' }
sources:
  - id: memt-paper
    resource: ../raw/arXiv-2610.26825v2-MemT-1.0/paper.tex
    scope: ../raw/arXiv-2610.26825v2-MemT-1.0/
    kind: paper
    revision: arXiv-2610.26825v2
    title: 'MemT-1.0: Towards Memory-Native Evolution'
---

MemT-1.0 adds learned memory machinery to selected Transformer layers: a persistent, trajectory-specific local state carries information across steps, while trained hyper-memory parameters control writing and reading. This differs from retaining a growing collection of textual records; fixed storage comes with finite capacity and imperfect recall. **Reported**, not independently implemented or verified.[^memt-paper]

## State and update

- Each memory layer has a multi-channel matrix `M` of shape `Hkv × dk × dv`, initialized to zero for each independent trajectory. During online interaction the backbone and hyper-memory parameters are fixed, while the local matrices evolve.[^memt-paper]
- Queries read the incoming step snapshot via normalized Q and `Q M / sqrt(dk)`; RMS normalization and a gated output are added to the original attention branch. On completion of a turn, the stable GDN-2 writer processes token-level key/value updates with erase, write and forget gates; the resulting state becomes available in the next step.[^memt-paper]
- Mixture-of-Storage (MoS) extends the state with independent memory experts. Separate dense read and write routers use shared learned expert addresses; every expert participates rather than sparse top-k routing. The evaluated Nano and Flash configurations each use **one expert per memory layer**; multi-expert capacity experiments are separate.[^memt-paper]

## Model geometry and resource boundaries

| Configuration | Nano | Flash |
| --- | --- | --- |
| Backbone | Qwen3.6-35B-A3B | Prepared DeepSeek-V4-Flash |
| Memory layers | 10 | 20 |
| State elements per trajectory | 10,485,760 | 335,544,320 |
| FP32 persistent state | 40 MiB | 1,280 MiB |
| Trainable memory parameters | 450,931,360 | 3,608,608,000 |

These are reported logical persistent states, excluding shared weights and active-step KV cache. Storage is constant in history length for a fixed configuration, not constant in the number of separate trajectories.[^memt-paper]

## Contradictions

The architecture section's MoS equations route erase and write but explicitly leave log-decay unchanged; the infrastructure section instead says storage probabilities modulate erase, write **and log-decay**. These statements cannot both describe the same update as written. Implementation was not available for adjudication.[^memt-paper]

## Relationships

- **Depends on** [MemT training and scaling](memt-training-and-scaling.md) for learned read/write capabilities.
- **Related:** [MemT evaluation and efficiency](memt-evaluation-and-efficiency.md) quantifies the finite-state trade-off; [MemT source map](memt-source-map.md) records outstanding inspection.

[^memt-paper]: `sections/model_architecture.tex` §§ Overview, Native Memory Block and Scaling Native Memory Capacity; `sections/infra.tex` §§ Efficient Operators and Stateful Inference; `appendix/adaptation_backbone.tex` Table backbone-memory-geometry; `sections/discussion.tex`.
