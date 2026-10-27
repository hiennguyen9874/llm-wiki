---
type: Concept
title: "Native SDK API catalog: APIs, introduction versions and chip support"
description: "Catalog of the ACAP Native SDK APIs as of 12.2 — what each does, the Native SDK release that introduced it, supported chips, beta status and renames — plus the ACAP 3 APIs that were replaced or left behind and an inventory of the generated API reference trees."
tags: [edge-ai, axis, acap, api, native-sdk]
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
  - id: acap-docs-native-api
    resource: ../raw/acap-documentation/docs/api/native-sdk-api.md
    scope: ../raw/acap-documentation/docs/api/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Native SDK API, Beta API and Computer Vision SDK API pages"
  - id: acap-docs-version-comparison
    resource: ../raw/acap-documentation/docs/introduction/acap-version-comparison.md
    scope: ../raw/acap-documentation/docs/introduction/acap-version-comparison.md
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "ACAP version comparison"
---

# Native SDK API catalog: APIs, introduction versions and chip support

The ACAP Native SDK exposes ten Axis-specific APIs, six open-source libraries and one supplementary mechanism (VAPIX access). Every Axis API entry states the chips it supports and the Native SDK version that introduced it; the page warns that the feature must also exist on the product — the Video capture API, for example, needs an image sensor.[^acap-docs-native-api] ARTPEC-9 appears in every chip list, which matches the 12.2 release that added it ([ACAP release history](acap-release-history.md)).

## Axis APIs

| API | Purpose (from the page) | Since SDK | Chips |
| --- | --- | --- | --- |
| Video capture (VDO) | Video streams; `libvdo` | 1.0 | ARTPEC-9/8/7/6, CV25 |
| Event (Axevent) | Send and receive events: stateless (pulse), stateful (state) and data events | 1.0 | ARTPEC-9/8/7/6, CV25 |
| License Key | Per-application licence checks | 1.0 | ARTPEC-9/8/7/6, CV25 |
| Machine learning (Larod) | Run models on the device accelerator; all larod API versions available | 1.0 | ARTPEC-9/8/7, CV25 (no ARTPEC-6) |
| Axoverlay | Draw overlays | 1.0 | ARTPEC-9/8/7/6 |
| Parameter | Application parameters, settings page | 1.13 | ARTPEC-9/8/7/6, CV25 |
| Edge storage | Storage access | 1.11 | ARTPEC-9/8/7/6, CV25, i.MX 6SoloX |
| Serial port | RS-232, RS-422, RS-485; product dependent | 1.11 | ARTPEC-9/8/7 |
| Bounding Box | Bounding-box drawing, listed under the Overlay APIs | 1.15 | ARTPEC-9/8/7, CV25 |
| Message Broker (**beta**) | Publish/subscribe consumption of AXIS OS metadata by topic; formerly Metadata Broker | 1.13 | ARTPEC-9/8/7, CV25 |

Open-source libraries: Cairo and OpenCL 1.2 (since 1.0; OpenCL on ARTPEC-9/8/7 only), FastCGI (1.6), OpenSSL, Jansson and Curl (1.14).[^acap-docs-native-api] The supplementary item is [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).

Details worth keeping:

- **VDO**: on ARTPEC-6 rotation can be set per stream; on all other platforms it is a global image-source option chosen at install time and per-stream rotation requests are ignored. The version table runs to AXIS OS 11.6 ↔ VdoStream 9.78.12.[^acap-docs-native-api]
- **Message Broker**: AXIS OS 11.9 ↔ API 0.23.2 with topic `com.axis.analytics_scene_description.v0.beta`; 11.11 ↔ 0.26.5 with `com.axis.consolidated_track.v1.beta`. The 4.15 release renamed callback `on_metadata` to `on_message`, and 12.0 renamed the API from Metadata Broker.[^acap-docs-native-api]
- **FastCGI** lists ARTPEC-9/8/7/6 and CV25 on the final page, while the release-note tables for 4.10 to 4.14 omitted ARTPEC-6 (and S5/S5L) and added i.MX 6SoloX and 6ULL; the final page restores ARTPEC-6 and drops the i.MX chips, so it is the most recent statement, but the intermediate change is never explained ([ACAP release history](acap-release-history.md)).
- **Beta rule**: Beta APIs are "for prototyping and should not be used for production"; feedback goes to the examples repositories' issue trackers.[^acap-docs-native-api]

