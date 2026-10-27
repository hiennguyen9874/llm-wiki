---
type: Concept
title: "Container-based ACAP applications: Docker ACAP, Docker Compose ACAP and the Computer Vision SDK"
description: "Legacy container path for Axis apps: Docker-based build on the Computer Vision SDK image, image transfer and remote run through the Docker ACAP, TLS prerequisite, and the Docker Compose ACAP variant."
tags: [edge-ai, axis, acap, docker, containers, lifecycle]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-container-build-run
    resource: ../raw/acap/reference/develop-container-applications/build-install-run/index.md
    scope: ../raw/acap/reference/develop-container-applications/build-install-run/
    kind: docs
    revision: "ACAP version 12"
    title: "Build, install, run | Axis developer documentation"
---

# Container-based ACAP applications: Docker ACAP, Docker Compose ACAP and the Computer Vision SDK

Container-based ACAP is the older of Axis's two application models. The application is a Docker image built on the **ACAP Computer Vision SDK** and runs on the camera under a separate ACAP that provides the Docker daemon — the **Docker ACAP** — with the `docker` client normally driving it from another machine over TLS. Axis now marks this path as legacy: new products released on AXIS OS 12.x have no container support, existing container-capable products are supported until end of 2031, the Computer Vision SDK was archived at AXIS OS 12.0 with its utilities moved to ACAP Runtime, and the recommended model is the native `.eap` application of the Native SDK. The page therefore matters for maintaining and retiring container deployments, not for new designs.[^acap-container-build-run]

## Lifecycle status

The vendor banner that fronts this reference section states the whole constraint set in four points:[^acap-container-build-run]

| Statement | Consequence |
| --- | --- |
| New Axis products released on AXIS OS 12.x will not have container support | Container support is a property of the hardware generation, not only of the OS version |
| All products with existing container support remain supported until end of 2031, when AXIS OS 2026 LTS reaches end of life | A hard horizon for container deployments; it is tied to an LTS date, not to a feature roadmap |
| ACAP Native SDK is the recommended way to build analytics, computer vision and machine learning applications on Axis devices | New development belongs on the native model, not on containers |
| The ACAP Computer Vision SDK is archived; utility libraries and scripts now live in ACAP Runtime | The image lineage endpoint is ACAP Runtime plus the `acap-computer-vision-sdk-examples` repository |

The same banner appears on the device-compatibility page, so both halves of the container reference carry the deprecation statement; the device and image matrix itself is in [container application compatibility](acap-container-compatibility.md).[^acap-container-build-run]

## Build

Because the application is a container, the toolchain is Docker and a build is only needed when the application uses a **custom image**. Axis draws the line explicitly: if the image is readily available, no build step exists at all. Computer Vision functionality is reached by basing the image on the ACAP Computer Vision SDK image published on Docker Hub (`axisecp/acap-computer-vision-sdk`), and the repository `acap-computer-vision-sdk-examples` carries the worked custom-image examples; generic instructions for writing a Docker image are delegated to Docker's own documentation.[^acap-container-build-run]

This is the same Docker-on-the-build-machine model used by the Native SDK, but with a different output: an image that will run in a container on the device rather than a `.eap` package installed by the application framework. The native build and packaging flow is in [Build, install, and control ACAP applications](acap-build-install-control.md), and the shared build environment in [Môi trường phát triển ACAP](acap-dev-environment-setup.md).[^acap-container-build-run]

## Install and run

### Prerequisite: Docker ACAP and TLS

Installing or running a container application requires the **Docker ACAP** to be installed on the camera. The Docker ACAP ships with TLS authentication **enabled by default**, so certificates must be added to the camera before the ACAP can be started; the examples assume TLS is active. A setting exists to disable TLS authentication, and Axis describes using it as *extremely insecure*.[^acap-container-build-run]

The two practical consequences are that a container deployment starts with a certificate step that the page leaves to the Docker ACAP repository, and that every command below carries `--tlsverify` and port `2376` — the TLS-authenticated Docker daemon port — rather than plain TCP.[^acap-container-build-run]

