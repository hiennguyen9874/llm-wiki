---
type: Concept
title: Pydantic AI provider SDK retries
description: The retry layer inside each provider SDK — how many attempts OpenAI, Anthropic, Google, Bedrock and the rest make by default, how ModelSettings max_retries sets it per request, and how that setting interacts with a fallback chain.
tags: [pydantic-ai, models, reliability, retries]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:20:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-retries
    resource: ../raw/core-concepts/retries/index.md
    scope: ../raw/core-concepts/retries/
    kind: documentation
    revision: sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56
    title: "Retries"
---

**Reported, Pydantic AI version unspecified:** between the HTTP transport and the model sits the provider SDK's own client, which re-issues a failed request before your code hears about it — its defaults, retryable errors and configuration differ by provider, so the attempt budget has to be sized from the client you actually use[^pydantic-docs-retries] A retrying transport sits *below* this client, so the two stack rather than replace each other: configuring one never disables the other[^pydantic-docs-retries] Pydantic AI exposes exactly one portable control over the layer, the per-request `ModelSettings['max_retries']`, and it cannot be honoured by every SDK[^pydantic-docs-retries]

## One setting, three scopes

`ModelSettings['max_retries']` sets how many times the SDK client retries one request without your building the client yourself; `0` makes a single attempt[^pydantic-docs-retries] The SDK still decides which failures it retries and how long it waits between them[^pydantic-docs-retries] Like any model setting it applies per model, per agent or per run[^pydantic-docs-retries]

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', model_settings={'max_retries': 0})
```

Set it to `0` whenever another layer owns retrying, so the budget stays the one configured there instead of being multiplied by the SDK's own[^pydantic-docs-retries] The documented cases are a retrying transport on the HTTP client, a durable engine's retry policy, and a fallback model that should move to its next candidate as soon as one fails; `RetryOnModelErrors` (in [same-model retries](pydantic-ai-retry-on-model-errors.md)) sets it to `0` itself[^pydantic-docs-retries]

## Interaction with a fallback chain

With `ModelFallback`, a `max_retries` set on the agent or the run applies to **every** model in the chain and takes precedence over each model's own settings[^pydantic-docs-retries] The way to keep SDK retries on the last model — the one with nothing to fall back to — is therefore to set the value on the other models instead[^pydantic-docs-retries]

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import ModelFallback
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel

agent = Agent(
    OpenAIChatModel('gpt-6.1-sol', settings={'max_retries': 0}),
    capabilities=[ModelFallback(AnthropicModel('claude-sonnet-5-5'))],
)
```

The same rule holds for a `FallbackModel`'s candidates: the wrapper's models carry their own settings, or the surrounding agent's setting wins[^pydantic-docs-retries] [Model fallback](pydantic-ai-model-fallback.md) owns the trigger policy and failed-attempt accounting this setting only sizes.

## Default attempts per provider

| Model | Attempts by default | `max_retries` supported | Notes |
| --- | --- | --- | --- |
| OpenAI and the model classes built on it | 3 | Yes | Full support, including an `AsyncAzureOpenAI` client[^pydantic-docs-retries] |
| Anthropic | 3 | Yes | Full support, including `AsyncAnthropicBedrock`, `AsyncAnthropicVertex` and `AsyncAnthropicFoundry`[^pydantic-docs-retries] |
| Groq | 3 | Yes | Full support[^pydantic-docs-retries] |
| Cohere | 3 for status 408, 409, 429 and 5xx; 1 for a connection error or timeout | Yes | Full support[^pydantic-docs-retries] |
| Google | 1 unless the provider has `retry_options` | Yes | Limited: keeps the delays and status codes of the provider's `retry_options`, or the SDK's defaults when those are unset; on `google-genai` 2.31.0 and later a later request of a streamed long decode is sent 3 more times regardless, and a connection that cannot open or a pre-response timeout is retried up to `max_retries` on each of those[^pydantic-docs-retries] |
| Mistral | 1 unless the client has a `retry_config` | Yes | Limited: only `0` has meaning — the SDK bounds retries by elapsed time rather than count, so `0` disables a client-side `retry_config` and every other value is ignored[^pydantic-docs-retries] |
| TypeSafe | 3 | Yes | Limited: the request's other `RetryPolicy` options are the SDK defaults, not the client's[^pydantic-docs-retries] |
| AWS Bedrock | 5, in boto3's default `legacy` retry mode | No | boto3 retries per client; for one attempt, pass a `bedrock_client` built with `Config(retries={'max_attempts': 0})`[^pydantic-docs-retries] |
| xAI | up to 5, for a request that fails with `UNAVAILABLE` | No | gRPC retries per channel[^pydantic-docs-retries] |
| Hugging Face | 1 | No | The client makes no retries[^pydantic-docs-retries] |

