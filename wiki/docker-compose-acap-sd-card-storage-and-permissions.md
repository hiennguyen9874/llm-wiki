---
type: Concept
title: "Docker Compose ACAP SD card storage, post-install script and group mapping"
description: "How the Docker Compose ACAP places the Docker data root on an SD card or internal storage, detects the card through axstorage, rejects vfat and exfat, checks permissions, repairs ownership in its post-install script, and maps the sdk and storage groups into containers, with path and logic defects."
tags: [edge-ai, axis, acap, docker, sd-card, storage, permissions, postinstall, c]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-storage
    resource: ../raw/docker-compose-acap/app/sd_disk_storage.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe)"
    title: "sd_disk_storage.c — axstorage subscription for SD_DISK"
  - id: dc-postinstall
    resource: ../raw/docker-compose-acap/app/postinstallscript.sh
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "postinstallscript.sh"
  - id: dc-wrapper
    resource: ../raw/docker-compose-acap/app/dockerdwrapperwithcompose.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "dockerdwrapperwithcompose.c"
  - id: dc-readme
    resource: ../raw/docker-compose-acap/README.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "README"
  - id: dc-manifest
    resource: ../raw/docker-compose-acap/app/manifest.json
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "ACAP manifest of the application"
---

# Docker Compose ACAP SD card storage, post-install script and group mapping

Docker images and containers are large, so the application can put the dockerd **data root** on an SD card instead of internal storage. The choice is the `SDCardSupport` setting (default `no`). The wrapper then waits for the `SD_DISK` storage area, requires a file system with Unix permissions, checks that the rootless application user can write there, and otherwise stops dockerd with a specific [Status code](docker-compose-acap-daemon-runtime.md). The README lists wrong permissions after a firmware or application upgrade as a known issue.[^dc-readme][^dc-wrapper]

## README guidance

- dockerd needs Unix permissions: ext4, ext3 and xfs work; a vfat card may need reformatting.
- Capacity and speed matter: the README cites the Computer Vision SDK `object-detector-python` example as having much longer inference time on a small, slow card.
- Versions before 3.0 ran as root and may have left a root-owned directory (`/var/spool/storage/SD_DISK/dockerd` before 2.0, `/var/spool/storage/areas/SD_DISK/<app>` from 2.0). The rootless application cannot use it; fix by reformatting, deleting the directory, or temporarily allowing root-privileged apps and reinstalling so the post-install script repairs ownership.
- When migrating from a rootful release, copy images off, stop and uninstall, format the card, restart the device and install the rootless version.[^dc-readme]

## Detection and setup in code

| Stage | Behaviour | Locator |
| --- | --- | --- |
| Subscribe | After listing storages with `ax_storage_list`, subscribes to the literal id `SD_DISK` | `sd_disk_storage_init`, `subscribe` |
| Events | `WRITABLE` triggers `ax_storage_setup_async` and returns the path via `ax_storage_get_path`; `EXITING` calls back with NULL and releases | `subscribe_cb`, `setup_cb` |
| Consumer | On removal dockerd is stopped and Status 5 set; otherwise the area is stored and the main loop quits so dockerd restarts | `sd_card_callback` |
| Prepare | `mkdir -p <area>/data` through `system()`; reject `vfat`/`exfat` by parsing `/proc/mounts` (Status 6); require `access` write permission (Status 7) | `setup_sdcard`, `get_filesystem_of_path` |
| Fallback | With SD support off the data root is `<localdata>/data` | `prepare_data_root` |

[^dc-storage][^dc-wrapper]

## Post-install script

`postinstallscript.sh` runs under `/bin/sh -e` and does three things:[^dc-postinstall]

1. **Gate:** exits 77 (`EX_NOPERM`) with a syslog warning if `/usr/bin/containerd` is missing, which blocks installation on devices without container support.
2. **`daemon.json`:** creates `localdata/daemon.json` containing `{}` with `umask 077` if absent, and `chown`s it to the owner of `localdata` only when running as root.
3. **Ownership repair:** when run as root and the SD area exists, recursively `chown`s it to the owner of `localdata`.

The framework does not set ownership on the SD card, which the script comments give as the reason for the repair.[^dc-postinstall]

## Container group mapping

The manifest gives the application user the secondary groups `sdk` and `storage`.[^dc-manifest] Inside a rootless container the user is mapped so that container `root` equals the application user, and only uid and gid are mapped. To reach device resources owned by those groups, a container needs `group_add` (Compose) or `--group-add` with the **mapped** numeric ids: `sdk` is 1 and `storage` is 2; group names cannot be used and are displayed incorrectly inside the container. The numeric mapping is README prose; nothing in the code defines it.[^dc-readme]

## Defects and mismatches (Observed)

1. **Path mismatch:** the script repairs `/var/spool/storage/SD_DISK/areas/<app>`, while the README names `/var/spool/storage/areas/SD_DISK/<app>`. The API path used by the wrapper comes from `ax_storage_get_path`; the README's order is the one consistent with the 2.0 layout. By synthesis, the repair step may never match, but this was not tested.[^dc-postinstall][^dc-readme]
2. **Repair needs root:** a normal non-root install cannot repair ownership, which is why the README's workaround enables root-privileged apps temporarily.[^dc-postinstall][^dc-readme]
3. **Missing return:** in `subscribe_cb` an `if (error)` branch lacks a `return`, so execution may continue with a NULL storage id; the storage list is partly leaked when subscription fails.[^dc-storage]
4. **Leak and nesting:** `sd_card_callback` leaks the previous area string and may call `stop_dockerd` (a nested main loop) from a callback.[^dc-wrapper]
5. **Shell construction:** the unquoted `system()` call makes an SD area path with spaces or metacharacters unsafe; only a non-zero return is checked.[^dc-wrapper]

## Evidence class

Procedures and guidance are **Reported** by the README; detection logic, script behaviour and defects are **Observed** by static reading. The path-mismatch consequence is **Synthesis**. Nothing was run on a camera with an SD card.

## Relationships

- **Part of** [Docker Compose ACAP repository](docker-compose-acap-repository.md).
- **Feeds** Status codes 5 to 7 in [Daemon runtime](docker-compose-acap-daemon-runtime.md).
- **Uses** the storage service shown in [ACAP examples: storage, serial, recording and license key](acap-example-storage-serial-recording-licensekey.md) (`axstorage` subscriptions).
- **Relates to** user and group semantics in [ACAP application user types and permissions](acap-application-user-permissions.md).

[^dc-storage]: `app/sd_disk_storage.c::{sd_disk_storage_init, subscribe, subscribe_cb, setup_cb}`.
[^dc-postinstall]: `app/postinstallscript.sh` (whole file: containerd check, `UID_DOT_GID`, `daemon.json`, `SD_CARD_AREA` repair).
[^dc-wrapper]: `app/dockerdwrapperwithcompose.c::{setup_sdcard, get_filesystem_of_path, prepare_data_root, sd_card_callback}`.
[^dc-readme]: `README.md` §Using an SD card as storage (incl. CAUTION), §Installation NOTE (migrating), §Using host user secondary groups in container, §Overview Known Issues.
[^dc-manifest]: `app/manifest.json::resources.linux.user.groups`.
