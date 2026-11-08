---
type: Concept
title: MemT-1.0 training and scaling
description: Backbone preparation, memory training objectives, reported scaling experiments, and training infrastructure for MemT-1.0.
tags: [agent-memory, training, native-memory]
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

MemT trains its memory parameters on a frozen backbone, using continued pre-training and subsequent memory-focused post-training. The authors report 34B tokens of memory training data and improvements with additional training and memory experts; these are research claims, not independently reproduced.[^memt-paper]

## Data and objective

The reported corpus comprises 20B continued pre-training (CPT) tokens and 14B post-training tokens. Some training data derive from anonymized internal MemOS interaction patterns. Flash's DeepSeek backbone is separately prepared through post-training before memory is attached; Nano uses Qwen as released.[^memt-paper]

In off-policy distillation, a frozen teacher receives full past text while the memory-equipped student receives the current step plus local state. Both are teacher-forced on fixed teacher-generated trajectories. The forward KL uses a renormalized top-K teacher distribution but a full-vocabulary student distribution; the paper describes cross-entropy for CPT and KL distillation for post-training. Independent trajectories reset state.[^memt-paper]

## Scaling and infrastructure

**Reported:** on one Nano post-training trajectory across two epochs, mean memory score increases from 36.65 to 46.80, with intermediate fluctuations; this varies training exposure and optimizer steps together rather than isolating data quantity. Four MoS experts outperform two at three matched checkpoints; at 5,500 steps the mean advantage is 2.69 points. The evaluated released geometries use one expert, so the scaling study is not a measurement of their deployed configuration.[^memt-paper]

A layer-wise training schedule batches independent trajectory packs but propagates state only within each trajectory. The authors report a synthetic four-expert, 32K-token single-block experiment: 4,096-token windows reduce peak allocated GPU memory from 47.83 to 9.49 GiB, while median forward-plus-backward time rises from 463.0 to 470.6 ms. This is a block microbenchmark, not end-to-end model training.[^memt-paper]

See [architecture](memt-native-memory-architecture.md) for the differing descriptions of MoS decay routing and [source map](memt-source-map.md) for pending coverage.

[^memt-paper]: `sections/training.tex` §§ Backbone Preparation, Data Construction and Training Objectives; `sections/scaling.tex` §§ Scaling Protocol, Data and Training Scaling and Memory Capacity Scaling; `sections/infra.tex` §§ Distributed Training and Efficient Operators, Table infra-window-tradeoff; `appendix/infra_experiment_details.tex` §§ Experimental Setup and Measurement Method; `appendix/adaptation_backbone.tex` Table backbone-memory-geometry.