The model classes that honour the setting are listed under `ModelSettings.max_retries`; the others leave their retries unchanged and warn with `UnsupportedSettingWarning` that they are ignoring it[^pydantic-docs-retries] With a non-honouring model in a fallback chain, the setting has to go on the other models' own settings rather than on the agent or the run[^pydantic-docs-retries]

Provider-specific configuration that goes beyond this setting — a custom SDK client, `HttpRetryOptions`, a boto3 `Config`, xAI's channel retries — belongs to each provider page, which this capture links rather than reproduces[^pydantic-docs-retries]

## Evidence and coverage

The package is `raw/core-concepts/retries/`, one `index.md` capture (7,480 words as declared, 7,700 by local `wc -w`, 861 lines, content digest `sha256:0585554b`) with no attachments, includes or supporting files[^pydantic-docs-retries] Every external link — `ModelSettings.max_retries`, `UnsupportedSettingWarning`, `ModelFallback`, `FallbackModel`, `Agent`, `AgentRetries`, `ModelAPIError`, and the OpenAI, Anthropic, Google, Groq, Cohere, TypeSafe, xAI and AWS Bedrock provider pages — was read as a link, not followed[^pydantic-docs-retries]

## Limits

- The page names **no Pydantic AI version, date, author or licence**, and its numbers are SDK behaviour as of an unknown release pair, so the concept is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-retries]
- "Attempts by default" is the vendor's table, not a measurement: no client was constructed and no default verified. Whether `max_retries` counts retries or attempts is stated only for the setting ("how many times the SDK client retries", so `1 + N` attempts), while the table's column is attempts[^pydantic-docs-retries]
- The `ModelSettings.max_retries` API page that enumerates which model classes honour the setting was read as a link, not followed, so the honouring set is recorded here only through the providers the table covers[^pydantic-docs-retries]
- Evidence class: **Reported** — nothing was installed, no SDK client built, no attempt counted and no warning raised in this ingest.

## Relationships

- **Is one of the three wire layers** in [retry layers and multiplication](pydantic-ai-retry-layers.md), where this layer is `M` and its interaction with the others produces `N × F × M × K` wire requests.
- **Stacks on** [transport retries](pydantic-ai-transport-retries.md), which sit below it and are the reason to set `max_retries=0` when the transport owns retrying.
- **Is switched off by** [same-model retries](pydantic-ai-retry-on-model-errors.md), whose capability sends with `max_retries=0` unless you set a value yourself.
- **Sizes the attempt budget of** [model fallback](pydantic-ai-model-fallback.md), where an agent-level setting overrides every chain member's own.
- **Is bounded by** [run controls](pydantic-ai-run-controls.md) `request_timeout`, which covers all attempts of one request to one model, while `timeout` covers a single attempt.
- **Differs per provider** in ways [models and providers](pydantic-ai-models-and-providers.md), [Google models in Pydantic AI](google-models-in-pydantic-ai.md), [Anthropic models in Pydantic AI](anthropic-models-in-pydantic-ai.md) and [OpenAI models in Pydantic AI](openai-models-in-pydantic-ai.md) record from each provider's own page.

[^pydantic-docs-retries]: Pydantic Docs, "Retries" (<https://pydantic.dev/docs/ai/core-concepts/retries/>, 7,480 words as declared and 7,700 by local `wc -w`, 861 lines; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/retries/index.md`, content digest sha256:0585554ba2329f9cc5d9994123af5a4d45b6b27e3502211628eda5768b9b7b56. §"Provider SDK retries" (raw lines 514–519) for the layer's placement, the per-provider divergence, the stacking rule and the provider-page links; §"Setting the SDK retry count per request" (520–574) for `ModelSettings['max_retries']` and its three scopes, the `sdk_max_retries.py` sample, the three cases for setting `0`, the `ModelFallback` precedence rule and the `fallback_max_retries.py` sample, the `FallbackModel` parity, the ten-row default-attempts table, the `UnsupportedSettingWarning` rule and the fallback-chain advice; §"Choosing one retry owner" (57–106) for the per-provider default summary, the Google long-decode exception and the SDK retry ownership row. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence; no client was built and no attempt observed.
