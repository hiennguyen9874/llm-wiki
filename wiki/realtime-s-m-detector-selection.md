---
type: Synthesis
title: Realtime N-S-M detector selection
description: Which N/S/M realtime detector to choose by parameter class, deployment constraints, pretraining, or latency-bucketed NAS.
tags: [detection, realtime, decision, edge]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T05:19:40Z }
sources:
  - id: rtdetrv4-2510-25257-v1
    resource: ../raw/arXiv-2510.25257v1/main.tex
    scope: ../raw/arXiv-2510.25257v1/
    kind: paper
    revision: v1
    title: 'RT-DETRv4: Painlessly Furthering Real-Time Object Detection with Vision Foundation Models'
  - id: yolo26-2509-25164-v5
    resource: ../raw/arXiv-2509.25164v5/template.tex
    scope: ../raw/arXiv-2509.25164v5/
    kind: paper
    revision: v5
    title: 'YOLO26: Key Architectural Enhancements and Performance Benchmarking for Real-Time Object Detection'
  - id: deimv2-2509-20787-v4
    resource: ../raw/arXiv-2509.20787v4/main.tex
    scope: ../raw/arXiv-2509.20787v4/
    kind: paper
    revision: v4
    title: 'Real-Time Object Detection Meets DINOv3'
  - id: dfine-2410-13842-v1
    resource: ../raw/arXiv-2410.13842v1/iclr2025_conference.tex
    scope: ../raw/arXiv-2410.13842v1/
    kind: paper
    revision: v1
    title: 'D-FINE: Redefine Regression Task in DETRs as Fine-grained Distribution Refinement'
  - id: yolov12-2502-12524-v1
    resource: ../raw/arXiv-2502.12524v1/main.tex
    scope: ../raw/arXiv-2502.12524v1/
    kind: paper
    revision: v1
    title: 'YOLOv12: Attention-Centric Real-Time Object Detectors'
  - id: yolov13-2506-17733-v2
    resource: ../raw/arXiv-2506.17733v2/a_main.tex
    scope: ../raw/arXiv-2506.17733v2/
    kind: paper
    revision: v2
    title: 'YOLOv13: Real-Time Object Detection with Hypergraph-Enhanced Adaptive Visual Perception'
  - id: rfdetr-2511-09554-v2
    resource: ../raw/arXiv-2511.09554v2/iclr2026_conference.tex
    scope: ../raw/arXiv-2511.09554v2/
    kind: paper
    revision: v2
    title: 'RF-DETR: Neural Architecture Search for Real-Time Detection Transformers'
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: for 640px COCO realtime, N/S/M names are not comparable until the resource constraint is fixed. Treat N as roughly 2–4M parameters, S as 9–10M, and M as 18–20M; choose `YOLO26-N/S/M` as one deployment-oriented family, `DEIMv2-Nano/S` for reported accuracy within true N/S parameter classes, `D-FINE-M` with Objects365 pretraining for reported M-class accuracy, and `RT-DETRv4-S/M` as the no-Objects365 accuracy–latency balance. Use `RF-DETR-N/S/M` only as latency buckets because its 30–34M parameters do not match ordinary N/S/M size classes.

## Decision matrix

**Synthesis:** select by the binding constraint rather than by the vendor's size suffix:

| Constraint | N | S | M |
| --- | --- | --- | --- |
| One deployment family, simple export | YOLO26-N | YOLO26-S | YOLO26-M |
| Highest reported AP in the true parameter class | DEIMv2-Nano | DEIMv2-S | D-FINE-M with Objects365 |
| Accuracy–latency without Objects365 pretraining | DEIMv2-Nano, with unoptimized implementation caveat | RT-DETRv4-S | RT-DETRv4-M |
| Latency bucket only; 30–34M params acceptable | RF-DETR-N | RF-DETR-S | RF-DETR-M |

**Synthesis:** the architecture-level default is now end-to-end NMS-free detection with dense supervision during training and sparse one-to-one outputs at inference. YOLO26 emphasizes a lean export graph[^yolo26-2509-25164-v5-1]; D-FINE, DEIMv2, RT-DETRv4, and RF-DETR trade more DETR/VFM machinery for localization or AP.

## N-scale at 640px

**Reported** N numbers below mix true 2–4M parameter models with RF-DETR's latency-defined `N`; they are not one size-matched leaderboard:

| Model | Reported AP | Params / FLOPs | Reported latency |
| --- | ---: | --- | --- |
| DEIMv2-Nano | 43.0[^deimv2-2509-20787-v4-3] | 3.57M / 6.86G | 2.32 ms; implementation not latency-optimized |
| YOLOv13-N | 41.6 / 57.8 / 45.1[^yolov13-2506-17733-v2-2] | 2.5M / 6.4G | 1.97 ms T4, 39.97 ms CPU ONNX |
| YOLO26-N | 40.9, 40.1 e2e[^yolo26-2509-25164-v5-1] | 2.4M / 5.4B | 1.7 ms T4 TRT10 FP16, 38.9 ms CPU ONNX |
| RF-DETR-N | 48.0[^rfdetr-2511-09554-v2-1] | 30.5M / 31.9G | 2.3 ms; latency bucket, not parameter-matched |

- **Reported:** DEIMv2-Nano has the highest AP among the inspected true-N models, but the paper states that its latency implementation is not optimized[^deimv2-2509-20787-v4-3].
- **Reported:** YOLO26-N has the lowest reported T4 and CPU latency in this true-N table and exposes separate standard/e2e AP columns[^yolo26-2509-25164-v5-1].
- **Synthesis:** choose DEIMv2-Nano for an accuracy-first N experiment and YOLO26-N for deployment-first N. RF-DETR-N is a latency-defined operating point rather than a nano model in memory or parameter budget.

## S-scale at 640px

**Reported** COCO `val2017` S numbers below are vendor-protocol reports, not a shared leaderboard[^reseach-2026-09-17-1]:

| Model | Reported AP | Params / FLOPs | Reported latency |
| --- | ---: | --- | --- |
| RT-DETRv4-S | 49.7 / 66.8 / 54.1, `AP_S` 30.2[^rtdetrv4-2510-25257-v1-1] | 10M / 25G | 3.66 ms, 273 FPS |
| DEIMv2-S | 50.9 / 68.3 / 55.1, `AP_S` 31.4[^deimv2-2509-20787-v4-1] | 9.71M / 25.62G | 5.78 ms, unoptimized |
| DEIM-S baseline in same table | 49.0 / 65.9, `AP_S` 30.4[^rtdetrv4-2510-25257-v1-1] | 10M / 25G | 3.66 ms |
| YOLO26-S | 48.6, 47.8 e2e[^yolo26-2509-25164-v5-1] | 9.5M / 20.7B | 2.5 ms T4 TRT10 FP16, 87.2 ms CPU ONNX |
| D-FINE-S | 48.5; 50.7 with Objects365[^dfine-2410-13842-v1-1] | 10.2M / 25.2G | 3.49 ms |
| YOLOv12-S | 48.0 / 65.0, `AP_S` 29.8[^yolov12-2502-12524-v1-1] | 9.3M / 21.4G | 2.61 ms |
| YOLOv13-S | 48.0 / 65.2[^yolov13-2506-17733-v2-1] | 9.0M / 20.8G | 2.98 ms |
| RF-DETR-S | 52.9[^rfdetr-2511-09554-v2-1] | 32.1M / 59.8G, 3.5 ms | latency bucket, not params-matched |

- **Reported:** RT-DETRv4-S reaches 49.7 AP at identical params/FLOPs/latency to DEIM-S 49.0, via training-only DSI plus GAM with no inference change[^rtdetrv4-2510-25257-v1-1].
- **Reported:** DEIMv2-S is the first reported sub-10M model above 50 AP at 50.9 AP, but latency is explicitly unoptimized and FlashAttention is named as future work[^deimv2-2509-20787-v4-1].
- **Reported:** DEIMv2-S gains concentrate on medium/large objects while small objects barely move: 52.6 to 55.3 `AP_M`, 65.7 to 70.3 `AP_L`, but only 30.4 to 31.4 `AP_S` versus DEIM-S[^deimv2-2509-20787-v4-2].
- **Synthesis:** for deployable S, prefer YOLO26-S for lowest T4 latency plus CPU ONNX path and clean export. Without Objects365 pretraining, RT-DETRv4-S is the accuracy–latency balance while DEIMv2-S is the highest reported AP with slower, unoptimized latency. With Objects365 allowed, D-FINE-S reaches 50.7 AP at 3.49 ms, nearly DEIMv2-S accuracy under a different pretraining regime[^dfine-2410-13842-v1-1].

## M-scale at 640px

