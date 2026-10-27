---
type: Concept
title: "Docker Compose ACAP repository: rootless Docker on Axis devices, overview and coverage ledger"
description: "What AxisCommunications/docker-compose-acap at 4.0.0-2-g985c8ce is: an ACAP that runs rootless dockerd with the Docker and Compose CLIs on container-capable Axis cameras, its release table, requirements, known issues, layout, coverage ledger and the main README-versus-code gaps."
tags: [edge-ai, axis, acap, docker, docker-compose, containers, rootless, repository]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-readme
    resource: ../raw/docker-compose-acap/README.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe, 2026-10-21)"
    title: "AxisCommunications/docker-compose-acap — README (git submodule)"
  - id: dc-license
    resource: ../raw/docker-compose-acap/LICENSE
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "Apache License 2.0"
  - id: dc-manifest
    resource: ../raw/docker-compose-acap/app/manifest.json
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "ACAP manifest of the application"
---

# Docker Compose ACAP repository: rootless Docker on Axis devices, overview and coverage ledger

The Docker Compose ACAP ("the application", `appName` `dockerdwrapperwithcompose`) runs a **rootless Docker daemon** on a container-capable Axis device and bundles the Docker CLI and the Docker Compose CLI, so containers can be started from the device itself, from a remote client, or from another native ACAP application.[^dc-readme] It is the repository behind the "Docker Compose ACAP" described by the vendor in [Container-based ACAP applications](acap-container-applications.md); that page recorded it only as a link target, and this concept and its siblings now cover the repository's contents. The current release is 4.0.0 (Docker 29.8.1, AXIS OS 12.0 or newer, rootless).[^dc-readme]

## Identity

| Field | Value |
| --- | --- |
| Upstream | `https://github.com/AxisCommunications/docker-compose-acap` (git remote `origin`) |
| Snapshot | `4.0.0-2-g985c8ce` = `985c8cede8b73d3a02a74c36e8a71d17b04852fe`, committed 2026-10-21; 41 tracked files, 204 commits since 2021-07-06 |
| Licence | Apache License 2.0 for the repository and for `app/LICENSE`[^dc-license] |
| Languages | C (GLib, FastCGI, axparameter, axstorage), shell, Dockerfile, GitHub Actions YAML |
| Package | `Docker_Daemon_with_Compose_<version>_<ARCH>_signed.eap` for releases, built unsigned by the Dockerfile; signing is a CI step |
| Manifest | `schemaVersion` 1.7.0, `appId` 414150, `runMode` `once`, version 4.0.0, `embeddedSdkVersion` 3.0, container host enabled[^dc-manifest] |

## Releases

The README's release table is the vendor's compatibility statement:[^dc-readme]

| Release | AXIS OS min. | dockerd | Type | Note |
| --- | --- | --- | --- | --- |
| 4.0.0 | 12.0 | 29.8.1 | rootless | latest |
| 3.0.3 | 11.10 | 26.0.0 | rootless | AXIS OS 2024 LTS |
| 2.0.0 | 11.9 | 26.0.0 | rootful | AXIS OS 2024 LTS |
| 1.5.0 | 10.12 | 26.0.0 | rootful | AXIS OS 2022 LTS |

From AXIS OS 12.0 rootful ACAP applications (user `root`) are no longer supported; on AXIS OS 11.5 to 11.11 they need "allow root" enabled. Only `aarch64` products that existed before AXIS OS 12.0 are supported on 12; both `aarch64` and `armv7hf` are supported on 11.11. Container capability is checked through the Axis Product Selector, and the Native SDK must support the device.[^dc-readme] This is consistent with the container end-of-support horizon in [Container application compatibility](acap-container-compatibility.md).

## What the application does

- Starts **rootlesskit → dockerd** under the application's own non-root user, so containers have no root on the host; behaviour and flags are in [Daemon runtime](docker-compose-acap-daemon-runtime.md).[^dc-readme]
- Exposes seven settings (SD card, TLS, TCP socket, IPC socket, two log levels, a read-only status) through the device web UI or `param.cgi`; changing one while running restarts dockerd.[^dc-readme][^dc-manifest]
- Secures a TCP daemon with TLS certificates uploaded over HTTP ([certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md)).
- Can keep the Docker data root on an SD card ([SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md)).
- Is built in a container from the Native SDK image and CI-signed ([build and packaging](docker-compose-acap-build-and-packaging.md), [CI and maintenance](docker-compose-acap-ci-and-maintenance.md)).

## Known issues stated by the README

1. SD card permissions can be wrong after a firmware or application upgrade.
2. Only uid and gid are mapped between device and containers, not secondary groups; device resources group-owned by `sdk` or `storage` need `group_add` with *mapped* ids.
3. Container networking requires `DOCKER_INSECURE_NO_IPTABLES_RAW=1`, which omits the Docker 28 raw-table hardening for published ports; Docker API TLS does not protect container services, so publish few ports and authenticate services separately.
4. `buildx` is not bundled, so buildx-dependent features do not work on the device.[^dc-readme]

## Usage paths

