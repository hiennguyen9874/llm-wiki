---
type: Concept
title: Real-time end-to-end detection without NMS
description: How 2024–2026 real-time detectors converged on NMS-free end-to-end inference with dense training supervision and distributional localization.
tags: [detection, detr, yolo, nms-free, label-assignment]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T00:00:00Z }
sources:
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: real-time detection is converging from `YOLO = dense + NMS` versus `DETR = sparse queries + bipartite matching` toward NMS-free end-to-end inference, with dense supervision used only during training and refined localization modeling[^reseach-2026-09-17-1].

## Dense training, sparse inference

- **Reported:** RT-DETRv3 (WACV 2025) adds hierarchical dense positive supervision to fix sparse Hungarian one-to-one supervision, keeping inference end-to-end[^reseach-2026-09-17-2].
- **Reported:** DEIM (CVPR 2025) introduces Dense one-to-one matching plus Matchability-Aware Loss; paper reports ~50% training-time reduction in its experiments[^reseach-2026-09-17-3].
- **Reported:** YOLO26 provides native one-to-one NMS-free head, drops DFL, and uses Progressive Loss plus Small-Target-Aware Label Assignment (STAL)[^reseach-2026-09-17-4].
- **Synthesis:** the durable pattern is **train dense → infer sparse**: rich positive signals while learning, simple NMS-free pipeline at deployment.

## Localization as distribution refinement

- **Reported:** D-FINE (ICLR 2025 Spotlight) reframes box regression as Fine-grained Distribution Refinement with Global Optimal Localization Self-Distillation, without large added inference cost[^reseach-2026-09-17-5].
- **Synthesis:** this extends the older shift in classification toward distributional or soft targets into localization as structured prediction.

## Closed-set real-time snapshot with protocol caveat

**Reported** COCO box AP values from the source synthesis; protocols differ by vendor and hardware, so this is a landscape view rather than an absolute ranking[^reseach-2026-09-17-6]:

| Model | Reported COCO box AP | Note |
| --- | ---: | --- |
| RF-DETR-2XL | 60.1 | Roboflow benchmark, T4 17.2 ms |
| DEIMv2-X | 57.8 | 50.3M params, uses DINOv3 |
| YOLO26-X | 57.5 | Ultralytics reports 11.8 ms T4 TensorRT |
| RT-DETRv4-X | 57.0 | 78 FPS T4, VFM distillation without inference overhead |
| DEIM-D-FINE-X | ~56.4–56.5 | CVPR paper reports 78 FPS T4 |
| RT-DETRv3-R101 | 54.6 | Dense supervision in training |

Earlier anchors in the same lineage include RT-DETRv2 bag-of-freebies and multi-scale sampling, LW-DETR lightweight ViT encoder plus shallow decoder, YOLOv12 attention-centric design (reported N 40.6 AP / 1.64 ms T4), and YOLOv13 hypergraph adaptive correlation[^reseach-2026-09-17-7].

## Relationships

- Uses [Vision foundation models for detection](vision-foundation-models-for-detection.md) for teacher or backbone signals in DEIMv2 and RT-DETRv4.
- Contrasts with [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md), which replaces the closed-set class taxonomy rather than optimizing closed-set AP.
- Constrained by [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) Pareto and small-target assignment limits.

## Contradictions

- None within this source. Cross-vendor AP and latency numbers use different measurement setups; treat 0.5 AP gaps as non-decisive without a shared protocol.

## Coverage limits

- All AP, latency, and training-time figures are **reported**, not reproduced; external arXiv, CVF, GitHub, Ultralytics, and Roboflow links in the source were not fetched.
- Local `raw/arXiv-*` packages were not reconciled in this operation and remain separate future sources.
- Source claims coverage to 17/09/2026 and states absolute completeness is infeasible because new preprints appear weekly.

[^reseach-2026-09-17-1]: `raw/reseach.md`, section “Bức tranh tổng thể” — YOLO-vs-DETR convergence claim.
[^reseach-2026-09-17-2]: `raw/reseach.md`, table row “RT-DETRv3 – WACV” and section “1. End-to-end, NMS-free” / “2. assignment / supervision”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “DEIM – CVPR”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “YOLO26” and section “10. Small objects”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “D-FINE – ICLR Spotlight” and section “3. Localization/bbox regression”.
[^reseach-2026-09-17-6]: `raw/reseach.md`, section “Snapshot về closed-set real-time detection hiện nay” including explicit non-ranking warning.
[^reseach-2026-09-17-7]: `raw/reseach.md`, table rows RT-DETRv2, LW-DETR, YOLOv12, YOLOv13.
