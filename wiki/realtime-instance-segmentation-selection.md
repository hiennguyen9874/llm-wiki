---
type: Synthesis
title: Realtime instance segmentation model selection
description: Which instance segmentation model to choose for fast closed-set, open-vocabulary, or video deployment.
tags: [segmentation, realtime, decision, video, open-vocabulary]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T18:45:00Z }
sources:
  - id: rfdetr-2511-09554-v2
    resource: ../raw/arXiv-2511.09554v2/iclr2026_conference.tex
    scope: ../raw/arXiv-2511.09554v2/
    kind: paper
    revision: v2
    title: 'RF-DETR: Neural Architecture Search for Real-Time Detection Transformers'
  - id: yolo26-2509-25164-v5
    resource: ../raw/arXiv-2509.25164v5/template.tex
    scope: ../raw/arXiv-2509.25164v5/
    kind: paper
    revision: v5
    title: 'YOLO26: Key Architectural Enhancements and Performance Benchmarking for Real-Time Object Detection'
  - id: ultralytics-yolo26-doc-9f4ac453
    resource: ../raw/yolo26.md
    kind: documentation
    revision: 'sha256:9f4ac4536d6123446238912e6d4a30240b4f67f29e5cd0e78ec1e7a64ac0f4eb'
    title: Ultralytics YOLO26
  - id: ultralytics-yolo27-doc-52318137
    resource: ../raw/yolo27.md
    kind: documentation
    revision: 'sha256:52318137ab7ee6336c52d1566ed1c0a39bc081c97b4736a2e5e5c1cdc18df7b5'
    title: Ultralytics YOLO27
  - id: yoloe-2503-07465-v2
    resource: ../raw/arXiv-2503.07465v2/camera_ready.tex
    scope: ../raw/arXiv-2503.07465v2/
    kind: paper
    revision: v2
    title: 'YOLOE: Real-Time Seeing Anything'
  - id: sam3-2511-16719-v2
    resource: ../raw/arXiv-2511.16719v2/main.tex
    scope: ../raw/arXiv-2511.16719v2/
    kind: paper
    revision: v2
    title: 'SAM 3: Segment Anything with Concepts'
  - id: sam2-2408-00714-v2
    resource: ../raw/arXiv-2408.00714v2/sam2.1_arxiv.tex
    scope: ../raw/arXiv-2408.00714v2/
    kind: paper
    revision: v2
    title: 'SAM 2: Segment Anything in Images and Videos'
  - id: tar-iccv2025-cheng
    resource: ../raw/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper.md
    scope: ../raw/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper/
    kind: paper
    title: 'Temporal-aware Query Routing for Real-time Video Instance Segmentation'
  - id: dfine-seg-2602-23043-v1
    resource: ../raw/2602.23043v1/2602.23043v1.md
    scope: ../raw/2602.23043v1/
    kind: paper
    revision: v1
    title: 'D-FINE-SEG: Object Detection and Instance Segmentation Framework with Multi-Backend Deployment'
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
---

Synthesis: "SOTA instance segmentation" is now three separate questions — closed-set image, open-vocabulary/concept-prompted, and video — and the fastest credible answer differs in each. For fast closed-set COCO-style masks, **RF-DETR-Seg** currently offers the strongest reported accuracy–latency Pareto, with **YOLO26-Seg** as the leaner deployment-oriented family; for real-time open-vocabulary masks, **YOLOE-Seg** is the fast option while **SAM 3** is the highest-quality but heavy option; for video, **SAM 2.1 / SAM 3** plus decoder-routing techniques such as **TAR** are the relevant real-time points.

## Decision matrix

**Synthesis:** choose by task formulation first, because the three families share neither training data nor metrics:

