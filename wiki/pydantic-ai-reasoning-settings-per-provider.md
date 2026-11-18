---
type: Concept
title: Pydantic AI reasoning settings per provider
description: Provider-native thinking settings behind Pydantic AI's unified switch — Anthropic budgets, adaptive and interleaved thinking, OpenAI reasoning summaries and ids, Groq's three reasoning formats, and each provider's preservation and off-switch rules.
tags: [ml, pydantic-ai, thinking, model-settings]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:20:00Z }
sources:
  - id: pydantic-thinking-docs-2026
    resource: ../raw/capabilities/thinking/index.md
    scope: ../raw/capabilities/thinking/
    kind: documentation
    revision: sha256:d7e5d288fa00c8a2628fcf1b0afb94d6a8a70fe2a6e0fa2f163ef59d5550b99b
    title: "Thinking"
---

The [unified `thinking` setting](pydantic-ai-thinking.md) covers the common case, and each provider still exposes its own control for the cases it does not: pinning a token budget, enabling interleaved thinking, choosing a reasoning format, or preserving reasoning across turns[^pydantic-thinking-docs-2026]. These provider-specific settings take precedence over the unified value, so reaching for one is how you escape the translation table — with the documented exception that `thinking=False` still disables reasoning on Cerebras and Groq's qwen3 models[^pydantic-thinking-docs-2026].

## OpenAI

Two channels behave differently[^pydantic-thinking-docs-2026]:

- **Chat Completions.** `OpenAIChatModel` converts text inside `<think>` tags into `ThinkingPart`s, with the tag shape set by the model profile's `thinking_tags` field. An OpenAI-compatible provider that returns reasoning in its own field rather than in tags is handled automatically through the `<provider>:<model>` shorthand, and the field name can be set with `openai_chat_thinking_field`. Providers that want their reasoning fields returned unchanged — for caching or interleaved thinking — are served by `openai_chat_send_back_thinking_parts`.
- **Responses.** `OpenAIResponsesModel` generates native thinking parts once `openai_reasoning_effort` and `openai_reasoning_summary` are set in model settings. The `pro` reasoning mode is a third control: independent of effort, never set by the unified `thinking` setting, and reachable only through `openai_reasoning_mode`.

Responses sends the unique ids of reasoning, text and function-call parts from history by default, which raises an error such as `Item 'rs_123' of type 'reasoning' was provided without its required following item.` when the history being sent does not match exactly what the API returned — the common cause being a history processor that rebuilt it[^pydantic-thinking-docs-2026]. `openai_send_reasoning_ids=False` turns that off, at the cost of the model no longer seeing those ids.

## Anthropic

The native setting is `anthropic_thinking`, declared as `{'type': 'enabled', 'budget_tokens': 1024}` for extended thinking[^pydantic-thinking-docs-2026]. The budget arithmetic is a hard constraint rather than guidance: the budget counts toward `max_tokens`, which Anthropic requires to be greater than the budget, and when `max_tokens` is unset Pydantic AI raises its own default as needed to leave at least 4,096 tokens beyond the budget[^pydantic-thinking-docs-2026].

Thinking tokens are reported twice on this provider — as `output_reasoning_tokens` on the usage and as `RunUsage.details['thinking_tokens']` — billed inside `output_tokens`, with the detail key omitted entirely when a response used no thinking tokens[^pydantic-thinking-docs-2026].

### Carried-over thinking

Reasoning that cannot ride Anthropic's native channel — because the signature did not survive storage, a history processor rebuilt the part, or the part came from another canonical system — is sent as text, but not from the turn it was produced in[^pydantic-thinking-docs-2026]. Claude's own reasoning takes this path whenever its signature was lost, which the docs call the common case for a history round-tripped through your own storage[^pydantic-thinking-docs-2026]. This is the exception the cross-provider history rule in [thinking and reasoning control](pydantic-ai-thinking.md) points to.

### Interleaved thinking

