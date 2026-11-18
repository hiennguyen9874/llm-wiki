---
type: Concept
title: Pydantic AI observability
description: Pydantic AI instruments with plain OpenTelemetry, defaults to instrumentation v5 with aggregated usage attributes, and prints a first-run banner until a backend is configured.
tags: [ml, pydantic-ai, agents, observability]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:05:00Z }
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
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
  - id: pydantic-multi-agent-guide
    resource: ../raw/guides/multi-agent-applications/index.md
    scope: ../raw/guides/multi-agent-applications/
    kind: documentation
    revision: sha256:2439e904aa5b1b1ecacfc0e0dcc1dbb8f5e89062198169f4f9f22304589598c1
    title: "Multi-agent Applications"
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
  - id: pydantic-logfire-docs
    resource: ../raw/integrations/logfire/index.md
    scope: ../raw/integrations/logfire/
    kind: documentation
    revision: sha256:5ea6a3e098a0dc8e4c1337ae9bebbef2d5489cc135597569711c1a96e77d6381
    title: "Pydantic Logfire Debugging and Monitoring"
---

Pydantic AI's instrumentation is plain OpenTelemetry, so any OTel backend works; Logfire is Pydantic's commercial hosted platform, with a free Personal plan and an Enterprise self-hosted option on your own Kubernetes cluster[^dd-v2-tour-2026] Local development needs two lines:

```python
import logfire
logfire.configure(send_to_logfire='if-token-present')  # plain OTel; any backend works
logfire.instrument_pydantic_ai()
```

## What v2 changed on the wire

Instrumentation v5 is the default in V2, and run spans now report usage under `gen_ai.aggregated_usage.*`. Any dashboard query that read token totals from run spans has to change[^dd-v2-tour-2026]

Model-request spans also carry prompt-cache health attributes from v2.55 — `pydantic_ai.cache.*` hit ratio, cached-prefix size, a `pydantic_ai.cache.collapse` event when a prefix is lost unexpectedly, and a `pydantic_ai.cache.not_enabled` flag[^dd-v2-tour-2026] See [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md) for what places a cache, and [prompt-cache health](pydantic-ai-prompt-cache-health.md) for reading the counters and the collapse signals.

One provider-specific attribute names the transport rather than the model: with OpenAI Responses WebSockets enabled, each request's `chat` span records `pydantic_ai.transport` as `'websocket'` or `'http'`, or under Temporal on the model activity span within that trace, and HTTP-only mode leaves it unset[^pydantic-openai-2026] See [OpenAI Responses API features](openai-responses-api-features.md).

## Instrumenting for production

The two-line setup above is what `uvx logfire-cli wizard --task pydantic-ai` writes on your machine: it signs you in, picks or creates a project, and has your coding agent add that instrumentation[^pydantic-production-docs] In production a write token is what lets the spans leave the process; the free tier covers getting started[^pydantic-production-docs]

Two details matter beyond the two lines[^pydantic-production-docs]:

- **Without the Logfire SDK**, `Agent.instrument_all()` or the `Instrumentation` capability does the same against your own tracer provider.
- **The run nests inside its request**: the same SDK instruments FastAPI and the HTTP requests to the provider, so a run appears inside the request that started it, with the raw prompt it sent.

Every run carries its `run_id` and `conversation_id`, and run metadata such as a tenant or user ID lands on the run span, so traces can be filtered by it[^pydantic-production-docs]

### Content is on by default

Telemetry includes prompts, completions and tool arguments by default. `include_content=False` on `InstrumentationSettings` keeps them out of Pydantic AI's spans, and `include_binary_content=False` leaves out the bytes of images, audio and documents[^pydantic-production-docs] Neither setting touches run metadata, your own spans, or captured HTTP request bodies, so those are configured separately[^pydantic-production-docs] A third flag, `include_model_request_parameters=False`, drops the per-request schema attribute as a size measure; all three and what each one covers are on [Pydantic AI instrumentation format](pydantic-ai-instrumentation-format.md).

