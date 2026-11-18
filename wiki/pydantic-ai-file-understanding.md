---
type: Concept
title: Pydantic AI file understanding
description: Pydantic AI's FileUnderstanding capability — how a model's profile decides which files another model must describe, where that description lives in the history, and what it costs in requests, cached prefix and client-held conversations.
tags: [pydantic-ai, agents, media]
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
  - id: pydantic-file-understanding-docs
    resource: ../raw/capabilities/file-understanding/index.md
    scope: ../raw/capabilities/file-understanding/
    kind: documentation
    revision: sha256:64dbbbca7a40ac5cd589dbf775721ae19ef040e6f3f0b7d065167405caa391d2
    title: "File Understanding"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

`FileUnderstanding` is a core [capability](pydantic-ai-capability-primitive.md) that lets an agent take images, documents, audio and video its model cannot read: before each attempt at a request, every such file in a user prompt or a tool result is replaced by a text description of it, written by a model that can read it[^pydantic-file-understanding-docs] The file is judged against the model serving that attempt, so combining the capability with `ModelFallback` gives the file to a candidate that reads it and the description only to one that cannot. Files the agent's model does accept are sent unchanged. The capability therefore does not widen what a model can read — it substitutes text for what the model would otherwise reject.

Without the capability the two paths already differ: a file a *tool* returned that the model cannot read is replaced by a note naming the file, while a file in a *user prompt* fails the request[^pydantic-file-understanding-docs] The tool half is the same note behaviour recorded on [models and providers](pydantic-ai-models-and-providers.md); the user-prompt half is the failure this capability exists to prevent.

## What counts as unreadable

The decision comes from the model's [profile](pydantic-ai-models-and-providers.md), one flag per input kind plus a media-type narrowing where the model has one[^pydantic-file-understanding-docs]:

| Input kind | Kind flag | Media-type narrowing |
| --- | --- | --- |
| Image | `supports_image_input` | `supported_image_media_types` |
| Document | `supports_document_input` | `supported_document_media_types` |
| Audio file | `supports_audio_file_input` | `supported_audio_media_types` |
| Video | `supports_video_input` | `supported_video_media_types` |

Because most models accept images and documents, the practical effect on them is mostly describing audio and video. The named exceptions are Word and Excel documents on `AnthropicModel`, and — on Claude and OpenAI models — an image outside JPEG, PNG, GIF and WebP, such as a HEIC photo. A text-only model such as Jev has everything described[^pydantic-file-understanding-docs]

Google adds a version-shaped pair of exceptions rather than a provider-wide one: **Gemini 2.5 models** do not read Word or Excel documents while **Gemini 3 models** do, and TIFF is read only on Google Cloud — the Gemini API rejects it. Both differences are the kind this capability turns into a description rather than a failure, and both are profile facts rather than capability settings, so which model the agent is on decides which files get described[^pydantic-google-2026]

A flag is `True` unless an adapter or a model family is known not to take that kind of file, so it is not a claim that the model *reads* it[^pydantic-file-understanding-docs] The failure case is a text-only model served through an adapter that sends images anyway — a text-only Llama behind vLLM — where the images are sent and the provider rejects them. The profile has to be corrected at construction:

```python
model = OpenAIChatModel(
    'meta-llama/Llama-3.3-70B-Instruct',
    provider=VLLMProvider(base_url='http://localhost:8000/v1'),
    profile=ModelProfile(supports_image_input=False, supports_document_input=False),
)
agent = Agent(model, capabilities=[FileUnderstanding(fallback_subagent_model='openai:gpt-6.1-sol')])
```

That is the same profile-override mechanism documented for `ModelProfile` generally: the capability trusts the profile, so a wrong profile silently disables describing rather than raising.

## Wiring and the describer prompt

