---
title: "Best Langfuse Alternatives in 2026"
author: "Bill Easton"
site: "Pydantic"
published: 2026-08-26T09:00:00.000Z
source: "https://pydantic.dev/articles/best-langfuse-alternatives"
domain: "pydantic.dev"
language: "en"
description: "Compare Langfuse alternatives in 2026: Pydantic Logfire, LangSmith, Braintrust, Arize Phoenix, Helicone, Laminar, and Confident AI, with licenses and pricing."
word_count: 3070
---

An agent gives a wrong answer at 2am. The Langfuse trace is right there: prompt, model call, tool call, tokens, cost. Nothing in it looks broken. The real cause is a connection-pool timeout in a retrieval service two hops upstream, and that never reached Langfuse, because [Langfuse's OpenTelemetry endpoint currently ingests trace data and not logs or metrics](https://langfuse.com/integrations/native/opentelemetry). So half the story sits in a different tool, under a different ID, and the on-call engineer reassembles it by hand.

The Langfuse core is MIT licensed, it self-hosts with no usage limits, and prompt management, datasets, experiments, and evaluators are all in the product. Teams still leave it, and they leave in predictable directions.

**TL;DR.** [Pydantic Logfire](https://pydantic.dev/logfire) is our pick when the AI feature is part of a larger application and you want model calls, database queries, and queue work in one OpenTelemetry trace you can query with SQL. Choose **Langfuse** if MIT-licensed self-hosting of the whole LLM workflow is the hard requirement. **LangSmith** if the app is built on LangChain or LangGraph. **Braintrust** if a deploy gate keyed to an eval score is the point. **Arize Phoenix** if you want a local-first tracing and evaluation sandbox. **Helicone** if a gateway that logs is the shape you want and maintenance mode is acceptable. **Laminar** if Apache 2.0 self-hosting at a low paid entry matters most. **Confident AI** if your team already writes DeepEval metrics.

*Last updated: August 26, 2026. Prices and license terms were read from each vendor's own pages on that date.*

## Why teams look for a Langfuse alternative

Four reasons come up repeatedly.

- **The billing unit is not the span.** Langfuse [defines a billable unit as a trace, an observation, or a score](https://langfuse.com/docs/administration/billable-units), so evaluations and annotations add to the same meter that tracing does. Improving quality measurement increases the bill in a way that is easy to miss when you size a plan.
- **Traces arrive, logs and metrics do not.** Langfuse's OTLP endpoint currently accepts trace data only, over HTTP/JSON or HTTP/protobuf, [with gRPC not yet supported](https://langfuse.com/integrations/native/opentelemetry). LLM traces therefore live in one system and the rest of production telemetry lives in another.
- **Some governance features need an enterprise key.** All core features are MIT licensed with no usage limits, and [nine features require a `LANGFUSE_EE_LICENSE_KEY`](https://langfuse.com/self-hosting/license-key): project-level RBAC roles, protected prompt labels, data retention policies, audit logs, server-side data masking, UI customization, organization creators, the org management API with SCIM, and the instance management API. Several of those are exactly what a security review asks for.
- **Ownership changed.** [ClickHouse acquired Langfuse in January 2026](https://clickhouse.com/blog/clickhouse-acquires-langfuse-open-source-llm-observability). Both companies committed to keeping the project open source and self-hostable, and the cloud running as-is. That is a real commitment and it is also a new owner, which is enough to make some teams re-run the evaluation.

## What to look for in a replacement

These are our criteria, and they are opinionated.

- **Does your instrumentation survive leaving?** There is a difference between a platform that speaks OpenTelemetry across its whole data model and one that accepts OTLP through an adapter for the LLM slice. The first means your spans are portable. The second means they are portable only for the part the adapter covers.
- **Does the tool see past the model call?** Most LLM observability products assume model calls belong in their own silo, separate from HTTP handlers, database queries, and background jobs. Production failures rarely respect that boundary.
- **What sits on the meter?** Count the meters, then check what each one counts. Requests, spans, units, scores, and processed gigabytes are not interchangeable, and a free tier measured in a favorable unit tells you very little.
- **What does the license actually permit?** "Open source" and "source available" are different things. Elastic License 2.0 and business-source style licenses are not OSI-approved, and an MIT core with a separately licensed enterprise directory is not the same as an MIT product.
- **Can you ask a question nobody predicted?** A filter bar is a ceiling. A query language is not.

## How we compared

We read each vendor's current pricing page and product documentation on the date above, and we opened the license file in each repository. For every product we recorded the free tier with its limits, the first paid tier with its period and included volume, whether OTLP ingest covers traces only or traces along with logs and metrics, and whether self-hosting includes every feature. Every entry gets a lane and a catch, including ours. Where a capability was not clearly documented, we say so.

## The best Langfuse alternatives in 2026

### 1\. Pydantic Logfire: best Langfuse alternative overall

[Logfire](https://pydantic.dev/logfire) treats an LLM call as one span among many. The model call, the tool call, the Postgres query behind the tool, the HTTP request that started it, and the logs emitted along the way land in the same trace, on one meter. It is OpenTelemetry-native for traces, logs, and metrics, so [any language with an OTel SDK can point at the endpoint](https://pydantic.dev/docs/logfire/guides/alternative-clients/) and first-class SDKs cover Python, TypeScript, and Rust. Querying is [PostgreSQL-compatible SQL](https://pydantic.dev/docs/logfire/reference/sql/) over the raw records table, including joins and window functions, and an MCP server exposes the same queries to coding agents. [Evaluations](https://pydantic.dev/docs/logfire/evaluate/evals/) and [managed prompts](https://pydantic.dev/docs/logfire/prompt-management/) with versions, labels, and rollout targeting live in the same product. The free Personal plan carries 10 million records a month and the [Team plan is $49 a month](https://pydantic.dev/pricing) with $2 per additional million records.

Self-hosting is Enterprise only. If your requirement is to run the platform yourself on permissively licensed code, Logfire does not meet it, and Langfuse's MIT core does, with the nine enterprise-key features as the boundary. The LLM-workflow surface is also younger: Langfuse has more years of dataset and experiment tooling behind it. One more thing worth knowing before you size a plan: because the meter counts every record, instrumenting the whole application is exactly what puts volume on it.

Best for teams whose AI feature is one part of a larger service, who want one query surface over all of it, and who accept a hosted-by-default platform in exchange.

### 3\. LangSmith: when the app is built on LangChain or LangGraph

LangSmith is built by the LangChain team, so LangChain and LangGraph applications trace into it without an adapter in between, which matters if your agent is a LangGraph graph. It also accepts standard OTLP traces at `https://api.smith.langchain.com/otel`, so non-LangChain services can report into the same project.

Pricing combines seats and traces: the [Plus plan is $39 per seat per month with 10,000 base traces included](https://www.langchain.com/pricing-langsmith), and the free Developer tier is capped at one seat and 5,000 base traces a month. Retention is tiered: 14 days for base traces, 400 days for extended traces, which carry their own charge. The product is closed source and self-hosting is Enterprise only.

Pick it when the team is already committed to LangChain or LangGraph and accepts per-seat plus per-trace pricing for the first-party integration.

### 4\. Braintrust: when a deploy gate keyed to an eval score is the point

Braintrust puts the evaluation loop first: datasets, scorers, experiments, prompt management with runtime `invoke()` and version pinning, and CI gates that block a deploy when a score regresses. It [ingests OTLP traces](https://www.braintrust.dev/docs/integrations/sdk-integrations/opentelemetry) and maps GenAI semantic-convention attributes into structured inputs, outputs, and token metrics.

The bill has several independent meters. [Pro is $249 a month](https://www.braintrust.dev/pricing) and includes $249 of model credits, 5 GB of processed data with $3 per GB after, 50,000 scores with $1.50 per 1,000 after, and 30-day retention with $0.50 per GB per month beyond it. The free Starter tier holds 1 GB, 10,000 scores, and 14 days. It is proprietary, and on-premises deployment is Enterprise only.

Right for teams whose bottleneck is regression testing rather than production debugging, and who can budget across four meters.

### 5\. Arize Phoenix: for a local-first tracing and evaluation sandbox

Phoenix runs on a laptop or a container and covers tracing, prompt management with versioning, a playground for comparing prompt variants, datasets, and experiments. It is OpenTelemetry-based and uses the OpenInference conventions, which makes it easy to point existing OTel instrumentation at it.

Phoenix is licensed under the [Elastic License 2.0](https://github.com/Arize-ai/phoenix/blob/main/LICENSE), which is source available and not OSI-approved, so calling it open source is inaccurate and a legal review may treat it differently from MIT or Apache 2.0. Arize AX is the commercial layer above Phoenix, where the [free tier is 25,000 spans a month with 15-day retention and Pro is $50 a month](https://phoenix.arize.com/pricing/) for 50,000 spans and 10 GB with 30-day retention. Ownership is also in motion: [Dynatrace agreed to acquire Arize on August 13, 2026](https://www.dynatrace.com/news/press-release/dynatrace-to-acquire-arize/), with closing expected subject to regulatory review.

It fits individual engineers and research teams who want tracing and evals running locally in minutes, and whose legal review accepts a source-available license.

### 6\. Helicone: for gateway-shaped logging, with maintenance mode priced in

Helicone sits in front of the model provider as an OpenAI-compatible gateway, so a base-URL change starts producing logs, with caching, fallbacks, and multi-provider routing in the same layer. There is an async path that keeps it out of the request path, an OpenLLMetry integration that bypasses the proxy entirely, prompt versioning with experiments, and LLM-judge and custom evaluators. It is [Apache 2.0](https://github.com/Helicone/helicone/blob/main/LICENSE) and self-hosts via Docker Compose or Helm. The free Hobby tier covers [10,000 requests a month on one seat, and Pro is $79 a month](https://www.helicone.ai/pricing).

Helicone was acquired by Mintlify and, in the company's own words, its services "will remain live for the foreseeable future in maintenance mode," meaning [security updates, new models, and bug fixes keep shipping](https://www.helicone.ai/blog/joining-mintlify) as of the March 3, 2026 announcement. New feature work is not part of that commitment, and the announcement names no sunset date in either direction.

Choose it if gateway-shaped logging on permissive code is the requirement and maintenance mode is priced in.

### 7\. Laminar: if Apache 2.0 self-hosting at a low paid entry matters most

Laminar is [Apache 2.0](https://github.com/lmnr-ai/lmnr) end to end and self-hosts from a `docker compose up`, with a fuller compose file for production. It accepts OTLP over gRPC and HTTP, and the documented feature set covers tracing, evals against datasets locally or in CI, labeling, a playground that replays a traced span with a different prompt or model, and raw SQL from the UI, CLI, or MCP. Paid entry is low: [Starter is $30 a month for 3 GB with $2 per GB after](https://laminar.sh/pricing) and 30-day retention, against a free tier of 1 GB with 7-day retention on one seat and one project.

Coverage is narrower than the older platforms here. Laminar's [documentation](https://laminar.sh/docs/tracing/otel) centers on tracing, and we could not confirm from it, in August 2026, either full log ingestion alongside traces or a versioned prompt registry of the kind Langfuse and LangSmith document. Both are worth checking against the current docs before you build a workflow on them. It is also a far smaller project than Langfuse, roughly 3,200 GitHub stars against roughly 34,000 in August 2026, which is a real consideration when the plan is to self-host it.

For teams that want permissive licensing and a cheap first paid tier, and that can accept a narrower and younger feature surface.

### 8\. Confident AI (DeepEval): where the eval suite is already DeepEval

[DeepEval](https://github.com/confident-ai/deepeval) is an Apache 2.0 metrics library with roughly 17,900 GitHub stars in August 2026, and Confident AI is the hosted platform around it: tracing, online evaluation that runs DeepEval metrics on spans as they arrive, annotation queues, prompt versioning, and CI regression testing. It [accepts OTLP over HTTP](https://www.confident-ai.com/docs/integrations/opentelemetry) at a dedicated endpoint, so instrumentation is not locked to the DeepEval SDK.

The step from free to paid is steep. The [free tier is one project, two seats, five test runs a week, and 1 GB-month of trace spans, with additional spans dropped rather than billed; Starter is $200 a month](https://www.confident-ai.com/pricing) for five projects and 5 GB-months, and Team is $2,000 a month. The library is Apache 2.0 but the platform is proprietary, and on-premises deployment is Enterprise only.

Suited to teams whose evaluation suite is already written in DeepEval, at a budget that clears the $200 tier.

## Comparison at a glance

| Tool | License | Self-host | OTLP ingest | Evals | Prompt management | Free tier | Paid entry | Billing unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pydantic Logfire | Proprietary platform, MIT SDKs | Enterprise plan only | Traces, logs, and metrics | Yes, hosted judges and Pydantic Evals | Yes, versions, labels, rollout | 10M records/month, 30-day retention | [$49/month Team](https://pydantic.dev/pricing) | Records: spans, logs, metrics |
| Langfuse | MIT core; `ee/` directories under a separate license | Yes, core with no usage limits; 9 features need an EE key | Traces only, HTTP/JSON or protobuf | Yes, LLM-as-a-judge and custom | Yes | Hobby: 50k units/month, 30-day data access | [$29/month Core](https://langfuse.com/pricing) | Units: traces + observations + scores |
| LangSmith | Proprietary | Enterprise plan only | Traces | Yes | Yes | 5k base traces/month, 1 seat | [$39/seat/month Plus](https://www.langchain.com/pricing-langsmith) | Seats plus base and extended traces |
| Braintrust | Proprietary | Enterprise plan only | Traces, GenAI conventions mapped | Yes, scorers and CI gates | Yes, runtime invoke and pinning | 1 GB data and 10k scores/month, 14-day retention | [$249/month Pro](https://www.braintrust.dev/pricing) | Processed data GB, scores, model credits, retention |
| Arize Phoenix | Elastic License 2.0, source available, not OSI-approved | Yes, Phoenix runs locally or self-hosted | Traces, OpenInference conventions | Yes | Yes, versioning and playground | Phoenix free; Arize AX free 25k spans/month | [Arize AX $50/month Pro](https://phoenix.arize.com/pricing/) | Spans and GB ingested on AX |
| Helicone | Apache 2.0 | Yes, Docker Compose or Helm | OpenLLMetry async logger; no general OTLP endpoint | Yes, LLM judge and custom | Yes, versioning and experiments | 10k requests/month, 1 seat | [$79/month Pro](https://www.helicone.ai/pricing) | Requests plus storage |
| Laminar | Apache 2.0 | Yes, `docker compose` | Traces, gRPC and HTTP | Yes, local or CI against datasets | Not confirmed in the docs, Aug 2026 | 1 GB, 7-day retention, 1 seat | [$30/month Starter](https://laminar.sh/pricing) | Data GB plus Signals tokens |
| Confident AI (DeepEval) | Platform proprietary; DeepEval Apache 2.0 | Enterprise on-premises only | Traces, OTLP over HTTP | Yes, online and CI | Yes, versioning | 1 project, 5 test runs/week, 1 GB-month | [$200/month Starter](https://www.confident-ai.com/pricing) | GB-months of trace spans |

## How to choose

- Your AI code is one service inside a larger application, and the failures cross that boundary: **Pydantic Logfire**.
- Your legal review requires an OSI-approved license end to end: **Laminar** or **Helicone**, both Apache 2.0. Langfuse's core is MIT and self-hosts without usage limits, but the separately licensed `ee/` directories mean it does not pass an end-to-end test.
- Your telemetry must stay on your infrastructure and there is budget for a supported deployment: **Pydantic Logfire** Enterprise self-hosts the full platform; **Arize Phoenix** self-hosts free where the Elastic License 2.0 works for you.
- You are on LangChain or LangGraph and the framework fit outweighs per-seat pricing: **LangSmith**.
- Your release process should fail when an eval score drops: **Braintrust**.
- You want tracing and evals running on a laptop this afternoon: **Arize Phoenix**.
- You want a proxy that logs, caches, and fails over, and you accept maintenance mode: **Helicone**.
- Your evaluation suite is already DeepEval: **Confident AI**.
- You want to write SQL against raw telemetry instead of learning a filter syntax: **Pydantic Logfire** or **Laminar**.

## When Langfuse is still the right call

Three situations still favor staying put.

The first is licensing. Langfuse's core is MIT and self-hosts with no usage limits and no scalability difference from the cloud. Logfire self-hosting is Enterprise only. If "we run it, on code we can fork" is a requirement rather than a preference, Langfuse's MIT core meets it, with the enterprise-key features as the boundary, and Logfire's Enterprise-only self-hosting does not.

The second is sunk workflow. Prompt versions, datasets, experiment history, and annotation queues represent real work, and none of it moves with a DSN change. Migrating is worth it when the thing you cannot do today is costing you more than the rewrite.

The third is data residency. Langfuse publishes [EU, US, Japan, and HIPAA cloud regions](https://langfuse.com/security) alongside self-hosting, which is a shorter path than a custom agreement when a specific jurisdiction is contractual.

## Frequently asked questions

**Is Langfuse open source?** The core is, under MIT. The repository's license file carves out the `ee/`, `web/src/ee/`, and `worker/src/ee/` directories, which are governed by a separate commercial license, and nine features require an enterprise license key at runtime. "MIT core with a commercially licensed enterprise edition" is the accurate description.

**What is the cheapest Langfuse alternative?** Self-hosting Laminar or Helicone on your own hardware, both Apache 2.0, costs only the infrastructure. Among hosted plans, Langfuse Core at $29 a month and Laminar Starter at $30 a month are the lowest paid entries here. Pydantic Logfire's free Personal plan carries 10 million records a month and hard-caps rather than billing past it, though the free tiers in this comparison are measured in different units and do not convert cleanly.

**Which alternatives can I self-host with every feature?** Laminar and Helicone publish self-hosting under Apache 2.0. Langfuse self-hosts its MIT core with no usage limits, with nine features gated behind an enterprise key. Arize Phoenix self-hosts under the Elastic License 2.0, which is not OSI-approved. LangSmith, Braintrust, Confident AI, and Pydantic Logfire offer self-hosting or on-premises deployment on their enterprise tiers.

**Does switching mean re-instrumenting everything?** Not if both ends speak OpenTelemetry. Langfuse, LangSmith, Braintrust, Arize Phoenix, Laminar, Confident AI, and Pydantic Logfire all publish an OTLP trace endpoint, so a standard OTel SDK can be redirected with an endpoint and a header, and Helicone documents an OpenLLMetry path that bypasses its proxy. What does not move automatically is anything vendor-specific: prompt registries, dataset definitions, and scorer implementations.

**Can Pydantic Logfire replace Langfuse?** For teams that want LLM telemetry connected to the application around it, on one meter and one query language, yes. For teams that want to run the whole platform themselves on MIT-licensed code, no, and the [Logfire vs Langfuse comparison](https://pydantic.dev/logfire/vs-langfuse) sets out both sides in detail.

**Does full-stack observability mean a bigger bill?** It means more records, so it depends on the meter. On Logfire the same record price covers a database span and an LLM span, and the 10 million included records apply to both, so the question is total volume rather than which product it came from. On per-signal products, adding application telemetry usually means adding a second vendor.

## Try Pydantic Logfire free

The free Personal plan includes 10 million records a month: LLM calls, HTTP requests, database queries, logs, and metrics on one meter, queryable with PostgreSQL-compatible SQL. [Get started](https://pydantic.dev/signup), or read the [Logfire vs Langfuse comparison](https://pydantic.dev/logfire/vs-langfuse) first.
