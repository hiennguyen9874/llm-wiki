---
title: "Multimodal Input"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/input/"
domain: "pydantic.dev"
language: "en"
description: "Send images, audio, video, PDFs and other documents to a Pydantic AI agent by URL, as binary content, or as files uploaded to a provider's Files API."
word_count: 2163
---

Alongside text, agents can accept image, audio, video, and document input.

## Image Input

If you have a direct URL for the image, you can use [`ImageUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ImageUrl):

image\_input.py

```python
from pydantic_ai import Agent, ImageUrl

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync(
    [
        'What company is this logo from?',
        ImageUrl(url='https://iili.io/3Hs4FMg.png'),
    ]
)
print(result.output)
#> This is the logo for Pydantic, a data validation and settings management library in Python.
```

If you have the image locally, you can also use [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent):

local\_image\_input.py

```python
import httpx

from pydantic_ai import Agent, BinaryContent

image_response = httpx.get('https://iili.io/3Hs4FMg.png')  # Pydantic logo

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync(
    [
        'What company is this logo from?',
        BinaryContent(data=image_response.content, media_type='image/png'),  # (1)
    ]
)
print(result.output)
#> This is the logo for Pydantic, a data validation and settings management library in Python.
```

To ensure the example is runnable we download this image from the web, but you can also use `Path().read_bytes()` to read a local file's contents.

## Audio Input

For audio, use [`AudioUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.AudioUrl) or [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent).

## Video Input

For video, use [`VideoUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.VideoUrl) or [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent).

## Document Input

For documents, use [`DocumentUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.DocumentUrl) or [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent).

If you have a direct URL for the document, you can use [`DocumentUrl`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.DocumentUrl):

document\_input.py

```python
from pydantic_ai import Agent, DocumentUrl

agent = Agent(model='anthropic:claude-sonnet-5-5')
result = agent.run_sync(
    [
        'What is the main content of this document?',
        DocumentUrl(url='https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf'),
    ]
)
print(result.output)
#> This document is the technical report introducing Gemini 1.5, Google's latest large language model...
```

Which document formats are supported varies by model. Pydantic AI sends a document of any media type that Python’s `mimetypes` knows a file extension for, carrying the media type and, where the API wants one, the extension (such as `pdf` or `pptx`), and a model that can’t read a format rejects it. Text-like content such as JSON or XML is inlined as text instead where the API has no file part.

You can also use [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent) to pass document data directly:

binary\_content\_input.py

```python
from pathlib import Path
from pydantic_ai import Agent, BinaryContent

pdf_path = Path('document.pdf')
agent = Agent(model='anthropic:claude-sonnet-5-5')
result = agent.run_sync(
    [
        'What is the main content of this document?',
        BinaryContent(data=pdf_path.read_bytes(), media_type='application/pdf'),
    ]
)
print(result.output)
#> The document discusses...
```

## Text Input

