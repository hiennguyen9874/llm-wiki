---
type: Concept
title: "Docker Compose ACAP build and packaging: Dockerfile stages, bundled binaries and unpinned inputs"
description: "How the Docker Compose ACAP EAP is built: the Native SDK 12.0.0 base image, procps and nsenter compiled from source, Docker 29.8.1, Compose v5.5.0, rootlesskit and slirp4netns downloaded unchecked, the acap-build packaging step, build.sh, sanitizer scope and the build defects."
tags: [edge-ai, axis, acap, docker, build, dockerfile, packaging, supply-chain]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-dockerfile
    resource: ../raw/docker-compose-acap/Dockerfile
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe)"
    title: "Dockerfile — multi-stage EAP build"
  - id: dc-buildsh
    resource: ../raw/docker-compose-acap/build.sh
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "build.sh — local buildx wrapper"
  - id: dc-makefile
    resource: ../raw/docker-compose-acap/app/Makefile
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "app/Makefile — wrapper binary build"
  - id: dc-buildcfg
    resource: ../raw/docker-compose-acap/.hadolint.yaml
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: ".hadolint.yaml and other build-side config"
  - id: dc-readme
    resource: ../raw/docker-compose-acap/README.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "README"
---

# Docker Compose ACAP build and packaging: Dockerfile stages, bundled binaries and unpinned inputs

The EAP is produced entirely inside Docker: a multi-stage `Dockerfile` starts from the **ACAP Native SDK** image, compiles two small utilities, downloads the Docker and rootless tooling as prebuilt binaries, builds the C wrapper with the app `Makefile`, and runs `acap-build` to package everything. The default target emits an **unsigned** `.eap`; signing happens only in CI ([CI and maintenance](docker-compose-acap-ci-and-maintenance.md)).[^dc-dockerfile] The documented command is `docker buildx build --file Dockerfile --build-arg ARCH=<ARCH> --output <build-folder> .`, with `--build-arg BUILD_WITH_SANITIZERS=1` as the one build option.[^dc-readme]

## Stages

| Stage | Base | Does |
| --- | --- | --- |
| `sdk_image` | `axisecp/acap-native-sdk:12.0.0-<ARCH>-ubuntu24.04` (tag only) | SDK toolchain; see [ACAP Native SDK image assembly](acap-native-sdk-image-assembly.md) |
| `build_image` | `sdk_image` | installs automake, autopoint, gettext, git, libtool, bison, flex |
| `ps` | `build_image` | clones procps `v4.0.7` (shallow), cross-compiles `src/ps/pscommand`, strips it |
| `nsenter` | `build_image` | clones util-linux `v2.42.3` (full clone), builds `nsenter` |
| `docker_binaries` | `sdk_image` | downloads `slirp4netns` 1.3.5, the Docker static tarball 29.8.1 (`docker`, `dockerd`, `docker-init`, `docker-proxy`), Compose v5.5.0 and the rootless-extras tarball (rootlesskit) |
| `build` | `sdk_image` | copies `app/`, `ps`, `nsenter` and the seven downloaded binaries, then `acap-build` with each bundled binary as an extra file; `ENTRYPOINT` is the SDK's `eap-install.sh` |
| `binaries` (default) | `scratch` | copies `/opt/app/*.eap` out |

[^dc-dockerfile]

## Bundled content

The package carries the wrapper, `docker`, `dockerd`, `docker-compose`, `docker-init`, `docker-proxy`, `ps`, `slirp4netns`, `rootlesskit` and `nsenter`; **buildx is not bundled**, as the README states.[^dc-dockerfile][^dc-readme] The wrapper links GLib, GIO, `axparameter`, `axstorage` and `fcgi` and is built with `-Wall -Werror`; with `BUILD_WITH_SANITIZERS` it adds address, leak and undefined-behaviour sanitizers.[^dc-makefile]

## Version inputs

`DOCKER_IMAGE_VERSION=29.8.1`, `DOCKER_COMPOSE_VERSION=v5.5.0`, `PROCPS_VERSION=v4.0.7`, `NSENTER_VERSION=v2.42.3`, `SLIRP4NETNS_VERSION=1.3.5`, `VERSION=12.0.0`, `UBUNTU_VERSION=24.04`, `REPO=axisecp`, `ARCH=armv7hf`. rootlesskit has no independent pin: `ROOTLESS_EXTRAS_VERSION` equals the Docker version, so a dockerd bump moves rootlesskit with it.[^dc-dockerfile]