## Backend routes and raw HTTP capture

The vendor Logfire page adds the detail the wizard hides, and states the cost of not configuring it: support is built in but optional, so with the `logfire` package absent or unconfigured there is virtually no overhead and nothing is sent[^pydantic-logfire-docs] Setup is `uvx logfire-cli wizard --task pydantic-ai`, which signs you in or creates a free account, picks or creates a project, and hands the instrumentation to your coding agent, which then checks that the first trace arrived; a coding agent can instead run `uvx logfire-cli --no-input --output json wizard --task pydantic-ai --print-prompt` and follow what it returns[^pydantic-logfire-docs] By hand, `uvx logfire-cli auth` authenticates the environment and `uvx logfire-cli init` connects the directory to a project, writing a `.logfire` directory in the working directory that the SDK reads as its configuration at run time — `logfire.configure()` finds the write token there unless one is passed directly[^pydantic-logfire-docs]

The SDK ships with `pydantic-ai`; on the slim package it is the `logfire` extra, `pip install "pydantic-ai-slim[logfire]"`[^pydantic-logfire-docs] The two-line setup is then `logfire.configure()` followed by `logfire.instrument_pydantic_ai()`, and after that a trace is generated for each run with spans for each model call and tool execution[^pydantic-logfire-docs]

Naming the agent matters here: `name=` labels its run span, and without it the name is inferred from the variable the agent is assigned to, falling back to `'agent'` when it can't be — agents kept in a list or dict — which is the case where several agents run in one app and their traces have to be told apart[^pydantic-logfire-docs]

### Local development against a different production backend

`send_to_logfire='if-token-present'` makes Logfire a development choice rather than an architectural one[^pydantic-logfire-docs] On a laptop, `logfire.configure()` reads the gitignored `.logfire` token and sends; a deployment without that directory or a `LOGFIRE_TOKEN` sends nothing to Logfire, and the SDK still exports to whatever `OTEL_EXPORTER_OTLP_ENDPOINT` names — with the warning that `.gitignore` does not keep the directory out of a Docker build context, so it has to be excluded there too[^pydantic-logfire-docs] If the application sets up its own OpenTelemetry SDK in production instead, the docs' advice is to call the two logfire lines only when developing locally and use `Agent.instrument_all()` in production, which uses the global providers that SDK configured[^pydantic-logfire-docs]

### Sending somewhere other than Logfire

Three routes, from most to least Logfire[^pydantic-logfire-docs]:

- **The Logfire SDK, another backend**: set `OTEL_EXPORTER_OTLP_ENDPOINT` and call `logfire.configure(send_to_logfire=False)` — without that flag the data goes to both Logfire and the named backend, and a backend needing authentication takes the other standard OTel environment variables.
- **No Logfire at all**: install `opentelemetry-sdk` and `opentelemetry-exporter-otlp`, build an `OTLPSpanExporter` into a `BatchSpanProcessor` and a `TracerProvider`, call `set_tracer_provider`, then `Agent.instrument_all()`.
- **A custom provider**: the global `TracerProvider` is the default, set automatically by `logfire.configure()` or manually by `set_tracer_provider`; a different one is passed as `InstrumentationSettings(tracer_provider=...)`, on an `Instrumentation` capability for one agent or through `Agent.instrument_all(settings)`.

### Raw HTTP bodies

Provider SDKs use either `httpx` or `httpx2` internally — except Bedrock, which uses boto3 — so Logfire's HTTPX instrumentation is what records the raw provider request and response, with `instrument_httpx(capture_all=True)` capturing headers and body for both directions[^pydantic-logfire-docs] `httpx2` instrumentation needs `opentelemetry-instrumentation-httpx>=0.65b0`, which the `logfire` extra installs; with a hand-pinned OpenTelemetry below that version, `logfire.instrument_httpx()` reports the missing requirement and emits no `httpx2` spans[^pydantic-logfire-docs] This capture sits outside `include_content=False`, so a deployment redacting agent spans can still ship prompt bodies through it[^pydantic-logfire-docs]

