---
type: Concept
title: Pydantic AI direct batch requests
description: Batching without an agent — model_request_batch over a list of BatchRequest, its splitting and resubmission rules, which errors come back per request and which are raised, and the low-level Model.batch_encode/create/status/results/decode/cancel API for managing jobs yourself.
tags: [pydantic-ai, models, batching, direct-api]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:30:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-batch-2026
    resource: ../raw/core-concepts/batch/index.md
    scope: ../raw/core-concepts/batch/
    kind: documentation
    revision: sha256:53d4b659984b6eae8adbebe06233751631e17a8e05d828ffab66252c2232be08
    title: "Batch Processing"
---

**Reported, Pydantic AI version unspecified:** below the [BatchModelRequests capability](pydantic-ai-batch-processing.md) sit two agent-free routes to the same provider batch APIs[^pydantic-batch-2026] `model_request_batch(model, requests)` from `pydantic_ai.direct` sends a list of `BatchRequest`s through a model's batch API, waits for all of them, and returns, **in request order**, each request's response or the `ModelAPIError` it failed with[^pydantic-batch-2026] Underneath it, the `batch_*` methods on `Model` expose the same work as submit-now / collect-later primitives you can store and resume yourself[^pydantic-batch-2026] These are the batch members of the module covered in [direct model requests](pydantic-ai-direct-model-requests.md); the prices, provider windows and credential rules are the ones in [batch processing](pydantic-ai-batch-processing.md), because it is the same machinery.

## model_request_batch

Each `BatchRequest` carries its own messages, its own model settings and its own request parameters — tools, output schema — and is identified by a `custom_id` that the caller chooses, which is what lets results be matched back to inputs after provider-side reordering[^pydantic-batch-2026] Unlike the capability, this call has no batch-assembly stage to tune: requests are split into as many batches as the provider requires, by count and by size, and `max_requests` defaults to `None`, meaning the provider's own limit rather than the capability's 1,000[^pydantic-batch-2026] `poll_interval` and `max_poll_interval` mean what they mean on the capability, and requests a batch did not run, or that failed transiently, are resubmitted in new batches up to `max_resubmissions` times[^pydantic-batch-2026] The call returns once every request holds either a response or an error resubmitting would not fix[^pydantic-batch-2026]

The error split is the part to get right, because it decides what one failing request does to the caller:

| Failure | What happens |
| --- | --- |
| A request fails | Its error is returned **in its place** in the result list |
| Creating, checking or collecting the batch fails | The call **raises**, after cancelling the batches it created that have not ended |
| A check fails the way a live request is retried on | Tried again at the next poll before it counts |
| The call is cancelled | The batches it created that have not ended are cancelled too |
| A request sets `request_timeout` | `UserError` — one request in a batch cannot be timed out separately; a bounded call needs `asyncio.timeout` around it |

Those last two rows are the ones with teeth: a per-request timeout is silently inexpressible rather than approximate, and cancellation is clean-up for *this* call's batches only, consistent with the rule in [batch processing](pydantic-ai-batch-processing.md) that a batch another process submitted is left running[^pydantic-batch-2026] `model_request_batch` and the `batch_*` methods are also **not traced**, unlike `model_request`, so a call made this way leaves no `chat` span and no `batch` span under [instrumentation](pydantic-ai-observability.md)[^pydantic-batch-2026]

## The low-level Model batch API

The six methods divide the job along a serialization boundary, which is the point: everything that has to be stored to read results later is plain data[^pydantic-batch-2026]

| Method | Role |
| --- | --- |
| `batch_encode` | Turns a `BatchRequest` into the provider's encoded format |
| `batch_create` | Submits encoded requests, returns a `Batch` handle |
| `batch_status` | Returns the batch's current state — the handle to pass on once it has ended |
| `batch_results` | Iterates the ended batch's results |
| `batch_decode` | Turns one result back into a response, raising the request's `ModelAPIError` if it failed |
| `batch_cancel` | Asks the provider to cancel a batch |

The `Batch` handle holds only plain data, so it can be dumped with a `TypeAdapter` and stored together with the requests' messages, settings and parameters — which are needed later to decode the results[^pydantic-batch-2026] The documented loop is submit, store the handle, poll `batch_status` from a scheduled job, and on `status == 'ended'` decode each result paired with its request by `custom_id`, treating a raised `ModelAPIError` as that request's failure[^pydantic-batch-2026]

