---
type: Concept
title: "ACAP application user types and permissions"
description: "Static versus dynamic ACAP application users: manifest fields, acap-<appName> identity and addon group, permission grants through Linux groups and D-bus methods, and data ownership migration."
tags: [edge-ai, axis, acap, manifest, security]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:28:00Z}
stale_after: 2027-04-30
sources:
  - id: acap-app-user
    resource: ../raw/acap/how-to-guides/configure-application-user/index.md
    scope: ../raw/acap/how-to-guides/configure-application-user/
    kind: docs
    revision: "ACAP version 12"
    title: "Configure application user | Axis developer documentation"
  - id: acap-manifest-upgrade
    resource: ../raw/acap/how-to-guides/upgrade-a-manifest/index.md
    scope: ../raw/acap/how-to-guides/upgrade-a-manifest/
    kind: docs
    revision: "ACAP version 12"
    title: "Upgrade a manifest | Axis developer documentation"
---

# ACAP application user types and permissions

An ACAP application needs a valid OS user to run as, and the manifest chooses between two models: a **static user** that already exists on the device, or a **dynamic user** that is created at install and removed at uninstall. Dynamic users are the recommended default since ACAP 4.0, but they start with only the `addon` group, so any API that checks group membership or D-bus method access must be granted explicitly through `resources.linux.user.groups` (plus `conditionalGroups` from manifest schema 1.8.0) and `resources.dbus.requiredMethods` (plus `conditionalMethods`). Static users remain the only option for ACAP 3, where Axis recommends the `sdk` user and group even though `sdk` will eventually be deprecated.[^acap-app-user]

## Choosing a user type

A native ACAP application runs on AXIS OS, which is Linux-based, so it runs as a user. When creating the application the user is selected in one of two ways:[^acap-app-user]

| Type | Definition |
| --- | --- |
| Dynamic user | A user created for the application when it is installed |
| Static user | A user that already exists on the device |

Since its introduction in ACAP 4.0, the dynamic user is what Axis recommends for ACAP applications. In ACAP 3 and prior the static user was the only option, and there Axis recommends setting `sdk` as both user and group — noting that the `sdk` user and group are subject to deprecation at some point in the future.[^acap-app-user] The horizon for that deprecation is now documented: from AXIS OS 13 the only permitted non-dynamic user is `sdk`, with the same permissions as the dynamic user, and `sdk` is scheduled for removal in AXIS OS 14 ([migration notes](acap-axis-os-13-14-migration.md)).

Manifest schema v2 hardens those framework rules inside the schema: `acapPackageConf.setup.user.username` accepts only `sdk`, while `setup.user.group`, `resources.linux.user.groups`/`conditionalGroups`, and `resources.dbus.requiredMethods`/`conditionalMethods` accept only the documented allowed values. A v2 violation can be rejected at build time, whereas v1 violations typically surfaced at installation time.[^acap-manifest-upgrade]

## Static user configuration

A static user requires `acapPackageConf.setup.user.username` and `acapPackageConf.setup.user.group` in `manifest.json`. Both the user and the group must exist and must be **permitted to be selected**; for example, from AXIS OS 12.0 it is no longer permitted to use the `root` user or group for an ACAP application.[^acap-app-user]

```json
{
    "schemaVersion": "1.7.0",
    "acapPackageConf": {
        "setup": {
            "appName": "static_user_app",
            "friendlyName": "App with static user",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0",
            "user": {
                "group": "sdk",
                "username": "sdk"
            }
        }
    }
}
```

## Dynamic user configuration

For a dynamic user, neither `acapPackageConf.setup.user.username` nor `acapPackageConf.setup.user.group` shall be specified, because the system sets them. The user name becomes `acap-<appName>` and the primary group is `addon`. One or more secondary groups may be declared in the manifest, and again each group must exist and must be permitted for the dynamic user to select it. Some resources — `dbus` in the manifest, for instance — are supported **only** for the dynamic user.[^acap-app-user]

```json
{
    "schemaVersion": "1.7.0",
    "acapPackageConf": {
        "setup": {
            "appName": "dynamic_user_app",
            "friendlyName": "App with dynamic user",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0"
        }
    }
}
```

## Granting permissions to a dynamic user

Membership in `addon` alone leaves the dynamic user without the rights many use cases need, so the manifest grants more. Two mechanisms exist: Linux groups for APIs that check group membership, and D-bus method access for APIs that call protected methods.[^acap-app-user]

### Additional groups

`resources.linux.user.groups` adds secondary groups. Example: the Edge Storage API (`axstorage`) requires membership in the `storage` group.[^acap-app-user]

