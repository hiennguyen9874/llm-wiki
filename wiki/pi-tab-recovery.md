---
type: Concept
title: Pi Tab Recovery and Storage
description: Pi Tab's bookmark and extension modes differ in conversation ownership, reload recovery, page authorization, and deletion guarantees.
tags: [pi-tab, recovery, browser-storage]
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

**Reported:** [Pi Tab](pi-tab-overview.md) retains local conversation history, but reload recovery is not equivalent to durable authorization to act on a new document. Bookmark and extension modes use separate stores and have different ownership and restart behavior.[^pi-tab]

## Storage and recovery

- Bookmark history is stored in webpage-origin IndexedDB; concurrent tabs may maintain separate records. The user must click the bookmark again after reload, then start a blank conversation or resume unfinished work. When another tab owns history, startup waits at most 1.5 seconds and offers retry or an explicitly independent conversation; absence of Web Locks also requires an independent conversation.[^pi-tab]
- Extension history is in extension IndexedDB, grouped by exact hostname; enabled tabs restore after reload while background tasks can continue. Navigation, reload, and closure revoke authorization for the old document; acting on the new page requires authorization. Closing the task's tab stops its tasks. After a background restart, interrupted tasks remain paused and can be cleared through the confirmation-based interrupted-task control.[^pi-tab]
- The guide does not guarantee continuity after browser closure, extension removal, or storage clearing; no cloud sync or automatic merging between modes is provided. Deleting a conversation removes its list entry and resets context, but the underlying Pi Durable history log remains in local storage; deletion is not secure erasure.[^pi-tab]

## Queue and side effects

Messages sent during a reply normally queue as `followUp`. A priority `steer` waits until the current tool round finishes, or a text-only reply completes; it does not interrupt an active model request or tool. Stop cancels the conversation and queued messages, but cannot undo page actions already performed.[^pi-tab]

These are **Reported** documentation claims, not reproduced recovery guarantees. Implementation and tests remain pending; see the [coverage ledger](pi-tab-overview.md#evidence-and-coverage).[^pi-tab]

[^pi-tab]: Pi Tab at `c753976e0906dbd7c5ca88152332434d1584b8a7`, `README.en.md` §§ Quick start, Continue a conversation on another page; `docs/usage.en.md` §§ Get started, Continue a conversation on another page, Conversation storage and recovery.
