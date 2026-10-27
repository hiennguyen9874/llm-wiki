---
type: Concept
title: "ACAP Computer Vision SDK examples repository"
description: "What the archived acap-computer-vision-sdk-examples repository contains: seven container-based Python and C examples for Axis aarch64 cameras, its deprecation status, required components, and an index of what each example demonstrates."
tags: [edge-ai, axis, acap, docker, containers, examples, acap-runtime, repository]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: cvex-readme
    resource: ../raw/acap-computer-vision-sdk-examples/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7 (98b1ea78387f82210ae8f3bac9c2e700565a811f, 2026-08-18)"
    title: "ACAP Computer Vision SDK examples — repository README"
  - id: cvex-tree
    resource: ../raw/acap-computer-vision-sdk-examples/hello-world-python/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "hello-world-python example (README, Dockerfile, compose, app)"
---

# ACAP Computer Vision SDK examples repository

`AxisCommunications/acap-computer-vision-sdk-examples` is the worked-example companion of the **container-based ACAP** model: seven small applications, each a Docker image (plus, for most, a Docker Compose file) that is built on a workstation and run on an Axis camera through the **Docker ACAP**. Six are Python and one packages the Monkey web server in C. The repository itself is the vendor's own statement that this model is legacy — its README leads with a deprecation banner — so the useful reading is as a reference for how Axis wired video capture, machine-learning inference and parameter access into containers, and as a maintenance aid for existing container deployments rather than as a template for new products.[^cvex-readme]

## Status and constraints

The README's banner makes four claims, all **Reported** by the vendor:[^cvex-readme]

- New Axis products released on AXIS OS 12.x will not have container support; products that already have it stay supported until end of 2031, when AXIS OS 2026 LTS reaches end of life.
- The recommended path for analytics, computer vision and machine-learning applications is the ACAP Native SDK and its `acap-native-sdk-examples`.
- The ACAP Computer Vision SDK is archived; its utility libraries and scripts moved to ACAP Runtime. The README's sentence pointing at the new setup links to this same repository, so it is circular rather than a pointer to Runtime examples (**Observed**).
- The only supported architecture is `aarch64`.

This matches the lifecycle statements already compiled in [Container-based ACAP applications](acap-container-applications.md) and the device matrix in [Container application compatibility](acap-container-compatibility.md); the native replacement is described in [ACAP Native SDK](axis-acap-native-sdk.md) and its official examples in [Official ACAP application examples](acap-application-examples.md).

## Required components

Two components outside the repository are needed, per the README:[^cvex-readme]

| Component | Role | Where it comes from |
| --- | --- | --- |
| Docker ACAP | The Docker daemon that runs the example containers on the camera | Must already be installed and running on the device |
| ACAP Runtime | Container image that exposes the video, machine-learning and parameter APIs over gRPC | Pulled from Docker Hub when `docker compose up` starts |

The README says ACAP Runtime is used "in a few examples". By inspection, five of seven use it (`minimal-ml-inference`, `object-detector-python`, `opencv-qr-decoder-python`, `parameter-api-python`, `pose-estimator-with-flask`); only `hello-world-python` and `web-server` do not.[^cvex-readme][^cvex-tree] How that runtime is wired is in [Containerized ACAP Runtime architecture in the CV SDK examples](acap-cv-examples-runtime-architecture.md).

## The seven examples

| Example | Language | Uses ACAP Runtime | What it demonstrates | Detail |
| --- | --- | --- | --- | --- |
| `hello-world-python` | Python | No | Smallest possible container: `python3` on `ubuntu:24.04` printing `Hello World!`; no camera access | This page |
| `minimal-ml-inference` | Python | Yes | Capture a frame, send it to a TFLite model through the Runtime, print the raw result | [ML inference and object detection examples](acap-cv-example-ml-inference-and-object-detection.md) |
| `object-detector-python` | Python | Yes | SSD MobileNet V2 object detection on the live stream or a still image, with boxes drawn | [ML inference and object detection examples](acap-cv-example-ml-inference-and-object-detection.md) |
| `opencv-qr-decoder-python` | Python | Yes (video only) | Decode QR codes from camera frames with OpenCV | [QR decoder example](acap-cv-example-opencv-qr-decoder.md) |
| `parameter-api-python` | Python | Yes (parameter service) | Read device parameters through the beta Parameter API over TLS gRPC | [Parameter API example](acap-cv-example-parameter-api.md) |
| `pose-estimator-with-flask` | Python | Yes | MoveNet pose estimation republished as an MJPEG stream by Flask on port 5000 | [Pose estimator example](acap-cv-example-pose-estimator-flask.md) |
| `web-server` | C | No | Monkey HTTP server 1.5.6 built from source in a container, port 2001 | [Monkey web server example](acap-cv-example-monkey-web-server.md) |

