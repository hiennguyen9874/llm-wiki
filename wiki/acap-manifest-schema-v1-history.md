---
type: Concept
title: "Manifest schema 1.x history and field reference"
description: "How the ACAP manifest.json schema evolved from 1.0 to 1.7.3: version-to-AXIS-OS-to-SDK mapping, fields and constraints added at each step, the core field set, signing's 1.3 minimum, and the places where the docs disagree."
tags: [edge-ai, axis, acap, manifest, schema]
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
  - id: acap-docs-manifest-schemas
    resource: ../raw/acap-documentation/docs/develop/manifest-schemas/index.md
    scope: ../raw/acap-documentation/docs/develop/manifest-schemas/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Manifest schemas and schema field descriptions v1.0 to v1.7.3"
  - id: acap-docs-project-structure
    resource: ../raw/acap-documentation/docs/develop/application-project-structure.md
    scope: ../raw/acap-documentation/docs/develop/application-project-structure.md
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Application project structure"
---

# Manifest schema 1.x history and field reference

The ACAP `manifest.json` schema went through twelve published 1.x versions between AXIS OS 10.7 and 12.2; each is tied to a minimum AXIS OS and a Native SDK version. Early versions added the building blocks (`resources`, uninstall script, `architecture`), the middle ones added web exposure and D-Bus permissions, and the last ones tightened naming rules. The latest 1.x schema is 1.7.3; the 2.x line that AXIS OS 13 requires is covered in [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md).[^acap-docs-manifest-schemas] The archive marks the per-version field pages as "automatically generated from manifest schema", and the repository forbids hand-editing them.[^acap-docs-repo]

## Version map

