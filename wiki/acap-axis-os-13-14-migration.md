---
type: Concept
title: "Preparing ACAP applications for AXIS OS 13 and 14"
description: "Breaking changes an ACAP application built with Native SDK 12 faces on AXIS OS 13/14 — enforced signing, mandatory compatibleOsVersions, restricted user/group resources, Larod and VDO removals — and the four-step migration path."
tags: [edge-ai, axis, acap, compatibility, migration, manifest]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:28:00Z}
stale_after: 2027-04-30
sources:
  - id: acap-future-os-major
    resource: ../raw/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/index.md
    scope: ../raw/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/
    kind: docs
    revision: "ACAP version 12"
    title: "Extend compatibility to future AXIS OS major versions | Axis developer documentation"
---

# Preparing ACAP applications for AXIS OS 13 and 14

An application built with **Native SDK 12** against AXIS OS 12.11 can stop working when the device is upgraded to AXIS OS 13.x, and a failed application installation during that upgrade can trigger a **rollback** of the OS upgrade itself. Axis therefore publishes the breaking changes relevant to application developers together with a four-step migration path, and names the changes already planned for AXIS OS 14 so they can be absorbed before the release. The guide is written for SDK 12 but states it is just as relevant for earlier SDK versions.[^acap-future-os-major]

## Migration path

The documented sequence is short, and its ordering matters: nothing is rebuilt until the application has been checked against the list of removed functionality and permissions.[^acap-future-os-major]

| Step | Action |
| --- | --- |
| 1 | **Review breaking changes** — verify the application uses no functionality or permission that AXIS OS 13 no longer supports |
| 2 | **Rebuild if needed** — change the application where it depends on a listed breaking change |
| 3 | **Reinstall** — install the updated application on the device; this is treated as an application upgrade, so state and data are preserved |
| 4 | **Test on AXIS OS 13** — upgrade the device once AXIS OS 13 is available and verify the application behaves as expected |

The reinstall in step 3 is deliberately an upgrade, not a fresh install: application data survives, which is why an in-place state migration does not have to be re-planned for this step.

## Breaking changes in AXIS OS 13

Only changes relevant to application developers are listed by the guide; the full OS-level list lives in the AXIS OS 13 release notes.[^acap-future-os-major]

| Area | Change | Effect on an application |
| --- | --- | --- |
| Application signing | Applications must be signed | Unsigned applications remain installable during development, but **not** in the preview release of AXIS OS 13 |
| Version declaration | `compatibleOsVersions` in the manifest becomes **mandatory** | An application is installed only if it declares compatibility with the target AXIS OS version. The field was introduced as optional in AXIS OS 12.10 |
| Manifest schema | Only schema v2 supports `compatibleOsVersions` | Manifests on schema v1 are not supported in AXIS OS 13, and `package.conf` as the configuration file is no longer supported |
| Install/uninstall scripts | New rules for post-install and pre-uninstall scripts | Script files need executable permissions; must finish within **5 minutes**; shell scripts must start with `#!/bin/sh`; a non-zero post-install exit fails the installation; `umask` is 022 at script start, so new files are world-readable but writable only by the application user |
| `dbus`, `user`, `groups` resources | Restricted to an explicit set of allowed values | Permitted values are the ones listed for adding permissions to the dynamic user. The only permitted non-dynamic user is `sdk`, which gets the same permissions as the dynamic user and is **scheduled for removal in AXIS OS 14** |
| DLPU access | Must be declared in the manifest | Without the `deepLearningProcessor` object, the application cannot use the DLPU; `required: false` still installs when DLPU access is unavailable |
| Larod model format | `.larod` format support removed | Convert models to `.tflite` |
| Larod API version | Versions 1 and 2 removed | Migrate to at least Larod API version 3 |
| VDO timestamp type | `uint16_t` option for the stream `timestamp` type removed | Adapt to `uint32_t` |
| VDO overlay enums | Non-functional `vdo_overlay_color_get_type` and `vdo_overlay_text_size_get_type` removed | Remove usage; they were never functional |
| VDO deprecated functions | Crop settings, `vdo_frame_get_is_last_buffer`, `vdo_frame_get_fd`, `vdo_frame_get_opaque` removed | Replace or drop the calls |
| Message Broker API | Removed, replaced by **Device Data Hub API** | The same data is available in the same format and no VAPIX parameters change; the client side must target the new API |
| SD card installation | Installing and running applications on an SD card removed | The beta feature was never officially supported or documented in the VAPIX Application API; a rework is planned |

### Declaring DLPU access

The resource object the manifest needs, placed in the `resources` section:[^acap-future-os-major]

```json
{
    "deepLearningProcessor": {
        "enabled": true,
        "required": true
    }
}
```

Setting `required` to `false` keeps the application installable on devices where DLPU access is not available, at the cost of having to handle the missing accelerator at runtime.

## Breaking changes in AXIS OS 14

