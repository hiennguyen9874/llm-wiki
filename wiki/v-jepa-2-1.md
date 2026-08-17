---
type: Concept
title: V-JEPA 2.1
description: A V-JEPA 2 successor recipe that adds dense visible-token prediction, intermediate-layer self-supervision, and joint image-video training for spatially detailed and temporally consistent frozen features.
tags: [video, representation-learning, self-supervised-learning, dense-prediction, multimodal-pretraining]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:40:58+07:00 }
sources:
  - id: vjepa21-readme
    resource: ../raw/vjepa2/README.md
    title: V-JEPA 2 official PyTorch repository README
  - id: vjepa21-config
    resource: ../raw/vjepa2/configs/train_2_1/vitg16/pretrain-256px-16f.yaml
    title: V-JEPA 2.1 ViT-g pretraining configuration
  - id: vjepa21-train
    resource: ../raw/vjepa2/app/vjepa_2_1/train.py
    title: V-JEPA 2.1 training implementation
  - id: vjepa21-model
    resource: ../raw/vjepa2/app/vjepa_2_1/models/vision_transformer.py
    title: V-JEPA 2.1 vision-transformer implementation
  - id: vjepa21-chart
    resource: ../raw/vjepa2/assets/bars_teaser_tikz-1.png
    title: V-JEPA 2.1 frozen-feature benchmark chart
  - id: vjepa21-changelog
    resource: ../raw/vjepa2/CHANGELOG.md
    title: V-JEPA 2 repository changelog
---

# V-JEPA 2.1

V-JEPA 2.1 extends V-JEPA 2’s masked teacher-feature prediction into a denser self-supervised recipe intended to preserve spatial detail and temporal consistency. Its repository documentation names three main changes: prediction loss on both visible and masked tokens, supervision from multiple encoder depths, and shared training across images and videos with modality-specific tokenization. Released frozen encoders span ViT-B through ViT-G (about 80M to 2B parameters), but the repository does not contain the cited paper, and its paper link remains `TODO`; architecture and benchmark claims are therefore provisional repository evidence rather than a fully auditable paper synthesis.[^vjepa21-readme]

## Dense and deep predictive loss

The student encoder receives only visible tokens. A predictor reconstructs target-encoder features for masked positions as in V-JEPA, but also emits predictions for visible context positions. The training loop applies an L1-style feature loss to masked predictions and a separately weighted context loss to visible-token predictions; the checked ViT-g configuration enables this with `predict_all: true` and image/video context-loss weights of 0.5.[^vjepa21-config][^vjepa21-train]

Deep self-supervision concatenates normalized target features from four depths rather than using only the final encoder representation. The implementation selects four approximately depth-spaced blocks—for example layers 9, 19, 29, and 39 in a 40-block encoder—and the predictor projects to the corresponding multi-level targets.[^vjepa21-model][^vjepa21-train] This supports the mechanism described by the README, but the available code does not by itself establish which component causes each reported transfer gain.

## Image-video training and scale

The implementation has separate 2D image and 3D video patch embedders, learned image/video modality embeddings, and distributed rank allocation between image and video loaders. The checked ViT-g pretraining configuration mixes Kinetics-710, Something-Something v2, and HowTo video path lists while assigning half the ranks to ImageNet-1K images; those paths and weights document the supplied recipe, not a verified accounting of the data used for every released checkpoint.[^vjepa21-config][^vjepa21-model][^vjepa21-train]

The README publishes 384-resolution checkpoints for ViT-B (80M), ViT-L (300M), ViT-g (1B), and ViT-G (2B). It also documents a later 64-frame cooldown stage. The checked public YAML files are named for 256-pixel training while the checkpoint table says 384 resolution, so exact checkpoint-to-config reproduction is not established by the repository snapshot.[^vjepa21-readme][^vjepa21-config]

## Reported transfer signals

The repository’s embedded benchmark chart reports that, relative to V-JEPA 2, V-JEPA 2.1 improves frozen-feature results on NYUv2 depth estimation (0.642 to 0.307 error), Ego4D short-term anticipation (6.02 to 7.71), DAVIS object tracking (52.5 to 69.0), ADE20K semantic segmentation (24.4 to 47.9), Something-Something v2 recognition (77.3 to 77.7), and Epic-Kitchens anticipation (39.7 to 40.8). Its listed Kinetics-400 and ImageNet-1K changes are smaller (87.3 to 87.7 and 85.1 to 85.5), and several values remain below the chart’s selected previous state of the art.[^vjepa21-chart]

These numbers are useful release signals, not directly reproducible comparisons here: the snapshot lacks the 2.1 paper and detailed evaluation protocols, and the README chart does not fully specify heads, input views, or checkpoint variants. PCA visualizations in the README qualitatively show more object-aligned dense features, but they are illustrations rather than quantitative proof.[^vjepa21-readme]

## Contradictions and coverage limits

- The README dates the V-JEPA 2.1 release to 2026-03-16, while `CHANGELOG.md` labels version 0.0.2 as 2025-03-16—even though it places the initial 0.0.1 release later, on 2025-06-05. The chronology makes the changelog date internally inconsistent, but this page does not silently correct immutable evidence.[^vjepa21-readme][^vjepa21-changelog]
- The repository was inspected through its README, relevant diagrams, 2.1 training configurations, and core encoder/predictor/training code. The absent paper and uninspected external checkpoints limit coverage of data provenance, ablations, evaluation protocols, and exact released-weight reproducibility.[^vjepa21-readme]

## Relationships

- **Extends:** [V-JEPA 2](v-jepa-2.md) with dense context-token prediction, intermediate-layer targets, image-video tokenizers, and scaling to a listed 2B encoder; it does not replace V-JEPA 2-AC’s action-conditioned robotics system.[^vjepa21-readme]
- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through masked and visible EMA-teacher feature prediction across image and video inputs.[^vjepa21-readme][^vjepa21-train]
- **Compared in:** [Video backbones and encoders comparison](video-backbones-and-encoders-comparison.md) as a frozen encoder whose strongest new repository evidence is for dense transfer rather than long-context memory.

[^vjepa21-readme]: [V-JEPA 2 official PyTorch repository README](../raw/vjepa2/README.md)
[^vjepa21-config]: [V-JEPA 2.1 ViT-g pretraining configuration](../raw/vjepa2/configs/train_2_1/vitg16/pretrain-256px-16f.yaml)
[^vjepa21-train]: [V-JEPA 2.1 training implementation](../raw/vjepa2/app/vjepa_2_1/train.py)
[^vjepa21-model]: [V-JEPA 2.1 vision-transformer implementation](../raw/vjepa2/app/vjepa_2_1/models/vision_transformer.py)
[^vjepa21-chart]: [V-JEPA 2.1 frozen-feature benchmark chart](../raw/vjepa2/assets/bars_teaser_tikz-1.png)
[^vjepa21-changelog]: [V-JEPA 2 repository changelog](../raw/vjepa2/CHANGELOG.md)