Three constraints come with the lower level. All requests passed to **one** `batch_create` call must share a `group` and fit within `Model.batch_max_requests` and `Model.batch_max_bytes`, or the call raises `UserError` — which is exactly the grouping and splitting `model_request_batch` performs for you[^pydantic-batch-2026] `batch_create` does **not** retry a failed submission, because the provider may have created the batch before the connection failed, so the provider's batches should be checked before resubmitting; a retrying transport will resend it anyway unless its `validate_response` skips batch creates[^pydantic-batch-2026] And resubmission is now yours: neither retrying failed requests nor handling a request the batch ended without a result for is done for you[^pydantic-batch-2026]

## Limits

- The capture names **no Pydantic AI version, publication date, author or licence**, so every symbol, default and error name here is version-unknown and this page is `draft` under the `pydantic-ai` domain rule[^pydantic-batch-2026]
- The `BatchRequest` field list, the `Batch` schema, the meaning of `group` beyond "must be equal", and the `Batch.status` value set are described in prose only; the API reference pages the source links are not in this repository.
- Unstated: whether `model_request_batch` accepts the same model-selection forms as `model_request` (a `Model`, a `<provider>:<model>` string, or an inferred one), what its own polling does between checks, and how it resolves the ambiguity of duplicate `custom_id`s.
- Nothing was installed, no request encoded, submitted, polled, decoded or cancelled and no result stored, so every claim is **Reported** and none **Observed** or **Reproduced**. One reading is **Synthesis**: the six methods plus a `TypeAdapter` are enough to rebuild the capability's own submit-and-collect cycle by hand, which is why the capability's resubmission, credential and retention rules apply to a hand-rolled job too.

## Relationships

- **Is the lowest of the three levels** in [batch processing](pydantic-ai-batch-processing.md): the capability above it, this direct call and `Model.batch_*` here, with the capability's own settings and failure rules inherited rather than re-specified.
- **Extends** [direct model requests](pydantic-ai-direct-model-requests.md), which owns the `pydantic_ai.direct` module's function list, the request and response objects and the instrumentation switch this route lacks.
- **Is superseded in convenience by** [pending batch responses](pydantic-ai-pending-batch-responses.md) for agent runs: a stored `Batch` handle and a stored pending-response history solve the same collect-later problem at different levels.
- **Defers provider batch shape to** [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), [OpenAI Responses API features](openai-responses-api-features.md) and [Google models in Pydantic AI](google-models-in-pydantic-ai.md): batch size ceilings, `custom_id` charsets, uploads and per-provider failure reporting.
- **Undoes the SDK's retry settings rather than the SDK's own attempts**: `batch_create` sends once on purpose, so a transport below the SDK can still duplicate a create — the retry layers each provider page records in [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md) and [Google models in Pydantic AI](google-models-in-pydantic-ai.md) sit underneath that decision.

[^pydantic-batch-2026]: Pydantic Docs, "Batch Processing" (<https://pydantic.dev/docs/ai/core-concepts/batch/>; 4,953 words as declared, 5,013 by local `wc -w` including frontmatter and markup; 487 lines; language `en`; no publication date, author, licence or Pydantic AI version), local capture `raw/core-concepts/batch/index.md`, content digest sha256:53d4b659. "Direct batch requests" (raw lines 338–381) for `model_request_batch`'s signature and return order, `BatchRequest`'s per-request messages/settings/parameters, the `custom_id` sample, the splitting rule with `max_requests=None`, the polling and resubmission settings, the per-request-versus-raised error split, the cancellation clean-up, the `request_timeout` `UserError`, and the tracing gap; "The low-level Model API" (382–446) for `batch_encode`/`batch_create`/`batch_status`/`batch_results`/`batch_decode`/`batch_cancel`, the `Batch`-as-plain-data rule with its `TypeAdapter` round trip, the `group` and size constraints on one `batch_create`, the no-retry rule with its provider-check caveat, and the by-hand resubmission and missing-result handling; "Details" (447–456) and "Retrying transports" (291–337) for the shared splitting and credential rules and the transport hazard; "Supported providers and APIs" (21–35) for the batch-capable model list; and the provider cross-references as linked, not followed. Evidence class: **Reported** — vendor documentation naming no version; no request encoded, submitted, decoded or cancelled.
