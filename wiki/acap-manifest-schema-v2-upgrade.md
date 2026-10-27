---
type: Concept
title: "Upgrading an ACAP manifest to schema v2"
description: "How to move an ACAP manifest from schema 1.x to 2.x: same-major schema bumps, required fields, compatibleOsVersions semantics, resource restrictions, and validation timing."
tags: [edge-ai, axis, acap, manifest, compatibility, migration]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:28:00Z}
stale_after: 2027-04-30
sources:
  - id: acap-manifest-upgrade
    resource: ../raw/acap/how-to-guides/upgrade-a-manifest/index.md
    scope: ../raw/acap/how-to-guides/upgrade-a-manifest/
    kind: docs
    revision: "ACAP version 12"
    title: "Upgrade a manifest | Axis developer documentation"
---

# Upgrading an ACAP manifest to schema v2

An ACAP `manifest.json` is versioned by `schemaVersion`, and Axis separates two kinds of upgrade: a routine bump to the newest schema **within the current major version**, and the breaking move from schema 1.x to **schema 2.x**. The same-major bump is recommended because newer schemas can reject faulty values earlier, while the major upgrade changes required fields, removes others, redefines `compatibleOsVersions`, and narrows allowed `user`, `groups`, `dbus`, and DLPU resources.[^acap-manifest-upgrade]

## Updating within the same major version

