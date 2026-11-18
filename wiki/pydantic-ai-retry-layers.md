---
type: Concept
title: Pydantic AI retry layers and multiplication
description: The nine places a Pydantic AI run can re-attempt work, why their budgets do not share, the N×F×M×K multiplication that decides how many wire requests one logical call sends, and how to choose a single retry owner.
tags: [pydantic-ai, reliability, retries, models]
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

**Reported, Pydantic AI version unspecified:** "retry" names nine different things in one agent run, at nine layers that share no budget, and the layers nest — a retry at one layer re-runs every layer nearer the wire, so the attempts *multiply* rather than add[^pydantic-docs-retries] Three of the nine are agent retries that cost a model round trip and leave a record in message history; the other six are invisible to the model[^pydantic-docs-retries] The operational consequence is a design rule, not a tuning knob: because the HTTP transport, the provider SDK and a durable engine all re-send the same request for the same failures, pick **one** of them to own retrying and give the others a single attempt[^pydantic-docs-retries]

## The nine layers

| Layer | What it re-attempts | Configured with | Message history |
| --- | --- | --- | --- |
| Transport | The same HTTP request | `AsyncHTTPX2TenacityTransport` on the HTTP client | Nothing[^pydantic-docs-retries] |
| Provider SDK | The same HTTP request, re-issued by the SDK's own client | The SDK client; provider-specific defaults | Nothing[^pydantic-docs-retries] |
| Durable execution | The whole model request, re-executed by the engine and re-entering every layer nearer the wire | Temporal `ActivityConfig.retry_policy`, DBOS `StepConfig.max_attempts`, Prefect `TaskConfig.retries` | Nothing — the engine replays the step[^pydantic-docs-retries] |
| Same-model request retries | The same request against the *same* model on a transient error | `RetryOnModelErrors`' `retry_on` and `max_attempts` | Only the winning response, listing the rest in `failed_attempts`[^pydantic-docs-retries] |
| Model fallback | The same request against a *different* model | `ModelFallback`, or `FallbackModel` | Only the winning response, with `failed_attempts`[^pydantic-docs-retries] |
| Model request attempts | The same request step, same or another model, when a hook raises `RetryModelRequest` | The hook; no retry budget, at most 100 attempts per step | Only the accepted response, with `failed_attempts`[^pydantic-docs-retries] |
| Tool | One tool call, by asking the model to correct it | `retries={'tools': N}` plus per-tool limits | A `ToolReturnPart` with `outcome='retried'` as that call's result[^pydantic-docs-retries] |
| Output | The final answer, by asking the model to correct it | `retries={'output': N}` plus `ToolOutput(max_retries=N)` | A `RetryFeedbackPart`, or a retried `ToolReturnPart`[^pydantic-docs-retries] |
| Model-request hooks | The request, from `before_model_request`, `after_model_request`, `wrap_model_request` or `on_model_request_error` raising `ModelRetry` | The hook; it draws on the **output** budget | A new request carrying a `RetryFeedbackPart`[^pydantic-docs-retries] |

Only the last three are agent retries: each costs a model round trip, because a retry *is* another request, and each leaves something the model can see next time[^pydantic-docs-retries] Everything above them in the table is wire-level bookkeeping the model never observes — a failed attempt there produces no message part at all[^pydantic-docs-retries] Batched requests add a tenth layer of their own: a request that failed on the provider's side is resubmitted in a new batch, up to `max_resubmissions` times[^pydantic-docs-retries]

## Multiplication

The layers do not share budgets but they do stack, so the worst case is a product rather than a sum[^pydantic-docs-retries] For one logical call:

| Factor | What it counts | Set by |
| --- | --- | --- |
| `N` | Model requests per logical call: the initial attempt, one follow-up per tool call (a *successful* tool call queues another request), plus whatever the tool and output budgets add | `retries={'tools': …}`, `retries={'output': …}`, the number of tool calls |
| `F` | Attempts per model request: one per model in a `ModelFallback` chain, times `max_attempts` per model under `RetryOnModelErrors`, plus `RetryModelRequest` attempts | `ModelFallback`, `RetryOnModelErrors.max_attempts`, capability hooks |
| `M` | Attempts inside the provider SDK client | The SDK, overridable per request with `ModelSettings['max_retries']` |
| `K` | Attempts on the wire | The transport's stop strategy, where `stop_after_attempt(N)` means `N` total attempts, not one plus `N` |