## `build.sh`

A local wrapper (`#!/bin/bash -eu`) that accepts `armv7hf` or `aarch64`, optional `--plain`, `--cache` and `--image-tag`, and runs `docker buildx build` with `ARCH`, proxy and sanitizer build arguments and `--output build-<arch>`. `--no-cache` is the default and the image tag is effectively unused because the output is local files; the default tag `docker-acap-with-compose:1.0` is stale.[^dc-buildsh]

## Defects and supply-chain gaps (Observed)

1. **No integrity checks:** the Docker, Compose, rootless-extras and slirp4netns downloads have no checksum or signature verification; `curl` runs without `-f`, so an HTTP error page can be saved and made executable, failing only later.[^dc-dockerfile]
2. **Mutable inputs:** the base image has a tag but no digest, apt packages are unpinned (hadolint DL3008 is ignored), and the Compose and procps references use `v` prefixes while slirp4netns does not.[^dc-dockerfile][^dc-buildcfg]
3. **Stale `ARCH` default:** `ARG ARCH=armv7hf` is paired with an SDK 12.0.0 tag, but AXIS OS 12 supports only aarch64, so a plain `docker build` is likely to fail; the README still presents `<ARCH>` as either. CI builds both architectures regardless.[^dc-dockerfile][^dc-readme]
4. **Masked errors:** none of the heredoc `RUN` blocks use `set -e`, so a failing `apt-get update`, `curl` or `./configure` can be hidden by a later successful command; an unsupported `ARCH` yields an empty download path rather than an error.[^dc-dockerfile]
5. **Brittle output:** `COPY --from=build /opt/app/*.eap /` expects exactly one EAP; `ln -s` without `-f` fails if the link exists.[^dc-dockerfile]
6. **Sanitizer scope:** only the wrapper is instrumented; the compiled `ps`, `nsenter` and all downloaded binaries are not, so the README's wording overstates coverage.[^dc-dockerfile][^dc-makefile]
7. **Context hygiene:** `.dockerignore` excludes only `build-*`, `tmp` and `.vscode`, so `.git` and `.github` enter the build context; `.gitignore` still lists Docker binary names from an older layout.[^dc-buildcfg]
8. **Manifest version drift:** `embeddedSdkVersion` 3.0 in the manifest versus SDK 12.0.0 in the build ([repository overview](docker-compose-acap-repository.md)).

## Evidence class

Stages, versions and defects are **Observed** by static reading. The stated release versions are **Reported** by the README and agree with the Dockerfile. No build was run, no image was pulled and no binary was downloaded, so the claim that a plain `docker build` fails is **Synthesis**.

## Relationships

- **Part of** [Docker Compose ACAP repository](docker-compose-acap-repository.md).
- **Depends on** [ACAP Native SDK repository](acap-native-sdk-repository.md) and its published image; SDK conventions are in [ACAP examples build and manifest conventions](acap-examples-build-and-manifest-conventions.md).
- **Produces** the package whose runtime is in [Daemon runtime](docker-compose-acap-daemon-runtime.md).
- **Compared with** the similar two-Dockerfile supply-chain observations in [ACAP 3 SDK image assembly](acap3-sdk-image-assembly.md).
- **Signed by** the CI path in [CI and maintenance](docker-compose-acap-ci-and-maintenance.md); manual signing background is in [ACAP application signing](acap-application-signing.md).

[^dc-dockerfile]: `Dockerfile` lines 3–14 (ARGs), stage `sdk_image` through `binaries` (`FROM` lines and the `RUN` blocks for procps, util-linux, downloads, `acap-build`), `ENTRYPOINT`, final `COPY --from=build /opt/app/*.eap`.
[^dc-buildsh]: `build.sh` (argument validation, `--plain`/`--cache`/`--image-tag`, final `docker buildx build`).
[^dc-makefile]: `app/Makefile::{PKGS, OBJS, BUILD_WITH_SANITIZERS}`.
[^dc-buildcfg]: `.hadolint.yaml` (ignored rules DL3003, DL3008, DL3018, DL3019, SC2103, SC2164); `.dockerignore`; `.gitignore`; `.editorconfig`; `.clang-format` (LLVM-based, 4 spaces, 100 columns).
[^dc-readme]: `README.md` §Building the application and §Build options; §Overview Known Issues (buildx).
