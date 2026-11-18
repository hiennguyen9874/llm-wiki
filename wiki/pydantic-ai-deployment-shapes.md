---
type: Concept
title: Pydantic AI deployment shapes
description: How a Pydantic AI agent is deployed — the five shapes from web service to voice agent, the process-local concurrency knobs a long-running server needs, and why a deploy can break runs that are already in flight.
tags: [pydantic-ai, agents, production, deployment]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:47:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

There is nothing Pydantic-specific to host. An agent is a Python object in the process that runs it, so deployment is whatever your Python deploys, and the choice that matters is where a run **starts** and how long it **lives**[^pydantic-production-docs] Because a conversation's state lives in a store the application owns or in the durable engine rather than in the process, any instance can continue any conversation — which is what makes every shape below horizontally replaceable[^pydantic-production-docs]

## The five shapes

| Shape | Where the run starts | What the shape requires |
| --- | --- | --- |
| A web service | Inside your FastAPI, Starlette, Django or Flask handler | Nothing beyond the web app; scale it like any other web app |
| A worker | A queue or a schedule | A durable engine's workers — Temporal, DBOS queues, Prefect deployments — or Harness Render Workflows, which runs model requests and supported tool calls as separate tasks |
| A serverless function | An invocation | A durable-function runtime such as AWS Lambda durable functions, so a timed-out or retried invocation resumes instead of starting over |
| A voice agent | A live call | Long-lived compute, because a realtime session holds a provider connection open for the whole call; request-scoped functions do not fit |
| An agent on a repository | Issues, pull requests or a schedule | Harness GitHub Agentic Workflows |

Two of the rows are really the durable-execution decision wearing a deployment hat: a worker needs an engine's worker model, and serverless needs a durable function that can resume rather than restart[^pydantic-production-docs] Which engines exist, where each ships and whose version policy covers it is in [Pydantic AI durable execution](pydantic-ai-durable-execution.md); the voice row's hosting constraints are in [realtime voice agents](pydantic-ai-realtime-voice.md).

## A long-running server

In a server that stays up, runs are async and share one event loop, so the process needs explicit bounds rather than one thread per request[^pydantic-production-docs]:

- `max_concurrency` caps how many runs execute at once, with a queue limit behind it for backpressure[^pydantic-production-docs]
- `UseThreadExecutor` gives synchronous tools a bounded thread pool instead of letting them block the loop[^pydantic-production-docs]
- A slow tool can run as a Harness [background tool](pydantic-ai-harness-background-tools.md) while the agent keeps working[^pydantic-production-docs]

The queue limit is the part worth noticing: a concurrency cap without backpressure turns a burst into unbounded waiting, not into a refusal.

## A deploy changes what in-flight runs replay against

Pin your versions. Pydantic AI follows its own [version policy](https://pydantic.dev/docs/ai/project/version-policy/), and the [Harness](pydantic-ai-harness.md) follows its 0.x policy separately[^pydantic-production-docs] With a durable engine, that is not only an upgrade-hygiene point but a correctness one: a deploy changes what an in-flight run replays against, so **adding a tool or changing a type the engine stored can break a run that started under the old code**[^pydantic-production-docs] The page's two remedies are to let those runs drain on the old version or to follow the engine's own versioning guidance — Temporal's, or the constraints AWS Lambda's durable functions impose[^pydantic-production-docs]

The same rule already appears as step identity: DBOS derives step names from the agent's `name` and each toolset's `id`, so renaming either breaks in-flight workflows, and adding a workspace changes an agent's steps in a way DBOS cannot recover across — see [Pydantic AI on DBOS](pydantic-ai-dbos.md).

## Limits

- One vendor documentation page naming **no Pydantic AI, Harness or platform version, no date, no author and no licence**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-production-docs]
- The section is a list of shapes, not a deployment guide: it gives no manifest, container, region, memory, cold-start, scaling or cost figure for any of the five, and no per-platform configuration for the durable functions, worker models or repository agents it names.
- "Any instance can continue any conversation" holds only when the state is actually stored or the engine holds it; the source does not discuss a deployment that keeps history in memory.
- The GitHub Agentic Workflows row is a name and a trigger, with no setup or permission model described.
- Nothing was deployed, containerised, scaled, frozen or resumed, so every claim is **Reported**.

## Relationships

- **Expands the deployment row of** [Pydantic AI production readiness](pydantic-ai-production-readiness.md), whose table stops at "your own Python process".
- **Requires** [durable execution](pydantic-ai-durable-execution.md) for the worker and serverless shapes, and [Conversation state](pydantic-ai-conversation-state.md) or an engine journal for the statelessness the other three rely on.
- **Is constrained for the voice shape by** [realtime voice agents](pydantic-ai-realtime-voice.md): a live session needs long-lived compute rather than a request-scoped function.
- **Uses** [Harness background tools](pydantic-ai-harness-background-tools.md) to keep a slow tool off the request's critical path.
- **Repeats** the in-flight-version rule that [Pydantic AI on DBOS](pydantic-ai-dbos.md) states as permanent step identity and [Pydantic AI on Temporal](pydantic-ai-temporal.md) states as activity names.
- **Bounds the process through** [Pydantic AI cost and spend limits](pydantic-ai-cost-and-spend-limits.md): `max_concurrency` is one of the four non-monetary runaway bounds compiled there.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. Locators are line ranges in that capture: 323–335 for the deployment question, the five shapes and their requirements, the shared event loop and `max_concurrency`/queue-limit/`UseThreadExecutor`/background-tool paragraph, and the version policy plus in-flight replay warning; 299–321 for the web-service handler and the UI adapter route. Evidence class: **Reported** — vendor documentation for its own framework; nothing was deployed or measured.
