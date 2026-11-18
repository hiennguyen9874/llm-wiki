---
type: Concept
title: Pydantic AI deferred tools
description: How a Pydantic AI run hands a tool call to someone else — the two deferral flavors, resolution inline through a HandleDeferredToolCalls handler or by ending the run and resuming a new one, resume tokens, the conversation that carries pending requests, and the stream events that announce them.
tags: [pydantic-ai, agents, tools, approvals]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:18:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-deferred-tools
    resource: ../raw/tools-toolsets/deferred-tools/index.md
    scope: ../raw/tools-toolsets/deferred-tools/
    kind: documentation
    revision: sha256:62784e57799f951023c4d49ef78e380bed6e4a45fbf494098736d7fb3ed6fbb4
    title: "Deferred Tools"
---

**Reported, Pydantic AI version unspecified:** a deferred tool is a call the model may request but the run will not execute in the same process — and Pydantic AI gives it two flavors (approval-required, externally executed) and two resolution routes (a handler that answers inline, or an ended run that a caller resumes)[^pydantic-docs-deferred-tools] The docs allow exactly three reasons to defer: the call needs a person's approval, its result depends on an upstream service, frontend or user, or producing the result would take longer than it is reasonable to keep the agent process alive[^pydantic-docs-deferred-tools] Everything else on this page is the machinery those three reasons share, which is why the same `DeferredToolRequests` object carries both kinds of pending work and why one pause may mix them.

## Two kinds of deferral

| Flavor | Signalled by | Pending payload | Answers carried in |
| --- | --- | --- | --- |
| Approval required | `requires_approval=True`, or a tool raising `ApprovalRequired` | `DeferredToolRequests.approvals` — `ToolCallPart`s with the model's arguments | `DeferredToolResults.approvals` |
| Executed externally | A tool raising `CallDeferred` (`kind='external'`), or an `ExternalToolset` | `DeferredToolRequests.calls` — `ToolCallPart`s with validated arguments | `DeferredToolResults.calls` |

Both lists carry the tool name, the arguments and a unique tool-call id, and the two are not interchangeable: an id placed in the wrong dictionary is what `build_results()` is there to reject[^pydantic-docs-deferred-tools] The flavor also decides what "validated" means in the payload — an approval request shows the arguments as the model sent them, while an external call's arguments are the validated ones[^pydantic-docs-deferred-tools]

## Two routes to resolve a call

| Route | Resolver lives | What the caller does | Run behaviour |
| --- | --- | --- | --- |
| Inline handler | In the agent's process (an approval gate, an external service client) | Registers `HandleDeferredToolCalls(handler=…)`; the handler returns a `DeferredToolResults` | One call continues as if the tools had returned normally |
| Stop the world | Outside the process (a UI adapter that asks a person, a worker that finishes a job) | The run ends with `DeferredToolRequests`; the caller starts a **new** run with the history plus `deferred_tool_results=` | Two runs: the follow-up gets its own `run_id` |

The vendor's framing of the choice is where the resolver lives, not which flavor is deferred[^pydantic-docs-deferred-tools] The two compose, and that composition is the important shape: a handler may resolve a subset of the calls and let the remainder bubble up as `DeferredToolRequests` output for an outer caller — which is the only reason to keep `DeferredToolRequests` in the output type once a handler exists[^pydantic-docs-deferred-tools]

Two rules belong to the stop-the-world route. `DeferredToolRequests` must be in the `Agent`'s `output_type` so the possible output types are inferred correctly, or passed at run time instead — and a run-time `output_type` **overrides** the constructor's for type-inference reasons, so it has to restate the original output type explicitly[^pydantic-docs-deferred-tools] The follow-up run also must not reuse the paused run's `run_id`; pause-and-resume correlation is kept through `conversation_id`[^pydantic-docs-deferred-tools]

## The handler route

`HandleDeferredToolCalls(handler=…)` is registered as an ordinary [capability](pydantic-ai-capability-primitive.md); its handler receives the `RunContext` and the `DeferredToolRequests` and returns a `DeferredToolResults` resolving some or all of them, after which the tool execution pipeline applies the results inline[^pydantic-docs-deferred-tools] `DeferredToolRequests.build_results()` is the convenience constructor for that return value: it validates that every tool-call id refers to a pending request of the correct kind, and `approve_all=True` auto-approves any approval request not otherwise specified[^pydantic-docs-deferred-tools]

Declining is a first-class outcome, not an error. A handler that omits a call, or returns `None`, passes it to the next `HandleDeferredToolCalls` capability or to anything else overriding the `handle_deferred_tool_calls` hook, and whatever stays unresolved surfaces as `DeferredToolRequests` output[^pydantic-docs-deferred-tools] A custom capability that resolves approvals or external calls itself overrides that hook directly instead of registering a separate `HandleDeferredToolCalls`, and the same hook is also reachable through the `Hooks` capability[^pydantic-docs-deferred-tools]

