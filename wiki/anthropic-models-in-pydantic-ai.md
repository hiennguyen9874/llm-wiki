---
type: Concept
title: Anthropic models in Pydantic AI
description: The Anthropic route in Pydantic AI — one prefix and model class over four transports, the max_tokens default derived from the model name, service tier, fast mode and data residency, what Claude reads, the half-price Message Batches API, and which state survives a change of platform.
tags: [pydantic-ai, models, providers, anthropic, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

Anthropic is one route in Pydantic AI — the `anthropic:` prefix, `AnthropicModel` over `AnthropicProvider` — but one model class reaches Claude through four transports, and the same class derives several of its defaults from the model *name* rather than from the request: `max_tokens`, fast-mode support and the token-counting surface all key off the name the page was told.[^pydantic-anthropic-2026] This page is that route and its transport. The Anthropic-specific behaviours that change how a request is *assembled* are compiled separately — prompt caching and prefix stability in [Anthropic prompt caching](anthropic-prompt-caching.md), task budgets and compaction in [Anthropic context management](anthropic-context-management.md), thinking-binding, forced tool choice and strict-schema limits in [Anthropic request constraints](anthropic-request-constraints.md), and the web and code-execution tools in [Anthropic server-side tools](anthropic-server-side-tools.md).

## One prefix, one class, one provider

The install is `pip install "pydantic-ai-slim[anthropic]"` or the full `pydantic-ai`, and `ANTHROPIC_API_KEY` is the only configuration the bare prefix needs[^pydantic-anthropic-2026] The prefix resolves the name, and `AnthropicModelName` lists the latest Claude ids for autocomplete, but any other model id the API accepts works too, so a new release needs no library upgrade[^pydantic-anthropic-2026]

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-sonnet-5-5')
```

`AnthropicModel('claude-sonnet-5-5')` with no prefix reaches the same route, and the `provider` argument takes a hand-built `AnthropicProvider(api_key=...)` when the key should not come from the environment[^pydantic-anthropic-2026]

**The HTTP client is httpx2.** `AnthropicProvider` accepts a custom `httpx2.AsyncClient` through `http_client`, and a legacy `httpx.AsyncClient` is *not* accepted: `anthropic` 1.0 is built on `httpx2` and rejects one at client construction[^pydantic-anthropic-2026] Pointing a client at a proxy means building it with the same library, not the older one.

**Two retry layers stack.** The `AsyncAnthropic` client the provider builds retries on its own — `max_retries=2` by default, so one model request can reach the network up to three times before application code sees an error[^pydantic-anthropic-2026] Three ways to move that count: pass `max_retries=0` when constructing the client yourself (for example as `anthropic_client=`), set `ModelSettings['max_retries']` per model, agent or run without building a client, or accept the default[^pydantic-anthropic-2026] The `ModelSettings` route also covers an `AsyncAnthropicBedrock` or `AsyncAnthropicVertex` client, which the agent cannot rebuild[^pydantic-anthropic-2026] How this multiplies with agent-level retry budgets is covered in [model API errors](pydantic-ai-model-api-errors.md).

## `max_tokens` is required, and its default comes from the name

Anthropic requires `max_tokens`, and thinking counts toward it[^pydantic-anthropic-2026] Leaving it unset does not mean "unlimited": Pydantic AI sends the model's maximum output and **streams the request behind the scenes**, because a response that long can take more than ten minutes[^pydantic-anthropic-2026] The named maxima are 64,000 on Claude Sonnet 4.5 and 128,000 on Claude Opus 5 and Claude Haiku 5.5; a model whose maximum isn't known gets 16,384, and models older than Claude Sonnet 4.5 get 4,096, because they reject a request whose input plus `max_tokens` exceeds the context window[^pydantic-anthropic-2026]

Two consequences follow. A `timeout` on such a request limits the wait **between streamed chunks**, not the whole response, so it does not behave like the timeout on a non-streamed request[^pydantic-anthropic-2026] And a `max_tokens` you set above a known maximum is silently lowered to it, which is what makes one setting portable across models — except where a beta raises the ceiling, such as `output-300k-2026-03-24` for Message Batches, which is left alone[^pydantic-anthropic-2026]

Because the default is keyed to the model name, a model reached through a Bedrock ARN or a custom deployment name is not recognized, and there `max_tokens` has to be set by hand[^pydantic-anthropic-2026]

## Service tier, reasoning effort and fast mode

Service tier controls latency and throughput, and Anthropic takes it through either the unified `service_tier` field or the provider's `anthropic_service_tier`, with the provider field winning when both are set[^pydantic-anthropic-2026] Anthropic's own values are `'auto'` and `'standard_only'`, and the unified field maps onto them rather than passing through:

| Unified `service_tier` | Sent to Anthropic |
| --- | --- |
| `'auto'` | `'auto'` — priority capacity when available |
| `'default'` | `'standard_only'` — forces the standard tier |
| `'flex'`, `'priority'` | Not part of Anthropic's tier model; silently ignored |

`anthropic_effort` tunes per-step reasoning depth and shares an `output_config` object with task budgets — see [Anthropic context management](anthropic-context-management.md)[^pydantic-anthropic-2026]

**Fast mode** trades price for output tokens per second: `anthropic_speed='fast'` enables it and Pydantic AI adds the required `fast-mode-2026-02-01` beta itself[^pydantic-anthropic-2026] The documented support is Claude Opus 4.6, 4.7, 4.8, 5 and 5.5 plus Claude Fable 5.2 and Mythos 5.2 — generally available on Fable 5.2, Mythos 5.2 and Opus 5.5, and a research preview on Opus 4.8 and Opus 5[^pydantic-anthropic-2026] On any other model `anthropic_speed='fast'` is ignored with a `UserWarning` rather than raising[^pydantic-anthropic-2026] Responses that ran fast carry `provider_details['speed'] == 'fast'`, and `ModelResponse.cost()`, `usage.cost` and usage limits then price the request at fast-mode rates from `genai-prices`[^pydantic-anthropic-2026]

## Data residency

`anthropic_inference_geo` decides where inference runs: `'us'` keeps it on US infrastructure, `'global'` lets it run in any available geography, and unset means the workspace's default applies[^pydantic-anthropic-2026] US-only inference is priced at 1.1× the standard rate, and that premium is **not** in `ModelResponse.cost()`, `usage.cost` or usage limits yet, so a US-pinned agent under-reports its bill[^pydantic-anthropic-2026] The setting is sent on the Claude API, Claude Platform on AWS and Anthropic-managed Claude on Google Cloud, Message Batches included, and where the request ran comes back in `provider_details['inference_geo']`[^pydantic-anthropic-2026]

Models older than Claude Opus 4.5, Sonnet 4.5 and Haiku 4.5 — those three included — reject the setting with a 400, which Pydantic AI raises rather than dropping[^pydantic-anthropic-2026]

## What Claude reads

Claude takes JPEG, PNG, GIF and WebP images, and an `image/jpg` file is sent as `image/jpeg`, the spelling the API accepts[^pydantic-anthropic-2026] An image of another type that a tool returns is sent as a note naming it rather than as the image[^pydantic-anthropic-2026] `AnthropicModel` also takes PDF and plain-text documents, and no audio or video[^pydantic-anthropic-2026] How the profile flags behind that decide which files another model must describe is in [file understanding](pydantic-ai-file-understanding.md).

## Four transports, and what survives a change of platform

Cloud platforms are reached by passing a platform SDK client to `AnthropicProvider` rather than by a different model class[^pydantic-anthropic-2026]:

| Platform | Client | Notes |
| --- | --- | --- |
| AWS Bedrock | `AsyncAnthropicBedrockMantle` | Anthropic's recommended path; uses the Messages API |
| AWS Bedrock, legacy | `AsyncAnthropicBedrock` | `InvokeModel` API with ARN-versioned model ids |
| Google Cloud Vertex AI | `AsyncAnthropicVertex` | Takes `region` and `project_id` |
| Microsoft Foundry | `AsyncAnthropicFoundry` | Takes an API key (`ANTHROPIC_FOUNDRY_API_KEY`) and a resource; Entra ID per Anthropic's docs |

History is designed to move between them. Every platform verifies Claude's thinking signatures and redacted thinking, so both are sent back whichever client produced them — including from `BedrockConverseModel` with a Claude model, and from a subclass of `AnthropicProvider` that only changes its `name`, since all of them share the `anthropic` canonical system — and search, fetch and advisor results travel with them[^pydantic-anthropic-2026]

The exception is provider-held objects. Code execution results, and the container and file ids they refer to, stay with the provider that ran them: Anthropic Files API file ids and code execution container ids are not sent through the `AsyncAnthropicBedrock`, `AsyncAnthropicVertex` or `AsyncAnthropicFoundry` clients, where `anthropic_accepts_file_and_container_ids` is `False`[^pydantic-anthropic-2026] The practical effects are that an `UploadedFile` raises a `UserError`, a `CodeExecutionTool`'s files are not uploaded, and no container from history is reused[^pydantic-anthropic-2026]

## The Batch API

`AnthropicModel` speaks Message Batches, which cost 50% of standard API prices and combine with prompt-caching discounts[^pydantic-anthropic-2026] A batch holds up to 100,000 requests or 256 MB, may mix models and settings, and a request's `custom_id` must be 1 to 64 letters, digits, `_` or `-`[^pydantic-anthropic-2026] Beta flags apply to a whole batch, so requests needing different ones — through `anthropic_betas` — go into separate batches[^pydantic-anthropic-2026]

Four limits matter before choosing the route. Message Batches are unavailable through Bedrock, Vertex AI, Microsoft Foundry and the [Pydantic AI Gateway](pydantic-ai-gateway.md), so they need `AnthropicProvider` and a Claude API key or auth token on the client[^pydantic-anthropic-2026] They do not support streaming, `anthropic_speed`, or `max_tokens=0` cache pre-warming[^pydantic-anthropic-2026] Transport timeouts and custom headers must be configured on the Anthropic client, because per-request `timeout` and `extra_headers` are unsupported, and a user-agent supplied in `extra_headers` is ignored in any spelling since Pydantic AI always sends its own[^pydantic-anthropic-2026] Retrieving a batch needs the endpoint and beta flags that submitted it, but not the same key: any key the workspace accepts works[^pydantic-anthropic-2026] The batching surface itself is in [batch processing](pydantic-ai-batch-processing.md), with the OpenAI route in [OpenAI Responses API features](openai-responses-api-features.md); concurrency and pacing are in [model concurrency](pydantic-ai-model-concurrency.md).

## Limits

- The page names **no Pydantic AI version** and carries no publication date, so every API name, default and beta flag here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-anthropic-2026]
- All claims are **Reported**: no package was installed, no key supplied, no model constructed and no request sent, so `max_tokens` defaults, fast-mode pricing, the residency premium and the batch limits are documentation, not measurements[^pydantic-anthropic-2026]
- The model maxima, the fast-mode model list and the data-residency model exclusions are the vendor's snapshot; Anthropic's own linked pages hold the current lists and were read as links, not followed[^pydantic-anthropic-2026]
- The 1.1× US-only price is stated but not reconciled against `genai-prices`, which the page says does not include it yet[^pydantic-anthropic-2026]

## Relationships

- **Details the Anthropic row** of the provider directory in [models and providers](pydantic-ai-models-and-providers.md), which records how a `<provider>:<model>` string resolves at all.
- **Depends on** [Anthropic prompt caching](anthropic-prompt-caching.md) for the cache prefixes whose cost dominates a long Claude agent, and on [Anthropic request constraints](anthropic-request-constraints.md) for what a request may carry at all.
- **Shares its platform clients with** [Anthropic context management](anthropic-context-management.md), whose on-demand compaction is documented, verified or unverified per transport, and with [Anthropic server-side tools](anthropic-server-side-tools.md), whose container ids do not cross those clients.
- **Raises** the errors catalogued in [model API errors](pydantic-ai-model-api-errors.md), including the 400 a residency setting gets on an older model.
- **Half-price counterpart** of the OpenAI batch route in [OpenAI Responses API features](openai-responses-api-features.md).
- **Readable only as documents and images by** [file understanding](pydantic-ai-file-understanding.md), which relies on the same profile flags for what Claude cannot take.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Install"/"Configuration"/"Environment variable"/"provider argument" (raw lines 11–56) for the install group, `ANTHROPIC_API_KEY`, the `anthropic:` prefix, `AnthropicModelName` autocomplete and the `provider` argument; §"Custom HTTP Client" (73–96) for the `httpx2.AsyncClient`, the rejected legacy `httpx.AsyncClient` under `anthropic` 1.0, the SDK's `max_retries=2` and the three ways to change it; §"Image input" (97–100) for the four image formats, `image/jpg` → `image/jpeg`, PDF and plain text, and no audio or video; §"Model settings" (101–129) for the required `max_tokens`, the 64,000/128,000/16,384/4,096 maxima, background streaming, the per-chunk `timeout`, the lowered-above-maximum rule and the name-keyed recognition caveat; §"Service tier" (120–129) for `anthropic_service_tier` precedence and the `'auto'`/`'default'`/`'flex'`/`'priority'` mapping; §"Cloud Platform Integrations" (130–192) for the Bedrock Mantle and legacy clients, `AsyncAnthropicVertex` and `AsyncAnthropicFoundry`; §"History across platforms" (193–198) for the verified thinking signatures, the shared `anthropic` canonical system, the travelling search/fetch/advisor results and the `anthropic_accepts_file_and_container_ids=False` consequences; §"Batch API" (577–582) for the 50% price, 100,000-request/256 MB ceiling, `custom_id` charset, beta granularity, the transports and settings it refuses, and the retrieval-key rule; §"Fast mode" (634–650) for `anthropic_speed`, the auto-added beta, the supported-model list and `provider_details['speed']`; §"Data residency" (651–669) for `anthropic_inference_geo`, the un-billed 1.1× premium, the sending transports, `provider_details['inference_geo']` and the 400 on older models; §"Task Budgets" line 206 for `anthropic_effort` sharing `output_config`. Evidence class: **Reported** — vendor documentation; nothing was installed, constructed, sent or billed.
