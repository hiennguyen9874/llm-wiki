---
type: Concept
title: Pydantic AI thinking and reasoning control
description: Pydantic AI's unified thinking control — the Thinking capability and thinking model setting, the seven effort values, how each maps onto a provider's native reasoning control, and how reasoning parts and tokens are accounted for.
tags: [ml, pydantic-ai, thinking, model-settings]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:12:00Z }
sources:
  - id: pydantic-thinking-docs-2026
    resource: ../raw/capabilities/thinking/index.md
    scope: ../raw/capabilities/thinking/
    kind: documentation
    revision: sha256:d7e5d288fa00c8a2628fcf1b0afb94d6a8a70fe2a6e0fa2f163ef59d5550b99b
    title: "Thinking"
---

Thinking — the docs also call it reasoning — is the step-by-step work a model does before answering, and Pydantic AI exposes it as one vocabulary rather than a provider matrix: a `Thinking` capability and a `thinking` model setting accept the same values, and the framework translates whichever value you chose into the selected provider's own control[^pydantic-thinking-docs-2026]. The unified route is the default; a provider-specific setting still wins where one is set, so the translation table rather than the unified value is where per-model behaviour is actually decided[^pydantic-thinking-docs-2026].

## Two entry points, one vocabulary

`Thinking` ships in core `pydantic-ai` and attaches to the agent; the bare field sets the same thing without a capability[^pydantic-thinking-docs-2026]:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking

