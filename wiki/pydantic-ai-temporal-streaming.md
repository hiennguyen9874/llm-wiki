---
type: Concept
title: Pydantic AI Temporal streaming and cancellation
description: How a durable Pydantic AI run delivers events and stops — buffered streams versus live handlers, Workflow Streams as an offset-addressed topic for frontends, what cancellation can cross the boundary, run timeouts and token counting, suspended provider turns, and continue-as-new for long runs.
tags: [ml, pydantic-ai, agents, durability, temporal, streaming]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-temporal-docs
    resource: ../raw/capabilities/durable_execution/temporal/index.md
    scope: ../raw/capabilities/durable_execution/temporal/
    kind: documentation
    revision: sha256:d1d6bdec59bcd1f8230987074ce0d7a28d0a365a38df590e4b5efb7326aead73
    title: "Durable Execution with Temporal"
---

**Reported, Pydantic AI version unspecified:** the streaming and cancellation APIs that work in-process do not all survive the durable boundary intact. `run_stream()`, `run_stream_events()` and `Agent.iter()` run inside a Temporal workflow, but their events are buffered behind the model activity; a live feed needs either a durability event-stream handler or Temporal's own Workflow Streams; and stopping a run has four different mechanisms with four different replay stories.[^pydantic-temporal-docs] The wiring, naming and payload rules this page builds on are in [Pydantic AI on Temporal](pydantic-ai-temporal.md).

## Streams arrive whole, not as deltas

The model stream is consumed inside the durable activity, so the workflow only sees the final response once the activity completes. Each part then arrives as a single `PartStartEvent` carrying its full content, rather than as the deltas the provider streamed, because the deltas are not recorded in the activity's result.[^pydantic-temporal-docs] Anything that needs per-token behaviour — a typewriter UI, a token-level guardrail — therefore has to be built on the live path below, not on the iterator.

Two handler paths exist, and they are distinct:[^pydantic-temporal-docs]

| Path | Where it runs | What it sees | Determinism |
| --- | --- | --- | --- |
| `event_stream_handler=` on `TemporalDurability` | Model events live inside the model-request activity; each tool event in its own event-handler activity | Live events | May run more than once if an activity retries, so side effects must be idempotent |
| `ProcessEventStream` capability | Workflow code | Tool and final-output events live; model events replayed from the final response after each request | Must be deterministic, because it re-runs on replay |

Both fire once, for different things: the durability handler sees the live stream inside the activity, while `ProcessEventStream` sees the buffered replay in workflow code. A per-run `Agent.run(event_stream_handler=...)` also runs workflow-side against replayed model events.[^pydantic-temporal-docs] Data flows in through the `deps` object and out through a Workflow Stream or an external system the handler can write to and the consumer can read.[^pydantic-temporal-docs]

`run_stream_sync()` is not usable in workflow code at all — it requires no running event loop — so under `TemporalDurability` the documented choices are the buffered async APIs or `Agent.run()` with an event-stream handler. Outside a workflow the agent behaves normally, so `run_stream_sync()` works as usual.[^pydantic-temporal-docs]

## Workflow Streams as the transport

Setting `event_stream_topic` on `TemporalDurability` turns the workflow itself into a durable, offset-addressed channel that a consumer outside it subscribes to, with no message queue to operate. The workflow hosts an `AgentEventStream` inside `async with`, and the topic is what enables streaming — orthogonally to `event_stream_handler`, which still sees every event if both are set.[^pydantic-temporal-docs] A consumer holding only a workflow handle calls `durability.stream_agent_events(client, handle, output_type=str)` and receives the same `AgentStreamEvent`s in order, ending with the `AgentRunResultEvent` that carries the result — a durable `run_stream_events()` across the process boundary.[^pydantic-temporal-docs]

Three behaviours follow from the design:[^pydantic-temporal-docs]

