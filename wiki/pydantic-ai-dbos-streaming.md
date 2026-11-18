---
type: Concept
title: Pydantic AI DBOS streaming and cancellation
description: How a DBOS-durable Pydantic AI run delivers events and stops — buffered model streams, the three event-handler placements and their replay rules, workflow-level cancellation, run deadlines, token counting, and durable polling for suspended turns.
tags: [ml, pydantic-ai, agents, durability, dbos, streaming]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:15:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-dbos-docs
    resource: ../raw/capabilities/durable_execution/dbos/index.md
    scope: ../raw/capabilities/durable_execution/dbos/
    kind: documentation
    revision: sha256:244a04f5850362a7fba71144476c4757655019e142a4e838712ae39035332862
    title: "Durable Execution with DBOS"
---

**Reported, Pydantic AI version unspecified:** a DBOS durable run is observable but not steerable. `run_stream()` and `run_stream_events()` still work inside a workflow, but the model stream is consumed inside a step and the workflow then replays the final response, so a consumer receives each part whole instead of as deltas, cannot cancel the stream, and cannot pass a `CancellationToken` in.[^pydantic-dbos-docs] What remains controllable moves up a level: you cancel the DBOS workflow, you bound the run with `timeout=`, and you choose where event handlers run — inside a step, in workflow code, or per run — because that placement decides what replays.[^pydantic-dbos-docs]

The engine's step model, naming rules and concurrency hazards are in [Pydantic AI on DBOS](pydantic-ai-dbos.md); the equivalent split for the other co-maintained engine is [Pydantic AI Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md).

## Streams arrive whole, not as deltas

Inside a workflow, `Agent.run_stream()` and `Agent.run_stream_events()` work, but their events are buffered: the model stream runs inside the durable step, and once the step completes the workflow replays its final response, so each part arrives as one `PartStartEvent` carrying its full content rather than as the deltas the model streamed — and those deltas are not recorded in the step's result.[^pydantic-dbos-docs] `Agent.run_stream_sync()` is excluded outright: it requires no running event loop and wraps `run_stream()`, so workflow code must use the buffered async APIs or `Agent.run()` with an event stream handler. Outside a workflow an agent with `DBOSDurability` behaves normally, so `run_stream_sync()` works as usual, while the deprecated `DBOSAgent` forbids `run_stream()` inside workflows.[^pydantic-dbos-docs]

## Three places an event handler can run

Passing `event_stream_handler=` to `DBOSDurability` is the route for handlers with I/O side effects: it runs inside a DBOS step, receives model events live inside each model-request step, receives each tool event in its own event-handler step, and — like any step — may run more than once if the workflow recovers before that step is checkpointed, so its side effects must be idempotent.[^pydantic-dbos-docs]

| Handler | Runs in | What it sees | Replay behaviour |
| --- | --- | --- | --- |
| `DBOSDurability(event_stream_handler=...)` | A DBOS step | Model events live inside the model step; each tool event in its own handler step | May run again if recovery precedes the checkpoint — keep side effects idempotent |
| `ProcessEventStream` capability | Workflow code | Tool and final-output events live; model events replayed from the final response after each model request | Re-runs on replay, so it must be deterministic |
| `Agent.run(event_stream_handler=...)` | Workflow code, against replayed model events | The buffered replay | Re-runs with the workflow |

A durability `event_stream_handler=` and a separately registered `ProcessEventStream` are two distinct handlers and each fires once.[^pydantic-dbos-docs]

## What `ctx.emit()` guarantees

Emissions are journal-positioned rather than ordered globally.[^pydantic-dbos-docs]

