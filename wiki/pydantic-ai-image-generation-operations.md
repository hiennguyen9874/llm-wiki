---
type: Concept
title: Pydantic AI image generation operations
description: Provider-specific editing, geometry, auth, errors, and telemetry for Pydantic AI's direct ImageGenerator API — Google's Files API and gs:// references, its SynthID watermark and billed thinking included — plus when to choose it over the agent capability.
tags: [pydantic-ai, agents, media]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:56:12Z }
stale_after: 2027-02-18
sources:
  - id: image-guide
    resource: ../raw/guides/image-generation/index.md
    scope: ../raw/guides/image-generation/
    kind: article
    revision: sha256:c44e81dceb4a021636dcec3decc6a20e285d53614aa56e7334c2cfeb6d3f8a25
    title: Image Generation
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

Pydantic AI's vendor guide describes the direct `ImageGenerator` API for application-controlled generation and editing, including provider-specific constraints that a portable interface cannot hide. The guide does not identify a framework version; all API and behavior claims below are **Reported for that version-unknown documentation**, not independently verified. For the version 2.41 announcement and agent-controlled alternative, see [Pydantic AI image generation](pydantic-ai-image-generation.md).[^image-guide]

## Provider and editing boundaries

The guide selects OpenAI GPT Image with `openai:`, Gemini Developer API with `google:`, Vertex AI with `google-cloud:`, and Grok Imagine with `xai:`. Install the matching `pydantic-ai-slim[openai]` (key in `OPENAI_API_KEY`), `[google]` (key in `GOOGLE_API_KEY` for the Gemini Developer API) or `[xai]` (key in `XAI_API_KEY`) extra; the `google-cloud:` prefix uses Application Default Credentials instead of an API key, and xAI goes through the official SDK over gRPC. `gateway/google:` routes through Vertex, while `gateway/openai:` and `gateway/xai:` are rejected. DALL·E 2 and 3 are rejected rather than treated as GPT Image models.[^image-guide]

For editing, `images=` accepts ordered `BinaryImage`, `ImageUrl`, or provider-hosted `UploadedFile` references, subject to provider constraints. Masked editing is not supported. Downloads by Pydantic AI are limited to 50 MiB.[^image-guide]

| Provider | Editing and output constraints |
| --- | --- |
| OpenAI | No `UploadedFile`; reference content must be PNG, JPEG or WebP. Multiple outputs use `openai_n`. |
| Gemini Developer API | Hosted file IDs must be Files API URIs, not `files/...` names. A Files API `ImageUrl` needs an explicit media type. One image per request. |
| Vertex AI | Hosted file IDs must be `gs://` URIs; `gs://` image URLs are forwarded server-side unless `force_download` is set, in which case downloading fails. Other URLs are downloaded and inlined. The client transport determines the file store. |
| xAI | Hosted files must precede URL and binary references or `UserError` is raised; xAI enforces a documented maximum of five references. Multiple outputs use `xai_n`. gRPC ignores `extra_headers` and `extra_body` with a warning. |

These are the guide's version-unknown behaviors; check current provider documentation before relying on specific model limits.[^image-guide]

## Google's file references, and what every image costs

The Google setup page supplies the mechanism behind the two Google rows above[^pydantic-google-2026] Both APIs are reached through the same `ImageGenerator` with a prefixed model name — `ImageGenerator('google:gemini-3.1-flash-lite-image', settings=GoogleImageGenerationSettings(google_image_config={'aspect_ratio': '1:1', 'image_size': '1K'}))` for the Gemini Developer API and the same settings object with a `google-cloud:` model for Vertex — and constructing `GoogleImageGenerationModel` with a `GoogleCloudProvider` is how the Vertex project and location are set explicitly[^pydantic-google-2026]

A reference image takes three routes[^pydantic-google-2026]:

| Reference | What is sent |
| --- | --- |
| `BinaryImage` or an inline image | Inline bytes, on both APIs |
| A downloadable image URL | Downloaded and inlined, on both APIs |
| A reference the selected transport hosts itself | Forwarded as a `fileData` part, **not downloaded** |

The third row is the transport-dependent one. On the Gemini Developer API the reference is a Files API URI, passed as an `UploadedFile` or an `ImageUrl`; on Vertex AI, where the Files API is not available, it is a Cloud Storage `gs://bucket/path` URI, passed as an `UploadedFile` whose `file_id` starts with `gs://` or an `ImageUrl` whose URL does and that is not `force_download`[^pydantic-google-2026] Vertex reads the object server-side, so a multi-megabyte reference never passes through your process[^pydantic-google-2026] Neither transport accepts the other's references: a Files API id sent to Vertex raises a `UserError`[^pydantic-google-2026]

**Which API a model talks to is read off the client, not the provider name** — the same rule that decides Files API versus `gs://` in [multimodal input](pydantic-ai-multimodal-input.md)'s upload table — so a Vertex-backed client passed to `GoogleProvider` is treated as Vertex, while a Gemini Developer API client passed to `GoogleCloudProvider` keeps Files API support[^pydantic-google-2026] A configuration that pairs the wrong provider with the wrong client therefore fails on the file reference rather than at construction.

