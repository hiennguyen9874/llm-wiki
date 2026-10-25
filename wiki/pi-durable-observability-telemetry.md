---
type: Concept
title: Pi Durable Observability and Telemetry
description: Pi Durable exposes committed state through watches and agent events, reports failures through onReport, and emits typed telemetry spans, events, metrics, and usage totals.
tags: [pi-durable, observability, telemetry, events]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T16:07:19Z }
stale_after: 2027-01-25
sources:
  - id: pi-durable-readme
    resource: ../raw/pi-durable-readme.md
    kind: docs
    title: "@earendil-works/pi-durable README"
  - id: tannermidd-durable
    resource: ../raw/tannermidd-durable/index.md
    scope: ../raw/tannermidd-durable/
    kind: article
    title: "Pi Durable, explained (Pi Pocket guide)"
---

Everything a UI needs is committed state. `watch()` returns the conversation's structural view at attachment, then delivers each commit that touches it together with that commit's Chord operations, one callback at a time. `watch.value` exposes `entries` (the active transcript) and the built-in documents (`pi.live`, `pi.inbox`, `pi.usage`, `pi.agent`, `pi.provider`). A watch ends once, and `closed`/`stop()` gives the reason: `stopped`, `cancelled` (its acquisition context was cancelled), `retired` (a document watch whose incarnation retired, after delivering `[["r", null]]`), `ended` (the Harness closed), `listener_error`, or `failed` (the Harness failed). An ended watch keeps its last value and no longer references the Harness.[^pi-durable-readme]

## Watch delivery

Commits that land while a callback runs are delivered together in the next callback: the newest view plus the operations of all of them, folded (string appends join, repeated field sets keep the last). Past 10,000 pending operations the callback receives one root replacement `[["r", view]]` with the whole newest view instead. The guide reports a separate, coarser cap: a slow watch keeps at most 100 undelivered frames and then receives one frame holding the newest view.[^tannermidd-durable] A client that joins late or reconnects starts from the current view; nothing is replayed. `watchDoc()` watches one document, and `subscribeCommits()` sees what was actually stored, including deferred commits.[^pi-durable-readme]

## Agent events

For consumers that want coding-agent-style events (`message_start`, `message_update`, `tool_execution_start`, ...) instead of structural state, `watchEvents(harness, conversationId, context)` yields a `snapshot` and then batches derived from commits, one batch per commit, applied on top of the snapshot. Message and tool updates carry deltas: text and thinking appends, appended tool-call argument text, and output trims and appends. A consumer more than 100 batches behind receives a fresh `snapshot` event instead. The README points to `test/examples/18-json.ts` for a full run's event stream.[^pi-durable-readme]

## Reports

`onReport(error, info)` classifies what happened in `info.type`:[^pi-durable-readme]

- `session_failed` for the error that failed the Harness (a Storage error, often a platform reset).
- `task_faulted`, `task_parked`, `migration_failed`, `task_outdated`, or `task_error` for a task, with `info.task` (`id`, `kind`, `conversationId`) and `info.extension` naming the installing extension.
- `extension_error` for hooks, sections, wrappers, and tools, with the extension's name.
- `host_error` for a host callback, named in `info.callback`.
- `listener_error` for a throwing or rejecting listener.

A host can feed `task_faulted` reports of one kind to its own circuit breaker. Reports also emit a `pi.durable.report` event on the current span, with only `type`, optional fixed `reason`, `extension`, and `task.id`; without a span the NOOP span drops it, and no root report span is created. The `pi.durable.reports` metric counts all reports by `type` only, including those without a span; clock failures report without a phase context.[^pi-durable-readme]

## Telemetry

`HarnessOptions.telemetry` accepts a host-owned `TelemetryContext` from `@earendil-works/pi-telemetry`, with optional `propagation` and `metrics`; omitted, it is a no-op. `DURABLE_TELEMETRY_SCHEMA` documents the typed spans, events, and metrics. Attributes contain IDs and control metadata, never messages, arguments, or results; IDs point to the transcript.[^pi-durable-readme]

| Span | Covers |
| --- | --- |
| `pi.durable.submit` | The public submit call and its commit; each input starts a new root trace linked to the caller's current span, and a write is a child of its caller. Duplicate `requestId` preserves the original submission and carrier. |
| `pi.durable.phase` | One run or abort phase of every task, including its decision commit — never the next phase, a durable wait, or a restart. Attributes identify task, phase, attempt when present, `resumed`, and outcome; tool phases also identify the tool and call. |

Events emitted include `pi.durable.report`, `entry`, `submission`, `checkpoint` (committed running phase changes), and `replay` (a nested call answered from its stored result). Failed phase outcomes set error status with a fixed category (`task_faulted`, `task_failed`, or `task_orphaned`) and a diagnostic message truncated to 500 characters; diagnostics can contain caller content, but no error detail or exception name is recorded. An `aborted` outcome keeps status `ok`, including interruption by close or cancellation.[^pi-durable-readme]

Trace propagation stores optional opaque `trace` carriers in submission and task JSON without a storage migration. Phase spans extract their task's stored carrier, or start at the adapter root when absent or unknown. `TaskOptions.trace` inherits the creator's carrier, accepts an explicit override, or uses `"root"`. A run started for several queued inputs takes the first input's trace, and its first invocation's phase spans link to the other inputs through immutable task `links`; a steer stays in the running trace and its submit span links to that run's carrier. Metrics record `pi.durable.phase.duration` (milliseconds, by task/phase/outcome) and `pi.durable.tasks.active` (live tasks by name), and closing the Harness releases its active counts.[^pi-durable-readme]

## Usage totals

Each conversation keeps token and cost totals in `docs["pi.usage"]`: per `provider/model` for model responses, and per tool name for tool results that report usage. Failed and aborted attempts count too. `harness.usage(context)` returns session-wide totals as `{ models, tools }`.[^pi-durable-readme]

## Evidence and limits

Observability behavior is **Reported** documentation; no watch, event stream, or telemetry exporter was run. The guide's 100-frame cap is a secondary report and its relation to the README's 10,000-operation rule is not stated. The telemetry schema is named but its full field list is not reproduced here, and the README's claim about report event contents is a limit for consumers needing exact payloads.

## Relationships

- **Observes** [conversations](pi-durable-conversations.md), [tasks](pi-durable-tasks.md), [tools](pi-durable-tools-nested-calls.md), and [compaction](pi-durable-compaction.md).
- **Reflects** the commit ordering and deferred persistence of [crash recovery](pi-durable-crash-recovery.md).
- **Depends on** `@earendil-works/pi-telemetry` and [storage](pi-durable-storage.md) commits.
- **Surfaces** failures classified by [extensions and hooks](pi-durable-extensions-hooks-agents.md).

[^pi-durable-readme]: @earendil-works/pi-durable README (`raw/pi-durable-readme.md`), locators: §Watching a Conversation, §Agent Events (Experimental), §Failures and Recovery, §Usage and Cost, §Quick Start, §Task Graph.

[^tannermidd-durable]: Pi Pocket, “Pi Durable, explained” (`raw/tannermidd-durable/index.md`), locators: §Clients show committed state.