- **The iterator ends on its own** when the run does, so no separate completion signal is needed. A clean end means the run is over whether or not it produced a result: `events.result` is the `AgentRunResult` on success and `None` otherwise, and `handle.result()` then propagates the failure or cancellation.
- **Acknowledging the terminal event is what lets the workflow finish.** Leaving the `async with` block is what makes the stream readable until a subscriber acknowledges that event, which `stream_agent_events()` does internally. Nobody watching is not an error: the wait is bounded by `drain_timeout`, 30 seconds by default, and the workflow result stays authoritative either way. Raise `drain_timeout` if clients need a longer window.
- **Offsets are the resume primitive.** A subscriber defaults to `from_offset=0`, which replays everything published so far and then continues live, so a refreshed tab rebuilds the whole message. A client that still holds what it received passes `from_offset=offset + 1` and takes only the rest. Offsets run over the whole stream rather than per topic, so a topic-filtered subscription sees gaps wherever the workflow published elsewhere — which is why they must be read off the stream rather than counted.

Each independent workflow chain needs a unique workflow id; continue-as-new preserves it across the chain, so it must not be reused for an unrelated workflow.[^pydantic-temporal-docs]

### Driving a UI protocol

Because the stream ends in an `AgentRunResultEvent`, it is exactly what a `UIAdapter` consumes, including `on_complete`, which receives the run result as it would in-process. The protocol work splits across the boundary: the HTTP handler turns the request into a protocol stream and the workflow rebuilds the run arguments from the same body it was handed.[^pydantic-temporal-docs] In the documented `ChatWorkflow`, the body is stored as a constructor argument, an `AgentEventStream` is created in `@workflow.init`, and the run is built from `VercelAIAdapter(agent=agent, run_input=VercelAIAdapter.build_run_input(body))` — messages, deferred tool results and conversation id. The handler starts the workflow and returns `adapter.streaming_response(adapter.transform_stream(events))` over the topic.[^pydantic-temporal-docs]

That makes the workflow the queue: starting it hands the run to a worker, the HTTP request is only a subscriber, and the request can go away without touching the run.[^pydantic-temporal-docs]

Reattachment is where the security boundary sits. Storing the workflow id alongside the conversation — under the same ownership check the conversation already has — lets a second endpoint resume a run the client did not start. Taking a workflow id straight off the request path would let anyone replay anyone else's conversation, because a Temporal handle carries no authorization of its own.[^pydantic-temporal-docs]

### Choosing what to publish

A model stream emits one `PartDeltaEvent` per token and every published event stays in the workflow's state for the life of the run, so an unfiltered topic costs both history size and cost. Passing a `WorkflowStreamTopic` instead of a bare name allows a filter — the documented one drops per-token deltas with `not isinstance(event, PartDeltaEvent)` — while the terminal `AgentRunResultEvent` is always published, since it is what ends a subscription.[^pydantic-temporal-docs]

Under the hood the live model stream is published by `workflow_stream_event_handler()`, which returns an ordinary `EventStreamHandler` that can be composed or wrapped; `event_stream_topic` is preferred because it also publishes the run's workflow-side events and the terminal event, neither of which a handler alone can do.[^pydantic-temporal-docs]

Emitting from the wrong place fails loudly. `ctx.emit()` from a tool or an event-stream handler raises `UserError`, because both run inside activities that cannot reach the run's event stream — which covers custom events from application tools and capability events from a capability's own tools. The route is to emit from capability hooks, which run in the workflow; emitting from activities is tracked in pydantic-ai#7971.[^pydantic-temporal-docs] Capability `@on_event` listeners run in workflow code rather than in a durable unit, so they re-run on every replay and must be deterministic; I/O belongs in a durability `event_stream_handler=`, which runs in its own activity.[^pydantic-temporal-docs]

## Cancellation

Cancelling the streaming object does not cross the boundary: `AgentStream.cancel()` is unavailable across it. Stopping an in-flight model request means cancelling the Temporal workflow, whose cancellation reaches the activity through its heartbeats and cancels any server-side job before the activity completes.[^pydantic-temporal-docs]

