---
type: Concept
title: OpenAI decision models in Pydantic AI
description: OpenAI's Decisions API as a Pydantic AI decision model — the `openai-decisions:` route, input-token-only billing, the Responses-shaped conversation mapping, four request limits rejected before sending, and how a declined question fails the run.
tags: [pydantic-ai, models, openai, decision]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:22:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
---

`openai-decisions:gpt-6-luna` runs a GPT model as a decision model: the agent's output type and tools become typed questions, and the answer comes back as a value plus a probability or a distribution rather than as text[^pydantic-openai-2026] `OpenAIDecisionsModel` is the third OpenAI dialect and the second shipped implementation of the [DecisionModel contract](jev-decision-model.md), which until this page was evidenced only by TypeSafe Jev — and it is the first OpenAI material in the wiki to name an OpenAI route rather than an API surface shared with Responses. It reads the same `OPENAI_API_KEY` and takes the same `OpenAIProvider`, custom client included, so `agent = Agent('openai-decisions:gpt-6-luna', output_type=bool, instructions='Is this request harmful?')` is the whole setup[^pydantic-openai-2026] Only `gpt-6-luna` is currently supported, a model the Responses API also serves, which is why the `'openai-decisions:'` prefix rather than the model name is what selects it[^pydantic-openai-2026]

## One request, input-token billing

All the questions of a request go to the API in one call, and usage is reported in tokens as on the Responses API[^pydantic-openai-2026] The billing asymmetry is the reason to care: OpenAI bills only input tokens on this API, with no cache-read or cache-write charges[^pydantic-openai-2026] The `cost` Pydantic AI reports comes from genai-prices' prices for `gpt-6-luna`, which price cached input separately, so the reported figure can differ from the bill when the API reports cached tokens — the same class of gap the Jev capture recorded for a missing price entry[^pydantic-openai-2026]

## The conversation arrives as Responses items

Where other decision models are sent a `state`, OpenAI's Decisions API is sent the conversation as Responses input items, with roles preserved: system prompts, user prompts, answers, and tool calls with their results keep their roles, so a question can name what to judge, such as "the user's latest request", where another backend would point at the state's `text`[^pydantic-openai-2026] Item types the API cannot take are degraded to text rather than dropped[^pydantic-openai-2026]:

| Item | What the API receives |
| --- | --- |
| Thinking | Text on the assistant channel, wrapped in thinking tags |
| A tool result whose call is no longer in history | A framed `<pyai:tool_result>` on the user channel |
| An image from an assistant response | A user message, right after the assistant's `<image N>` reference to it |
| Retry feedback | A `developer` message, so it isn't read as a newer request |
| A request-side `CompactionPart` summary | Framed user text |
| A lone prompt with no history | Plain text |

Images come in through `BinaryContent`, `BinaryImage` or `ImageUrl`, and an `ImageUrl` is downloaded and sent inline as a data URL[^pydantic-openai-2026] Images in user input and in message history — including assistant file parts and tool or native-tool images — are sent where they appear in the conversation, while instructions remain separate questions; `vendor_metadata={'detail': 'high'}` sets the detail level, accepting `'low'`, `'high'`, `'auto'` and `'original'`, and survives the URL download[^pydantic-openai-2026]

`timeout`, `extra_headers` and `extra_body` are forwarded to the request and the other generic settings such as `temperature` are ignored[^pydantic-openai-2026] `OpenAIDecisionsModelSettings` carries the two thresholds every decision model has, `decision_boolean_threshold` and `decision_route_threshold`, which is the same concept the TypeSafe capture records as `typesafe_boolean_threshold` in [Jev structured scoring judge](jev-structured-scoring-judge.md) (**Synthesis**: this page names only the OpenAI fields; that the two are the same provider-neutral threshold is inferred from both governing yes/no confidence per model).

## Four limits, checked before the request

`OpenAIDecisionsModel` validates the API's request limits itself, before sending a request or downloading image URLs, so the failure is a Pydantic AI error rather than a provider 400[^pydantic-openai-2026]

