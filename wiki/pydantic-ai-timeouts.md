---
type: Concept
title: Pydantic AI timeouts
description: Which timeout knob bounds which unit of work in a Pydantic AI run — the model attempt, the whole request, the wait for the first streamed event, a tool, a hook, an MCP connection, a realtime handshake and the whole run — and the error each one raises.
tags: [pydantic-ai, agents, reliability, timeouts]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:30:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-timeouts
    resource: ../raw/core-concepts/timeouts/index.md
    scope: ../raw/core-concepts/timeouts/
    kind: documentation
    revision: sha256:f05691956599cfeccf1de6aa3383a528e516d06310baf5db2d282edda7bd852f
    title: "Timeouts"
---

Bounding one step inside a run, bounding the whole run, and ending a run from inside a tool are three separate mechanisms in Pydantic AI with three separate failure modes, and the ten settings that do the bounding are enforced at four different layers: the provider client, the framework itself, `FunctionToolset`, and the process or workflow clock[^pydantic-docs-timeouts] The layer is what decides whether the setting works on a given model or toolset at all, so the map below is ordered by unit of work and annotated with the enforcing layer rather than by API surface[^pydantic-docs-timeouts]

## The ten knobs

| Unit bounded | Setting | Enforced by | On expiry |
| --- | --- | --- | --- |
| One model request **attempt** — a provider SDK's retries re-arm it per attempt, and on a streamed response it bounds the wait for each chunk, not the whole response | `timeout` on `ModelSettings` | The provider client, and only on model classes that forward the setting | `ModelTimeoutError`, a `ModelAPIError`; the run fails unless a `FallbackModel` or a transport retry handles it |
| A **whole model request** — every attempt the SDK and transport make, and reading a streamed response through its last chunk | `request_timeout` on `ModelSettings` | Pydantic AI, on every model | `ModelRequestTimeout`; the run fails unless a `FallbackModel` falls back on it |
| The **wait for a streamed response to start** — every attempt until its first output, but not the output after it | `first_event_timeout` on `ModelSettings` | Pydantic AI, on every model | `ModelRequestTimeout` with `setting='first_event_timeout'`; nothing has been streamed yet, so a `FallbackModel` or the `ModelFallback` capability falls back on it |
| A **function tool call** | `Agent(tool_timeout=...)` or `timeout=` on one tool | `FunctionToolset` only | The model receives a retried tool result `'Timed out after N seconds.'`, consuming that tool's retry budget; a `def` tool is not actually stopped |
| A **hook function** | `timeout=` on the `@hooks.on.*` decorator | The `Hooks` capability | `HookTimeoutError`, which is an `AgentRunError` and aborts the run; a `def` hook is not actually stopped either |
| **Connecting** to an MCP server — the connection and the `initialize` handshake | `MCPToolset(init_timeout=...)`, default `5` seconds | `MCPToolset` | The connection fails |
| A **single MCP request** | `MCPToolset(read_timeout=...)`, default `300` seconds | `MCPToolset` | The request fails; under the default `tool_error_behavior='retry'` the model sees it as a retryable tool error |
| **Opening a realtime session** | `handshake_timeout` on `RealtimeModelSettings`, default `30` seconds — OpenAI, Azure OpenAI, xAI and Gemini | The realtime model | `RealtimeError`; on a reconnect it consumes a `ReconnectPolicy` attempt instead |
| **Total work** done by a run — requests, tool calls, tokens or cost | `UsageLimits` | Pydantic AI | `UsageLimitExceeded`; this is not a wall-clock bound |
| **Wall-clock duration** of a whole run | `timeout=` on any run method | Pydantic AI, on the process or workflow clock | `RunTimedOut`, carrying everything the run completed |

The first three rows sit on one axis worth keeping straight: `timeout` is the start-to-close timeout of one attempt, and `request_timeout` is the schedule-to-close timeout of the request that attempt belongs to — Temporal's terms, used by the vendor for an in-process distinction[^pydantic-docs-timeouts]

## Where the setting does not apply

Four qualifications decide whether a knob is live at all[^pydantic-docs-timeouts]