Whole-run cancellation splits into four mechanisms with distinct consequences:[^pydantic-temporal-docs]

| Mechanism | Where it is called | Result |
| --- | --- | --- |
| `AgentRun.cancel()` | Workflow code | Raises `RunCancelled` as an ordinary application outcome: a caught one lets the workflow complete normally and stays replay-deterministic; an uncaught one fails the workflow as a typed application error, and the run state does not cross that boundary |
| `RunContext.cancel()` | Must be the run's own process | From a tool in an activity it raises a clear `UserError` instead of hanging |
| `CancellationToken`, created in workflow code and fired from a `@workflow.signal` handler | External actor signalling the workflow | Cancels the run first-party without cancelling the workflow; uncaught, the resulting `RunCancelled` fails the workflow as above |
| Cancelling the workflow itself | Temporal client or UI | Remains an external cancellation: `CancelledError` keeps propagating and the workflow ends *Cancelled* |

The token is the one with a replay hazard worth stating precisely. A signal handler runs on the workflow event loop and is recorded in history, so a token fired from one cancels the run at the same point on replay. Fired from anywhere else — another thread, an activity, code outside the workflow — while a run is using it, it raises `UserError` and leaves both the run and the token untouched, because that cancellation could not be replayed. Fired from elsewhere *before* any run has taken it, it cannot be detected: the run then starts already cancelled at a point history does not record, and the workflow will not replay.[^pydantic-temporal-docs] A cancelled token stays cancelled, so a workflow that runs an agent more than once — once per chat turn, say — must create a fresh token for each run. A signal arriving before the run starts cancels it as soon as it does, and the external actor fires it with `handle.signal(MyAgentWorkflow.cancel)`.[^pydantic-temporal-docs]

Catching `RunCancelled` inside the workflow is also what keeps `all_messages()` available, since the run state does not survive the failure boundary.[^pydantic-temporal-docs]

## Run timeouts

A run's `timeout=` works inside a workflow. Its deadline is computed from `workflow.now()` and enforced by a workflow timer, so a replayed workflow computes the same deadline and fires the same timer; when it fires, the in-flight activity is cancelled according to its `cancellation_type` and the run raises `RunTimedOut` in workflow code.[^pydantic-temporal-docs]

- Like `RunCancelled`, an uncaught `RunTimedOut` fails the workflow as a typed application error, so catching it is what preserves `all_messages()`.[^pydantic-temporal-docs]
- `RunContext.deadline` is serialized into activities, so an agent run by a tool inside an activity inherits the deadline too — and the deprecated `TemporalAgent` rejects `timeout=` outright.[^pydantic-temporal-docs]
- The deadline bounds the run, not the workflow. A workflow's `execution_timeout` would end it without recording the run's history, so it stays a backstop.[^pydantic-temporal-docs]

## Counting tokens before a request

With `count_tokens_before_request=True`, the provider is called in an `agent__{name}__model_count_tokens` activity ahead of each model request activity, configured like the model request activities.[^pydantic-temporal-docs] A model that cannot count raises `NotImplementedError`, and a request it cannot count raises `UserError` in workflow code without the activity being retried; any other error, a `UserError` subclass included, fails the activity as it would fail a model request. A history recorded by an earlier version, which counted in workflow code, replays unchanged because a `workflow.patched()` marker distinguishes the two.[^pydantic-temporal-docs]

## Suspended turns and background mode

Some providers pause a turn mid-flight (Anthropic `pause_turn`) or run it as a server-side job that is polled until ready (OpenAI background mode). Pydantic AI continues such a turn transparently: each segment runs in its own model request activity, the workflow checkpoints the suspended `ModelResponse` and its background job id between segments, the final response is merged and usage is recorded once, and a `message_history` ending in a suspended response resumes by passing that response to the first activity.[^pydantic-temporal-docs]

