---
type: Concept
title: Pydantic AI image generation
description: Pydantic AI v2.41's ImageGenerator direct API and ImageGeneration capability — three image providers behind one interface, the native-versus-local fallback, and how a BinaryImage comes back as a tool result.
tags: [ml, pydantic-ai, agents, media]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T06:10:00Z }
stale_after: 2027-01-30
sources:
  - id: pydantic-image-gen-2026
    resource: ../raw/image-generation/index.md
    scope: ../raw/image-generation/
    kind: article
    revision: sha256:2563fee14c8dd9209912c64e26cb10d888eb54d1e0d027343f546fe21ceaf69e
    title: "Generate images with Pydantic AI"
---

Pydantic AI 2.41.0 added a dedicated image-generation path: an `ImageGenerator` you call directly, with no agent run, plus an `ImageGeneration` [capability](pydantic-ai-capability-primitive.md) that hands the same generator to an agent so the model decides when to draw[^pydantic-image-gen-2026] One interface covers OpenAI GPT Image, Google Gemini through either the Gemini Developer API or Vertex AI, and xAI Grok Imagine, and it returns images as `BinaryImage` values that can then become agent input or tool output. The path it replaces is the older one, where image generation ran through a conversational model holding an image-generation native tool. Everything below is Pydantic's own announcement; no generator was called in this ingest.

## Two entry points

| Entry point | Declared as | Who decides to generate |
| --- | --- | --- |
| Direct | `ImageGenerator('openai:gpt-image-2')`, then `.generate_sync(prompt)` or `await .generate(prompt)` | Your application |
| Agent capability | `capabilities=[ImageGeneration(native=False, local=images)]` | The model, as a tool call inside the run |

The provider prefix selects the backend: `openai:` for GPT Image, `google:` for the Gemini Developer API, `google-cloud:` for Vertex AI, `xai:` for Grok Imagine, and each provider needs its own optional dependency and credentials. The article's install example is `uv add 'pydantic-ai-slim[openai]>=2.41.0'` with `OPENAI_API_KEY` exported[^pydantic-image-gen-2026]

`generate_sync` returns a result whose `.image` is a `BinaryImage` carrying bytes and media type directly, so the documented write is `Path('cafe.png').write_bytes(result.image.data)`; asynchronous code awaits `images.generate(...)` instead. Passing reference images through `images=` edits or transforms them rather than generating from text alone[^pydantic-image-gen-2026]

## The native/local switch

`ImageGeneration` takes three shapes, and they differ in whether a fallback exists at all[^pydantic-image-gen-2026]:

| Declaration | Behaviour |
| --- | --- |
| `ImageGeneration()` | Native only; no fallback configured for you |
| `ImageGeneration(local=images)` | Prefers native generation when the agent's model supports it, otherwise uses the supplied generator |
| `ImageGeneration(native=False, local=images)` | Forces the supplied generator |

"Local" means a tool implementation in your application, not a local model — the generator still calls the remote image provider. The article is explicit that this is fallback based on model capabilities, not automatic failover between image providers after a failed request, so cross-provider resilience remains the application's problem. The native path is the `ImageGenerationTool` native tool, which asks the conversational model to generate the image[^pydantic-image-gen-2026] That makes `ImageGeneration` a second instance of the pattern recorded for `WebSearch` on the [capability primitive](pydantic-ai-capability-primitive.md) page: one capability, provider-native where possible, an application-supplied local implementation otherwise.

## Reading the image back out

Under the capability, `result.output` stays the model's text and the image arrives as a tool result, so it is read off `result.all_messages()` — filtering message parts for `ToolReturnPart`, then `part.files` for `BinaryImage`[^pydantic-image-gen-2026] The image also stays in the conversation, which is what lets the model keep working on what it just made; the article's example has it write alt text for the illustration it generated.

A hand-written tool gives the same effect with control over what the tool returns. A tool may return `list[str | BinaryImage]`: the text becomes the tool result the model reads, while the `BinaryImage` enters the model's input as an image[^pydantic-image-gen-2026] That list form is the documented way to both confirm the work in words and hand the picture back for follow-up reasoning.

