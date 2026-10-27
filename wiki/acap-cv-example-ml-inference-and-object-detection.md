---
type: Concept
title: "CV SDK examples: minimal ML inference and object detection"
description: "How minimal-ml-inference and object-detector-python run a quantized SSD MobileNet V2 COCO model through the containerized ACAP Runtime: model image, env files, frame sizes, detection post-processing, the still-image variant, and where README and code disagree."
tags: [edge-ai, axis, acap, object-detection, tflite, ssd-mobilenet, acap-runtime, examples]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: cvex-readme
    resource: ../raw/acap-computer-vision-sdk-examples/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "ACAP Computer Vision SDK examples — repository README"
  - id: cvex-min-docs
    resource: ../raw/acap-computer-vision-sdk-examples/minimal-ml-inference/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "minimal-ml-inference README"
  - id: cvex-min-code
    resource: ../raw/acap-computer-vision-sdk-examples/minimal-ml-inference/app/simple_inference.py
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "minimal-ml-inference implementation (app, Dockerfile.model, compose, env)"
  - id: cvex-det-docs
    resource: ../raw/acap-computer-vision-sdk-examples/object-detector-python/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "object-detector-python README"
  - id: cvex-det-code
    resource: ../raw/acap-computer-vision-sdk-examples/object-detector-python/app/detector.py
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "object-detector-python implementation (detector.py, static-image.yml, compose, config)"
---

# CV SDK examples: minimal ML inference and object detection

Two of the [CV SDK examples](acap-cv-sdk-examples-repository.md) show the machine-learning path end to end; the repository README describes them as a minimal ML inference application and an object detector on the camera's video stream.[^cvex-readme] `minimal-ml-inference` is the smallest "capture → infer → print" client; `object-detector-python` adds labels, thresholding, box drawing and a still-image mode. Both send uint8 frames from the Runtime's video service to the Runtime's TensorFlow-Serving-style inference service, using the same model: Google Coral's post-training-quantized **SSD MobileNet V2 COCO** with a built-in `TFLite_Detection_PostProcess` op. The architecture is in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md); this page records what is specific to the two applications.[^cvex-min-code][^cvex-det-code]

## Model image

Both `Dockerfile.model` files are identical: `FROM alpine` (untagged, so `latest`), three `ADD`s from `https://github.com/google-coral/edgetpu/raw/master/test_data/` into `/models/` — `ssd_mobilenet_v2_coco_quant_postprocess.tflite`, `coco_labels.txt` and `COPYRIGHT` — and `CMD /bin/ls /models`. The `raw/master` URLs follow a moving branch with no checksum; the model may change or disappear without any change in this repository (**Observed**). The model input resolution is not stated anywhere in the repository.[^cvex-min-code][^cvex-det-code]

The container's only job is to populate the shared `acap_dl-models` volume that the Runtime reads at `/models`, which is why the compose file defines a service for it.[^cvex-min-code]

## minimal-ml-inference

`app/simple_inference.py` reads `INFERENCE_HOST` and `MODEL_PATH`, fixes the video stream to **224×224 at 10 fps**, and loops forever: `get_frame()`, add a batch dimension with `np.expand_dims(axis=0)`, call `InferenceClient.infer({'data': image}, MODEL_PATH)`, and `print(result)`. There is no resize, label lookup, threshold, error handling, or use of the `success` flag. The expected output is the model's raw output tensors. Env files set `MODEL_PATH=/models/ssd_mobilenet_v2_coco_quant_postprocess.tflite`; `INFERENCE_CHIP` is 2 (`cpu`) or 12 (`artpec8`).[^cvex-min-code][^cvex-min-docs]

Compose adds `INFERENCE_PORT=0` and a host `/tmp:/output` bind; neither is read by this application.[^cvex-min-code]

## object-detector-python

### Camera stream mode

`app/detector.py` reads `INFERENCE_HOST`, `DETECTION_THRESHOLD` (default `0.5`), `MODEL_PATH`, optional `IMAGE_PATH`, and `OBJECT_LIST_PATH` (`/models/coco_labels.txt` in compose). It opens a **480×320 at 10 fps** video stream, then for each frame:[^cvex-det-code]

1. `detect()` expands dims, casts to uint8 and calls `infer`.
2. The three outputs `TFLite_Detection_PostProcess`, `…:1`, `…:2` are squeezed into boxes, classes and confidences.
3. The code walks the confidences and truncates all three arrays at the first one below the threshold, printing `<n> Objects found`. This assumes the post-process op returns detections sorted by descending confidence; if every entry passes, all are returned.
4. `draw_bounding_boxes` scales normalized boxes by frame size, draws rectangles and labels with OpenCV and prints each label.

