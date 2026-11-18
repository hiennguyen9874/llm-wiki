---
type: Concept
title: Pydantic AI prompt-cache health
description: How to tell whether a Pydantic AI prompt cache is actually working — the per-request read and write counters, the hit ratio and its same-model caveat, the eight `pydantic_ai.cache.*` span attributes with the collapse classification and its once-per-episode event, and the order in which to check a low hit rate.
tags: [pydantic-ai, caching, observability, cost]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-capabilities-caching-2026
    resource: ../raw/capabilities/caching/index.md
    scope: ../raw/capabilities/caching/
    kind: documentation
    revision: sha256:2271a04714729433cd83bd2b3b2736f277df0c334ccee9e91a135d096cc2ce23
    title: "Caching"
  - id: pydantic-logfire-docs
    resource: ../raw/integrations/logfire/index.md
    scope: ../raw/integrations/logfire/
    kind: documentation
    revision: sha256:5ea6a3e098a0dc8e4c1337ae9bebbef2d5489cc135597569711c1a96e77d6381
    title: "Pydantic Logfire Debugging and Monitoring"
---

A cache hit is invisible in the request itself, so Pydantic AI exposes it twice: as provider usage counters on every response, normalized across providers, and as span attributes on instrumented model requests. The failure mode neither surface closes is silence — a request that falls short of the vendor's detection thresholds, a provider that reports no cache usage, and a cache that was never established all produce no warning and no collapse event.[^pydantic-capabilities-caching-2026] Everything here extends [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), which owns the switch, the retention tiers and the breakpoint placement; this page owns the question "is the cache working, and if not, why".

## Reading the counters

The smallest check is two requests over one long shared prefix. With `Caching()` on an agent whose instructions carry a document well above the provider's minimum cacheable length, the first response reports what it wrote and the follow-up reports what it read[^pydantic-capabilities-caching-2026]:

```python
first = agent.run_sync('How many vacation days do new employees get?')
second = agent.run_sync('And after five years?', message_history=first.all_messages())

written = first.response.usage.cache_write_tokens  # the handbook and the first question
read = second.response.usage.cache_read_tokens     # what the first request wrote
```

Three facts explain most zero readings. A prefix below the provider's minimum cacheable length — between about 1,024 and 4,096 tokens depending on provider and model — is never cached, so both counts stay at zero. Some providers, such as OpenAI before GPT-5.6, report only cache reads. And a prefix is only read back by a request that starts with it, which in a conversation means continuing with the full `message_history`.[^pydantic-capabilities-caching-2026]

Every response's `RequestUsage` normalizes `cache_read_tokens` and `cache_write_tokens` across providers, and a run's `RunUsage` (`result.usage`) sums them over all of the run's requests. `input_tokens` includes cache reads and writes, so `cache_read_tokens / input_tokens` — the `cache_hit_ratio` property — is a comparable per-request ratio. A run's ratio is only interpretable when every request went to the same model.[^pydantic-capabilities-caching-2026]

## The signals instrumentation adds

With instrumentation enabled, model-request spans carry a per-request hit ratio and the size of the established cached prefix. A request that loses a meaningful part of that prefix is recorded as a cache collapse with a classified reason, such as an expired provider retention window or provider-native compaction, and only an unexpected collapse emits a `pydantic_ai.cache.collapse` span event. A request long enough to cache that reaches a model which needs caching configured, with none configured, is flagged as `pydantic_ai.cache.not_enabled`. On Anthropic, `pydantic_ai.cache.requested_breakpoints` and `pydantic_ai.cache.applied_breakpoints` expose any `CachePoint` that was dropped to fit the request's breakpoint limit.[^pydantic-capabilities-caching-2026] Logfire renders the same data as prompt-cache health, and the vendor Logfire page gives the attribute list, thresholds and classification this page records below[^pydantic-logfire-docs]

### The attribute family

Eight attributes, all on model-request spans[^pydantic-logfire-docs]:

| Attribute | What it holds |
| --- | --- |
| `pydantic_ai.cache.hit_ratio` | The request's input tokens read from the prompt cache — `cache_read_tokens / input_tokens`, where input tokens include cache reads and writes |
| `pydantic_ai.cache.established_tokens` | The cached-prefix size later requests are judged against, for the conversation and the response's provider, endpoint (`provider_url`) and model; it grows as the prefix does, and drops to whatever the current request established after a collapse, so an intentional bust is reported once rather than against a stale high-water mark |
| `pydantic_ai.cache.collapsed` | `true` when the request read back less of the established prefix than it could have: more than 5% **and** at least 2,000 tokens short — the thresholds Claude Code uses for a prompt-cache miss |
| `pydantic_ai.cache.missed_tokens` | Previously established tokens that were not read after a collapse |
| `pydantic_ai.cache.collapse_reason` | The classification: `unexpected`, `ttl_expired`, `compacted`, `unknown` or `unreported`, and more values may be added |
| `pydantic_ai.cache.not_enabled` | `true` when the request was long enough to cache on a model that needs caching configured, and none was configured |
| `pydantic_ai.cache.requested_breakpoints` | The breakpoints an Anthropic request asked for, as paths into the request: `system[i]`, `tools[i]`, `messages[i].content[j]`, plus `automatic` for the breakpoint automatic caching places itself |
| `pydantic_ai.cache.applied_breakpoints` | The breakpoints that request was sent with, after dropping the ones over Anthropic's limit |

None of them is on the agent-run span: one ratio aggregated across requests to different models is not interpretable, which is the same reason the OpenTelemetry GenAI conventions dropped cache attributes from `invoke_agent` spans. A run-level figure is computed instead from its `gen_ai.aggregated_usage.*` token counts[^pydantic-logfire-docs] The breakpoint indices point into the request as sent to Anthropic, after consecutive request parts are merged into one message, not into the message history — a `CachePoint` is marked on the block before it rather than being an entry of its own, and only the request records the two lists, not the token count that `count_tokens_before_request` makes before it[^pydantic-logfire-docs]

### Classifying a collapse

Exactly one reason emits the `pydantic_ai.cache.collapse` span event, and the event means "reuse fell when the cache should still have been warm" rather than "something about caching happened"[^pydantic-logfire-docs]:

| `collapse_reason` | Meaning | Emits the event |
| --- | --- | --- |
| `unexpected` | The provider's retention window should still have been active, so the cached prefix most likely changed | Yes — carrying `established_tokens`, `cache_read_tokens`, `missed_tokens` and the `provider_name` and `model_name` that served the request |
| `ttl_expired` | The gap since the last request exceeded the provider's retention window | No |
| `compacted` | A `CompactionPart` — provider-native compaction, or a summary the application or `SummarizingCompaction` wrote — replaced the history before it, shrinking the prefix by design | No |
| `unknown` | The provider publishes no retention window, so the collapse cannot be attributed | No |
| `unreported` | The response reported no cache usage at all | No |

A compaction summary that replaces an earlier one with the same text and `metadata` cannot be told apart from it, which is why the docs advise distinct metadata on every summary the application writes — `SummarizingCompaction` does[^pydantic-logfire-docs] A sustained collapse, such as a prefix that moves on every request so the provider keeps writing a cache nothing reads back, is recorded on every request's span but emits the event once, firing again only after a healthy read-back re-stabilizes the cache[^pydantic-logfire-docs] The detector sees usage and timing rather than request content, so it reports that a miss happened and not what caused it — which is why the diagnostic order below still starts from the request[^pydantic-logfire-docs]

### What `not_enabled` and an unreported response each mean

A response reporting neither cache reads nor writes is ambiguous, and which way it reads depends on the provider[^pydantic-logfire-docs] On providers that report writes (Anthropic, Bedrock) it means the cache was not engaged for that request — caching disabled, or a prompt below the provider's minimum cacheable size; on providers that report only reads (OpenAI's implicit caching) it is what a full cache miss looks like. The established prefix was re-sent uncached either way, so the collapse and its missed tokens are recorded as `unreported` and no event is emitted, because the cause cannot be determined from usage alone; before anything has been cached such responses are ignored entirely[^pydantic-logfire-docs]

`not_enabled` is narrower. Models such as Anthropic's, Bedrock's Claude and Nova, and OpenRouter's Anthropic routes only cache what the request asks for, so the flag is set when all four hold: at least 4,096 input tokens (above every supported model's minimum, per the docs), no caching configured through the unified `cache` setting or a provider-specific one, no `CachePoint` in the history, and no reported cache usage[^pydantic-logfire-docs] Its span event carries `input_tokens` and the serving `provider_name` and `model_name`, once per conversation and model; `cache=False` says the omission was deliberate and is not reported[^pydantic-logfire-docs]

