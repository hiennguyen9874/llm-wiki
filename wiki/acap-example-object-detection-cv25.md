---
type: Concept
title: "ACAP example: object detection on Ambarella CV25 with JPEG crops"
description: "How object-detection-cv25 runs SSD MobileNet v2 on the CV25 CVFlow DLPU with software box decoding, anchor boxes and NMS, saves JPEG crops from a second HD stream, and the threshold-truncation and shutdown defects in its code."
tags: [edge-ai, axis, acap, examples, cv25, larod, object-detection]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP example: object detection on Ambarella CV25 with JPEG crops

`object-detection-cv25` is the CV25-only detector. Unlike the other [Larod examples](acap-example-larod-object-detection.md), it decodes SSD MobileNet v2 outputs in software (CV25 provides no box postprocessing), uses a second high-resolution VDO stream, and writes each accepted detection as a JPEG crop to `/tmp/detection_<i>.jpg` instead of drawing boxes.[^native-examples] It shares no code with the other three inference examples: it has its own `imgprovider.c`, `imgutils.c` and `postprocessing.c`, the older Larod API (`larodCreateModelInputs/Outputs` with `-DLAROD_API_VERSION_3`), temp-file `mmap` tensors and libjpeg-turbo.

## Model and flow

- **Model:** `ssd_mobilenet_v2_cv25_coco_300.bin` plus `ssd_mobilenet_v2_cv25_coco_300_anchor_boxes.bin` and `coco_labels.txt`, downloaded in the Dockerfile from `acap-ml-models.s3.amazonaws.com/ssd_mobilenet`. CV25 needs width in multiples of 32, so the 300-pixel input is padded by 20 to 320; outputs are hard-coded as 1917 boxes (×4 floats) and 1917×91 class scores.
- **Device:** only `ambarella-cvflow` is accepted; any other device exits with "supports only cv25 device".
- **Preprocessing:** two `cpu-proc` models: standard-definition `nv12` to `rgb-planar` 300x300 with a centred crop map, and high-definition `nv12` to `rgb-interleaved` for crops. Padding is applied in software (`padImageWidth`).
- **Postprocessing (`postprocessing.c`):** `loadDetectionStruct` reads offsets and anchors and takes the argmax class; `applyAnchors` decodes with scales y=10, x=10, h=5, w=5 and clamps to [0,1]; `suppressLowScoreBoxes`; quicksort by score and O(N²) per-class IoU NMS; label index offset by −1, background filtered.
- **Defaults:** the manifest passes the positional values `300 300 20 80 640 360 70 91 1917` (the README names them; the individual meanings were not mapped one by one here, beyond input size 300x300, padding 20 and the 1917 and 91 output dimensions); the argument parser accepts only positive integers, so a padding or threshold of zero cannot be requested.
- **Build:** aarch64 default; the CI matrix passes no build args.[^native-examples]

## Observed defects

- `int confidenceThreshold = threshold / 100.0;` and `int iouThreshold = 0.5;` (`object_detection.c:961-962`, re-verified) truncate to `0`, so low-score suppression does nothing and NMS suppresses any overlapping same-class box (IoU > 0) instead of 0.5. Only the final per-object `score >= threshold/100.0` filter is correct. The README snippet shows the float expression.
- `while (true)` never checks `stopRunning`, so the graceful shutdown path and the post-loop stream-stop block are unreachable and the process exits `EXIT_FAILURE`.
- HD crop arithmetic assumes 16:9 and `crop_interleaved` does not clamp, so an out-of-range box reads past the mapped buffer; the final `munmap` length is smaller than the padded allocation.
- README package names disagree (`object_detection_app_1_0_0_cv25.eap` vs `object_detection_cv25_1_0_0_aarch64.eap`); it says the model is converted with the Ambarella toolchain while the Dockerfile only downloads a prebuilt `.bin`; `<signal.h>` is not included.[^native-examples]

Evidence class: **Observed** (static); the threshold truncation was re-checked directly in the source.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Sibling of** [Larod inference examples](acap-example-larod-object-detection.md); the CV25 model-conversion procedure is in [training guides](acap-example-model-training-guides.md) (the `tensorflow-to-larod-cv25` pipeline produces a different model).
- **Uses** `ambarella-cvflow`; chip context in [generations, chip architectures and compatibility](acap-chip-architecture-and-sdk-compatibility.md).

[^native-examples]: `object-detection-cv25/Dockerfile`; `object-detection-cv25/app/object_detection.c` (device check, `larodCreateModelInputs`, `padImageWidth`, lines 961–962 for thresholds, `while (true)` loop and cleanup); `object-detection-cv25/app/postprocessing.c::loadDetectionStruct, applyAnchors, suppressOverlappingBoxes`; `object-detection-cv25/app/imgutils.c::crop_interleaved`; `object-detection-cv25/app/manifest.json.cv25`; `object-detection-cv25/README.md` §"Designing the application"; `.github/workflows/object-detection-cv25.yml`.
