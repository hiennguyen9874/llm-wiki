---
type: Concept
title: Pydantic AI transport retries
description: The tenacity transports that re-send a failed HTTP request beneath the model client — installation, RetryConfig and validate_response, the Retry-After-aware wait strategy, connection-pool and proxy consequences, the error shape a retried failure finally raises, and the provider exceptions.
tags: [pydantic-ai, reliability, retries, transport]
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

**Reported, Pydantic AI version unspecified:** transport retries live below the model client, so a failed HTTP request is re-sent without the agent ever knowing — the layer is opt-in, and nothing retries there unless you install a retrying transport on the `httpx2` client you hand the provider[^pydantic-docs-retries] It is the right layer for rate limits, connection resets and 5xx responses because *you* decide which errors qualify, through a tenacity predicate plus a `validate_response` hook[^pydantic-docs-retries] The catch is that a transport replaces the client's own transport, so it also takes over the connection pool, and it cannot retry a streamed response that fails after the headers arrived[^pydantic-docs-retries]

## Setup

Tenacity is an extra, installed through the `retries` dependency group: `pip install 'pydantic-ai-slim[retries]'`[^pydantic-docs-retries] Build the client with `create_async_httpx2_client(transport=transport)` so it keeps the timeouts and user agent of the clients Pydantic AI builds, and turn the provider SDK's own retries off with `ModelSettings['max_retries']=0` so the transport is the only layer retrying rather than one whose attempts multiply with the SDK's[^pydantic-docs-retries]

```python
import httpx2
from tenacity import retry_if_exception_type, stop_after_attempt, wait_exponential

from pydantic_ai import Agent
from pydantic_ai.models import create_async_httpx2_client
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.retries import AsyncHTTPX2TenacityTransport, RetryConfig, wait_retry_after

def create_retrying_client():
    def should_retry_status(response):
        if response.status_code in (429, 502, 503, 504):
            response.raise_for_status()  # raises HTTPStatusError

    transport = AsyncHTTPX2TenacityTransport(
        config=RetryConfig(
            retry=retry_if_exception_type((httpx2.HTTPStatusError, httpx2.ConnectError)),
            wait=wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=1, max=60),
                max_wait=300,
            ),
            stop=stop_after_attempt(5),
            reraise=True,
        ),
        validate_response=should_retry_status,
    )
    return create_async_httpx2_client(transport=transport)

client = create_retrying_client()
model = OpenAIChatModel('gpt-6.1-sol', provider=OpenAIProvider(http_client=client))
agent = Agent(model, model_settings={'max_retries': 0})
```

`validate_response` is what turns an HTTP status into a retryable failure: without one, only network errors and timeouts are retried, because a 4xx or 5xx is a normal response to `httpx2`[^pydantic-docs-retries]

## Pool, proxy and limits

Because the transport you pass replaces the one the client would have built, it owns the connection pool[^pydantic-docs-retries] Without `wrapped`, a retrying transport sends its attempts through an `httpx2.AsyncHTTPTransport` it creates with the same pool limits as Pydantic AI's own clients — 1000 connections, up to 100 kept alive[^pydantic-docs-retries] Two consequences:

- HTTPX stops reading proxies from `HTTP_PROXY`, `HTTPS_PROXY` and `ALL_PROXY` once a client has a transport, so a proxied deployment must pass its own `wrapped` transport with `proxy=`[^pydantic-docs-retries]
- A `wrapped` transport you build yourself has HTTPX's default pool of 100 connections and 20 kept alive unless you set `limits` too, e.g. `wrapped=httpx2.AsyncHTTPTransport(proxy=..., limits=httpx2.Limits(max_connections=1000, max_keepalive_connections=100))`[^pydantic-docs-retries]

## Wait strategies

`wait_retry_after()` is a tenacity wait strategy that respects HTTP `Retry-After`[^pydantic-docs-retries] It parses the header from HTTP 429 responses in both the seconds form (`"30"`) and the HTTP-date form (`"Wed, 21 Oct 2015 07:28:00 GMT"`), prefers the `retry-after-ms` header that OpenAI and Anthropic send the way their SDKs do, falls back to a strategy you pass as `fallback_strategy=` when the header is absent or unparseable, and never waits beyond `max_wait`[^pydantic-docs-retries]

