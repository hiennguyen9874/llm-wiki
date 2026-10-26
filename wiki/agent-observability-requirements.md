---
type: Concept
title: Agent observability requirements
description: Why request-scoped APM and prompt tracers miss agent failures, and the five signals an agent observability layer must put on one trace.
tags: [ml, agents, observability, tracing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:20:00Z }
stale_after: 2027-04-01
sources:
  - id: vstrom-obs-2026
    resource: ../raw/agent-observability-layer/index.md
    scope: ../raw/agent-observability-layer/
    kind: article
    revision: sha256:96ff417fa583a5eb8cf66fe05b55eb3bf99c1eed
    title: "AI agent observability: the production layer you need"
---

An agent observability layer is not application monitoring with LLM attributes. Because the same query can produce a different tool-call sequence and reasoning path on consecutive runs, and because the costly failures — wrong tool arguments, abandoned context, degraded reasoning over a long chain — usually raise no exception, the layer must capture the agentic loop as spans, correlate LLM, tool, database and business-logic work on one timeline, attach token cost and latency per step, correlate parent and child spans across handoffs, and rest on a portable OpenTelemetry standard[^vstrom-obs-2026] Vstorm frames these as the requirements a team checks *before* choosing a tool; [Pydantic AI observability](pydantic-ai-observability.md) describes one implementation of them[^vstrom-obs-2026]

## Why request-scoped monitoring misses the failure

Traditional APM assumes a deterministic path: an HTTP handler that returns the same response for the same input[^vstrom-obs-2026] Agents invalidate that assumption in two directions at once[^vstrom-obs-2026]

- **Non-reproducible behaviour.** Consecutive runs of one query differ in tool-call sequence, intermediate reasoning and final output[^vstrom-obs-2026]
- **Silent failure.** Infinite loops, wrong tool selection, context abandonment and quality decay along a long reasoning chain rarely throw; the catchable exception is replaced by a confident-looking wrong answer[^vstrom-obs-2026]

The illustrative incident in the source is the shape to design against: a model called the right tool with the wrong argument three steps upstream, then reasoned smoothly over the bad result to a fluent, plausible, incorrect answer. No exception, no failed test, clean logs[^vstrom-obs-2026]

Two consequences follow from that shape. Debugging moves from the request to the **session** — isolated traces are useless until shared identifiers connect them into one readable execution graph[^vstrom-obs-2026] And cost and latency compound step by step, so without per-step cost tracking an agent's bill arrives before its cost profile does[^vstrom-obs-2026]

## The five requirements as a checklist

| Requirement | What it must capture | Failure it exposes |
| --- | --- | --- |
| Agentic loop as spans | Plan, call tool, observe, iterate — each its own step with duration and error surface | A divergence you can point at instead of re-running and hoping |
| One correlated, full-stack trace | The LLM call, tool execution, database query and business logic on a single timeline | Whether the fault is the model, the tool, or the backend |
| Per-step cost and latency | Token usage and spend attached to each step, not summed at the end | A cost surprise discovered on the invoice |
| Session correlation | Parent and child spans across multi-agent handoffs, so orchestrator and workers read as one graph | Which link in a delegated chain degraded |
| A portable standard underneath | Instrumentation on OpenTelemetry, with merged semantic conventions for LLM workloads | Rewriting instrumentation when the vendor changes |

The table's contents are the source's five bullets restated; OpenTelemetry having merged semantic conventions for LLM workloads is reported as the standard-definition basis for OpenTelemetry agent tracing[^vstrom-obs-2026]

## Why the usual substitutes fall short

Three fallbacks half-work, which is described as the dangerous part[^vstrom-obs-2026]

- **Traditional APM.** Captures latency and error rates but, without an AI/agent integration, has no vocabulary for tokens, prompts, tool calls or eval results[^vstrom-obs-2026]
- **Print statements and log spelunking.** Workable for a demo, hopeless past a few hundred runs a day[^vstrom-obs-2026]
- **LLM-only tracing tools.** The closest fit and still short: an LLM-focused integration can capture model and tool spans automatically, while database and other application work needs application-level instrumentation[^vstrom-obs-2026]

The source's own comparison places Sentry/Datadog in traditional API, database, cache, background-task and system-metric monitoring, LangSmith in LLM and agent tracing, and Pydantic Logfire across both columns[^vstrom-obs-2026] That table is vendor-framed and was not independently checked.

## Limits

- The source is a guest post from Vstrom published by Pydantic, and it ends by promoting Logfire and Vstrom's own Pydantic Deep Agents harness; it is vendor material with a stated, partial disclosure[^vstrom-obs-2026]
- No measurement, benchmark, incident count or cost figure backs the claims; the opening incident is the author's anecdote[^vstrom-obs-2026]
- Competing tools' coverage is asserted in a marketing table, not tested; treat the column assignment as the author's claim[^vstrom-obs-2026]
- The article names no Pydantic AI version and no OpenTelemetry semantic-convention version[^vstrom-obs-2026]
- Evidence class: **Reported**.

## Relationships

- **Implemented by** [Pydantic AI observability](pydantic-ai-observability.md), which documents Logfire as an opinionated OpenTelemetry wrapper over exactly these signals.
- **Closes into** [Pydantic Evals](pydantic-evals.md): captured production traces are pitched as the dataset an evaluation suite is built from.
- **Feeds** [agent optimization platforms](agent-optimization-platforms.md): this checklist is the observe half of the diagnose-propose-ship loop that page defines.
- **Frames** the trace-driven improvement loop noted in [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md), where an agent reads its own runs.
- **Operationalized by** [Logfire MCP server](logfire-mcp-server.md), which turns the correlated trace into an ad hoc SQL query surface for a coding agent rather than a dashboard.

[^vstrom-obs-2026]: Antoni Kozelski (Vstrom), "AI agent observability: the production layer you need", Pydantic, published 2026-10-01, guest post; §"The failure mode traditional monitoring can't see" (raw lines 19–26) for non-reproducibility, silent failure modes, the session unit of debugging and per-step cost; §"How teams cope today, and why it doesn't hold" (lines 27–34) for the APM, log-spelunking and LLM-only gaps; §"What the AI agent observability layer must capture" (lines 35–56) for the five requirements, the comparison table and the merged OTel semantic conventions; §"Doing it with Pydantic Logfire" and the closing harness promotion (lines 57–90) for the vendor disclosure. Local capture: `raw/agent-observability-layer/index.md`, 1,113 words, content digest sha256:96ff417f. The single attachment `assets/production-to-evaluation-flywheel.png` was inspected and matches the caption's four-stage flywheel. Evidence class: **Reported** — an opinion piece with no measurements.
