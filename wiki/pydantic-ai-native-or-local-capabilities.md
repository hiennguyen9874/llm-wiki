---
type: Concept
title: Pydantic AI native-or-local capabilities
description: How Pydantic AI's provider-adaptive tools — WebSearch, WebFetch, ImageGeneration, XSearch and MCP — choose between a provider-native tool and a local implementation, what native= and local= accept, which defaults reverse, and which constraints lock a capability to the native path.
tags: [pydantic-ai, agents, llm-frameworks, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:40:00Z }
stale_after: 2026-12-23
sources:
  - id: pydantic-docs-capabilities-overview
    resource: ../raw/capabilities/overview/index.md
    scope: ../raw/capabilities/overview/
    kind: docs
    revision: sha256:6434ebdb6f8a86b177d4659f738e214d9f719260787ae93cd1bcda3811bd15c
    title: "Capabilities"
  - id: pydantic-docs-common-tools
    resource: ../raw/tools-toolsets/common-tools/index.md
    scope: ../raw/tools-toolsets/common-tools/
    kind: documentation
    revision: sha256:486815f0bf53e56a8207d8ba279e0be48d23940050a72b9fb6a3ec9fc36cf42c
    title: "Common Tools"
---

Five Pydantic AI capabilities — `WebSearch`, `WebFetch`, `ImageGeneration`, `XSearch` and `MCP` — are *provider-adaptive*: each covers one fixed concern across two implementations, a **native** tool the model provider invokes when the model supports it (the work happens on the provider's side, for instance Anthropic's web search running server-side and returning results inline) and a **local** implementation that runs in your Python process for models that do not[^pydantic-docs-capabilities-overview] All five subclass `NativeOrLocalTool`, which can also be used directly or subclassed to build your own provider-adaptive tool. The page names no Pydantic AI version, so the defaults and argument shapes below are version-unknown.

## Which direction each capability defaults to

`WebSearch`, `WebFetch`, `ImageGeneration` and `XSearch` default to **native** and you opt into local with `local=`; `MCP` defaults the other way — it runs the server locally in your process and `native=True` opts into the provider's own MCP connector — because MCP carries credentials[^pydantic-docs-capabilities-overview] That asymmetry is the security-relevant fact on the page: for the four tool capabilities the provider may be the one executing, and only for MCP is the local path the default.

| Capability | Local fallback | Notes |
| --- | --- | --- |
| `WebSearch` | `local='duckduckgo'` or `local=True` (DuckDuckGo) | Requires the `duckduckgo` optional group |
| `WebFetch` | `local=True` (markdownify-based fetch) | Requires the `web-fetch` optional group |
| `ImageGeneration` | Direct model via `local=ImageGenerator(...)` or `fallback_image_model='provider:image-model'`, or a subagent via `fallback_subagent_model=` | The direct routes use the direct image-generation API without a subagent |
| `XSearch` | Subagent via `fallback_subagent_model=` | No default non-xAI fallback: on a non-xAI model you must set `fallback_subagent_model` to an xAI model that supports `XSearchTool` |
| `MCP` | Direct connection to the MCP server, which is the default | Accepts any `MCPToolset` input; transport is auto-detected from a URL |

The image-generation rows are the same route set compiled in [image generation](pydantic-ai-image-generation.md), and the MCP rows are the layer choice compiled in [MCP integration](pydantic-ai-mcp-integration.md).

## What `native=` and `local=` accept

Each side is configured through its own keyword[^pydantic-docs-capabilities-overview]:

| Side | Accepts | Semantics |
| --- | --- | --- |
| `native=` | `True` | The capability's default native tool instance |
| | `False` | Disable the native tool |
| | an explicit instance such as `WebSearchTool(...)` | Fine-grained native configuration |
| | a callable taking `RunContext` | Returns a native tool or `None`, re-resolved per request; `None` omits the native tool for that request |
| `local=` | `True` | The bundled local fallback, on capabilities that have one (`WebSearch`, `WebFetch`) |
| | `False` | Disable the local side |
| | a named strategy string where supported | e.g. `'duckduckgo'` |
| | any callable, `Tool`, or `AbstractToolset` | Your own implementation |
| | an `ImageGenerator` | On `ImageGeneration` only |

Optional installs are opt-in: asking for a local strategy whose extra is not installed raises a `UserError` at *construction* time with an install hint, rather than failing on first use[^pydantic-docs-capabilities-overview]

## Constraints can lock the native path

Some constraint fields require the native tool because the bundled local fallback cannot enforce them, and passing one locks the capability to the native path; if the model does not support the native tool, or its native tool cannot apply the constraint, the capability raises a `UserError`[^pydantic-docs-capabilities-overview] The page's two examples split the cases:

- `WebSearch(max_uses=5)` — limiting searches per run requires native, because the local fallback cannot track a call count.
- `WebFetch(allowed_domains=['example.com'], local=True)` — a domain filter that is still enforced locally when native is unavailable or cannot apply it.

Which constraint fields are native-only is not enumerated on the page; [native tools](pydantic-ai-native-tools.md) names the four restricting fields — `allowed_domains`, `blocked_domains`, `max_uses` and `external_web_access=False` — and resolves an unsupported model differently from this page, a disagreement recorded as a contradiction there.

## Identity, deferral and durability

Because these capabilities contribute model-facing tools, their `id`, `description` and `defer_loading` fields are meaningful: setting `description` and `defer_loading` keeps the tool hidden until the model loads the matching workflow with `load_capability`[^pydantic-docs-capabilities-overview] Each covers a single fixed concern, so `id` already defaults to a stable value — `'web_search'`, `'web_fetch'`, `'image_generation'`, `'x_search'`, and for `MCP` one derived from the server URL — which is the id [durable execution](pydantic-ai-durable-execution.md) registers the contributed toolset under, so durability works unconfigured[^pydantic-docs-capabilities-overview] Set `id` only to rename, and see the custom-capabilities page for the collision behaviour when two capabilities share one.

