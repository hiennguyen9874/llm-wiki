---
type: Concept
title: Pydantic AI deferred tool approval
description: How Pydantic AI pauses a run for human approval without holding a process open, and how ApprovalReviewer and ToolCallJudge automate opposite halves of the decision.
tags: [ml, pydantic-ai, agents, safety]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:53:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-docs-deferred-tools
    resource: ../raw/tools-toolsets/deferred-tools/index.md
    scope: ../raw/tools-toolsets/deferred-tools/
    kind: documentation
    revision: sha256:62784e57799f951023c4d49ef78e380bed6e4a45fbf494098736d7fb3ed6fbb4
    title: "Deferred Tools"
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

Approval in Pydantic AI does not block a thread. A tool marked `requires_approval=True` — or one that raises `ApprovalRequired` — ends the run with `DeferredToolRequests` as its output. The application stores the state, asks a person, and starts a new run with the message history plus `DeferredToolResults`[^dd-v2-tour-2026]

## The round trip

1. The model requests a tool call that needs approval.
2. The run returns `DeferredToolRequests` instead of a final answer, carrying the pending calls in its `approvals` list; the declared output type must include it, e.g. `output_type=[str, DeferredToolRequests]`.
3. The application decides, building a `DeferredToolResults` where each `tool_call_id` maps to `True` or to a denial such as `ToolDenied('Over the self-serve limit')`.
4. A second run resumes with `message_history=first.all_messages()` and `deferred_tool_results=...`.

For decisions that need no human in the loop, the `HandleDeferredToolCalls` capability takes a handler and resolves approvals inside the same run[^dd-v2-tour-2026] The deferred requests themselves travel in the [Conversation](pydantic-ai-conversation-state.md) object when one is used. The routing detail behind this list — handler versus ended run, the resume token, the pause object both flavors share, and the two events that announce a pause — is recorded in [Pydantic AI deferred tools](pydantic-ai-deferred-tools.md); this page keeps the approval decision itself[^pydantic-docs-deferred-tools].

## What can require approval

Approval is declared on any tool-registration surface, or decided inside the tool when it depends on the call[^pydantic-docs-deferred-tools]:

| Where | How | What it covers |
| --- | --- | --- |
| `@agent.tool`, `@agent.tool_plain`, `Tool(...)`, `FunctionToolset.tool`, `FunctionToolset.add_function()` | `requires_approval=True` | That one tool, always; the function may then assume the call was approved |
| `FunctionToolset(...)` | `requires_approval=True` | Every tool in the set, `Tool` instances included — only a function added with `requires_approval=False` opts out |
| Inside the function | `raise ApprovalRequired` | Calls whose risk depends on arguments, [dependencies](pydantic-ai-dependencies.md) or message history |
| An `args_validator` | `raise ApprovalRequired` | The same, decided before the function body runs |
| A toolset the agent does not own (an MCP server) | The `ApprovalRequiredToolset` wrapper in [toolset composition](pydantic-ai-toolset-composition.md) | Calls to tools a set provides |

`RunContext.tool_call_approved` is `True` when the call has already been approved, which is how a conditional tool avoids asking twice[^pydantic-docs-deferred-tools] A pending approval request carries a `ToolCallPart` with the tool name, the arguments **as the model sent them**, and a unique tool-call id[^pydantic-docs-deferred-tools] — so what the reviewer sees is not necessarily what the tool will run with.

## Answering, and changing, the call

Each `approvals` entry in `DeferredToolResults` is a boolean, a `ToolApproved`, or a `ToolDenied` with an optional `message` shown to the model[^pydantic-docs-deferred-tools] The three levers over the arguments differ in *when* they act, which is the part worth choosing deliberately[^pydantic-docs-deferred-tools]:

| Lever | Runs | Effect on what the reviewer sees |
| --- | --- | --- |
| A tool-validation hook such as `after_tool_validate` | Before approval | The request still shows the model's arguments, the tool runs with the rewritten ones, and validation runs again on resume |
| `before_tool_execute` | Only once the call is approved | The rewrite happens after approval, so the reviewer sees the model's arguments |
| `ToolApproved(override_args=...)` | At approval time | The approver supplies the arguments; validation runs on those instead of the model's |