Interleaved thinking needs the beta header in the model settings alongside a thinking budget — `extra_headers={'anthropic-beta': 'interleaved-thinking-2025-05-14'}` with `anthropic_thinking={'type': 'enabled', 'budget_tokens': 10000}`[^pydantic-thinking-docs-2026]. Adaptive thinking enables it automatically, so the header is the manual switch for budget-based thinking[^pydantic-thinking-docs-2026].

### Adaptive thinking and effort

From `claude-opus-4-6` onward, Anthropic's adaptive thinking lets the model decide when and how much to think per request, and it replaces extended thinking: `type: 'enabled'` with `budget_tokens` is deprecated on Opus 4.6 and removed on Opus 4.7, 4.8, 5 and 5.5, Sonnet 5 and 5.5, and Haiku 5.5[^pydantic-thinking-docs-2026]. The adaptive shape is `{'type': 'adaptive'}` with effort carried separately by `anthropic_effort`, which the docs describe as controlling how much effort the model puts into its response, independent of thinking[^pydantic-thinking-docs-2026].

Three consequences matter operationally[^pydantic-thinking-docs-2026]:

- **The newest Claude models think without any setting.** Opus 5 and later, Sonnet 5, Haiku 5.5, and the Fable and Mythos models think adaptively by default. `thinking=False` turns it off on Opus 5, Sonnet 5 and Haiku 5.5, and sends `between_tools` on Sonnet 5.5; Opus 5.5, Fable and Mythos cannot turn thinking off and drop to the lowest effort instead, while Mythos Preview, which has no effort setting, keeps its default.
- **A forced tool choice stops Claude from thinking.** An agent with a structured `output_type` therefore uses Native Output rather than Tool Output on these models unless thinking is off.
- **Thinking tokens count against Anthropic's loop-wide task budgets,** so adaptive thinking scales down as the budget depletes.

## Google

The native route is `google_thinking_config`, carrying `include_thoughts` and `thinking_level` (a `ThinkingLevel` value such as `MEDIUM`); the framing, the accepted levels and the per-model differences are compiled in [Google thinking levels](google-thinking-levels.md), the Google setup page this docs page defers to[^pydantic-thinking-docs-2026]. The unified mapping — Gemini 3+/Gemma 4 levels versus Gemini 2.5 budgets — is in [thinking and reasoning control](pydantic-ai-thinking.md).

## xAI

Grok reasoning models produce native thinking, and preserving it across turns is opt-in: `XaiModelSettings.xai_include_encrypted_content=True`[^pydantic-thinking-docs-2026]. Without it, multi-turn reasoning content does not come back.

## Bedrock

For Claude Sonnet 4.6+, Opus 4.6+ and Haiku 5.5, the unified `thinking` setting already emits AWS's required adaptive-thinking shape, so no Bedrock-specific setting is needed[^pydantic-thinking-docs-2026]. Older Claude models, or a pinned `budget_tokens`, go through `bedrock_additional_model_requests_fields` — for example `{'thinking': {'type': 'enabled', 'budget_tokens': 1024}}` on `BedrockConverseModel`[^pydantic-thinking-docs-2026]. Claude served through Bedrock inherits the Anthropic model profile, so carried-over thinking behaves as it does on the direct API[^pydantic-thinking-docs-2026].

## Groq

Groq returns reasoning in three formats, and the choice is visible in the message history[^pydantic-thinking-docs-2026]:

| `groq_reasoning_format` | What arrives |
| --- | --- |
| `'raw'` | Thinking text inside `<think>` tags, converted automatically to `ThinkingPart`s |
| `'hidden'` | No thinking text in the content at all |
| `'parsed'` | A structured reasoning part in the response, converted to a `ThinkingPart` |

The unified `thinking` setting selects `'parsed'`, and for the gpt-oss family its level also drives Groq's `reasoning_effort` (`'minimal'`/`'low'` → `'low'`, `'medium'` → `'medium'`, `'high'`/`'xhigh'`/`'max'` → `'high'`, `True` → `'medium'`)[^pydantic-thinking-docs-2026]. `groq_reasoning_format` and `groq_reasoning_effort` are the finer controls, and the explicit effort takes precedence over the unified mapping[^pydantic-thinking-docs-2026].

