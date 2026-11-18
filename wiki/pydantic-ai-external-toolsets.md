---
type: Concept
title: Pydantic AI external toolsets
description: How a Pydantic AI agent offers tools it cannot execute itself — an ExternalToolset built from ToolDefinitions, the deferred round trip that hands calls to a frontend or upstream service, and the result types a call may come back as.
tags: [pydantic-ai, agents, tools, frontend]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:26:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-toolsets
    resource: ../raw/tools-toolsets/toolsets/index.md
    scope: ../raw/tools-toolsets/toolsets/
    kind: documentation
    revision: sha256:376fcf77e23d854d7b3adfbd3c7ab51b845516590c4c146bd4a21e9c8ee55355
    title: "Toolsets"
---

**Reported, Pydantic AI version unspecified:** `ExternalToolset` is the toolset for tools the agent can describe but not run — they are provided and executed by an upstream service or by a frontend — and it is built from a list of `ToolDefinition`s carrying the names, argument JSON schemas and descriptions[^pydantic-docs-toolsets] Its whole behaviour is the deferral: the run does not execute the call, it ends and returns it. That makes it the mirror image of every other toolset on [Pydantic AI toolsets](pydantic-ai-toolsets.md), which exist to execute something, and it is why the interesting part of this page is the round trip rather than the class.

## The round trip

1. The model calls a tool in the external set, and the call is treated as **deferred**[^pydantic-docs-toolsets]
2. The run ends with a `DeferredToolRequests` output object whose `calls` list holds `ToolCallPart`s — tool name, validated arguments, and a unique tool-call id — instead of a final answer[^pydantic-docs-toolsets]
3. The application passes those calls to whatever will execute them: the upstream service, or the frontend that owns the tool[^pydantic-docs-toolsets]
4. It builds a `DeferredToolResults` whose `calls` dictionary maps each tool-call id to the value to return[^pydantic-docs-toolsets]
5. A new run resumes with the original message history **and** `deferred_tool_results=...`[^pydantic-docs-toolsets]

One declaration is load-bearing: `DeferredToolRequests` must appear in the `output_type` of the agent or of the run, otherwise the possible output types are not inferred correctly[^pydantic-docs-toolsets] The `DeferredToolRequests` object is not exclusive to this path — the approval sample in [toolset composition](pydantic-ai-toolset-composition.md) shows the same class carrying an `approvals` list of `ToolCallPart`s beside an empty `calls` list, so one pause can in principle carry both kinds of pending work[^pydantic-docs-toolsets]

## What a call may come back as

The `calls` mapping is not restricted to return values; each entry is one of three shapes, and the difference between the two failure shapes is what decides retry accounting[^pydantic-docs-toolsets]:

| Entry | Meaning | Effect on the tool's retry budget |
| --- | --- | --- |
| An arbitrary value, or a `ToolReturn` | The result | Consumed as an ordinary tool result |
| `ModelRetry` | The call failed in a way the model should correct | Consumed, per [tool execution](pydantic-ai-tool-execution.md) |
| `ToolFailed` | A definitive failure to report | Reported as a failed result **without** consuming the retry budget |

A `ToolReturn` is the richer carrier: it is the same object that separates a result from extra content and metadata described in [tool results and returned files](pydantic-ai-tool-results.md).

## The documented wiring

The sample splits the agent into a reusable half and a request-shaped half. The reusable half builds a small `FunctionToolset` and an agent with a structured `output_type`; the request half is a function that takes the frontend's `messages`, its `frontend_tools: list[ToolDefinition]`, and optional `deferred_tool_results`, constructs `ExternalToolset(frontend_tools)` and runs the agent[^pydantic-docs-toolsets] Three notes on that function are the operational detail[^pydantic-docs-toolsets]:

- run-time `toolsets=` are **additional** to the constructor's, so the external set joins the agent's own tools rather than replacing them;
- run-time `output_type=` **overrides** the constructor's, so it must restate the agent's own output type beside `DeferredToolRequests` or the structured result is lost;
- no `user_prompt` is passed, because the frontend supplies the prompt inside `messages`.

The front end of the loop is a `while True` that dispatches by name: for each `output.calls` entry it looks the tool up in a `{name: function}` dictionary, calls it with `**tool_call.args_as_dict()`, and writes the result into `deferred_tool_results.calls[tool_call.tool_call_id]`; an unknown name becomes `ModelRetry(f"Unknown tool {tool_call.tool_name!r}")`, which is how a frontend reports a tool definition the backend no longer implements without ending the run[^pydantic-docs-toolsets] The sample's stub returns `'es-MX'` standing in for `navigator.language`, which is the shape the feature is aimed at: a capability only the browser has[^pydantic-docs-toolsets]

