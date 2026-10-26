---
type: Concept
title: LLM observability platform comparison
description: How eight LLM observability platforms differ on licence, self-hosting, OTLP ingest coverage and the unit each one bills — and which one to pick once Langfuse is off the table.
tags: [ml, agents, observability, vendors, licensing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:24:36Z }
stale_after: 2027-02-26
sources:
  - id: pydantic-langfuse-alts-2026
    resource: ../raw/best-langfuse-alternatives/index.md
    scope: ../raw/best-langfuse-alternatives/
    kind: article
    revision: sha256:ca8ebbf2906627e3d5b930e13b62421d77cefb001be9758f3487f2a344b13ace
    title: "Best Langfuse Alternatives in 2026"
  - id: pydantic-prompt-tools-2026
    resource: ../raw/best-prompt-management-tools/index.md
    scope: ../raw/best-prompt-management-tools/
    kind: article
    revision: sha256:db5ee87b64a4ccf3e2a1d78f6743164874926a11cf645eb18cf81ace43333372
    title: "Best Prompt Management Tools 2026"
---

Eight products are positioned to replace Langfuse in 2026, and the facts that decide between them are structural rather than feature checkboxes: what the licence actually permits, whether ingest covers the whole application or only the model call, what the meter counts, and whether the query surface is a filter bar or a language[^pydantic-langfuse-alts-2026] The comparison that supplies this page ranks Pydantic Logfire first and keeps Langfuse as a legitimate answer, while the article itself is Pydantic's own[^pydantic-langfuse-alts-2026] — so the transferable content is the four procurement axes and the licence and billing facts, not the ranking. The knowledge base documents the top-ranked product's own surfaces in [Pydantic AI observability](pydantic-ai-observability.md), [Logfire agent optimization](logfire-agent-optimization.md) and [agent optimization platforms](agent-optimization-platforms.md); this page covers the field those claims are made against.

## The five questions the comparison turns on

The author states these criteria are opinionated, and the fifth is the one most vendors avoid answering[^pydantic-langfuse-alts-2026]

| Question | What separates the answers | What a weak answer costs |
| --- | --- | --- |
| Does your instrumentation survive leaving? | OpenTelemetry across the whole data model versus OTLP accepted through an adapter for the LLM slice | Spans are portable only for the part the adapter covers |
| Does the tool see past the model call? | HTTP handlers, database queries and background jobs on the same trace as model and tool spans | Production failures that cross the boundary are invisible |
| What sits on the meter? | How many meters exist and what each one counts — requests, spans, units, scores, gigabytes | A free tier measured in a favourable unit says very little about the shape of the first real bill |
| What does the licence actually permit? | OSI-approved licence end to end versus "source available" (Elastic License 2.0, business-source style) versus an MIT core beside a separately licensed enterprise directory | "Open source" in a feature table is not the same as open source in a legal review |
| Can you ask a question nobody predicted? | A query language versus a filter bar | The filter bar is a ceiling on what you can diagnose |

## How the comparison was assembled

Prices and licence terms were read from each vendor's own pricing page and product documentation on 2026-08-26, and the licence file was opened in each repository; the stated method records the free tier with its limits, the first paid tier with its period and included volume, whether OTLP ingest covers traces only or traces plus logs and metrics, and whether self-hosting includes every feature[^pydantic-langfuse-alts-2026] The author states that every entry gets a lane and a catch, including his own, and where a capability was not clearly documented the comparison says so[^pydantic-langfuse-alts-2026] That is a documentation-reading method, not a trial: no platform was installed or benchmarked, and the figures are one dated snapshot.

## The eight platforms