### Getting the image onto the device

The client connects to the daemon on the camera with the `-H` flag instead of a local socket, so the image must first reach the device. Axis documents two routes:[^acap-container-build-run]

| Route | Mechanism | Command |
| --- | --- | --- |
| Container registry | Build and push the image to a registry, then pull it on the camera | `docker push $IMAGE_NAME`; `docker --tlsverify -H tcp://$CAMERA_IP:2376 pull $IMAGE_NAME` |
| Peer-to-peer | Save the image locally and pipe it into the device's daemon | `docker save $IMAGE_NAME \| docker --tlsverify -H tcp://$CAMERA_IP:2376 load` |

### Running it

Once the image is on the device, the application is started remotely through the same `-H` connection:[^acap-container-build-run]

```sh
# single application image
docker --tlsverify -H tcp://$CAMERA_IP:2376 run $IMAGE_NAME

# application described by a docker-compose.yml
docker-compose --tlsverify -H tcp://$CAMERA_IP:2376 up
docker-compose --tlsverify -H tcp://$CAMERA_IP:2376 down -v
```

A `docker-compose.yml` is recommended when the application depends on environment variables, mounts and devices, because those are preserved in the compose description. `down -v` also removes the containers, networks **and volumes** the application created, so it is the matching cleanup command rather than a stop command.[^acap-container-build-run]

### Docker daemon proxy

If the device sits behind a proxy, the **Docker daemon on the device** must be configured, using the Proxy Setup section of the Docker ACAP repository. This is a third proxy layer, distinct from the build-machine Docker daemon and build environment and from the device-wide `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` variables described in [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md).[^acap-container-build-run]

## Docker Compose ACAP

The **Docker Compose ACAP** is a second, larger ACAP: it bundles not only the Docker daemon but also the Docker client and Compose CLI. With it installed, Docker commands run **on the camera** instead of from another machine, which is why the package is significantly bigger. Its stated main purpose is not interactive use but enabling containers to be started *by a native ACAP application*, as shown by the `container-example` in the `acap-native-sdk-examples` repository — an application that must itself launch containers needs a Docker client on the device.[^acap-container-build-run]

The two ACAPs therefore answer different deployment shapes:

| | Docker ACAP | Docker Compose ACAP |
| --- | --- | --- |
| Contains | Docker daemon | Docker daemon, Docker client, Compose CLI |
| Typical driver | `docker` client on a workstation over TLS | Commands on the camera, or a native ACAP calling Docker |
| Size | Smaller | Significantly larger |
| Fits | Standalone container application | Containers orchestrated from a native ACAP application |

## Source coverage