`DeferredToolResults` also takes a `metadata` dictionary keyed by tool-call id, which the tool reads from `RunContext.tool_call_metadata` — the channel for a reviewer's note, a reason code, or a protected-file flag reaching the code that executes[^pydantic-docs-deferred-tools] On the declaring side, `ApprovalRequired(metadata={...})` puts the tool's own context on the pending request, where `DeferredToolRequests.metadata` exposes it to the caller[^pydantic-docs-deferred-tools].

## Two models, opposite powers

The source frames both Harness capabilities as answers to approval fatigue — prompts that people stop reading — and stresses that they do not do the same job[^dd-v2-tour-2026]:

| Capability | Added | Model's decision | Effect | Can it deny? |
| --- | --- | --- | --- | --- |
| `ApprovalReviewer` | v2.57.0, Harness | One risk question per call that already needs approval; `no` (not risky) approves on the person's behalf, `yes` or `unsure` leaves it to the person | Removes low-risk prompts | No — and it never runs the call itself |
| `ToolCallJudge` | v2.53.0, Harness | `yes` blocks a call whether or not a person is watching | Blocks risky calls | Yes |

The Harness README's distinction, quoted in the article, is: "Use Tool Call Judge when you want a model to say no... Use Approval Reviewer when you want a model to say yes on a person's behalf." Which one fits depends on whether the failure mode is too many prompts or too few[^dd-v2-tour-2026]

## Failure mode the design avoids

Holding a process open while waiting for a person ties approval latency directly to compute and connection lifetime. Deferring the run makes the wait free, and the resume path is the same one a crash-recovery engine would use, which is why approval design and [durable execution](pydantic-ai-durable-execution.md) interact.

## Where the decision arrives

The pause is one mechanism, but the decision reaches it over several routes, and choosing one is a deployment decision rather than an approval one[^pydantic-production-docs]:

- **Over a stream to a frontend** — the [UI adapters](pydantic-ai-production-readiness.md) carry approvals on the same AG-UI or Vercel AI stream as text and tool calls, and the CLI carries them too.
- **Inside a durable workflow** — the workflow can wait for the decision itself instead of ending; the vendor's DBOS example parks on `DBOS.recv_async('approvals', timeout_seconds=7 * 24 * 3600)` and turns a timeout into a denial for every pending call.
- **Inline, in the same process** — a `HandleDeferredToolCalls` handler resolves calls without ending the run, which is the only route that works mid-session in [realtime](pydantic-ai-realtime-voice.md).
- **By a second model** — `ToolCallJudge` blocks and `ApprovalReviewer` approves on a person's behalf, the two Harness capabilities compared above.

