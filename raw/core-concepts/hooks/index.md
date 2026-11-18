---
title: "Hooks"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/hooks/"
domain: "pydantic.dev"
language: "en"
description: "Add lifecycle hooks to a Pydantic AI agent to log, modify, retry or skip model requests, tool calls, output and stream events, without subclassing."
word_count: 3758
---

Hooks let you intercept and modify agent behavior at every stage of a run — model requests, tool calls, streaming events — using simple decorators or constructor arguments. No subclassing needed.

The [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) capability is the recommended way to add [lifecycle hooks](https://pydantic.dev/docs/ai/capabilities/custom/#hooking-into-the-lifecycle) for application-level concerns like logging, metrics, and lightweight validation. For reusable capabilities that combine hooks with tools, instructions, or model settings, subclass [`AbstractCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability) instead — see [Building custom capabilities](https://pydantic.dev/docs/ai/capabilities/custom/).

## Hook lifecycle

Every stage of a run (the run itself, each node, model request, tool call, and output) has the same hook lifecycle:

```
wrap_* enter → before_* → operation (on_*_error if it fails) → after_* → wrap_* exit
```

A `wrap_*` hook that returns without calling its handler skips everything inside it. [`run_stream()` handles node hooks differently](#node-hooks), and [Hook ordering](#hook-ordering) covers how several hooks and capabilities combine.

## Quick start

Create a [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) instance, register hooks via `@hooks.on.*` decorators, and pass it to your agent:

hooks\_decorator.py

```python
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()

@hooks.on.before_model_request
async def log_request(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    print(f'Sending {len(request_context.messages)} messages to the model')
    #> Sending 1 messages to the model
    return request_context

agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello!')
print(result.output)
#> success (no tool calls)
```

## Registering hooks

### Decorator registration

The `hooks.on` namespace provides decorator methods for every lifecycle hook. Use them as bare decorators or with parameters:

```python
# Bare decorator
@hooks.on.before_model_request
async def my_hook(ctx, request_context):
    return request_context

# With parameters (timeout, tool filter)
@hooks.on.before_model_request(timeout=5.0)
async def my_timed_hook(ctx, request_context):
    return request_context
```

Multiple hooks can be registered for the same event — they fire in registration order.

### Constructor kwargs

You can also pass hook functions directly to the [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) constructor:

hooks\_constructor.py

```python
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks

async def log_request(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    print(f'Sending {len(request_context.messages)} messages to the model')
    #> Sending 1 messages to the model
    return request_context

agent = Agent('test', capabilities=[Hooks(before_model_request=log_request)])
result = agent.run_sync('Hello!')
print(result.output)
#> success (no tool calls)
```

Both sync and async hook functions are accepted. Sync functions are run in a thread pool, so a slow one won’t hold up the rest of the run.

### On-demand hooks

[`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) is a capability, so it can be loaded on demand just like any other capability. This is useful for optional, user-requested behavior such as verbose request logging:

deferred\_hooks\_capability.py

```python
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks

request_logging_hooks = Hooks(
    id='request-logging',
    description='Use when the user asks for verbose request diagnostics.',
    defer_loading=True,
)

@request_logging_hooks.on.before_model_request
async def log_request(
    ctx: RunContext,
    request_context: ModelRequestContext,
) -> ModelRequestContext:
    print(f'Model request at step {ctx.run_step}: {len(request_context.messages)} messages')
    return request_context

agent = Agent('openai-responses:gpt-6.1-sol', capabilities=[request_logging_hooks])
```

Pydantic AI skips hooks owned by a deferred `Hooks` instance until its capability is loaded.

Use on-demand hooks for optional behavior that only applies after the capability is loaded. For human-in-the-loop tool approval, pass [`requires_approval=True`](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) when registering a tool, raise [`ApprovalRequired`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ApprovalRequired) for conditional approval, or wrap a toolset with [`ApprovalRequiredToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.ApprovalRequiredToolset).

## Hook types

### Run hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_run` | `before_run=` | `before_run` |
| `after_run` | `after_run=` | `after_run` |
| `run` | `run=` | `wrap_run` |
| `run_error` | `run_error=` | `on_run_error` |

The run lifecycle is dispatched once per agent run. `wrap_run` (registered via `hooks.on.run`) runs once and encloses `before_run`, graph iteration with `on_run_error` recovery, and `after_run`; a wrapper that does not call its handler skips those inner hooks.

A [realtime session](https://pydantic.dev/docs/ai/realtime/capabilities/) is a run: the same four hooks fire once around the session, with `wrap_run` recovery and `after_run` result transformation applied when the session closes.

### Node hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_node_run` | `before_node_run=` | `before_node_run` |
| `after_node_run` | `after_node_run=` | `after_node_run` |
| `node_run` | `node_run=` | `wrap_node_run` |
| `node_run_error` | `node_run_error=` | `on_node_run_error` |

Node hooks fire for each graph step ([`UserPromptNode`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.UserPromptNode), [`ModelRequestNode`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.ModelRequestNode), [`CallToolsNode`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.CallToolsNode)).

Node hooks fire no matter how the run is driven: [`agent.run()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`agent_run.next()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRun.next), and `async for node in agent_run:` over [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter) all advance the run the same way.

### Model request hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_model_request` | `before_model_request=` | `before_model_request` |
| `prepare_model_request` | `prepare_model_request=` | `prepare_model_request` |
| `after_model_request` | `after_model_request=` | `after_model_request` |
| `model_request` | `model_request=` | `wrap_model_request` |
| `model_request_error` | `model_request_error=` | `on_model_request_error` |

Model request hooks fire around each model request step, which usually makes one LLM call, and more when a hook asks for another attempt. [`ModelRequestContext`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.ModelRequestContext) bundles `model`, `messages`, `model_settings`, and `model_request_parameters`. To swap the model for a given request, set `request_context.model` to a different [`Model`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model) instance.

`before_model_request` and `model_request` (wrap) use the same message-persistence rules. Each receives two top-level views of the messages:

- Mutating or assigning `request_context.messages` changes only the current model request (except for the deprecated appends below).
- Mutating the `ctx.messages` list changes persistent history returned by `all_messages()` and used by later requests, but not the current model request.
- To change both, update both explicitly.

[`ProcessHistory`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ProcessHistory) and compaction deliberately update both, preserving their existing history-rewriting contract. Because a history processor transforms the current request view and makes its whole result persistent, its position relative to other message hooks remains significant.

To skip the model call entirely, raise [`SkipModelRequest(response)`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.SkipModelRequest) from `before_model_request` or `model_request` (wrap).

`before_model_request` runs once per request step. `prepare_model_request` runs before every *attempt* at the request, with `request_context.model` set to the model about to serve it, which differs from the step’s model when a hook moves the request to another model by raising [`RetryModelRequest`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.RetryModelRequest). Use it for preparation that depends on the model; see [Retrying and falling back](https://pydantic.dev/docs/ai/capabilities/custom/#model-request-attempts).

### Tool validation hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_tool_validate` | `before_tool_validate=` | `before_tool_validate` |
| `after_tool_validate` | `after_tool_validate=` | `after_tool_validate` |
| `tool_validate` | `tool_validate=` | `wrap_tool_validate` |
| `tool_validate_error` | `tool_validate_error=` | `on_tool_validate_error` |

Validation hooks fire when the model’s JSON arguments are parsed and validated. All tool hooks receive `call` ([`ToolCallPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolCallPart)) and `tool_def` ([`ToolDefinition`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition)) parameters.

To skip validation, raise [`SkipToolValidation(args)`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.SkipToolValidation) from `before_tool_validate` or `tool_validate` (wrap).

A tool call can only be [deferred](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) once its arguments have been validated, so a call with invalid arguments is retried instead of reaching whoever resolves the deferral. So [`ApprovalRequired`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ApprovalRequired) and [`CallDeferred`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.CallDeferred) can be raised from `after_tool_validate` (and from `tool_validate` after its `handler()` has returned), but raising them from `before_tool_validate`, from `tool_validate` before it calls `handler()`, or from `tool_validate_error` is a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). A deferral from a tool’s [`args_validator`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#args-validator) is held until `after_tool_validate` has checked the validated arguments; a deferral raised by `tool_validate` after its handler returns happens after that gate has already run.

An [external tool](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#external-tool-execution) is executed outside the run, which therefore can’t approve its calls, so raising `ApprovalRequired` while validating one is a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). Raise `CallDeferred` instead, with any `metadata` the code that executes the call needs to approve it.

Whoever resolves the deferral is shown the arguments as the model sent them, not as these hooks rewrote them. If they approve the call, the hooks run again and the tool runs with the rewritten arguments. [Human-in-the-Loop Tool Approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) shows where to change arguments instead.

### Tool execution hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_tool_execute` | `before_tool_execute=` | `before_tool_execute` |
| `after_tool_execute` | `after_tool_execute=` | `after_tool_execute` |
| `tool_execute` | `tool_execute=` | `wrap_tool_execute` |
| `tool_execute_error` | `tool_execute_error=` | `on_tool_execute_error` |

Execution hooks fire when the tool function runs. `args` is always the validated `dict[str, Any]`.

To skip execution, raise [`SkipToolExecution(result)`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.SkipToolExecution) from `before_tool_execute` or `tool_execute` (wrap).

Every execution hook can [defer](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) the call — the arguments are validated by this point — but raise `ApprovalRequired`/`CallDeferred` from `before_tool_execute` (or from `tool_execute` before it calls `handler()`). A deferral from `after_tool_execute`, or from `tool_execute` after `handler()` has returned, is accepted but happens too late to be useful: the tool function already ran, so its side effects happened and its result is discarded.

### Output validation hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_output_validate` | `before_output_validate=` | `before_output_validate` |
| `after_output_validate` | `after_output_validate=` | `after_output_validate` |
| `output_validate` | `output_validate=` | `wrap_output_validate` |
| `output_validate_error` | `output_validate_error=` | `on_output_validate_error` |

Output validation hooks fire when structured output is parsed against the output schema. They do **not** fire for plain text or image output. All output hooks receive an `output_context` ([`OutputContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.OutputContext)) parameter.

### Output processing hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `before_output_process` | `before_output_process=` | `before_output_process` |
| `after_output_process` | `after_output_process=` | `after_output_process` |
| `output_process` | `output_process=` | `wrap_output_process` |
| `output_process_error` | `output_process_error=` | `on_output_process_error` |

Output processing hooks fire when the output is processed — extracting values, calling output functions, and running output validators.

See [Output hooks](https://pydantic.dev/docs/ai/capabilities/custom/#output-hooks) for the full lifecycle, signatures, and details on how output validators interact with processing hooks.

### Tool preparation

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `prepare_tools` | `prepare_tools=` | `prepare_tools` |
| `prepare_output_tools` | `prepare_output_tools=` | `prepare_output_tools` |

Filters or modifies tool definitions the model sees on each step.

`prepare_tools` handles **function** tools; `prepare_output_tools` handles [output tools](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.ToolOutput) separately, with `ctx.max_retries` reflecting the **output** retry budget. Both run as `PreparedToolset` wrappers — the result flows into the model’s request *and* `ToolManager.tools`, so filtering also blocks tool execution.

### Deferred tool call hook

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `deferred_tool_calls` | `deferred_tool_calls=` | `handle_deferred_tool_calls` |

Resolves [deferred tool calls](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) (approval-required or externally-executed) inline during a run. The hook receives a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) and returns a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) (or `None` to decline). Multiple registered hooks accumulate: each receives the still-unresolved requests and can resolve some or all of them.

hooks\_deferred\_tool\_calls.py

```python
from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()

@hooks.on.deferred_tool_calls
async def auto_approve(
    ctx: RunContext, *, requests: DeferredToolRequests
) -> DeferredToolResults:
    return requests.build_results(approve_all=True)

agent = Agent('test', capabilities=[hooks])

@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'
```

For pure application-level handler registration without other hooks, the dedicated [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HandleDeferredToolCalls) capability is more concise — see [Resolving deferred calls with a handler](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#resolving-deferred-calls-with-a-handler).

### Event stream hooks

| `hooks.on.` | Constructor kwarg | `AbstractCapability` method |
| --- | --- | --- |
| `run_event_stream` | `run_event_stream=` | `wrap_run_event_stream` |
| `event` | `event=` | *(per-event convenience)* |

`run_event_stream` wraps the full event stream as an async generator. `event` observes individual events at the same dispatch point as capability [`on_event`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.on_event) listeners. Callbacks can be synchronous or asynchronous and return `None`.

Tool and model events flow through this stream, along with framework events such as [`EnqueuedMessagesEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.EnqueuedMessagesEvent) when messages [injected mid-run](https://pydantic.dev/docs/ai/core-concepts/message-history/#injecting-messages-mid-run) with [`ctx.enqueue()`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.enqueue) enter run history, application [custom events](https://pydantic.dev/docs/ai/core-concepts/agent/#custom-events), and the [capability events](https://pydantic.dev/docs/ai/capabilities/overview/#capability-events) published by capabilities. Because an `event` callback belongs to the application rather than to a capability, it is also a place to [emit](https://pydantic.dev/docs/ai/core-concepts/agent/#custom-events) a [`CustomEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CustomEvent) of your own, which is how you [republish a capability’s internal event](https://pydantic.dev/docs/ai/capabilities/overview/#capability-events) to a frontend. An `event` callback also participates in [immediately dispatched](https://pydantic.dev/docs/ai/capabilities/overview/#reacting-to-events) capability decision events, so application code can set decision fields before the emitter continues. During a [realtime session](https://pydantic.dev/docs/ai/realtime/capabilities/), both hooks fire, and realtime-only [`RealtimeSessionEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.RealtimeSessionEvent) members flow through the same stream.

Pass event classes to filter the callback:

hooks\_event.py

```python
from pydantic_ai import Agent, PartStartEvent, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()
event_count = 0

@hooks.on.event(PartStartEvent)
async def count_events(ctx: RunContext, event: PartStartEvent) -> None:
    global event_count
    event_count += 1

agent = Agent('test', capabilities=[hooks])
```

Or use it bare to observe every event, with `event` typed as the full [`AgentStreamEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.AgentStreamEvent) union:

hooks\_event\_bare.py

```python
from pydantic_ai import Agent, AgentStreamEvent, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()
event_log: list[str] = []

@hooks.on.event
async def log_events(ctx: RunContext, event: AgentStreamEvent) -> None:
    event_log.append(event.event_kind)

agent = Agent('test', capabilities=[hooks])
```

Prefer naming the classes. Filtering by type isn’t only about narrowing the `event` argument for the type checker: the classes are what let dispatch skip a capability entirely for events it doesn’t listen to, so in a run with many capabilities a bare callback anywhere in the tree means every event is offered to everything.

Returning a replacement event from `hooks.on.event` is deprecated. Use `hooks.on.run_event_stream` to transform, replace, or filter events.

#### Listening without a Hooks capability

When events are all you want to observe, [`@agent.on_event`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.on_event) registers a listener straight on the agent, with the same filtering, typing and `timeout=`:

agent\_on\_event.py

```python
from pydantic_ai import Agent, FunctionToolCallEvent, RunContext

agent = Agent('test')
called_tools: list[str] = []

@agent.on_event(FunctionToolCallEvent)
async def track_tools(ctx: RunContext, event: FunctionToolCallEvent) -> None:
    called_tools.append(event.part.tool_name)
```

Bare works the same way: `@agent.on_event` on its own sees every event.

Listeners registered on the agent join after its own capabilities, so they see the events those emitted, and they survive an overridden root capability. Capability ordering still applies: one asking for `position='innermost'` keeps that position and its listeners run after these. An agent that never calls `on_event` is unaffected: with nothing registered, the listener capability is never added to the run at all.

Like `hooks.on.event`, they dispatch *upstream* of `run_event_stream`: a listener sees each event as emitted, not as finally delivered, so a capability that rewrites or drops events in its stream wrapper does so after every listener has run — and a listener can see an event no consumer ever receives. When you need the delivered stream, wrap it with `run_event_stream` or consume [`run_stream_events()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events).

Only events can be registered this way. The other hook families are interceptors — they sit in a wrap chain, take and return the value, and where they sit relative to the other capabilities is a choice you need to make — so they go on a `Hooks` capability whose position in `capabilities=` is yours to pick.

## Tool hook filtering

Tool hooks (validation and execution) support a `tools` parameter to target specific tools by name:

hooks\_tool\_filter.py

```python
from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.capabilities import Hooks, ValidatedToolArgs
from pydantic_ai.messages import ToolCallPart

hooks = Hooks()
call_log: list[str] = []

@hooks.on.before_tool_execute(tools=['send_email'])
async def audit_dangerous_tools(
    ctx: RunContext,
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: ValidatedToolArgs,
) -> ValidatedToolArgs:
    call_log.append(f'audit: {call.tool_name}')
    return args

agent = Agent('test', capabilities=[hooks])

@agent.tool_plain
def send_email(to: str) -> str:
    return f'sent to {to}'

result = agent.run_sync('Send an email to test@example.com')
print(call_log)
#> ['audit: send_email']
```

The `tools` parameter accepts a sequence of tool names. The hook only fires for matching tools — other tool calls pass through unaffected.

## Timeouts

Each hook supports an optional `timeout` in seconds. If the hook exceeds the timeout, a [`HookTimeoutError`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.HookTimeoutError) is raised:

hooks\_timeout.py

```python
import asyncio

from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks, HookTimeoutError

hooks = Hooks()

@hooks.on.before_model_request(timeout=0.01)
async def slow_hook(
    ctx: RunContext, request_context: ModelRequestContext
) -> ModelRequestContext:
    await asyncio.sleep(10)  # Will be interrupted by timeout
    return request_context  # pragma: no cover

agent = Agent('test', capabilities=[hooks])
try:
    agent.run_sync('Hello')
except HookTimeoutError as e:
    print(f'Hook timed out: {e.hook_name} after {e.timeout}s')
    #> Hook timed out: before_model_request after 0.01s
```

Timeouts are set via the decorator parameter (`@hooks.on.before_model_request(timeout=5.0)`) or via the constructor when using kwargs.

## Wrap hooks

Wrap hooks are the outermost layer of a stage, so they can surround the complete lifecycle with setup and teardown logic. Calling the supplied `handler` runs the `before_*` chain, the core operation with `on_*_error` recovery, and the `after_*` chain. Returning without calling the handler skips that inner lifecycle.

A short-circuiting wrapper also skips policy hooks in `before_*`. Put mandatory authorization in an outer wrapper or outside any short-circuitable cache.

In the `hooks.on` namespace, wrap hooks drop the `wrap_` prefix — `hooks.on.model_request` corresponds to `wrap_model_request`:

hooks\_wrap.py

```python
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks, WrapModelRequestHandler
from pydantic_ai.messages import ModelResponse

hooks = Hooks()
wrap_log: list[str] = []

@hooks.on.model_request
async def log_request(
    ctx: RunContext, *, request_context: ModelRequestContext, handler: WrapModelRequestHandler
) -> ModelResponse:
    wrap_log.append('before')
    response = await handler(request_context)
    wrap_log.append('after')
    return response

agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello!')
print(wrap_log)
#> ['before', 'after']
```

## Hook ordering

For every stage, the `wrap_*` hooks enclose the rest of the [hook lifecycle](#hook-lifecycle).

Within a single [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) instance, `before_*`, `after_*`, and `on_*_error` functions fire in **registration order** (the order they were defined or passed to the constructor). Registered `wrap_*` functions nest as middleware, with the first registered wrapper outermost.

Across multiple capabilities, the [composition rules](https://pydantic.dev/docs/ai/capabilities/custom/#composition-and-middleware-semantics) apply: `before_*` fires in capability order, `after_*` and `on_*_error` fire in reverse capability order, and `wrap_*` nests with the first capability outermost. These families do not interleave capability by capability: all wrappers are entered before any `before_*` hook, so even the innermost capability’s wrapper runs before the outermost capability’s `before_*` hook.

Hook timing also affects what is populated on [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext). Early run and node hooks can fire before the current step’s tool manager and model request parameters have been assembled. At that point `ctx.available_tool_names` can still include tool-search discoveries reconstructed from history, but `ctx.tools` and current request parameters may be empty or reflect the previous step. `before_model_request` and later model-request hooks see the request about to be sent, including the current function tools, native tools, and model settings. Tool and output hooks see the state for the call or output currently being processed.

For on-demand capabilities, `ctx.loaded_capability_ids` is derived from message history before each model request, so a capability loaded during a step appears from the *next* step onwards — the same step that first carries its instructions to the model, and therefore the first on which its tools can be called. Function tools, native tools, and model settings from the loaded capability appear on that request too, and hooks owned by the capability run for hook points reached from then on. A hook that looks for a capability in the very turn it was loaded will not find it.

## Error hooks

Error hooks (`*_error` in the `hooks.on` namespace, `on_*_error` on `AbstractCapability`) use **raise-to-propagate, return-to-recover** semantics:

- **Raise the original error** — propagates unchanged *(default)*
- **Raise a different exception** — transforms the error
- **Return a result** — suppresses the error

They run around failures from the core operation, inside the wrapped handler. Recovery therefore happens before control returns through the `wrap_*` chain: wrappers see the recovered result, and only unrecovered failures propagate out through them. Exceptions from `before_*`, `after_*`, or `wrap_*` are outside the corresponding error hook’s scope.

See [Error hooks](https://pydantic.dev/docs/ai/capabilities/custom/#error-hooks) for the full pattern and recovery types.

## Triggering retries with ModelRetry and failures with ToolFailed

Hooks can raise [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) to ask the model to try again with a custom message — the same exception used in [tool functions](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries) and output validators. `ModelRetry` always means “ask the model again”: to abort the run from a hook instead, raise any other exception and it propagates to the caller.

**Model request hooks** (`before_model_request`, `after_model_request`, `wrap_model_request`, `on_model_request_error`):

- The retry message is sent back to the model as a [`RetryFeedbackPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.RetryFeedbackPart), rendered in Pydantic AI’s own voice rather than the user’s — see [Feedback that belongs to no tool call](https://pydantic.dev/docs/ai/core-concepts/retries/#feedback-that-belongs-to-no-tool-call)
- `before_model_request`: no response is saved, since the model wasn’t called. The next request adds the retry message to the existing history, and `before_model_request` hooks run again for it, so a hook that always raises uses up the retry budget
- `after_model_request`: the original response is preserved in message history so the model can see what it said
- `wrap_model_request`: the response is preserved only if the handler was called
- Retries count against the output side of the agent’s retry budget
- [`run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream) can’t retry a response it has already streamed as final output, so a `ModelRetry` rejecting it raises [`UnexpectedModelBehavior`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UnexpectedModelBehavior) when the `async with` block exits. [`run_stream_events()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events) and [`iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter) retry it

**Tool hooks** (`before/after_tool_validate`, `wrap_tool_validate`, `on_tool_validate_error`, `before/after_tool_execute`, `wrap_tool_execute`, `on_tool_execute_error`):

- Converted to retried tool results, same as when a tool function raises `ModelRetry`
- Retries count against the tool’s `max_retries` limit

**Output hooks** (`before/after_output_validate`, `wrap_output_validate`, `on_output_validate_error`, `before/after_output_process`, `wrap_output_process`, `on_output_process_error`):

- Converted to retries, same as when an output function raises `ModelRetry`
- For tool output, retries count against the tool’s `max_retries` limit
- For text output, retries count against the output side of the agent’s retry budget

An `on_*_error` hook only covers its stage’s core operation. [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) raised by a `before_*`, `after_*`, or `wrap_*` hook therefore bypasses it. From a core operation, `ModelRetry` is passed to `on_tool_validate_error` and `on_output_validate_error`, but bypasses `on_model_request_error`, `on_tool_execute_error`, and `on_output_process_error` as control flow.

[`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed) bypasses the tool-validation and tool-execution error hooks. From the core model call or core output processing it is an ordinary exception passed to `on_model_request_error` or `on_output_process_error`; when raised by a `before_*`, `after_*`, or `wrap_*` hook, it is outside the corresponding error hook’s scope.

Tool validation and execution hooks can also raise [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed) to report a failed tool result without consuming the tool’s retry budget. This has the same model-visible outcome and retry-budget behavior as raising `ToolFailed` from the tool function itself, and is useful when an error hook converts a third-party exception into a failure the model can see.

hooks\_model\_retry.py

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.exceptions import ModelRetry
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models import ModelRequestContext

hooks = Hooks()

@hooks.on.after_model_request
async def check_response(
    ctx: RunContext,
    *,
    request_context: ModelRequestContext,
    response: ModelResponse,
) -> ModelResponse:
    if 'PLACEHOLDER' in str(response.parts):
        raise ModelRetry('Response contains placeholder text. Please provide real data.')
    return response

agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello')
print(result.output)
#> success (no tool calls)
```

By default, any exception other than `ModelRetry` or `ToolFailed` raised inside a tool escapes the tool boundary and aborts the entire run. A tool-execution hook lets you intercept these in one place — without editing every tool — and choose how each surfaces to the model. The distinction is the semantic one between [requesting a retry](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries) and [reporting a failure](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-failed):

- raise `ModelRetry` for **transient** errors, where the same call might succeed if tried again;
- raise `ToolFailed` for **definitive** failures, where retrying won’t help and the model should see the result and adapt (choose another approach, tell the user, etc.).

The hook below makes that call based on an upstream status code — the per-error analogue of the MCP [`tool_error_behavior`](https://pydantic.dev/docs/ai/mcp/client/#tool-errors) setting:

hooks\_convert\_tool\_errors.py

```python
from typing import Any

from pydantic_ai import Agent, RunContext, ToolCallPart, ToolDefinition, ToolReturnPart
from pydantic_ai.capabilities import Hooks
from pydantic_ai.exceptions import ModelRetry, ToolFailed
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

class UpstreamError(Exception):
    """Stand-in for an HTTP client error that carries the response status code."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code

hooks = Hooks()

@hooks.on.tool_execute_error
async def convert_upstream_errors(
    ctx: RunContext,
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: dict[str, Any],
    error: Exception,
) -> Any:
    if isinstance(error, UpstreamError):
        if error.status_code >= 500 or error.status_code == 429:
            # Transient: the same call might succeed, so ask the model to try again.
            raise ModelRetry(f'Upstream returned {error.status_code}, please try again.')
        # Definitive (e.g. 404, 403): retrying won't help — report it so the model can adapt.
        raise ToolFailed(f'Upstream returned {error.status_code}: {error}')
    raise error  # unrelated errors still abort the run

def model_fn(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    last_part = messages[-1].parts[-1]
    if isinstance(last_part, ToolReturnPart):
        return ModelResponse(parts=[TextPart(f'Could not fetch the document ({last_part.content}).')])
    return ModelResponse(parts=[ToolCallPart('get_document', {'doc_id': 42}, tool_call_id='call-1')])

agent = Agent(FunctionModel(model_fn), capabilities=[hooks])

@agent.tool_plain
def get_document(doc_id: int) -> str:
    raise UpstreamError(404, f'document {doc_id} not found')

result = agent.run_sync('Fetch document 42')
print(result.output)
#> Could not fetch the document (Upstream returned 404: document 42 not found).
```

Because the failure was raised as `ToolFailed` rather than `ModelRetry`, the model receives it as a [`ToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturnPart) with `outcome='failed'` and decides what to do next, instead of burning a retry on a call that can’t succeed.

## When to use Hooks vs AbstractCapability

| Use [`Hooks`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Hooks) | Use [`AbstractCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability) |
| --- | --- |
| Application-level hooks (logging, metrics) | Reusable, packaged capabilities |
| Quick one-off interceptors | Combined tools + hooks + instructions + settings |
| No configuration state needed | Complex per-run state management |
| Single-file scripts | Multi-agent shared behavior |
