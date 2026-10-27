---
type: Concept
title: "Axis Model Zoo YOLOv5 guide: train, export, evaluate and deploy on ARTPEC-8 and ARTPEC-9"
description: "The docs/yolov5.md procedure: pin Ultralytics YOLOv5, apply the SoC-specific Axis patch, train, export int8 TFLite (--per-tensor only for ARTPEC-8), evaluate and deploy through the object-detection-yolov5 example, with licensing and the gaps the guide leaves open."
tags: [edge-ai, axis, model-zoo, yolov5, training, quantization, artpec-8, artpec-9, tflite]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T08:25:00Z }
stale_after: 2027-04-30
sources:
  - id: mz-readme
    resource: ../raw/axis-model-zoo/README.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (66bf5ea7fc1d14b21e2e0d67db5205f02528e6f8, 2026-10-09)"
    title: "AxisCommunications/axis-model-zoo — README (git checkout)"
  - id: mz-yolov5
    resource: ../raw/axis-model-zoo/docs/yolov5.md
    scope: ../raw/axis-model-zoo/
    kind: code
    revision: "v1.0.7-42-g66bf5ea (docs/yolov5.md last changed in 1535c09, 2025-10-10)"
    title: "Run YOLOv5 on ARTPEC-8 and ARTPEC-9"
---

# Axis Model Zoo YOLOv5 guide: train, export, evaluate and deploy on ARTPEC-8 and ARTPEC-9

`docs/yolov5.md` in the [Axis Model Zoo](axis-model-zoo-repository.md) explains how Axis's YOLOv5 models were made and how to produce your own: take upstream Ultralytics YOLOv5 at a pinned commit, apply an Axis **patch** hosted on S3 (one per SoC), train, export an **int8 TFLite** model, optionally validate and time it, then package it into an ACAP.[^mz-yolov5] It states that ARTPEC-8 supports YOLOv5 "starting from AXIS OS 11.7" and that ARTPEC-9 is also supported, with `yolov5n`, `yolov5s` and `yolov5m` the tested sizes; larger ones risk exceeding device memory.[^mz-yolov5] The guide is **Reported**; the commands were not run, and the upstream repository, S3 patches and remote models were not fetched.

## Procedure

| Step | Command or action (from the guide) |
| --- | --- |
| 1. Clone and pin | `git clone https://github.com/ultralytics/yolov5`, `git checkout 95ebf68f92196975e53ebc7e971d0130432ad107`, then `curl -L https://acap-ml-models.s3.amazonaws.com/yolov5/yolov5_artpec8.patch \| git apply` (or `yolov5_artpec9.patch`), `pip install -r requirements.txt`[^mz-yolov5] |
| 2. Train | `python3 train.py --name axis-train --data coco.yaml --epochs 300 --weights '' --cfg yolov5n.yaml --batch-size 128`; use `--weights` to start from a checkpoint, and the Ultralytics custom-data tutorial for your own dataset[^mz-yolov5] |
| 3. Export | ARTPEC-8: `python3 export.py --weights runs/train/axis-train/weights/best.pt --include tflite --int8 --per-tensor`; ARTPEC-9: the same without `--per-tensor`[^mz-yolov5] |
| 4. Evaluate (optional) | `python3 val.py --weights …/best-int8.tflite`; add `--data` for your own dataset[^mz-yolov5] |
| 5. Speed (optional) | Use [model_performance_tester.py](axis-model-zoo-speed-benchmark-pipeline.md) and the developer-site "Test your model" page[^mz-yolov5] |
| 6. Deploy | Use the `object-detection-yolov5` example of `acap-native-sdk-examples`; by default it downloads a pre-trained model, and you can substitute your own model and labels via its Dockerfile parameters[^mz-yolov5] |
| 7. Checkpoints | Pre-trained checkpoints and measurements for n/s/m live in the README tables[^mz-yolov5] |

## ARTPEC-8 versus ARTPEC-9 as documented

