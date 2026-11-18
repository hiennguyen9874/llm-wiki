---
type: Concept
title: Pydantic AI lifecycle hooks
description: The `Hooks` capability as Pydantic AI's interception surface — the ten hook families and their `AbstractCapability` methods, the wrap-before-operation-after lifecycle, message-persistence and model-attempt rules, deferral and validation ordering, error recovery, and the ModelRetry-versus-ToolFailed split with its retry-budget accounting.
tags: [pydantic-ai, hooks, agents, capabilities]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:38:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-hooks
    resource: ../raw/core-concepts/hooks/index.md
    scope: ../raw/core-concepts/hooks/
    kind: documentation
    revision: sha256:bc45fcc0a6078f730458fc42665a3fa45cfe9dab28cfb83db14f6a311c270f0e
    title: "Hooks"
  - id: pydantic-docs-timeouts
    resource: ../raw/core-concepts/timeouts/index.md
    scope: ../raw/core-concepts/timeouts/
    kind: documentation
    revision: sha256:f05691956599cfeccf1de6aa3383a528e516d06310baf5db2d282edda7bd852f
    title: "Timeouts"
---

Hooks are Pydantic AI's interception surface: the [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) capability, attached through `Agent(..., capabilities=[hooks])`, exposes one `before_`/`after_`/`wrap_`/`on_*_error` family per run stage, so logging, metrics, validation and retry policy can be added without subclassing an agent or a capability[^pydantic-docs-hooks] The same capability earns two other roles from this design: it is the *recommended* place for application-level concerns (logging, metrics, lightweight validation), while a reusable bundle that also ships tools, instructions or model settings is meant to subclass [`AbstractCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability) instead — the naming of the surface belongs to [the capability primitive](pydantic-ai-capability-primitive.md), and this page is the hook machinery underneath it[^pydantic-docs-hooks]

## The lifecycle every stage shares

Every stage — the run, each node, each model request, each tool call, each output — runs the same sequence[^pydantic-docs-hooks]:

```
wrap_* enter → before_* → operation (on_*_error if it fails) → after_* → wrap_* exit
```

A `wrap_*` hook that returns without calling its handler skips everything inside it, so a wrapper is either setup/teardown around the whole stage or a short-circuit that replaces it[^pydantic-docs-hooks] The shortcut has a security consequence the page states plainly: a short-circuiting wrapper also skips the policy hooks registered in `before_*`, so mandatory authorization belongs in an outer wrapper or outside any cache that can short-circuit[^pydantic-docs-hooks]

## Registering hooks

| Route | Shape | Note |
| --- | --- | --- |
| Decorator | `@hooks.on.before_model_request`, bare or parameterised as `@hooks.on.before_model_request(timeout=5.0)` | One method per lifecycle hook in the `hooks.on` namespace |
| Constructor | `Hooks(before_model_request=log_request)` | Same functions, passed as kwargs |
| Capability | `Hooks(id=..., description=..., defer_loading=True)` | Loaded on demand like any capability |

Multiple hooks may be registered for one event and fire in registration order[^pydantic-docs-hooks] Both sync and async functions are accepted, and sync functions run in a thread pool so a slow one does not stall the run[^pydantic-docs-hooks]

On-demand registration is the subtle case: hooks owned by a deferred `Hooks` instance are skipped until that capability is loaded, which makes it a fit for optional behaviour such as verbose request diagnostics rather than for anything a run depends on unconditionally[^pydantic-docs-hooks] The source names `requires_approval=True`, `ApprovalRequired` and `ApprovalRequiredToolset` as the routes for human-in-the-loop approval instead of a deferred hook[^pydantic-docs-hooks]

## The hook families

Each family maps a decorator name to a constructor kwarg to the `AbstractCapability` method a subclass would override — the third column is what makes a custom capability and a `Hooks` instance the same mechanism[^pydantic-docs-hooks]:

| Stage | `hooks.on.` names | `AbstractCapability` methods |
| --- | --- | --- |
| Run | `before_run`, `after_run`, `run`, `run_error` | `before_run`, `after_run`, `wrap_run`, `on_run_error` |
| Node | `before_node_run`, `after_node_run`, `node_run`, `node_run_error` | `before_node_run`, `after_node_run`, `wrap_node_run`, `on_node_run_error` |
| Model request | `before_model_request`, `prepare_model_request`, `after_model_request`, `model_request`, `model_request_error` | `before_model_request`, `prepare_model_request`, `after_model_request`, `wrap_model_request`, `on_model_request_error` |
| Tool validation | `before_tool_validate`, `after_tool_validate`, `tool_validate`, `tool_validate_error` | `before_tool_validate`, `after_tool_validate`, `wrap_tool_validate`, `on_tool_validate_error` |
| Tool execution | `before_tool_execute`, `after_tool_execute`, `tool_execute`, `tool_execute_error` | `before_tool_execute`, `after_tool_execute`, `wrap_tool_execute`, `on_tool_execute_error` |
| Output validation | `before_output_validate`, `after_output_validate`, `output_validate`, `output_validate_error` | `before_output_validate`, `after_output_validate`, `wrap_output_validate`, `on_output_validate_error` |
| Output processing | `before_output_process`, `after_output_process`, `output_process`, `output_process_error` | `before_output_process`, `after_output_process`, `wrap_output_process`, `on_output_process_error` |
| Tool preparation | `prepare_tools`, `prepare_output_tools` | `prepare_tools`, `prepare_output_tools` |
| Deferred calls | `deferred_tool_calls` | `handle_deferred_tool_calls` |
| Event stream | `run_event_stream`, `event` | `wrap_run_event_stream`; `event` has no capability method |

The wrap hooks drop the `wrap_` prefix in the decorator namespace: `hooks.on.model_request` is `wrap_model_request`, and `hooks.on.run` is `wrap_run`[^pydantic-docs-hooks]

Three families carry scope rules worth stating apart from the table[^pydantic-docs-hooks]:

- **Run hooks** are dispatched once per agent run. `wrap_run` encloses `before_run`, the graph iteration with `on_run_error` recovery, and `after_run`. A realtime session counts as one run, so the same four hooks fire once around it, with `wrap_run` recovery and `after_run` result transformation applied when the session closes — see [realtime voice](pydantic-ai-realtime-voice.md).
- **Node hooks** fire for each graph step (`UserPromptNode`, `ModelRequestNode`, `CallToolsNode`) regardless of how the run is driven: `agent.run()`, `agent_run.next()`, or `async for node in agent_iter`. The step machinery is [the graph builder](pydantic-ai-graph-builder.md)'s.
- **Output validation hooks** fire only when structured output is parsed against its schema; plain text and image output never reach them. Output *processing* hooks are the wider stage — extracting values, calling output functions, running output validators — covered by [structured output](pydantic-ai-structured-output.md).

## What a model-request hook may change

`ModelRequestContext` bundles `model`, `messages`, `model_settings` and `model_request_parameters`, and setting `request_context.model` to another `Model` instance swaps the model for that request[^pydantic-docs-hooks] The message rule is the part that bites, because two views exist and editing one is not editing the other:

- Mutating or assigning `request_context.messages` changes **only the current model request**.
- Mutating the `ctx.messages` list changes **persistent history** — what `all_messages()` returns and later requests see — but not the current request.
- To change both, update both explicitly.

[`ProcessHistory`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ProcessHistory) and compaction deliberately update both, preserving their history-rewriting contract, and because a history processor transforms the current request view and makes the whole result persistent, its position relative to other message hooks is significant[^pydantic-docs-hooks] That interaction is where hook order and [prompt caching](pydantic-ai-prompt-caching.md)'s prefix stability meet: a hook that rewrites `ctx.messages` mid-request invalidates the prefix the cache was built on.

`before_model_request` runs once per request **step**; `prepare_model_request` runs before every **attempt** at it, with `request_context.model` set to the model about to serve that attempt — which differs from the step's model when [fallback](pydantic-ai-model-fallback.md) or a hook moves the request by raising [`RetryModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.RetryModelRequest)[^pydantic-docs-hooks] Preparation that depends on the model therefore belongs in `prepare_model_request`, and policy that must run once belongs in `before_model_request`.

