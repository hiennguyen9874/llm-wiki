---
type: Concept
title: OpenTelemetry backend selection
description: What still differs once every backend accepts OTLP — cross-signal querying, the query ceiling, high-cardinality tolerance, the meter, GenAI awareness, self-hosting and breadth — plus the eight 2026 backends and the pick-by-constraint rules.
tags: [ml, agents, observability, vendors]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:22:42Z }
stale_after: 2027-02-26
sources:
  - id: pydantic-otel-backends-2026
    resource: ../raw/best-opentelemetry-backends/index.md
    scope: ../raw/best-opentelemetry-backends/
    kind: article
    revision: sha256:178352f2db9f69b041aafd799a2586d816302366db1240c9526baf098328757d
    title: "Best OpenTelemetry Backends in 2026"
---

OpenTelemetry makes the backend a configuration value — an OTLP endpoint and a token for a single-store service, or a collector pipeline per signal for the multi-store stacks — so the decision is reversible at the wire while dashboards, alerts, saved queries and team habit migrate slowly[^pydantic-otel-backends-2026] Because every candidate accepts standard OTLP, the comparison has to move up one level to what each backend does with telemetry after it lands, and the source reduces that to seven axes: cross-signal querying, the query ceiling, high-cardinality tolerance, what the meter counts, GenAI awareness, self-hosting and residency, and breadth beyond application telemetry[^pydantic-otel-backends-2026] The article is written by Pydantic and ranks its own Pydantic Logfire first, so the axes and the published facts are the reusable part and the ranking is a vendor claim[^pydantic-otel-backends-2026] This page covers OTLP-native backends for application telemetry; the LLM-observability and eval products that compete on a narrower agent-shaped surface are compared in [LLM observability platform comparison](llm-observability-platform-comparison.md), which the author explicitly excludes from scope[^pydantic-otel-backends-2026]

## The seven axes that survive OTLP parity

| Axis | The question it asks | What a weak answer costs |
| --- | --- | --- |
| Cross-signal querying | Can one query span traces, logs and metrics, or is correlation done in the dashboard layer across separate stores and languages? | "What did the requests behind these slow spans log?" becomes a tab-switching exercise |
| The query ceiling | Is the surface a filter bar with fixed aggregates, or SQL-class querying? | The filter bar is a ceiling you discover during your worst incident |
| High-cardinality tolerance | Can user IDs, tenant IDs and prompt hashes be grouped by cheaply? | Metrics-first designs punish exactly the attributes you want to slice on |
| The meter | Per record, per host, per span, per seat, or several meters at once? | An unpredictable bill, and pressure to stop collecting something |
| GenAI awareness | Does an LLM span render as a first-class conversation, and is it correlated with the surrounding trace? | Agent runs arrive as a blob of attributes in a separate view |
| Self-hosting and residency | Can telemetry stay on your infrastructure, and at which tier? | The field narrows fast once residency is a hard requirement |
| Breadth beyond app telemetry | RUM, synthetic monitors, continuous profiling? | Wanting all of it in one contract pulls toward the enterprise APMs |

The first four are ordinary APM procurement questions re-asked against OTLP data; the last three are where an agent workload changes the answer[^pydantic-otel-backends-2026]

## GenAI awareness is the least settled axis

OpenTelemetry's semantic conventions for generative AI cover model names, token counts and tool calls, but they are young: they recently moved to a dedicated repository, attribute names are still shifting, and instrumentation typically makes prompt and response content capture opt-in because it carries user data[^pydantic-otel-backends-2026] The practical consequence is that backends differ less on whether they claim GenAI support — token dashboards, cost tracking and agent views are now common — than on three tests: whether an agent run renders as a conversation with tool calls or as a list of raw spans, whether LLM telemetry is correlated with the surrounding application trace or lives in its own view, and what can still be asked after the fact[^pydantic-otel-backends-2026] On those tests the author's answer is Logfire, because supported instrumentation renders conversations and the surrounding trace is one SQL join away[^pydantic-otel-backends-2026]

## The backends at a glance

