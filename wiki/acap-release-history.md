---
type: Concept
title: "ACAP release history 4.0 to 12.2"
description: "Version-by-version timeline of ACAP releases from 4.0 beta (2021) to 12.2 (January 2025): minimum AXIS OS, SDK pairing, new APIs, manifest-schema steps, deprecations, breaking changes and the security arc, with the inconsistencies found in the release notes."
tags: [edge-ai, axis, acap, release-notes, versioning]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T15:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-release-notes
    resource: ../raw/acap-documentation/docs/release-notes/index.md
    scope: ../raw/acap-documentation/docs/release-notes/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "ACAP release notes 4.0 beta 1 to 12.2"
---

# ACAP release history 4.0 to 12.2

ACAP shipped about one release every two months from 4.0 (27 September 2021) to 4.15 (3 July 2024), each pairing a Computer Vision SDK image and a Native SDK of the same `1.x` number with a stepping minimum AXIS OS; the numbering then jumped to 12.0 (4 November 2024) to align ACAP, the Native SDK and AXIS OS. The notes record three long arcs: a security arc that removed root and made signing the default, a manifest-schema arc from 1.3 to 1.7.3, and a container arc that ended with the Computer Vision SDK being deprecated.[^acap-docs-release-notes] The archive is a frozen snapshot of the pages now hosted on `developer.axis.com`, so the live pages are authoritative where they differ.[^acap-docs-repo]

## Timeline

"Min OS" is the minimum AXIS OS stated in each note. From 4.0 to 4.15 the Computer Vision SDK and Native SDK carry the same `1.x` number as the release (4.n ↔ 1.n).[^acap-docs-release-notes]

| ACAP | Date | Min OS | Highlights |
| --- | --- | --- | --- |
| 4.0 beta 1 | 13 Jul 2021 | CV build `21.27.3_1`; Native 10.6 | First ACAP 4 beta. Native SDK for 32/64-bit ARTPEC-6; APIs AxEvent, AxOverlay, Cairo, Larod, Licensekey, OpenCL, Vdo; Docker Compose ACAP for `.eap` apps |
| 4.0 | 27 Sep 2021 | 10.7 | Native SDK adds ARTPEC-7, S5 and S5L; Docker ACAP and Compose ACAP 1.1.1 |
| 4.1 | 13 Jan 2022 | 10.9 | Architecture-independent apps; manifest schema 1.3 adds `architecture` (`all` allowed); 64-bit ARTPEC-8 begins. Overlay API and OpenCL are `armv7hf` only |
| 4.2 | 4 May 2022 | 10.10 | Full ARTPEC-8 support; Overlay and OpenCL on `aarch64`; VAPIX API listing supported SDKs |
| 4.3 | 31 Aug 2022 | 10.12 (LTS) | Container base images move to Ubuntu 22.04; Parameter API (ACAP Runtime, gRPC) examples labelled Beta |
| 4.4 | 12 Oct 2022 | 11.0 | CV25 support; schema 1.3.1 (`=` in `runOptions`, `appName` max length 26); ACAP Runtime 1.1.2 |
| 4.5 | 14 Nov 2022 | 11.1 | P1467-LE and P1468-LE added; known regression in `openssl_curl_example` |
| 4.6 | 13 Jan 2023 | 11.2 | VAPIX switch for unsigned apps; FastCGI added to the Native SDK; ACAP Runtime 1.2.0; Docker ACAP 1.3.0 |
| 4.7 | 28 Feb 2023 | 11.3 | ACAP Runtime open-sourced; automatic `package.conf` to `manifest.json` upgrades; Axis Model Zoo launched |
| 4.8 | 24 Apr 2023 | 11.4 | Larod v1 build-time deprecation warning; examples `larod` and `vdo-larod-preprocessing` removed |
| 4.9 | 26 Jun 2023 | 11.5 | i.MX 6SoloX and i.MX 6ULL audio chipsets; Docker ACAP and Compose ACAP distributed as signed `.eap` on GitHub |
| 4.10 | 26 Sep 2023 | 11.6 | Root-privileged ACAP VAPIX interface (11.5); runtime VAPIX service-account credentials in beta (11.6); `docker compose` V2; new `acap-build` options |
| 4.11 | 20 Nov 2023 | 11.7 | Schema 1.4.0; Edge storage API and Serial port API |
| 4.12 | 19 Jan 2024 | 11.8 | Schema 1.5.0: reverse proxy, web-content access policy, D-Bus `.*`; root disallowed by default, breaking the post-install-script reverse proxy and Docker ACAP 1.x |
| 4.13 | 4 Mar 2024 | 11.9 | Containers built with CV SDK ≤ 1.12 that use `libvdostream.so` fail on 11.9 (CV SDK 1.13 required); schema 1.6.0; Axparameter API and Metadata Broker API; VAPIX service-account API goes GA; C++ container examples removed |
| 4.14 | 3 May 2024 | 11.10 | Curl, Jansson, OpenSSL libraries; schema 1.7.0 (`containerHost`, `createDockerSymlinks`); Docker ACAP 3.0.0 rootless; only uid/gid, not secondary groups, are mapped into containers |
| 4.15 | 3 Jul 2024 | 11.11 (LTS) | Bounding Box API; Developer Mode; Metadata Broker `on_metadata` → `on_message` (breaking); last CV SDK for `armv7hf`; Service Portal validates against the latest schema within the same major |
| 12.0 | 4 Nov 2024 | 12.0 | Versions align with AXIS OS; Ubuntu 24.04 base image; schema 1.7.1; root access removed, signing required by default with a toggle; S5L, S5, i.MX 6SoloX and i.MX 6ULL leave the active track; CV SDK deprecated as the "Computer Vision solution"; Metadata Broker renamed Message Broker; ACAP Runtime 2.0.0 |
| 12.1 | 25 Nov 2024 | 12.1 | Schema 1.7.2 (`friendlyName` limits); Event API event-declaration templates deprecated |
| 12.2 | 21 Jan 2025 | 12.2 | ARTPEC-9 across all APIs and examples; ARTPEC-9 conversion and optimisation docs; yolov5-on-artpec9 guide; schema 1.7.3; build and runtime proxy docs |