- Entry point: `raw/acap/reference/develop-container-applications/build-install-run/index.md`, one file, 711 words, site `developer.axis.com`, revision "ACAP version 12". No assets or attachments in the folder. Every section was read: lifecycle banner, §ACAP Computer Vision SDK incl. Docker ACAP (§Build, §Install and run, §Configure network proxy settings), §The Docker Compose ACAP.
- Supporting artifacts referenced by the source but **outside** the ingested scope: `raw/docker-compose-acap/` is now compiled as its own source in [Docker Compose ACAP repository](docker-compose-acap-repository.md) (revision `4.0.0-2-g985c8ce`), and `raw/acap-native-sdk-examples/container-example/` is covered by [ACAP example: containers from a native ACAP](acap-example-container-in-native-acap.md). No implementation detail from either is asserted on this page; this page rests only on the vendor documentation page.
- Excluded: the external links to Docker Hub (`axisecp/acap-computer-vision-sdk`), the `docker-acap` and `docker-compose-acap` repositories, `ACAP Runtime`, Docker's sample-application guide, and the AXIS OS support/end-of-life pages. All remain outside this page's scope and unverified here; the examples repository (`raw/acap-computer-vision-sdk-examples/`) is compiled in [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- Limits: the page does not state the minimum AXIS OS version for the Docker ACAP, how certificates are generated or installed, how a container application is registered in the device UI, or how containers appear to the AXIS OS application framework once running. It also gives no resource limits for containers and no guidance on migrating an existing container application to the Native SDK.

## Implementation of the Docker Compose ACAP

The repository behind the Docker Compose ACAP is documented in [Docker Compose ACAP repository](docker-compose-acap-repository.md): release 4.0.0 runs **rootless** dockerd 29.8.1 (AXIS OS 12.0 or newer, `aarch64` devices), while rootful releases 1.5.0 and 2.0.0 and the rootless 3.0.3 serve AXIS OS 10.12 to 11.x. Its TLS defaults, certificate upload endpoint and `DOCKER_INSECURE_NO_IPTABLES_RAW=1` networking caveat refine the "TLS enabled by default" statement above for the Compose variant; see [certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md) and [daemon runtime](docker-compose-acap-daemon-runtime.md). Those findings come from the repository (Observed/Reported by its README), not from the vendor page cited on this page.

## Evidence class

Commands, the TLS default, the registry and save/load routes, the Compose recommendations, and the division of labour between the two ACAPs are **Reported** from official Axis documentation. The lifecycle statements are also **Reported**, but now from the primary vendor reference rather than from secondary research. Nothing is **Reproduced**: no image was built, no certificate was installed, and no `docker` command was executed against a device in this ingest.

## Relationships

- **Superseded by** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): Axis recommends the native `.eap` model for analytics, computer vision and ML applications, and the container path is deprecated since ACAP 12.
- **Constrained by** [container application compatibility](acap-container-compatibility.md): only specific devices and AXIS OS versions support containers, and the legacy image matrix pins each ACAP computer vision SDK image to an AXIS OS range.
- **Alternative to** [Build, install, and control ACAP applications](acap-build-install-control.md): the same Docker build machine produces either a container image or a `.eap` package, and the install/control channels differ completely.
- **Affected by** [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md): the device's Docker daemon needs its own proxy configuration, separate from the build-machine and device-wide proxy layers.
- **Requires** the Docker ACAP plus TLS certificates on the device before any container can start; certificate issuance is delegated to the external Docker ACAP repository.
- **Hosts** the containerized ACAP Runtime gRPC service ([ACAP Runtime repository](acap-runtime-repository.md)), whose image carries no default flags and must be started with chip, model and TLS options.
- **Uses** the archived ACAP Computer Vision SDK image lineage, whose utilities and scripts moved to ACAP Runtime at AXIS OS 12.0.
- **Exemplified by** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md): the worked custom-image examples this page refers to, with the concrete commands in [Building and deploying the CV SDK container examples](acap-cv-examples-build-deploy-workflow.md) and the Runtime wiring in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md).
- **Uses** the `container-example` from [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md) as the documented case of a native ACAP launching containers with the Docker Compose ACAP.
- **Constrains** migration planning: the end-of-2031 support horizon is the deadline for moving a container deployment onto the Native SDK, as weighed in [Hướng triển khai custom AI trên Axis](axis-edge-ai-adoption-guide.md).
- **Detailed by** [Docker Compose ACAP repository](docker-compose-acap-repository.md): the code and build of the Docker Compose ACAP, including its rootless operation and certificate endpoint.
- **Contrast** [ACAP example: containers from a native ACAP](acap-example-container-in-native-acap.md): the native-SDK `container-example` carries a docker-saved image inside an `.eap` and starts it through the Docker Compose ACAP.

[^acap-container-build-run]: Official documentation: [Build, install, run — Axis developer documentation](../raw/acap/reference/develop-container-applications/build-install-run/index.md), whole page, ACAP version 12: warning banner "Note on container applications", §ACAP Computer Vision SDK incl. Docker ACAP (§Build, §Install and run incl. Docker ACAP/TLS note, registry and `save`/`load` commands, `run` and `docker-compose` commands, §Configure network proxy settings), §The Docker Compose ACAP.
