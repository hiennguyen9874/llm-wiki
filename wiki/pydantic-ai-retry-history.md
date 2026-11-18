---
type: Concept
title: Pydantic AI retry records in message history
description: What a retry leaves behind in Pydantic AI history — the retried ToolReturnPart with its RetryInfo, the RetryFeedbackPart stored without wording and rendered per model, the causes and tags behind each form, and how to find and audit rejected calls.
tags: [pydantic-ai, messages, retries, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:20:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-retries
    resource: ../raw/core-concepts/retries/index.md
    scope: ../raw/core-concepts/retries/
    kind: documentation
    revision: sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56
    title: "Retries"
---

**Reported, Pydantic AI version unspecified:** a retry leaves one of exactly two records in history, and neither is a second part standing in for a result[^pydantic-docs-retries] A retry that belongs to a tool call **is** that call's result — a `ToolReturnPart` carrying the call's `tool_call_id` and marked `outcome='retried'`, so a retried call and a successful one look the same apart from the outcome[^pydantic-docs-retries] A retry that answers no call — the text output path, or a `ModelRetry` from a model-request hook — becomes a `RetryFeedbackPart`, which stores *why* the response could not be used and nothing about how to say it[^pydantic-docs-retries] Both stay in history, so a later run that reuses that history replays the failures to the model[^pydantic-docs-retries]

## A retried tool call

The part's `content` is the feedback itself: the `ModelRetry` message, or a `ValidationError`'s error details serialized as plain JSON data[^pydantic-docs-retries] It reaches the model on the provider's native error channel, the same one a failed result uses — Anthropic's `is_error`, Bedrock's `status='error'`, Gemini's `error` key, or an `{"error": …}` wrapper where the provider has none[^pydantic-docs-retries]

The vendor's round-trip sample shows the shape: a `FunctionModel` asks for `lookup_user`, the tool raises `ModelRetry`, and the message list comes back as `UserPromptPart`, `ToolCallPart`, `ToolReturnPart`, `ToolCallPart`, `ToolReturnPart`, `TextPart`[^pydantic-docs-retries]

`ToolFailed` records the same kind of part with `outcome='failed'` and does **not** consume the retry budget, so repeated failures are bounded by `UsageLimits` rather than by a retry count[^pydantic-docs-retries] The outcome is the whole difference: `'retried'` asks the model to correct the call, `'failed'` tells it to adapt — the budget and failure semantics are owned by [tool execution, retries and failures](pydantic-ai-tool-execution.md)[^pydantic-docs-retries]

## The audit metadata

A retried `ToolReturnPart` also records why the call must be made again and how far into its budget it is, in its `retry` field: a `RetryInfo` object[^pydantic-docs-retries]

| Field | Meaning |
| --- | --- |
| `cause` (`ToolRetryCause`) | `'validation_error'`, `'model_retry'`, or — for a call rejected before any tool ran — `'unknown_tool'` (the model invented the name) or `'unavailable_tool'` (the tool exists but cannot be called at this step)[^pydantic-docs-retries] |
| `attempt` | Which retry of that tool this is, counting from 1[^pydantic-docs-retries] |
| `max_retries` | The limit the attempt was checked against, so `attempt == max_retries` marks the last retry the run will make before raising[^pydantic-docs-retries] |

Both counters are `None` for a retry that is not charged to the budget, such as a tool's first `'unavailable_tool'` refusal[^pydantic-docs-retries] None of it is sent to the model, so recording it does not change the request[^pydantic-docs-retries]

The two framework-side causes are the ones with no hook: `'unknown_tool'` and `'unavailable_tool'` never resolve to a tool, so no tool hook sees them and the recorded part is what to match on[^pydantic-docs-retries]

## Finding and auditing retries

`is_retry(part)` matches a retried `ToolReturnPart` and a `RetryFeedbackPart` — exactly what the deprecated `RetryPromptPart` used to record, and stored histories load in this new shape, so it replaces an `isinstance(part, RetryPromptPart)` check[^pydantic-docs-retries] A `'failed'` outcome is not a retry and `is_retry` leaves it out; to find every tool call that reached the model as an error, check `isinstance(part, BaseToolReturnPart) and part.outcome in ERROR_OUTCOMES`, where `ERROR_OUTCOMES` holds `'retried'` and `'failed'` — which also covers a native tool's return[^pydantic-docs-retries]

Two cautions from the page[^pydantic-docs-retries]:

- **Do not rely on `retry` being set.** A retried return loaded from a deprecated `RetryPromptPart`, or one your own code builds, can carry `retry=None`; the outcome is the check that always holds
- **The last rejection is not in history.** When a tool's retry budget runs out the run raises `UnexpectedModelBehavior` instead of recording another retried result, so exhaustion is only visible as the exception

With instrumentation on, each attempt is also visible in telemetry: a tool's span carries `pydantic_ai.tool.retry.cause`, `pydantic_ai.tool.retry.attempt` and `pydantic_ai.tool.retry.max_retries`, and an output function's span carries `pydantic_ai.output.retry.*` for a retry that answers no tool call[^pydantic-docs-retries]

A capability can collect the parts from every request the run builds in `after_node_run`, which — unlike `on_event` — does not move the run onto the streaming path[^pydantic-docs-retries] The page's `AuditRejectedCalls` sample keeps a list of `(tool_name, retry)` pairs, and against a model that invents `lookup_customer` it prints `[('lookup_customer', RetryInfo(cause='unknown_tool', attempt=1, max_retries=1))]`[^pydantic-docs-retries]

## RetryFeedbackPart: stored meaning, rendered wording

The text output path has no tool call to answer, so its retry is a new `ModelRequest` whose only part is a `RetryFeedbackPart`[^pydantic-docs-retries] The stored part carries no wording at all; each model turns it into a sendable part when the request is built, and its `retry.cause` decides which one — which is why the same history can be replayed against any model[^pydantic-docs-retries]

| `cause` | What the model is sent | Why |
| --- | --- | --- |
| `'validation_error'` | A user turn opening with one line saying the application's validation is speaking, not the user, followed by the errors wrapped in `<pyai:validation_errors>…</pyai:validation_errors>` | The feedback quotes the output the model itself wrote, which may in turn quote untrusted user input; the tag marks those words off from a person's turn[^pydantic-docs-retries] |
| `'model_retry'` | The same attributed user turn, with the `ModelRetry` message wrapped in `<pyai:retry_feedback>…</pyai:retry_feedback>` | Output validators routinely interpolate the rejected output into the message, so it can carry the model's own words[^pydantic-docs-retries] |
| `'no_output'` | A mid-conversation system prompt, degraded to `<system>`-tagged user text where the provider takes no system message mid-conversation | The text is the framework's own fixed request for usable output and carries nothing the model wrote; a `'no_output'` part with any other content — one your own code builds — goes out fenced in `<pyai:retry_feedback>` like `'model_retry'`[^pydantic-docs-retries] |

The same `RetryInfo` records the `attempt` on the run's output-retry budget and the `max_retries` it was checked against, and that attempt is the `ctx.retry` the next output validation sees[^pydantic-docs-retries] Which budget that counter belongs to — one shared budget on the text path, a per-output-tool limit on the tool path — is owned by [structured output](pydantic-ai-structured-output.md)[^pydantic-docs-retries]

The sample makes the shape concrete: an output validator raising `ModelRetry('answer with the number spelled out as a word')` leaves a `RetryFeedbackPart(content='answer with the number spelled out as a word', retry=RetryInfo(cause='model_retry', attempt=1, max_retries=1), timestamp=…)`[^pydantic-docs-retries]

## Replay and redaction

Because retries stay in history, reusing that history in a later run replays the failures to the model; filtering them out is a `ProcessHistory` capability's job[^pydantic-docs-retries] That is a choice about what the model should remember, not a change to the budget, and it composes with the history-editing rules in [history processors](pydantic-ai-history-processors.md).

## Evidence and coverage

The package is `raw/core-concepts/retries/`, one `index.md` capture (7,480 words as declared, 7,700 by local `wc -w`, 861 lines, content digest `sha256:0585554b`) with no attachments, includes or supporting files[^pydantic-docs-retries] Links read rather than followed: the `ToolReturnPart`, `RetryFeedbackPart`, `RetryInfo`, `ToolRetryCause`, `BaseToolReturnPart`, `ERROR_OUTCOMES`, `is_retry`, `ModelRequest`, `ModelResponse.failed_attempts`, `UnexpectedModelBehavior`, `ModelRetry`, `ToolFailed`, `UsageLimits`, `FunctionModel`, `Agent`, `AbstractCapability.after_node_run`, `AbstractCapability.on_event` and `ProcessHistory` API pages, the hooks page, the message-history page, the Logfire integration page, the native-tools and tools-advanced pages, and the output page[^pydantic-docs-retries]

## Limits

- The page names **no Pydantic AI version, date, author or licence**; the record shapes, the `<pyai:…>` tags and the deprecated `RetryPromptPart` therefore describe an unknown release. The concept is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-retries]
- The printed sample outputs are the vendor's own runs, quoted rather than reproduced; no run was executed here[^pydantic-docs-retries]
- `UnexpectedModelBehavior` is named as what exhaustion raises but its constructor, message fields and cause chain are not given, so a handler that needs the last rejection's `retry` details has no documented way to reach them[^pydantic-docs-retries]
- Whether the `RetryInfo` of a `'no_output'` part or of a native tool's return follows the same rules is unstated[^pydantic-docs-retries]
- Evidence class: **Reported** — no agent run, history serialized, part constructed, retry exhausted or capability attached in this ingest.

