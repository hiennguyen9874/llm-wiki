---
type: Concept
title: Pydantic AI Gateway
description: Logfire's bring-your-own-key gateway as a routing and metering layer — named provider routes, native protocol passthrough for models that are not chat models, and what it adds on top of a provider's own API.
tags: [pydantic-ai, gateway, routing, operations]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:12:00Z }
stale_after: 2027-03-25
sources:
  - id: jev-gateway-2026
    resource: ../raw/jev-pydantic-ai-gateway/index.md
    scope: ../raw/jev-pydantic-ai-gateway/
    kind: article
    revision: sha256:cd20eca277244de9ee4f24d189acc0b1cde2b11ee3bc5796fc8422bae7e11c6d
    title: "TypeSafe Jev in Pydantic AI Gateway"
---

Pydantic AI Gateway is a proxy inside Pydantic Logfire that takes a provider credential into a registry and exposes it behind **one gateway key**, metering every request into the same spend view and limits as the language models[^jev-gateway-2026] Its routing model is the durable part: a provider is registered in the UI under a route name you choose, requests reach it at `/proxy/<route>`, and its own protocol is forwarded natively instead of being translated into the OpenAI chat format — which is what lets a classification model with its own API sit behind the same gateway as a chat model[^jev-gateway-2026] The gateway is additive rather than a re-pricing: the source states it does not change Jev's cost or how fast it answers, so the argument for using it is operational[^jev-gateway-2026] Everything here is Pydantic's own account of one provider; no provider was connected and no request was sent in this ingest.

## Registering a provider

The provider lives in Logfire under **Gateway → Providers**, where **Add a bring-your-own-key (BYOK) provider** runs a three-step stepper — **Provider type**, **Connect provider**, **Name your provider**[^jev-gateway-2026] The provider-type screen groups its choices as Popular (Anthropic, Google AI Studio, OpenAI), Cloud platforms (AWS Bedrock, Azure Foundry, Google Vertex AI) and More providers (Custom, Doubleword, Groq, Hugging Face, Mistral, Modal, Ollama, TypeSafe AI) behind a search field — labels read off the screenshot, not from prose[^jev-gateway-2026]

Two details on the key step matter beyond this provider:

- The key field is labelled **Encrypted before storage**, and the form states that the Gateway asks the provider for its models with those credentials, so a refused credential is caught at setup rather than on the first request[^jev-gateway-2026]
- The name you give the provider becomes the **route name** in the URL, which is why `typesafe` appears in every endpoint below[^jev-gateway-2026]

The **Connect** dialog then defaults to `jev-latest` and produces a snippet with the gateway key already filled in[^jev-gateway-2026]

## Native protocol instead of chat translation

Jev speaks TypeSafe's System One API rather than the OpenAI chat format, so the Gateway forwards it natively; the documented request puts the model, the judged material in `state`, and one entry per question in `questions` on a provider-specific endpoint[^jev-gateway-2026]

```bash
curl https://gateway-us.pydantic.dev/proxy/typesafe/v1/systemone \
  -H "Authorization: Bearer $PYDANTIC_AI_GATEWAY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "jev-latest",
    "state": "Help! My payouts have been failing for 3 days.",
    "questions": {
      "is_urgent": { "type": "noul", "instructions": "Does this convey urgency?" }
    }
  }'
```

The same endpoint shape works from TypeSafe's own SDK by pointing `base_url` at `https://gateway-us.pydantic.dev/proxy/typesafe`, so adopting the gateway does not require a different client library[^jev-gateway-2026] Two limits follow from the protocol rather than from policy: streaming requests are refused before they are forwarded, because System One answers in one response, and Jev is absent from the chat playground because there is nothing to chat with[^jev-gateway-2026]

## What the gateway adds

Against calling TypeSafe directly, the source claims exactly three additions for this provider[^jev-gateway-2026]:

| Addition | Scope |
| --- | --- |
| Cost and usage | Every request is metered, so Jev appears in the same spend view and limits as the language models |
| Guardrails | Input guardrails run on `state`, the instructions and the criteria before the request goes upstream |
| One key | The application holds a gateway key instead of a TypeSafe key |

What the source does not say is as consequential as what it does: it gives no gateway fee or markup, no separate rate limit, no region list beyond the `gateway-us` host in the examples, and no retry or failover behaviour[^jev-gateway-2026] The claim that Jev's cost and latency are unchanged is therefore a statement about the provider bill, not evidence that the gateway is free[^jev-gateway-2026]

