---
type: Concept
title: Pydantic AI native tool configuration
description: What each provider-executed native tool supports in Pydantic AI — the per-provider support matrices for web search, X search, code execution, image generation, web fetch, memory, MCP servers, file search and the advisor, the parameters each provider honours or refuses, and the usage each tool bills.
tags: [pydantic-ai, native-tools, tools, providers]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:30:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-native-tools
    resource: ../raw/tools-toolsets/native-tools/index.md
    scope: ../raw/tools-toolsets/native-tools/
    kind: documentation
    revision: sha256:937d5ddc210f169eaf29f261253f91d5d308dc573d5607e6780363ae417e9bd7
    title: "Native Tools"
---

Each of the nine native tools has its own support boundary, and the boundary is narrower than the tool list suggests: web search runs almost everywhere, web fetch on two providers, memory on one, and no tool runs everywhere[^pydantic-docs-native-tools] Two rules recur across every tool and explain most of the matrices. A tool with parameters that restrict what it may do — `allowed_domains`, `blocked_domains`, `max_uses`, `external_web_access=False` — is treated as unsupported on a model that cannot apply them, so the tool is refused rather than degraded[^pydantic-docs-native-tools] And several tools bill in their own unit, reported in `RequestUsage.details` under a per-tool key rather than folded silently into tokens[^pydantic-docs-native-tools] The layer those rules belong to — attachment, `provider_settings` addressing, dynamic selection — is compiled in [Pydantic AI native tools](pydantic-ai-native-tools.md); this page is the per-tool half. The capture names no Pydantic AI version and no date, so every matrix row and default below is version-unknown.

## Web search

Support is broad but the parameter support is not[^pydantic-docs-native-tools]

| Provider | Supported | What to know |
| --- | --- | --- |
| OpenAI Responses | ✅ | Full support, and only the Responses API — Chat Completions is not supported. Search sources land on the `NativeToolReturnPart` only when `openai_include_web_search_sources` is set |
| Anthropic | ✅ | Full support |
| Google | ✅ | **No parameter support at all**, so any restricting parameter makes the tool unsupported. Sources are the return part's content, except on Gemini 3 with the Gemini API where they sit under the `sources` key of the last web search return, because Gemini does not say which search found which source. Gemini 2.5 and Google Cloud report searches after the text they ground |
| xAI | ✅ | Takes `blocked_domains`, `allowed_domains` and `user_location` |
| Groq | ✅ | Limited parameters, and only through Groq's compound models |
| OpenRouter | ✅ | OpenRouter's Beta web-search server tool; the model may make 0–N searches |
| OpenAI Chat, Bedrock, Mistral, Cohere, HuggingFace | ❌ | — |

The OpenRouter row carries the capture's own honesty note: recorded requests verify only that OpenRouter accepts the parameter *names*, and the per-engine effects are OpenRouter's documentation rather than observed behaviour[^pydantic-docs-native-tools] Per that documentation, native search ignores `search_context_size`, `user_location` is native-only, native OpenAI ignores `blocked_domains`, and `max_uses` works with non-native or Anthropic native search; sources surface in `provider_details['annotations']` only when a non-native engine ran the search[^pydantic-docs-native-tools]

### Parameters

| Parameter | OpenAI | Anthropic | xAI | Groq | OpenRouter |
| --- | --- | --- | --- | --- | --- |
| `search_context_size` | ✅ | ❌ | ❌ | ❌ | ✅ |
| `user_location` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `blocked_domains` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `allowed_domains` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `max_uses` | ❌ | ✅ | ❌ | ❌ | ✅\* |
| `external_web_access` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `provider_settings.anthropic.response_inclusion` | ❌ | ✅ | ❌ | ❌ | ❌ |
| `provider_settings.openrouter.engine`, `mode`, `max_results`, `max_total_results`, `max_characters` | ❌ | ❌ | ❌ | ❌ | ✅ |

\* OpenRouter forwards `max_uses` only to Anthropic-native search; other native providers ignore it[^pydantic-docs-native-tools]