Realtime speech-to-speech sessions are instrumented by the same `logfire.instrument_pydantic_ai()` call rather than a separate one: a session appears as an agent run whose child spans mark each model response, tool call and turn boundary as the conversation unfolds[^pydantic-logfire-docs] See [realtime voice agents](pydantic-ai-realtime-voice.md).

## Decision spans

Instrumentation also covers decisions as well as conversations. From Pydantic AI 2.50.0, every request sent by a `DecisionModel` — the base class behind TypeSafe Jev's `TypeSafeModel` — produces a `decide` span nested under the `chat` span, carrying the questions, the answers with their probabilities, the thresholds applied and the route being filled[^jev-live-view-2026] Logfire renders it as a **Classifier output** panel on the Agent Run tab, with each rubric level's probability and a link to the underlying span[^jev-live-view-2026] The answers follow the same `include_content` setting as every other span, so with content capture off the question types and routes survive while the text and answers do not[^jev-live-view-2026] See [Logfire decision tracing](logfire-decision-tracing.md).

## Instrumenting more than agents

Instrumentation is not limited to agent runs: an `ImageGenerator(..., instrument=True)` traces its own image-generation call, so provider calls appear beside agent and tool spans on one trace[^pydantic-image-gen-2026] The rendering is not uniform yet — on the recorded stack, Pydantic AI 2.41.0 with Logfire 5.0.0, an image returned directly by the `ImageGeneration` capability showed as JSON rather than with the preview Logfire renders for a tool's own binary content, an acknowledged gap tracked as an issue[^pydantic-image-gen-2026] See [Pydantic AI image generation](pydantic-ai-image-generation.md).

## The trace is the graph

When an orchestrator's choreography is code rather than a graph object, the trace already has the shape of the run. Sub-agents are Pydantic AI agents, so each run and model call is an OpenTelemetry span in the orchestrator's trace, and the fan-out, the join and every retry appear nested the way the code was written — which is the argument that agent observability needs no graph visualizer, because the trace is the drawing[^colvin-code-is-graph-2026] This page's span tree is what that rests on; the architecture argument is in [Code as the agent graph](code-as-agent-graph.md).

The claim assumes the nesting follows the code, which holds for an `asyncio.gather` fan-out over agent calls; nothing in the source shows how a nested sub-agent run appears when the sub-agent is itself a long-lived session or a durable-workflow activity.

Read across agents rather than within one run, the span tree is also the debugging surface the vendor guide specifies for a multi-agent system: which agent handled which part of the request, when and why one agent called another, latency, token usage and cost broken down per agent, the trigger that started the run, and any instrumented work inside tool calls[^pydantic-multi-agent-guide] This is why agent `name=` matters there — it is the grouping key that separates a parent from a delegate[^pydantic-multi-agent-guide] The setup command it gives, `uvx logfire-cli wizard --task pydantic-ai`, is the same instrumentation as the two lines above, and the guide points at Logfire's Python, JavaScript/TypeScript and Rust SDKs or plain OTel to put the rest of a stack on that trace[^pydantic-multi-agent-guide] See [multi-agent patterns](pydantic-ai-multi-agent-patterns.md).

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
- The production path — the wizard, `Agent.instrument_all()`, the `Instrumentation` capability, the run-metadata filter and the two content flags with their limits — comes from the vendor's own production page, which names no version or date. No wizard was run, no key supplied, no span or HTTP body inspected, and whether `include_content=False` is the default anywhere is unstated[^pydantic-production-docs]
- The setup, export and HTTP-capture sections rest on the vendor's own integration page, which names **no Pydantic AI, Logfire or `opentelemetry-instrumentation-httpx` version, no publication date and no author**, so its added sections are version-unknown even though the page as a whole keeps `stable` on its independently sourced instrumentation claims. Nothing was installed, authenticated, initialized, exported, captured or streamed[^pydantic-logfire-docs]
- The decision-span section rests on one vendor article published 2026-09-29 that describes a feature of its own ecosystem; no `decide` span was produced or opened, and the source names no Logfire version[^jev-live-view-2026]
- The "trace is the drawing" reading is the `pydantic-graph` author's argument on Pydantic's site; no orchestrated run's trace was opened here, and the claim that spans nest exactly as the code was written is reported rather than observed[^colvin-code-is-graph-2026]
- Evidence class: **Reported**.

