---
type: Concept
title: Pydantic AI multi-agent patterns
description: How to structure more than one Pydantic AI agent — the five-level complexity ladder, hand-wired delegation with usage forwarding and run-scoped cancellation, application-driven hand-off, deep-agent composition from Harness capabilities, and what a multi-agent trace has to show.
tags: [pydantic-ai, agents, architecture]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:45:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-multi-agent-guide
    resource: ../raw/guides/multi-agent-applications/index.md
    scope: ../raw/guides/multi-agent-applications/
    kind: documentation
    revision: sha256:2439e904aa5b1b1ecacfc0e0dcc1dbb8f5e89062198169f4f9f22304589598c1
    title: "Multi-agent Applications"
---

The vendor guide frames multi-agent design as roughly five levels of complexity rather than as competing libraries, reserves graph-based control flow for "the most complex cases", and notes that the levels combine inside one application[^pydantic-multi-agent-guide] The durable content is the boundary between them: who decides the next agent runs, whether control comes back, what state is shared across the boundary, and what an operator can see afterwards[^pydantic-multi-agent-guide] The page names no Pydantic AI version, so every API below is version-unknown.

## The five levels

| Level | Who picks the next agent | Does control come back | Where it is compiled |
| --- | --- | --- | --- |
| Single agent | Nobody — the familiar loop | — | The core agent pages |
| Agent delegation | The parent model, inside one of its tool calls | Yes, when the delegate finishes | This page, and the [Harness `SubAgents`](pydantic-ai-subagents.md) capability |
| Programmatic hand-off | Application code and/or a human, between runs | No — the next call is a new run | This page |
| Graph-based control flow | A typed state machine | Via the graph's edges | [pydantic-graph core library](pydantic-graph-core.md) and [graph builder](pydantic-ai-graph-builder.md) |
| Deep agent | The one agent itself, over a composed capability set | — | The [Harness](pydantic-ai-harness.md), below |

Delegation has two routes at the same level: a delegate called by hand from a tool, or the Harness's `SubAgents`, which turns the same idea into one `delegate_task` tool over a roster[^pydantic-multi-agent-guide] The hand-wired route is the one this page documents; the roster, per-delegate budgets, failure handling and disk-defined delegates are in [Harness subagents](pydantic-ai-subagents.md).

## Delegating to an agent from a tool

The mechanism is plain Python: a function tool on the parent calls `delegate.run(...)` and returns the delegate's output[^pydantic-multi-agent-guide] Several consequences follow from how agents are built.

Agents are stateless and designed to be global, so the delegate is not passed in through [dependencies](pydantic-ai-dependencies.md) — it is imported or module-level in both places[^pydantic-multi-agent-guide]

Usage does not aggregate by itself. Passing the parent's `ctx.usage` to the delegate's `usage=` makes the delegate's requests count towards the parent's `result.usage`: the guide's single-tool example prints `requests=3` for one parent request plus one delegate run, and the dependency example with a tool inside the delegate prints `requests=4` for two requests on each side[^pydantic-multi-agent-guide] Omit it and the parent's reported usage undercounts what the application actually spent.

Cancellation is run-scoped. A delegate that cancels itself surfaces to the parent as a **failed tool return** rather than cancelling the parent, while a `CancellationToken` shared from the parent cancels the whole tree of runs at once[^pydantic-multi-agent-guide] The surfaces that fire those cancellations are in [run controls](pydantic-ai-run-controls.md) and [tool execution, retries and failures](pydantic-ai-tool-execution.md).

Dependencies should match or narrow. The guide states the delegate "generally" needs the same dependencies as its caller or a subset, so the practical rule is to pass `ctx.deps` and declare the same `deps_type` on both agents — a delegate declaring more than the parent carries cannot be satisfied[^pydantic-multi-agent-guide] The example threads one `ClientAndKey` dataclass through an `httpx` client and API key into a tool inside the delegate.

Naming is optional and operationally useful. `name=` labels each agent's run span, so naming both agents is what lets a trace distinguish parent from delegate; when omitted the name is inferred from the variable the agent is assigned to and falls back to `'agent'` when it cannot be — agents held in a list or dict, for instance[^pydantic-multi-agent-guide]

A **full** hand-off, where the first agent should not regain control, is not a tool return at all: the guide points at an [output function](pydantic-ai-structured-output.md) for that case[^pydantic-multi-agent-guide]

## Handing off between runs in application code