## Relationships

- **Is the record half of** [retry layers and multiplication](pydantic-ai-retry-layers.md), whose "message history" column this page expands.
- **Extends** [tool execution, retries and failures](pydantic-ai-tool-execution.md) with the audit fields, the framework-side causes and the `is_retry`/`ERROR_OUTCOMES` queries over the parts it creates.
- **Extends** [structured output](pydantic-ai-structured-output.md) with the rendering rule for the retry feedback it counts.
- **Feeds** [same-model retries](pydantic-ai-retry-on-model-errors.md), whose attempts appear in the same `failed_attempts` list the winning `ModelResponse` carries.
- **Shares its parts with** [message history](pydantic-ai-message-history.md), which owns the request/response records these parts live in, and with [history repair](pydantic-ai-history-repair.md), which synthesizes `ToolReturnPart`s for interrupted calls.
- **Is filtered by** [history processors](pydantic-ai-history-processors.md) when the model should not see its earlier mistakes.
- **Appears in telemetry as** the `pydantic_ai.tool.retry.*` and `pydantic_ai.output.retry.*` span attributes covered by [Pydantic AI observability](pydantic-ai-observability.md).

[^pydantic-docs-retries]: Pydantic Docs, "Retries" (<https://pydantic.dev/docs/ai/core-concepts/retries/>, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/retries/index.md`, content digest sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56. §"What a retry looks like in message history" (raw lines 613–670) for the retried `ToolReturnPart`, the `retry_history.py` sample and its printed message list, the `content` carriers, the `ToolFailed` contrast, the native error channels and the `ProcessHistory` note; §"Auditing rejected tool calls" (671–733) for `RetryInfo`/`ToolRetryCause`, `attempt`/`max_retries`, the `None` cases, the no-hook causes, the span attributes, `after_node_run`, the `AuditRejectedCalls` sample and its printed tuple, and the `UnexpectedModelBehavior` exhaustion rule; §"Finding tool errors in history" (734–774) for `is_retry`, the deprecated `RetryPromptPart`, `ERROR_OUTCOMES`, the `BaseToolReturnPart` check, the native-tool coverage and the `retry=None` caution; §"Output retries" (775–803) for the text-path `ModelRequest`/`RetryFeedbackPart` split, the tool-path binding to the output tool's `tool_call_id` and the shared triggers; §"Feedback that belongs to no tool call" (804–856) for the stored-no-wording rule, the `retry_feedback_history.py` sample, the `ctx.retry` continuity and the three-row `cause` table with its tags. Evidence class: **Reported** — vendor documentation naming no version; nothing was serialized, constructed or executed.
