---
type: Concept
title: Pydantic AI capability events
description: How a reusable Pydantic AI capability publishes typed CapabilityEvents for coordination and observability — namespaces and wire kinds, reserved envelope fields, capability attribution, stream versus immediate dispatch, and how listeners and adapters consume them.
tags: [pydantic-ai, agents, llm-frameworks, events]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:23:32Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-capabilities-overview
    resource: ../raw/capabilities/overview/index.md
    scope: ../raw/capabilities/overview/
    kind: docs
    revision: sha256:6434ebdb6f8a86b177d4659f738e214d9f719260787ae93cd1bcda3811bd15c
    title: "Capabilities"
---

A capability can publish typed **`CapabilityEvent`**s so that other capabilities — and the application — can coordinate around what it did, and so a UI or a trace can observe it[^pydantic-docs-capabilities-overview] A capability defines each payload as a dataclass in a stable namespace and emits it from an async capability hook or a capability-contributed tool with `await ctx.emit(...)`; capability events are a separate family from the application's `CustomEvent`, and emitting a `CustomEvent` from a capability raises a `UserError`[^pydantic-docs-capabilities-overview] The page names no Pydantic AI version, so the mechanics below are version-unknown.

## Declaring an event family

An event is a dataclass subclassing `CapabilityEvent` with a `namespace=` keyword, and the namespace is meant to be a module-level constant named after the capability or its `id`[^pydantic-docs-capabilities-overview] The vendor's own example declares `FileWriteEvent(CapabilityEvent, namespace=WORKSPACE)` with `path` and `bytes_written` payload fields and emits it from a `FunctionToolset` tool before the capability exposes that toolset through `get_toolset()`[^pydantic-docs-capabilities-overview]

The declaration rules:

| Rule | Behaviour |
| --- | --- |
| Namespace required | A `CapabilityEvent` subclass without one raises `TypeError` at definition time, rather than letting an unnamespaced event reach the stream |
| Namespace inherited | A subclass of another capability event inherits its namespace and contributes only its own name, so a shared base defines the family; a subclass can pass its own `namespace=` to move out |
| Event name | Derived from the class name unless an explicit `name=` is passed |
| Reserved field names | `data`, `capability_id`, `tool_call_id`, `tool_name` and `event_kind` belong to the envelope and are rejected when the class is defined |
| Abstract base | A base carrying only the namespace and common fields is marked `abstract=True`: it stays out of the registry and cannot be emitted, while subclasses register as usual |
| Dataclass required | The base must be decorated with `@dataclass` like any other event; an undecorated base contributes no fields and is rejected rather than silently producing payloads that miss them |
| Registry | Kinds are registered when the class is defined and must be unique within the process; re-executing the same definition, as when re-running a notebook cell, replaces the registration |

The **kind** is `namespace.event_name` — `workspace.file_read` in the page's example — and it is the event's wire identifier, not a display label[^pydantic-docs-capabilities-overview] Renaming a class therefore renames the tag, which breaks compatibility wherever events outlive the emitting process: [durable execution](pydantic-ai-durable-execution.md) histories and caches, persisted event logs, and subscribers matching on the kind. The stated rule is that a capability published as a library should pin `name=` on each of its events.

Deserialization has an import-order requirement: the module defining an event must be imported before the adapter that deserializes it is created, because each pydantic `TypeAdapter` captures the kinds registered at its own creation[^pydantic-docs-capabilities-overview] An event whose kind was not registered at that moment arrives as an `UnknownCapabilityEvent` with a `UserWarning`, without losing its payload fields, and re-serializing it preserves the wire representation so a later consumer can recover the typed event.

## Attribution on the event

Pydantic AI stamps the emitting capability's run id as `capability_id`[^pydantic-docs-capabilities-overview] For a capability given an `id` that is the `id`; for one without, it is a handle the framework mints per run — the page's example is `'<file_reader:4f3a9c>'` — which differs every run and must not be matched on, so a subscriber that needs to recognise a capability should require an explicit `id`. Events emitted from a capability's tools also receive `tool_call_id` and `tool_name`.

## Two dispatch modes

Listeners normally run when the event reaches its position in the stream, which is what keeps listener ordering equal to stream ordering and keeps listener work off the emitter's latency path[^pydantic-docs-capabilities-overview] Two timings are documented:

- **Stream dispatch (default).** For events emitted during tool execution, listeners run before the next model request. An event emitted during `before_model_request` may only reach listeners after that request begins, with the same as-soon-as-possible timing as `ctx.enqueue()`.
- **Immediate dispatch.** An event class declaring `dispatch='immediate'` runs every listener before `emit` returns, which is what a decision event needs when a listener must mutate it before the emitter continues.

The immediate mode's contract, as the page states it[^pydantic-docs-capabilities-overview]:

- `emit` returns only once every listener has run, and returns the *same instance* it was given, so a decision is readable immediately off either reference.
- Pydantic AI buffers the event before invoking listeners; stream consumers receive it only after all listeners have run, so nobody observes a decision half-made.
- Attribution is stamped on the event in place.
- An event emitted by a listener appears in the stream after the decision event.
- Inline events are still delivered exactly once, including when the same instance is re-emitted.
- Stream-dispatch listeners run inside user-defined `wrap_run_event_stream()` wrappers.

