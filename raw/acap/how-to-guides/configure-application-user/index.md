---
title: "Configure application user | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/configure-application-user/"
domain: "developer.axis.com"
language: "en"
description: "Difference between the application user types"
word_count: 1242
---

Version: ACAP version 12

## Difference between the application user types

A native ACAP application runs on AXIS OS, and as with any application that runs on a Linux-based OS, it needs a valid user to run as. When creating the application the user can be selected in two ways. Either by selecting a **dynamic user**, i.e. a user that will be created for the application when it is installed, or by selecting a **static user**, i.e. a user that already exists on the device.

Since its introduction in ACAP version 4.0, it's recommended to use a **dynamic user** in ACAP applications. In ACAP version 3 and prior, the **static user** was the only option and there it is recommended to set `sdk` as user and group. Note, though, that the `sdk` user and group is subject to be deprecated at some point in the future.

### Example of manifest.json for an application with a static user

If setting up the ACAP application for a static user, the `acapPackageConf.setup.user.username` and `acapPackageConf.setup.user.group` fields need to be specified in the manifest file. Note that, both the user and the group need to exist and need to be permitted to be selected. E.g., from AXIS OS 12.0 it is no longer permitted to use the `root` user or group for an ACAP application.

```markdown
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

### Example of manifest.json for an application with a dynamic user

If setting up the ACAP application for a dynamic user neither `acapPackageConf.setup.user.username` nor `acapPackageConf.setup.user.group` shall be specified in the manifest file, as these will be set by the system. The name of the user will be `acap-<appName>` and the primary group will be `addon`. It is possible to specify one or more secondary groups that the user should belong to in the manifest. Again, any such group needs to exist and it needs to be permitted for the dynamic user to select that group. Also note that some **resources**, such as **dbus** in the manifest file, are only supported for the dynamic user.

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

## Adding permissions to dynamic user

Since the basic case of a dynamic user only has the permissions given to it by being a member of the `addon` group it is easy to see that it would run in to permission issues for many use cases that a static user may be able to perform. Here we list different ways of solving these issues.

### Configure additional groups

Some of the [supported APIs](https://developer.axis.com/acap/reference/supported-apis/) require that the application user is a member of the correct group in order to use them. One such example is the Edge Storage API, axstorage, that requires being a member of the `storage` group. This can be added to the dynamic user by setting `resources.linux.user.groups` to `["storage"]` in the manifest as shown below.

```markdown
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

#### Conditional groups