To upgrade within the same major version, set `schemaVersion` to the latest version available in the ACAP SDK. This is always recommended: a newer schema may contain checks that prevent faulty values which would otherwise cause installation or runtime errors. The same checks are also applied when the package is signed in the [ACAP Service Portal](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/#acap-service-portal).[^acap-manifest-upgrade]

**Synthesis:** the major upgrade below is a separate, manual step; [Build, install, and control ACAP applications](acap-build-install-control.md) records that `acap-build` rewrites `schemaVersion` only within the same major version.

## Upgrading to schema v2.x

Manifest schema v2.0 introduces changes that are incompatible with 1.x. The field-level differences are:[^acap-manifest-upgrade]

| Field | v1.x | v2.x |
| --- | --- | --- |
| `appName` | Required | Required |
| `architecture` | Optional (set at build time) | Required (set at build time) |
| `compatibleOsVersions` | — | Required — array of `{min, max}` OS version ranges |
| `runMode` | Required | Required |
| `vendor` | Required | Required |
| `vendorId` | — | Required — 10-character hex string |
| `version` | Required | Required |
| `embeddedSdkVersion` | Optional | Removed |
| `containers` | Optional | Removed |

Schema v2.x also restricts values that schema 1.x accepted for the application user, groups, and D-Bus methods, and adds a required-form DLPU resource:[^acap-manifest-upgrade]

| Field | v1.x | v2.x |
| --- | --- | --- |
| `acapPackageConf.setup.user.username` | Any\* | Restricted to `sdk` only |
| `acapPackageConf.setup.user.group` | Any\* | Available groups only |
| `resources.linux.user.groups` / `conditionalGroups` | Any\* | Available groups only |
| `resources.dbus.requiredMethods` / `conditionalMethods` | Any\* | Available D-Bus methods only |
| `resources.deepLearningProcessor` | N/A | `enabled` + `required` |

\* `Any` means the manifest schema accepts any value, but framework rules still restrict what can be used — for example, `root` is not an allowed user and some D-Bus methods are not allowed. In schema v1.x these violations are typically detected at installation time; in schema v2.x they are validated earlier and can fail at build time.[^acap-manifest-upgrade]

## Architecture

`architecture` is required in v2.x. As before, the ACAP SDK adds the field automatically at build time.[^acap-manifest-upgrade]

## compatibleOsVersions

`compatibleOsVersions` must state which AXIS OS versions the application supports. The values are enforced on AXIS OS 12.10 and later and may in the future also need to match version ranges declared in the ACAP Service Portal.[^acap-manifest-upgrade] On AXIS OS 13 the field itself becomes mandatory, as recorded in [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md).

The `min` and `max` fields have different rules:[^acap-manifest-upgrade]

- `max` must always be specified by the developer.
- If `min` is omitted, ACAP SDK 12.11 and later sets it to the minimum AXIS OS version the SDK is compatible with — the oldest version the SDK is guaranteed to support.
- If `min` is explicitly provided, the SDK preserves it, even when it targets an AXIS OS version earlier than the SDK's own baseline.
- The patch number matters: an SDK is not guaranteed to work on AXIS OS versions built before the SDK, even within the same minor version.

The source gives two examples, both built with ACAP SDK 12.11, which automatically supplies `min: "12.11"`:[^acap-manifest-upgrade]

```json
{
    "compatibleOsVersions": [
        {
            "max": "12"
        }
    ]
}
```

This first application is not declared compatible with AXIS OS 13, so it is not allowed to upgrade to 13. The second declares compatibility with 13:[^acap-manifest-upgrade]

```json
{
    "compatibleOsVersions": [
        {
            "max": "13"
        }
    ]
}
```

## Resource-specific changes

### User, groups, and D-Bus

The resources in the `dbus`, `user`, and `groups` objects are restricted to an explicit set of allowed values. A manifest that violates these limits gets a validator error pointing to the resource at fault. The page points to the dynamic-user permission documentation for the allowed groups and D-Bus methods — see [ACAP application user types and permissions](acap-application-user-permissions.md).[^acap-manifest-upgrade]

### DLPU

An application that needs the DLPU on AXIS OS 13.0 must declare it in the `resources` section:[^acap-manifest-upgrade]

```json
{
    "deepLearningProcessor": {
        "enabled": true,
        "required": true
    }
}
```

Setting `required` to `false` allows the application to install even when DLPU access is unavailable, at the cost of handling the missing accelerator at runtime.[^acap-manifest-upgrade]

### Vendor ID

The `vendorId` field must match the vendor registered in the ACAP Service Portal, and it is a 10-character hex string.[^acap-manifest-upgrade] The signing guide records the exact-match rule for the account-specific `vendor` and `vendorId` values — see [ACAP application signing: service portal and signing service](acap-application-signing.md).

## Coverage and limits

- **Entry point and scope:** `raw/acap/how-to-guides/upgrade-a-manifest/index.md`, one 694-word page in the ACAP 12 documentation on `developer.axis.com`. The folder contains no subpages, images, or attachments.
- **Inspected:** the whole page — the same-major recommendation, both v1.x/v2.x comparison tables and the `Any` footnote, architecture, `compatibleOsVersions` rules and both JSON examples, resource restrictions, DLPU, and `vendorId`.
- **External links now compiled:** the ACAP Service Portal signing page is compiled as [ACAP application signing](acap-application-signing.md), and the user/group/D-Bus permission lists are compiled as [ACAP application user types and permissions](acap-application-user-permissions.md).
- **Not read:** the manifest schema reference itself, which the page does not link directly but which determines the exact schema version shipped with each SDK. The page names schema 2.x and 2.0, not a specific patch version, and gives no SDK-to-schema-version table.
- **No execution:** no manifest was validated, built, signed, or installed. All field requirements, validation timing, and `compatibleOsVersions` behavior are **Reported**, not **Reproduced**.
- **Capture noise:** the note about framework restrictions is captured with a malformed callout header (`> [!-secondary] -secondary`), and the source uses the future tense for the AXIS OS 12.10 enforcement. Neither changes the technical content.

## Evidence class

All substantive claims are **Reported** from Axis's official ACAP 12 documentation, read on 2026-10-27. No claim is **Observed** or **Reproduced**. The conclusion that `acap-build` cannot perform the major upgrade is **Synthesis** from the documented same-major rewrite in [Build, install, and control ACAP applications](acap-build-install-control.md) and the separate v2 procedure in this page.

## Relationships

- **Follows** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): the package.conf conversion produces a schema 1.x manifest, which is the input to this v2 upgrade.
- **Elaborates** [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md): the v2 field table, `compatibleOsVersions` mechanics, and resource restrictions are the manifest-level detail behind that page's breaking-change summary.
- **Constrained by** [Build, install, and control ACAP applications](acap-build-install-control.md): `acap-build` rewrites `schemaVersion` only within the same major version, so the 1.x-to-2.x step is manual.
- **Uses** [ACAP application user types and permissions](acap-application-user-permissions.md): v2 narrows `user.username` to `sdk` and restricts `user.group`, groups, and D-Bus methods to the documented allowed values.
- **Depends on** [ACAP application signing: service portal and signing service](acap-application-signing.md): `vendorId` is a v2 field whose value comes from the portal, and the non-TIP signing service accepts only v2.x manifests.
- **Applies to** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): the schema 1.7.4 manifest used by a new project needs this upgrade before it can target AXIS OS 13.
- **Related to** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the SDK version determines which schema versions are available and what `compatibleOsVersions.min` is set to.

[^acap-manifest-upgrade]: Official documentation: [Upgrade a manifest — Axis developer documentation](../raw/acap/how-to-guides/upgrade-a-manifest/index.md), whole page: §Upgrade within the same major version; §Upgrade to schema v2.x (§Architecture; §Compatible OS Versions including Example 1 and Example 2; §Resources — Restrictions on dbus, user and groups, DLPU, Vendor ID), including both comparison tables and the `Any` footnote.
