---
type: Concept
title: Pydantic AI prompt injection defender
description: The Harness PromptInjectionDefender capability — StackOne Defender classifies local tool results after the tool returns, reports flagged verdicts as spans and callbacks, withholds high-or-critical results on request, and needs an explicit id to survive replay.
tags: [pydantic-ai, agents, harness, security]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:20:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-prompt-injection-defender-docs
    resource: ../raw/harness/prompt-injection-defender/index.md
    scope: ../raw/harness/prompt-injection-defender/
    kind: documentation
    revision: sha256:df840340d8ed46251585a4c52c924cb7195b55409f230a5f62e057b27c4f6c0c
    title: "Prompt Injection Defender"
---

`PromptInjectionDefender` is the [Harness](pydantic-ai-harness.md) capability that screens **local tool results** for indirect prompt injection — instructions planted in third-party data such as emails, tickets, documents and MCP payloads that redirect the agent — using StackOne's `stackone-defender` after the tool returns[^pydantic-prompt-injection-defender-docs] It is a detection layer, not a sandbox: it decides what the model is allowed to read, which is the complement of what [guardrails](pydantic-ai-harness.md) do for input and output and of the [tool approval](pydantic-ai-deferred-approvals.md) path that decides what the agent may run. The page names no Pydantic AI or Harness version, so every behaviour below is version-unknown.

## Where it sits in the loop

The hook is `after_tool_execute`, and the ordering is deliberate: `get_ordering()` places the defender **closest to tool execution**, before other capabilities reshape the result, so it classifies the raw tool return rather than a summary, a truncation or another capability's re-rendering[^pydantic-prompt-injection-defender-docs] A clean result passes through unchanged; a result the defence rejects is replaced whole and never reaches the model.

Each model-visible part of a result is classified separately, and **one blocked part withholds the whole result** — the withholding is not per part[^pydantic-prompt-injection-defender-docs]

`tool_filter` takes the standard `ToolSelector`, defaulting to `'all'`; non-matching tools always pass through, so a defender can be scoped to the few tools that read untrusted third-party text rather than every tool[^pydantic-prompt-injection-defender-docs]

## Two detection tiers

| Tier | Install | Catches |
| --- | --- | --- |
| Pattern detection (base extra) | `pydantic-ai-harness[prompt-injection-defender]` | Known patterns over recognised text fields, bare string results, and `ToolReturn` content |
| Local ML classification (`semantic_detection=True`) | `pydantic-ai-harness[prompt-injection-defender-ml]` | Text under fields the pattern tier does not recognise |

Semantic detection is what covers the unrecognised-field gap; without it those strings are not classified at all — and strings used as **mapping keys** are not classified even with it[^pydantic-prompt-injection-defender-docs] The base extra requires Python 3.11 or newer; on Python 3.15 the ML extra installs pattern detection only until ONNX Runtime publishes 3.15 wheels, so the tier silently narrows on that interpreter.

The model is preloaded off the event loop in `before_run`, which is the reason a custom bridge matters under distributed workers (below).

## Reporting, withholding and telemetry

The default is **report-only**: a flagged result still reaches the model[^pydantic-prompt-injection-defender-docs] Three surfaces then exist, and they are independent:

- `block_high_risk=True` asks the built-in defence to reject high or critical risk results, replacing them with `blocked_message`; the default message accepts `{tool_name}` and `{risk_level}` placeholders, literal braces must be doubled, and an invalid placeholder raises `UserError` at construction.
- `on_detection(ctx, call, verdict)` runs a sync or async callback for each flagged verdict — including sanitisation, rejection and escalation — and an exception from it **fails the run**; a single `ToolReturn` can produce separate verdicts for its return value and its additional content items.
- A zero-duration `prompt_injection flagged` OpenTelemetry span is emitted per flagged verdict, with or without either option above, carrying `gen_ai.tool.name`, `gen_ai.tool.call.id`, `prompt_injection.action` (`blocked` or `reported`), `.risk_level`, `.detections` (the matched pattern names), `.tier2_score` when semantic detection scored the result, and `.fields_sanitized` only when the instrumentation captures content.

Two asymmetries belong together: the tool result text itself is never recorded on the span, and a withheld result carries a diagnostics summary on `ToolReturn.metadata` under `prompt_injection`, which the application can read and the model cannot[^pydantic-prompt-injection-defender-docs] That keeps a blocked payload out of both the prompt and the trace.

## What it does not classify

The scope is narrower than "all tool output", and every gap is a bypass[^pydantic-prompt-injection-defender-docs]:

- **Provider-native tools** — hosted web search and other server-side tools never transit the client, so they are never classified.
- **Externally supplied deferred results** are outside the scope as well.
- **Retry and failure text** raised through `ModelRetry`/`ToolFailed` is not classified.
- For a `ToolReturn`, only `return_value` and model-visible `content` are classified; `ToolReturn.metadata` and additional content items' metadata are not, and a rejected result drops value, content and metadata together.
- **Referenced media is not fetched or decoded**, so instructions inside images, audio, video or documents are not inspected.

