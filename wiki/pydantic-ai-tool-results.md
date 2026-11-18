---
type: Concept
title: Pydantic AI tool results and returned files
description: What a tool's return value does on its way to the model — JSON and media returns, the three routes a returned file takes by model and media type, the framing that marks provenance, the note that replaces a file the model cannot read, and the ToolReturn fields that separate the result from extra content and metadata.
tags: [pydantic-ai, agents, tools, media]
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
---

**Reported, Pydantic AI version unspecified:** a tool may return anything Pydantic can serialize to JSON, and media returns are routed by the model *and* the media type rather than by the return annotation — the same `ImageUrl` ends up inside the tool result on one model, on the user channel with provenance framing on another, and as a note in its place on a third[^pydantic-docs-tools-advanced] Two rules make that routing safe to reason about: everything the routing adds is request-only and never stored, so replaying the same history against a different model produces a different request from identical history; and `ToolReturn` is the escape hatch that separates the value your code wants from the content the model sees[^pydantic-docs-tools-advanced]

## What a tool may return

A tool returns any JSON-serializable value — a `datetime`, a Pydantic model, an `ImageUrl`, a `DocumentUrl` — and Pydantic AI serializes it into the tool result[^pydantic-docs-tools-advanced] The documented sample prints four runs of one agent: a `datetime` answered as text, a `User` model answered field by field, a logo URL the model describes, and a PDF URL whose single line of text it reads back[^pydantic-docs-tools-advanced]

Two serialization details are worth keeping:

- Some models accept semi-structured values natively while others expect text and still extract meaning from JSON; when a Python object is returned to a text-expecting model the value is serialized to JSON[^pydantic-docs-tools-advanced]
- A value whose JSON form is a string — `datetime`, `UUID`, `Decimal` — is sent as that string *without* JSON quotes, which is exactly what it reloads as after the history is stored and loaded, so the model reads the same text either way[^pydantic-docs-tools-advanced]

Returning media is where the model stops being irrelevant to the return type. The page's own sample returns `ImageUrl` and `DocumentUrl` straight from `@agent.tool_plain` functions on an OpenAI Responses model, and both arrive inside the tool result because that model and those media types allow it[^pydantic-docs-tools-advanced]

## Where a returned file is sent

There are three routes, and the selection is per file, not per tool[^pydantic-docs-tools-advanced]:

| Route | Reached by | Mechanics |
| --- | --- | --- |
| Inside the tool result | Anthropic and OpenAI Responses for images and documents; Gemini 3 for the types in `GoogleModelProfile.google_supported_mime_types_in_tool_returns`; Bedrock for the media kinds a model family supports | The file travels in the tool result as the model's API expects |
| On the user channel | OpenAI Chat Completions, Groq, Mistral, xAI, Hugging Face and Gemini 2.5 and earlier accept text only in a tool result; Gemini 3 and Bedrock fall back here for a media type they cannot carry | The file is sent the way a user upload arrives, framed with the call that produced it |
| As a note in its place | The model cannot read that kind of file, or that media type, as its profile's file-input flags report | The file is replaced by a sentence naming it and the run continues |

The note route is the widest in practice, and the page enumerates it: an image outside JPEG, PNG, GIF and WebP on Claude and OpenAI models (HEIC, for instance); a GIF on xAI; audio other than WAV and MP3 on OpenAI Chat Completions; documents other than text on Chat Completions providers without file input such as Azure and vLLM; audio and video on Anthropic, OpenAI Responses, Mistral and xAI; video on OpenAI Chat Completions; audio on OpenAI models without `audio` in the model name; audio on Bedrock and video on Bedrock outside Nova; anything but images on Groq and Hugging Face; any file on Cohere; and documents other than PDF and plain text on Anthropic, or other than PDF and text formats on Mistral[^pydantic-docs-tools-advanced]

### Framing on the user channel

A file demoted to the user channel must not read as something the person attached, so the request wraps it with the call it came from[^pydantic-docs-tools-advanced]:

```
<pyai:tool_result tool_name="get_photo" tool_call_id="call_9cQx" file_id="d9a13f">
[the image]
</pyai:tool_result>
```

The tool result itself carries `See file d9a13f.` in place of the file, and each file gets its own tags, so several tools returning media in one step still map file to call[^pydantic-docs-tools-advanced] A failed Gemini tool return is the one exception: its result is Gemini's native `error` string, which takes no file references, so the tags alone carry attribution[^pydantic-docs-tools-advanced] Realtime sessions frame tool-produced files the same way[^pydantic-docs-tools-advanced]

The design point is that this mirrors how a mid-conversation `SystemPromptPart` is framed as `<system>...</system>` for a model whose API has no place to put one — and, like that framing, it is prompt text, so it tells the model where content came from rather than proving it[^pydantic-docs-tools-advanced] Provenance-as-text is the same trust boundary [client-supplied history](pydantic-ai-client-supplied-history.md) records[^pydantic-docs-tools-advanced]

The framing is applied while the request is built and is never stored: the file stays on the `ToolReturnPart` in your history, so the same history replayed against a model that takes files natively puts them in the tool result with no framing at all[^pydantic-docs-tools-advanced]

### The note that replaces an unreadable file

Sending a file the model cannot read would fail the whole request, which is out of proportion for something the model asked a tool for, so the file becomes a sentence[^pydantic-docs-tools-advanced]:

```
File d9a13f (audio/mpeg, 48,213 bytes) was not sent: this model cannot read audio files.
```