One logical call can therefore put up to `N × F × M × K` requests on the network[^pydantic-docs-retries] The vendor's own worked example: `retries={'output': 2}` (up to 3 requests for the final answer alone), the OpenAI SDK's default `max_retries=2` (3 attempts per request) and `stop_after_attempt(2)` (2 wire attempts) give `3 × 1 × 3 × 2 = 18`, doubling to 36 with a two-model fallback; with `ModelSettings(timeout=10)` that is 180 seconds of request time before any backoff wait[^pydantic-docs-retries]

Two subtleties sit outside the product:

- A `FallbackModel` walks its own models inside a *single* `F` attempt, outside the 100-attempt ceiling, so a `FallbackModel` used as one of `ModelFallback`'s models multiplies the two[^pydantic-docs-retries]
- A `prepare_model_request` hook that moves an attempt to another model before anything is sent counts towards the ceiling but records no failed attempt and no span[^pydantic-docs-retries]

Every wire request pays its own latency and bills its own tokens once it reaches the model, so budgets must absorb the worst case, not the happy path[^pydantic-docs-retries]

## What the budgets do not bound

`UsageLimits.request_limit` (default `50`) bounds only `N`: it counts the model responses committed to each run's history and never sees fallback attempts, `RetryModelRequest` attempts, SDK retries or transport retries beneath them[^pydantic-docs-retries] Their tokens and cost *do* count towards the token and cost limits whenever the provider reports them — as it does for a response a fallback model rejected — but usually not for a request that failed[^pydantic-docs-retries]

The three time settings split along the same seam[^pydantic-docs-retries]:

| Setting | Scope |
| --- | --- |
| `ModelSettings.timeout` | One attempt; a retrying SDK client re-arms it per retry, and only on model classes that forward it |
| `ModelSettings.request_timeout` | All `M × K` attempts of one request to one model, on every model class |
| `ModelSettings.first_event_timeout` | Those attempts on a streamed request, up to the first output — not the response that follows it |

## Choosing one retry owner

A rate limit, a 5xx and a dropped connection are exactly the failures the transport, the SDK and a durable engine each re-send, so stacking them adds little that one could not do alone and delays both the error reaching the agent and a fallback model getting its turn[^pydantic-docs-retries] Unless the layers are meant to cover different failure sets, hand the job to one and give the others a single attempt[^pydantic-docs-retries]

