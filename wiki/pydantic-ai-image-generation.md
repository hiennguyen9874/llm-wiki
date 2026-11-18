---
type: Concept
title: Pydantic AI image generation
description: Pydantic AI's ImageGenerator direct API and ImageGeneration capability — the native-tool, direct-model and subagent routes an agent chooses between, which settings each route applies, and where the generated BinaryImage lands.
tags: [ml, pydantic-ai, agents, media]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:34:00Z }
stale_after: 2027-01-30
sources:
  - id: pydantic-image-gen-2026
    resource: ../raw/image-generation/index.md
    scope: ../raw/image-generation/
    kind: article
    revision: sha256:2563fee14c8dd9209912c64e26cb10d888eb54d1e0d027343f546fe21ceaf69e
    title: "Generate images with Pydantic AI"
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
  - id: pydantic-image-gen-capability-docs
    resource: ../raw/capabilities/image-generation/index.md
    scope: ../raw/capabilities/image-generation/
    kind: documentation
    revision: sha256:9a2451a4bea14f49a395b66f9464f2c43f01aea4c52aba6dbb65694390deead9
    title: "ImageGeneration Capability"
---

Pydantic AI 2.41.0 added a dedicated image-generation path: an `ImageGenerator` you call directly, with no agent run, plus an `ImageGeneration` [capability](pydantic-ai-capability-primitive.md) that hands the same generator to an agent so the model decides when to draw[^pydantic-image-gen-2026] One interface covers OpenAI GPT Image, Google Gemini through either the Gemini Developer API or Vertex AI, and xAI Grok Imagine, and it returns images as `BinaryImage` values that can then become agent input or tool output. The path it replaces is the older one, where image generation ran through a conversational model holding an image-generation native tool. Both sources are vendor material and no generator was called in this ingest; the capability's reference page adds the routing contract recorded below — which route a request takes, which settings survive it, and which message part carries the image[^pydantic-image-gen-capability-docs]

## Two entry points

| Entry point | Declared as | Who decides to generate |
| --- | --- | --- |
| Direct | `ImageGenerator('openai:gpt-image-2')`, then `.generate_sync(prompt)` or `await .generate(prompt)` | Your application |
| Agent capability | `capabilities=[ImageGeneration(native=False, local=images)]` | The model, as a tool call inside the run |

The provider prefix selects the backend: `openai:` for GPT Image, `google:` for the Gemini Developer API, `google-cloud:` for Vertex AI, `xai:` for Grok Imagine, and each provider needs its own optional dependency and credentials. The article's install example is `uv add 'pydantic-ai-slim[openai]>=2.41.0'` with `OPENAI_API_KEY` exported[^pydantic-image-gen-2026]

`generate_sync` returns a result whose `.image` is a `BinaryImage` carrying bytes and media type directly, so the documented write is `Path('cafe.png').write_bytes(result.image.data)`; asynchronous code awaits `images.generate(...)` instead. Passing reference images through `images=` edits or transforms them rather than generating from text alone[^pydantic-image-gen-2026]

## The native/local switch

`ImageGeneration` takes a few shapes, and they differ in whether — and how — a fallback exists at all[^pydantic-image-gen-2026][^pydantic-image-gen-capability-docs]:

| Declaration | Behaviour |
| --- | --- |
| `ImageGeneration()` | Native only; no fallback configured for you |
| `ImageGeneration(local=images)` | Prefers native generation when the agent's model supports it, otherwise uses the supplied generator |
| `ImageGeneration(native=False, local=images)` | Forces the supplied generator |
| `ImageGeneration(fallback_image_model='openai:...')` | Prefers native, otherwise the direct image API through that model |
| `ImageGeneration(fallback_subagent_model='google:...')` | Prefers native, otherwise a subagent running that model's native image tool |

