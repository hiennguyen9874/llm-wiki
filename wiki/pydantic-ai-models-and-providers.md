---
type: Concept
title: Pydantic AI models and providers
description: How a `<provider>:<model>` string resolves to a model class, a provider and a profile — the 38-service provider directory, the capability flags and context window a profile carries, the HTTP client lifecycle behind a model, and what a custom model must implement.
tags: [pydantic-ai, models, providers, configuration]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:35:00Z }
stale_after: 2027-02-18
sources:
  - id: models-overview-2026
    resource: ../raw/models/overview/index.md
    scope: ../raw/models/overview/
    kind: documentation
    revision: sha256:b0b88d61e84966c7b8b8d70207b0cf386810413968eaa0d0246ca6690ef10a66
    title: "Models and Providers"
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

Pydantic AI's portability claim reduces to one string: `Agent('openai:gpt-6.1-sol')` parses into a model class, a provider and a profile, and swapping the string swaps all three without touching the agent[^models-overview-2026] The three terms are worth keeping apart because each answers a different question — the model class says which API dialect is spoken, the provider says where the request goes and how it authenticates, and the profile says what the model behind that API can actually do[^models-overview-2026] Around that core sit three operational surfaces a production deployment has to configure rather than discover: the HTTP client a provider owns, the concurrency a model will tolerate, and the escape hatch of writing a model class for an unsupported API[^models-overview-2026] The page below covers the first and third; concurrency lives in [model concurrency](pydantic-ai-model-concurrency.md) and the failure taxonomy in [model API errors](pydantic-ai-model-api-errors.md).

## Model, provider, profile

| Term | What it is | What it decides |
| --- | --- | --- |
| **Model** | A Pydantic AI class wrapping a vendor SDK behind one vendor-agnostic API, named `<VendorSdk>Model` (`OpenAIChatModel`, `AnthropicModel`, `GoogleModel`) | The API the request is expressed in; the actual LLM name is a constructor argument |
| **Provider** | A class handling authentication and the connection to one vendor or endpoint | Which endpoint is hit and which credential scheme applies — e.g. `AzureProvider` gives `OpenAIChatModel` Azure auth, a gateway or a compatible vendor reuses an existing model class |
| **Profile** | A description of how requests to a model or model family must be built to get good results | Schema restrictions, supported modalities, native tools, context window — independent of model and provider class |

A `<provider>:<model>` name such as `openai:gpt-6.1-sol` or `openrouter:google/gemini-3-pro-preview` selects all three automatically; instantiating a model class directly and passing `provider=` and/or `profile=` overrides the selection[^models-overview-2026]

## Provider directory

The directory lists **38 routes**, each with a setup page and its model-string prefix; the prefix is what goes before the colon, and some routes need an explicit model or client instead[^models-overview-2026] The source groups the entries by the kind of service, which is the useful cut when choosing a deployment:

- **Model developers**: OpenAI (`openai:`, `openai-chat:`, `openai-responses:`), Anthropic, Google/Gemini API, Cohere, DeepSeek, Meta, Mistral, Moonshot AI, xAI, Z.AI
- **Cloud platforms**: AWS Bedrock, Google Cloud/Vertex AI, Microsoft Azure/Foundry, Alibaba Cloud (DashScope), Heroku AI, OVHcloud, Snowflake Cortex — each runnable on the cloud's own credentials
- **Inference platforms**: Cerebras, Crusoe, Fireworks AI, Groq, Hugging Face, Nebius, SambaNova, Together AI, vLLM (self-hosted)
- **Gateways**: Pydantic AI Gateway (`gateway/<provider>:`), LiteLLM (over HTTP, without the `litellm` package), OpenRouter, Vercel AI Gateway
- **Subscription access**: GitHub Copilot, OpenAI Codex, and `openai-chatgpt:` for using a user's own ChatGPT plan
- **Decision models**: Google, OpenAI, TypeSafe and System One, each behind its own `*-decisions:`/`system-one:`/`typesafe:` prefix
- **Local inference**: Ollama, both local and cloud

