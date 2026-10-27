---
type: Concept
title: "Docker Compose ACAP daemon runtime: rootlesskit launch, settings, status codes and defects"
description: "How dockerdwrapperwithcompose.c starts and supervises rootlesskit and dockerd on an Axis device: main loop, parameter-driven restarts, command-line and environment construction, ports, settings defaults, the eight Status codes, logging, and the code defects found."
tags: [edge-ai, axis, acap, docker, rootless, rootlesskit, dockerd, axparameter, c]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T22:00:00Z }
stale_after: 2027-04-30
sources:
  - id: dc-wrapper
    resource: ../raw/docker-compose-acap/app/dockerdwrapperwithcompose.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce (985c8cede8b73d3a02a74c36e8a71d17b04852fe)"
    title: "dockerdwrapperwithcompose.c — the wrapper's main program"
  - id: dc-manifest
    resource: ../raw/docker-compose-acap/app/manifest.json
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "ACAP manifest of the application"
  - id: dc-readme
    resource: ../raw/docker-compose-acap/README.md
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "README"
  - id: dc-log
    resource: ../raw/docker-compose-acap/app/log.c
    scope: ../raw/docker-compose-acap/
    kind: code
    revision: "4.0.0-2-g985c8ce"
    title: "log.c — logging to syslog or stdout"
---

# Docker Compose ACAP daemon runtime: rootlesskit launch, settings, status codes and defects

The application's single binary, `dockerdwrapperwithcompose`, is a **supervisor**: it reads seven ACAP parameters, builds a long **rootlesskit** command line that wraps `dockerd`, spawns it, watches the child, and restarts it whenever a setting changes, a certificate is uploaded, or the SD card appears or disappears. It does not run `dockerd` directly; the spawned child is rootlesskit with `slirp4netns` networking.[^dc-wrapper] Overview and requirements are in [Docker Compose ACAP repository](docker-compose-acap-repository.md).

## Control flow

| Step | Behaviour | Locator |
| --- | --- | --- |
| Start | Creates a GLib main loop; `--stdout` is the only command-line switch (default log goes to syslog); allows dockerd to start; registers parameter callbacks (exit `EX_SOFTWARE` on failure); sets environment; installs `SIGINT`/`SIGTERM`; starts the FastCGI thread and SD storage subscription | `main`, `parse_command_line`, `setup_axparameter` |
| Loop | While no child is running and starting is allowed, `read_settings_and_start_dockerd`, then run the main loop; after it returns, refresh the debug level and stop dockerd | `main` |
| Setting change | A callback on every parameter except `Status` sets the allow flag and schedules a one-second timeout that quits the main loop, avoiding the documented AXParameter deadlock if the callback blocked | `setup_axparameter` callback |
| Child exit | A GLib child watch records Status (1 for a clean exit, 2 for a non-zero one), clears the pid, removes `/var/run/user/<uid>/docker.pid`, re-chmods the XDG runtime dir to 0700 and quits the loop so `main` restarts it | `check_child_process_exit_code_and_clean_up` |
| Stop | `stop_dockerd` terminates the child; the final exit path sets Status `-1 NOT STARTED` | `stop_dockerd`, end of `main` |

Restart triggers from other components (certificate upload, SD card events) call into the same loop; see [Certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md) and [SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md).[^dc-wrapper]

## Command line that is built

`build_daemon_args` writes one space-separated string into a static 1024-byte buffer, which `g_strsplit` then splits on spaces before `g_spawn_async` runs it with `G_SPAWN_DO_NOT_REAP_CHILD` and `G_SPAWN_SEARCH_PATH`.[^dc-wrapper]

- **rootlesskit options:** `--subid-source=static`, `--net=slirp4netns`, `--disable-host-loopback`, `--copy-up=/etc`, `--copy-up=/run`, `--propagation=rslave`, `--port-driver slirp4netns`, `--cidr=10.0.3.0/24`, plus `--debug` when `DockerdLogLevel` is `debug`.
- **Port publishing:** `-p <host-ip>:<port>:<port>/tcp` with port 2376 when TLS is used and 2375 otherwise; the host IP comes from `gethostname` and `gethostbyname`.
- **dockerd options:** `--config-file /usr/local/packages/<app>/localdata/daemon.json`, `--log-level=<DockerdLogLevel>`, `--data-root` (SD area `/data` or the localdata `/data`), for IPC `--group 0 -H unix:///var/run/user/<uid>/docker.sock`, for TCP `-H tcp://0.0.0.0:2375|2376` with `--tlsverify=true` or `--tls=false`, and the `--tlscacert/--tlscert/--tlskey` flags when TLS is on.
- **Environment:** the child inherits the wrapper's environment plus `DOCKER_INSECURE_NO_IPTABLES_RAW=1`; the wrapper sets `PATH`, `HOME` (the app directory), `XDG_RUNTIME_DIR=/var/run/user/<uid>` and `XTABLES_LOCKFILE=/tmp/<app>_xtables.lock`.[^dc-wrapper]

The `DOCKER_INSECURE_NO_IPTABLES_RAW=1` setting is the code behind the README's second known issue (omitted raw-table hardening) described in the [repository overview](docker-compose-acap-repository.md).[^dc-readme]

## Settings and defaults

| Parameter | Type | Default | Effect |
| --- | --- | --- | --- |
| `SDCardSupport` | bool | `no` | data root on the SD card |
| `UseTLS` | bool | `yes` | TLS on the TCP socket; ignored when TCP is off |
| `TCPSocket` | bool | `yes` | remote daemon on 2375/2376 |
| `IPCSocket` | bool | `yes` | local Unix socket for on-device CLI and containers |
| `ApplicationLogLevel` | enum | `info` | `debug` or `info` for the wrapper |
| `DockerdLogLevel` | enum | `warn` | `debug`, `info`, `warn`, `error`, `fatal` |
| `Status` | hidden string | `-1 No Status` | state, written by the wrapper |

