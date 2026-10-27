---
type: Concept
title: "ACAP SDK version 3 (legacy)"
description: "The legacy ACAP SDK 3.x (3.0 to 3.5): SDK-to-firmware mapping, toolchain versions, chip architectures, package.conf versus manifest.json, build tools, the 13 ACAP 3 APIs, signing services and how it relates to the Native SDK that replaced it."
tags: [edge-ai, axis, acap, legacy, sdk-3]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T19:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-sdk3
    resource: ../raw/acap-documentation/docs/acap-sdk-version-3/index.md
    scope: ../raw/acap-documentation/docs/acap-sdk-version-3/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "ACAP version 3.1.0 - 3.5 SDK Documentation"
---

# ACAP SDK version 3 (legacy)

ACAP SDK 3.x is the Docker-based SDK generation that preceded the Native SDK. The archived documentation is titled "ACAP version 3.1.0 - 3.5 SDK Documentation", styled as "an older version of ACAP" by the archive's layout,[^acap-docs-repo] and covers SDK releases 3.0 to 3.5 for firmware 9.70 up to 10.9 and later.[^acap-docs-sdk3] Axis labels the ACAP 3 generation "actively maintained" on its version-history page but says the descendant Native SDK "replaces many of the older APIs"; for new work use the Native SDK ([ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md)). Apps that must run on AXIS OS older than 10.7 still need ACAP 3 builds.[^acap-docs-sdk3]

## Contents and architecture

- **Format**: from 3.1 the SDK is three Docker images — ACAP SDK (build and packaging tools plus API headers and libraries), ACAP Toolchain (compilers and scripts) and ACAP API — published on Docker Hub as `axisecp/acap-sdk` (Ubuntu-based). Decoupling from the host OS is what allows Linux, Windows and macOS. Example tag: `3.5-armv7hf-ubuntu20.04`.[^acap-docs-sdk3]
- **Requirements**: Linux, Windows or macOS; Docker (Docker CE 18.09 or later on Linux, compared with Docker Engine 23.0.0 or later for the current docs); Git; Visual Studio Code optional via the *Remote - Containers* extension.[^acap-docs-sdk3]
- **Verification**: build, install and run `hello-world` from `AxisCommunications/acap3-examples`.[^acap-docs-sdk3]

## SDK, firmware and toolchain

| SDK | Firmware and later | Notable changes |
| --- | --- | --- |
| 3.0 | 9.70 | gcc 8.3; no mips; Overlay, open-standard and Video capture APIs |
| 3.1 | 9.80 (LTS) | gcc 9.2; Docker-based toolchain and API images; Machine learning API (larod 1) introduced |
| 3.2 | 10.2 | gcc 9.3; signed/unsigned toggle (firmware 11.2); Capture deprecated |
| 3.3 | 10.5 | `manifest.json` support; larod 2.0 with hardware-accelerated crop/scale/colour-space preprocessing |
| 3.4 | 10.6 | glibc 2.32; reproducible builds; larod 2.0 handles TFLite on firmware ≥ 10.6; conversion-tool support for all defines |
| 3.5 | 10.9 | ARTPEC-8; manifest schema 1.3; glibc 2.33; Media Capture (`libcapture.so`) removed; 3.4.2 earlier changed `-L dir` to `-Ldir` and added a `python` → `python3` symlink |

Forward compatibility: an app is compatible with the listed firmware and later ones until the next firmware LTS; breaking changes are announced in advance.[^acap-docs-sdk3]

## Hardware

Architectures are `armv7hf` (32-bit) and `aarch64` (64-bit). Chip mapping for ACAP 3: i.MX 6ULL, i.MX 6SoloX, ARTPEC-6, ARTPEC-7, S2E, S2L, S3L → `armv7hf`; ARTPEC-8, S5, S5L → `aarch64`. "If you're not sure, use `armv7hf`, which supports most products."[^acap-docs-sdk3]

## Packaging

- `.eap` (Embedded Application Package) with mandatory `[application name].(c/cpp)`, `LICENSE` (an empty one fails the build), `Makefile` and `manifest.json`. Use `manifest.json` from SDK 3.3, `package.conf` for 3.2 and earlier.
- `package.conf` mandatory keys: `APPGRP`, `APPID`, `APPMAJORVERSION`/`APPMINORVERSION`/`APPMICROVERSION`, `APPNAME`, `APPOPTS`, `APPTYPE`, `APPUSR`, `LICENSENAME`, `LICENSEPAGE`, `OTHERFILES`, `PACKAGENAME`, `REQEMBDEVVERSION`, `STARTMODE` (`respawn|once|never`), `VENDOR`. Optional: `PREUPGRADESCRIPT`, `POSTINSTALLSCRIPT`, `SETTINGSPAGEFILE`, `VENDORHOMEPAGELINK`.
- Manifest schema 1.0 ↔ firmware 10.6/SDK 3.4; 1.1 ↔ 10.6/3.4; 1.2 ↔ 10.7/3.5; 1.3 ↔ 10.9/3.5. License-key handling for manifest apps needs firmware 10.6. Later schemas are in [Manifest schema 1.x history](acap-manifest-schema-v1-history.md); note that the SDK numbers here (3.4/3.5) differ from the Native SDK numbers in that table (1.0 to 1.1).
- `create-package.sh` builds `package.conf` projects; `acap-build` builds `manifest.json` projects (runs `make`, validates, emits backward-compatible `package.conf`, supports `-a` for extra files); EAP name pattern `<PACKAGENAME>_<MAJOR>_<MINOR>_<MICRO>_<SDK_ARCHITECTURE>.eap`; install with `eap-install.sh [install|start|stop|remove]`. See [Build, install, and control ACAP applications](acap-build-install-control.md).
- Reproducible builds (3.4.0) are "practices … that ensure the resulting binary can be reproduced"; example `acap3-examples/reproducible-package`.
- With a manifest, pre-upgrade scripts and process forking are unsupported because systemd manages the lifecycle.[^acap-docs-sdk3]