The handler can also **wait** without ending the run. A third parameter, a resume token, either answers the call right away or is handed to the approver, whose endpoint later resolves the token with the decision: by default the wait happens in your process, and in a [durable execution](pydantic-ai-durable-execution.md) run on an engine that supports it — currently AWS Lambda durable functions — the engine records the wait and suspends the run until the decision arrives[^pydantic-docs-deferred-tools] That is the distinction that makes the third parameter worth knowing: the same handler code is a blocking wait on a normal process and a durable suspension on a replaying one.

## What a pending call says it waits for

`DeferredToolRequests.kind()` returns `'approval'` for anything in `approvals` and `'question'` or `'external'` for anything in `calls`, so a caller never has to infer the interaction from the tool name[^pydantic-docs-deferred-tools] A tool marks its call as a question for the user — rather than work done elsewhere — with `raise CallDeferred(kind='question')`, and the Harness `AskUser` capability does exactly that[^pydantic-docs-deferred-tools] The answer may name who gave it in `DeferredToolResults.answered_by`, which Pydantic AI reports but does not check[^pydantic-docs-deferred-tools] — a reported field, not an authorization one.

## External execution: the mechanics

Conditional deferral is the pattern the docs recommend when whether to defer depends on the arguments, on the run context (dependencies, message history) or on the expected duration: the tool schedules the background work itself, passes along `RunContext.tool_call_id` so the result can be matched later, and then raises `CallDeferred`[^pydantic-docs-deferred-tools] The tool's `args_validator` may raise `CallDeferred` too, so only calls with valid arguments are ever handed off[^pydantic-docs-deferred-tools]

The vendor's background-task sample is the correlation recipe: generate a task id independent of the tool-call id, pass it via `CallDeferred(metadata={'task_id': …})`, read it back from `requests.metadata[tool_call_id]`, and map results to calls by that task id — falling back to `ModelRetry` for a call with no result[^pydantic-docs-deferred-tools] `metadata` is also accepted on the approval path, where `ApprovalRequired(metadata=…)` surfaces through the same keyed dictionary[^pydantic-docs-deferred-tools]

Each `DeferredToolResults.calls` entry is an arbitrary value, a `ToolReturn`, or an exception: `ModelRetry` when the model should try again, `ToolFailed` when the failure should be reported as final without spending the retry budget[^pydantic-docs-deferred-tools] See [tool execution](pydantic-ai-tool-execution.md) for the accounting and [external toolsets](pydantic-ai-external-toolsets.md) for the set that declares described-but-not-executed tools up front.

## Pausing and resuming a conversation

A run that ends with `DeferredToolRequests` has paused its conversation, and the forms of pause are why the requests must be stored rather than reconstructed: history shows which calls are unanswered but not which needed approval, which needed an external result, or what metadata the tool attached when it deferred[^pydantic-docs-deferred-tools] The requests therefore live on the run's `conversation` as `conversation.deferred_tool_requests`, so serializing the [Conversation](pydantic-ai-conversation-state.md) — `ConversationTypeAdapter.dump_json()` keyed by `conversation_id`, read back with `validate_json()` — is the whole persistence story[^pydantic-docs-deferred-tools]

Resuming rebuilds the results from those stored requests with `requests.build_results(...)`, which checks each answer against the request it answers, so a stale or mistyped tool-call id fails there rather than inside the run; after the resumed run finishes, `result.conversation.deferred_tool_requests` is `None`[^pydantic-docs-deferred-tools]

## Watching a pause in the event stream

A deferred call emits an ordinary `FunctionToolCallEvent`, which is exactly the problem for a UI: that event does not say the call is paused, or what interaction is expected[^pydantic-docs-deferred-tools] Two further `AgentStreamEvent`s carry it:

| Event | Emitted | Carries |
| --- | --- | --- |
| `DeferredToolRequestsEvent` | Once per batch of deferred calls, **before** any handler runs | The `DeferredToolRequests` |
| `DeferredToolResultsEvent` | When a handler resolves some or all of the requests | The `DeferredToolResults` |

Each resolved call then executes through the regular pipeline and emits its own `FunctionToolResultEvent`, and **no** event is emitted when results are instead supplied to a new run through `deferred_tool_results`, because the caller already knows them[^pydantic-docs-deferred-tools] The design intent is the split these events enable: the handler holds pure resolution logic (for instance waiting on a resume token) while the stream consumer owns all frontend communication, with no private map of which tools are interactive[^pydantic-docs-deferred-tools]

## Where the approval flavor is constrained

Approval mechanics are recorded in [deferred tool approval](pydantic-ai-deferred-approvals.md); the two constraints this source states about routing are worth keeping here. In a [realtime voice session](pydantic-ai-realtime-voice.md), approval must be resolved inline, typically by a `HandleDeferredToolCalls` handler, and a call nothing resolves is refused every time[^pydantic-docs-deferred-tools] And when a capability's tool validation hook rewrites arguments, the approval request still shows the model's arguments while the tool runs with the rewritten ones — validation, hooks included, runs again when the approved call resumes[^pydantic-docs-deferred-tools]

