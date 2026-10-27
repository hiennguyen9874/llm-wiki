---
type: Concept
title: "Remote debugging ACAP applications with GDB and VS Code"
description: "Debug an ACAP application on the device from VS Code: the vendor page, plus what the remote-debug-example actually does (gdbserver 9.2 cross-build, dev container, launch.json, scp and ssh steps, Developer Mode need) and its limits."
tags: [edge-ai, axis, acap, debugging, gdb, vscode]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-remote-debug
    resource: ../raw/acap/how-to-guides/debugging/index.md
    scope: ../raw/acap/how-to-guides/debugging/
    kind: docs
    revision: "ACAP version 12"
    title: "Debugging | Axis developer documentation"
  - id: remote-debug-example
    resource: ../raw/acap-native-sdk-examples/remote-debug-example/README.md
    scope: ../raw/acap-native-sdk-examples/remote-debug-example/
    kind: code
    revision: "acap-native-sdk-examples 12.11.0-7-g3025a4e"
    title: "remote-debug-example (acap-native-sdk-examples)"
---

# Remote debugging ACAP applications with GDB and VS Code

An ACAP application can be debugged while it runs on the device, not only inferred from its log output. Axis documents one path: **GNU Debugger (GDB)** on the device plus **Visual Studio Code** as the front end, packaged as the `remote-debug-example` in the `acap-native-sdk-examples` repository. The debugging page is only a pointer to that example — it states the shape of the workflow but leaves the actual commands to the example's README, which is now local and compiled in the next section.[^acap-remote-debug]

## What the documented setup provides

According to the page, the GDB server plus VS Code combination lets a developer:[^acap-remote-debug]

- set **breakpoints** in the application source;
- **inspect variables** while the application runs on the device;
- debug through VS Code's graphical interface instead of a terminal GDB session.

This is interactive, execution-level inspection: the application is stopped at a chosen point and its state is read, rather than reconstructed from emitted messages.

## Documented workflow

The page names these steps and defers the details to the example:[^acap-remote-debug]

| Step | What the page says |
| --- | --- |
| 1 | Use the `remote-debug-example` from `acap-native-sdk-examples`; it lists the prerequisites. |
| 2 | Build and start the dev container. |
| 3 | Upload the GDB server to the device. |
| 4 | Debug the application through VS Code's user interface. |

The example sits alongside the other SDK examples; see [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md) for how that collection is organized.

## What the example actually does

Observed from the example's files (revision `12.11.0-7-g3025a4e`):[^remote-debug-example]

- **Image:** the Dockerfile starts from the SDK image, installs `gdb-multiarch` and `ssh`, and cross-compiles **gdbserver 9.2** (`ARG GDB_VERSION=9.2`, prefix `/opt/build/gdb`, `--host=$($CC -dumpmachine)`, `--with-sysroot=${SDKTARGETSYSROOT}`) so the server matches the device architecture. A final stage also runs `acap-build ./` as a build test.
- **Dev container:** `docker build . --platform=linux/amd64 --build-arg ARCH=<armv7hf|aarch64> -t dev_container:<arch>`; `app/.devcontainer/<arch>-container/devcontainer.json` binds the workspace to `/opt/app` and recommends the `ms-vscode.cpptools` and `webfreak.debug` extensions. The image tag must match the device architecture.
- **Application:** `remote_debug.c` deliberately writes to a string literal (`message[0] = 'h'`) to cause a segmentation fault to debug. The Makefile builds with `-g3 -O0`, keeps the symbol-rich binary in `app/debug/remote_debug`, and strips the copy that is installed. `app/.vscode/launch.json` points `program` at `/opt/app/debug/remote_debug`, `miDebuggerPath` at `/usr/bin/gdb-multiarch` and `miDebuggerServerAddress` at `192.168.0.90:1234`.
- **Procedure (README):** build with `acap-build .` inside the dev container; install with `eap-install.sh <IP> <ADMIN> <PASSWORD> install`; copy gdbserver with `scp /opt/build/gdb/bin/gdbserver acap-remote_debug@<IP>:/tmp/`; over `ssh` start `/tmp/gdbserver :1234 /usr/local/packages/remote_debug/remote_debug`; start the session with F5 in VS Code; stop with Shift+F5 and clean with `make clean`.
- **Prerequisite:** **Developer Mode**, which creates the SSH user `acap-remote_debug` with a settable password (see [SSH and Developer Mode](axis-device-ssh-developer-mode.md)). The manifest `runOptions` are not forwarded to gdbserver.
- **Limits:** the device IP and port are hard-coded in `launch.json`; the process dies at the fault and ends the gdbserver session. Nothing was built or run here.