Operationally this changes what a timeout covers:[^pydantic-temporal-docs]

- **Activity timeouts are per provider round trip.** Size `start_to_close_timeout` and `heartbeat_timeout` for one round trip, not for the whole turn; model request activities default to a 30-second `heartbeat_timeout`.
- **`request_timeout` covers the whole turn**, runs as a workflow timer, and cancels the in-flight activity when it fires. Under the `ModelFallback` capability each model tried gets its own activity and workflow timer; under `FallbackModel` the deadlines run inside the activities and the picked model's deadline carries from segment to segment.
- **`first_event_timeout` always runs inside the activity**, because that is what sees the stream's events, and it carries over the same way until the turn produces output.
- **Retries and waits are per segment.** A failed segment retries independently, background poll delays use durable Temporal timers rather than activity wall-clock time, and batching behaves the same way — submission and each check are separate activities with durable timers between them.
- **Teardown is its own activity.** If an error abandons a suspended job, the provider teardown runs in a dedicated cancellation activity.

## Continue-as-new for long-running agents

A workflow's execution history is capped at roughly 50,000 events or 50MB, which a long enough agent run can reach. Temporal's answer is `continue_as_new`: finish the current execution and start a fresh one with a clean history, carrying forward the arguments supplied.[^pydantic-temporal-docs]

`TemporalDurability(continue_as_new=...)` takes a sync or async function receiving the run's `RunContext`, called just before each model request when `workflow.info().is_continue_as_new_suggested()` is true. Your function then calls `workflow.continue_as_new()` with whatever the workflow's `@workflow.run` method needs to resume — including the conversation so far — and at that point every tool result from the previous step is already in history with nothing in flight.[^pydantic-temporal-docs]

- The server decides when to suggest continuing, from history event count and size; `limit.historyCount.suggestContinueAsNew` and `limit.historySize.suggestContinueAsNew` dynamic-config values tune it per namespace.[^pydantic-temporal-docs]
- An async function can first execute an activity — storing history elsewhere and passing a reference, for example — or return without calling `continue_as_new()` at all to wait for a condition only the application can judge, in which case it is called again before the next model request. `None`, the default, disables the feature.[^pydantic-temporal-docs]
- The documented continuation passes `None` as the prompt, because the carried-over history already ends with the request the model was about to receive (the latest tool results), so the new run sends it as-is instead of appending a user message.[^pydantic-temporal-docs]
- Carrying `usage` and `usage_limits` across the boundary is what keeps limits such as `request_limit` bounding the whole logical run instead of resetting on each continuation. Those arguments are the application's ordinary workflow arguments, not a feature of the capability — the function and the `@workflow.run` signature are yours to shape.[^pydantic-temporal-docs]

### Reusing a Responses WebSocket across activities

An OpenAI Responses model can keep one WebSocket across model activities when the worker holds the registered model open: install `pydantic-ai-slim[openai-realtime]`, set `openai_transport='websocket'`, and enter the model around the worker's lifetime.[^pydantic-temporal-docs] Each activity still checkpoints its own result.

- Activities borrow the socket only on the event loop where an outer model context holds it; without that owner, or for a model created only inside an activity, requests use HTTP, and capacity overflow also falls back to HTTP.[^pydantic-temporal-docs]
- Set `max_retries=0` when Temporal owns the retry budget: it disables transport retries for WebSocket requests and for HTTP overflow, compaction and token counting.[^pydantic-temporal-docs]
- Connections are worker-local resources. A replacement worker uses its own model and connection and can resend the retained conversation, which is why the full message history should be kept — especially with `openai_store=False`. Replaying completed activities uses their recorded results without opening a connection.[^pydantic-temporal-docs]
- With instrumentation on, the model activity's span records `pydantic_ai.transport` as `'websocket'` or `'http'` within each request's `chat` span, which is the observable difference between the two paths.[^pydantic-temporal-docs]

## Coverage and limits