Raising [`SkipModelRequest(response)`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.SkipModelRequest) from `before_model_request` or `model_request` skips the call entirely[^pydantic-docs-hooks]

## Deferral needs validated arguments

The tool stage is split so that a deferral can only happen once the arguments are known good, and the split decides where a hook is allowed to raise[^pydantic-docs-hooks]:

| Hook | May raise `ApprovalRequired` / `CallDeferred`? | Why |
| --- | --- | --- |
| `before_tool_validate` | No — `UserError` | Arguments are not validated yet |
| `tool_validate` before `handler()` | No — `UserError` | Same |
| `tool_validate` after `handler()` returns | Yes | Validation has completed inside the wrapper |
| `after_tool_validate` | Yes | The documented gate for approval |
| `tool_validate_error` | No — `UserError` | Argument validation failed; the call is retried instead |
| `before_tool_execute`, `tool_execute` before `handler()` | Yes | The recommended place to defer at execution time |
| `after_tool_execute`, `tool_execute` after `handler()` | Accepted but useless | The tool already ran: side effects happened, result discarded |

An `args_validator` deferral is held until `after_tool_validate` has checked the validated arguments; a deferral raised by `tool_validate` after its handler returns happens after that gate has already run[^pydantic-docs-hooks] An [external tool](pydantic-ai-deferred-approvals.md) executes outside the run, so the run cannot approve it: raising `ApprovalRequired` while validating one is a `UserError`, and the route is `CallDeferred` with whatever `metadata` the executing code needs[^pydantic-docs-hooks]

The rewrite boundary is also explicit: whoever resolves the deferral sees the arguments **as the model sent them**, not as these hooks rewrote them. If they approve, the hooks run again and the tool executes with the rewritten arguments[^pydantic-docs-hooks] A reviewer therefore approves the call the model made, not the call the application will run — a gap worth naming whenever a hook sanitizes arguments before a human sees them.

## Preparation, validation and execution are separate stages

- **`prepare_tools` / `prepare_output_tools`** filter or modify the tool definitions the model sees on each step, and run as `PreparedToolset` wrappers: the result feeds both the model's request and `ToolManager.tools`, so filtering also blocks execution[^pydantic-docs-hooks] Function tools go through `prepare_tools`; output tools are handled separately by `prepare_output_tools`, which sees `ctx.max_retries` as the **output** retry budget[^pydantic-docs-hooks]
- **Execution hooks** receive `args` as the validated `dict[str, Any]`; raising `SkipToolExecution(result)` skips the function and supplies the result directly[^pydantic-docs-hooks]
- **`deferred_tool_calls`** resolves approval-required or externally-executed calls inline during a run: it receives `DeferredToolRequests` and returns `DeferredToolResults`, or `None` to decline[^pydantic-docs-hooks] Several registered hooks accumulate rather than override — each receives the still-unresolved requests and may resolve some or all — and the dedicated `HandleDeferredToolCalls` capability is the shorter form when a handler is the only thing wanted[^pydantic-docs-hooks]

## Observing events

Two hooks share the event stream but sit at different depths[^pydantic-docs-hooks]:

- **`run_event_stream`** (`wrap_run_event_stream`) wraps the full stream as an async generator — the only supported place to transform, replace or filter events, since returning a replacement event from `hooks.on.event` is deprecated.
- **`event`** observes individual events at the same dispatch point as capability `on_event` listeners; callbacks may be sync or async and return `None`. Passing an event class (`@hooks.on.event(PartStartEvent)`) filters it; bare sees the full `AgentStreamEvent` union.

Passing the class is not only about typing the parameter: the classes are what let dispatch skip a capability entirely for events it does not listen to, so a bare callback anywhere in the tree means every event is offered to everything[^pydantic-docs-hooks] An `event` callback belongs to the application rather than to a capability, which makes it the place to `enqueue`-triggered `EnqueuedMessagesEvent` handling, to emit a `CustomEvent` of your own, and to republish a capability's internal event; it also participates in immediately dispatched capability decision events, so application code can set decision fields before the emitter continues[^pydantic-docs-hooks]