```python
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

`fallback_subagent_model` names the model that writes the descriptions, as a `'provider:model'` string or a `Model` instance, and it must itself accept the files it is given[^pydantic-file-understanding-docs] The name is `fallback_subagent_model` — the same field name the [image generation](pydantic-ai-image-generation.md) capability uses for a different job (a subagent that draws), so the two capabilities share a keyword without sharing semantics. `instructions` replaces the default request for a detailed description, which is what makes the describer task-shaped rather than generic:

```python
FileUnderstanding(
    fallback_subagent_model='anthropic:claude-sonnet-5-5',
    instructions='Transcribe the text in this file. Keep headings and tables.',
)
```

The source gives no schema for the default instructions, no cap on file size, and no statement of what happens when the describer model fails or refuses[^pydantic-file-understanding-docs] Treat the describer as a second model contract to configure and monitor, not as a guaranteed fallback.

## Where the description lands

The description reaches the model between `-----BEGIN FILE-----` and `-----END FILE-----` lines that name the file — the same inline form used for text files sent to models that take no attachments. Each case is handled differently[^pydantic-file-understanding-docs]:

| Input | What the model receives |
| --- | --- |
| Image, audio, video, or a document the model cannot read | The description, inside `-----BEGIN FILE-----` … `-----END FILE-----`, marked `text/plain` whatever the file was |
| Text-like document (plain text, CSV, JSON, XML, YAML) | The text itself, inlined unchanged with its own media type — no describer call |
| Provider file reference (`UploadedFile`) | Left alone, because only its own provider can read it |

The media-type consequence is worth stating plainly: a described PDF, image or audio clip is prose to the model, so anything the describer omitted is unavailable downstream no matter how the agent later reasons about it.

## Described once per conversation

A file is described once per conversation. The description is recorded in the message history under the framework's reserved `__pydantic_ai__` namespace, inside the [`metadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelRequest.metadata) of the request that holds the file; that metadata is not sent to the model. Every later request reuses the recorded text instead of describing the file again[^pydantic-file-understanding-docs]

| Situation | Effect |
| --- | --- |
| Continuing from `message_history` | Same description |
| Another worker serving the next turn | Same description |
| A [durable](pydantic-ai-durable-execution.md) run replaying its history | Same description |
| A separate conversation | Described again |
| History held on the client and sent back | Described again each turn, possibly differently |

The payoff is stated as two things: earlier requests keep the same content from one request to the next, which keeps the [prompt cache](pydantic-ai-prompt-caching.md) valid, and the describer is paid for once[^pydantic-file-understanding-docs] Identity for that lookup is the URL for a file given by URL, and the bytes plus media type for binary content; the downloaded text of a text document given by URL is recorded the same way, so it is not downloaded again[^pydantic-file-understanding-docs]

The client-held case is the hole in that guarantee. The [UI adapters](https://pydantic.dev/docs/ai/integrations/ui/overview/) leave the `__pydantic_ai__` namespace out of the history they send to a client, and `sanitize_messages` drops it from untrusted history a client sends back — so in a conversation whose history lives on the client, the file is described again every turn, a new description can differ, and each difference invalidates the cached prefix[^pydantic-file-understanding-docs] This is the practical argument for keeping server-side history (or [Conversation state](pydantic-ai-conversation-state.md), which persists that history) when prompts carry files.

## Cost and limit accounting

Describing is a model run of its own, so it has its own requests — but its requests, tokens and cost are added to the agent run's `RunUsage`, and the run's `UsageLimits` are checked before any describing request is sent, as if those were the run's next requests[^pydantic-file-understanding-docs] A `request_limit` therefore bounds describing and the agent's own requests together. Files that need describing in one request are described concurrently, each once however often it appears[^pydantic-file-understanding-docs]

Consequences a build has to plan for[^pydantic-file-understanding-docs]:

- A run whose prompt holds several unreadable files spends requests before its first real request, so a `request_limit` sized for the agent's own turns can be exhausted by describing alone.
- Token and cost accounting is honest — a run that described files reports the describer's spend — but it is not separable in the usage object, and the source says nothing about a distinct span or attribute that would mark the describing calls in [traces](pydantic-ai-observability.md).

## With model fallback

Inside an agent, `ModelFallback` is the intended way to move between models, because each candidate is judged by its own profile: a candidate that reads the file gets it, and only one that cannot gets the description[^pydantic-file-understanding-docs] A `FallbackModel` wrapper is the case that does not work — it has no single profile, so the capability leaves its files alone, and each model it tries receives a note in place of a tool's file that model cannot read[^pydantic-file-understanding-docs] That splits the two [fallback mechanisms](pydantic-ai-model-fallback.md) on file handling, not just on failure triggers.

## Limits

- The source is a single vendor reference page: 798 words as declared, 809 by local `wc -w`, no publication date, no author, and **no Pydantic AI version**, so every API name here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-file-understanding-docs]
- Nothing was executed: no package installed, no agent run, no describer call, no cache hit or miss measured, no trace opened. Every behavioural claim is **Reported**[^pydantic-file-understanding-docs]
- The tool-returned-note half is also recorded on [models and providers](pydantic-ai-models-and-providers.md) from the same publisher's documentation set, which repeats the claim rather than independently verifying it.
- Unstated by the source: how a describer failure or refusal surfaces, whether the describer itself is retried, any file-size or token ceiling, the default description prompt, whether describing appears as its own span, the added latency, and which models are valid describers beyond the one example.
- The example's models (`typesafe:jev-latest`, `openai:gpt-6.1-sol`, `anthropic:claude-sonnet-5-5`) are unpinned aliases, so the pairing of a text-only primary with a reading describer is illustrative rather than a tested configuration.