| Owner | Choose it when | Give the others one attempt with |
| --- | --- | --- |
| `RetryOnModelErrors` (the vendor's recommendation) | The agent should own retrying: it decides by normalized error categories, retries a stream that fails before any output, records every attempt in `failed_attempts`, composes with `ModelFallback`, and waits durably on Temporal and DBOS | Nothing for the SDK — the capability already sends with `max_retries=0` unless you set it; no retrying transport; on Temporal keep a bounded `maximum_attempts` for crashes and timeouts, since model errors become non-retryable automatically[^pydantic-docs-retries] |
| The provider SDK | Its defaults suit you, which is what you get without configuring anything | Nothing, except on Temporal, where a model request activity retries without limit until `maximum_attempts=1`; DBOS and Prefect do not retry a step by default[^pydantic-docs-retries] |
| A retrying transport | You want one policy across providers, your own error set, or waits that respect `Retry-After` up to a limit you set | `ModelSettings['max_retries']=0`, and one attempt in a durable engine's retry policy[^pydantic-docs-retries] |
| A durable execution engine | The request runs as a Temporal activity or DBOS/Prefect step and you want the engine to record and schedule its attempts | `max_retries=0` and no retrying transport[^pydantic-docs-retries] |

With one owner, a failing request is retried on the wire at most as far as that owner allows: `K` for a transport stopped by `stop_after_attempt(K)`, `1 + N` for an SDK allowed `N` retries, or the engine's maximum[^pydantic-docs-retries] Each model in a `ModelFallback` chain gets that budget again, so a chain of `F` models allows `F` times as many — give the models before the last one a smaller budget to make fallback happen sooner[^pydantic-docs-retries]

The one documented exception is a streamed Google long decode on `google-genai` 2.31.0 and later, whose SDK can send a later request that fails up to four times over its own budget[^pydantic-docs-retries] Setting `max_retries=0` matters even for errors you expect only the transport to see: the Anthropic and Groq SDKs retry *any* exception the HTTP client raises, including the `HTTPStatusError` a `validate_response` raises after the transport's last attempt, so a 503 a transport stopped by `stop_after_attempt(3)` gives up on goes on the wire 9 times under the SDK's default 2 retries, and 12 times for a streamed Google long decode[^pydantic-docs-retries]

## Recovery scopes compared

What a layer re-attempts decides when to reach for it[^pydantic-docs-retries] Retrying the same model suits transient failures — the next attempt sends the same request, so the prompt cache earlier requests built usually still applies and the behavior and price stay the same[^pydantic-docs-retries] Falling back switches to a different model for a provider that stays down or rejects the request, and the next model usually starts without that prompt cache, can answer differently and is priced differently[^pydantic-docs-retries] Correcting a tool call or the output is neither: the request succeeded and the model is asked to do better[^pydantic-docs-retries]

| Scope | Cost of another attempt | Message history | Counts against | How you see it |
| --- | --- | --- | --- | --- |
| Transport | Another HTTP request plus the wait | Nothing | The stop strategy and the request's `request_timeout`; each attempt gets a fresh `timeout` | An HTTPX span per attempt under HTTPX instrumentation[^pydantic-docs-retries] |
| Provider SDK | The same, with the SDK's own wait | Nothing | `max_retries` and the request's `request_timeout` | An HTTPX span per attempt plus SDK logging; the agent sees only the final response or error[^pydantic-docs-retries] |
| Durable step | The whole model request again, including its SDK and transport retries | Nothing — the engine records the attempt that succeeded | The engine's retry policy, unlimited by default on Temporal | The engine's own history[^pydantic-docs-retries] |
| Same model | Another request to the same model, usually reusing the prompt cache | Only the accepted response, with `failed_attempts` | `max_attempts` per model and at most 100 attempts per request step; **not** `request_limit`, though a rejected response's tokens and cost do count | `failed_attempts` and one `model request attempt` span per failure[^pydantic-docs-retries] |
| Fallback | A request to a different model with a different price and likely no prompt cache | Only the winning response, whose `model_name` names the model, with `failed_attempts` | One attempt per chain member with its own SDK and transport retries; not `request_limit` | `failed_attempts`, the attempt spans, and a `FallbackExceptionGroup` when every model fails[^pydantic-docs-retries] |
| Correction (tool, output, hook `ModelRetry`) | Another model request carrying the feedback | A retried `ToolReturnPart` or a `RetryFeedbackPart`, which stays in history for a later run that reuses it | The tool or output budget, and also `request_limit` and the token and cost limits | The message history and the `pydantic_ai.tool.retry.*` span attributes[^pydantic-docs-retries] |
| Run restart | Everything the run did, again | A new run with only the history you pass it | Your own code; each run starts with fresh retry budgets and usage limits | A separate agent run span[^pydantic-docs-retries] |

## What is never retried

Four things fall outside every layer above[^pydantic-docs-retries]:

- **`prepare` callbacks.** An exception from a per-tool `prepare=`, from `PrepareTools`, or from a dynamic toolset propagates out of the run unchanged — including `ModelRetry`, which is not turned into a retry there. To hide a tool for a turn, return `None` instead of raising[^pydantic-docs-retries]
- **Exceptions other than `ModelRetry` and `ToolFailed`.** Anything else a tool raises propagates, unless a capability implements `on_tool_execute_error`, which sees it first and may return a replacement result or raise `ModelRetry`[^pydantic-docs-retries]
- **Control flow.** `ApprovalRequired` and `CallDeferred` are not errors: they end the run with a `DeferredToolRequests` output instead of propagating — except in a realtime session, which cannot pause and answers the model with an explanation instead[^pydantic-docs-retries]
- **Whole agent runs.** Nothing re-runs an agent for you. Pydantic Evals has its own `retry_task` and `retry_evaluators` for retrying an evaluation task, and because those sit outside the agent, a retried task starts with fresh tool and output budgets[^pydantic-docs-retries]

## Evidence and coverage

The package is `raw/core-concepts/retries/`, holding one `index.md` capture (`title: "Retries"`, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines, `domain: pydantic.dev`, `language: en`, content digest `sha256:0585554b`). There are no attachments, includes, imports, downloads or supporting files, and every external link on the page — the `RetryOnModelErrors`, `ModelFallback`, `TemporalDurability`, `UsageLimits`, `ModelSettings`, `ModelAPIError`, `ModelHTTPError`, `ModelFallback`, `RetryModelRequest`, `FallbackExceptionGroup`, `ToolReturnPart`, `RetryFeedbackPart`, `RetryInfo`, `ToolRetryCause`, `is_retry`, `ERROR_OUTCOMES`, `PrepareTools`, `ApprovalRequired`, `CallDeferred` and `DeferredToolRequests` API pages, the durable-execution engine pages for Temporal, DBOS, Prefect, AWS Lambda, Azure Durable Task, Absurd, pgtask and Render Workflows, the model pages for OpenAI, Anthropic, Google, Groq, Cohere, Mistral, TypeSafe, AWS Bedrock, Hugging Face and xAI, and the Pydantic Evals retry-strategies page — was read as a link, not followed[^pydantic-docs-retries]

## Limits

- The page names **no Pydantic AI version, author, publication date or licence**, so every default and error name here is version-unknown and the concept is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-retries]
- Its samples pin `openai:gpt-6.1-sol`, `anthropic:claude-sonnet-5-5`, `claude-sonnet-5-5` and `google:gemini-3.8-flash`, none of which another capture in this wiki corroborates[^pydantic-docs-retries]
- The multiplication formula is the vendor's, expressed in prose; no cap is stated for the `fallback × FallbackModel` combination beyond "it multiplies", and the 100-attempt ceiling is attributed to a "request step" without defining the step's boundary[^pydantic-docs-retries]
- Evidence class: **Reported** throughout, with **Synthesis** only where a reading is labelled as one. Nothing was installed, no agent run, no retry exhausted, no budget multiplied and no engine configured in this ingest.