Programmatic hand-off puts the decision in your code, or in a person, and calls the agents in succession; it drops the shared-dependency constraint, because each agent is a separate run with its own deps[^pydantic-multi-agent-guide] Three mechanics carry the state across those runs:

| Carried thing | How | Consequence |
| --- | --- | --- |
| Usage | One `RunUsage()` created by the application and passed to every `run(usage=…)` | The application's total, because no parent run exists to supply `ctx.usage` |
| Limits | One `UsageLimits(request_limit=15)` passed to every run | A budget for the whole app rather than one agent |
| History | `message_history=result.all_messages(...)` within one agent's retry loop | The next attempt sees the failed one instead of starting over |

The guide's flight example shows both halves of the retry pattern[^pydantic-multi-agent-guide] A `Failed` output model is unioned with the success model so the model can say it found nothing, and — because each union member is registered as a separate output tool — that failure is a normal typed tool result rather than an exception[^pydantic-multi-agent-guide] The loop then re-asks with `result.all_messages(output_tool_return_content='Please try again.')`, which replaces what the model reads at the failed output tool's return while keeping the conversation; the seat example loops until a `SeatPreference` comes back, re-asking the person each time.

Once each agent's loop is a function, the application body is just the sequence: find the flight, then the seat[^pydantic-multi-agent-guide] The guide spends its length on that decomposition rather than on orchestration syntax, which is the same position [Code as the agent graph](code-as-agent-graph.md) argues at more length.

## Graphs and deep agents

For the most complex control flow the vendor defers to `pydantic-graph` and states no criteria of its own beyond "graph-based state machine"[^pydantic-multi-agent-guide] The node model, registration and rendering are compiled in [pydantic-graph core library](pydantic-graph-core.md), the builder's fan-out and joins in [graph builder](pydantic-ai-graph-builder.md), and the vendor's own caution that most agents should stay on plain Python is recorded on both those pages.

A **deep agent** is the fifth level: one autonomous agent that composes the architectural patterns instead of delegating to other agents, and the guide's contribution is the mapping from each pattern to the Harness capability that ships it[^pydantic-multi-agent-guide]

| Deep-agent concern | Capability | Compiled in |
| --- | --- | --- |
| Planning and progress tracking | `Planning` | [Harness planning](pydantic-ai-harness-planning.md) |
| File reading, writing and editing | `FileSystem` and `Shell`, local or containerised | [file system](pydantic-ai-harness-filesystem.md), [shell](pydantic-ai-harness-shell.md) |
| Task delegation with isolated context | `SubAgents`, to stop recursive delegation | [Harness subagents](pydantic-ai-subagents.md) |
| Sandboxed code execution | `Shell` over a workspace backend such as `DockerContainer`, and `CodeMode` | [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md), [code mode](pydantic-ai-code-mode.md) |
| Context management | core Compaction and the Harness compaction strategies | No capture compiled here yet; [Anthropic context management](anthropic-context-management.md) covers only the Claude route |
| Human-in-the-loop | Tool approval for dangerous calls | [deferred tool approval](pydantic-ai-deferred-approvals.md) |
| Durable execution | State surviving API failures, crashes and restarts | [durable execution](pydantic-ai-durable-execution.md) |

`Coder` is named as the ready-made assembly of four of those — file system, shell, delegation and context management — usable whole or taken apart[^pydantic-multi-agent-guide] The contract is in [Harness coder](pydantic-ai-harness-coder.md).

## Seeing which agent did what

The guide treats multi-agent debugging as a tracing problem and gives one setup command, `uvx logfire-cli wizard --task pydantic-ai`, which has a coding agent add `logfire.configure()` and `logfire.instrument_pydantic_ai()` to the project[^pydantic-multi-agent-guide] The list of what the resulting trace shows is the operational requirement: which agent handled which part of the request, when and why one agent called another, end-to-end latency broken down by agent, token usage and cost per agent, what triggered the run (HTTP request, scheduled job, user action), and what happened inside tool calls including any instrumented database or HTTP work[^pydantic-multi-agent-guide] That is the same span tree [observability](pydantic-ai-observability.md) describes, read with agent identity as the grouping key — which is why the `name=` advice above matters.

Because the instrumentation is OpenTelemetry, a TypeScript frontend, API gateway or other-language service can join the same trace through Logfire's Python, JavaScript/TypeScript and Rust SDKs or any OTel-instrumented application, and any OTel-compatible backend is equally usable[^pydantic-multi-agent-guide]

