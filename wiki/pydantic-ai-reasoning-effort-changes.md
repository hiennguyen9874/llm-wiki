---
type: Concept
title: Pydantic AI reasoning effort changes
description: How reasoning effort changes during a conversation — the mid-conversation route each API accepts as a delta, the cases that fall back to a request-level setting, the prompt-cache cost of that fallback, and the ModelSettingsDeltaPart that records it in history.
tags: [ml, pydantic-ai, thinking, prompt-caching]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:26:00Z }
sources:
  - id: pydantic-thinking-docs-2026
    resource: ../raw/capabilities/thinking/index.md
    scope: ../raw/capabilities/thinking/
    kind: documentation
    revision: sha256:d7e5d288fa00c8a2628fcf1b0afb94d6a8a70fe2a6e0fa2f163ef59d5550b99b
    title: "Thinking"
---

An agent's [thinking effort](pydantic-ai-thinking.md) is not fixed for the life of a conversation: it can change between runs, or between steps inside one run[^pydantic-thinking-docs-2026]. The naive way to change it — putting the new level in the next request — costs more than it looks, because request-level effort is part of the provider's prompt-cache key, so the whole conversation is processed again[^pydantic-thinking-docs-2026]. Where an API can change effort from a point onward, Pydantic AI sends it that way instead and keeps every earlier request on the effort the conversation started with; the change is recorded in message history so a later run can replay it[^pydantic-thinking-docs-2026].

## Asking for the change

Two seams accept a new level per step: a `model_settings` callable and a capability's `get_model_settings`[^pydantic-thinking-docs-2026]. Per run it is the plain setting, as in the docs' two-turn sample where the planning turn runs at `'low'` and the review turn — same conversation, continued through `message_history=result.all_messages()` — runs at `'high'`[^pydantic-thinking-docs-2026]:

```python
result = agent.run_sync('Plan the database migration.', model_settings={'thinking': 'low'})
result = agent.run_sync(
    'Now check the plan for anything that could lose data.',
    message_history=result.all_messages(),
    model_settings={'thinking': 'high'},
)
```

The distinction that matters is not `run` versus step but whether the provider takes the change as a delta or as a new request-level value[^pydantic-thinking-docs-2026].

## Where the API takes a mid-conversation change

Three APIs accept effort as a change applied from a point in the conversation onward, and Pydantic AI sends it that way so the cache prefix survives[^pydantic-thinking-docs-2026]:

| API | How the change is sent | Models |
| --- | --- | --- |
| OpenAI Responses | a `configuration_update` input item | GPT-6 family[^pydantic-thinking-docs-2026] |
| Anthropic | an effort-only `system` entry with a per-message `output_config`, under the `mid-conversation-output-config-2026-07-01` beta | Claude Fable 5.1 and 5.2, Mythos 5.1 and 5.2, Opus 5.5, Opus 5, Sonnet 5.5 and Haiku 5.5 on the Claude API and Google Cloud; Fable 5.1 and Opus 5.5 on the legacy Bedrock InvokeModel client; Opus 5.5 on the Bedrock Messages API client[^pydantic-thinking-docs-2026] |
| OpenRouter | a content-less `system` message carrying a `configuration_update`, which OpenRouter passes on in the routed model's own form | Claude Fable 5.1 and 5.2, Opus 5.5, Opus 5, Sonnet 5.5 and Haiku 5.5; GPT-6 Astra, Sol and Luna, GPT-6.1 Sol, and GPT-6.2 Sol and Astra — but not their `-pro` variants[^pydantic-thinking-docs-2026] |

## When it falls back to a request-level setting

Every other API and model gets the new level as the request-level setting, which re-processes the conversation[^pydantic-thinking-docs-2026]. Four named cases force that path even where the API would otherwise take a delta[^pydantic-thinking-docs-2026]:

- A provider-specific effort setting is in use — `openai_reasoning_effort`, `anthropic_effort` or `openrouter_reasoning`.
- OpenAI truncation (`openai_truncation='auto'`) or server-side compaction is on.
- Anthropic thinking is not adaptive, for example `between_tools` on Claude Sonnet 5.5 or `disabled` on Claude Haiku 5.5.
- The change is to or from `True` or `False`, which names no effort level.