| Tool | Licence | Self-host | OTLP ingest | Evals | Prompt management | Free tier | Paid entry | Billing unit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pydantic Logfire | Proprietary platform, MIT SDKs | Enterprise plan only | Traces, logs and metrics | Yes — hosted judges and Pydantic Evals | Yes — versions, labels, rollout | 10M records/month, 30-day retention | $49/month Team | Records: spans, logs, metrics |
| [Langfuse](langfuse.md) | MIT core; `ee/` directories separately licensed | Yes — core with no usage limits; nine features need an EE key | Traces only, HTTP/JSON or protobuf | Yes — LLM-as-a-judge and custom | Yes | Hobby 50k units/month, 30-day data access | $29/month Core | Units: traces + observations + scores |
| LangSmith | Proprietary | Enterprise plan only | Traces | Yes | Yes | 5k base traces/month, 1 seat | $39/seat/month Plus | Seats plus base and extended traces |
| Braintrust | Proprietary | Enterprise plan only | Traces, GenAI conventions mapped | Yes — scorers and CI gates | Yes — runtime `invoke()`, version pinning | 1 GB data and 10k scores/month, 14 days | $249/month Pro | Processed GB, scores, model credits, retention |
| Arize Phoenix / AX | Elastic License 2.0, source available, not OSI-approved | Yes — Phoenix runs locally or self-hosted | Traces, OpenInference conventions | Yes | Yes — versioning and playground | Phoenix free; Arize AX 25k spans/month | Arize AX $50/month Pro | Spans and GB ingested on AX |
| Helicone | Apache 2.0 | Yes — Docker Compose or Helm | OpenLLMetry async logger; no general OTLP endpoint | Yes — LLM judge and custom | Yes — versioning and experiments | 10k requests/month, 1 seat | $79/month Pro | Requests plus storage |
| Laminar | Apache 2.0 | Yes — `docker compose` | Traces, gRPC and HTTP | Yes — local or CI against datasets | Not confirmed in the docs, August 2026 | 1 GB, 7 days, 1 seat | $30/month Starter | Data GB plus Signals tokens |
| Confident AI (DeepEval) | Platform proprietary; DeepEval library Apache 2.0 | Enterprise on-premises only | Traces, OTLP over HTTP | Yes — online and CI | Yes — versioning | 1 project, 5 test runs/week, 1 GB-month | $200/month Starter | GB-months of trace spans |

Details the table compresses, all as published on 2026-08-26[^pydantic-langfuse-alts-2026]

- **Logfire** is billed per record, with the same price covering a database span and an LLM call, $2 per additional million records on the Team plan, and a Personal plan that hard-caps at 10 million records a month rather than billing past it.
- **LangSmith** combines seats and traces: Plus includes 10,000 base traces, retention is 14 days for base traces and 400 days for extended traces, which carry their own charge.
- **Braintrust** runs four independent meters — processed data ($3/GB after the included 5 GB), scores ($1.50 per 1,000 after 50,000), retention ($0.50 per GB per month beyond 30 days) and $249 of model credits inside the Pro price.
- **Arize** splits the free local Phoenix from the commercial AX layer, where Pro is $50 a month for 50,000 spans, 10 GB and 30-day retention; Dynatrace agreed to acquire Arize on 2026-08-13, with closing subject to regulatory review.
- **Helicone** prices a permissive proxy: 10,000 requests a month free, Pro at $79, with caching, fallbacks and multi-provider routing in the same layer; Mintlify's acquisition leaves it in maintenance mode, shipping security updates, new models and bug fixes, with no sunset date named.
- **Laminar** is Apache 2.0 end to end and the cheapest first paid step at $30 a month for 3 GB, on roughly 3,200 GitHub stars against Langfuse's roughly 34,000.
- **Confident AI** drops spans beyond the free 1 GB-month rather than billing for them, then jumps to $200 a month (five projects, 5 GB-months) and $2,000 for the Team tier.

## The meter is the real differentiator

The author's argument is that the number of meters, not the headline free tier, predicts the bill[^pydantic-langfuse-alts-2026] Two consequences follow that a buyer can check without running anything.

Where evaluation and annotation land on the same meter as tracing, improving quality measurement raises the tracing bill — Langfuse counts a trace, an observation and a score as interchangeable billable units, so scoring work is a cost line that is easy to miss when sizing a plan[^pydantic-langfuse-alts-2026] Where they are separate meters (Braintrust) the bill is legible per activity but multiplies. Where the product bills per record and treats a score as an ordinary record (Logfire), the price is flat but the volume grows with how much of the application you instrument, which the author names as the catch of his own recommendation[^pydantic-langfuse-alts-2026]

