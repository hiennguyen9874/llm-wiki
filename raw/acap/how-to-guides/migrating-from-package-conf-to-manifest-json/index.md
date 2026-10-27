---
title: "Migrating from package.conf to manifest.json | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/"
domain: "developer.axis.com"
language: "en"
description: "This page will help you migrate your ACAP application from being based on"
word_count: 1361
---

Version: ACAP version 12

This page will help you migrate your ACAP application from being based on `package.conf` to being based on `manifest.json`.

> [!-info] -info
> info
> 
> This guide describes migration from `package.conf` to `manifest.json` using schema 1.x. If you need schema 2.x, first complete this migration, then follow [Upgrading to schema 2.x](https://developer.axis.com/acap/how-to-guides/upgrade-a-manifest/#upgrade-to-schema-v2x).

## Background

There are currently two ways to define an application and its configuration, using `manifest.json` or `package.conf`. Since its introduction in ACAP SDK 3.3, `manifest.json` has been the recommended option, and it's highly encouraged to migrate from `package.conf` to `manifest.json`. In AXIS OS 12, `package.conf` is deprecated and will be removed in AXIS OS 13, as announced in [Upcomming breaking changes](https://help.axis.com/en-us/axis-os#acap-applications).

## Before starting

To figure out if this migration guide is relevant for you, check for a file named `manifest.json` in your ACAP application project files directory. If it exists, congratulations! You're already using the recommended `manifest.json`. If not, consider following this migration guide.

> [!-info] -info
> info
> 
> Your project may contain both `manifest.json` and `package.conf` files, as `acap-build` generates a `package.conf` during application building.

## Migration guide

To migrate to using `manifest.json`, a `manifest.json` file has to be created, containing the same configuration as your current `package.conf`.

### Generate initial manifest.json file

It is possible to generate an initial `manifest.json` file based on the configuration in your `package.conf` file by using the conversion script available in the ACAP Native SDK container. Alternatively, see [Manifest file](https://developer.axis.com/acap/reference/application-project-structure/#manifestjson) to create a `manifest.json` file from scratch. Follow these instructions to generate an initial `manifest.json` file:

1. Follow the instructions in [Building interactively inside the SDK container](https://developer.axis.com/acap/how-to-guides/build-install-run/#building-interactively-inside-the-sdk-container) to enter into the SDK container shell prompt.
2. Navigate to the directory containing the `package.conf` file.
3. Find the manifest schema version you want to validate against by checking the mapping between the SDK and schema in [Manifest schema version mapping](https://developer.axis.com/acap/reference/manifest-schemas/general-info/#manifest-schema-version-mapping).
4. Run `packageconf2manifest.py --schema-version x.y.z` (insert the version found from the step above).
5. In the newly created `manifest.json` file, set the value of `embeddedSdkVersion` to "3.0".

To invoke help on using **packageconf2manifest**, run `packageconf2manifest.py -h`.

### Mapping between package.conf and manifest.json

The table below shows the package configuration with `manifest.json` file, in relationship with the `package.conf` file.

For a list of all manifest fields and information on which that are required, see [Manifest schemas](https://developer.axis.com/acap/reference/manifest-schemas/general-info/).

| Setting | With manifest file | In package conf and files | Description |
| --- | --- | --- | --- |
| Application identifier and main binary | acapPackageConf.   setup.   appName | APPNAME | The name of the application’s executable binary file. |
| The user friendly name of the application | acapPackageConf.   setup.   friendlyName | PACKAGENAME   MENUNAME | A user-friendly package name, to be used by for instance device management software, when referring to the application. |
| Name of the application vendor | acapPackageConf.   setup.   vendor | VENDOR | The name of the vendor that created the application, to be used by for instance device management software, when referring to the vendor. Signing an application requires this field be set to the name you registered with as an [Axis Technology Integration Partner](https://www.axis.com/partner/technology-integration-partner-program) |
|  | acapPackageConf.   setup.   vendorUrl | VENDORHOMEPAGELINK | Specifies a link to the vendor’s homepage, to be used by for instance device management software, when referring to the vendor. |
| Version for the ACAP application | acapPackageConf.   setup.   version | APPMAJORVERSION | A numerical value of the application’s major version. |
|  |  | APPMINORVERSION | A numerical value of the application’s minor version. |
|  |  | APPMICROVERSION | A numerical value of the application’s micro version. |
| User and group for execution and file ownership | acapPackageConf.   setup.   user.username | APPUSR | The user that the application will run as. It's recommended to use [dynamic user](https://developer.axis.com/acap/reference/application-project-structure/#user-and-group) by not specifying user with this field. |
|  | acapPackageConf.   setup.   user.group | APPGRP | The group that the application will run as. It's recommended to use [dynamic user](https://developer.axis.com/acap/reference/application-project-structure/#user-and-group) by not specifying group with this field. |
| ID of the application in Axis ACAP portal | acapPackageConf.   setup.   appId | APPID | The application copy protection identifier. Provided by Axis and required when using Axis copy protection solution. |
| Application architecture | acapPackageConf.   setup.   architecture [^1] | APPTYPE | The automatically generated architecture of the application. For architecture-independent applications, this field can be set to `all`. |
| The execution behavior of the application | acapPackageConf.   setup.   runMode | STARTMODE | Defines how the application is started. Possible values are:   \- **once** The application will be started at boot.   \- **respawn** The application will be started at boot and restarted if it exits.   \- **respawnOnFailure** The application will be started at boot and restarted if it exits with a non-zero exit code.   \- **never** The application will never be started automatically, only through a VAPIX request. |
| Special options for binary execution | acapPackageConf.   setup.   runOptions | APPOPTS | Contains the application command-line options (may be empty). |
| Open source licenses file | file: `LICENSE` | file: `LICENSE` | A file containing all open source licenses of the application. |
| Copy protection solution | acapPackageConf.   copyProtection.   method | LICENSEPAGE | Specifies if a copy protection solution is used by the application. Possible values are:   \- **axis** Protected by Axis copy protection license solution.   \- **custom** Protected by a custom copy protection license solution, not provided by Axis.   \- **none** Not protected by any license copy protection license solution. |
| Application specific installation script | acapPackageConf.   installation.   postInstallScript | POSTINSTALLSCRIPT | A shell script that runs on the device when the installation is completed. |
| Application specific uninstallation script | acapPackageConf.   uninstallation.   preUninstallScript | N/A | A shell script that runs on the device before uninstallation of application is started. |
| Required embedded development version | acapPackageConf.   setup.   embeddedSdkVersion | REQEMBDEVVERSION | Specifies the minimum required embedded development version that the device running the application must support. The version is dependent on the set APIs used in the application. |
| Application specific setting page | acapPackageConf.   configuration.   settingPage | SETTINGSPAGEFILE | Specifies the HTML page for custom settings, to be used by for instance device management software, allowing a user to browse the application settings page. The file must be in a directory called `html` in the application project. |
| Supported CGI endpoints | acapPackageConf.   configuration.   httpConfig\[\].name | HTTPCGIPATHS and file | CGI path relative to application web root |
| Package custom files in application | N/A | OTHERFILES | This option in `package.conf` has been replaced by a [build tool](https://developer.axis.com/acap/how-to-guides/build-install-run/#the-acap-build-tool) option and is not part of `manifest.json`. An example `acap-build . -a file1 -a file2` |
|  | acapPackageConf.   configuration.   httpConfig\[\].type |  | CGI implementation type, e.g. transferCgi |
|  | acapPackageConf.   configuration.   httpConfig\[\].access |  | Access policy for calling the CGI |
| Product integrated application parameters | acapPackageConf.   configuration.   paramConfig\[\].default | file: param.conf | Parameter default value |
|  | acapPackageConf.   configuration.   paramConfig\[\].name |  | Name of the parameter |
|  | acapPackageConf.   configuration.   paramConfig\[\].type |  | Parameter type definition string |
| Application specific web client pages | folder: `html/` | folder: `html/` |  |
| Application specific dynamically linked libraries | folder: `lib/` | folder: `lib/` |  |

### Discontinued support when using manifest.json

The following is no longer supported for an ACAP application, when using a `manifest.json` file:

- **Pre-upgrade script** – Script assigned to `PREUPGRADESCRIPT` in `package.conf` that runs before an application is installed as an upgrade.
- **Forking main process** – Forking and demonizing of the application during start.

> [!-info] -info
> info
> 
> Instead of the application forking the main process, the application is started by systemd, which assumes failure if the main process dies, and writes any output to stdout/stderr to the system log.

### Building.eap file

Building an application based on `package.conf` application is done with the `create-package.sh` script. When building an application based on `manifest.json`, it is instead recommended to use the [build tool](https://developer.axis.com/acap/how-to-guides/build-install-run/#the-acap-build-tool). If any additional files were previously listed in `OTHERFILES` in `package.conf`, these now need to be listed as inputs to the `acap-build` command using the flag `-a`, for example `acap-build . -a file1 -a file2`.

When building an application based on `manifest.json`, a `package.conf` file will be generated by `acap-build`, so you might still see it in your project files. Note however that the generated `package.conf` might be removed in the future. For now, it's generated for compatibility reasons.

## Revert migration

Migrating from `manifest.json` to `package.conf` is possible, but there is no support for reinstalling a `package.conf` application that is already installed as a version that uses `manifest.json`. Instead, the application must be uninstalled and installed again. The difference between doing this and a normal reinstalling is that the localdata folder and its content will be deleted.

[^1]: This parameter is generated at the build step for architecture-dependent applications and should not be added. For architecture-independent applications, e.g. like a [shell script](https://github.com/AxisCommunications/acap-native-sdk-examples/blob/master/shell-script-example/app/manifest.json), the architecture can be set to `all` in the `manifest.json` file.