"Local" means a tool implementation in your application, not a local model — the generator still calls the remote image provider. The article is explicit that this is fallback based on model capabilities, not automatic failover between image providers after a failed request, so cross-provider resilience remains the application's problem. The native path is the `ImageGenerationTool` native tool, which asks the conversational model to generate the image[^pydantic-image-gen-2026] That makes `ImageGeneration` a second instance of the pattern recorded for `WebSearch` on the [capability primitive](pydantic-ai-capability-primitive.md) page: one capability, provider-native where possible, an application-supplied local implementation otherwise.

## Fallback options: direct model or subagent

`ImageGeneration` covers a model that does not generate images natively with two built-in mechanisms, plus any implementation you write yourself[^pydantic-image-gen-capability-docs]:

| Route | Configured as | What the tool call becomes |
| --- | --- | --- |
| Native tool | the provider's native tool, or `native=ImageGenerationTool(...)` | the conversational model's own image-generation tool |
| Direct model | `local=ImageGenerator(...)`, or `fallback_image_model='provider:model'` | one image API call, with no extra agent run |
| Subagent | `fallback_subagent_model='provider:model'` | an additional agent whose native `ImageGenerationTool` produces the image |
| Your own | `local=` with a callable, `Tool` or toolset | whatever that implementation does |

The fallback fields are alternatives: stating more than one raises `UserError`[^pydantic-image-gen-capability-docs] `local` is the field that takes a reusable `ImageGenerator`, whose own settings then apply, while a bare `ImageGenerationModel` or a `'provider:model'` name goes on `fallback_image_model`[^pydantic-image-gen-capability-docs] Because `ImageGeneration` ships no local strategy of its own, a `local=` callable is also the only way to supply an implementation of your own, and the capability passes it none of its image settings[^pydantic-image-gen-capability-docs] The two fields that name an image model are not interchangeable: `image_model` configures the provider's native tool and is unprefixed, while `fallback_image_model` selects the direct model and carries its provider[^pydantic-image-gen-capability-docs]

Choose the direct model when the geometry or the image model is yours to decide; choose the subagent when you want the other model's native tool semantics and the settings that tool carries[^pydantic-image-gen-capability-docs] An explicit native instance — or a callable taking `RunContext` that returns an `ImageGenerationTool` or `None` — is how the native path gets its full provider-native configuration; that callable resolves on every model request and again when the subagent runs, with the same `deps` but a separate `RunContext`, so shared configuration must read `ctx.deps`[^pydantic-image-gen-capability-docs]

## Reading the image back out

Under the capability the image is in the run's message history, not necessarily in its final response: an agent usually answers in text after drawing, so `result.response.images` is empty unless that last response carries the image[^pydantic-image-gen-capability-docs] Where it lands depends on the route[^pydantic-image-gen-capability-docs]:

| Route | The image is in |
| --- | --- |
| Native tool | `ModelResponse.images` on the response that generated it |
| Direct model, subagent | the `generate_image` tool call's `ToolReturnPart.files` |
| A `local` tool of your own | that tool's own return part, under its own tool name |

The announcement described the tool-result half only; the capability reference is explicit that the native path puts the image on the model response instead[^pydantic-image-gen-2026][^pydantic-image-gen-capability-docs] Collecting both covers whichever path each request took, which is why the documented pattern walks `all_messages()` and checks each message type rather than reading `result.output`[^pydantic-image-gen-capability-docs] A hand-written tool should return `BinaryImage` values rather than raw `bytes`, because bytes reach the model as base64 text[^pydantic-image-gen-capability-docs]

A hand-written tool gives the same effect with control over what the tool returns. A tool may return `list[str | BinaryImage]`: the text becomes the tool result the model reads, while the `BinaryImage` enters the model's input as an image[^pydantic-image-gen-2026] That list form is the documented way to both confirm the work in words and hand the picture back for follow-up reasoning.

## The image as the run's output