## Relationships

- **Owns the map for** [transport retries](pydantic-ai-transport-retries.md), [provider SDK retries](pydantic-ai-provider-sdk-retries.md) and [same-model retries](pydantic-ai-retry-on-model-errors.md), which are the three wire-level layers this page only counts.
- **Is the recovery-scope comparison** that [model fallback](pydantic-ai-model-fallback.md) deferred as a link: one attempt per chain member, with its SDK and transport retries beneath it, and not `request_limit`.
- **Reconciles** [model API errors](pydantic-ai-model-api-errors.md), whose normalized categories are what `RetryOnModelErrors` chooses by and what a hand-written retry predicate excludes.
- **Bounds** the `request_limit` and `max_retries` rows of [run controls](pydantic-ai-run-controls.md): the usage limit covers `N` alone, while the time settings split across attempts and requests.
- **Feeds** [tool execution, retries and failures](pydantic-ai-tool-execution.md), which owns the tool-retry precedence ladder and per-tool counters that make up `N`'s correction terms.
- **Corrects the pointer in** [durable execution](pydantic-ai-durable-execution.md) and [Pydantic AI on Temporal](pydantic-ai-temporal.md): the stack's multiplication is defined here, and Temporal's unbounded `maximum_attempts=0` default is its `F`-like layer.
- **Counts an extra layer for** [batch processing](pydantic-ai-batch-processing.md), where a provider-side failure is resubmitted in a new batch up to `max_resubmissions` times.
- **Has its wall clock defined by** [Pydantic AI timeouts](pydantic-ai-timeouts.md): `timeout` is the start-to-close deadline of one attempt and `request_timeout` the schedule-to-close deadline of the whole request, so the product's worst case is bounded by the latter rather than by the number of attempts.

[^pydantic-docs-retries]: Pydantic Docs, "Retries" (<https://pydantic.dev/docs/ai/core-concepts/retries/>, `domain: pydantic.dev`, `language: en`, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/retries/index.md`, content digest sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56. §"The layers" (raw lines 26–42) for the nine-row table, the last-three-are-agent-retries rule, the invisible six, and the `max_resubmissions` batch layer; §"Retry multiplication" (44–55) for the `N`/`F`/`M`/`K` factors, the 18-request worked example and its 180-second worst case, the `FallbackModel`-inside-one-attempt rule and the `prepare_model_request` bookkeeping; the same section for `UsageLimits.request_limit`, `request_timeout`, `timeout` and `first_event_timeout`; §"Choosing one retry owner" (57–106) for the four-owner table, the SDK defaults, the Google long-decode exception and the Anthropic/Groq 9-and-12-wire-request cases; §"Recovery scopes compared" (107–119) for the scope table and the prompt-cache, price and history consequences; §"What is never retried" (857–861) for `prepare` callbacks, non-`ModelRetry` exceptions, `ApprovalRequired`/`CallDeferred` and Pydantic Evals' `retry_task`/`retry_evaluators`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence; nothing was installed or executed.