## Settings, and where provider differences leak

Common settings such as `dimensions` and `aspect_ratio` share one interface while provider-specific controls keep their prefixes. The adapters validate supported geometry and warn about settings that are ignored or overridden, but the provider still enforces its own limits, so a warning is not a guarantee. The article points at a separate settings guide for the per-provider differences and does not reproduce them[^pydantic-image-gen-2026]

## Why it shipped

The stated rationale is also the adoption argument[^pydantic-image-gen-2026]:

- **Less adapter code.** Provider setup, request mapping, and decoding into one result type are written once instead of per project.
- **Typed settings and earlier feedback.** Geometry is checked before the request, as a warning rather than a silent drop.
- **Comparable models.** Switching provider is a credential plus prefixed settings change, not a rewrite of the response handling.
- **Framework integration.** A `BinaryImage` can become agent input or a tool result, and the [Harness](pydantic-ai-harness.md) adds media externalization for moving large payloads out of persisted message history. Storage is configured separately — generating an image does not persist it.
- **Tracing.** The generator is instrumented, so its calls appear beside agent and tool spans in Logfire.

The maintainers' own framing is that they had treated image generation as a tool anyone could hand-roll until users asked for it, and that the release came from a community champion — Egon Ferri opened the original PR — rather than from a roadmap item. The release landed after the [Harness](pydantic-ai-harness.md), the capability work, and [v2](pydantic-ai-v2-release.md) shipped in between[^pydantic-image-gen-2026]

## Tracing

`ImageGenerator(..., instrument=True)` traces the image-generation call and `logfire.instrument_pydantic_ai()` traces the surrounding agent; the article's recorded cafe workflow shows a visual-brief subagent, the generation, and the alt-text step on one trace[^pydantic-image-gen-2026] One version-bound caveat: on the recorded stack — Pydantic AI 2.41.0 with Logfire 5.0.0 — an image returned directly by the capability appeared as JSON in Logfire rather than with the preview rendered for a tool's own binary content, with preview parity tracked as an open issue. [Pydantic AI observability](pydantic-ai-observability.md) carries the instrumentation context this sits in.

## Limits

- Every claim above is **Reported** from a vendor announcement; no `ImageGenerator` was constructed, no provider called, no image written, and no trace inspected[^pydantic-image-gen-2026]
- The page is `draft` under the `pydantic-ai` domain rule: the only supporting source is vendor material and the only versions named are the `>=2.41.0` install floor and the 2.41.0 trace, so behaviour in later releases is unconfirmed.
- Per-provider settings, output formats, and editing surfaces live in linked guides that were read as links, not followed; the article does not restate them.
- Cost, rate limits, content-policy handling, and image storage or retention are not covered at all.
- The native tool's own argument shape is described by reference to the native-tools guide only.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md): `ImageGeneration` is a core capability and the second documented case of the native-or-local fallback pattern.
- **Returns** `BinaryImage` values that become tool results and agent input, so generated output rejoins the message history that [conversation state](pydantic-ai-conversation-state.md) persists.
- **Uses** the [Harness](pydantic-ai-harness.md)'s media externalization when generated payloads must leave persisted message history.
- **Traced by** [Pydantic AI observability](pydantic-ai-observability.md), through `instrument=True` and the Logfire instrumentor.
- **Ships in** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) line at the 2.41.0 boundary.

[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, 1,398 words; §"Generate an image" (raw lines 19–46) for the install command and version floor, provider prefixes, `generate_sync`/`generate`, `BinaryImage`, and reference images; §"Let an agent generate the image" (lines 47–86) for the three `ImageGeneration` shapes, the native `ImageGenerationTool` path, and reading images from `ToolReturnPart.files`; §"Why we added image generation" (lines 87–102) for typed settings, the rationale list, media externalization, and the decision to ship; §"Write your own tool and trace it in Logfire" (lines 103–140) for the `list[str | BinaryImage]` tool return, `instrument=True`, the 2.41.0/Logfire 5.0.0 preview gap, and the issue link; §"Keeping open source fun" (lines 141–157) for Egon Ferri and the original PR. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; nothing was executed.