## Relationships

- **Carries** the attributes exposed by [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md).
- **Emits the format detailed in** [Pydantic AI instrumentation format](pydantic-ai-instrumentation-format.md): format versions 2–6 with v5 the default, aggregated-usage attribute names, three histograms, and the three redaction settings this page's content section names.
- **Names the transport** on OpenAI `chat` spans through `pydantic_ai.transport`, as [OpenAI Responses API features](openai-responses-api-features.md) records.
- **Feeds** [Pydantic Evals](pydantic-evals.md), offline and online.
- **Implements** the framework-independent checklist in [agent observability requirements](agent-observability-requirements.md).
- **Surfaces** the warnings and failure modes described in [Pydantic AI run controls](pydantic-ai-run-controls.md).
- **Queried through** [Logfire MCP server](logfire-mcp-server.md), the hosted MCP interface that turns these spans into SQL answers for a coding agent.
- **Is read across agents in** [multi-agent patterns](pydantic-ai-multi-agent-patterns.md): per-agent latency, tokens and cost, the delegation decisions and the trigger for the run, grouped by the `name=` each agent carries[^pydantic-multi-agent-guide]
- **Substitutes for a graph visualizer** under the argument in [Code as the agent graph](code-as-agent-graph.md): a code-shaped orchestration leaves its fan-out, join and retries in the span tree.
- **Feeds** [Logfire agent optimization](logfire-agent-optimization.md), which puts an optimizer and managed configuration on the same trace.
- **Is priced and licensed in** [LLM observability platform comparison](llm-observability-platform-comparison.md), the vendor comparison that ranks this delivery path first and names Enterprise-only self-hosting as its disqualifier.
- **Traces** [image generation](pydantic-ai-image-generation.md) through `instrument=True`, with a known preview gap for capability-returned images at 2.41.0.
- **Traces** [realtime voice agents](pydantic-ai-realtime-voice.md) as one session span per call with `user speech` and `chat` spans, transcripts written into `pydantic_ai.all_messages`, and two drop counters — no special backend handling.
- **Gains a decision span kind** at 2.50.0, rendered as [Logfire decision tracing](logfire-decision-tracing.md) rather than as a conversation.
- **Records** [model fallback](pydantic-ai-model-fallback.md) as one `chat` span that ends OK plus a `model request attempt <model name>` child span ending in ERROR per abandoned attempt, positioned by `pydantic_ai.model_request.attempt`.
- **Shows** [model concurrency](pydantic-ai-model-concurrency.md) contention as a waiting span carrying queue depth and configured limits, identified by the limiter's `name`.
- **Traces** [embeddings](pydantic-ai-embeddings.md) through `instrument=True` on one `Embedder` or `Embedder.instrument_all()` across all of them.
- **Chooses among backends in** [OpenTelemetry backend selection](opentelemetry-backend-selection.md), which treats this instrumentation as the portable asset and the backend as the renegotiable part.
- **Is made replay-safe on Temporal by** [Pydantic AI on Temporal](pydantic-ai-temporal.md), where `LogfirePlugin` installs Temporal's deterministic tracer before any client, worker or replayer exists.
- **Records the environment** as `pydantic_ai.workspace.id` on a run span even with `include_content=False`, because the id identifies the environment rather than content — per [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md).
- **Traces** [batched model requests](pydantic-ai-batch-processing.md) one batch at a time: a `batch <model>` span in a trace of its own links the `chat` span of every request in the batch, each check is a `batch check <model>` child, and each request's span carries `pydantic_ai.batch.id`.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Observability: Logfire or any OpenTelemetry backend" (raw lines 594–613) for the OTel-versus-Logfire boundary, the two-line setup, instrumentation v5 and `gen_ai.aggregated_usage.*`, cache attributes, and the banner; §"Pydantic Evals" for the shared span tree and `gen_ai.evaluation.result` events. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — docs summary; nothing was instrumented or exported.