Two caveats the source attaches to that list: a company may appear under more than one service kind, and **feature support depends on the model and API you pick even when two services share an API format**[^models-overview-2026] For work that is not waiting on a user, Anthropic, OpenAI and Gemini API models can also go through their providers' batch APIs at about half the price[^models-overview-2026] — the mechanism, its settings and the profile flags that decide which models have a batch API are in [batch processing](pydantic-ai-batch-processing.md).

The OpenAI row is the directory's deepest route and the one worth reading separately: [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md) records `openai:` as the Responses default, `openai-chat:` as the legacy Chat Completions pin, and `openai-decisions:` as the decision-model dialect, while [OpenAI Responses API features](openai-responses-api-features.md) holds everything only the default route offers and [OpenAI decision models](openai-decision-models.md) the Decisions contract. The two captures disagree on the list itself rather than on behaviour: this directory names `openai:`, `openai-chat:` and `openai-responses:` for OpenAI, and the setup page names `openai:`, `openai-chat:` and `openai-decisions:` while using `openai-responses:` only in an example — so four prefixes exist and neither source enumerates all four (**Synthesis**).

Anything else OpenAI-compatible becomes a first-class route through `OpenAICompatibleProvider` with a service name (not `OpenAIProvider`), and any other API needs a [custom model](#custom-models)[^models-overview-2026] For tests and development the directory is bypassed entirely with `TestModel` or `FunctionModel`[^models-overview-2026]

Anthropic is the other route worth reading on its own, because one prefix covers four transports: `anthropic:` resolves to `AnthropicModel`, and the same class reaches the Claude API, Amazon Bedrock (through the newer Messages-API client or the legacy `InvokeModel` one), Vertex AI and Microsoft Foundry by passing a platform SDK client to `AnthropicProvider` rather than by changing the prefix[^pydantic-anthropic-2026] Two details do not follow from the directory: the provider takes an `httpx2.AsyncClient` and rejects a legacy `httpx.AsyncClient` at construction, and `max_tokens` — which Anthropic requires — defaults to a maximum derived from the model **name**, so a model reached through a Bedrock ARN or a custom deployment name has to be set by hand[^pydantic-anthropic-2026] The rest of that row, including fast mode, data residency, the Batch API and what survives a change of platform, is in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md).

Google is the row the directory splits in two — "Google/Gemini API" among the model developers and "Google Cloud/Vertex AI" among the cloud platforms, with Google listed a third time among the decision models — and the setup page shows why one model class covers all of it: `GoogleModel` reaches both endpoints through `GoogleProvider` (`google:`) and `GoogleCloudProvider` (`google-cloud:`), and `GoogleDecisionsModel` adds the `google-decisions:` dialect[^pydantic-google-2026] Three things the grouping hides: **both** Gateway Google routes resolve to `GoogleCloudProvider`, so a Gemini-API-only feature such as `FileSearchTool` needs the direct provider; Batch Mode exists only on the Gemini API — not on Google Cloud and not through the Gateway; and history does not cross the two transports unchanged, because each rejects the other's thought signatures[^pydantic-google-2026] The route itself is in [Google models in Pydantic AI](google-models-in-pydantic-ai.md).

## Reading a model's profile

`ModelProfile` is a `TypedDict` whose keys are all optional, so capability checks are `.get()` calls on `model.profile` rather than attribute access[^models-overview-2026] The flags fall into three groups:

- **Output and tools**: `supports_text_output`, `supports_tools`, `supports_json_schema_output`, `supported_native_tools`
- **Input kinds**: `supports_image_input`, `supports_document_input`, `supports_audio_file_input`, `supports_video_input`
- **Media-type narrowing**: `supported_image_media_types`, `supported_document_media_types`, `supported_audio_media_types`, `supported_video_media_types` — unset by default, so the kind alone decides; where set, a file outside the set counts as unreadable