You can use [`TextContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.TextContent) to provide text input with additional metadata:

text\_content\_input.py

```python
from pydantic_ai import Agent, TextContent

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync([
    'Summarize the key points from this text.',
    TextContent(
        content=(
            'Pydantic AI is a Python agent framework. '
            'It supports text, image, audio, video, and document input.'
        ),
        metadata={'source': 'pydantic_ai_inputs.txt'},
    ),
])
```

This is equivalent to passing the text as a `str`, but allows you to include additional `metadata` that can be accessed programmatically in your agent logic.

## Structured Input

Use [`StructuredContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.StructuredContent) to pass a structured value as part of the user prompt, such as the state of the app the user is looking at, or the data a [decision model](https://pydantic.dev/docs/ai/models/decision/#structured-input) should judge. The value stays structured in the message history, so a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history) or an evaluator can read it back, while the model is sent it as text:

structured\_content\_input.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, StructuredContent

class UIState(BaseModel):
    url: str
    cart_total: float

agent = Agent('openai:gpt-6.1-sol')
ui_state = UIState(url='/products/42', cart_total=949.0)
result = agent.run_sync([StructuredContent(ui_state, tag='ui_state'), 'Why did the total jump?'])
```

The model is sent `<ui_state>{"url":"/products/42","cart_total":949.0}</ui_state>`, followed by the question. By default the value is rendered as compact JSON, wrapped in `tag` when one is given, with `<`, `>` and `&` escaped so that a value from an untrusted client, rendered on your server, can’t close the tag. Pass `format='xml'` to render it with [`format_as_xml`](https://pydantic.dev/docs/ai/api/pydantic-ai/format_prompt/#pydantic_ai.format_prompt.format_as_xml) instead, or a function that takes the value and returns the text. A `description` is written on the line before the value. A `tag` is lowercase with `_` between words, and can’t be one of the tags the framework frames its own text in, such as `system` or `tool_result`, so the value can’t read as the framework speaking.

The text is rendered once, when the item is created, and stored in [`content`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.StructuredContent.content) beside the value. A message history that is stored and loaded again is therefore sent exactly as before, which keeps the prompt cache prefix intact, even when the text came from a function that isn’t stored. The text isn’t rendered again when the value changes, so to change the value, create a new item, or use `dataclasses.replace(item, value=..., content='')`, passing `format` again if the item was created with one. After loading, [`value`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.StructuredContent.value) is the JSON-compatible form of the value, such as a dict in place of a Pydantic model.

To render a kind of value the same way wherever it is used, subclass `StructuredContent` and override [`render`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.StructuredContent.render):

structured\_content\_subclass.py

```
from pydantic import BaseModel

from pydantic_ai import StructuredContent, format_as_xml

class UIState(BaseModel):
    url: str
    cart_total: float

class UIStateContent(StructuredContent):
    value: UIState

    def render(self) -> str:
        return format_as_xml(self.value, root_tag='ui_state')

print(UIStateContent(UIState(url='/products/42', cart_total=949.0)).content)
"""
<ui_state>
  <url>/products/42</url>
  <cart_total>949.0</cart_total>
</ui_state>
"""
```

`StructuredContent` is a [`TextContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.TextContent), so code that reads the text of a prompt handles it like any other text. A [decision model](https://pydantic.dev/docs/ai/models/decision/#structured-input) is the exception: it is sent the value itself when the prompt is a single `StructuredContent`. Code that rewrites the text of a prompt, such as a redaction step, should therefore replace the item with a plain `TextContent` holding the new text, as the harness’s [guardrails](https://pydantic.dev/docs/ai/harness/guardrails/) and [compaction](https://pydantic.dev/docs/ai/harness/compaction/) do.

The [Vercel AI](https://pydantic.dev/docs/ai/integrations/ui/vercel-ai/#structured-content) and [AG-UI](https://pydantic.dev/docs/ai/integrations/ui/ag-ui/#structured-content) adapters dump the item as ordinary text in the user message, which a frontend shows like any other user text, and carry its value in the metadata of that text part (Vercel AI) or message (AG-UI, from `ag-ui-protocol` 0.1.11), so it loads back whole. The same goes for an item [enqueued mid-run](https://pydantic.dev/docs/ai/core-concepts/message-history/#injecting-messages-mid-run) with `ctx.enqueue`, which accepts it like any other user content. Like `TextContent.metadata`, its `metadata` doesn’t make the round-trip.

## User-side download vs. direct file URL

When using one of `ImageUrl`, `AudioUrl`, `VideoUrl` or `DocumentUrl`, Pydantic AI will default to sending the URL to the model provider, so the file is downloaded on their side.

Support for file URLs varies depending on type and provider:

| Model | Send URL directly | Download and send bytes | Unsupported |
| --- | --- | --- | --- |
| [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel) | `ImageUrl` | `AudioUrl` (audio models only), `DocumentUrl` | `VideoUrl`. `DocumentUrl` [not supported with `AzureProvider`](https://pydantic.dev/docs/ai/models/azure/#using-azure-with-the-responses-api) or [`AlibabaProvider`](https://pydantic.dev/docs/ai/models/compatible-apis/#alibaba-cloud-model-studio-dashscope) |
| [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) | `ImageUrl`, `AudioUrl`, `DocumentUrl` | — | `VideoUrl` |
| [`AnthropicModel`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl` |
| [`GoogleModel`](https://pydantic.dev/docs/ai/api/models/google/#pydantic_ai.models.google.GoogleModel) (Google Cloud) | All URL types | — | — |
| [`GoogleModel`](https://pydantic.dev/docs/ai/api/models/google/#pydantic_ai.models.google.GoogleModel) (Gemini API) | [YouTube](https://pydantic.dev/docs/ai/models/google/#document-image-audio-and-video-input), [Files API](https://pydantic.dev/docs/ai/models/google/#document-image-audio-and-video-input) | All other URLs | — |
| [`XaiModel`](https://pydantic.dev/docs/ai/api/models/xai/#pydantic_ai.models.xai.XaiModel) | `ImageUrl` | `DocumentUrl` | `AudioUrl`, `VideoUrl` |
| [`MistralModel`](https://pydantic.dev/docs/ai/api/models/mistral/#pydantic_ai.models.mistral.MistralModel) | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl`, `DocumentUrl` (non-PDF, non-text) |
| [`BedrockConverseModel`](https://pydantic.dev/docs/ai/api/models/bedrock/#pydantic_ai.models.bedrock.BedrockConverseModel) | S3 URLs (`s3://`) | `ImageUrl`, `DocumentUrl`, `VideoUrl` (Nova only) | `AudioUrl`, and `VideoUrl` outside Nova |
| [`OpenRouterModel`](https://pydantic.dev/docs/ai/api/models/openrouter/#pydantic_ai.models.openrouter.OpenRouterModel) | `ImageUrl`, `DocumentUrl`, `VideoUrl` | `AudioUrl` | — |

When Pydantic AI downloads files itself, it downloads at most 50 MiB per file and 500 MiB in total for the files of one model request, and raises a `ValueError` past either limit. To send larger files, pass them as [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent), or send the URL to a provider that fetches it itself.

A model that does not accept a kind of file at all can still be given one through the [File Understanding](https://pydantic.dev/docs/ai/capabilities/file-understanding/) capability, which has another model describe it in text first. Without it, a file in a user prompt that the model can’t take fails the request, while one a tool returned is [replaced by a note naming it](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-return-file-provenance), so the run goes on.

A model API may be unable to download a file (e.g., because of crawling or access restrictions) even if it supports file URLs. For example, [`GoogleModel`](https://pydantic.dev/docs/ai/api/models/google/#pydantic_ai.models.google.GoogleModel) on Google Cloud limits YouTube video URLs to one URL per request.

In such cases, you can instruct Pydantic AI to download the file content locally and send that instead of the URL by setting `force_download` on the URL object:

force\_download.py

```
from pydantic_ai import ImageUrl, AudioUrl, VideoUrl, DocumentUrl

ImageUrl(url='https://example.com/image.png', force_download=True)
AudioUrl(url='https://example.com/audio.mp3', force_download=True)
VideoUrl(url='https://example.com/video.mp4', force_download=True)
DocumentUrl(url='https://example.com/doc.pdf', force_download=True)
```

When Pydantic AI downloads a file, it sends the `media_type` you passed if it differs from the one the URL’s extension implies. Otherwise it uses the server’s `Content-Type`, falling back to the URL’s extension when the header is missing or generic (`application/octet-stream` or `binary/octet-stream`). Pass `media_type` explicitly for URLs without an extension, or for servers that report the wrong type:

explicit\_media\_type.py

```
from pydantic_ai import ImageUrl

ImageUrl(url='https://example.com/receipt-123', media_type='image/png', force_download=True)
```

## Uploaded Files

Some model providers have their own file storage APIs where you can upload files and reference them by ID or URL.

Use [`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile) to reference files that have been uploaded to a provider’s file storage API.

### Supported Models

| Model | Support |
| --- | --- |
| [`AnthropicModel`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModel) | ✅ via [Anthropic Files API](https://docs.anthropic.com/en/docs/build-with-claude/files) |
| [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel) | ✅ via [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) |
| [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) | ✅ via [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) |
| [`GoogleModel`](https://pydantic.dev/docs/ai/api/models/google/#pydantic_ai.models.google.GoogleModel) | ✅ via [Google Files API](https://ai.google.dev/gemini-api/docs/files) |
| [`BedrockConverseModel`](https://pydantic.dev/docs/ai/api/models/bedrock/#pydantic_ai.models.bedrock.BedrockConverseModel) | ✅ via S3 URLs (`s3://bucket/key`) |
| [`XaiModel`](https://pydantic.dev/docs/ai/api/models/xai/#pydantic_ai.models.xai.XaiModel) | ✅ via [xAI Files API](https://docs.x.ai/docs/guides/files) |
| Other models | ❌ Not supported |

### Provider Name Requirement

When using [`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile) you must set the `provider_name`. Uploaded files are specific to the system they are uploaded to and are not transferable across providers. Trying to use a message that contains an `UploadedFile` with a different provider will result in an error. Within one provider name, Pydantic AI doesn’t track which endpoint or account a file was uploaded to: send it to a model whose client can read it.

If you want to introduce portability into your agent logic to allow the same prompt history to work with different provider backends, you can use a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history) to remove or rewrite `UploadedFile` parts from messages before sending them to a provider that does not support them. Be aware that stripping out `UploadedFile` instances might confuse the model, especially if references to those files remain in the text.

### Media Type Inference

The `media_type` parameter is optional for [`UploadedFile`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UploadedFile). If not specified, Pydantic AI will attempt to infer it from the `file_id`:

1. If `file_id` is a URL or path with a recognizable file extension (e.g., `.pdf`, `.png`), the media type is inferred automatically
2. For opaque file IDs (e.g., `'file-abc123'`), the media type defaults to `'application/octet-stream'`

### Anthropic

Follow the [Anthropic Files API docs](https://docs.anthropic.com/en/docs/build-with-claude/files) to upload files. You can access the underlying Anthropic client via `provider.client`.

uploaded\_file\_anthropic.py

```
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

async def main():
    provider = AnthropicProvider()
    model = AnthropicModel('claude-sonnet-5-5', provider=provider)

    # Upload a file using the provider's client (Anthropic client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.beta.files.upload(file=f)

    # Reference the uploaded file; the beta header is added automatically
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...

asyncio.run(main())
```

### OpenAI

Follow the [OpenAI Files API docs](https://platform.openai.com/docs/api-reference/files/create) to upload files. You can access the underlying OpenAI client via `provider.client`.

uploaded\_file\_openai.py

```
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

async def main():
    provider = OpenAIProvider()
    model = OpenAIChatModel('gpt-6.1-sol', provider=provider)

    # Upload a file using the provider's client (OpenAI client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.files.create(file=f, purpose='user_data')

    # Reference the uploaded file
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...

asyncio.run(main())
```

### Google

Follow the [Google Files API docs](https://ai.google.dev/gemini-api/docs/files) to upload files. You can access the underlying Google GenAI client via `provider.client`.

uploaded\_file\_google.py

```
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

async def main():
    provider = GoogleProvider()
    model = GoogleModel('gemini-3.8-flash', provider=provider)

    # Upload a file using the provider's client (Google GenAI client)
    with open('document.pdf', 'rb') as f:
        file = await provider.client.aio.files.upload(file=f)
        assert file.uri is not None

    # Reference the uploaded file by URI (media_type is optional for Google)
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=file.uri, media_type=file.mime_type, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...

asyncio.run(main())
```

### Bedrock (S3)

For Bedrock, files must be uploaded to S3 separately (e.g., using [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html)). The assumed role must have `s3:GetObject` permission on the bucket.

uploaded\_file\_bedrock.py

```
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.bedrock import BedrockConverseModel

async def main():
    model = BedrockConverseModel('global.anthropic.claude-sonnet-5-5')

    agent = Agent(model)
    result = await agent.run([
        'Summarize this document',
        UploadedFile(
            file_id='s3://my-bucket/document.pdf',
            provider_name=model.system,  # 'bedrock'
            media_type='application/pdf',  # Optional for .pdf, but recommended
        ),
    ])
    print(result.output)
    #> The document discusses the main topics and key findings...

asyncio.run(main())
```

### xAI

Follow the [xAI Files API docs](https://docs.x.ai/docs/guides/files) to upload files. You can access the underlying xAI client via `provider.client`.

uploaded\_file\_xai.py

```
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.xai import XaiProvider

async def main():
    provider = XaiProvider()
    model = XaiModel('grok-4.7', provider=provider)

    # Upload a file using the provider's client (xAI client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.files.upload(f, filename='document.pdf')

    # Reference the uploaded file
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...

asyncio.run(main())
```
