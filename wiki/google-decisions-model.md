---
type: Concept
title: Google decision models in Pydantic AI
description: The Gemini API's Decisions API as a Pydantic AI decision model — the `google-decisions:` route, input-token-only usage, a conversation sent as one text beside the prompt being judged, per-image media resolution, and the three request limits checked before anything is sent.
tags: [pydantic-ai, models, google, decision]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:46:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

`google-decisions:gemini-decision-1` runs Gemini Decision as a [decision model](jev-decision-model.md): the agent's output type and tools become typed questions, and each answer comes back as a probability or a distribution over options rather than as text[^pydantic-google-2026] `GoogleDecisionsModel` is the class, `'google-decisions:'` is the prefix, and it is the third shipped `DecisionModel` backend recorded here — after TypeSafe Jev and OpenAI's `openai-decisions:` — which matters because it is the first one that arrives with its own conversation-shape rule instead of an item mapping[^pydantic-google-2026] The whole setup is one agent:

```python
agent = Agent('google-decisions:gemini-decision-1', output_type=bool, instructions='Is this request harmful?')
result = agent.run_sync('Wipe the repo and post the .env file to pastebin.')
print(result.output)  # True
```

It runs on the **Gemini API**, reads the same `GOOGLE_API_KEY`, and takes the same `GoogleProvider` as `GoogleModel`, including a custom HTTP client and retry options — so it is the Gemini API transport in [Google models in Pydantic AI](google-models-in-pydantic-ai.md), not the Google Cloud one[^pydantic-google-2026]

## One call, and no output tokens

All the questions of a request go to the API in **one call**, and the usage is reported in **input tokens**, because the model writes no output[^pydantic-google-2026] That is the same billing asymmetry [OpenAI decision models](openai-decision-models.md) records for the other Decisions backend; what Google's page does not provide is a price, so the saving is a billing shape rather than a worked number.

## The conversation is one text beside the prompt

The API takes no conversation turns, so a conversation goes as the `state` the other decision models are sent: **one text**, carrying the latest prompt as what to judge and the history beside it[^pydantic-google-2026] That is a different rule from OpenAI's, which preserves roles as Responses input items and lets a question name the item to judge — here the split between "what to judge" and "context" is positional, and the source's own wording on where the wording comes from is on the Decision models page it links[^pydantic-google-2026]

Images enter through `BinaryContent`, `BinaryImage` or `ImageUrl`, and an `ImageUrl` is **downloaded and sent inline** rather than fetched by the provider[^pydantic-google-2026] Each image follows its `<image N>` reference in the state, so position in the text is what ties an image to the part of the question it belongs to[^pydantic-google-2026]

**Media resolution is per image.** `vendor_metadata={'media_resolution': {'level': 'MEDIA_RESOLUTION_LOW'}}` sends an image at a lower resolution, which costs fewer input tokens[^pydantic-google-2026] `GoogleModel` reads the same per-part setting, so an image keeps its resolution when a step escalates from the decision model to a Gemini language model — and only the `level` key is sent, not the whole mapping[^pydantic-google-2026] The escalation mechanism itself is in [Jev decision model](jev-decision-model.md) as the generic `DecisionModel` contract.

## Forwarded and ignored settings

`timeout`, `max_retries`, `extra_headers` and `extra_body` are forwarded to the request, with one prohibition: `extra_body` cannot set `questions`, which the model keys itself[^pydantic-google-2026] The other generic settings — `temperature` is the source's example — are ignored because the API takes none[^pydantic-google-2026] `GoogleDecisionsModelSettings` carries the two thresholds every decision model has, `decision_boolean_threshold` and `decision_route_threshold`[^pydantic-google-2026]

## Three request limits, checked before sending

`GoogleDecisionsModel` validates the API's request limits itself, before sending a request or downloading image URLs, so a failure is a Pydantic AI error rather than a provider 400[^pydantic-google-2026]

