---
type: Concept
title: Pydantic AI multimodal input
description: How a Pydantic AI prompt carries images, audio, video and documents — URL objects versus BinaryContent, the per-model URL-versus-download matrix with its 50 MiB caps, force_download and media-type resolution, and UploadedFile references to provider file stores.
tags: [pydantic-ai, agents, input, multimodal]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T10:58:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-input-docs
    resource: ../raw/core-concepts/input/index.md
    scope: ../raw/core-concepts/input/
    kind: documentation
    revision: sha256:8d3034fd3ee8f26e5c8a864f5afe7a7fecaea79d4470362b67d35fd0aa0e2196
    title: "Multimodal Input"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

**Reported, Pydantic AI version unspecified:** a prompt is a list that mixes plain strings with typed content parts, and the file-shaped parts come in two forms — a URL object (`ImageUrl`, `AudioUrl`, `VideoUrl`, `DocumentUrl`) that is passed to the provider by default, or `BinaryContent` carrying bytes and a media type[^pydantic-input-docs] Which form actually works, and whether Pydantic AI or the provider fetches the bytes, depends on the model class and the file kind, and that per-model split is the operationally important part of this page. A provider that stores files itself is reached with a third form, `UploadedFile`, which references an id rather than a URL or bytes. Text keeps two wrappers of its own — `TextContent` for text plus metadata, and [structured content](pydantic-ai-structured-content.md) for a typed value — and everything else here is about files.

## The content-part taxonomy

| What the prompt needs | Part | What it holds |
| --- | --- | --- |
| Image by URL | `ImageUrl` | URL, optional `media_type`, `force_download` |
| Audio by URL | `AudioUrl` | same |
| Video by URL | `VideoUrl` | same |
| Document by URL | `DocumentUrl` | same |
| Any file as bytes | `BinaryContent` | `data` plus an explicit `media_type` |
| Text plus metadata | `TextContent` | `content` and a `metadata` mapping |
| Typed value | `StructuredContent` | value rendered to text, kept structured in history |
| Provider-hosted file | `UploadedFile` | `file_id`, `provider_name`, optional `media_type` |

The image, audio and video pages of the source are one or two lines each: use the URL type, or `BinaryContent` when the file is local[^pydantic-input-docs] The image example reads a file with `Path().read_bytes()` into `BinaryContent(data=..., media_type='image/png')`; the audio and video sections add no example of their own.

`TextContent` is equivalent to passing a `str`, except that its `metadata` can be read programmatically in agent logic[^pydantic-input-docs] It is the base class of [structured content](pydantic-ai-structured-content.md), so anything that reads prompt text sees a structured item as text as well.

## Documents and media types

A document's accepted format is the model's decision, not the framework's: Pydantic AI sends any media type that Python's `mimetypes` knows a file extension for, carrying the media type and, where the API wants one, the extension (`pdf`, `pptx`), and a model that cannot read that format rejects it[^pydantic-input-docs] Text-like content such as JSON or XML is inlined as text instead, where the API has no file part for it. The docs' binary example passes `BinaryContent(data=pdf_path.read_bytes(), media_type='application/pdf')` for a PDF.

## URL or bytes: the per-model matrix

With one of the four URL types, Pydantic AI's default is to send the URL to the model provider, so the file is downloaded on the provider's side[^pydantic-input-docs] Support is not uniform — the same URL type can be accepted directly by one model class and require a local download by another:

| Model | Sent as URL directly | Downloaded and sent as bytes | Unsupported |
| --- | --- | --- | --- |
| `OpenAIChatModel` | `ImageUrl` | `AudioUrl` (audio models only), `DocumentUrl` | `VideoUrl`; `DocumentUrl` with `AzureProvider` or `AlibabaProvider` |
| `OpenAIResponsesModel` | `ImageUrl`, `AudioUrl`, `DocumentUrl` | — | `VideoUrl` |
| `AnthropicModel` | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl` |
| `GoogleModel` (Google Cloud) | all URL types | — | — |
| `GoogleModel` (Gemini API) | YouTube and Files API URLs | all other URLs | — |
| `XaiModel` | `ImageUrl` | `DocumentUrl` | `AudioUrl`, `VideoUrl` |
| `MistralModel` | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl`, `DocumentUrl` (non-PDF, non-text) |
| `BedrockConverseModel` | S3 URLs (`s3://`) | `ImageUrl`, `DocumentUrl`, `VideoUrl` (Nova only) | `AudioUrl`; `VideoUrl` outside Nova |
| `OpenRouterModel` | `ImageUrl`, `DocumentUrl`, `VideoUrl` | `AudioUrl` | — |