This is what makes a capability branch possible before a request rather than after a failure: check whether a model takes text, tools, native JSON-schema output or a specific native tool, instead of discovering the limitation at request time[^models-overview-2026] The model class still wins over the profile — `AnthropicModel` reads neither audio nor video and only PDF and plain-text documents, and OpenAI Chat Completions takes only WAV and MP3 audio, whatever a profile says[^models-overview-2026] A file a tool returns that the model cannot take is sent as a note naming the file, and [file understanding](pydantic-ai-file-understanding.md) reads the same flags to decide what to describe in text first[^models-overview-2026]

`model.profile` is normally the **resolved** profile: `DEFAULT_PROFILE` merged with the provider's defaults, so `profile.get('supports_tools')` returns a value[^models-overview-2026] Two exceptions matter when writing the check:

- Supply the default as the fallback — `profile.get('supports_tools', DEFAULT_PROFILE['supports_tools'])` — when `profile=` was passed as a callable or a partial dict[^models-overview-2026]
- A `FallbackModel` has no single profile at all, because its candidates may differ; inspect each model in `fallback_model.models` instead, and with the `ModelFallback` capability read `request_context.model` inside a capability hook[^models-overview-2026]

The same structure carries `context_window`, the maximum tokens in one request or `None` when unknown, exposed on every model as `model.context_window` — including wrappers such as `InstrumentedModel`, with a `FallbackModel` reporting the **smallest** window among its candidates so history that fits it fits whichever candidate answers[^models-overview-2026] Inside a run, `ctx.context_window_used` reports the fraction in use[^models-overview-2026] Profiles are not [capabilities](pydantic-ai-capability-primitive.md): the profile describes the underlying model, a capability bundles tools, hooks and settings you add to an agent[^models-overview-2026]

## HTTP client lifecycle

When a provider creates its own HTTP client, it owns that client's lifecycle, so using the agent as an async context manager is what keeps connections alive across runs and closes them cleanly on exit[^models-overview-2026]

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')

async def main():
    async with agent:
        result = await agent.run('What is the capital of France?')
        print(result.output)
```

A `Model` or `Provider` can be entered directly for the same effect; a long-lived web server should enter the agent once at startup and run inside the block[^models-overview-2026] Without that block the behaviour depends on where the run's model came from:

| Where the model comes from | HTTP client behaviour |
| --- | --- |
| The agent's own model, or a `Model` instance passed to a run | Created with the model, reused on the same event loop, never closed until the agent/model/provider is entered and exited; `defer_model_check=True` makes a model name behave this way |
| A model **name** passed to a run, or returned by a model selector | A new provider and client per run, closed when the run ends; inside `async with agent:` one provider per name is reused until the block exits |
| A `Model` **instance** a model selector returns | Entered and exited per run, closing and recreating the client; inside `async with agent:` an instance selected again (identified by identity) stays open until the block exits |

Two rules follow from connections belonging to the event loop that opened them[^models-overview-2026] Repeated `run_sync()` calls in one thread share an event loop and so share the client; on a *new* event loop the provider creates a new client when the old loop is not running, and the old client stays open because it cannot be closed from another loop — so entering the agent inside each loop is what closes it before its loop closes. That includes `run_sync()` from a worker-thread pool, where the fix is one model per thread or one entered agent per thread, and concurrent loops, which need one model each. A durable-execution run is exempt because its requests are sent from the engine's activities, steps or tasks[^models-overview-2026]

Pydantic AI only closes or replaces clients **it** created: an `http_client` or provider SDK client you pass in (`openai_client`, `anthropic_client`, Google's `client`, `hf_client`, `xai_client`) is yours to close, and it is kept even on another event loop, where it can fail with the SDK's own `RuntimeError: Event loop is closed`[^models-overview-2026]

### Configuring the client

The created clients default to a **600-second timeout** (20 minutes for Google) with a 5-second connect timeout and a pool of up to 1,000 connections, 100 of them kept alive while idle — the OpenAI and Anthropic SDK defaults[^models-overview-2026] `create_async_httpx2_client()` keeps the remaining defaults and Pydantic AI's `User-Agent` while changing timeout and limits, and because you created it you close it; the same client handed to several providers makes them share one connection pool, and it accepts a custom `transport` such as a retrying one[^models-overview-2026]

```python
import httpx2

