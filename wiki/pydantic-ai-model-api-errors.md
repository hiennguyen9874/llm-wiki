---
type: Concept
title: Pydantic AI model API errors
description: The eleven provider-neutral ModelAPIError categories, the provider signal that decides between them, the HTTP error surface a handler reads, and the rule that says which failures are worth retrying.
tags: [pydantic-ai, models, errors, reliability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:22:00Z }
stale_after: 2027-02-18
sources:
  - id: models-overview-2026
    resource: ../raw/models/overview/index.md
    scope: ../raw/models/overview/
    kind: documentation
    revision: sha256:b0b88d61e84966c7b8b8d70207b0cf386810413968eaa0d0246ca6690ef10a66
    title: "Models and Providers"
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
---

A failing provider request raises `ModelAPIError` rather than the vendor SDK's own exception, which stays reachable as `__cause__`, and the concrete class names what kind of failure it was so handling code never has to test the provider name[^models-overview-2026] The taxonomy is built for branching — wait versus do not wait, retry versus never retry, shrink the input versus switch model — and it is decided from the provider's own signal rather than the HTTP status alone[^models-overview-2026] This page covers classification and the evidence an error carries; [model fallback](pydantic-ai-model-fallback.md) consumes the same categories as its default trigger, and [model concurrency](pydantic-ai-model-concurrency.md) covers the rate limiting those categories report on.

## The eleven categories

| Exception | Raised when | Retry helps |
| --- | --- | --- |
| `ModelRateLimitError` | A rate limit was reached, e.g. HTTP 429 | Yes — after waiting |
| `ModelQuotaExceededError` | The account's quota, credits or billing is exhausted, e.g. HTTP 402 or OpenAI's `insufficient_quota` | No |
| `ModelUnavailableError` | The provider or model is temporarily unavailable, e.g. HTTP 503 or a gRPC `UNAVAILABLE` from the provider | Maybe |
| `ModelOverloadedError` | The provider is unavailable *because it is overloaded*, e.g. HTTP 529 or Anthropic's `overloaded_error`; a subclass of `ModelUnavailableError` | Maybe |
| `ModelServerError` | Another server error, e.g. HTTP 500, 502 or 504 | Maybe |
| `ModelConnectionError` | The request could not reach the provider, or its response could not be read; `phase` says whether the request may have reached the provider | Maybe |
| `ModelTimeoutError` | An attempt timed out at the transport layer; a subclass of `ModelConnectionError` | Yes |
| `ModelRequestRejectedError` | The provider rejected the request itself, e.g. HTTP 400, 413 or 422 — resending it unchanged will not succeed | No |
| `ModelContextWindowExceededError` | The input exceeds the model's context window; a subclass of `ModelRequestRejectedError` | No |
| `ModelAuthenticationError` | The provider rejected the credentials or forbids this request for them, e.g. HTTP 401 or 403; a subclass of `ModelRequestRejectedError` | No |
| `ModelNotFoundError` | The provider could not find the model, deployment or resource named, e.g. HTTP 404; a subclass of `ModelRequestRejectedError` | No |

A `request_timeout` deadline spanning all attempts raises `ModelRequestTimeout` instead of the transport-level `ModelTimeoutError`, which is the distinction between "this attempt timed out" and "the request's time budget is gone"[^models-overview-2026] Anything that does not fit raises a plain `ModelAPIError` or `ModelHTTPError`, as before[^models-overview-2026] Embedding models raise the same errors as chat models[^models-overview-2026]

## The provider's signal decides, not the status code

Status codes are ambiguous, so the category is assigned from the provider's error code or type where one exists and from the error message only when the provider offers nothing else[^models-overview-2026] The cases the source spells out:

- A 429 is a rate limit **unless** the provider says the quota is exhausted — the Gemini API names the exceeded quota in its `RESOURCE_EXHAUSTED` error, so its daily quota is a `ModelQuotaExceededError`[^models-overview-2026]
- Anthropic's tier spend cap is also a 429, but its `enforced_spend_limit_reached` error code makes it a `ModelQuotaExceededError`[^models-overview-2026]
- A 503 is only `ModelUnavailableError` unless the provider says it is **overloaded**, which promotes it to `ModelOverloadedError`[^models-overview-2026]
- A 400 is `ModelRequestRejectedError`, or a subclass when the provider says why: the Gemini API sends `API_KEY_INVALID` as a 400, which is a `ModelAuthenticationError`[^models-overview-2026]
- Exhausted credits, a reached spend limit or disabled billing are a `ModelQuotaExceededError` even when sent as a 400, as Anthropic and the Gemini API do[^models-overview-2026]

Every `ModelAPIError` also exposes the provider's `provider_error_code`, `provider_error_type` and `body` when available[^models-overview-2026]

## Before the stream opens or inside it

An error is reported the same way whether the provider sent it before a stream opened or inside an already open stream: an HTTP 503 from Bedrock and a `serviceUnavailableException` arriving inside a Bedrock stream both raise a `ModelHTTPError` with status 503 that is also a `ModelUnavailableError`, and the second sets `in_stream` so the two remain distinguishable[^models-overview-2026] That keeps streaming from being a second error-handling path.

## What an HTTP error carries

A 4xx or 5xx response raises `ModelHTTPError`, which is also an instance of its category when one applies, and exposes[^models-overview-2026]:

- `status_code` and the response `body`
- `headers`, a lowercase-keyed `dict[str, str]`, or `None` for providers that do not surface headers such as gRPC ones
- `retry_after` as a float, parsed from `retry-after-ms` or `Retry-After` including both delta-seconds and HTTP-date forms, or from the `RetryInfo` in a Google error body, or `None` when the provider said nothing; the plain `ModelAPIError` carries it too
- `provider_retry_hint`, from the `x-should-retry` header OpenAI and Anthropic send to say whether a retry may help
- `suggested_model_id`, a best-effort close match added to the message when OpenAI, Anthropic, Gemini, Bedrock or Groq reports an unavailable model identifier — guidance after the provider rejects, deliberately **not** local validation, so custom deployments and new model names keep working
- `hint`, guidance appended when the error has a known fix outside the request, such as the data-retention mode Bedrock requires for some models

A status a retrying transport gave up on carries its body and headers too[^models-overview-2026] A [custom model](pydantic-ai-models-and-providers.md) raises the same shape with `ModelHTTPError.for_category(ModelRateLimitError, status_code=429, ...)`, and the result is an instance of both classes with a class named after the category, so tracebacks, `repr()`, OpenTelemetry spans and `failed_attempts` all show `ModelRateLimitError`[^models-overview-2026]

## What to retry

The categories separate a failure that may go away from one that cannot be fixed by sending the same request again, so a hand-written retry predicate is two exclusions[^models-overview-2026]

```python
from pydantic_ai import ModelAPIError, ModelQuotaExceededError, ModelRequestRejectedError

def should_retry(error: ModelAPIError) -> bool:
    return not isinstance(error, ModelRequestRejectedError | ModelQuotaExceededError)
```

Because `ModelAuthenticationError`, `ModelNotFoundError` and `ModelContextWindowExceededError` subclass `ModelRequestRejectedError`, they are skipped too[^models-overview-2026] The same classification reaches the durability layer: under Temporal the activity does not retry them either, since they sit in `non_retryable_model_errors` by default[^models-overview-2026] For the request-level budgets that decide when a timeout is a timeout, see [run controls](pydantic-ai-run-controls.md).

The overflow case has a preferred fix: compaction keeps a conversation under the context window, and the source recommends it over waiting for `ModelContextWindowExceededError`, because model performance usually degrades well before the hard limit[^models-overview-2026]

## Limits

