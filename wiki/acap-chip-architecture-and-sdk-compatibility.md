---
type: Concept
title: "ACAP generations, chip architectures and SDK-to-AXIS OS compatibility"
description: "How to pick the right ACAP SDK: ACAP generations 1 to 12, the SoC-to-architecture table, the ACAP/Native SDK/AXIS OS mapping for 4.x and 12.x, image tag format, forward-compatibility rules, and the Native SDK versus Computer Vision solution decision."
tags: [edge-ai, axis, acap, compatibility, versioning, soc]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T18:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-compat
    resource: ../raw/acap-documentation/docs/axis-devices-and-compatibility/index.md
    scope: ../raw/acap-documentation/docs/axis-devices-and-compatibility/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Axis devices & compatibility"
  - id: acap-docs-version-history
    resource: ../raw/acap-documentation/docs/introduction/version-history.md
    scope: ../raw/acap-documentation/docs/introduction/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Introduction: version history, version comparison, SDK overview"
---

# ACAP generations, chip architectures and SDK-to-AXIS OS compatibility

An ACAP application is compatible with a device when it was compiled for the device's chip **architecture** and the device's AXIS OS provides the APIs it uses. The archived documentation gives the answer as three lookups: the SoC decides `armv7hf` or `aarch64`; the AXIS OS version decides which ACAP/SDK release can be used; and the application keeps working on later AXIS OS versions until the next LTS.[^acap-docs-compat] This page fills the gap that [ACAP version rules](acap-versioning.md) recorded — the version-history and compatibility pages that were missing from the later `raw/acap/` capture.

## Generations

| ACAP | Year | Status (archived page) | Note |
| --- | --- | --- | --- |
| 12 and later | 2024 | Actively developed | First release aligned to AXIS OS versioning; ACAP LTS scope follows AXIS OS LTS within the same major |
| 4 | 2021 | "Actively maintained" | Introduced the Computer Vision SDK and the Native SDK; not equal to SDK or AXIS OS version |
| 3 | 2020 | "Actively maintained" | See [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md) |
| 2 | 2014 | End of support Q4 2021 | No maintenance |
| 1 | 2009 | Deprecated | ACAP was "the world's first camera-based video analytics platform" |

The page lists only ACAP 12 although 12.0 to 12.2 exist, and still labels 3 and 4 "actively maintained" while 12.x is current, so it is stale ([ACAP documentation repository](acap-documentation-repository.md), which is an archived snapshot).[^acap-docs-repo][^acap-docs-version-history]

## Chip to architecture

| SoC | Architecture |
| --- | --- |
| ARTPEC-6, ARTPEC-7, i.MX 6SoloX | `armv7hf` |
| ARTPEC-8, ARTPEC-9, Ambarella CV25 | `aarch64` |

The Native SDK supports "all products for the chips listed that support the minimum AXIS OS version". The ACAP 3 table additionally lists i.MX 6ULL, S2E, S2L, S3L (`armv7hf`) and S5, S5L (`aarch64`).[^acap-docs-compat] ARTPEC-9 appears only in this table and in the release notes (12.2); no per-version SDK is tied to it here. Whether a feature exists also depends on the product: the Video capture API needs an image sensor.[^acap-docs-compat]

## Version mapping

**From 12.0**: ACAP release, Native SDK and AXIS OS share major.minor. "ACAP version 12.0 contains acap-native-sdk 12.0.0 and maps to AXIS OS 12.0"; 12.1 and 12.2 follow the same pattern, each valid "and later until LTS". Image tag format: `<image-version>-<architecture>-<container-distribution>`, for example `axisecp/acap-native-sdk:12.0.0-aarch64-ubuntu24.04`.[^acap-docs-compat]

**ACAP 4.x** (Native SDK image version `1.x` equals the minor): 4.0 ↔ 10.7+; 4.1 ↔ 10.9+; 4.2 ↔ 10.10+; **4.3 ↔ 10.12 LTS**; 4.4 ↔ 11.0+; 4.5 ↔ 11.1+; 4.6 ↔ 11.2+; 4.7 ↔ 11.3+; 4.8 ↔ 11.4+; 4.9 ↔ 11.5+; 4.10 ↔ 11.6+; 4.11 ↔ 11.7+; 4.12 ↔ 11.8+; 4.13 ↔ 11.9+; 4.14 ↔ 11.10+; **4.15 ↔ 11.11 LTS**. The same rows apply to the legacy Computer Vision SDK images, where 4.12 is annotated "breaking change"; that table is in [Container application compatibility](acap-container-compatibility.md).[^acap-docs-compat]

