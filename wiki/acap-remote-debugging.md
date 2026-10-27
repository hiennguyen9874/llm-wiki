---
type: Concept
title: "Remote debugging ACAP applications with GDB and VS Code"
description: "Debug an ACAP application on the device from VS Code: the remote-debug-example, dev container and GDB server setup, and what the vendor page leaves undocumented."
tags: [edge-ai, axis, acap, debugging, gdb, vscode]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T05:13:03Z }
stale_after: 2027-04-30
sources:
  - id: acap-remote-debug
    resource: ../raw/acap/how-to-guides/debugging/index.md
    scope: ../raw/acap/how-to-guides/debugging/
    kind: docs
    revision: "ACAP version 12"
    title: "Debugging | Axis developer documentation"
---

# Remote debugging ACAP applications with GDB and VS Code

An ACAP application can be debugged while it runs on the device, not only inferred from its log output. Axis documents one path: **GNU Debugger (GDB)** on the device plus **Visual Studio Code** as the front end, packaged as the `remote-debug-example` in the `acap-native-sdk-examples` repository. The debugging page is only a pointer to that example — it states the shape of the workflow but leaves the actual commands to the example's README, which is not part of `raw/`.[^acap-remote-debug]

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

## Limits of this page

The source is a 94-word overview with no sub-sections, so the following are **not established** by it:[^acap-remote-debug]

- which prerequisites the example requires (debug build flags such as `-g`, a compiler or GDB version, network reachability, credentials, or device-side permissions);
- how the GDB server is obtained, which port it listens on, and how VS Code attaches to it (launch configuration, `gdbserver`/`gdb` invocation);
- whether the GDB server comes from the SDK image or is built or supplied by the example;
- any supported AXIS OS or ACAP version, and whether debugging works on all camera models;
- whether the application runs under the normal ACAP runtime or needs a special debug launch when attached.

The authoritative procedure lives in the external repository. Until that README and its scripts are captured in `raw/`, the actionable steps on this page are deliberately absent rather than reconstructed from memory. This is why the concept is `draft`.

## Logs versus a debugger

The two facilities answer different questions and do not replace each other: [Application logging trong ACAP](acap-application-logging.md) records messages the application chose to emit and is the only documented route for `LOG_DEBUG`, but it says nothing about variable state the code did not print. **Synthesis:** a debugger is the better tool for a wrong value at a known code location, while logs are better for behavior that only appears over time or after deployment. The logging page requires SSH for `journalctl`; the debugging page does not state its own device-access requirement, so that cannot be assumed to be the same.

## Độ phủ nguồn

- Entry point: `raw/acap/how-to-guides/debugging/index.md` (94 words), site `developer.axis.com`, bộ tài liệu ACAP 12. The folder contains only this file — no images, attachments, or sub-pages — and the whole page was read.
- No code, command, or configuration block exists in the source; the body above therefore quotes no commands.
- External references not present in `raw/` and therefore unverified: the `acap-native-sdk-examples` repository, the `remote-debug-example` directory and its README, and the tools it documents.
- The page carries no publication or update date; `revision: "ACAP version 12"` is inferred from the documentation bundle, as with the other ACAP pages in this wiki.

## Độ tin cậy

Every claim about the debugging method, the example's existence, and the quoted workflow steps is **Reported** by Axis's official documentation, read on 2026-10-27. No claim is **Observed** (the example repository was not inspected) or **Reproduced** (no dev container was built, no GDB server uploaded, no remote debugging session run). The statement that breakpoints and variable inspection become available is the vendor's description of what the example achieves, not a measured result here.

## Relationships

- **Depends on** [ACAP Native SDK và nền tảng ứng dụng camera Axis](axis-acap-native-sdk.md): the example, toolchain, and container images come from the SDK ecosystem.
- **Uses** [Môi trường phát triển ACAP: Docker SDK và VS Code Dev Containers](acap-dev-environment-setup.md): step 2 starts the dev container, and VS Code supplies the debugger UI.
- **Uses** [Ví dụ ứng dụng ACAP chính thức](acap-application-examples.md): `remote-debug-example` is one entry in that collection.
- **Complements** [Application logging trong ACAP](acap-application-logging.md): logs observe emitted messages, a debugger stops execution and inspects live state.
- **Constrained by** [phiên bản ACAP và tương thích với AXIS OS](acap-versioning.md) in principle, although the debugging page names no version requirement.
- **Pending on** the external `remote-debug-example` README, which must be captured in `raw/` before the procedure can become `stable`.

[^acap-remote-debug]: Tài liệu chính thức: [Debugging — Axis developer documentation](../raw/acap/how-to-guides/debugging/index.md), toàn bộ trang (94 từ, không chia mục); các liên kết tới `acap-native-sdk-examples` và `remote-debug-example` là external link chưa được kiểm chứng.