## Custom defence and durable execution

Passing `defense=` a configured `stackone_defender.PromptDefense` hands over thresholds, per-tool risky fields, the detection provider and Tier 3 configuration; that object then owns blocking and semantic-detection configuration, and combining it with the corresponding capability option raises `UserError`[^pydantic-prompt-injection-defender-docs] Call `defense.warmup_tier2()` at application startup to load the classifier before the first tool result.

Under Temporal, DBOS or Prefect the capability changes shape[^pydantic-prompt-injection-defender-docs]:

- The semantic warmup, and classification when `semantic_detection=True` or a `defense` is supplied, run as **durable operations**, because the ML classifier cannot load in workflow code; a replay reuses the recorded verdict.
- `on_detection` and the span run from the **hook**, so a replay repeats them — an idempotency obligation on the callback.
- On distributed workers the `warmup` activity may load the model on a different worker from the one that later calls `classify`, which loads it on first use; a warm classifier therefore requires a supplied `defense` warmed at worker startup.
- A durable operation is addressed by the capability's `id`, and `PromptInjectionDefender` has **no default `id`**, because several scoped defenders compose on one agent — so a defender on a durable-capable agent must be given a distinct `id` per defender, or Pydantic AI refuses to bind the agent and names the fix. Outside durable execution the `id` stays optional.

That missing default is the one contrast with [PydanticAIDocs](pydantic-ai-harness-docs.md), which ships a default `id` because only one docs source can exist on an agent; the two rules follow from the same principle rather than contradicting each other.

## Coverage and limits

The package is the single `index.md` capture with no attachments, includes or supporting files; the flow diagram was read in its text form[^pydantic-prompt-injection-defender-docs] External links — the capabilities overview, instrumentation, and the `defender-py` repository — were read as links and not followed. The page states no version, date, author or licence, so the concept is `draft` under the `pydantic-ai` domain rule.

Nothing was installed, no tool result classified, no result blocked, no callback fired and no span inspected, so every claim is **Reported** and none **Observed** or **Reproduced**. Unstated and consequential: what the pattern set actually contains, the risk thresholds behind "high or critical", the classifier's false-positive and false-negative rates, the token or latency cost per result, and whether the base pattern tier can be defeated by encoding — a security claim this page cannot support either way.

## Relationships

- **Complements** [guardrails](pydantic-ai-harness.md) (input, output, tool-call and tool-result checks) and [deferred tool approval](pydantic-ai-deferred-approvals.md) (what may run): this capability is about what the model may read.
- **Ordered before** other result-reshaping capabilities by `get_ordering()`, so a [background tool](pydantic-ai-harness-background-tools.md) result or a truncated one is classified in its raw form.
- **Depends on** the [lifecycle hooks](pydantic-ai-lifecycle-hooks.md) contract for its placement in the loop.
- **Constrained by** [durable execution](pydantic-ai-durable-execution.md): an explicit `id` per defender, and a replay that repeats the callback and the span but not the classification.
- **Emits telemetry into** [Pydantic AI observability](pydantic-ai-observability.md) as `prompt_injection flagged` spans.

[^pydantic-prompt-injection-defender-docs]: Pydantic Docs, "Prompt Injection Defender", <https://pydantic.dev/docs/ai/harness/prompt-injection-defender/>; local capture `raw/harness/prompt-injection-defender/index.md`, content digest sha256:df840340, 1,477 words as declared (1,546 by `wc -w`), 276 lines, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11 for the purpose and the StackOne dependency; 13–35 for the flow diagram (tool → `after_tool_execute` → defender → result or notice, plus the `on_detection` and `block_high_risk` branches); 37–63 for the two install extras, the Python 3.11 floor, the pattern scope and `semantic_detection=True`; 65–83 for the usage example; 85–94 for the six options and their interaction errors; 96–112 for the `on_detection` example and the `prompt_injection` metadata note; 114–125 for the span name and attribute list; 127–132 for the scope limits (native tools, deferred results, retry text, `ToolReturn` fields, mapping keys, media); 134–146 for the durable-execution behaviour, the `warmup`/`classify` worker split and the missing default `id`; 148–165 for the custom `defense` and `warmup_tier2()`; 167–275 for the API reference (`defense` including its Tier 3 note, `block_high_risk`, `semantic_detection`, `tool_filter`, `on_detection`, `blocked_message`, `get_ordering`, `before_run`, and `after_tool_execute` at 272 with the per-part classification and whole-result withholding rule). Evidence class: **Reported** — vendor documentation for its own package, with no execution or measured detection rate behind it.
