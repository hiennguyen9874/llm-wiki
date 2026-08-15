---
type: Concept
title: Temporal action understanding
description: Video tasks that recognize, localize, segment, or anticipate actions across time.
tags: [video, temporal-learning, action-understanding]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T10:12:47Z }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
---

# Temporal action understanding

Temporal action understanding separates four output granularities: clip-level recognition, interval-level localization, frame-level segmentation, and future-action anticipation.[^video-temporal-survey]

## Task formulations

| Task | Input | Output |
| --- | --- | --- |
| Action recognition | Usually a trimmed clip | One action/class label |
| Temporal action localization/detection | Untrimmed video | Action intervals `(start, end, class)` |
| Action segmentation | Video sequence | A class label for every frame/timestep |
| Action anticipation | Observations through time `t` | One or more future actions |

Localization must identify uncertain action boundaries; segmentation is susceptible to over-segmentation, where noisy predictions fragment an otherwise continuous action. Anticipation and online action understanding must not use future frames at prediction time.[^video-temporal-survey]

## Supervision trade-off

Precise temporal intervals are expensive to annotate. Weakly supervised temporal action localization instead learns from video-level action labels while inferring frame or segment boundaries; the source lists multiple-instance learning, activation sequences, pseudo-labels, contrastive learning, and text supervision as families for this setting.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) as a source of pretrained features.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
