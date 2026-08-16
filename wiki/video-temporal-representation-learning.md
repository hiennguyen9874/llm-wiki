---
type: Concept
title: Video temporal representation learning
description: Pretraining video features to encode appearance, motion, order, dynamics, and longer-range semantics for downstream tasks.
tags: [video, representation-learning, self-supervised-learning, foundation-models]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:33:34+07:00 }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: i3d-paper
    resource: ../raw/I3D/full_kinetics_update_v0.tex
    title: Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset
  - id: videomae-paper
    resource: ../raw/VideoMAE/main.tex
    title: "VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training"
  - id: internvideo-paper
    resource: ../raw/InternVideo/main.tex
    title: "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
  - id: internvideo2-paper
    resource: ../raw/InternVideo2/main.tex
    title: "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
  - id: lv-mae-paper
    resource: ../raw/LV-MAE/main.tex
    title: "LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders"
---

# Video temporal representation learning

Video representation learning aims to encode temporal structure—appearance, motion, ordering, dynamics, and long-range semantics—rather than optimize only one downstream action label.[^video-temporal-survey]

## Pretraining families

The source groups self-supervised video learning into transformation/order prediction, contrastive learning, and masked video modeling.[^video-temporal-survey] Masked video modeling hides a large fraction of spatiotemporal input and trains an encoder-decoder to reconstruct the missing content; its stated motivation is temporal redundancy in video. VideoMAE is a pixel-reconstruction instance that shares a tube mask across frames and feeds only the remaining visible tokens to its encoder during pretraining.[^videomae-paper]

LV-MAE applies masked modeling at a coarser level: it reconstructs masked sequences of frozen short-video embeddings rather than video pixels. This permits its long-range Transformer to receive one token per five-second segment, but it transfers the short-video encoder's representational limits into the long-video model.[^lv-mae-paper]

## Supervised video pretraining

Supervised pretraining on a large action-video dataset can also yield transferable temporal features. The I3D study reports that Kinetics pretraining improved every evaluated architecture when transferred to UCF-101 and HMDB-51; its fixed I3D features plus a newly trained classifier outperformed direct target-dataset training in the reported split-1 experiments.[^i3d-paper] This is controlled evidence for its architecture and action-recognition transfers, not evidence for transfer to unrelated video tasks.

## Foundation-model direction

The source characterizes video foundation models as a shift from single-task models toward general-purpose video representations. It highlights combining generative masked-video objectives with discriminative video–text contrastive alignment, and later adding next-token prediction in multimodal training.[^video-temporal-survey]

A useful unresolved design tension is the balance between appearance understanding and motion/temporal understanding. The source reports that foundation models can be strong in one while weak in the other; this is retained as an unverified research-gap claim rather than a settled comparison.[^video-temporal-survey]

InternVideo is a concrete modular response to this tension: it trains masked-video and video–text contrastive branches separately, then learns cross-model attention between their features under action-classification supervision. This is paper-specific evidence that feature coordination can be evaluated across action and video–language tasks, not evidence that it resolves the tension generally.[^internvideo-paper]

InternVideo2 extends this progressive family with unmasked-token distillation, video–audio–speech–text alignment, and video-conditioned next-token prediction. Its paper supplies transfer evaluations, but its authors retain fixed-resolution and sampling limits and do not claim a consistent world model; its results therefore do not settle the appearance-versus-temporal-understanding tension generally.[^internvideo2-paper]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Supports:** [Temporal action understanding](temporal-action-understanding.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md).
- **Depends on:** [Long-video temporal modeling](long-video-temporal-modeling.md) when context exceeds a short clip.
- **Instantiated by:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) through ImageNet initialization and supervised Kinetics pretraining.
- **Instantiated by:** [VideoMAE](videomae.md) through masked pixel reconstruction on unlabeled video clips.[^videomae-paper]
- **Instantiated by:** [InternVideo](internvideo.md) by coordinating separately pretrained masked-video and video–text encoders.[^internvideo-paper]
- **Instantiated by:** [InternVideo2](internvideo2.md) through progressive token distillation, multimodal alignment, and video-conditioned next-token prediction.[^internvideo2-paper]
- **Instantiated by:** [LV-MAE](lv-mae.md) through masked reconstruction of frozen clip-level embeddings for bounded long-video sequences.[^lv-mae-paper]

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^i3d-paper]: [Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset](../raw/I3D/full_kinetics_update_v0.tex)
[^videomae-paper]: [VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training](../raw/VideoMAE/main.tex)
[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
