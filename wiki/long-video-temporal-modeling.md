---
type: Concept
title: Long-video temporal modeling
description: Scalable representations and retrieval mechanisms for preserving fine-grained events across long video contexts.
tags: [video, long-context, temporal-learning, efficiency]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T10:23:21Z }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: timesformer-paper
    resource: ../raw/TimeSformer/TimeSformer_arxiv_v17.tex
    title: Is Space-Time Attention All You Need for Video Understanding?
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

## Architectural alternatives

The source identifies local/hierarchical attention and state-space models as alternatives to full global attention. It motivates state-space approaches by approximately linear sequence scaling, but does not provide verified comparative evidence that they are preferable for a particular video task.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md).
- **Supports:** [Video temporal representation learning](video-temporal-representation-learning.md).
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) as a fixed-budget sparse-sampling approach.
- **Uses:** [TimeSformer](timesformer.md) as a factorized-attention approach that expands clip-level temporal coverage.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^timesformer-paper]: [Is Space-Time Attention All You Need for Video Understanding?](../raw/TimeSformer/TimeSformer_arxiv_v17.tex)
