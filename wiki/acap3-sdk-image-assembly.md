---
type: Concept
title: "ACAP 3 SDK image assembly: stages, environment patching and reproducibility gaps"
description: "How Dockerfile.aarch64 and Dockerfile.armv7hf build the ACAP SDK 3.5 image: acap-api and acap-toolchain 3.5 overlaid on ubuntu:22.04, installed tools, protoc and khrplatform.h downloads, environment-setup sed patches, the three-line arch difference, and unpinned or unchecked inputs."
tags: [edge-ai, axis, acap, sdk-3, docker, toolchain, reproducibility]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T19:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap3-sdk-repo
    resource: ../raw/acap3-sdk/README.md
    scope: ../raw/acap3-sdk/
    kind: code
    revision: "3.5-aarch64-28-g4e4fe04 (4e4fe046e47dcbbfcdf6bd14b0473e90d8ce5e50, 2026-10-01)"
    title: "AxisCommunications/acap3-sdk (git checkout)"
---

# ACAP 3 SDK image assembly: stages, environment patching and reproducibility gaps

Each Dockerfile is a three-stage build that creates the ACAP SDK 3.5 developer image by copying a ready-made SDK tree and API sysroot out of two Axis images into a fresh Ubuntu 22.04 base, installing host tools, then patching the SDK's `environment-setup*` script in place. Nothing is compiled; the SDK payload is not in the repository.[^acap3-sdk-repo] Context: [ACAP 3 SDK repository](acap3-sdk-repository.md). Evidence class: **Observed** from static reading and `diff`; nothing was built.

## The two files differ in three lines

`diff Dockerfile.aarch64 Dockerfile.armv7hf` shows only: line 2 `ARG ARCH=aarch64` vs `armv7hf`; line 16 `crossbuild-essential-arm64` vs `crossbuild-essential-armhf`; line 51 the repeated `ARG ARCH`. `ARCH` is redeclared on line 51 because a global `ARG` declared before `FROM` is not visible inside a stage (comment-less; the repo history says "Dockerfile requires ARCH to be defined again in new context", `1323e79`). Everything else (API/toolchain tags, sysroot paths, patches) follows from `ARCH`.[^acap3-sdk-repo] Unlike the Native SDK pair ([image assembly](acap-native-sdk-image-assembly.md)), the armv7hf file has no extra compiler-flag overrides.

## Build arguments

| Arg | Default | Role |
| --- | --- | --- |
| `ARCH` | `aarch64` / `armv7hf` | Target architecture; selects image tags and sysroot directory |
| `API_VERSION` | `3.5` | Tag of `axisecp/acap-api` |
| `TOOLCHAIN_VERSION` | `3.5` | Tag of `axisecp/acap-toolchain` |
| `TOOLCHAINS_UBUNTU_VERSION` | `20.04` | Ubuntu suffix of the api and toolchain tags |
| `SDK_UBUNTU_VERSION` | `22.04` | Final-stage base `ubuntu:<version>` |
| `REPO` | `axisecp` | Docker Hub organization of the inputs |
| `AXPROTOC` | `3.13.0` | `protoc` version to download |
| `KHR_DIR` | `/opt/axis/acapsdk/sysroots/${ARCH}/usr/include/KHR` | Destination for `khrplatform.h` |

There is no `ENV` instruction; the build environment comes from the sourced SDK script.[^acap3-sdk-repo]

## Stages

1. `api` = `axisecp/acap-api:3.5-<arch>-ubuntu20.04` (line 9).
2. `toolchain` = `axisecp/acap-toolchain:3.5-<arch>-ubuntu20.04` (line 10).
3. Final stage `ubuntu:22.04` (line 11). The `20.04` in the input tags names the distro those images were built on, not the final base; the two Ubuntu versions are independent args.

## What the final stage does (in order)