Three readings of the table matter when choosing an input form[^pydantic-input-docs]: a URL type in the "unsupported" column fails rather than silently downloading, "downloaded" only happens because the model class does not take that URL directly, and the matrix is per model *class*, so a provider reached through a compatible-API adapter inherits the adapter's row rather than the service's own capabilities.

The matrix's nine rows cover eight model classes (Google appears twice), not the whole [provider directory](pydantic-ai-models-and-providers.md), so an unlisted model class's row is simply absent from the source rather than known to support nothing.

### What the Google capture adds

The Google setup page fills in the two Google rows from the provider side[^pydantic-google-2026]:

- Gemini reads JPEG, PNG, GIF, WebP, HEIC, HEIF, AVIF and BMP; **TIFF is read only on Google Cloud**, and the Gemini API rejects it.
- Word and Excel documents are read by Gemini 3 models and not by Gemini 2.5 models — the same shape of gap [file understanding](pydantic-ai-file-understanding.md) records for Claude.
- A file of another type that a *tool* returns is sent as a note naming it rather than as the file, which is the general tool-return rule above.
- A YouTube `VideoUrl` is sent as Gemini's direct YouTube input, so Pydantic AI neither downloads nor uploads the video.
- An image's resolution can be set per part with `vendor_metadata={'media_resolution': {'level': …}}`; `GoogleModel` reads it, and a lower level costs fewer input tokens. [Google decision models](google-decisions-model.md) sets the same per-part field.

The provider rules that configure all of this — the two transports, the 50 MiB download cap, `force_download` and `UploadedFile` — are in [Google models in Pydantic AI](google-models-in-pydantic-ai.md)[^pydantic-google-2026]

## Download caps and `force_download`

When Pydantic AI downloads files itself, it takes at most **50 MiB per file** and **500 MiB in total for the files of one model request**, and raises a `ValueError` past either limit[^pydantic-input-docs] The documented escapes are to pass the file as `BinaryContent` or to send the URL to a provider that fetches it itself — which is the default, so the cap only constrains the download path.

A provider that supports file URLs may still fail to fetch one, for crawling or access restrictions; the docs' example is `GoogleModel` on Google Cloud limiting YouTube video URLs to one per request[^pydantic-input-docs] Setting `force_download=True` on the URL object switches that file to the local-download path:

```python
from pydantic_ai import ImageUrl, AudioUrl, VideoUrl, DocumentUrl

ImageUrl(url='https://example.com/image.png', force_download=True)
AudioUrl(url='https://example.com/audio.mp3', force_download=True)
VideoUrl(url='https://example.com/video.mp4', force_download=True)
DocumentUrl(url='https://example.com/doc.pdf', force_download=True)
```

On the download path the sent media type is resolved in a fixed order[^pydantic-input-docs]: the `media_type` you passed wins if it differs from the one the URL's extension implies; otherwise the server's `Content-Type` is used; and when that header is missing or generic (`application/octet-stream`, `binary/octet-stream`), the URL's extension decides. Pass `media_type` explicitly for URLs without an extension or for servers that report the wrong type — `ImageUrl(url='https://example.com/receipt-123', media_type='image/png', force_download=True)`.

## Files the model cannot read

Without help, the two paths diverge: a file in a *user prompt* that the model cannot take fails the request, while a file a *tool* returned is replaced by a note naming it, so the run continues[^pydantic-input-docs] The [FileUnderstanding capability](pydantic-ai-file-understanding.md) is the documented way to keep either path alive, having another model describe the file in text first.

## Processing video on demand

Without `media_processing`, Gemini uses its default **static** processing of a video[^pydantic-google-2026] Setting `vendor_metadata={'media_processing': 'AGENTIC'}` on a `VideoUrl` lets Gemini inspect relevant video segments on demand instead, on the models Google documents for agentic video understanding[^pydantic-google-2026]