| Need | Recommended | Why / trade-off |
| --- | --- | --- |
| Fast closed-set masks, fine-tuning base | RF-DETR-Seg Nano→M | Best reported mask-AP-per-ms at small sizes; NAS searchable |
| Closed-set masks, lean edge export | YOLO26-Seg N/S/M | NMS-free + DFL-free export to ONNX/TensorRT/CoreML/TFLite/OpenVINO |
| Custom-dataset segmentation with an existing DETR detector | D-FINE-SEG | Reuses D-FINE box model plus PAN-only mask head and multi-backend export |
| Real-time open-vocabulary masks | YOLOE-Seg | Text/visual/prompt-free prompting with re-parameterized, real-time inference |
| Best open-vocabulary mask quality | SAM 3 | Concept → all instances + identity + track, but ~850M params |
| Real-time video masks | SAM 2.1 / SAM 3; TAR for decoder-heavy pipelines | Streaming memory, or skip redundant decoder layers per frame |

## Fast closed-set image segmentation

- **Reported:** RF-DETR-Seg adds a lightweight mask branch that bilinearly upsamples the same low-resolution encoder map used for detection, projects it to pixel embeddings, and dots per-decoder-layer query embeddings against it, omitting multi-scale backbone features to save latency[^rfdetr-2511-09554-v2-1].
- **Reported:** COCO `val2017` (T4 TensorRT) mask AP / latency: Seg-N `40.3` / `3.4` ms, Seg-S `43.1` / `4.4` ms, Seg-M `45.3` / `5.9` ms, Seg-L `47.1` / `8.8` ms, Seg-XL `48.8` / `13.5` ms, Seg-2XL `49.9` / `21.8` ms, Seg-Max `50.5` / `95.6` ms[^rfdetr-2511-09554-v2-2].
- **Reported:** YOLO26 segmentation e2e box/mask AP at 640 px ranges from N-seg `39.6`/`33.9` (53.3 ms CPU ONNX / 2.1 ms T4) to X-seg `56.5`/`47.0` (787.0 ms / 16.4 ms), with ONNX, TensorRT, CoreML, TFLite, and OpenVINO export and stable FP16/INT8 behavior[^yolo26-2509-25164-v5-4]; the current documentation page lists the same export set as LiteRT rather than TFLite[^ultralytics-yolo26-doc-9f4ac453-1].
- **Reported:** the YOLO26 instance-segmentation head adds a semantic segmentation loss to improve convergence and an upgraded proto module that aggregates multi-scale information for mask quality, reported at up to +2.5 box AP and +3.7 mask AP over YOLO11 on COCO instance segmentation[^ultralytics-yolo26-doc-9f4ac453-1].
- **Synthesis:** the Ultralytics documentation page and the v5 architecture/benchmark paper report identical YOLO26l/x-seg box and mask AP (l `54.4`/`45.5`, x `56.5`/`47.0`) and the same N/S/M values as table B, so those numbers are cross-reported by two Ultralytics artifacts; both remain vendor-internal and neither is an independent benchmark[^ultralytics-yolo26-doc-9f4ac453-1][^yolo26-2509-25164-v5-4].
- **Synthesis:** the caveat matters more than the ranking. RF-DETR Seg-N beats older YOLOv8/11 sizes and FastInst-R50 on the reported table, and the Roboflow same-protocol comparison places RF-DETR Seg-2XL `49.9`/`21.8` ms against YOLO26-X-Seg `46.8`/`12.92` ms; that is one vendor's internal protocol, not an independent leaderboard[^reseach-2026-09-17-7].
- **Reported:** Ultralytics also previews YOLO27-seg, unreleased and preliminary, at 640 px with n 41.8 box / 35.4 mask AP (3.0M / 11.2B, 22.0 ms CPU ONNX, 0.73 ms RTX PRO 6000 TensorRT 11), s 50.0/42.5 (11.6M / 43.1B), m 53.2/45.0 (25.4M / 139.6B), and l 57.7/47.9 (67.5M / 361.9B); the two-architecture split applies to detection only, so all `-seg` scales and every other task keep the CNN architecture[^ultralytics-yolo27-doc-52318137-1].
- **Synthesis:** YOLO27-seg is deliberately kept out of tables A and B: its numbers are vendor-preliminary, its latency host (RTX PRO 6000 TensorRT 11 FP16 plus AMD EPYC 9655 ONNX FP32) matches neither protocol, and the models are unreleased, so it informs no selection today beyond indicating that the successor family keeps a CNN segmentation path and reports higher mask AP at every scale[^ultralytics-yolo27-doc-52318137-1][^ultralytics-yolo27-doc-52318137-2].
- **Synthesis:** prefer RF-DETR-Seg when accuracy per millisecond dominates and a NAS/fine-tuning workflow is acceptable; prefer YOLO26-Seg when export simplicity and low CPU/ONNX latency dominate.

