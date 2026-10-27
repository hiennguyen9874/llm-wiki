---
title: "Extend compatibility to future AXIS OS major versions"
site: "Axis developer documentation"
source: "https://developer.axis.com/acap/how-to-guides/extend-compatibility-to-future-axis-os-major-versions/"
domain: "developer.axis.com"
language: "en"
description: "This guide describes how to make an application built with Native SDK 12"
word_count: 938
---

Version: ACAP version 12

This guide describes how to make an application built with Native SDK 12 compatible with AXIS OS 13. Upgrading a device from AXIS OS 12.11 to 13.x introduces breaking changes that may break your application or even trigger a rollback upon application installation during AXIS OS upgrade. Follow the steps below to update your application.

> [!-info] -info
> info
> 
> Note that this guide is just as relevant when using earlier versions of the SDK.

1. **Review breaking changes**: Ensure your ACAP application does not use any functionality or permissions that are not supported in AXIS OS 13, listed in [Changes for ACAP application in AXIS OS 13](https://help.axis.com/en-us/axis-os#acap-applications).
2. **Rebuild application if needed**: If your application depends on any of the listed breaking changes, update it to align with the new requirements.
3. **Reinstall the application**: Install the updated application on the device. This is treated as an application upgrade, preserving state and data.
4. **Test application on AXIS OS 13**: When available, upgrade the device to AXIS OS 13 and test that the application works as expected.

## Breaking changes in AXIS OS 13

> [!-info] -info
> info
> 
> This table only lists breaking changes relevant for application developers. For a full list of breaking changes, see [AXIS OS 13 breaking changes](https://help.axis.com/en-us/axis-os#changes-in-axis-os-13).

### Enforcement of application signing

Applications are required to be signed. See the [ACAP application signing](https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/) page for signing information.

> [!-info] -info
> info
> 
> It will be possible to install unsigned applications during development, but not in the preview release of AXIS OS 13.

### AXIS OS version compatibility declaration

In AXIS OS 12.10, an optional field `compatibleOsVersions` was introduced in the application manifest that specifies the AXIS OS versions the application supports. From AXIS OS 13, this field will be mandatory, and applications will only get installed if they state compatibility with the target AXIS OS version.

> [!-info] -info
> info
> 
> Note that only manifests using manifest schema v2 support this feature, meaning that manifests using schema v1 won't be supported in AXIS OS 13. Additionally, using `package.conf` as the configuration file won't be supported either. See [Upgrade to schema v2](https://developer.axis.com/acap/how-to-guides/upgrade-a-manifest/#upgrade-to-schema-v2x) for more information.

### Changed rules for application install/uninstall scripts

If an application contains a post-install script or a pre-uninstall script, the following rules will apply:

- The scripts files must have executable permissions.
- The scripts must complete within 5 minutes.
- If they are shell scripts, they must start with #!/bin/sh.
- If the post-install script exits with anything else than zero, installation will fail.
- - The umask will be 022 when the script starts, ensuring that newly created files are readable by all users, but writable only by the application user.

### Restrictions on dbus, user and groups

The resources specified in the `dbus`, `user` and `groups` objects in the manifest will be restricted to an explicit set of allowed values. The permitted resources match those listed in [Adding permissions to dynamic user](https://developer.axis.com/acap/how-to-guides/configure-application-user/#adding-permissions-to-dynamic-user).

The only non-dynamic user permitted will be the `sdk` user, which will have the same permissions as the dynamic user. The `sdk` user is scheduled for removal in AXIS OS 14.

### Machine learning API (Larod)

#### Usage declaration in the manifest

If your application needs access to the DLPU, you must add the following object to the `resources` section in the manifest.

```json
{
    "deepLearningProcessor": {
        "enabled": true,
        "required": true
    }
}
```

Set `required` to false if you want your application to get installed even if DLPU access is not available.

#### Removal of.larod model format

Support for the `.larod` model format will be removed from the [Machine learning API (Larod)](https://developer.axis.com/acap/reference/supported-apis/#machine-learning-api-larod). Use the `.tflite` format instead.

#### Removal of Larod version 1 & 2

Version 1 and 2 of the [Machine learning API (Larod)](https://developer.axis.com/acap/reference/supported-apis/#machine-learning-api-larod) will be removed. Migrate to at least version 3 of the API according to the migration guide found in [Changes in the Larod API](https://developer.axis.com/acap/acap-native-sdk-version-12/api/src/api/larod/html/md__opt_builder-doc_larod_doc_api-changes.html).

### Video capture API (VDO)

#### Removal of uint16\_t for VDO\_TIMESTAMP

The `uint16_t` option for choosing `timestamp` type when creating a stream with [Video capture API (VDO)](https://developer.axis.com/acap/reference/supported-apis/#video-capture-api-vdo) will be removed. Adapt to `uint32_t`.

#### Removal of overlay enums

Non-functional enums in the [Video capture API (VDO)](https://developer.axis.com/acap/reference/supported-apis/#video-capture-api-vdo) will be removed to improve API experienceand avoid false expectations that these enums would be working. The following enums will be removed:

- `vdo_overlay_color_get_type`
- `vdo_overlay_text_size_get_type`

#### Removal of deprecated functions

The following [Video capture API (VDO)](https://developer.axis.com/acap/reference/supported-apis/#video-capture-api-vdo) functions will be removed:

- `Crop settings`
- `vdo_frame_get_is_last_buffer`
- `vdo_frame_get_fd`
- `vdo_frame_get_opaque`

For more information, see the [Deprecated list](https://developer.axis.com/acap/acap-native-sdk-version-12/api/src/api/vdostream/html/deprecated.html) in the API documentation.

### Message Broker API will be removed and replaced by Device Data Hub API

The [Message Broker API](https://developer.axis.com/acap/reference/supported-apis/#message-broker-api) will be removed. The same data previously provided via Message Broker will be available through the [Device Data Hub API](https://developer.axis.com/acap/reference/supported-apis/#device-data-hub-api) in the same format. No VAPIX parameters will change.

### Remove the ability to install and run applications on SD card

This is a beta feature that has never been officially supported or documented in the [VAPIX Application API](https://developer.axis.com/vapix/applications/application-api/). For security reasons it will be removed in AXIS OS 13. A rework is planned for the future.

## Breaking changes in AXIS OS 14

Here is an extended list of breaking changes planned for AXIS OS 14. It is recommended to already now update your application to be compatible with these changes.

> [!-info] -info
> info
> 
> Note that there might be additional deprecations and breaking changes in AXIS OS 14 that are not listed here yet.

> [!-info] -info
> info
> 
> This table only lists breaking changes relevant for application developers. For a full list of breaking changes, see [AXIS OS 14 breaking changes](https://help.axis.com/en-us/axis-os#changes-in-axis-os-14).

### Removal of axhttp API

The legacy API, axhttp (see [HTTP API](https://developer.axis.com/acap/3/api/#http-api) in the ACAP version 3 documentation), supported in ACAP SDK 3.5 will be removed in AXIS OS 14.
