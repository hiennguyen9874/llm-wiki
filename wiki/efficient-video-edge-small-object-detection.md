---
type: Concept
title: Efficient video, edge, and small-object detection
description: How temporal reuse, Pareto-driven edge scaling, and small-target assignment address video, mobile, and small-object limits.
tags: [detection, segmentation, video, edge, small-object]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T00:00:00Z }
sources:
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: after closed-set AP saturates near 57–60, progress is increasingly measured as an AP–latency–memory–power Pareto with temporal reuse for video, scaled families for edge, and dedicated assignment for small targets[^reseach-2026-09-17-1].

## Image to video through memory and dynamic compute

- **Reported:** SAM 2 / 2.1 unifies image and video promptable segmentation with streaming memory; paper reports about 6× faster image segmentation than SAM[^reseach-2026-09-17-2].
- **Reported:** CAVIS (ICCV 2025) exploits around-instance context plus cross-frame contrastive representation for video instance segmentation[^reseach-2026-09-17-3].
- **Reported:** Temporal-aware Query Routing (ICCV 2025) skips decoder layers based on inter-frame change; paper reports MinVIS rising from 24.7 to 34.6 FPS in its experiments[^reseach-2026-09-17-4].
- **Synthesis:** reusable direction is `state/memory + cached feature + dynamic computation` rather than running an image detector independently per frame.

## Edge and mobile as first-class objectives

- **Reported:** DEIMv2 spans X down to Nano, Pico, Femto, and Atto; reported Pico has about 1.5M parameters at 38.5 COCO AP[^reseach-2026-09-17-5].
- **Reported:** YOLO26n is reported at 40.9 AP with about 1.7 ms T4 TensorRT in Ultralytics benchmarks, with joint CPU, ONNX, and TensorRT optimization[^reseach-2026-09-17-6].
- **Reported:** RF-DETR-Seg spans Nano to 2XL for real-time instance segmentation; in the same Roboflow protocol, Seg-N is reported at 40.3 mask AP / 3.4 ms and Seg-2XL at 49.9 AP / 21.8 ms on T4 TensorRT FP16, versus YOLO26-X-Seg 46.8 AP / 12.92 ms[^reseach-2026-09-17-7].
- **Synthesis:** these cross-vendor numbers share a protocol only within the cited Roboflow benchmark, not as an independent leaderboard.

## Small objects remain open

- **Reported:** YOLO26 adds STAL and a P2 architecture variant for small-object scenarios[^reseach-2026-09-17-8].
- **Synthesis:** high-resolution features, adaptive tiling, pyramids, query initialization, assignment, and joint super-resolution plus detection remain fertile because aerial, surveillance, and inspection failures persist after overall AP gains.

## Relationships

- Depends on [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) for deploy-time detector efficiency.
- Depends on [Vision foundation models for detection](vision-foundation-models-for-detection.md) for small-model distillation and NAS backbones.
- Uses [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md) tracking and memory ideas for unified box-mask-track video.

## Contradictions

- None within this source. Apparent conflicts between vendor AP or FPS claims reflect different hardware, input sizes, and TensorRT or FP16 setups rather than direct contradictions.

## Coverage limits

- All AP, FPS, latency, and parameter figures are **reported**, not reproduced; CVF, GitHub, Roboflow, and Ultralytics evidence was not fetched.
- Local `raw/arXiv-*` packages were not reconciled here.
- YOLO26 unified detection, instance segmentation, semantic segmentation, depth, pose, and OBB coverage is noted from the source synthesis without per-task verification[^reseach-2026-09-17-9].

[^reseach-2026-09-17-1]: `raw/reseach.md`, sections “9. Edge/mobile” and “Snapshot về closed-set real-time detection”.
[^reseach-2026-09-17-2]: `raw/reseach.md`, table row “SAM 2 / SAM 2.1”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “CAVIS – ICCV”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “Temporal-aware Query Routing – ICCV”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “DEIMv2” and section “9. Edge/mobile”.
[^reseach-2026-09-17-6]: `raw/reseach.md`, section “9. Edge/mobile”.
[^reseach-2026-09-17-7]: `raw/reseach.md`, section “7. Instance segmentation không còn là một nhánh riêng”.
[^reseach-2026-09-17-8]: `raw/reseach.md`, section “10. Small objects vẫn là bài toán chưa giải xong”.
[^reseach-2026-09-17-9]: `raw/reseach.md`, table row “YOLO26”.
