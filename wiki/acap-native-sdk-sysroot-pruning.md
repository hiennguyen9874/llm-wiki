---
type: Concept
title: "ACAP Native SDK sysroot pruning: which Axis OS libraries are hidden from applications"
description: "How the SDK Dockerfiles overlay the acap-api sysroot and then delete legacy directories, libraries, pkg-config files and headers (apr, boost, gnutls, protobuf, python, paho, udev and more), why it matters for linking, and how the lists change over time."
tags: [edge-ai, axis, acap, sdk, sysroot, docker, libraries]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T18:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-native-sdk-repo
    resource: ../raw/acap-native-sdk/README.md
    scope: ../raw/acap-native-sdk/
    kind: code
    revision: "12.10.0-2-geed6dcf (eed6dcff23c17e744b773473646251752b91184f, 2026-08-18)"
    title: "AxisCommunications/acap-native-sdk (git submodule)"
---

# ACAP Native SDK sysroot pruning: which Axis OS libraries are hidden from applications

After overlaying the Axis OS API sysroot onto the toolchain sysroot, both Dockerfiles delete a long block-list of "legacy" content from `/opt/axis/acapsdk/sysroots/${ARCH}/usr/lib` and `usr/include`. The result is that an application built in the SDK image can only link against and include what the sysroot still carries; libraries on this list are present on the camera's firmware image but are deliberately not offered as ACAP build dependencies.[^acap-native-sdk-repo] This page records the lists and their meaning; the surrounding build steps are in [SDK image assembly](acap-native-sdk-image-assembly.md).

Evidence class: **Observed** from `Dockerfile.aarch64` lines 69-186 (identical in `Dockerfile.armv7hf` offset by two lines). The pruning was not executed, so the actual sysroot contents are **Unverified**. The glob patterns are reproduced as written; what each library is used for outside this file is common knowledge, not stated in the repo.

## Mechanism

The API image supplies `usr/lib`, `usr/include`, `usr/share/protobuf` and one `nlohmann_json.pc` (copied into `usr/lib/pkgconfig`). Because the API sysroot is an overlay on the toolchain sysroot, the pruning step has to remove things from the result rather than choose what to copy. Four layers run with `WORKDIR` set to the target directory, so each `rm` uses relative globs:[^acap-native-sdk-repo]

| Layer | Directory | Removed |
| --- | --- | --- |
| Directories (lines 70-86) | `usr/lib` | `*.d`, `apr-util*`, `*-poky-linux*`, `conf-migrate`, `dbus-*`, `gdk-pixbuf-*`, `icu`, `legacyconfig`, `modules`, `opkg`, `python3*`, `rcscripts`, `service_registry`, `systemd`, `udev` |
| Files and symlinks (lines 89-129) | `usr/lib` | `*-poky-linux*`, `apr*`, `libapac*`, `libax_daemon*`, `libboost_*`, `libcapture*`, `libevent.so*`, `libgcrypt*`, `libgmp*`, `libgnutls*`, `libgpg-error*`, `libhogweed*`, `libicu*`, `libjpeg*`, `liblzma*`, `libmagic*`, `libmenu*`, `libmicrohttpd*`, `libmount*`, `libnet_http*`, `libnettle*`, `libpaho*`, `libpango*`, `libparam*`, `libprotobuf*`, `libprotoc*`, `libpython*`, `libscene*`, `libsdbusplus*`, `libservice_registry*`, `libsmartcols*`, `libsqlite*`, `libti*`, `libturbojpeg*`, `libubsan*`, `libudev*`, `libuser_manager*`, `libyuv*`, `os-release` |
| pkg-config (lines 132-155) | `usr/lib/pkgconfig` | `.pc` files for the same families, plus `gmp`, `gmpxx`, `gnutls`, `gpg-error`, `hogweed`, `nettle`, `sdbusplus`, `service_registry`, `video-service`, `python*`, `libprotobuf-c.pc` |
| Headers (lines 158-186) | `usr/include` | `ax_daemon.h`, `axis`, `capture*`, `dbus-*`, `event.h`, `gcrypt.h`, `gmock`, `gmp-32.h`, `gmp.h`, `gmpxx.h`, `gnutls`, `google`, `gpg-error*`, `gpgrt*`, `gtest`, `libyuv*`, `magic.h`, `microhttpd.h`, `nettle`, `pango-*`, `protobuf-c`, `python3*`, `sdbusplus`, `service_registry.h`, `video-service` |

