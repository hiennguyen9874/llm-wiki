---
type: Concept
title: Vision foundation models for detection
description: How DINOv3-class representations are distilled or adapted into small real-time detectors without paying foundation-model inference cost.
tags: [detection, foundation-models, distillation, nas, dinov3]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T00:00:00Z }
sources:
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: the strongest 2025–2026 pattern is **large foundation model during training → small specialist at inference**, either by direct feature use with adapters or by semantic distillation that is removed at deploy time[^reseach-2026-09-17-1].

## DINOv3 as representation source

- **Reported:** DINOv3 scales self-supervised learning to 1.7B images and up to 7B parameters, with emphasis on dense-feature quality; frozen backbones are reported as strong on detection and segmentation[^reseach-2026-09-17-2].
- **Synthesis:** deploying a 7B backbone directly in a detector is impractical, so downstream work focuses on transfer rather than direct deployment.

## Two transfer branches

- **Reported:** DEIMv2 consumes DINOv3 features through backbone or distillation plus a Spatial Tuning Adapter, spanning X down to Atto or Pico; reported DEIMv2-X 57.8 COCO AP, S 50.9 AP under 10M params, Pico ~1.5M params at 38.5 COCO AP[^reseach-2026-09-17-3].
- **Reported:** RT-DETRv4 (ECCV 2026) distills semantic knowledge from a vision foundation model via Deep Semantic Injector plus Gradient-guided Adaptive Modulation without increasing inference cost; reported X 57.0 COCO AP at 78 FPS T4[^reseach-2026-09-17-4].
- **Synthesis:** DEIMv2 keeps foundation features closer to runtime via adapters, while RT-DETRv4 keeps the teacher training-only.

## NAS returns for Pareto search

- **Reported:** RF-DETR combines DINOv2 with LW-DETR and weight-sharing neural architecture search to explore accuracy-versus-latency tradeoffs and dataset-specific adaptation; paper reports 2XL beyond 60 COCO AP[^reseach-2026-09-17-5].
- **Synthesis:** this matters most for industrial vision where CCTV, Jetson Orin, T4 server, aerial small-object, and microscopy optima differ; NAS plus pretrained VFM plus short fine-tuning is the reusable pipeline to watch.

## Relationships

- Uses [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) as the deploy-time architecture receiving distilled signals.
- Supports [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md) where semantic quality depends on foundation representations.
- Constrained by [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) hardware and resolution limits.

## Contradictions

- None within this source. Vendor-reported AP figures should not be compared as if from one leaderboard.

## Coverage limits

- All scale, AP, parameter, and FPS figures are **reported**, not reproduced; Meta, arXiv, and GitHub evidence behind them was not fetched.
- Local `raw/arXiv-*` packages were not reconciled here.
- MambaVision hybrid Mamba-Transformer backbone is noted in the source as an alternative backbone direction but was not made a separate claim set in this concept[^reseach-2026-09-17-6].

[^reseach-2026-09-17-1]: `raw/reseach.md`, section “4. Vision Foundation Model trở thành backbone/teacher”.
[^reseach-2026-09-17-2]: `raw/reseach.md`, table row “DINOv3”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “DEIMv2” and section “9. Edge/mobile”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “RT-DETRv4 – ECCV 2026”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “RF-DETR” and section “5. NAS đang quay lại”.
[^reseach-2026-09-17-6]: `raw/reseach.md`, table row “MambaVision – CVPR”.
