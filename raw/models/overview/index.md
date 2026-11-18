---
title: "Models and Providers"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/models/overview/"
domain: "pydantic.dev"
language: "en"
description: "Pydantic AI is model-agnostic: switch between OpenAI, Anthropic, Gemini, Amazon Bedrock, Google Vertex AI, Azure OpenAI and local models by changing one string. Find each provider's setup guide, model selection and fallback configuration."
word_count: 6420
---

Pydantic AI supports model developers, cloud platforms, inference services, gateways, and local model servers. Find your service below and follow its setup guide for installation, authentication, and supported features.

Pydantic AI is model-agnostic: switch an agent between OpenAI, Anthropic, Gemini, Amazon Bedrock, Google Vertex AI, Azure OpenAI and local models by changing one string, without rewriting the agent. It runs on [Azure OpenAI](https://pydantic.dev/docs/ai/models/azure/), [Amazon Bedrock](https://pydantic.dev/docs/ai/models/bedrock/) and [Google Vertex AI](https://pydantic.dev/docs/ai/models/google-cloud/) with your cloud’s own credentials.

To keep an agent running when a provider fails, give it other models to fall back to with the [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) capability: see [Fallback Model](#fallback-model).

## Provider directory

Pass a name in the form `<provider>:<model>` to [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) to select a provider by its prefix. Some routes require an explicit model or client instead; each setup guide shows the available options.

| Provider and setup | Service | Model selection |
| --- | --- | --- |
| [Pydantic AI Gateway](https://pydantic.dev/docs/ai/overview/gateway/) | Gateway | `gateway/<provider>:` |
| [OpenAI](https://pydantic.dev/docs/ai/models/openai/) | Model developer | `openai:`, `openai-chat:`, `openai-responses:` |
| [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/) | Model developer | `anthropic:` |
| [Google / Gemini API](https://pydantic.dev/docs/ai/models/google/) | Model developer | `google:` |
| [AWS Bedrock](https://pydantic.dev/docs/ai/models/bedrock/) | Cloud platform | `bedrock:`, `bedrock-mantle:`; Anthropic client |
| [Google Cloud / Vertex AI](https://pydantic.dev/docs/ai/models/google-cloud/) | Cloud platform | `google-cloud:`; Anthropic client |
| [Microsoft Azure / Foundry](https://pydantic.dev/docs/ai/models/azure/) | Cloud platform | `azure:`, `azure-responses:`; Anthropic client |
| [Alibaba Cloud / Qwen (DashScope)](https://pydantic.dev/docs/ai/models/compatible-apis/#alibaba-cloud-model-studio-dashscope) | Cloud platform; model developer | `alibaba:` |
| [Cerebras](https://pydantic.dev/docs/ai/models/cerebras/) | Inference platform | `cerebras:` |
| [Cohere](https://pydantic.dev/docs/ai/models/cohere/) | Model developer | `cohere:` |
| [Crusoe](https://pydantic.dev/docs/ai/models/crusoe/) | Inference platform | `crusoe:` |
| [DeepSeek](https://pydantic.dev/docs/ai/models/deepseek/) | Model developer | `deepseek:`; explicit Responses model |
| [Fireworks AI](https://pydantic.dev/docs/ai/models/compatible-apis/#fireworks-ai) | Inference platform | `fireworks:` |
| [GitHub Copilot](https://pydantic.dev/docs/ai/models/github-copilot/) | Subscription access | `github-copilot:` |
| [Google / Gemini API decisions](https://pydantic.dev/docs/ai/models/google/#decisions-api) | [Decision model](https://pydantic.dev/docs/ai/models/decision/) | `google-decisions:` |
| [Groq](https://pydantic.dev/docs/ai/models/groq/) | Inference platform | `groq:` |
| [Heroku AI](https://pydantic.dev/docs/ai/models/compatible-apis/#heroku-ai) | Cloud platform | `heroku:` |
| [Hugging Face](https://pydantic.dev/docs/ai/models/huggingface/) | Inference platform | `huggingface:` |
| [LiteLLM](https://pydantic.dev/docs/ai/models/compatible-apis/#litellm) | Self-hosted gateway (over HTTP; doesn’t use the `litellm` package) | `litellm:` |
| [Meta](https://pydantic.dev/docs/ai/models/meta/) | Model developer | `meta:` |
| [Mistral](https://pydantic.dev/docs/ai/models/mistral/) | Model developer | `mistral:` |
| [Moonshot AI / Kimi](https://pydantic.dev/docs/ai/models/moonshotai/) | Model developer | `moonshotai:` |
| [Nebius AI Studio](https://pydantic.dev/docs/ai/models/compatible-apis/#nebius-ai-studio) | Inference platform | `nebius:` |
| [Ollama](https://pydantic.dev/docs/ai/models/ollama/) | Local inference; cloud inference | `ollama:` |
| [OpenAI ChatGPT plan usage](https://pydantic.dev/docs/ai/models/openai-chatgpt/) | Subscription access for your app’s users | `openai-chatgpt:` with an explicit provider |
| [OpenAI Codex](https://pydantic.dev/docs/ai/models/openai-codex/) | Subscription access | `openai-codex:` |
| [OpenAI Decisions API](https://pydantic.dev/docs/ai/models/openai/#decisions-api) | [Decision model](https://pydantic.dev/docs/ai/models/decision/) | `openai-decisions:` |
| [OpenRouter](https://pydantic.dev/docs/ai/models/openrouter/) | Gateway | `openrouter:` |
| [OVHcloud AI Endpoints](https://pydantic.dev/docs/ai/models/compatible-apis/#ovhcloud-ai-endpoints) | Cloud platform | `ovhcloud:` |
| [SambaNova](https://pydantic.dev/docs/ai/models/compatible-apis/#sambanova) | Inference platform | `sambanova:` |
| [Snowflake Cortex](https://pydantic.dev/docs/ai/models/snowflake/) | Cloud platform | `snowflake:` |
| [System One API](https://pydantic.dev/docs/ai/models/system-one/) | [Decision models](https://pydantic.dev/docs/ai/models/decision/) such as CLM, Laya, and Ollama’s | `system-one:` |
| [Together AI](https://pydantic.dev/docs/ai/models/compatible-apis/#together-ai) | Inference platform | `together:` |
| [TypeSafe (Jev)](https://pydantic.dev/docs/ai/models/typesafe/) | [Decision model](https://pydantic.dev/docs/ai/models/decision/) | `typesafe:` |
| [Vercel AI Gateway](https://pydantic.dev/docs/ai/models/compatible-apis/#vercel-ai-gateway) | Gateway | `vercel:` |
| [vLLM](https://pydantic.dev/docs/ai/models/compatible-apis/#vllm) | Self-hosted inference | `vllm:` |
| [xAI](https://pydantic.dev/docs/ai/models/xai/) | Model developer | `xai:` |
| [Z.AI](https://pydantic.dev/docs/ai/models/zai/) | Model developer | `zai:` |

The service descriptions help you find a deployment option; a company may offer more than one kind of service. Feature support depends on the model and API you select, even when two services use the same API format.

For work that isn’t waiting on a user, Anthropic, OpenAI and Gemini API models can also send requests through their providers’ [batch APIs](https://pydantic.dev/docs/ai/core-concepts/batch/), at about half the price.

For an OpenAI-compatible endpoint not listed here, use [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_compatible.OpenAICompatibleProvider) with a name for the service, as [Other endpoints](https://pydantic.dev/docs/ai/models/compatible-apis/#other-endpoints) explains; for any other API, implement a [custom model](#custom-models).

For testing and development, use [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/) or [`FunctionModel`](https://pydantic.dev/docs/ai/api/models/function/).

### OpenAI-compatible Providers

Many entries in the directory use OpenAI-compatible APIs. Their setup guides cover which model class to use; [Other compatible APIs](https://pydantic.dev/docs/ai/models/compatible-apis/) explains custom endpoints, which use [`OpenAICompatibleProvider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.openai_compatible.OpenAICompatibleProvider) rather than `OpenAIProvider`, and model profiles.

## Models, providers, and profiles

Pydantic AI uses a few key terms to describe how it interacts with different LLMs:

- **Model**: This refers to the Pydantic AI class used to make requests following a specific LLM API (generally by wrapping a vendor-provided SDK, like the `openai` python SDK). These classes implement a vendor-SDK-agnostic API, ensuring a single Pydantic AI agent is portable to different LLM vendors without any other code changes just by swapping out the Model it uses. Model classes are named roughly in the format `<VendorSdk>Model`, for example, we have `OpenAIChatModel`, `AnthropicModel`, `GoogleModel`, etc. When using a Model class, you specify the actual LLM model name (e.g., `gpt-6.1-sol`, `claude-sonnet-5-5`, `gemini-3.8-flash`) as a parameter.
- **Provider**: This refers to provider-specific classes which handle the authentication and connections to an LLM vendor. Passing a non-default *Provider* as a parameter to a Model is how you can ensure that your agent will make requests to a specific endpoint, or make use of a specific approach to authentication (e.g., you can use Azure auth with the `OpenAIChatModel` by way of the `AzureProvider`). In particular, this is how you can make use of an AI gateway, or an LLM vendor that offers API compatibility with the vendor SDK used by an existing Model (such as `OpenAIChatModel`).
- **Profile**: This refers to a description of how requests to a specific model or family of models need to be constructed to get the best results, independent of the model and provider classes used. For example, different models have different restrictions on the JSON schemas that can be used for tools, and the same schema transformer needs to be used for Gemini models whether you’re using `GoogleModel` or `OpenAIChatModel` with `OpenRouterProvider`.

When you instantiate an [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) with just a name formatted as `<provider>:<model>`, e.g. `openai:gpt-6.1-sol` or `openrouter:google/gemini-3-pro-preview`, Pydantic AI will automatically select the appropriate model class, provider, and profile. If you want to use a different provider or profile, you can instantiate a model class directly and pass in `provider` and/or `profile` arguments.

### Inspecting a model’s profile

A model’s [`ModelProfile`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile) also describes what the model can do. It is a `TypedDict` whose keys are all optional, so you read capability flags with `.get()` on `model.profile` — for example [`supports_text_output`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_text_output), [`supports_tools`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_tools), [`supports_json_schema_output`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_json_schema_output), and [`supported_native_tools`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_native_tools). This is useful when you want to branch on a capability rather than discover a limitation at request time — for example checking whether a model supports text generation, tool calling, native JSON-schema output, or a specific native tool before relying on it:

```python
from pydantic_ai.models.test import TestModel
from pydantic_ai.native_tools import WebSearchTool

model = TestModel()
profile = model.profile

print(profile.get('supports_tools'))
#> True
print(profile.get('supports_text_output'))
#> True
print(profile.get('supports_json_schema_output'))
#> False
print(WebSearchTool in profile.get('supported_native_tools', frozenset()))
#> True
```

The profile also says which files the model accepts: [`supports_image_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_image_input), [`supports_document_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_document_input), [`supports_audio_file_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_audio_file_input) and [`supports_video_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_video_input) for each kind of file, narrowed to particular media types by [`supported_image_media_types`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_image_media_types), [`supported_document_media_types`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_document_media_types), [`supported_audio_media_types`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_audio_media_types) and [`supported_video_media_types`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_video_media_types). The image, audio and video sets are unset by default, so a file of those kinds is judged by its kind alone; where a profile sets one, a file of a media type outside it counts as one the model can’t read. The [OpenAI](https://pydantic.dev/docs/ai/models/openai/#image-input), [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/#image-input), [Google](https://pydantic.dev/docs/ai/models/google/#document-image-audio-and-video-input) and [xAI](https://pydantic.dev/docs/ai/models/xai/#image-input) pages list the formats their models read. Each model class also turns off what its API can’t take, whatever the profile says: [`AnthropicModel`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel), for example, reads neither audio nor video, and only PDF and plain-text documents, and [OpenAI Chat Completions](https://pydantic.dev/docs/ai/models/openai/#audio-input) takes only WAV and MP3 audio. A file a tool returns that the model can’t take is [sent as a note naming it](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance), and the [File Understanding](https://pydantic.dev/docs/ai/capabilities/file-understanding/) capability reads the same flags to decide which files to describe in text first.

`model.profile` is usually the fully *resolved* profile: keys from [`DEFAULT_PROFILE`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.DEFAULT_PROFILE) are merged with the provider’s defaults, so `profile.get('supports_tools')` returns a value. If you supply `profile=` as a callable (or otherwise have a partial profile dict), pass the default as the fallback, `profile.get('supports_tools', DEFAULT_PROFILE['supports_tools'])` (after importing `DEFAULT_PROFILE`), to tolerate missing keys. Individual model adapters expose their resolved profile the same way, so the same check works whether the model was selected automatically from a `<provider>:<model>` name or instantiated directly. A [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) is different: it has no single profile because its candidate models may have different capabilities. Inspect the profile of each model in `fallback_model.models` instead. With the [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) capability, each attempt is made with a model of its own, so a capability hook reads the profile of the model serving the attempt from `request_context.model`. Don’t confuse profiles with [Capabilities](https://pydantic.dev/docs/ai/capabilities/overview/), which are reusable bundles of tools, hooks, and settings you add to an agent — the profile describes what the underlying model itself supports.

The profile also carries the model’s [`context_window`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.context_window): the maximum number of tokens it can handle in a single request, or `None` when unknown. Every model, including a `FallbackModel` and wrappers like [`InstrumentedModel`](https://pydantic.dev/docs/ai/api/models/instrumented/#pydantic_ai.models.instrumented.InstrumentedModel), exposes it as [`model.context_window`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.AbstractModel.context_window); a fallback model reports the smallest window among its candidates, so history that fits it fits whichever candidate answers. Inside a run, [`ctx.context_window_used`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.context_window_used) reports the fraction in use, or `None` when it cannot be calculated. See [Compact when the context window fills](https://pydantic.dev/docs/ai/core-concepts/message-history/#compact-when-the-context-window-fills) for an example that handles this case.

## HTTP Client Lifecycle

When a [`Provider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.Provider) creates its own HTTP client (i.e. you don’t pass a custom `http_client`), it owns that client’s lifecycle. Using the [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) as an async context manager keeps the HTTP client open across every run inside the block, so the runs reuse its connections, and closes it cleanly on exit:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')

async def main():
    async with agent:
        result = await agent.run('What is the capital of France?')
        print(result.output)
        #> The capital of France is Paris.
```

You can also use a [`Model`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model) or [`Provider`](https://pydantic.dev/docs/ai/api/pydantic-ai/providers/#pydantic_ai.providers.Provider) directly as an async context manager for the same effect. In a long-lived service such as a web server, enter the agent once when the service starts and run it inside that block.

What happens without that block depends on where a run’s model comes from:

- **The agent’s own model, or a `Model` instance passed to a run:** the provider creates its HTTP client along with the model, and runs on the same event loop reuse it. Nothing closes the client until you enter and exit the agent, model or provider. An agent created with `defer_model_check=True` treats its model name like a model name passed to a run.
- **A model name passed to a run**, as in `agent.run(..., model='openai:gpt-6.1-sol')`, or returned by a [model selector](https://pydantic.dev/docs/ai/capabilities/select-model/): the run creates a new provider, with a new HTTP client, and closes the client when it ends, so no connections are reused. Inside `async with agent:`, the agent instead creates one provider per model name and reuses it for later runs until the block exits. A [`resolve_model_id`](https://pydantic.dev/docs/ai/capabilities/resolve-model-id/) capability can resolve the same name differently for each run, so with one, each run resolves the name again.
- **A `Model` instance a model selector returns:** each run enters and exits the model, which closes its provider’s HTTP client at the end of the run and creates a new one for the next. Inside `async with agent:`, a model that’s selected again, which the agent tells apart by identity, is instead entered by the agent and kept open until the block exits. A new instance the selector builds for a single run is still closed when that run ends. With a `resolve_model_id` capability, each run enters and exits the model again.

An HTTP client’s connections belong to the event loop that opened them, so a client that stays open between runs can’t be used from another event loop. Repeated [`run_sync()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_sync) calls in one thread share an event loop, and so share the client. When a run of an agent that isn’t entered is on a new event loop and the one the client was last used on isn’t running, as with a second `asyncio.run(agent.run(...))`, the provider creates a new client for it. The old one isn’t closed, as it can’t be closed from another event loop, and its own has usually closed already. So when each run gets its own event loop, enter the agent inside it to close the client before its event loop is. That includes `run_sync()` calls from a pool of worker threads, as in a FastAPI `def` endpoint, a Django or Flask view or a `ThreadPoolExecutor`: each thread has its own event loop, so a call on a different thread than the last one replaces the client, and the old one keeps its connections open until it’s garbage collected. Give each thread its own model, or enter the agent in each thread. Event loops that run at the same time would share the client, so give each its own model as well. A durable execution run leaves the clients alone, as its requests are sent from the engine’s activities, steps or tasks.

Pydantic AI only ever closes or replaces an HTTP client it created itself. A client you pass in is yours to close, whether it’s an `http_client` or a provider SDK client, such as `openai_client`, `anthropic_client` (including `AsyncAnthropicVertex`), Google’s `client`, Hugging Face’s `hf_client`, or `xai_client`. It’s also kept when a run is on another event loop, where it can fail with the provider SDK’s own error, such as `RuntimeError: Event loop is closed`.

### Configuring the HTTP client

The HTTP clients Pydantic AI creates have a 600-second timeout (20 minutes for [Google](https://pydantic.dev/docs/ai/models/google/#long-decode)) with a 5-second connect timeout, and a connection pool of up to 1000 connections, of which up to 100 are kept alive while idle. These are the defaults of the OpenAI and Anthropic SDKs’ own clients. To change them, create a client with [`create_async_httpx2_client()`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.create_async_httpx2_client), which keeps the remaining defaults and Pydantic AI’s `User-Agent`, and pass it to the provider as `http_client`:

configure\_http\_client.py

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
        print(result.output)
        #> The capital of France is Paris.
```

Because you created the client, you close it, here by leaving the `async with` block. Passing the same client to several providers makes them share its connection pool. It also takes a `transport`, such as a retrying one: see [A retrying client](https://pydantic.dev/docs/ai/core-concepts/retries/#a-retrying-client).

The Groq, Cohere and GitHub providers take a legacy `httpx.AsyncClient` instead, which you build yourself with the same arguments, for example `httpx.AsyncClient(timeout=httpx.Timeout(120, connect=5), limits=httpx.Limits(max_connections=200, max_keepalive_connections=50))`.

## Custom Models

To implement support for a model API that’s not already supported, you will need to subclass the [`Model`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model) abstract base class. For streaming, you’ll also need to implement the [`StreamedResponse`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.StreamedResponse) abstract base class.

A subclass with dataclass equality, including one that inherits it, compares its `settings` and `profile` along with its dataclass fields. A subclass that hashes by identity, such as a direct non-dataclass subclass of `Model` or a direct `@dataclass(eq=False)` subclass, compares by identity. Its `repr` shows its `model_name`, any dataclass fields, and its `settings` and `profile` when set. Define `__eq__` or `__repr__` on the subclass to replace either.

The best place to start is to review the source code for existing implementations, e.g. [`OpenAIChatModel`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai/_chat_model.py).

For details on when we’ll accept contributions adding new models to Pydantic AI, see the [contributing guidelines](https://pydantic.dev/docs/ai/project/contributing/#new-model-rules).

## HTTP Request Concurrency

You can limit the number of concurrent HTTP requests to a model using the [`ConcurrencyLimitedModel`](https://pydantic.dev/docs/ai/api/pydantic-ai/concurrency/#pydantic_ai.ConcurrencyLimitedModel) wrapper. This is useful for respecting rate limits or managing resource usage when running many agents in parallel.

model\_concurrency.py

```python
import asyncio

from pydantic_ai import Agent, ConcurrencyLimitedModel

# Wrap a model with concurrency limiting
model = ConcurrencyLimitedModel('openai:gpt-6.1-sol', limiter=5)

# Multiple agents can share this rate-limited model
agent = Agent(model)

async def main():
    # These will be rate-limited to 5 concurrent HTTP requests
    results = await asyncio.gather(
        *[agent.run(f'Question {i}') for i in range(20)]
    )
    print(len(results))
    #> 20
```

The `limiter` parameter accepts:

- An integer for simple limiting (e.g., `limiter=5`)
- A [`ConcurrencyLimit`](https://pydantic.dev/docs/ai/api/pydantic-ai/concurrency/#pydantic_ai.ConcurrencyLimit) for advanced configuration with backpressure control
- A [`ConcurrencyLimiter`](https://pydantic.dev/docs/ai/api/pydantic-ai/concurrency/#pydantic_ai.ConcurrencyLimiter) for sharing limits across multiple models

### Shared Concurrency Limits

To share a concurrency limit across multiple models (e.g., different models from the same provider), you can create a [`ConcurrencyLimiter`](https://pydantic.dev/docs/ai/api/pydantic-ai/concurrency/#pydantic_ai.ConcurrencyLimiter) and pass it to multiple `ConcurrencyLimitedModel` instances:

shared\_concurrency.py

```python
import asyncio

from pydantic_ai import Agent, ConcurrencyLimitedModel, ConcurrencyLimiter

# Create a shared limiter with a descriptive name
shared_limiter = ConcurrencyLimiter(max_running=10, name='openai-pool')

# Both models share the same concurrency limit
model1 = ConcurrencyLimitedModel('openai:gpt-6.1-sol', limiter=shared_limiter)
model2 = ConcurrencyLimitedModel('openai:gpt-6-luna', limiter=shared_limiter)

agent1 = Agent(model1)
agent2 = Agent(model2)

async def main():
    # Total concurrent requests across both agents limited to 10
    results = await asyncio.gather(
        *[agent1.run(f'Question {i}') for i in range(10)],
        *[agent2.run(f'Question {i}') for i in range(10)],
    )
    print(len(results))
    #> 20
```

An agent and the `ConcurrencyLimitedModel` used for its own model request must use separate `ConcurrencyLimiter` instances. If you set `Agent(max_concurrency=...)` as well as `ConcurrencyLimitedModel(limiter=...)`, using the same instance raises [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). Nested `ConcurrencyLimitedModel` wrappers also need different limiter instances.

Re-entering a `ConcurrencyLimiter` through an agent on the same task raises `RuntimeError`; use a separate limiter for the nested run. When an agent delegates to another agent through a tool, each run or model request acquires its own slot. A shared pool must have enough capacity for the parent and nested operation to run at the same time.

When instrumentation is enabled, requests waiting for a concurrency slot appear as spans with attributes showing the queue depth and configured limits. The `name` parameter on `ConcurrencyLimiter` helps identify shared limiters in traces.

## Handling Model API Errors

When a request to a model provider fails, Pydantic AI raises a [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError) rather than the provider SDK’s own exception, which remains available as `__cause__`. When the provider says what went wrong, the error is an instance of one of these categories, whichever provider it came from:

| Exception | Raised when |
| --- | --- |
| [`ModelRateLimitError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRateLimitError) | A rate limit was reached, e.g. an HTTP 429. Waiting and retrying may help. |
| [`ModelQuotaExceededError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelQuotaExceededError) | The provider said the account’s quota, credits, or billing is exhausted, e.g. an HTTP 402 or OpenAI’s `insufficient_quota`. Waiting won’t help. |
| [`ModelUnavailableError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelUnavailableError) | The provider or model is temporarily unavailable, e.g. an HTTP 503 or a gRPC `UNAVAILABLE` sent by the provider. |
| [`ModelOverloadedError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelOverloadedError) | The provider said it’s unavailable because it’s overloaded, e.g. an HTTP 529 or Anthropic’s `overloaded_error`. A subclass of `ModelUnavailableError`. |
| [`ModelServerError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelServerError) | The provider failed with another server error, e.g. an HTTP 500, 502, or 504. |
| [`ModelConnectionError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelConnectionError) | The request could not reach the provider, or its response could not be read. Its [`phase`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelConnectionError.phase) says whether the request may have reached the provider. |
| [`ModelTimeoutError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelTimeoutError) | An attempt timed out at the transport layer. A subclass of `ModelConnectionError`. A [`request_timeout`](https://pydantic.dev/docs/ai/core-concepts/timeouts/#model-request-deadlines) deadline over all attempts raises [`ModelRequestTimeout`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRequestTimeout) instead. |
| [`ModelRequestRejectedError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRequestRejectedError) | The provider rejected the request itself, e.g. an HTTP 400, 413 or 422, so sending it again unchanged won’t succeed. |
| [`ModelContextWindowExceededError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelContextWindowExceededError) | The input exceeds the model’s context window. A subclass of `ModelRequestRejectedError`. |
| [`ModelAuthenticationError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAuthenticationError) | The provider rejected the credentials, or doesn’t allow them to make the request, e.g. an HTTP 401 or 403. A subclass of `ModelRequestRejectedError`. |
| [`ModelNotFoundError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelNotFoundError) | The provider couldn’t find the model, deployment or other resource the request names, e.g. an HTTP 404. A subclass of `ModelRequestRejectedError`. |

A provider’s own signal decides between categories that share a status code: a 429 is a rate limit unless the provider says the quota is exhausted (the Gemini API names the exceeded quotas in its `RESOURCE_EXHAUSTED` error, so its daily quota is a `ModelQuotaExceededError`), and a 503 is only unavailable unless the provider says it’s overloaded. Anthropic’s tier spend cap is a 429 too, but its `enforced_spend_limit_reached` error code makes it a `ModelQuotaExceededError`. A 400 is a `ModelRequestRejectedError`, or one of its subclasses when the provider says why: a `ModelContextWindowExceededError`, a `ModelNotFoundError`, or a `ModelAuthenticationError` (the Gemini API sends `API_KEY_INVALID` as a 400). Exhausted credits, a reached spend limit, or disabled billing are a `ModelQuotaExceededError` instead, even when the provider sends them as a 400, as Anthropic and the Gemini API do.

Other errors are raised as a plain `ModelAPIError` or [`ModelHTTPError`](#handling-http-errors), as they always were. Categories are assigned from the provider’s error code or type where it sends one, and from the error message only where the provider offers nothing else. Every `ModelAPIError` also exposes the provider’s [`provider_error_code`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.provider_error_code), [`provider_error_type`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.provider_error_type), and error [`body`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.body), when available.

[Embedding models](https://pydantic.dev/docs/ai/guides/embeddings/#handling-errors) raise the same errors.

An error is reported the same way whether the provider sent it before a stream opened or inside an already open stream. For example, both an HTTP 503 from Bedrock and a `serviceUnavailableException` in a Bedrock stream raise a `ModelHTTPError` with status 503 that is also a `ModelUnavailableError`. The second has [`in_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.in_stream) set, so you can still tell them apart.

This lets you decide what to do about a failure without knowing which provider it came from:

handle\_model\_errors.py

```python
from pydantic_ai import Agent, ModelContextWindowExceededError, ModelRateLimitError

agent = Agent('openai:gpt-6.1-sol')

try:
    result = agent.run_sync('What is the capital of France?', message_history=history)
except ModelRateLimitError as exc:
    raise MyRateLimitException('AI service is rate-limited. Try again shortly.', retry_after=exc.retry_after)
except ModelContextWindowExceededError:
    result = agent.run_sync('What is the capital of France?', message_history=summarize(history))
```

[`retry_after`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.retry_after) is the number of seconds the provider asked you to wait, as a `float`, or `None` if it didn’t say.

See [Compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) for keeping a conversation under the context window in the first place, which is preferable to waiting for `ModelContextWindowExceededError`: model performance usually degrades well before the hard limit.

The categories also tell a failure that may go away apart from one that won’t. If you retry model requests yourself, skip the ones that sending the same request to the same model again can’t fix:

should\_retry.py

```python
from pydantic_ai import (
    ModelAPIError,
    ModelAuthenticationError,
    ModelHTTPError,
    ModelQuotaExceededError,
    ModelRateLimitError,
    ModelRequestRejectedError,
)

def should_retry(error: ModelAPIError) -> bool:
    return not isinstance(error, ModelRequestRejectedError | ModelQuotaExceededError)

print(should_retry(ModelHTTPError.for_category(ModelAuthenticationError, status_code=401, model_name='my-model')))
#> False
print(should_retry(ModelHTTPError.for_category(ModelRateLimitError, status_code=429, model_name='my-model')))
#> True
```

[`ModelAuthenticationError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAuthenticationError), [`ModelNotFoundError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelNotFoundError) and [`ModelContextWindowExceededError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelContextWindowExceededError) are all a `ModelRequestRejectedError`, so `should_retry` skips them too. Under [Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#activity-retries), the activity doesn’t retry them either, as they’re in `non_retryable_model_errors` by default.

### HTTP errors

When a provider returns a 4xx or 5xx response, the error is a [`ModelHTTPError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError), and also an instance of the error category above that it belongs to, if any. The exception exposes the [`status_code`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.status_code), the response [`body`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.body), and the provider’s **response headers** via the [`headers`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.headers) attribute (a `dict[str, str]` with lowercase keys, or `None` for providers that don’t surface headers, such as gRPC-based providers). Its [`retry_after`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError.retry_after) is parsed from the `retry-after-ms` or `Retry-After` header, handling both the integer delta-seconds and HTTP-date formats, or, for a Google error without them, from the `RetryInfo` in its [body](https://pydantic.dev/docs/ai/models/google/#http-retries), and [`provider_retry_hint`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.provider_retry_hint) from the `x-should-retry` header that OpenAI and Anthropic send to say whether retrying may help. A status a [retrying transport](https://pydantic.dev/docs/ai/core-concepts/retries/#error-handling) gave up on carries its body and headers too.

When [OpenAI](https://pydantic.dev/docs/ai/models/openai/), [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/), the [Google Gemini API](https://pydantic.dev/docs/ai/models/google/), [Amazon Bedrock](https://pydantic.dev/docs/ai/models/bedrock/), or [Groq](https://pydantic.dev/docs/ai/models/groq/) reports that a requested model identifier is unavailable, Pydantic AI adds a close known match to the error message when one exists. The suggestion is also available as [`suggested_model_id`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.suggested_model_id). This is best-effort guidance after the provider rejects a request, not local validation: unknown model identifiers remain valid so custom deployments and newly released models continue to work.

When a provider error has a known fix outside the request, such as the [data retention](https://pydantic.dev/docs/ai/models/bedrock/#data-retention) mode Amazon Bedrock requires for some models, Pydantic AI appends guidance to the error message. It is also available as [`hint`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.hint).

A [custom model](#custom-models) can raise the same errors with [`ModelHTTPError.for_category`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError.for_category), which builds a `ModelHTTPError` that is also an instance of the given category, so code that handles either catches it. Its class is named after the category, so tracebacks, `repr()`, OpenTelemetry spans and [`failed_attempts`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.failed_attempts) show it as, say, `ModelRateLimitError`:

custom\_model\_errors.py

```python
from pydantic_ai import ModelHTTPError, ModelRateLimitError

def map_error(status_code: int, body: object) -> ModelHTTPError:
    if status_code == 429:
        return ModelHTTPError.for_category(ModelRateLimitError, status_code=429, model_name='my-model', body=body)
    return ModelHTTPError(status_code, 'my-model', body)

error = map_error(429, {'error': 'Too many requests'})
print(isinstance(error, ModelHTTPError), isinstance(error, ModelRateLimitError))
#> True True
```

## Fallback Model

To make an agent fall back to other models when a provider fails, add the [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) capability. The agent’s model is attempted first, then each of the capability’s models in turn, until one succeeds:

agent\_model\_fallback.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ModelFallback

agent = Agent('openai:gpt-6.1-sol', capabilities=[ModelFallback('anthropic:claude-sonnet-5-5')])
```

`ModelFallback` makes each attempt within the agent’s own request loop, so capabilities see the model that will serve each attempt and prepare the request for it, each attempt is [batched](https://pydantic.dev/docs/ai/core-concepts/batch/) on its own model, and under [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) each attempt is a durable model operation of its own. See [Model Fallback](https://pydantic.dev/docs/ai/capabilities/model-fallback/) for how it works, and [Migrating from `FallbackModel`](https://pydantic.dev/docs/ai/capabilities/model-fallback/#migrating-from-fallbackmodel) to move an agent over. [Recovery scopes compared](https://pydantic.dev/docs/ai/core-concepts/retries/#recovery-scopes) sets fallback beside retrying the same model and the other ways a request is attempted again.

The rest of this section covers [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel), which remains the way to fall back with [direct model requests](https://pydantic.dev/docs/ai/core-concepts/direct/) or a standalone model, outside an agent. Its `fallback_on` policies, failed attempts and telemetry work the same way under `ModelFallback`, so the handler examples below apply to both.

You can use [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) to attempt multiple models in sequence until one succeeds. Pydantic AI can switch to the next model when the current model raises an exception (like a 4xx/5xx API error) **or** when the response content indicates a semantic failure (like a truncated response or a failed native tool call).

By default, fallback triggers on [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError) (4xx/5xx API errors, and connection failures or timeouts before the response starts), so you don’t need to configure anything for the most common use case. That includes every [error category](#handling-model-api-errors): rate limits, exhausted quota, unavailable or overloaded providers, server errors, connection failures and timeouts, and rejected requests, including [context window overflows](#context-window-overflow): another model or provider may accept a request, credentials or model name the first one rejected, and a model with a larger context window may accept an input that overflowed another model’s. To fall back only on some of them, pass those categories as `fallback_on`, e.g. `fallback_on=(ModelRateLimitError, ModelUnavailableError, ModelServerError)`.

This behavior is controlled by the `fallback_on` parameter (see [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel)), which accepts exception types, exception handlers, and response handlers — all of which can be sync or async.

In the following example, the agent first makes a request to the OpenAI model (which fails due to an invalid API key), and then falls back to the Anthropic model.

fallback\_model.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel

openai_model = OpenAIChatModel('gpt-6.1-sol')
anthropic_model = AnthropicModel('claude-sonnet-5-5')
fallback_model = FallbackModel(openai_model, anthropic_model)

agent = Agent(fallback_model)
response = agent.run_sync('What is the capital of France?')
print(response.output)
#> The capital of France is Paris.

print(response.all_messages())
"""
[
    ModelRequest(
        parts=[
            UserPromptPart(
                content='What is the capital of France?',
                timestamp=datetime.datetime(...),
            )
        ],
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
    ),
    ModelResponse(
        parts=[TextPart(content='The capital of France is Paris.')],
        usage=RequestUsage(cost=Decimal('0.000182'), input_tokens=56, output_tokens=7),
        model_name='claude-sonnet-5-5',
        model_id='fallback:openai:gpt-6.1-sol,anthropic:claude-sonnet-5-5',
        timestamp=datetime.datetime(...),
        run_id='...',
        conversation_id='...',
        failed_attempts=[
            ModelRequestAttempt(
                model_name='gpt-6.1-sol',
                provider_name='openai',
                outcome='error',
                error="ModelHTTPError: status_code: 401, model_name: gpt-6.1-sol, body: {'error': 'Invalid API Key'}",
                timestamp=datetime.datetime(...),
                duration=datetime.timedelta(...),
            )
        ],
    ),
]
"""
```

The `ModelResponse` message above indicates in the `model_name` field that the output was returned by the Anthropic model, which is the second model specified in the `FallbackModel`.

### Per-Model Settings

You can configure different [`ModelSettings`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings) for each model in a fallback chain by passing the `settings` parameter when creating each model. This is particularly useful when different providers have different optimal configurations:

fallback\_model\_per\_settings.py

```python
from pydantic_ai import Agent, ModelSettings
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel

# Configure each model with provider-specific optimal settings
openai_model = OpenAIChatModel(
    'gpt-6.1-sol',
    settings=ModelSettings(thinking='high', max_tokens=2000)  # More reasoning for OpenAI
)
anthropic_model = AnthropicModel(
    'claude-sonnet-5-5',
    settings=ModelSettings(thinking='low', max_tokens=1000)  # A quicker fallback
)

fallback_model = FallbackModel(openai_model, anthropic_model)
agent = Agent(fallback_model)

result = agent.run_sync('Write a creative story about space exploration')
print(result.output)
"""
In the year 2157, Captain Maya Chen piloted her spacecraft through the vast expanse of the Andromeda Galaxy. As she discovered a planet with crystalline mountains that sang in harmony with the cosmic winds, she realized that space exploration was not just about finding new worlds, but about finding new ways to understand the universe and our place within it.
"""
```

In this example, if the OpenAI model fails, the agent will automatically fall back to the Anthropic model with its own configured settings. The `FallbackModel` itself doesn’t have settings - it uses the individual settings of whichever model successfully handles the request.

### Exception Handling

The next example demonstrates the exception-handling capabilities of `FallbackModel`. If all models fail, a [`FallbackExceptionGroup`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.FallbackExceptionGroup) is raised, which contains all the exceptions encountered during the `run` execution.

fallback\_model\_failure.py

```python
from pydantic_ai import Agent, ModelAPIError
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.openai import OpenAIChatModel

openai_model = OpenAIChatModel('gpt-6.1-sol')
anthropic_model = AnthropicModel('claude-sonnet-5-5')
fallback_model = FallbackModel(openai_model, anthropic_model)

agent = Agent(fallback_model)
try:
    response = agent.run_sync('What is the capital of France?')
except* ModelAPIError as exc_group:
    for exc in exc_group.exceptions:
        print(exc)
```

By default, the `FallbackModel` only moves on to the next model if the current model raises a [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError), which includes [`ModelHTTPError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelHTTPError). You can customize this behavior by passing a custom `fallback_on` argument to the `FallbackModel` constructor.

### Context Window Overflow

`FallbackModel` also falls back when a model raises [`ModelContextWindowExceededError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelContextWindowExceededError), since a later model in the chain may have a larger context window. If the whole chain fails, the overflow is in the [`FallbackExceptionGroup`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.FallbackExceptionGroup), where `except* ModelContextWindowExceededError` reaches it. If none of your models has a larger window, you can avoid sending the oversized request to each of them by excluding the overflow from `fallback_on`, so it propagates as is:

fallback\_without\_overflow.py

```python
from pydantic_ai import Agent, ModelContextWindowExceededError, ModelAPIError
from pydantic_ai.models.fallback import FallbackModel

def fallback_on(exc: Exception) -> bool:
    return isinstance(exc, ModelAPIError) and not isinstance(exc, ModelContextWindowExceededError)

agent = Agent(FallbackModel('openai:gpt-6.1-sol', 'anthropic:claude-sonnet-5-5', fallback_on=fallback_on))

try:
    result = agent.run_sync('What is the capital of France?', message_history=history)
except ModelContextWindowExceededError:
    result = agent.run_sync('What is the capital of France?', message_history=summarize(history))
```

### Failed attempts and usage

The response that answers lists every attempt the `FallbackModel` moved on from in [`failed_attempts`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.failed_attempts), in order. Each [`ModelRequestAttempt`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequestAttempt) records the model and provider it tried, whether it raised an error (with the error as `'ExceptionType: message'`) or returned a response a [response handler](#response-based-fallback) rejected, when it started and how long it took, and the usage the provider reported for it. An attempt that raised has no usage, as the provider reported none. When every model fails, the same attempts are on the [`FallbackExceptionGroup`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.FallbackExceptionGroup)’s `attempts`.

A rejected response was still generated and billed, so its tokens and cost are added to the run’s [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) and count towards the token and cost limits in [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits). They stay on the attempt rather than being folded into the answering response’s `usage`, and the rejected response itself is not added to the message history. A fallback attempt isn’t a response the agent acted on, so it doesn’t count towards [`request_limit`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits.request_limit).

The rejected responses’ usage counts when every model fails, too. If it exceeds a limit, [`UsageLimitExceeded`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UsageLimitExceeded) is raised with the `FallbackExceptionGroup` as its `__cause__`.

The rejected responses’ usage also counts when the request ends another way: a later model raises an error that `fallback_on` doesn’t cover, the run is cancelled or times out.

fallback\_model\_attempts.py

```python
from pydantic_ai import Agent, ModelMessage, ModelResponse, OutputTokenLimitExceeded, TextPart
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.usage import RequestUsage

def truncated(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    return ModelResponse(
        parts=[TextPart('The capital of France is')],
        usage=RequestUsage(input_tokens=60, output_tokens=100),
        finish_reason='length',
    )

def complete(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    return ModelResponse(
        parts=[TextPart('The capital of France is Paris.')],
        usage=RequestUsage(input_tokens=60, output_tokens=8),
    )

fallback_model = FallbackModel(
    FunctionModel(truncated, model_name='primary'),
    FunctionModel(complete, model_name='backup'),
    fallback_on=OutputTokenLimitExceeded,
)
agent = Agent(fallback_model)
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.
print(result.usage)
#> RunUsage(input_tokens=120, output_tokens=108, requests=1)
print(result.response.usage)
#> RequestUsage(input_tokens=60, output_tokens=8)
for attempt in result.response.failed_attempts or []:
    print(attempt.model_name, attempt.outcome, attempt.usage)
    #> primary rejected RequestUsage(input_tokens=60, output_tokens=100)
```

When the agent is [instrumented](https://pydantic.dev/docs/ai/integrations/logfire/), the model request (`chat`) span describes the model that answered and ends OK. Each attempt the `FallbackModel` moved on from gets its own child span, `model request attempt <model name>`, which ends with an ERROR status, the way a failed tool call gets its own span inside a successful agent run. An error is recorded on that span as an exception, and a response rejected by a [response handler](#response-based-fallback), or as a refusal, carries its usage, cost and finish reason instead, as a `chat` span would. Each attempt span names the model it tried in its `gen_ai.provider.name` and `gen_ai.request.model` attributes, and gives its zero-based position among the request’s attempts in `pydantic_ai.model_request.attempt`. With [`include_content=False`](https://pydantic.dev/docs/ai/integrations/logfire/#excluding-prompts-and-completions), the exception keeps only its type. The attempt span is created once the attempt has failed, so spans the tried model opens itself, such as a [decision model](https://pydantic.dev/docs/ai/models/decision/)’s `decide` span, sit beside it under the `chat` span rather than inside it.

### Response-Based Fallback

In addition to exception-based fallback, you can also trigger fallback based on the **content** of a model’s response. This is useful when a model returns a successful HTTP response (no exception), but the response content indicates a semantic failure — for example, an unexpected finish reason or a native tool reporting failure.

The `fallback_on` parameter accepts:

- A tuple of exception types: `(ModelAPIError, ModelHTTPError)`
- An exception handler (sync or async): `lambda exc: isinstance(exc, MyError)`
- A response handler (sync or async): `def check(r: ModelResponse) -> bool`
- A list mixing all of the above: `[ModelAPIError, exc_handler, response_handler]`

Handler type is auto-detected by inspecting type hints on the first parameter. If the first parameter is hinted as [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse), it’s a response handler. Otherwise (including untyped handlers and lambdas), it’s an exception handler.

As the hints are resolved at runtime, every annotated type in the handler signature must be imported at runtime rather than only under `if TYPE_CHECKING:`. If any annotation can’t be resolved, a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) is raised instead of the handler being silently treated as an exception handler.

#### Finish Reason Example

A simple use case is checking the model’s finish reason — for example, falling back if the response was truncated due to length limits:

fallback\_on\_finish\_reason.py

```python
from pydantic_ai import Agent
from pydantic_ai.messages import FinishReason, ModelResponse
from pydantic_ai.models.fallback import FallbackModel

def bad_finish_reason(response: ModelResponse) -> bool:
    """Fallback if the model stopped due to length limit, content filter, or error."""
    reason: FinishReason | None = response.finish_reason
    # Trigger fallback for problematic finish reasons
    return reason in ('length', 'content_filter', 'error')

fallback_model = FallbackModel(
    'openai:gpt-6.1-sol',
    'anthropic:claude-sonnet-5-5',
    fallback_on=bad_finish_reason,
)

agent = Agent(fallback_model)
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.
```

#### Native Tool Failure Example

A more complex use case is when using native tools like web search or URL fetching. For example, Google’s native web fetch, enabled with the [`WebFetch`](https://pydantic.dev/docs/ai/capabilities/web-fetch/) capability, may return a successful response with a status indicating the URL fetch failed. This example uses the [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) capability, which takes the same `fallback_on`:

fallback\_on\_native\_tool.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ModelFallback, WebFetch
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel

def web_fetch_failed(response: ModelResponse) -> bool:
    """Check if a web_fetch native tool failed to retrieve content."""
    for call, result in response.native_tool_calls:
        if call.tool_name != 'web_fetch':
            continue
        if not isinstance(result.content, list):
            continue
        for item in result.content:
            if isinstance(item, dict):
                status = item.get('url_retrieval_status', '')
                if status and status != 'URL_RETRIEVAL_STATUS_SUCCESS':
                    return True
    return False

google_model = GoogleModel('gemini-3.8-flash')
anthropic_model = AnthropicModel('claude-sonnet-5-5')

agent = Agent(
    google_model,
    capabilities=[
        WebFetch(),
        # Auto-detected as response handler via type hint
        ModelFallback(anthropic_model, fallback_on=web_fetch_failed),
    ],
)

# If Google's web_fetch fails, automatically falls back to Anthropic
result = agent.run_sync('Summarize https://ai.pydantic.dev')
print(result.output)
"""
Pydantic AI is a Python agent framework for building production-grade LLM applications.
"""
```

Response handlers receive the [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse) returned by the model and should return `True` to trigger fallback to the next model, or `False` to accept the response.

Without a handler, an empty or thinking-only response is re-prompted on the same model, up to the output retry limit (see the note above). A response handler can send it to the backup model instead, by rejecting a successful response that contains no text or tool call. This predicate is for a text-output agent; if your output type accepts other response parts, include those parts in the predicate. Include [`ModelAPIError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelAPIError) in the handler list so API errors still fall back; see [Combining Handlers](#combining-handlers).

fallback\_on\_empty\_response.py

```python
from pydantic_ai import (
    Agent,
    ModelAPIError,
    ModelMessage,
    ModelResponse,
    NativeToolCallPart,
    TextPart,
    ToolCallPart,
)
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.models.function import AgentInfo, FunctionModel

def empty(_messages: list[ModelMessage], _info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart('')])

def answer(_messages: list[ModelMessage], _info: AgentInfo) -> ModelResponse:
    return ModelResponse(parts=[TextPart('The capital of France is Paris.')])

def has_no_actionable_output(response: ModelResponse) -> bool:
    return not any(
        (isinstance(part, TextPart) and part.has_content())
        or isinstance(part, (ToolCallPart, NativeToolCallPart))
        for part in response.parts
    )

agent = Agent(
    # These deterministic models simulate an empty primary response and a backup answer.
    FallbackModel(
        FunctionModel(empty, model_name='primary'),
        FunctionModel(answer, model_name='backup'),
        fallback_on=[ModelAPIError, has_no_actionable_output],
    ),
    output_type=str,
)
result = agent.run_sync('What is the capital of France?')
print(result.output)
#> The capital of France is Paris.
```

#### Combining Handlers

You can combine exception types, exception handlers, and response handlers in a single list:

fallback\_on\_mixed.py

```python
from pydantic_ai.exceptions import ModelAPIError
from pydantic_ai.models.fallback import FallbackModel

from fallback_on_native_tool import anthropic_model, google_model, web_fetch_failed

fallback_model = FallbackModel(
    google_model,
    anthropic_model,
    fallback_on=[
        ModelAPIError,  # Exception type
        lambda exc: 'rate limit' in str(exc).lower(),  # Exception handler (untyped lambda)
        web_fetch_failed,  # Response handler (auto-detected via type hint)
    ],
)
```

### Exception Handling in Middleware and Decorators

When using `FallbackModel`, it’s important to understand that [`FallbackExceptionGroup`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.FallbackExceptionGroup) inherits from Python’s [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup). This means that existing exception handling code that catches specific exceptions (like `ModelAPIError`) won’t automatically catch the individual exceptions wrapped inside the group.

For example, if you have middleware or a decorator that catches `ModelAPIError`:

middleware\_without\_fallback.py

```python
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from pydantic_ai import ModelAPIError

T = TypeVar('T')

# This handler will NOT catch ModelAPIError when using FallbackModel!
def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ModelAPIError as e:  # Won't catch FallbackExceptionGroup
            print(f'API error: {e}')
            raise

    return wrapper
```

This decorator will miss `ModelAPIError` exceptions when using `FallbackModel`, because they’re wrapped in a `FallbackExceptionGroup` containing one exception per failed model, in the order the models were tried.

To handle both cases, you can use Python 3.11+ `except*` syntax, which catches matching exceptions from exception groups as well as bare exceptions. Note that `except*` always delivers the caught exceptions as an `ExceptionGroup` (even if the original was a bare exception), so re-raising will propagate an `ExceptionGroup` rather than the original exception type:

middleware\_with\_fallback.py

```python
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from pydantic_ai import ModelAPIError

T = TypeVar('T')

def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except* ModelAPIError as exc_group:
            for exc in exc_group.exceptions:
                print(f'API error: {exc}')
            raise

    return wrapper
```

You can also catch `FallbackExceptionGroup` directly if you want to handle it specifically:

catch\_fallback\_exception\_group.py

```python
from pydantic_ai import Agent, FallbackExceptionGroup
from pydantic_ai.models.fallback import FallbackModel

agent = Agent(FallbackModel('openai:gpt-6-luna', 'anthropic:claude-sonnet-5-5'))

try:
    response = agent.run_sync('What is the capital of France?')
except FallbackExceptionGroup as exc_group:
    print(f'All {len(exc_group.exceptions)} models failed:')
    for exc in exc_group.exceptions:
        print(f'  - {exc}')
```