- **`ModelSettings['timeout']` is per model class, not universal.** Only the classes listed under `ModelSettings.timeout` forward it to their provider client, and the ones built on OpenAI's inherit the forwarding from `OpenAIChatModel`/`OpenAIResponsesModel`. Other classes ignore it, warn with `UnsupportedSettingWarning`, and the HTTP client's own timeout applies instead. Where the class cannot take one, the provider may expose its own: `XaiProvider` takes a client-level `timeout` or a preconfigured `xai_client`, `BedrockProvider` takes `aws_read_timeout`/`aws_connect_timeout` or a preconfigured `bedrock_client`, and `HuggingFaceProvider` rejects `http_client` in favour of `hf_client`. Google and Mistral additionally reject an `httpx.Timeout` **object** and accept only a number of seconds.
- **A client Pydantic AI creates has its own deadlines.** By default a 600-second total timeout with a 5-second connect timeout, 20 minutes for Google's long decode. A request timeout given in seconds on such a client — including `create_async_httpx2_client()` and including the timeout `google-genai` sends with every Gemini request — can shorten but never lengthen the client's connect timeout (5 seconds) or its pool timeout (600 seconds, 20 minutes for Google). A longer connect means passing an `httpx.Timeout` whose `connect` differs from its other phases, or your own `http_client`.
- **`request_timeout` and `first_event_timeout` are enforced by Pydantic AI on every model.** They are never sent to the provider, so they behave the same everywhere, including on the classes that ignore `timeout`.
- **Tool timeouts are per `FunctionToolset`.** `Agent(tool_timeout=...)` sets the default only for tools registered on the agent; it does not reach a `FunctionToolset` you constructed and passed via `toolsets=[...]`, which needs its own `FunctionToolset(timeout=...)`. Tools from an MCP server, an external toolset, or a custom `AbstractToolset` read neither setting and must be bounded at the server or transport level instead.

## A deadline you enforce yourself

A deadline enforced inside a tool body should be caught and re-raised as `ModelRetry` or `ToolFailed` rather than allowed to escape, because what a bare `TimeoutError` does depends on whether that tool has a timeout of its own[^pydantic-docs-timeouts]

| Tool's own timeout | Effect of a bare `TimeoutError` |
| --- | --- |
| None on the tool or its toolset | An ordinary exception that propagates out of the run, unless a capability implementing `on_tool_execute_error` turns it into a replacement tool result or a `ModelRetry` |
| Configured | The call runs inside `anyio.fail_after(timeout)`, which signals expiry with `TimeoutError` too, so your own `TimeoutError` is indistinguishable from the deadline expiring and becomes the same `'Timed out after N seconds.'` retried result — reporting a deadline that may never have passed |

Re-raising in the tool is the local choice; a hook is the way to apply one policy across every tool[^pydantic-docs-timeouts]

## The whole-request deadline

`request_timeout` is one clock over the whole request to one model: every attempt the provider SDK and the HTTP transport make, the backoff between them, any continuation of a response the provider paused, and reading a streamed response through its last chunk[^pydantic-docs-timeouts] When it passes, the request is cancelled and `ModelRequestTimeout` is raised; being a `ModelAPIError`, an `on_model_request_error` hook can recover from it on a non-streamed request[^pydantic-docs-timeouts] A single attempt's timeout, controlled by `timeout`, is a different error and is never reported as `ModelRequestTimeout`[^pydantic-docs-timeouts]

The consequences that are easy to get wrong[^pydantic-docs-timeouts]:

- **Streaming.** The deadline is fixed when the request is made and covers reading the stream to its last chunk, so the time your consumer takes counts towards it: a consumer still reading when it passes gets `ModelRequestTimeout` from the stream, and what has been streamed is kept in history as an `'interrupted'` response. Once the last chunk is read, the deadline no longer applies. The streaming `run()` does behind the scenes — with an event stream handler, for example — is included.
- **Fallback.** `ModelFallback` and `FallbackModel` give each model they try a fresh deadline, and the default `fallback_on` moves on when one runs out; each expired attempt is recorded in the response's `failed_attempts`. A paused response's continuation is still the same request and keeps its deadline, while a later run resuming the paused response from history starts a fresh one. A model's own `settings` can set a different `request_timeout`, applying only when neither the agent nor the run sets one. Once a streamed response has started, neither falls back any more, so running out while it is being read raises `ModelRequestTimeout`.
- **Durable execution.** On Temporal the deadline runs on the workflow's clock as a durable timer; when it passes, the model request activity is cancelled — ending its activity retries — and `ModelRequestTimeout` is raised in the workflow. With `ModelFallback`, each model tried is its own request in its own activity with its own deadline; a `FallbackModel` runs inside one activity with the deadlines it gives each model. Each segment of a paused response is a separate activity, and the picked model's deadline carries across segments as a wall-clock timestamp, so it still covers the whole continuation. On DBOS and Prefect a `FallbackModel`'s deadlines carry between steps the same way; otherwise the deadline runs on the process's clock around the model request step, and a workflow recovered after a crash starts a fresh one.
- **Run timeouts.** A run's `timeout=` bounds the request too, so both deadlines apply and the earlier one wins. If the run's passes first, the request is cancelled with the run and `RunTimedOut` is raised rather than `ModelRequestTimeout`, and no fallback happens.
- **Direct requests and batching.** `model_request()` and `model_request_stream()` apply the deadline too. Under `BatchModelRequests` it covers the whole wait, from queueing until the batch result arrives. The capture says `model_request_batch()` "refuses it" without naming which setting is refused, so that one detail is unrecorded here rather than guessed.

## The first-event deadline

`request_timeout` must be long enough for the longest healthy response, so it cannot also give up quickly on a provider that accepts a request and then takes far longer than usual to start answering; `first_event_timeout` bounds only that wait[^pydantic-docs-timeouts] The rules that make it usable[^pydantic-docs-timeouts]:

- **Only output counts.** A provider event carrying none — OpenAI's `response.created`, which acknowledges a Responses API request immediately — does not satisfy it.
- **It covers attempts, backoff and paused or background continuations**, until one of them produces output; a later run resuming a paused response from history starts a fresh deadline.
- **Streamed requests only.** A request is streamed whenever something consumes the run's events, such as `run_stream()` or an event stream handler. On a non-streamed request the first output arrives with the whole response, so the setting does nothing and `request_timeout` is the tool.
- **With `request_timeout`, both apply until the first event** and whichever passes first raises; after it, only `request_timeout` does.
- **Under fallback,** nothing has reached the consumer yet, so `FallbackModel` and `ModelFallback` fall back by default and give each model a fresh deadline. A model's own `settings` may set a different value, applying only when neither the agent nor the run sets one.
- **Under durable execution,** a streamed request runs inside a durable unit that consumes the stream, so the deadline is enforced inside it on the process's clock, and a `FallbackModel` runs inside it too, falling back there as usual. On Temporal, `ModelRequestTimeout` is in `non_retryable_model_errors` by default, so the activity is not retried and the `ModelFallback` capability — which falls back in workflow code — moves on straight away, or the request fails. On DBOS and Prefect it is retried according to the step's or task's retry policy, which does not retry by default. Each segment of a paused response is a separate unit, and the deadline carries over as a wall-clock timestamp until output has been produced.

The vendor's motivating case: a primary model that usually starts streaming within 2 seconds but takes 45 during a degradation, given 20 seconds to start with a 600-second `request_timeout` behind it, so a healthy but slow response is never cut off[^pydantic-docs-timeouts]

## Bounding a whole run

`timeout=` (in seconds) is accepted by `run()`, `run_sync()`, `run_stream()`, `run_stream_sync()`, `run_stream_events()` and `iter()`, and bounds everything the run does: every model request, tool call and hook, plus — for the streaming methods — the time spent consuming the stream[^pydantic-docs-timeouts] When it expires the run is cancelled as `CancellationToken` cancels it: the in-flight model request or stream is closed, running tool calls are cancelled, and `RunTimedOut` is raised carrying everything the run completed[^pydantic-docs-timeouts]

`all_messages()` includes the completed tool results and the partial response of an interrupted stream, so passing it as `message_history` resumes the work[^pydantic-docs-timeouts] Three properties follow from `RunTimedOut`'s type and from where the deadline lives[^pydantic-docs-timeouts]:

- **`RunTimedOut` subclasses `RunCancelled`** — so `except RunCancelled` catches every deliberate stop — and also `TimeoutError`, which `asyncio.timeout()` raises. Unlike `asyncio.timeout()` it needs no state recovered from the exception chain, and the deadline is visible inside the run.
- **The deadline is readable:** `RunContext.deadline` is the UTC time the run must finish by and `RunContext.remaining_time()` the seconds left, so a tool can size its own work or timeouts to fit.
- **A delegated run inherits it.** An agent run from a tool can make the deadline earlier with its own `timeout=` but never later; when the shared deadline passes the parent raises `RunTimedOut`, while a sub-agent's own shorter timeout fails just the delegate tool.
- **Running out of time is cancellation, not a model error,** so neither `ModelFallback` nor `FallbackModel` falls back on it; `request_timeout` is the way to give up on one slow request while the run continues.
- **It is an asyncio timer.** Under another async backend such as Trio, `timeout=` raises a `UserError` before the run starts.
- **The UI adapters take it too.** `run_stream()`, `run_stream_native()` and `dispatch_request()` on a UI adapter accept `timeout=`; the first and third report a timed-out run to the client the same way as a first-party cancellation and pass the `RunTimedOut` to their `on_cancel` callback, and `run_stream_native()` raises it.
- **Under durable execution the deadline is stored as wall-clock time,** so a replayed or recovered run keeps the deadline it started with; `TemporalDurability`, `DBOSDurability` and `PrefectDurability` handle this, and the deprecated wrapper agents reject `timeout=` outright.

## Ending a run from inside a tool

What a tool raises decides whether the run continues and what the model sees[^pydantic-docs-timeouts]

| Raise | Run continues? | The model sees |
| --- | --- | --- |
| `ModelRetry` | Yes | A retried tool result asking it to correct the call; consumes that tool's retry budget |
| `ToolFailed` | Yes | A failed tool result to adapt to; does not consume the retry budget |
| `ApprovalRequired` / `CallDeferred` | Ends the run with a `DeferredToolRequests` output, unless a `HandleDeferredToolCalls` handler resolves the call inline | Nothing yet |
| Any other exception | No — it propagates out of `agent.run()`, unless a capability implementing `on_tool_execute_error` returns a replacement result or raises `ModelRetry` | By default nothing |
| `RunContext.cancel()` (no exception) | No | The run ends with `RunCancelled` and the tool's return value is discarded |

Inside a realtime session two rows read differently, because a live conversation cannot wait for an out-of-band result: a deferral that would end a run with `DeferredToolRequests` instead answers the model with an explanation that the tool cannot complete during the session and keeps going, and an ordinary exception answers the model with a generic failure — never the exception's message — while still being raised to you[^pydantic-docs-timeouts]

No exception ends a run early with a *successful* output. To let a tool finish the run with a value, make that value the run's output through an output tool the model can call, or an output function[^pydantic-docs-timeouts]

## Limits

- The capture names **no Pydantic AI version, publication date, author or licence**, so this page is `draft` under the `pydantic-ai` domain rule with a `stale_after`, and every API name, default and error class here is version-unknown[^pydantic-docs-timeouts]
- Nothing was installed, constructed, timed out, cancelled, streamed or connected, so every claim is **Reported**. The evidence-class split between enforcement layers is **Synthesis** from the vendor's four qualifications.
- Named but not enumerated: the per-provider model-class list that forwards `timeout`, the settings each realtime provider honours, `ReconnectPolicy`'s attempt accounting, and which of the three batching settings `model_request_batch()` refuses.
- The sibling captures under `raw/core-concepts/` — `retries`, `hooks`, `persistence`, `direct`, `batch` and the rest — are separate sources; their concepts are linked rather than restated, and the durable-execution engine pages this page defers to were read as links only.

## Relationships

