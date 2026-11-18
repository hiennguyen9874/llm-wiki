---
type: Concept
title: Google thinking levels in Pydantic AI
description: How a Gemini or Gemma effort setting resolves to a native thinking level in Pydantic AI — the snapping rule and profile override, the Gemini 4 and Gemma 4 level sets, the models that cannot turn thinking off, and where a thinking_budget is rejected.
tags: [pydantic-ai, models, google, thinking, model-settings]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:42:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

Google takes thinking two ways in Pydantic AI: the provider-agnostic `Thinking` capability, and Google's own `google_thinking_config` for the cases the unified switch does not cover[^pydantic-google-2026] What makes the Google route worth its own page is that **the accepted levels differ per model**, so an effort value is not a promise — Pydantic AI resolves each model's supported levels from Google's documented thinking table and snaps a requested effort to the nearest supported one[^pydantic-google-2026] The unified vocabulary, the seven effort values and the Gemini 2.5 budget arithmetic are in [thinking and reasoning control](pydantic-ai-thinking.md); this page is the Google half that the provider table defers to.

## Two entry points

The capability is the portable one and needs no Google vocabulary[^pydantic-google-2026]:

```python
from pydantic_ai.capabilities import Thinking

agent = Agent('google:gemini-3.8-flash', capabilities=[Thinking(effort='medium')])
```

The native one is `GoogleModelSettings.google_thinking_config`, taking `include_thoughts` and `thinking_level` as a `ThinkingLevel` value such as `ThinkingLevel.MEDIUM`[^pydantic-google-2026] The source presents the native config as the "advanced usage" path without saying how it combines with a `Thinking` capability on the same agent — precedence between the two is unstated, so treat it as unpinned rather than as "native wins"[^pydantic-google-2026]

## Snapping, and the profile that declares a level set

Snapping has a floor given by the resolved profile. For a model id Google's table does not cover, declare the accepted levels with `GoogleModelProfile.google_thinking_levels`, whose default is **every level but `xhigh`**; a requested effort the model does not support then resolves to the nearest one it does[^pydantic-google-2026] That default explains the general rule without a table entry: a model nobody described is assumed to take everything below the top level.

## The Gemini 4 family

`gemini-4-argon`, `gemini-4-carbon` and `gemini-4-hydrogen` support `low`, `medium` and `high`, so both `thinking=False` and `'minimal'` resolve to **`low`**, the floor of the family[^pydantic-google-2026] `gemini-4-hydrogen` additionally supports `xhigh`, its deepest reasoning level, which `thinking='xhigh'` and `'max'` select; on the two models without it, both resolve to `high`[^pydantic-google-2026]

The top level is sent even though the client library does not know it: the `google-genai` SDK's `ThinkingLevel` enum has no `XHIGH`, so the SDK warns `XHIGH is not a valid ThinkingLevel` and sends the level anyway[^pydantic-google-2026] A warning here is therefore not a failure.

One family member rejects the budget form on one transport: on **Google Cloud**, `gemini-4-argon` rejects a `thinking_budget` inside `google_thinking_config` with a **400**, so that model has to be configured with `thinking_level` there[^pydantic-google-2026]

## Gemma 4

`gemma-4-31b-it` and `gemma-4-26b-a4b-it` support only `minimal` and `high` **on the Gemini API**, and reject any `thinking_budget`[^pydantic-google-2026] The mapping that follows is coarse in both directions: `thinking=False` and `'low'` resolve to `minimal`, and `'medium'` and above resolve to `high`[^pydantic-google-2026] Without a `thinking` setting at all, Gemma 4 thinks by default there[^pydantic-google-2026]

## The models that cannot turn thinking off

`thinking=False` turns thinking off where the model allows it[^pydantic-google-2026] The Pro models do not, so Pydantic AI asks for the least they allow instead[^pydantic-google-2026]:

| Model | What `thinking=False` sends |
| --- | --- |
| Gemini 3 Pro, on the Gemini API | Its lowest thinking level — `low` on `gemini-3.1-pro-preview` |
| Gemini 2.5 Pro | Its minimum `thinking_budget` of 128 tokens |
| Gemini 3 Pro, on Google Cloud | `thinking_budget=0`, which that transport accepts and the Gemini API rejects — a real off switch |

In the first two cases the response is not asked to return the thoughts, so "off" reads as "as little as this model will do" rather than as a disable[^pydantic-google-2026]

## Per-model exceptions worth remembering

- **`gemini-3.1-flash-image`** is documented with `minimal` and `high` only, but **only the Gemini API enforces those**, so Pydantic AI applies them only when the client talks to the Gemini API and leaves Vertex AI on the default levels[^pydantic-google-2026] Which API a client talks to is read from the client, not from the provider name — the same rule that decides Files API versus `gs://` references in [image generation operations](pydantic-ai-image-generation-operations.md).
- **The Gemini 3 image models are thinking models.** Thinking is always on and billed, and its tokens are included in the result's `usage`[^pydantic-google-2026] Nothing can be set to avoid that cost.

## Limits

- The source names **no Pydantic AI version** and no publication date, so this page's level sets and snapping rules are version-unknown and it is `draft` under the `pydantic-ai` domain rule[^pydantic-google-2026]
- The level sets are the vendor's statement of what Pydantic AI resolves from Google's thinking table; the table itself is referenced by link and not reproduced, so a model not named here — `gemini-3.8-flash` among them — has no stated level set[^pydantic-google-2026]
- Precedence between a `Thinking` capability and `google_thinking_config` on the same agent is unstated (see above), and the source does not say what `Thinking()` with no argument sends on Google.
- No model was called and no thinking config sent: the 400 for a budget on Google Cloud, the `XHIGH` warning and every snapping example are **Reported**, not observed[^pydantic-google-2026]

## Relationships

- **Implements the Google rows** of [thinking and reasoning control](pydantic-ai-thinking.md), which holds the unified vocabulary, the Gemini 2.5 budget mapping and the reasoning-token accounting, and of the Google section of [reasoning settings per provider](pydantic-ai-reasoning-settings-per-provider.md).
- **Configures** models reached through [Google models in Pydantic AI](google-models-in-pydantic-ai.md), which owns the providers, the two transports and the settings object.
- **Interacts with** [Anthropic request constraints](anthropic-request-constraints.md) by contrast: a forced tool choice there stops Claude thinking, while on Google the constraint is which level the model accepts at all.
- **Applies to** the image models described in [image generation operations](pydantic-ai-image-generation-operations.md), where thinking is billed on every generated image.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Configure thinking" (raw lines 328–364) for the `Thinking(effort='medium')` example, `google_thinking_config` with `include_thoughts`/`thinking_level`, the resolve-and-snap rule, the `gemini-3.1-flash-image` Gemini-API-only exception, `GoogleModelProfile.google_thinking_levels` and its default, the three `gemini-4-*` models and their levels, `gemini-4-hydrogen`'s `xhigh`, the `XHIGH` SDK warning, the Google Cloud 400 on `thinking_budget` for `gemini-4-argon`, the two Gemma 4 ids with `minimal`/`high` only and their default thinking, the Pro-model floors (`low` on `gemini-3.1-pro-preview`, 128 tokens for Gemini 2.5 Pro, `thinking_budget=0` on Google Cloud) and the absent `include_thoughts`; §"Image generation" (278–300) for the always-on billed thinking of the Gemini 3 image models. Evidence class: **Reported** — vendor documentation; no model was constructed, configured or called.
