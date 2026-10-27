---
type: Concept
title: "Building and deploying the CV SDK container examples to a camera"
description: "The common procedure the container examples document: device and workstation requirements, exporting image names, qemu cross-build, TLS prune/save/load to the Docker ACAP, compose up and down, plus the README pitfalls that break it."
tags: [edge-ai, axis, acap, docker, docker-compose, deployment, procedure]
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
  - id: cvex-ml-docs
    resource: ../raw/acap-computer-vision-sdk-examples/minimal-ml-inference/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "minimal-ml-inference README (requirements and run procedure)"
  - id: cvex-run-docs
    resource: ../raw/acap-computer-vision-sdk-examples/hello-world-python/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "hello-world-python and other example READMEs (run procedure)"
---

# Building and deploying the CV SDK container examples to a camera

Per the repository README, all examples use the Docker framework and carry step-by-step instructions in their own README.[^cvex-readme] Every example in the [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md) is deployed the same way: build the image on a workstation (cross-building for `linux/arm64/v8` with qemu), clear the camera's Docker store, push the image directly into the camera's Docker daemon over TLS, and run it with Docker Compose through the same remote connection. The READMEs repeat the procedure with small differences in variables. It is the concrete, command-level form of the generic flow in [Container-based ACAP applications](acap-container-applications.md).[^cvex-ml-docs][^cvex-run-docs]

## Requirements

All example READMEs list the same prerequisites (**Reported**):[^cvex-ml-docs]

- **Device:** ARTPEC-8 DLPU camera (example given: Q1656), firmware 11.10 or higher, and **Docker ACAP 3.0** installed and started, using TLS with TCP and IPC socket and an SD card as storage.
- **Workstation:** Docker Desktop 4.11.1+, or Docker Engine 20.10.17+ with BuildKit and Docker Compose 1.29.2+.
- **Device setting:** under the device's Apps page, enable **Allow unsigned apps** before loading images.

The repository-level statements — `aarch64` only, container support ending with AXIS OS 12.x products and the 2031 horizon — are in the [repository overview](acap-cv-sdk-examples-repository.md); the wider device matrix is in [Container application compatibility](acap-container-compatibility.md). The README requirement that the chip be ARTPEC-8 is stricter than the example env files, which include a `cpu` variant for the ML examples (see [Runtime architecture](acap-cv-examples-runtime-architecture.md)).

## Procedure

```sh
# 1. names (shell variables are read by docker-compose.yml)
export APP_NAME=acap4-minimal-ml-inference      # per example
export MODEL_NAME=acap-dl-models                # ML examples only
export CHIP=artpec8                             # 'artpec8' or 'cpu'; ML examples only

# 2. cross-build support and build
docker run --rm --privileged multiarch/qemu-user-static --credential yes --persistent yes
docker build --tag $APP_NAME .
docker build --file Dockerfile.model --tag $MODEL_NAME .   # ML examples only

# 3. clear the device Docker store, over TLS on 2376
DEVICE_IP=<camera IP>; DOCKER_PORT=2376
docker --tlsverify --host tcp://$DEVICE_IP:$DOCKER_PORT system prune --all --force

# 4. transfer directly (no registry)
docker save $APP_NAME | docker --tlsverify --host tcp://$DEVICE_IP:$DOCKER_PORT load
docker save $MODEL_NAME | docker --tlsverify --host tcp://$DEVICE_IP:$DOCKER_PORT load

# 5. run and clean up
docker --tlsverify --host tcp://$DEVICE_IP:$DOCKER_PORT compose --env-file ./config/env.aarch64.$CHIP up
docker --tlsverify --host tcp://$DEVICE_IP:$DOCKER_PORT compose --env-file ./config/env.aarch64.$CHIP down --volumes
```

Notes that the READMEs state or that follow from the files:[^cvex-ml-docs][^cvex-run-docs]

- **Variable scope.** Compose substitutes `${APP_NAME}` and `${MODEL_NAME}` from the *workstation* shell, since the `docker` client runs there; examples without an `--env-file` (hello-world, QR, parameter, web-server) rely on `APP_NAME` being exported.
- **Prune is destructive.** `system prune --all --force` removes every unused image, container and network on the camera's Docker daemon, not just this example's.
- **Direct transfer.** The `save | load` pipe is the peer-to-peer route also described in [Container-based ACAP applications](acap-container-applications.md); a registry route is possible but not documented in the examples.
- **Runtime image.** If the inference-server image is absent on the device it is pulled from Docker Hub by `compose up`; on pull failure, pull it on the workstation and load it to the device.
- **TLS trouble.** The README points to the Docker ACAP repository's TLS chapter and the `DOCKER_CERT_PATH` variable; the examples do not explain certificate creation.
- **Cleanup.** `down --volumes` also deletes the named volumes (`inference-server`, `acap_dl-models`), which matters because the volumes hold the Unix socket and the model.

## Where the READMEs diverge from the files

These are **Observed** mismatches that cause confusion when following the text:

| README statement | What the files show | Where |
| --- | --- | --- |
| "`CHIP` … to select the right manifest file" at build time | No Dockerfile declares a `CHIP` build argument; the chip is chosen at run time by the env file | `minimal-ml-inference`, `pose-estimator-with-flask` |
| Expected-output snippet puts `--env-file`/`--file` before `compose` and omits `compose` | Not valid Docker CLI as written; the procedure above is the valid form | `object-detector-python` |
| Service-name output such as `object-detector_1` | Compose service is `object-detector-python` | `object-detector-python` |
| Example structure lists `simple_inference.py` at the example root | The file is `app/simple_inference.py` | `minimal-ml-inference` |

Further README-versus-code mismatches per example are on the example pages linked from the [repository overview](acap-cv-sdk-examples-repository.md). CI builds the same images with `docker build` only; it does not exercise steps 3–5 ([CI and maintenance](acap-cv-examples-ci-and-maintenance.md)).

## Relationships

- **Instantiates:** the generic Docker ACAP path in [Container-based ACAP applications](acap-container-applications.md), including its TLS prerequisite.
- **Contrasts with:** the `.eap` build/install flow of [Build, install, and control ACAP applications](acap-build-install-control.md); signing there does not apply here, but unsigned-app enablement does.
- **Proxy-restricted networks:** see [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md) for the device Docker daemon proxy layer.

## Source coverage

- Inspected: the "How to run the code" sections of all seven example READMEs, the requirements blocks, and the compose files' variable use. The commands above are the common form; per-example differences (variables, model build, expected output) are on the example pages.
- Not verified: the Docker ACAP repository's installation and TLS instructions (external), and any device behavior; no command was executed.

## Evidence class

The procedure and requirements are **Reported** (vendor READMEs); the divergence table is **Observed**; the variable-scope and prune consequences are **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Getting started, §Requirements, at `12.10.0-3-g98b1ea7`.
[^cvex-ml-docs]: `minimal-ml-inference/README.md` §Requirements, §How to run the code (§Build the Docker images, §Set your device IP address and clear Docker memory, §Install the images, §Run the containers); `object-detector-python/README.md` §The expected output; `pose-estimator-with-flask/README.md` §Build the Docker images; `Dockerfile`s for the `CHIP` argument check; at `12.10.0-3-g98b1ea7`.
[^cvex-run-docs]: `hello-world-python/README.md::L26-89`, `opencv-qr-decoder-python/README.md::L41-90`, `parameter-api-python/README.md::L45-93`, `web-server/README.md` §How to run the code; at `12.10.0-3-g98b1ea7`.
