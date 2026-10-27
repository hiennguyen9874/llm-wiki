---
type: Concept
title: "CV SDK example: MoveNet pose estimation published with Flask"
description: "How pose-estimator-with-flask runs MoveNet SinglePose Lightning through ACAP Runtime on a 1080p camera stream, draws 17 keypoints, and republishes MJPEG on port 5000, with model details, constants, and defects."
tags: [edge-ai, axis, acap, pose-estimation, movenet, flask, mjpeg, acap-runtime, examples]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T14:00:00Z }
stale_after: 2027-08-31
sources:
  - id: cvex-readme
    resource: ../raw/acap-computer-vision-sdk-examples/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "ACAP Computer Vision SDK examples — repository README"
  - id: cvex-pose-docs
    resource: ../raw/acap-computer-vision-sdk-examples/pose-estimator-with-flask/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "pose-estimator-with-flask README and assets"
  - id: cvex-pose-code
    resource: ../raw/acap-computer-vision-sdk-examples/pose-estimator-with-flask/app/detector_with_flask.py
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "pose-estimator-with-flask implementation (app, template, Dockerfiles, compose, config)"
---

# CV SDK example: MoveNet pose estimation published with Flask

`pose-estimator-with-flask` is the most complete application among the [CV SDK examples](acap-cv-sdk-examples-repository.md): a Python container that captures 1080p frames from the camera, runs **MoveNet SinglePose Lightning** through the containerized ACAP Runtime, draws the 17 detected body keypoints and their connections on the frame, and serves the result as a Motion-JPEG stream from a Flask web app on port 5000 (the repository README lists it as pose estimation published as a video stream using Flask).[^cvex-readme] Browsing `http://<camera-ip>:5000` shows the annotated live video. The Runtime plumbing is the shared pattern in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md).[^cvex-pose-docs][^cvex-pose-code]

## Architecture

The README's diagram (`assets/scheme.jpg`, inspected) shows two sides. On the camera: a *Model* container loads the model into the *Inference server* container; the *Application* container (Flask) sends inference requests and receives results from it. On the workstation: *Docker build* produces the containers loaded onto the camera. The application *publishes on port 5000* to a browser at `Camera IP:5000`. `assets/frame_36.jpg` is a sample output showing a person with yellow joints and red bones.[^cvex-pose-docs]

Compose defines three services: `pose-estimator` (port `5000:5000`, `INFERENCE_HOST=unix:///tmp/acap-runtime.sock`, `MODEL_PATH`), `inference-server` (the Runtime, `-m ${MODEL_PATH} -j ${INFERENCE_CHIP}`) and the model service filling `acap_dl-models`. Env files differ only in `INFERENCE_CHIP`: `2` for CPU, `12` for the DLPU (see [Runtime architecture](acap-cv-examples-runtime-architecture.md)).[^cvex-pose-code]

## Model

- **File:** `movenet_single_pose_lightning_ptq.tflite`, post-training quantized, fetched by `Dockerfile.model` from `https://raw.githubusercontent.com/google-coral/test_data/master/…` together with the `…_ptq_edgetpu.tflite` variant. The Edge TPU variant is downloaded but no `MODEL_PATH` references it (dead artifact); both URLs follow `master` with no checksum.[^cvex-pose-code]
- **Input:** 192×192 pixels, passed as uint8 without normalization (`image.astype(np.uint8)`). The README gives the same input size.[^cvex-pose-docs]
- **Output:** tensor `StatefulPartitionedCall:0` with shape 1×1×17×3: per keypoint `(y, x, confidence)`, normalized coordinates. The code indexes `[0][0]` and splits coordinates `[:, :2]` from confidences `[:, 2]`.[^cvex-pose-code]

The README motivates pose estimation as better than plain detection for tracking people under partial occlusion, and lists autonomous-driving pedestrian intent and healthcare fall detection as applications (**Reported**, no measurements).[^cvex-pose-docs]

## Processing flow

`Detector` opens `VideoCaptureClient` at **1920×1080, 10 fps**, then per frame (`get_frame`):[^cvex-pose-code]

1. Crop the centre square `frame[:, 420:-420, :]` (1080×1080).
2. `cv2.resize` to 192×192 (`INTER_AREA`) and call `infer`.
3. Draw keypoints and connections on the full-resolution square: 18 edge pairs from a table, drawn only when both endpoints exceed `DETECTION_THRESHOLD` (default `0.3`); keypoints are filled circles of radius 20 and lines have thickness 4.
4. `gen()` JPEG-encodes the frame and yields `--frame` multipart parts; `/video_feed` returns `multipart/x-mixed-replace; boundary=frame`, and `/` renders `templates/index.html` — one `<img src=video_feed>`.

`app.run(host='0.0.0.0', threaded=True)` starts the **Flask development server** on the default port 5000 with no authentication or TLS, so anyone who can reach the camera network can watch the stream (**Observed**).[^cvex-pose-code]

## Defects and mismatches

All **Observed** by static inspection:[^cvex-pose-code][^cvex-pose-docs]

- README lists `app/pose-estimator-with-flask.py`; the file is `app/detector_with_flask.py`.
- README Overview says the application "performs object detection"; it performs pose estimation.
- README asks to export `CHIP` "to select the right manifest file" during build; no Dockerfile reads it.
- `draw_keypoints` multiplies `point[1]` by height and `point[0]` by width — swapped relative to the `(y, x)` output; it only works because the crop is square (1080×1080).
- Colour codes in the edge table are unused (all lines `(0,0,255)`); the drawing happens before the RGB→BGR conversion, which explains the red/yellow look.
- `gen()` creates a new `Detector` per client connection, so each browser tab opens its own video stream and inference client.
- Dead fields (`debug`, `detection_type`, `object_list`, `background`) and a typo `firs_frame`; `INFERENCE_PORT` and the `/tmp:/output` bind are unused.

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Uses:** [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md); deploy with the [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md).
- **Sibling:** [ML inference and object detection](acap-cv-example-ml-inference-and-object-detection.md).
- **Exposure trade-off (synthesis):** a native ACAP would put such an HTTP endpoint behind Apache — see [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md) — instead of publishing a raw port.

## Source coverage

- Inspected: `README.md`, `Dockerfile`, `Dockerfile.model`, `docker-compose.yml`, `config/env.*`, `app/detector_with_flask.py`, `app/templates/index.html`, and both images in `assets/` (diagram and sample frame).
- Not verified: the model files (external, not in repo), observed frame rate, DLPU compatibility of the MoveNet ops, and every runtime behavior. No code was run.

## Evidence class

Structure, constants and defects are **Observed**; applications and benefits are **Reported**; the exposure comment is **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Example applications, at `12.10.0-3-g98b1ea7`.
[^cvex-pose-docs]: `pose-estimator-with-flask/README.md` §intro, §Overview, §Applications, §Example structure, §Build the Docker images; `assets/scheme.jpg`, `assets/frame_36.jpg`, at `12.10.0-3-g98b1ea7`.
[^cvex-pose-code]: `pose-estimator-with-flask/app/detector_with_flask.py::{Detector.__init__, read_environment, detect, get_frame, draw_keypoints, draw_connections, gen, video_feed, __main__}`; `app/templates/index.html`; `Dockerfile::L1-33`; `Dockerfile.model::L5-7`; `docker-compose.yml`; `config/env.aarch64.{cpu,artpec8}`, at `12.10.0-3-g98b1ea7`.