- An event emitted with `ctx.emit()` inside a tool call takes its handler step's journal position at emission, before the tool's later durable calls; the handler still runs in the stream consumer, in emission order and after immediate capability listeners settle, and `emit` does not wait for it — so a handler can depend on later tool work, and a tool can report progress before waiting for a consumer's response.[^pydantic-dbos-docs]
- An emission from inside a DBOS step — an MCP or dynamic-toolset tool, an `event_stream_handler`, or a tool you decorated with `@DBOS.step` — is delivered when the step actually runs and is **not** re-emitted when its recorded result is replayed on recovery. Like a log line written inside a step, it is a side effect of running the step, not part of its recorded result.[^pydantic-dbos-docs]
- Plain function tools and capability hooks run in workflow code, where an emission re-runs with the rest of the workflow; `@on_event` listeners run there too, so they re-run on recovery and must be deterministic, with I/O kept in a durability `event_stream_handler=` that runs in its own step.[^pydantic-dbos-docs]
- A missed event is treated as a missed notification, not as lost state — unlike `ctx.enqueue()`, which is rejected inside a step because dropping it would change what the model sees. Carrying a durable unit's emitted events in its recorded output, so a replay reproduces them, is tracked in pydantic-ai#7971.[^pydantic-dbos-docs]

## Cancellation belongs to the workflow

Because the model stream is consumed inside the step, `AgentStream.cancel()` is not available across the durable boundary, and a `CancellationToken` cannot be passed to a DBOS durable run.[^pydantic-dbos-docs] `RunContext.cancel()` raises a clear `UserError` inside a step-wrapped unit — a dynamic or MCP tool, or an `event_stream_handler` — whose recorded result would replay without re-running; a plain function tool runs at workflow level, where `cancel()` works and is replay-consistent.[^pydantic-dbos-docs]

To stop a run from outside, cancel the DBOS workflow. DBOS aborts it with its own exception rather than an `asyncio.CancelledError` — `DBOSWorkflowCancelledError`, or `DBOSWorkflowConflictIDError` on dbos 3.2 and later — but the run's state is attached to it, so catching it inside the workflow and calling `RunCancelled.from_cancellation()` recovers the message history after cancellation. The `DBOSAwaitedWorkflowCancelledError` that the workflow's caller receives does not carry that state, because DBOS builds that error from the workflow's recorded status; and a workflow that fails with an `AgentRunError` stores the run's whole conversation with the recorded error, so catching the error in the workflow keeps it out.[^pydantic-dbos-docs]

## A deadline that survives recovery

A run's `timeout=` works inside a workflow, and the run's start time is recorded as a `{name}.run_start_time` step, so a recovered workflow keeps the deadline the run started with — and may find that it has already passed. When the deadline passes, the run raises `RunTimedOut` in workflow code, where it can be caught. The deprecated `DBOSAgent` rejects `timeout=`.[^pydantic-dbos-docs]

The deadline bounds the agent run, not the workflow: bounding the workflow as well means starting it inside DBOS's `SetWorkflowTimeout`, which cancels the workflow when it expires.[^pydantic-dbos-docs]

## Counting tokens before a request

With `count_tokens_before_request=True`, the count runs as a `{name}__model.count_tokens` step ahead of each model request step, so recovery replays the recorded count instead of calling the provider again.[^pydantic-dbos-docs]

## Suspended turns and background mode

When a provider pauses a turn mid-flight (Anthropic `pause_turn`) or runs it as a server-side job that is polled until ready (OpenAI background mode), durability is per segment rather than per turn:[^pydantic-dbos-docs]

- Each segment runs in a separate model request step, and the wait between polls is a durable `DBOS.sleep` step, so recovery skips waits that already completed.[^pydantic-dbos-docs]
- The suspended `ModelResponse` and the background job id are checkpointed between segments, the final response is merged, and usage is recorded once.[^pydantic-dbos-docs]
- A `message_history` ending in a suspended response is passed to the first step, and step timeouts should be sized for one provider round trip.[^pydantic-dbos-docs]
- If an error abandons a suspended job, its provider teardown runs in a dedicated cancellation step. Batched requests behave the same way: submitting a request and each check on its batch are separate steps, with durable sleeps between checks.[^pydantic-dbos-docs]