| Aspect | ARTPEC-8 | ARTPEC-9 |
| --- | --- | --- |
| Patch | `yolov5_artpec8.patch` | `yolov5_artpec9.patch` |
| Export flags | `--int8 --per-tensor` | `--int8` |
| Reference camera and RAM | Q1656, 2 GB | Q1728, 4 GB |
| README speeds (AXIS OS 12.11.72) | n 55.57 / s 69.97 / m 95.65 ms (Q1656-LE); n 100.07 ms (P1465-LE) | n 31.85 / s 35.00 / m 42.70 ms |
| README mAP | 23.5 / 32.3 / 37.9 | 23.3 / 32.2 / 38.1 |

The `--per-tensor` split matches other material in the wiki: the ARTPEC-8 DLPU uses per-tensor quantisation and per-axis models run significantly slower (see [tensorflow-to-larod training guides](acap-example-model-training-guides.md)), and ARTPEC-9 limits per-channel quantisation to a small operator set ([ARTPEC-9 operator support](axis-artpec-9-operator-support.md)). The exported files differ in size (for example YOLOv5n 2,117,296 vs 1,964,168 bytes), which supports but does not prove different quantisation (**Observed** sizes, **Synthesis** cause; see [model files](axis-model-zoo-model-files-and-licensing.md)).[^mz-readme]

## Licensing

The guide says the Axis patch is licensed AGPL-3.0-only, with the licence text on S3, while the page itself carries the repository's Apache-2.0 licence; the README applies AGPL-3.0-only to the YOLOv5/YOLOv8 model files.[^mz-yolov5][^mz-readme] Anyone redistributing exported models or patched code should check these terms (**Reported**; licence text not fetched).

## What the guide leaves open (Observed by reading; Synthesis where marked)

- **Image size is never mentioned**; the 640 input is only implied by the `_640` model file names and the YOLOv5 default.
- **`--weights ''` trains from scratch**, and the later note to add `--weights` must replace it, not be appended.
- **No int8 calibration data flag** is given for `export.py`, so custom-dataset quantisation would rely on the defaults (**Synthesis**).
- **No environment pinning** (Python, PyTorch, CUDA) and no description of what the patch changes; `curl | git apply` has no dry run.
- **Minimum AXIS OS for ARTPEC-9 is missing**, and the "11.7" ARTPEC-8 claim is unsourced here; the pre-merge ARTPEC-9 guide's "under 2 GB RAM" threshold became "less memory".
- **Deployment gaps:** nothing on larod device strings, packaging the `.tflite` into an `.eap`, or the NMS/dequantisation post-processing, which live in the [Larod examples](acap-example-larod-object-detection.md) (output `Nx(5+C)` uint8 with quantisation scale and zero point).
- **Metric and dataset for the README's accuracy** are not pinned: the evaluation step is optional and names no dataset, although the README cites it as the mAP source ([benchmark results](axis-model-zoo-benchmark-results.md)).
- **Timing tool difference:** the recommended tester omits the warm-up used for the README table.
- **Stale cross-repo links:** other Axis repositories still link to the pre-merge guide names `yolov5-on-artpec8.md` and `yolov5-on-artpec9.md`; the guide was merged and renamed to `docs/yolov5.md` in October 2025.

## Relationships

- **Part of:** [Axis Model Zoo repository](axis-model-zoo-repository.md).
- **Produces the models in:** [model files](axis-model-zoo-model-files-and-licensing.md) and [benchmark results](axis-model-zoo-benchmark-results.md).
- **Constraints:** [Axis DLPU](axis-dlpu.md), [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md).
- **Deployment:** [Larod examples](acap-example-larod-object-detection.md), [Custom model deployment](axis-custom-model-deployment.md).

[^mz-readme]: `README.md` §Object detection (YOLOv5 rows), `[!NOTE]` AGPL block, §Accuracy measure.
[^mz-yolov5]: `docs/yolov5.md` — intro paragraph, §1 clone and patch, §2 training, §3 export, §4 evaluate (Optional), §5 speed, §6 deploy, §7 checkpoints, licence sections; `git log` of `docs/` (`1535c09`, `a8b6a35`, `dff2bea`).
