---
type: Concept
title: Pydantic AI production readiness
description: The questions to answer before shipping a Pydantic AI agent, the mechanism that answers each one, the three jobs one checkpointer does elsewhere, and the composition the vendor runs end to end.
tags: [pydantic-ai, agents, production, reliability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:45:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

"Going to Production" is a collation page rather than a feature page: it answers eleven questions a team asks before shipping an agent, gives each a one-line answer and a link, and then walks one runnable service that puts the answers together[^pydantic-production-docs] Its durable contribution is the mapping itself plus two things the linked pages do not say in one place — the split of a single checkpointer's job into three separate mechanisms, and the rule that a crash-recovery engine's replay is bound to the code that started the run[^pydantic-production-docs]

The page also states its own hosting boundary. Pydantic AI, Pydantic Evals and Pydantic AI Harness are MIT-licensed Python packages that run in the caller's process, and durable execution runs on an engine the caller operates or that engine's own cloud: there is no Pydantic-hosted agent runtime. The two hosted pieces are optional and plug in beside the process — Logfire for traces and the Gateway for one key across providers[^pydantic-production-docs]

## The pre-ship map

The vendor's table is the shortest form of the answer, and its install column is the part that decides ownership: a piece that ships in `pydantic-ai` follows core's version policy, one that needs a Harness extra follows the Harness's 0.x policy instead[^pydantic-production-docs]

| Before shipping, you want to know… | Mechanism the page names | Install |
| --- | --- | --- |
| What happens when the process crashes mid-run? | A [durable execution](pydantic-ai-durable-execution.md) engine | `pydantic-ai-slim` with one engine extra, such as `[dbos]` or `[temporal]` |
| How does a human approve a risky action days later? | [Deferred tools](pydantic-ai-deferred-tools.md) end the run; a later run resumes it | `pydantic-ai` |
| How do I keep conversation state? | Store the run's [`Conversation`](pydantic-ai-conversation-state.md) in your database | `pydantic-ai` |
| How do I bound cost and runaway loops? | [`UsageLimits`](pydantic-ai-cost-and-spend-limits.md) per run, `SpendLimits` per budget | `pydantic-ai`, and the [Harness](pydantic-ai-harness.md) for `SpendLimits` |
| What happens when a provider is down? | A [fallback model](pydantic-ai-model-fallback.md), transport retries, or Gateway failover | `pydantic-ai`, or the hosted [Gateway](pydantic-ai-gateway.md) |
| Where do API keys go? | Environment variables, or one Gateway key for every provider | `pydantic-ai`, or the Gateway |
| How do I see what happened? | OpenTelemetry traces of every run, in Logfire or any OTel backend | `pydantic-ai` (includes `logfire`) |
| How do I test and evaluate changes? | Unit tests with `TestModel`, then evals on datasets and live traffic | `pydantic-ai` (includes `pydantic-evals`) |
| How do I limit what the agent can touch? | Per-caller tools, approval, and a sandbox for model-written code | `pydantic-ai`, and the Harness for sandboxes |
| How do I serve it to a frontend? | AG-UI or Vercel AI streams from any ASGI app | `pydantic-ai` |
| How do I deploy it? | As your own Python process: a web app, a worker or a function | Your infrastructure |

The last row is the honest one: every other answer is a library feature, and deployment has no Pydantic-side component at all[^pydantic-production-docs] The shapes that row hides — and the concurrency knobs a long-running server needs — are in [Pydantic AI deployment shapes](pydantic-ai-deployment-shapes.md).

## One checkpointer, three jobs

Frameworks built around a checkpointer use one mechanism — state saved after each step — to cover crash recovery, pausing for a human and resuming a thread. Pydantic AI splits those jobs, and the split is the design decision worth carrying into architecture[^pydantic-production-docs]:

| Job | Mechanism | Granularity |
| --- | --- | --- |
| Crash recovery inside a run | Durable execution | One model request or journaled tool call |
| Pausing for a human | Deferred tools: the run ends, nothing stays in memory | A whole run boundary |
| Continuing between runs | The stored `Conversation` | A chat thread: messages, usage, id, pending calls |
| Resuming or forking from a point | Harness `StepPersistence` | A settled tool-call boundary, plus a tool-effect ledger |

`StepPersistence` complements the `Conversation` rather than replacing it. Its snapshots hold messages only — not the usage and pending deferred calls a `Conversation` carries — and its ledger records whether each tool call started, returned or raised. A call that never finished therefore has an **unknown outcome**: the page's instruction is to check the external system before running it again[^pydantic-production-docs]

The same rule reaches every engine: a step that was in flight when the process died runs again from its start, so a tool with side effects has to be safe to repeat, for example by passing an idempotency key to the API it calls[^pydantic-production-docs] Model requests, tool calls and output validation each retry on their own layer before a run fails with something like `UnexpectedModelBehavior`; that multiplication is compiled in [Pydantic AI retry layers and multiplication](pydantic-ai-retry-layers.md).

## The composition the page runs end to end

The reference service is one file: FastAPI, a DBOS-backed agent, a refund tool that needs approval, and OpenTelemetry traces. It needs a model provider key and nothing else — DBOS keeps state in a SQLite file, and traces go to Logfire when a token is present or to any collector named by `OTEL_EXPORTER_OTLP_ENDPOINT`[^pydantic-production-docs] The load-bearing details are small and easy to miss:

- The agent declares `output_type=[str, DeferredToolRequests]` so a pending approval can be the run's output, and carries `capabilities=[DBOSDurability()]`.
- The refund tool is marked `requires_approval=True` **and** decorated `@DBOS.step()`, because DBOS durability does not wrap application function tools.
- The workflow publishes state with `DBOS.set_event_async`, and waits for the decision with `DBOS.recv_async('approvals', timeout_seconds=7 * 24 * 3600)`; a timeout is turned into a denial for every pending call instead of leaving the run waiting forever.
- Continuation is `agent.run(conversation=result.conversation, deferred_tool_results=output.build_results(approvals=approvals))`, and the loop repeats while the output is still `DeferredToolRequests`.
- The HTTP surface only starts, reads and signals: `POST /runs` returns a workflow id, `GET /runs/{run_id}` reads the state event with `timeout_seconds=0` (so it answers `None` until the workflow starts), and `POST /runs/{run_id}/approvals` sends the decision as a signal. No request has to stay open for the run to continue[^pydantic-production-docs]

The payoff the page claims is that killing the server and starting it again recovers the workflow, replays the model requests and the already-finished refund step from the database, and returns to waiting where it was[^pydantic-production-docs] This is the vendor's description of its own example; nothing here was run.

## Rules that cross several answers

- **One engine per agent**: an engine is attached as a capability, and a second one is refused — see [durable execution](pydantic-ai-durable-execution.md).
- **A conversation id is a key, not a credential**: check that the caller may access the conversation before loading it, and serialize concurrent updates to one conversation — a version column or a per-conversation lock — so two instances do not continue the same stored version[^pydantic-production-docs] See [Conversation state](pydantic-ai-conversation-state.md).
- **A streamed response bypasses the response check**: `ModelFallback` can try the next model on an API error or on a non-streamed response that fails a check you define, but a streamed response, as a frontend gets, is accepted as it is[^pydantic-production-docs] See [model fallback](pydantic-ai-model-fallback.md).
- **Approval can wait inside the workflow**: the same deferral that a person answers minutes later over an HTTP call can be awaited by a durable workflow, carried over a UI adapter's stream, or resolved inline by a `HandleDeferredToolCalls` handler when the approver is in the same process[^pydantic-production-docs] See [deferred tool approval](pydantic-ai-deferred-approvals.md).
- **A UI adapter endpoint is not an authentication boundary**: run it inside your own authenticated route, and treat client-submitted messages as untrusted input[^pydantic-production-docs] See [client-supplied history](pydantic-ai-client-supplied-history.md).
- **Telemetry carries prompts, completions and tool arguments by default**: `include_content=False` keeps them out of Pydantic AI's spans and `include_binary_content=False` drops media bytes, but neither touches run metadata, your own spans or captured HTTP request bodies[^pydantic-production-docs] See [observability](pydantic-ai-observability.md).
- **Keys come from the process or one Gateway key**: each provider reads its own environment variable or takes `api_key=` on its provider class; under the Gateway the application holds one `PYDANTIC_AI_GATEWAY_API_KEY` whose keys can each carry a spending cap, one per service or environment[^pydantic-production-docs] See [Gateway](pydantic-ai-gateway.md).

## Limits

- A vendor documentation page naming **no Pydantic AI, Harness, Evals or Logfire version, no publication date, no author and no licence**, so this page is `draft` under the `pydantic-ai` domain rule[^pydantic-production-docs] Every API name, default and install extra here is version-unknown.
- The page is an index by construction: each answer is one sentence pointing at a page that holds the contract. The linked concept is the authority for anything beyond the rule restated above, and several of those pages are themselves vendor-only.
- Nothing was installed, imported, built, deployed, approved, traced, evaluated or priced in this ingest. The end-to-end service, the crash-and-restart behaviour, the spend arithmetic and the `include_content` scope are all **Reported**.
- The example's model aliases (`anthropic:claude-sonnet-5-5`, `openai:gpt-6.1-sol`) appear nowhere else in this wiki, and the page states no price, latency, throughput or scaling figure for any shape it names.
- The seven-day approval window, the SQLite file and the omitted authentication, ownership checks, deduplication and usage limits are properties of one illustrative snippet, not recommendations; the page says explicitly what it leaves out[^pydantic-production-docs]

## Relationships

- **Composes** [durable execution](pydantic-ai-durable-execution.md), [deferred tools](pydantic-ai-deferred-tools.md) and [Conversation state](pydantic-ai-conversation-state.md), the three mechanisms its checkpointer split separates.
- **Delegates cost bounding to** [Pydantic AI cost and spend limits](pydantic-ai-cost-and-spend-limits.md), where the `UsageLimits` and `SpendLimits` semantics the table names are compiled.
- **Delegates hosting to** [Pydantic AI deployment shapes](pydantic-ai-deployment-shapes.md), which expands the "your own Python process" row.
- **Depends on** [observability](pydantic-ai-observability.md) for the trace answer and on [Pydantic Evals](pydantic-evals.md) for the evaluation half of the quality answer.
- **Uses** [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) for the isolation answer, and [model fallback](pydantic-ai-model-fallback.md) plus [retry layers](pydantic-ai-retry-layers.md) for the outage answer.
- **Constrains** the [Gateway](pydantic-ai-gateway.md) to an optional hosted piece: failover, load balancing and spending caps are its additions, while calling providers directly remains supported.
- **Positions** the framework in [Pydantic AI ecosystem positioning](pydantic-ai-ecosystem-positioning.md): no hosted runtime and MIT packages in your own process is the vendor's own statement of that boundary.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. Locators are line ranges in that capture: 11–13 for the MIT packages, the caller-operated engine and the two hosted services; 15–31 for the eleven-question table and the "built with" pointer; 33–124 for the end-to-end service (the `DBOSDurability` agent and `output_type`, the `requires_approval` refund tool with `@DBOS.step()`, the `set_event_async`/`recv_async` approval loop with its seven-day timeout, the `build_results` continuation, and the three HTTP routes); 126–132 for the crash question, the in-flight step repeating and the idempotency-key advice; 134–142 for the checkpointer split, the `StepPersistence` snapshots and tool-effect ledger; 144–181 for the approval routes; 183–187 for the stored `Conversation`, the conversation id as a key and the concurrent-update serialization; 189–219 for the cost bounds; 221–234 for fallback, SDK retries and Gateway failover; 236–238 for key placement; 240–257 for traces, the two-line setup and the content-exclusion settings; 259–289 for testing, evals and online evaluation; 291–297 for authorization, approval and sandboxing; 299–321 for the UI adapters and the authentication warning; 323–335 for the deployment shapes and version pinning. Evidence class: **Reported** — vendor documentation for its own framework; nothing was installed, built, deployed, approved, traced or evaluated.