## OpenRouter

`openrouter_reasoning` takes the router's own reasoning object — `{'effort': 'high'}` in the sample — for direct control where the unified mapping's route-dependent lowering is not what you want[^pydantic-thinking-docs-2026].

## Z.AI

The unified `thinking` setting is the entry point on Z.AI; preserving thinking content across multi-turn conversations additionally needs `ZaiModelSettings.zai_clear_thinking=False`, because the default clears it[^pydantic-thinking-docs-2026].

## GitHub Copilot

Copilot inherits the unified `thinking` setting as `reasoning_effort` from `OpenAIChatModel` and adds no gate of its own, so whether an id accepts a level, and which levels, is a per-model fact Copilot reports in its own catalogue and enforces itself — an unsupported level comes back as `400 invalid_reasoning_effort`[^pydantic-thinking-docs-2026]. Its Anthropic and Google ids return reasoning in a non-standard `reasoning_text` field, which Pydantic AI maps to a `ThinkingPart` and sends back in the same field; its OpenAI and Moonshot ids accept the setting and reason but return no reasoning text, so they yield no thinking part at all[^pydantic-thinking-docs-2026]. The Anthropic ids also think adaptively, making effort a ceiling rather than an instruction — an easy question can come back with no reasoning — and their effort list has no `none`, so `thinking=False` fails with the `400` above[^pydantic-thinking-docs-2026].

## Snowflake Cortex

Claude models on Cortex take `snowflake_reasoning={'max_tokens': 4096}` for the reasoning budget, or the unified `thinking` setting; OpenAI models take the unified setting or `openai_reasoning_effort`[^pydantic-thinking-docs-2026]. Claude requires `temperature` to be exactly 1 while thinking, and Cortex's own default differs, so `SnowflakeModel` sets `temperature=1` automatically when reasoning is enabled and no temperature was set explicitly[^pydantic-thinking-docs-2026]. Other model families ignore `thinking`[^pydantic-thinking-docs-2026].

## Mistral

Mistral deprecated the `magistral` family in favour of adjustable-reasoning models: `magistral-medium-latest` and `magistral-small-latest` now point at Medium 3.5 and Small 4 and reason only when asked, while dated `magistral` ids always reasoned and accept no reasoning setting, so `thinking` sends nothing for them[^pydantic-thinking-docs-2026]. The adjustable families are the Large 4, Small 4 and Medium 3.5 families, and the split is narrow: Small 4 and Medium 3.5 accept only `'high'` and `'none'`; Large 4 accepts `'low'`, `'medium'` and `'high'` and cannot turn reasoning off[^pydantic-thinking-docs-2026]. Older `mistral-small-*`/`mistral-medium-*` snapshots and `mistral-large-latest` do not support reasoning and silently ignore `thinking`[^pydantic-thinking-docs-2026]. The capability is native-provider only: OpenAI-compatible hosts such as LiteLLM or Azure ignore it, with OpenRouter the exception because it maps the unified setting onto its own `reasoning` parameter for any model it routes[^pydantic-thinking-docs-2026].

## Cohere

`command-a-reasoning-08-2025` thinks by default and takes Cohere's `thinking` parameter, where `thinking=False` sends `type='disabled'` and an effort level caps the budget (512, 2,048, 8,192, 16,384 and 31,000 tokens for the levels in ascending order)[^pydantic-thinking-docs-2026]. When the model returns a `tool_plan`, the plan it writes before its tool calls, `CohereModel` keeps it as a `ThinkingPart` with `provider_details={'tool_plan': True}` and sends it back to Cohere as `tool_plan` beside those calls — a tool-specific reasoning artefact rather than free-form thinking[^pydantic-thinking-docs-2026].

## Hugging Face

