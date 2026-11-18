---
type: Concept
title: Pydantic AI tool choice
description: How tool_choice decides which tools a Pydantic AI request may call — the four static forms and ToolOrOutput, forcing a named output tool, why 'required' has to come from a capability, the per-provider forcing matrix and profile flags, and which choices break the prompt cache.
tags: [pydantic-ai, agents, tools, prompt-caching]
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

**Reported, Pydantic AI version unspecified:** `tool_choice` in `ModelSettings` decides which tools a request may call, and in Pydantic AI it carries an extra constraint the provider APIs do not state — a choice that would stop the agent from ever finishing is rejected before the request is sent[^pydantic-docs-tools-advanced] That is why `'required'` "has to be set dynamically via a capability": forcing a function tool on every step leaves the model no step on which to produce a final answer[^pydantic-docs-tools-advanced] The setting also has two side effects a build decision should account for: which providers can honour it at all is a property of the *model*, not the vendor, and restricting the tool array can invalidate the provider's prompt cache[^pydantic-docs-tools-advanced]

## Two kinds of tool

Pydantic AI separates **function tools** — registered through `@agent.tool`, toolsets or MCP — from **output tools**, the internal tools used for structured output[^pydantic-docs-tools-advanced] Every option below is defined against that split, and most of the surprising rules come from it[^pydantic-docs-tools-advanced]

## Options

| Value | Effect |
| --- | --- |
| `'auto'` (default) | The model decides; all tools available |
| `'none'` | Function tools disabled; the model may answer in text or with an output tool |
| `'required'` | Force a function tool call. **Excludes output tools**, so a static setting raises at `agent.run()`; use a capability or direct model requests |
| `['tool_a', …]` | Force a call to one of the named function *and/or* output tools. A static list must name an output tool so the run can finish |
| `ToolOrOutput(function_tools=[…])` | Restrict function tools while auto-including all output tools |

A list can also force one specific output tool among several, provided the tools have names: with `output_type=[ToolOutput(Fruit, name='return_fruit'), ToolOutput(Vehicle, name='return_vehicle')]`, `tool_choice=['return_fruit']` forces a `Fruit`[^pydantic-docs-tools-advanced] The three forms then differ precisely:

- `'required'` excludes output tools entirely;
- a named list forces a named tool, and needs an output tool in it to stay runnable;
- `ToolOrOutput` keeps the named function tools and *all* output tools, and still allows text or image output[^pydantic-docs-tools-advanced]

The documented example sets `{'tool_choice': 'none'}` on one run and `ToolOrOutput(function_tools=['get_weather'])` on another[^pydantic-docs-tools-advanced]

## Interaction with deferred tools

A tool hidden by deferred loading is ignored when forcing by name, and an explicit choice raises only when *every* requested tool is hidden; `'required'` raises when every function tool is hidden[^pydantic-docs-tools-advanced] Whether a deferred tool can be forced at all depends on how its definition would reach the model, and the page splits the cases by declaration shape[^pydantic-docs-tools-advanced]

