---
type: Concept
title: "Axis Model Zoo model files: inventory, duplication, link types and licensing"
description: "The 17 binary models in axis-model-zoo/models, their formats and which README rows they serve, the 80 MB of copied duplicates under the benchmark app, remote link types (Coral, S3, local), and the Apache-2.0 versus AGPL-3.0 licence split for YOLO models."
tags: [edge-ai, axis, model-zoo, models, tflite, licensing, agpl, artpec, cv25, cv75]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:10:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-models
    resource: ../raw/axis-model-zoo/models/
    scope: ../raw/axis-model-zoo/
    kind: dataset
    revision: "v1.0.7-42-g66bf5ea"
    title: "models/ — 17 committed binary model files"
  - id: mz-app-models
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/larod-test/app/models/
    scope: ../raw/axis-model-zoo/
    kind: dataset
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod-test/app/models/ — 19 files per SoC (benchmark input)"
  - id: mz-app-license
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/larod-test/app/LICENSE
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "larod-test app LICENSE (Apache-2.0 text plus AGPL-3.0 text)"
  - id: mz-af-readme
    resource: ../raw/axis-model-zoo/scripts/auto-test-framework/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea"
    title: "auto-test-framework README (how to add models)"
---

# Axis Model Zoo model files: inventory, duplication, link types and licensing

The repository ships real model binaries (no Git LFS, no `.gitattributes`; every `.tflite` starts with the `TFL3` magic, the `.bin` files are vendor-compiled graphs).[^mz-models] They sit in two places: the root `models/` directory (17 files, 101,226,138 bytes ≈ 96.6 MiB) and the benchmark app's per-SoC folders (19 files ≈ 119.1 MiB), which duplicate 13 of the root files **as independent copies**.[^mz-app-models] Context: [Axis Model Zoo repository](axis-model-zoo-repository.md); numbers per row in [benchmark results](axis-model-zoo-benchmark-results.md). All inventory findings below are **Observed** (listing, sizes, SHA-256, header strings); no model was parsed or run.

## Root `models/` inventory

| File | Bytes | Format / target | Served README rows |
| --- | --- | --- | --- |
| `mobilenet_v2_1.0_224_quant.tflite` | 3,610,798 | TFLite uint8, DLPU | MobileNetV2 TF1 on ARTPEC-8 (two cameras) and ARTPEC-9 |
| `mobilenet_v2_1.0_224_quant_edgetpu.tflite` | 4,283,046 | Edge TPU compiled | ARTPEC-7 MobileNetV2 TF1 |
| `tf2_mobilenet_v2_1.0_224_ptq_edgetpu.tflite` | 4,430,486 | Edge TPU compiled | ARTPEC-7 MobileNetV2 TF2 |
| `tf2_mobilenet_v3_edgetpu_1.0_224_ptq_edgetpu.tflite` | 5,270,166 | Edge TPU compiled | ARTPEC-7 MobileNetV3 |
| `ssd_mobilenet_v2_coco_quant_postprocess.tflite` / `_edgetpu` | 6,220,797 / 6,911,677 | detector with post-process op | SSD MobileNet v2 (ARTPEC-8/-9 / ARTPEC-7) |
| `ssdlite_mobiledet_coco_qat_postprocess.tflite` / `_edgetpu` | 4,330,856 / 5,395,936 | detector with post-process op | SSDLite MobileDet (ARTPEC-8/-9 / ARTPEC-7) |
| `yolov5n.tflite`, `yolov5s.tflite`, `yolov5m.tflite` | 2,117,296 / 7,631,216 / 21,330,744 | ARTPEC-8 YOLOv5 exports | YOLOv5n/s/m on ARTPEC-8 |
| `mobilenetv2_cavalry.bin`, `EfficientNet-lite0.bin` | 3,685,496 / 4,897,444 | CV25 (Ambarella CVflow) | CV25 MobileNetV2, EfficientNet-Lite0 |
| `cv25_yolov5s.bin` | 7,417,032 | CV25 detector | YOLOv5s-CV25 (linked locally) |
| `cv75_mobilenetv2.bin`, `cv75_efficientnet-lite2-int8.bin`, `cv75_yolov8n_det.bin` | 3,753,776 / 6,595,048 / 3,344,324 | CV75 | the three CV75 rows (linked locally) |

## Duplication and what is missing from `models/`

