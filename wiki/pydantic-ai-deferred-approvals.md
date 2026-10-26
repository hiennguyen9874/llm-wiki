---
type: Concept
title: Pydantic AI deferred tool approval
description: How Pydantic AI pauses a run for human approval without holding a process open, and how ApprovalReviewer and ToolCallJudge automate opposite halves of the decision.
tags: [ml, pydantic-ai, agents, safety]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:00:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

Approval in Pydantic AI does not block a thread. A tool marked `requires_approval=True` — or one that raises `ApprovalRequired` — ends the run with `DeferredToolRequests` as its output. The application stores the state, asks a person, and starts a new run with the message history plus `DeferredToolResults`[^dd-v2-tour-2026]

## The round trip

1. The model requests a tool call that needs approval.
2. The run returns `DeferredToolRequests` instead of a final answer; the declared output type must include it, e.g. `output_type=[str, DeferredToolRequests]`.
3. The application decides, building a `DeferredToolResults` where each `tool_call_id` maps to `True` or to a denial such as `ToolDenied('Over the self-serve limit')`.
4. A second run resumes with `message_history=first.all_messages()` and `deferred_tool_results=...`.

For decisions that need no human in the loop, the `HandleDeferredToolCalls` capability takes a handler and resolves approvals inside the same run[^dd-v2-tour-2026] The deferred requests themselves travel in the [Conversation](pydantic-ai-conversation-state.md) object when one is used.

## Two models, opposite powers

The source frames both Harness capabilities as answers to approval fatigue — prompts that people stop reading — and stresses that they do not do the same job[^dd-v2-tour-2026]:

| Capability | Added | Model's decision | Effect | Can it deny? |
| --- | --- | --- | --- | --- |
| `ApprovalReviewer` | v2.57.0, Harness | One risk question per call that already needs approval; `no` (not risky) approves on the person's behalf, `yes` or `unsure` leaves it to the person | Removes low-risk prompts | No — and it never runs the call itself |
| `ToolCallJudge` | v2.53.0, Harness | `yes` blocks a call whether or not a person is watching | Blocks risky calls | Yes |

The Harness README's distinction, quoted in the article, is: "Use Tool Call Judge when you want a model to say no... Use Approval Reviewer when you want a model to say yes on a person's behalf." Which one fits depends on whether the failure mode is too many prompts or too few[^dd-v2-tour-2026]

## Failure mode the design avoids

Holding a process open while waiting for a person ties approval latency directly to compute and connection lifetime. Deferring the run makes the wait free, and the resume path is the same one a crash-recovery engine would use, which is why approval design and [durable execution](pydantic-ai-durable-execution.md) interact.

## Limits

- Only the pause/decide/resume path was exercised, against `TestModel`; the `ApprovalReviewer` and `ToolCallJudge` model behaviour was not tested[^dd-v2-tour-2026]
- The risk question `ApprovalReviewer` asks, its model, and its cost are not documented in this capture, so its false-approval rate is unknown.
- Denial handling is shown as a string reason; how a model should react to repeated denials, and whether audit records are produced, is not covered.
- Evidence class: **Reported**.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md) for inline resolution and for attaching reviewers.
- **Resumes through** [Conversation state](pydantic-ai-conversation-state.md), which retains deferred tool requests.
- **Complements** [durable execution](pydantic-ai-durable-execution.md): both turn a long wait into a serialized pause.
- **Depends on** the [Harness](pydantic-ai-harness.md), which ships both reviewer capabilities.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Human approval without holding a process open" (raw lines 265–329) for `requires_approval`, `DeferredToolRequests`/`DeferredToolResults`, `HandleDeferredToolCalls`, the `ApprovalReviewer` versus `ToolCallJudge` comparison and the quoted README distinction; §"Release timeline since V2.0" for the v2.53.0 and v2.57.0 introduction dates. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — author-run `TestModel` example plus a README quotation; no Harness package, reviewer prompt, or live approval was inspected.
