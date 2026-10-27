---
title: "Upgrade a manifest | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/upgrade-a-manifest/"
domain: "developer.axis.com"
language: "en"
description: "Upgrade within the same major version"
word_count: 694
---

Version: ACAP version 12

## Upgrade within the same major version

To upgrade your manifest within the same major version, change `schemaVersion` to the latest version available in your ACAP SDK. This is always recommended, since a newer schema may contain checks that prevent faulty values that would otherwise cause installation or runtime errors. The same checks will also be encountered when signing the ACAP package in the [ACAP Service Portal](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/#acap-service-portal).

## Upgrade to schema v2.x

Manifest schema v2.0 introduces a few changes that are incompatible with 1.x. To help understand the differences between versions, the table below compares the fields in manifest schema v1.x and v2.x:

| Field | v1.x | v2.x |
| --- | --- | --- |
| `appName` | Required | Required |
| `architecture` | Optional (set at build time) | Required (set at build time) |
| `compatibleOsVersions` | \- | Required — array of {min, max} OS version ranges |
| `runMode` | Required | Required |
| `vendor` | Required | Required |
| `vendorId` |  | Required — 10-char hex string |
| `version` | Required | Required |
| `embeddedSdkVersion` | Optional | Removed |
| `containers` | Optional | Removed |

The following table highlights additional restrictions introduced in schema v2.x for user and group definitions, D-Bus methods, and DLPU configuration.

| Field | v1.x | v2.x |
| --- | --- | --- |
| `acapPackageConf.setup.user.username` | Any\* | Restricted to `sdk` only |
| `acapPackageConf.setup.user.group` | Any\* | [Available groups](https://developer.axis.com/acap/how-to-guides/configure-application-user/#available-groups) |
| `resources.linux.user.groups` / `conditionalGroups` | Any\* | [Available groups](https://developer.axis.com/acap/how-to-guides/configure-application-user/#available-groups) |
| `resources.dbus.requiredMethods` / `conditionalMethods` | Any\* | [Available D-Bus methods](https://developer.axis.com/acap/how-to-guides/configure-application-user/#available-d-bus-methods) |
| `resources.deepLearningProcessor` | N/A | enabled + required |

> [!-secondary] -secondary
> note
> 
> \* `Any` means the manifest schema accepts any value, but framework rules still restrict what can be used. For example, `root` is not an allowed user, and some D-Bus methods are not allowed.
> 
> In manifest schema v1.x, these violations are typically detected at installation time. In manifest schema v2.x, they are validated earlier and can fail already at build time.

The sections below provide detailed information on some of the changes mentioned in the previous tables.

### Architecture

`architecture` is now required. The ACAP SDK will, as before, add this field automatically.

### Compatible OS Versions

`compatibleOsVersions` must contain information about which versions of AXIS OS that an application is compatible with.

These values will be enforced in AXIS OS 12.10 and later, and in the future, they may also need to match with version ranges specified in the [ACAP Service Portal](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/#acap-service-portal).

If a developer omits the `min` field, ACAP SDK 12.11 and later automatically sets it to a value that matches the minimum AXIS OS version that SDK is compatible with, which is the oldest version the SDK is guaranteed to be compatible with. If a value is explicitly provided, it is preserved and not modified by the SDK, even if it targets an earlier AXIS OS version. Developers must always specify the max field.

When manually specifying the `min` field, it is important to consider the patch number in the version triplet. The SDK is not guaranteed to be compatible with those OS versions that were built before the SDK, even within the same minor version.

#### Example 1: Prevent upgrade to next major

This application is built using ACAP SDK 12.11, so it cannot be guaranteed to work on AXIS OS versions earlier than 12.11. The `acap-build` script will automatically set the `min` field to 12.11. The developer hasn't verified that it will work on AXIS OS 13, or has decided against letting it upgrade to 13.

```json
{
    "compatibleOsVersions": [
        {
            "max": "12"
        }
    ]
}
```

#### Example 2: Compatible with next major

This application is built using ACAP SDK 12.11 and it is prepared to work on AXIS OS 13. The `acap-build` script will automatically set the `min` field to 12.11.

```json
{
    "compatibleOsVersions": [
        {
            "max": "13"
        }
    ]
}
```

### Resources

#### Restrictions on dbus, user and groups

The resources specified in the `dbus`, `user` and `groups` objects are restricted to an explicit set of allowed values. If your manifest violates these limitations, the error message from the validator should point you to which resource is at fault.

#### DLPU

If your application needs access to the DLPU on AXIS OS 13.0, you must add the following object to the resources section.

```json
{
    "deepLearningProcessor": {
        "enabled": true,
        "required": true
    }
}
```

Set required to false if you want your application to get installed even if DLPU access is not available.

#### Vendor ID

The `vendorId` field must match the vendor registered in the [ACAP Service Portal](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/#acap-service-portal).