Which to choose is a workload decision, in the source's own terms: static for short clips, whole-video summaries, latency-sensitive queries and frame-level precision across the clip; agentic for long videos or for retrieving specific moments or topics[^pydantic-google-2026]

Source and processing mode are independent — a YouTube `VideoUrl` still uses direct YouTube input, with no download or upload, even when agentic processing is on, and Google lists YouTube URLs among the supported agentic sources[^pydantic-google-2026] Where the steps land differs by transport: on the Gemini Developer API each processing step appears in the response as a `NativeToolCallPart` and `NativeToolReturnPart` named `media_processing`, while **Vertex AI returns signature-only parts**, so those steps never appear in the message history[^pydantic-google-2026] An agent that inspects history for those parts therefore works on one transport and silently sees nothing on the other.

## Uploaded files

`UploadedFile` references a file that already sits in a provider's own file store, by id or URL, instead of sending URL or bytes[^pydantic-input-docs]

### Which models accept one

| Model | File store |
| --- | --- |
| `AnthropicModel` | Anthropic Files API |
| `OpenAIChatModel`, `OpenAIResponsesModel` | OpenAI Files API |
| `GoogleModel` | Google Files API |
| `BedrockConverseModel` | S3 URLs (`s3://bucket/key`) |
| `XaiModel` | xAI Files API |
| every other model | not supported |

### `provider_name` is part of the identity

`provider_name` is required, and the file is not transferable: uploading to one provider and sending the message to another raises an error[^pydantic-input-docs] Within a single provider name, Pydantic AI does not track which endpoint or account holds the file, so it is the caller's job to send it to a model whose client can read it. The examples pass `provider_name=model.system`, which is how they derive the name from the model instance. For a history that must move between backends, the documented tactic is a history processor that removes or rewrites `UploadedFile` parts before a provider that cannot take them — the [Conversation state](pydantic-ai-conversation-state.md) page covers the persisted history such a processor edits — with the warning that stripping a file the surrounding text still refers to can confuse the model.

`media_type` is optional and inferred from `file_id`[^pydantic-input-docs]: a URL or path with a recognizable extension (`.pdf`, `.png`) yields that type, while an opaque id such as `'file-abc123'` falls back to `'application/octet-stream'`.

### Per-provider upload flows

Each supported provider is reached through the Pydantic AI provider object's underlying client, so the upload itself is the vendor SDK's call[^pydantic-input-docs]

| Provider | Upload call | Reference sent |
| --- | --- | --- |
| Anthropic | `provider.client.beta.files.upload(file=f)` — beta header added automatically | `UploadedFile(file_id=uploaded_file.id, provider_name=model.system)` |
| OpenAI | `provider.client.files.create(file=f, purpose='user_data')` | `UploadedFile(file_id=uploaded_file.id, provider_name=model.system)` |
| Google | `provider.client.aio.files.upload(file=f)`, then `file.uri` | `UploadedFile(file_id=file.uri, media_type=file.mime_type, provider_name=model.system)` |
| Bedrock | upload to S3 separately, e.g. with boto3; the assumed role needs `s3:GetObject` | `UploadedFile(file_id='s3://my-bucket/document.pdf', media_type='application/pdf', provider_name=model.system)` |
| xAI | `provider.client.files.upload(f, filename='document.pdf')` | `UploadedFile(file_id=uploaded_file.id, provider_name=model.system)` |

The docs' Bedrock note calls `media_type` optional for a `.pdf` but recommended, and comments `provider_name=model.system  # 'bedrock'`. The upload cells are the vendor clients' APIs as printed in the examples, not Pydantic AI methods.

## Limits

- Single vendor reference page: 2,163 words as declared, 2,282 by local `wc -w` including frontmatter and markup, no publication date, no author, and **no Pydantic AI version**, so every API name is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-input-docs]
- Nothing was executed: no package installed, no URL fetched, no file downloaded or uploaded, no provider called. Every claim is **Reported**[^pydantic-input-docs]
- The URL-versus-download matrix is the source's own claim, with no test or trace behind it; its rows key to model classes, so a model named in the examples (`gpt-6.1-sol`, `claude-sonnet-5-5`, `gemini-3.8-flash`, `grok-4.7`, `global.anthropic.claude-sonnet-5-5`) appears nowhere else in this wiki and is illustrative rather than corroborated.
- Unstated by the source: per-provider file-size limits for `UploadedFile`, whether `UploadedFile` survives history serialization the way [structured content](pydantic-ai-structured-content.md) does, how an unsupported URL type surfaces (error versus retry), the timeout for the download path, and any caching or deduplication of repeated downloads.
- The source's audio and video sections are one sentence each; nothing is said about codecs, container formats, sample rates or duration limits.