Labels come from `read_object_list`, which parses lines `<id> <label>[,alias…]`; calling it with no path would raise, though both compose files set the path.[^cvex-det-code]

### Still-image mode

`static-image.yml` is an alternative compose file that sets `IMAGE_PATH=dog416.png` (a 416×416 PNG bundled in `app/`) and mounts the host's `/usr/lib/libvdostream.so.1` and `/var/run/dbus`. `run_image_source` loads the image with `cv2.imread`, retries inference until it succeeds, draws the boxes, writes `/output/Objects-detector.jpg` (host `/tmp` through the bind mount) and prints total inference time in milliseconds. The README's expected output is `1 Objects found / person` for the stream and `3 Objects found / bicycle, dog, car` for the dog image. The retry loop sleeps one second per attempt and has no attempt limit, and the VDO library mount appears unnecessary for image-only mode (**Synthesis**).[^cvex-det-code][^cvex-det-docs]

## Where README and files disagree

All **Observed** by static comparison:[^cvex-det-docs][^cvex-min-docs][^cvex-det-code]

- Both READMEs show a model layout `ssdlite-mobilenet-v2` plus `objects.txt`; the actual files are `ssd_mobilenet_v2_coco_quant_postprocess.tflite` and `coco_labels.txt`.
- `object-detector-python/README.md` says the program "uses OpenCV to capture pictures"; capture is the Runtime's gRPC video service, and OpenCV only reads, draws and writes images.
- The same README calls the compose files a "larod inference server"; the server is the containerized ACAP Runtime.
- `minimal-ml-inference/README.md` shows `simple_inference.py` in the example root and asks to export `CHIP` "to select the right manifest file"; the file is `app/simple_inference.py` and no Dockerfile uses `CHIP`.
- Frames of 224×224 and 480×320 are sent without resizing to the model's input size; whether the Runtime resizes is not documented in this repository, so correctness of the detections is **Unverified** from the code.
- `opencv-python` is installed in `minimal-ml-inference` but never imported there.

## Constraints

- **Chip.** README requires an ARTPEC-8 DLPU camera (e.g. Q1656); a CPU variant exists through `config/env.aarch64.cpu` ([architecture page](acap-cv-examples-runtime-architecture.md)). The model is uint8-quantized, consistent with the DLPU quantization rules in [DLPU model constraints](axis-dlpu-model-constraints.md) (**Synthesis**).
- **Reproducibility.** Mutable model URL, unpinned `alpine`, unpinned pip packages.
- **Deployment.** Follow [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md); use `down --volumes` to remove the model volume.

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Uses:** [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md); the server side of its `Predict` calls is described in [ACAP Runtime Machine learning API](acap-runtime-machine-learning-api.md) and the frame source in [Video capture API](acap-runtime-video-capture-api.md).
- **Sibling:** [Pose estimator with Flask](acap-cv-example-pose-estimator-flask.md) reuses the same pattern with a different model.
- **Native alternative (synthesis):** the Native SDK's `object-detection` and `vdo-larod` examples in [Official ACAP application examples](acap-application-examples.md).

## Source coverage

- Inspected statically: both `README.md`, `Dockerfile`, `Dockerfile.model`, `docker-compose.yml`, `config/env.*`, `app/simple_inference.py`, `app/detector.py`, `static-image.yml`; `dog416.png` by metadata only.
- Not inspected: the downloaded model and label files (not in the repository), the Runtime's resizing behavior, and any device output. No code was run.

## Evidence class

Pipeline, constants and mismatches are **Observed**; output samples and requirements are **Reported** by the READMEs; the sorted-confidence assumption and the "unnecessary mount" reading are **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Example applications, at `12.10.0-3-g98b1ea7`.
[^cvex-min-docs]: `minimal-ml-inference/README.md` §Overview, §Example structure, §Requirements, §Build the Docker images, §Run the containers (expected output), at `12.10.0-3-g98b1ea7`.
[^cvex-min-code]: `minimal-ml-inference/app/simple_inference.py::L7-26`; `Dockerfile.model::L5-12`; `docker-compose.yml::L1-38`; `config/env.aarch64.{cpu,artpec8}::L1-3`; `Dockerfile::L3-41`, at `12.10.0-3-g98b1ea7`.
[^cvex-det-docs]: `object-detector-python/README.md` §Overview, §Example structure, §The expected output, at `12.10.0-3-g98b1ea7`.
[^cvex-det-code]: `object-detector-python/app/detector.py::{read_enviroment, detect, read_object_list, draw_bounding_boxes, run_camera_source, run_image_source}` (L37-133); `static-image.yml::L1-43`; `docker-compose.yml`; `Dockerfile.model`; `config/env.aarch64.*`; `app/dog416.png`, at `12.10.0-3-g98b1ea7`.