```json
{
    "schemaVersion": "1.7.0",
    "resources": {
        "linux": {
            "user": {
                "groups": ["storage"]
            }
        }
    },
    "acapPackageConf": {
        "setup": {
            "appName": "dynamic_user_app",
            "friendlyName": "App with user in storage group",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0"
        }
    }
}
```

### Conditional groups

A group may be unavailable or not permitted on some devices while remaining usable on others. From **manifest schema 1.8.0**, `resources.linux.user.conditionalGroups` adds such groups conditionally: the application keeps working when the group cannot be obtained. The documented case is the `pipewire` group for the Pipewire audio API.[^acap-app-user]

```json
{
    "resources": {
        "linux": {
            "user": {
                "groups": ["storage"],
                "conditionalGroups": ["pipewire"]
            }
        }
    }
}
```

### Available groups

| Group | Needed for |
| --- | --- |
| `admin` | Parameter API |
| `operator` | Parameter API |
| `viewer` | Parameter API |
| `storage` | Axstorage API |
| `metadata` | Message Broker API |
| `gpu` | OpenCL, OpenGL ES |
| `pipewire` | Pipewire |
| `video` | Bounding Box API |
| `hidraw` | HIDRAW access for ACAP |

Each row's APIs are links into the official *Supported APIs* reference, which is outside `raw/` and not verified in this ingest.[^acap-app-user]

### D-bus methods

Some supported APIs require the application user to reach D-bus methods. The documented example is the VAPIX API, which uses `com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials`. `resources.dbus.requiredMethods` grants it to the dynamic user.[^acap-app-user] What the application then does with that method — acquiring an admin-level service-account credential and calling VAPIX on `127.0.0.12` — is compiled in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).

```json
{
    "schemaVersion": "1.7.0",
    "resources": {
        "dbus": {
            "requiredMethods": ["com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials"]
        }
    },
    "acapPackageConf": {
        "setup": {
            "appName": "dynamic_user_app",
            "friendlyName": "App with VAPIX access",
            "vendor": "Axis Communications",
            "embeddedSdkVersion": "3.0",
            "runMode": "never",
            "version": "1.0.0"
        }
    }
}
```

### Conditional D-bus methods

`resources.dbus.conditionalMethods` mirrors conditional groups: methods are requested, and the application still runs when they are unavailable. The documented snippet grants the VAPIX credentials method unconditionally and the AxOverlay/Bounding Box graphics methods conditionally.[^acap-app-user]

```json
{
    "resources": {
        "dbus": {
            "requiredMethods": ["com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials"],
            "conditionalMethods": ["com.axis.Graphics2.*"]
        }
    }
}
```

### Available D-bus methods

| D-bus method | Needed for |
| --- | --- |
| `com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials` | VAPIX API |
| `com.axis.Graphics2.*` | AxOverlay API (legacy), Bounding Box API |
| `com.axis.Overlay2.*` | AxOverlay API (legacy), Bounding Box API |
| `com.axis.RecordingNotify1.*` | Recording Notify API |
| `com.axis.RecordingPlayback1.*` | Recording Playback API |
| `com.axis.RecordingSearch1.*` | Recording Search API |

As with the group table, the API targets are external reference links and their current content was not verified.[^acap-app-user]

## Static versus dynamic user

|  | Static user | Dynamic user |
| --- | --- | --- |
| Availability | Already existing on the device | Created when the application is installed and removed when it is uninstalled |
| Primary group | As set for the existing user | `addon` |
| Secondary group(s) | As set for the existing user | `resources.linux.user.groups` or `resources.linux.user.conditionalGroups` in the manifest |
| Executing user | `acapPackageConf.setup.user.username` in the manifest | `acap-<appName>`, where `<appName>` is `acapPackageConf.setup.appName` in the manifest |
| Executing group | `acapPackageConf.setup.user.group` in the manifest | `addon` |

## Migrating application data when the user changes

On upgrade, files and folders stored in the application folder are backed up and restored during the process, and if the application user changed between the installed version and the upgrade version, ownership of those files is correctly set to the new user. Data the application stores **outside** the application folder is not covered and must be handled by the application itself; one documented workaround is a post-install or pre-uninstall script that changes ownership.[^acap-app-user]

Up until AXIS OS 11.11 LTS such scripts can run as the `root` user by setting the `AllowRoot` toggle to on, even when the application itself runs as a non-root user. The documented script derives the application user from the owner of `localdata`, checks whether it runs as root, and re-owns a data area on the SD card:[^acap-app-user]