## Relationships

- **Is a** core `pydantic-ai` [capability](pydantic-ai-capability-primitive.md), reached through `pydantic_ai.capabilities`.
- **Depends on** [models and providers](pydantic-ai-models-and-providers.md) for the profile flags and media-type sets that decide what needs describing.
- **Complements** [model fallback](pydantic-ai-model-fallback.md): `ModelFallback` is per-candidate and file-aware, while `FallbackModel` forces the note path.
- **Protects** [prompt caching](pydantic-ai-prompt-caching.md) by keeping the description byte-stable across requests — and loses that protection when history is regenerated from a client.
- **Travels with** [conversation state](pydantic-ai-conversation-state.md): the recorded description is part of the message history that state persists.
- **Receives files through** [multimodal input](pydantic-ai-multimodal-input.md), which catalogues the URL, byte and uploaded-file parts a prompt can carry and the per-model download rules behind them.
- **Is the alternative to the note path described in** [Pydantic AI tool results and returned files](pydantic-ai-tool-results.md): a tool-returned file the model cannot read is replaced in the request by `File <id> (<media type>, <bytes>) was not sent: this model cannot read …` unless this capability describes it instead, while a file in a user prompt or in `ToolReturn.content` is sent as-is and fails the request rather than being noted or described[^pydantic-docs-tools-advanced].
- **Accounts into** the run's usage, which [run controls](pydantic-ai-run-controls.md) bound through `usage_limits`.
- **Gains Google's version-shaped exceptions from** [Google models in Pydantic AI](google-models-in-pydantic-ai.md): Word and Excel are unreadable on Gemini 2.5 and readable on Gemini 3, and TIFF is unreadable on the Gemini API but readable on Google Cloud[^pydantic-google-2026]

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Document, Image, Audio, and Video Input" (raw lines 200–247) for the image formats Gemini reads, TIFF being read only on Google Cloud and rejected by the Gemini API, Gemini 2.5 not reading Word or Excel while Gemini 3 does, and a tool-returned file of another type being sent as a note naming it. Evidence class: **Reported** — vendor documentation; no file was sent or described.

[^pydantic-file-understanding-docs]: Pydantic Docs, "File Understanding", <https://pydantic.dev/docs/ai/capabilities/file-understanding/>; local capture `raw/capabilities/file-understanding/index.md`, content digest sha256:64dbbbca, 798 words as declared (809 by `wc -w`), no publication date, author or framework version. Lines 10–11 for the capability's definition, per-attempt judging, `ModelFallback` interaction, and the without-the-capability note-versus-failure split; lines 14–27 for the `file_understanding_capability.py` example; line 29 for the five profile flags and their media-type sets, plus the Word/Excel, exotic-image and Jev cases; line 31 for the "`True` unless known not to take it" rule and lines 35–48 for the vLLM text-only profile override; line 50 for `fallback_subagent_model` and its must-accept-the-files rule; lines 54–61 for the `instructions` example; line 63 for the `-----BEGIN FILE-----`/`-----END FILE-----` framing, the `text/plain` marking, the text-like-document pass-through and the untouched `UploadedFile`; line 65 for once-per-conversation recording, the `__pydantic_ai__` namespace in `ModelRequest.metadata`, the three replay paths, the URL/bytes identity, the prompt-cache argument, and the UI-adapter and `sanitize_messages` caveat; line 67 for concurrent describing, `RunUsage` attribution and `UsageLimits`; line 69 for `ModelFallback` versus `FallbackModel`. Evidence class: **Reported** — vendor documentation with no execution behind it.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Where a returned file is sent" (raw lines 70–99) for the three routes a tool-returned file takes, the `File <id> (<media type>, <bytes>) was not sent: this model cannot read …` note, the File Understanding alternative, and the deliberate failures for a file in a user prompt or in `ToolReturn.content`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