## Evidence and coverage

The material is §"External Toolset", raw lines 735–887, inside the vendor's single Toolsets capture — 5,125 words as declared, 5,192 by local `wc -w`, 1,023 lines, no attachments, includes, downloads or supporting files[^pydantic-docs-toolsets] The capture names **no Pydantic AI version, date, author or licence**, so the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set. Every link it offers — `ExternalToolset`, `ToolDefinition`, `DeferredToolRequests`, `DeferredToolResults`, `ToolCallPart`, `ToolReturn`, `ModelRetry`, `ToolFailed` and the deferred-tools guide — was read as a link, not followed; that guide has since been compiled as [Pydantic AI deferred tools](pydantic-ai-deferred-tools.md), which carries the handler route, the metadata correlation and the pause object this page's round trip omits. Nothing was installed, no `ExternalToolset` built, no run paused, no `deferred_tool_results` handed back and no frontend loop executed, so every claim is **Reported** and none **Observed** or **Reproduced**. Limits: `args_as_dict()` is shown being called but not documented; whether an `ExternalToolset` may mix with a deferred *approval* pause in one `DeferredToolRequests` is unstated beyond the shared class; and what happens when an entry is missing from `DeferredToolResults.calls`, or when the frontend returns a value that fails the tool's declared return schema, is not described.

## Relationships

- **Is the frontend-executed counterpart of** [Pydantic AI toolsets](pydantic-ai-toolsets.md): the same attachment sites apply, but this set executes nothing and returns its calls.
- **Shares the pause object with** [Pydantic AI deferred tool approval](pydantic-ai-deferred-approvals.md): both end a run in `DeferredToolRequests` and resume with `DeferredToolResults`, one through `calls` and the other through `approvals`.
- **Is one flavor of** [Pydantic AI deferred tools](pydantic-ai-deferred-tools.md), which covers the routes that resolve either list — an inline `HandleDeferredToolCalls` handler, a resume token, or a new run — and the rule that a call nothing resolves bubbles up as output.
- **Splits failure handling the way** [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md) records it, with `ModelRetry` spending the budget and `ToolFailed` reporting a definitive failure without spending it.
- **Carries results through** [Pydantic AI tool results and returned files](pydantic-ai-tool-results.md), because a `ToolReturn` can separate the model-visible result from content and metadata.
- **Constrains** [Pydantic AI structured output](pydantic-ai-structured-output.md)'s `output_type` whenever the run may pause, since `DeferredToolRequests` has to be part of the declared union.
- **Keeps execution outside** [Pydantic AI durable execution](pydantic-ai-durable-execution.md)'s recorded units: the Temporal table compiled in [Pydantic AI temporal](pydantic-ai-temporal.md) lists `ExternalToolset` among the non-executing toolsets whose calls are not wrapped as activities.
- **Sits on the trust boundary described in** [Pydantic AI client-supplied history](pydantic-ai-client-supplied-history.md): the tool definitions and the results both arrive from the client, so what a client may fabricate is that page's subject.
- **Is the agent-side of a UI protocol integration**, such as the Vercel AI and AG-UI conversions noted in [Pydantic AI Harness background tools](pydantic-ai-harness-background-tools.md), where capability parts do not cross the wire.

[^pydantic-docs-toolsets]: Pydantic Docs, "Toolsets" (<https://pydantic.dev/docs/ai/tools-toolsets/toolsets/>, `domain: pydantic.dev`, `language: en`, 5,125 words as declared and 5,192 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/toolsets/index.md`, 1,023 lines, content digest sha256:376fcf77. §"External Toolset" (raw lines 735–887) for the `ExternalToolset` construction from `ToolDefinition`s, the deferred-call rule, the `DeferredToolRequests.calls` payload and its tool-call ids, the `DeferredToolResults.calls` mapping to a value, `ToolReturn`, `ModelRetry` or `ToolFailed`, the `output_type` requirement, the `deferred_toolset_agent.py` / `deferred_toolset_api.py` / `deferred_tools.py` samples with the run-time `toolsets` and `output_type` notes, the absent `user_prompt`, the frontend dispatch loop with `args_as_dict()` and the unknown-tool `ModelRetry`, and the `navigator.language` framing; §"Requiring Tool Approval" (535–597) for the approval sample's `DeferredToolRequests(calls=[], approvals=[...], metadata={})` print showing both lists on one object. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.
