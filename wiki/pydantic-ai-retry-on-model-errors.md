---
type: Concept
title: Pydantic AI same-model retries
description: The RetryOnModelErrors capability — which transient error categories it re-requests the same model for, how max_attempts, retry_after and max_delay bound it, why it switches the SDK's own retries off, and what it records in failed_attempts.
tags: [pydantic-ai, reliability, retries, capabilities]
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

**Reported, Pydantic AI version unspecified:** `RetryOnModelErrors` is the retry layer the *agent* can see — it attempts the same model again when a request fails with an error that waiting may fix, and it is configured on the agent like any other capability[^pydantic-docs-retries] By default that means a rate limit, an unavailable or overloaded model, a server error or a connection error, the set `TRANSIENT_MODEL_ERRORS` lists[^pydantic-docs-retries] It is the vendor's recommended retry owner: it decides by normalized error categories rather than status codes, retries a stream that failed before producing any output, records every attempt where fallback records its own, and switches the provider SDK's retries off so its budget is the only one in play[^pydantic-docs-retries]

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import RetryOnModelErrors

agent = Agent('openai:gpt-6.1-sol', capabilities=[RetryOnModelErrors()])
# or, with a larger budget:
agent = Agent('openai:gpt-6.1-sol', capabilities=[RetryOnModelErrors(max_attempts=4)])
```

The capability is also nameable from a YAML or JSON [agent spec](pydantic-ai-agent-specs.md), which lists it among the built-in capabilities a spec can configure by string, because it takes no callable arguments.

## The contract

| Property | Behaviour |
| --- | --- |
| Decides by | The normalized `ModelAPIError` categories every model raises, not HTTP status codes; `retry_on` chooses which[^pydantic-docs-retries] |
| Waits | The error's `retry_after`, or an exponential backoff — never longer than `max_delay`, and never past the request's or the run's deadline[^pydantic-docs-retries] |
| Durable wait | On Temporal and DBOS the wait is durable: nothing runs while it lasts and a recovered run does not wait again[^pydantic-docs-retries] |
| Streams | Retries a stream that fails before any output, which a retrying transport cannot do once the response headers have arrived[^pydantic-docs-retries] |
| Records | Every attempt in the answering response's `failed_attempts`, in the same list model fallback uses[^pydantic-docs-retries] |
| Composes | Each model in a `ModelFallback` chain is retried before the request falls back to the next one[^pydantic-docs-retries] |
| Owns the budget | Sends with `ModelSettings['max_retries']=0`, so `max_attempts` is the number of requests actually sent; a `max_retries` you set yourself is kept[^pydantic-docs-retries] |
| Bounded by | `max_attempts` per model, at most 100 attempts per request step, and a `request_timeout` that covers its retries of a model *and* the waits between them[^pydantic-docs-retries] |

The `max_attempts` ceiling is that of the request step rather than of the capability alone: a capability that raises `RetryModelRequest` draws on the same up-to-100 attempts, and the factor each model contributes to the multiplication in [retry layers](pydantic-ai-retry-layers.md) is this setting[^pydantic-docs-retries]

## How it relates to the other layers

`RetryOnModelErrors` occupies a distinct scope from the two wire layers below it and from fallback beside it[^pydantic-docs-retries] Compared with transport or SDK retries it can see the model request rather than the HTTP exchange, which is what lets it retry a stream before output and wait according to the provider's own `retry_after` in a way a durable engine can suspend[^pydantic-docs-retries] Compared with `ModelFallback` it never changes model: retrying the same model is for transient failures, where the next attempt sends the same request so the prompt cache built by earlier requests usually still applies and the behaviour and price stay the same[^pydantic-docs-retries]

That pair is why the vendor's one-owner table recommends it and asks for nothing else: no retrying transport, and no SDK retries because the capability already sends with `max_retries=0`[^pydantic-docs-retries] The one thing to keep configured is a bounded durable-engine policy — on Temporal, model errors become non-retryable in the activity automatically, so `maximum_attempts` remains as the bound for crashes and timeouts rather than for model failures[^pydantic-docs-retries]

## A policy of your own

To re-attempt the same model with logic the capability does not express, a capability can raise `RetryModelRequest` without a model from `on_model_request_error` or `after_model_request`[^pydantic-docs-retries] A `ModelRetry` raised from a model-request hook is a different thing: it draws on the **output** budget and leaves a `RetryFeedbackPart` in history, as [retry records](pydantic-ai-retry-history.md) describes[^pydantic-docs-retries]

## Evidence and coverage

The package is `raw/core-concepts/retries/`, one `index.md` capture (7,480 words as declared, 7,700 by local `wc -w`, 861 lines, content digest `sha256:0585554b`) with no attachments, includes or supporting files[^pydantic-docs-retries] Links read rather than followed: the `RetryOnModelErrors`, `TRANSIENT_MODEL_ERRORS`, `ModelResponse.failed_attempts`, `ModelAPIError.retry_after`, `RetryModelRequest`, `UsageLimits`, `ModelSettings`, `ModelFallback`, `Agent` and `AgentRetries` API pages, the retry-on-model-errors capability page, the model-fallback capability page, the custom-capabilities "model request attempts" section, the durable-execution pages for Temporal and DBOS, and the models overview's error-handling section[^pydantic-docs-retries]

## Limits

- The page names **no Pydantic AI version, date, author or licence**; the capability's own page is the link this capture points at for the full constructor, and was read as a link, not followed, so the complete `retry_on` vocabulary beyond the default transient set is unstated here. The concept is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-retries]
- `max_attempts`' default value is never given — the samples use the bare constructor and then `max_attempts=4`, so only "four is a deliberate increase" can be read[^pydantic-docs-retries]
- `max_delay`'s default and the shape of the exponential backoff are unstated, as is what the capability does with an error no category fixes[^pydantic-docs-retries]
- The samples pin `openai:gpt-6.1-sol`, which no other capture in this wiki corroborates[^pydantic-docs-retries]
- Evidence class: **Reported** — nothing was installed, no capability attached, no attempt made and no `retry_after` honoured in this ingest.

## Relationships

- **Owns the `F` factor** of [retry layers and multiplication](pydantic-ai-retry-layers.md), where its `max_attempts` multiplies with SDK and transport attempts beneath it.
- **Consumes** the categories in [model API errors](pydantic-ai-model-api-errors.md), which is where the transient-versus-permanent split and the `retry_after` parse come from.
- **Composes with** [model fallback](pydantic-ai-model-fallback.md): each model is retried before the request moves to the next, and both record into `failed_attempts`.
- **Switches off** [provider SDK retries](pydantic-ai-provider-sdk-retries.md) by sending with `max_retries=0`, which is the concrete form of the one-owner rule.
- **Adds the agent-visible layer that** [transport retries](pydantic-ai-transport-retries.md) cannot provide for a stream that fails after its headers.
- **Waits durably under** [durable execution](pydantic-ai-durable-execution.md), where Temporal's `maximum_attempts` stays as the crash and timeout bound rather than the model-error bound.
- **Is nameable from** [agent specs](pydantic-ai-agent-specs.md), among the serializable capability names.
- **Pairs with** [tool execution, retries and failures](pydantic-ai-tool-execution.md), which owns the tool-side correction budget a retried request can still trigger.

[^pydantic-docs-retries]: Pydantic Docs, "Retries" (<https://pydantic.dev/docs/ai/core-concepts/retries/>, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/retries/index.md`, content digest sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56. §"Retries" opening (raw lines 1–16) for the quickstart sample and the direct-request alternative; §"The layers" (26–42) for the same-model row and its `failed_attempts` record; §"Retrying the same model" (575–594) for `TRANSIENT_MODEL_ERRORS`, the category-based `retry_on`, the `retry_after`/`max_delay`/deadline rule, the durable wait, the stream-before-output case, `failed_attempts` and composition with fallback, the `retry_on_model_errors_layer.py` sample, the `max_retries=0` ownership rule and the `request_timeout` coverage; §"Model fallback is not a retry" (595–600) for the `RetryModelRequest` route from `on_model_request_error`/`after_model_request`; §"Choosing one retry owner" (57–106) for the recommendation, the Temporal non-retryable default and the bounded `maximum_attempts` advice; §"Recovery scopes compared" (107–119) for the prompt-cache and price argument for same-model retrying. Evidence class: **Reported** — vendor documentation naming no version; nothing was executed.
