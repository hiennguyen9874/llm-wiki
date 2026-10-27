---
type: Concept
title: "CV SDK example: Monkey web server in a container"
description: "How the web-server example builds Monkey HTTP server 1.5.6 from source inside an arm64 Ubuntu 24.04 container, what monkey.patch changes, the port 2001 listener, the three C API demos, and the AXIS OS 12 reverse-proxy limitation."
tags: [edge-ai, axis, acap, web-server, monkey, docker, c, examples]
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
  - id: cvex-web-docs
    resource: ../raw/acap-computer-vision-sdk-examples/web-server/README.md
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "web-server README"
  - id: cvex-web-code
    resource: ../raw/acap-computer-vision-sdk-examples/web-server/Dockerfile
    scope: ../raw/acap-computer-vision-sdk-examples/
    kind: code
    revision: "12.10.0-3-g98b1ea7"
    title: "web-server Dockerfile, monkey.patch and docker-compose.yml"
---

# CV SDK example: Monkey web server in a container

`web-server` is the odd one out among the [CV SDK examples](acap-cv-sdk-examples-repository.md): no Python, no ACAP Runtime, no camera access. It packages the **Monkey HTTP server** (a lightweight C web server with a plugin and C API) as a container for the Docker ACAP, so a camera can serve web pages on **port 2001**. The repository holds only a `Dockerfile`, a compose file and a patch; the server source is cloned at build time. The README is titled for "ACAP version 4".[^cvex-web-docs][^cvex-web-code]

## Build

The Dockerfile starts `FROM ubuntu:24.04` with `--platform=linux/arm64/v8` and:[^cvex-web-code]

1. Installs build tools (`git make cmake pkg-config libglib2.0-dev libsystemd0`) and a second block with `g++-aarch64-linux-gnu` and `:arm64` variants of glib/libc/libsystemd after `dpkg --add-architecture arm64`. Because the image is already arm64 through `--platform`, the cross-toolchain block is redundant (**Synthesis**).
2. Copies `monkey.patch`, clones the upstream project at **branch `v1.5.6`** and runs `git apply ../monkey.patch`.
3. Runs `./configure` with prefix `/usr/local`, data/config dir `/usr/local/packages/monkey/html`, log dir `/tmp`, plug-in dir `/usr/local/packages/monkey/lib`, pid file `/tmp/monkey.pid`, then `make && make install`.
4. Copies the `monkey` library/binary into `examples/`, switches `LDFLAGS` to `LDLIBS` with `sed`, builds the examples and installs `hello`, `list` and `quiz` into `/usr/local/bin`.
5. Sets `LD_LIBRARY_PATH=/usr/local/lib`, copies the build context to `/tmp/` and starts `CMD monkey`.

Compose has one service, `monkey-app`, with `image: ${APP_NAME}` and `ports: "2001:2001"`; no volumes, environment or entrypoint.[^cvex-web-code]

## What `monkey.patch` changes

The 238-line patch touches six files (**Observed**, `monkey.patch`):[^cvex-web-code]

- `configure` — adds `-fcommon`, needed on GCC 10+ for tentative definitions in Monkey 1.5.6.
- `examples/Makefile` — links against `glib-2.0` and `monkey` via pkg-config, uses `LDLIBS`, `-ldl` and `-Wl,--no-as-needed,-rpath,$ORIGIN/lib`.
- `examples/{hello,list,quiz}.c` — replace a blocking `getchar()` wait with a GLib `GMainLoop`, add `openlog`/`syslog` start-up and error logging, and call `exit(0)` instead of returning 1 on init failure so a container does not exit non-zero.
- `src/mk_server.c` — hard-codes the `RLIMIT_NOFILE` capacity to `1048576` instead of `getrlimit()`, with the stated reason "to avoid unmanagable memory allocation".

In short: the patch makes an old upstream release build with a modern toolchain and behave well as a container's PID 1.

## Running and serving

The README says to build, `system prune`, `docker save | docker load`, then `docker … compose up` and open `http://<AXIS_DEVICE_IP>:2001`. The server's configured data directory is `/usr/local/packages/monkey/html`, and the repository ships no HTML, so what a browser shows is Monkey's stock default page (**Synthesis** from the configure flags). To run a C API demo, rebuild with another `CMD` (e.g. `CMD hello`) or add `entrypoint: hello` to the compose file; only one server process runs at a time on port 2001.[^cvex-web-docs]

Procedure details and requirements (ARTPEC-8 DLPU device, firmware 11.10+, Docker ACAP 3.0 with TLS) are in the [build and deploy workflow](acap-cv-examples-build-deploy-workflow.md); the proxy note refers to `~/.docker/config.json` on the workstation (see [Proxy configuration for ACAP builds and runtime](acap-proxy-configuration.md)).[^cvex-web-docs]

## Limitations stated and found

- **Reverse proxy (Reported).** From AXIS OS 12.0, a reverse-proxy configuration can no longer be set for a container because root access was removed, so this example works only with its default configuration — i.e. a direct, unauthenticated port. The README points to native examples (`web-server`, `web-server-using-fastcgi`), which use the manifest-based mechanisms in [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).[^cvex-web-docs]
- **Exposure (Observed).** The container listens on all interfaces on plain HTTP; there is no `EXPOSE`, TLS, authentication or logging setup in the repository.[^cvex-web-code]
- **Stale expected output (Observed).** The sample banner shows `arm-linux-gnueabihf-gcc … cortex-a9 9.3.0` and "Built Jun 18 2021", i.e. a 32-bit ARTPEC-7-era build, not the aarch64/Ubuntu 24.04 image this Dockerfile produces.
- **Documentation.** The README's file tree omits `monkey.patch`; the root README labels the example "C++" although the code is C.[^cvex-readme]

## Relationships

- **Part of:** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md).
- **Contrasts with:** the native web-server examples in [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md) and the Flask exposure in [pose estimator example](acap-cv-example-pose-estimator-flask.md).
- **Runs under:** [Container-based ACAP applications](acap-container-applications.md).

## Source coverage

- Inspected statically: `README.md`, `Dockerfile`, `docker-compose.yml`, `monkey.patch` in full structure (patch purpose summarized, not reproduced). The upstream Monkey source is cloned at build time and is **not** in the repository or in `raw/`; Monkey's behavior beyond the patch is unverified. Nothing was built or run.

## Evidence class

Build steps and patch contents are **Observed**; requirements, limitation and expected output are **Reported** by the README; the default-page and redundant-toolchain remarks are **Synthesis**.

[^cvex-readme]: `raw/acap-computer-vision-sdk-examples/README.md` §Example applications (web-server entry), at `12.10.0-3-g98b1ea7`.
[^cvex-web-docs]: `web-server/README.md` §intro, §Structure of this application, §Requirements, §Limitation, §How to run the code, §The expected output, §C API Examples, §Proxy settings, at `12.10.0-3-g98b1ea7`.
[^cvex-web-code]: `web-server/Dockerfile::L3-67`; `web-server/monkey.patch::{configure, examples/Makefile, examples/hello.c, examples/list.c, examples/quiz.c, src/mk_server.c}`; `web-server/docker-compose.yml`, at `12.10.0-3-g98b1ea7`.
