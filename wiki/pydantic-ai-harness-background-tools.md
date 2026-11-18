---
type: Concept
title: Pydantic AI Harness background tools
description: The Harness BackgroundTools capability — selected tools run while the agent keeps working, and each result returns as a framed follow-up message with a task ID, with its retry, cancellation, hook-ordering, streaming and durability consequences.
tags: [pydantic-ai, agents, harness, concurrency]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:50:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-background-tools-docs
    resource: ../raw/harness/background-tools/index.md
    scope: ../raw/harness/background-tools/
    kind: documentation
    revision: sha256:607b6966e299ee556368f1f2c54b8aad865953f6032e798568312df60ebfcf03
    title: "Background Tools"
---

`BackgroundTools` is the [Harness](pydantic-ai-harness.md) capability that lets selected tools run while the agent keeps working: the model is told the call started, with a task ID, and each finished result arrives later as a follow-up message carrying the same ID[^pydantic-background-tools-docs] It is the answer to a slow tool the model should not block on — a research call, a crawl, a long external job — rather than to a whole delegation, which is [subagent task control](pydantic-ai-subagent-tasks.md)'s job. The capability supplies both halves: it decides which tools run in the background, and it writes the started and completed messages so the model can tell a pending call from a finished one. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## Selecting which tools run in the background

The default selector is `'background': True` in tool metadata, and `BackgroundTools(tools=...)` takes the standard `ToolSelector`, so the same three forms work as anywhere else[^pydantic-background-tools-docs]:

| Selector form | Example | Effect |
| --- | --- | --- |
| Metadata match (default) | `BackgroundTools()` or `BackgroundTools(tools={'background': True})` | Every tool whose metadata carries the key/value pair |
| Custom metadata key | `BackgroundTools(tools={'kind': 'research'})` | Uses a different metadata entry as the marker |
| Tool names | `BackgroundTools(tools=['slow_research', 'deep_dig'])` | Named tools only |
| Predicate | `BackgroundTools(tools=lambda ctx, td: td.name.startswith('research_'))` | A callable over the run context and the tool's definition |

Marking tools one by one is not required: `SetToolMetadata` or `FunctionToolset.with_metadata(background=True)` marks a whole toolset, and the selector then matches those tools as it would any other[^pydantic-background-tools-docs]

A tool selected by `BackgroundTools(tools=...)` **always** runs in the background — the model gets no say[^pydantic-background-tools-docs] The per-call opt-in is metadata value `'optional'` instead of `True`: the model then sees a `run_in_background` argument and chooses for each call, while the function itself never receives that argument, so it must not declare a parameter of that name.

Three places ignore the opt-in and run normally even when `run_in_background` is set: sequential tools, realtime sessions, and the calls [Code Mode](pydantic-ai-code-mode.md)'s `run_code` makes from its sandbox[^pydantic-background-tools-docs] The capability therefore changes tool scheduling only where a tool call is a model-issued call the run itself executes.

## What the model sees

The model first receives a message saying the tool started, including a task ID; when the tool finishes, the result arrives with the same ID[^pydantic-background-tools-docs] Each follow-up — a success or a handled failure — is a `BackgroundToolResultPart` from `pydantic_ai_harness.background_tools`, a `CapabilityPart` the run enqueues for its next `ModelRequest`; history is searched by that type, and `tool_name`, `tool_call_id` and `outcome` name the call it completes[^pydantic-background-tools-docs]

The frame is the load-bearing part, because the follow-up travels on the **user channel**:

- The result is wrapped in `<tool_result tool_name="..." tool_call_id="...">` tags, analogous to the `<pyai:tool_result>` tags Pydantic AI puts around tool files it sends on that channel, with a note in the application's voice saying the tool wrote it — not the user and not the application[^pydantic-background-tools-docs]
- Text inside the output that looks like the frame's own tag, or like an application frame such as `<system>`, gets a further note naming the tool as its author, so it cannot close the frame early or speak as the application[^pydantic-background-tools-docs]
- A failed call is framed the same way with `outcome="failed"`, wrapping the message from `ModelRetry` or `ToolFailed`[^pydantic-background-tools-docs]

The payload is what the tool returned: its text and files, then any `ToolReturn.content`, in that frame with adjacent text joined on separate lines, while `ToolReturn.metadata` is discarded[^pydantic-background-tools-docs] Because the follow-up is a capability part, the Vercel AI and AG-UI message conversions leave it out, so it stays in server-side history — the same server-history argument [Harness planning](pydantic-ai-harness-planning.md) makes for its plan records and [multimodal input](pydantic-ai-multimodal-input.md) makes for structured content.

