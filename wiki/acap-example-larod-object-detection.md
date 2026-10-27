---
type: Concept
title: "ACAP examples: Larod inference with vdo-larod, object-detection and YOLOv5"
description: "How vdo-larod, object-detection and object-detection-yolov5 run models on Axis devices: models and download sources, larod device names per chip, VDO preprocessing, postprocessing, arguments and defaults, build per CHIP, shared code, and defects."
tags: [edge-ai, axis, acap, examples, larod, inference, object-detection, yolov5]
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

# ACAP examples: Larod inference with vdo-larod, object-detection and YOLOv5

Three examples share one skeleton for running a model on the device: read frames from VDO, resize or convert them with the `cpu-proc` preprocessing device when needed, run the model through the Larod API on a chip-specific device, and either log scores (`vdo-larod`) or draw boxes with the Bounding Box API (`object-detection`, `object-detection-yolov5`).[^native-examples] The CV25-only detector, which has an independent code lineage, is in [Object detection on CV25](acap-example-object-detection-cv25.md). Models for `vdo-larod` come from the [training guides](acap-example-model-training-guides.md). All three use the SDK image `acap-native-sdk:12.11.0`.

## Comparison

| | `vdo-larod` | `object-detection` | `object-detection-yolov5` |
| --- | --- | --- | --- |
| Task | person/car classifier, log only | SSD MobileNet v2 COCO boxes | YOLOv5n COCO boxes |
| Input | 256x256 | 300x300 | 640x640 (read from model at build time) |
| Chips (manifest per `CHIP`) | artpec8, artpec9, cpu, edgetpu, cv25 | artpec8, artpec9, cpu, edgetpu | artpec8, artpec9, cpu |
| Larod devices | `axis-a8-dlpu-tflite`, `a9-dlpu-tflite`, `cpu-tflite`, `google-edge-tpu-tflite`, `ambarella-cvflow` | same minus CV25 | `axis-a8-dlpu-tflite`, `a9-dlpu-tflite`, `cpu-tflite` |
| Model files | `custom_resnet_{artpec8,edgetpu,cv25}_car_human_256.*` from `acap-ml-models.s3.amazonaws.com/tensorflow_to_larod_resnet` (artpec8 file also for artpec9 and cpu) | `ssd_mobilenet_v2_coco_quant_postprocess[_edgetpu].tflite`, `coco_labels.txt` from Google Coral `test_data` | `yolov5n_artpec{8,9}_coco_640.tflite` from `acap-ml-models.s3.amazonaws.com/yolov5` |
| VDO `image.fit` | `scale` (argv) | `crop` (hard-coded) | `crop` |
| Output handling | two scores, uint8 ÷ 2.55 to percent (float32 on CV25) | 4 tensors (boxes, classes, scores, count), model already NMS'd | one uint8 tensor N×(5+C), dequantize, filter, NMS in app |
| Arguments | device, model, `scale` | model, threshold, labels, `-d` device | model, `-c` device; thresholds via AXParameter |
| Visible result | syslog lines | red thin boxes on stream | red thin boxes on stream |

## Shared pipeline (`vdo-larod/app/*.c`; identical or near-identical in the others)

- **Chip selection:** a `manifest.json.<CHIP>` is copied to `manifest.json` by the Dockerfile (`--build-arg CHIP=…`); its `runOptions` pass the Larod device name, model path and options to the binary, e.g. `a9-dlpu-tflite` for ARTPEC-9. `cpu` and `edgetpu` manifests omit the `deepLearningProcessor` resource. Chip background is in [Axis DLPU](axis-dlpu.md) and [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md).
- **Larod use** (`model.c`): `larodConnect`, device list validation, `larodLoadModel` with private access (retry up to 50 times on `LAROD_ERROR_POWER_NOT_AVAILABLE`), `larodAllocModelInputs/Outputs`, tensors backed by VDO buffers via `larodSetTensorFdProps(MAP|DMABUF)` and `larodConvertVmemFdToDmabuf` for vmem buffers, job requests, synchronous `larodRunJob` only (no async pipelining).
- **Stream choice** (`channel_util.c`): `vdo-larod` requests the model's size (unrotating 90/270) and falls back to YUV; `object-detection` and `-yolov5` pick the smallest resolution at the native aspect ratio that is at least the model size (e.g. 1280x720 for 640x640) then crop; `vdo-larod` pads with black bars when scaling (`crop_map` is `NULL`).
- **Preprocessing** (`model_preprocessing.c`): only when stream and model sizes or formats differ, on device `cpu-proc` (libyuv), `nv12` to `rgb-interleaved`/`rgb-planar`, asserting the output tensor size equals 3·w·h.
- **Frame-rate adaptation** (`img_util.c`, shared): every 10 frames the mean analysis time maps to 30/25/20/15/10/5/1 fps and the stream rate is updated.[^native-examples]