| Model | Reported AP | Params / FLOPs | Reported latency |
| --- | ---: | --- | --- |
| RT-DETRv4-M | 53.5 / 71.1 / 58.1, `AP_S` 34.9[^rtdetrv4-2510-25257-v1-1] | 19M / 57G | 5.91 ms, 169 FPS |
| YOLO26-M | 53.1, 52.5 e2e[^yolo26-2509-25164-v5-1] | 20.4M / 68.2B | 4.7 ms T4, 220.0 ms CPU |
| DEIMv2-M | 53.0[^deimv2-2509-20787-v4-1] | 18.11M / 52.2G | 8.80 ms, unoptimized |
| DEIM-M baseline | 52.7[^rtdetrv4-2510-25257-v1-1] | 19M / 57G | 5.91 ms |
| D-FINE-M | 52.3, 55.1 after Objects365 pretraining[^dfine-2410-13842-v1-1] | 19.2M / 56.6G | 5.55 / 5.62 ms |
| YOLOv12-M | 52.5, `AP_S` 35.7 strongest small-object in M group[^yolov12-2502-12524-v1-1] | 20.2M / 67.5G | 4.86 ms |
| RF-DETR-M | 54.7[^rfdetr-2511-09554-v2-1] | 33.7M / 78.8G, 4.4 ms | latency bucket, not params-matched |

- **Reported:** RT-DETRv4-M 53.5 beats DEIM-M 52.7 and D-FINE-M 52.3 at the same 19M/57G/5.91 ms operating point[^rtdetrv4-2510-25257-v1-1].
- **Reported:** YOLO26-M gives the best T4 latency in the params-matched M group at 4.7 ms for 53.1 AP, 52.5 e2e[^yolo26-2509-25164-v5-1].
- **Synthesis:** for deployable M, prefer YOLO26-M. Without Objects365 pretraining, prefer RT-DETRv4-M for the 19M-class accuracy–latency balance; with Objects365 allowed, D-FINE-M reports the highest inspected M-class AP at 55.1 and 5.62 ms[^dfine-2410-13842-v1-1]. Use RF-DETR-M 54.7 only when ~33M parameters are acceptable for a faster latency bucket[^rfdetr-2511-09554-v2-1].

## Relationships

- Uses [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) for dense-training plus sparse-inference, distributional localization, and VFM-distillation mechanisms.
- Uses [Vision foundation models for detection](vision-foundation-models-for-detection.md) for DINOv3 transfer branches and NAS backbones.
- Constrained by [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) for edge Pareto, CPU/ONNX cost, and small-target limits.

## Contradictions

- No direct contradiction. Cross-vendor AP and latency use different T4, TensorRT, input, NMS, e2e, and buffering setups; treat gaps around 0.5 AP as non-decisive without a shared protocol[^reseach-2026-09-17-1].
- RF-DETR latency uses 200 ms buffering between forwards, requires same-artifact accuracy-latency reporting, and notes YOLO multi- versus single-class NMS plus FP16 degradation and D-FINE FP16 opset fix with about 0.1 ms recompilation variance[^rfdetr-2511-09554-v2-2].

## Coverage limits

- All AP, `AP_S`/`AP_M`/`AP_L`, params, FLOPs, FPS, and latency figures are **reported**, not reproduced; no code was executed.
- **Observed** by static inspection only: table locations named in footnotes were read as text; PDF figures were not visually inspected beyond captions and body-text reproduction.
- YOLO26 reports both standard and e2e mAP columns; RF-DETR N/S/M all carry 30–34M parameters and therefore represent latency buckets rather than parameter-matched scale classes; DEIMv2 latency is reported as unoptimized.
- Source claims coverage to 17/09/2026; absolute completeness is infeasible because new preprints appear weekly[^reseach-2026-09-17-1].

