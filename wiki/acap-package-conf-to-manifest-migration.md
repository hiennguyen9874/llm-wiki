---
type: Concept
title: "Migrating ACAP applications from package.conf to manifest.json"
description: "Migration path from package.conf to manifest.json in ACAP 12: packageconf2manifest conversion, field mapping, discontinued features, acap-build packaging changes, and the revert caveat."
tags: [edge-ai, axis, acap, migration, manifest]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T15:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-package-conf-migration
    resource: ../raw/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/index.md
    scope: ../raw/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/
    kind: docs
    revision: "ACAP version 12"
    title: "Migrating from package.conf to manifest.json | Axis developer documentation"
---

# Migrating ACAP applications from package.conf to manifest.json

An ACAP application can be defined either by `manifest.json` or by the older `package.conf`. `manifest.json` has been the recommended form since ACAP SDK 3.3, and `package.conf` is deprecated in AXIS OS 12 and slated for removal in AXIS OS 13. Axis's migration path is mechanical: generate a starting `manifest.json` from the existing `package.conf` with `packageconf2manifest.py` inside the SDK container, then reconcile the fields the script cannot infer — most notably `embeddedSdkVersion`, version components, architecture, user/group, and packaged extra files. The durable value is the field mapping, the features that disappear, and the fact that reverting requires an uninstall that deletes `localdata`.[^acap-package-conf-migration]

## Before starting

Check the project directory for `manifest.json`. Its presence means the project already uses the recommended format. A project may contain **both** files even after migration, because `acap-build` generates a `package.conf` during the build for backward compatibility.[^acap-package-conf-migration]

## Generate an initial manifest.json

The conversion script ships in the ACAP Native SDK container. Enter the SDK container, navigate to the directory containing `package.conf`, look up the manifest schema version that matches the SDK, and run the script:[^acap-package-conf-migration]

1. Start an interactive shell in the SDK container as described in [Build, install, and control ACAP applications](acap-build-install-control.md).
2. `cd` to the directory that contains `package.conf`.
3. Find the SDK-to-schema mapping in the manifest schema documentation.
4. Run `packageconf2manifest.py --schema-version x.y.z`, substituting the mapped version.
5. Set `embeddedSdkVersion` to `"3.0"` in the generated `manifest.json`.

`packageconf2manifest.py -h` prints the script's help. This guide targets **manifest schema 1.x**; schema 2.x is a separate upgrade to perform only after this migration is complete. The v2 upgrade — required fields, `compatibleOsVersions`, resource restrictions, and DLPU declaration — is compiled in [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md).[^acap-package-conf-migration]

## Mapping between the two formats

The migration table pairs each `manifest.json` setting with its `package.conf` equivalent. Blank equivalents mean the guide shows no `package.conf` source field for that manifest field.[^acap-package-conf-migration]

| Setting | `manifest.json` | `package.conf` / file | Notes |
| --- | --- | --- | --- |
| Application identifier and main binary | `acapPackageConf.setup.appName` | `APPNAME` | Name of the application's executable binary |
| User-friendly application name | `acapPackageConf.setup.friendlyName` | `PACKAGENAME`, `MENUNAME` | Used by device management software |
| Vendor name | `acapPackageConf.setup.vendor` | `VENDOR` | Signing requires the name registered as an Axis Technology Integration Partner |
| Vendor homepage | `acapPackageConf.setup.vendorUrl` | `VENDORHOMEPAGELINK` | |
| Application version | `acapPackageConf.setup.version` | `APPMAJORVERSION`, `APPMINORVERSION`, `APPMICROVERSION` | Three numeric components become one version |
| Run user | `acapPackageConf.setup.user.username` | `APPUSR` | Omit to use the recommended dynamic user |
| Run group | `acapPackageConf.setup.user.group` | `APPGRP` | Omit to use the recommended dynamic user |
| Copy-protection identifier | `acapPackageConf.setup.appId` | `APPID` | Provided by Axis and required for Axis copy protection |
| Architecture | `acapPackageConf.setup.architecture` | `APPTYPE` | Generated at build time for architecture-dependent apps; `all` for architecture-independent apps |
| Execution behavior | `acapPackageConf.setup.runMode` | `STARTMODE` | `once`, `respawn`, `respawnOnFailure`, or `never` |
| Command-line options | `acapPackageConf.setup.runOptions` | `APPOPTS` | May be empty |
| Open-source licenses | file `LICENSE` | file `LICENSE` | |
| Copy-protection method | `acapPackageConf.copyProtection.method` | `LICENSEPAGE` | `axis`, `custom`, or `none` |
| Post-install script | `acapPackageConf.installation.postInstallScript` | `POSTINSTALLSCRIPT` | Runs on the device when installation completes |
| Pre-uninstall script | `acapPackageConf.uninstallation.preUninstallScript` | N/A | Runs on the device before uninstallation |
| Minimum embedded development version | `acapPackageConf.setup.embeddedSdkVersion` | `REQEMBDEVVERSION` | Depends on the APIs the application uses |
| Custom settings page | `acapPackageConf.configuration.settingPage` | `SETTINGSPAGEFILE` | File must be in the project's `html/` directory |
| CGI endpoint name | `acapPackageConf.configuration.httpConfig[].name` | `HTTPCGIPATHS` and file | Path relative to the application web root |
| CGI type | `acapPackageConf.configuration.httpConfig[].type` | — | For example `transferCgi` |
| CGI access policy | `acapPackageConf.configuration.httpConfig[].access` | — | Policy for calling the CGI |
| Parameter default | `acapPackageConf.configuration.paramConfig[].default` | file `param.conf` | |
| Parameter name | `acapPackageConf.configuration.paramConfig[].name` | — | |
| Parameter type | `acapPackageConf.configuration.paramConfig[].type` | — | Type definition string |
| Web client pages | folder `html/` | folder `html/` | |
| Bundled shared libraries | folder `lib/` | folder `lib/` | |
| Extra packaged files | N/A | `OTHERFILES` | Replaced by the `acap-build` option `-a` |