## object-detection specifics

Threshold is `argv[2]/100.0` (float); labels file is required for box drawing; box tensor order is `[y_min, x_min, y_max, x_max]` normalized; drawing uses `bbox_coordinates_frame_normalized`, `bbox_rectangle`, `bbox_commit`. Build: `acap-build . -a 'label/labels.txt' -a 'model/converted_model.tflite'`. Logs `Object %d: Classes: %s - Scores: %f - Locations: [...]`.

## object-detection-yolov5 specifics

- A first Docker stage on TensorFlow 2.21.0 runs `parameter_finder.py` to write `model_params.h` (`MODEL_INPUT_HEIGHT/WIDTH`, `QUANTIZATION_SCALE/ZERO_POINT`, `NUM_CLASSES`=80, `NUM_DETECTIONS`=25200) from the downloaded `.tflite`.
- Parsing in `object_detection_yolov5.c`: `filter_detections` (dequantize element 4 as object likelihood, drop below threshold), pairwise `non_maximum_suppression` with centre-form IoU, argmax class over elements 5..5+C, `find_corners` clamped to [0,1].
- Thresholds are AXParameters `ConfThresholdPercent` (default 25) and `IouThresholdPercent` (default 5), read once at startup and divided by `100.0`; extra manifest keys are `paramConfig` and the Graphics2/Overlay2 D-Bus methods.
- README notes the model is AGPL-3.0-only and warns Apple Silicon users to disable Rosetta. The package is `object_detection_yolov5_<CHIP>_1_0_0_<ARCH>.eap`.[^native-examples]

## Observed defects

- `vdo-larod/app/vdo_larod.c::main` reads `argv[1..3]` before the `argc != 4` check at line 143, so a start without arguments is undefined behaviour; `model.c:38` uses `>` instead of `>=` in a tensor index check; the Makefile needs `jq`, which the Dockerfile does not install.
- CV25 output order is car first, person second, the reverse of the TFLite models (`vdo_larod.c:301-315`).
- `object_detection.c` indexes four output tensors without checking the tensor count and does not bounds-check `labels[...]`; `labelparse.c` writes one byte past its 60-character cap.
- `object-detection-yolov5` uses a 25200-element stack VLA (about 100 KB) and quadratic NMS; its label parser drops `n/a` entries, so label indices shift.
- README edge-TPU text calls it the ARTPEC-7 DLPU while the `edgetpu` manifest declares no DLPU resource.[^native-examples]

All findings are **Observed** from static inspection; no model was downloaded or run.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Uses** VDO ([capture page](acap-example-vdo-video-capture-and-opencl.md)), Larod, Bounding Box ([overlays page](acap-example-overlays-and-bounding-box.md)) and the Parameter API (see [events and parameters](acap-example-events-and-parameters.md)).
- **Depends on** models produced by [training guides](acap-example-model-training-guides.md).
- **Replaces** the container-era [ML inference and object detection examples](acap-cv-example-ml-inference-and-object-detection.md) for native ACAP.
- **Supports** [Deploying a custom AI model to an Axis camera](axis-custom-model-deployment.md).

[^native-examples]: `vdo-larod/Dockerfile`, `vdo-larod/app/{vdo_larod.c,model.c,model_preprocessing.c,channel_util.c,img_util.c,manifest.json.*}`; `object-detection/Dockerfile`, `object-detection/app/{object_detection.c,argparse.c,labelparse.c,channel_util.c}`; `object-detection-yolov5/Dockerfile`, `object-detection-yolov5/app/{object_detection_yolov5.c,parameter_finder.py,manifest.json.*}`, READMEs of all three. argv-check ordering was re-verified at `vdo-larod/app/vdo_larod.c:125-143`.
