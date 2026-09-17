---
type: Concept
title: Open-vocabulary promptable perception
description: How text prompts, visual exemplars, and concept prompts are replacing fixed taxonomies and unifying detection, segmentation, and tracking.
tags: [detection, segmentation, open-vocabulary, prompting, sam]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T00:00:00Z }
sources:
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: fixed `class_id ∈ {0,...,79}` formulation is shifting toward `concept = embedding(text / image / exemplar)`, with one promptable model increasingly covering detection plus segmentation plus tracking[^reseach-2026-09-17-1].

## Progression from grounding to concept segmentation

- **Reported:** YOLO-World (CVPR 2024) brings YOLO to real-time open-vocabulary detection via vision-language pretraining, with a YOLO-World-Seg variant[^reseach-2026-09-17-2].
- **Reported:** Grounding DINO 1.5 scales grounding data beyond 20M images, splitting Pro for accuracy and Edge for real-time; paper reports Pro 55.7 AP zero-shot on LVIS-minival and Edge around 75 FPS TensorRT in its setup[^reseach-2026-09-17-3].
- **Reported:** T-Rex2 combines text prompt plus visual exemplar for generic and open-set detection[^reseach-2026-09-17-4].
- **Reported:** YOLOE (ICCV 2025) supports text prompt, visual prompt, and prompt-free modes in one real-time framework for detection and segmentation[^reseach-2026-09-17-5].
- **Reported:** SAM 3 performs concept-prompted detection plus segmentation plus tracking from a noun phrase or image exemplar, returning masks and identities for all matching instances on images and video[^reseach-2026-09-17-6].

## Why SAM 3 matters in this lineage

- **Synthesis:** earlier stages still resembled `text → box`; YOLOE adds `prompt → box + mask`; SAM 3 moves to `concept → all matching instances → mask + identity + track`, removing the manual detector-plus-SAM composition.
- Instance segmentation therefore stops behaving as a separate branch: RF-DETR, YOLO26, YOLOE, and SAM 3 share backbones or unified query representations across box, mask, and track outputs[^reseach-2026-09-17-7].

## Relationships

- Builds on [Vision foundation models for detection](vision-foundation-models-for-detection.md) for semantic representation quality.
- Contrasts with [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md), which optimizes closed-set AP rather than prompt generality.
- Extends into [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) through SAM 2 streaming memory and video tracking.

## Contradictions

- None within this source. Real-time open-vocabulary claims and SAM 3 unified claims come from different authors and protocols, so latency and generality are not directly comparable.

## Coverage limits

- All capability, AP, and FPS figures are **reported**, not reproduced; CVF, arXiv, Meta, and GitHub sources behind them were not fetched.
- Local `raw/arXiv-*` packages were not reconciled here.
- Source material is a Vietnamese synthesis to 17/09/2026 that explicitly disclaims absolute completeness.

[^reseach-2026-09-17-1]: `raw/reseach.md`, sections “Bức tranh tổng thể” and “6. Open-vocabulary detection”.
[^reseach-2026-09-17-2]: `raw/reseach.md`, table row “YOLO-World – CVPR 2024”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “Grounding DINO 1.5” and section “9. Edge/mobile”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “T-Rex2”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “YOLOE – ICCV”.
[^reseach-2026-09-17-6]: `raw/reseach.md`, table row “SAM 3”.
[^reseach-2026-09-17-7]: `raw/reseach.md`, section “7. Instance segmentation không còn là một nhánh riêng”.