agent = Agent('anthropic:claude-opus-5-5', capabilities=[Thinking(effort='high')])
agent = Agent('anthropic:claude-opus-5-5', model_settings={'thinking': 'high'})
```

| Value | Effect |
| --- | --- |
| `True` | Enable thinking at the provider's default effort level[^pydantic-thinking-docs-2026] |
| `False` | Disable thinking; on a model that cannot turn it off, think as little as the model allows — its lowest effort, level or budget; a model with no thinking setting at all keeps its default[^pydantic-thinking-docs-2026] |
| `'minimal'` / `'low'` / `'medium'` / `'high'` / `'xhigh'` / `'max'` | Enable at a specific level; an unsupported level maps to the closest value the model accepts[^pydantic-thinking-docs-2026] |

Omitted means the model's own default, so the setting is opt-in rather than an override of provider behaviour[^pydantic-thinking-docs-2026]. `False` is a request for *least* thinking, not a guarantee of none: the docs catalogue the models that reason always-on and therefore drop to their floor instead (`gpt-oss` on Cerebras and Groq, Grok 4.5–4.7, GLM-5.3, Mistral Large 4, o-series and GPT-5 on OpenAI)[^pydantic-thinking-docs-2026].

## Precedence, and the warning that names both sides

Provider-specific settings take precedence when both are set, with one exception the docs call out explicitly: `thinking=False` still disables reasoning on Cerebras and on Groq's qwen3 models, so the off-switch is not overridable there[^pydantic-thinking-docs-2026]. When the provider-specific setting comes from a broader scope than `thinking` — the model's `settings` while `thinking` arrives from this capability, `agent.run()` or a direct request — Pydantic AI raises a `UserWarning` that names both[^pydantic-thinking-docs-2026]. Two silent cases: settings given as a callable (dynamic model settings) are not checked at all, and neither are capability settings — this capability's `thinking` included — once any capability's settings are a callable or deferred with `defer_loading`[^pydantic-thinking-docs-2026].

## Provider translation

The capability maps each value onto the selected provider's native shape. The cells below condense the vendor's own table; the snapping and off-switch notes are where models inside one provider diverge[^pydantic-thinking-docs-2026].

| Provider | `Thinking()` / `Thinking(effort=True)` | `Thinking(effort='high')` | Off-switch and snapping |
| --- | --- | --- | --- |
| Anthropic, adaptive | `anthropic_thinking={'type': 'adaptive'}` | adaptive plus `effort='high'` | `False` sends `type='disabled'` on models that think by default, `type='between_tools'` on Sonnet 5.5, and adaptive plus `effort='low'` on Opus 5.5, Fable and Mythos (Mythos Preview has no effort setting and gets nothing); `'xhigh'` on Opus 4.7, 4.8, 5, 5.5, Sonnet 5 and 5.5 and Haiku 5.5; `'max'` sends `effort='max'` |
| Anthropic, older | `{'type': 'enabled', 'budget_tokens': 10000}` | `budget_tokens=16384` | `'low'` maps to 2,048 tokens and `'xhigh'`/`'max'` to 32,768; Claude Opus 4.5 also takes an effort up to `'high'`, so the two highest levels send `effort='high'` |
| OpenAI | `reasoning_effort='medium'` | `reasoning_effort='high'` | Effort is snapped per model: GPT-5.6 and GPT-6 Astra map `'minimal'` to `'low'`, the o-series accept `low`–`high`, and `-pro` models accept only `high` (GPT-5 Pro) or `medium`–`xhigh`; `'max'` becomes `reasoning_effort='max'` on the Responses API for GPT-5.6 and GPT-6 and `'xhigh'` elsewhere; Chat Completions rejects `'max'`; `False` sends `'none'` where accepted, otherwise the model's floor (`'low'` on o3, `'minimal'` on GPT-5) |
| Google, Gemini 3+ and Gemma 4 | `include_thoughts=True` | `thinking_level='HIGH'` | Levels snap to the documented set — models without `minimal` receive `'LOW'` for unified `'minimal'`, `'xhigh'`/`'max'` become `'XHIGH'` on `gemini-4-hydrogen` and `'HIGH'` elsewhere; `False` sends the lowest level without `include_thoughts`, and on Google Cloud it instead sends `thinking_budget=0` |
| Google, Gemini 2.5 | `include_thoughts=True` | `thinking_budget=24576` | `False` sends `thinking_budget=0`; Gemini 2.5 Pro cannot turn thinking off and gets its minimum of 128 tokens |
| Groq | `reasoning_format='parsed'`, plus `reasoning_effort='medium'` for gpt-oss | `reasoning_format='parsed'`, plus `reasoning_effort='high'` for gpt-oss | gpt-oss cannot disable reasoning, so `False` sends `reasoning_effort='low'` with `reasoning_format='hidden'`; qwen3 takes `reasoning_effort='none'`, a true disable, through `extra_body` |
| Mistral | `reasoning_effort='high'` | `reasoning_effort='high'` | Only adjustable-reasoning models; Small 4 and Medium 3.5 accept only `'high'`/`'none'`, Large 4 accepts `'low'`/`'medium'`/`'high'` and cannot disable, and dated `magistral` ids receive nothing |
| OpenRouter | `reasoning={'effort': 'medium', 'enabled': True}` | `reasoning={'effort': 'high', 'enabled': True}` | `False` sends `effort='none'`; routes that cannot disable get `'low'`, routes where OpenRouter makes reasoning mandatory get `'minimal'`, and `'max'` is lowered to the highest effort the routed model supports; all through `extra_body` |
| Cerebras | `reasoning_effort` omitted | `reasoning_effort` omitted | `False` sends `'none'`; gpt-oss reasons always-on and drops to `'low'` |
| Snowflake Cortex | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | Claude models only, through `extra_body`; `temperature=1` is set automatically; other model families ignore `thinking` |
| Crusoe | `reasoning_effort='medium'` | `reasoning_effort='high'` | Inherited from `OpenAIChatModel` and the vendor-prefixed model profile; `False` sends `'none'` only where that profile accepts it |
| GitHub Copilot | `reasoning_effort='medium'` | `reasoning_effort='high'` | No client-side gate, so every level is forwarded and Copilot's per-id list raises `400 invalid_reasoning_effort`; unified `'max'` goes out as `'xhigh'`; `False` sends `'none'`, which the `claude-` and `gemini-` ids reject |
| DeepSeek | `reasoning_effort='medium'` | `reasoning_effort='high'` | V4 models; `'max'` sends `'max'`, and `'xhigh'` is mapped down to `'high'` |
| MiniMax | `reasoning_effort='medium'` | `reasoning_effort='high'` | `'max'` becomes `'xhigh'`; the M2 family and M3.1-Flash reason always-on and reject `'none'`, so `False` sends no effort at all, while M3 takes `'none'`; nothing is sent on Bedrock |
| Moonshot AI | `reasoning_effort='medium'` | `reasoning_effort='high'` | `'max'` sends `'max'` on Kimi K3, K2.6 and K2.7 and `'xhigh'` on the others; `False` disables thinking on K2.5 and K2.6, drops to `'low'` on always-reasoning K3, and sends nothing on K2.7 Code, which has no effort setting |
| Ollama | `reasoning_effort='medium'` | `reasoning_effort='high'` | Follows the resolved model profile: `deepseek-r1` reasons, `gpt-oss` on Ollama sends nothing; `False` sends `'none'` only on profiles that accept it |
| Z.AI | `thinking={'type': 'enabled'}` | enabled, plus `reasoning_effort='high'` on GLM-5.2 and GLM-5.3 | `False` sends `type='disabled'`; GLM-5.3 always reasons and takes `type='enabled'` with `reasoning_effort='low'`, and accepts only `low`, `high` and `max` |
| xAI | `reasoning_effort` omitted on Grok 4.3, which applies its own default | `reasoning_effort='high'` | Grok 4.3 accepts `none`/`low`/`medium`/`high`; Grok 3 Mini accepts `none`/`low`/`high` and gets `'high'` for `True`; Grok 4.5–4.7 accept `low`/`medium`/`high` but not `none`, so they reason always-on and `False` sends `'low'`; `'xhigh'` and `'max'` send `'high'` |
| Cohere | `thinking={'type': 'enabled'}` | enabled with `token_budget=16384` | Reasoning models only; `False` sends `type='disabled'`; effort maps to 512 (`'minimal'`), 2,048 (`'low'`), 8,192 (`'medium'`), 16,384 (`'high'`) and 31,000 tokens (`'xhigh'`/`'max'`) |
| Bedrock, Claude 4.6+ and Haiku 5.5 | `thinking.type='adaptive'` | adaptive plus `output_config.effort='high'` | Effort lives in the sibling `output_config` field; `'xhigh'` passes through only on the models whose profile supports it and otherwise becomes `max`, which passes through |
| Bedrock, older Claude | `thinking.type='enabled'` | `budget_tokens=16384` | Budget-based like the direct Anthropic API |
| Bedrock, DeepSeek V3.2 | `reasoning_effort='high'` | `reasoning_effort='high'` | Converse accepts `low` and `medium` but they do not reason, so every enabled level sends `'high'`; `False` sends `'none'` |
| Bedrock, OpenAI GPT-OSS | `reasoning_effort='medium'` | `reasoning_effort='high'` | `'minimal'` becomes `'low'` and `'xhigh'`/`'max'` become `'high'`; `'none'` is rejected, so `False` sends `'low'` |
| Bedrock, OpenAI GPT-5.6 and GPT-6 | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | Responses-shaped object; `False` sends `'none'`, or `'low'` on GPT-6 Astra and GPT-6.1 Sol, which reject it; `'minimal'` becomes `'low'` and `'max'` becomes `'xhigh'` |
| Bedrock, Qwen | `reasoning_config='high'` | `reasoning_config='high'` | `'minimal'`/`'low'` become `'low'`; `False` sends `'none'`; Qwen3-Coder returns no reasoning, so `thinking` sends nothing |
| Bedrock, xAI Grok | `reasoning` omitted on Grok 4.7; `reasoning={'effort': 'medium'}` on 4.6 | `reasoning={'effort': 'high'}` | 4.6 and 4.7 accept `low`–`xhigh` (`'minimal'` folds to `'low'`, `'max'` to `'xhigh'`) and always reason, so `False` sends `'low'` |
| Bedrock, Z.AI GLM-4.7 and GLM-5 | `reasoning_effort='high'` | `reasoning_effort='high'` | `low`/`medium` are accepted but do not reason, so every enabled level sends `'high'`; `False` sends `'none'` |
| Bedrock, Z.AI GLM-5.3 | `reasoning_effort='max'`, its default | `reasoning_effort='high'` | Always reasons; levels pass through except `'minimal'` → `'low'`; `False` sends `'low'` |
| Bedrock Mantle | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | Served on the Responses API, so effort rides the `reasoning` object; `False` sends `'none'` and `'max'` sends `'xhigh'` |

The table is the vendor's statement of intent for version-unknown Pydantic AI, not a schema: several rows name a model family whose current level set is described in prose, and the per-model acceptance lists live in the provider pages rather than here[^pydantic-thinking-docs-2026] The per-model level sets behind the two Google rows — the Gemini 4 family and its `xhigh`, Gemma 4's two levels, the Pro models that cannot switch off, the image-model exception and the `GoogleModelProfile` override — are compiled in [Google thinking levels](google-thinking-levels.md)..

## Reasoning tokens in usage

Where a provider reports how many output tokens were reasoning tokens, Pydantic AI surfaces the count as `output_reasoning_tokens` on the response usage and sums it over the run in `RunUsage`[^pydantic-thinking-docs-2026]. The count is included in `output_tokens` rather than added to it, and reads `0` when the model did not reason or the provider does not report it separately — so it is a readable subset of the output total, not a separate bill line[^pydantic-thinking-docs-2026].

## Thinking parts in message history

A `ThinkingPart` from message history is sent back to the model rather than dropped, because the reasoning is usually load-bearing for the turns that follow it and dropping it would cost the model context it produced for itself[^pydantic-thinking-docs-2026]. The only profile value that opts out is `False` on `openai_chat_send_back_thinking_parts`, which no shipped model sets[^pydantic-thinking-docs-2026].

Where the provider offers its own reasoning channel — a signed thinking block, an encrypted reasoning item, a dedicated `reasoning` field — that channel carries the part, and each such channel checks a credential the provider minted, a signature or the id it issued[^pydantic-thinking-docs-2026]. The channel is therefore open only to a part that still holds that credential and came from a provider that can verify it: the same provider, or one on the same canonical system, such as the OpenAI API for reasoning from the Codex backend, or Bedrock for Claude thinking produced by the Anthropic API[^pydantic-thinking-docs-2026]. A part that lost the credential on a storage round trip, was rebuilt by a history processor, or came from a `FallbackModel` member with another canonical system cannot use the channel, and Pydantic AI then writes the reasoning out as text in the model's thinking tags instead of dropping it[^pydantic-thinking-docs-2026]. Anthropic is the exception to both where that text goes and how it is tagged, covered in [reasoning settings per provider](pydantic-ai-reasoning-settings-per-provider.md)[^pydantic-thinking-docs-2026].

## Limits

- Single vendor reference page with no publication date, author, licence or Pydantic AI version, so every API name and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-thinking-docs-2026].
- The model names in the samples (`claude-opus-5-5`, `gpt-6-astra`, `gemini-4-hydrogen`, `kimi-k3`) are the vendor's own examples; nothing else in this wiki corroborates them.
- No package was installed, no agent constructed, no provider called and no span opened: every claim is **Reported**, none **Observed** or **Reproduced**, and no effort mapping was checked against a live API error.
- The page states precedence and snapping rules but not the exact warning text, the full per-model level lists, or how a provider rejects an out-of-range effort beyond the Copilot `400 invalid_reasoning_effort` example.

## Relationships

- **Is a** [capability](pydantic-ai-capability-primitive.md) in core `pydantic-ai`, and the thinnest one described there: it is essentially a model setting with a typed surface.
- **Detailed for each provider** by [reasoning settings per provider](pydantic-ai-reasoning-settings-per-provider.md), which owns the native settings, budget arithmetic, adaptive and interleaved thinking, and reasoning formats.
- **Changed over time** by [reasoning effort changes](pydantic-ai-reasoning-effort-changes.md), which covers per-run and per-step effort changes and their effect on the prompt cache.
- **Interacts with** [prompt caching](pydantic-ai-prompt-caching.md): a request-level effort value is part of the provider's cache key.
- **Constrained by** [model fallback](pydantic-ai-model-fallback.md), where per-model `ModelSettings` carry different efforts and a chain member on another canonical system loses the reasoning channel.
- **Carried in** [conversation state](pydantic-ai-conversation-state.md): `ThinkingPart`s and recorded effort deltas are part of the messages a saved thread replays.
- **Interacts with** [structured output](pydantic-ai-structured-output.md) on Anthropic, where a forced tool choice stops thinking and a structured `output_type` switches to Native Output.

[^pydantic-thinking-docs-2026]: Pydantic Docs, "Thinking", <https://pydantic.dev/docs/ai/capabilities/thinking/>, 4,279 words as declared and 4,325 by local `wc -w`, language `en`, no publication date, author or Pydantic AI version named; local capture `raw/capabilities/thinking/index.md`, content digest sha256:d7e5d288. §"Unified thinking settings" (raw lines 15–45) for the capability and bare-setting samples, the `True`/`False`/level semantics, the omitted-means-default rule, provider-specific precedence, the Cerebras and Groq qwen3 exceptions, the broader-scope `UserWarning`, and the callable and `defer_loading` exclusions; §"Provider translation" (lines 46–80) for every row of the table and its snapping and off-switch notes; line 82 for `output_reasoning_tokens`, its place inside `output_tokens`, and the zero case; §"Thinking in message history" (lines 84–90) for `ThinkingPart` replay, the `openai_chat_send_back_thinking_parts` opt-out, the credential and canonical-system rule, and the text fallback. Evidence class: **Reported** — vendor documentation; nothing was installed, run or measured.
