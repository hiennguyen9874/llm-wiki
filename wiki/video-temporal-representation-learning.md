---
type: Concept
title: Video temporal representation learning
description: Pretraining video features to encode appearance, motion, order, dynamics, and longer-range semantics for downstream tasks.
tags: [video, representation-learning, self-supervised-learning, foundation-models]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:03:39+07:00 }
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
  - id: f2g-paper
    resource: ../raw/Foresee-to-Ground/main.tex
    title: "Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding"
  - id: xclip-recognition-paper
    resource: ../raw/2208.02816_X-CLIP/main.tex
    title: Expanding Language-Image Pretrained Models for General Video Recognition
  - id: videoprism-paper
    resource: ../raw/2402.13217_VideoPrism/main.tex
    title: "VideoPrism: A Foundational Visual Encoder for Video Understanding"
  - id: vjepa2-paper
    resource: ../raw/2506.09985_V-JEPA 2/main.tex
    title: "V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning"
---

# Video temporal representation learning

Video representation learning aims to encode temporal structure—appearance, motion, ordering, dynamics, and long-range semantics—rather than optimize only one downstream action label.[^video-temporal-survey]

## Pretraining families

The source groups self-supervised video learning into transformation/order prediction, contrastive learning, and masked video modeling.[^video-temporal-survey] Masked video modeling hides a large fraction of spatiotemporal input and trains an encoder-decoder to reconstruct the missing content; its stated motivation is temporal redundancy in video. VideoMAE is a pixel-reconstruction instance that shares a tube mask across frames and feeds only the remaining visible tokens to its encoder during pretraining.[^videomae-paper]

LV-MAE applies masked modeling at a coarser level: it reconstructs masked sequences of frozen short-video embeddings rather than video pixels. This permits its long-range Transformer to receive one token per five-second segment, but it transfers the short-video encoder's representational limits into the long-video model.[^lv-mae-paper]

## Predictive temporal pretraining for event proposals

Foresee-to-Ground pretrains a temporal module by predicting a global-view latent sequence from multiple local views made with temporal crops, strides, or subsampling. It adds sliced isotropic Gaussian regularization to the latent distribution, then reuses the temporal module’s full-sequence features for query-agnostic event-span proposals. This is source-specific evidence for representation learning intended to expose event transitions and support grounding, not a general validation that predictive objectives yield boundary-sensitive features.[^f2g-paper]

## Joint-embedding predictive video learning

V-JEPA 2 predicts masked video representations from visible tubelets using an EMA teacher and L1 feature regression rather than reconstructing pixels. Its scaling study combines more data, encoders up to 1B parameters, longer training, and a progressive cooldown from 16-frame 256×256 clips to as many as 64 higher-resolution frames. The source reports gains under frozen attentive probes, but its ablations combine changes in data, scale, schedule, and resolution and do not establish that feature prediction alone causes the full improvement.[^vjepa2-paper]

The same frozen representation supports a separately trained action-conditioned predictor for robot-frame forecasting. This is evidence that a video representation can become the state space of a latent dynamics model after interaction-data post-training, not that the action-free encoder itself learns controllable dynamics.[^vjepa2-paper]

## Supervised video pretraining

Supervised pretraining on a large action-video dataset can also yield transferable temporal features. The I3D study reports that Kinetics pretraining improved every evaluated architecture when transferred to UCF-101 and HMDB-51; its fixed I3D features plus a newly trained classifier outperformed direct target-dataset training in the reported split-1 experiments.[^i3d-paper] This is controlled evidence for its architecture and action-recognition transfers, not evidence for transfer to unrelated video tasks.

## Language-image model adaptation

X-CLIP adapts an image-text-pretrained encoder to clip-level video recognition without a new web-scale video-text pretraining stage. It retains frame-local patch processing while using one temporary message token per frame for cross-frame exchange, then applies a shallow temporal integration Transformer. A video-conditioned prompting module also adapts class-text embeddings to each video's visual content. This is source-specific evidence for transferring an image-text joint space into fully supervised, few-shot, and cross-dataset zero-shot video classification, not evidence for temporal localization or long-video understanding.[^xclip-recognition-paper]

## Sequential semantic and contextual distillation

VideoPrism first contrastively aligns video and text, then continues the video encoder with masked modeling against frozen Stage-1 teacher features. Its local objective reconstructs all teacher token embeddings after shuffling visible and mask tokens, while a separate global objective matches the teacher's pooled intact-video embedding from visible student tokens. Under the paper's frozen MAP probes, Stage 2 improves the reported Stage-1 results across appearance, motion, localization, retrieval, and zero-shot classification tasks; component ablations show task-dependent rather than uniformly additive effects.[^videoprism-paper]

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
- **Used by:** [Foresee-to-Ground (F2G)](foresee-to-ground.md) through multi-view latent prediction and geometry regularization before query-agnostic event-span proposal generation.[^f2g-paper]
- **Instantiated by:** [X-CLIP: CLIP adaptation for video recognition](x-clip-video-recognition.md) through cross-frame message passing, temporal integration, and video-conditioned class-text representations.[^xclip-recognition-paper]
- **Instantiated by:** [VideoPrism](videoprism.md) through sequential video-text alignment and masked global-local teacher-feature distillation with token shuffling.[^videoprism-paper]
- **Instantiated by:** [V-JEPA 2](v-jepa-2.md) through masked EMA-teacher feature prediction, followed separately by action-conditioned latent-dynamics post-training.[^vjepa2-paper]
- **Compared in:** [Video backbones and encoders comparison](video-backbones-and-encoders-comparison.md), which separates backbone architecture, pretraining recipe, corpus scale, and task-specific transfer evidence.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^i3d-paper]: [Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset](../raw/I3D/full_kinetics_update_v0.tex)
[^videomae-paper]: [VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training](../raw/VideoMAE/main.tex)
[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
[^f2g-paper]: [Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding](../raw/Foresee-to-Ground/main.tex)
[^xclip-recognition-paper]: [Expanding Language-Image Pretrained Models for General Video Recognition](../raw/2208.02816_X-CLIP/main.tex)
[^videoprism-paper]: [VideoPrism: A Foundational Visual Encoder for Video Understanding](../raw/2402.13217_VideoPrism/main.tex)
[^vjepa2-paper]: [V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning](../raw/2506.09985_V-JEPA%202/main.tex)