- **Host packages** (`apt-get install --no-install-recommends`, lines 15-26): the arch-specific `crossbuild-essential-*`, `make`, `pkg-config`, `python3-pip`, `python3-jsonschema`, `curl`, `iputils-ping`, `xz-utils`, `git`, `less`, `vim`. A comment says `curl` and `iputils-ping` are required by `eap-install.sh` (see [Build, install, and control](acap-build-install-control.md)). `python3-pip` is installed but no `pip install` appears, so there are no pinned Python dependencies.
- **`python` symlink** to `python3` in `/usr/bin` (line 29).
- **SDK tree:** `COPY --from=toolchain /opt/axis/sdk/temp /opt/axis/acapsdk` (line 32), and `/opt/axis/tools` from the toolchain; the `axis-acap-manifest-tools*.deb` in it is installed with `apt-get install` and `/opt/axis/tools` removed (lines 33-35). The manifest tools back the `manifest.json` workflow used from SDK 3.3.
- **`protoc` 3.13.0:** a prebuilt x86_64 binary downloaded from Maven Central to `/usr/bin/protoc` (line 39); the comment says it matches the target protobuf libraries.
- **Environment patching** of `/opt/axis/acapsdk/environment-setup*` with `sed -i` (lines 42-48): prepend the manifest-generator directory to `PATH`; rewrite `/opt/axis/sdk` to `/opt/axis/acapsdk`; append `-L$SDKTARGETSYSROOT/usr/lib` to the `CC`, `CPP` and `CXX` definitions; append `-Wl,--disable-new-dtags` to `LDFLAGS` to avoid rpath/RUNPATH issues with dynamic libraries.
- **API sysroot overlay:** copy `usr/lib/`, `usr/include/` and `usr/share/protobuf/` for `${ARCH}` from the `api` stage into `/opt/axis/acapsdk/sysroots/${ARCH}/` (lines 52-54). This is the headers-and-libraries side of the ACAP 3 APIs listed in [the legacy page](acap-sdk-version-3-legacy.md).
- **Missing OpenGL header:** download `khrplatform.h` from the Khronos EGL-Registry into the sysroot's `KHR` directory (line 58), a fix for the OpenGL ES open-standard API.
- **Shell hook:** append `. /opt/axis/acapsdk/environment-*` to `/etc/bash.bashrc` so interactive Bash users get the cross-compiler variables (line 61).
- **`WORKDIR /opt/app`** (line 64).

No `USER`, `ENTRYPOINT` or `CMD` is set: the image runs as root and defaults to the Ubuntu shell, i.e. it is a build or dev image, not an application runtime.[^acap3-sdk-repo] Contrast with the Native SDK image, which also *prunes* the sysroot ([sysroot pruning](acap-native-sdk-sysroot-pruning.md)); here the only deletion is the removed tools directory, so the whole ACAP 3 API sysroot stays visible (**Observed**: no `rm`/removal lists in either file).

## Reproducibility and supply-chain gaps

All **Observed**; none was tested by building.

- **Mutable base tags:** the three `FROM` lines use tags, not `@sha256` digests, and the 3.5 images could be re-pushed.
- **No checksums or signatures** anywhere: `protoc` is version-pinned (3.13.0) but unverified; `curl --fail -L` only catches HTTP errors.
- **Unpinned download:** `khrplatform.h` comes from the `master` branch of `KhronosGroup/EGL-Registry` with no commit SHA and no `--fail`, so a failed fetch or changed file could pass silently or alter the image.
- **apt state:** the second `apt-get install` of the local deb (line 34) relies on lists fetched on line 15 and leaves `/var/lib/apt/lists` in the layer; the first `apt-get update` is not cleaned either (image size, not correctness).
- **Image tag mismatch:** the tag family `3.5-*-ubuntu20.04` was set before the Ubuntu 22.04 bump; see [the repository page](acap3-sdk-repository.md#release-tag-scheme-and-history).
- **Host assumption:** the downloaded `protoc` and the README's "amd64" mean the image only works as intended on an x86_64 host (**Synthesis**).

## Relationships

- **Part of** [ACAP 3 SDK repository](acap3-sdk-repository.md); **checked by** [CI and maintenance](acap3-sdk-repo-ci-and-maintenance.md).
- **Depends on** the external `axisecp/acap-api` and `axisecp/acap-toolchain` images (not local).
- **Produces** the build environment used by `acap3-examples` per [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md) and [Build, install, and control ACAP applications](acap-build-install-control.md).
- **Compare with** [ACAP Native SDK image assembly](acap-native-sdk-image-assembly.md), the same pattern with a newer base, build-arg set and sysroot pruning.

[^acap3-sdk-repo]: [AxisCommunications/acap3-sdk](../raw/acap3-sdk/README.md) at `4e4fe04`: `Dockerfile.aarch64` lines 2-11 (args and stages), 13-26 (apt), 28-29 (python symlink), 31-35 (toolchain copy, manifest-tools deb), 37-39 (`protoc`), 41-48 (environment `sed` patches), 50-54 (api sysroot overlay), 56-58 (`khrplatform.h`), 60-61 (bashrc hook), 63-64 (`WORKDIR`); `Dockerfile.armv7hf` lines 2, 16, 51; `diff` of the two files; `git log -- Dockerfile.aarch64` (commits `1323e79`, `22ab945`).