`@agent.on_event` registers a listener straight on the agent with the same filtering, typing and `timeout=`, for the case where events are the only thing wanted[^pydantic-docs-hooks] Its placement rules matter: listeners join **after** the agent's own capabilities, and survive an overridden root capability, while a capability asking for `position='innermost'` keeps that position, so its listeners run after these; with nothing registered, the listener capability is never added to the run[^pydantic-docs-hooks] Because it dispatches **upstream** of `run_event_stream`, a listener sees each event as emitted rather than as finally delivered — a listener can see an event no consumer ever receives[^pydantic-docs-hooks] Only events can be registered this way: the other families are interceptors whose position relative to other capabilities is a decision, so they belong on a `Hooks` capability placed deliberately in `capabilities=[...]`[^pydantic-docs-hooks]

## Filtering and timeouts

Validation and execution tool hooks accept `tools=[...]` with tool names; the hook fires only for matching tools and every other call passes through[^pydantic-docs-hooks]

Every hook takes an optional `timeout` in seconds, set on the decorator or through the constructor kwarg. Exceeding it raises `HookTimeoutError`, which carries `hook_name` and `timeout`[^pydantic-docs-hooks] Two consequences are stated on the timeouts page rather than here[^pydantic-docs-timeouts]: `HookTimeoutError` is an `AgentRunError`, so it aborts the run rather than being retried or handed to the model, and a `def` hook is not actually stopped — like a `def` tool, its worker thread runs to completion after the deadline has fired.

## Ordering, and what `RunContext` holds when a hook fires

Within one `Hooks` instance, `before_*`, `after_*` and `on_*_error` fire in registration order, and registered `wrap_*` functions nest as middleware with the first registered outermost[^pydantic-docs-hooks] Across capabilities the composition rules apply: `before_*` in capability order, `after_*` and `on_*_error` in reverse capability order, `wrap_*` nesting with the first capability outermost[^pydantic-docs-hooks] The families do not interleave capability by capability — **all wrappers are entered before any `before_*` hook runs**, so even the innermost capability's wrapper precedes the outermost capability's `before_*`[^pydantic-docs-hooks]

Timing changes what `RunContext` can answer[^pydantic-docs-hooks]:

- Early run and node hooks can fire before the step's tool manager and model request parameters are assembled; `ctx.available_tool_names` may still list tool-search discoveries reconstructed from history, while `ctx.tools` and the request parameters are empty or hold the previous step.
- `before_model_request` and later model-request hooks see the request about to be sent — current function tools, native tools, model settings included.
- Tool and output hooks see the state for the call or output being processed.

For on-demand capabilities, `ctx.loaded_capability_ids` is derived from message history **before each model request**, so a capability loaded during a step appears from the *next* step onwards — the same step that first carries its instructions to the model, and therefore the first on which its tools can be called[^pydantic-docs-hooks] The source's own conclusion is that a hook looking for a capability in the very turn it was loaded will not find it; the wider consequence, read here rather than stated there, is that an on-demand hook cannot police the step it was activated by, because activation and visibility land one step apart — **Synthesis**.

## Error hooks recover inside the wrapper

Error hooks (`*_error`, or `on_*_error` on a capability) are raise-to-propagate, return-to-recover[^pydantic-docs-hooks]:

| The hook does | Effect |
| --- | --- |
| Raises the original error | Propagates unchanged (the default) |
| Raises a different exception | Transforms the error |
| Returns a result | Suppresses the error |

They run inside the wrapped handler, so recovery happens before control returns through the `wrap_*` chain: wrappers see the recovered result and only unrecovered failures travel outward[^pydantic-docs-hooks] Exceptions raised by `before_*`, `after_*` or `wrap_*` are outside the corresponding error hook's scope[^pydantic-docs-hooks]

## Retry or failure: `ModelRetry` versus `ToolFailed`

Both exceptions are available from hooks, and they mean opposite things[^pydantic-docs-hooks]:

- `ModelRetry` always means "ask the model again", with the given message. To abort a run from a hook, raise anything else and it propagates to the caller.
- `ToolFailed` reports a failed tool result **without consuming the tool's retry budget** — the same model-visible outcome as raising it from the tool function, useful when an error hook converts a third-party exception into a failure the model should adapt to.

What `ModelRetry` does depends on where it is raised[^pydantic-docs-hooks]:

| Raised from | Persisted response | Budget charged |
| --- | --- | --- |
| `before_model_request` | None, since the model was not called; the next request adds the retry message and `before_model_request` runs again | Output side |
| `after_model_request` | The original response, so the model can see what it said | Output side |
| `model_request` (wrap) | The response only if the handler was called | Output side |
| Tool validation or execution hooks | Converted to a retried tool result, as from the tool function | That tool's `max_retries` |
| Output validation or processing hooks | Converted to a retry, as from an output function | Tool `max_retries` for tool output; the output side for text output |

The retry message reaches the model as a `RetryFeedbackPart` in Pydantic AI's own voice rather than the user's[^pydantic-docs-hooks] Streaming adds a trap: `run_stream()` cannot retry a response it has already streamed as final output, so a `ModelRetry` rejecting it raises `UnexpectedModelBehavior` when the `async with` block exits, while `run_stream_events()` and `iter()` retry it[^pydantic-docs-hooks] Streaming detail lives in [streamed output](pydantic-ai-streamed-output.md).

Control-flow exceptions do not pass through every error hook[^pydantic-docs-hooks]:

- `ModelRetry` from a `before_*`, `after_*` or `wrap_*` hook bypasses the stage's `on_*_error` hook entirely. From a core operation it reaches `on_tool_validate_error` and `on_output_validate_error`, but bypasses `on_model_request_error`, `on_tool_execute_error` and `on_output_process_error`.
- `ToolFailed` bypasses the tool validation and execution error hooks. From the core model call or core output processing it is an ordinary exception for `on_model_request_error` or `on_output_process_error`; from a `before_*`, `after_*` or `wrap_*` hook it is outside the corresponding error hook's scope.

The semantic rule the source draws is transient versus definitive: raise `ModelRetry` where the same call might succeed if tried again, and `ToolFailed` where retrying will not help and the model should see the outcome and adapt[^pydantic-docs-hooks] Its worked example puts the distinction in one `tool_execute_error` hook keyed on an upstream status code — `5xx` or `429` become `ModelRetry`, `404` or `403` become `ToolFailed`, anything else is re-raised so it aborts the run — which it calls the per-error analogue of the MCP client's `tool_error_behavior` setting[^pydantic-docs-hooks] A `ToolFailed` result reaches the model as a `ToolReturnPart` with `outcome='failed'`[^pydantic-docs-hooks] The general error taxonomy those codes map onto is [model API errors](pydantic-ai-model-api-errors.md).

## When to use `Hooks` versus `AbstractCapability`

| `Hooks` | `AbstractCapability` |
| --- | --- |
| Application-level hooks (logging, metrics) | Reusable, packaged capabilities |
| Quick one-off interceptors | Combined tools + hooks + instructions + settings |
| No configuration state needed | Complex per-run state management |
| Single-file scripts | Multi-agent shared behaviour |

This is the source's own table, and it is the practical companion to the capability primitive's account of what a capability bundles[^pydantic-docs-hooks]

## Limits