The model can then tell the user, or try another tool[^pydantic-docs-tools-advanced] Like the framing, the note lives only in the request: the file stays on the `ToolReturnPart`, and each model a `FallbackModel` tries decides for itself, so a candidate that can read the file is sent it[^pydantic-docs-tools-advanced] The [File Understanding](pydantic-ai-file-understanding.md) capability is the alternative that keeps the file's meaning rather than replacing it — a model that can read the file describes it in text instead[^pydantic-docs-tools-advanced]

Two cases deliberately fail rather than degrade: a file in a user prompt, and a file inside `ToolReturn.content`. Both are sent as they are, and a model that cannot take them still fails the request, because you or your user chose to send it[^pydantic-docs-tools-advanced]

## ToolReturn

`ToolReturn` exists for the cases where one value is not enough[^pydantic-docs-tools-advanced] Its four fields split four jobs:

| Field | Reaches the model? | Purpose |
| --- | --- | --- |
| `return_value` | Yes, as the tool's result | The actual result, serialized; may carry multimodal content directly |
| `tools` | Yes, as an availability record | Names of `defer_loading=True` tools this call revealed |
| `content` | Yes, as a **separate user message** after the tool result | Extra content you want outside the tool result |
| `metadata` | No | For your application: logging, debugging, further processing (other frameworks call this "artifacts") |

The sample is a computer-automation tool that clicks and returns before/after screenshots: the model receives both images plus the labels `Before:` and `After:` as its own user-channel content, while the application reads `return_value` and the coordinates in `metadata`[^pydantic-docs-tools-advanced]

Two behaviours are easy to miss[^pydantic-docs-tools-advanced]:

- `content` is sent as written. It is you adding user content deliberately, so it is *not* framed the way a file the model's API could not take is framed — and, by the same rule, a file there is not replaced by a note.
- `tools` is recorded as a `ToolAvailabilityDeltaPart` immediately after this call's `ToolReturnPart` in the same `ModelRequest`. The revealed names persist when history is resumed, but the definitions themselves still come from the agent at run time.

For media that should sit in the tool result natively, the documented advice is to return it from the function or put it in `return_value` — not in `content`[^pydantic-docs-tools-advanced]

## Contradictions

- **Whether a `FallbackModel` lets a capable candidate read a tool-returned file.** This capture says the note is per-model and each attempt decides for itself, "so one that can read the file is sent it"[^pydantic-docs-tools-advanced] [Model fallback](pydantic-ai-model-fallback.md) records the opposite emphasis — that a `FallbackModel` has no single profile, leaves files alone, and so "each model receives a note in its place", resting on the [File Understanding](pydantic-ai-file-understanding.md) capture, whose relationships section says `FallbackModel` "forces the note path". Neither is chosen here. The two could be reconciled if the note rule follows each candidate's own profile (this capture's reading) and the other captures describe only the case where no candidate can read the file, but no source states that reconciliation.

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, default and error text here is version-unknown, and its samples pin model names (`openai:gpt-6.1-sol`, `google:gemini-3.8-flash`, `anthropic:claude-sonnet-5-5`) that no other capture in this wiki corroborates. Every external link — the `ToolReturn`, `ToolReturnPart`, `SystemPromptPart`, `ToolAvailabilityDeltaPart`, `BinaryContent`, `ImageUrl`, `DocumentUrl`, `FallbackModel` and `Agent` API pages, the input, message-history, file-understanding, output, models-overview and tool pages, and the Logfire traces — was read as a link, not followed. Nothing was installed, no tool registered or called, no media returned, no request built and no history replayed, so every claim is **Reported** and none is **Observed** or **Reproduced**; the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because the routing matrix, the framing syntax and the `ToolReturn` fields are release-sensitive.

## Relationships

- **Follows** [Pydantic AI function tools](pydantic-ai-function-tools.md): that page owns how a function becomes a tool and what its schema says; this one starts where the function returns.
- **Pairs with** [Pydantic AI multimodal input](pydantic-ai-multimodal-input.md): the same `BinaryContent`, `ImageUrl` and `DocumentUrl` parts arrive from a user prompt there and from a tool result here, and only the tool-result route gets the note-and-framing treatment.
- **Feeds** [Pydantic AI file understanding](pydantic-ai-file-understanding.md), which decides which files need describing instead of being noted, and which the note path bypasses.
- **Depends on** [Pydantic AI models and providers](pydantic-ai-models-and-providers.md) for the profile flags that choose the route, and on [model fallback](pydantic-ai-model-fallback.md) when the route is decided per attempt.
- **Coordinates with** [Pydantic AI tool search](pydantic-ai-tool-search.md): `ToolReturn.tools` is the reveal path for deferred tools, and the `ToolAvailabilityDeltaPart` it writes is the same record a mid-run tool addition writes.
- **Inherits its trust caveat from** [Pydantic AI client-supplied history](pydantic-ai-client-supplied-history.md): the `<pyai:tool_result>` frame attributes content, it does not authenticate it.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Tool Output" (raw lines 13–69) for JSON-serializable returns, the four-run sample, the semi-structured-versus-text rule and the unquoted-scalar rule; §"Where a returned file is sent" (70–99) for the three routes and their model and media-type lists, the `<pyai:tool_result>` frame and `See file …` substitution, the Gemini error-string exception, the realtime note, the `SystemPromptPart` analogy, the request-only rule, the `FallbackModel` per-model decision, the File Understanding alternative, and the user-prompt and `ToolReturn.content` failures; §"Advanced Tool Returns" (100–151) for the `click_and_capture` sample and the `return_value`/`tools`/`content`/`metadata` semantics, the `ToolAvailabilityDeltaPart` placement, the no-framing rule for `content` and the artifacts comparison. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