| Backend | Meter | Cross-signal querying | Query surface | Self-host |
| --- | --- | --- | --- | --- |
| Pydantic Logfire | One per-record meter | One SQL surface | PostgreSQL-compatible SQL | Enterprise only |
| Grafana stack (Tempo, Loki, Mimir) | Usage-based cloud or free OSS | Dashboard-layer correlation | TraceQL + LogQL + PromQL | Yes |
| SigNoz | Usage-based cloud or OSS | One app, per-signal tables | Builder + ClickHouse SQL | Yes |
| Jaeger | Free OSS | Traces (+ span metrics) | UI filters + PromQL | Yes |
| Honeycomb | Per event + metric points | Events (+ metrics) | Proprietary query UI | Private Cloud (AWS) |
| Dash0 | Per unit, published rates | One store | PromQL + SQL | No |
| OpenObserve | OSS (AGPL) or cloud | One store | SQL-like + UI | Yes |
| Datadog / New Relic / Dynatrace | Per host, GB, or user (varies) | Cross-product views | Proprietary per product | No (except Dynatrace Managed) |

The article states that rates and capabilities were last verified in August 2026 and that meters change, so the linked pricing pages are the authority[^pydantic-otel-backends-2026]

## What each entry is actually good for

- **Pydantic Logfire** — traces, logs and metrics in one store on one per-record meter; the free plan includes 10 million records a month, with Team and Growth billing overage at a single per-record rate; querying is PostgreSQL-compatible SQL with joins, subqueries and window functions, so a slow trace joins to the log lines inside it in one statement; Pydantic AI, OpenAI and Anthropic SDK instrumentation is maintained in-house; self-hosting exists only on Enterprise, and Personal, Team and Growth are managed-only[^pydantic-otel-backends-2026]
- **Grafana (Tempo, Loki, Mimir)** — the path of least resistance when dashboards already live in Grafana; all components are open source and OTLP-capable, Grafana Cloud adds a free tier and GenAI dashboards, and the structural cost is three stores and three query languages with correlation pushed into the dashboard layer[^pydantic-otel-backends-2026]
- **SigNoz** — one self-hosted ClickHouse-backed app for traces, logs and metrics with APM views, dashboards and alerting included, LLM observability documented over the GenAI conventions, an open-source core with commercial features on top, and ClickHouse plus the ingestion pipeline as your operational burden[^pydantic-otel-backends-2026]
- **Honeycomb** — traces and logs treated as wide events for group-by-any-attribute investigation, OTLP on all three signals, events, metric data points and telemetry processing metered separately, and a proprietary query model that makes the saved questions Honeycomb-shaped[^pydantic-otel-backends-2026]
- **Dash0** — the narrow case is PromQL over OTel data in a managed backend with published per-unit rates; there is no self-hosted edition listed, and as the youngest product its workflow depth is the thing to evaluate before standardising[^pydantic-otel-backends-2026]
- **OpenObserve** — a single-binary Rust backend with object-storage persistence, the fit for self-hosting without operating a ClickHouse cluster, licensed AGPL-3.0 since a 2023 relicence from Apache 2.0 with a commercial edition on top, and with younger investigation workflows[^pydantic-otel-backends-2026]
- **Datadog, New Relic, Dynatrace** — all ingest OTLP alongside proprietary agents and cover the breadth focused backends skip; two checks before defaulting: OTel-ingested data does not always reach feature parity with agent-collected data (Datadog's OTLP metrics intake expects delta temporality while most SDKs default to cumulative), and per-host, per-GB and per-user pricing with per-feature SKUs is the spreadsheet single-meter backends exist to avoid[^pydantic-otel-backends-2026]
- **Jaeger** appears in the comparison table as free OSS with traces plus span metrics, UI filters plus PromQL, and self-hosting, and in the decision list as the option when traces alone are enough — the article gives it no section of its own[^pydantic-otel-backends-2026]

Named as worth evaluating but outside the article's scope: Elastic's OpenTelemetry distribution, ClickHouse ClickStack (HyperDX), and Uptrace[^pydantic-otel-backends-2026]

## Choosing by constraint

- **Default** — Logfire, on one store, one meter, SQL across traces, logs, metrics and LLM spans, and a free tier large enough to prove it on a real workload[^pydantic-otel-backends-2026]
- **Dashboards already in Grafana, and three query languages can be staffed** — Tempo/Loki/Mimir[^pydantic-otel-backends-2026]
- **Self-hosting is a hard requirement** — Logfire Enterprise keeps the same product on your infrastructure; going open source instead means SigNoz if you will operate ClickHouse, OpenObserve for the smallest footprint where AGPL fits, or Jaeger with Prometheus if traces alone are enough[^pydantic-otel-backends-2026]
- **The team already debugs in the wide-events style and accepts a proprietary query model** — Honeycomb[^pydantic-otel-backends-2026]
- **PromQL in a managed backend is the requirement** — Dash0[^pydantic-otel-backends-2026]
- **The enterprise-APM contract already exists** — send OTLP into it and verify feature parity before renewing[^pydantic-otel-backends-2026]

"Open source" is explicitly not one answer across that list: Jaeger and the Grafana OSS components are permissively licensed, SigNoz is open source at the core with commercial enterprise features, and OpenObserve is AGPL-3.0 with a commercial edition — and the trade is a bill against operations work either way[^pydantic-otel-backends-2026]

## Reversible at the wire, expensive in the workflow

Switching backends repoints the OTLP exporter endpoint and token, or edits the collector pipeline for a multi-store stack where each signal can need its own endpoint and credentials; what gets rebuilt is backend-side configuration — dashboards, alerts, saved queries, and any sampling or temporality settings the new backend expects[^pydantic-otel-backends-2026] The author's conclusion is that the worst outcome is not choosing the "wrong" backend but delaying instrumentation while comparing them, since the instrumentation is the asset and the backend is the part that can be renegotiated[^pydantic-otel-backends-2026]

## Limits

- The source is Pydantic's own comparison (author Bill Easton, published 2026-08-26) and ranks Pydantic Logfire first; the axes, the meters and the constraint list all serve that ranking, and the Logfire entry is written in the first person[^pydantic-otel-backends-2026]
- No backend was installed, no OTLP exporter pointed anywhere and no pricing page fetched in this ingest; every rate is the article's August 2026 statement carried once, and its own text tells the reader to re-check the linked pages[^pydantic-otel-backends-2026]
- Jaeger has a table row and appears in the decision list but gets no section, so its facts here come from the table alone; Elastic, ClickStack and Uptrace are named without evaluation (**Synthesis** from the source's own structure)[^pydantic-otel-backends-2026]
- The claim that instrumentation typically makes prompt and response capture opt-in is stated generally for instrumentations; no instrumentation was inspected to confirm it[^pydantic-otel-backends-2026]
- The article's scope excludes AI-specific evaluation platforms by its own statement, so this page is about storage and querying, not about scoring[^pydantic-otel-backends-2026]
- Coverage: the capture is a single `index.md` with no attachments, includes or manifests; the closing "Try Pydantic Logfire free" block was excluded as promotion except the free-tier figure, which the body already carries, and the external links were read as links and not followed[^pydantic-otel-backends-2026]
- Evidence class: **Reported**.

## Relationships

- **Depends on** [agent observability requirements](agent-observability-requirements.md) for the failure model that makes cross-signal correlation and wide-event querying necessary rather than nice to have.
- **Is the application-telemetry counterpart of** [LLM observability platform comparison](llm-observability-platform-comparison.md), which compares the narrower LLM-observability products on licence, OTLP scope and billable unit.
- **Frames the backend choice under** [Pydantic AI observability](pydantic-ai-observability.md), where Logfire is one OTLP destination among the ones compared here.
- **Supplies the independence criterion used by** [agent optimization platforms](agent-optimization-platforms.md): OpenTelemetry-native ingest is what keeps the diagnostic loop portable across an acquisition.
- **Costs and limits the delivery path described in** [Logfire agent optimization](logfire-agent-optimization.md), since one per-record meter prices the traces that optimizer reads.

[^pydantic-otel-backends-2026]: Bill Easton, "Best OpenTelemetry Backends in 2026", Pydantic, published 2026-08-26, 1,861 words as declared; local capture `raw/best-opentelemetry-backends/index.md`, content digest sha256:178352f2. §"Opening and scope" (lines 13–15) for OTLP reversibility at the wire versus workflow migration and the exclusion of AI-specific eval platforms; §"What actually differs between OTLP backends" (lines 17–27) for the seven axes, the GenAI semantic-convention maturity note, the opt-in content capture, the Enterprise-only Logfire self-hosting and the breadth argument; §"The best OpenTelemetry backends in 2026" (lines 29–61) for the Logfire, Grafana, SigNoz, Honeycomb, Dash0, OpenObserve and enterprise-APM entries with their prices, licences, self-hosting options and query surfaces, plus the Elastic, ClickStack and Uptrace aside; §"Comparison at a glance" (lines 63–76) for the eight-row table and the August 2026 verification note; §"How to choose" (lines 78–85) for the constraint list and the licence distinctions; §"When the backend choice matters less than you think" (lines 87–89) for the instrument-now argument; §"Frequently asked questions" (lines 91–99) for the backend definition, the switching procedure with its sampling and temporality caveats, the three GenAI separating tests, and the licence-per-backend answer. Evidence class: **Reported** — a vendor comparison article; nothing was fetched, installed or measured.
