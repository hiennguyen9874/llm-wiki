---
type: Concept
title: Video-language temporal grounding and reasoning
description: Text-conditioned localization and inference over event timing, order, duration, frequency, state changes, and causal relations in video.
tags: [video, language, temporal-grounding, temporal-reasoning, video-llm]
status: draft
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T10:12:47Z }
sources:
  - id: video-temporal-survey
    resource: ../raw/TongHopCacHuongXuLyVideo.md
    title: Tổng hợp các hướng xử lý video
---

# Video-language temporal grounding and reasoning

Video-language temporal grounding finds the interval in a video that matches a natural-language query; temporal reasoning additionally answers questions about relationships among events. The source treats these as distinct capabilities beyond image-style video QA.[^video-temporal-survey]

## Grounding

Given a video and query, temporal grounding returns a start and end time for the matching moment. The source uses the related names *moment retrieval*, *temporal sentence grounding*, and *natural-language video localization*.[^video-temporal-survey]

For long video, grounding needs a mechanism to preserve or retrieve relevant evidence without processing every frame at full resolution. Timestamp-aware tokens, adaptive frame scaling, and instruction-conditioned supervision are presented in the source as emerging approaches; their reported results are unverified in this wiki.[^video-temporal-survey]

## Reasoning relations

The source identifies these temporal reasoning targets:

- ordering: whether one event occurs before or after another;
- duration and frequency;
- intervening events and multi-hop relations;
- state transitions caused by actions; and
- causal explanations.

It argues that fine-grained temporal reasoning remains difficult for multimodal LLMs even when their appearance-based semantic understanding is strong.[^video-temporal-survey]

## Explicit temporal representations

A neuro-symbolic direction translates questions and video events into explicit temporal relations such as *before*, *overlaps*, and *during*, then uses those relations to retrieve evidence before visual-language reasoning. This is a proposed architectural pattern in the source, not a verified general solution.[^video-temporal-survey]

## Relationships

- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Depends on:** [Long-video temporal modeling](long-video-temporal-modeling.md) for long-context evidence access.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) for visual and video–text features.

[^video-temporal-survey]: [Tổng hợp các hướng xử lý video](../raw/TongHopCacHuongXuLyVideo.md)
