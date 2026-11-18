---
type: Concept
title: OpenAI models in Pydantic AI
description: The OpenAI route in Pydantic AI — three API dialects behind three model prefixes, the provider and SDK client it builds, the image and audio formats it accepts, strict-schema limits, service-tier and moderation settings, and OpenAI's prompt-cache breakpoints, TTLs and write costs.
tags: [pydantic-ai, models, providers, openai, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
---

OpenAI is not one route in Pydantic AI but three, distinguished by the model-string prefix, and picking one decides what the rest of the page is even about: `openai:` speaks the Responses API by default, `openai-chat:` pins the legacy Chat Completions API, and `openai-decisions:` runs a GPT model as a decision model rather than a text generator[^pydantic-openai-2026] Everything below is the vendor's own OpenAI setup page for version-unknown Pydantic AI, so it is the detail behind the OpenAI row of the [model and provider directory](pydantic-ai-models-and-providers.md) rather than a replacement for it. The features that exist only on the default route — reasoning mode and context, server-side state, compaction, background mode, the Batch API and Responses WebSockets — are compiled separately in [OpenAI Responses API features](openai-responses-api-features.md), and the Decisions route in [OpenAI decision models](openai-decision-models.md).

## Three dialects behind one vendor

Install is `pip install "pydantic-ai-slim[openai]"` or the full `pydantic-ai`, and `OPENAI_API_KEY` is the only configuration the bare prefix needs; the default `base_url` is `https://api.openai.com/v1`[^pydantic-openai-2026] The same page also covers the OpenAI-flavored routes with their own providers — the ChatGPT-plan and Codex OAuth providers, and Azure OpenAI through `AsyncAzureOpenAI` — which are reachable from the same model classes but documented elsewhere.

| Prefix | Model class | API | Notes |
| --- | --- | --- | --- |
| `openai:` | `OpenAIResponsesModel` | Responses | The default; the only route with the Responses-only features |
| `openai-chat:` | `OpenAIChatModel` | Chat Completions | Legacy dialect; five settings reach OpenAI only here |
| `openai-decisions:` | `OpenAIDecisionsModel` | Decisions | Typed questions with probabilities instead of text |

Choosing the Chat dialect costs feature surface, and on the newest models it costs tools outright: GPT-6 models reject tools, output tools included, on Chat Completions while reasoning is on, so `OpenAIChatModel` raises a `ModelRequestRejectedError` before it sends such a request, which a [`FallbackModel`](pydantic-ai-model-fallback.md) treats like the API's own 400[^pydantic-openai-2026] The workarounds are narrow. `gpt-6-sol`, `gpt-6-luna` and `gpt-6.1-terra` take tools on Chat Completions with reasoning off — `thinking=False` sends `reasoning_effort='none'` — except that OpenAI documents tool calling for `gpt-6.1-terra` through Responses only, and `gpt-6.2-sol`, `gpt-6.2-astra`, `gpt-6.1-sol` and `gpt-6-astra` don't accept `'none'` at all[^pydantic-openai-2026] `OpenAIProvider` encodes this as the profile flag `openai_chat_function_tools_require_reasoning_off` for those model names, including through a custom `base_url`, so a proxy needs no change; another server that serves those names and does accept tools with reasoning turns the flag off in the model's profile[^pydantic-openai-2026] Use Responses whenever reasoning and tools have to coexist.

The five `ModelSettings` fields that only Chat Completions carries are `seed`, `presence_penalty`, `frequency_penalty`, `logit_bias` and `stop_sequences`; the Responses API accepts none of them, so they are dropped on the default `openai:` path[^pydantic-openai-2026]

## The provider and its client

`OpenAIProvider` can be constructed for its `api_key`, or handed a custom `AsyncOpenAI` client through `openai_client` to set `organization`, `project` or `base_url`; `AsyncAzureOpenAI` is a subclass, so the same constructor takes an Azure endpoint and API version[^pydantic-openai-2026] For rotating credentials, `api_key` also accepts an async callable that the OpenAI SDK calls before each request, with two consequences: batch processing refuses such a client, and Responses WebSockets send its requests over HTTP[^pydantic-openai-2026]

The SDK client retries on its own, independently of the agent's retry budgets — `max_retries=2` by default, so one model request can reach the network up to three times[^pydantic-openai-2026] It honours the `x-should-retry` response header and otherwise retries 408, 409, 429 and 5xx plus timeouts and connection errors, but not other 4xx responses such as 400 or 401; `max_retries=0` keeps the retry policy in your own transport, and `ModelSettings['max_retries']` changes the count per model, agent or run without building a client[^pydantic-openai-2026] The layering of SDK retries under agent retries is the multiplication covered in [model API errors](pydantic-ai-model-api-errors.md).

## What the dialects accept

**Images.** `OpenAIProvider` lists JPEG, PNG, GIF and WebP as the formats OpenAI models read, and OpenAI's API rejects the rest — HEIC, AVIF, BMP and TIFF — so an image of another type that a tool returns is sent as a note naming it[^pydantic-openai-2026] The list belongs to `OpenAIProvider`, not to OpenAI's API: pointing `OpenAIProvider(base_url=...)` at a server that reads more formats calls for `OpenAICompatibleProvider`, or for `profile=OpenAIModelProfile(supported_image_media_types=frozenset({...}))`[^pydantic-openai-2026]

**Audio.** Only Chat Completions takes audio input, and only for models with `audio` in their name such as `gpt-audio` and `gpt-4o-audio-preview`; the Responses API takes none[^pydantic-openai-2026] With another OpenAI model, audio in the prompt errors and audio a tool returns is replaced by a note, and only WAV and MP3 are accepted (`audio/wav`, `audio/mpeg`, and the `audio/x-wav` and `audio/mp3` spellings) — anything else raises a `UserError` naming its media type before an `AudioUrl` is even downloaded[^pydantic-openai-2026] OpenAI-compatible providers, Azure included, report audio input for every model because their names don't say which models take it, so the same profile-or-`OpenAICompatibleProvider` escape applies.

## Strict structured outputs

For ordinary, non-fine-tuned models on `OpenAIProvider` or `OpenAIChatGPTProvider`, `min_length` and `max_length` on string fields keep their bounds in strict structured outputs; fine-tuned `ft:` models get a conservative schema transformer because OpenAI documents extra Structured Outputs restrictions for them, and the Codex backend keeps its old handling because the stricter support has not been verified against it[^pydantic-openai-2026] Tuples split by arity: a one-item tuple such as `tuple[int]` stays strict through a typed array `items` schema, while a multi-item fixed tuple uses `prefixItems`, which OpenAI strict mode does not support — inferred strictness falls back to non-strict, and an explicitly strict `ToolOutput` or `NativeOutput` raises a `UserError` instead[^pydantic-openai-2026] The documented replacement for an exact item count is a bounded list:

```python
from typing import Annotated

from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    coordinates: Annotated[list[int], Field(min_length=4, max_length=4)]
```

OpenAI also caps nesting depth and object property count, and [rejects a strict schema over those limits](https://developers.openai.com/api/docs/guides/structured-outputs#objects-have-limitations-on-nesting-depth-and-size); `OpenAIProvider` therefore lets inferred strictness fall back to non-strict, which OpenAI accepts, while an explicit `strict=True` is sent as written and can fail server-side[^pydantic-openai-2026] The same rules reach function tool parameters in strict mode.

## Service tier

Latency and cost trade through the unified `service_tier` field or OpenAI's own `openai_service_tier`; both pass `'auto'`, `'default'`, `'flex'` and `'priority'` through unchanged, and the provider-specific field wins when both are set[^pydantic-openai-2026] `openai_service_tier` additionally accepts OpenAI's `'fast'`, the newer name for `'priority'`, and `'ultrafast'`, which OpenAI takes only on the Responses API over HTTP and WebSocket and only on supported models[^pydantic-openai-2026] The tier a request asked for is not the tier it got: OpenAI may downgrade, so the serving tier is recorded in `ModelResponse.provider_details['service_tier']` and the reported cost is calculated at that tier's prices[^pydantic-openai-2026]

## Prompt caching

OpenAI caches prompts implicitly for all supported models, so no setting or marker is needed and hits arrive through the normalized `cache_read_tokens` usage field[^pydantic-openai-2026] On GPT-5.6 and later the unified `ModelSettings.cache` setting — or the `Caching` capability — adds explicit caching on top: `cache=True` sends `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` and turns on `openai_cache_instructions`, while `cache='12h'` sends a 12-hour TTL on the Responses API only and snaps to `'30m'` on Chat Completions, as does every other retention; setting the provider fields yourself takes precedence[^pydantic-openai-2026] The framework-wide switch and its provider matrix are in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md); what follows is the OpenAI-specific machinery.

### Breakpoints and TTL

Retention before GPT-5.6 is set per request with `openai_prompt_cache_retention`, and defaults to the organization's data-retention configuration: `24h` without zero data retention, `in_memory` with it[^pydantic-openai-2026] On GPT-5.6 and later OpenAI deprecates that field in favour of the `ttl` in `openai_prompt_cache_options`, which is a *minimum* lifetime rather than a maximum — a prefix stays eligible for 30 minutes, or 12 hours with `'ttl': '12h'` on the Responses API, after its most recent write or reuse, and OpenAI may keep it longer[^pydantic-openai-2026] The TTL is request-wide and Pydantic AI ignores the generic per-marker `CachePoint.ttl` on OpenAI; `'12h'` is rejected with a 400 on Chat Completions[^pydantic-openai-2026]

GPT-5.6 and GPT-6 support implicit and explicit breakpoints on both APIs, with an implicit one created by default; to control the prefix precisely, insert `CachePoint` after the user content block that should end it[^pydantic-openai-2026] Three placement rules follow. A `CachePoint` that opens a user message marks the end of the *previous* message instead, such as the tool result before it, matching Anthropic and Bedrock. On the Responses API an assistant output cannot carry a breakpoint, so it lands on the closest earlier input, and one with no earlier content raises a `UserError`[^pydantic-openai-2026]

`openai_cache_instructions` caches instructions without the unified setting, placing its breakpoint after the last static instruction so dynamic instructions from `@agent.instructions` functions or toolsets sit outside the cached prefix; they still invalidate the conversation after them, which is what `on_change='append'` exists to avoid[^pydantic-openai-2026] Unlike Anthropic and Bedrock, OpenAI gives the appended instructions no second breakpoint — it keeps only a request's last four, so a second instruction breakpoint would evict the one after the static instructions, which is exactly the prefix a new conversation reads[^pydantic-openai-2026] On the Responses API the top-level `instructions` field cannot carry a breakpoint at all, so the instructions are sent as leading input messages instead, and that relocation degrades in four documented cases: any request continuing server-side state (`openai_previous_response_id`, `openai_conversation_id`, or compacted history) leaves the instructions in place and gets no breakpoint; with `openai_previous_response_id='auto'` that includes the first request; a response created with cached instructions must not later be continued through `openai_previous_response_id`, since its stored input carries them; and such requests still get OpenAI's implicit breakpoint, so what they lose is only the shared-instructions saving[^pydantic-openai-2026]

The budget is smaller than it looks. Caching needs a prefix of at least 1,024 tokens, and a shorter one is not cached even when marked; with `mode='implicit'` OpenAI writes one implicit plus up to three explicit breakpoints, with `mode='explicit'` up to four explicit and no implicit one, and a request over that keeps only the last four — which drops the instruction breakpoint first, because it is the earliest in the request[^pydantic-openai-2026]

### Cost and diagnostics

Writes and reads surface as `result.usage.cache_write_tokens` and `result.usage.cache_read_tokens`[^pydantic-openai-2026] For GPT-5.6 and later families OpenAI bills writes at 1.25× the uncached input rate with the 30-minute TTL and 2.5× with the 12-hour TTL, and `cache_write_tokens` does not distinguish the two — so a cost computed from usage prices 12-hour writes at the 30-minute rate[^pydantic-openai-2026]

`openai_prompt_cache_key` is no longer needed for hits on GPT-5.6 and later, because OpenAI routes to the cache automatically; on earlier models a stable key helps send same-prefix requests to the same cache, at a suggested ~15 requests per minute per key[^pydantic-openai-2026] Keys do not share prefixes, so a fresh key per request or conversation pays the write every time; leave it unset, or set one stable key per group you want cached separately, such as a customer[^pydantic-openai-2026]

Cache misses are explainable. Pydantic AI requests OpenAI's prompt cache diagnostics on GPT-5.6 and later with the Responses API on the OpenAI API itself — not Azure, OpenRouter or another compatible provider — comparing each request against the most recent OpenAI response in the history, and skipping the comparison after a standalone compaction response or a later compatible encrypted compaction that came from another provider or an endpoint without shared server state[^pydantic-openai-2026] The verdict sits in `provider_details['prompt_cache_diagnostics']`, for example `{'type': 'cache_hit'}` or `{'type': 'cache_miss', 'reason': 'model_changed', 'cache_missed_tokens': 4175, 'comparison_reusable_tokens': 4175}`; diagnostics are free, do not affect caching, work with `openai_store=False`, and are switched off with `openai_prompt_cache_diagnostics=False`[^pydantic-openai-2026]

## Moderation and safety identifier

Moderation is off by default on both APIs and runs on request input and output when enabled with `openai_moderation`, typically `{'model': 'omni-moderation-latest'}`; results land under `provider_details['moderation']` with `input` and `output` entries carrying the flagged status, per-category flags and scores, identically on the streaming and non-streaming paths except that Chat Completions nests each entry one level deeper under a `results` list[^pydantic-openai-2026]

`openai_safety_identifier` is sent on both APIs and sends nothing when unset; it should carry a hash of the end user's ID, since its purpose is letting OpenAI detect users violating usage policies without receiving identifying information[^pydantic-openai-2026] It is also the replacement for the `openai_user` field, alongside `prompt_cache_key`[^pydantic-openai-2026]

## Image generation

`ImageGenerator('openai:gpt-image-2', settings=OpenAIImageGenerationSettings(dimensions=(1280, 720), openai_quality='low', openai_output_format='jpeg'))` reaches OpenAI's Images API rather than a conversational Responses model, and accepts `BinaryImage` and `ImageUrl` as reference inputs[^pydantic-openai-2026] Its edit endpoint needs file content and refuses an `UploadedFile` provider file ID; transparent backgrounds depend on the model and need PNG or WebP output; provider-specific settings are forwarded as-is so newly supported values are not blocked by stale client-side checks[^pydantic-openai-2026] Two operational constraints: GPT Image models require a verified organization on a paid usage tier, and on an unverified one every request fails with a rate-limit error before anything generates; complex prompts can take up to two minutes[^pydantic-openai-2026] Per-provider geometry, editing and telemetry are in [image generation operations](pydantic-ai-image-generation-operations.md).

## Limits

- The source names **no Pydantic AI version** and no publication date, so the page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown[^pydantic-openai-2026]
- Model names such as `gpt-6.1-sol` and `gpt-image-2` are the source's; no model list, pricing page or rate-limit table was fetched.
- Nothing was installed, no model constructed, no request sent, no cache write measured and no image generated, so every claim is **Reported** — the 1.25×/2.5× write multipliers, the 1,024-token minimum and the ~15-requests-per-minute guidance are the docs' numbers reproduced, not measurements.
- **Synthesis**: the framework-level caching summary in [prompt caching](pydantic-ai-prompt-caching.md) lists retention tiers `'5m'`, `'30m'` and `'1h'` and never mentions `'12h'`, while this page documents only `'30m'` and `'12h'` for OpenAI — neither source states how the generic tier list maps onto OpenAI's accepted values, so the two are left unreconciled rather than merged.
- The structured-output section is a set of schema rules, not a schema reference: which exact nesting depth and property count OpenAI enforces is only linked.

## Relationships

- **Details** the OpenAI row of [Pydantic AI models and providers](pydantic-ai-models-and-providers.md), which defines the model/provider/profile triad this page instantiates.
- **Extends into** [OpenAI Responses API features](openai-responses-api-features.md), the features only the default `openai:` route offers, and [OpenAI decision models](openai-decision-models.md), the third dialect.
- **Raises** `ModelRequestRejectedError` locally when Chat Completions is asked for tools with reasoning, covered as a category by [model API errors](pydantic-ai-model-api-errors.md) and handled by [model fallback](pydantic-ai-model-fallback.md).
- **Supplies** the OpenAI mechanics behind [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).
- **Reaches** [Pydantic AI image generation](pydantic-ai-image-generation.md) through the `openai:` image-model prefix and its provider-specific settings.
- **Recorded in traces** as `pydantic_ai.transport` and the cache attributes that [Pydantic AI observability](pydantic-ai-observability.md) describes.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, 7,634 words as declared and 7,648 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Install" and §"Environment variable" (lines 11–57) for the extras, `OPENAI_API_KEY`, the `openai:` → `OpenAIResponsesModel` default and its `base_url`; lines 29–57 for the GPT-6 tools-with-reasoning rule, the `ModelRequestRejectedError` raised before sending, the per-model `thinking=False`/`'none'` exceptions, `gpt-6.1-terra`'s Responses-only tool calling, and the `openai_chat_function_tools_require_reasoning_off` profile flag; §"Configure the provider" (59–74) for `OpenAIProvider`, the async-callable `api_key` and its batch/WebSocket consequences; §"Custom OpenAI Client" (75–120) for `openai_client`, `AsyncAzureOpenAI`, the SDK's `max_retries=2` and its retry predicate, `x-should-retry`, `max_retries=0` and `ModelSettings['max_retries']`; §"Image input" (145–148) for the JPEG/PNG/GIF/WebP list, the rejected formats, the note for a tool-returned file and the profile/`OpenAICompatibleProvider` escape; §"Structured output schemas" (149–165) for the `min_length`/`max_length` rule, the `ft:` transformer, the unverified Codex backend, the single-item-tuple and `prefixItems` behaviour, the `UserError`, the bounded-list example and the nesting/property limits; §"Service tier" (183–190) for the two fields, the four shared values, precedence, `'fast'`/`'ultrafast'` and `provider_details['service_tier']`; §"Prompt caching" (191–265) for implicit caching, the GPT-5.6 unified-setting mapping and snapping, the minimum-lifetime TTL, `CachePoint` placement, the instruction breakpoint and its four degraded cases, the 1,024-token floor and four-breakpoint budget, retention and ZDR defaults, `cache_write_tokens`/`cache_read_tokens`, the 1.25×/2.5× write prices, `openai_prompt_cache_key`, and the diagnostics payload; §"Moderation" (266–287) for `openai_moderation`, `provider_details['moderation']` and the Chat nesting; §"Safety identifier" (288–295) for `openai_safety_identifier` and the `openai_user` replacement; §"Image generation" (121–144) for `ImageGenerator` with `gpt-image-2`, `OpenAIImageGenerationSettings`, the Images API, reference inputs, the edit-endpoint constraint, transparent backgrounds, the passthrough rule, the verified-organization requirement and the two-minute ceiling; §"Chat Completions API" (663–689) for the five Chat-only settings and the audio rules; §"OpenAI-compatible Models" (734–736). Evidence class: **Reported** — vendor documentation; nothing was installed, constructed, sent, generated or measured.