Text inside `<think>` tags becomes a `ThinkingPart`, reasoning returned in a separate `reasoning` field by an inference provider also becomes one, and both kinds are sent back inside thinking tags on later requests[^pydantic-thinking-docs-2026]. The tags are configurable through the profile's `thinking_tags` field, the same seam OpenAI-compatible providers use[^pydantic-thinking-docs-2026].

## Limits

- One vendor reference page with no publication date, author or Pydantic AI version; every setting name and constraint is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-thinking-docs-2026].
- The per-provider sections are prose plus runnable-looking samples, not schemas: no accepted-value list per model, no error taxonomy beyond Copilot's `400 invalid_reasoning_effort`, and no default value for most settings is stated.
- Model names (`claude-opus-4-8`, `gemini-3.5-flash`, `grok-4.3`, `glm-5`, `openai/gpt-oss-120b`) are the vendor's samples; nothing here corroborates them, and the Google and Bedrock details are deferred to pages this ingest did not read.
- Nothing was installed, constructed or called — no budget set, no beta header sent, no reasoning format observed, no `tool_plan` returned — so every claim is **Reported**.

## Relationships

- **Details** the provider rows of [thinking and reasoning control](pydantic-ai-thinking.md), which owns the unified vocabulary and the translation table.
- **Overrides** that unified setting, per its documented precedence.
- **Extends** [models and providers](pydantic-ai-models-and-providers.md), whose per-model profile and settings classes carry these fields.
- **Feeds** [reasoning effort changes](pydantic-ai-reasoning-effort-changes.md), where a provider-specific effort setting is one of the cases that forces a request-level change instead of a mid-conversation delta.
- **Depends on** [prompt caching](pydantic-ai-prompt-caching.md) indirectly: reasoning sent back in a provider's native channel keeps the prefix stable, while the text fallback for a lost credential changes it.
- **Interacts with** [structured output](pydantic-ai-structured-output.md) on Anthropic, where thinking and a forced tool choice are mutually exclusive.

[^pydantic-thinking-docs-2026]: Pydantic Docs, "Thinking", <https://pydantic.dev/docs/ai/capabilities/thinking/>, 4,279 words as declared and 4,325 by local `wc -w`, no publication date, author or Pydantic AI version named; local capture `raw/capabilities/thinking/index.md`, content digest sha256:d7e5d288. §"Unified thinking settings" (raw lines 15–45, cited for the precedence rule and the Cerebras/Groq exceptions); §"OpenAI" (127–155) for `<think>` conversion, `thinking_tags`, `openai_chat_thinking_field`, `openai_chat_send_back_thinking_parts`, `openai_reasoning_effort`/`openai_reasoning_summary`, `pro` reasoning mode, the `rs_123` error and `openai_send_reasoning_ids`; §"Anthropic" (156–225) for `anthropic_thinking`, the `max_tokens`/budget rule and the 4,096-token default, `output_reasoning_tokens` and `RunUsage.details['thinking_tokens']`, carried-over thinking, the interleaved beta header, adaptive thinking and its model list, `anthropic_effort`, the default-thinking models, the `between_tools` and lowest-effort off-switches, forced tool choice versus Native Output, and task budgets; §"Google" (226–245); §"xAI" (246–261) for `xai_include_encrypted_content`; §"Bedrock" (262–289) for the adaptive passthrough and `bedrock_additional_model_requests_fields`; §"Groq" (290–313) for the three formats and the two explicit settings; §"OpenRouter" (314–329); §"Z.AI" (330–345) for `zai_clear_thinking`; §"GitHub Copilot" (346–351) for the no-gate rule, `reasoning_text`, the ceiling behaviour and the `400`; §"Snowflake Cortex" (352–371) for `snowflake_reasoning` and the automatic `temperature=1`; §"Mistral" (372–377) for the deprecation, the two model groups and the provider restriction; §"Cohere" (378–383) for the budget levels and `tool_plan`; §"Hugging Face" (384–386) for the tags and `reasoning` field. Evidence class: **Reported** — vendor documentation; no provider was configured or called.