`user_location` is a `WebSearchUserLocation` with `city`, `country`, `region` and `timezone`[^pydantic-docs-native-tools] Anthropic cannot be given both `blocked_domains` and `allowed_domains`[^pydantic-docs-native-tools] `search_context_size` (`'high'` in the sample) and `external_web_access` are the two options that tune rather than restrict[^pydantic-docs-native-tools]

### What a search bills

| Provider | Key | Counted as |
| --- | --- | --- |
| Anthropic | `web_search_requests` in `RequestUsage.details` | The number of searches, included in `RunUsage.cost` |
| Google | `web_search_requests` in `details`, plus billed `web_searches` on `RequestUsage` | One per **unique query** on Gemini 3; one per **grounded request that returned a web source** on Gemini 2.5 and older. Included in `RunUsage.cost`, without deducting Google's free grounding allowance |
| OpenAI | `web_search_requests` in `details` | The number of searches, included in `RunUsage.cost`; pages the model opens or searches *within* do not count as searches |

The Google row is the one to design a budget around: the same tool bills per unique query on Gemini 3 and per grounded request on older models, so the same conversation can cost a different number of web searches after a model upgrade[^pydantic-docs-native-tools] The OpenAI clarification is the other one that matters — following links inside a page it already fetched is free of the search counter.

## X search

`XSearchTool` is natively supported by xAI models only[^pydantic-docs-native-tools] On other models it is reachable through the `XSearch` capability with `fallback_subagent_model` set — the same no-default-fallback rule compiled in [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md)[^pydantic-docs-native-tools]

The tool takes `allowed_x_handles`, `from_date` and `to_date` as `datetime` values, and two content switches, `enable_image_understanding` and `enable_video_understanding`[^pydantic-docs-native-tools] The capture gives no per-parameter provider matrix, because there is only one native provider.

## Code execution

| Provider | Supported | What to know |
| --- | --- | --- |
| OpenAI Responses | ✅ | Requires `openai_include_code_execution_outputs` for the output to appear on the return part |
| Google | ✅ | Subject to the Gemini 3-versus-earlier combination rules |
| Anthropic | ✅ | On compatible models, with a compatible tool version chosen automatically. Raises `UserError` on the Bedrock clients (`AsyncAnthropicBedrock`, `AsyncAnthropicBedrockMantle`) |
| xAI | ✅ | Full support |
| Bedrock | ✅ | Nova 2.0 models only |
| Groq, OpenAI Chat, Mistral, Cohere, HuggingFace | ❌ | Chat Completions has no code execution; use the Responses model |

Anthropic's version-selection override, its server-side sandbox and its container lifecycle are compiled in [Anthropic server-side tools](anthropic-server-side-tools.md)[^pydantic-docs-native-tools]

### Images out of code execution

On OpenAI, code that draws produces images, which arrive on `ModelResponse.images` as `BinaryImage` objects and can serve as the run's image output with `output_type=BinaryImage`[^pydantic-docs-native-tools] Both reading the image and using it as output need `openai_include_code_execution_outputs=True` — without the setting the image is not available, not merely unrendered[^pydantic-docs-native-tools]

### Files in the container

A file reaches a provider's code execution container through the provider's own Files API, then into the tool as a `UploadedFile` reference[^pydantic-docs-native-tools] Uploads are provider calls you make yourself — Anthropic's beta files endpoint with `betas=['files-api-2025-04-14']`, OpenAI's `files.create(..., purpose='assistants')` — and the tool only carries the resulting id[^pydantic-docs-native-tools]

| Parameter | Anthropic | OpenAI | Google | xAI |
| --- | --- | --- | --- | --- |
| `files` | ✅ | ✅ | ❌ | ❌ |

A file whose `UploadedFile.provider_name` does not match the model provider is **ignored**, not rejected[^pydantic-docs-native-tools] That is the failure mode to watch: a container-backed analysis run against the wrong provider sees no file and no error, and the model answers about data it never had.

## Image generation

