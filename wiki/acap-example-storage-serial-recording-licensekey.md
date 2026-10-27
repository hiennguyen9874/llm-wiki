---
type: Concept
title: "ACAP examples: storage, RS485 serial port, recording playback and license key"
description: "How axstorage, axserialport, recording-playback and licensekey use device services: storage event subscription and writes, RS485 loopback settings, D-Bus recording span and segment queries, and periodic license verification, with manifests, constants and defects."
tags: [edge-ai, axis, acap, examples, axstorage, axserialport, recording, licensekey, dbus]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP examples: storage, serial port, recording playback and license key

Four examples cover device services that an application usually reaches through an SDK library or D-Bus rather than through video or ML APIs.[^native-examples] All have `runMode: "never"` and log through syslog.

## axstorage

- **Purpose:** the storage lifecycle with `ax_storage_list`, `ax_storage_subscribe`, `ax_storage_get_status` (events writable, available, exiting, full), `ax_storage_setup_async`, `ax_storage_release_async`, `ax_storage_get_path`, `ax_storage_unsubscribe`. Manifest group `storage`.
- **Flow:** list disks, subscribe to each, and on a status change set the disk up when writable, not full, not exiting and not yet set up; the callback stores the `AXStorage*` and path (e.g. `/var/spool/storage/areas/SD_DISK/axstorage`). Two 10-second timers append `counter: N` to `file1.log` and `file2.log`. On exit the disks are released and unsubscribed.
- **Defects:** README status lines print `writable NO/YES` while the code prints empty or `not ` prefixes; `setup_disk_cb` does not NULL-check the lookup and the subscribe callback may run before the item is appended to the disk list.[^native-examples]

## axserialport

- **Purpose:** the serial-port API with GLib I/O channels. `ax_serial_init` then settings: enable, 19200 baud, 8 data bits, no parity, 1 stop bit, RS485 4-wire mode (`AX_SERIAL_RS485_4`), bias and termination disabled, `ax_serial_sync_port_settings`, `ax_serial_get_fd`. Manifest group `admin`.
- **Flow:** the fd is wrapped by `g_io_channel_unix_new` with raw encoding; an input watch reads two bytes and logs `timestamp: MM:SS`, and a 10-second timer writes elapsed minutes and seconds. It needs a physical RS485 four-wire loopback (diagram `assets/loopback-diagram.png`, not interpreted here).
- **Defects:** settings are hard-coded and all `ax_serial_set_*` return values are ignored; the minutes byte is a `gchar` and wraps.[^native-examples]

## recording-playback

- **Purpose:** find recordings and be told about new ones over D-Bus using `libsystemd` (`sd_bus_call_method`, `sd_event_default`). Manifest `dbus.requiredMethods`: `Search1.ListSpans`, `Search1.GetSpanAttributes`, `Playback1.GetSegment`.
- **Flow:** `ListSpans` (reply `a(ssss)`, max 1000) → per span `GetSpanAttributes` (containers and tracks with `string`/`int32` attributes) → per container `GetSegment` repeatedly, using the previous stop time as search time until it is empty (tolerating `SegmentNotFound`) → match `SegmentCompleted` signals and run the event loop.
- **Limits:** storage id fixed to `SD_DISK`; requires an SD card with recordings; `panic()` exits without cleanup. The example is MIT-licensed while the README `../LICENSE` link points at the Apache root file.[^native-examples]

## licensekey

- **Purpose:** verify a signed license for a device and application with `licensekey_verify(app_name, APP_ID, MAJOR, MINOR)`; the Makefile statically links `licensekey_stat` and dynamically `licensekey`.
- **Flow:** `main` refuses any argument, checks immediately and then every `CHECK_SECS=300` in a GLib main loop; logs `Licensekey is invalid` until a valid key is installed.
- **Manifest:** `appId "0"`, `vendor "-"`, `copyProtection.method "axis"` (required to install a key from the device GUI). `APP_ID` and version are compile-time defines that must match the manifest; keys come from the ACAP Service Portal.[^native-examples]

The signing aspect of the Service Portal is in [ACAP application signing](acap-application-signing.md); that is separate from license keys.

Evidence class: **Observed** (static); none run, and the README log samples were not reproduced.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); permissions in [shared conventions](acap-examples-build-and-manifest-conventions.md).
- **Uses** APIs listed in [Native SDK API catalog](acap-native-sdk-api-catalog.md); D-Bus grants in [ACAP application user types and permissions](acap-application-user-permissions.md).

[^native-examples]: `axstorage/app/axstorage.c::subscribe_cb, setup_disk_cb, write_data`, `axstorage/README.md`; `axserialport/app/axserialport.c::main, incoming_data, send_timer_data`, `axserialport/README.md`; `recording-playback/app/recording_playback.c::get_all_span_ids, parse_get_span_attributes_reply, get_all_segments`, `recording-playback/app/manifest.json`; `licensekey/app/{licensekey_handler.c,Makefile,manifest.json}`, `licensekey/README.md`.
