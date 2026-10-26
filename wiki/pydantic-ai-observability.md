---
type: Concept
title: Pydantic AI observability
description: Pydantic AI instruments with plain OpenTelemetry, defaults to instrumentation v5 with aggregated usage attributes, and prints a first-run banner until a backend is configured.
tags: [ml, pydantic-ai, agents, observability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:12:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
  - id: vstrom-obs-2026
    resource: ../raw/agent-observability-layer/index.md
    scope: ../raw/agent-observability-layer/
    kind: article
    revision: sha256:96ff417fa583a5eb8cf66fe05b55eb3bf99c1eed
    title: "AI agent observability: the production layer you need"
  - id: pydantic-langfuse-alts-2026
    resource: ../raw/best-langfuse-alternatives/index.md
    scope: ../raw/best-langfuse-alternatives/
    kind: article
    revision: sha256:ca8ebbf2906627e3d5b930e13b62421d77cefb001be9758f3487f2a344b13ace
    title: "Best Langfuse Alternatives in 2026"
  - id: pydantic-image-gen-2026
    resource: ../raw/image-generation/index.md
    scope: ../raw/image-generation/
    kind: article
    revision: sha256:2563fee14c8dd9209912c64e26cb10d888eb54d1e0d027343f546fe21ceaf69e
    title: "Generate images with Pydantic AI"
  - id: jev-live-view-2026
    resource: ../raw/jev-pydantic-ai-live-view/index.md
    scope: ../raw/jev-pydantic-ai-live-view/
    kind: article
    revision: sha256:288f23ddf22c009f4ada93b87fcc6526a089ea7ece6d6c5a229a7dd98e2636f0
    title: "Pydantic AI agents on Jev, traced in Logfire"
  - id: colvin-code-is-graph-2026
    resource: ../raw/the-code-is-the-graph/index.md
    scope: ../raw/the-code-is-the-graph/
    kind: article
    revision: sha256:d8803b5fa767d23f0a03bda63f364781d1f1f476ba4e3d243f33e05dea5f21be
    title: "The code is the graph"
---

Pydantic AI's instrumentation is plain OpenTelemetry, so any OTel backend works; Logfire is Pydantic's commercial hosted platform, with a free Personal plan and an Enterprise self-hosted option on your own Kubernetes cluster[^dd-v2-tour-2026] Local development needs two lines:

```python
import logfire
logfire.configure(send_to_logfire='if-token-present')  # plain OTel; any backend works
logfire.instrument_pydantic_ai()
```

## What v2 changed on the wire

Instrumentation v5 is the default in V2, and run spans now report usage under `gen_ai.aggregated_usage.*`. Any dashboard query that read token totals from run spans has to change[^dd-v2-tour-2026]

Model-request spans also carry prompt-cache health attributes from v2.55 — `pydantic_ai.cache.*` hit ratio, cached-prefix size, a `pydantic_ai.cache.collapse` event when a prefix is lost unexpectedly, and a `pydantic_ai.cache.not_enabled` flag[^dd-v2-tour-2026] See [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).

## Decision spans

Instrumentation also covers decisions as well as conversations. From Pydantic AI 2.50.0, every request sent by a `DecisionModel` — the base class behind TypeSafe Jev's `TypeSafeModel` — produces a `decide` span nested under the `chat` span, carrying the questions, the answers with their probabilities, the thresholds applied and the route being filled[^jev-live-view-2026] Logfire renders it as a **Classifier output** panel on the Agent Run tab, with each rubric level's probability and a link to the underlying span[^jev-live-view-2026] The answers follow the same `include_content` setting as every other span, so with content capture off the question types and routes survive while the text and answers do not[^jev-live-view-2026] See [Logfire decision tracing](logfire-decision-tracing.md).

## Instrumenting more than agents

Instrumentation is not limited to agent runs: an `ImageGenerator(..., instrument=True)` traces its own image-generation call, so provider calls appear beside agent and tool spans on one trace[^pydantic-image-gen-2026] The rendering is not uniform yet — on the recorded stack, Pydantic AI 2.41.0 with Logfire 5.0.0, an image returned directly by the `ImageGeneration` capability showed as JSON rather than with the preview Logfire renders for a tool's own binary content, an acknowledged gap tracked as an issue[^pydantic-image-gen-2026] See [Pydantic AI image generation](pydantic-ai-image-generation.md).

## The trace is the graph

When an orchestrator's choreography is code rather than a graph object, the trace already has the shape of the run. Sub-agents are Pydantic AI agents, so each run and model call is an OpenTelemetry span in the orchestrator's trace, and the fan-out, the join and every retry appear nested the way the code was written — which is the argument that agent observability needs no graph visualizer, because the trace is the drawing[^colvin-code-is-graph-2026] This page's span tree is what that rests on; the architecture argument is in [Code as the agent graph](code-as-agent-graph.md).

The claim assumes the nesting follows the code, which holds for an `asyncio.gather` fan-out over agent calls; nothing in the source shows how a nested sub-agent run appears when the sub-agent is itself a long-lived session or a durable-workflow activity.

## The first-run banner

Until instrumentation is configured, the first run prints a banner to stderr when a person or a coding agent is reading it. It is suppressed under pytest, when `CI` is set, or with `PYDANTIC_AI_NO_BANNER=1`[^dd-v2-tour-2026] The banner is the only in-band nudge that a run is uninstrumented, which is why it appears in scripts that never configured Logfire.

## OpenTelemetry is also the eval substrate

The agentic evaluators in [Pydantic Evals](pydantic-evals.md) read the local span tree, so they need the `logfire` SDK configured even when nothing is sent anywhere. Online evaluation emits `gen_ai.evaluation.result` events into the same pipeline, keyed by the agent's `name`[^dd-v2-tour-2026] Observability is therefore not optional instrumentation for teams that grade trajectories; it is the input.

## Logfire as the delivery path

Vstrom's requirements checklist uses Logfire as its worked example: an AI-native platform from the Pydantic team, built as an "opinionated wrapper around OpenTelemetry", adopted by initializing it and instrumenting the agent at the entry point instead of editing agent code — `logfire.configure()` then `logfire.instrument_pydantic_ai()`[^vstrom-obs-2026] That matches the boundary above: the wire format stays plain OTel, so the backend remains swappable.

Reported as free once the spans exist: conversation replay, tool-call inspection, and token and cost breakdowns, because Logfire detects GenAI semantic conventions in the spans automatically[^vstrom-obs-2026] The claimed differentiator over LLM-only tooling is breadth — API, database, cache and background-task work land on the same trace as the agent, so a debugging session can answer "was it the model, the tool, or the backend?"[^vstrom-obs-2026] Two query surfaces are named: the data over PostgreSQL-compatible SQL, and an MCP server, so a coding agent can interrogate production without a purpose-built dashboard[^vstrom-obs-2026] [Logfire MCP server](logfire-mcp-server.md) covers that MCP surface in detail.

The post also generalises the setup to anything built on Pydantic AI, citing Vstrom's own Pydantic Deep Agents harness as lighting up with the same one-line instrumentation[^vstrom-obs-2026] It names no Pydantic AI version, and none of these capabilities was exercised here. See [agent observability requirements](agent-observability-requirements.md) for the framework-independent checklist these features are measured against.

## The commercial boundary

Logfire's own platform is proprietary while its SDKs are MIT, self-hosting is Enterprise only, and the published hosted entry is a free Personal plan of 10 million records a month with 30-day retention and a $49/month Team plan with $2 per additional million records[^pydantic-langfuse-alts-2026] The meter is the SDK's record — spans, logs and metrics share one price — so instrumenting the whole application rather than the agent is exactly what puts volume on the bill, which is the published catch of recommending it[^pydantic-langfuse-alts-2026] Langfuse is the mirror image on both axes: MIT core that self-hosts without usage limits, but traces-only ingest[^pydantic-langfuse-alts-2026] The eight-platform licence and billing comparison these figures come from, and the case where Enterprise-only self-hosting disqualifies Logfire, are in [LLM observability platform comparison](llm-observability-platform-comparison.md).

## Limits

- No backend, collector, or Logfire account was exercised; attribute names and the v5 default are reported from the release and docs summary[^dd-v2-tour-2026]
- The Logfire capability claims in the section above — replay, cost breakdown, full-stack coverage, SQL and MCP access, Deep Agents inheritance — come from a Vstrom guest post hosted by Pydantic and are vendor material[^vstrom-obs-2026] This page stays `stable` because its instrumentation, cache-attribute and banner claims also rest on the independent third-party source cited above.
- Logfire's plan limits, retention, and self-hosted requirements are reported only from the 2026-08-26 Pydantic comparison above; no Logfire price page was fetched and the free-tier cap, Team price and retention were not exercised[^pydantic-langfuse-alts-2026]
- The banner behaviour was observed by the author on every uninstrumented run, not in this ingest.
- The decision-span section rests on one vendor article published 2026-09-29 that describes a feature of its own ecosystem; no `decide` span was produced or opened, and the source names no Logfire version[^jev-live-view-2026]
- The "trace is the drawing" reading is the `pydantic-graph` author's argument on Pydantic's site; no orchestrated run's trace was opened here, and the claim that spans nest exactly as the code was written is reported rather than observed[^colvin-code-is-graph-2026]
- Evidence class: **Reported**.

## Relationships

- **Carries** the attributes exposed by [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).
- **Feeds** [Pydantic Evals](pydantic-evals.md), offline and online.
- **Implements** the framework-independent checklist in [agent observability requirements](agent-observability-requirements.md).
- **Surfaces** the warnings and failure modes described in [Pydantic AI run controls](pydantic-ai-run-controls.md).
- **Queried through** [Logfire MCP server](logfire-mcp-server.md), the hosted MCP interface that turns these spans into SQL answers for a coding agent.
- **Substitutes for a graph visualizer** under the argument in [Code as the agent graph](code-as-agent-graph.md): a code-shaped orchestration leaves its fan-out, join and retries in the span tree.
- **Feeds** [Logfire agent optimization](logfire-agent-optimization.md), which puts an optimizer and managed configuration on the same trace.
- **Is priced and licensed in** [LLM observability platform comparison](llm-observability-platform-comparison.md), the vendor comparison that ranks this delivery path first and names Enterprise-only self-hosting as its disqualifier.
- **Traces** [image generation](pydantic-ai-image-generation.md) through `instrument=True`, with a known preview gap for capability-returned images at 2.41.0.
- **Traces** [realtime voice agents](pydantic-ai-realtime-voice.md) as one session span per call with `user speech` and `chat` spans, transcripts written into `pydantic_ai.all_messages`, and two drop counters — no special backend handling.
- **Gains a decision span kind** at 2.50.0, rendered as [Logfire decision tracing](logfire-decision-tracing.md) rather than as a conversation.
- **Chooses among backends in** [OpenTelemetry backend selection](opentelemetry-backend-selection.md), which treats this instrumentation as the portable asset and the backend as the renegotiable part.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Observability: Logfire or any OpenTelemetry backend" (raw lines 594–613) for the OTel-versus-Logfire boundary, the two-line setup, instrumentation v5 and `gen_ai.aggregated_usage.*`, cache attributes, and the banner; §"Pydantic Evals" for the shared span tree and `gen_ai.evaluation.result` events. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary; nothing was instrumented or exported.

[^vstrom-obs-2026]: Antoni Kozelski (Vstrom), "AI agent observability: the production layer you need", Pydantic, published 2026-10-01, guest post; §"Doing it with Pydantic Logfire" (raw lines 57–75) for the OpenTelemetry-wrapper description, the two-call setup, automatic GenAI convention detection, replay and cost breakdowns, cross-stack tracing, SQL and MCP access; §"What changes when observability is a first-class layer" (lines 76–85) for the Pydantic AI inheritance claim and Pydantic Deep Agents. Local capture: `raw/agent-observability-layer/index.md`, content digest sha256:96ff417f. Evidence class: **Reported** — vendor guest post; nothing was configured or traced.

[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, §"Write your own tool and trace it in Logfire" (raw lines 103–140) for `instrument=True`, the 2.41.0/Logfire 5.0.0 stack, and the capability-returned-image preview gap. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; no trace was opened here.
[^pydantic-langfuse-alts-2026]: Bill Easton, "Best Langfuse Alternatives in 2026", Pydantic, published 2026-08-26; §"1. Pydantic Logfire: best Langfuse alternative overall" (raw lines 46–52) for the proprietary-platform/MIT-SDK split, Enterprise-only self-hosting, Personal 10M records with 30-day retention, the $49/month Team plan with $2 per additional million records, the per-record meter and the volume catch; §"Comparison at a glance" (lines 102–113) for the same figures in table form and the Langfuse traces-only ingest contrast; §"Frequently asked questions" (lines 137–149) for the Logfire-versus-Langfuse self-hosting distinction. Local capture: `raw/best-langfuse-alternatives/index.md`, content digest sha256:ca8ebbf2. Evidence class: **Reported** — vendor comparison article; no price page fetched, no account or plan exercised.

[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"The chat span wasn't enough" (raw lines 59–68) for `DecisionModel`, the `decide` span nested under `chat` in 2.50.0 and its recorded payload, and the `include_content` behaviour; §"Seeing it in Live view" (lines 70–82) for the Agent Run tab's **Classifier output** panel, the per-level rubric probabilities and **View decision span**. Evidence class: **Reported** — vendor article; no span, trace or Logfire project was opened here.
[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Long live graphs" (raw lines 145–167) for the claim that each sub-agent run and model call is an OpenTelemetry span in the orchestrator's trace, that fan-out, join and retries nest as the code was written, and that agent observability therefore needs no graph visualizer. Evidence class: **Reported** — vendor article; no trace was produced or inspected here.