What comes back is not only a boolean: an approval can carry edited arguments (`ToolApproved(override_args=...)`) and a denial can carry a message the model sees — both covered in [answering, and changing, the call](#answering-and-changing-the-call).

## Limits

- The approval surfaces, the three argument levers and the metadata channels come from a vendor page naming **no Pydantic AI version or date**, so they are version-unknown[^pydantic-docs-deferred-tools]; what the handler may do with a review, and whether repeated denials are tracked anywhere, is unstated.
- Only the pause/decide/resume path was exercised, against `TestModel`; the `ApprovalReviewer` and `ToolCallJudge` model behaviour was not tested[^dd-v2-tour-2026] No approval surface above was declared, no handler or approver called, and no rewritten argument observed, so the additions are **Reported**.
- The risk question `ApprovalReviewer` asks, its model, and its cost are not documented in this capture, so its false-approval rate is unknown.
- Denial handling is shown as a string reason; how a model should react to repeated denials, and whether audit records are produced, is not covered.
- The four delivery routes come from the vendor's production page, which names no version or date; the stream, workflow and CLI routes were not exercised, and the seven-day wait is one example's constant rather than a recommended timeout[^pydantic-production-docs]
- Evidence class: **Reported**.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) for inline resolution and for attaching reviewers.
- **Resumes through** [Conversation state](pydantic-ai-conversation-state.md), which retains deferred tool requests.
- **Complements** [durable execution](pydantic-ai-durable-execution.md): both turn a long wait into a serialized pause.
- **Depends on** the [Harness](pydantic-ai-harness.md), which ships both reviewer capabilities.
- **Is gated by** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md): `ApprovalRequired` and `CallDeferred` may only be raised once arguments are validated or from the execution-preparation hooks, and the `deferred_tool_calls` hook resolves requests inline as an alternative to returning them to the caller.
- **Is entered through** an `args_validator` described in [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md): validation runs before approval is requested, a validator may raise `ApprovalRequired` or `CallDeferred` without consuming the retry budget, deferred calls are only deferred when their arguments already validated, and the validator runs a second time after approval with `RunContext.tool_call_approved` set[^pydantic-docs-tools-advanced].
- **Cannot pause** a [realtime voice session](pydantic-ai-realtime-voice.md): a live call has no caller to return `DeferredToolRequests` to, so a `HandleDeferredToolCalls` handler resolves each request during the call, which can mean waiting for a person mid-session.
- **Is one of the three jobs** [Pydantic AI production readiness](pydantic-ai-production-readiness.md) separates from a checkpointer, beside durable execution and the stored conversation.
- **Is also offered at the toolset layer**, as the gated wrappers catalogued in [Pydantic AI toolset composition](pydantic-ai-toolset-composition.md), where the decision is a predicate over each call's arguments, including the `ApprovalRequiredToolset` wrapper for sets the agent does not own.
- **Is one flavor of** [Pydantic AI deferred tools](pydantic-ai-deferred-tools.md), which owns the routing both flavors share: the inline handler and its resume token, `kind()`, the paused `Conversation`, and the stream events.
- **Reaches the executing tool through** `RunContext.tool_call_metadata`, filled from `DeferredToolResults.metadata`[^pydantic-docs-deferred-tools].
- **Is refused rather than paused** in a realtime session, where an unresolved approval is refused every time instead of ending the run[^pydantic-docs-deferred-tools].

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. §"How does a human approve a risky action, and the run resume days later?" (raw lines 144–181) for storing the `Conversation`, `deferred_tool_requests`, the edited-argument and denial-message note, the UI-adapter and CLI routes, the durable-workflow wait, the inline handler and the two Harness reviewers; §"An end-to-end service" (lines 33–124) for the `DBOS.recv_async('approvals', timeout_seconds=7 * 24 * 3600)` loop and its timeout-to-denial default. Evidence class: **Reported** — vendor documentation; no approval was requested, delivered or audited.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Human approval without holding a process open" (raw lines 265–329) for `requires_approval`, `DeferredToolRequests`/`DeferredToolResults`, `HandleDeferredToolCalls`, the `ApprovalReviewer` versus `ToolCallJudge` comparison and the quoted README distinction; §"Release timeline since V2.0" for the v2.53.0 and v2.57.0 introduction dates. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — author-run `TestModel` example plus a README quotation; no Harness package, reviewer prompt, or live approval was inspected.

[^pydantic-docs-deferred-tools]: Pydantic Docs, "Deferred Tools" (<https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/deferred-tools/index.md`, content digest sha256:62784e57. §"Deferred Tools" intro for the pause-and-resume frame and the two resolution routes; §"Human-in-the-Loop Tool Approval" (raw lines 101–327) for `requires_approval=True` on every registration surface, the `FunctionToolset` constructor applying to `Tool` instances with `requires_approval=False` as the only opt-out, raising `ApprovalRequired` from a function or its `args_validator`, `RunContext.tool_call_approved`, the `ApprovalRequiredToolset` pointer, the pending request's model-supplied arguments, `ToolApproved(override_args=...)` and `ToolDenied(message)`, the `metadata` dictionary reaching `RunContext.tool_call_metadata`, `ApprovalRequired(metadata=...)` surfacing on the request, the `after_tool_validate` versus `before_tool_execute` rewrite rules, and the realtime refusal. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Custom Args Validator" (raw lines 665–755) for `args_validator`'s signature and its `ModelRetry`/`ToolFailed`/`ApprovalRequired`/`CallDeferred` outcomes, validation running before approval is requested and only on calls that will be deferred, the `validate_transfer` sample, the post-approval re-run under `ctx.tool_call_approved`, the dedicated durable validation unit, and `args_valid` on `FunctionToolCallEvent`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
