---
type: Concept
title: "Proxy configuration for ACAP builds and runtime"
description: "Three proxy layers for ACAP work: Docker daemon and build-environment proxy on the build machine, the device's own Docker daemon for container applications, and HTTP_PROXY/HTTPS_PROXY/NO_PROXY global proxies on the Axis device for applications that need internet access."
tags: [edge-ai, axis, acap, networking, docker]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T06:05:00Z }
stale_after: 2027-04-30
sources:
  - id: axis-proxy
    resource: ../raw/acap/how-to-guides/proxy/index.md
    scope: ../raw/acap/how-to-guides/proxy/
    kind: docs
    revision: "ACAP version 12"
    title: "Proxy | Axis developer documentation"
  - id: acap-vapix-access
    resource: ../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md
    scope: ../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/
    kind: docs
    revision: "ACAP version 12"
    title: "VAPIX access for ACAP applications | Axis developer documentation"
  - id: acap-container-build-run
    resource: ../raw/acap/reference/develop-container-applications/build-install-run/index.md
    scope: ../raw/acap/reference/develop-container-applications/build-install-run/
    kind: docs
    revision: "ACAP version 12"
    title: "Build, install, run | Axis developer documentation"
---

# Proxy configuration for ACAP builds and runtime

Proxy support for ACAP splits into independent layers that are configured in different places. On the build machine, the ACAP Native SDK build environment runs in Docker, so a proxied network requires proxy settings both for the Docker daemon and for the build/container environment. On the device, AXIS OS exposes global proxy settings as environment variables that ACAP applications pick up automatically. A third layer appears only with container-based applications: the Docker daemon running on the device needs its own proxy configuration before it can pull images. Configuring one layer does not configure the others.[^axis-proxy]

## Build-time proxy on the build machine

The ACAP Native SDK build environment uses Docker. When the build machine sits inside a network that uses a proxy, the Docker toolchain needs to be configured at two levels:[^axis-proxy]

| Level | Why it is needed | Where Axis points |
| --- | --- | --- |
| Docker daemon | To pull ACAP Native SDK images from Docker Hub through the proxy | Docker's **Daemon proxy configuration** guide |
| Docker build environment | To build and run containers when the `Dockerfile` installs Ubuntu packages with `apt` or downloads files with `curl` | Docker's **Use a proxy server with the Docker CLI** guide |

The daemon setting covers image pulls before any container exists; the build-environment setting covers commands executed inside the build. Both are delegated to Docker's own documentation rather than reproduced by Axis.[^axis-proxy]

## Runtime proxy on the Axis device

Proxy settings may also be needed on the Axis device to run an ACAP application successfully, especially when the device is behind a network proxy and the application requires internet access. The mechanism is a **global device proxy**: AXIS OS exposes the settings as environment variables that ACAP applications automatically pick up. Three proxy types can be configured:[^axis-proxy]

- `HTTP_PROXY`
- `HTTPS_PROXY`
- `NO_PROXY`

A global device proxy can be configured through either channel:[^axis-proxy]

1. The VAPIX **Network Settings API**, specifically its set-global-proxy-configuration operation.
2. The device network page at `http://<AXIS_DEVICE_IP>/index.html#system/network`, section **Global proxies**.

### Loopback exception for VAPIX service accounts

A global proxy also intercepts traffic the application sends to the device itself. Reaching the local virtual host `127.0.0.12` — the address used for VAPIX service-account calls — is possible only when `127.0.0.12` is present in the **`No proxy`** list.[^acap-vapix-access] Without that entry the loopback path is proxied away and the request fails. The credentials and call flow that depend on this are compiled in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).

### Third layer: the device's Docker daemon

Container-based applications add a proxy layer that the global device proxy does not cover. If the device sits behind a proxy, the **Docker daemon on the device** must itself be configured; Axis points to the Proxy Setup section of the Docker ACAP repository for that. Global `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY` variables are picked up by ACAP applications, whereas the device daemon proxies its own image pulls, so a container deployment can fail at pull time even when the global proxy is correct. The container deployment itself is described in [Container-based ACAP applications](acap-container-applications.md).[^acap-container-build-run]

## Coverage and limits

- Entry point and only artifact: `raw/acap/how-to-guides/proxy/index.md` (264 words, ACAP version 12). The whole page was read; it has no attachments or supporting files.
- The page delegates the concrete Docker daemon and Docker CLI proxy configuration to two external Docker guides, and the request schema to the external VAPIX Network Settings API page. Those details are **not compiled here** because they are not present in `raw/`.
- Supporting source: `raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md` (ACAP version 12), read only for the `No proxy` requirement for `127.0.0.12`; the rest of that guide is compiled in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
- Supporting source: `raw/acap/reference/develop-container-applications/build-install-run/index.md` (ACAP version 12), read only for the device-side Docker daemon proxy requirement; the container workflow is compiled in [Container-based ACAP applications](acap-container-applications.md).
- This concept is `draft` for that reason: the layer model, the three environment variables, and the two configuration channels are complete, but stepping through the exact proxy setup still requires the linked external instructions.

## Trust

All claims are **Reported** from official Axis documentation for ACAP version 12. None are **Observed** or **Reproduced**: no Docker daemon, build container, or Axis device was reconfigured during this ingest.

## Relationships

- **Used by** [Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers](acap-dev-environment-setup.md): the SDK arrives as a Docker image, so image pulls and `Dockerfile` commands are what the build-time proxy must cover.
- **Used by** [Chuẩn bị thiết bị Axis cho phát triển ACAP](axis-device-setup.md): global proxy is a device-side network setting independent of the host build setup.
- **Uses** VAPIX Network Settings API or the device web interface to set the global device proxy.
- **Relates to** [Build, install, and control ACAP applications](acap-build-install-control.md): the Dockerfile build path is the one most affected by a proxied build network.
- **Affects** [VAPIX access from ACAP applications](acap-vapix-service-account-access.md): the `No proxy` list must contain `127.0.0.12`, or an application's VAPIX calls never reach the local virtual host.
- **Affects** [Container-based ACAP applications](acap-container-applications.md): the device's Docker daemon needs separate proxy configuration before it can pull container images.

[^axis-proxy]: Official documentation: [Proxy — Axis developer documentation](../raw/acap/how-to-guides/proxy/index.md), ACAP version 12; §Proxy in build time › Docker daemon proxy, §Proxy in build time › Docker build environment, §Proxy in runtime, §Proxy in runtime › Configure global device proxy.

[^acap-vapix-access]: Official documentation: [VAPIX access for ACAP applications — Axis developer documentation](../raw/acap/how-to-guides/VAPIX-access-for-ACAP-applications/index.md), §Make a VAPIX call › info note on the global device proxy.

[^acap-container-build-run]: Official documentation: [Build, install, run — Axis developer documentation](../raw/acap/reference/develop-container-applications/build-install-run/index.md), §ACAP Computer Vision SDK incl. Docker ACAP › §Install and run › §Configure network proxy settings.