**Forward compatibility**: an app built with an older SDK works on newer AXIS OS within the same LTS window; after an LTS, removed APIs may break it, and breaking changes "are always announced in advance". Between LTS releases new SDKs only add functionality, so use the latest SDK. To support AXIS OS older than 10.7, build with ACAP 3. The Axis Virtual Loan Tool provides loan cameras for testing.[^acap-docs-compat]

## Native SDK or Computer Vision solution

| Aspect | Native SDK | Computer Vision solution (deprecated) |
| --- | --- | --- |
| Minimum AXIS OS | 10.7 | 10.7 and an SD card |
| Languages | C, C++ | C/C++, Python, .NET and others |
| Development | Docker | Docker |
| Deployment | Web GUI or VAPIX | Docker (container) |
| Products | Most Axis products from ARTPEC-6 up | Container-capable products only (see the compatibility lists) |

Axis says the Native SDK is "always applicable and fully supported" and the way to build analytics, computer vision and machine learning on ACAP devices. For AXIS OS 12.0 and later the container track is Docker ACAP, Docker Compose ACAP and ACAP Runtime; for earlier AXIS OS it is the Computer Vision SDK, "deprecated and not available for AXIS OS 12.0 and later". New 12.x products have no container support; existing ones are supported until end of 2031 when the AXIS OS 2026 LTS ends; `armv7hf` container support ended after AXIS OS 11.11.[^acap-docs-version-history] Related reasoning: [Hướng triển khai custom AI trên Axis](axis-edge-ai-adoption-guide.md) and [Container-based ACAP applications](acap-container-applications.md). The table's "Deployment: Docker" row conflicts with the page's own 12.0 guidance, as noted in the repository ledger.

## Practical prerequisites

Current docs require Docker Engine 23.0.0 or later on Linux (Docker Desktop stable on Windows and macOS), Git, and any editor; the ACAP 3 docs required Docker CE 18.09 or later. Developer-environment setup is in [ACAP developer environment](acap-dev-environment-setup.md).[^acap-docs-version-history]

## Evidence and limits

All rows are **Reported** and transcribed from the archived pages. The 4.x table equals the one in the later container-compatibility capture, so the two agree; the numbers are independent of ARTPEC-9, which no version table mentions. Nothing here was checked against a device or against the live site.

## Relationships

- **Implemented by** [ACAP Native SDK image assembly](acap-native-sdk-image-assembly.md): `armv7hf` and `aarch64` Dockerfiles that differ only in the cross package and two armv7hf `-U` flags; see [repository overview](acap-native-sdk-repository.md).
- **Extends** [ACAP version rules](acap-versioning.md) and **resolves** its coverage limit about the missing version history and compatibility pages.
- **Depends on** [ACAP release history](acap-release-history.md) for what changed in each release.
- **Constrains** [Manifest schema 1.x history](acap-manifest-schema-v1-history.md) and [ACAP application signing](acap-application-signing.md).
- **Uses** [Container application compatibility](acap-container-compatibility.md) for the container device filter.
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; the docs were migrated to `developer.axis.com/acap`.
[^acap-docs-compat]: [axis-devices-and-compatibility/index.md](../raw/acap-documentation/docs/axis-devices-and-compatibility/index.md) §Hardware compatibility (chip table), §Software compatibility, §ACAP Native SDK software compatibility (12.x and 4.x tables), §Forward compatibility, §Supporting older AXIS OS, §Camera loan tool.
[^acap-docs-version-history]: [version-history.md](../raw/acap-documentation/docs/introduction/version-history.md) §ACAP version 12 and higher, §ACAP version 1–4; `acap-version-comparison.md`; `acap-sdk-overview.md` §Summary comparison table, §ACAP Computer Vision solution; `get-started/set-up-developer-environment/pre-requisites.md`; `acap-sdk-version-3/get-started/acap-development-requirements.md`.