| Provider | Supported | What to know |
| --- | --- | --- |
| OpenAI Responses | ✅ | Full support, and **only models newer than GPT-5.2**. Metadata such as the `revised_prompt` sent to the image model appears on the return part |
| Google | ✅ | Limited parameters, and only on image-generation models such as `gemini-3.1-flash-image` |
| Anthropic, xAI, Groq, Bedrock, Mistral, Cohere, HuggingFace | ❌ | — |

Two asymmetries are worth stating plainly. Google's image models do not support function tools at all, and they always retain the option of generating an image even when `ImageGenerationTool` is not specified — so on those models the tool is a configuration surface, not a switch[^pydantic-docs-native-tools] And on OpenAI, `provider_settings.openai.model` chooses the *image* model underneath without changing the agent's conversational model[^pydantic-docs-native-tools]

Generated images land on `ModelResponse.images` as `BinaryImage`; pairing the tool with `output_type=BinaryImage` also enables the tool automatically when it was not named[^pydantic-docs-native-tools] That auto-enable is the same behaviour the direct and subagent routes are compared against in [Pydantic AI image generation](pydantic-ai-image-generation.md)[^pydantic-docs-native-tools]

### Parameters and geometry

| Parameter | OpenAI | Google |
| --- | --- | --- |
| `provider_settings.openai.action` | ✅ — `'auto'` (default), `'generate'`, `'edit'` | ❌ |
| `provider_settings.openai.background` | ✅ | ❌ |
| `provider_settings.openai.input_fidelity` | ✅ | ❌ |
| `provider_settings.openai.moderation` | ✅ | ❌ |
| `provider_settings.openai.model` | ✅ — an OpenAI image model id | ❌ |
| `provider_settings.openai.partial_images` | ✅ | ❌ |
| `provider_settings.openai.quality` | ✅, but `gpt-image-2` and earlier reject `xhigh` and `max` | ❌ |
| `output_compression` | ✅ default 100, JPEG or WebP only | ✅ default 75, JPEG only, Google Cloud only |
| `output_format` | ✅ | Google Cloud only |
| `size` | ✅ `'auto'` (default), `1024x1024`, `1024x1536`, `1536x1024` | ✅ `512`, `1K` (default), `2K`, `4K` |
| `aspect_ratio` | ✅ `1:1`, `2:3`, `3:2` | ✅ `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |

OpenAI exposes only discrete sizes, so Pydantic AI maps the ratio: `'1:1'` → `1024x1024`, `'2:3'` → `1024x1536`, `'3:2'` → `1536x1024`[^pydantic-docs-native-tools] Any other ratio is an error, and if `size` is also set it must equal the computed value[^pydantic-docs-native-tools] `action='auto'` lets the model decide between generating and editing an image already in context[^pydantic-docs-native-tools]

On Gemini image models the ratio and resolution controls need the tool named explicitly: omit `ImageGenerationTool` and the model still draws, but `aspect_ratio` and `size` have nowhere to go[^pydantic-docs-native-tools] `size` as a resolution control is stated for Gemini 3 Pro Image and later[^pydantic-docs-native-tools]

## Web fetch

| Provider | Supported | What to know |
| --- | --- | --- |
| Anthropic | ✅ | Full support; wraps Anthropic's own web fetch tool, whose caller and citation behaviour is compiled in [Anthropic server-side tools](anthropic-server-side-tools.md) |
| Google | ✅ | **No parameters**, and fixed limits: 20 URLs per request, 34 MB maximum per URL |
| xAI | ❌ | Browsing happens inside `WebSearchTool` instead |
| OpenAI, Groq, Bedrock, Mistral, Cohere, HuggingFace | ❌ | — |

| Parameter | Anthropic | Google |
| --- | --- | --- |
| `max_uses` | ✅ | ❌ |
| `allowed_domains` | ✅ | ❌ |
| `blocked_domains` | ✅ | ❌ |
| `provider_settings.anthropic.enable_citations` | ✅ | ❌ |
| `provider_settings.anthropic.max_content_tokens` | ✅ | ❌ |
| `provider_settings.anthropic.use_cache` | ✅ | ❌ |
| `provider_settings.anthropic.response_inclusion` | ✅ | ❌ |

Since Google honours none of the restricting three, combining a domain filter or a use cap with the Google route leaves the local fallback, `optional=True` omission or a `UserError` — and never a silently unfiltered fetch[^pydantic-docs-native-tools] The 34 MB per-URL ceiling is Google's, applied without a local pre-check, so an oversized page is discovered as a provider failure rather than a validated argument[^pydantic-docs-native-tools]

## Memory

`MemoryTool` is Anthropic-only, and it is not a memory store: it declares the native tool, and **you** supply a tool named `memory` that implements the sub-commands[^pydantic-docs-native-tools] Anthropic's SDK provides `BetaAbstractMemoryTool` to subclass — the sample returns canned strings and the `LocalFilesystemMemoryTool` example is the starting point for a real one — and the agent's side is a `@agent.tool_plain` function forwarding `**command` to `fake_memory.call(command)`[^pydantic-docs-native-tools]

The consequence is that `MemoryTool()` alone gives the model nothing to call: without the matching `memory` function tool the model has no implementation behind the native declaration. Storage, durability and concurrency are entirely yours. This is a different thing from [Pydantic AI Harness memory](pydantic-ai-harness-memory.md), which owns a notebook, a store and a prompt budget rather than a provider-side tool.

## Advisor

`AdvisorTool` is supported by Anthropic — on the Claude API and Claude Platform on AWS, but not on Amazon Bedrock — and by OpenRouter with any executor model[^pydantic-docs-native-tools]

| Parameter | Anthropic | OpenRouter |
| --- | --- | --- |
| `model` | ✅ required | ✅ required, an OpenRouter catalog slug such as `anthropic/claude-opus-4.8` |
| `max_uses` | ✅ cap per request | ❌ fixed gateway limit, ignored |
| `max_tokens` | ✅ minimum 1024; the result then carries a `stop_reason` | ✅ maps to `max_completion_tokens` |
| `provider_settings.anthropic.caching` | ✅ `'5m'` or `'1h'` | ❌ no equivalent |
| `provider_settings.openrouter.forward_transcript` | ❌ | ✅ |

On OpenRouter the advisor sees only the prompt from the tool call unless `forward_transcript` is set[^pydantic-docs-native-tools] Aggregate consultation counts are surfaced under `ModelResponse.provider_details['server_tool_use']`[^pydantic-docs-native-tools] With Anthropic, Pydantic AI keeps both plaintext and encrypted advisor results in message history and strips advisor blocks once the tool is no longer enabled, streaming pauses while a consultation runs, and advisor usage is reported under `advisor_*` keys in `RequestUsage.details` but **excluded** from the executor's top-level token totals[^pydantic-docs-native-tools]

The capability that builds this tool, `Advisor`, and its local fallback are compiled in [Pydantic AI Harness advisor](pydantic-ai-harness-advisor.md)[^pydantic-docs-native-tools]

## MCP servers

`MCPServerTool` hands an MCP server to the provider: the server must live at a public URL the provider can reach, and the route supports far less than the agent-side [MCP client](pydantic-ai-mcp-client.md)[^pydantic-docs-native-tools] What it buys instead is optimised context use and caching and no round trip back to your process[^pydantic-docs-native-tools]

| Provider | Supported | What to know |
| --- | --- | --- |
| OpenAI Responses | ✅ | OpenAI connectors work by passing a special `x-openai-connector:<connector_id>` URL |
| Anthropic | ✅ | Full support |
| xAI | ✅ | Full support |
| Google, Groq, OpenAI Chat, Bedrock, Mistral, Cohere, HuggingFace | ❌ | — |

| Parameter | OpenAI | Anthropic | xAI |
| --- | --- | --- | --- |
| `authorization_token` | ✅ | ✅ | ✅ |
| `allowed_tools` | ✅ | ✅ | ✅ |
| `description` | ✅ | ❌ | ✅ |
| `headers` | ✅ | ❌ | ✅ |

`id` and `url` are the required pair[^pydantic-docs-native-tools] The `description` and `headers` gaps on Anthropic mean a server that needs a custom header cannot be reached natively there — the local path is the alternative. The three-layer choice between this tool, `MCPToolset` and the `MCP` capability is compiled in [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md)[^pydantic-docs-native-tools]

## File search

`FileSearchTool` is a fully managed RAG path: the provider stores the files, chunks them, embeds them and injects the retrieved context into the prompt[^pydantic-docs-native-tools]

| Provider | Supported | What to know |
| --- | --- | --- |
| OpenAI Responses | ✅ | Files must be uploaded into vector stores through the OpenAI Files API; `openai_include_file_search_results` puts results on the return part |
| Google (Gemini API) | ✅ | Files uploaded through the Gemini Files API are **deleted after 48 hours**; up to 2 GB per file and 20 GB per project |
| xAI | ✅ | Mapped to xAI collections search; requires collection IDs; `xai_include_collections_search_output` puts results on the return part |
| Google Cloud, Anthropic, Groq, OpenAI Chat, Bedrock, Mistral, Cohere, HuggingFace | ❌ | Google Cloud is unsupported, and so are Google routes through the Pydantic AI Gateway |

The Gemini retention rule is the operational fact to plan around: a store built once does not survive two days, so a scheduled agent must re-upload rather than reuse[^pydantic-docs-native-tools]

`max_num_results` caps a search. OpenAI Responses sends it as `max_num_results` and accepts 1 to 50; xAI sends it as the collections `limit`; without it each provider applies its own default[^pydantic-docs-native-tools] xAI adds two options under `provider_settings.xai` — `instructions` and `retrieval_mode` — and defaults to 10 results over hybrid retrieval when they are omitted[^pydantic-docs-native-tools] The framework ships no chunking, embedding or store-management API here: each provider's own client does the upload, as the OpenAI vector-store and Gemini file-search-store samples show[^pydantic-docs-native-tools] Building that pipeline yourself is the alternative compiled in [RAG retrieval pipeline design](rag-retrieval-pipeline.md).

## Limits

- The capture names **no Pydantic AI version, author, publication date or licence**, so every matrix cell, default and parameter name here is version-unknown; the page is `draft` under the `pydantic-ai` domain rule with a `stale_after`, and every claim is **Reported** — nothing was installed, uploaded, generated, executed, fetched or searched[^pydantic-docs-native-tools]
- The matrices are the vendor's prose and tables, not generated from capability profiles; nothing cross-checks a row against the provider's own API, and the OpenRouter web-search row is explicitly marked as parameter-name verification only.
- Coverage: `raw/tools-toolsets/native-tools/` holds that one `index.md` capture, with no attachments, includes, downloads or supporting files; every external link — the nine `native_tools` API anchors, the Anthropic/OpenAI/Google/xAI/OpenRouter tool documentation, the Files API pages, the DeepWiki and GitHub MCP servers and the OpenAI connector guide — was read as a link, not followed.
- Model names in the samples (`claude-sonnet-5-5`, `claude-opus-5-5`, `gpt-6.1-sol`, `gemini-3.8-flash`, `gemini-3.1-flash-image`, `grok-4.7`, `gpt-image-2.5-flare`) are unpinned aliases that no release-pinned capture here corroborates.
- The capture states no price for any tool. Web-search counts reach `RunUsage.cost` but the per-search price and Google's free grounding allowance are not given, and no advisor, file-search or image-generation price appears at all.
- What an unsupported-provider request does at the wire — whether the tool is omitted from the request or the request fails — is described only through the capability-level fallback rules, and no provider error text is quoted.

## Relationships

- **Depends on** the layer compiled in [Pydantic AI native tools](pydantic-ai-native-tools.md) for how these tools are attached, how `provider_settings` is keyed and what a restricting parameter does.
- **Configures** the same tools whose internals are owned by [Anthropic server-side tools](anthropic-server-side-tools.md), [Pydantic AI image generation](pydantic-ai-image-generation.md), [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md) and [Pydantic AI Harness advisor](pydantic-ai-harness-advisor.md); this page adds the cross-provider comparison those pages do not make.
- **Supplies the native side of** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md): the support matrices here decide when a provider-adaptive capability reaches its native half or takes the local one.
- **Is the provider-managed alternative to** [RAG retrieval pipeline design](rag-retrieval-pipeline.md): `FileSearchTool` buys chunking, embedding and retrieval from the provider, and the trade is a 48-hour Gemini retention window and a per-provider store API.
- **Diverges from** [Pydantic AI Harness memory](pydantic-ai-harness-memory.md): `MemoryTool` is a provider-side tool whose implementation you write, while the Harness capability owns the store, the prompt budget and the write receipts.
- **Bills through** the usage accounting compiled in [Pydantic AI models and providers](pydantic-ai-models-and-providers.md): the per-tool keys land in `RequestUsage.details`, which is what cost reporting and [prompt-cache health](pydantic-ai-prompt-cache-health.md) read.

[^pydantic-docs-native-tools]: Pydantic Docs, "Native Tools" (<https://pydantic.dev/docs/ai/tools-toolsets/native-tools/>, `domain: pydantic.dev`, `language: en`, 4,976 words as declared and 5,692 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/native-tools/index.md`, 1,148 lines, content digest sha256:937d5ddc. §"Web Search Tool" (raw lines 88–203) for the provider table, the OpenAI Responses-only and `openai_include_web_search_sources` rules, the Google no-parameter and `sources`-key exceptions, xAI's three parameters, Groq's compound models, the OpenRouter Beta server tool with its recorded-verification caveat, the per-provider usage paragraphs and their billing units, the parameter matrix with the `max_uses` footnote, the `WebSearchUserLocation` fields and the Anthropic either-or domain rule, and the restricting-parameter resolution; §"X Search Tool" (204–259) for the xAI-only support, the `XSearch` fallback-subagent route and the parameter list; §"Code Execution Tool" (261–280) for the provider table, the Anthropic Bedrock `UserError`, the Nova 2.0 rule and `openai_include_code_execution_outputs`; its §"Usage" (280–346) for `ModelResponse.images`, `BinaryImage` and image output; §"File Uploads" (347–421) for the Files API uploads, the `UploadedFile` reference, the `provider_name`-mismatch ignore rule and the `files` matrix; §"Image Generation Tool" (423–600) for the provider table, the newer-than-GPT-5.2 rule, `revised_prompt`, the Google function-tool and always-available-image rules, `ModelResponse.images`, the auto-enable with `output_type=BinaryImage`, the `aspect_ratio`-to-`size` mapping and its error cases, the `action` default and the image-model setting, the Google ratio and resolution controls, and the parameter matrix; §"Web Fetch Tool" (602–685) for the provider table, Google's 20-URL and 34 MB limits, the xAI-scope note, the parameter matrix and the no-parameter Google rule; §"Memory Tool" (687–769) for the Anthropic-only support, the required `memory` tool, `BetaAbstractMemoryTool` and the forwarding sample; §"Advisor Tool" (771–819) for the provider table, the OpenRouter executor and transcript-default rules, `server_tool_use`, the Anthropic history, streaming and `advisor_*` accounting rules, and the parameter matrix; §"MCP Server Tool" (821–978) for the public-URL requirement, the reduced feature set, the context-and-caching rationale, the provider table with OpenAI connectors, the parameter matrix and the required `id`/`url` pair; §"File Search Tool" (980–1140) for the provider table, the vector-store and file-search-store uploads, the Gemini 48-hour deletion and 2 GB/20 GB limits, the Google Cloud and Gateway exclusion, `max_num_results` and its OpenAI 1–50 and xAI `limit` forms, the `xai_include_collections_search_output` setting, and the xAI `instructions`/`retrieval_mode` defaults. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.