### The edges the detector already handles

Several cases that look like misses are classified rather than flagged[^pydantic-logfire-docs]:

- **A paused and resumed request** — an Anthropic `pause_turn` continuation — is one model request whose usage sums every segment, so it is judged by its final segment, whose prompt carries the whole prefix.
- **A response whose cache reads may be summed over a native tool's internal model calls**, such as web search, is judged but does not raise the established prefix or re-arm the event, because its total is not a prefix the next request can read back.
- **Continued conversations are judged per conversation, not per run**, so a run continuing from `message_history`, including history that was serialized and loaded back, is measured against what the previous run cached — which is where a moved prefix most often shows.
- **The marks live in process memory**, forgotten once a conversation has been idle longer than any provider keeps a cache (24 hours) or when more than 4,096 conversations have been active more recently.
- **A model switch is never a collapse.** The prefix is tracked per provider, endpoint and model, so a `FallbackModel` failover starts a fresh mark and switching back is judged against the original one.
- **Retention comes from the request's own settings** — the unified `cache` setting, `anthropic_cache='1h'`, `openai_prompt_cache_retention='24h'` on models before GPT-5.6 — resolved by `Model.resolve_cache_retention()` or else the provider's `default_cache_retention` in its profile. Explicit `CachePoint` TTLs extend it; with no known retention, collapses stay `unknown` even when cache points carry TTLs.

For the same signals as Python warnings during development and in CI, the Harness **Warn On Cache Busts** capability shares that detector and classification, and additionally warns when caching is not enabled at all[^pydantic-capabilities-caching-2026] See [Pydantic AI capability catalog](pydantic-ai-capability-catalog.md) for where it sits among the Harness capabilities.

## Diagnosing a low hit rate

These signals detect that a cache was missed, not why, so the source gives an order of checks[^pydantic-capabilities-caching-2026]:

1. Confirm caching is enabled for the model, and that no provider-specific cache setting overrides the unified one.
2. Confirm the shared prefix is above the provider's minimum cacheable length.
3. Compare each response's `cache_read_tokens` and `cache_write_tokens`; writes without later reads mean the prefix changed or expired before it was read.
4. Look for a change that moves the prefix — per-request timestamps, instructions rewritten mid-conversation, reordered tool definitions, a rewriting history processor, a switch of model or provider — and confirm conversations continue with their full `message_history`.
5. Check whether the gap between requests exceeds the provider's retention, and whether requests of one conversation reach the same cache (OpenRouter's provider routing, xAI's sticky routing, OpenAI's `openai_prompt_cache_key`).
6. Ask the provider: Anthropic's cache diagnostics and OpenAI's prompt-cache diagnostics report why a request missed.

The causes that step 4 uncovers are enumerated in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), and several other concepts record a specific one: a request-level [reasoning effort change](pydantic-ai-reasoning-effort-changes.md) re-processes the conversation, the local [tool search](pydantic-ai-tool-search.md) fallback and a `tools[]`-moving [on-demand capability](pydantic-ai-on-demand-capabilities.md) load both spend the prefix, [prompt framing](pydantic-ai-prompt-framing.md) changes it when the announcement is not sent back, and [file understanding](pydantic-ai-file-understanding.md) keeps it stable only while its description stays in the history metadata.

## Why no warning is not proof

Absence of a collapse event or warning does not show that caching works: a request that falls short by less than the detection thresholds, a provider that reports no cache usage, or a cache that was never established all stay silent[^pydantic-capabilities-caching-2026] The counters are therefore the primary evidence, and the span signals are a second reader of the same wire data rather than an independent check.

## Limits

