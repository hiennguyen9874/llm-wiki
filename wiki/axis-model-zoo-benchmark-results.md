---
type: Concept
title: "Axis Model Zoo benchmark results: speed and accuracy per chip, with provenance"
description: "Normalised classification and detection tables from the Axis Model Zoo README (AXIS OS 12.11.72), derived speed ratios across ARTPEC-7/8/9, CV25 and CV75, and the provenance and comparability limits of every speed and accuracy figure."
tags: [edge-ai, axis, model-zoo, benchmark, artpec, cv25, cv75, yolov5, mobilenet]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:05:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-readme-update
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/readme_update.py
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "readme_update.py — speed-cell rewriter"
---

# Axis Model Zoo benchmark results: speed and accuracy per chip, with provenance

The README's two tables give, per platform and reference camera, a model's mean inference time (ms) and a quality metric (Top-1/Top-5 for classification, mAP for detection), all stamped "Values for AXIS OS 12.11.72".[^mz-readme] This page normalises them (all numbers **Reported** by the README unless stated) and records how far each can be trusted. Repository context: [Axis Model Zoo repository](axis-model-zoo-repository.md).

## Image classification (speed ms · Top-1 / Top-5 %)

| Platform (device) | MobileNetV2 (TF1) | MobileNetV2 (TF2) | MobileNetV3 (TF2) | EfficientNet-Lite0 | EfficientNet-Lite2 |
| --- | --- | --- | --- | --- | --- |
| ARTPEC-7 (Q1615 Mk III) | 4.42 · 68.9 / 88.2 | 4.58 · 69.6 / 89.1 | 4.76 · 72.7 / 91.1 | — | — |
| ARTPEC-8 (P1465-LE) | 9.89 · 68.8 / 88.9 | — | — | — | — |
| ARTPEC-8 (Q1656-LE) | 5.36 · 68.8 / 88.9 | — | — | — | — |
| ARTPEC-9 (Q1728) | 2.02 · 69.1 / 89.0 | — | — | — | — |
| CV25 (M3085-V) | 5.35 · 66.8 / 87.2 | — | — | 6.86 · 71.2 / 90.3 | — |
| CV75 (M2048-LE) | 2.98 · 67.2 / 89.2 | — | — | — | 6.96 · 72.6 / 91.4 |

## Object detection (speed ms · mAP %)

| Platform (device) | SSD MobileNet v2 | SSDLite MobileDet | YOLOv5n | YOLOv5s | YOLOv5m | Other |
| --- | --- | --- | --- | --- | --- | --- |
| ARTPEC-7 (Q1615 Mk III) | 18.07 · 25.6 | 34.17 · 32.9 | — | — | — | — |
| ARTPEC-8 (P1465-LE) | 28.14 · 25.6 | 38.53 · 32.9 | 100.07 · 23.5 | — | — | — |
| ARTPEC-8 (Q1656-LE) | 17.84 · 25.6 | 28.19 · 32.9 | 55.57 · 23.5 | 69.97 · 32.3 | 95.65 · 37.9 | — |
| ARTPEC-9 (Q1728) | 10.48 · 25.6 | 21.48 · 32.9 | 31.85 · 23.3 | 35.00 · 32.2 | 42.70 · 38.1 | — |
| CV25 (M3085-V) | — | — | — | 128.36 · 37.0 | — | — |
| CV75 (M2048-LE) | — | — | — | — | — | YOLOv8n_det 11.48 · 37.3 |

The YOLOv5 rows are named "-Artpec8" / "-Artpec9": they are **different trained and quantised artefacts**, so cross-generation mAP differences (23.5 vs 23.3, 32.3 vs 32.2, 37.9 vs 38.1) are model effects, not device effects.[^mz-readme] (The documented export difference is `--per-tensor` for ARTPEC-8 only; see [YOLOv5 guide](axis-model-zoo-yolov5-training-guide.md).)

## Derived observations (Synthesis from the tables, ratios computed from the cited rows)