[^rtdetrv4-2510-25257-v1-1]: `raw/arXiv-2510.25257v1/sec/3_method.tex`, Tab. `tab:comparison` S/M rows — S 49.7/66.8/54.1 at 10M/25G/3.66ms/273FPS and M 53.5/71.1/58.1 at 19M/57G/5.91ms/169FPS, with DEIM-S 49.0, DEIM-M 52.7, D-FINE-S 48.5, D-FINE-M 52.3, YOLOv12-S 48.0, YOLOv12-M 52.5, YOLOv13-S 48.0 baselines in the same table; plus `sec/4_experiments.tex` S/M comparison prose.
[^yolo26-2509-25164-v5-1]: `raw/arXiv-2509.25164v5/template.tex`, Tab. `tab:yolo26_metrics` detection panel — 640px N 40.9/40.1 e2e at 38.9ms CPU ONNX and 1.7ms T4 TRT10 FP16 with 2.4M/5.4B; S 48.6/47.8 at 87.2ms/2.5ms with 9.5M/20.7B; M 53.1/52.5 at 220.0ms/4.7ms with 20.4M/68.2B. Secs. Architectural Enhancements and Real-Time Deployment report DFL removal, native NMS-free inference, and ONNX/TensorRT/CoreML/TFLite/OpenVINO export rationale.
[^deimv2-2509-20787-v4-1]: `raw/arXiv-2509.20787v4/sec/1_intro.tex`, Tab. `tab:main` plus `sec/3_method.tex`, Tab. `tab:XLMS` — S 50.9 at 9.71M/25.62G/5.78ms and M 53.0 at 18.11M/52.20G/8.80ms, first sub-10M above 50 AP claim, plus unoptimized-latency and FlashAttention note in `sec/4_experiments.tex`.
[^deimv2-2509-20787-v4-2]: `raw/arXiv-2509.20787v4/sec/4_experiments.tex`, small-object paragraph — DEIMv2-S versus DEIM-S 55.3 versus 52.6 `AP_M`, 70.3 versus 65.7 `AP_L`, 31.4 versus 30.4 `AP_S`; DINOv3 global-semantics versus fine-detail reading.
[^deimv2-2509-20787-v4-3]: `raw/arXiv-2509.20787v4/sec/1_intro.tex`, Tab. `tab:main`, Nano row — 43.0 AP at 3.57M/6.86G/2.32ms; `sec/3_method.tex`, Tab. `tab:my_sorted_label_asc`, ultra-light comparison; `sec/4_experiments.tex`, SOTA comparison paragraph, states latency was not optimized and names FlashAttention as future acceleration.
[^dfine-2410-13842-v1-1]: `raw/arXiv-2410.13842v1/sec/appendix.tex`, Tab. `tab:model_of_SM` plus surrounding prose — S 48.5 at 10.2M/25.2G/3.49ms rising to 50.7 after Objects365, M 52.3 at 19.2M/56.6G/5.55ms rising to 55.1 at 5.62ms.
[^yolov12-2502-12524-v1-1]: `raw/arXiv-2502.12524v1/main.tex`, Tab. Comparison with popular detectors plus Tab. Detailed performance — S 48.0/65.0/51.8 at 21.4G/9.3M/2.61ms with `AP_S` 29.8, M 52.5/69.6/57.1 at 67.5G/20.2M/4.86ms with `AP_S` 35.7; T4 TensorRT FP16 protocol.
[^yolov13-2506-17733-v2-1]: `raw/arXiv-2506.17733v2/sections/tables/coco_compare.tex`, Tab. `tab:coco_compare` — S 48.0/65.2/52.0 at 20.8G/9.0M/2.98ms; COCO Train2017/Val2017 640px T4 TensorRT FP16 setting in `sections/5_experiment.tex`.
[^yolov13-2506-17733-v2-2]: `raw/arXiv-2506.17733v2/sections/tables/coco_compare.tex`, Tab. `tab:coco_compare`, N row — 41.6/57.8/45.1 AP at 2.5M/6.4G/1.97ms T4; `sections/tables/latency.tex`, Tab. `tab:latency` — 1.25ms RTX 4090 and 39.97ms CPU ONNX; `sections/5_experiment.tex`, implementation details — COCO 640px and TensorRT FP16 protocol.
[^rfdetr-2511-09554-v2-1]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Tab. `tab:coco_det` — N 48.0 at 30.5M/31.9G/2.3ms, S 52.9 at 32.1M/59.8G/3.5ms, and M 54.7 at 33.7M/78.8G/4.4ms; latency-bucketed sizing following LW-DETR.
[^rfdetr-2511-09554-v2-2]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Tab. `tab:latency` plus Sec. Standardizing Latency Benchmarking — 200ms buffering, same-artifact rule, YOLO NMS and FP32-to-FP16 issues, D-FINE FP16 to 0.5 AP fixed by ONNX opset 17, about 0.1ms TensorRT recompilation variance.
[^reseach-2026-09-17-1]: `raw/reseach.md`, section “Snapshot về closed-set real-time detection hiện nay” — explicit non-absolute-ranking warning due to differing protocols, plus weekly-preprint incompleteness note.