The only application-facing change the guide already lists for AXIS OS 14 is the **removal of the legacy `axhttp` API** (the HTTP API from the ACAP version 3 documentation, supported in ACAP SDK 3.5). The recommendation is to make the application compatible with it now rather than after the release, and the guide explicitly warns that further deprecations and breaking changes may still be added to the AXIS OS 14 list.[^acap-future-os-major]

## What this implies for upgrade planning

**Synthesis**, built from the table and from [the build/packaging behavior](acap-build-install-control.md):

- The mandatory `compatibleOsVersions` field turns a manifest-schema question into an upgrade blocker: a manifest on schema v1, or one built from `package.conf`, fails at install time on AXIS OS 13 rather than at runtime. Because `acap-build` rewrites `schemaVersion` only to the highest version **within the same major version** and fills `compatibleOsVersions.min` for v2 manifests, a v1.x manifest needs the explicit major upgrade described in [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md); the SDK thresholds remain 12.10.0 for the compatibility field and 12.11.0 for the same-major rewrite.
- Enforced signing means the development habit of installing unsigned builds has a hard end at AXIS OS 13 preview. A production signing path, not a per-developer workaround, is the prerequisite for shipping to 13.x.
- The 5-minute script budget forbids long install-time work such as model download or on-device conversion; such work has to move into first-run application logic.
- The `sdk` user survives only one major version, so any manifest still using a static `sdk` user has to move to the dynamic user model before AXIS OS 14; see [ACAP application user types and permissions](acap-application-user-permissions.md).
- Because an application install failure during the OS upgrade can roll the OS back, testing the `.eap` install as an **upgrade** (step 3) is not optional for fielded devices.

## Coverage and limits

- Entry point: `raw/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/index.md` (938 words), part of the ACAP version 12 documentation set; the whole page was read and it carries no figures or assets.
- Material the page defers to that is **not** in `raw/`: the ACAP section of the AXIS OS 13 and 14 release notes, the Larod API-changes migration guide, the VDO deprecated list, the dynamic-user permission list, and the VAPIX Application API. The manifest upgrade guide is now compiled as [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md), which records the v2 field and resource deltas; the exact allowed values for `dbus`, `user`, and `groups` are compiled in [ACAP application user types and permissions](acap-application-user-permissions.md). The signing guide is now in `raw/` and compiled as [ACAP application signing](acap-application-signing.md).
- The page gives no release dates for AXIS OS 13 or 14 and no minimum SDK version per breaking change; the SDK thresholds above are inferred from the compatibility field's introduction in AXIS OS 12.10 and from `acap-build`'s documented rewriting behavior.
- The capture has formatting noise: four `> [!-info] -info` callouts whose body repeats "info", one bullet written as `- -` inside the script list, and a missing space in "API experienceand". None of it was carried into this concept.

## Evidence

All substantive claims are **Reported** from Axis's official ACAP 12 documentation, read on 2026-10-27. No claim is **Reproduced** or **Observed**: no application was rebuilt or installed, and no AXIS OS 13 device was available. The planning implications section is **Synthesis**.

## Relationships

- **Depends on** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the ACAP version must match the target AXIS OS LTS, and a major OS jump changes more than the version number.
- **Follows** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): a legacy `package.conf` application must first finish that schema 1.x migration before the schema 2.x upgrade and compatibility declaration required here.
- **Elaborated by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): the v2 field table, `compatibleOsVersions` rules, and resource restrictions are the manifest-level mechanics behind the breaking changes summarized here.
- **Constrains** [Build, install, and control ACAP applications](acap-build-install-control.md): `compatibleOsVersions` and schema v2 become mandatory, and unsigned installation stops working on AXIS OS 13 preview.
- **Constrains** [ACAP application user types and permissions](acap-application-user-permissions.md): from AXIS OS 13 only `sdk` is allowed as a non-dynamic user, and it is removed in AXIS OS 14.
- **Requires** [ACAP application signing](acap-application-signing.md): the signed-only policy this page reports as enforced is the install-time consequence of the signing workflow, whose two partner paths and manifest values are recorded there.
- **Constrains** [Triển khai custom AI model lên camera Axis](axis-custom-model-deployment.md) and [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): DLPU access must be declared in the manifest, `.larod` is gone, and Larod API v1/v2 are removed in favor of v3.
- **Affects** [SSH và Developer Mode trên thiết bị Axis](axis-device-ssh-developer-mode.md): the SSH developer path for 12.11 must be re-checked when the device moves to 13.x.

[^acap-future-os-major]: Official documentation: [Extend compatibility to future AXIS OS major versions — Axis developer documentation](../raw/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/index.md), whole page: §introduction (four migration steps), §Breaking changes in AXIS OS 13 (Enforcement of application signing; AXIS OS version compatibility declaration; Changed rules for application install/uninstall scripts; Restrictions on dbus, user and groups; Machine learning API (Larod) — usage declaration, removal of `.larod`, removal of Larod version 1 & 2; Video capture API (VDO) — `uint16_t` timestamp, overlay enums, deprecated functions; Message Broker API; SD card installation), §Breaking changes in AXIS OS 14 (Removal of axhttp API).
