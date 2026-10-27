---
type: Concept
title: "CV SDK example: QR code decoding with OpenCV"
description: "How opencv-qr-decoder-python reads 640x360 frames from the ACAP Runtime video service and decodes QR codes with OpenCV's QRCodeDetector, including its Runtime-only compose layout, requirements and README inaccuracies."
tags: [edge-ai, axis, acap, opencv, qr-code, video-capture, acap-runtime, examples]
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
  - id: cvex-qr-docs
    resource: ../raw/acap-computer-vision-sdk-examples/opencv-qr-decoder-python/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "opencv-qr-decoder-python README"
  - id: cvex-qr-code
    resource: ../raw/acap-computer-vision-sdk-examples/opencv-qr-decoder-python/app/qr.py
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "opencv-qr-decoder-python implementation (qr.py, Dockerfile, compose)"
---

# CV SDK example: QR code decoding with OpenCV

`opencv-qr-decoder-python` shows how to use the camera as a video source without any neural network; the repository README lists it as detecting and decoding QR codes in the video stream with OpenCV.[^cvex-readme] A Python container pulls frames from the **video-capture** service of the containerized ACAP Runtime, flips channel order and hands each frame to OpenCV's built-in `QRCodeDetector`, printing any decoded text. It is the minimal example of the "video only" use of the Runtime, in contrast to the inference examples in [ML inference and object detection](acap-cv-example-ml-inference-and-object-detection.md).[^cvex-qr-docs][^cvex-qr-code]

## Composition

The compose file defines two services. `qr-decoder-app` (`image: ${APP_NAME}`, json-file logging 5×100k, `PYTHONUNBUFFERED=1`, `INFERENCE_HOST=unix:///tmp/acap-runtime.sock`) shares the named volume `inference-server` at `/tmp` with `inference-server` — `axisecp/acap-runtime:2.0.1-aarch64-containerized`, entrypoint `/opt/app/acap_runtime/acapruntime`, no model (`-m`) or chip (`-j`) flags, mounting the D-Bus socket, `/run/parhand/parhandsocket`, `/usr/lib` and `/usr/bin`. There is no model container. The pattern is otherwise the one in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md).[^cvex-qr-code]

The Dockerfile is the multi-stage form: `proto-image` `axisecp/acap-runtime:2.0.1-protofiles` supplies `requirements.txt` and the VDO client modules (`/build/vdo/proto_utils`, imported as `vdo_proto_utils`); the runtime stage is `ubuntu:24.04` with `python3`, `python3-pip`, `python3-venv`, `ffmpeg`, `libsm6`, `libxext6`, a venv in `/opt/venv`, and unpinned `numpy` and `opencv-python`. `CMD ["python3","qr.py"]`.[^cvex-qr-code]

## Application flow

`app/qr.py` reads `INFERENCE_HOST`, creates `VideoCaptureClient(socket, 640, 360, 10)` — a hard-coded 640×360 stream at 10 fps — and `cv2.QRCodeDetector()`. The infinite loop does `get_frame()`, reverses the channel axis (`frame[:, :, ::-1]`, RGB→BGR for OpenCV), calls `detectAndDecodeMulti`, and prints each decoded string or `No QR found`. There is no exit condition, rate limit beyond the 10 fps stream, or result output other than the log.[^cvex-qr-code]

## Requirements

Same as the other examples: ARTPEC-8 DLPU device (e.g. Q1656), firmware 11.10+, Docker ACAP 3.0 with TLS, TCP and IPC socket and SD-card storage; the workstation needs Docker Desktop 4.11.1+ or Docker Engine 20.10.17+ with Compose 1.29.2+. Deployment follows the [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md); the README uses `down --volumes`. Because no model is involved, the DLPU is not actually used by the code (**Synthesis**), so the chip requirement reflects the repository's common baseline rather than a technical need.[^cvex-qr-docs]

## Discrepancies and leftovers

All **Observed**:[^cvex-qr-docs][^cvex-qr-code]

- The README says the app "performs an inference using a deep learning model"; it uses OpenCV's classical QR detector, no model.
- The README says OpenCV requirements will be in `docker-compose.yml`; they are installed in the Dockerfile.
- `ffmpeg`, `libsm6`, `libxext6` are unused (no GUI or video I/O); `requirements.txt` is copied to `/` before `WORKDIR` is set, leaving a stray file.
- The comment `# Instatiate` is a typo; the README states no expected output.

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Uses:** [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md) (video service only).
- **Sibling by service:** [Parameter API example](acap-cv-example-parameter-api.md) uses a different Runtime service in the same Compose shape.

## Source coverage

- Inspected statically: `README.md`, `Dockerfile`, `docker-compose.yml`, `app/qr.py`. Not verified: OpenCV QR reliability at 640×360, frame latency, or any device behavior. Nothing was executed.

## Evidence class

Flow and constants are **Observed**; requirements are **Reported**; the DLPU-not-used comment is **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Example applications, at `12.10.0-3-g98b1ea7`.
[^cvex-qr-docs]: `opencv-qr-decoder-python/README.md::L3-10` (overview), §Requirements, §How to run the code (L41-90), at `12.10.0-3-g98b1ea7`.
[^cvex-qr-code]: `opencv-qr-decoder-python/app/qr.py::L22-47`; `Dockerfile::L3-40`; `docker-compose.yml::L3-30`, at `12.10.0-3-g98b1ea7`.