[^vstrom-obs-2026]: Antoni Kozelski (Vstrom), "AI agent observability: the production layer you need", Pydantic, published 2026-10-01, guest post; §"Doing it with Pydantic Logfire" (raw lines 57–75) for the OpenTelemetry-wrapper description, the two-call setup, automatic GenAI convention detection, replay and cost breakdowns, cross-stack tracing, SQL and MCP access; §"What changes when observability is a first-class layer" (lines 76–85) for the Pydantic AI inheritance claim and Pydantic Deep Agents. Local capture: `raw/agent-observability-layer/index.md`, content digest sha256:96ff417f. Evidence class: **Reported** — vendor guest post; nothing was configured or traced.

[^pydantic-image-gen-2026]: David Sanchez, "Generate images with Pydantic AI", Pydantic, published 2026-09-14, §"Write your own tool and trace it in Logfire" (raw lines 103–140) for `instrument=True`, the 2.41.0/Logfire 5.0.0 stack, and the capability-returned-image preview gap. Local capture: `raw/image-generation/index.md`, content digest sha256:2563fee1. Evidence class: **Reported** — vendor announcement; no trace was opened here.
[^pydantic-langfuse-alts-2026]: Bill Easton, "Best Langfuse Alternatives in 2026", Pydantic, published 2026-08-26; §"1. Pydantic Logfire: best Langfuse alternative overall" (raw lines 46–52) for the proprietary-platform/MIT-SDK split, Enterprise-only self-hosting, Personal 10M records with 30-day retention, the $49/month Team plan with $2 per additional million records, the per-record meter and the volume catch; §"Comparison at a glance" (lines 102–113) for the same figures in table form and the Langfuse traces-only ingest contrast; §"Frequently asked questions" (lines 137–149) for the Logfire-versus-Langfuse self-hosting distinction. Local capture: `raw/best-langfuse-alternatives/index.md`, content digest sha256:ca8ebbf2. Evidence class: **Reported** — vendor comparison article; no price page fetched, no account or plan exercised.

