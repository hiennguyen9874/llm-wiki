---
type: Concept
title: Pydantic AI model fallback
description: The two ways to keep an agent answering when a model fails — the in-loop ModelFallback capability and the standalone FallbackModel — with their triggers, response handlers, per-model settings, failed-attempt accounting and attempt spans.
tags: [pydantic-ai, models, errors, reliability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:22:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: models-overview-2026
    resource: ../raw/models/overview/index.md
    scope: ../raw/models/overview/
    kind: documentation
    revision: sha256:b0b88d61e84966c7b8b8d70207b0cf386810413968eaa0d0246ca6690ef10a66
    title: "Models and Providers"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

Pydantic AI has two fallback mechanisms with one trigger vocabulary: the `ModelFallback` capability, which swaps models inside the agent's own request loop, and `FallbackModel`, a model wrapper for direct model requests and standalone models[^models-overview-2026] The distinction is not cosmetic — a capability sees the model that will serve each attempt and can prepare the request for it, each attempt is batched on its own model, and under durable execution each attempt becomes its own durable model operation, whereas the wrapper knows nothing about the surrounding agent[^models-overview-2026] What both share is `fallback_on`: a policy list that decides on exceptions **and** on the content of a successful response, which is how a truncated answer or a failed native tool call triggers a switch that no status code would report[^models-overview-2026] The categories being caught are defined in [model API errors](pydantic-ai-model-api-errors.md).

## Two mechanisms, one policy

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ModelFallback

agent = Agent('openai:gpt-6.1-sol', capabilities=[ModelFallback('anthropic:claude-sonnet-5-5')])
```

The agent's own model is attempted first, then each of the capability's models in turn, until one succeeds[^models-overview-2026]

| | `ModelFallback` capability | `FallbackModel` wrapper |
| --- | --- | --- |
| Where attempts happen | Inside the agent's request loop | In the model object |
| What capabilities see | The model that will serve the attempt, via `request_context.model` | Nothing — there is no per-attempt capability hook |
| Batching | Each attempt batched on its own model, and a resumed run whose batch failed moves on to the next model — see [batch processing](pydantic-ai-batch-processing.md) | Not applicable |
| Durable execution | Each attempt is a durable model operation of its own | — |
| Use for | Any agent | Direct model requests and standalone models |

The source documents a migration path from `FallbackModel` to the capability and sets the wrapper's `fallback_on`, `failed_attempts` and telemetry behaviour beside it, so the handler examples below apply to both[^models-overview-2026]

## What triggers a fallback

By default the trigger is `ModelAPIError`, which needs no configuration for the common case[^models-overview-2026] That default is deliberate and broad: every [error category](pydantic-ai-model-api-errors.md) falls back — rate limits, exhausted quota, unavailable or overloaded providers, server errors, connection failures, timeouts and rejected requests including context-window overflow — because another model or provider may accept a request, credentials or model name the first one rejected, and a larger context window may accept an input that overflowed another[^models-overview-2026] To narrow it, pass categories as `fallback_on=(ModelRateLimitError, ModelUnavailableError, ModelServerError)`[^models-overview-2026]

`fallback_on` accepts four kinds of entry, sync or async, and mixes them in one list[^models-overview-2026]:

- A tuple of exception types
- An exception handler: `lambda exc: isinstance(exc, MyError)`
- A response handler: `def check(r: ModelResponse) -> bool`
- A list combining all of the above

The kind is auto-detected from the **type hint on the first parameter**: annotated `ModelResponse` means a response handler, anything else — including untyped handlers and lambdas — means an exception handler[^models-overview-2026] Because hints are resolved at runtime, every annotated type in the signature must be imported for real rather than under `if TYPE_CHECKING:`; an unresolvable annotation raises `UserError` instead of silently degrading the handler into an exception handler[^models-overview-2026]

### Response-based triggers

A provider can answer 200 OK and still have failed semantically. Three worked cases in the source:

- **Truncated output**: a handler returning `reason in ('length', 'content_filter', 'error')` sends a length-limited answer to the backup model[^models-overview-2026]
- **A native tool that failed**: Google's native `web_fetch`, enabled with the `WebFetch` capability, can return success while its result carries a `url_retrieval_status` other than `URL_RETRIEVAL_STATUS_SUCCESS`; iterating `response.native_tool_calls` and rejecting that response hands the summary to Anthropic instead[^models-overview-2026]
- **An empty or thinking-only response**: without a handler this is re-prompted on the same model up to the output retry limit, so a response handler that rejects any response with no non-empty `TextPart`, `ToolCallPart` or `NativeToolCallPart` is what routes it to the backup[^models-overview-2026]

Two qualifications on that last case: the predicate is written for a text-output agent, and if the output type accepts other parts the predicate has to include them; and `ModelAPIError` must be added to the handler list explicitly, or API errors stop falling back once a custom `fallback_on` replaces the default[^models-overview-2026]

## Per-model settings

Fallback is the reason to configure settings per model rather than per agent: `FallbackModel` takes no settings of its own and uses whichever model answered, so a primary can run `ModelSettings(thinking='high', max_tokens=2000)` while the backup that only needs speed runs `ModelSettings(thinking='low', max_tokens=1000)`[^models-overview-2026]

## Context-window overflow

Overflow falls back by default, since a later model in the chain may have a larger window, and if the whole chain fails the overflow is inside the `FallbackExceptionGroup` where `except* ModelContextWindowExceededError` reaches it[^models-overview-2026] When no model has a larger window, the source advises excluding overflow from `fallback_on` so the oversized request is not sent to every candidate and instead propagates as itself[^models-overview-2026]

## Accounting for attempts

The answering response's `model_name` says which model produced it, its `model_id` becomes `fallback:openai:gpt-6.1-sol,anthropic:claude-sonnet-5-5`, and every attempt it moved on from appears in `failed_attempts` in order[^models-overview-2026] Each `ModelRequestAttempt` records[^models-overview-2026]:

- The model and provider it tried
- Whether it raised (the error rendered as `'ExceptionType: message'`) or returned a response a response handler rejected
- When it started, how long it took, and the usage the provider reported — an attempt that raised has none, because the provider reported none

The usage accounting is the part that changes a cost model. A rejected response was still generated **and billed**, so its tokens and cost are added to the run's `RunUsage` and count towards `UsageLimits` — the page's own example ends at `RunUsage(input_tokens=120, output_tokens=108, requests=1)` for 60+60 input and 100+8 output tokens across two models[^models-overview-2026] That usage stays on the attempt rather than being folded into the answering response's `usage` (60 in, 8 out), and the rejected response is not added to message history[^models-overview-2026] A fallback attempt is not a response the agent acted on, so it does not count towards `request_limit`[^models-overview-2026] If the accumulated usage exceeds a limit, `UsageLimitExceeded` is raised with the `FallbackExceptionGroup` as its `__cause__` — and the rejected responses' usage counts the same when the request instead ends by an uncovered error, cancellation or timeout[^models-overview-2026] When every model fails, the same attempts are on the exception group's `attempts`[^models-overview-2026]

## Traces

Under instrumentation the `chat` span describes the model that *answered* and ends OK; each abandoned attempt gets its own child span, `model request attempt <model name>`, ending with ERROR status — the same shape as a failed tool call inside a successful run[^models-overview-2026] On that span[^models-overview-2026]:

- An exception is recorded as an exception; a response rejected by a handler, or a refusal, carries its usage, cost and finish reason instead, as a `chat` span would
- `gen_ai.provider.name` and `gen_ai.request.model` name the model it tried
- `pydantic_ai.model_request.attempt` gives its zero-based position among the request's attempts
- With `include_content=False` the exception keeps only its type

The attempt span is created **after** the attempt failed, so spans the tried model opens itself — a decision model's `decide` span, for instance — sit beside it under the `chat` span rather than inside it[^models-overview-2026] That detail matters for anyone building span-tree queries against [observability](pydantic-ai-observability.md).

## Exception shape

If every model fails, `FallbackExceptionGroup` is raised containing all the exceptions in the order the models were tried[^models-overview-2026] Because it inherits Python's `ExceptionGroup`, existing middleware that catches `ModelAPIError` **misses it**, so a decorator has to switch to `except*` — and note that `except*` always delivers an `ExceptionGroup`, so re-raising propagates a group rather than the original type[^models-overview-2026] Catching `FallbackExceptionGroup` directly is the option when the all-models-failed case needs its own handling[^models-overview-2026]

## Limits

- The page names **no Pydantic AI version**, so when `ModelFallback` arrived, and whether it predates the v2.59.0 line in [run controls](pydantic-ai-run-controls.md), is unstated; the page is `draft` under the `pydantic-ai` domain rule[^models-overview-2026]
- The `ModelFallback` semantics beyond the three named consequences — whether it rewrites history, how it interacts with message history and output retries, and its own span names — are not stated[^models-overview-2026]
- Response handlers are described through examples only: no list of `finish_reason` values, no schema for `native_tool_calls`, and no statement of what happens when two handlers disagree[^models-overview-2026]
- The `ModelFallback` migration page, the model-fallback guide and the retrying-transport guide were read as links, not followed; the recovery-scopes comparison this capture defers to is compiled in [retry layers and multiplication](pydantic-ai-retry-layers.md)[^models-overview-2026]
- Evidence class: **Reported** — the printed `RunUsage` and `failed_attempts` come from the source's own sample output; no agent run, fallback triggered, span opened or usage measured in this ingest.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Switching between the Gemini API and Google Cloud" (raw lines 80–82) for the mutually rejected thought signatures, the documented `skip_thought_signature_validator` substitution in a `FallbackModel` that falls back from Google Cloud to the Gemini API, thinking sent as text, and the `canonical_system` values (`google`, `google-cloud`) that tell the transports apart whatever the base URL. Evidence class: **Reported** — vendor documentation; no fallback was executed.

## Relationships

- **Uses** [model API errors](pydantic-ai-model-api-errors.md), whose categories are the default trigger policy.
- **Introduced by** [models and providers](pydantic-ai-models-and-providers.md): a fallback chain has no single profile or context window, so capability checks inspect each candidate.
- **Recorded in** [observability](pydantic-ai-observability.md) through one ERROR-status attempt span per abandoned try.
- **Differs from** [durable execution](pydantic-ai-durable-execution.md) retries: retry re-attempts the same model and step, fallback changes which model serves the attempt.
- **Occupies one row of** [retry layers and multiplication](pydantic-ai-retry-layers.md), where a fallback attempt is one model request with its own SDK and transport attempts beneath it, is not bounded by `request_limit`, and multiplies with a `FallbackModel` nested inside it.
- **Composes with** [same-model retries](pydantic-ai-retry-on-model-errors.md): each model in the chain is retried before the request falls back to the next, and both write into `failed_attempts`.
- **Constrained by** [run controls](pydantic-ai-run-controls.md) `usage_limits` and `request_timeout`, which the failed attempts' usage counts against.
- **Depends on the deadline rules in** [Pydantic AI timeouts](pydantic-ai-timeouts.md): each chain member gets a fresh `request_timeout`/`first_event_timeout`, the expired ones land in `failed_attempts`, no fallback happens after a streamed response has started, and `RunTimedOut` is never a fallback trigger because it is cancellation rather than a model error.
- **Distinct from** [model concurrency](pydantic-ai-model-concurrency.md): a concurrency limiter queues requests, it does not re-route them.
- **Differs from** `FallbackModel` on file handling: with [file understanding](pydantic-ai-file-understanding.md) attached, `ModelFallback` judges each candidate by its own profile and hands the file to one that reads it, while a `FallbackModel` wrapper has no single profile and leaves files alone, so each model receives a note in its place. [Tool results and returned files](pydantic-ai-tool-results.md) reports the opposite reading of the wrapper — that each attempt's note is request-only, so a candidate that can read the file is sent it — and records the disagreement under its contradictions rather than choosing[^pydantic-docs-tools-advanced].
- **Recovers from** a rejected forced tool choice: on OpenRouter routes that return a 400 for forcing while the model reasons (Qwen3.8 Flash), the error is a `ModelRequestRejectedError`, which this page's wrapper falls back on — see [Pydantic AI tool choice](pydantic-ai-tool-choice.md)[^pydantic-docs-tools-advanced].
- **Does not need a uniform chain on Google**: a fallback **from Google Cloud to the Gemini API** works, because `GoogleModel` sends `skip_thought_signature_validator` in place of the other transport's thought signature — which both accept — and sends thinking as text, telling the transports apart by `ModelResponse.canonical_system` rather than by base URL or provider name[^pydantic-google-2026] That substitution is what makes the history portable at all; see [Google models in Pydantic AI](google-models-in-pydantic-ai.md).
- **Loses the reasoning channel across canonical systems**: [thinking and reasoning control](pydantic-ai-thinking.md) records that a `ThinkingPart` from a chain member on another canonical system cannot use the provider's signed or encrypted channel and is re-sent as text in thinking tags instead.

[^models-overview-2026]: Pydantic Docs, "Models and Providers", <https://pydantic.dev/docs/ai/models/overview/>, 6,420 words as declared, no publication date and no version named; local capture `raw/models/overview/index.md`, content digest sha256:b0b88d61. §"Fallback Model" (lines 345–425) for the `ModelFallback` example, the in-loop consequences (lines 358–360), the wrapper's scope and shared policy, and the default `ModelAPIError` trigger; lines 366–425 for `fallback_on`, the `fallback_model.py` output including `model_id`, `model_name` and `failed_attempts`; §"Per-Model Settings" (lines 426–459) for settings on each model; §"Exception Handling" (lines 460–485) and §"Context Window Overflow" (lines 486–506) for the exception group and the exclude-overflow advice; §"Failed attempts and usage" (lines 507–557) for `ModelRequestAttempt` fields, the `RunUsage(input_tokens=120, output_tokens=108, requests=1)` output and `RequestUsage(input_tokens=60, output_tokens=8)`, the billing and limit rules, `request_limit`, `UsageLimitExceeded` and line 556 for the `model request attempt <model name>` spans and their attributes; §"Response-Based Fallback" (lines 558–717) for the handler kinds, the type-hint auto-detection at line 569, the finish-reason, native-tool and empty-response handlers, and the `UserError` on unresolvable annotations; lines 651 for the re-prompt-without-a-handler rule and the include-`ModelAPIError` caveat; §"Combining Handlers" and §"Exception Handling in Middleware and Decorators" (lines 718–792) for the mixed list, the `ExceptionGroup` inheritance and the `except*` rewrite. Evidence class: **Reported** — vendor documentation and its own sample output; no run, no span opened.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Where a returned file is sent" (raw lines 70–99) for the claim that the note is request-only and each `FallbackModel` attempt decides for itself, so a candidate that can read the file is sent it; §"Provider Support" inside Tool Choice (512–532) for `ModelRequestRejectedError` on OpenRouter routes such as Qwen3.8 Flash that reject a forced tool choice while reasoning. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
