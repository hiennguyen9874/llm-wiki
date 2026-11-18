---
title: "Thinking"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/capabilities/thinking/"
domain: "pydantic.dev"
language: "en"
description: "Enable thinking and reasoning effort in Pydantic AI with the Thinking capability, or use native settings for OpenAI, Anthropic, Google, Bedrock and more."
word_count: 4279
---

Thinking (or reasoning) is the process by which a model works through a problem step-by-step before providing its final answer.

The simplest way to enable thinking across supported providers is the [`Thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Thinking) [capability](https://pydantic.dev/docs/ai/capabilities/overview/). Provider-specific settings are available for advanced usage when you need direct access to a provider’s native thinking controls.

## Unified thinking settings

Use the [`Thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Thinking) capability to enable thinking:

thinking\_capability.py

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking

agent = Agent('anthropic:claude-opus-5-5', capabilities=[Thinking(effort='high')])
```

You can also set the underlying `thinking` field in [`ModelSettings`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings) directly:

unified\_thinking.py

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-opus-5-5', model_settings={'thinking': 'high'})
```

The [`Thinking.effort`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Thinking.effort) value accepts:

- `True` — enable thinking with the provider’s default effort level
- `False` — disable thinking; on a model that can’t turn thinking off, think as little as the model allows (its lowest effort, level, or budget). A model that offers no thinking setting at all keeps its default
- `'minimal'` / `'low'` / `'medium'` / `'high'` / `'xhigh'` / `'max'` — enable thinking at a specific effort level (unsupported levels map to the closest available value)

