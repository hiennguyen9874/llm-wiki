---
type: Concept
title: Pydantic AI native tools
description: How a provider-executed native tool is attached and configured in Pydantic AI — the nine `*Tool` classes behind `NativeTool`, the call and return parts with the commentary rule, `provider_settings` keyed by model class, the restricting parameters that can stop a tool being sent, and per-request dynamic selection.
tags: [pydantic-ai, native-tools, tools, agents]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:40:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-native-tools
    resource: ../raw/tools-toolsets/native-tools/index.md
    scope: ../raw/tools-toolsets/native-tools/
    kind: documentation
    revision: sha256:937d5ddc210f169eaf29f261253f91d5d308dc573d5607e6780363ae417e9bd7
    title: "Native Tools"
  - id: pydantic-docs-common-tools
    resource: ../raw/tools-toolsets/common-tools/index.md
    scope: ../raw/tools-toolsets/common-tools/
    kind: documentation
    revision: sha256:486815f0bf53e56a8207d8ba279e0be48d23940050a72b9fb6a3ec9fc36cf42c
    title: "Common Tools"
---

*Native tools* are the tools a model provider supplies and executes, as against *common tools*, which are your own implementations executed by Pydantic AI[^pydantic-docs-native-tools] The difference is who runs the work: a native tool's round trip never comes back to your process, so its call and result appear in the model's response as `NativeToolCallPart` and `NativeToolReturnPart` rather than as a tool call your code answers[^pydantic-docs-native-tools] Pydantic AI wraps nine such tools in one `NativeTool` capability, and everything about configuring them follows from two rules: options that change *what the tool may do* stay on the tool and can stop it being sent to a model that cannot enforce them, while options that merely tune a provider's behaviour live under `provider_settings` and are addressed by **model class**, not by model vendor[^pydantic-docs-native-tools] The capture names no Pydantic AI version and no date, so every class name, field and matrix below is version-unknown.

## The nine tools

| Tool | What the provider does | Providers that support it |
| --- | --- | --- |
| `WebSearchTool` | Searches the web | OpenAI Responses, Anthropic, Google, xAI, Groq (compound models), OpenRouter |
| `XSearchTool` | Searches X/Twitter; xAI only | xAI |
| `CodeExecutionTool` | Runs code in a provider sandbox | OpenAI Responses, Google, Anthropic, xAI, Bedrock (Nova 2.0 only) |
| `ImageGenerationTool` | Generates images | OpenAI Responses, Google |
| `WebFetchTool` | Pulls URL contents into context | Anthropic, Google |
| `MemoryTool` | Uses memory | Anthropic |
| `MCPServerTool` | Calls a remote MCP server, transport handled by the provider | OpenAI Responses, Anthropic, xAI |
| `FileSearchTool` | Managed RAG search over uploaded files | OpenAI Responses, Google (Gemini API), xAI |
| `AdvisorTool` | Consults a stronger model mid-generation | Anthropic, OpenRouter |

The per-tool parameter sets, support-matrix exceptions and usage accounting are compiled in [native tool configuration](pydantic-ai-native-tool-configuration.md); the tools whose behaviour is already owned elsewhere are [Anthropic server-side tools](anthropic-server-side-tools.md) for Claude's web, fetch and code-execution versions, [Pydantic AI image generation](pydantic-ai-image-generation.md) for the image routes, [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md) for the `MCPServerTool` layer, and [Pydantic AI Harness advisor](pydantic-ai-harness-advisor.md) for the capability built on top of `AdvisorTool`[^pydantic-docs-native-tools]

## Attaching one, and what comes back

A native tool goes into the agent's `capabilities` list wrapped in `NativeTool`, and the provider's infrastructure executes it[^pydantic-docs-native-tools] Both directions of the round trip are message parts — `NativeToolCallPart` and `NativeToolReturnPart` — which is what makes a server-side call inspectable in history and renderable in a UI; the return parts are reachable through `ModelResponse.native_tool_calls`[^pydantic-docs-native-tools]

The output rule is the part that surprises. Text a model writes **before** a native tool call is commentary, not output, so it does not become the run's result — *unless* no text follows the last native tool call[^pydantic-docs-native-tools] The exception exists because some providers report a tool after the text it grounds: Google with Gemini 2.5 reports the searches behind an answer after the answer[^pydantic-docs-native-tools] An answer that is followed by a visible search call therefore still counts as the output, and code that reads `result.output` does not have to care which order the provider chose.

## Two configuration layers

Provider-independent options are fields on the tool class itself; anything a provider adds beyond them goes under `provider_settings`, keyed by the model class[^pydantic-docs-native-tools] Both the outer dictionary and each provider's entry are `TypedDict`s, so an IDE completes both levels[^pydantic-docs-native-tools] Each model reads only the options it knows from its own entry, and anything else is **ignored rather than rejected**, matching how model settings behave[^pydantic-docs-native-tools]

The key is the model class you wrote, not the company behind the model[^pydantic-docs-native-tools] That produces three cases worth keeping straight:

| You write | Entry read |
| --- | --- |
| `AnthropicModel(...)` | `anthropic` |
| `OpenRouterModel('anthropic/claude-…')` | `openrouter` — not `anthropic`, although the model is Claude |
| `OpenAIChatModel(base_url='https://openrouter.ai/api/v1')` | neither — the class is OpenAI's even though the endpoint is OpenRouter's |

Which values are legal is the provider API's judgement, not the `TypedDict`'s: the typed dictionary validates shape, the API rejects a value it does not accept[^pydantic-docs-native-tools]

Settings that restrict what a tool may do stay top-level fields rather than moving into `provider_settings`, because a model that cannot apply them must not run the tool without them[^pydantic-docs-native-tools] Keeping the local fallback of a provider-adaptive capability means passing the configured tool to its `native=` argument, as in `WebSearch(native=WebSearchTool(provider_settings={'openrouter': {'engine': 'exa'}}))`[^pydantic-docs-native-tools]

### Deprecated single-provider fields

Some options that only one provider ever used began as top-level fields — `ImageGenerationTool.quality` is the capture's example[^pydantic-docs-native-tools] They still work, but are deprecated and should be set and read under `provider_settings`[^pydantic-docs-native-tools] The trap is that the old field is a separate slot, not a view: `ImageGenerationTool(provider_settings={'openai': {'quality': 'high'}}).quality` still reads the default `'auto'`, so migration must move the *read* as well as the write[^pydantic-docs-native-tools] Setting the same option to different values in both places raises a `UserError`[^pydantic-docs-native-tools]

## Restricting parameters decide whether the tool is sent

Four fields restrict what a tool may do rather than tune its results: `allowed_domains`, `blocked_domains`, `max_uses`, and `external_web_access=False`[^pydantic-docs-native-tools] When one is set and the serving model cannot apply it, Pydantic AI treats the tool as unsupported by that model and resolves it in a fixed order[^pydantic-docs-native-tools]

| Fallback available? | Outcome |
| --- | --- |
| A local implementation is configured | The local fallback runs in the native tool's place |
| The capability is `optional=True` and no local fallback | The tool is left out of the request |
| Neither | A `UserError` naming the settings |

