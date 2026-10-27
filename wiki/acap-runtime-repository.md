---
type: Concept
title: "ACAP Runtime repository: gRPC service for Axis cameras, overview and coverage ledger"
description: "What AxisCommunications/acap-runtime at 2.0.1-10-ge375fc9 is: a C++ gRPC server exposing machine-learning inference, video capture and parameter APIs to containerized clients, its identity, distribution history, layout, coverage ledger and the main README-versus-code gaps."
tags: [edge-ai, axis, acap, acap-runtime, grpc, repository, docker, larod, vdo]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: rt-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9 (e375fc9586e270042c9c46dde7645c20761b06bf, 2026-08-18)"
    title: "AxisCommunications/acap-runtime — README (git submodule)"
  - id: rt-diagram
    resource: ../raw/acap-runtime/assets/gRPC.png
    scope: ../raw/acap-runtime/
    kind: image
    revision: "2.0.1-10-ge375fc9"
    title: "ACAP Runtime Service with gRPC client (architecture diagram)"
  - id: rt-license
    resource: ../raw/acap-runtime/LICENSE
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "Apache License 2.0"
  - id: rt-manifest
    resource: ../raw/acap-runtime/manifest-aarch64.json
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "ACAP manifest for the aarch64 package"
---

# ACAP Runtime repository: gRPC service for Axis cameras, overview and coverage ledger

ACAP Runtime is a **network-protocol service built on gRPC** that runs on an Axis camera and exposes three device capabilities — machine-learning inference, video capture and parameter reading — to client applications "written in any gRPC compatible language" on the same device.[^rt-readme] Its practical role is the bridge that lets a *container* (Docker ACAP / Docker Compose ACAP) use camera hardware it cannot link against directly, which is exactly how the examples in the [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md) use it (see [their Runtime architecture](acap-cv-examples-runtime-architecture.md)). The source is a small C++17 program (about 2,000 lines under `src/`) that wraps the larod, VDO and AXParameter libraries of the device SDK behind generated gRPC stubs; this page is the entry point, and the detail lives in the linked concepts below.

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/acap-runtime` (git remote `origin`), vendored as a submodule at `raw/acap-runtime/` |
| Revision | `e375fc9586e270042c9c46dde7645c20761b06bf`, `git describe` = `2.0.1-10-ge375fc9`, commit date 2026-08-18 (the date looks clock-skewed relative to the 2025 tags; treat as unverified) |
| Latest tag | `2.0.1` (2025-06-18); before it `2.0.0` (2024-09-20) and `1.3.1` (2023-04-24) |
| License | Apache License 2.0 (`LICENSE`); README copyright "2022, Axis Communications AB, Lund, Sweden"[^rt-license] |
| Languages | C++17 (server and tests), one C shim, Python (client wrappers, device test runner), protobuf, Dockerfile, YAML |
| Maintained by | one catch-all CODEOWNERS entry for two Axis teams ([CI and maintenance](acap-runtime-ci-and-maintenance.md)) |

## The three APIs

The README lists three APIs; the diagram shows them as three boxes inside the "ACAP Runtime Service" next to a dashed "Extended Functionality" box (an extension point, no code), with a "gRPC Server" bar on top. The client side is a "Client App" with a "gRPC Stub"; the legend colours the Runtime as "parts of ACAP Runtime maintained" by Axis and the client as "parts to be implemented by user". Arrows are labelled "Proto Request" and "Proto Response".[^rt-readme][^rt-diagram]

| API | Wire contract | Backed by | Concept |
| --- | --- | --- | --- |
| Machine learning | TensorFlow Serving `PredictionService` (r2.9) with two added fields | larod (`-llarod`), libyuv preprocessing | [ML API](acap-runtime-machine-learning-api.md) |
| Video capture | `videocapture.v1.VideoCapture` (`NewStream`, `DeleteStream`, `GetFrame`) | VDO (`vdostream`) | [Video capture API](acap-runtime-video-capture-api.md) |
| Parameter | `keyvaluestore.KeyValueStore.GetValues` (read-only) | `axparameter` | [Parameter API](acap-runtime-parameter-api.md) |

**Observed:** only the Machine learning API is a TensorFlow Serving implementation, and only its `Predict` RPC; the README's phrase "an implementation of TensorFlow Serving" overstates it (details in the ML concept). The README also does not mention the two fields that connect the ML and video APIs (`stream_id`, `frame_reference`).[^rt-readme]

## Requirements and distribution

- Device: Docker ACAP or Docker Compose ACAP **2.0.0 or higher**, AXIS OS **11.10 or higher**, certificate files if TLS is used. Computer: Docker Desktop 4.11.1+ or Docker Engine 20.10.17+, plus Buildx to build locally.[^rt-readme]
- Distribution: pre-built images on Docker Hub `axisecp/acap-runtime`, tagged `<version>-<ARCH>-containerized`. Up to release 1.3.1 it was also shipped as an ACAP `.eap`; **from 2.0.0 it is a Docker image only**. A second image, `<version>-protofiles`, carries generated Python client files.[^rt-readme]
- The README release table lists `2.0.0` (min AXIS OS 11.10) as "Latest release" and `1.3.1` (min 10.12) as the "Legacy release AXIS OS 2022 LTS". Tag `2.0.1` exists and is not listed, and the README's compose and TLS examples still pin `2.0.0` (**Observed**, git tags versus README).[^rt-readme]
- 2.0.0 → 2.0.1 is three commits: a multi-platform Dockerfile refactor, `g_unix_signal_add` replacing `sigaction`, and a fix to `tf_proto_utils.py`; the 10 commits after 2.0.1 are CI hardening and README lint (**Observed**, `git log`). See [CI and maintenance](acap-runtime-ci-and-maintenance.md).

## How to run it (README)

The README example runs the image's `/opt/app/acap_runtime/acapruntime -j 12` with four mounts (D-Bus socket, `/run/parhand/parhandsocket`, `/usr/lib`, `/usr/bin`) and a shared volume at `/tmp` carrying the Unix socket `/tmp/acap-runtime.sock`; the client sets `INFERENCE_HOST=unix:///tmp/acap-runtime.sock` and `INFERENCE_PORT=0`.[^rt-readme] Flags, chip ids, sockets and TLS are in [Server configuration and security](acap-runtime-server-configuration-and-security.md); the image build is in [Build and image packaging](acap-runtime-build-and-image-packaging.md).

