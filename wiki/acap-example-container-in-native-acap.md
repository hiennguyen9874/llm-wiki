---
type: Concept
title: "ACAP example: running containers from a native ACAP (container-example)"
description: "How container-example embeds a docker-saved Alpine image in a native .eap and uses post-install, start and pre-uninstall scripts with the external Docker Compose ACAP to run a netcat web service on port 8080, with its lifecycle, prerequisites and defects."
tags: [edge-ai, axis, acap, examples, containers, docker-compose]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP example: running containers from a native ACAP

`container-example` shows a native ACAP that carries a container image and starts it through the Docker Compose ACAP already installed on the device. The README warns that container solutions are deprecated from AXIS OS 12.0 and that armv7hf is unsupported after 11.11, matching the cut-offs in [Container application compatibility](acap-container-compatibility.md).[^native-examples]

## Build

- Prepare the image first: `docker pull --platform="linux/arm64/v8" alpine:3.19.1 && docker save -o alpine.tar alpine:3.19.1`. `alpine.tar` is gitignored.
- The Dockerfile (default `ARCH=aarch64`, hard-coded `${REPO}/acap-native-sdk`) copies the example root and runs `acap-build . -a alpine.tar -a docker-compose.yml`. The `Makefile` has an empty `all:` target; the expected package is `Container_Example_1_0_0_aarch64.eap`.
- The example breaks the standard layout: `Makefile`, `manifest.json`, `LICENSE` and `postinstall.sh` sit at the example root.[^native-examples]

## Lifecycle

| Phase | Action |
| --- | --- |
| Install | manifest `installation.postInstallScript` → `postinstall.sh` runs `docker load -i alpine.tar` |
| Start | executable `containerExample` changes to its own directory, installs a `trap` for INT/TERM that runs `docker compose down`, runs `docker compose up`, then sleeps in a loop (604800 s) |
| Stop | SIGTERM trap → `docker compose down` |
| Uninstall | `uninstallation.preUninstallScript` → `preuninstall.sh` runs `docker image rm alpine:3.19.1` |

The compose file defines one service, `alpine`, running `while true; do printf 'HTTP/1.1 200 OK\n\nHello from an ACAP\!' | nc -l -p 80; done`, mapped `8080:80`. Browsing to `http://<AXIS_DEVICE_IP>:8080` shows "Hello from an ACAP!".[^native-examples]

## Prerequisites and defects

- Requires the **Docker Compose ACAP** 3.0+ with `IPCSocket=yes` (TCP optional, TLS recommended) and a container-capable device; background in [Container-based ACAP applications](acap-container-applications.md).
- **Observed:** `docker compose up` runs in the foreground, so the trailing sleep loop is only reached if compose exits, and the shell trap may be deferred while the foreground child runs; `postinstall.sh` is committed non-executable while `preuninstall.sh` is executable; the Makefile and manifest keep no `resources`.
- Not verified: whether `docker compose up` stops cleanly on SIGTERM on a device.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Depends on** the external Docker Compose ACAP, whose repository is compiled in [Docker Compose ACAP repository](docker-compose-acap-repository.md): its `IPCSocket` setting, the `addon` group requirement for CLI callers and the rootless 4.0.0 requirement of AXIS OS 12.0 bear on how this example's scripts reach Docker. This is a link from the other repository's README; the example's own scripts were not re-read against it here.
- **Bridges to** the legacy container path covered by [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md); the README's own deprecation note is the vendor position.

[^native-examples]: `container-example/{README.md,Dockerfile,Makefile,manifest.json,postinstall.sh,preuninstall.sh,containerExample,docker-compose.yml,.gitignore}`; `.github/workflows/container-example.yml`.