The distinction against the other parameters is the whole point of the separation: an option that only tunes results is silently dropped on a model that does not support it, while one that restricts behaviour can never be dropped — the tool itself goes[^pydantic-docs-native-tools] This is also the enumeration [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md) leaves open when it says which constraint fields are native-only is not listed; see [Contradictions](#contradictions) for the one place the two captures disagree.

## Dynamic configuration

A native tool can be built per request by wrapping a function in `NativeTool`[^pydantic-docs-native-tools] The function takes a `RunContext` and returns an `AbstractNativeTool` or `None`, and `None` omits the tool for that request[^pydantic-docs-native-tools] The capture's sample keys off dependencies — no stored location, no web search at all; a location, a search restricted to that city[^pydantic-docs-native-tools]

The function is called for **each model request**, with `ctx.model` set to the model about to receive it, so a tool can be decided by that model's provider or profile[^pydantic-docs-native-tools] That is what makes it compose with [model fallback](pydantic-ai-model-fallback.md): when `ModelFallback` moves a request to another model, the function runs again with the new model, so each model receives the tool it would have received on its own rather than the tool chosen for the first one[^pydantic-docs-native-tools]

## Google tool combinations

Gemini 3 models support combining native tools with function tools, output tools included, and with `NativeOutput`[^pydantic-docs-native-tools] Earlier Gemini models cannot use those combinations, so structured output alongside a native tool has to go through `PromptedOutput` there[^pydantic-docs-native-tools] The same split shows up per tool: Google's `WebSearchTool` takes no parameters at all, and where Gemini reports which search found which source it does so differently on the Gemini API than on Google Cloud[^pydantic-docs-native-tools]

## Contradictions

The two captures disagree about what a restricting parameter does when the serving model cannot apply it and a local fallback exists.

- **Whether a constraint locks the native path or falls back to local.** [Native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md) reports that passing a constraint field *locks the capability to the native path*, and that an unsupported native tool raises a `UserError`; this capture reports the opposite resolution — the local fallback runs in the native tool's place whenever one is configured, and only the `optional=True` or no-fallback cases reach omission or a `UserError`[^pydantic-docs-native-tools] Neither is chosen here. The tension is real rather than a paraphrase difference, because the two resolutions cannot both hold for `max_uses`: a local DuckDuckGo search cannot enforce a per-run call count, so running it in place of a capped native search would silently discard the cap the caller asked for. Both pages share a publisher and neither names a version, so no revision signal dates one ahead of the other.

## Limits

- The capture names **no Pydantic AI version, author, publication date or licence**, so every class name, field name, deprecation and matrix row here is version-unknown; the page is `draft` under the `pydantic-ai` domain rule with a `stale_after`, and every claim is **Reported** — nothing was installed, no tool attached, no request sent and no provider called[^pydantic-docs-native-tools]
- The nine-tool list is the page's own inventory and is not cross-checked against a package manifest; whether these are all the native tool classes, or all that sit under `NativeTool`, is unstated.
- The `provider_settings` `TypedDict`s are described but not enumerated: only the fields used in samples appear anywhere on the page, so a complete option list per provider has to come from the API reference, which was read as a link and not followed.
- Which value a provider API will accept is left to the API; the page records no validation table, so a rejected option surfaces as a provider error with no local check.
- The capture never states what a `NativeToolCallPart` carries beyond `tool_name`, `args`, `tool_call_id` and provider details in its samples, nor whether native parts are replayed to a different provider on a history round trip.
- `optional=True` is named as a capability field but not defined here; its semantics come from the capability pages compiled elsewhere.

## Relationships

- **Configured per tool in** [native tool configuration](pydantic-ai-native-tool-configuration.md), which holds the per-tool support matrices, parameter tables and usage accounting this page deliberately leaves out.
- **Generalises** [native-or-local capabilities](pydantic-ai-native-or-local-capabilities.md): that page owns the `native=`/`local=` routing, this one owns what is inside the `native=` half and when a native tool is refused outright.
- **Contrasts with** [Pydantic AI common tools](pydantic-ai-common-tools.md), the other side of this page's opening distinction: there, DuckDuckGo search, web fetch and Tavily search are implemented in Pydantic AI, require only an optional install group, and are attached through `Agent(tools=[…])`, so the round trip comes back to your process and the provider needs no support for the tool[^pydantic-docs-common-tools]
- **Supplies the tool layer behind** [Anthropic server-side tools](anthropic-server-side-tools.md), [Pydantic AI image generation](pydantic-ai-image-generation.md), [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md) and [Pydantic AI Harness advisor](pydantic-ai-harness-advisor.md), each of which compiles one tool's internal behaviour rather than the shared contract.
- **Composes with** [Pydantic AI model fallback](pydantic-ai-model-fallback.md): a dynamic `NativeTool` factory is re-evaluated per attempt with the new model as `ctx.model`, and a native tool's failed return can be a fallback trigger.
- **Recorded in history as** the parts described in [Pydantic AI tool kinds and typed parts](pydantic-ai-tool-kinds.md) and [Pydantic AI message history](pydantic-ai-message-history.md), which own part shapes and replay rather than tool configuration.
- **Produces the citable results handled by** [Pydantic AI citations](pydantic-ai-citations.md), since the native search and fetch tools are what a provider attaches citation sources to.
- **Fits the catalog row for** "Native Tool" in [Pydantic AI capability catalog](pydantic-ai-capability-catalog.md), where it is a core capability rather than a Harness one.

[^pydantic-docs-native-tools]: Pydantic Docs, "Native Tools" (<https://pydantic.dev/docs/ai/tools-toolsets/native-tools/>, `domain: pydantic.dev`, `language: en`, 4,976 words as declared and 5,692 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/native-tools/index.md`, 1,148 lines, content digest sha256:937d5ddc. Lines 10–20 for the native-versus-common definition and the nine-tool list with their one-line purposes; line 22 for `NativeTool` in `capabilities` and provider execution; line 24 for `NativeToolCallPart`/`NativeToolReturnPart`, `ModelResponse.native_tool_calls`, and the commentary-unless-nothing-follows rule with the Gemini 2.5 example; lines 26–32 for the two configuration layers, the `TypedDict` pair, the ignored-not-rejected rule, the model-class key with the `OpenRouterModel`/`OpenAIChatModel` cases, provider-API judgement, the restricting-settings-stay-top-level rule, the `WebSearch(native=WebSearchTool(provider_settings=…))` sample, and the deprecated single-provider fields with the `quality` read-back trap and the `UserError` on conflicting values; lines 34–37 for the Google tool-combination rules; lines 39–41 for the parameters Google's web search does not take; §"Dynamic Configuration" (43–86) for the callable form, the `RunContext` signature, the `AbstractNativeTool | None` return, the per-request call with `ctx.model`, the omission-on-`None` rule and the `ModelFallback` re-call; §"Restricting parameters" (200–202) for the four restricting fields and the three-way resolution. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.

[^pydantic-docs-common-tools]: Pydantic Docs, "Common Tools" (https://pydantic.dev/docs/ai/tools-toolsets/common-tools/; `domain: pydantic.dev`; language `en`; 1,167 words as declared and 1,224 by local `wc -w`; no publication date, author, licence or Pydantic AI version). Section used: the page opening, which presents the tools as implemented in Pydantic AI and runnable with any model, beside the three install lines (`pydantic-ai-slim[duckduckgo]`, `[web-fetch]`, `[tavily]`) and the `Agent(…, tools=[duckduckgo_search_tool()])` sample. Local capture: `raw/tools-toolsets/common-tools/index.md`, content digest sha256:486815f0. Evidence class: **Reported** — nothing was installed or called.