### Closed-set COCO masks, models up to M

**Synthesis:** two reported protocols exist here and must not be mixed. The RF-DETR paper re-benchmarks YOLOv8/YOLOv11-seg and FastInst on T4 TensorRT with latency including proto→mask conversion[^rfdetr-2511-09554-v2-2]; the YOLO26 paper reports its own 640 px end-to-end T4 TensorRT10 FP16 plus CPU ONNX numbers[^yolo26-2509-25164-v5-4]. Within the RF-DETR protocol RF-DETR-Seg N/S/M leads mask AP at the same or lower latency, but at ~33–36M parameters versus 3–27M for the YOLO baselines.

**Reported** table A — RF-DETR paper protocol, COCO `val2017` mask AP, T4 TensorRT[^rfdetr-2511-09554-v2-2]:

| Model | Size | Params (M) | GFLOPs | Latency (ms) | mask AP | AP50 | AP75 | AP_S | AP_M | AP_L |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| YOLOv8-seg | N | 3.4 | 12.6 | 3.5 | 28.3 | 45.6 | 29.8 | 9.3 | 31.3 | 44.3 |
| YOLOv11-seg | N | 2.9 | 10.4 | 3.6 | 30.0 | 47.8 | 31.5 | 10.0 | 33.4 | 47.7 |
| RF-DETR-Seg | N | 33.6 | 50.0 | 3.4 | **40.3** | 63.0 | 42.6 | 16.3 | 45.3 | 63.6 |
| YOLOv8-seg | S | 11.8 | 42.6 | 4.2 | 34.0 | 53.8 | 36.0 | 13.6 | 38.5 | 52.2 |
| YOLOv11-seg | S | 10.1 | 35.5 | 4.6 | 35.0 | 55.4 | 37.1 | 15.3 | 39.7 | 53.9 |
| RF-DETR-Seg | S | 33.7 | 70.6 | 4.4 | **43.1** | 66.2 | 45.9 | 21.9 | 48.5 | 64.1 |
| YOLOv8-seg | M | 27.3 | 110.2 | 7.0 | 37.3 | 58.2 | 39.9 | 16.7 | 43.0 | 56.1 |
| YOLOv11-seg | M | 22.4 | 123.3 | 6.9 | 38.5 | 60.0 | 40.9 | 18.0 | 44.3 | 57.6 |
| RF-DETR-Seg | M | 35.7 | 102.0 | 5.9 | **45.3** | 68.4 | 48.8 | 25.5 | 50.4 | 65.3 |
| FastInst | R50 | 29.7 | 99.7 | 39.6* | 34.9 | 56.0 | 36.2 | 13.3 | 38.0 | 56.8 |

`*` = PyTorch latency; the model does not expose a TensorRT artifact in that table. FastInst is NMS-based, not end-to-end.

**Reported** table B — YOLO26 paper protocol, 640 px, end-to-end, T4 TensorRT10 FP16 and CPU ONNX[^yolo26-2509-25164-v5-4]:

