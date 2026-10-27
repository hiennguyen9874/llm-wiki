---
type: Concept
title: "Container application compatibility: Axis devices and Computer Vision SDK image versions"
description: "Which Axis devices run container applications, how to filter for them in the Product selector, the armv7hf cut-off at AXIS OS 11.11, and the legacy ACAP 4.x to Computer Vision SDK image to AXIS OS matrix."
tags: [edge-ai, axis, acap, docker, containers, compatibility]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-container-compat
    resource: ../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/index.md
    scope: ../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/
    kind: docs
    revision: "ACAP version 12"
    title: "Axis devices & compatibility | Axis developer documentation"
---

# Container application compatibility: Axis devices and Computer Vision SDK image versions

Container support is not a property of "an Axis camera with ACAP": Axis scopes it to **specific devices and specific AXIS OS versions**. Two hard boundaries define the field. Architecturally, container applications are `aarch64` only — `armv7hf` container support ended after AXIS OS 11.11. Temporally, the compatibility table in the reference applies only to legacy deployments before AXIS OS 12.0, because from AXIS OS 12.0 the ACAP Computer Vision SDK was archived and its utility libraries and scripts moved to **ACAP Runtime**. For any device running AXIS OS 12 or later, the answer is therefore not "which image do I pick" but "use the Native SDK, or ACAP Runtime with the `acap-computer-vision-sdk-examples` repository".[^acap-container-compat]

## Device compatibility

Axis states the constraint directly: for containerized applications using the ACAP Computer Vision solution, compatibility is limited to specific devices and AXIS OS versions, and `armv7hf` container support is no longer available after AXIS OS 11.11. There is no complete list published as a table in the reference; the list is a live query in the Product selector.[^acap-container-compat]

### Filtering the Product selector

The Product selector exposes container capability as one filter among several, and filters combine. The three that matter for container deployments:[^acap-container-compat]

| Filter section | Filter field | Value to choose | Selects |
| --- | --- | --- | --- |
| Hardware platform | **System-on-chip** | `ARTPEC-8` | Devices with `aarch64` |
| Hardware platform | **Container support** | checkbox | Devices with container support |
| Hardware platform | **Compute capabilities** | `DLPU` | Devices with a deep learning processing unit |

Axis also publishes pre-filtered links for the `aarch64` case: one for container support alone (SoC `ARTPEC-8` + Container support) and one for container plus accelerator (SoC `ARTPEC-8` + Compute capabilities `DLPU` + Container support). Those links encode `ARTPEC-8` as the only SoC value in the filter, which matches the `aarch64`-only boundary and the `ARTPEC-8`/`ARTPEC-9` generation described in [Axis DLPU](axis-dlpu.md).[^acap-container-compat]

**Synthesis:** the filter combination is the operational test. "Container support" alone answers whether the image can run at all; adding "Compute capabilities = DLPU" answers whether that same product can accelerate inference. A container project that needs accelerated CV therefore has to pass both filters, and the result is a hardware generation (`ARTPEC-8` and later in the published links), not a model list.

## Software compatibility: the legacy image matrix

The reference keeps one table, explicitly "for reference and to support legacy applications using versions prior to AXIS OS 12.0". The **Image version** is the Docker image release tag of the ACAP Computer Vision SDK on Docker Hub, and the tag format is `<image-version>-<architecture>-<sdk_type>` — in the example `1.5-...`, `1.5` is the image version.[^acap-container-compat]

| ACAP release | ACAP CV SDK image version | Compatible with AXIS OS version |
| --- | --- | --- |
| 4.0 | 1.0 | 10.7 and later |
| 4.1 | 1.1 | 10.9 and later |
| 4.2 | 1.2 | 10.10 and later |
| 4.3 | 1.3 | 10.12 (LTS) |
| 4.4 | 1.4 | 11.0 and later |
| 4.5 | 1.5 | 11.1 and later |
| 4.6 | 1.6 | 11.2 and later |
| 4.7 | 1.7 | 11.3 and later |
| 4.8 | 1.8 | 11.4 and later |
| 4.9 | 1.9 | 11.5 and later |
| 4.10 | 1.10 | 11.6 and later |
| 4.11 | 1.11 | 11.7 and later |
| 4.12 | 1.12 | 11.8 (breaking change) |
| 4.13 | 1.13 | 11.9 and later |
| 4.14 | 1.14 | 11.10 and later |
| 4.15 | 1.15 | 11.11 (LTS) |

Reading the table:[^acap-container-compat]

- Each ACAP release pins exactly one Computer Vision SDK image version, and the two counters advance together (`4.x` ↔ `1.x`), so image version is a proxy for ACAP release.
- The AXIS OS column is a **minimum**: "10.7 and later" means that image is the floor for AXIS OS 10.7 upward, which is why later rows keep a single image current per release rather than one image per OS.
- Three rows are special: `10.12 (LTS)`, `11.8 (breaking change)` and `11.11 (LTS)`. The breaking-change marker on ACAP 4.12 / image 1.12 means code or images around that boundary are not interchangeable.
- The table stops at ACAP 4.15 / image 1.15 / AXIS OS 11.11, the last `armv7hf`-era LTS line, consistent with the `armv7hf` cut-off and with the SDK's archival at AXIS OS 12.0. Anything on 12.x and later falls outside it.
- These are **ACAP 4.x** releases, i.e. the numbering that predates the "ACAP version equals AXIS OS version" rule introduced at AXIS OS 12.0 — the numbering history is in [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md).

