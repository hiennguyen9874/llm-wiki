---
type: Concept
title: "Building ACAP Runtime: Dockerfile stages, Makefile, containerized image and protofiles image"
description: "How the Runtime is built: the multi-stage Dockerfile on the Native SDK image with a cross-built gRPC, the TEST and DEBUG switches, what the containerized and eap images contain, the Makefile link line, the separate Dockerfile.proto that produces Python client files, and the reproducibility gaps."
tags: [edge-ai, axis, acap, acap-runtime, docker, build, grpc, protobuf, reproducibility]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: rt-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9 (e375fc9586e270042c9c46dde7645c20761b06bf)"
    title: "ACAP Runtime README (§Building, §Building protofiles, §Test suite)"
  - id: rt-dockerfile
    resource: ../raw/acap-runtime/Dockerfile
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "Dockerfile — multi-stage build of the Runtime"
  - id: rt-makefile
    resource: ../raw/acap-runtime/Makefile
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "Makefile — C++ build, protoc rules, test binary"
  - id: rt-protodockerfile
    resource: ../raw/acap-runtime/Dockerfile.proto
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "Dockerfile.proto — Python protofiles image"
  - id: rt-protoworkflow
    resource: ../raw/acap-runtime/.github/workflows/build-proto-image.yml
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "build-proto-image.yml — publishes the protofiles image"
---

# Building ACAP Runtime: Dockerfile stages, Makefile, containerized image and protofiles image

The Runtime is built **inside the ACAP Native SDK image**: the Dockerfile starts from `axisecp/acap-native-sdk`, cross-builds gRPC for the target, compiles the C++ server with `acap-build` into an `.eap`, and then unpacks that `.eap` into a plain Ubuntu image for Docker ACAP. A second, unrelated Dockerfile produces the Python client-side files. The README's build commands are one line each; this page records what they really do.[^rt-readme][^rt-dockerfile]

## README commands

```sh
docker buildx build --file Dockerfile --build-arg ARCH=<ARCH> --tag acap-runtime:<ARCH>-containerized .
docker build -f Dockerfile.proto -t acap-runtime-proto:latest .
```

`<ARCH>` is `armv7hf` or `aarch64`. The test-suite variant adds `--build-arg TEST=yes --target runtime-base` ([Test suite](acap-runtime-test-suite.md)).[^rt-readme]

## Dockerfile