These are the same values accepted by the underlying `thinking` model setting. When omitted, the model uses its default behavior. Provider-specific settings (documented in the sections below) take precedence when both are set, except that `thinking=False` still disables reasoning on Cerebras and on Groq’s qwen3 models. If the provider-specific setting comes from a broader scope than `thinking` (for example, the model’s `settings` while `thinking` comes from this capability, `agent.run()` or a direct request), a `UserWarning` names both. Settings given as a callable ([dynamic model settings](https://pydantic.dev/docs/ai/core-concepts/agent/#dynamic-model-settings)) are not checked, and neither are capability settings, this capability’s `thinking` included, once any capability’s settings are a callable or are deferred with `defer_loading`.

### Provider translation

The `Thinking` capability maps each effort value to the selected provider’s native format:

| Provider | `Thinking()` / `Thinking(effort=True)` | `Thinking(effort='high')` | Notes |
| --- | --- | --- | --- |
| Anthropic (adaptive thinking) | `anthropic_thinking={'type': 'adaptive'}` | `{type: 'adaptive'}` + `effort='high'` | Claude Opus 4.7, 4.8, 5, 5.5, Sonnet 5 and 5.5, and Haiku 5.5 also support `effort='xhigh'`; `'max'` → `effort='max'`. `thinking=False` → `type='disabled'` on models that think by default, `type='between_tools'` on Sonnet 5.5, and `{type: 'adaptive'}` + `effort='low'` on Opus 5.5 and the Fable and Mythos models, which can’t turn thinking off (Mythos Preview, which has no effort setting, gets nothing) |
| Anthropic (older) | `anthropic_thinking={'type': 'enabled', 'budget_tokens': 10000}` | `budget_tokens=16384` | Budget-based; `'low'` → 2048 tokens, `'xhigh'` and `'max'` → 32768. Claude Opus 4.5 also takes an effort up to `'high'`, so `'xhigh'` and `'max'` send `effort='high'` |
| OpenAI | `reasoning_effort='medium'` | `reasoning_effort='high'` | Unified efforts map to the closest effort the model accepts: GPT-5.6 and GPT-6 Astra map `'minimal'` to `'low'`, the o-series accept `low`–`high`, and the `-pro` models accept only `high` (GPT-5 Pro) or `medium`–`xhigh`. `'max'` → `reasoning_effort='max'` on the Responses API for GPT-5.6 and GPT-6, and `'xhigh'` (or the closest accepted effort) everywhere else, including Codex and ChatGPT plan usage: the Chat Completions API rejects `'max'`. `thinking=False` → `'none'` where accepted; models that can’t turn reasoning off (the o-series, GPT-5, the `-pro` models, GPT-6 Astra) get their lowest effort instead (e.g. `'low'` on o3, `'minimal'` on GPT-5) |
| Google (Gemini 3+, Gemma 4) | `include_thoughts=True` | `thinking_level='HIGH'` | Unified efforts snap to the nearest documented level — e.g. `gemini-3.1-flash-lite-image` and Gemma 4 (levels: `minimal`, `high`) map `'low'` to `'MINIMAL'` and `'medium'`/`'xhigh'`/`'max'` to `'HIGH'` — and models without `minimal` map unified `'minimal'` to `'LOW'`; `'xhigh'` and `'max'` → `'XHIGH'` on `gemini-4-hydrogen` and `'HIGH'` on models without that level; `gemini-3.1-flash-image` applies its `minimal, high` set only on the Gemini API (see [Google](https://pydantic.dev/docs/ai/models/google/#configure-thinking)). `thinking=False` → the lowest level the model accepts, without `include_thoughts` (`'LOW'` on Gemini 3.1 Pro, which can’t turn thinking off on the Gemini API; on Google Cloud it gets `thinking_budget=0`, which turns thinking off there) |
| Google (Gemini 2.5) | `include_thoughts=True` | `thinking_budget=24576` | `thinking=False` → `thinking_budget=0`; Gemini 2.5 Pro can’t turn thinking off, so it gets its minimum, `thinking_budget=128` |
| Groq | `reasoning_format='parsed'` (gpt-oss also `reasoning_effort='medium'`) | `reasoning_format='parsed'` (gpt-oss also `reasoning_effort='high'`) | gpt-oss: unified effort → `reasoning_effort` (`low`/`medium`/`high`, via `extra_body`); it can’t turn reasoning off, so `thinking=False` → `reasoning_effort='low'` with `reasoning_format='hidden'`; qwen3: `thinking=False` → `reasoning_effort='none'` (true disable, via `extra_body`) |
| Mistral | `reasoning_effort='high'` | `reasoning_effort='high'` | Only on adjustable-reasoning models (e.g. `mistral-small-latest`, `mistral-medium-3-5`, and `magistral-medium-latest` and `magistral-small-latest`, which point at them); dated `magistral` ids reason always-on and get no `reasoning_effort`. Small 4 and Medium 3.5 accept only `'high'`/`'none'`, so every enabled level (incl. `'minimal'`) → `'high'` and only `thinking=False` → `'none'`; Large 4 (`mistral-large-4`, `mistral-large-4-0`) accepts `'low'`/`'medium'`/`'high'` and can’t turn reasoning off, so `False`/`'minimal'`/`'low'` → `'low'`, `'medium'` → `'medium'`, and `True`/`'high'`/`'xhigh'`/`'max'` → `'high'` |
| OpenRouter | `reasoning={'effort': 'medium', 'enabled': True}` | `reasoning={'effort': 'high', 'enabled': True}` | `thinking=False` → `effort='none'`; routes to models that can’t turn reasoning off get `effort='low'`, and routes where OpenRouter makes reasoning mandatory get `effort='minimal'` (see [below](#openrouter)); `'max'` → `effort='max'`, which OpenRouter lowers to the highest effort the routed model supports; via `extra_body` |
| Cerebras | `reasoning_effort` omitted (reasons by default) | `reasoning_effort` omitted | `thinking=False` → `reasoning_effort='none'`; gpt-oss reasons always-on, so `thinking=False` → its lowest effort, `reasoning_effort='low'` |
| Snowflake Cortex | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | Claude models only (via `extra_body`); sets `temperature=1` automatically; other families ignore `thinking` |
| Crusoe | `reasoning_effort='medium'` | `reasoning_effort='high'` | Inherited from `OpenAIChatModel`; follows the vendor-prefixed model profile (`zai/`, `deepseek-ai/`, …). `thinking=False` → `'none'` only where that profile accepts it |
| GitHub Copilot | `reasoning_effort='medium'` | `reasoning_effort='high'` | Inherited from `OpenAIChatModel` with no client-side gate: every value is forwarded and Copilot enforces its own per-id list, so a level an id doesn’t offer comes back as `400 invalid_reasoning_effort`. Unified `'max'` goes out as `'xhigh'`. `thinking=False` → `'none'`, which the `claude-` and `gemini-` ids reject. Those two families return reasoning in `reasoning_text`, mapped to a `ThinkingPart`; `gpt-5.4` and `kimi-k3` reason but return no reasoning text |
| DeepSeek | `reasoning_effort='medium'` | `reasoning_effort='high'` | V4 models; `'max'` → `reasoning_effort='max'`. DeepSeek maps `'xhigh'` to `'high'`, so `'max'` is the way to its deepest reasoning |
| MiniMax | `reasoning_effort='medium'` | `reasoning_effort='high'` | `minimax/`, `MiniMaxAI/` and `minimaxai/` ids on `OpenAICompatibleProvider`, `LiteLLMProvider` and `TogetherProvider`; `'max'` → `'xhigh'`. The M2 family and M3.1-Flash always reason and reject `'none'`, so `thinking=False` sends no `reasoning_effort`; M3 can turn thinking off and gets `'none'`. On Bedrock, `thinking` sends nothing |
| Moonshot AI | `reasoning_effort='medium'` | `reasoning_effort='high'` | `'max'` → `reasoning_effort='max'` on Kimi K3, K2.6 and K2.7, and `'xhigh'` on the other Kimi models. `thinking=False` → `thinking={'type': 'disabled'}` on Kimi K2.5 and K2.6 (via `extra_body`), and `reasoning_effort='low'` on Kimi K3, which always reasons; Kimi K2.7 Code always reasons and has no effort setting, so it gets nothing |
| Ollama | `reasoning_effort='medium'` | `reasoning_effort='high'` | Inherited from `OpenAIChatModel`, so it follows the resolved model profile: `deepseek-r1` reasons, `gpt-oss` on Ollama sends nothing. `thinking=False` → `'none'` only on profiles that accept it |
| Z.AI | `thinking={'type': 'enabled'}` | `thinking={'type': 'enabled'}`, plus `reasoning_effort='high'` on GLM-5.2 and GLM-5.3 | Via `extra_body`; `thinking=False` → `type='disabled'`. GLM-5.3 always reasons, so `thinking=False` → `type='enabled'` with its lowest effort, `reasoning_effort='low'`; it accepts only `low`/`high`/`max` (per Z.AI’s docs and the error message returned when disabling thinking on it), mapping the other unified levels to the nearest one |
| xAI | `reasoning_effort` omitted on Grok 4.3 (uses its default) | `reasoning_effort='high'` | Grok 4.3 supports `'none'`, `'low'`, `'medium'`, and `'high'`, and `thinking=True` omits the parameter so the model applies its own default; Grok 3 Mini supports `'none'`, `'low'`, and `'high'` (`thinking=True` → `'high'`); Grok 4.5, 4.6 and 4.7 support `'low'`, `'medium'`, and `'high'` but not `'none'`, so they reason always-on (`thinking=True` → `'medium'` on 4.5 and 4.6) and `thinking=False` → `'low'`. `'xhigh'` and `'max'` → `'high'` |
| Cohere | `thinking={'type': 'enabled'}` | `thinking={'type': 'enabled', 'token_budget': 16384}` | Reasoning models (e.g. `command-a-reasoning-08-2025`) only; `thinking=False` → `type='disabled'`; `'minimal'` → 512 tokens, `'low'` → 2048, `'medium'` → 8192, `'xhigh'` and `'max'` → 31000 |
| Bedrock (Claude 4.6+ and Haiku 5.5) | `thinking.type='adaptive'` | `{type: 'adaptive'}` + `output_config.effort='high'` | Effort lives in the sibling `output_config` field per AWS docs; `xhigh` passes through on the models whose profile supports it (the same ones as the direct Anthropic API, e.g. Opus 4.7+, Sonnet 5, and Haiku 5.5) and maps to `max` on the others (Opus 4.6 and Sonnet 4.6 reject `xhigh`); `'max'` passes through |
| Bedrock (Claude older) | `thinking.type='enabled'` | `budget_tokens=16384` | Budget-based |
| Bedrock (DeepSeek V3.2) | `reasoning_effort='high'` | `reasoning_effort='high'` | Converse accepts `low` and `medium` but they don’t reason, so every enabled level → `'high'`, the only level that reasons; `thinking=False` → `'none'` |
| Bedrock (OpenAI GPT-OSS) | `reasoning_effort='medium'` | `reasoning_effort='high'` | Converse accepts only `low`/`medium`/`high`, so `'minimal'` → `'low'` and `'xhigh'` and `'max'` → `'high'`; it rejects `'none'`, so `thinking=False` → `'low'` |
| Bedrock (OpenAI GPT-5.6 and GPT-6) | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | The Responses API shape, which Converse expects for these models; `thinking=False` → `effort='none'`, or `'low'` on GPT-6 Astra and GPT-6.1 Sol, which reject `'none'`; unified `'minimal'` → `'low'`, `'max'` → `'xhigh'` |
| Bedrock (Qwen) | `reasoning_config='high'` | `reasoning_config='high'` | `'minimal'`/`'low'` → `'low'`, other levels → `'high'`; `thinking=False` → `'none'`. Qwen3-Coder returns no reasoning, so `thinking` sends nothing |
| Bedrock (xAI Grok) | `reasoning` omitted on Grok 4.7 (uses its `'high'` default); `reasoning={'effort': 'medium'}` on Grok 4.6 | `reasoning={'effort': 'high'}` | Grok 4.6 and 4.7 accept `'low'`, `'medium'`, `'high'`, and `'xhigh'` (`'minimal'` folds to `'low'`, `'max'` to `'xhigh'`); they always reason, so `thinking=False` → `'low'` |
| Bedrock (Z.AI GLM-4.7/GLM-5) | `reasoning_effort='high'` | `reasoning_effort='high'` | Converse accepts `low` and `medium` but they don’t reason, so every enabled level → `'high'`, the only level that reasons; `thinking=False` → `'none'` |
| Bedrock (Z.AI GLM-5.3) | `reasoning_effort='max'` (its default) | `reasoning_effort='high'` | Always reasons; levels pass through except `'minimal'` → `'low'` (Bedrock, unlike Z.AI’s API, accepts `low` through `max`); `thinking=False` → `'low'` |
| Bedrock Mantle | `reasoning={'effort': 'medium'}` | `reasoning={'effort': 'high'}` | Served on the Responses API, so effort rides the `reasoning` object; `thinking=False` → `effort='none'`; `'max'` → `effort='xhigh'` |

Many providers report how many of a response’s output tokens were reasoning tokens. Pydantic AI reports that count as `output_reasoning_tokens` on the response’s usage, and sums it over the run in [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage). It’s included in `output_tokens`, and it’s `0` when the model didn’t reason or the provider doesn’t report the count separately.

## Thinking in message history

Pydantic AI sends a [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) from message history back to the model instead of dropping it. Reasoning is usually load-bearing for the turns that follow it, so dropping it would cost the model context it produced for itself. The one profile value that opts out of sending it is `False` on [`openai_chat_send_back_thinking_parts`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_send_back_thinking_parts), which no shipped model sets.

Where the provider’s own reasoning channel is available — a signed thinking block, an encrypted reasoning item, a dedicated `reasoning` field — that is what carries it. Each of those channels checks a credential the provider minted, a signature or the id it issued for the item, so the channel is only open for a part that still has one and came from a provider that can verify it: the same provider, or one with the same [canonical system](https://pydantic.dev/docs/ai/core-concepts/message-history/#sending-history-to-another-provider), such as the OpenAI API for reasoning from the Codex backend, or Bedrock for Claude’s thinking from the Anthropic API. A part that lost it on a round trip through storage, was rebuilt by a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history), or came from a model in a [`FallbackModel`](https://pydantic.dev/docs/ai/api/models/fallback/#pydantic_ai.models.fallback.FallbackModel) chain with another canonical system can’t use it; Pydantic AI then writes the reasoning out as text in the model’s thinking tags rather than dropping it.

Anthropic is the exception to both *where* that text goes and *how* it is tagged — see [Carried-over thinking](#carried-over-thinking).

## Changing effort mid-conversation

The effort level can change from one run to the next, or from one step to the next through a `model_settings` callable or a capability’s [`get_model_settings`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability.get_model_settings):

effort\_mid\_conversation.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6-astra')
result = agent.run_sync('Plan the database migration.', model_settings={'thinking': 'low'})
result = agent.run_sync(
    'Now check the plan for anything that could lose data.',
    message_history=result.all_messages(),
    model_settings={'thinking': 'high'},
)
```

The request-level effort is part of the provider’s [prompt cache](https://pydantic.dev/docs/ai/capabilities/caching/) key, so sending the new level there makes the provider process the whole conversation again. Where the API can change the effort from a point in the conversation onward, Pydantic AI sends the change that way instead, and every request keeps the effort the conversation started with:

| API | How the change is sent | Models |
| --- | --- | --- |
| OpenAI Responses | a `configuration_update` input item | GPT-6 family |
| Anthropic | an effort-only `system` entry with a per-message `output_config`, under the `mid-conversation-output-config-2026-07-01` beta | Claude Fable 5.1 and 5.2, Mythos 5.1 and 5.2, Opus 5.5, Opus 5, Sonnet 5.5 and Haiku 5.5 on the Claude API and Google Cloud; Fable 5.1 and Opus 5.5 on the legacy Bedrock InvokeModel client; Opus 5.5 on the Bedrock Messages API client |
| OpenRouter | a content-less `system` message carrying a `configuration_update`, which OpenRouter sends on in the routed model’s own form | Claude Fable 5.1 and 5.2, Opus 5.5, Opus 5, Sonnet 5.5 and Haiku 5.5; GPT-6 Astra, Sol and Luna, GPT-6.1 Sol, and GPT-6.2 Sol and Astra, but not their `-pro` variants |

Every other API and model gets the new level as the request-level setting, as before. So do these cases, where the API doesn’t take a mid-conversation change:

- A provider-specific effort setting such as `openai_reasoning_effort`, `anthropic_effort` or `openrouter_reasoning` is set.
- OpenAI truncation (`openai_truncation='auto'`) or server-side compaction is in use.
- Anthropic thinking isn’t adaptive, such as `between_tools` on Claude Sonnet 5.5 or `disabled` on Claude Haiku 5.5.
- The change is to or from `True` or `False`, which names no effort level.

The framework records each change in message history as a [`ModelSettingsDeltaPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelSettingsDeltaPart) at the end of the request it applies to, and the first request that names an effort level records one too. The part holds the changed settings by their unified [`ModelSettings`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings) keys, such as `{'thinking': 'high'}`; `RecordedModelSettings` lists the keys that can be recorded, which today is only the `thinking` effort level. Each model adapter sends the keys it can change mid-conversation in place and the rest as request-level settings. A later run that continues from `message_history` reads the parts to know which effort the conversation started with and which changes to send again. The Vercel AI adapter carries them through the client. The AG-UI adapter streams and dumps them as `pydantic_ai_model_settings_delta` activity messages, which `@ag-ui/client` doesn’t send back; see [Records carried as activity messages](https://pydantic.dev/docs/ai/integrations/ui/ag-ui/#activity-records).

## OpenAI

When using the [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel), text output inside `<think>` tags is converted to [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) objects. You can customize the tags using the [`thinking_tags`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.thinking_tags) field on the [model profile](https://pydantic.dev/docs/ai/models/compatible-apis/#model-profile).

Some [OpenAI-compatible model providers](https://pydantic.dev/docs/ai/models/overview/#openai-compatible-providers) might also support native thinking parts that are not delimited by tags. Instead, they are sent and received as separate, custom fields in the API. Typically, if you are calling the model via the `<provider>:<model>` shorthand, Pydantic AI handles it for you. Nonetheless, you can still configure the fields with [`openai_chat_thinking_field`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_thinking_field).

If your provider recommends sending these custom fields back unchanged for caching or interleaved thinking, use [`openai_chat_send_back_thinking_parts`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_send_back_thinking_parts).

### OpenAI Responses

The [`OpenAIResponsesModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModel) can generate native thinking parts. Set `OpenAIResponsesModelSettings.openai_reasoning_effort` and [`OpenAIResponsesModelSettings.openai_reasoning_summary`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_summary) in the [model settings](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings) to enable native thinking parts. Models that support it can additionally use a `pro` [reasoning mode](https://pydantic.dev/docs/ai/models/openai/#reasoning-mode), which is independent of the effort and never set by the unified `thinking` setting.

By default, the unique IDs of reasoning, text, and function call parts from the message history are sent to the model, which can result in errors like `"Item 'rs_123' of type 'reasoning' was provided without its required following item."` if the message history you’re sending does not match exactly what was received from the Responses API in a previous response, for example if you’re using a [history processor](https://pydantic.dev/docs/ai/core-concepts/message-history/#processing-message-history). To disable this, you can disable the [`OpenAIResponsesModelSettings.openai_send_reasoning_ids`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_send_reasoning_ids) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings).

openai\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.6-sol')
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort='low',
    openai_reasoning_summary='detailed',
)
agent = Agent(model, model_settings=settings)
...
```

## Anthropic

To enable thinking, use the [`AnthropicModelSettings.anthropic_thinking`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_thinking) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings).

anthropic\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-sonnet-4-5')
settings = AnthropicModelSettings(
    anthropic_thinking={'type': 'enabled', 'budget_tokens': 1024},
)
agent = Agent(model, model_settings=settings)
...
```

The thinking budget counts toward [`max_tokens`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.max_tokens), which Anthropic requires to be greater than the budget. When you don’t set `max_tokens`, Pydantic AI raises its [default](https://pydantic.dev/docs/ai/models/anthropic/#model-settings) as needed to leave at least 4096 tokens beyond the budget.

Pydantic AI reports how many thinking tokens Anthropic used as `output_reasoning_tokens`, and also in [`RunUsage.details`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage.details) under the `thinking_tokens` key. They are billed within `output_tokens`, so they are a readable subset of the output total rather than an addition to it, and the key is omitted entirely when a response used no thinking tokens.

### Carried-over thinking

Reasoning that can’t ride Anthropic’s native reasoning channel — see [Thinking in message history](#thinking-in-message-history) for when that happens — is sent as text, but not from the turn it was produced in. Claude’s *own* reasoning takes this path too whenever its signature didn’t survive, which is the common case: a history round-tripped through your storage.

### Interleaved Thinking

To enable [interleaved thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking), you need to include the beta header in your model settings:

anthropic\_interleaved\_thinking.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-sonnet-4-5')
settings = AnthropicModelSettings(
    anthropic_thinking={'type': 'enabled', 'budget_tokens': 10000},
    extra_headers={'anthropic-beta': 'interleaved-thinking-2025-05-14'},
)
agent = Agent(model, model_settings=settings)
...
```

### Adaptive Thinking & Effort

Starting with `claude-opus-4-6`, Anthropic supports [adaptive thinking](https://docs.anthropic.com/en/docs/build-with-claude/adaptive-thinking), where the model dynamically decides when and how much to think based on the complexity of each request. This replaces extended thinking (`type: 'enabled'` with `budget_tokens`) which is deprecated on Opus 4.6 and removed on Opus 4.7, 4.8, 5, 5.5, Sonnet 5 and 5.5, and Haiku 5.5. Claude Opus 4.7, 4.8, 5, 5.5, Sonnet 5 and 5.5, and Haiku 5.5 also add the `xhigh` effort level. Unified `thinking='max'` sends `effort='max'`, which every Claude model with an effort setting accepts except Claude Opus 4.5. Adaptive thinking also automatically enables interleaved thinking.

Claude Opus 5 and later, Claude Sonnet 5, Haiku 5.5, and the Claude Fable and Mythos models think adaptively without any thinking setting. On Claude Opus 5, Sonnet 5, and Haiku 5.5, the unified `thinking=False` setting turns that off by sending `anthropic_thinking={'type': 'disabled'}`, and on Claude Sonnet 5.5 by sending `{'type': 'between_tools'}`. Claude Opus 5.5 and the Fable and Mythos models can’t turn thinking off, so `thinking=False` sends adaptive thinking at the lowest effort, `low`; Claude Mythos Preview has no effort setting, so it keeps its default. Because a forced tool choice stops Claude from thinking, a structured `output_type` on these models uses Native Output rather than Tool Output unless thinking is off; see [Forced tool choice](https://pydantic.dev/docs/ai/models/anthropic/#forced-tool-choice).

anthropic\_adaptive\_thinking.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-opus-4-8')
settings = AnthropicModelSettings(
    anthropic_thinking={'type': 'adaptive'},
    anthropic_effort='high',
)
agent = Agent(model, model_settings=settings)
...
```

The [`anthropic_effort`](https://pydantic.dev/docs/ai/api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_effort) setting controls how much effort the model puts into its response (independent of thinking). See the [Anthropic effort docs](https://docs.anthropic.com/en/docs/build-with-claude/effort) for details.

Thinking tokens count against Anthropic’s loop-wide [task budgets](https://pydantic.dev/docs/ai/models/anthropic/#task-budgets-beta), so adaptive thinking naturally scales down as the budget depletes.

## Google

For advanced usage, use the [`GoogleModelSettings.google_thinking_config`](https://pydantic.dev/docs/ai/api/models/google/#pydantic_ai.models.google.GoogleModelSettings.google_thinking_config) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings).

google\_thinking\_part.py

```python
from google.genai.types import ThinkingLevel

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

model = GoogleModel('gemini-3.5-flash')
settings = GoogleModelSettings(google_thinking_config={'include_thoughts': True, 'thinking_level': ThinkingLevel.MEDIUM})
agent = Agent(model, model_settings=settings)
...
```

See the [Google model docs](https://pydantic.dev/docs/ai/models/google/#configure-thinking) for more details.

## xAI

xAI reasoning models (Grok) support native thinking. To preserve the thinking content for multi-turn conversations, enable [`XaiModelSettings.xai_include_encrypted_content`](https://pydantic.dev/docs/ai/api/models/xai/#pydantic_ai.models.xai.XaiModelSettings.xai_include_encrypted_content).

xai\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.xai import XaiModel, XaiModelSettings

model = XaiModel('grok-4.3')
settings = XaiModelSettings(xai_include_encrypted_content=True)
agent = Agent(model, model_settings=settings)
...
```

## Bedrock

For Claude Sonnet 4.6+, Opus 4.6+, and Haiku 5.5, Pydantic AI’s unified `thinking` setting translates to AWS’s required [adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html) shape automatically — set [`ModelSettings.thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) and you’re done.

Claude served through Bedrock inherits the Anthropic model profile, so reasoning replayed from history follows [Carried-over thinking](#carried-over-thinking) here too.

For older Claude models or to pin a specific `budget_tokens`, you can still use [`BedrockModelSettings.bedrock_additional_model_requests_fields`](https://pydantic.dev/docs/ai/api/models/bedrock/#pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_additional_model_requests_fields) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings) to pass provider-specific configuration directly:

- [Claude](#tab-panel-0-0)
- [OpenAI](#tab-panel-0-1)
- [Qwen](#tab-panel-0-2)
- [Deepseek](#tab-panel-0-3)

bedrock\_claude\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings

model = BedrockConverseModel('us.anthropic.claude-sonnet-4-5-20250929-v1:0')
model_settings = BedrockModelSettings(
    bedrock_additional_model_requests_fields={
        'thinking': {'type': 'enabled', 'budget_tokens': 1024}
    }
)
agent = Agent(model=model, model_settings=model_settings)
```

## Groq

Groq supports different formats to receive thinking parts:

- `"raw"`: The thinking part is included in the text content inside `<think>` tags, which are automatically converted to [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) objects.
- `"hidden"`: The thinking part is not included in the text content.
- `"parsed"`: The thinking part has its own structured part in the response which is converted into a [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) object.

The unified [`ModelSettings.thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) setting works across providers: it selects `reasoning_format='parsed'` so thinking parts are returned, and for the gpt-oss family its effort level also drives Groq’s `reasoning_effort` (`minimal`/`low` → `'low'`, `medium` → `'medium'`, `high`/`xhigh`/`max` → `'high'`, `True` → `'medium'`).

Two composable [model settings](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings) give finer control: [`GroqModelSettings.groq_reasoning_format`](https://pydantic.dev/docs/ai/api/models/groq/#pydantic_ai.models.groq.GroqModelSettings.groq_reasoning_format) selects how thinking parts are returned (the formats above), and [`GroqModelSettings.groq_reasoning_effort`](https://pydantic.dev/docs/ai/api/models/groq/#pydantic_ai.models.groq.GroqModelSettings.groq_reasoning_effort) (sent to Groq as `reasoning_effort`) controls how much the model reasons, taking precedence over the unified `thinking` mapping:

groq\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel, GroqModelSettings

model = GroqModel('openai/gpt-oss-120b')
settings = GroqModelSettings(groq_reasoning_format='parsed', groq_reasoning_effort='medium')
agent = Agent(model, model_settings=settings)
...
```

## OpenRouter

To enable thinking, use the [`OpenRouterModelSettings.openrouter_reasoning`](https://pydantic.dev/docs/ai/api/models/openrouter/#pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_reasoning) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings).

openrouter\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel, OpenRouterModelSettings

model = OpenRouterModel('openai/gpt-5.2')
settings = OpenRouterModelSettings(openrouter_reasoning={'effort': 'high'})
agent = Agent(model, model_settings=settings)
...
```

## Z.AI

To enable thinking, use the unified [`thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings). To preserve thinking content across multi-turn conversations, also set [`ZaiModelSettings.zai_clear_thinking`](https://pydantic.dev/docs/ai/api/models/zai/#pydantic_ai.models.zai.ZaiModelSettings.zai_clear_thinking) to `False`.

zai\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.zai import ZaiModel, ZaiModelSettings

model = ZaiModel('glm-5')
settings = ZaiModelSettings(thinking=True, zai_clear_thinking=False)
agent = Agent(model, model_settings=settings)
...
```

## GitHub Copilot

Copilot takes the unified [`thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) setting as `reasoning_effort`, inherited from [`OpenAIChatModel`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModel). Whether a given id accepts it, and which levels, is a per-model fact Copilot reports in its own catalog and enforces itself; [`GitHubCopilotModel`](https://pydantic.dev/docs/ai/api/models/github_copilot/#pydantic_ai.models.github_copilot.GitHubCopilotModel) adds no gate of its own.

Copilot’s Anthropic and Google ids return their reasoning in a non-standard `reasoning_text` field, which Pydantic AI maps to a [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) and sends back in the same field on later turns. Its OpenAI and MoonshotAI ids accept the setting and reason on it, but Copilot returns no reasoning text for them, so they yield no `ThinkingPart`. The Anthropic ids reason adaptively besides, so the effort is a ceiling rather than an instruction and an easy question may come back with no reasoning at all. Their `reasoning_effort` list also has no `none`, so `thinking=False` goes out as `reasoning_effort='none'` and Copilot answers `400 invalid_reasoning_effort`. See [GitHub Copilot](https://pydantic.dev/docs/ai/models/github-copilot/#thinking).

## Snowflake Cortex

To enable thinking on Claude models, use the unified [`thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) [model setting](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings), or set [`SnowflakeModelSettings.snowflake_reasoning`](https://pydantic.dev/docs/ai/api/models/snowflake/#pydantic_ai.models.snowflake.SnowflakeModelSettings.snowflake_reasoning) directly to control the reasoning token budget:

snowflake\_thinking\_part.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.snowflake import SnowflakeModel, SnowflakeModelSettings

model = SnowflakeModel('claude-sonnet-4-6')
settings = SnowflakeModelSettings(snowflake_reasoning={'max_tokens': 4096})
agent = Agent(model, model_settings=settings)
...
```

On OpenAI models, use the unified `thinking` setting or [`openai_reasoning_effort`](https://pydantic.dev/docs/ai/api/models/openai/#pydantic_ai.models.openai.OpenAIChatModelSettings.openai_reasoning_effort).

Claude requires `temperature` to be exactly 1 when thinking is enabled, but Cortex applies a different default when the request doesn’t specify one, so `SnowflakeModel` sets `temperature` to 1 automatically when reasoning is enabled and you haven’t set it explicitly.

## Mistral

Mistral has [deprecated](https://docs.mistral.ai/resources/deprecated/native-reasoning) the `magistral` family in favor of the adjustable-reasoning models below: `magistral-medium-latest` and `magistral-small-latest` point at Mistral Medium 3.5 and Small 4, and reason only when asked to. The dated `magistral` ids always reasoned and offer no reasoning setting, so `thinking` sends nothing for them.

Models with adjustable reasoning (the Mistral Large 4, Small 4, and Medium 3.5 families: `mistral-large-4`, `mistral-large-4-0`, `mistral-small-latest`, `mistral-small-2603`, `mistral-medium-latest`, `mistral-medium`, `mistral-medium-3`, `mistral-medium-3-5`, `mistral-medium-3.5`, `mistral-medium-2604`, `magistral-medium-latest`, `magistral-small-latest`) are controlled via the unified [`thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) setting, which maps to Mistral’s `reasoning_effort`. Small 4 and Medium 3.5 accept only `'high'` (full thinking) and `'none'` (thinking suppressed), so every enabled level maps to `'high'` and only `thinking=False` maps to `'none'`. Large 4 (`mistral-large-4`, `mistral-large-4-0`) accepts `'low'`, `'medium'`, and `'high'` and can’t turn reasoning off: `False`, `'minimal'` and `'low'` map to `'low'`, `'medium'` maps to `'medium'`, and `True`, `'high'`, `'xhigh'` and `'max'` map to `'high'`. Older `mistral-small-*` / `mistral-medium-*` snapshots and `mistral-large-latest` do not support reasoning, so `thinking` is silently ignored for them. Adjustable reasoning applies when using the native Mistral provider; OpenAI-compatible providers that host these models (such as LiteLLM or Azure) do not support it and `thinking` is ignored there. OpenRouter is the exception: it maps the unified `thinking` setting to its own `reasoning` parameter for any model it routes.

## Cohere

Thinking is supported by the `command-a-reasoning-08-2025` model, which thinks by default. The unified [`thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.thinking) setting maps to Cohere’s [`thinking` parameter](https://docs.cohere.com/docs/reasoning): `thinking=False` turns reasoning off with `type='disabled'`, and an effort level caps it with a `token_budget` (`'minimal'` → 512 tokens, `'low'` → 2048, `'medium'` → 8192, `'high'` → 16384, `'xhigh'` and `'max'` → 31000).

When the model returns a [`tool_plan`](https://docs.cohere.com/docs/tool-use-overview), the plan it writes before its tool calls, [`CohereModel`](https://pydantic.dev/docs/ai/api/models/cohere/#pydantic_ai.models.cohere.CohereModel) keeps it as a [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) with `provider_details={'tool_plan': True}` and sends it back to Cohere as `tool_plan` beside those tool calls.

## Hugging Face

Text output inside `<think>` tags is automatically converted to [`ThinkingPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ThinkingPart) objects. Reasoning that an Inference Provider returns in the separate `reasoning` field also becomes a `ThinkingPart`, and both kinds are sent back in thinking tags on later requests. You can customize the tags using the [`thinking_tags`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.thinking_tags) field on the [model profile](https://pydantic.dev/docs/ai/models/compatible-apis/#model-profile).
