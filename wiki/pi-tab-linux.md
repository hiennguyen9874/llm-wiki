---
type: Concept
title: Pi Tab Linux Tools
description: Pi Tab's extension offers per-conversation ephemeral Linux Wasm tools with restricted networking and explicit loss and replay limits.
tags: [pi-tab, linux, browser-agents]
status: draft
created: 2026-11-14
generated: { by: llm-wiki-agent/1, at: 2026-11-14T15:48:34Z }
stale_after: 2027-02-14
sources:
  - id: pi-tab
    resource: ../raw/pi-tab/README.en.md
    scope: ../raw/pi-tab/
    kind: code
    revision: c753976e0906dbd7c5ca88152332434d1584b8a7
    title: Pi Tab 1.5.3
---

**Reported:** the [Pi Tab](pi-tab-overview.md) extension provides a separate Linux Wasm environment for each conversation, starting on its first command or file operation. It offers `bash`, `read`, `grep`, and `edit`; `bash` actually runs BusyBox `/bin/sh`, not GNU Bash, and the default directory is `/workspace`.[^pi-tab]

## Persistence and networking

**Reported:** child agents have independent filesystems. Files survive page reloads and tab closure, but conversation reset or deletion, extension reload, background-page recreation, and browser exit discard them; unfinished Linux tool calls do not replay automatically. Bundled kernel and filesystem permit offline startup, although model calls still need a model service.[^pi-tab]

The built-in `curl` routes HTTP(S) through JavaScript fetch in the extension background. Pipes, redirection, file transfers, and cancellation are supported, but proxies, `-k`, and browser cookies are not. There is no host directory mount, interactive terminal, or general command registry. These filesystem lifetime limits are separate from [conversation history and task recovery](pi-tab-recovery.md).[^pi-tab]

## Build and evidence

The documentation says normal `npm run build` verifies and copies prebuilt Linux assets; `npm run build:linux` requires Docker and rebuilds them. The Linux guide describes a worker/guest bridge and separately licensed kernel, BusyBox, musl and runtime. No build or test was executed, and the source and bundled binary internals were not audited; behavior is **Reported**, with further package work pending in the [coverage ledger](pi-tab-overview.md#evidence-and-coverage).[^pi-tab]

[^pi-tab]: Pi Tab at `c753976e0906dbd7c5ca88152332434d1584b8a7`, `README.en.md` § Linux in the extension; `linux/README.md` §§ 重建资源, 通信.