Global args: `ARCH=armv7hf`, `REPO=axisecp`, `VERSION=1.14` (the Native SDK release, unrelated to the manifests' `embeddedSdkVersion "3.0"`), `UBUNTU_VERSION=22.04`, `GRPC_VERSION=v1.65.5`. Everything is tag-pinned; **no image digests**.[^rt-dockerfile]

| Stage | Base / role |
| --- | --- |
| `containerized_aarch64`, `containerized_armv7hf` | `--platform=linux/arm64/v8` or `linux/arm/v7` `ubuntu:22.04` (final runtime userland) |
| `acap-native-sdk` | `${REPO}/acap-native-sdk:${VERSION}-${ARCH}-ubuntu22.04` |
| `build_base` | SDK image plus `pkg-config g++ cmake libssl-dev gnupg openssl`; sysroot `libabsl*.so*` deleted so Abseil links statically |
| `tensorflow` | clones TensorFlow and TensorFlow Serving branch `r2.9` for the protos |
| `testdata` | Coral Edge TPU repo and test models, a 10000-day self-signed `CN=localhost` cert |
| `build_grpc` / `build_grpc_arm` | host gRPC (so `protoc` and `grpc_cpp_plugin` exist) and an ARM cross build into the SDK sysroot, with gtest headers copied in |
| `build` | applies `predict_additions.patch`, then `acap-build` |
| `runtime-base` | SDK image with the `.eap`; entrypoint is the SDK's `eap-install.sh` (`<ip> <password> install|start|stop|remove`) |
| `containerized` | Ubuntu image, `/opt/app/`, each `.eap` untarred into `acap_runtime/`, `ENTRYPOINT ["/opt/app/acap_runtime/acapruntime"]` |
| `binaries` | `scratch` with only the `.eap` |

**Build switches** (`build` stage): `DEBUG` (any non-empty) gives `-O0 -ggdb` with `manifest-$ARCH.json`; `TEST` (any non-empty — README uses `yes`, CI uses `true`) gives `-g0 -DTEST` with `manifest-test.json` and `-a 'testdata/*'`, producing the app `acapruntimetest`; otherwise a release build. `-D__arm64__` is added only for `aarch64`.[^rt-dockerfile]

**Dependencies.** protobuf is not pinned separately; it comes from the gRPC v1.65.5 submodule. larod, VDO and axparameter are not built here; they come from the SDK sysroot (`-llarod -DLAROD_API_VERSION_2`, pkg-config `vdostream axparameter gio-2.0 glib-2.0`).[^rt-makefile] The TF protos are patched with the two fields described in the [ML API](acap-runtime-machine-learning-api.md).

**Containerized image facts.**
- The entrypoint carries **no flags**, so a container started without arguments has chip id 0 (ML off) and no TLS ([Server configuration](acap-runtime-server-configuration-and-security.md)); no `USER` is set, so it runs as root.
- It is the *same binary* as the eap, run under Docker ACAP; the `.eap` path survives only for the test package and `runtime-base`.
- Whether the untarred eap layout puts `acapruntime` at the entrypoint path could not be verified without building (**Unverified**); CI never runs the containerized image.

## Makefile

`BINARY` is derived from the git remote basename with dashes removed (`acapruntime`), so a checkout without a configured remote builds a wrong name. Flags: `-DLAROD_API_VERSION_2 -std=c++17`; about 110 hand-listed Abseil/gRPC/protobuf libraries plus static `libssl.a`/`libcrypto.a`; `protoc --cpp_out` and `--grpc_out` rules over `apis/**/*.proto`. Targets: `all` runs `install/strip`, builds the server (compiling `main.c` through `$(CXX)`) and a gtest binary from `test/*.cc`, and `test` runs it. The test link expects `/usr/src/googletest` paths and `-lgtest`, while the Dockerfile copies only gtest headers into the sysroot — the two paths disagree (**Observed**, likely stale). A comment mentions `-fsanitize=leak` that no flag implements.[^rt-makefile]

## Protofiles image (`Dockerfile.proto`)

One stage on `--platform=linux/arm64/v8 ubuntu:22.04`: pip-installs `grpcio`/`grpcio-tools` 1.65.5, `protobuf` 5.28.1 and `six`, shallow-clones TensorFlow `v2.9.0` and TF Serving `2.9.0`, and runs `grpc_tools.protoc` into three directories:[^rt-protodockerfile]

| Directory | Contents |
| --- | --- |
| `/build/tf/proto_utils` | TF/TF-Serving Python protos, `tf_proto_utils.py` (**unpatched** — no `stream_id`/`frame_reference`) |
| `/build/vdo/proto_utils` | `videocapture_pb2*`, `vdo_proto_utils.py` |
| `/build/param/proto_utils` | `keyvaluestore_pb2*` only |

plus `/build/requirements.txt` from `pip freeze | grep -E '^(grpcio|protobuf|six)=='` (those three packages; no numpy or OpenCV). The image has no entrypoint; it is a file carrier that client Dockerfiles `COPY --from`, as the [CV examples](acap-cv-examples-runtime-architecture.md) do.

`build-proto-image.yml` builds it for `linux/arm64` with QEMU, extracts the three directories and checks they are non-empty, then pushes `axisecp/acap-runtime:<version>-protofiles` to Docker Hub using two repository secrets (names only: `ECOSYSTEM_SERVICE_USER_DOCKER_HUB`, `ECOSYSTEM_ACCESS_TOKEN_DOCKER_HUB`). It runs on pushes to `main`, semver tags and pull requests, and the push step is guarded only by `if: success()`, so same-repo PR runs reach it (fork PRs would fail login). It produces a single tag, no architecture suffix.[^rt-protoworkflow]

## Reproducibility and staleness

TensorFlow and TF Serving are cloned from moving branch `r2.9`; Coral artifacts come from `master`; one model is fetched over plain `http`; `curl -k` and deprecated `apt-key` are used; apt packages are unpinned (hadolint DL3008 is ignored). `.gitignore` ignores `apis/` with narrow exceptions, so a new proto file stays untracked until allow-listed. Rebuilds are therefore not reproducible (**Observed**). The in-tree manifests still say `1.3.1`; CI rewrites them only in the workspace ([CI and maintenance](acap-runtime-ci-and-maintenance.md)).

## Relationships

- **Depends on:** the Native SDK image ([ACAP Native SDK repository](acap-native-sdk-repository.md), [image assembly](acap-native-sdk-image-assembly.md)); the build pattern is the generic `acap-build` flow in [Build, install, and control](acap-build-install-control.md).
- **Produces:** the container consumed by [Container-based ACAP applications](acap-container-applications.md) and the protofiles used by the [CV SDK examples](acap-cv-examples-build-deploy-workflow.md).
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).

## Evidence class

Stages, args, switches and file lists are **Observed** statically. No image was built, so the layout of the untarred eap and any build failure are **Unverified**.

[^rt-readme]: `README.md` §Building ACAP Runtime, §Building protofiles for Python, §Test suite.
[^rt-dockerfile]: `Dockerfile::{ARG L3-7, stages L10-240, build switches L189-209, containerized L225-236, binaries L238-240}`, `.hadolint.yaml` L2-6, `.gitignore` L3-5.
[^rt-makefile]: `Makefile::{BINARY L16, TEST L17, libs L32-66, PKGS L69-73, flags L75-76, targets L84-133}`.
[^rt-protodockerfile]: `Dockerfile.proto::{ARGs L5-9, TF L34-57, VDO L60-68, param L71-76, requirements L78}`.
[^rt-protoworkflow]: `.github/workflows/build-proto-image.yml::{triggers L5-37, build_proto_image L43-115}`.
