---
type: Concept
title: Video temporal learning
description: A task taxonomy for learning temporal structure in video, spanning recognition, localization, representation learning, language grounding, and reasoning.
tags: [video, temporal-learning, taxonomy]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T10:12:47Z }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
---

# Video temporal learning

Video temporal learning concerns representations and decisions that depend on change, order, duration, and dynamics across frames rather than appearance in isolated images. The source organizes the field from short-clip recognition through long-video and language-based temporal reasoning.[^video-temporal-survey]

## Task map

- **Recognition:** assign one or more labels to a trimmed video clip.
- **Localization and detection:** identify action class and start/end intervals in untrimmed video.
- **Segmentation:** assign an action label at each frame or timestep.
- **Anticipation:** predict upcoming actions from observations available so far.
- **Representation learning:** pretrain temporal representations without task-specific labels.
- **Video–language understanding:** ground a natural-language query in time and answer temporal questions.
- **Long-video understanding:** retain and retrieve information over clips, events, scenes, or hours of video.

## Modeling progression

The source describes a progression from 2D frame encoders with temporal aggregation and 3D convolutions, through non-local operations and video Transformers, toward foundation models and multimodal LLM systems.[^video-temporal-survey] This is a taxonomy, not a claim that later approaches universally replace earlier ones: compute budget, video length, labels, and output granularity determine the appropriate family.

## Relationships

- **Uses:** [Temporal action understanding](temporal-action-understanding.md) for dense and predictive task formulations.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) for pretrained video features.
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) for scalable temporal context.
- **Uses:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) for text-conditioned localization and inference.

## Evidence limits

This is a compilation of one survey-style source. Several of its numbered links visibly do not match the nearby named paper (including entries for TSN, MViT, Video Swin, and ActionFormer), so individual paper-level attributions and recency claims are unverified here. The task taxonomy is retained as draft synthesis pending verification against primary sources.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
