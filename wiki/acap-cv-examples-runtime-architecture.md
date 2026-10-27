---
type: Concept
title: "Containerized ACAP Runtime architecture in the CV SDK examples"
description: "How the container examples reach the camera: an application container, an ACAP Runtime inference-server container and a model-volume container linked by a Unix gRPC socket, with the chip-id switch, mounts, Dockerfile pattern and proto client libraries."
tags: [edge-ai, axis, acap, acap-runtime, grpc, docker-compose, dlpu, architecture]
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
  - id: cvex-ml-docs
    resource: ../raw/acap-computer-vision-sdk-examples/minimal-ml-inference/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "minimal-ml-inference README (overview, requirements, hardware acceleration)"
  - id: cvex-ml-config
    resource: ../raw/acap-computer-vision-sdk-examples/minimal-ml-inference/docker-compose.yml
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "minimal-ml-inference compose, Dockerfiles, env files and app"
  - id: cvex-runtime-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "ACAP Runtime README (chip id table, configuration flags)"
---

# Containerized ACAP Runtime architecture in the CV SDK examples

Per the repository README, ACAP Runtime is a container image the examples pull from Docker Hub at start.[^cvex-readme] Five of the seven examples in the [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md) do not talk to camera hardware directly. They run next to a second container — the **inference-server**, the containerized build of **ACAP Runtime** — and call it over **gRPC on a Unix domain socket** stored in a shared Docker volume. The Runtime owns video capture (VDO), the machine-learning inference service (TensorFlow Serving API) and the parameter store; the application container only imports generated protobuf client modules. The pattern, and the one switch that moves inference from CPU to the ARTPEC-8 DLPU, is the same in every ML example.[^cvex-ml-docs][^cvex-ml-config]

## Three containers

The ML README describes the composition: the first container holds the application built in the example, the second (*inference-server*) captures images and performs inference by implementing the TensorFlow Serving API, and a third container holds the deep-learning model, which is copied into a volume shared with the other two.[^cvex-ml-docs]

| Container (compose service) | Image | Responsibility |
| --- | --- | --- |
| Application | `${APP_NAME}` built from the example's `Dockerfile` | gRPC client: pulls frames, sends tensors, post-processes results |
| `inference-server` | `axisecp/acap-runtime:2.0.1-aarch64-containerized` | ACAP Runtime process `/opt/app/acap_runtime/acapruntime -m ${MODEL_PATH} -j ${INFERENCE_CHIP}` |
| Model (`acap_dl-models`) | `${MODEL_NAME}` built from `Dockerfile.model` | Populates named volume `acap_dl-models` with the `.tflite` file and labels |

No ports are published for the Runtime. The application reaches it with `INFERENCE_HOST=unix:///tmp/acap-runtime.sock`, and the socket exists because both containers mount the named volume `inference-server` at `/tmp`. The model volume is mounted read-only at `/models` in both.[^cvex-ml-config] Only `pose-estimator-with-flask` publishes a port, and that is the Flask app's, not the Runtime's (see [pose estimator](acap-cv-example-pose-estimator-flask.md)).

### What the inference-server mounts from the device

The inference-server compose service also bind-mounts host resources, which is what lets a container use the camera's services:[^cvex-ml-config]

- `/run/dbus/system_bus_socket` — the D-Bus system bus.
- `/run/parhand/parhandsocket` — the parameter-handler socket (`parameter-api-python` mounts `/run/confcache/confcachesocket` instead — see [Parameter API example](acap-cv-example-parameter-api.md)).
- `/usr/lib` and `/usr/bin` from the host, which supply the device's native libraries to the Runtime binary.

**Synthesis:** these four mounts are the integration contract between a container and AXIS OS; they tie the containers to the host's filesystem layout, which is one reason the model could not be carried to AXIS OS 12-era products without container support.

## Choosing the chip: CPU versus DLPU

Each ML example has `config/env.aarch64.cpu` and `config/env.aarch64.artpec8`, passed with `docker compose --env-file ./config/env.aarch64.$CHIP`. In `minimal-ml-inference`, `object-detector-python` and `pose-estimator-with-flask` the two files are identical except for one line:[^cvex-ml-config]

| File | `INFERENCE_CHIP` | Meaning |
| --- | --- | --- |
| `env.aarch64.artpec8` | `12` | DLPU hardware accelerator |
| `env.aarch64.cpu` | `2` | CPU inference |

The shared keys are `MODEL_PATH` and `INFERENCE_SERVER_IMAGE`. The ACAP Runtime README documents `-j <chip id>` as the chip used by the machine-learning service and lists `12` as `LAROD_CHIP_TFLITE_ARTPEC8DLPU` ("ARTPEC-8 DLPU with TensorFlow Lite"), the default for its `aarch64` images. Its table has no entry for id `2`, so what `2` selects is **not documented in the Runtime README** (**Observed**); the Runtime's own tests use `cpuChipId = "2"` for CPU inference (see [Server configuration](acap-runtime-server-configuration-and-security.md)), consistent with the examples' file name and README ("`cpu`"), and the example README says the hardware accelerator gives best performance on DLPU-equipped ARTPEC-8 cameras.[^cvex-runtime-readme][^cvex-ml-docs] The two ids are numeric chip enums of the Machine learning API, not the larod channel names (`cpu-tflite`, `axis-a8-dlpu-tflite`) that the issue template asks for — see [CI and maintenance](acap-cv-examples-ci-and-maintenance.md) and [Axis DLPU](axis-dlpu.md).

The runtime README also says the service can bind either a Unix socket (default) or a network socket, selected by a non-zero `-p` port, and runs TLS-authenticated by default with `-c`/`-k` certificate and key files. The ML examples' `INFERENCE_PORT=0` equals the Runtime's default of a Unix socket; no application code reads the variable (**Observed**).[^cvex-runtime-readme][^cvex-ml-config]