| Model | Params (M) | FLOPs (B) | T4 (ms) | CPU ONNX (ms) | box AP (e2e) | mask AP (e2e) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| YOLO26n-seg | 2.7 | 9.1 | 2.1 | 53.3 | 39.6 | 33.9 |
| YOLO26s-seg | 10.4 | 34.2 | 3.3 | 118.4 | 47.3 | 40.0 |
| YOLO26m-seg | 23.6 | 121.5 | 6.7 | 328.2 | 52.5 | 44.1 |

- **Synthesis:** within table B the mask AP ordering is YOLO26m-seg `44.1` > YOLO26s-seg `40.0` > YOLO26n-seg `33.9`, but these are a different protocol from table A, so do not place YOLO26s-seg `40.0` against RF-DETR-Seg-N `40.3` as if measured alike[^yolo26-2509-25164-v5-4].
- **Synthesis:** D-FINE-SEG has no COCO mask table in its artifact (TACO protocol only), so it is excluded from both closed-set COCO tables; see the specialist section below[^dfine-seg-2602-23043-v1-1].

### Segmentation-capable models excluded from these tables

**Synthesis:** the two tables cover only closed-set COCO instance segmentation at ≤ M scale under two reported protocols. Segmentation-capable models absent from them fall into these groups, each documented in a linked concept rather than re-numbered here:

- **Closed-set COCO but larger than M:** MaskDINO-R50 (`46.3` mask AP / `242` ms*) and MambaVision's Cascade Mask R-CNN results (86–145M params) — see [Hybrid Mamba-Transformer vision backbone](hybrid-mamba-transformer-vision-backbone.md) and table A above.
- **Classic/foundational closed-set:** Mask R-CNN, HTC, and Mask2Former remain the reference instance-segmentation designs — see [Object detection building blocks and speed-up techniques](object-detection-building-blocks-speedup.md).
- **Other YOLO `-seg` variants:** YOLOv5 (limited), YOLOv6, YOLOv7, and YOLOv9 support instance segmentation per the YOLO26 overview but have no compiled COCO mask numbers; only YOLOv8-seg, YOLOv11-seg, and YOLO26-seg do[^reseach-2026-09-17-7].
- **Open-vocabulary / promptable:** YOLO-World-Seg, YOLOE-seg, SAM, SAM 2/2.1, and SAM 3 — see [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md).
- **Video instance segmentation:** SAM 2.1, SAM 3, CAVIS, TAR, MinVIS, DVIS++, GenVIS, and AutoQ-VIS — see [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md).
- **Semantic or panoptic only (not instance):** DINOv3/`dino.txt` open-vocabulary semantic segmentation, UPerNet, MambaVision ADE20K, and YOLO26's semantic/depth claims — the docs ship `yolo26*-sem` as a separate five-scale task family (Cityscapes mIoU, not instance masks), distinct from `yolo26*-seg`[^ultralytics-yolo26-doc-9f4ac453-2] — see [Vision foundation models for detection](vision-foundation-models-for-detection.md).
- **Specialist fine-tuning path with a non-COCO benchmark:** D-FINE-SEG, measured on TACO rather than COCO `val2017`[^dfine-seg-2602-23043-v1-1].

## Open-vocabulary and promptable segmentation

