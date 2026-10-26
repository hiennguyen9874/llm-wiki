---
type: Concept
title: WeKnora cross-session memory
description: Principal-scoped resident memory, query recall, explicit versus automatic writes, confirmation states, and bounded extraction.
tags: [ml, weknora, memory]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora separates durable personal memory from session history and document knowledge. **Observed:** memory belongs to a principal within a workspace, uses a small resident block plus query-matched recall, and can be searched on demand by an agent. Workspace, subject, and per-request agent switches gate access; missing workspace memory configuration is disabled.[^weknora]

## Model and trust states

`internal/types/memory.go` declares profile, preference, fact, task, and interest kinds. Profile/preference/interest form the resident set; fact/task are situational. Origins distinguish explicit requests, background extraction, and manual edits. Statuses are active, superseded, archived, and pending. The pending-state contract keeps inferred statements out of prompts until confirmation; supersession retains the history of replaced statements rather than deleting it.[^weknora]

**Observed budgets:** resident block 900 runes; query recall at most five situational items within 600 runes; on-demand search defaults to ten items, caps at twenty, and budgets 2,000 runes. A memory item is capped at 300 runes, and the default active-item capacity is 200. These are character/rune budgets, not exact tokenizer counts.[^weknora]

## Read and extraction paths

**Observed:** `Service.Recall` performs no model call and degrades failures into no memory instead of failing the chat. It loads active resident items, caps selected interests, then recalls situational candidates while excluding already resident IDs. It renders current items rather than trusting only a cached block, using that cache as a fallback. `SearchMemory` uses the same enabled-scope predicate, excludes non-active states, and records usage of matched items.[^weknora]

Write modes distinguish `explicit_only` (no background extraction model call) from `auto`. `ScheduleExtraction` records pending per-session work before enqueueing so debounce/minimum interval defer processing instead of silently dropping turns. Inspected extraction constants cap a run at 40 messages, eight candidate items per segment, and three segments; a one-hour gap divides topics, and follow-up runs handle remaining work.[^weknora]

## Privacy and failure boundaries

Scope is derived from request context rather than a client-selected memory subject ID. The service intentionally uses the same not-found response for absent items and scope mismatches. Error sentinels distinguish disabled memory, previously forgotten statements, and content left useless after sensitive-data redaction. **Limit:** declarations and initial service logic do not establish that every extraction, confirmation, deletion, or redaction path obeys these contracts.[^weknora]

## Relationships

- Used by the [agent turn runtime](weknora-agent-runtime.md), but not equivalent to its conversation-history window.
- Extracted asynchronously through [task queues](weknora-task-queues.md).
- Principal boundaries depend on [authentication and authorization](weknora-security.md).

## Coverage limits

Selected sections of memory types, service, extraction scheduling, and search were read. Repository scoping, vector/lexical ranking, consolidation, tombstones, confirmation APIs, retention, and evaluation datasets/tests remain pending. No memory quality, deletion, or isolation test was run; see the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `internal/types/memory.go` kind/origin/status/write-mode constants, rune/item budgets, `ResidentMemoryKinds`, `MemorySubject`, `MemoryAllowedForAgent`; `internal/application/service/memory/service.go::workspaceConfig`, `enabledScope`, `Recall`, error sentinels; `memory/search.go::MemoryAvailable`, `SearchMemory`, `lexicalPoolSize`; `memory/extract.go::ScheduleExtraction` and extraction-budget constants. Package entry: [README](../raw/WeKnora/README.md), “Memory and curation” and v0.8.0 notes.