- **Elaborates** [run controls](pydantic-ai-run-controls.md), which introduced the run and request budgets at two scopes; this page adds the try-it-again semantics, the per-model-class caveats and the whole-run error type.
- **Bounds each attempt inside** [retry layers and multiplication](pydantic-ai-retry-layers.md): `timeout` is the per-attempt start-to-close deadline, and `request_timeout` is what bounds all of one request's `M × K` attempts, so the multiplication's worst-case wall clock is a `request_timeout` question, not a product.
- **Sizes** [provider SDK retries](pydantic-ai-provider-sdk-retries.md) and [transport retries](pydantic-ai-transport-retries.md): each of their attempts sits under the same `timeout`, and neither is visible to `request_timeout` except as elapsed time.
- **Is the deadline** [model fallback](pydantic-ai-model-fallback.md) falls back on — a fresh one per model, recorded in `failed_attempts` — and the one it cannot fall back on once a stream has started or when the failure is `RunTimedOut`.
- **Nests tool timeouts** under the run budget: [tool execution, retries and failures](pydantic-ai-tool-execution.md) owns the retried `'Timed out after N seconds.'` result and the `FunctionToolset` scope, while this page records that a `def` tool keeps running past its deadline and that a self-raised `TimeoutError` is indistinguishable from expiry.
- **Nests hook timeouts** under the same budget: [lifecycle hooks](pydantic-ai-lifecycle-hooks.md) owns `HookTimeoutError` and the per-hook `timeout=`, which aborts the run rather than retrying.
- **Reaches the MCP layer** at [MCP client](pydantic-ai-mcp-client.md): `init_timeout` (5 s) and `read_timeout` (300 s) are the only deadlines an MCP tool has, because `tool_timeout` never reaches a remote toolset.
- **Reaches realtime** at [realtime provider support and settings](pydantic-ai-realtime-provider-support.md): `handshake_timeout` (30 s) bounds opening a session and, on a reconnect, spends a `ReconnectPolicy` attempt instead of failing.
- **Changes under** [durable execution](pydantic-ai-durable-execution.md) and its engines: deadlines become durable timers or wall-clock payloads so a replay or recovery keeps the deadline the run started with, which [Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md) and [DBOS streaming and cancellation](pydantic-ai-dbos-streaming.md) record engine by engine.
- **Differs from** [model API errors](pydantic-ai-model-api-errors.md): a timeout is only one of eleven categories, and `ModelTimeoutError`/`ModelRequestTimeout` are the two that a deadline produces.
- **Ends runs the way** [deferred tools](pydantic-ai-deferred-tools.md) and [deferred tool approval](pydantic-ai-deferred-approvals.md) end them: `ApprovalRequired`/`CallDeferred` are in this page's tool table only as the exit from a run, with the resume machinery owned there.

[^pydantic-docs-timeouts]: Pydantic Docs, "Timeouts" (<https://pydantic.dev/docs/ai/core-concepts/timeouts/>, `domain: pydantic.dev`, `language: en`, 3,128 words as declared and 3,202 by local `wc -w`, 192 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/timeouts/index.md`, content digest sha256:f0569195. §"Bounding how long a step takes" (raw lines 13–43) for the ten-row unit/setting/on-expiry table, the Temporal start-to-close versus schedule-to-close comparison, the three qualifications including the per-model-class forwarding rule, the provider-specific `timeout` surfaces (`XaiProvider`, `BedrockProvider`, `HuggingFaceProvider`, Google and Mistral rejecting an `httpx.Timeout`), the created client's 600-second/5-second/20-minute defaults and the cannot-lengthen rule, and the `FunctionToolset`-only tool scope with its `FunctionToolset(timeout=...)` remedy; lines 36–43 for the `ModelRetry`/`ToolFailed` re-raise advice, the `on_tool_execute_error` recovery route and the `anyio.fail_after` indistinguishability; §"Model request deadlines" (45–83) for the per-attempt versus whole-request split, `ModelRequestTimeout` as a `ModelAPIError` with its `on_model_request_error` recovery, the per-attempt `ModelTimeoutError` distinction, and the streaming, fallback, durable-execution, run-timeout, direct-request and batching bullets including the per-segment wall-clock carry-over and the `model_request_batch()` refusal; the `first_event_timeout.py` sample (90–102) for the 20-second-start/600-second-request example and the `request_timeout.py` sample (49–68) for the 30-second-attempt/90-second-request pair; §"Waiting for the first event" (84–122) for the motivation, the `response.created` non-event, the streamed-only scope, the fallback and `request_timeout` interaction, and the Temporal `non_retryable_model_errors` and DBOS/Prefect retry-policy split; §"Bounding a whole run" (123–176) for the six run methods, the cancellation semantics, `all_messages()`, the `RunCancelled`/`TimeoutError` bases, `RunContext.deadline`/`remaining_time()`, delegation inheritance, the no-fallback rule, the Trio `UserError`, the UI adapters and the wall-clock durable storage, with the `run_timeout.py` sample (127–141) and the delegation sample (154–170); §"Ending a run from inside a tool" (177–192) for the five-row raise table, the realtime-session exceptions to its last two rows, `RunContext.cancel()` and the no-successful-early-output rule. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence; nothing was installed or executed.