- **Reported:** YOLOE unifies text-prompt, visual-prompt, and prompt-free detection plus segmentation in one YOLO-based real-time model; the segmentation head is YOLACT-style (prototypes plus mask coefficients), and text embeddings are re-parameterized into the last convolution so inference matches native YOLO with zero text-encoder overhead[^yoloe-2503-07465-v2-1].
- **Reported:** LVIS-val zero-shot segmentation AP^m (text/visual): YOLOE-v8-S `17.7`/`16.8`, M `20.8`/`20.3`, L `23.5`/`22.0`, above LVIS-Base fine-tuned YOLO-Worldv2-M/L by 3.0/3.7 AP^m at M/L[^yoloe-2503-07465-v2-2].
- **Reported:** the YOLO26 generation ships YOLOE-26, an open-vocabulary detection-plus-segmentation variant that keeps the optional NMS-free end-to-end head so text-, visual-, and prompt-free segmentation stays real-time; YOLOE-26x reports LVIS-minival `40.6`/`38.5`/`31.1` AP for text/visual/prompt-free prompting, which its end-to-end head trails by `1.1`/`2.3`/`1.2` AP[^ultralytics-yolo26-doc-9f4ac453-3]. Per-scale tables and prompt-free variants are compiled in [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md).
- **Reported:** SAM 3 Promptable Concept Segmentation takes a noun phrase, image exemplars, or both and returns instance plus semantic masks for every matching instance with identities across video; zero-shot image results include LVIS mask AP `48.5` (versus `38.5` DINO-X) and COCO box AP `56.4`[^sam3-2511-16719-v2-3].
- **Reported:** SAM 3 is ~850M params (~450M vision, ~300M text, ~100M detector/tracker) with H200 latency of 30 ms per image at 100+ objects; video cost scales with object count unless Object Multiplex buckets memory[^sam3-2511-16719-v2-4].
- **Synthesis:** "fast open-vocabulary segmentation" and "best open-vocabulary segmentation" are currently different models: YOLOE-Seg is the deployable real-time point, SAM 3 is the quality ceiling at foundation-model cost.

## Video instance segmentation

- **Reported:** SAM 2 uses a once-per-frame Hiera encoder plus FIFO memory bank and object pointers; Hiera-B+/L reach MOSE-val `76.6`/`77.9` and DAVIS17-val `90.2`/`90.7` at `43.8`/`30.2` FPS (A100, batch 1)[^sam2-2408-00714-v2-5].
- **Reported:** TAR (ICCV 2025) profiles online VIS at ~45% encoder, ~52% decoder, ~3% tracker, then skips redundant decoder layers per query with a synchronizer plus router: ResNet-50 TAR+MinVIS rises `24.7`→`34.6` FPS (YTVIS19 `47.4`→`48.4` AP) and TAR+DVIS++ `22.4`→`32.8` FPS; the headline number assumes FlashAttention-2 plus operator fusion on top of routing[^tar-iccv2025-cheng-6].
- **Reported:** SAM 3 couples the concept detector with a SAM-2-style tracker and reports VOS J&F MOSEv1 `78.4`, DAVIS17 `92.2`, SA-V val `83.5`, with interactive SA-37 at `43.5` FPS; Object Multiplex changes multi-object cost from O(N) to O(ceil(N/M)) with ~5.2x throughput at 128 objects[^sam3-2511-16719-v2-5].
- **Synthesis:** for video, prefer `once-per-frame encoder + memory/tracker` over per-frame independent image segmentation, and add temporal decoder routing when the transformer decoder dominates runtime.

## Specialist fine-tuning path

- **Reported:** D-FINE-SEG extends D-FINE with a PAN-only mask head, ROI-cropped mask losses, full-map matching cost, and a reproducible ONNX/TensorRT/OpenVINO train-export-infer pipeline; on its TACO protocol it reports roughly 65% mean relative segmentation-F1 gain over YOLO26-seg at about 10% latency overhead[^dfine-seg-2602-23043-v1-1].
- **Synthesis:** treat the D-FINE-SEG versus YOLO26 gap as conditional on its own TACO dataset, 50-versus-100-epoch schedule, fixed thresholds, and from-scratch mask head; it is evidence for a workflow, not a universal ranking[^dfine-seg-2602-23043-v1-1].

## Relationships

- Uses [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) for the closed-set detector machinery shared with segmentation heads.
- Uses [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md) for YOLOE and SAM 3 concept prompting.
- Uses [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) for RF-DETR-Seg, SAM 2 streaming memory, TAR routing, and edge export details.
- Uses [Vision foundation models for detection](vision-foundation-models-for-detection.md) for DINOv2/DINOv3 pretraining that backs RF-DETR-Seg.
- Parallels [Realtime N-S-M detector selection](realtime-s-m-detector-selection.md), which covers closed-set box detection only.