## Errors, retries and how a run ends

Failures split by what the model can act on[^pydantic-background-tools-docs]:

| Failure | What happens |
| --- | --- |
| `ModelRetry`, `ToolFailed`, approval and deferral errors | Reported to the model as text in the same frame, including when raised by a `before_tool_execute` or `after_tool_execute` hook |
| `ValidationError` from such a hook | Also reported, with the call retried as a sequential tool retries it |
| Any other tool exception | Ends the run with the original exception, as for a sequential tool |
| Running out of retries, or `CancelledError` | Ends the run |

Retry accounting follows the sequential case so that `ctx.retry` and `ctx.last_attempt` mean the same thing[^pydantic-background-tools-docs] A `ModelRetry` or `ValidationError` counts toward the tool's `retries` when its follow-up is delivered, however long the tool ran; a result resets the count; the started message does neither. The run ends at its next step, so a model request already in progress finishes first, and a tool can call `ctx.cancel()` to stop the run and the other background tools.

A normal run waits for its background tools to finish, and a pending call counts toward `tool_calls_limit`[^pydantic-background-tools-docs] Stopping early or pausing for deferred tools cancels unfinished ones. Results of tools that finished before a deferred-tool pause stay in the message history so a resumed run sees them — unless every call in the paused step was deferred — while results not yet delivered when a run stops early are dropped. Async tools must allow cancellation, because ignoring it can prevent the run from stopping.

## Limits and hook ordering

The source states six limitations, and four of them are ordering effects that are easy to get wrong[^pydantic-background-tools-docs]:

- **Streaming does not deliver results.** `run_stream()` and `run_stream_sync()` wait for background tools but never deliver their results, so a streamed response may only say the work started. `run_stream_events()`, `run()`, `run_sync()`, or consuming all of `agent.iter()` are the routes when the final response needs the result.
- **Sequential tools can overlap background work** that started earlier, so tools sharing state must protect it or stay out of the background.
- **Realtime sessions are unchanged**, because they already run tools concurrently.
- **Hook placement decides what a hook sees.** `after_tool_execute`, `on_tool_execute_error` and `wrap_tool_execute` hooks of capabilities listed *after* `BackgroundTools` run inside the background task and see the real result; `wrap_tool_execute` hooks of capabilities listed *before* it, and tool result events, see the started message.
- **The result is plain text in the user channel.** A tool returning untrusted content (a fetched web page, say) can make that content look like another task's result, so such output must be delimited or sanitized inside the tool.
- **Argument repair needs to come first.** List `RepairToolArguments`, or `Coder` which includes it, before `BackgroundTools`; otherwise a malformed call that sets `run_in_background` is retried rather than repaired, and a repaired call runs in the foreground.

[Lifecycle hooks](pydantic-ai-lifecycle-hooks.md) is the surface those placement rules act on: the hook families, their cross-capability ordering and the event dispatch point are documented there, and this capability is a concrete case where the same hook sees two different outcomes depending on where its capability sits in the list.

## Tracing and durable execution

`BackgroundTools` adds no tracing spans of its own[^pydantic-background-tools-docs] Pydantic AI's tool span ends when the started message is returned, so the span neither covers the tool's work nor records a failure; the completed result survives only in the agent's message history, which is the reason to keep that history where [observability](pydantic-ai-observability.md) can read it.

Under [durable execution](pydantic-ai-durable-execution.md) the capability works with Temporal[^pydantic-background-tools-docs] With DBOS, durable work belongs in an explicit DBOS step that the background tool calls, and `ctx.enqueue()` must not be called inside a durable activity or task, because its messages cannot be restored during replay — the same replay constraint [DBOS streaming](pydantic-ai-dbos-streaming.md) records for `ctx.emit()` and `ctx.enqueue()` in steps.

## Configuration

```python
from pydantic_ai import Agent
from pydantic_ai_harness import BackgroundTools

agent = Agent('openai:gpt-6.1-sol', capabilities=[BackgroundTools()])

@agent.tool_plain(metadata={'background': 'optional'})
async def slow_research(query: str) -> str:
    return f'Research findings for {query!r}'
```

The constructor takes one argument, `BackgroundTools(tools: ToolSelector = {'background': True})`[^pydantic-background-tools-docs] It also loads from an agent spec, with `capabilities: [{BackgroundTools: {}}]` in YAML and `Agent.from_file(..., custom_capability_types=[BackgroundTools])` at load time, which is the same opt-in [agent specs](pydantic-ai-agent-specs.md) requires for capabilities outside the serializable built-in set[^pydantic-background-tools-docs]

