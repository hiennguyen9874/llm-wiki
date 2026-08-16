---
type: Concept
title: Temporal action understanding
description: Video tasks that recognize, localize, segment, or anticipate actions across time.
tags: [video, temporal-learning, action-understanding]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:44:11+07:00 }
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

Localization must identify uncertain action boundaries; segmentation is susceptible to over-segmentation, where noisy predictions fragment an otherwise continuous action. Anticipation and online action understanding must not use future frames at prediction time.[^video-temporal-survey]

## Untrimmed classification is not localization

An untrimmed-video classifier can address varying action locations, durations, and background without returning intervals. For example, TSN’s M-TWI evaluates fixed-rate snippets, pools within multi-scale temporal windows, and aggregates windows into a video-level class score.[^temporal-segment-networks] This is distinct from temporal action localization, whose output must include action boundaries.

## Proposal generation precedes classification

Temporal action proposal generation returns class-agnostic intervals and confidence scores rather than detections. A two-stage detector can subsequently assign action categories to retrieved proposals. BMN is one such proposal generator: it combines predicted boundaries with a dense start-duration confidence map, while the paper supplies classification separately for its detection evaluation.[^bmn-paper]

## Supervision trade-off

Precise temporal intervals are expensive to annotate. Weakly supervised temporal action localization instead learns from video-level action labels while inferring frame or segment boundaries; the source lists multiple-instance learning, activation sequences, pseudo-labels, contrastive learning, and text supervision as families for this setting.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) as a source of pretrained features.
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) for video-level classification across sparse global samples.
- **Includes:** [Boundary-Matching Network (BMN)](boundary-matching-network.md) as a class-agnostic proposal-generation method.

[^bmn-paper]: [BMN: Boundary-Matching Network for Temporal Action Proposal Generation](../raw/BMN/main.tex)
[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