Examples named in the page include `consume-scene-metadata` (Message Broker), `curl-openssl`, `vapix`, and the per-API examples in `acap-native-sdk-examples`, covered in [Official ACAP application examples](acap-application-examples.md).

## ACAP 3 APIs replaced or left behind

The version-comparison page records what happened to ACAP 3 APIs when the Native SDK succeeded the ACAP SDK:[^acap-docs-version-comparison]

| ACAP 3 API | Replacement in the Native SDK |
| --- | --- |
| axHTTP | `web-server` and `web-server-using-fastcgi` examples; see [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md) |
| axSerialPort | Serial Port API, Native SDK 1.11 |
| axStorage | Edge Storage API, Native SDK 1.11 |
| axParameter | Parameter API, Native SDK 1.13 |
| axAudio | "Will get a new API in a later release" (no replacement stated in this source) |
| axPTZ | "Not yet decided" |
| Capture (Media capture) | Video capture API (VDO); Capture was removed from SDK 3.5 |

The ACAP 3 reference additionally lists Audio (axaudio), HTTP (axhttp) and Pan-tilt-zoom (axptz), which have no Native SDK API page ([ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md)).

## Container-side APIs

The archived Computer Vision SDK page documents the container-side equivalents: a gRPC video-capture client (`vdo_proto_utils.VideoCaptureClient`, `get_frame`), a TensorFlow Serving inference client (`tf_proto_utils.InferenceClient`, `infer`), a beta Parameter API, and Python packages (NumPy, OpenCV, Flask). The SDK was archived and refactored into ACAP Runtime, new AXIS OS 12.x products have no container support, and existing container products are supported to end of 2031. See [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md).[^acap-docs-native-api]

## Generated API reference trees (inventory only)

| Tree | Files | Contents |
| --- | ---: | --- |
| `docs/api/src` | 890 | Doxygen HTML (2025) for axevent, axoverlay, axparameter, axserialport, axstorage, bbox, larod, licensekey, message-broker, vdostream, plus original C examples |
| `docs/acap-sdk-version-3/api/src` | 1,052 | Doxygen HTML (2022) for the ACAP 3 libraries including axaudio, axhttp, axptz and capture |
| `3.5/` | 1,052 | Duplicate of the previous tree except three redirect stubs |
| `3.4/` | 49 | Only the deprecated `capture` library and stubs |

Version markers in headers: liblarod 3.2.254 and Message Broker 0.29.2 in the Native tree; liblarod 3.1.28 in the ACAP 3 tree. `docs/api/_setup_apidocs.sh -v <ver>` swaps in new generated docs; its baked list is `axevent axoverlay axparameter axserialport axstorage bbox larod licensekey vdostream` plus `message-broker` (or `metadata-broker` for versions matching `4.x`), and its accepted versions are 4.x or 10 and above.[^acap-docs-native-api] These trees were inventoried by file listing and header sampling, not read in full; the repository is an archived snapshot whose pages all redirect to `developer.axis.com` ([ACAP documentation repository](acap-documentation-repository.md)).[^acap-docs-repo]

## Evidence and limits

Catalog content is **Reported** and read statically. Chip lists are transcribed per API; product-level availability is not stated. The header-level behaviour of each API was not read. The Native SDK 12.x versions of the API pages in the later `raw/acap/` capture, if any, were not compared.

## Relationships

- **Part of** [ACAP Native SDK and the Axis camera application platform](axis-acap-native-sdk.md), whose "public SDK capabilities" section this refines with versions and chips.
- **Supersedes** the ACAP 3 API set listed above; see [ACAP SDK version 3 (legacy)](acap-sdk-version-3-legacy.md).
- **Depends on** [ACAP release history](acap-release-history.md) for the release that introduced each API.
- **Uses** [Axis DLPU](axis-dlpu.md) through Larod for model inference.
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-native-api]: [native-sdk-api.md](../raw/acap-documentation/docs/api/native-sdk-api.md) §Compatibility, each API's "Compatibility" and "Version history" subsections, §Open Source APIs, §Supplementary APIs; `beta-api.md`; `computer-vision-sdk-apis.md` top notice and API sections; `_setup_apidocs.sh`; file counts from `find` over `docs/api/src`, `docs/acap-sdk-version-3/api/src`, `3.4/`, `3.5/`.
[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; `diff -r 3.5 docs/acap-sdk-version-3/api/src` differs only in three redirect stubs.
[^acap-docs-version-comparison]: [acap-version-comparison.md](../raw/acap-documentation/docs/introduction/acap-version-comparison.md) §What are the differences … (APIs replacement table).