## Relationships

- **Depends on** [models and providers](pydantic-ai-models-and-providers.md): the model class decides which URL types are sent directly and which are downloaded, and the provider object exposes the client used for uploads.
- **Complements** [file understanding](pydantic-ai-file-understanding.md), which keeps a run alive when the model cannot read a file that this page's parts deliver.
- **Uses** [history processors](pydantic-ai-conversation-state.md) to make an `UploadedFile` history portable between providers.
- **Feeds** [image generation operations](pydantic-ai-image-generation-operations.md), where `BinaryContent`, `ImageUrl` and `UploadedFile` are the accepted reference inputs with their own per-provider constraints.
- **Ends up on the user channel when returned from a tool**, as [Pydantic AI tool results and returned files](pydantic-ai-tool-results.md) records: the same URL and byte parts this page delivers in a prompt are routed by model and media type out of a tool result, framed as `<pyai:tool_result>` content when demoted, or replaced by a note the model can read[^pydantic-docs-tools-advanced].
- **Pairs with** [structured content](pydantic-ai-structured-content.md): the same prompt list holds file parts and typed-value parts.
- **Is detailed by** [Google models in Pydantic AI](google-models-in-pydantic-ai.md) for the Google rows of the URL matrix and by [Google decision models](google-decisions-model.md) for the per-part media resolution this page's Google input follows.[^pydantic-google-2026]

[^pydantic-input-docs]: Pydantic Docs, "Multimodal Input", <https://pydantic.dev/docs/ai/core-concepts/input/>; local capture `raw/core-concepts/input/index.md`, content digest sha256:8d3034fd, 2,163 words as declared (2,282 by `wc -w` including frontmatter and markup), no publication date, author or framework version. Lines 11 for the input kinds; 13–55 for `ImageUrl` and the `BinaryContent` image example; 57–63 for audio and video; 65–107 for `DocumentUrl`, the `mimetypes`/extension rule and the inlining of text-like documents; 109–131 for `TextContent` and its `metadata`; 189–203 for the default URL pass-through and the nine-row model matrix; 205 for the 50 MiB/500 MiB caps, the `ValueError` and the escapes; 207 for the file-understanding alternative and the user-prompt-fails versus tool-note split; 209–234 for provider download failures, `force_download` and the media-type resolution order; 236–252 for `UploadedFile` and its supported-model table; 254–258 for the required `provider_name`, the non-transferability error and the history-processor tactic; 260–265 for media-type inference; 267–431 for the five per-provider upload examples. Evidence class: **Reported** — vendor documentation with no execution behind it.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Document, Image, Audio, and Video Input" (raw lines 200–247) for the image formats with TIFF on Google Cloud only, Word/Excel by Gemini 3, the tool-returned-file note, the direct YouTube `VideoUrl` and the Files API `DocumentUrl`; §"Agentic video processing" (249–276) for static as the default, the Google recommendations for each mode, `vendor_metadata={'media_processing': 'AGENTIC'}`, the independence of source and mode with direct YouTube input, the `media_processing` `NativeToolCallPart`/`NativeToolReturnPart` on the Gemini Developer API and the signature-only Vertex parts; §"Decisions API" (529–568) for `vendor_metadata={'media_resolution': {'level': …}}` being read by `GoogleModel` and costing fewer input tokens. Evidence class: **Reported** — vendor documentation; no video, image or file was sent.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Where a returned file is sent" (raw lines 70–99) for the tool-returned route of the same `ImageUrl`, `DocumentUrl` and `BinaryContent` parts, the `<pyai:tool_result …>` framing on the user channel, the note that replaces an unreadable file, and the request-only rule that leaves the file on the `ToolReturnPart`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