The cache implication is the operational point: on any of those paths the provider sees a different request-level effort and starts the conversation again, so a plan-then-verify loop that raises effort between turns pays full input price on the second turn[^pydantic-thinking-docs-2026]. This is the same cache key described in [prompt caching](pydantic-ai-prompt-caching.md).

## The record it leaves in history

Each change is recorded as a `ModelSettingsDeltaPart` at the end of the request it applies to, and the first request that names an effort level records one too[^pydantic-thinking-docs-2026]. The part stores the changed settings under their unified `ModelSettings` keys — `{'thinking': 'high'}` — and `RecordedModelSettings` lists which keys can be recorded, which today is only the thinking effort level[^pydantic-thinking-docs-2026]. Each model adapter sends the keys it can change mid-conversation in place and the rest as request-level settings, so the record is a portable description of intent rather than a provider payload[^pydantic-thinking-docs-2026].

A later run that continues from `message_history` reads those parts to learn which effort the conversation started with and which changes to send again, which is why the record is kept rather than collapsed into the newest value[^pydantic-thinking-docs-2026]. Two adapters handle it explicitly: the Vercel AI adapter carries the parts through the client, while the AG-UI adapter streams and dumps them as `pydantic_ai_model_settings_delta` activity messages, which `@ag-ui/client` does not send back — so a UI-held history loses the mid-conversation change[^pydantic-thinking-docs-2026]. See [conversation state](pydantic-ai-conversation-state.md) for the history object that keeps them.

## Limits

- One vendor reference page with no publication date or Pydantic AI version, so the route table, the beta header name and the model lists are version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-thinking-docs-2026].
- The cache cost is stated by the docs as a consequence of the effort being in the provider's cache key; no cache-hit or token measurement is given, and none was reproduced here.
- The AG-UI and Vercel adapter behaviour is described in one clause each; the `@ag-ui/client` round-trip was not exercised, and the activity message shape was not read.
- The `gpt-6-astra` alias in the sample appears nowhere else in this wiki, and nothing was installed or run — every claim is **Reported**.

## Relationships

- **Changes** the effort set through [thinking and reasoning control](pydantic-ai-thinking.md).
- **Conflicts with** [prompt caching](pydantic-ai-prompt-caching.md) on the fallback path: a request-level effort is a new cache key, so the conversation is processed again.
- **Recorded in** [conversation state](pydantic-ai-conversation-state.md), whose persisted messages carry the `ModelSettingsDeltaPart`s a later run replays.
- **Forced by** a provider-specific setting from [reasoning settings per provider](pydantic-ai-reasoning-settings-per-provider.md), which is the first of the four fallback cases.
- **Depends on** the capability's `get_model_settings` hook described in [capability primitive](pydantic-ai-capability-primitive.md) for per-step changes.

[^pydantic-thinking-docs-2026]: Pydantic Docs, "Thinking", <https://pydantic.dev/docs/ai/capabilities/thinking/>, 4,279 words as declared and 4,325 by local `wc -w`, no publication date, author or Pydantic AI version named; local capture `raw/capabilities/thinking/index.md`, content digest sha256:d7e5d288. §"Changing effort mid-conversation" (raw lines 92–126) for the per-run and per-step seams, the `effort_mid_conversation.py` two-turn sample, the prompt-cache key statement, the OpenAI Responses `configuration_update`, Anthropic's effort-only `system` entry and `mid-conversation-output-config-2026-07-01` beta with its model and client list, OpenRouter's content-less `system` message and model list, the four request-level fallback cases, `ModelSettingsDeltaPart` placement and key shape, `RecordedModelSettings`, the adapter split, the Vercel AI passthrough and the AG-UI `pydantic_ai_model_settings_delta` activity messages. Evidence class: **Reported** — vendor documentation; no run, provider request or cache measurement was performed.
