---
title: "Best LLM Evaluation Tools 2026"
author: "Bill Easton"
site: "Pydantic"
published: 2026-08-26T09:00:00.000Z
source: "https://pydantic.dev/articles/best-llm-evaluation-tools"
domain: "pydantic.dev"
language: "en"
description: "Compare seven LLM evaluation tools in 2026: Pydantic Logfire, Braintrust, Langfuse, LangSmith, Arize Phoenix, Confident AI, and Galileo, priced and licensed."
word_count: 3349
---

*By Bill Easton. Evaluation workflows updated September 12, 2026; pricing and licenses checked August 26, 2026.*

Picking a metric is the easy part of evaluating an LLM application. The hard part is knowing where the number came from, whether you can reach the run that produced it, and what it costs to keep producing numbers every day.

**TL;DR.** Pydantic [Logfire](https://pydantic.dev/logfire) combines a shared evaluation workspace with production tracing. Curate a hosted dataset or keep cases in code, compare a changed prompt or model against a baseline, and inspect the outputs and traces behind regressions. Scores use the same record allowance as the rest of your telemetry, with no separate score fee. The comparisons below cover alternatives for teams with existing framework, SDK, or deployment requirements.

Every price and license below was checked against the vendor's own pricing page or documentation on August 26, 2026, and each carries the plan and period it applies to. That matters here: the same workload can cost nothing or a few thousand dollars a month depending on which meter it trips.

## Why teams look for a dedicated evaluation tool

- **A test suite has no score.** `pytest` returns pass or fail. Most interesting questions about model output are graded: is this summary faithful to the source, did the agent pick the right tool, is the refusal appropriate. Some of those are assertions, and some need a scoring model.
- **Regressions arrive without a deploy.** A provider ships a new model snapshot, a retrieval index refreshes, users change how they phrase things. Nothing in the repository changed and the quality did anyway.
- **A score with no trace behind it is a dead end.** "Faithfulness dropped to 0.71" is a starting point, not a finding. Fixing it means reading the prompt, the retrieved chunks, and the tool calls from the specific run that scored 0.71.
- **Evaluation has a bill of its own.** Some vendors meter scores individually, some meter traces plus observations plus scores, and some meter gigabyte-months of span storage. Running more evaluations is the entire point of the tool, and on several of these platforms it is also the fastest way to raise the invoice.

## Offline evals, online evals, and LLM-as-a-judge are not three tools

Most comparison pages in this category treat these as three product features to tick off. They are not. Two of them are places you run an evaluation, and the third is a way to compute a score.

**Offline evals** run a fixed dataset through your system deliberately. A dataset is a reusable collection of cases, each with an input, an optional expected output, and metadata. One run of the system over that dataset is an experiment, and you compare experiments to each other to find out whether a change helped. Our [datasets and experiments guide](https://pydantic.dev/docs/logfire/evaluate/datasets-and-experiments/) describes the model in more detail.

**Online evals** attach evaluators to real production traffic, usually sampled, and score requests nobody curated. The question is different: not "did this change improve my test set" but "is the thing users actually send still working". We covered the workflow in [online evals in Pydantic Logfire](https://pydantic.dev/articles/online-evals-pydantic-logfire).

**LLM-as-a-judge** is a scoring method, and it works in either mode. Its alternatives are deterministic checks (the JSON validates, the citation is present, latency is under a bound) and human labels. Combining all three is a workflow choice rather than a purchasing one, and [our walkthrough of Airbnb's three-layer approach](https://pydantic.dev/articles/three-layer-evals-logfire) shows what that looks like in code.

Here is the useful part. The columns that comparison pages fill with check marks no longer separate these products; the glance table records how each tool approaches the three modes, with vendor documentation linked from the entries. What separates them is where the score lands, what unit it is billed in, and how far you are from the trace that produced it.

## How we compared

Five criteria, roughly in the order they start to matter after the first month:

- **Where the score lands.** Is an eval result a first-class record sitting next to the trace that produced it, or an object in a separate evaluation database?
- **What the billing unit is.** Scores, traces, units, gigabyte-months, and seats are not interchangeable. The unit a vendor picks tells you which of your habits gets expensive.
- **The license, precisely.** MIT and Apache 2.0 are open-source licenses. The Elastic License 2.0 is source-available: you can read and run the code, and you may not offer it to third parties as a managed service. If self-hosting is part of the plan, that difference decides things.
- **Instrumentation portability.** All seven accept OpenTelemetry over OTLP, so tracing survives a vendor change. Eval results are the part that does not always travel: when scores are a proprietary object type, they stay behind.
- **Whether it does anything outside evals.** Some of these are evaluation products. Some are observability platforms with evaluation inside them. Both are defensible, and buying the wrong one is expensive.

Every claim below links to a primary source, so you can check it yourself.

## The best LLM evaluation tools in 2026

### 1\. Pydantic Logfire: best LLM evaluation tool overall

[Pydantic Logfire](https://pydantic.dev/logfire/evals) gives your team a shared place to build datasets and review experiments. [Manage cases in the web UI or keep them in code](https://pydantic.dev/docs/logfire/evaluate/manage-datasets/), alongside the application they test. A hosted case can come from a production trace and retain its source link. [Compare a candidate with a baseline](https://pydantic.dev/docs/logfire/evaluate/review-experiments/#compare-a-candidate-with-a-baseline) to find regressed cases, read their outputs and recorded evaluator reasons, and inspect the model and tool calls behind them.

Run tasks and evaluators in your application or eval suite with [Pydantic Evals for Python](https://pydantic.dev/docs/ai/evals/evals/) or the [TypeScript SDK](https://pydantic.dev/docs/logfire/typescript-sdk/evals/). Configure Logfire to send the results to the shared workspace; evaluations can also run entirely locally. [Live evals](https://pydantic.dev/docs/logfire/evaluate/live-evals/) score sampled production traffic. Evaluation records and traces share the same store and are queryable with PostgreSQL-compatible SQL.

There is no separate score fee: evaluation records count toward the [Personal plan's 10 million monthly records](https://pydantic.dev/pricing). Team starts at $49 a month with the same allowance, then $2 per million additional records. Model and judge inference costs are separate. Personal and Team retain data for 30 days; Growth starts at $249 a month with up to 90-day retention. The [SDK exports to any OTLP backend](https://pydantic.dev/docs/logfire/how-to-guides/alternative-backends/), and Enterprise supports self-hosting.

Best for teams comparing agent, prompt, and model changes who want to review the failing cases and their execution traces in the same workspace.

#### Turn a production failure into a regression test

Suppose a support agent uses the wrong refund policy. Keep that request as a test case, with the correct policy recorded as the expected behavior. In Logfire:

1. Preserve the relevant span as a [hosted dataset case](https://pydantic.dev/docs/logfire/evaluate/manage-datasets/#add-a-case-from-a-production-trace), linked to the original trace.
2. Review the input and record the correct policy as the expected behavior. Remove sensitive data the test doesn't need, and include successful cases to check for regressions.
3. Run a baseline, then test a changed prompt, model, or application implementation on the same cases with the same evaluators. Your application or eval suite executes the runs; the [code guide](https://pydantic.dev/docs/logfire/evaluate/evals-in-code/) covers setup.
4. [Compare the results](https://pydantic.dev/docs/logfire/evaluate/review-experiments/#compare-a-candidate-with-a-baseline) case by case. Read changed outputs and recorded evaluator reasons, then inspect their traces. Check recorded duration, tokens, and cost alongside quality before keeping the change.

Your team defines the expected behavior. Logfire keeps the original failure, evaluation results, and candidate traces available for review, so an improved average doesn't hide a newly broken case.

### 2\. Braintrust: for teams already using its evaluation workflows

Braintrust is organized around the eval loop: experiments, a hosted playground for prompt iteration, human review, and side-by-side comparison. It accepts OpenTelemetry at [`https://api.braintrust.dev/otel`](https://www.braintrust.dev/docs/integrations/sdk-integrations/opentelemetry) with an EU data plane available, and the free Starter plan includes [10,000 scores, 1 GB of processed data, and 14-day retention at $0 a month](https://www.braintrust.dev/pricing).

The score itself is the meter. Braintrust's billing FAQ defines a score as the result of ["offline or online evaluations"](https://www.braintrust.dev/docs/admin/billing/faq#what-are-scores) and counts each one, so the number that rises is the number the product exists to produce. Past the allowance that is $2.50 per thousand scores on Starter and $1.50 per thousand on Pro, which is $249 a month with 50,000 scores and 5 GB included. Its OTLP ingest also requires a root span: the docs note that traces made only of child spans do not appear in the logs table. Self-hosting is Enterprise. We worked the score arithmetic through on a nightly benchmark in [focus on evals with Logfire](https://pydantic.dev/articles/focus-on-evals-with-logfire), and covered the [migration path](https://pydantic.dev/articles/switching-from-braintrust) for teams that arithmetic convinces.

An existing investment in Braintrust datasets, scorers, and experiment history is a reason to stay. For a new project, compare the per-score bill with Logfire's record-based pricing at your expected evaluation volume.

### 4\. LangSmith: if the application is already LangChain or LangGraph

LangSmith comes from the team behind LangChain and LangGraph, so tracing those frameworks needs no extra instrumentation. Datasets and experiments cover the offline side, and [online evaluations](https://docs.langchain.com/langsmith/online-evaluations) run LLM-as-a-judge evaluators against a configurable sample of production runs, so judge cost tracks the sample rate. The Developer plan is [free, capped at a maximum of one seat, with 5,000 base traces a month](https://www.langchain.com/pricing-langsmith).

The bill has two axes. Plus is $39 per seat a month with 10,000 base traces included, then pay-as-you-go priced in LangChain Storage Units at $1.00 per unit, and base traces retain for 14 days unless you pay to upgrade them to 400-day extended traces. The OTLP path has a documented failure mode: [a span whose parent is never sent to LangSmith is dropped](https://docs.langchain.com/langsmith/trace-with-opentelemetry), silently, which is a real risk for teams fanning telemetry out to more than one backend. Self-hosted and hybrid deployments are Enterprise only.

Right for teams standardized on LangChain or LangGraph, where the framework integration is worth the per-seat pricing and the 14-day default retention.

### 5\. Arize Phoenix: for a free local-first evaluation app

Phoenix runs on a laptop, in Docker, or on Kubernetes, and Arize documents self-hosting as free with [no license fees, no usage limits, and no feature gates](https://arize.com/docs/phoenix/self-hosting). It ingests OTLP using OpenInference semantic conventions, groups traces into datasets so you can rerun them against a new version, and scores traces and spans with LLM evaluators, code-based checks, or human labels.

Phoenix is source-available rather than open source. The repository ships under the [Elastic License 2.0](https://github.com/Arize-ai/phoenix/blob/main/LICENSE), which specifically prohibits providing the software to third parties as a hosted or managed service. Anyone planning to embed it in their own product should read that clause first. The hosted route is Arize AX, metered in spans: [AX Free is 25,000 spans a month with 15-day retention, and AX Pro is $50 a month with 50,000 spans and 10 GB](https://arize.com/pricing). Those allowances go quickly against production agent traffic.

It fits teams that want an evaluation UI on their own hardware today, and that check licenses before standardizing on anything.

### 6\. Confident AI (DeepEval): where DeepEval's metric catalog is the draw

[DeepEval](https://deepeval.com/docs/evaluation-introduction) is [Apache 2.0](https://github.com/confident-ai/deepeval/blob/main/LICENSE.md) and ships [50+ ready-to-use evaluation metrics](https://deepeval.com/docs/metrics-introduction), most of them LLM-graded, using G-Eval, DAG, and QAG techniques, in Python and TypeScript. Confident AI is the hosted platform on top: it accepts [OTLP over HTTP](https://www.confident-ai.com/docs/integrations/opentelemetry) and runs metric collections against ingested traces and spans, which is online evaluation without writing the scoring path yourself.

The free plan is shaped like a trial rather than a working tier: [2 seats, 1 project, 5 test runs a week, and 1 GB-month of trace spans, after which spans are dropped](https://www.confident-ai.com/pricing). The next step up is Starter at $200 a month, which is a steep first paid step for a two-person team. Billing is denominated in gigabyte-months of span storage at $1 per additional GB-month, a unit that is harder to predict from application code than a count of records or traces. The OTLP endpoint accepts HTTP only, not gRPC, and [self-hosting the platform](https://www.confident-ai.com/docs/self-hosting) is an Enterprise arrangement.

Suited to teams that will write their evals against DeepEval's 50+ metrics whether or not they buy the platform: the library is Apache 2.0 either way, and the hosted platform is the part that starts at $200 a month.

### 7\. Galileo: when judge-model cost at volume is the binding constraint

Galileo's [Luna-2 small language models](https://galileo.ai/luna-2) are trained specifically for evaluation rather than general chat, which is a direct answer to the reason most teams sample their judges: a general-purpose model is too slow and too expensive to run on everything. Metrics apply to both experiments and live log streams, custom metrics can be LLM-graded or code-based, and it accepts [OTLP traces](https://docs.galileo.ai/integrations/otel). The free plan is [5,000 traces a month with unlimited users](https://galileo.ai/pricing).

Pro is $100 a month for 50,000 traces at annual billing, and the pricing page says cost scales with trace volume without publishing an overage rate, so anything past the tier is a quote rather than a calculation. Cisco announced its intent to acquire Galileo on April 9, 2026, and the same announcement now carries a [May 22, 2026 update](https://blogs.cisco.com/news/cisco-announces-the-intent-to-acquire-galileo) stating "we are pleased to have completed the acquisition of Galileo." That puts the roadmap inside a much larger observability portfolio and makes the long-term product direction someone else's decision.

For enterprises scoring at volumes where the judge model's own token bill is the binding constraint.

## Comparison at a glance

| Tool | License | Self-hosting | Offline evals | Online evals | LLM-as-a-judge | OTLP ingest | Free tier | Paid entry | Billing unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pydantic Logfire | SDKs MIT; platform proprietary | Enterprise plan only | Hosted or code-defined cases; compare runs from Python or TypeScript | Same `Evaluator` classes on sampled live traffic | Built-in `LLMJudge` plus custom evaluators | Native, and the SDK can export to any OTLP backend | [Personal, $0/month: 10M records, 30-day retention](https://pydantic.dev/pricing) | [Team, $49/month: 10M records, then $2/M](https://pydantic.dev/pricing) | Telemetry records; no separate score fee |
| Braintrust | Proprietary | Enterprise | Eval suites in Python and TypeScript, plus a hosted playground | Online scores recorded through the SDK, counted like offline ones | LLM-graded and code scorers | Endpoint at `api.braintrust.dev/otel`; traces need a root span | [Starter, $0/month: 10k scores, 1 GB, 14-day retention](https://www.braintrust.dev/pricing) | [Pro, $249/month: 50k scores, 5 GB, 30-day retention](https://www.braintrust.dev/pricing) | Scores, processed GB, and retention GB-months |
| Langfuse | Core MIT; `ee/` directories commercial | Free for the core; license key for RBAC, audit logs, retention policies | Datasets and dataset runs | Managed evaluators on production traces | Managed LLM-as-a-judge; each score is a billable unit | HTTP/JSON and HTTP/protobuf; no gRPC | [Hobby, $0/month: 50k units, 2 users, 30-day access](https://langfuse.com/pricing) | [Core, $29/month: 100k units, then $8/100k](https://langfuse.com/pricing) | Units: traces plus observations plus scores |
| LangSmith | Proprietary | Enterprise (self-hosted or hybrid) | Datasets and experiments | Automations with a sampling rate on production runs | LLM-as-a-judge at run level | Endpoint at `api.smith.langchain.com/otel`; orphan spans are dropped | [Developer, $0/month: 1 seat maximum, 5k base traces](https://www.langchain.com/pricing-langsmith) | [Plus, $39/seat/month: 10k base traces](https://www.langchain.com/pricing-langsmith) | Seats plus base traces, priced in $1.00 storage units |
| Arize Phoenix | Elastic License 2.0 (source-available) | Free self-host, no feature gates | Datasets and experiment reruns | Scores on traces and spans from LLM, code, or human labels | Prebuilt and custom LLM evaluators | Native, OpenInference conventions | [Self-host $0; AX Free, $0/month: 25k spans, 15-day retention](https://arize.com/pricing) | [AX Pro, $50/month: 50k spans, 10 GB](https://arize.com/pricing) | Spans and storage GB on AX; your hardware self-hosted |
| Confident AI (DeepEval) | DeepEval Apache 2.0; platform proprietary | Enterprise (containerized) | DeepEval test runs with 50+ ready-to-use metrics | Metric collections on ingested spans | G-Eval, DAG, and QAG metrics | HTTP only at `otel.confident-ai.com`; no gRPC | [Free, $0/month: 2 seats, 1 project, 5 test runs/week, 1 GB-month](https://www.confident-ai.com/pricing) | [Starter, $200/month: 5 GB-months of spans](https://www.confident-ai.com/pricing) | GB-months of trace spans, $1 per extra GB-month |
| Galileo | Proprietary | Enterprise (hosted, VPC, or on-premises) | Experiments | Metrics on live log streams | Luna-2 evaluation models plus LLM-as-a-judge | Endpoint at `api.galileo.ai/otel/traces` | [Free, $0/month: 5,000 traces, unlimited users](https://galileo.ai/pricing) | [Pro, $100/month billed yearly: 50k traces](https://galileo.ai/pricing) | Traces; overage rate not published |

*Figures checked against each vendor's published pricing and documentation on August 26, 2026. Model inference is billed separately by every tool here.*

## How to choose

- **You want shared datasets, candidate comparisons, and the traces behind failing cases, on one record allowance:** Pydantic Logfire.
- **Your team already maintains its scorers and experiment history in Braintrust:** weigh the cost of migrating those workflows against the per-score bill.
- **Self-hosting under an OSI-approved license is a hard requirement:** Langfuse.
- **Telemetry cannot leave your network and there is budget for a supported deployment:** Pydantic Logfire on Enterprise, which self-hosts the full platform.
- **Your application is LangChain or LangGraph and you value the native integration most:** LangSmith.
- **You want something running on your own hardware today, at zero cost, and you are not reselling it:** Arize Phoenix.
- **You want a large metric catalog to copy from before you commit to a platform:** DeepEval, hosted or not.
- **You are scoring enough production traffic that the judge model's token bill is the problem:** Galileo.
- **You are cost-driven and evaluation-heavy:** compare the meters, not the base prices. A per-score meter and a per-record meter bill the same nightly suite very differently.

## When your existing setup is still the right call

Not every team needs any of these. If your evals are a handful of assertions in CI plus a spreadsheet, and you look at them once a sprint, a platform adds a vendor before it adds insight. Write the failing cases down first.

If you already use Braintrust or Langfuse, plan for the cases, evaluators, and experiment history you need to preserve. Use a representative dataset to compare Logfire's regression-review workflow and running costs before moving the rest.

And if you have a hard on-premises requirement, Logfire's self-hosting lives on the Enterprise plan; without that budget, Langfuse under MIT, or Phoenix under the Elastic License 2.0 if you are not offering it as a service, is the realistic path.

## Frequently asked questions

### What is the difference between offline and online LLM evals?

The decision rule: offline is for changes you make, online is for changes you did not make. Run the dataset before you promote a prompt or model change; that is offline, and it catches a regression before deploy. Provider snapshot updates, index refreshes, and drifting user behavior arrive without a deploy, and only scoring live traffic catches those.

### Is LLM-as-a-judge accurate enough to trust?

Useful, yes. Unsupervised, no. The practical approach is to keep each judge narrow, ask for a recorded reason, and calibrate it against human labels on a small gold set. Deterministic checks should carry every question they can answer: cheaper, faster, and not subject to drift.

### Which LLM evaluation tools are genuinely open source?

Langfuse's core is MIT licensed, DeepEval is Apache 2.0, and the Logfire SDKs are MIT. Arize Phoenix is source-available under the Elastic License 2.0, which permits self-hosting but not offering it to third parties as a managed service. Braintrust, LangSmith, and Galileo are proprietary platforms. The distinction matters most when self-hosting is a requirement.

### Do I need a separate eval tool if I already have observability?

With Logfire, you can start evaluating in the same project: [create a dataset](https://pydantic.dev/docs/logfire/evaluate/manage-datasets/), send an experiment from your eval suite, and review its results alongside your traces. You don't need to buy another platform to add that workflow.

### What is the cheapest way to start evaluating an LLM application?

Write cases against an open-source library first and run them locally. Pydantic Evals and DeepEval both do that at no cost. When you need shared history and comparison across runs, the free tiers differ by an order of magnitude in what they hold: 10 million records a month on Logfire Personal, 50,000 units on Langfuse Hobby, 25,000 spans on Arize AX Free, 5,000 traces on Galileo.

### If I pick one, can I move later?

Your tracing moves easily, because all seven accept OpenTelemetry over OTLP. Two things do not move as cleanly. Eval history is stored per vendor, so baselines usually stay behind, and evaluators written against a vendor SDK need rewriting unless the tool runs plain code you own. Keeping evaluator logic in your own repository is the cheapest insurance available.

## Try Pydantic Logfire free

The [free Personal plan](https://pydantic.dev/pricing) includes 10 million records a month, and eval scores are records rather than a separate meter. [Start with the evals docs](https://pydantic.dev/docs/logfire/evaluate/evals-in-code/), or [sign up](https://pydantic.dev/signup) and send your first experiment.