Two costs are unconditional. The adapter requests an **image-only response**, because `ImageGenerator` returns generated images rather than Gemini's optional conversational text[^pydantic-google-2026] And every generated image carries a **SynthID watermark**, which cannot be switched off; the Gemini 3 image models are thinking models, so thinking is always on and billed, and its tokens are included in the result's `usage`[^pydantic-google-2026] The per-model thinking levels are in [Google thinking levels](google-thinking-levels.md).

## Model names and custom providers

The provider validates the model name, so any current model in a family works, including a release newer than the installed Pydantic AI version. `KnownImageGenerationModelName` only drives autocompletion and every other name is passed through unchanged, which makes adopting a new image model a configuration change rather than a library upgrade. The cost is that per-model geometry tables and canonical shapes are keyed only to the versions Pydantic AI knows, so an unrecognized OpenAI model falls back to the pass-through dimensions described under settings, and a Google or xAI model outside the known mapping fails before the request.[^image-guide]

Authentication, base URL and the underlying SDK client are customized by constructing the provider's image model class instead of passing a `'provider:model'` string — `OpenAIImageGenerationModel('gpt-image-2.5-flare', provider=OpenAIProvider(base_url=..., api_key=...))`, then `ImageGenerator(model)`. Each class takes the same `Provider` its SDK uses, so an OpenAI-compatible gateway or a pre-configured client behaves as it does for conversational models.[^image-guide]

## Settings and geometry

In the version-unknown guide, settings merge model → generator → call, with later values overriding matching keys. `dimensions=(width, height)` and `aspect_ratio` are mutually exclusive; prefixed geometry overrides the corresponding portable mapping and warns on disagreement. OpenAI maps ratios to known sizes; Gemini sends the ratio to the provider; xAI uses a restricted gRPC enum. Unsupported OpenAI or xAI ratios raise `UserError`, while a Gemini rejection can be `ModelHTTPError`.[^image-guide]

For an unrecognized OpenAI model, structurally valid exact dimensions are forwarded for provider validation, but `aspect_ratio` fails without a canonical mapping. For Google and xAI, dimensions outside the selected model's known mapping fail before the request. The guide's model-specific dimension tables include vendor-reported live API checks, but give no test date or reproducible protocol; consult the source tables rather than assuming identical pixels across models or tiers.[^image-guide]

`dimensions` also accepts shapes outside the canonical ratio table when the selected model documents or has been verified to produce them exactly, and the acceptance rule is per family. GPT Image 1.x takes only `1024×1024`, `1024×1536` or `1536×1024`. GPT Image 2 and 2.6 take any positive shape whose sides are multiples of 16, whose longest edge is at most 3840, whose aspect ratio is at most 3:1, and whose area falls between 655,360 and 8,294,400 pixels; any other non-DALL·E OpenAI model is forwarded as `size` for OpenAI itself to judge. Gemini 2.5 Flash Image serves only its ten canonical shapes with no separate resolution tier, Gemini 3.1 Flash Lite Image only its fourteen `1K` shapes, Gemini 3 Pro Image adds `2K` and `4K` variants by multiplying both sides by 2 or 4, and Gemini 3.1 Flash Image adds those tiers plus `512` variants by halving both sides, with five extended ratios whose tiers do not scale uniformly. Grok Imagine accepts its verified `1k` and `2k` shapes, while `grok-imagine-image-2.0` raises `UserError` for `dimensions` because nobody has probed it — use `aspect_ratio` or the `xai_` settings there, which xAI validates itself.[^image-guide]

The guide reports that `openai_moderation` on edits, `openai_input_fidelity` on generation, and xAI's `extra_headers` and `extra_body` are dropped with warnings; Google also drops non-string-keyed-mapping `extra_body` with a warning. Transparent OpenAI backgrounds require PNG or WebP and model support.[^image-guide]

## Results, usage, and instrumentation

In the version-unknown guide, a result holds at least one normalized image plus request usage, model and provider identity, and provider-specific details. `result.image` returns the first `BinaryImage`, while `result.images[n].content` and per-image metadata such as `revised_prompt` are what multi-output calls need, and `result.usage.input_tokens` reports tokens per call. OpenAI's echoed size, quality and background are request parameters, not measurements of the returned bytes: the only geometry-adjacent field is `output_format`, derived from the bytes themselves. xAI's `provider_details.cost_usd`, when present, is provider-reported batch cost — the whole batch when `xai_n` is above 1 — not the portable `cost()` calculation.[^image-guide]

`instrument=True` or `ImageGenerator.instrument_all()` enables generator spans. The guide says spans include model identity, usage, image count and non-binary output metadata, but exclude image bytes, reference contents, URLs, provider file IDs and request escape hatches; provider SDK spans are separate. The span operation name `image_generation` is custom, while `image` is a standard output type.[^image-guide]

## Failure modes and retries