The architecture row carries a caveat: `architecture` is generated automatically for architecture-dependent applications and should not be added by hand; an architecture-independent application, such as a shell script, sets it to `all`.[^acap-package-conf-migration]

## Behavior that manifest.json removes

Two `package.conf` capabilities have no equivalent when the application uses `manifest.json`:[^acap-package-conf-migration]

- **Pre-upgrade script** — the script assigned to `PREUPGRADESCRIPT`, which ran before an application was installed as an upgrade.
- **Forking main process** — forking and daemonizing the application during startup.

The replacement for the second is operational rather than a manifest field: systemd starts the application, treats the death of the main process as failure, and writes stdout/stderr to the system log. That no-fork constraint is also recorded in [Build, install, and control ACAP applications](acap-build-install-control.md).[^acap-package-conf-migration]

## Build and packaging changes

A `package.conf` application is built with `create-package.sh`. For a `manifest.json` application the guide recommends the `acap-build` tool instead. Files that were previously listed in `OTHERFILES` must now be passed as `acap-build` inputs with `-a`, for example `acap-build . -a file1 -a file2`.[^acap-package-conf-migration]

`acap-build` still emits a `package.conf` for a manifest-based project, so the generated file may remain visible in the project. The guide says this compatibility output may be removed in the future. The full `acap-build` behavior and the available build paths are described in [Build, install, and control ACAP applications](acap-build-install-control.md).[^acap-package-conf-migration]

## Reverting the migration

Migrating back from `manifest.json` to `package.conf` is possible, but a `package.conf` application cannot be reinstalled over a version already installed as a manifest-based application. The application must be uninstalled and installed again; unlike a normal reinstall, that removes the `localdata` folder and its contents.[^acap-package-conf-migration]

## Coverage and limits

- **Entry point and scope:** `raw/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/index.md`, one 1,361-word page in the ACAP 12 documentation on `developer.axis.com`. The folder contains no subpages, images, or attachments.
- **Inspected:** the whole page — background, pre-checks, conversion steps, full field-mapping table (including the architecture footnote), discontinued features, build guidance, and revert caveat.
- **Not read:** linked pages outside this folder, including the manifest schema mapping, application project structure, manifest schemas, ACAP build guide, partner program page, and the shell-script example. Claims that depend on them are reported only as this page states them. The schema 2.x upgrade guide is now compiled separately as [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md).
- **No execution:** `packageconf2manifest.py`, `acap-build`, and a device install were not run, and no legacy project was converted. The conversion command and its output are therefore **Reported**, not **Reproduced**.
- **Capture noise:** three `> [!-info] -info` callouts repeat the word "info", and the background section contains the typo "Upcomming". Neither affects the technical content.
- **Scope boundary:** this page is the schema 1.x migration only. Schema 2.x and `compatibleOsVersions` are covered by [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md), and the AXIS OS 13 install rules by [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md), not by this source.

## Evidence class

All substantive claims are **Reported** from Axis's official ACAP 12 documentation, read on 2026-10-27. No claim is **Reproduced** or **Observed**. The ordering of the migration as a prerequisite for the schema 2.x upgrade is **Synthesis** from the source's explicit instruction to complete this migration first.

## Relationships

- **Depends on** [Build, install, and control ACAP applications](acap-build-install-control.md): the interactive SDK container is where `packageconf2manifest.py` runs, and `acap-build` is the replacement for `create-package.sh`.
- **Constrained by** [Phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md): the SDK-to-schema mapping selects the `--schema-version`, and `package.conf` support ends with AXIS OS 13.
- **Elaborated by** [Manifest schema 1.x history](acap-manifest-schema-v1-history.md): the schema versions (1.0 to 1.7.3) that the SDK-to-schema mapping selects, with the fields each added.
- **Precedes** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): the generated schema 1.x manifest is the input to the v2 field and resource upgrade.
- **Precedes** [Preparing ACAP applications for AXIS OS 13 and 14](acap-axis-os-13-14-migration.md): this schema 1.x migration is a prerequisite before the schema 2.x upgrade and `compatibleOsVersions` declaration that AXIS OS 13 requires.
- **Uses** [ACAP application user types and permissions](acap-application-user-permissions.md): both `setup.user.username` and `setup.user.group` should be omitted to keep the recommended dynamic user rather than carrying over a static user.
- **Elaborates** [Tạo, build và cài ACAP application đầu tiên](acap-first-application-workflow.md): the target format and the manifest fields used by a new project are the destination of this migration.
- **Contrasts with** a fresh project: migration must preserve the legacy field set and then remove pre-upgrade scripts and process forking, whereas a new manifest-based application never declares them.
- **Relates to** [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md): `settingPage` and `httpConfig` are part of this table, while reverse proxy left the post-install script for a manifest section in manifest 1.5.0.

[^acap-package-conf-migration]: Official documentation: [Migrating from package.conf to manifest.json — Axis developer documentation](../raw/acap/how-to-guides/migrating-from-package-conf-to-manifest-json/index.md), whole page: §Background, §Before starting, §Migration guide (§Generate initial manifest.json file, §Mapping between package.conf and manifest.json, §Discontinued support when using manifest.json, §Building .eap file), §Revert migration.