```python
from tenacity import wait_exponential
from pydantic_ai.retries import wait_retry_after

basic = wait_retry_after()
custom = wait_retry_after(
    fallback_strategy=wait_exponential(multiplier=2, max=120),
    max_wait=600,  # never more than 10 minutes
)
```

## Transport classes

| Class | Client | Status |
| --- | --- | --- |
| `AsyncHTTPX2TenacityTransport` | `httpx2.AsyncClient` — the recommended path for most uses | Current[^pydantic-docs-retries] |
| `HTTPX2TenacityTransport` | Synchronous `httpx2.Client` | Current[^pydantic-docs-retries] |
| `TenacityTransport`, `AsyncTenacityTransport` | Deprecated `httpx.AsyncClient`, for SDKs still on the legacy client (Groq, Cohere) | Deprecated in v2, removed in v3 with legacy client support[^pydantic-docs-retries] |

A retrying transport works with any provider whose `http_client` argument accepts an `httpx2.AsyncClient`; each provider page states the client type it takes[^pydantic-docs-retries] AWS Bedrock is the exception on both counts: it retries through boto3, configured as `Config(retries={'max_attempts': 5, 'mode': 'adaptive'})`[^pydantic-docs-retries]

The page also carries four worked patterns — a rate-limit client with `wait_retry_after` and `stop_after_attempt(10)`, a network-resilient client retrying `TimeoutException`/`ConnectError`/`ReadError`, and a custom predicate that retries 5xx but not 4xx — all differing only in the `retry=` predicate, the wait strategy and the stop count[^pydantic-docs-retries]

## What the error finally is

The transports re-raise the last exception once attempts run out, and the model raises it as a `ModelAPIError` like any other failed request: a status your `validate_response` rejected becomes a `ModelHTTPError` with that status and its error category, while a connection error or timeout becomes a `ModelConnectionError` or `ModelTimeoutError`[^pydantic-docs-retries] A fallback model moves on from any of them by default[^pydantic-docs-retries]

Before retrying or re-raising, both current transports read the response body, so the error keeps its `body` and gains what Pydantic AI parses from it: the category (an exhausted quota's `ModelQuotaExceededError`, an overloaded provider's `ModelOverloadedError`), `provider_error_code`, `provider_error_type`, and, for Google, the wait in `retry_after`[^pydantic-docs-retries] The bookkeeping that follows[^pydantic-docs-retries]:

- Each rejected attempt downloads its error body, and the completed download returns the connection to the pool
- A *success* status your `validate_response` rejects is closed without reading its body
- If reading an error body fails, the response is closed and your `validate_response` exception is still raised, with `body` `None`
- The deprecated `TenacityTransport`/`AsyncTenacityTransport` close a rejected response unread, so its error's `body` is `None` and only the status sets its category

Some model-level recoveries still run for a status the transport gave up on — Anthropic's retries for an expired code execution container and a stale thinking block — while others do not, so the fallback moves on instead: Azure content filters and OpenAI background mode are the examples[^pydantic-docs-retries]

## Building backoff outside a transport

When the backoff is hand-rolled, `ModelAPIError.retry_after` supplies the provider's own wait already parsed into seconds, and the normalized error categories say which failures a retry cannot fix — a `ModelRequestRejectedError` for a rejected API key or an unknown model[^pydantic-docs-retries] Those categories are compiled in [model API errors](pydantic-ai-model-api-errors.md)[^pydantic-docs-retries]

## Operating notes

The vendor's own list: start with 3–5 retries; use exponential backoff; cap the maximum wait; respect `Retry-After`; log retry attempts, which Logfire picks up automatically once `httpx2` is instrumented; and consider a circuit breaker for high-traffic applications[^pydantic-docs-retries] Retries add latency, so the application's total timeout has to account for them, retry rates are worth monitoring as a systemic-failure signal, and async transports serve concurrent requests better[^pydantic-docs-retries]

If the client also submits batches, `validate_response` must skip batch creates: the transport otherwise re-sends a create that failed with an error response, which can create a second batch[^pydantic-docs-retries] [Batch processing](pydantic-ai-batch-processing.md) records that hazard from the batch side[^pydantic-docs-retries]

## Evidence and coverage

