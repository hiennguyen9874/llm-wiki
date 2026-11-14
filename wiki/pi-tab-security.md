---
type: Concept
title: Pi Tab Security and Integrations
description: Pi Tab's page access, model credentials, and remote MCP integrations cross different trust boundaries in bookmark and extension modes.
tags: [pi-tab, security, mcp]
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

**Reported:** [Pi Tab](pi-tab-overview.md) can read and change webpages and send task-relevant content and attachments to the configured model service; MCP tool arguments also leave the device. Treat both webpage actions and configured remote services as meaningful trust boundaries. Stopping a task does not reverse actions already taken.[^pi-tab]

## Browser and credentials

Bookmark tools execute in the page environment and can access exposed page JavaScript globals; extension tools use an isolated environment while still operating on the DOM. Bookmark requests depend on page policies and CORS, while extension model requests originate in its background environment. The manifest statically requests access to all HTTP(S) hosts; this does not establish what it accesses in any particular session.[^pi-tab]

**Reported:** saved bookmarks can contain model API keys and can carry them through sharing or browser synchronization; do not share credential-bearing bookmarks. The README distinguishes provider OAuth credentials, which it says are not exported in bookmarks: they remain per origin in bookmark mode and in the extension across sites. It reports that Anthropic's token endpoint blocks cross-origin sign-in from the installation site, requiring the extension for that sign-in.[^pi-tab]

The user guide's model section says its page does not perform OAuth login or refresh and that a bookmark downloads no external scripts, while the README's Account sign-in section describes native OAuth and on-demand OAuth/Bedrock code. These statements may refer to different contexts or versions; the documentation does not resolve the scope here. Implementation inspection is pending, so do not treat either as a universal verified claim.[^pi-tab]

## MCP boundary

**Reported:** MCP supports remote streamable HTTP, not local stdio processes or servers requiring OAuth. Bookmark connections require server CORS; extension connections originate in the background. Headers may reference configured environment values, and hidden tools are not registered. Imports preview changes and validate atomically; saving and successful connection are separate outcomes. The user guide warns that concurrent plain-HTTP bookmark windows lack strict mutual exclusion for MCP configuration writes.[^pi-tab]

The claims above are source reports except for the explicitly observed manifest declaration; no exploit testing or runtime verification was performed. Implementation and tests are pending; see the [coverage ledger](pi-tab-overview.md#evidence-and-coverage).[^pi-tab]

[^pi-tab]: Pi Tab at `c753976e0906dbd7c5ca88152332434d1584b8a7`, `README.en.md` §§ MCP servers, Before you start, Account sign-in; `docs/usage.en.md` §§ Configure your model, MCP servers, Scope and limitations; `SECURITY.md` § 使用时的安全边界; `extension/manifest.json` § host_permissions.