[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"The chat span wasn't enough" (raw lines 59–68) for `DecisionModel`, the `decide` span nested under `chat` in 2.50.0 and its recorded payload, and the `include_content` behaviour; §"Seeing it in Live view" (lines 70–82) for the Agent Run tab's **Classifier output** panel, the per-level rubric probabilities and **View decision span**. Evidence class: **Reported** — vendor article; no span, trace or Logfire project was opened here.
[^colvin-code-is-graph-2026]: Samuel Colvin, "The code is the graph", Pydantic, published 2026-10-13T09:00Z, 2,445 words as declared; local capture `raw/the-code-is-the-graph/index.md`, content digest sha256:d8803b5f. §"Long live graphs" (raw lines 145–167) for the claim that each sub-agent run and model call is an OpenTelemetry span in the orchestrator's trace, that fan-out, join and retries nest as the code was written, and that agent observability therefore needs no graph visualizer. Evidence class: **Reported** — vendor article; no trace was produced or inspected here.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Responses WebSockets" (raw lines 584–662), the sentence introducing the HTTP-versus-socket record, for `pydantic_ai.transport` being `'websocket'` or `'http'` on each request's `chat` span, its placement on the model activity span under Temporal, and its absence in HTTP-only mode. Evidence class: **Reported** — vendor documentation; no span was opened, exported or inspected here.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. §"How do I see what happened?" (raw lines 240–257) for the OTel-everywhere claim, `uvx logfire-cli wizard --task pydantic-ai`, the write token and free tier, FastAPI and provider-HTTP instrumentation, `Agent.instrument_all()` and the `Instrumentation` capability, `run_id`/`conversation_id` and run metadata on the run span, and `include_content=False`/`include_binary_content=False` with what neither covers. Evidence class: **Reported** — vendor documentation; no wizard, span or HTTP body was inspected.

[^pydantic-logfire-docs]: Pydantic Docs, "Pydantic Logfire Debugging and Monitoring", <https://pydantic.dev/docs/ai/integrations/logfire/>, `domain: pydantic.dev`, `language: en`, 5,651 words as declared and 5,851 by local `wc -w`, 565 lines, no publication date, author, licence or Pydantic AI version; local capture `raw/integrations/logfire/index.md`, content digest sha256:5ea6a3e0. §"Pydantic Logfire" (raw lines 21–31) for the optional built-in support and the no-overhead-and-nothing-sent rule; §"Using Logfire" (lines 33–121) for the interactive and non-interactive wizard forms, `pip install pydantic-ai` versus `pydantic-ai-slim[logfire]`, `logfire-cli auth` and `init`, the `.logfire` directory `logfire.configure()` reads, the two instrumentation calls, and `name=` labelling the run span with its variable-name fallback to `'agent'`; §"Use Logfire for local development, even if production uses something else" (lines 123–137) for `send_to_logfire='if-token-present'`, the deployment with no `.logfire` or `LOGFIRE_TOKEN` sending nothing, the Docker build context warning, the surviving `OTEL_EXPORTER_OTLP_ENDPOINT` export, and the local-two-lines-versus-`Agent.instrument_all()` production split; §"Debugging" (lines 138–145) for realtime sessions being covered by the same call; §"Monitoring HTTP Requests" (lines 152–179) for `instrument_httpx(capture_all=True)`, the `httpx`/`httpx2` provider SDKs with Bedrock on boto3, the `opentelemetry-instrumentation-httpx>=0.65b0` requirement and its silent-failure mode below that; §"Using OpenTelemetry" and §"Logfire with an alternative OTel backend" (lines 181–238) for the endpoint variable, `send_to_logfire=False` and the dual-send note; §"OTel without Logfire" and §"Alternative Observability backends" (lines 239–285) for the raw SDK route and backend swappability; §"Setting OpenTelemetry SDK providers" (lines 436–456) for the global provider default and custom providers through `InstrumentationSettings` or an `Instrumentation` capability; §"Adding Custom Metadata" (lines 559–565) for the `metadata` attribute. Evidence class: **Reported** — vendor documentation; no wizard, CLI, token, span, metric or HTTP body was inspected.

[^pydantic-multi-agent-guide]: Pydantic Docs, "Multi-agent Applications", <https://pydantic.dev/docs/ai/guides/multi-agent-applications/>; local capture `raw/guides/multi-agent-applications/index.md`, content digest sha256:2439e904, 2,082 words as declared (2,144 by `wc -w`), no publication date, author, licence or framework version. §"Observing Multi-Agent Systems" (raw lines 370–402) for `uvx logfire-cli wizard --task pydantic-ai`, the `logfire.configure()`/`instrument_pydantic_ai()` pairs it installs, the six things the trace is read for, the JS/TS and Rust SDKs plus OTel compatibility, and the reasoning-versus-backend isolation claim; §"Agent delegation" (line 76) for `name=` labelling an agent's run span. Evidence class: **Reported** — vendor guide; no wizard was run, no trace opened.