| Limit | Detail | What happens |
| --- | --- | --- |
| 255 options in one pick-one question | A field counts its own options; the route question counts every tool plus every output type | `UserError` |
| 10 levels in one rubric | A field of eleven or more whole numbers from 0 becomes a pick-one instead | Silent re-shaping, not an error |
| 200 questions in one request | A `list` or `dict` of options counts one question per option | `ModelAPIError` before images download, so a `FallbackModel` can take over |
| 128 images in one request | Images in history and tool results count | `ModelAPIError` before images download |

The 200-question cap interacts with routing. With tools or a union of output types, every route's fields can travel in the same request as the route question when they fit both the cap and the documented size cutoff; otherwise the model picks a route first and the fields are filled in a second request[^pydantic-openai-2026] A selected route whose fields exceed the cap raises `UnfillableRoute` before filling, again so a [fallback model](pydantic-ai-model-fallback.md) can take over — but an API error during an otherwise valid fill still fails the run rather than falling back[^pydantic-openai-2026]

## Declines fail the run

The model can decline a question, for instance one asking it to infer a customer's race or a disability[^pydantic-openai-2026] A declined question fails the run with a `ContentFilterError`, even when the model answered the other questions, or when the declined question belongs to a route the model did not pick; a question declined while filling a route the model already selected fails with an `UnexpectedModelBehavior` naming the route[^pydantic-openai-2026] There is no partial-answer mode: one decline discards the response. The error classes themselves are catalogued in [model API errors](pydantic-ai-model-api-errors.md).

## Limits

- The source names **no Pydantic AI version** and no publication date, so the page is `draft` under the `pydantic-ai` domain rule; whether `OpenAIDecisionsModel` predates or postdates the v2.50.0 TypeSafe work recorded in [Jev decision model](jev-decision-model.md) is unstated[^pydantic-openai-2026]
- One model only — `gpt-6-luna` — with no price, latency or accuracy figure, and no comparison against a language model on the same question, so the input-token-only argument is a billing rule without a worked cost.
- The four limits are pre-flight checks described as such; none was exercised, so the shapes that trigger them (which tool-plus-output combination reaches 255 routes, what the "size cutoff" is) stay undescribed.
- Nothing was installed, no key supplied, no decision requested and no decline observed; every claim is **Reported**, and the `cost` divergence from genai-prices is unquantified.

## Relationships

- **Implements** the decision-model contract in [Jev decision model](jev-decision-model.md): output fields as questions, a value with a probability, no explanatory text.
- **Shares a route** with [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md), which covers the provider, client and the other two dialects.
- **Traces as** any decision model does — the `decide` span and Classifier panel in [Logfire decision tracing](logfire-decision-tracing.md) — since the span work is on the framework side, not the backend's.
- **Falls back through** [model fallback](pydantic-ai-model-fallback.md) on `ModelAPIError` and `UnfillableRoute`, but not on a valid fill that the API then rejects.
- **Differs from** [Jev structured scoring judge](jev-structured-scoring-judge.md) on what is billed: input tokens only here, with no cache charges, against Jev's per-question pricing model.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, 7,634 words as declared and 7,648 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Decisions API" (lines 690–733) for the Decisions API description, `OpenAIDecisionsModel`, the `'openai-decisions:gpt-6-luna'` prefix and why the prefix selects the route, the `output_type=bool` example and its printed `True`, the shared `OPENAI_API_KEY` and `OpenAIProvider`, the one-call/all-questions shape, input-token-only billing, the genai-prices cost caveat, the Responses-input-items mapping and the degradation table, the image input forms and `vendor_metadata={'detail': …}`, the forwarded and ignored settings, `OpenAIDecisionsModelSettings` and its two thresholds, and the four limits with their `UserError`/`ModelAPIError`/`UnfillableRoute` outcomes; line 733 for the decline behaviour and its `ContentFilterError`/`UnexpectedModelBehavior`. Evidence class: **Reported** — vendor documentation; nothing was installed, keyed, requested or declined.
