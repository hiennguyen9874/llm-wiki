---
type: Concept
title: "ACAP Runtime server: command-line flags, chip ids, sockets, TLS and legacy parameter override"
description: "How the acapruntime binary starts and is configured: the flag table and real defaults, the chip-id table, Unix versus network socket, what TLS does and does not provide, the legacy -o device-parameter override, shutdown behaviour and the defects in startup code."
tags: [edge-ai, axis, acap, acap-runtime, grpc, tls, configuration, larod]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T21:00:00Z }
stale_after: 2027-08-31
sources:
  - id: rt-readme
    resource: ../raw/acap-runtime/README.md
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9 (e375fc9586e270042c9c46dde7645c20761b06bf)"
    title: "ACAP Runtime README (§Configuration, §Chip id, §TLS, §gRPC socket)"
  - id: rt-server
    resource: ../raw/acap-runtime/src/acap_runtime.cpp
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "acap_runtime.cpp — AcapRuntime() and RunServer()"
  - id: rt-util
    resource: ../raw/acap-runtime/src/util.cpp
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "util.cpp — get_parameter_value() (parhandclient wrapper)"
  - id: rt-manifests
    resource: ../raw/acap-runtime/manifest-aarch64.json
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "ACAP manifests (aarch64, armv7hf, test)"
  - id: rt-tests
    resource: ../raw/acap-runtime/test/inference_test.cc
    scope: ../raw/acap-runtime/
    kind: code
    revision: "2.0.1-10-ge375fc9"
    title: "inference_test.cc — chip ids used by the repository's own tests"
---

# ACAP Runtime server: command-line flags, chip ids, sockets, TLS and legacy parameter override

The server is started as `acapruntime [flags]`. The README presents TLS and a chip id as defaults, but in the code the **real defaults are an insecure channel, a Unix socket and chip id 0**, which switches the Machine learning API off; the "defaults" the README quotes (chip 4 on armv7hf, 12 on aarch64, TLS on) exist only in the legacy native-ACAP manifests and are applied through the legacy `-o` flag. Anyone running the published container must therefore pass `-j`, `-m` and the certificate flags explicitly, as every example in the [CV SDK examples](acap-cv-examples-runtime-architecture.md) does.[^rt-readme][^rt-server][^rt-manifests]

## Flags and effective defaults

The README lists the flags; the code agrees, with the defaults set at the top of `AcapRuntime()`.[^rt-readme][^rt-server]

| Flag | Meaning | Effective default | Note |
| --- | --- | --- | --- |
| `-v` | verbose logging | off | |
| `-a <IP>` | gRPC bind address | `0.0.0.0` | used only with a non-zero port |
| `-p <port>` | gRPC port | `0` = Unix socket | `atoi`, no range check |
| `-t <seconds>` | run time, for tests | `0` = until signalled | |
| `-c <file>` / `-k <file>` | TLS certificate / private key | empty | TLS only if **both** are given |
| `-j <chip id>` | chip for the ML API | `0` = ML disabled | `atoi`, not validated |
| `-m <file>` | model to preload | none | repeatable (pushed into a list) |
| `-o` | override settings from device parameters | off | legacy; README says not to use it |
| `-h` | usage | — | accepted but not in the usage text (**Observed**) |

An unknown option prints usage and exits with failure. Startup order is: `openlog`, signal setup, option parsing, optional `-o` override, then `RunServer` inside a try/catch that logs any `std::exception` to syslog and returns failure.[^rt-server]

## Chip id

The ML API needs the larod chip for the device. The README says the pre-built native application defaulted to 4 (`armv7hf`) and 12 (`aarch64`), that 0 (`LAROD_CHIP_INVALID`) means the inference service is not started, and gives this table:[^rt-readme]

| Id | larod name | Description |
| --- | --- | --- |
| 0 | `LAROD_CHIP_INVALID` | invalid chip |
| 1 | `LAROD_CHIP_DEBUG` | dummy chip for debugging |
| 4 | `LAROD_CHIP_TPU` | Google TPU |
| 6 | `LAROD_CHIP_CVFLOW_NN` | Ambarella CVFlow (NN) |
| 8 | `LAROD_CHIP_TFLITE_GLGPU` | GPU with TensorFlow Lite — experimental, "subject to change" |
| 9 | `LAROD_CHIP_CVFLOW_PROC` | Ambarella CVFlow (proc) |
| 10 | `LAROD_CHIP_ACE` | Axis Compute Engine |
| 11 | `LAROD_CHIP_LIBYUV` | CPU with libyuv |
| 12 | `LAROD_CHIP_TFLITE_ARTPEC8DLPU` | ARTPEC-8 DLPU with TensorFlow Lite |
| 13 | `LAROD_CHIP_OPENCL` | image processing with OpenCL |

The README notes there is no direct correlation between chip id and architecture. **Id 2 is not in the table** although the examples use it for CPU inference; the repository's own tests use `cpuChipId = "2"`, `tpuChipId = "4"` and `dlpuChipId = "12"`, so the repository itself treats 2 as the CPU chip (**Observed**, `test/inference_test.cc` L42-44, `test/inference_unittest.cc` L38-40). The larod enum name for 2 is not stated anywhere in the repo.[^rt-tests] This resolves, in the repo's favour, the question the [Runtime architecture page](acap-cv-examples-runtime-architecture.md) left open. Chip ids are larod enums, not SoC names; for SoC-level choices see [ACAP generations, chip architectures and SDK compatibility](acap-chip-architecture-and-sdk-compatibility.md), and chip 12 targets the [DLPU](axis-dlpu.md).

## Sockets

