---
type: Concept
title: "ACAP Native SDK image assembly: stages, environment patching and architecture differences"
description: "How Dockerfile.aarch64 and Dockerfile.armv7hf build the SDK image: acap-api and acap-toolchain overlay on ubuntu:24.04, installed tools, environment-setup sed patches, shell hook, build args, and the two armv7hf-only differences."
tags: [edge-ai, axis, acap, sdk, docker, toolchain, build]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T19:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-native-sdk-repo
    resource: ../raw/acap-native-sdk/README.md
    scope: ../raw/acap-native-sdk/
    kind: code
    revision: "12.10.0-2-geed6dcf (eed6dcff23c17e744b773473646251752b91184f, 2026-08-18)"
    title: "AxisCommunications/acap-native-sdk (git submodule)"
---

# ACAP Native SDK image assembly: stages, environment patching and architecture differences

The SDK developer image is built as a three-stage Dockerfile: two Axis-published images (`acap-api` and `acap-toolchain`) are used only as `COPY --from` sources, and the final stage is plain `ubuntu:24.04` with the toolchain tree copied in, an Axis manifest-tools deb installed, the toolchain's `environment-setup*` script patched with `sed`, the API sysroot overlaid, and the shell configured to source the SDK for interactive users. The two architectures differ in exactly two ways (see below).[^acap-native-sdk-repo] Which libraries are then deleted is covered in [sysroot pruning](acap-native-sdk-sysroot-pruning.md); the repo overview is [ACAP Native SDK repository](acap-native-sdk-repository.md).

Line numbers refer to `Dockerfile.aarch64` (192 lines); `Dockerfile.armv7hf` has 194, shifted by two. Evidence class: **Observed** by static inspection and `diff`; the image was not built.

## Build arguments

| ARG | Default | Role (`Dockerfile.aarch64` lines 2-8) |
| --- | --- | --- |
| `ARCH` | `aarch64` (`armv7hf` in the other file) | Selects base image tags and the sysroot directory |
| `API_VERSION`, `TOOLCHAIN_VERSION` | `latest` | Tag of the `acap-api` and `acap-toolchain` images |
| `TOOLCHAINS_UBUNTU_VERSION`, `SDK_UBUNTU_VERSION` | `24.04` | Ubuntu flavor of the two builder images and of the final image |
| `REPO` | `axisecp` | Registry namespace of the builder images |
| `AXIS_OS_VERSION_TAG` | `unknown` | Exported as `ENV AXIS_OS_VERSION` (line 16), added in `44ef0ff` "compatibleOSVersion in SDK" |

Builder images are `${REPO}/acap-api:${API_VERSION}-${ARCH}-ubuntu${TOOLCHAINS_UBUNTU_VERSION}` and `${REPO}/acap-toolchain:${TOOLCHAIN_VERSION}-${ARCH}-ubuntu${TOOLCHAINS_UBUNTU_VERSION}` (lines 10-11). `ARCH` is re-declared after `FROM` (line 59) because ARG values do not cross stage boundaries.[^acap-native-sdk-repo] The only `ENV` in the file is `AXIS_OS_VERSION`; its `unknown` default means the Axis OS version is supplied by whoever runs the build, and nothing checks it against the API or toolchain tags.

## Assembly steps

1. **Host packages** (lines 20-37, one `apt-get` layer with `--no-install-recommends` and list cleanup): `crossbuild-essential-arm64` (armv7hf: `crossbuild-essential-armhf`), `make`, `pkg-config`, `python3-pip`, `python3-jsonschema`, `curl`, `iputils-ping`, `xz-utils`, `git`, `less`, `jq`, `bash-completion`, `tree`, `nano`, `vim`. Only `curl` and `iputils-ping` carry a stated reason: "required by eap-install.sh" (line 19; see [installing with eap-install.sh](acap-build-install-control.md)). There is no `pip install`.[^acap-native-sdk-repo]
2. **`python` alias** (line 41): `ln -s python3 python`.
3. **Toolchain copy** (lines 44-47): `/opt/axis/sdk/temp` from the toolchain image becomes `/opt/axis/acapsdk`; `/opt/axis/tools` is copied, `axis-acap-manifest-tools*.deb` is installed with `apt-get install -y`, then the directory is removed. This second apt call has no `apt-get update` and no list cleanup.
4. **PATH patch** (line 50): every `export PATH=` line in `environment-setup*` gets `/opt/axis/acapsdk/axis-acap-manifest-tools/manifest-generator:` prepended, which is how the manifest generator reaches `PATH`. `acap-build` itself is not named in the Dockerfiles; it comes with the copied toolchain tree.
5. **Path and flag patches** (lines 54-56, all on `/opt/axis/acapsdk/environment-setup*`): rewrite `/opt/axis/sdk` to `/opt/axis/acapsdk`; append `-L$SDKTARGETSYSROOT/usr/lib` inside `CC`, `CPP` and `CXX` values (expanded when the script is sourced, not at build time); append `-Wl,--disable-new-dtags` to `LDFLAGS`, with the comment "to solve dynamic library rpath issues".
6. **API overlay** (lines 59-63): from the `api` image copy `usr/lib/`, `usr/include/`, `usr/share/protobuf/` and `usr/share/pkgconfig/nlohmann_json.pc` (the last placed in `usr/lib/pkgconfig`; added in `030dc43`) into `/opt/axis/acapsdk/sysroots/${ARCH}/`.
7. **Missing OpenGL header** (lines 65-67): `curl` downloads `KHR/khrplatform.h` from the Khronos `EGL-Registry` `master` branch into the sysroot.
8. **Pruning** (lines 69-186): the `rm` layers described in [sysroot pruning](acap-native-sdk-sysroot-pruning.md).
9. **Shell hook** (lines 188-189): appends `. /opt/axis/acapsdk/environment-*` to `/etc/bash.bashrc`; `WORKDIR /opt/app` ends the file. There is no `ENTRYPOINT`, `CMD` or `USER`, so the image runs as root and defaults to the `ubuntu` base image's shell.[^acap-native-sdk-repo]