## Application image pattern

All Runtime-using Dockerfiles share one multi-stage shape:[^cvex-ml-config]

1. Stage `proto-image` is `${REPO}/${IMAGE}:${RUNTIME_VERSION}-protofiles`, i.e. `axisecp/acap-runtime:2.0.1-protofiles`. It supplies the pinned gRPC/protobuf `requirements.txt` and generated client modules.
2. Stage `runtime-image` is `ubuntu:24.04` for `linux/arm64/v8`. It installs `python3`, `python3-pip`, `python3-venv`, `ffmpeg`, `libsm6`, `libxext6` (unpinned), builds `/opt/venv`, and `pip install`s the proto requirements plus unpinned `numpy` and `opencv-python`.
3. It copies `/build/vdo/proto_utils` (module `vdo_proto_utils`, `VideoCaptureClient`) and, for inference examples, `/build/tf/proto_utils` (`tf_proto_utils`, `InferenceClient`) into `/opt/app`, then `COPY app/* .` and sets the `CMD`.

The inference client call is `InferenceClient.infer({'data': image}, MODEL_PATH)` and the video client is `VideoCaptureClient(socket, width, height, fps).get_frame()`; each example fixes its own stream geometry (224×224@10, 480×320@10, 640×360@10, 1920×1080@10). `ffmpeg`, `libsm6` and `libxext6` are unused leftovers in `minimal-ml-inference` and `opencv-qr-decoder-python` (**Observed**).[^cvex-ml-config]

## Constraints and failure modes

- **Version drift.** The Runtime version `2.0.1` is written in `ARG RUNTIME_VERSION` in each Dockerfile and again in `INFERENCE_SERVER_IMAGE` in each env file; nothing keeps them equal.[^cvex-ml-config]
- **Mutable inputs.** Model images use untagged `alpine` (`:latest`) and download models from `raw/master` URLs of Google Coral repositories; pip packages are unpinned. Rebuilds are not reproducible (**Observed**).
- **Pull dependency.** If the device cannot reach Docker Hub, the README says to pull the Runtime image on the workstation and `docker load` it to the device.[^cvex-ml-docs]
- **Security.** The Runtime socket is a local file; there is no network exposure by default. `parameter-api-python` is the one example that turns TLS on.

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Used by:** [ML inference and object detection](acap-cv-example-ml-inference-and-object-detection.md), [pose estimator](acap-cv-example-pose-estimator-flask.md), [QR decoder](acap-cv-example-opencv-qr-decoder.md), [Parameter API](acap-cv-example-parameter-api.md).
- **Runs under:** the Docker ACAP described in [Container-based ACAP applications](acap-container-applications.md); deployment steps in [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md).
- **Runtime internals:** [ACAP Runtime repository](acap-runtime-repository.md) and its concepts — [server configuration](acap-runtime-server-configuration-and-security.md), [ML API](acap-runtime-machine-learning-api.md), [video capture API](acap-runtime-video-capture-api.md), [Parameter API](acap-runtime-parameter-api.md) and [build and packaging](acap-runtime-build-and-image-packaging.md).
- **Native counterpart (synthesis):** the same capture/inference roles are served in-process by VDO and Larod in [ACAP Native SDK](axis-acap-native-sdk.md); model constraints for the DLPU are in [DLPU model constraints](axis-dlpu-model-constraints.md).

## Source coverage

- Inspected: the compose files, Dockerfiles, `Dockerfile.model`, env files and app code of the five Runtime-using examples, and the ML README's overview, requirements and hardware-acceleration sections.
- Local `raw/acap-runtime/` (revision `2.0.1-10-ge375fc9`) was consulted here only for the `-j`, `-m`, `-p`, `-c`, `-k` flags and the chip-id table; its source, protos, tests and build are compiled separately in [ACAP Runtime repository](acap-runtime-repository.md) and its concepts.
- Not verified: the contents of the `axisecp/acap-runtime` images on Docker Hub, the `/build/*/proto_utils` modules (their API is inferred from how the examples call them), and the larod enum name for chip `2` (the Runtime's tests treat it as CPU).

## Evidence class

Wiring, mounts, env values and the Dockerfile pattern are **Observed** by static inspection. The chip-id semantics are **Reported** by the Runtime README (id 12) and **Observed** only as a test constant for id 2. The "integration contract" reading is **Synthesis**. Nothing was executed.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Required components, at `12.10.0-3-g98b1ea7`.
[^cvex-ml-docs]: `minimal-ml-inference/README.md` §Overview, §Requirements, §Install the images (note on pulling the inference-server), §Hardware acceleration; `object-detector-python/README.md` §Overview; `pose-estimator-with-flask/README.md` §Overview, at `12.10.0-3-g98b1ea7`.
[^cvex-ml-config]: `minimal-ml-inference/docker-compose.yml::{simple-inference-client-app, inference-server, acap_dl-models}`; `minimal-ml-inference/Dockerfile::L3-41`; `minimal-ml-inference/config/env.aarch64.{cpu,artpec8}::INFERENCE_CHIP`; same keys in `object-detector-python/config/*` and `pose-estimator-with-flask/config/*`; `opencv-qr-decoder-python/Dockerfile::L12-40`; `Dockerfile.model` of each ML example; `*/app/*.py::INFERENCE_HOST`; at `12.10.0-3-g98b1ea7`.
[^cvex-runtime-readme]: `raw/acap-runtime/README.md` §Configuration (flag list, notes 1–3), §Chip id table, §TLS, revision `2.0.1-10-ge375fc9`.