## Coverage and limits

The package is one `index.md` capture, 4,754 words as declared and 4,758 by local `wc -w` including frontmatter, content digest sha256:244a04f5, with no attachments, includes or supporting files; this page draws on four of its sections and leaves the workflow/step model, naming, payloads, child workflows and retries to [Pydantic AI on DBOS](pydantic-ai-dbos.md).[^pydantic-dbos-docs]

- The page names no Pydantic AI, DBOS or Logfire release version, author, publication date or licence, so every API, event class and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule.[^pydantic-dbos-docs]
- Every external link in these sections — the streaming docs, the Pydantic AI API references for `PartStartEvent`, `AgentStream`, `CancellationToken`, `RunContext.cancel`, `RunCancelled`, `RunTimedOut` and `ProcessEventStream`, DBOS's `sleep` and context references, and the pydantic-ai#7971 thread — was read as a link, not followed.[^pydantic-dbos-docs]
- Nothing was installed, no stream consumed, no event emitted or replayed, no workflow cancelled, no deadline exceeded and no background job polled, so every claim is **Reported** and none **Observed** or **Reproduced**; the source gives no latency, chunk-size or ordering measurement to check the buffering claim against.[^pydantic-dbos-docs]
- Evidence class: **Reported**.

## Relationships

- **Specialises** [Pydantic AI on DBOS](pydantic-ai-dbos.md): the step model here is the same journal, and event-handler placement is a consequence of which code DBOS runs as a step.[^pydantic-dbos-docs]
- **Contrasts with** [Pydantic AI Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md): both engines buffer model streams and push cancellation to the workflow, but Temporal offers Workflow Streams and continue-as-new, neither of which appears in the DBOS page.[^pydantic-dbos-docs]
- **Constrains** [Pydantic AI run controls](pydantic-ai-run-controls.md) under this engine: run timeouts survive recovery while `CancellationToken` and `RunContext.cancel()` do not cross a step boundary.[^pydantic-dbos-docs]
- **Interacts with** [Pydantic AI model API errors](pydantic-ai-model-api-errors.md): `retry_after` becomes a durable sleep between two model steps, which is described on the DBOS page rather than here.[^pydantic-dbos-docs]
- **Limits** [Pydantic AI observability](pydantic-ai-observability.md) visibility under this engine: emitted events are not part of a step's recorded result, so a replay does not reproduce them.[^pydantic-dbos-docs]

[^pydantic-dbos-docs]: Pydantic, "Durable Execution with DBOS" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/dbos/`), 4,754 words as declared, 4,758 by local `wc -w`, no version, date or author stated; local capture `raw/capabilities/durable_execution/dbos/index.md`, content digest sha256:244a04f5. §"Streaming" (lines 213–234) for the buffered `run_stream()`/`run_stream_events()` behaviour, the `PartStartEvent` replay, `run_stream_sync()`'s exclusion, the durability `event_stream_handler`, `ProcessEventStream`, the per-run handler, the `ctx.emit()` journal position and re-emission rules, the `ctx.enqueue()` contrast and issue #7971, `AgentStream.cancel()`, `CancellationToken`, `RunContext.cancel()`, workflow cancellation and its exception types, `RunCancelled.from_cancellation()` and the `AgentRunError` conversation; §"Run Timeouts" (235–240) for the recorded start time, `RunTimedOut` and `SetWorkflowTimeout`; §"Counting Tokens Before a Request" (241–244); §"Suspended Turns and Background Mode" (245–248) for per-segment steps, durable sleeps, checkpointed suspended responses, teardown and batched requests; §"Wrapper-agent path (deprecated)" (130–156) for the wrapper's `run_stream` prohibition and rejected `timeout=`. Evidence class: **Reported** — vendor reference page naming no version; nothing was installed or executed.