- One vendor reference page naming **no Pydantic AI version and no date**, so which release introduced the collapse classification, the `not_enabled` flag or the breakpoint attributes is unstated; the page is `draft` under the `pydantic-ai` domain rule[^pydantic-capabilities-caching-2026]
- The 1,024–4,096-token minimum is the vendor's range across providers and models, not a measured floor. The attribute list, the 5%-and-2,000-token collapse threshold, the collapse-reason vocabulary and the 24-hour/4,096-conversation memory bounds come from the vendor Logfire integration page, which names **no Pydantic AI version and no date**, so which release introduced them is still unstated[^pydantic-logfire-docs]
- `SummarizingCompaction`'s metadata scheme, the `gen_ai.aggregated_usage.*` sub-attributes a run-level ratio is computed from, and the Harness **Warn On Cache Busts** capability's warning text are named but not specified in either source[^pydantic-logfire-docs]
- No package was installed, agent run, cache written or read, span opened, collapse induced or warning raised, so every claim is **Reported** and none **Observed** or **Reproduced**.
- The counters are only as good as provider reporting: a provider that omits cache usage makes a working cache look absent, and this page cannot distinguish the two from Pydantic AI's side[^pydantic-capabilities-caching-2026]

## Relationships

- **Details** [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md), which owns the `Caching` capability, the retention tiers and the per-provider breakpoint translation this page measures.
- **Uses** [Pydantic AI observability](pydantic-ai-observability.md) for the span tree these attributes sit on, and [Pydantic AI instrumentation format](pydantic-ai-instrumentation-format.md) for the attribute-naming and content-redaction rules that decide whether they are exported at all.
- **Depends on** [message history](pydantic-ai-message-history.md): a conversation that does not continue with its full `message_history` cannot read back what the previous request wrote.
- **Explains misses recorded by** [reasoning effort changes](pydantic-ai-reasoning-effort-changes.md), [tool search](pydantic-ai-tool-search.md), [on-demand capabilities](pydantic-ai-on-demand-capabilities.md), [prompt framing](pydantic-ai-prompt-framing.md) and [file understanding](pydantic-ai-file-understanding.md), each of which names how it moves or preserves the prefix.
- **Complements** [history processors](pydantic-ai-history-processors.md), whose cache-cold scheduling uses `prompt_cache_outlook` to spend a rewrite when a miss is already priced in.

[^pydantic-logfire-docs]: Pydantic Docs, "Pydantic Logfire Debugging and Monitoring", <https://pydantic.dev/docs/ai/integrations/logfire/>, `domain: pydantic.dev`, `language: en`, 5,651 words as declared and 5,851 by local `wc -w`, 565 lines, no publication date, author, licence or Pydantic AI version; local capture `raw/integrations/logfire/index.md`, content digest sha256:5ea6a3e0. §"Prompt-cache health" (raw lines 288–332) for the eight-attribute table and what each attribute holds, the run-span exclusion and its `invoke_agent` rationale, the requested/applied breakpoint paths and the merged-message index rule, the collapse-reason table with the single-emitting `unexpected` case and the event's payload, the once-per-episode firing rule, the compaction-metadata warning, the ambiguous no-usage response on write-reporting versus read-only providers, the four `not_enabled` conditions with `cache=False` exempt, the paused-and-resumed and native-tool-reads rules, per-conversation tracking, the 24-hour and 4,096-conversation memory bounds, model switches starting a fresh mark, retention resolution through `resolve_cache_retention()` and `default_cache_retention`, and the pointer to Harness **Warn On Cache Busts** warning on `unexpected` and `unknown` collapses. Evidence class: **Reported** — vendor documentation; no request was cached, no span inspected and no collapse induced.

[^pydantic-capabilities-caching-2026]: Pydantic Docs, "Caching", <https://pydantic.dev/docs/ai/capabilities/caching/>, 3,412 words as declared and 3,560 by local `wc -w`, 252 lines, `domain: pydantic.dev`, `language: en`, no publication date and no Pydantic AI version named; local capture `raw/capabilities/caching/index.md`, content digest sha256:2271a047. §"Monitoring cache efficiency" (raw lines 187–216) for the two-request check, `cache_write_tokens` and `cache_read_tokens`, the 1,024–4,096-token minimum range, the read-only reporting of OpenAI before GPT-5.6, the `RequestUsage`/`RunUsage` normalization, `input_tokens` including cache traffic, the `cache_hit_ratio` property and the same-model condition, the hit-ratio and established-prefix span attributes, the classified collapse and its `pydantic_ai.cache.collapse` event, the `pydantic_ai.cache.not_enabled` flag, the Anthropic requested/applied breakpoint attributes, the link to Logfire's prompt-cache health, the Harness Warn On Cache Busts capability, the six diagnostic steps, and the closing warning that silence does not prove caching works. Evidence class: **Reported** — vendor documentation; nothing was cached, measured, instrumented or diagnosed.