## Why it matters to developers (Synthesis)

- **Linking and header errors.** A project that needs a library on this list (for example Boost, GnuTLS, libjpeg, libturbojpeg, SQLite, libpaho MQTT or libyuv) will not find it in the SDK sysroot. The documented remedy is to cross-compile and bundle the library inside the application, as described in [third-party libraries](acap-third-party-libraries.md). Presence of a library in the firmware does not imply it is part of the SDK contract.
- **Public SDK surface is defined negatively.** Of the APIs that the SDK documents in the [API catalog](acap-native-sdk-api-catalog.md), the ones with libraries not in this list remain visible. For example `libparam*` and `libax_daemon*` are removed here, while `axaudio` and `axhttp` were deleted from the lists in `0751145` (2025-06-13) to bring those APIs back. Whether the catalog and these lists are kept in sync is **Unverified**; the catalog page was compiled from an older documentation snapshot (12.2).
- **Protobuf is split.** `usr/share/protobuf/` is copied from the API image (so `.proto` definitions are available), while `libprotobuf*`, `libprotoc*`, `usr/include/google` and `protobuf-c` pieces are deleted. **Observed** asymmetry; the Dockerfile gives no rationale. Treat protobuf use as requiring a bundled implementation unless the documentation says otherwise.
- **Python is excluded.** `python3*`, `libpython*` and the `python*` pkg-config files are removed, although the final Ubuntu stage installs Python 3 for tooling (see [image assembly](acap-native-sdk-image-assembly.md)); host Python and the target sysroot are separate.

## How the lists change

Commits show the block-list being edited as a maintenance activity (subjects and diffs from `git log`/`git show`, **Observed**):[^acap-native-sdk-repo]

- `19ec803` (#86, 2026-05-04): `libpaho` removal from the SDK (one line added per Dockerfile; the `libpaho*` entry in the lib-file list).
- `8b054d1` (2025-11-04) added `libnlohmann*` and `nlohmann` to the block list; `b351c0b` (2025-11-05) reverted a merge (PR #5, branch `changes/remove-api/libnlohmann`) and the diff deletes exactly those entries again, so no `nlohmann` entry remains in the lists at HEAD. `nlohmann_json.pc` is additionally copied in explicitly (`030dc43`, #87), so nlohmann_json is a deliberate exception to the overlay-and-prune pattern. Why the add and revert happened is not stated.
- `0751145` (#74, 2025-06-13): re-added `axaudio` and `axhttp` by deleting `libaxaudio*`, `libaxhttp*`, `axaudio.pc`, `axhttp.pc` and `axsdk/axaudio*`, `axsdk/axhttp*` from the lists.

The removal of `libpaho` (MQTT client) is the most consequential visible change for users who relied on it; no migration note exists in the repo, so how it is communicated (release notes) is outside this evidence.

## Limits

- The API and toolchain images were not available, so which of the glob patterns actually match files is unknown; some entries may be no-ops. `rm -rf` and `rm -f` tolerate non-matching globs.
- Rationale per library is not stated in the Dockerfile; only the section comments say "legacy" (lines 69, 88, 131, 157). Reasons in this page are labeled Synthesis or are omitted.
- Compatibility between this pruning and the 12.x/13.x manifest and API changes is not covered here; see [AXIS OS 13 and 14 migration](acap-axis-os-13-14-migration.md).

## Relationships

- **Part of** [SDK image assembly](acap-native-sdk-image-assembly.md) in [ACAP Native SDK repository](acap-native-sdk-repository.md).
- **Constrains** [Integrating third-party libraries into ACAP applications](acap-third-party-libraries.md): libraries on the block-list must be built and bundled by the application.
- **Related to** [Native SDK API catalog](acap-native-sdk-api-catalog.md): the catalog lists the supported APIs; this page lists the libraries the SDK image hides.

[^acap-native-sdk-repo]: [AxisCommunications/acap-native-sdk](../raw/acap-native-sdk/README.md) at `eed6dcf`: `Dockerfile.aarch64` lines 58-63 (API overlay), 69-86, 88-129, 131-155, 157-186 (removal lists); `Dockerfile.armv7hf` same sections at +2 offset; `git log` and `git show` of `19ec803`, `8b054d1`, `b351c0b`, `0751145`, `030dc43`.
