---
type: Concept
title: Pydantic AI cost and spend limits
description: The two budget layers a Pydantic AI agent runs under — per-run UsageLimits and Harness SpendLimits — what each counts and when it checks, plus the timeouts, concurrency caps and caching that bound a runaway loop.
tags: [pydantic-ai, agents, cost, reliability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:46:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

Pydantic AI bounds spend at two scopes and hands a third to a proxy: `UsageLimits` caps one run in core, Harness `SpendLimits` caps a day, month or tenant, and the [Gateway](pydantic-ai-gateway.md) enforces caps per project, user and API key before a request reaches a provider[^pydantic-production-docs] None of the three is a reservation, so the honest promise is bounded overshoot rather than a hard ceiling. Around them sit the four things that stop a runaway loop without counting money: timeouts, cancellation, concurrency caps and prompt caching.

## Per-run limits

`UsageLimits` caps a single run on four quantities — agent-loop requests, successful tool calls, tokens, and cost in USD — and raises `UsageLimitExceeded` once a limit is hit[^pydantic-production-docs] The named fields in the vendor's example are `request_limit`, `tool_calls_limit` and `cost_limit`; `cost_limit` takes a `Decimal`, so the comparison is decimal rather than float[^pydantic-production-docs]

Three properties decide what the numbers actually mean:

- **`request_limit` counts turns of the agent loop, not attempts sent to a provider.** Retries below the loop do not each consume the budget[^pydantic-production-docs]
- **Tokens and cost are checked after a response arrives**, so the request that crosses a limit has already been paid for[^pydantic-production-docs]
- **Cost is best-effort.** A model that [genai-prices](https://github.com/pydantic/genai-prices) has no pricing data for is not counted at all, so `request_limit` belongs beside `cost_limit`, and model prices need keeping up to date[^pydantic-production-docs]

```python
from decimal import Decimal

from pydantic_ai import Agent, UsageLimits

agent = Agent('openai:gpt-6.1-sol', tool_timeout=30)

limits = UsageLimits(request_limit=25, tool_calls_limit=50, cost_limit=Decimal('0.50'))

async def handle(prompt: str) -> str:
    result = await agent.run(prompt, usage_limits=limits)
    return result.output
```

## What hitting a limit costs, and how to keep the work

A run that hits a limit returns no result, but the work before it is not lost: capture its messages and resume from them rather than re-running the prompt and repeating its tool calls[^pydantic-production-docs] The response that crossed a token or cost limit stays in the run's messages, so a run continued from a captured message list — with or without a new prompt — does not pay for it again[^pydantic-production-docs] The alternative the page offers is to tell the model how many requests it has left, so it produces its output before the limit rather than after it[^pydantic-production-docs]

Note the separation: the *budget* is per run, while a [`Conversation`](pydantic-ai-conversation-state.md) is what keeps usage counting across turns and approvals. Passing one conversation back into later runs is what makes a per-run limit behave like a thread limit[^pydantic-production-docs]

## Budgets longer than one run

Harness `SpendLimits` refuses the next request once a budget is spent[^pydantic-production-docs] It is deliberately weaker than it sounds:

| Property | Consequence |
| --- | --- |
| A brake, not a reservation | The request that crosses the line completes |
| Concurrent runs each pass the check | Spend can overshoot by more than one request |
| In-memory store by default | Budgets spanning worker processes or restarts need a shared store |
| Unpriced responses count as free | Set `on_unpriced='raise'` to refuse instead of giving them away |

The Gateway closes the last gap differently: its daily, weekly and monthly caps are per project, user and API key and are enforced before the request reaches the provider, so a key that is over budget never spends[^pydantic-production-docs] That is the one place in this set where the check happens before the cost rather than after it.

## The other runaway bounds

- **Timeouts** bound each model request, tool call and hook, and a whole run separately; the `tool_timeout=30` in the snippet above is the tool one[^pydantic-production-docs] See [Pydantic AI timeouts](pydantic-ai-timeouts.md).
- **Cancellation** stops a run from a stop button or a timer[^pydantic-production-docs]
- **`max_concurrency`** caps how many runs one agent executes at once, with a queue limit for backpressure[^pydantic-production-docs]
- **[`ConcurrencyLimitedModel`](pydantic-ai-model-concurrency.md)** caps concurrent requests to a model within one process — concurrency, not requests per minute, so the provider's rate-limit responses still need handling[^pydantic-production-docs]
- **The `Caching` capability** turns on [prompt caching](pydantic-ai-prompt-caching.md), so a multi-turn run stops paying full price for its instructions, tools and history on every request; [prompt-cache health](pydantic-ai-prompt-cache-health.md) on each request span shows when a change broke the cache, and Logfire's token and cost metrics break spend down by provider and model[^pydantic-production-docs]

## Limits

- One vendor documentation page naming **no Pydantic AI or Harness version, no date, no author and no licence**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-production-docs]
- The `UsageLimits` field list beyond `request_limit`, `tool_calls_limit` and `cost_limit` is not given, and neither is the shape of the token limits or the exact accounting of a cached request.
- `SpendLimits`' budget windows, its store interface, how a shared store is configured and what `on_unpriced='raise'` raises are all unstated; the only default given is the in-memory store.
- The Gateway cap enforcement is the vendor's claim about its own hosted proxy; no request was made through it and no cap was hit.
- Nothing was installed, no run was costed, no limit was hit, no price table was read and no cache hit was measured, so every claim here is **Reported**.
- The example's figures (25 requests, 50 tool calls, $0.50) are illustrative, not a recommendation, and the page states no price or latency figure for any model.

## Relationships

- **Is the cost half of** [Pydantic AI production readiness](pydantic-ai-production-readiness.md), which names both budget layers in its pre-ship map.
- **Extends** [Pydantic AI run controls](pydantic-ai-run-controls.md): that page owns error categories, time budgets and instruction placement; this one owns the money-shaped caps.
- **Depends on** [Conversation state](pydantic-ai-conversation-state.md) for usage that survives between runs, and on [retry layers](pydantic-ai-retry-layers.md) for why a request limit does not count provider attempts.
- **Is complemented by** [Pydantic AI timeouts](pydantic-ai-timeouts.md), [model concurrency](pydantic-ai-model-concurrency.md) and [prompt caching](pydantic-ai-prompt-caching.md), the three bounds that act before or beside the money counters.
- **Uses** the [Gateway](pydantic-ai-gateway.md) when a cap has to be enforced before a request leaves the process.
- **Ships `SpendLimits` from** the [Harness](pydantic-ai-harness.md), so that layer follows the Harness 0.x version policy rather than core's.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. Locators are line ranges in that capture: 189–219 for `UsageLimits` and its four quantities, the `request_limit` loop-turn semantics, the post-response token and cost check, the `Decimal` cost limit, the best-effort pricing and genai-prices reference, the captured-message recovery and the wrapping-up guidance, `SpendLimits` and its brake/shared-store/unpriced properties, the Gateway caps, and the timeouts, cancellation, concurrency and caching paragraph. Evidence class: **Reported** — vendor documentation for its own framework; nothing was installed, costed or measured.