## Contradictions

- No direct contradiction found. Cross-vendor mask AP and latency use different input sizes, TensorRT/FP16 setups, thresholds, and protocols; treat small gaps as non-decisive without a shared benchmark[^reseach-2026-09-17-7].
- Closed-set mask AP (COCO), open-vocabulary mask AP (LVIS), and video metrics (J&F, mAP, pHOTA) are not comparable; the decision matrix separates them for this reason[^sam3-2511-16719-v2-3].

## Coverage limits

- All AP, FPS, latency, and parameter figures are **reported**, not reproduced; no code was executed.
- The selection is compiled from [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md), [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md), [Vision foundation models for detection](vision-foundation-models-for-detection.md), and their primary raw sources; no new raw inspection was performed for this synthesis[^rfdetr-2511-09554-v2-1].
- Source claims cover to 17/09/2026; newer preprints may change the closed-set and video recommendations, and absolute completeness is infeasible[^reseach-2026-09-17-7].
- Preference statements are **synthesis** from the cited reported numbers and their stated protocols, not independently verified measurements.
- **Observed** by static inspection: `raw/yolo26.md` (SHA-256 `9f4ac453…`) was fully read for its segmentation-relevant sections. No model, weight, or example was downloaded or executed; the linked paper `arXiv:2606.03748`, task guides, images, and video were not fetched, so its metrics remain vendor-reported[^ultralytics-yolo26-doc-9f4ac453-1].
- **Observed** by static inspection: `raw/yolo27.md` (SHA-256 `52318137…`, 305 lines) was fully read for the segmentation table, two-architecture scope, and unreleased status. No model, weight, or example was downloaded or executed, and the YOLO27 waitlist and task guides were not fetched, so YOLO27-seg values are vendor-preliminary reports on a third benchmark protocol.