## Coverage, evidence and limits

The source is one `index.md` capture — 3,310 words as declared, 3,331 by local `wc -w`, 583 lines, no attachments, includes, downloads or supporting files[^pydantic-docs-deferred-tools] It names **no Pydantic AI version, publication date, author or licence**, so the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set, and every API name here is version-unknown. Its external links — the `HandleDeferredToolCalls`, `DeferredToolRequests`, `DeferredToolResults`, `RunContext`, `ToolApproved`, `ToolDenied`, `Conversation` and message types, the capabilities, custom-capabilities, hooks, toolsets, tools-advanced, durable-execution, AWS Lambda, AskUser, realtime-tools, message-history, output, MCP and conversation references, and the linked handler page — were read as links, not followed. The samples pin `openai:gpt-6.1-sol`, a model alias no package confirms. Limits: it does not say what the handler may raise, whether a resume token can time out or be reused, how a partially resolved batch orders its remaining calls, what happens when an entry is missing from `DeferredToolResults.calls` (beyond the bubble-up rule), or how a tool's declared return schema is enforced on an externally supplied value. Nothing was installed, no agent run, no handler called, no token resolved, no conversation serialized, no stream consumed and no durable suspension made, so every claim is **Reported** and none **Observed** or **Reproduced**.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md): the recommended handler route is a capability, and the underlying unit is the `handle_deferred_tool_calls` hook.
- **Is resolved through** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), whose `deferred_tool_calls` hook is the same resolution point a custom capability overrides.
- **Constrains** [structured output](pydantic-ai-structured-output.md): the stop-the-world route only infers its output types correctly when `DeferredToolRequests` is in the declared union.
- **Is paused into** [Conversation state](pydantic-ai-conversation-state.md), which carries `deferred_tool_requests` because the requests cannot be rebuilt from messages.
- **Owns the routing that** [deferred tool approval](pydantic-ai-deferred-approvals.md) uses for the approval flavor, where the declaration surfaces and who decides are the subject.
- **Composes with** [external toolsets](pydantic-ai-external-toolsets.md): that page covers `ExternalToolset` and the result shapes, this one covers the handler route, metadata correlation and the pause object both share.
- **Is answered as a question by** [Harness ask user](pydantic-ai-harness-ask-user.md), whose tools raise `CallDeferred(kind='question')` and whose answerer runs before a general handler.
- **Reuses** the event stream described in [streamed output](pydantic-ai-streamed-output.md), adding two events that say what a tool call is waiting for.
- **Suspends durably under** [durable execution](pydantic-ai-durable-execution.md) and the engines listed there, currently AWS Lambda durable functions for a recorded wait on a resume token.
- **Cannot pause** a [realtime voice session](pydantic-ai-realtime-voice.md), where an unresolved approval is refused rather than handed to the caller.

[^pydantic-docs-deferred-tools]: Pydantic Docs, "Deferred Tools" (<https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/>, `domain: pydantic.dev`, `language: en`, 3,310 words as declared and 3,331 by local `wc -w`, 583 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/deferred-tools/index.md`, content digest sha256:62784e57. §"Deferred Tools" intro (raw lines 11–33) for the three reasons to defer, the two flavors, the inline-handler versus end-the-run routes and their resolver-location criterion, the composition rule, the follow-up run's own `run_id` and `conversation_id` correlation, the resume-token third parameter with the in-process default and the AWS Lambda durable suspension, `kind()`'s three values, `CallDeferred(kind='question')` and `AskUser`, `DeferredToolResults.answered_by` being reported and not checked, and the `output_type` requirement including the run-time override; §"Resolving deferred calls with a handler" (35–100) for `HandleDeferredToolCalls` registration, `build_results()` and `approve_all`, the omitted-call/`None` hand-off, the bubble-up and `output_type` implication, the `handle_deferred_tool_calls` hook and its `Hooks` exposure, and the `deferred_tool_handler.py` sample; §"Human-in-the-Loop Tool Approval" (101–327) for the realtime inline rule and the argument-rewriting rule; §"External Tool Execution" (328–493) for conditional `CallDeferred`, `RunContext.tool_call_id`, the `args_validator` path, the `ExternalToolset` pointer, the do-nothing tool function, the result types with `ModelRetry`/`ToolFailed`, and the `external_tool.py` task-id/metadata sample; §"Pausing a conversation" (494–551) for `conversation.deferred_tool_requests`, the not-rebuildable-from-messages rationale, `ConversationTypeAdapter.dump_json`/`validate_json`, `build_results()` validation and the `None` afterwards; §"Observing deferred tool calls in a stream" (552–583) for `FunctionToolCallEvent` being insufficient, `DeferredToolRequestsEvent` before any handler, `DeferredToolResultsEvent`, the per-call `FunctionToolResultEvent`, the no-event rule for a new run's `deferred_tool_results`, and the resolution/presentation split. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