## Repository layout and coverage ledger

The checkout has 61 tracked files (about 11,200 lines, 4,276 of them one BMP). All project-owned text files were read statically by six parallel explorers and the main agent; **nothing was built or executed** (no Docker, no device).

| Area | Files | Status | Concept |
| --- | --- | --- | --- |
| `src/` | `main.c`, `acap_runtime.cpp`, `inference.{cpp,h}`, `video_capture.{cpp,h}`, `parameter.{cpp,h}`, `util.{cpp,h}`, `read_text.{cc,h}` | inspected in full | server, ML, video, parameter concepts |
| `apis/` | `keyvaluestore.proto`, `videocapture.proto`, `predict_additions.patch`, `wrappers/{tf,vdo}_proto_utils.py` | inspected in full | ML, video, parameter concepts |
| Build | `Dockerfile`, `Dockerfile.proto`, `Makefile`, `manifest-{aarch64,armv7hf,test}.json`, `.dockerignore`, `.gitignore` | inspected in full | [Build and image packaging](acap-runtime-build-and-image-packaging.md) |
| `test/`, `.github/test/`, `testdata/` | six gtest source files plus helpers, device runner, two BMPs | inspected; BMPs by name and size only | [Test suite](acap-runtime-test-suite.md) |
| `.github/`, lint/editor configs, `CONTRIBUTING.md`, `CODEOWNERS` | 3 workflows, 4 composite actions, Renovate, `.hadolint.yaml`, `.markdownlint.yaml`, `.yamllint.yml`, `.clang-format`, `.editorconfig`, `.vscode/` | inspected in full | [CI and maintenance](acap-runtime-ci-and-maintenance.md) |
| `assets/gRPC.png` | architecture diagram | viewed | this page |
| `LICENSE` | Apache 2.0 | identified, not summarised | this page |

Excluded or unavailable: the TensorFlow, TensorFlow Serving and gRPC sources and the Coral/TF test models fetched at image build time, the SDK images and larod/VDO/axparameter sources, the Docker Hub images, and the Docker ACAP repositories. `testdata/solid_300x300.bmp` is a binary referenced by no test. The `.git` directory was used only for tags and `git log`.

## README versus code (summary)

These are persisted in detail in the concepts named; the ones that change how a reader should use the service:

- The README documents TLS as default; the binary's own defaults are **insecure with chip id 0** (ML disabled), and the image has no default flags ([server configuration](acap-runtime-server-configuration-and-security.md)).
- The README's "TLS authenticated" mode is server-side TLS only; no client certificate is requested.
- The Python protofiles are generated **without** the `stream_id`/`frame_reference` patch ([ML API](acap-runtime-machine-learning-api.md)).
- The in-tree manifests still say version `1.3.1`.[^rt-manifest]

## Relationships

- **Used by:** the five Runtime-using examples via [Containerized ACAP Runtime architecture in the CV SDK examples](acap-cv-examples-runtime-architecture.md), including the [Parameter API example](acap-cv-example-parameter-api.md) and [ML inference examples](acap-cv-example-ml-inference-and-object-detection.md).
- **Depends on:** Docker ACAP or Docker Compose ACAP ([Container-based ACAP applications](acap-container-applications.md)); the Native SDK image the Runtime is built in ([ACAP Native SDK repository](acap-native-sdk-repository.md)).
- **Part of (synthesis):** the container path that Axis now deprecates in favour of native `.eap` applications ([ACAP Native SDK](axis-acap-native-sdk.md)); a native app calls larod, VDO and AXParameter directly ([Native SDK API catalog](acap-native-sdk-api-catalog.md)).
- **Documented in:** [ACAP documentation repository](acap-documentation-repository.md) as the "beta" ACAP Runtime section of the CV SDK API page (link target only; not read here).

## Evidence class

Identity, APIs, layout and the release/tag gap are **Observed** by static inspection of the checkout. Role statements ("bridge for containers") are the README's (**Reported**) plus **Synthesis**. Nothing is **Reproduced**.

[^rt-readme]: `README.md` §Notable Releases, §Overview, §Requirements, §APIs, §Usage (compose example); `git describe`, `git tag` and `git log` of the checkout at `2.0.1-10-ge375fc9`.
[^rt-diagram]: `assets/gRPC.png` — boxes "ACAP Runtime Service" (gRPC Server; Machine learning API, Parameter API, Video capture API; dashed Extended Functionality), "Client App" (gRPC Stub), arrows "Proto Request"/"Proto Response", colour legend.
[^rt-license]: `LICENSE` header (Apache License 2.0); `README.md` copyright line and §License.
[^rt-manifest]: `manifest-aarch64.json::{appName, version, runOptions}` — `acapruntime`, `1.3.1`, `-o`.