If the port is 0 the server listens on `unix:///tmp/acap-runtime.sock` (hard-coded; there is no socket-path flag) and ignores `-a`; otherwise it listens on `address:port`. After start the socket file is `chown`ed to the process's uid/gid and `chmod`ed `0660`. The README documents the same default and the `-a`/`-p` alternative for network sockets.[^rt-readme][^rt-server] The socket is only reachable by a container that shares the directory (the examples share a named volume at `/tmp`). The unlink of the socket file at shutdown is not explicit in the code (**Unverified** whether gRPC removes it).

## TLS

TLS is used only when both `-c` and `-k` are non-empty; otherwise the server starts **insecure**. With both set it builds server credentials from the PEM files (empty root certs) and never requests a client certificate, so it provides **encryption and server identity only, not client authentication** — the README's "TLS authenticated mode" is loosely worded (**Observed**).[^rt-server] The README warns that running without TLS is "extremely insecure", and gives a self-signed recipe: `openssl req -x509 -batch -subj '/CN=localhost' -days <n> -newkey rsa:4096 -nodes -out server.pem -keyout server.key`, with the files mounted at `/opt/app/certificates` and `-c`/`-k` pointing to them.[^rt-readme] Clients that verify the certificate need the CN `localhost` or a target-name override (the [Parameter API example](acap-cv-example-parameter-api.md) sets `grpc.default_authority = localhost`). `README` text about the docker-run example puts the whole entrypoint in one quoted string, which does not work as written with `docker run --entrypoint` (**Synthesis**, shell quoting).

## Legacy `-o` parameter override

With `-o` the binary reads four device parameters of its own ACAP application — `Verbose`, `IpPort`, `ChipId`, `UseTLS` — by shelling out to `parhandclient get root.<app>.<param>` and overrides the parsed flags; `UseTLS=yes` injects the fixed paths `/usr/local/packages/acapruntime/server.pem` and `server.key`. The native manifests set `runOptions: "-o"` and ship `ChipId` `12` (aarch64) or `4` (armv7hf), `IpPort` `0`, `Verbose` `no`, `UseTLS` `yes`; that is the origin of the README's defaults.[^rt-server][^rt-util][^rt-manifests] Since 2.0.0 the container is the only distribution, so `-o` and these manifests matter only to the test-suite package ([Test suite](acap-runtime-test-suite.md)).

### Defects in this path (Observed, static)

1. `get_parameter_value()` returns `value.c_str()` of a **local `std::string`**, so the caller reads freed memory (`util.cpp` L40, after the string is destroyed at return).[^rt-util]
2. It never returns `NULL`; failures return `""`. Every `if (x != NULL)` in `AcapRuntime()` is therefore always true, and a failed read silently sets verbose off, port 0 and **chip 0 (ML disabled)**.[^rt-server][^rt-util]
3. The default app-name argument is `"Acapruntime"` (capital A) while the manifest `appName` is `acapruntime`; a case mismatch would break the lookup if the parameter store is case-sensitive (**Unverified**).
4. `-o` is applied after `getopt`, so it overrides flags rather than yielding to them.

## Shutdown and logging defects

- With `-t > 0` the main thread just sleeps; the GLib main loop is not running, so `SIGINT`/`SIGTERM` handlers (registered with `g_unix_signal_add`) cannot stop it early. With `-t 0` a signal arriving before the loop is created calls `g_main_loop_quit(NULL)`.[^rt-server]
- The `LOG` macro compares `#level == "ERROR"` by pointer, so ERROR lines may not print when not verbose; real failures reach syslog only.
- `read_text()` ignores the `fread` result and returns the buffer with a trailing NUL, so a short read gives a truncated PEM with no check.
- No validation of port or chip id; negative or non-numeric values pass through `atoi`.

## Relationships

- **Configures:** [Machine learning API](acap-runtime-machine-learning-api.md) (needs `-j`, `-m`), [Video capture API](acap-runtime-video-capture-api.md), [Parameter API](acap-runtime-parameter-api.md); all share one server and one socket.
- **Part of:** [ACAP Runtime repository](acap-runtime-repository.md).
- **Run with:** the compose pattern in [Containerized ACAP Runtime architecture](acap-cv-examples-runtime-architecture.md); the image has no default flags ([Build and image packaging](acap-runtime-build-and-image-packaging.md)).
- **Contradicts (README vs code):** TLS-by-default and chip defaults — see above.

## Evidence class

All items are **Observed** by static reading of `acap_runtime.cpp`, `util.cpp` and the manifests, compared with the README. The dangling-pointer defect and the `-t` signal behaviour are inferred from code structure; nothing was executed (**Unverified** at runtime).

[^rt-readme]: `README.md` §Usage (compose example), §Configuration (flag list and notes 1-3), §Chip id (table), §TLS, §gRPC socket.
[^rt-server]: `src/acap_runtime.cpp::{AcapRuntime (L166-250), RunServer (L72-146), Usage (L149-160), LOG (L34-36), init_signals (L65-68)}` at `2.0.1-10-ge375fc9`.
[^rt-util]: `src/util.cpp::get_parameter_value (L20-48)`, `src/util.h` L25 (default `app_name`).
[^rt-manifests]: `manifest-aarch64.json`, `manifest-armv7hf.json` (`runOptions "-o"`, `paramConfig ChipId/Verbose/IpPort/UseTLS`; `ChipId` 12 versus 4); `manifest-test.json` has only `Verbose` and no `runOptions`.
[^rt-tests]: `test/inference_test.cc` L42-44 (`cpuChipId`, `tpuChipId`, `dlpuChipId`) and `test/inference_unittest.cc` L38-40.
