---
title: "OpenAI"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/models/openai/"
domain: "pydantic.dev"
language: "en"
description: "Use OpenAI GPT models with Pydantic AI via the Responses, Chat Completions or Decisions API, with native tools, background mode, conversations and compaction."
word_count: 7634
---

## Install

To use OpenAI models or OpenAI-compatible APIs, you need to either install `pydantic-ai`, or install `pydantic-ai-slim` with the `openai` optional group:

Terminal

```bash
pip install "pydantic-ai-slim[openai]"
```

## Configuration

To use OpenAI models with the OpenAI API, go to [platform.openai.com](https://platform.openai.com/) and follow your nose until you find the place to generate an API key.

## Environment variable

Once you have the API key, you can set it as an environment variable:

Terminal

```bash
export OPENAI_API_KEY='your-api-key'
```

The bare `'openai:'` prefix resolves to [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel), which uses the modern [Responses API](https://platform.openai.com/docs/api-reference/responses).

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')
...
```

To pin to the legacy [Chat Completions API](https://platform.openai.com/docs/api-reference/chat) instead, use the `'openai-chat:'` prefix, which resolves to [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel). GPT-6 models reject tools, output tools included, on Chat Completions while reasoning is on, so `OpenAIChatModel` raises a [`ModelRequestRejectedError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRequestRejectedError) before it sends such a request, which [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) falls back on as it would on the API’s 400. Use Responses whenever you need reasoning and tools together. `gpt-6-sol`, `gpt-6-luna` and `gpt-6.1-terra` also take tools on Chat Completions with reasoning off: `thinking=False` sends `reasoning_effort='none'`, although [OpenAI documents tool calling for `gpt-6.1-terra` through Responses only](https://developers.openai.com/api/docs/models/gpt-6.1-terra). `gpt-6.2-sol`, `gpt-6.2-astra`, `gpt-6.1-sol` and `gpt-6-astra` don’t accept `'none'`, so use the Responses API for tool calling with them. [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider) sets [`openai_chat_function_tools_require_reasoning_off`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_function_tools_require_reasoning_off) for these models, including through a custom `base_url`, as a proxy to OpenAI needs. Another server that serves these model names and accepts tools with reasoning turns it off with `openai_chat_function_tools_require_reasoning_off=False` in the model’s [profile](https://pydantic.dev/docs/ai/models/overview/#models-and-providers).

Or initialise the model directly with just the model name:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model)
...
```

By default, the model uses the `OpenAIProvider` with the `base_url` set to `https://api.openai.com/v1`.

## Configure the provider

If you want to pass parameters in code to the provider, you can programmatically instantiate the [OpenAIProvider](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider) and pass it to the model:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIResponsesModel('gpt-6.1-sol', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model)
...
```

For short-lived or rotating credentials, `api_key` also accepts an async callable that returns the key, which the OpenAI SDK calls before each request. [Batch processing](https://pydantic.dev/docs/ai/core-concepts/batch/#which-requests-share-a-batch) refuses such a client, and [Responses WebSockets](#responses-websockets) send its requests over HTTP.

## Custom OpenAI Client

`OpenAIProvider` also accepts a custom `AsyncOpenAI` client via the `openai_client` parameter, so you can customise the `organization`, `project`, `base_url` etc. as defined in the [OpenAI API docs](https://platform.openai.com/docs/api-reference).

The client retries failed requests on its own, independently of the agent’s retry budgets. It defaults to `max_retries=2`, so one model request can reach the network up to three times. It honors the `x-should-retry` response header; without that header, it retries status 408, 409, 429 or 5xx, plus timeouts and connection errors, but not other 4xx responses such as 400 or 401. Set `max_retries=0` to keep the retry policy in your transport alone, or set [`ModelSettings['max_retries']`](https://pydantic.dev/docs/ai/core-concepts/retries/#setting-the-sdk-retry-count-per-request) to change the count for a model, agent or run without building the client yourself. See [Retry multiplication](https://pydantic.dev/docs/ai/core-concepts/retries/#retry-multiplication) for how the layers stack.

custom\_openai\_client.py

```python
from openai import AsyncOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncOpenAI(max_retries=3)
model = OpenAIResponsesModel('gpt-6.1-sol', provider=OpenAIProvider(openai_client=client))
agent = Agent(model)
...
```

You could also use the [`AsyncAzureOpenAI`](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints) client to use the Azure OpenAI API. Note that the `AsyncAzureOpenAI` is a subclass of `AsyncOpenAI`.

```python
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIChatModel(
    'gpt-6.1-sol',
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)
...
```

For Grok deployments on Azure, see [Grok tool schemas](https://pydantic.dev/docs/ai/models/azure/#grok-tool-schemas) for the `AzureProvider` route and the explicit custom-profile workaround with `OpenAIProvider`.

## Image generation

Use [`ImageGenerator`](https://pydantic.dev/docs/ai/api/pydantic-ai/images/#pydantic_ai.images.ImageGenerator) with an `openai:` image model for direct generation and reference-image editing. This uses OpenAI’s Images API rather than a conversational Responses model:

openai\_image\_generation.py

```python
from pydantic_ai import ImageGenerator
from pydantic_ai.images.openai import OpenAIImageGenerationSettings

generator = ImageGenerator(
    'openai:gpt-image-2',
    settings=OpenAIImageGenerationSettings(
        dimensions=(1280, 720),
        openai_quality='low',
        openai_output_format='jpeg',
    ),
)
```

OpenAI accepts [`BinaryImage`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryImage) and [`ImageUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ImageUrl) reference inputs. Its image-edit endpoint requires file content and does not accept an [`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile) provider file ID. Transparent-background support varies by model and requires PNG or WebP output. Provider-specific settings are forwarded to OpenAI so newly supported values are not blocked by stale client-side checks. See the [image-generation guide](https://pydantic.dev/docs/ai/guides/image-generation/) for generation, editing, geometry, and normalized settings.

GPT Image models require a verified organization on a paid usage tier: on an unverified organization every request fails with a rate-limit error before anything generates. Complex prompts can take up to two minutes to process.

## Image input

`OpenAIProvider` lists JPEG, PNG, GIF and WebP as the images OpenAI models read. OpenAI’s API rejects others, such as HEIC, AVIF, BMP and TIFF. An image of another type that a tool returns is [sent as a note naming it](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance). The list applies to `OpenAIProvider` only. If you point `OpenAIProvider(base_url=...)` at another server that reads more formats, use [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/models/compatible-apis/#other-endpoints) for it, or pass `profile=OpenAIModelProfile(supported_image_media_types=frozenset({...}))` to the model.

## Structured output schemas

For ordinary, non-fine-tuned models used with [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider) or [`OpenAIChatGPTProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTProvider), which serves the same public OpenAI API, string fields with `min_length` or `max_length` keep those bounds in strict structured outputs. Fine-tuned `ft:` models use a conservative schema transformer because OpenAI documents additional Structured Outputs restrictions for those models. The strict tuple and string-bound support described here has not been verified against the Codex backend, so [`OpenAICodexProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_codex.OpenAICodexProvider) retains its existing schema handling.

A one-item tuple such as `tuple[int]` can remain strict: its single allowed element is represented as a typed array `items` schema. Multi-item fixed tuples such as `tuple[int, int, int, int]` still use `prefixItems`; OpenAI strict mode does not support that tuple schema, so inferred strictness falls back to non-strict mode and explicitly strict [`ToolOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.ToolOutput) or [`NativeOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.NativeOutput) raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). The same rules apply to function tool parameters in [strict mode](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#strict-mode). To keep an exact item count in strict mode, use a bounded list:

```python
from typing import Annotated

from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    coordinates: Annotated[list[int], Field(min_length=4, max_length=4)]
```

OpenAI also limits how deeply objects can nest in a strict schema and how many object properties it can have, and rejects a strict schema over [these limits](https://developers.openai.com/api/docs/guides/structured-outputs#objects-have-limitations-on-nesting-depth-and-size). With [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider), inferred strictness falls back to non-strict mode for a tool or output schema over them, which OpenAI accepts, and an explicit `strict=True` is sent as is.

## Model settings

You can customize model behavior using [`OpenAIResponsesModelSettings`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings):

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort='low',
    service_tier='flex',
)
agent = Agent(model, model_settings=settings)
...
```

### Service tier

OpenAI supports controlling the [service tier](https://platform.openai.com/docs/api-reference/responses/create#responses-create-service_tier) to trade off latency and cost. You can use the unified [`service_tier`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.service_tier) field or the provider-specific `openai_service_tier` field. Both accept `'auto'`, `'default'`, `'flex'`, and `'priority'`, passed through unchanged. `openai_service_tier` takes precedence over the unified field when both are set.

`openai_service_tier` also accepts OpenAI’s [`'fast'`](https://developers.openai.com/api/docs/guides/fast-mode), the newer name for `'priority'`, and [`'ultrafast'`](https://developers.openai.com/api/docs/guides/ultrafast-mode), which OpenAI only accepts on the Responses API, over both HTTP and WebSocket, and only on supported models.

OpenAI may serve a request on a different tier than the one requested, for example when a `'priority'` request is downgraded. The tier that actually served the request is stored in `ModelResponse.provider_details['service_tier']`, and the request’s cost is calculated at that tier’s prices.

### Prompt caching

OpenAI [caches prompts implicitly](https://developers.openai.com/api/docs/guides/prompt-caching#how-caching-works) for all supported models: no setting or marker is needed, and cache hits are reported through the normalized usage fields like `cache_read_tokens`. On GPT-5.6 and later, the unified [`ModelSettings.cache`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.cache) setting (or the [`Caching`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Caching) capability) also configures explicit caching: `cache=True` sends `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` and turns on `openai_cache_instructions` (described below) so separate conversations share the cached instructions. `cache='12h'` sends `'ttl': '12h'` instead on the Responses API, the only one that accepts it; on Chat Completions it snaps to `'30m'`, as does every other retention. Setting `openai_prompt_cache_options` or `openai_cache_instructions` yourself takes precedence over the unified setting. See [Caching](https://pydantic.dev/docs/ai/capabilities/caching/) for the cost trade-off, Pydantic AI’s prefix-stability guarantees and how to monitor cache efficiency. The unified setting works the same way with the Azure OpenAI v1 API, except that `AzureProvider` snaps `'12h'` to `'30m'`: see [Azure prompt caching](https://pydantic.dev/docs/ai/models/azure/#prompt-caching).

How long a cached prefix survives depends on the [retention policy](https://developers.openai.com/api/docs/guides/prompt-caching#cache-lifetime) in effect: `in_memory` typically keeps it for 5–10 minutes of inactivity, up to an hour, while `24h` can keep it for up to a day. On models before GPT-5.6, the unified setting adds nothing to the request, and the default retention follows your organization’s data-retention configuration — `24h` without zero data retention, `in_memory` with it. [`openai_prompt_cache_retention`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModelSettings.openai_prompt_cache_retention) sets it per request:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.5')
settings = OpenAIResponsesModelSettings(openai_prompt_cache_retention='24h')
agent = Agent(model, model_settings=settings)
...
```

For GPT-5.6 and later, OpenAI deprecates `prompt_cache_retention` in favor of the `ttl` in `openai_prompt_cache_options`, which sets a minimum lifetime rather than a maximum: a cached prefix remains eligible for reuse for 30 minutes (or 12 hours with `'ttl': '12h'`, on the Responses API only) after its most recent write or reuse, though OpenAI may retain it longer.

GPT-5.6 and GPT-6 models support OpenAI’s [implicit and explicit prompt cache breakpoints](https://developers.openai.com/api/docs/guides/prompt-caching#choose-a-caching-mode) with both the Responses and Chat Completions APIs. OpenAI creates an implicit breakpoint by default. To control the cacheable prefix precisely, insert [`CachePoint`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CachePoint) after the user content block that should end the prefix:

```python
from pydantic_ai import Agent, CachePoint
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

settings = OpenAIResponsesModelSettings(
    openai_prompt_cache_key='product-docs-v1',
    openai_prompt_cache_options={'mode': 'explicit', 'ttl': '30m'},
)
agent = Agent('openai:gpt-5.6-sol', model_settings=settings)

result = agent.run_sync([
    'Long-lived reference material...',
    CachePoint(),
    'Answer using the reference material.',
])
```

A `CachePoint` that opens a user message marks the end of the previous message instead, such as the tool result before it, the same as on Anthropic and Bedrock. On the Responses API, assistant output can’t carry a breakpoint, so it goes on the closest earlier input instead. One with no earlier content in the conversation raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError).

To cache the instructions without the unified setting, set `openai_cache_instructions`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

settings = OpenAIResponsesModelSettings(
    openai_prompt_cache_key='support-app:kb-v1',
    openai_cache_instructions=True,
)
agent = Agent(
    'openai:gpt-5.6-sol',
    instructions='Long-lived support policies...',
    model_settings=settings,
)

result = agent.run_sync('Where is order 1234?')
```

The breakpoint is placed after the last static instruction, so dynamic [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions) (from `@agent.instructions` functions or [toolsets](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/)) stay outside the cached prefix and don’t invalidate it when they change. They do invalidate the cached conversation after them, so for instructions that change mid-conversation use [`on_change='append'`](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes), and [keep untrusted text out of instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#untrusted-instruction-text). With no static instructions, it goes on the last [system prompt](https://pydantic.dev/docs/ai/core-concepts/agent/#system-prompts) instead, which is just as stable. Unlike on [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/#smart-instruction-caching) and [Bedrock](https://pydantic.dev/docs/ai/models/bedrock/#prompt-caching), the `on_change='append'` instructions after the static ones get no breakpoint of their own: OpenAI keeps only a request’s last four, so a second instruction breakpoint would push out the one after the static instructions first, which is what a new conversation reads. Leave `openai_prompt_cache_options` on its default `mode='implicit'` so OpenAI also keeps caching the growing conversation.

On the Responses API the top-level `instructions` field cannot carry a breakpoint, so the instructions are sent as leading input messages instead. Because a stored response keeps its input and replays it to the request that continues it, this has some limits:

- It only happens on requests that don’t continue server-side state. When [`openai_previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id) or [`openai_conversation_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id) is set, or the history has been [compacted](https://pydantic.dev/docs/ai/capabilities/compaction/), the setting leaves the instructions where they would otherwise go (normally the top-level field) and adds no breakpoint.
- With `openai_previous_response_id='auto'`, that includes the first request, which has no response to continue yet. Otherwise its relocated instructions would be replayed next to every later request’s own [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), which may belong to a different agent.
- Don’t continue a response created with `openai_cache_instructions` (which `cache=True` turns on) through `openai_previous_response_id` later on, since its stored input includes the instructions it was created with.
- Requests that continue server-side state still get OpenAI’s implicit breakpoint with the default `mode='implicit'`. What they give up is a breakpoint at the end of the instructions, which lets separate conversations share the cached instructions. Agent runs send the full message history by default, so this only affects runs that opt into server-side state.

Caching requires a prefix of at least 1024 tokens; shorter prefixes are not cached even when explicitly marked. With `mode='implicit'` (the default), OpenAI may write one implicit and up to three explicit breakpoints. With `mode='explicit'`, it may write up to four explicit breakpoints and no implicit breakpoint. If a request sets more breakpoints than that, OpenAI writes only the last four, and the instruction breakpoint is the earliest one in a request, so it is the first to be dropped. The TTL is request-wide, configured through `openai_prompt_cache_options`: `'30m'` (the default) or, on the Responses API only, `'12h'`. Chat Completions rejects `'12h'` with a 400. Pydantic AI ignores the generic per-marker [`CachePoint.ttl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CachePoint.ttl) value on OpenAI.

On GPT-5.6 and later, OpenAI routes requests to the cache automatically, so you don’t need `openai_prompt_cache_key` to get cache hits. Requests with different keys don’t reuse each other’s cached prefixes, so every new key pays the cache write again. Leave the key unset so all requests share a common prefix, or set one stable key per group you want cached separately, such as a customer. Don’t set a new key per request or conversation. On earlier models, a stable key helps OpenAI send requests with the same prefix to the same cache; OpenAI suggests about 15 requests per minute per key.

When OpenAI reports prompt cache writes, Pydantic AI exposes them as [`result.usage.cache_write_tokens`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage.cache_write_tokens). Cache reads are available as [`result.usage.cache_read_tokens`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage.cache_read_tokens). For GPT-5.6 and later model families, OpenAI bills cache writes at 1.25 times the uncached input token rate with the 30-minute TTL, and 2.5 times with the 12-hour TTL. `cache_write_tokens` doesn’t tell the two apart, so a cost calculated from usage prices 12-hour writes at the 30-minute rate.

To help explain cache misses, Pydantic AI requests OpenAI’s [prompt cache diagnostics](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics) on GPT-5.6 and later models with the Responses API on the OpenAI API itself (not Azure, OpenRouter or other OpenAI-compatible providers): each request compares itself against the most recent OpenAI response in the message history. It skips the comparison when that response is a [standalone compaction response](#message-compaction), or when a later compatible encrypted compaction came from another provider or from an endpoint that doesn’t share server state with this one. The result is in the response’s [`provider_details`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_details) under the `'prompt_cache_diagnostics'` key, for example `{'type': 'cache_hit'}`, or `{'type': 'cache_miss', 'reason': 'model_changed', 'cache_missed_tokens': 4175, 'comparison_reusable_tokens': 4175}` when the prefix couldn’t be reused. Diagnostics are free, don’t affect caching, and work with `openai_store=False`. To leave them off, set [`openai_prompt_cache_diagnostics`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_diagnostics) to `False`.

### Moderation

Both the Responses and Chat Completions APIs can run [moderation](https://platform.openai.com/docs/guides/moderation) on the input and output of a request. Moderation is off by default; enable it with `openai_moderation`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(
    openai_moderation={'model': 'omni-moderation-latest'}
)
agent = Agent(model, model_settings=settings)

result = agent.run_sync('Your prompt here')
moderation = (result.response.provider_details or {}).get('moderation')
```

When the response includes moderation results, they are stored under the `'moderation'` key of [`ModelResponse.provider_details`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.provider_details), with `input` and `output` entries each carrying the flagged status, per-category flags, and category scores.

With [`OpenAIChatModel`](#chat-completions-api), use [`OpenAIChatModelSettings`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModelSettings) instead. The results are surfaced the same way on both the non-streaming and streaming paths, except that the Chat Completions API nests each entry one level deeper, under a `results` list.

### Safety identifier

OpenAI uses a [safety identifier](https://developers.openai.com/api/docs/guides/safety-best-practices#implement-safety-identifiers) to detect end users who may be violating its usage policies. Set it with [`openai_safety_identifier`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModelSettings.openai_safety_identifier) on both the Responses and Chat Completions APIs; nothing is sent when it is unset. Pass a hash of the end user’s ID, such as their username or email address, so that no identifying information reaches OpenAI.

OpenAI is replacing the `user` field, which [`openai_user`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModelSettings.openai_user) sends, with `safety_identifier` and `prompt_cache_key`.

The features below are specific to the Responses API and only available on [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) (the default). For background on how the Responses API differs from Chat Completions, see the [OpenAI API docs](https://platform.openai.com/docs/guides/migrate-to-responses).

### Reasoning mode

The GPT-5.6 and GPT-6 families can use OpenAI’s [`standard` and `pro` reasoning modes](https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode). `standard` is the default; `pro` performs more model work to improve reliability on difficult tasks, at the cost of higher latency and token usage. The mode is independent of the reasoning effort: any combination of mode and effort is valid, and the unified [`thinking`](https://pydantic.dev/docs/ai/capabilities/thinking/) setting only ever influences the effort, so `pro` is used only when you set it explicitly.

Configure the mode with [`openai_reasoning_mode`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_mode); there is no separate `pro` model to select:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.6-sol')
settings = OpenAIResponsesModelSettings(openai_reasoning_mode='pro')
agent = Agent(model, model_settings=settings)
...
```

The setting is ignored on models that don’t support reasoning mode, per [`OpenAIModelProfile.openai_responses_supports_reasoning_mode`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_reasoning_mode).

### Reasoning context

Reasoning models can use OpenAI’s [reasoning context](https://developers.openai.com/api/docs/guides/reasoning#preserve-reasoning-across-calls) to control which prior-turn reasoning items are available to the model when sampling. `auto` defers to the model’s own default (OpenAI treats it exactly like not sending the field), `current_turn` makes only the active turn’s reasoning available, and `all_turns` renders compatible reasoning items from earlier turns into the next sample. `all_turns` requires access to earlier response items via [`previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id), a conversation, or replayed history; on a first request it behaves like `current_turn`.

Pydantic AI sends `all_turns` by default on models that support it, so that earlier-turn reasoning stays available without opting in — consistent with how prior thinking is sent back to other models. This renders earlier reasoning into each follow-up sample, which costs additional input tokens; set `auto` explicitly to defer to OpenAI’s own per-model default, or `current_turn` to keep earlier turns out of the sample.

Configure the context with [`openai_reasoning_context`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_context):

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.6-sol')
settings = OpenAIResponsesModelSettings(openai_reasoning_context='all_turns')
agent = Agent(model, model_settings=settings)
...
```

`auto` and `current_turn` are sent to any model that supports reasoning. `all_turns` is sent only to models whose profile sets [`OpenAIModelProfile.openai_responses_supports_reasoning_context`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_reasoning_context) (currently the GPT-5.4, GPT-5.5, GPT-5.6, and GPT-6 families); on other models it is ignored.

### Native tools

The Responses API has native tools that you can use instead of building your own:

- [Web search](https://platform.openai.com/docs/guides/tools-web-search): allow models to search the web for the latest information before generating a response.
- [Code interpreter](https://platform.openai.com/docs/guides/tools-code-interpreter): allow models to write and run Python code in a sandboxed environment before generating a response.
- [Image generation](https://platform.openai.com/docs/guides/tools-image-generation): allow models to generate images based on a text prompt.
- [File search](https://platform.openai.com/docs/guides/tools-file-search): allow models to search your files for relevant information before generating a response.
- [Computer use](https://platform.openai.com/docs/guides/tools-computer-use): allow models to use a computer to perform tasks on your behalf.

Web search, Code interpreter, Image generation, and File search are natively supported through the [Native tools](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/) feature.

Computer use can be enabled by passing an [`openai.types.responses.ComputerToolParam`](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/computer_tool_param.py) in the `openai_native_tools` setting on [`OpenAIResponsesModelSettings`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings). It doesn’t currently generate [`NativeToolCallPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.NativeToolCallPart) or [`NativeToolReturnPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.NativeToolReturnPart) parts in the message history, or streamed events; please submit an issue if you need native support for this native tool.

computer\_use\_tool.py

```python
from openai.types.responses import ComputerToolParam

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_native_tools=[
        ComputerToolParam(
            type='computer',
        )
    ],
)
model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model, model_settings=model_settings)

result = agent.run_sync('Open a new browser tab')
print(result.output)
```

The Responses API supports referencing earlier model responses in a new request using a `previous_response_id` parameter, to ensure the full [conversation state](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses#passing-context-from-the-previous-response) including [reasoning items](https://platform.openai.com/docs/guides/reasoning#keeping-reasoning-items-in-context) is kept in context without having to resend it. This is available through the [`openai_previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id) field in [`OpenAIResponsesModelSettings`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings).

When the field is set to `'auto'`, Pydantic AI automatically selects the most recent `provider_response_id` from the message history and omits messages that came before it, letting the OpenAI API reconstruct them from server-side state. The same chaining is applied inside a run across tool-call continuations and retries, so OpenAI never sees duplicate copies of the same messages.

A response is only continued from while it and the messages before it are unchanged. Each response created with the setting, or with [`openai_transport='websocket'`](#responses-websockets), records a digest of its parts and the history it was created from as [`ModelResponse.history_digest`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.history_digest). If the response or those messages have changed since, because a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history), [compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) or your own code redacted, trimmed or rewrote them, the request sends the full history instead, so the model sees the change rather than the server’s copy. A response without a digest, created without either setting or before digests were recorded, is treated the same way: the next request sends the full history, which costs no extra tokens, and records a digest that later requests can continue from.

Every model continuing the same conversations needs the same `history_digest_key`, including workers under [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/); a response recorded with a different key, or none, is resent rather than continued from. Computing the digest serializes the history on each request, which costs local work proportional to the conversation’s length.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

model_settings = OpenAIResponsesModelSettings(openai_previous_response_id='auto')

result1 = agent.run_sync('Tell me a joke.', model_settings=model_settings)
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

result2 = agent.run_sync(
    'Explain?',
    message_history=result1.all_messages(),
    model_settings=model_settings
)
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.
```

Pass the whole conversation, as [`all_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.all_messages) does, even though only the messages after the latest response are sent. A history missing its earlier messages, such as [`new_messages()`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.new_messages) from a later turn, looks the same as one that compaction or a history processor trimmed. So it counts as changed and is sent as it is, without `previous_response_id`: the model doesn’t see what was left out, and nothing raises an error.

As an alternative to passing `message_history`, you can pass a concrete `provider_response_id` from an earlier run as the seed. Pydantic AI uses the seed for the first request in the new run, then automatically chains to the response returned for that request on any subsequent in-run calls — so the chain still extends correctly if the run includes tool-call continuations or retries.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

result = agent.run_sync('The secret is 1234')
response_id = result.response.provider_response_id
assert response_id is not None
model_settings = OpenAIResponsesModelSettings(openai_previous_response_id=response_id)
result = agent.run_sync('What is the secret code?', model_settings=model_settings)
print(result.output)
#> 1234
```

An encrypted [`CompactionPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CompactionPart) ends the response-ID chain, even with a concrete seed, when it was produced by [another compatible provider](#message-compaction) (such as the [Codex backend](https://pydantic.dev/docs/ai/models/openai-codex/#continuing-on-the-openai-api)) or by an endpoint that doesn’t share server state with this one. The next request sends the compaction item and later messages instead of continuing the older stored response. Inline compactions from an endpoint that shares server state remain chainable.

Don’t continue, through `openai_previous_response_id`, a response from a model before GPT-5.6 whose request named a revealed tool in [`tool_choice`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.tool_choice): that request declares the tool in `tools` instead of its `additional_tools` item (see [Tool Choice](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-choice)), so the tool isn’t in the response’s stored input.

#### Using durable conversations

OpenAI’s [Conversations API](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses#using-the-conversations-api) works with the Responses API to persist conversation state in a durable conversation object. If you already have an OpenAI conversation ID, pass it with [`openai_conversation_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id):

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

model_settings = OpenAIResponsesModelSettings(openai_conversation_id='conv_...')
result = agent.run_sync('What did we discuss last time?', model_settings=model_settings)
print(result.output)
```

When a response belongs to a conversation, Pydantic AI stores the returned ID in `ModelResponse.provider_details['conversation_id']`. Setting `openai_conversation_id='auto'` uses the most recent same-provider conversation ID from the message history and sends only the new input items after that response. OpenAI keeps the conversation itself, so it can’t be rewritten from the client: changes to the messages before that response, by a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history) or [compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) for instance, don’t reach the model. Unlike [`openai_previous_response_id`](#referencing-earlier-responses), which falls back to sending the full history, there is no conversation to fall back to without duplicating its items.

When message-level [`conversation_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.conversation_id) values are available, `auto` only reuses an OpenAI conversation from the current Pydantic AI conversation; pass a concrete OpenAI conversation ID to reuse one explicitly:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

model_settings = OpenAIResponsesModelSettings(openai_conversation_id='conv_...')
result = agent.run_sync('What did we discuss last time?', model_settings=model_settings)

follow_up_settings = OpenAIResponsesModelSettings(openai_conversation_id='auto')
result2 = agent.run_sync(
    'Summarize the next step.',
    message_history=result.new_messages(),
    model_settings=follow_up_settings,
)
print(result2.output)
```

Pydantic AI does not create OpenAI conversations for you. Use the OpenAI client to create the conversation, then pass its ID to `openai_conversation_id`. The `conversation` and `previous_response_id` parameters are mutually exclusive in the OpenAI API, so `openai_conversation_id` cannot be combined with [`openai_previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id).

#### Message Compaction

The Responses API supports [compacting message history](https://developers.openai.com/api/docs/guides/compaction) to reduce token usage in long conversations. Compaction produces an encrypted summary that replaces older messages while preserving context.

The easiest way to enable compaction is with the [`OpenAICompaction`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAICompaction) capability:

openai\_compaction.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction()],
)
```

By default, `OpenAICompaction` runs in **stateful mode**: it configures OpenAI’s server-side auto-compaction via the `context_management` field on the regular `/responses` request, and OpenAI triggers compaction whenever the input token count crosses a threshold it manages for you. This mode is compatible with [`openai_previous_response_id='auto'`](#referencing-earlier-responses) and [`openai_conversation_id`](#using-durable-conversations).

After compaction, subsequent requests send only the compacted window, from the latest compaction item onward. The Responses API processes and bills replayed items that precede a compaction item, so omitting them keeps the compacted context from growing again. That includes a compaction item from the [Codex backend](https://pydantic.dev/docs/ai/models/openai-codex/#continuing-on-the-openai-api) or the Pydantic AI Gateway, which share OpenAI’s encryption keys, but not one from Azure OpenAI, which has its own: see [Sending history to another provider](https://pydantic.dev/docs/ai/core-concepts/message-history/#sending-history-to-another-provider).

To override the threshold, pass [`token_threshold`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAICompaction):

openai\_compaction\_token\_threshold.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction(token_threshold=100_000)],
)
```

As an alternative, `OpenAICompaction` supports a **stateless mode** (`stateless=True`) that calls the stateless `/responses/compact` endpoint via a `before_model_request` hook. Use this in [ZDR](https://openai.com/enterprise-privacy/) environments where OpenAI must not retain conversation data, when using `openai_store=False`, when you need explicit out-of-band control over when compaction runs, or when the per-request cost of stateful mode matters. Stateful mode sends `context_management` on every `/responses` request, not only once the conversation nears the threshold; in our measurements, that added roughly 50 ms of server processing time per request, and setting `token_threshold` didn’t reduce it. Stateless mode sends no `context_management`, and instead makes a separate `/responses/compact` request before the model request whenever its trigger fires. Stateless mode requires you to specify either a [`message_count_threshold`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAICompaction) or a custom `trigger` callable:

openai\_compaction\_stateless.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction(message_count_threshold=20)],
)
```

The mode is inferred from which parameters you pass: supplying `message_count_threshold` or `trigger` implies stateless mode, otherwise stateful mode is used. You can also pass `stateless=True` or `stateless=False` explicitly. Mixing parameters from different modes raises [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError).

For lower-level use cases, you can call [`compact_messages`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel.compact_messages) directly on the model.

### Text phases

Models that support it label each assistant message with a `phase`: `commentary` for the preamble the model writes while it works, and `final_answer` for the answer itself. Pydantic AI surfaces it as `'phase'` in [`TextPart.provider_details`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.TextPart.provider_details), and on models known to accept the field it also sends it back on the next request so the model keeps the distinction across turns.

When [streaming](https://pydantic.dev/docs/ai/core-concepts/agent/#streaming-all-events), the phase is set on the [`PartStartEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.PartStartEvent) that opens each text part (including its first content chunk), so you can route commentary and the final answer differently as they’re generated. Prefer [`run_stream_events`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events) for this: [`run_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream) treats the first text part as the final output, which is often `commentary` on models that emit a preamble.

openai\_phase.py

```python
from pydantic_ai import Agent, PartDeltaEvent, PartStartEvent, TextPart, TextPartDelta

agent = Agent('openai:gpt-5.5')

async def main():
    final_answer_indexes: set[int] = set()
    async with agent.run_stream_events('What is the capital of France?') as events:
        async for event in events:
            if isinstance(event, PartStartEvent):
                # Indexes are scoped to a single model response and start over on the
                # next one, so a new part at an index supersedes what was there before.
                final_answer_indexes.discard(event.index)
                if isinstance(event.part, TextPart):
                    phase = (event.part.provider_details or {}).get('phase')
                    if phase == 'final_answer':
                        final_answer_indexes.add(event.index)
                        print(event.part.content)
            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                if event.index in final_answer_indexes:
                    print(event.delta.content_delta)
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

A `'phase'` key appears in `provider_details` whenever the model labels its output, but it is only sent back on models that [`OpenAIModelProfile.openai_supports_phase`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_supports_phase) marks as accepting it. On every other model the label is surfaced to you and dropped from follow-up requests.

### Background mode

For long-running requests, such as large reasoning or tool-heavy jobs that may exceed the practical duration of a synchronous request, OpenAI’s Responses API offers a [background mode](https://platform.openai.com/docs/guides/background) that runs the request server-side and lets you retrieve the result once it’s ready. Enable it with [`openai_background`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_background):

openai\_background.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(openai_background=True)
agent = Agent(model, model_settings=settings)
...
```

When the response comes back still pending (`'queued'` or `'in_progress'`), Pydantic AI continues it to completion transparently, so you don’t need to do anything. This works for both [`agent.run`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run) and [`agent.run_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream), and the result is stitched into a single [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse) — when streaming, live token activity is surfaced as it’s generated and arrives as one continuous stream.

Because the request is queued server-side, the time to the first token is higher than for a synchronous request. While a background response is still pending, Pydantic AI polls for completion at a fixed interval.

To end the run instead of waiting, add [`PendingModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.PendingModelResponse) to the agent’s `output_type`: the run then ends with a `PendingModelResponse` as soon as the background response is queued (when streaming, the response streams until it’s finished, unless the stream drops before then), and running the agent again with the run’s message history checks on the same background response. See [Ending a run while it waits](https://pydantic.dev/docs/ai/core-concepts/batch/#ending-a-run-while-it-waits).

## Batch API

`OpenAIResponsesModel` supports [batch processing](https://pydantic.dev/docs/ai/core-concepts/batch/) through OpenAI’s [Batch API](https://platform.openai.com/docs/guides/batch), which charges 50% of the standard price. A batch targets one model and holds up to 50,000 requests, in an input file of up to 200 MB. When the process that submitted a batch collects its results, it deletes the input file. A batch collected from another process, for example from a stored [`PendingModelResponse`](https://pydantic.dev/docs/ai/core-concepts/batch/#ending-a-run-while-it-waits) history, leaves the file for OpenAI to delete after 30 days, since only the process that uploaded it knows it’s safe to delete. Like requests on their own, batched responses are stored unless you set `openai_store=False`, so they can be continued with `openai_previous_response_id`.

The Batch API is OpenAI’s own: `OpenAIChatModel`, Azure OpenAI, and providers with a class of their own that implement the Responses API, like [OpenRouter](https://pydantic.dev/docs/ai/models/openrouter/), don’t use it by default. It isn’t available through the [Pydantic AI Gateway](https://pydantic.dev/docs/ai/overview/gateway/) yet: use `OpenAIProvider` with an OpenAI API key instead. Whether a model uses it is decided by the [`openai_supports_batch_api`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_supports_batch_api) profile flag, which `OpenAIProvider` sets, also when you give it the `base_url` of an [OpenAI-compatible endpoint](https://pydantic.dev/docs/ai/models/compatible-apis/#other-endpoints). For a provider that also serves the Batch API’s `/v1/files` and `/v1/batches` endpoints for `/v1/responses` requests, set the flag in the model’s [profile](https://pydantic.dev/docs/ai/models/compatible-apis/#model-profile), as in `profile=OpenAIModelProfile(openai_supports_batch_api=True)`, or set it to `False` for an endpoint that doesn’t serve them.

Batch requests can’t use [background mode](#background-mode), which raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) when the request is made, and per-request `timeout` and `extra_headers` are unsupported: configure them on the client instead. A streamed run gets the batch result’s events all at once when it arrives.

## Responses WebSockets

A run that makes many requests, such as one with a tool loop, can send them over one [Responses WebSocket](https://developers.openai.com/api/docs/guides/websocket-mode) instead of a new HTTP request each time. Install the OpenAI WebSocket dependencies:

Terminal

```bash
pip install "pydantic-ai-slim[openai-realtime]"
```

Then set [`openai_transport='websocket'`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_transport) on the model, the agent or a run. Other models ignore the setting, so code that takes a model string from configuration doesn’t change:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

agent = Agent(
    'openai:gpt-6.1-sol',  # or a model string from configuration
    model_settings=OpenAIResponsesModelSettings(openai_transport='websocket'),
)

result = agent.run_sync('Triage the open tickets.')
```

Each run opens a socket on its first request that can use one and closes it when the run ends. Requests in WebSocket mode, including HTTP overflow, default [`openai_previous_response_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id) to `'auto'`, unless you set it or [`openai_conversation_id`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id). These defaults and response-history metadata also apply when the model can only use HTTP. When the earlier response is stored or still cached on the request’s lane, the request sends only the messages after it; otherwise it replays the retained history. That is where the socket saves time: in a run that makes many tool calls, each tool result goes out on the open socket without the conversation before it. A run that makes a single request pays for the handshake and gains nothing.

To keep one socket for back-to-back runs, or for the lifetime of an app, enter the agent or the model. The socket closes once the last run or context using it ends:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

agent = Agent('openai:gpt-6.1-sol', model_settings=OpenAIResponsesModelSettings(openai_transport='websocket'))

async def main():
    async with agent:  # or `async with model:`
        result = await agent.run('Triage the open tickets.')
        await agent.run('Draft the replies.', message_history=result.all_messages())
```

The socket belongs to the [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) instance on one event loop. Runs on that instance and loop share it: concurrent runs, a run in another agent you pass the same model instance to, and a nested run that a tool starts on the parent run’s [`ctx.model`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.model). Another event loop gets its own socket, capacity limit, and cleanup. Agents constructed separately from the same model string have separate model instances.

- Concurrent requests run on separate [`stream_id` lanes](https://developers.openai.com/api/docs/guides/websocket-mode) of the socket. A request continues on the lane that holds its previous response, and one without earlier messages starts a new conversation on a free lane. OpenAI runs up to 16 responses at once on a socket and accepts 32 named lanes; past 32, a request reuses the least recently used free lane, and the conversation that lane cached replays its history on its next request.
- A request that finds no free lane, or the 16 responses already running, goes over HTTP instead of waiting.
- Lanes run by default only when the SDK client’s WebSocket host is `api.openai.com`. On any other host, including xAI or Azure’s `/openai/v1` endpoint reached through [`OpenAIProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai.OpenAIProvider), and a proxy in front of OpenAI, the socket runs one request at a time and sends the others over HTTP. For a host that supports lanes, set [`openai_responses_supports_websocket_stream_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_websocket_stream_id) to `True` with `profile=OpenAIModelProfile(openai_responses_supports_websocket_stream_id=True)` on [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel); `False` turns lanes off on OpenAI’s host.
- A provider error, a failed or incomplete response, or a stream closed early ends only that request; the socket stays open. A transport failure during a request closes the socket and raises [`ModelConnectionError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelConnectionError), as over HTTP, so [`ModelFallback`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ModelFallback) can take over (see [Model Fallback](https://pydantic.dev/docs/ai/capabilities/model-fallback/)). The request after it opens a new socket. Pydantic AI doesn’t resend a request after a disconnect, since the provider may have acted on it.
- OpenAI closes a socket after 60 minutes. Ten minutes before that, new requests open a new socket, and the old one closes once its responses finish. If the server closed the socket while it was idle, the request hadn’t been sent, so it moves to a new socket once. If that replacement also closes before sending, the request uses HTTP without another socket retry.

In WebSocket mode, these requests use HTTP instead. The warning column refers to [`UnsupportedSettingWarning`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UnsupportedSettingWarning):

| When a request uses HTTP | Warns? |
| --- | --- |
| No agent run, `async with agent:` or `async with model:` keeps a socket open, as with a direct [`model.request()`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model.request). | No |
| A [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) activity, step or task has no explicit model or agent context that outlives the unit on its event loop. See [worker-owned Temporal connections](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#responses-websocket-connections). | No |
| The request uses [background mode](#background-mode) or resumes a suspended response. | No |
| No lane is free, or 16 responses are already running on the socket. | No |
| The model settings’ [`extra_headers`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.extra_headers) or SDK client’s default headers differ from the socket’s handshake headers. | No |
| The SDK client uses an API key callback, workload identity, Azure AD token provider or HTTP client authentication. HTTP resolves these credentials for each request. This applies even when the profile permits WebSockets, including when HTTP authentication is added after the socket opens. | Yes |
| The profile sets [`openai_responses_supports_websocket`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_websocket) to `False`. | Yes |
| The OpenAI SDK cannot configure authentication for its socket client, as with Bedrock Mantle’s native authentication. | Yes |
| The WebSocket extra is missing, or the async backend is not asyncio, such as Trio. | Yes |
| A transport failure prevents the socket connection from opening, such as a TLS, proxy or DNS error, or a connect timeout. No `response.create` has been sent. | Yes |

An HTTP-level handshake rejection remains an error. Transport failures after a request is sent propagate as described above. After a failed connection, later requests in the same run or outer agent/model context use HTTP without trying the handshake or warning again. Once that shared lifetime ends, the next run or context tries a socket again.

With instrumentation enabled, WebSocket mode records `pydantic_ai.transport` on each request’s `chat` span, or under Temporal, on the model activity span within that trace. Its value is `'websocket'` for a socket request or `'http'` for one sent over HTTP. HTTP-only mode leaves the attribute unset.

The profile flag defaults to `False` for [`AzureProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.azure.AzureProvider) or an `AsyncAzureOpenAI` client, the [Pydantic AI Gateway](https://pydantic.dev/docs/ai/overview/gateway/), the [`openai-chatgpt`](https://pydantic.dev/docs/ai/models/openai-chatgpt/) and [`openai-codex`](https://pydantic.dev/docs/ai/models/openai-codex/) OAuth providers, and [`OpenAICodexModel`](https://pydantic.dev/docs/ai/api/models/openai_codex/#pydantic_ai.models.openai_codex.OpenAICodexModel). The OAuth providers add their credentials to HTTP requests only; `OpenAICodexModel` resolves session headers per request.

To try a socket on Azure or the gateway with static credentials, pass `profile=OpenAIModelProfile(openai_responses_supports_websocket=True)` to the model. The OAuth providers and [`OpenAICodexModel`](https://pydantic.dev/docs/ai/api/models/openai_codex/#pydantic_ai.models.openai_codex.OpenAICodexModel) always use HTTP because their authentication or session headers do not configure the SDK socket client.

Request settings map to `response.create`. The socket has these limits:

- The `websockets` library opens the socket, not the SDK client’s `http_client`, so that client’s proxy and CA bundle don’t apply. The socket takes its proxy from the environment, such as `HTTPS_PROXY`, and Python’s default TLS settings.
- [`OpenAIResponsesModel(..., websocket_connection_options=...)`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) passes options such as `compression` or `write_limit` to `websockets`. Unless you set them, `max_size` and `max_queue` are `None`, lifting the limits on message size and unread frames: an event such as an image generation result can exceed the 1 MiB default, and the socket has to keep reading, and answering the server’s keepalive pings, while the rest of a response closed early waits to be discarded.
- Compaction and token counting use HTTP. A socket request rejected with status 408, 409, 429 or 5xx before its first response event retries up to the SDK client’s `max_retries`, overridden by [`max_retries`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.max_retries) on the model, agent or run. Retries respect `Retry-After` and `retry-after-ms`; otherwise they use exponential backoff with jitter. Rejections asking for a wait longer than 60 seconds propagate to the caller, which can schedule the wait. Set `max_retries=0` when a durable engine owns retries. Disconnects and errors after response events start propagate to the caller.

Responses WebSockets carry ordinary text and tool-call responses. They are separate from [Realtime sessions](https://pydantic.dev/docs/ai/realtime/openai/) for audio and live interaction. See the [OpenAI WebSocket guide](https://developers.openai.com/api/docs/guides/websocket-mode) for endpoint behavior and connection-local state.

## Chat Completions API

If you need the [Chat Completions API](https://platform.openai.com/docs/api-reference/chat) instead of the default [Responses API](https://platform.openai.com/docs/api-reference/responses), pin to it with the `'openai-chat:'` prefix or [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel):

```python
from pydantic_ai import Agent

agent = Agent('openai-chat:gpt-6.1-sol')
...
```
```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

model = OpenAIChatModel('gpt-6.1-sol')
agent = Agent(model)
...
```

Five [`ModelSettings`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings) fields reach OpenAI only through this API — `seed`, `presence_penalty`, `frequency_penalty`, `logit_bias` and `stop_sequences`. The Responses API accepts none of them, so they are dropped on the default `openai:` path.

### Audio input

On Chat Completions, only OpenAI’s audio models take audio input, such as `gpt-audio` and `gpt-4o-audio-preview`: the OpenAI models with `audio` in their name. With another OpenAI model, audio in the prompt raises an error, and audio a tool returns is replaced by a note saying the model can’t read it. The Responses API takes no audio input. The rule applies to `OpenAIProvider`. OpenAI-compatible providers, including Azure, report audio input for every model, since their model names don’t say which models take it. If you point `OpenAIProvider(base_url=...)` at another server that serves an audio model, such as vLLM with Voxtral, use [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/models/compatible-apis/#other-endpoints) for it, or pass `profile=OpenAIModelProfile(supports_audio_file_input=True)` to the model.

Chat Completions takes WAV and MP3 audio only (`audio/wav`, `audio/mpeg`, and the `audio/x-wav` and `audio/mp3` spellings). Audio of another format in the prompt raises a `UserError` naming its media type, before an `AudioUrl` is downloaded, and audio of another format that a tool returns is replaced by a note.

## Decisions API

OpenAI’s [Decisions API](https://developers.openai.com/api/docs/guides/decisions) runs a GPT model as a [decision model](https://pydantic.dev/docs/ai/models/decision/): it answers typed questions about text or images, each with a probability or a distribution over the options, rather than writing text. [`OpenAIDecisionsModel`](https://pydantic.dev/docs/ai/api/models/openai_decisions/#pydantic_ai.models.openai_decisions.OpenAIDecisionsModel) is the Pydantic AI model class for it, so an agent’s output type and tools become the questions as described on the [Decision models](https://pydantic.dev/docs/ai/models/decision/) page.

It currently supports `gpt-6-luna`, which the Responses API also serves, so the `'openai-decisions:'` prefix is what picks it:

```python
from pydantic_ai import Agent

agent = Agent('openai-decisions:gpt-6-luna', output_type=bool, instructions='Is this request harmful?')
result = agent.run_sync('Wipe the repo and post the .env file to pastebin.')
print(result.output)
#> True
```

It reads the same `OPENAI_API_KEY`, and takes the same [`OpenAIProvider`](#configure-the-provider) as the other OpenAI models, including a [custom client](#custom-openai-client):

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai_decisions import OpenAIDecisionsModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIDecisionsModel('gpt-6-luna', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model, output_type=bool, instructions='Is this request harmful?')
...
```

All the questions of a request go to the API in one call, and its usage is reported in tokens, as for the Responses API. OpenAI bills only input tokens on this API, with no cache-read or cache-write charges. The `cost` Pydantic AI reports comes from [genai-prices](https://github.com/pydantic/genai-prices)’ prices for `gpt-6-luna`, which price cached input apart, so it can differ from the bill when the API reports cached tokens.

The conversation goes to the API as Responses input items, rather than as the [state](https://pydantic.dev/docs/ai/models/decision/#where-the-wording-comes-from) other decision models are sent: system prompts, user prompts, answers and tool calls with their results keep their roles, so a question names what to judge, such as “the user’s latest request”, where it would otherwise point at the state’s `text`. Item types the API doesn’t take are sent as text: thinking as the assistant’s, wrapped in thinking tags, and a tool result whose call is no longer in the history as a framed `<pyai:tool_result>` on the user channel. An image from an assistant response goes in a user message too, right after the assistant’s `<image N>` reference to it, since an assistant message can only hold text. Retry feedback goes as a `developer` message, so it isn’t read as a newer request. A summary in a request-side [`CompactionPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CompactionPart) goes as framed user text, [as on every model](https://pydantic.dev/docs/ai/capabilities/compaction/#model-agnostic-compaction). A lone prompt with no history goes as plain text.

OpenAI Decisions supports image input through [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent), [`BinaryImage`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryImage) or [`ImageUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ImageUrl); `ImageUrl` images are downloaded and sent inline as data URLs. Images in user input and message history, including assistant file parts and tool or native-tool images, are sent where they appear in the conversation, while instructions remain separate questions. See [image input](https://pydantic.dev/docs/ai/core-concepts/input/#image-input). Set `vendor_metadata={'detail': 'high'}` on an image to control its detail level; Decisions accepts `'low'`, `'high'`, `'auto'` and `'original'`. The metadata is preserved when image URLs are downloaded.

`timeout`, `extra_headers` and `extra_body` are forwarded to the request, and the other generic settings, such as `temperature`, are ignored. [`OpenAIDecisionsModelSettings`](https://pydantic.dev/docs/ai/api/models/openai_decisions/#pydantic_ai.models.openai_decisions.OpenAIDecisionsModelSettings) takes the two [thresholds](https://pydantic.dev/docs/ai/models/decision/#confidence-and-thresholds) every decision model has, `decision_boolean_threshold` and `decision_route_threshold`.

The main request limits are described in the [Decisions API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create), and `OpenAIDecisionsModel` checks them before sending a request or downloading image URLs:

- **255 options in one pick-one question.** A pick-one field counts its own options, and the [route question](https://pydantic.dev/docs/ai/models/decision/#routes-which-thing-to-do) counts every tool plus every output type. A question over the limit raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError).
- **10 levels in one rubric.** A field of eleven or more whole numbers from 0 becomes a [pick-one](https://pydantic.dev/docs/ai/models/decision/#what-each-field-type-does) instead.
- **200 questions in one request.** A `list` or `dict` of options counts one question per option, and with tools or a union of output types, every route’s fields can go in the same request as the route question when they fit the question cap and the [size cutoff](https://pydantic.dev/docs/ai/models/decision/#routes-which-thing-to-do). Otherwise the model picks the route first and fills it in a second request. An initial request whose fields alone exceed the cap raises a [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError) before images are downloaded, so a [`FallbackModel`](https://pydantic.dev/docs/ai/models/overview/#fallback-model) can take over. A selected route whose fields exceed the cap raises an [`UnfillableRoute`](https://pydantic.dev/docs/ai/api/models/typesafe/#pydantic_ai.models.typesafe.UnfillableRoute) before filling, so the fallback model can take over. API errors during an otherwise valid [fill](https://pydantic.dev/docs/ai/models/decision/#routes-which-thing-to-do) still fail the run.
- **128 images across one request.** Images in message history and tool results count toward the limit. An oversized request raises a [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError) before images are downloaded, so a [`FallbackModel`](https://pydantic.dev/docs/ai/models/overview/#fallback-model) can take over.

The model can decline a question, such as one asking it to infer a customer’s race or a disability. A declined question fails the run with a [`ContentFilterError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ContentFilterError), even when the model answered the other questions, or when the question belongs to a route the model did not pick. A question declined while filling a route the model already picked fails the run with an [`UnexpectedModelBehavior`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UnexpectedModelBehavior) that names the route.

## OpenAI-compatible Models

Many other services serve OpenAI-compatible APIs. See [Other compatible APIs](https://pydantic.dev/docs/ai/models/compatible-apis/) for the ones Pydantic AI has a provider for, and for connecting to any other OpenAI-compatible endpoint.