On the device, the CLIs need `IPCSocket`, and the caller must be the application user or in the `addon` group; a second ACAP must use a dynamic user, as in the [container-example](acap-example-container-in-native-acap.md). Remotely, `TCPSocket` is required and the port is 2376 with TLS or 2375 without. Images can be pulled, or moved with `docker save | docker load`. Behind a proxy, `daemon.json` in the application's `localdata` directory carries the Docker `proxies` block and needs Developer Mode and an application restart; see [Proxy configuration](acap-proxy-configuration.md) for the other proxy layers.[^dc-readme]

## README versus code (Observed)

- The README says armv7hf and aarch64 are both buildable (`<ARCH>`), but the Dockerfile's `ARCH` default is `armv7hf` while its SDK base is 12.0.0, which only supports aarch64 devices; see [build and packaging](docker-compose-acap-build-and-packaging.md).
- The README's `curl … | "browser_download_url…"` download snippet is not valid shell (no `jq`).
- The README's SD card legacy path (`/var/spool/storage/areas/SD_DISK/<app>`) differs from the path the post-install script uses; see [SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md).
- The manifest declares `embeddedSdkVersion` 3.0 although the build uses Native SDK 12.0.0.[^dc-manifest]
- The README never mentions `build.sh`, the `REPO` and `VERSION` build arguments, or the proxy build arguments.

## Coverage ledger

Revision `4.0.0-2-g985c8ce`; all 41 tracked files were inventoried and read statically, none executed.

| Area | Files | Treatment | Concept |
| --- | --- | --- | --- |
| Docs | `README.md`, `CONTRIBUTING.md`, `LICENSE`, `app/LICENSE` | read; licence identified | this page, [CI and maintenance](docker-compose-acap-ci-and-maintenance.md) |
| Wrapper | `app/dockerdwrapperwithcompose.c`, `app/app_paths.h`, `app/log.{c,h}` | read | [Daemon runtime](docker-compose-acap-daemon-runtime.md) |
| Upload and TLS | `app/fcgi_server.{c,h}`, `app/fcgi_write_file_from_stream.{c,h}`, `app/http_request.{c,h}`, `app/tls.{c,h}`, `app/html/index.html` | read | [Certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md) |
| Storage | `app/sd_disk_storage.{c,h}`, `app/postinstallscript.sh` | read | [SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md) |
| Package | `app/manifest.json`, `app/Makefile` | read | this page and [build and packaging](docker-compose-acap-build-and-packaging.md) |
| Build | `Dockerfile`, `build.sh`, `.dockerignore`, `.hadolint.yaml`, `.gitignore`, `.editorconfig`, `.clang-format`, `.vscode/*` | read | [Build and packaging](docker-compose-acap-build-and-packaging.md) |
| CI | `.github/workflows/{cd,lint,cherry-picker}.yml`, `.github/actions/*/action.yml`, `.github/renovate.json`, `CODEOWNERS`, `.markdownlint.yaml`, `.yamllint.yml` | read | [CI and maintenance](docker-compose-acap-ci-and-maintenance.md) |

Limits: nothing was built, signed or run; the Native SDK base image, the downloaded Docker, Compose, rootlesskit and slirp4netns binaries, the Docker docs, the VAPIX pages and the GitHub releases are not local; the stated release table and device compatibility were not checked against the Product Selector; the README's dockerd 29.8.1 and Compose 5.5.0 agree with the Dockerfile and git log but no binary was inspected.

## Evidence class

Identity, layout, defaults and the README-versus-code findings are **Observed** from static inspection at the fixed revision. The release table, requirements, device compatibility and known-issue statements are **Reported** by the README. Nothing is **Reproduced**.

## Relationships

- **Implements** the "Docker Compose ACAP" of [Container-based ACAP applications](acap-container-applications.md), the vendor-documented route for starting containers from a native ACAP.
- **Used by** [ACAP example: containers from a native ACAP](acap-example-container-in-native-acap.md), which calls this application's CLIs from its own scripts.
- **Depends on** [ACAP Native SDK repository](acap-native-sdk-repository.md) for the build image and on container support described in [Container application compatibility](acap-container-compatibility.md).
- **Related to** the Docker-ACAP-based containerized [ACAP Runtime repository](acap-runtime-repository.md) and the archived [CV SDK examples](acap-cv-sdk-examples-repository.md), whose containers ran on the predecessor Docker ACAP.
- **Parts:** [Daemon runtime](docker-compose-acap-daemon-runtime.md), [Certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md), [SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md), [Build and packaging](docker-compose-acap-build-and-packaging.md), [CI and maintenance](docker-compose-acap-ci-and-maintenance.md).

[^dc-readme]: `README.md` §Notable Releases (table and IMPORTANT note), §Overview (NOTE, Known Issues), §Requirements incl. Container capability, §Installation and Usage (Settings, Using the application, Proxy Setup, Loading images), §Building the application; `git describe`, `git rev-parse`, `git log` and `git remote -v` of the checkout.
[^dc-license]: `LICENSE` and `app/LICENSE` headers (Apache License 2.0); `README.md` §License.
[^dc-manifest]: `app/manifest.json::{schemaVersion, acapPackageConf.setup, acapPackageConf.configuration.paramConfig, containers}`.