The comparison also warns that free tiers in different units do not convert cleanly, so the cheapest alternative is not answerable from the free-tier column: self-hosting Laminar or Helicone costs infrastructure only, while the lowest hosted entries are Langfuse Core at $29 and Laminar Starter at $30[^pydantic-langfuse-alts-2026]

## Switching vendors is cheap for spans, expensive for workflow

Every product in this comparison except Helicone publishes an OTLP **trace** endpoint, so a standard OpenTelemetry SDK can be redirected with an endpoint and a header — which is the practical payoff of the portability criterion, and the reason the ingest scope (traces only, or traces with logs and metrics) matters more than the endpoint's existence[^pydantic-langfuse-alts-2026] Helicone's documented path is OpenLLMetry, which bypasses its proxy[^pydantic-langfuse-alts-2026]

What does not move automatically is everything vendor-specific: prompt registries, dataset definitions and scorer implementations[^pydantic-langfuse-alts-2026] The same limit is why the article treats sunk workflow as a reason to stay, and why [Pydantic Evals](pydantic-evals.md) style local scoring is the cheaper thing to port.

## Choosing by constraint

- **The AI feature is one service inside a larger application, and failures cross that boundary:** Pydantic Logfire.
- **Legal review requires an OSI-approved licence end to end:** Laminar or Helicone, both Apache 2.0; Langfuse's MIT core does not pass an end-to-end test because of the separately licensed `ee/` directories.
- **Telemetry must stay on your infrastructure, with budget for a supported deployment:** Logfire Enterprise, or Arize Phoenix free where Elastic License 2.0 is acceptable.
- **The app is already LangChain or LangGraph, and framework fit outweighs per-seat pricing:** LangSmith.
- **A deploy must fail when an eval score drops:** Braintrust.
- **Tracing and evals should run on a laptop today:** Arize Phoenix.
- **A logging, caching, failover proxy is the desired shape, and maintenance mode is acceptable:** Helicone.
- **The eval suite is already DeepEval:** Confident AI.
- **SQL against raw telemetry instead of a filter syntax:** Logfire or Laminar[^pydantic-langfuse-alts-2026]

## Limits

- The source is a comparison article published by Pydantic (author Bill Easton, 2026-08-26) that ranks Pydantic Logfire first; criteria, lanes, catches and prices all serve that ranking[^pydantic-langfuse-alts-2026]
- No platform was installed, no trace exported and no price page, licence file or acquisition announcement was fetched in this ingest; every licence, tier, retention period and price is a published assertion read once, on one date[^pydantic-langfuse-alts-2026]
- The article's numbered entries run 1, 3, 4 … 8 with no entry 2, so the missing second-ranked entry is Langfuse by inference from the shortlist: the Langfuse facts on this page are drawn from the introduction, the comparison table, the "when Langfuse is still the right call" section and the FAQ, not from a dedicated entry (**Synthesis**)[^pydantic-langfuse-alts-2026]
- Capability gaps are only as accurate as the vendors' docs on that date; Laminar's prompt-registry and log-ingest coverage are explicitly marked unconfirmed by the author, and no gap was verified[^pydantic-langfuse-alts-2026]
- The article names no Pydantic AI version and touches no framework API; it is platform-market knowledge, not build guidance, which is why this page stays `stable` while the pricing columns carry a `stale_after`[^pydantic-langfuse-alts-2026]
- Corroboration is partial: the Langfuse/ClickHouse and Helicone/Mintlify ownership claims also appear in [agent optimization platforms](agent-optimization-platforms.md), but both articles are Pydantic's, so the competitor column remains single-vendor-sourced. `raw/best-llm-evaluation-tools/` has since been compiled into [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), where the 2026-08-26 table repeats the Langfuse unit definition, the HTTP/JSON-and-protobuf-with-no-gRPC ingest scope and the Hobby and Core figures — the same publisher again, so repetition rather than independent verification, and the rows here are unchanged. `raw/best-opentelemetry-backends/` is now compiled into [OpenTelemetry backend selection](opentelemetry-backend-selection.md), which is the same publisher again and a different comparison — OTLP-native application-telemetry backends rather than LLM-observability products — so it confirms nothing here beyond the shared August 2026 verification date, and Logfire's per-record meter and Enterprise-only self-hosting are the only facts it repeats. `raw/best-prompt-management-tools/` is now compiled into [prompt management tools](prompt-management-tools.md); it is the same publisher and author on the same 2026-08-26 date, and it repeats the Helicone Apache 2.0 licence, the Mintlify maintenance-mode wording, the $79 Pro and 10k-request Hobby tiers, Langfuse's MIT core and $29 Core entry, LangSmith's Enterprise-only self-hosting and $39 seat, and Braintrust's data-plane-yours control-plane-theirs model and $249 Pro tier — so it dates those rows at that date rather than verifying them, and it adds nothing about OTLP ingest scope[^pydantic-prompt-tools-2026].
- Evidence class: **Reported**.