## Limits

- The source is a single vendor documentation page — "Background Tools", Pydantic Docs, 1,264 words as declared and 1,325 by local `wc -w`, **no publication date, no author, no licence and no Pydantic AI or Harness version**. Under the `pydantic-ai` domain rule the page is `draft` and every API name is version-unknown[^pydantic-background-tools-docs]
- Nothing was executed: no package installed, no agent constructed, no background tool started, awaited, cancelled or retried, no stream consumed, no hook ordered and no durable run replayed. Every behavioural claim is **Reported**[^pydantic-background-tools-docs]
- The example pins `openai:gpt-6.1-sol`, an alias no release pin corroborates here, so it is illustrative rather than tested.
- Unstated by the source: the task-ID format, how many background tools may run at once, whether a follow-up is delivered mid-run or only between steps, how a tool's `retries` budget interacts with a result that is never delivered, what a client-held history does when the capability part is dropped, and whether `BackgroundTools` publishes any typed [capability event](pydantic-ai-capability-events.md).
- External links — the `ToolSelector` and `CapabilityPart` API references, `SetToolMetadata`, `ToolReturn`, the `RepairToolArguments` and Harness version-policy pages, and the capability overview — were read as links, not followed.

## Relationships

- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md), attached through `capabilities=[BackgroundTools()]` and covered by the Harness's 0.x version policy.
- **Differs from** [subagent task control](pydantic-ai-subagent-tasks.md): that mechanism gives a delegation a receipt, steering, questions and a persisted session, while this one keeps a single tool call inside the same run and returns its result as a message.
- **Is ordered against by** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md): a tool hook's capability position decides whether it observes the started message or the real result, and tool result events see the start.
- **Depends on** [conversation state](pydantic-ai-conversation-state.md) for the follow-up to survive: the result is a capability part, which UI-adapter conversions drop, so a client-held history loses it.
- **Becomes durable under** [Pydantic AI durable execution](pydantic-ai-durable-execution.md) with Temporal, and under [DBOS](pydantic-ai-dbos.md) only through an explicit step the background tool calls.
- **Excludes** [Code Mode](pydantic-ai-code-mode.md)'s sandbox calls and [realtime voice](pydantic-ai-realtime-voice.md) sessions, which keep their own scheduling even when `run_in_background` is set.
- **Charges** the retry budgets of [run controls](pydantic-ai-run-controls.md) exactly as a sequential tool does, and counts a pending call against `tool_calls_limit`.

[^pydantic-background-tools-docs]: Pydantic Docs, "Background Tools", <https://pydantic.dev/docs/ai/harness/background-tools/>; local capture `raw/harness/background-tools/index.md`, content digest sha256:607b6966, 1,264 words as declared (1,325 by `wc -w`), no publication date, author, licence or Pydantic AI/Harness version. Lines 15–38 for the install command, the `BackgroundTools()` attachment, the `slow_research` tool with `metadata={'background': True}`, the default-selector rule and the version-policy note; lines 39–55 for the sequence diagram (started message with task ID, other calls or turn end, follow-up user message with result and same task ID); lines 57–99 for the `ToolSelector` forms (metadata key, custom key, names, predicate), the `'optional'` value and its `run_in_background` argument, the sequential/realtime/`run_code` exclusions and the do-not-declare rule, plus `SetToolMetadata` and `FunctionToolset.with_metadata(background=True)`; lines 115–125 for the started message, the `BackgroundToolResultPart` capability part enqueued for the next `ModelRequest` with `tool_name`/`tool_call_id`/`outcome`, the Vercel AI and AG-UI omission, the `<tool_result>` frame and its `<pyai:tool_result>` analogy, the anti-spoofing note, `outcome="failed"`, the payload and the discarded `ToolReturn.metadata`, the error table, the retry accounting and `ctx.retry`/`ctx.last_attempt`, the next-step end, `ctx.cancel()`, the wait-for-completion rule, `tool_calls_limit`, deferred-pause cancellation and kept results, dropping on early stop and the cancellation requirement; lines 127–134 for the six limitations (stream delivery, sequential overlap, realtime, hook ordering and tool result events, untrusted content, `RepairToolArguments`/`Coder` ordering); lines 136–138 for the absent spans and the tool span ending at the started message; lines 140–146 for Temporal support, the DBOS explicit-step rule and the `ctx.enqueue()` replay prohibition; lines 148–151 for the `BackgroundTools(tools: ToolSelector = {'background': True})` signature; lines 154–175 for the agent-spec YAML and `custom_capability_types`. Evidence class: **Reported** — vendor documentation with no execution behind it.