## Limits

- The capture is one `index.md` (2,082 words as declared, 2,144 by local `wc -w`) naming **no Pydantic AI version, publication date, author or licence**, so this page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown[^pydantic-multi-agent-guide]
- Its samples pin `openai:gpt-6.1-sol` and `google:gemini-3.8-flash`, which no other capture here corroborates, and their printed `RunUsage` figures are vendor output, not measurements.
- The dependency rule is stated as a tendency ("generally"), so a delegate needing fewer dependencies is advice rather than an enforced constraint; whether `usage=` on a delegate also inherits the parent's `usage_limits` is not stated.
- What a delegate's unhandled exception does to the parent run, how deep delegation may nest, and whether the graph level has any Pydantic AI integration point beyond "use pydantic-graph" are all unstated.
- Excluded as example or decorative detail: the four Mermaid control-flow diagrams (the same facts carried as prose above), the full bodies of the two sample programs, and the closing link to the flight-booking example, which was read as a link and not followed.
- Nothing was installed, delegated, cancelled, handed off, graphed or traced, so every claim is **Reported** — none **Observed** or **Reproduced**.

## Relationships

- **Is the pattern-level companion to** [Harness subagents](pydantic-ai-subagents.md): the same delegation done by hand instead of through `delegate_task`, with usage forwarding, dependency narrowing and run-scoped cancellation as the hand-wired obligations.
- **Depends on** [Pydantic AI dependencies](pydantic-ai-dependencies.md) for the deps narrowing rule, and on [run controls](pydantic-ai-run-controls.md) for the usage limits a hand-off shares.
- **Shares its cancellation semantics with** [tool execution, retries and failures](pydantic-ai-tool-execution.md): a self-cancelling delegate arrives as a failed tool return.
- **Defers graph control flow to** [pydantic-graph core library](pydantic-graph-core.md) and [graph builder](pydantic-ai-graph-builder.md), and argues for code over graphs alongside [Code as the agent graph](code-as-agent-graph.md).
- **Assembles the deep-agent level from** [Harness](pydantic-ai-harness.md) capabilities — [planning](pydantic-ai-harness-planning.md), [filesystem](pydantic-ai-harness-filesystem.md), [shell](pydantic-ai-harness-shell.md), [subagents](pydantic-ai-subagents.md), [code mode](pydantic-ai-code-mode.md), compaction, [approvals](pydantic-ai-deferred-approvals.md) and [durable execution](pydantic-ai-durable-execution.md) — with [Coder](pydantic-ai-harness-coder.md) as the prebuilt assembly.
- **Is made readable through** [observability](pydantic-ai-observability.md): agent names become span identity, and per-agent latency, tokens and cost are what the trace is read for.

[^pydantic-multi-agent-guide]: Pydantic Docs, "Multi-agent Applications" (<https://pydantic.dev/docs/ai/guides/multi-agent-applications/>, `domain: pydantic.dev`, `language: en`, 2,082 words as declared and 2,144 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/guides/multi-agent-applications/index.md`, content digest sha256:2439e904. Lines 11–19 for the five levels and the composing rule; §"Agent delegation" (21–103) for the tool-return mechanism, the output-function alternative (23), agents as stateless globals kept out of deps (25), `ctx.usage` forwarding to `usage=` and the printed `requests=3`/`requests=4` counts (27, 82, 62–70, 178–190), run-scoped cancellation and the shared `CancellationToken` (29), `name=` span labelling with variable inference and the `'agent'` fallback (76), and the same-or-subset dependency rule with `deps_type` and `deps=ctx.deps` (100–145); §"Programmatic agent hand-off" (205–350) for application/human choosing the next agent and independent deps (207–209), the `FlightDetails | Failed` union and separate output tools (226–232, 314), the shared `RunUsage()` and `UsageLimits` (232–303), `all_messages(output_tool_return_content='Please try again.')` (265), and the seat-preference loop (291–330); §"Pydantic Graphs" (352–354) for the deferral; §"Deep Agents" (356–368) for the seven concerns, their capability links and the `Coder` assembly; §"Observing Multi-Agent Systems" (370–402) for the `uvx logfire-cli wizard --task pydantic-ai` setup, the six things Logfire shows, and the multi-language OpenTelemetry visibility. Evidence class: **Reported** — vendor guide naming no version; nothing was installed, run or traced.