| Schema | AXIS OS | SDK | Change |
| --- | --- | --- | --- |
| 1.0 | 10.7 | 1.0 | Initial basic version |
| 1.1 | 10.7 | 1.0 | Additional fields: `resources` (D-Bus, dynamic Linux user), `fastCgi` http type |
| 1.2 | 10.7 | 1.0 | Uninstall support (`uninstallation.preUninstallScript`), needed by Docker Compose ACAP |
| 1.3 | 10.9 | 1.1 | `architecture` (`all`, `aarch64`, `armv7hf`) added at packaging; first schema usable for signing |
| 1.3.1 | 11.0 | 1.4 | `schemaVersion` becomes three-part; `=` allowed in `runOptions`; `appName` max length 26 |
| 1.4.0 | 11.7 | 1.11 | `( ) , . ! ? & '` allowed in `vendor` |
| 1.5.0 | 11.8 | 1.12 | Reverse-proxy config; web-content access policy; `-` in secondary groups; `.*` in D-Bus method lists |
| 1.6.0 | 11.9 | 1.13 | `$` and `\` in reverse-proxy `apiPath`; optional `$schema`; `-` in D-Bus method strings |
| 1.7.0 | 11.10 | 1.14 | `containers.containerHost` and `containers.createDockerSymlinks` |
| 1.7.1 | 12.0 | 12.0.0 | `-` in `user` and `group`; `appName` must start with a letter and have at least two characters |
| 1.7.2 | 12.1 | 12.1.0 | `friendlyName`: no `\n` or `\r`, max 256 characters |
| 1.7.3 | 12.2 | 12.2.0 | Reverse-proxy `apiPath` of length 1 allowed |

Recommendation from the index: use the newest schema in the SDK. When signing, the ACAP Portal validates against the latest released schema **within the same major version**, and the minimum for signing is 1.3 because that version introduced the mandatory-for-signing `architecture` field.[^acap-docs-manifest-schemas]

## Field reference (stable core)

Fields are optional unless marked required.[^acap-docs-manifest-schemas]

- **Top level**: `schemaVersion` (required; two-part up to 1.3, three-part from 1.3.1), `$schema` (1.6.0+), `acapPackageConf`, `resources` (1.1+).
- **`acapPackageConf.setup`**: `appName` (required, the executable name), `vendor` (required), `version` (required, semver), `runMode` (required: `respawn` restarts on exit; `once` is not restarted but runs again after reboot; `never` is never restarted), `runOptions`, `friendlyName`, `vendorUrl`, `appId` (Axis-issued, for copy protection), `embeddedSdkVersion`, `architecture` (1.3+), `user` (static user and group).
- **`installation.postInstallScript`** and **`uninstallation.preUninstallScript`** (1.2+): shell scripts in the package root.
- **`configuration`**: `settingPage` (file under `html/`), `paramConfig[]` (`name`, `default`, `type`, all required), `httpConfig[]` (`transferCgi`, `fastCgi`, and from 1.5.0 a web-content object `type: directory` with `access` `admin|operator|viewer`, default `admin`), `reverseProxy[]` (1.5.0+: Unix-socket form with `apiType` `http|ws|fcgi` or TCP form; `access` adds `anonymous`), `containers` (1.7.0+).
- **`copyProtection.method`**: `none`, `axis` or `custom`.
- **`resources`** (1.1+): `dbus.requiredMethods` (absent method means the app is rejected at install) versus `dbus.conditionalMethods` (app installs and must cope), and `linux.user.groups[]` for a dynamic user's secondary groups. A dynamic user and a static `setup.user` are mutually exclusive. See [ACAP application user types and permissions](acap-application-user-permissions.md).

`embeddedSdkVersion` should be `3.0` for new releases; `2.0` applies to schema 1.0 and AXIS OS 10.5 or earlier.[^acap-docs-project-structure]

## package.conf correspondence

`application-project-structure.md` maps manifest keys to `package.conf` variables (for example `appName`↔`APPNAME`, `runMode`↔`STARTMODE`, `architecture`↔`APPTYPE`, `settingPage`↔`SETTINGSPAGEFILE`, `embeddedSdkVersion`↔`REQEMBDEVVERSION`); `OTHERFILES` was replaced by `acap-build -a`. The conversion procedure is in [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md). Schema files live under `/opt/axis/acapsdk/axis-acap-manifest-tools/schema/schemas` in the SDK image.[^acap-docs-project-structure]

## Disagreements and stale items

- Constraints introduced in 1.4.0, 1.6.0, 1.7.1, 1.7.2 and 1.7.3 appear **only** in the index table; the auto-generated pages from 1.3.1 onward still describe `appName` as "Name of the executable file" and show no vendor charset or length limits. Treat the index table as the authority on changes, the field pages as authority on structure. **Observed**.
- The pages for 1.7.1, 1.7.2 and 1.7.3 are field-for-field identical to 1.7.0 apart from the title line.
- `application-project-structure.md` lists a Preupgrade Script (AXIS OS 9.30) as optional yet says pre-upgrade scripts are unsupported with `manifest.json`; the latter matches the migration guide. Its dynamic-user paragraph drops `.setup.` from `acapPackageConf.setup.user.*`. **Observed**.
- Examples in `develop/` use `schemaVersion` 1.3.1, 1.5.0, 1.6.0 and 1.7.0 in different pages, so no single example is current.

## Limits

All claims are **Reported** and compared by static reading; no manifest was validated against the JSON schema files, which are not in the snapshot. The 2.x schema and `compatibleOsVersions` are outside this source.

## Relationships

- **Precedes** [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): 1.7.x is the last schema before the 13.x requirement.
- **Depends on** [ACAP release history](acap-release-history.md) for the release that carried each schema.
- **Constrains** [ACAP application signing](acap-application-signing.md): signing needs schema ≥ 1.3, `vendor` and `architecture`.
- **Used by** [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md) (`reverseProxy`, `httpConfig`) and [VAPIX access from ACAP applications](acap-vapix-service-account-access.md) (`dbus.requiredMethods`).
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [CONTRIBUTING.md](../raw/acap-documentation/CONTRIBUTING.md) rule against editing generated files, and `.github/super-linter.env` regex excluding `schema-field-descriptions-v*`; the snapshot is the archived repository per [README](../raw/acap-documentation/README.md).
[^acap-docs-manifest-schemas]: [manifest-schemas/index.md](../raw/acap-documentation/docs/develop/manifest-schemas/index.md) §Required fields, §Manifest schema version mapping and its table; `schema-field-descriptions-v1.0.md` to `v1.7.3.md` (field lists and diffs between consecutive versions).
[^acap-docs-project-structure]: [application-project-structure.md](../raw/acap-documentation/docs/develop/application-project-structure.md) §Manifest file content (mapping table and footnote 2), §Manifest file schema, §Discontinued support when using manifest file, §User and group.
