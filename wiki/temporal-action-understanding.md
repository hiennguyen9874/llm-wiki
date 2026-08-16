---
type: Concept
title: Temporal action understanding
description: Video tasks that recognize, localize, segment, or anticipate actions across time.
tags: [video, temporal-learning, action-understanding]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:21:31+07:00 }
sources:
  - id: bmn-paper
    resource: ../raw/BMN/main.tex
    title: BMN: Boundary-Matching Network for Temporal Action Proposal Generation
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: ms-tcn-paper
    resource: ../raw/MS-TCN/egpaper_final.tex
    title: MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation
  - id: mvit-paper
    resource: ../raw/MViT/mvit_arxiv.tex
    title: Multiscale Vision Transformers
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
  - id: videomae-paper
    resource: ../raw/VideoMAE/main.tex
    title: "VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training"
  - id: actionformer-paper
    resource: ../raw/ActionFormer/main.tex
    title: "ActionFormer: Localizing Moments of Actions with Transformers"
  - id: futr-paper
    resource: ../raw/FutureTransformer/main.tex
    title: Future Transformer for Long-term Action Anticipation
  - id: internvideo-paper
    resource: ../raw/InternVideo/main.tex
    title: "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
  - id: mat-paper
    resource: ../raw/Memory-and-AnticipationTransformer/main.tex
    title: Memory-and-Anticipation Transformer for Online Action Understanding
---

# Temporal action understanding

Temporal action understanding separates four output granularities: clip-level recognition, interval-level localization, frame-level segmentation, and future-action anticipation.[^video-temporal-survey]

## Task formulations

| Task | Input | Output |
| --- | --- | --- |
| Action recognition | Usually a trimmed clip | One action/class label |
| Temporal action proposal generation | Untrimmed video | Class-agnostic candidate intervals with confidence scores |
| Temporal action localization/detection | Untrimmed video | Action intervals `(start, end, class)` |
| Action segmentation | Video sequence | A class label for every frame/timestep |
| Action anticipation | Observations through time `t` | One or more future actions |
| Online action detection | Observations through current time | Current action class at each timestep |

Online action detection classifies the action as it occurs without future access; it is not interval-level temporal action localization, which must return action boundaries. MAT treats online detection as the zero-gap ($\tau=0$) case of a shared detection-and-fixed-gap-anticipation formulation, taking its current prediction from short-term memory and its future prediction from a gap-aligned future token.[^mat-paper]

Localization must identify uncertain action boundaries; segmentation is susceptible to over-segmentation, where noisy predictions fragment an otherwise continuous action. MS-TCN addresses fully supervised frame-level segmentation with multi-stage temporal refinement and a smoothing objective over adjacent frame predictions.[^ms-tcn-paper] Anticipation and online action understanding must not use future frames at prediction time.[^video-temporal-survey]

## Long-term action anticipation

Long-term action anticipation predicts a sequence of future actions from an observed prefix, potentially covering minutes rather than only the next action. One segment-based formulation predicts each future action class and its duration, then expands the segments into framewise labels for evaluation.[^futr-paper]

FUTR uses this formulation with globally attended sampled past-frame features and ordered future-action queries. It emits the query outputs in parallel, so its decoder can model bidirectional dependencies among predicted future actions without feeding a preceding predicted class back as input.[^futr-paper] Its auxiliary segmentation loss requires past-frame labels during training; it is therefore distinct from anticipation settings that provide only coarser action annotations.

## Untrimmed classification is not localization

An untrimmed-video classifier can address varying action locations, durations, and background without returning intervals. For example, TSN’s M-TWI evaluates fixed-rate snippets, pools within multi-scale temporal windows, and aggregates windows into a video-level class score.[^temporal-segment-networks] This is distinct from temporal action localization, whose output must include action boundaries.

## Proposal generation precedes classification

Temporal action proposal generation returns class-agnostic intervals and confidence scores rather than detections. A two-stage detector can subsequently assign action categories to retrieved proposals. BMN is one such proposal generator: it combines predicted boundaries with a dense start-duration confidence map, while the paper supplies classification separately for its detection evaluation.[^bmn-paper]

## Transformer backbone across task granularity