Failures arrive as the framework's ordinary exception types rather than as empty results, so a rejected prompt can be retried explicitly.[^image-guide]

| Exception | Raised when |
| --- | --- |
| `ContentFilterError` | A provider blocks the request or its output: OpenAI's `moderation_blocked` response, Google's safety, recitation or prohibited-content blocks (including Model Armor on Cloud), or xAI flagging every image in a batch. |
| `UserError` | The request cannot be built: an empty prompt, a reference-image type the selected provider does not accept, or `dimensions` the selected model cannot produce exactly. |
| `ModelHTTPError`, `ModelAPIError` | Other 4xx and 5xx provider responses, or a provider that cannot be reached; xAI's gRPC status codes map onto these same two. |
| `ModelRateLimitError`, `ModelUnavailableError`, `ModelConnectionError`, `ModelTimeoutError` | Narrower categories the provider errors also instantiate when the provider says what went wrong, or when an attempt fails at the transport. |

A moderation block is therefore a catchable signal, not a dead end: the guide's pattern catches `ContentFilterError` and re-issues the call with a rewritten prompt. xAI is the exception to all-or-nothing moderation — a partially blocked batch returns the clean images and reports the blocked positions instead of raising. Generation can take minutes and fronting proxies often cut connections at 60–180 seconds, so client and proxy timeouts must exceed the worst case.[^image-guide]

## Testing and extensions

The guide's version-unknown `TestImageGenerationModel` produces a deterministic 1×1 PNG without provider calls; `generator.override(model=test_model)` permits inspection of `last_settings`. Setting `ALLOW_MODEL_REQUESTS = False` blocks real image requests but not the test model. A custom `ImageGenerationModel` can call `prepare_generate()` to validate inputs and merge defaults, and must return at least one image; `WrapperImageGenerationModel` wraps an existing model.[^image-guide]

## Choosing between the direct API and an agent

The guide closes with a three-way split that resolves to the two entry points recorded in [Pydantic AI image generation](pydantic-ai-image-generation.md): use `ImageGenerator` when the application decides to generate or edit, needs several outputs, or supplies reference images; use the `ImageGeneration` capability when an agent should decide, with native execution where available and a direct image-model fallback otherwise; and use `ImageGenerationTool` alone when you need direct control over a conversational provider's native image-generation tool. Provider-adaptive agent usage and reading the image back out of an agent run are documented on the capability page, not in this guide.[^image-guide]

## Limits and relationships

- **Coverage:** the local package consists of the inspected `index.md`; external API, provider and capability links were not fetched. The capture supplies no publication date, framework version, license, or independent corroboration. No code, tests, provider requests or telemetry were executed or inspected. The canonical pixel tables are summarized as acceptance rules rather than reproduced, and their live-API verification carries no date or protocol. `draft` reflects these limits.
- **Extends** [Pydantic AI image generation](pydantic-ai-image-generation.md) with the direct API's operational constraints; the announcement's v2.41.0 floor does not establish the version of this guide.
- **Uses** [Pydantic AI observability](pydantic-ai-observability.md) for the wider instrumentation context.
- **Is completed for Google by** [Google models in Pydantic AI](google-models-in-pydantic-ai.md), which owns the two Google transports this page's file-reference rules depend on, and by [Google thinking levels](google-thinking-levels.md) for the effort settings behind the billed thinking.[^pydantic-google-2026]

[^image-guide]: Pydantic Docs, “Image Generation,” https://pydantic.dev/docs/ai/guides/image-generation/, 3,684 words; local capture `raw/guides/image-generation/index.md`, content digest sha256:c44e81dceb4a021636dcec3decc6a20e285d53614aa56e7334c2cfeb6d3f8a25. Cited sections, with capture line ranges: “Quick Start” (13–53), “Choosing a model” (54–65), “Editing Images” (66–97), “Providers” (98–197, including “Customizing the provider” 180–197), “Settings” (198–343, including “Output Geometry” 228–244, “Canonical Dimensions for `aspect_ratio`” 245–271, “Supported Exact dimensions” 272–316, and “Provider-Specific Settings” 317–343), “Results and Usage” (344–375), “Error Handling” (376–408), “Instrumentation” (409–433), “Testing” (434–462), “Building Custom Image Generation Models” (463–513), and “Using Image Generation with an Agent” (514–524). **Reported**, vendor documentation; framework version and publication date unspecified.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Image generation" (raw lines 278–300) for `ImageGenerator` over `google:` and `google-cloud:` models with `GoogleImageGenerationSettings(google_image_config={'aspect_ratio': '1:1', 'image_size': '1K'})`, `GoogleImageGenerationModel` with a `GoogleCloudProvider` for explicit project and location, the inline/downloadable/`fileData` reference routes, the Files API URI versus `gs://` distinction with the `UploadedFile`/`ImageUrl` forms, the server-side Vertex read, the `UserError` on a cross-transport reference, the client-decides-the-API rule, the image-only response, the unconditional SynthID watermark and the always-on billed thinking of the Gemini 3 image models.
