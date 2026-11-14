---
type: Concept
title: Pi Tab Browser Agent Overview
description: Pi Tab runs a Pi Durable-based agent as a bookmark or Chrome extension, with distinct page access, storage, and collaboration scopes.
tags: [pi-tab, browser-agents]
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

Pi Tab is a browser-based agent for reading and interacting with the current page, offered as a bookmarklet or Chrome extension. **Reported:** it builds on [Pi Durable](pi-durable-overview.md), supports model selection and conversation history, and can act on the DOM or run JavaScript. The two modes have separate histories and materially different execution and storage boundaries.[^pi-tab]

## Modes and operation

**Reported:** the bookmark carries its runtime and configured model settings; launch it on each page. Settings and history are scoped to the page origin, and collaboration stays on the same page. The extension is loaded unpacked through `chrome://extensions`, runs on ordinary HTTP(S) pages, shares model settings across sites and groups conversations by exact hostname; its tab tools support cross-tab work. Installing it does not add extension tools to bookmark sessions.[^pi-tab]

The extension exposes `tab_list`, `tab_open`, `tab_send`, and `tab_read`. A new tab or window creates an independent task, not an inherited transcript. Cross-site continuation instead opens an existing conversation from history on an enabled destination page; selecting history alone does not send a message.[^pi-tab]

**Observed:** the package declares Node.js 24 or newer for development and pins `@earendil-works/pi-durable` 1.4.0; the extension manifest is Manifest V3 and requests tabs, storage, offscreen, scripting, and HTTP(S) host permissions. These are static declarations, not a runtime verification.[^pi-tab]

## Evidence and coverage

The English README, English user guide, security policy, package manifest, extension manifest and Linux guide were inspected; behavior is **Reported** unless explicitly identified as observed. No build, browser execution, or tests were run. Source implementation, tests, build/release scripts, issue documents, configuration and remaining translations are pending inspection; bundled/generated `dist`, installer HTML, lockfile, OAuth bundles, Linux binaries and vendored code were inventoried but not analyzed. The repository is Apache-2.0 with separately licensed Linux components, per its README. No independent verification is claimed. This partial package coverage keeps the page draft.[^pi-tab]

## Relationships

- **Uses** [Pi Durable](pi-durable-overview.md) as its reported agent harness.
- **Has operational constraints described by** [Pi Tab Recovery and Storage](pi-tab-recovery.md).
- **Has trust boundaries described by** [Pi Tab Security and Integrations](pi-tab-security.md).
- **Offers** [Pi Tab Linux Tools](pi-tab-linux.md) in extension mode.

[^pi-tab]: Pi Tab repository at revision `c753976e0906dbd7c5ca88152332434d1584b8a7`, `README.en.md` §§ Highlights, Quick start, Continue a conversation on another page, Contribute; `docs/usage.en.md` § Install the Chrome extension; `package.json` (version, engines, dependencies); `extension/manifest.json` (permissions, host_permissions).