`read_settings` rejects both sockets off (Status 4), checks certificates only when TCP is on (Status 3), prepares the data root, and applies mode 0750 to the app directory only when both Compose and the IPC socket are in use.[^dc-manifest][^dc-wrapper]

## Status codes

The wrapper's enum and strings match the README table exactly.[^dc-wrapper][^dc-readme]

| Code | Name | Where set |
| --- | --- | --- |
| -1 | NOT STARTED | spawn failure and program exit |
| 0 | RUNNING | immediately after the spawn, not when dockerd is ready |
| 1 | DOCKERD STOPPED | child exited with code 0; restart follows |
| 2 | DOCKERD RUNTIME ERROR | child exited with a non-zero code; needs a parameter change or restart |
| 3 | TLS CERT MISSING | TCP on, TLS on, a PEM absent |
| 4 | NO SOCKET | neither socket selected |
| 5 | NO SD CARD | SD support on but no card, or card removed |
| 6 | SD CARD WRONG FS | `vfat` or `exfat` |
| 7 | SD CARD WRONG PERMISSION | area missing or not writable by the app user |

Two mismatches: the manifest default string `-1 No Status` differs from the code's `-1 NOT STARTED`, and the README lists `Status` as read-only while the wrapper itself writes it with `ax_parameter_set`.[^dc-manifest][^dc-wrapper]

## Logging

`log.c` installs one GLib log handler, either syslog or stdout, chosen at start. It filters debug messages by an atomic flag, maps the application `debug` level to `LOG_INFO` so debug lines are visible in syslog, and uses the non-fatal error level because `G_LOG_LEVEL_ERROR` aborts.[^dc-log]

## Proxy and `daemon.json`

The C code never parses `daemon.json`; the post-install script creates it as `{}` and proxy settings are a manual edit. A malformed file only makes dockerd exit, shown as Status 2.[^dc-wrapper][^dc-readme]

## Defects and fragilities (Observed)

1. **Space-split argv:** a path with a space (SD area, package directory) produces a wrong argument vector; the static 1024-byte buffer has no truncation repair, and a write past it makes `args_end - args_wr` an enormous unsigned size.
2. **Unchecked hostname lookup:** `gethostbyname` and `h_addr_list[0]` are dereferenced without a check, so a host with no resolvable name crashes the wrapper.
3. **Unchecked NULLs:** `get_parameter_value` may return NULL for the log level, which then goes into `strcmp` and `%s`; several `GError` messages are read without confirming the error was set.
4. **Race in `is_process_alive`:** it calls `waitpid` on a pid GLib's child watch also reaps, and compares the global pid, not its argument.
5. **Leak:** `sd_card_callback` duplicates the area string and never frees the previous one.
6. **Shell and nested loops:** `setup_sdcard` runs an unquoted `system("mkdir -p …")`; `read_settings` blocks in a nested loop (up to five seconds) while waiting for the SD callback, and `g_source_remove` can then target a timeout that already fired.
7. **Early RUNNING:** Status 0 is set when the process is spawned, so a startup failure briefly shows 0 before 2.
8. **Thread hand-off:** restarts requested from the FastCGI thread mutate state used by the main thread without locking, and a request while the main loop is not running can be lost.
9. **Signals:** after the first `SIGINT`/`SIGTERM` the handler is removed, so a second signal kills the wrapper without stopping dockerd.
10. **Comment drift and hard-coded values:** a comment says SIGTERM on the 20th call while the code uses 13; `/proc/mounts`, `/var/run/user/%d`, ports 2375/2376 and the `10.0.3.0/24` CIDR are hard-coded; the XDG runtime directory is chmodded but never created by the wrapper.[^dc-wrapper]

Evidence for the defects is static reading only.

## Evidence class

Flow, flags, defaults and status mapping are **Observed** from the code; the README Status table is **Reported** and agrees with it. Defects are **Observed** by inspection and **Unverified** by execution. Nothing was run on a device.

## Relationships

- **Part of** [Docker Compose ACAP repository](docker-compose-acap-repository.md).
- **Triggered by** [Certificates and TLS](docker-compose-acap-certificate-upload-and-tls.md) (restart after upload) and [SD card storage and permissions](docker-compose-acap-sd-card-storage-and-permissions.md) (card events).
- **Runs as** a dynamic or static ACAP user described in [ACAP application user types and permissions](acap-application-user-permissions.md); the manifest adds `sdk` and `storage` groups.
- **Uses** the AXParameter API patterns catalogued in [ACAP examples: events and parameters](acap-example-events-and-parameters.md) and the FastCGI model of [Exposing an HTTP API from an ACAP application](acap-web-server-reverse-proxy-fastcgi.md).
- **Packaged by** [Build and packaging](docker-compose-acap-build-and-packaging.md).

[^dc-wrapper]: `app/dockerdwrapperwithcompose.c::{main, parse_command_line, setup_axparameter, read_settings, read_settings_and_start_dockerd, build_daemon_args, check_child_process_exit_code_and_clean_up, stop_dockerd, is_process_alive, setup_sdcard, sd_card_callback, set_env_variables}`, the status enum and string table, and `app/app_paths.h`.
[^dc-manifest]: `app/manifest.json::acapPackageConf.configuration.paramConfig`, `resources.linux.user.groups`.
[^dc-readme]: `README.md` §Settings, §Status codes, §Proxy Setup, §Overview NOTE and Known Issues.
[^dc-log]: `app/log.c::{log_init, log_threshold_met, log_to_stdout}`; `app/log.h`.