MViT is evaluated as a fixed-clip Transformer backbone for Kinetics, Something-Something-V2, and Charades classification, then as a Kinetics-pretrained backbone with a video-adapted RoI head for AVA human-action detection.[^mvit-paper] The latter localizes actions around annotated frames with regions; it is not evidence that MViT alone outputs temporal action intervals or framewise segmentation.

ActionFormer directly targets interval-level TAL: it classifies each temporal feature-grid location and regresses distances to its action boundaries, using a multiscale local-attention Transformer and convolutional heads. This is a single-stage anchor-free detector, unlike proposal generation and clip-level classification.[^actionformer-paper]

## Self-supervised backbone transfer

VideoMAE is a masked-video-pretraining method rather than a task head. Its source transfers a Kinetics-400-pretrained ViT-B to AVA human-action detection and reports 26.7 mAP without labeled-Kinetics fine-tuning and 31.8 mAP with it; this is frame-centered detection evidence, not evidence for temporal action intervals or framewise segmentation.[^videomae-paper]

## Foundation-model backbone transfer

InternVideo provides a pretrained ViT-H backbone rather than a new temporal-action-localization head. In the paper's backbone substitution experiments, it pairs that backbone with ActionFormer for THUMOS-14, ActivityNet-v1.3, and FineAction, and with TCANet for HACS Segment; reported average mAP values are 71.58, 39.00, 17.57, and 41.55 respectively.[^internvideo-paper] These results are evidence for the stated backbone/head combinations under their protocols, not a claim that InternVideo alone returns temporal intervals.

## Supervision trade-off

Precise temporal intervals are expensive to annotate. Weakly supervised temporal action localization instead learns from video-level action labels while inferring frame or segment boundaries; the source lists multiple-instance learning, activation sequences, pseudo-labels, contrastive learning, and text supervision as families for this setting.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) as a source of pretrained features.
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) for video-level classification across sparse global samples.
- **Includes:** [Boundary-Matching Network (BMN)](boundary-matching-network.md) as a class-agnostic proposal-generation method.
- **Includes:** [MS-TCN (Multi-Stage Temporal Convolutional Network)](ms-tcn.md) as a fully supervised frame-level segmentation method.
- **Includes:** [Multiscale Vision Transformers (MViT)](multiscale-vision-transformers-mvit.md) as a Transformer backbone evaluated for clip classification and frame-centered human-action detection.[^mvit-paper]
- **Includes:** [Video Swin Transformer](video-swin-transformer.md) as a local-attention Transformer backbone evaluated for clip-level action recognition.[^video-swin-paper]
- **Uses:** [VideoMAE](videomae.md) as a self-supervised pretrained backbone for clip classification and frame-centered human-action detection.[^videomae-paper]
- **Includes:** [ActionFormer](actionformer.md) as a single-stage anchor-free Transformer for interval-level temporal action localization.[^actionformer-paper]
- **Includes:** [Future Transformer (FUTR)](future-transformer-futr.md) as a long-term, framewise action-anticipation model with parallel segment decoding.[^futr-paper]
- **Includes:** [Memory-and-Anticipation Transformer (MAT)](memory-and-anticipation-transformer-mat.md) as a unified online current-action detection and fixed-gap anticipation model.[^mat-paper]
- **Uses:** [InternVideo](internvideo.md) as a pretrained feature backbone evaluated with existing action-recognition, temporal-localization, and spatiotemporal-localization heads.[^internvideo-paper]

[^bmn-paper]: [BMN: Boundary-Matching Network for Temporal Action Proposal Generation](../raw/BMN/main.tex)
[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^ms-tcn-paper]: [MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation](../raw/MS-TCN/egpaper_final.tex)
[^mvit-paper]: [Multiscale Vision Transformers](../raw/MViT/mvit_arxiv.tex)
[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
[^videomae-paper]: [VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training](../raw/VideoMAE/main.tex)
[^actionformer-paper]: [ActionFormer: Localizing Moments of Actions with Transformers](../raw/ActionFormer/main.tex)
[^futr-paper]: [Future Transformer for Long-term Action Anticipation](../raw/FutureTransformer/main.tex)
[^internvideo-paper]: [InternVideo: General Video Foundation Models via Generative and Discriminative Learning](../raw/InternVideo/main.tex)
[^mat-paper]: [Memory-and-Anticipation Transformer for Online Action Understanding](../raw/Memory-and-AnticipationTransformer/main.tex)