```sh
#!/bin/sh -e

# Get the application user by asking for the owner of the applications localdata folder
UID_DOT_GID="$(stat -c %u.%g localdata)"

# Check if the script runs as root
IS_ROOT=$([ "$(id -u)" -eq 0 ] && echo true || echo false)

# Specify the path to data that needs ownership to be changed, e.g. on the SD card
APP_NAME="$(basename "$(pwd)")"
SD_CARD_AREA=/var/spool/storage/SD_DISK/areas/"$APP_NAME"

# Change ownership if the script runs as root and the data exists
if $IS_ROOT && [ -d "$SD_CARD_AREA" ]; then
 chown -R "$UID_DOT_GID" "$SD_CARD_AREA"
fi
```

## Source coverage

- Entry point: `raw/acap/how-to-guides/configure-application-user/index.md` (1242 words), site `developer.axis.com`, revision "ACAP version 12". The folder holds this one file; no images, attachments, or supporting artifacts.
- Supporting source: `raw/acap/how-to-guides/upgrade-a-manifest/index.md` (694 words), read for the schema v2 restrictions on `user`, `groups`, and `dbus` and for the build-time validation change.
- Every section was read in full: user-type difference, static and dynamic `manifest.json` examples, group and D-bus permissions including conditional variants and both availability tables, the static-versus-dynamic comparison, and the data-migration script.
- The page fences its JSON examples as `markdown` and one snippet as `sh`; the JSON is reproduced here as JSON with whitespace preserved except for the abbreviated fragments, which are kept verbatim.
- Out-of-`raw/` targets, unverified: *Supported APIs* reference (all group and D-bus method rows), the manifest schema version mapping page, and the Parameter, Axstorage, Message Broker, OpenCL, OpenGL ES, Pipewire, Bounding Box, HIDRAW, AxOverlay, Recording Notify/Playback/Search API anchors. The VAPIX access how-to guide is now compiled as [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
- Limits in the source: no minimum AXIS OS version is given per feature beyond the 12.0 `root` prohibition and the 1.8.0 schema requirement for conditional entries; no deprecation timeline for the `sdk` user; nothing on how a running application is affected by an ownership change outside the application folder; the script's behavior on systems without an SD card area is only implied by the `-d` guard.

## Evidence class

All content is **Reported** from official Axis documentation (ACAP version 12 set), read on 2026-10-27. Nothing is **Reproduced**: no application was built or installed, no manifest validated against a schema, and no migration script executed.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): the user model, manifest resources, and group/D-bus permission surfaces belong to the ACAP platform rather than to application code.
- **Constrained by** [breaking changes của AXIS OS 13/14](acap-axis-os-13-14-migration.md): từ AXIS OS 13 chỉ còn `sdk` là non-dynamic user được phép, và `sdk` bị bỏ trong AXIS OS 14; các giá trị `dbus`, `user`, `groups` bị giới hạn theo danh sách cho phép của dynamic user.
- **Constrained by** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): schema v2 narrows static user selection to `sdk`, restricts group and D-Bus resources, and can reject violations at build time.
- **Constrained by** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the `root` prohibition starts at AXIS OS 12.0 and conditional groups need manifest schema 1.8.0, so the schema and OS versions bound what can be declared.
- **Used by** [SSH và Developer Mode trên thiết bị Axis](axis-device-ssh-developer-mode.md): the `acap-<appName>` dynamic user is the account Developer Mode exposes over SSH.
- **Enables** the Parameter, Axstorage, Message Broker, OpenCL/OpenGL ES, Pipewire, Bounding Box, HIDRAW, VAPIX, AxOverlay, and Recording APIs, each through a specific group or D-bus method grant; the VAPIX flow is detailed in [VAPIX access from ACAP applications](acap-vapix-service-account-access.md).
- **Follows** [Build, install, and control ACAP applications](acap-build-install-control.md): permissions take effect at install, and upgrade/reinstall is what carries the data-ownership migration.

[^acap-app-user]: Tài liệu chính thức: [Configure application user — Axis developer documentation](../raw/acap/how-to-guides/configure-application-user/index.md), toàn bộ trang: §Difference between the application user types (§Example of manifest.json for an application with a static user, §Example of manifest.json for an application with a dynamic user), §Adding permissions to dynamic user (§Configure additional groups, §Conditional groups, §Available groups, §Configure access to D-bus methods, §Conditional D-bus methods, §Available D-bus methods), §Static user vs. dynamic user, §Migrating application with data stored on the device. Các liên kết ra ngoài (`supported-apis`, manifest schema mapping, VAPIX access guide) chưa được kiểm chứng.
[^acap-manifest-upgrade]: Official documentation: [Upgrade a manifest — Axis developer documentation](../raw/acap/how-to-guides/upgrade-a-manifest/index.md), §Upgrade to schema v2.x: additional-restrictions table and its `Any` footnote.