## What this means for users (Synthesis)

- The compiler variables (`CC`, `CXX`, `CFLAGS`, `LDFLAGS`, `PKG_CONFIG_PATH`, `SDKTARGETSYSROOT`) come from the sourced script, not from Docker `ENV`. They are set in interactive bash sessions but not in plain `docker run ... make` or other non-interactive invocations unless the script is sourced explicitly. This is consistent with the documented Dockerfile builds, which source it explicitly in a `RUN` line (`RUN . /opt/axis/acapsdk/environment-setup* && acap-build ./` in the [first application workflow](acap-first-application-workflow.md), and the same pattern in [third-party library builds](acap-third-party-libraries.md)).
- `-Wl,--disable-new-dtags` makes the linker emit `DT_RPATH` rather than `DT_RUNPATH`, so rpath entries outrank `LD_LIBRARY_PATH`. This matters for bundling libraries as in [third-party libraries](acap-third-party-libraries.md) (**Synthesis** from the stated intent; not tested).
- The image is a developer convenience image: root user, editors, `git`, and a second cross compiler from Ubuntu (`crossbuild-essential-*`) alongside the Axis toolchain. It is not a hardened runtime.

## Architecture differences

`diff` shows exactly four hunks, all consequences of two differences:[^acap-native-sdk-repo]

| Difference | aarch64 | armv7hf |
| --- | --- | --- |
| Ubuntu cross package | `crossbuild-essential-arm64` (line 21) | `crossbuild-essential-armhf` (line 21) |
| Extra environment patches | none | lines 56-57 append `-U_TIME_BITS` and `-U_FILE_OFFSET_BITS` to `CC`/`CPP`/`CXX` |

The other two hunks are the `ARCH` default (`aarch64` vs `armv7hf`, lines 2 and 59/61). Neither file mentions `-march`, `-mfloat-abi`, NEON or VFP; any such triplet or flag comes from the toolchain image's `environment-setup*`, which is not local. The undefine flags were introduced as `-D_TIME_BITS=32 -D_FILE_OFFSET_BITS=32` and changed to `-U...` in `0d8c0cb` (2025-04-24). **Synthesis:** they plausibly relate to 32-bit `time_t` and large-file handling on armv7hf with newer glibc, but no commit message in the repo states the rationale. The mapping of architectures to chips (`armv7hf` ARTPEC-7, `aarch64` ARTPEC-8/9) is in [chip architecture compatibility](acap-chip-architecture-and-sdk-compatibility.md).

## Reproducibility and security observations

- **Observed:** `latest` tags for both builder images and an unpinned `master` download of `khrplatform.h` (no checksum) make rebuilds non-reproducible and dependent on network access to GitHub. Behind a corporate proxy this download is a build-time failure point; see [proxy configuration](acap-proxy-configuration.md).
- **Observed:** the global `sed` on `export PATH=` and the `environment-setup*` glob affect every matching file/line; if the toolchain image ever shipped more than one such script, all would be patched and all sourced.
- **Observed:** `ln -s python3 python` has no `-f`, so it would fail on a base image that already has `/usr/bin/python`.
- **Unverified:** whether the published `axisecp/acap-native-sdk` images are built from exactly these files with these defaults; the repo's CI only checks that the build succeeds (see [CI and maintenance](acap-native-sdk-repo-ci-and-maintenance.md)).

## Relationships

- **Part of** [ACAP Native SDK repository](acap-native-sdk-repository.md).
- **Depends on** the external `axisecp/acap-api` and `axisecp/acap-toolchain` images (not local).
- **Followed by** [sysroot pruning](acap-native-sdk-sysroot-pruning.md) within the same Dockerfile.
- **Produces** the environment used in [Build, install, and control ACAP applications](acap-build-install-control.md) and [ACAP development environment setup](acap-dev-environment-setup.md).
- **Checked by** [CI and maintenance](acap-native-sdk-repo-ci-and-maintenance.md).
- **Compare with** [ACAP 3 SDK image assembly](acap3-sdk-image-assembly.md), the same overlay pattern for ACAP SDK 3.5 on `ubuntu:22.04` without pruning.

[^acap-native-sdk-repo]: [AxisCommunications/acap-native-sdk](../raw/acap-native-sdk/README.md) at `eed6dcf`: `Dockerfile.aarch64` lines 2-8, 10-12, 15-16, 18-37, 41, 44-47, 50, 53-56, 58-67, 188-192; `Dockerfile.armv7hf` lines 2, 21, 56-57, 61; `diff` of the two files; `git show` of `44ef0ff`, `030dc43` and `0d8c0cb`.
