---
type: Concept
title: Pydantic AI model concurrency
description: ConcurrencyLimitedModel as the wrapper that caps in-flight model requests — the three limiter forms, sharing one limit across models, and the instance-separation rules that raise UserError or RuntimeError when ignored.
tags: [pydantic-ai, models, reliability, operations]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:55:00Z }
stale_after: 2027-02-18
sources:
  - id: models-overview-2026
    resource: ../raw/models/overview/index.md
    scope: ../raw/models/overview/
    kind: documentation
    revision: sha256:b0b88d61e84966c7b8b8d70207b0cf386810413968eaa0d0246ca6690ef10a66
    title: "Models and Providers"
---

`ConcurrencyLimitedModel` wraps any model or `<provider>:<model>` string and caps how many HTTP requests it has in flight at once, which is how many agents running in parallel stay inside a provider's rate limit instead of discovering it as `ModelRateLimitError`[^models-overview-2026] The wrapper is applied to the model rather than the agent, so one rate-limited model can serve several agents[^models-overview-2026] The rule that bites is that every layer of nesting needs its **own** limiter instance: reusing one across an agent's own request and its model, or across two nested wrappers, is a `UserError`, and re-entering a limiter through an agent on the same task is a `RuntimeError`[^models-overview-2026] The errors this prevents are catalogued in [model API errors](pydantic-ai-model-api-errors.md).

## The wrapper

```python
import asyncio

from pydantic_ai import Agent, ConcurrencyLimitedModel

model = ConcurrencyLimitedModel('openai:gpt-6.1-sol', limiter=5)
agent = Agent(model)

async def main():
    results = await asyncio.gather(*[agent.run(f'Question {i}') for i in range(20)])
    print(len(results))
    #> 20
```

`limiter` takes three forms[^models-overview-2026]:

| Form | Use |
| --- | --- |
| An integer, e.g. `limiter=5` | Simple per-model cap |
| A `ConcurrencyLimit` | Advanced configuration with backpressure control |
| A `ConcurrencyLimiter` | A limit shared across several models |

## Sharing one limit

Different models from the same provider usually share one account's rate limit, so the limiter is created once with a name and passed to several wrappers[^models-overview-2026]

```python
shared_limiter = ConcurrencyLimiter(max_running=10, name='openai-pool')
model1 = ConcurrencyLimitedModel('openai:gpt-6.1-sol', limiter=shared_limiter)
model2 = ConcurrencyLimitedModel('openai:gpt-6-luna', limiter=shared_limiter)
```

The `name` is not decoration: with instrumentation enabled it is what identifies the shared limiter in traces[^models-overview-2026]

## The separation rules

Four constraints, all of them runtime errors when broken[^models-overview-2026]:

- An agent and the `ConcurrencyLimitedModel` used for its own model request must use **separate** limiter instances — setting `Agent(max_concurrency=...)` and `ConcurrencyLimitedModel(limiter=...)` to the same instance raises `UserError`
- Nested `ConcurrencyLimitedModel` wrappers need different limiter instances
- Re-entering a limiter through an agent on the same task raises `RuntimeError`; a nested run needs a separate limiter
- A delegated run — an agent calling another agent through a tool — acquires its own slot for every run or model request, so a shared pool must have capacity for the parent and the nested operation at once

The shape of the constraint is that the limiter is an acquisition boundary, not a quota shared by reference: two acquisitions on one task would deadlock, and that is what the errors report.

## Traces

With instrumentation on, a request waiting for a slot appears as a span whose attributes show the queue depth and the configured limits, so contention is visible rather than inferred from latency[^models-overview-2026] See [observability](pydantic-ai-observability.md) for the surrounding span tree.

## Limits

- The page names **no Pydantic AI version**, so the wrapper's arrival version is unknown and the page is `draft` under the `pydantic-ai` domain rule[^models-overview-2026]
- `ConcurrencyLimit`'s advanced options are named but not enumerated, and no default limit, timeout-for-a-slot, queue bound or rejection behaviour is stated[^models-overview-2026]
- Whether a limiter caps requests, streaming connections or both, and whether it applies to native tool calls a provider makes server-side, is not stated[^models-overview-2026]
- The API reference pages for `ConcurrencyLimitedModel`, `ConcurrencyLimit` and `ConcurrencyLimiter` were read as links, not followed[^models-overview-2026]
- Evidence class: **Reported** — no wrapper constructed, no parallel run executed, no span inspected, so the `UserError` and `RuntimeError` conditions are documentation claims rather than reproduced behaviour.

## Relationships

- **Wraps** a model as described in [models and providers](pydantic-ai-models-and-providers.md), including a `FallbackModel` chain.
- **Prevents** [model API errors](pydantic-ai-model-api-errors.md) of the rate-limit category by queuing rather than failing.
- **Recorded in** [observability](pydantic-ai-observability.md) as queue-depth attributes on the waiting span.
- **Differs from** `Agent(max_concurrency=...)` and [run controls](pydantic-ai-run-controls.md) budgets: those bound one agent's concurrency and time, this bounds a model's in-flight HTTP requests.

[^models-overview-2026]: Pydantic Docs, "Models and Providers", <https://pydantic.dev/docs/ai/models/overview/>, 6,420 words as declared, no publication date and no version named; local capture `raw/models/overview/index.md`, content digest sha256:b0b88d61. §"HTTP Request Concurrency" (lines 179–247) for the wrapper and its purpose, the `model_concurrency.py` example, the three `limiter` forms; §"Shared Concurrency Limits" (lines 211–247) for `ConcurrencyLimiter(max_running=10, name='openai-pool')`, line 244 for the `UserError`/`RuntimeError` and nested-run rules, and line 246 for the queued-request spans and the `name` parameter in traces. Evidence class: **Reported** — vendor documentation; nothing was constructed, run or traced.