from pydantic_ai import Agent
from pydantic_ai.models import create_async_httpx2_client
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

async def main():
    async with create_async_httpx2_client(
        timeout=httpx2.Timeout(120, connect=5, pool=10),
        limits=httpx2.Limits(max_connections=200, max_keepalive_connections=50),
    ) as http_client:
        model = OpenAIChatModel('gpt-6.1-sol', provider=OpenAIProvider(http_client=http_client))
        agent = Agent(model)
        result = await agent.run('What is the capital of France?')
```

The Groq, Cohere and GitHub providers are the exception: they take a legacy `httpx.AsyncClient` you build yourself with the same arguments[^models-overview-2026]

## Custom models

An unsupported API means subclassing the `Model` abstract base class, plus `StreamedResponse` for streaming, and the recommended starting point is reading an existing implementation such as `OpenAIChatModel`[^models-overview-2026] Two consequences of the base class bisect the class hierarchy:

- A subclass with dataclass equality (including one inheriting it) compares `settings` and `profile` along with its dataclass fields; a direct non-dataclass subclass or a direct `@dataclass(eq=False)` subclass hashes by identity[^models-overview-2026]
- `repr` shows `model_name`, dataclass fields, and `settings` and `profile` when set; either can be replaced by defining `__eq__` or `__repr__`[^models-overview-2026]

Raising the shared error taxonomy from a custom model is covered in [model API errors](pydantic-ai-model-api-errors.md) via `ModelHTTPError.for_category`[^models-overview-2026] Whether a new model is accepted into the library is governed by the contributing guidelines' new-model rules, which the source points at without restating[^models-overview-2026]

## Limits

- The page names **no Pydantic AI version**, so every API name here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^models-overview-2026]
- The provider directory is one page's snapshot of 38 routes with no dates on the individual provider pages, no per-model capability matrix, and no prices; provider setup details were read as links, not followed[^models-overview-2026]
- Profile keys are named but not enumerated: `supported_native_tools` accepts which tool classes, and which per-provider defaults `DEFAULT_PROFILE` merges, are not stated[^models-overview-2026]
- The 600-second/1,000-connection defaults and the event-loop guidance are reported documentation; no client was created, no event loop run, and no connection pool measured in this ingest[^models-overview-2026]
- Evidence class: **Reported**.

## Relationships

- **Selects** [Pydantic AI Gateway](pydantic-ai-gateway.md) through the `gateway/<provider>:` prefix in the provider directory.
- **Details the OpenAI row** of the directory in [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md), with its three dialects and the client and schema rules behind them.
- **Details the Anthropic row** of the directory in [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md), with its single prefix over four transports, the `max_tokens` default keyed to the model name and the `httpx2` client requirement.
- **Details the Google rows** of the directory in [Google models in Pydantic AI](google-models-in-pydantic-ai.md), the three lines the directory spends on one model class — Gemini API, Google Cloud and the decision dialect — with the Gateway and batch-availability differences the grouping hides[^pydantic-google-2026]
- **Explained by** [model concurrency](pydantic-ai-model-concurrency.md), which wraps a model to cap its in-flight requests, and [model API errors](pydantic-ai-model-api-errors.md), which defines what a failing model raises.
- **Profiles reach** [model fallback](pydantic-ai-model-fallback.md): a fallback chain has no single profile or context window, so each candidate is inspected separately.
- **Gate** [file understanding](pydantic-ai-file-understanding.md), which reads the input-kind and media-type flags to decide which files another model must describe.
- **Constrains** [prompt caching](pydantic-ai-prompt-caching.md) and [conversation state](pydantic-ai-conversation-state.md) through `context_window`, the bound on how much history one request can carry.
- **Addresses** [Pydantic AI embeddings](pydantic-ai-embeddings.md) through the same `<provider>:<model>` string and the same provider classes, so the `azure:`, `ollama:` and `vllm:` shorthands and the OpenAI-compatible escape hatch carry over to embedding models — recorded on that page.
- **Depends on** [Pydantic AI v2 release](pydantic-ai-v2-release.md) for the version line this unversioned page cannot date itself against.
- **Is wrapped without an agent by** [direct model requests](pydantic-ai-direct-model-requests.md), which call these `Model` implementations directly and keep only schema translation.
- **Extends to** [realtime provider support and settings](pydantic-ai-realtime-provider-support.md): the same defaults-then-name-then-override profile resolution reaches `RealtimeModel`, where the profile also carries audio sample rates and the per-provider feature flags.

[^models-overview-2026]: Pydantic Docs, "Models and Providers", <https://pydantic.dev/docs/ai/models/overview/>, 6,420 words as declared, no publication date and no version named; local capture `raw/models/overview/index.md`, content digest sha256:b0b88d61. §"Provider directory" (lines 17–72) for the 38-row directory, the service kinds, the per-model feature caveat, batch APIs, `OpenAICompatibleProvider`, `TestModel`/`FunctionModel` and the ATX heading "OpenAI-compatible Providers"; §"Models, providers, and profiles" (lines 74–110) for the model/provider/profile definitions, name-based selection and profile overrides; §"Inspecting a model's profile" (lines 84–110) for the capability and media-type flags, the model-class override, file-note behaviour, `DEFAULT_PROFILE` resolution, the `FallbackModel` and `ModelFallback` profile caveats, `context_window` and `ctx.context_window_used`; §"HTTP Client Lifecycle" (lines 111–168) for the `async with agent` example and the three client-lifecycle cases, the event-loop and thread-pool rules, and which clients Pydantic AI closes; §"Configuring the HTTP client" (lines 139–168) for the 600-second/5-second/1,000/100 defaults, `create_async_httpx2_client`, the shared pool, `transport`, and the legacy `httpx.AsyncClient` providers; §"Custom Models" (lines 169–178) for `Model`/`StreamedResponse`, equality and `repr` semantics, `OpenAIChatModel` as a reference and the contributing-guidelines pointer. Evidence class: **Reported** — vendor documentation; no package installed, no model constructed, no request sent, no client reopened on a second loop.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Configuration"/"Environment variable" (raw lines 21–56) for the `anthropic:` prefix resolving to `AnthropicModel`; §"Custom HTTP Client" (73–96) for the `httpx2.AsyncClient` requirement and the rejected legacy client; §"Model settings" (101–119) for the required `max_tokens`, the name-keyed maximum and the ARN/custom-deployment caveat; §"Cloud Platform Integrations" (130–198) for `AnthropicProvider(anthropic_client=...)` with the Bedrock Mantle/legacy, Vertex and Foundry clients. Evidence class: **Reported** — vendor documentation; no client was constructed and no model resolved.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. Lines 11–18 for `GoogleModel` over the `google-genai` SDK, the two providers and their `google:`/`google-cloud:` prefixes, the two Gateway routes using `GoogleCloudProvider` and `FileSearchTool` requiring the direct Gemini API; §"Batch API" (493–499) for Batch Mode being unavailable on Google Cloud and through the Gateway; §"Switching between the Gemini API and Google Cloud" (80–82) for the mutually rejected thought signatures; §"Decisions API" (line 529) for `GoogleDecisionsModel` and the `google-decisions:` prefix. Evidence class: **Reported** — vendor documentation; no model was resolved and no request sent.