The sole artifact is the Pydantic documentation capture `index.md` (10,968 words as declared, 10,860 by local `wc -w`), inspected as text; there are no attachments, includes, downloads or supporting files.[^pydantic-temporal-docs]

- The page names no Pydantic AI or Temporal release version, author or publication date, so every API and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule.[^pydantic-temporal-docs]
- Every external link — Temporal's Workflow Streams, signals, continue-as-new, dynamic-configuration and activity-execution docs; the Pydantic AI API references for `AgentEventStream`, `TemporalDurability`, `UIAdapter` and `AgentStream`; and issue #7971 — was read as a link, not followed.[^pydantic-temporal-docs]
- Nothing was installed, no workflow streamed, reconnected or drained, no signal fired, no run cancelled or timed out, no suspended turn continued, no history rolled over to a new execution and no WebSocket opened, so every claim is **Reported**.[^pydantic-temporal-docs]
- Evidence class: **Reported**.

## Relationships

- **Specialises** [Pydantic AI on Temporal](pydantic-ai-temporal.md), which covers attachment, naming, payloads, activity configuration and retries; this page covers what happens while a long or streamed run is in flight.
- **Differs from** [Pydantic AI run controls](pydantic-ai-run-controls.md) and in-process streaming: the same `timeout=` and event APIs, with deadlines enforced by workflow timers and streams replayed rather than delivered as deltas.[^pydantic-temporal-docs]
- **Uses** [Pydantic AI conversation state](pydantic-ai-conversation-state.md) as the thing a UI protocol rebuilds from the request body, and derives a deterministic `conversation_id` when none is passed.[^pydantic-temporal-docs]
- **Defers to** [model fallback](pydantic-ai-model-fallback.md) for which model serves an attempt, since each fallback model gets its own activity and workflow timer under this engine.[^pydantic-temporal-docs]
- **Extends** [Pydantic AI durable execution](pydantic-ai-durable-execution.md): continue-as-new is the engine-specific answer to a run outliving its history budget.[^pydantic-temporal-docs]
- **Contrasted by** [E2B sandbox recovery](pydantic-ai-e2b-sandbox-recovery.md), the other worked Temporal recovery case in this wiki.[^pydantic-temporal-docs]

[^pydantic-temporal-docs]: Pydantic, "Durable Execution with Temporal" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/temporal/`), 10,968 words as declared, 10,860 by local `wc -w`, no version, date or author stated; local capture `raw/capabilities/durable_execution/temporal/index.md`, content digest sha256:d1d6bdec. §"Streaming" (lines 353–369) for the buffered iterators, the `PartStartEvent` delivery, the two handler paths, the per-run handler and `run_stream_sync`; §"Streaming events to a frontend with Workflow Streams" (370–430) for the topic setup, `AgentEventStream`, `stream_agent_events`, the terminal event, the acknowledgement and `drain_timeout`, unique workflow ids and continue-as-new; §"Driving a UI protocol" (431–508) for the adapter split, the `ChatWorkflow` and handler samples, the workflow-as-queue framing and the reattachment authorization warning; §"Reconnecting" (509–535) for `from_offset`, the resubscribe loop, `RPCError`, `events.result` and whole-stream offsets; §"Choosing what to publish" (536–563) for `PartDeltaEvent`, `WorkflowStreamTopic`, the always-published terminal event, `workflow_stream_event_handler`, the `ctx.emit()` restriction and `@on_event` replay determinism; §"Cancellation" (564–609) for `AgentStream.cancel`, the four cancellation mechanisms, the signal-handler replay rule and the reusable-token warning; §"Run Timeouts" (610–617); §"Counting Tokens Before a Request" (618–621); §"Suspended Turns and Background Mode" (622–632); §"Continuing as New for Long-Running Agents" (633–748) including the continuation sample and the Responses WebSocket reuse. Evidence class: **Reported** — vendor reference page naming no version; nothing was executed.