Setting `output_type=BinaryImage` makes the image the run's output instead of text[^pydantic-image-gen-capability-docs] That check runs against the agent's conversational model, not against a configured fallback: a model that does not generate images itself raises `UserError` even when a fallback is set, so on those models the image is collected from the history instead — and on a model that does, the setting enables its own native generation even beside `native=False`, so the output comes from that model rather than from the generator you configured[^pydantic-image-gen-capability-docs]

## Settings, precedence, and route warnings

Common settings such as `dimensions` and `aspect_ratio` share one interface while provider-specific controls keep their prefixes. The adapters validate supported geometry and warn about settings that are ignored or overridden, but the provider still enforces its own limits, so a warning is not a guarantee[^pydantic-image-gen-2026] The capability adds rules about which route can honour what[^pydantic-image-gen-capability-docs]:

- **Only the direct generator applies `dimensions`**, and only it applies the aspect ratios the native tool does not share, so a guarantee needs `native=False`. With the default `native=True`, a natively generating model takes the native path, which has no equivalent for them, and the request warns that the settings went unapplied.
- **A capability-level setting beats an inherited one.** A static native instance's `aspect_ratio` reaches whichever fallback is configured, while a capability-level `aspect_ratio` takes precedence over it. `dimensions` is the same geometry spelled differently and cannot be combined with it: setting both on the capability raises `UserError` at construction, once a direct generator is configured to apply them.
- **Native-only settings do not cross over.** `quality` and `output_format` belong to the native tool; on a direct generator their provider-prefixed equivalents (`openai_quality`, `openai_output_format`) are what you configure.
- **Two settings cannot reach the direct fallback at all.** `action='edit'` raises `UserError` there, because the `generate_image` tool receives no reference images, and `image_model` is ignored with a warning, because the generator already names the image model it uses. With `native=False` both land at construction — the warning and the error — while with native enabled they surface only on a request that routes to the generator.
- **Warnings are per model, and not guaranteed.** Under a `FallbackModel` each member takes the path its own profile selects and each dropped setting is named, including inside a workflow running on `TemporalDurability`. A `TemporalAgent` whose current model is a `FallbackModel`, or a routing model with no profile of its own, produces no warning, because nothing public says which model a request reaches.
- **The subagent speaks the native vocabulary.** `dimensions`, arbitrary GPT Image 2 sizes and additional aspect ratios are ignored there with a warning; use `native=False` with a direct generator for those. A provider's native tool, by contrast, silently drops a setting it has no field for — the warnings above are the framework's, not the provider's.

The direct generator must return exactly one `BinaryImage`; `ImageGenerator` used on its own is the path for multiple images or reference-image editing[^pydantic-image-gen-capability-docs] A provider content block becomes a retry prompt on either local path, so the model that wrote the prompt can rephrase it; the subagent additionally turns an `UnexpectedModelBehavior` from its run into a retry prompt, the direct model raises it, and `ImageGenerator` alone raises `ContentFilterError`[^pydantic-image-gen-capability-docs] The announcement points at a separate settings guide for the per-provider tables and does not reproduce them[^pydantic-image-gen-2026]

OpenAI's own setup page supplies the two constraints that decide whether a request runs at all: GPT Image models require a verified organization on a paid usage tier, so on an unverified one every request fails with a rate-limit error before anything generates, and complex prompts can take up to two minutes[^pydantic-openai-2026] It also states the passthrough policy behind the prefixed settings — provider-specific values are forwarded to OpenAI so newly supported ones are not blocked by stale client-side checks — and the OpenAI input rules [image generation operations](pydantic-ai-image-generation-operations.md) tabulates: the edit endpoint takes file content rather than an `UploadedFile` provider file ID, and transparent backgrounds need PNG or WebP output on a model that supports them[^pydantic-openai-2026]

## Why it shipped

The stated rationale is also the adoption argument[^pydantic-image-gen-2026]:

- **Less adapter code.** Provider setup, request mapping, and decoding into one result type are written once instead of per project.
- **Typed settings and earlier feedback.** Geometry is checked before the request, as a warning rather than a silent drop.
- **Comparable models.** Switching provider is a credential plus prefixed settings change, not a rewrite of the response handling.
- **Framework integration.** A `BinaryImage` can become agent input or a tool result, and the [Harness](pydantic-ai-harness.md) adds media externalization for moving large payloads out of persisted message history. Storage is configured separately — generating an image does not persist it.
- **Tracing.** The generator is instrumented, so its calls appear beside agent and tool spans in Logfire.

The maintainers' own framing is that they had treated image generation as a tool anyone could hand-roll until users asked for it, and that the release came from a community champion — Egon Ferri opened the original PR — rather than from a roadmap item. The release landed after the [Harness](pydantic-ai-harness.md), the capability work, and [v2](pydantic-ai-v2-release.md) shipped in between[^pydantic-image-gen-2026]

## Tracing

`ImageGenerator(..., instrument=True)` traces the image-generation call and `logfire.instrument_pydantic_ai()` traces the surrounding agent; the article's recorded cafe workflow shows a visual-brief subagent, the generation, and the alt-text step on one trace[^pydantic-image-gen-2026] Instrumentation is per generator rather than per agent: the agent-level `Instrumentation` capability does not reach a direct generator, so a run records no `image_generation` span unless the generator carries its own — pass `instrument=`, or switch it on globally with `ImageGenerator.instrument_all()`[^pydantic-image-gen-capability-docs] One version-bound caveat: on the recorded stack — Pydantic AI 2.41.0 with Logfire 5.0.0 — an image returned directly by the capability appeared as JSON in Logfire rather than with the preview rendered for a tool's own binary content, with preview parity tracked as an open issue. [Pydantic AI observability](pydantic-ai-observability.md) carries the instrumentation context this sits in.

## Agent specs

A direct model name in `fallback_image_model` survives into a JSON or YAML agent spec through `ImageGeneration.from_spec()`, which keeps that serializable subset explicit while exposing the same setting names[^pydantic-image-gen-capability-docs] Runtime objects are not serializable and stay in Python: an `ImageGenerationModel` on `fallback_image_model`, and the `ImageGenerator`, `Tool`, toolsets and callables that `local` takes[^pydantic-image-gen-capability-docs] `dimensions` is written as the two-item array JSON and YAML use, and Pydantic AI converts it to the `(width, height)` tuple the Python API takes[^pydantic-image-gen-capability-docs]:

```yaml
model: anthropic:claude-sonnet-5-5
capabilities:
  - ImageGeneration:
      native: false
      fallback_image_model: openai:gpt-image-2.5-flare
      dimensions: [1280, 720]
```

## Limits

- Every claim above is **Reported** from vendor documentation; no `ImageGenerator` was constructed, no provider called, no image written, and no trace inspected[^pydantic-image-gen-2026][^pydantic-image-gen-capability-docs]
- The page is `draft` under the `pydantic-ai` domain rule: both sources are vendor material, the only versions named are the `>=2.41.0` install floor and a 2.41.0 trace, and the capability reference page names no framework version at all, so every route, precedence and warning rule above is version-unknown and later-release behaviour is unconfirmed.
- Neither source reproduces the per-provider settings tables, and editing constraints and content-policy handling remain in the separately captured, version-unknown guide summarized in [image generation operations](pydantic-ai-image-generation-operations.md); the provider support tables under the native-tools guide are linked, not inspected.
- The routing rules are prose and examples rather than a schema: the sources do not state what a `local` callable is passed beyond that it gets no image settings, which model names each route accepts, or the exact text and trigger of each warning, and no example was run. The model names in the examples (`gpt-image-2.5-flare`, `gemini-3.1-flash-image`, `claude-sonnet-5-5`) are therefore illustrative, not confirmed to be available.
- The announcement does not cover cost, rate limits, content-policy handling, or image storage and retention; the operations guide reports provider cost metadata and moderation behavior, but not a complete pricing or retention policy.
- The native tool's own argument shape is described by reference to the native-tools guide only.