There might be occasions when a group doesn't exist or isn't allowed to be added to the dynamic user on specific devices, but you still want the application to have access to it on other devices that do not have the same restriction. From [manifest schema 1.8.0](https://developer.axis.com/acap/reference/manifest-schemas/general-info/#manifest-schema-version-mapping), this can be accomplished by adding the group *conditionally* with the `conditionalGroups` field in the manifest file. For example, you may want the `pipewire` group for the [Pipewire](https://developer.axis.com/acap/reference/supported-apis/#pipewire) audio API, but if it isn't obtainable, you still want the rest of the application to work:

```markdown
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

#### Available groups

Here is a table of available groups and for which APIs they are needed:

| Group | Needed for |
| --- | --- |
| `admin` | [Parameter API](https://developer.axis.com/acap/reference/supported-apis/#parameter-api) |
| `operator` | [Parameter API](https://developer.axis.com/acap/reference/supported-apis/#parameter-api) |
| `viewer` | [Parameter API](https://developer.axis.com/acap/reference/supported-apis/#parameter-api) |
| `storage` | [Axstorage API](https://developer.axis.com/acap/reference/supported-apis/#axstorage-api) |
| `metadata` | [Message Broker API](https://developer.axis.com/acap/reference/supported-apis/#message-broker-api) |
| `gpu` | [OpenCL](https://developer.axis.com/acap/reference/supported-apis/#opencl), [OpenGL ES](https://developer.axis.com/acap/reference/supported-apis/#opengl-es) |
| `pipewire` | [Pipewire](https://developer.axis.com/acap/reference/supported-apis/#pipewire) |
| `video` | [Bounding Box API](https://developer.axis.com/acap/reference/supported-apis/#bounding-box-api) |
| `hidraw` | [HIDRAW access for ACAP](https://developer.axis.com/acap/reference/supported-apis/#hidraw-access-for-acap) |

### Configure access to D-bus methods

Some of the [supported APIs](https://developer.axis.com/acap/reference/supported-apis/) require that the application user has access to D-bus methods. One such example is the VAPIX API, which uses the `com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials` D-bus method. This can be added to the dynamic user by specifying it in `resources.dbus.requiredMethods` in the manifest as shown below. For more info about the VAPIX API, see [VAPIX access for ACAP applications](https://developer.axis.com/acap/how-to-guides/VAPIX-access-for-ACAP-applications/).

```markdown
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

#### Conditional D-bus methods

Similarly to having [conditional groups](#conditional-groups), it's possible to have conditional D-bus methods by adding the methods to the `conditionalMethods` field in the manifest file. Here is a snippet of how that could be configured:

```markdown
{
    "resources": {
        "dbus": {
            "requiredMethods": ["com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials"],
            "conditionalMethods": ["com.axis.Graphics2.*"]
        }
    }
}
```

#### Available D-bus methods

Here is a table of available D-bus methods and for which APIs they are needed:

| D-bus method | Needed for |
| --- | --- |
| `com.axis.HTTPConf1.VAPIXServiceAccounts1.GetCredentials` | [VAPIX API](https://developer.axis.com/acap/reference/supported-apis/#vapix-access-for-acap) |
| `com.axis.Graphics2.*` | [AxOverlay API](https://developer.axis.com/acap/reference/supported-apis/#axoverlay-api-legacy), [Bounding Box API](https://developer.axis.com/acap/reference/supported-apis/#bounding-box-api) |
| `com.axis.Overlay2.*` | [AxOverlay API](https://developer.axis.com/acap/reference/supported-apis/#axoverlay-api-legacy), [Bounding Box API](https://developer.axis.com/acap/reference/supported-apis/#bounding-box-api) |
| `com.axis.RecordingNotify1.*` | [Recording Notify API](https://developer.axis.com/acap/reference/supported-apis/#recording-notify-api) |
| `com.axis.RecordingPlayback1.*` | [Recording Playback API](https://developer.axis.com/acap/reference/supported-apis/#recording-playback-api) |
| `com.axis.RecordingSearch1.*` | [Recording Search API](https://developer.axis.com/acap/reference/supported-apis/#recording-search-api) |

## Static user vs. dynamic user

|  | Static user | Dynamic user |
| --- | --- | --- |
| Availability | Already existing on the device | Created when application is installed and removed when it is uninstalled |
| Primary group | As set for the existing user | `addon` |
| Secondary group(s) | As set for the existing user | Set by `resources.linux.user.groups` or `resources.linux.user.conditionalGroups` in the manifest |
| Executing user | Set by `acapPackageConf.setup.user.username` in the manifest | `acap-<appName>` where \<appName> is set by `acapPackageConf.setup.appName` in the manifest |
| Executing group | Set by `acapPackageConf.setup.user.group` in the manifest | `addon` |

## Migrating application with data stored on the device

When upgrading an application any files and folders stored in the application folder will be backed up and restored during the process. If the application user is changed between the initial version of the application and the upgrade version the ownership of the files and folders will be correctly set to the new user. However, any files and folders stored, by the application, outside of the application folder, needs to be handled by the application itself. If such data exists and the ownership of it needs to be migrated one work-around is to utilize either a post-install or a pre-uninstall script. Up until AXIS OS 11.11 LTS it is possible to run such scripts as the root user by setting the `AllowRoot` toggle to on. This is the case even when the application itself has a non-root user. An example script for changing the ownership of files and folders:

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