## Relationships

- **Compares** [Langfuse](langfuse.md), whose MIT-core boundary and trace-plus-score meter are the baseline every row is read against.
- **Frames** [Pydantic AI observability](pydantic-ai-observability.md): Logfire's ingest breadth, SQL and MCP surfaces are the top-ranked column here.
- **Supplies the licence and billing axes** that [agent optimization platforms](agent-optimization-platforms.md) reads only as gaps beside the optimize-and-ship loop.
- **Has an eval-specific counterpart in** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), which keeps licence and ingest scope but adds where a score lands and what unit it is billed in.
- **Depends on** [agent observability requirements](agent-observability-requirements.md) for the vendor-neutral failure model underneath the "sees past the model call" criterion.
- **Borders** [OpenTelemetry backend selection](opentelemetry-backend-selection.md), which compares the OTLP-native application-telemetry backends these LLM-observability products sit beside, and which the same author keeps out of scope here.

[^pydantic-langfuse-alts-2026]: Bill Easton, "Best Langfuse Alternatives in 2026", Pydantic, published 2026-08-26; local capture `raw/best-langfuse-alternatives/index.md`, 3,070 words as declared, content digest sha256:ca8ebbf2. §"TL;DR" and the Langfuse framing (lines 13–19) for the shortlist and the Logfire pick; §"Why teams look for a Langfuse alternative" (lines 21–28) for the billable-unit, traces-only OTLP, enterprise-key and ownership reasons; §"What to look for in a replacement" (lines 30–38) for the five criteria and the opinionated-criteria admission; §"How we compared" (lines 40–42) for the 2026-08-26 method and the "every entry gets a lane and a catch" statement; §"The best Langfuse alternatives in 2026" (lines 46–100) for the Logfire, LangSmith, Braintrust, Arize Phoenix, Helicone, Laminar and Confident AI entries with their prices, licences, retention, GitHub-star counts and ownership notes; §"Comparison at a glance" (lines 102–113) for the eight-row table; §"How to choose" (lines 115–125) for the constraint list; §"Frequently asked questions" (lines 137–149) for the OTLP portability and cheapest-alternative answers. Evidence class: **Reported** — a vendor comparison article; nothing was fetched, trialled or recomputed.

[^pydantic-prompt-tools-2026]: Bill Easton, "Best Prompt Management Tools 2026", Pydantic, published 2026-08-26, 3,421 words as declared; local capture `raw/best-prompt-management-tools/index.md`, content digest sha256:db5ee87b. Used only for corroboration dating: §"The best prompt management tools in 2026" (lines 54–100) for the Helicone Apache 2.0 licence, the Mintlify maintenance-mode wording, the Hobby and Pro figures, Langfuse's MIT core, LangSmith's Enterprise-only self-hosting and per-seat price, and Braintrust's hybrid self-hosting model; §"Comparison at a glance" (lines 102–114) for the tier figures restated in one table. Evidence class: **Reported** — same publisher as the page's primary source, read once, nothing fetched.