[^rfdetr-2511-09554-v2-1]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Sec. Real-Time Instance Segmentation plus Fig. `fig:arch` — shared upsampled map, pixel-embedding projector, per-layer query dot product, no multi-scale backbone features, SAM2 pseudo-label O365 pretraining.
[^rfdetr-2511-09554-v2-2]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Tab. `tab:coco_seg` plus `supplement.tex` Tab. `tab:coco_seg_scale` — Seg-N `40.3`/`33.6M`/`50.0` GFLOPs/`3.4` ms through Seg-Max `50.5`/`95.6` ms.
[^yolo26-2509-25164-v5-4]: `raw/arXiv-2509.25164v5/template.tex`, Tab. `tab:yolo26_metrics` segmentation panel plus Sec. Real-Time Deployment / Flexible Export / Quantization — N-seg `39.6`/`33.9` at 53.3 ms CPU / 2.1 ms T4 through X-seg `56.5`/`47.0` at 787.0 ms / 16.4 ms, ONNX/TensorRT/CoreML/TFLite/OpenVINO and FP16/INT8 claims.
[^yoloe-2503-07465-v2-1]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Methodology Model Architecture plus Sec. Re-parameterizable Region-Text Alignment — YOLACT-style prototypes plus mask coefficients, `Label = O·P^T`, and RepRTA last-convolution re-parameterization.
[^yoloe-2503-07465-v2-2]: `raw/arXiv-2503.07465v2/camera_ready.tex`, Sec. Text and Visual Prompt Evaluation Tab. Segmentation evaluation on LVIS — zero-shot LVIS-val AP^m text/visual for v8-S/M/L and the YOLO-Worldv2 comparison.
[^sam3-2511-16719-v2-3]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Promptable Concept Segmentation plus Sec. Experiments Image PCS with Text (LVIS mask AP, COCO box AP, SA-Co metric table) and Appendix Limitations; Introduction for the 30 ms H200 latency.
[^sam3-2511-16719-v2-4]: `raw/arXiv-2511.16719v2/main.tex`, Sec. Model Tracker and Video Architecture plus Introduction — ~850M parameter budget and per-image 30 ms H200 timing; Appendix Limitations for linear video cost and Object Multiplex.
[^sam2-2408-00714-v2-5]: `raw/arXiv-2408.00714v2/sam2.1_arxiv.tex`, Sec. Comparison to state-of-the-art in semi-supervised VOS plus `tab/tab-mask2masklet-results-oss.tex` — Hiera-B+/L MOSE/DAVIS17 J&F at 43.8/30.2 FPS A100 batch-1.
[^tar-iccv2025-cheng-6]: `raw/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper.md`, Secs. 1/4.1-4.3 Tabs. 1 and 3 — MinVIS 45%/52%/3% time split, TAR FPS/AP deltas, FlashAttention-2 plus op-fusion additive gains.
[^dfine-seg-2602-23043-v1-1]: `raw/2602.23043v1/2602.23043v1.md`, Secs. 3-6 Tabs. 1-5 — PAN-only mask head, ROI-cropped losses and full-map matcher cost, TACO protocol, and the ~65% segmentation-F1 / ~10% latency summary against YOLO26-seg.
[^ultralytics-yolo26-doc-9f4ac453-1]: `raw/yolo26.md`, sections “Key Features” / Instance Segmentation Enhancements, “Performance Metrics” / Segmentation (COCO), and “FAQ” — semantic segmentation loss plus upgraded multi-scale proto module, the up to +2.5 box AP / +3.7 mask AP over YOLO11 claim, the n–x-seg box/mask e2e table, and the TensorRT/ONNX/CoreML/LiteRT/OpenVINO export list.
[^ultralytics-yolo26-doc-9f4ac453-2]: `raw/yolo26.md`, sections “Supported Tasks and Modes” and “Performance Metrics” / Semantic Segmentation (Cityscapes) — `yolo26*-seg` and `yolo26*-sem` listed as separate five-scale tasks with train/val/infer/export support.
[^ultralytics-yolo26-doc-9f4ac453-3]: `raw/yolo26.md`, section “YOLOE-26: Open-Vocabulary Detection and Segmentation” — open-vocabulary detection plus segmentation via text/visual/prompt-free modes, optional e2e head, LVIS-minival 40.6/38.5/31.1 AP non-e2e and 1.1/2.3/1.2 AP e2e deltas.
[^ultralytics-yolo27-doc-52318137-1]: `raw/yolo27.md`, sections “Supported Tasks and Modes,” “Performance Metrics” / Segmentation (COCO), and the two-architecture note — seven-task N/S/M/L matrix, CNN-only segmentation path, and preliminary YOLO27n/s/m/l-seg 640 px box/mask AP with params, FLOPs, AMD EPYC 9655 ONNX FP32, and RTX PRO 6000 TensorRT 11 FP16 latency.
[^ultralytics-yolo27-doc-52318137-2]: `raw/yolo27.md`, intro info callout and FAQ “When will YOLO27 be available?” — unreleased weights, configurations, and implementation code with no launch date, and benchmarks that may change before release.
[^sam3-2511-16719-v2-5]: `raw/arXiv-2511.16719v2/main.tex`, video object segmentation and interactive promptable-visual-segmentation results tables — MOSEv1 `78.4`, DAVIS17 `92.2`, and SA-V val `83.5` J&F with interactive SA-37 at `43.5` FPS; plus `multiplex.tex` for Object Multiplex bucketed memory and multi-object throughput scaling.
[^reseach-2026-09-17-7]: `raw/reseach.md`, section “7. Instance segmentation không còn là một nhánh riêng” — Roboflow-protocol Seg-N `40.3`/`3.4` ms and Seg-2XL `49.9`/`21.8` ms versus YOLO26-X-Seg `46.8`/`12.92` ms, with the non-independent-benchmark caveat and weekly-preprint incompleteness.
