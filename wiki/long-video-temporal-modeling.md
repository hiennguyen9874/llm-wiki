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

## Architectural alternatives

The source identifies local/hierarchical attention and state-space models as alternatives to full global attention. It motivates state-space approaches by approximately linear sequence scaling, but does not provide verified comparative evidence that they are preferable for a particular video task.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Supports:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md).
- **Supports:** [Video temporal representation learning](video-temporal-representation-learning.md).
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) as a fixed-budget sparse-sampling approach.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