- 13 of 17 root files are byte-identical to files under `larod-test/app/models/` (`artpec7/`, `artpec8/`, `cv25/`); the ARTPEC-8 TF1 SSD/MobileNet files are also copied into `artpec9/`. About 80.1 MB is therefore stored twice. The auto-test README tells contributors to create a "hard symbolic link", but the tree holds regular copies (git cannot store hard links).[^mz-af-readme]
- **ARTPEC-9 YOLOv5 files exist only in the benchmark app** (`artpec9/A9-yolov5n|s|m.tflite`, 1,964,168 / 7,336,376 / 21,329,048 bytes). They differ from the ARTPEC-8 files in size, consistent with the guide's different export flags.[^mz-app-models] The README links these rows to S3 URLs, so whether the S3 bytes equal the benchmarked bytes is **Unverified**.
- `cv25_yolov5s.bin` and the three `cv75_*.bin` files have no counterpart in the benchmark app (no `cv75/` folder at all).
- `EfficientNet-S.bin` is the only file ever deleted from `models/`, so file names are not stable identifiers.[^mz-models]

## Link types used in the README tables

| Link type | Rows | Notes |
| --- | --- | --- |
| Coral `google-coral/test_data` raw GitHub URL | 13 | all ARTPEC-7 Coral models, ARTPEC-8/-9 MobileNetV2 and SSD rows |
| S3 `acap-ml-models` bucket (model and, for YOLOv5, `.pt` checkpoint) | 8 | CV25 MobileNetV2/EfficientNet-Lite0 and all six ARTPEC-8/-9 YOLOv5 rows |
| Local `./models/…` | 4 | CV25 YOLOv5s and the three CV75 rows; no checkpoint offered |

Thirteen of the 17 root files are not linked by any README row; they exist as benchmark inputs, while the matching table rows link remote copies.[^mz-readme] Checkpoints (`ckpt`) are linked for TensorFlow/EfficientNet/YOLOv5 rows and absent for the local CV rows and the Coral detectors. Naming drifts between rows ("MobilenetV2", "SSD MobileNet v2", "SSD MobilenetV2", "Yolov5n-Artpec8", "Yolov8n_det-CV75"), so string joins from README rows to file names need manual mapping.

## Platform to larod backend and model folder

| README platform | larod device | Folder in the benchmark app |
| --- | --- | --- |
| ARTPEC-7 | `google-edge-tpu-tflite` | `artpec7/` (`*_edgetpu.tflite`) |
| ARTPEC-8 | `axis-a8-dlpu-tflite` | `artpec8/` |
| ARTPEC-9 | `a9-dlpu-tflite` | `artpec9/` |
| CV25 | `ambarella-cvflow` | `cv25/` |
| CV75 | — | none |

(Mapping is from the on-device script; see [speed pipeline](axis-model-zoo-speed-benchmark-pipeline.md).)

## Licensing

- **Repository code and docs:** Apache-2.0.
- **YOLOv5 / YOLOv8 model files:** "licensed under AGPL-3.0-only" to follow the Ultralytics licence; the licence text is hosted on S3 (`YOLOv5_LICENSE.txt`) rather than in the repository (**Reported**, remote text not fetched).[^mz-readme]
- The benchmark app's `LICENSE` file is **873 lines: Apache-2.0 text followed by the full AGPL-3.0 text** (from about line 213), added when YOLOv5 models were included; the app's `README` licence section still says only "Apache License 2.0" (**Observed**).[^mz-app-license]
- The accuracy app's `LICENSE` has no AGPL text, consistent with it shipping no YOLO models (**Observed**; see [accuracy harness](axis-model-zoo-accuracy-test-harness.md)).
- Practical reading (**Synthesis**, not legal advice): treat the YOLO artefacts as AGPL-3.0 and the Coral/TensorFlow-derived models under their own upstream licences, which this repository does not restate.

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md).
- **Rows and metrics:** [benchmark results](axis-model-zoo-benchmark-results.md).
- **How the YOLOv5 files are produced:** [YOLOv5 guide](axis-model-zoo-yolov5-training-guide.md).
- **Format constraints:** [Axis DLPU](axis-dlpu.md), [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md), [CV75 ONNX conversion](axis-cv75-onnx-conversion.md).

[^mz-readme]: `README.md` §Models tables (link columns), the `[!NOTE]` licensing block after the detection table.
[^mz-models]: `models/` directory listing, sizes and SHA-256; `git check-attr` (no attributes), `.gitattributes` absent; `git log` (`Delete EfficientNet-S.bin`); file headers (`TFL3`, `*_prim_split_*` strings).
[^mz-app-models]: `scripts/auto-test-framework/larod-test/app/models/{artpec7,artpec8,artpec9,cv25}/` listing; SHA-256 comparison against `models/`.
[^mz-app-license]: `scripts/auto-test-framework/larod-test/app/LICENSE` (873 lines; AGPL-3.0 text begins near line 213).
[^mz-af-readme]: `scripts/auto-test-framework/README.md` steps 1–4 ("Create a hard symbolic link … (to be improved)").