The manifest-schema details are in [Manifest schema 1.x history](acap-manifest-schema-v1-history.md); API-level additions in [Native SDK API catalog](acap-native-sdk-api-catalog.md).

## Arcs

- **Security**: VAPIX switch for unsigned apps (4.6, AXIS OS 11.2) → root-privilege toggle (4.10, 11.5) → runtime VAPIX credentials (11.6) → root disallowed by default (4.12, 11.8) → root removed and signed-only by default (12.0). The signing table is in [ACAP application signing](acap-application-signing.md) and the credentials mechanism in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).[^acap-docs-release-notes]
- **Containers**: Docker Compose ACAP beta (2021) → Ubuntu 22.04 images (4.3) → `docker compose` V2 (4.10) → rootless Docker ACAP 3.0.0 (4.14) → Computer Vision SDK deprecated at 12.0; containers unsupported on new 12.x products and supported to end of 2031 when the AXIS OS 2026 LTS ends. See [Container-based ACAP applications](acap-container-applications.md).[^acap-docs-release-notes]
- **Deprecations and removals** that bite old code: Larod v1 (warning from 4.8), `libvdostream.so` ABI (4.13), Metadata Broker callbacks (4.15), the Event API event-declaration templates (12.1), and the Overlay API name change to Axoverlay.

## Inconsistencies in the notes

- **FastCGI chip list**: 4.6 to 4.9 footnotes say the list "is now corrected to also include ARTPEC-6, S5L and S5", but the 4.10 to 4.14 tables list FastCGI only for ARTPEC-8, ARTPEC-7, CV25, i.MX 6SoloX and i.MX 6ULL, with no explanation. The later Native SDK API page lists FastCGI for ARTPEC-9/8/7/6 and CV25 and no i.MX chip ([Native SDK API catalog](acap-native-sdk-api-catalog.md)), so the intermediate tables are either wrong or reflect an undocumented temporary change. **Observed**, unresolved.
- **Chips leaving at 12.0**: the 12.0 note says S5L, S5, i.MX 6SoloX and i.MX 6ULL leave the active track, yet its API tables still list i.MX 6SoloX and drop S5/S5L/i.MX 6ULL without comment; 12.2 drops i.MX 6ULL and keeps i.MX 6SoloX. The compatibility page lists i.MX 6SoloX as supported at 12.x.
- **Naming drift**: Overlay API → Axoverlay API (4.15 on), Axparameter → Parameter API (4.14 on), Metadata Broker → Message Broker (12.0).
- **Root versus signing** are separate controls, but 4.12 and the signing page frame them differently without linking them.
- **Gaps**: 4.0 beta 1 cites a CV SDK build `21.27.3_1` outside the 10.x/11.x numbering; 12.2 has an empty `## Changes` heading; no notes exist between 4.15 and 12.0 beyond the alignment statement.

## Evidence and limits

Every row is **Reported** (the vendor's own notes, transcribed) and checked by static reading only; no SDK or device was run. Per-release contact addresses and external links are not reproduced. Product-level device lists inside each note were not transcribed.

## Relationships

- **Elaborates** [ACAP version rules](acap-versioning.md) and [ACAP generations and compatibility](acap-chip-architecture-and-sdk-compatibility.md).
- **Feeds** [Manifest schema 1.x history](acap-manifest-schema-v1-history.md) and [Native SDK API catalog](acap-native-sdk-api-catalog.md).
- **Precedes** [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md), which continues the root and signing arc.
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md), archive notice, and `redirect_to` front matter on each release-note page.
[^acap-docs-release-notes]: [release-notes/index.md](../raw/acap-documentation/docs/release-notes/index.md) and the pages `4.0_beta1.md`, `4.0.md` to `4.15.md`, `12.0.md` to `12.2.md` in the same folder: per-release sections "Minimum supported AXIS OS", "Changes", "Fixes", "Limitations", "Deprecation" and the API-compatibility tables.