The vendor's example is a veto: `FileWriteStartEvent` carries `cancelled` and `cancel_reason` with a `cancel()` method, a `write_file` tool emits it and refuses when `cancelled` comes back set, and a `ProtectGitDirectory` capability listens for it and cancels writes under `.git/`[^pydantic-docs-capabilities-overview]

## Reacting to events

A capability reacts with `@on_event(...)` on an async method, decorated with the event classes it accepts; filtering is `isinstance` against the classes passed[^pydantic-docs-capabilities-overview] A bare `@on_event` receives the full `AgentStreamEvent` union — model response deltas, tool call and result events, deferred and enqueued-message events, custom events and capability events.

Naming the classes is not only about typing the parameter: the classes are what let dispatch skip a capability without descending into it, so a bare `@on_event`, or an overridden `on_event()` whose dispatch cannot be known in advance, opts that capability into every event, and a capability that combines others reports the union of its children's[^pydantic-docs-capabilities-overview] The guidance is to override `listens_to()` alongside an overridden `on_event()` to declare what it dispatches. Dispatch ordering follows the same rules as stream order: listeners run sequentially in capability order, marked methods within one capability run in definition order, and the emitting capability receives its own events.

The page's worked example is a repo-context capability that listens for file-read and directory-list events and, when the path ends in `AGENTS.md`, calls `ctx.enqueue()` with a follow-the-instructions message[^pydantic-docs-capabilities-overview]

## Getting an event to a consumer

Capability events surface on the agent run's event stream, but they are internal coordination signals, so UI adapters do not forward them by default[^pydantic-docs-capabilities-overview] Three routes are documented:

| Route | Use it when |
| --- | --- |
| Override `handle_capability_event()` on a UI event stream | A protocol adapter should map the event onto its own protocol; the payload is built by the adapter because `CapabilityEvent` has no `to_payload()` |
| `@agent.on_event` plus `ctx.emit(CustomEvent(...))` | The application wants to expose a public payload to a frontend; the listener belongs to the application, which is one of the places application `CustomEvent`s may be emitted |
| `Hooks.on.event` | You want a `Hooks` [capability](pydantic-ai-capability-primitive.md) anyway, for the other hook families or to choose where it sits among capabilities |

## Limits

- The source is one vendor page section that names no Pydantic AI version and no date; every API name here is version-unknown, and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-capabilities-overview]
- The `CapabilityEvent` envelope is described by its reserved field names and by `kind`; its full schema, its serialized form and the `AgentStreamEvent` membership are never enumerated.
- Listener cost, error handling inside a listener, whether a listener can raise to fail the run, and how immediate dispatch interacts with [durable replay](pydantic-ai-durable-execution.md) are unstated; separate captures do state that `@on_event` listeners run in workflow code and must stay deterministic, and that `ctx.emit()` is refused from tools inside an activity, which is where a capability's own tool-emitted events would otherwise come from.
- No capability, event class, listener or adapter was constructed and no stream was consumed, so everything above is **Reported**.

## Relationships

- **Extends** the [capability primitive](pydantic-ai-capability-primitive.md): events are the run-time coordination channel a capability gets on top of instructions, tools, hooks and model settings.
- **Complements** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md): hooks intercept a stage, events report what a capability did and let another capability react; `Hooks.on.event` and `@agent.on_event` are the two registration surfaces shared by both.
- **Must stay deterministic under** [durable execution](pydantic-ai-durable-execution.md), [DBOS](pydantic-ai-dbos-streaming.md) and [Temporal](pydantic-ai-temporal-streaming.md), where listeners re-run on replay and emission from inside an activity is refused.
- **Channels observability into** [Pydantic AI observability](pydantic-ai-observability.md): the event stream is what instrumentation and UI adapters read, with capability events excluded from UI forwarding by default.
- **Documented alongside** the [capability catalog](pydantic-ai-capability-catalog.md), which lists the capabilities that publish them.

[^pydantic-docs-capabilities-overview]: Pydantic Docs, "Capabilities" (https://pydantic.dev/docs/ai/capabilities/overview/; 4,642 words as declared, 5,228 by local `wc -w`; language `en`; no publication date and no Pydantic AI version). Sections used: §intro (the publishing sentence and the on-demand/tool-search split); §"Capability events" (the `FileWriteEvent` and `Workspace` sample, the module-constant namespace advice, the `CustomEvent`-from-a-capability `UserError`, the five reserved envelope fields, `capability_id` and the per-run handle, `tool_call_id`/`tool_name`, UI adapters not forwarding, `handle_capability_event()`, the `@agent.on_event` republish sample, the `Hooks.on.event` alternative, the `kind` serialization and inheritance rules, the `abstract=True` base, the registry and `TypeAdapter`/`UnknownCapabilityEvent` rules); §"Reacting to events" (the `@on_event` decorator, the `isinstance` filter, the bare-`@on_event` union, dispatch skipping, `listens_to()`, the sequential listener and definition ordering, the emitter receiving its own events, the stream-position default with the tool-execution and `before_model_request` timings, `dispatch='immediate'`, the same-instance return, the buffered stream delivery, exactly-once delivery, and the wrapper interaction), plus the `FileWriteStartEvent` veto sample. Local capture: `raw/capabilities/overview/index.md`, content digest sha256:6434ebdb. Evidence class: **Reported** — vendor documentation naming no release version; nothing was constructed, emitted or consumed.
