---
type: Concept
title: Google models in Pydantic AI
description: The Google route in Pydantic AI — one model class over two providers and three prefixes, thought signatures that do not cross the Gemini API and Google Cloud, the two service-tier wire shapes, the HTTP client deadline and retry layers, what Gemini reads, half-price Batch Mode, and the screening settings that only work on Google Cloud.
tags: [pydantic-ai, models, providers, google, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

Google is one route in Pydantic AI — `GoogleModel` over the [`google-genai`](https://pypi.org/project/google-genai/) SDK — but the route forks in two places that decide most of its behaviour: whether the client talks to the **Gemini API** (`GoogleProvider`, prefix `google:`) or **Google Cloud**, formerly Vertex AI (`GoogleCloudProvider`, prefix `google-cloud:`), and whether a request is *streamed*, because several Google features (Model Armor screening, logprobs) only work without streaming. This page is that route and its transport: which provider and prefix a string resolves to, what state survives a move between the two endpoints, and the settings that change what a request carries. The per-model thinking levels are compiled separately in [Google thinking levels](google-thinking-levels.md), the continuation-token output path in [Google long decode](google-long-decode.md), the decision dialect in [Google decision models](google-decisions-model.md), and Google's image models in [Pydantic AI image generation operations](pydantic-ai-image-generation-operations.md).[^pydantic-google-2026]

## One class, two providers, three prefixes

The install is `pip install "pydantic-ai-slim[google]"` or the full `pydantic-ai`, and the Gemini API needs only `GOOGLE_API_KEY` in the environment; the prefix then resolves the name, and a provider can be built by hand when the key should not come from the environment[^pydantic-google-2026]

```python
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

model = GoogleModel('gemini-3.8-flash', provider=GoogleProvider(api_key='your-api-key'))
```

| Prefix | Provider | Endpoint |
| --- | --- | --- |
| `google:` | `GoogleProvider` | Gemini API (Google AI Studio), `generativelanguage.googleapis.com` |
| `google-cloud:` | `GoogleCloudProvider` | Google Cloud, `*-aiplatform.googleapis.com`, formerly Vertex AI |
| `google-decisions:` | `GoogleProvider` | The Gemini API's Decisions API, with `GoogleDecisionsModel` — see [Google decision models](google-decisions-model.md) |

Google Cloud's own authentication — Application Default Credentials, a service account, an API key, and customizing location or project — lives on the separate Google Cloud page, which was read as a link and not followed, so this page records only that those four routes exist[^pydantic-google-2026]

**The gateway route is Google Cloud, not the Gemini API.** Both `gateway/google:<model>` and `gateway/google-cloud:<model>` reach Google through `GoogleCloudProvider` via the [Pydantic AI Gateway](pydantic-ai-gateway.md), so a Gemini-API-only feature — the source's example is `FileSearchTool` — needs the direct `GoogleProvider` instead[^pydantic-google-2026] The batch route below is unavailable through the gateway for the same reason.

## Thought signatures do not cross the two transports

The Gemini API and Google Cloud reject each other's thought signatures, even though both providers are named `google` on the wire[^pydantic-google-2026] `GoogleModel` therefore carries the history across: when history from one endpoint continues on the other — the source's case is a `FallbackModel` falling back from Google Cloud to the Gemini API — it sends the documented `skip_thought_signature_validator` signature in place of the other transport's, which both accept, and sends thinking as text[^pydantic-google-2026]

It decides which transport produced a response from `ModelResponse.canonical_system`, which it always sets: `google` for a Gemini API response and `google-cloud` for a Google Cloud one, **whatever the base URL**[^pydantic-google-2026] For history recorded before Pydantic AI stored that field, a first-party Gemini API or Google Cloud `provider_url` decides, and a history recorded through a proxy URL is still sent with its signatures to a model with the same provider name[^pydantic-google-2026] Google Cloud and the Gateway's Google route — which is Google Cloud — accept each other's signatures, so only the Gemini-API-versus-Cloud direction needs the substitution[^pydantic-google-2026] The general history-portability rules are in [models and providers](pydantic-ai-models-and-providers.md); the fallback mechanics are in [model fallback](pydantic-ai-model-fallback.md).

## Service tier: one field, two wire shapes

The unified `service_tier` field works on both Google subsystems, and `google_cloud_service_tier` is the finer Google Cloud control; when both are set the provider-specific field wins[^pydantic-google-2026] The unified field is deliberately limited to the safe PT-with-spillover variants on Google Cloud, so any other routing combination has to be set on the provider field[^pydantic-google-2026]

On the **Gemini API** the unified value is sent as the request's `service_tier` field[^pydantic-google-2026]:

| `service_tier` | Sent to the Gemini API |
| --- | --- |
| `'auto'` | Omitted — the server default |
| `'default'` | `'standard'` |
| `'flex'` | `'flex'` |
| `'priority'` | `'priority'` |

On **Google Cloud** the same field becomes HTTP routing headers, and `'flex'` and `'priority'` always pick the PT-with-spillover variant so a customer with Provisioned Throughput keeps using reserved capacity first[^pydantic-google-2026]:

| `service_tier` | Google Cloud routing headers | Effective behavior |
| --- | --- | --- |
| `'auto'` / `'default'` | none | PT first, then standard on-demand spillover |
| `'flex'` | `X-Vertex-AI-LLM-Shared-Request-Type: flex` | PT first, then Flex PayGo spillover |
| `'priority'` | `X-Vertex-AI-LLM-Shared-Request-Type: priority` | PT first, then Priority PayGo spillover |

`google_cloud_service_tier` takes six values, which is the full routing matrix[^pydantic-google-2026]:

| Value | Headers | Behavior |
| --- | --- | --- |
| `'pt_only'` | `X-Vertex-AI-LLM-Request-Type: dedicated` | Provisioned Throughput only |
| `'pt_then_flex'` | shared-request `flex` | PT when quota allows, then Flex PayGo |
| `'pt_then_priority'` | shared-request `priority` | PT when quota allows, then Priority PayGo |
| `'on_demand'` | request-type `shared` | Standard on-demand only |
| `'flex_only'` | request-type `shared` + shared-request `flex` | Flex PayGo only |
| `'priority_only'` | request-type `shared` + shared-request `priority` | Priority PayGo only |

After the request, `ModelResponse.provider_details.get('traffic_type')` reports which tier served it — for example `ON_DEMAND_FLEX` or `ON_DEMAND_PRIORITY` — when the API returns it[^pydantic-google-2026]

## The HTTP client carries a 20-minute deadline

Google providers use `httpx2` by default and accept a custom `httpx2.AsyncClient` through `http_client`; the client the providers create — including through the Gateway — has a **20-minute timeout**, because long-decode models need it[^pydantic-google-2026] A legacy `httpx.AsyncClient` is still accepted during Pydantic AI v2 but emits a deprecation warning and is slated for removal in v3[^pydantic-google-2026]

A client you pass is applied differently: `google-genai` uses that client's read timeout — or **600 seconds** if it has none — for every phase of each request, and a client built without a `timeout` inherits httpx's default of 5 seconds, which the providers warn about because it is too short for most model requests[^pydantic-google-2026] So a custom client for a long-decode model needs a read timeout of at least 20 minutes.

`GoogleModel` also tells Google how long the whole request may take with the `X-Server-Timeout` header: the client's read timeout, or 20 minutes if that is longer[^pydantic-google-2026] Two consequences: a read timeout only bounds the wait *between bytes*, so a response that streams longer than the header is not cut off by the server, and a per-request `timeout` does not change the header — send the header yourself in `extra_headers` to set a different server deadline[^pydantic-google-2026]

**A user-agent you send replaces Pydantic AI's** on `GoogleModel` and `GoogleImageGenerationModel` requests, in any spelling, including one set on a client you pass; `google-genai` prefixes its own label, so it goes out as `google-genai-sdk/… gl-python/… <your value>`[^pydantic-google-2026] If the client spells the header other than `user-agent` — as in `HttpOptions(headers={'User-Agent': …})` — `google-genai` keeps its own lowercase `user-agent` beside it, so the value goes out on two lines[^pydantic-google-2026]

## Retries: the SDK does not retry by default

`google-genai` does not retry transient HTTP errors, so `GoogleProvider` and `GoogleCloudProvider` take a `retry_options: HttpRetryOptions` — attempts, initial and maximum delay, and status codes — which is passed through to the SDK's `HttpOptions.retry_options`[^pydantic-google-2026] The source's example sets four attempts, a one-second initial delay, a 60-second cap and the status list 408, 429, 500, 502, 503, 504.

`ModelSettings['max_retries']` overrides the number of attempts for a model, agent or run while keeping the delays and status codes set in `retry_options`; without `retry_options` the SDK's own defaults apply — a first delay of one second and the same six statuses[^pydantic-google-2026] The layered retry accounting in [model API errors](pydantic-ai-model-api-errors.md) applies here too.

One Google-specific signal is worth knowing: when an error carries no `retry-after-ms` or `Retry-After` header, `ModelAPIError.retry_after` is read from the `google.rpc.RetryInfo` detail in its **body**, including for an error chunk inside a stream and for a status a retrying transport gave up on[^pydantic-google-2026] Temporal waits that long before retrying a model activity, and your own backoff can read it; the SDK's `retry_options` and the unified `wait_retry_after` read only headers, so they see nothing there[^pydantic-google-2026]

## Batch Mode: half price, Gemini API only

`GoogleModel` speaks the Gemini API's Batch Mode, which charges **50% of the standard price**[^pydantic-google-2026] A job targets one model, its requests are uploaded as a file of up to **2 GB** — which is what limits how many it can hold — and it **expires if it has not finished within 48 hours**[^pydantic-google-2026]

Three boundaries decide whether the route is usable. Batch Mode is not available on Google Cloud, which runs batch prediction jobs from Cloud Storage or BigQuery instead, and not through the [Pydantic AI Gateway](pydantic-ai-gateway.md), which routes Google models to Google Cloud — so it needs `GoogleProvider` and a Gemini API key[^pydantic-google-2026] Per-request `timeout` and `extra_headers` are unsupported, so those are configured on the client[^pydantic-google-2026] And retrieving a job needs the model that submitted it but **not the same API key**: any key of the project works[^pydantic-google-2026]

File lifetime follows who collects the result. The process that submitted a job deletes its file when it retrieves the results, so the file does not count against the project's storage; a job collected from another process — for instance from a stored `PendingModelResponse` history — leaves its file in place until Google expires it, because only the uploader knows it is safe to delete[^pydantic-google-2026]

Failures are reported per request. A job that fails or is cancelled **before writing any results** does not report which requests it held, so retrieving it raises the job's error as a `ModelHTTPError`, which `model_request_batch` reports for each of the job's requests and an agent run waiting on the job raises — unless the error is one that resubmitting may fix, such as a server error, in which case the requests are submitted again[^pydantic-google-2026] An expired job, which also writes no results, raises a **504** `ModelHTTPError` saying so, and its requests are resubmitted too[^pydantic-google-2026] The batching surface itself, with its capability, splitting and failure rules, is in [batch processing](pydantic-ai-batch-processing.md); Anthropic's Message Batches are in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md).

## Safety settings, Model Armor and logprobs

Three settings change what goes into or comes out of a request, and two of them are Google Cloud only without streaming[^pydantic-google-2026]

**Safety settings** are the request field `google_safety_settings`, a list of `HarmCategory`/`HarmBlockThreshold` pairs — the source's example blocks hate speech at `BLOCK_LOW_AND_ABOVE` — taken through `GoogleModelSettings`[^pydantic-google-2026]

**Model Armor** is a Google Cloud security service that screens prompts and responses for prompt injection, jailbreaking and sensitive-data leakage, configured with `google_model_armor_config` and a prompt and response template name[^pydantic-google-2026] The templates must be created in advance in the Google Cloud Console and must sit in the **same region as the model endpoint**; a block raises a `ContentFilterError`[^pydantic-google-2026] The limitation is the one to remember: screening works only with non-streaming requests, so under `agent.run_stream()` Google Cloud applies no Model Armor at all — the prompt is not screened and the response text is returned unscreened[^pydantic-google-2026] If streaming is required, pre-screen prompts with the `google-cloud-modelarmor` SDK before calling the agent[^pydantic-google-2026]

**Logprobs** come from `google_logprobs` and `google_top_logprobs`, and are readable from `provider_details['logprobs']` and `provider_details['avg_logprobs']` on the response[^pydantic-google-2026] They are supported only for **non-streaming requests on Google Cloud**[^pydantic-google-2026]

**Context caching** has its own setting, `google_cached_content`, which takes a pre-created cached-content resource name and adds nothing to the unified `cache` switch — see [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), which records why the Google row differs from OpenAI's and Anthropic's[^pydantic-google-2026]

## What Gemini reads

`GoogleModel` takes documents, images, audio and video[^pydantic-google-2026] Gemini reads JPEG, PNG, GIF, WebP, HEIC, HEIF, AVIF and BMP images, and on Google Cloud it also reads TIFF, which the Gemini API rejects[^pydantic-google-2026] Gemini 2.5 models do not read Word or Excel documents while Gemini 3 models do, and a file of any other type that a *tool* returns is sent as a note naming it rather than as the file[^pydantic-google-2026] How those profile flags decide that a different model has to describe the file first is in [file understanding](pydantic-ai-file-understanding.md).

YouTube video URLs can be passed directly as `VideoUrl` and are sent without downloading or uploading the video, and files uploaded through the Gemini Files API can be passed as `DocumentUrl(url=file.uri, media_type=file.mime_type)`[^pydantic-google-2026] Which URL types each model takes directly is tabulated in [multimodal input](pydantic-ai-multimodal-input.md); the `media_processing='AGENTIC'` mode that makes Gemini inspect video segments on demand is recorded there too.[^pydantic-google-2026]

## Limits

- The source names **no Pydantic AI version** and carries no publication date, so every API name, default and header here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-google-2026]
- All claims are **Reported**: no package was installed, no key supplied, no model constructed and no request, batch or stream sent, so the 20-minute timeout, the header spellings, the tier mappings and the batch limits are documentation, not measurements[^pydantic-google-2026]
- The source's **"Streaming cancellation" section is a heading with no body** (raw line 527), so this page records no streaming-cancellation behaviour for Google rather than inferring one[^pydantic-google-2026]
- Google Cloud authentication, location and project selection, and Model Garden setup are deferred by the source to a page that was read as a link, not followed, and is not in this repository, so the credential story is unread rather than summarised.
- The model names in the examples — `gemini-3.8-flash`, `gemini-4-argon`, `gemini-3.1-pro-preview` — appear in no other capture here, and the source's word count is 4,106 as declared against 4,177 by local `wc -w`.
- The provider-level retry defaults are the SDK's, quoted; no transient error was produced, and the `RetryInfo`-from-body path was not exercised.

## Relationships

- **Details the Google rows** of the provider directory in [models and providers](pydantic-ai-models-and-providers.md), which records how a `<provider>:<model>` string resolves at all and lists Google/Gemini API, Google Cloud and the Google decision model separately.
- **Feeds** [Google thinking levels](google-thinking-levels.md), [Google long decode](google-long-decode.md) and [Google decision models](google-decisions-model.md), which own the per-model behaviour this page only configures.
- **Shares its transport with** [model fallback](pydantic-ai-model-fallback.md), whose Google Cloud → Gemini API case is what the thought-signature substitution exists for, and with [Pydantic AI Gateway](pydantic-ai-gateway.md), whose Google routes are Google Cloud.
- **Raises** the errors catalogued in [model API errors](pydantic-ai-model-api-errors.md): `ModelHTTPError` for batches and label limits, `ModelAPIError.retry_after` from `RetryInfo`, `ContentFilterError` from Model Armor and safety blocks.
- **Half-price counterpart** of the Anthropic and OpenAI batch routes in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md) and [OpenAI Responses API features](openai-responses-api-features.md), with the difference that Google's is the only one that deletes its upload on collection.
- **Supplies the Google row** of [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md) and the Gemini input rules behind [multimodal input](pydantic-ai-multimodal-input.md) and [file understanding](pydantic-ai-file-understanding.md).

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, 568 lines, content digest sha256:827e1922. §"Install"/"Configuration" (raw lines 20–69) for the `pydantic-ai-slim[google]` extra, `GOOGLE_API_KEY`, the `google:` prefix and the explicit `GoogleProvider(api_key=...)`; lines 11–18 for `GoogleModel` over `google-genai`, the two providers and prefixes, the two Gateway routes using `GoogleCloudProvider`, and `FileSearchTool` requiring the direct Gemini API; lines 71–78 for the four Google Cloud authentication routes deferred to the Google Cloud page; §"Switching between the Gemini API and Google Cloud" (80–82) for the mutually rejected thought signatures, the `skip_thought_signature_validator` substitution, thinking sent as text, `canonical_system`, the pre-storage `provider_url` fallback, the proxy-URL case and Cloud/Gateway signature acceptance; §"Service tier" (84–137) for the unified and `google_cloud_service_tier` precedence, both mapping tables, the six routing values and `provider_details['traffic_type']`; §"Custom HTTP Client" (143–169) for `httpx2`, the 20-minute created-client timeout, the 600-second/5-second passed-client rules and warning, the `X-Server-Timeout` derivation, the per-request `timeout` caveat, the legacy `httpx.AsyncClient` deprecation and the user-agent replacement; §"HTTP Retries" (171–198) for the SDK's no-retry default, `HttpRetryOptions`, the `max_retries` override, the SDK defaults, and `retry_after` from `google.rpc.RetryInfo` with Temporal and header-only `wait_retry_after`; §"Batch API" (493–499) for the 50% price, 2 GB upload, 48-hour expiry, the Google Cloud and Gateway exclusions, the unsupported per-request timeout and headers, the retrieval-key rule, file deletion by the collecting process, and the failed/cancelled/expired `ModelHTTPError` and resubmission rules; §"Model settings"/"Safety settings" (302–389) for `google_safety_settings`; §"Logprobs" (391–419) for `google_logprobs`/`google_top_logprobs`, the non-streaming and Google Cloud limits and the `provider_details` keys; §"Model Armor" (421–451) for the service, `google_model_armor_config`, the console-created same-region templates, `ContentFilterError`, the streaming gap and the `google-cloud-modelarmor` workaround; §"Document, Image, Audio, and Video Input" (200–247) for the image formats, TIFF on Google Cloud only, Word/Excel by Gemini 3, the tool-returned-file note, the YouTube `VideoUrl` and the Files API upload; line 527 for the empty "Streaming cancellation" heading; §"Context caching" (453–491) for `google_cached_content` being separate from the unified `cache` setting. Evidence class: **Reported** — vendor documentation; nothing was installed, constructed, sent or billed.