- The capture names **no Pydantic AI version**, date or author, so no API name here can be tied to a release; under the `pydantic-ai` domain rule the page is therefore `draft` rather than `stable`[^pydantic-docs-hooks]
- One version anchor is available indirectly: [the v2 release page](pydantic-ai-v2-release.md) records v2.54.0 as the release where `wrap_*` hooks began enclosing full stage lifecycles, which is the semantics described here — but the source itself does not say so.
- The hook tables are documentation prose, not a signature reference; parameter types, `ValidatedToolArgs`'s full surface, the `Handler` protocols (`WrapModelRequestHandler` and its siblings for each stage) and the `PreparedToolset` contract are shown only where an example touches them.
- The event documentation is a list of examples rather than a schema: which events carry which payload beyond `PartStartEvent`, `FunctionToolCallEvent`, `EnqueuedMessagesEvent`, `CustomEvent` and `RealtimeSessionEvent`, and where each `decision` field lives, is not enumerated.
- Not stated: the cost of a hook layer on hot paths (a per-token event filter, a wrap hook on every tool call), how a `HookTimeoutError` interacts with [durable execution](pydantic-ai-durable-execution.md) replay, whether timing out a `defer_loading=True` capability's hook leaves it half-loaded, and what happens when two capabilities both short-circuit the same stage.
- No agent, hook, capability or tool was constructed and no event stream consumed in this ingest, so every behaviour above is **Reported** from vendor documentation; nothing is **Observed** or **Reproduced**.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md): `Hooks` is itself a core capability, and capability ordering is what decides cross-capability `before_`/`after_`/`wrap_` nesting.
- **Is deferred by** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md): a `Hooks` instance with `defer_loading=True` contributes no hook until its capability is loaded, and a load made from `after_tool_execute` is the durable-execution workaround when a tool's own function cannot load.
- **Is the alternative to** subclassing `AbstractCapability` for application-level concerns, per the source's own selection table; the subclass side — configuration methods, `for_agent`/`for_run`, ordering constraints and durable operations — is [custom capabilities](pydantic-ai-custom-capabilities.md), whose hook signatures are these same methods.
- **Carries content that** [capability parts and authority](pydantic-ai-capability-parts-and-authority.md) renders: a part a hook enqueues is stored typed and rendered only on the way to the model, with its voice decided by its source and the capability's `authority` ceiling.
- **Wraps models per attempt through** `get_wrapper_model`, timings and the batch caveat in [capability model control](pydantic-ai-capability-model-control.md).
- **Gates** [deferred tool approval](pydantic-ai-deferred-approvals.md): `ApprovalRequired`/`CallDeferred` are only legal from the post-validation hooks, and a deferral presents the model's original arguments while the approved call re-runs the hooks and executes the rewritten ones.
- **Charges** the retry budgets described in [run controls](pydantic-ai-run-controls.md) — the output side for model and text-output `ModelRetry`, a tool's `max_retries` for tool hooks and `prepare_output_tools`.
- **Distinguishes** the error categories catalogued in [model API errors](pydantic-ai-model-api-errors.md) into transient `ModelRetry` and definitive `ToolFailed`.
- **Is bounded by** [Pydantic AI timeouts](pydantic-ai-timeouts.md), which owns the per-unit timeout map: a hook's `timeout=` is one row of it, and it is the only hook deadline a run has — the run's own `timeout=` bounds the hook from outside instead.
- **Shares its dispatch point with** [observability](pydantic-ai-observability.md): an `event` callback or `@agent.on_event` listener sees events as emitted, upstream of any `run_event_stream` transformation, which is what makes trace and metric instrumentation hook-based.
- **Pairs with** [capability events](pydantic-ai-capability-events.md) on the emitting side: a capability publishes a typed `CapabilityEvent` with `ctx.emit()`, and `@on_event` or `Hooks.on.event` reacts to it, with the same class-filtered dispatch and the `dispatch='immediate'` decision mode.
- **Interacts with** [prompt caching](pydantic-ai-prompt-caching.md) through history rewrites: a hook that mutates `ctx.messages` changes the persistent prefix the next request's cache is measured against.
- **Drains queued messages** in [mid-run injection](pydantic-ai-mid-run-injection.md): `'asap'` content is drained in `before_model_request` once ahead of the other capability hooks and once after them, so content a hook enqueues there lands in the request being prepared, while `'when_idle'` content is drained at the end of the run after every `after_node_run`.
- **Must stay deterministic inside** [durable execution](pydantic-ai-durable-execution.md): hooks that run in workflow code re-run on replay, and the `ctx.emit()` restriction applies to them.
- **Composes with** [structured output](pydantic-ai-structured-output.md), whose validation and processing stages are the output hook families, and with [streamed output](pydantic-ai-streamed-output.md), where a `ModelRetry` on already-streamed final output raises instead of retrying.
- **Applies once per** [realtime voice](pydantic-ai-realtime-voice.md) session, because a session is a run: `before_run`, `after_run`, `wrap_run` and `on_run_error` fire once around the whole call, while tool hooks still fire per tool call.
- **Is ordered against by** [Harness background tools](pydantic-ai-harness-background-tools.md): a tool hook's capability position relative to `BackgroundTools` decides whether it runs inside the background task with the real result or outside it with the started message, and tool result events see the start.