- **Same SoC, different camera.** P1465-LE and Q1656-LE both run ARTPEC-8 and the same model bytes, yet P1465-LE is 1.85× slower on MobileNetV2, 1.58× on SSD MobileNet v2, 1.37× on SSDLite MobileDet and 1.80× on YOLOv5n. The README does not explain the gap; treat reference *device*, not only SoC, as a variable.[^mz-readme]
- **ARTPEC-8 → ARTPEC-9 (Q1656-LE → Q1728).** Speed-up: MobileNetV2 2.65×, SSD MobileNet v2 1.70×, SSDLite 1.31×, YOLOv5n 1.75×, YOLOv5s 2.00×, YOLOv5m 2.24×. The gain grows with model size, suggesting small graphs are dominated by fixed overhead.
- **YOLOv5 n→s→m cost.** ARTPEC-8 (Q1656-LE): 55.57 → 69.97 → 95.65 ms (s/n 1.26×, m/s 1.37×). ARTPEC-9: 31.85 → 35.00 → 42.70 ms (s/n 1.10×, m/s 1.22×). On ARTPEC-9, YOLOv5s gives +8.9 mAP for about +10 % latency.
- **ARTPEC-7 vs ARTPEC-8 classification** is not like-for-like: ARTPEC-7 runs Coral-compiled `*_edgetpu.tflite` models on the Edge TPU backend, ARTPEC-8 runs plain `.tflite` on the DLPU, so the ARTPEC-7 MobileNetV2 (4.42 ms) beating ARTPEC-8 Q1656-LE (5.36 ms) is not a silicon comparison.
- **CV family.** CV75 MobileNetV2 is 1.80× faster than CV25 (2.98 vs 5.35 ms); CV75 YOLOv8n_det (11.48 ms, mAP 37.3) is 8.3× faster than Q1656-LE YOLOv5m (95.65 ms, mAP 37.9) at near-equal mAP; CV25 YOLOv5s is the slowest detector (128.36 ms) though its mAP (37.0) exceeds the ARTPEC YOLOv5s rows, again a different artefact.
- **Accuracy noise floor.** The byte-identical `mobilenet_v2_1.0_224_quant.tflite` reports Top-1 68.8 on both ARTPEC-8 cameras but 69.1 on ARTPEC-9, so on-camera accuracy is not bit-exact across DLPU generations; differences under about 0.5 percentage points should not be read as model differences.

## Provenance of the figures

| Metric | Source | Evidence class |
| --- | --- | --- |
| Speed, 23 rows | Automated manual-dispatch workflow: `larod-client -R 1000 -w 5 -p` mean job time, written into the README by `readme_update.py` ([speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md))[^mz-readme-update] | **Reported**; mechanism **Observed** |
| Speed, 4 rows (CV25 YOLOv5s, CV75 EfficientNet-Lite2, MobileNetV2, YOLOv8n_det) | Cells carry marker comments but no token in the updater and no CV75 device in the workflow, so they are hand-maintained[^mz-readme-update] | **Observed** gap; origin unverified |
| Classification accuracy, MobileNetV2 | On-camera ACAP ([accuracy harness](axis-model-zoo-accuracy-test-harness.md)); never re-run per OS release[^mz-readme] | **Reported** |
| Classification accuracy, MobileNetV3, EfficientNet-Lite0/Lite2, CV75 MobileNetV2 | No manifest or model for them in the harness; no in-repo reproduction path | **Unverified** |
| Detection mAP, SSD MobileNet v2 and SSDLite MobileDet | Copied from Coral's published results (identical 25.6 / 32.9 on every platform), never measured on an Axis camera[^mz-readme] | **Reported** |
| Detection mAP, Axis YOLOv5 | "Evaluate the model accuracy" step of the YOLOv5 guide, an optional step with no dataset pinned[^mz-readme] | **Reported**; dataset **Unverified** |
| Detection mAP, YOLOv5s-CV25 and YOLOv8n_det-CV75 | Not covered by the README's stated provenance (Coral or YOLOv5 guide) | **Unverified** |

## Limits when using the numbers

- A single AXIS OS version stamp covers every row, but the speed refresh is a manual run; whether a newer release has shipped since 12.11.72 was not checked.[^mz-readme]
- The README's "mAP" is undefined. Git history of the YOLOv5 guide shows an older table whose 0.235 value for YOLOv5n equals the README's 23.5 %, so the YOLOv5 figures are plausibly mAP@0.5:0.95 (**Synthesis**).
- The mean-of-1000 timing has no variance, percentile, firmware, temperature or `larod-client` version recorded, and measures pure model execution on random input, not a camera pipeline.
- Models are "off-the-shelf, not production quality"; the "TF version" column of the classification table has no defined meaning for vendor-compiled `.bin` graphs (CV25/CV75).[^mz-readme]

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md).
- **Produced by:** [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md) and [accuracy harness](axis-model-zoo-accuracy-test-harness.md).
- **Model files behind the rows:** [model files and licensing](axis-model-zoo-model-files-and-licensing.md).
- **Explains chip differences:** [Axis DLPU](axis-dlpu.md), [DLPU model constraints](axis-dlpu-model-constraints.md).

[^mz-readme]: `README.md` §Image classification (rows for ARTPEC-7/-8/-9, CV25, CV75), §Object detection (17 rows), the "Values for AXIS OS 12.11.72" line, §Speed measure, §Accuracy measure; the `<!--token-->` cell markers.
[^mz-readme-update]: `scripts/auto-test-framework/readme_update.py::tokens`, `::token_parameters` (23 entries; no `cv75_*` or `cv25_yolov5s`), `::main` ("Can't find token in file" path).