- The page names **no Pydantic AI version**, so the taxonomy's arrival version is unstated and the page is `draft` under the `pydantic-ai` domain rule[^models-overview-2026]
- Alignment with the v2.59.0 error-category snapshot on [run controls](pydantic-ai-run-controls.md) is unresolved rather than asserted: that source listed six categories and named no `ModelOverloadedError`, `ModelConnectionError`, `ModelTimeoutError`, `ModelRequestRejectedError`, `ModelAuthenticationError`, `ModelNotFoundError` or `ModelRequestTimeout`, and whether these predate or postdate v2.59.0 is not stated anywhere in this capture (**Synthesis** from the two sources)[^models-overview-2026]
- Which providers' codes map to `ModelOverloadedError` beyond Anthropic's, and whether every category is reachable on every provider, is not enumerated[^models-overview-2026]
- Evidence class: **Reported** — no provider was called, no error constructed or raised, and no retry executed in this ingest.

## Relationships

- **Refines** [run controls](pydantic-ai-run-controls.md), which records the same taxonomy at the level the v2.59.0 release tour showed.
- **Triggers** [model fallback](pydantic-ai-model-fallback.md), whose default `fallback_on` is `ModelAPIError` and therefore every category here.
- **Consumed by** [durable execution](pydantic-ai-durable-execution.md) through `non_retryable_model_errors` on Temporal activities.
- **Classified for** [retry layers and multiplication](pydantic-ai-retry-layers.md): these categories decide which layer can fix a failure, and `RetryOnModelErrors.retry_on` chooses from them rather than from status codes — see [same-model retries](pydantic-ai-retry-on-model-errors.md).
- **Raised identically by** custom models in [models and providers](pydantic-ai-models-and-providers.md) via `ModelHTTPError.for_category`.
- **Mitigated by** [model concurrency](pydantic-ai-model-concurrency.md), which is how a rate-limit error is avoided rather than caught.
- **Raised locally, before any request**, by `OpenAIChatModel` when GPT-6 tools meet reasoning on Chat Completions — the case [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md) records, where a `FallbackModel` treats the pre-send `ModelRequestRejectedError` exactly like the API's own 400[^pydantic-openai-2026].
- **Raised identically by** embedders in [Pydantic AI embeddings](pydantic-ai-embeddings.md), so one `except` clause covers an agent run and an embedding call.

[^models-overview-2026]: Pydantic Docs, "Models and Providers", <https://pydantic.dev/docs/ai/models/overview/>, 6,420 words as declared, no publication date and no version named; local capture `raw/models/overview/index.md`, content digest sha256:b0b88d61. §"Handling Model API Errors" (lines 248–319) for the `ModelAPIError`/`__cause__` contract, the eleven-row category table and its parent classes, `ModelRequestTimeout` against `ModelTimeoutError`, the plain `ModelAPIError`/`ModelHTTPError` fallback, embedding-model parity, the 429/503/400/spend-limit precedence rules, `provider_error_code`/`provider_error_type`/`body`; line 272 for the pre-stream and in-stream parity, the Bedrock example and `in_stream`; the `handle_model_errors.py` sample for the `retry_after` attribute; line 318 for the `should_retry` predicate and the Temporal `non_retryable_model_errors` default; §"HTTP errors" (lines 320–344) for `status_code`, `body`, `headers`, `retry_after` parsing, `provider_retry_hint`, `suggested_model_id`, `hint`, the retrying-transport note and `ModelHTTPError.for_category`; the compaction recommendation and the "performance degrades before the hard limit" sentence in §"Handling Model API Errors". Evidence class: **Reported** — vendor documentation; nothing was raised, caught or retried.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Environment variable" (raw lines 29–57), the GPT-6-tools-on-Chat-Completions paragraph, for `OpenAIChatModel` raising `ModelRequestRejectedError` before sending and `FallbackModel` falling back on it as it would on the API's 400. Evidence class: **Reported** — vendor documentation; no error was raised or caught here.