[^pydantic-docs-hooks]: Pydantic Docs, "Hooks" (https://pydantic.dev/docs/ai/core-concepts/hooks/; 3,758 words as declared, 4,049 by local `wc -w` including frontmatter and markup; no publication date, author or version stated), §"Hook lifecycle" (lines 15–24) for the wrap → before → operation → after sequence and the skip semantics; §"Quick start" (25–48) for the `Hooks()`-with-decorators form and the `capabilities=[hooks]` attachment; §"Registering hooks" (49–122) for decorator registration, constructor kwargs, the thread-pool note for sync hooks, registration-order delivery, and the `defer_loading=True` on-demand route with the `requires_approval`/`ApprovalRequired`/`ApprovalRequiredToolset` alternatives; §"Hook types" (123–351) for the four-hook shape of each family, the second column of `AbstractCapability` methods, the dropped `wrap_` prefix, the run/node/output-validation scope rules, `ModelRequestContext`'s four fields and the model swap, the two message views and their persistence rules, `ProcessHistory` and compaction updating both, the `before_model_request`-per-step versus `prepare_model_request`-per-attempt split with `RetryModelRequest`, `SkipModelRequest`, the validation/execution deferral table with `args_validator` and external-tool rules, the reviewer-sees-original-arguments rule, `SkipToolValidation` and `SkipToolExecution`, `PreparedToolset` and `prepare_output_tools`'s output retry budget, the accumulating `deferred_tool_calls` hook and `HandleDeferredToolCalls`, and `run_event_stream` versus `event` with filtering, `CustomEvent` emission, decision-field participation and the deprecated replacement return; §"Listening without a Hooks capability" (327–351) for `@agent.on_event`, listener placement after the owner's capabilities, the never-added listener capability, upstream dispatch and the events-only restriction; §"Tool hook filtering" (352–389) for the `tools=` parameter; §"Timeouts" (390–420) for `HookTimeoutError` and its `hook_name`/`timeout`; §"Wrap hooks" (421–453) for the outermost-layer semantics and the skipped-policy-hooks warning; §"Hook ordering" (454–465) for within-instance registration order, cross-capability composition and the wrappers-before-`before_*` rule, plus `RunContext` population timing and the `loaded_capability_ids` one-step lag; §"Error hooks" (466–477) for raise-to-propagate, return-to-recover, transformation, and the recovery-before-wrapper ordering; §"Triggering retries with ModelRetry and failures with ToolFailed" (478–598) for `RetryFeedbackPart`, the per-stage persistence and budget table, the `run_stream()`/`UnexpectedModelBehavior` limitation, the control-flow bypass list, the transient-versus-definitive rule, the `tool_execute_error` status-code example, the MCP `tool_error_behavior` analogy and `outcome='failed'`; §"When to use Hooks vs AbstractCapability" (599–606) for the selection table. Local capture: `raw/core-concepts/hooks/index.md`, content digest sha256:bc45fcc0. Evidence class: **Reported** — vendor documentation naming no release version; no hook, capability or agent was constructed and no event stream was consumed.

[^pydantic-docs-timeouts]: Pydantic Docs, "Timeouts" (<https://pydantic.dev/docs/ai/core-concepts/timeouts/>; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/timeouts/index.md`, content digest sha256:f0569195. §"Bounding how long a step takes" (raw lines 15–27) for the hook row — `timeout=` on the `@hooks.on.*` decorator, `HookTimeoutError` classified as an `AgentRunError` that aborts the run, and the `def` hook whose worker thread is not actually stopped. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