These details answer most of the open questions below: the GDB server is built by the example's Dockerfile (not taken from the SDK image), listens on port 1234 and VS Code attaches through `miDebuggerServerAddress`.[^remote-debug-example]

## Limits of the vendor page

The vendor page is a 94-word overview with no sub-sections, so the following are **not established** by it (items marked above are now answered by the example):[^acap-remote-debug]

- which prerequisites the example requires (debug build flags such as `-g`, a compiler or GDB version, network reachability, credentials, or device-side permissions);
- how the GDB server is obtained, which port it listens on, and how VS Code attaches to it (launch configuration, `gdbserver`/`gdb` invocation);
- whether the GDB server comes from the SDK image or is built or supplied by the example;
- any supported AXIS OS or ACAP version, and whether debugging works on all camera models;
- whether the application runs under the normal ACAP runtime or needs a special debug launch when attached.

Still unestablished after reading the example: supported AXIS OS and ACAP versions and device models for debugging, and behaviour on real hardware. Status moved from `draft` to `stable` because the intended synthesis is now complete and auditable, not because it was verified.

## Logs versus a debugger

The two facilities answer different questions and do not replace each other: [Application logging trong ACAP](acap-application-logging.md) records messages the application chose to emit and is the only documented route for `LOG_DEBUG`, but it says nothing about variable state the code did not print. **Synthesis:** a debugger is the better tool for a wrong value at a known code location, while logs are better for behavior that only appears over time or after deployment. The logging page requires SSH for `journalctl`; the debugging page does not state its own device-access requirement, so that cannot be assumed to be the same.

## Độ phủ nguồn

- Entry point: `raw/acap/how-to-guides/debugging/index.md` (94 words), site `developer.axis.com`, bộ tài liệu ACAP 12. The folder contains only this file — no images, attachments, or sub-pages — and the whole page was read.
- No code, command, or configuration block exists in the source; the body above therefore quotes no commands.
- `raw/acap-native-sdk-examples/remote-debug-example/` (README, `Dockerfile`, `app/Makefile`, `app/remote_debug.c`, `app/manifest.json`, `app/.vscode/launch.json`, two `devcontainer.json`) was read statically; the gdb source tarball, the SDK image and VS Code extensions are not local.
- The page carries no publication or update date; `revision: "ACAP version 12"` is inferred from the documentation bundle, as with the other ACAP pages in this wiki.

## Độ tin cậy

Claims in the first sections about the method and the four workflow steps are **Reported** by Axis's official documentation, read on 2026-10-27. The section "What the example actually does" is **Observed** from the example's files. No claim is **Reproduced** (no dev container was built, no GDB server uploaded, no remote debugging session run). The statement that breakpoints and variable inspection become available is the vendor's description of what the example achieves, not a measured result here.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): the example, toolchain, and container images come from the SDK ecosystem.
- **Uses** [Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers](acap-dev-environment-setup.md): step 2 starts the dev container, and VS Code supplies the debugger UI.
- **Uses** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): `remote-debug-example` is one entry in that collection.
- **Complements** [Application logging trong ACAP](acap-application-logging.md): logs observe emitted messages, a debugger stops execution and inspects live state.
- **Constrained by** [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md) in principle, although the debugging page names no version requirement.
- **Documented by** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md), where `remote-debug-example` is catalogued; its Dockerfile pattern follows [shared build conventions](acap-examples-build-and-manifest-conventions.md).

[^remote-debug-example]: Example package: `raw/acap-native-sdk-examples/remote-debug-example/README.md` (§ prerequisites and debug steps), `Dockerfile` (gdbserver stage), `app/remote_debug.c`, `app/Makefile`, `app/.vscode/launch.json`, `app/.devcontainer/*/devcontainer.json`, `app/manifest.json`, revision `12.11.0-7-g3025a4e`.

[^acap-remote-debug]: Tài liệu chính thức: [Debugging — Axis developer documentation](../raw/acap/how-to-guides/debugging/index.md), toàn bộ trang (94 từ, không chia mục); các liên kết tới `acap-native-sdk-examples` và `remote-debug-example` là external link chưa được kiểm chứng.