## APIs

The ACAP 3 API page lists thirteen APIs: Audio (axaudio), Video capture (vdostream), Media Capture (deprecated, removed in 3.5), Machine learning (larod 1.0 in 3.1, 2.0 in 3.3, 3.0 in 3.5; `larodDevice` replaces `larodChip`), Overlay (axoverlay), Open standard APIs (Cairo 1.16.0, OpenGL ES 2.0, OpenCL 1.2, OpenVX 1.0), Parameter (axparameter), HTTP (axhttp), Event (axevent, version 1.1 in 3.2 adds `ax_event_new2`; set `REQEMBDEVVERSION` 2.18 to exclude firmware ≤ 10.2), Edge storage (axstorage), License (licensekey), Serial port (axserialport) and Pan-tilt-zoom (axptz). VdoStream history ends at AXIS OS 11.0 ↔ VdoStream 9.0.4. The Native SDK replacements are in [Native SDK API catalog](acap-native-sdk-api-catalog.md).[^acap-docs-sdk3]

## Signing and device handling

- **Signing**: the sign-package service sits in the ACAP Service Portal and needs Technology Integration Partner access; the signature is appended and verified at install (firmware 9.20 onward, backward-compatible). Manifest fields such as `vendor` and `architecture` are required (schema 1.3, first released in SDK 3.5). Current rules are in [ACAP application signing](acap-application-signing.md).
- **Unsigned toggle**: needs SDK 3.2 and firmware 11.2: `applications/config.cgi?action=set&name=AllowUnsigned&value=true|false`, `action=get` to read; signed-only mode does not remove already installed unsigned apps.
- **VAPIX access** from AXIS OS 11.6: same mechanism as in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md), including the 11.8 rename of the D-Bus object path and method and the 200-account limit.
- **Device setup** repeats the current guide with older details: mandatory LTS-2018 (8.40) upgrade path before 10.9 for named devices, Axis Edge Vault auto-upgrade from 10.11 (irreversible), FTP upgrade only up to AXIS OS 11.0.[^acap-docs-sdk3] The current procedure is in [Preparing an Axis device](axis-device-setup.md).

## Evidence and limits

All content is **Reported** from the archived pages and read statically; no ACAP 3 image was pulled. The "actively maintained" label is stale relative to the ACAP 12 generation. Services-for-partners pages are condensed here because [ACAP application signing](acap-application-signing.md) holds the newer equivalents.

## Relationships

- **Superseded by** the ACAP Native SDK ([ACAP Native SDK](axis-acap-native-sdk.md)); migration from SDK 3 was described as "straightforward" in [ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md).
- **Uses** the same `eap-install.sh`/`acap-build` tooling now in [Build, install, and control ACAP applications](acap-build-install-control.md).
- **Precedes** [Manifest schema 1.x history](acap-manifest-schema-v1-history.md): schemas 1.0 to 1.3 first appeared in SDK 3.4 and 3.5.
- **Packaged by** the [ACAP 3 SDK repository](acap3-sdk-repository.md): two Dockerfiles that build the 3.5 image from `axisecp/acap-api` and `axisecp/acap-toolchain` on `ubuntu:22.04` ([image assembly](acap3-sdk-image-assembly.md), [CI and maintenance](acap3-sdk-repo-ci-and-maintenance.md)). That repo corroborates the three-image split and the `armv7hf`/`aarch64` targets, but its own README lists only "amd64" (the host), and nothing in it publishes the `axisecp/acap-sdk` image named above.
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; every v3 page redirects to `developer.axis.com`, and `_layouts/acap_sdk_version_3.html` adds the "older version of ACAP" banner.
[^acap-docs-sdk3]: [acap-sdk-version-3/index.md](../raw/acap-documentation/docs/acap-sdk-version-3/index.md) and its children: `introduction/index.md`; `get-started/` (`acap-development-requirements`, `compatibility`, `find-out-which-sdk-to-use`, `set-up-the-device`, `set-up-and-verify-the-sdk`); `develop-applications/` (`application-project-structure`, `build-install-and-run-the-application`, `reproducible-builds`, `develop-using-visual-studio-code`, `supported-languages`, `vapix-access-for-acap-applications`); `what-is-new-in-acap-sdk/index.md`; `services-for-partners/` (three pages); `api/index.md`.