## Relationships

- **Detailed for OpenAI** in [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md), which records the `gpt-image-2` settings form, the verified-organization requirement and the Images-API-versus-Responses split.
- **Detailed by** [image generation operations](pydantic-ai-image-generation-operations.md), covering a separate guide whose framework version is unspecified.
- **Routes through** [model fallback](pydantic-ai-model-fallback.md) when the conversational model is a `FallbackModel`: each member takes the route its own profile selects, and only the members whose profile is known produce a dropped-setting warning.
- **Warns under** the [durable execution](pydantic-ai-durable-execution.md) Temporal integration: the same per-route warnings appear inside a `TemporalDurability` workflow, but a `TemporalAgent` over a `FallbackModel` gives none.
- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md): `ImageGeneration` is a core capability and the second documented case of the native-or-local fallback pattern.
- **Returns** `BinaryImage` values that become tool results and agent input, so generated output rejoins the message history that [conversation state](pydantic-ai-conversation-state.md) persists.
- **Uses** the [Harness](pydantic-ai-harness.md)'s media externalization when generated payloads must leave persisted message history.
- **Traced by** [Pydantic AI observability](pydantic-ai-observability.md), through `instrument=True` and the Logfire instrumentor.
- **Ships in** the [Pydantic AI v2 release](pydantic-ai-v2-release.md) line at the 2.41.0 boundary.
- **Reaches the native route through** [native tool configuration](pydantic-ai-native-tool-configuration.md), which records `ImageGenerationTool`'s provider support, its parameter matrix, and the `aspect_ratio`-to-`size` mapping OpenAI's discrete sizes force.
- **Related to** [Pydantic AI structured output](pydantic-ai-structured-output.md): `output_type=BinaryImage` is one branch of the output contract, so an agent can return a generated image as its run output, and a `BinaryImage | str` agent keeps the text on `ModelResponse.text`.

[^pydantic-image-gen-capability-docs]: Pydantic Docs, "ImageGeneration Capability", https://pydantic.dev/docs/ai/capabilities/image-generation/, 1,550 words as declared; local capture `raw/capabilities/image-generation/index.md`, content digest sha256:9a2451a4. Cited sections with capture line ranges: opening definition and the native-only default (lines 11–41), the two model-naming fields (42–43), the routing examples (44–71), settings precedence, `action='edit'`, `image_model` and per-model warnings (73–78), per-generator instrumentation (79–90), "Getting the Generated Image" (92–129), "Fallback Options" (131–143), and "Agent Specs" (144–155). Evidence class: **Reported** — vendor documentation naming no framework version or publication date; nothing was executed.
[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, 1,398 words; §"Generate an image" (raw lines 19–46) for the install command and version floor, provider prefixes, `generate_sync`/`generate`, `BinaryImage`, and reference images; §"Let an agent generate the image" (lines 47–86) for the three `ImageGeneration` shapes, the native `ImageGenerationTool` path, and reading images from `ToolReturnPart.files`; §"Why we added image generation" (lines 87–102) for typed settings, the rationale list, media externalization, and the decision to ship; §"Write your own tool and trace it in Logfire" (lines 103–140) for the `list[str | BinaryImage]` tool return, `instrument=True`, the 2.41.0/Logfire 5.0.0 preview gap, and the issue link; §"Keeping open source fun" (lines 141–157) for Egon Ferri and the original PR. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; nothing was executed.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Image generation" (raw lines 121–144) for `ImageGenerator('openai:gpt-image-2')` and `OpenAIImageGenerationSettings`, the Images-API-versus-Responses split, `BinaryImage`/`ImageUrl` reference inputs, the edit endpoint's file-content requirement, transparent backgrounds needing PNG or WebP, the provider-settings passthrough rule, the verified-organization rate-limit failure and the two-minute ceiling. Evidence class: **Reported** — vendor documentation; no generator was constructed and no image generated.