The package is `raw/core-concepts/retries/`, one `index.md` capture (7,480 words as declared, 7,700 by local `wc -w`, 861 lines, content digest `sha256:0585554b`) with no attachments, includes or supporting files[^pydantic-docs-retries] Every external link — the `AsyncHTTPX2TenacityTransport`, `HTTPX2TenacityTransport`, `TenacityTransport`, `AsyncTenacityTransport`, `RetryConfig`, `wait_retry_after`, `create_async_httpx2_client`, `ModelAPIError`, `ModelHTTPError`, `ModelConnectionError`, `ModelTimeoutError`, `ModelQuotaExceededError`, `ModelOverloadedError`, `ContentFilterError`, `ModelRequestRejectedError`, `ModelSettings.max_retries`, `Agent`, `OpenAIChatModel`, `OpenAIProvider`, `AnthropicModel` and `AnthropicProvider` API pages, the tenacity and `httpx2` sites, the batch retrying-transports section, the Bedrock, Anthropic, Azure, OpenAI and Google model pages and the Logfire integration page — was read as a link, not followed[^pydantic-docs-retries]

## Limits

- The page names **no Pydantic AI version, date, author or licence**, so the transport names, the deprecated pair and the removal in v3 are version-unknown claims; the concept is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-retries]
- `RetryConfig`'s fields are shown but not enumerated; the default `wait`, `stop` and `retry` of a `RetryConfig` built without them are left to tenacity's documentation, which was read as a link, not followed[^pydantic-docs-retries]
- The retryable-status list is always the sample's `(429, 502, 503, 504)` or "4xx/5xx"; no provider-specific canonical set is given, and the `mode: 'adaptive'` Bedrock configuration is shown without its retry semantics[^pydantic-docs-retries]
- Evidence class: **Reported** — no transport was constructed, no request retried, no pool measured and no proxy exercised in this ingest.

## Relationships

- **Is one of the three wire layers** counted by [retry layers and multiplication](pydantic-ai-retry-layers.md), where `K` is this transport's stop strategy and where the one-owner rule says to give the SDK `max_retries=0` when this layer owns retrying.
- **Sits beneath** [provider SDK retries](pydantic-ai-provider-sdk-retries.md): the two stack rather than replace each other, so configuring one never disables the other.
- **Cannot replace** [same-model retries](pydantic-ai-retry-on-model-errors.md) for a stream that fails after the response headers arrive, which is the one case this layer cannot re-attempt.
- **Raises errors classified by** [model API errors](pydantic-ai-model-api-errors.md), whose categories and `retry_after` were originally read from the body this layer downloads.
- **Is skipped for batch creates by** [batch processing](pydantic-ai-batch-processing.md), whose `validate_response` exception rule prevents a second batch.
- **Hands retrying to boto3 on** AWS Bedrock, which takes no `httpx2` client — see [models and providers](pydantic-ai-models-and-providers.md).
- **Is traced per attempt as** an HTTPX span under [Pydantic AI observability](pydantic-ai-observability.md) when HTTPX instrumentation is on.

[^pydantic-docs-retries]: Pydantic Docs, "Retries" (<https://pydantic.dev/docs/ai/core-concepts/retries/>, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/retries/index.md`, content digest sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56. §"Transport retries" (raw lines 121–127) for the below-the-client placement, the opt-in rule, the tenacity/`httpx2` base, the Bedrock exception and the hand-rolled-backoff note; §"Installation" (129–141) for the `retries` extra; §"A retrying client" (142–197) for `create_async_httpx2_client`, the `max_retries=0` rule, the full `smart_retry_example.py` sample, the pool and proxy consequences and the batch-create warning; §"Wait strategies"/"wait_retry_after" (198–228) for the two header formats, `retry-after-ms`, `fallback_strategy`, `max_wait` and the sample; §"Transport classes" (229–286) for the async and sync classes and their samples; §"Common retry patterns" (287–402) for the rate-limit, network-error and custom-logic clients; §"Using with httpx2-compatible providers" (403–463) for the deprecated `TenacityTransport` pair and the OpenAI, OpenAI-compatible and Anthropic wiring; §"Best practices" (464–472); §"Error handling" (473–492) for the re-raised error mapping, body reading, unread success statuses, the deprecated transports' `body=None`, and the Anthropic/Azure/OpenAI recovery split; §"Performance considerations" (493–501); §"AWS Bedrock" (502–513) for the boto3 `Config`. Evidence class: **Reported** — vendor documentation naming no version; nothing was installed or executed.