| Shape | Behaviour |
| --- | --- |
| Declared with its schema deferred (a tool-search corpus member on a model with native search) | Pydantic AI sends the `tool_choice` naming it as-is. Anthropic accepts the force where it supports forcing. OpenAI Responses rejects it with a 400 until something reveals the tool — including after the model's own server-executed search — and accepts it after a `ToolReturn.tools` reveal on GPT-5.6 and later, while earlier models keep returning the 400 |
| Withheld until revealed (an on-demand capability's tool, a corpus member on a model without native search, a tool that appears mid-run) | Travels in the `additional_tools` item alone. Nameable on every model unless `openai_previous_response_id` or `openai_conversation_id` is set. GPT-5.6 and later accept the name; on earlier models Pydantic AI declares the tool in `tools` for that request — which misses the prompt cache — and with either stored-response setting the API rejects the name with `Tool choice '<name>' not found in 'tools' parameter.` |

## Setting it dynamically

The static validator is the constraint that shapes the API. `agent.run()` raises a `UserError` when a `'required'` value or an output-tool-free list arrives on the *static baseline* — the `model_settings` argument of `Agent.run`, the agent's own `model_settings`, or the underlying model's defaults — while a static list naming at least one output tool is accepted[^pydantic-docs-tools-advanced]

To vary the choice per step, a capability returns a callable from `get_model_settings`; it receives a `RunContext` with `ctx.messages` and `ctx.run_step`, so it can see what already happened[^pydantic-docs-tools-advanced] The documented `RequireFirstCall` capability forces one tool until a `ToolReturnPart` for it appears in the history, then returns empty `ModelSettings`, and the page notes that capability-supplied settings are resolved per step and therefore not rejected by the baseline validator[^pydantic-docs-tools-advanced] For a single model request with no agent loop, `pydantic_ai.direct.model_request` is the documented alternative[^pydantic-docs-tools-advanced]

## Provider support

`'auto'` and `'none'` work everywhere; the rest differ[^pydantic-docs-tools-advanced]

| Provider | `'required'` | Specific tools | Notes |
| --- | --- | --- | --- |
| OpenAI | ✓ | ✓ | Full support |
| Anthropic | ⚠️ | ⚠️ | Unsupported with extended thinking, and on Claude Opus 5.5, Sonnet 5.5, Fable 5.1/5.2 and Mythos 5.1/5.2; adaptive thinking accepts forcing but answers without thinking |
| Google | ✓ | ✓ | — |
| Bedrock | ✓ | Single only | Multiple tools fall back to `'any'`. Converse has no `'none'`, so `'none'` drops the tools; once the history holds a tool call Converse requires them, so they stay — Claude gets a native `'none'`, other models are not prevented from calling them (issue #10435) |
| Groq / HuggingFace | ✓ | Single only | Multiple tools fall back to `'required'` |
| Mistral | ✓ | ✓ | `'required'` maps to `'any'` |
| Cohere | ✓ | ✓ | `'required'` maps to `'REQUIRED'`; a named subset is applied by trimming the tools array |
| xAI | ✓ | ✓ | — |

With adaptive thinking, Claude answers a forced tool choice with only the tool call and no thinking, so Pydantic AI sends a force it inferred itself as `'auto'` while the request thinks — it forces only what you asked for explicitly[^pydantic-docs-tools-advanced]

The provider table does not cover the OpenAI-compatible family by name: models built on `OpenAIChatModel` — Cerebras, Crusoe, GitHub Copilot, Ollama, OpenRouter, Snowflake, Z.AI and Bedrock Mantle Chat — follow the OpenAI row unless the model profile restricts forcing, with Ollama ignoring `tool_choice` and OpenRouter keeping separate rules for Anthropic models and Qwen3.8 Flash[^pydantic-docs-tools-advanced]

### Forcing is a property of the model

Whether a model can be forced to call a tool lives on its [profile](pydantic-ai-models-and-providers.md) as `supports_forced_tool_choice` and `supports_forced_tool_choice_with_thinking`, so the restriction follows the model across every provider that serves it — Claude Opus 5.5 rejects forcing on OpenRouter just as on the Anthropic API[^pydantic-docs-tools-advanced] Two failure modes follow from that placement[^pydantic-docs-tools-advanced]:

- Where forcing is unavailable, an explicit `'required'` or list raises `UserError`, while forcing Pydantic AI inferred itself — from an output tool, say — falls back to `'auto'`.
- On OpenRouter, explicitly requested thinking on an Anthropic model makes forcing unavailable, because OpenRouter would otherwise silently drop the reasoning; thinking enabled by default does not add the restriction. Other OpenRouter routes that return a 400 for forcing while reasoning — Qwen3.8 Flash — raise a `ModelRequestRejectedError`, which `FallbackModel` falls back on.

## Prompt-cache implications

Most provider APIs cache on the full tools array, so restricting the visible set can cost the cache[^pydantic-docs-tools-advanced] Pydantic AI restricts in two ways, and only one is free[^pydantic-docs-tools-advanced]:

- **API-level filtering (cache-preserving).** The full array is sent and the provider is told to allow a subset: OpenAI Responses and OpenAI Chat through `OpenAIProvider` (`allowed_tools`), Google (`allowed_function_names`), and Bedrock and Mistral when forcing a single tool.
- **Client-side filtering (breaks the cache).** The array is trimmed before the request wherever the API has no native filter for that case.

The cache-breaking cases, per provider[^pydantic-docs-tools-advanced]:

| Provider | When the tool array is trimmed |
| --- | --- |
| Anthropic | A list of multiple tools, or a single tool with extended thinking or on a model that cannot be forced |
| OpenAI Chat | Only where `openai_chat_supports_allowed_tools` is off, as on OpenAI-compatible providers other than `OpenAIProvider`: a multiple-tool list, or a single tool on a non-forceable model. `OpenAIProvider` — including through a custom `base_url` — handles these natively with `allowed_tools`, and a compatible server that rejects or ignores it opts out with `openai_chat_supports_allowed_tools=False` in the profile |
| Bedrock | A multiple-tool list; a single tool with extended thinking or on a non-forceable model; `'none'` while the history has no tool calls |
| Groq / HuggingFace | A multiple-tool list |
| Mistral | A multiple-tool list — the API can force only a single named tool |
| Cohere | Any list — the API accepts no specific tool names |
| xAI | A multiple-tool list, or a single tool on a non-forceable model |
| OpenAI Responses | On models before GPT-5.6, a `tool_choice` (list or `ToolOrOutput`) naming a tool declared only in `additional_tools`, unless a stored-response setting is on — in which case the API rejects the request. `allowed_tools` handles every other case natively |
| Google | Never — `allowed_function_names` covers all cases |

The page's advice is to prefer the providers and cases marked "Never", or `ToolOrOutput` instead of a restrictive list, when cache hits matter[^pydantic-docs-tools-advanced]

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, default and error text here is version-unknown, and its samples pin `openai:gpt-6.1-sol` and `anthropic:claude-sonnet-5-5`, which no other capture here corroborates. Every external link — the `ModelSettings`, `ToolOrOutput`, `ToolOutput`, `Agent.run`, `AbstractCapability.get_model_settings`, `RunContext`, `ModelProfile`, `supports_forced_tool_choice`, `supports_forced_tool_choice_with_thinking`, `ModelRequestRejectedError`, `FallbackModel`, `pydantic_ai.direct` and OpenRouter model pages, issue #10435 and the Bedrock thinking section — was read as a link, not followed. Nothing was installed, no request sent with a `tool_choice`, no provider asked to force a tool, no cache read and no profile inspected, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because model lists, profile flags and the cache matrix move with releases.

## Relationships

- **Constrains** [Pydantic AI tool search](pydantic-ai-tool-search.md): a deferred tool is invisible to a forced choice until revealed, and the reveal mechanism decides whether the force is accepted at all.
- **Costs or preserves** the prefix described in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), which owns the general prefix rule this page's cache table applies to tools.
- **Depends on** [Pydantic AI models and providers](pydantic-ai-models-and-providers.md) for the profile flags that decide forcing, and on [model fallback](pydantic-ai-model-fallback.md) when a rejected force is recovered by re-routing.
- **Is set per step through** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): `get_model_settings` returning a callable is the only supported way to vary `tool_choice` inside a run.
- **Names output tools defined by** [Pydantic AI structured output](pydantic-ai-structured-output.md), which owns `ToolOutput(name=...)` and the output-tool set this setting includes or excludes.
- **Shares its Anthropic limits with** [Anthropic request constraints](anthropic-request-constraints.md), which records the thinking-versus-forced-tool-choice restriction and the models that refuse it.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Tool Choice" (raw lines 419–469) for the function-versus-output split, the five-row options table, the named-output-tool rule, `ToolOrOutput`, the deferred-tool interaction and the example; §"Dynamic tool choice via capabilities" (470–511) for the baseline `UserError`, the `RequireFirstCall` sample and `pydantic_ai.direct.model_request`; §"Provider Support" (512–532) for the provider matrix, adaptive thinking, the `OpenAIChatModel` family, the profile flags, `UserError` versus `'auto'`, OpenRouter's thinking rule and `ModelRequestRejectedError`; §"Prompt caching implications" (533–555) for API-level versus client-side filtering and the cache-breaking table. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