A `Capability` contributing several toolsets names each `'{capability_id}_{index}'`, and those are the ids durable execution registers them under; the same capability-derived id appears in the durable step naming compiled in [durable tool placement](pydantic-ai-durable-tool-placement.md) and [Pydantic AI on Temporal](pydantic-ai-temporal.md)[^pydantic-docs-capabilities-overview]

## Building your own

`NativeOrLocalTool` is usable directly: the page's sample pairs `CodeExecutionTool()` as the native side with `my_local_executor` as the local side[^pydantic-docs-capabilities-overview] Subclassing it is the documented route to a new provider-adaptive capability; subclassing `AbstractCapability` for the rest of the extension surface is covered in [capability primitive](pydantic-ai-capability-primitive.md).

## Limits

- The source names no Pydantic AI version and no date, so every default, accepted type and error is version-unknown; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-capabilities-overview]
- The page states the two-implementation model and the per-side argument vocabulary but never defines the resolution algorithm: whether native is decided from the model's profile, from provider support, or per request, and what happens when both sides are enabled and the provider rejects the native tool mid-run, are unstated (durability does document the `native=` factory being resolved twice, once on the workflow and once on the worker).
- Only two constraint examples are given; the full set of native-only constraint fields, the exact text of each warning and error, and the `local=` callable's signature are not documented here.
- The optional-extras names are the page's own; no package was installed, so whether the `duckduckgo` and `web-fetch` groups resolve as described is **Reported** only.
- No capability was constructed, no model called and no provider rejected a native tool, so nothing is **Observed** or **Reproduced**.

## Relationships

- **Generalises** the fallback shapes in [image generation](pydantic-ai-image-generation.md) and the layer choice in [MCP integration](pydantic-ai-mcp-integration.md), both of which are instances of the same `native=`/`local=` pair.
- **Implements** the capability primitive's "fall up" pattern — local first, native where available — described in [capability primitive](pydantic-ai-capability-primitive.md).
- **Depends on** the model profile's tool-support flags compiled in [models and providers](pydantic-ai-models-and-providers.md): a capability can only reach the native path where the model supports that tool.
- **Supplies stable toolset ids to** [durable execution](pydantic-ai-durable-execution.md) and its engine pages, which register the contributed toolsets by capability id.
- **Listed with its package attribution in** the [capability catalog](pydantic-ai-capability-catalog.md), where all five are core entries.
- **Supplies the citable results** described in [Pydantic AI citations](pydantic-ai-citations.md): the native web search, web fetch, file search and X search tools on this page are what a provider attaches citation sources to, and `Citations()` is the separate ask that some providers require.
- **Defers into** [capability events](pydantic-ai-capability-events.md): `description` and `defer_loading` are what keep the tool out of the prompt until `load_capability` runs.
- **Configured through** [native tools](pydantic-ai-native-tools.md) and [native tool configuration](pydantic-ai-native-tool-configuration.md), which own what goes inside the `native=` half — the `NativeTool` wrapper, `provider_settings` keyed by model class, and the per-provider support matrices — while this page owns the choice between the halves.
- **Shares the optional install groups with** [Pydantic AI common tools](pydantic-ai-common-tools.md): the `duckduckgo` and `web-fetch` extras the local fallbacks here require are the same groups that page's standalone `duckduckgo_search_tool()` and `web_fetch_tool()` factories install from, and that page's web fetch documents its own SSRF protection and content caps; neither capture states whether the capability's local path delegates to those factories, so the correspondence is unconfirmed[^pydantic-docs-common-tools]

[^pydantic-docs-capabilities-overview]: Pydantic Docs, "Capabilities" (https://pydantic.dev/docs/ai/capabilities/overview/; 4,642 words as declared, 5,228 by local `wc -w`; language `en`; no publication date and no Pydantic AI version). Section used: §"Provider-adaptive tools", including the two-implementation definition, the five-capability list, the local-fallback table with its optional groups, the `native=`/`local=` argument vocabulary, the `UserError` at construction for a missing extra, the `description`/`defer_loading`/`id` rules and their durable-execution use, the native-only constraint fields with the `WebSearch(max_uses=5)` and `WebFetch(allowed_domains=[...])` samples, the `MCP`-defaults-the-other-way rule and the `XSearch` no-default-fallback note, the `'{capability_id}_{index}'` toolset naming, and §"Building your own" for the `NativeOrLocalTool(native=CodeExecutionTool(), local=my_local_executor)` sample. Local capture: `raw/capabilities/overview/index.md`, content digest sha256:6434ebdb. Evidence class: **Reported** — vendor documentation naming no release version; nothing was installed, constructed or called.

[^pydantic-docs-common-tools]: Pydantic Docs, "Common Tools" (https://pydantic.dev/docs/ai/tools-toolsets/common-tools/; `domain: pydantic.dev`; language `en`; 1,167 words as declared, 1,224 by local `wc -w`; no publication date, author, licence or Pydantic AI version). Sections used: §"DuckDuckGo Search Tool" and §"Web Fetch Tool" for the `pydantic-ai-slim[duckduckgo]` and `pydantic-ai-slim[web-fetch]` install lines and the SSRF-protection and `max_content_length`/`max_download_bytes` defaults. Local capture: `raw/tools-toolsets/common-tools/index.md`, content digest sha256:486815f0. Evidence class: **Reported** — nothing was installed or called.