## What replaces the matrix on AXIS OS 12 and later

From AXIS OS 12.0 the ACAP Computer Vision SDK is archived; the utility libraries and scripts now live in **ACAP Runtime**, used together with the `acap-computer-vision-sdk-examples` repository. The compatibility question changes shape accordingly: instead of selecting a frozen SDK image per ACAP release, a deployment either runs a native `.eap` application built with the Native SDK — the recommended path, described in [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md) — or uses ACAP Runtime on a device that still has container support until the end-of-2031 horizon. Which devices keep container support is answered by the Product selector filters above, not by the legacy table.[^acap-container-compat]

## Source coverage

- Entry point: `raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/index.md`, one file, 450 words, site `developer.axis.com`, revision "ACAP version 12". No assets or attachments in the folder. Every section was read: lifecycle banner, §Computer Vision solution and device compatibility, §ACAP Computer Vision solution software compatibility.
- Excluded: the Product selector links (they embed live filter state, not a static device list), the Docker Hub tags page, `acap-runtime`, `acap-computer-vision-sdk-examples`, and the AXIS OS end-of-life page. This page's claims do not depend on the local `raw/acap-runtime/` or `raw/acap-computer-vision-sdk-examples/` submodules; the examples repository is compiled separately in [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md), and the Runtime repository, whose own requirements (AXIS OS 11.10+, Docker ACAP 2.0.0+) are in [ACAP Runtime repository](acap-runtime-repository.md), and does not restate the device matrix.
- Limits: no date is given for the compatibility table, no minimum AXIS OS version is stated for the Docker ACAP itself, and the page does not say whether `ARTPEC-9` products appear under the same selector filters. The `armv7hf` cut-off is stated as "no longer supported after AXIS OS 11.11" without saying whether existing `armv7hf` container installations keep working on that last supported version.

## Evidence class

The armv7hf cut-off, the Product selector filters, and the entire compatibility table are **Reported** from official Axis documentation; the table is transcribed verbatim, not inferred. The reading of the AXIS OS column as a minimum, and the mapping of the table boundary to the `armv7hf` cut-off and the 12.0 archival, are **Synthesis**. Nothing is **Reproduced**: no Product selector query was run and no image was pulled or tested against a device in this ingest.

## Relationships

- **Constrains** [Container-based ACAP applications](acap-container-applications.md): the build, transfer and run procedure only applies to the devices and image versions selected here.
- **Depends on** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the matrix belongs to the pre-12 numbering, where ACAP `4.x` releases do not share the AXIS OS version number.
- **Uses** [Axis DLPU](axis-dlpu.md): the accelerator filter is the `DLPU` compute capability, and the published `aarch64` filters fix `ARTPEC-8`.
- **Superseded by** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): from AXIS OS 12.0 the archived Computer Vision SDK is replaced by ACAP Runtime utilities and the native application model.
- **Illustrated by** [ACAP Computer Vision SDK examples repository](acap-cv-sdk-examples-repository.md): the examples' own requirements (ARTPEC-8 DLPU, firmware 11.10+, Docker ACAP 3.0, `aarch64`) are a narrower, example-specific baseline than this matrix.
- **Corroborated by** the archived [ACAP generations, chip architectures and SDK compatibility](acap-chip-architecture-and-sdk-compatibility.md) page: its Native SDK table lists the same ACAP 4.x ↔ `1.x` ↔ AXIS OS rows, and its chip table puts ARTPEC-9 and CV25 on `aarch64`, which answers the limit above only partly (it still does not say how the Product selector treats ARTPEC-9).
- **Follows** the container support horizon in [Container-based ACAP applications](acap-container-applications.md): existing container-capable products are supported until end of 2031, which bounds how long this matrix stays relevant.
- **Complemented by** [Docker Compose ACAP repository](docker-compose-acap-repository.md): its README release table gives the Docker Compose ACAP's own AXIS OS minimums (rootless 4.0.0 needs 12.0; 3.0.3 needs 11.10) and states that 12.0 supports only pre-existing `aarch64` products, consistent with the cut-off here.

[^acap-container-compat]: Official documentation: [Axis devices & compatibility — Axis developer documentation](../raw/acap/reference/develop-container-applications/axis-devices-and-compatibility/index.md), whole page, ACAP version 12: warning banner "Note on container applications", §Computer Vision solution and device compatibility (armv7hf note, Product selector filters and pre-filtered links), §ACAP Computer Vision solution software compatibility (ACAP Runtime note, image tag format, ACAP release / image version / AXIS OS table).