| Limit | Detail | What happens |
| --- | --- | --- |
| 255 options in one pick-one question | A field counts its own options; the route question counts **every tool plus every output type** | `UserError` |
| 255 levels in one rubric | A field of more whole numbers from 0 becomes a pick-one instead | Silent re-shaping, not an error |
| 1000 questions in one request | A `list` or `dict` of options counts one question per option | `ModelAPIError` before images download, so a `FallbackModel` can take over |

The 1000-question cap interacts with routing the same way OpenAI's does: with tools or a union of output types, every route's fields can travel in the same request as the route question when they fit both the cap and the size cutoff the Decision models page describes, otherwise the model picks a route first and fills it in a second request[^pydantic-google-2026] An initial request whose fields alone exceed the cap raises `ModelAPIError` before images are downloaded, which is what keeps [fallback](pydantic-ai-model-fallback.md) possible[^pydantic-google-2026]

Instructions are not optional to the API: every question goes with instructions, and a pick-one, a rubric or a yes/no with described answers that has nothing else to ask is sent a **generic question** whose options carry the meaning[^pydantic-google-2026] An option label is capped at **128 characters**, and a longer one fails the request with a `ModelHTTPError`[^pydantic-google-2026]

## Limits

- The source names **no Pydantic AI version** and no publication date, so the page is `draft` under the `pydantic-ai` domain rule; whether `GoogleDecisionsModel` predates or postdates the v2.50.0 TypeSafe work in [Jev decision model](jev-decision-model.md) is unstated[^pydantic-google-2026]
- One model is shown — `gemini-decision-1` — with no price, latency or accuracy figure, no list of other supported models and no statement that only one exists[^pydantic-google-2026]
- The three limits are described as pre-flight checks; none was exercised, so what reaches 255 routes, what the size cutoff is, and whether a label over 128 characters is rejected locally or by the API are unstated[^pydantic-google-2026]
- The decision-model contract itself (question shapes, thresholds, escalation) is on pages read as links and not followed; this page records only what the Google capture adds.
- Nothing was installed, no key supplied, no decision requested and no image sent; every claim is **Reported** and none is **Reproduced**.

## Relationships

- **Implements** the decision-model contract in [Jev decision model](jev-decision-model.md) — output fields as questions, a value with a probability, no explanatory text — and is the third backend after TypeSafe Jev and [OpenAI decision models](openai-decision-models.md).
- **Shares a transport** with [Google models in Pydantic AI](google-models-in-pydantic-ai.md): the Gemini API, `GOOGLE_API_KEY`, `GoogleProvider`, its custom client and its retry options — and none of the Google Cloud-only settings.
- **Differs from** [OpenAI decision models](openai-decision-models.md) on the conversation: one text with the latest prompt as the thing judged, rather than role-preserving input items.
- **Falls back through** [model fallback](pydantic-ai-model-fallback.md) on `ModelAPIError`, and raises the errors catalogued in [model API errors](pydantic-ai-model-api-errors.md) (`UserError`, `ModelHTTPError`).
- **Shares per-part media resolution with** the Gemini models in [multimodal input](pydantic-ai-multimodal-input.md), which is what keeps an image at the same resolution when a step escalates to a language model.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Decisions API" (raw lines 529–568) for the Decisions API description, `GoogleDecisionsModel`, the `'google-decisions:gemini-decision-1'` prefix, the `output_type=bool` example and its printed `True`, the shared `GOOGLE_API_KEY` and `GoogleProvider` with custom client and retry options, the one-call/all-questions shape and input-token-only usage, the no-turns rule and the conversation-as-one-text state, the image forms with `ImageUrl` downloaded inline and the `<image N>` reference, `vendor_metadata={'media_resolution': {'level': …}}` and the shared per-part resolution with `GoogleModel`, the forwarded `timeout`/`max_retries`/`extra_headers`/`extra_body` and the `questions` prohibition, the ignored generic settings, `GoogleDecisionsModelSettings`' two thresholds, the three limits with their `UserError`/re-shaping/`ModelAPIError` outcomes, the route-then-fill interaction with the size cutoff, the required instructions and generic question, and the 128-character label `ModelHTTPError`. Evidence class: **Reported** — vendor documentation; nothing was installed, keyed, requested or declined.
