---
title: "File Understanding"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/capabilities/file-understanding/"
domain: "pydantic.dev"
language: "en"
word_count: 798
---

The [`FileUnderstanding`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.FileUnderstanding) [capability](https://pydantic.dev/docs/ai/capabilities/overview/) lets an agent take images, documents, audio and video its model cannot read. Before each attempt at a request, every such file in a user prompt or a tool result is replaced by a text description of it, written by a model that can read it. The file is judged against the model serving that attempt, so with [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) a candidate that reads the file gets it, and only one that can’t gets the description. The agent’s model sees the description in the file’s place, and files it does accept are sent as they are. Without the capability, a file a tool returned that the model cannot read is [replaced by a note](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance) saying so, and one in a user prompt fails the request.

file\_understanding\_capability.py

```python
from pydantic_ai import Agent, DocumentUrl
from pydantic_ai.capabilities import FileUnderstanding

agent = Agent(
    'typesafe:jev-latest',
    output_type=bool,
    instructions='Is this document about animals?',
    capabilities=[FileUnderstanding(fallback_subagent_model='openai:gpt-6.1-sol')],
)
result = agent.run_sync([DocumentUrl('https://example.com/field-guide.pdf')])
print(result.output)
#> True
```

Which files need describing comes from the model’s [profile](https://pydantic.dev/docs/ai/models/overview/#inspecting-a-models-profile): [`supports_image_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_image_input), [`supports_document_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_document_input), [`supports_audio_file_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_audio_file_input), [`supports_video_input`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_video_input), and the media types each kind is narrowed to, such as [`supported_image_media_types`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supported_image_media_types). Most models accept images and documents, so with them the capability mostly has audio and video described; on [`AnthropicModel`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel), Word and Excel documents too, and on Claude and OpenAI models, an image in a format outside JPEG, PNG, GIF and WebP, such as a HEIC photo. A text-only model like [Jev](https://pydantic.dev/docs/ai/models/typesafe/) has everything described.

A flag is `True` unless an adapter or a model family is known not to take that kind of file, so it is not a check that the model reads it. A text-only model served through an adapter that sends images, such as a text-only Llama behind vLLM, needs its profile to say so, or its images are sent and the provider rejects them:

file\_understanding\_text\_only\_profile.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import FileUnderstanding
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles import ModelProfile
from pydantic_ai.providers.vllm import VLLMProvider

model = OpenAIChatModel(
    'meta-llama/Llama-3.3-70B-Instruct',
    provider=VLLMProvider(base_url='http://localhost:8000/v1'),
    profile=ModelProfile(supports_image_input=False, supports_document_input=False),
)
agent = Agent(model, capabilities=[FileUnderstanding(fallback_subagent_model='openai:gpt-6.1-sol')])
```

`fallback_subagent_model` is the model that writes the descriptions, as a `'provider:model'` name or a [`Model`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model) instance, and it must accept the files itself. `instructions` replaces the default request for a detailed description:

file\_understanding\_instructions.py

```python
from pydantic_ai.capabilities import FileUnderstanding

FileUnderstanding(
    fallback_subagent_model='anthropic:claude-sonnet-5-5',
    instructions='Transcribe the text in this file. Keep headings and tables.',
)
```

The description reaches the model between `-----BEGIN FILE-----` and `-----END FILE-----` lines that name the file, the same way text files are inlined for models that take no attachments. A description is prose, so its block is marked `text/plain` whatever the file was; a text-like document (plain text, CSV, JSON, XML, YAML) needs no describing, is inlined as it is, and keeps its own media type. A provider file reference ([`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile)) is left alone, since only its own provider can read it.

A file is described once per conversation. The description is recorded in the message history, under the framework’s reserved `__pydantic_ai__` namespace in the [`metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.metadata) of the request that holds the file (which is not sent to the model), and every later request uses that text instead of describing the file again. A turn that continues from `message_history`, another worker serving the next turn, and a [durable](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) run replaying its history all read the same description. Earlier requests therefore keep the same content from one request to the next, which keeps the prompt cache valid, and the describer is paid for once. A file given by URL is identified by its URL, and binary content by its bytes and media type. The downloaded text of a text document given by URL is recorded the same way, so it is not downloaded again. A separate conversation describes the file again. The [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) leave that namespace out of the history they send to a client, and [`sanitize_messages`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.sanitize_messages) drops it from [untrusted history](https://pydantic.dev/docs/ai/core-concepts/message-history/#loading-untrusted-history) a client sends back, so in a conversation whose history lives on the client the file is described again each turn, and a new description can differ, which changes earlier requests and costs the cached prefix.

The files a request needs described are described concurrently, each once however often it appears. Describing a file is a model run of its own, but its requests, tokens and cost are added to the agent run’s [usage](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage), and the run’s [usage limits](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) are checked before any describing request is sent, as if those were the run’s next requests: a `request_limit` bounds them together with the agent’s own.

Inside an agent, use [`ModelFallback`](https://pydantic.dev/docs/ai/capabilities/model-fallback/) to fall back between models: each candidate is judged by its own profile. A [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) has no single profile, so the capability leaves its files alone, and each model it tries is sent a note in place of a tool’s file that model can’t read.