## Reaching it from Pydantic AI

Pydantic AI can run an agent on Jev with `TypeSafeModel`, and the gateway sits underneath as a base URL change: install `pydantic-ai-slim[typesafe]`, construct `TypeSafeProvider` with the **gateway** key and `base_url='https://gateway-us.pydantic.dev/proxy/typesafe'`, then pass `TypeSafeModel('jev-latest', provider=provider)` to the agent[^jev-gateway-2026] Each field of the output type becomes a question, so the request shape is the same one described on [Jev structured scoring judge](jev-structured-scoring-judge.md) — a `Ticket` output type with `urgent: bool` and a four-value `area` literal produces `urgent=True area='billing'` for a duplicate-charge message[^jev-gateway-2026]

One tension is worth recording rather than resolving. The Connect dialog offers the moving alias `jev-latest`, while the evals design pins `typesafe:jev-1.13.0` precisely because a moving alias changes the judge between experiments[^jev-gateway-2026] **Synthesis:** the two defaults serve different jobs — the alias for getting a first request working, a pinned version for scores that will be compared across runs.

## Limits

- Single vendor article by a Pydantic developer, published 2026-09-25; nothing was executed, no key was supplied, no provider was connected, and no gateway request was made[^jev-gateway-2026]
- No Pydantic AI, Logfire or Gateway version is named. The API names — `TypeSafeModel`, `TypeSafeProvider`, the `typesafe` extra, `jev-latest` — are therefore dated to the article and unconfirmed against the wiki's v2.59.0-era release page, which is why this page is `draft` under the `pydantic-ai` domain rule[^jev-gateway-2026]
- Only TypeSafe is documented. The other provider types on the screenshot are names in a grid; how any of them handle protocol passthrough, key validation or metering is not described.
- Gateway pricing, its own rate limits, regional endpoints, retry and failover, guardrail configuration and pricing, and what the gateway retains of a request are all absent from the source.
- The screenshot labels are **Observed** in the images; the surrounding workflow, the key-validation guarantee and every cost statement are **Reported** prose.

## Relationships

- **Routes** [Jev structured scoring judge](jev-structured-scoring-judge.md): the same TypeSafe model and question-set design, reached through one metered key instead of TypeSafe credentials.
- **Meters into** the same Logfire account whose tracing surface is [Pydantic AI observability](pydantic-ai-observability.md) — traces come from instrumentation, spend and limits from the Gateway meter.
- **Depends on** provider-native protocols rather than the OpenAI chat format, so it is the alternative to per-provider credentials for models outside the chat shape.
- **Routes** [realtime voice sessions](pydantic-ai-realtime-voice.md) named as `gateway/<provider>:<model>`, putting per-audio-token or per-minute realtime spend under the same key and limits as text.

[^jev-gateway-2026]: Marcelo Trylesinski, "TypeSafe Jev in Pydantic AI Gateway", Pydantic, published 2026-09-25T09:00Z, 565 words as declared; local capture `raw/jev-pydantic-ai-gateway/index.md`, content digest sha256:cd20eca2. §"Set it up" (raw lines 17–71) for the Gateway/Providers path, the TypeSafe provider choice, the key step with its model-list validation, the provider-name-as-route rule, the `jev-latest` Connect default, the System One endpoint and request body, and the SDK `base_url`; §"What you get from the Gateway" (lines 73–82) for metering into the spend view and limits, guardrails over `state`/instructions/criteria, the single gateway key, the unchanged cost and latency, and the refusal of streaming plus the chat-playground absence; §"Using it from Pydantic AI" (lines 84–117) for `pydantic-ai-slim[typesafe]`, `TypeSafeProvider` with the gateway key and base URL, `TypeSafeModel('jev-latest', ...)`, output-type fields becoming questions, and the printed `urgent=True area='billing'`. Attachments inspected: `assets/typesafe-provider-type.png` for the three-step stepper, the provider-type grouping (Popular, Cloud platforms, More providers) and its labels; `assets/typesafe-api-key.png` for "Encrypted before storage", the "we ask the provider for its models" copy and the **Test & continue** button. Evidence class: **Reported**, **Observed** only for screenshot labels.
