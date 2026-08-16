---
type: Concept
title: Long-video temporal modeling
description: Scalable representations and retrieval mechanisms for preserving fine-grained events across long video contexts.
tags: [video, long-context, temporal-learning, efficiency]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:15:26+07:00 }
sources:
  - id: vivit-paper
    resource: ../raw/ViViT/main_arxiv.tex
    title: "ViViT: A Video Vision Transformer"
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: timesformer-paper
    resource: ../raw/TimeSformer/TimeSformer_arxiv_v17.tex
    title: Is Space-Time Attention All You Need for Video Understanding?
  - id: mvit-paper
    resource: ../raw/MViT/mvit_arxiv.tex
    title: Multiscale Vision Transformers
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
  - id: actionformer-paper
    resource: ../raw/ActionFormer/main.tex
    title: "ActionFormer: Localizing Moments of Actions with Transformers"
---

# Long-video temporal modeling

Long-video understanding cannot generally send every frame and visual token to global attention: context length and quadratic attention cost make this impractical. The source therefore emphasizes temporal compression, hierarchy, memory, and query-guided sampling.[^video-temporal-survey]

## Core strategies

- **Hierarchical modeling:** aggregate frames into clips, events, scenes, and video-level representations.
- **Temporal compression:** replace dense frame tokens with progressively coarser clip or event tokens.
- **Memory:** update a persistent state as new video segments arrive.
- **Query-guided retrieval or sampling:** select frames or segments conditional on a question rather than sampling uniformly.
- **Efficient temporal computation:** use sparse sampling, token pruning, local attention, adaptive resolution, or dynamic allocation of compute.

The common trade-off is retaining precise, short-lived events while modeling dependencies over minutes or hours.[^video-temporal-survey]

## Fixed-budget global sampling

Temporal Segment Networks provide a concrete sparse-sampling alternative: divide a video into equal temporal segments, sample one short snippet from each, and aggregate shared-encoder predictions. With a fixed segment count, compute is independent of video duration while samples remain distributed over the whole video.[^temporal-segment-networks] The trade-off is that unsampled short events can be missed; this is a classification-oriented design rather than a complete event-preservation mechanism.

## Factorized long-clip attention

TimeSformer provides a concrete attention-based alternative: it splits attention into temporal interactions at each patch location followed by spatial interactions within each frame. This changes per-patch comparisons from joint attention's $NF + 1$ to $N + F + 2$, where $N$ is patches per frame and $F$ is frames.[^timesformer-paper] In its long configuration, the source processes 96 frames spanning 102.4 seconds per clip and averages multiple non-overlapping clip predictions to cover each multi-minute HowTo100M video.[^timesformer-paper] Factorization makes longer clips feasible; it does not make full-video global attention or lossless event preservation free.

## Factorised encoder for longer clips

ViViT offers a different factorization: it first reduces the patches at each temporal index with a spatial Transformer, then applies a temporal Transformer only to those per-index representations.[^vivit-paper] In the paper's Kinetics-400 ablation, its ViViT-L/16x2 factorised encoder processed 128 frames sampled at stride 2—enough to cover the dataset's 250-frame, 10-second video with one view—and the source reports its highest accuracy for that configuration.[^vivit-paper] The same paper explicitly limits this evidence to clip-level classification; it does not demonstrate retention or retrieval across arbitrary-length video.

## Multiscale token hierarchy

MViT provides a fixed-clip hierarchical alternative: it pools queries at stage boundaries to shorten the output token sequence, pools keys and values to reduce attention cost, and increases channel width as spatiotemporal resolution falls.[^mvit-paper] This is a concrete token-compression mechanism, but the source evaluates 16–64-frame clips rather than arbitrary-duration video; it does not provide persistent memory or retrieval over a full long video.[^mvit-paper]

## Local spatiotemporal windows

Video Swin Transformer uses joint self-attention inside fixed-size 3D windows and shifts the window grid across successive blocks. Its Kinetics-400 ablation found that an $8 \times 7 \times 7$ temporal-spatial window incurred 88 GFLOPs versus 106 GFLOPs for a temporally global $16 \times 7 \times 7$ window, with a 0.3-point top-1 reduction for the reported Swin-T configuration.[^video-swin-paper] This is a local-attention speed--accuracy trade-off for fixed clips; it neither supplies persistent memory nor demonstrates retrieval over an arbitrary-duration video.

## Local temporal windows with a pyramid

For interval-level temporal action localization, ActionFormer combines local self-attention with a temporal feature pyramid. Its fixed-size window therefore covers a progressively wider temporal span at coarser levels; the paper gives a window of 19 at a 16×-downsampled level as covering 304 feature-grid steps. On THUMOS14, its ablation reports the same 66.8% average mAP for window size 19 as full attention, while reporting 45.3 versus 57.8 GMACs for a 2,304-step input. This is task- and implementation-specific evidence, not a general long-video guarantee.[^actionformer-paper]

## Architectural alternatives

The source identifies local/hierarchical attention and state-space models as alternatives to full global attention. It motivates state-space approaches by approximately linear sequence scaling, but does not provide verified comparative evidence that they are preferable for a particular video task.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md).
- **Supports:** [Video temporal representation learning](video-temporal-representation-learning.md).
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) as a fixed-budget sparse-sampling approach.
- **Uses:** [TimeSformer](timesformer.md) as a factorized-attention approach that expands clip-level temporal coverage.
- **Uses:** [ViViT (Video Vision Transformer)](vivit.md) as a spatial-then-temporal encoder that increases practical clip length.
- **Uses:** [Multiscale Vision Transformers (MViT)](multiscale-vision-transformers-mvit.md) as fixed-clip hierarchical token compression, not as arbitrary-length-video memory.[^mvit-paper]
- **Uses:** [Video Swin Transformer](video-swin-transformer.md) as local joint spatiotemporal attention with shifted cross-window connections, not as arbitrary-length-video memory.[^video-swin-paper]
- **Uses:** [ActionFormer](actionformer.md) as local temporal attention plus a feature pyramid for interval-level temporal action localization.[^actionformer-paper]

[^vivit-paper]: [ViViT: A Video Vision Transformer](../raw/ViViT/main_arxiv.tex)
[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^timesformer-paper]: [Is Space-Time Attention All You Need for Video Understanding?](../raw/TimeSformer/TimeSformer_arxiv_v17.tex)
[^mvit-paper]: [Multiscale Vision Transformers](../raw/MViT/mvit_arxiv.tex)
[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
[^actionformer-paper]: [ActionFormer: Localizing Moments of Actions with Transformers](../raw/ActionFormer/main.tex)