The README describes `web-server` as "a C++ example"; its sources and the patched Monkey files are C (**Observed**, `web-server/monkey.patch`).[^cvex-readme][^cvex-tree]

### hello-world-python

The Dockerfile starts `FROM ubuntu:${UBUNTU_VERSION}` (24.04) with `--platform=$DEVICE_PLATFORM` (`linux/arm64/v8`), installs only an unpinned `python3` with `--no-install-recommends`, copies `app/*` to `/opt/app` and runs `python3 simply_hello.py`. The script defines `greet_world()` and calls it under a `__main__` guard. The compose file has a single service whose `image` is `${APP_NAME}`, with no volumes, sockets, ports or environment — so the example proves the Docker ACAP deployment loop (see [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md)) and nothing about camera access. Its README states the common requirements and run path but does not warn that `APP_NAME` must be exported in the same shell, otherwise `image:` resolves empty.[^cvex-tree]

## Shared conventions

- **Layout.** Every example directory carries its own `README.md`, `Dockerfile` and `docker-compose.yml`; ML examples add `Dockerfile.model` and `config/env.aarch64.{cpu,artpec8}`.[^cvex-readme]
- **Base image.** All Dockerfiles use `ubuntu:24.04` with the platform pinned to `linux/arm64/v8`; Python examples add a virtual environment in `/opt/venv`.[^cvex-tree]
- **No tests.** There are no unit or on-device tests; CI only builds images (see [CI and maintenance](acap-cv-examples-ci-and-maintenance.md)).
- **Compose format.** Compose files declare `version: '3.3'`, an obsolete key in Compose v2 (**Observed**).[^cvex-tree]

## Relationships

- **Documents:** the worked examples behind the "Computer Vision SDK image" referenced in [Container-based ACAP applications](acap-container-applications.md).
- **Depends on:** Docker ACAP and ACAP Runtime; see [Containerized ACAP Runtime architecture in the CV SDK examples](acap-cv-examples-runtime-architecture.md) and the Runtime's own repository in [ACAP Runtime repository](acap-runtime-repository.md).
- **Superseded by (vendor recommendation):** the Native SDK path — [ACAP Native SDK](axis-acap-native-sdk.md).
- **Maintenance state:** [CI and maintenance of the CV SDK examples](acap-cv-examples-ci-and-maintenance.md).
- **Successor** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md): the native counterpart (inference, web server, parameters) without Docker ACAP or Runtime.

## Source coverage

- Entry point `README.md` and scope `raw/acap-computer-vision-sdk-examples/`, a git checkout at `12.10.0-3-g98b1ea7` (commit `98b1ea7`, 2026-08-18), 62 tracked files, license Apache-2.0, Axis copyright headers dating 2021–2022. Every project-owned text file was read statically by four explorers and the main agent; the repository's contents were not built or executed.
- Inventory by area: repo root (`README.md`, `LICENSE`, `CODEOWNERS`, `.editorconfig`, `.markdownlint.yml`, `.gitignore`, `.vscode/`), `.github/` (7 build workflows, `example-checks.yml`, `auto-sync-to-staging.yml`, `renovate.json`, 2 issue templates) and seven example directories.
- Binary or decorative files inspected by name and, where useful, by viewing: `pose-estimator-with-flask/assets/{scheme.jpg,frame_36.jpg}` (an architecture diagram and example output, summarized in the pose page) and `object-detector-python/app/dog416.png` (a 416×416 test image). `LICENSE` identified, not summarized.
- Not local and therefore not verified: the Docker ACAP and ACAP Runtime repositories' current state beyond the local `raw/acap-runtime/` submodule (compiled separately in [ACAP Runtime repository](acap-runtime-repository.md)), Docker Hub image contents, the model files downloaded at build time, and the Axis device compatibility pages.

## Evidence class

The catalog, layout, requirements and deprecation statements are **Reported** (vendor README) and **Observed** (static inspection of the files). Nothing was **Reproduced**: no image was built, no container was run, and no device was used.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` at `12.10.0-3-g98b1ea7` — §Note (banner, lines 5–18), §Requirements (§Supported architectures, §Required components), §Example applications; plus `CODEOWNERS`, `.github/workflows/*` for the Runtime-usage count.
[^cvex-tree]: `hello-world-python/{README.md, Dockerfile::L3-16, docker-compose.yml::L3-5, app/simply_hello.py::greet_world}` and `Dockerfile`/`docker-compose.yml` of all seven examples (base image, platform, compose `version`, Runtime services) at `12.10.0-3-g98b1ea7`; `web-server/monkey.patch` for the language.
