---
type: Concept
title: LLM evaluation tool comparison
description: How seven 2026 LLM evaluation tools differ on where a score lands, what unit it is billed in, and how far the score sits from the trace — with the meters, OTLP quirks and migration limits that decide between them.
tags: [ml, agents, evaluation, vendors, licensing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:10:00Z }
stale_after: 2027-02-26
sources:
  - id: pydantic-eval-tools-2026
    resource: ../raw/best-llm-evaluation-tools/index.md
    scope: ../raw/best-llm-evaluation-tools/
    kind: article
    revision: sha256:6a9f009216a57d12fd893e17a7388b01e6bfa5ed482e0d3443a5003ac5eab103
    title: "Best LLM Evaluation Tools 2026"
  - id: logfire-evals-focus-2026
    resource: ../raw/focus-on-evals-with-logfire/index.md
    scope: ../raw/focus-on-evals-with-logfire/
    kind: article
    revision: sha256:359c59fe65f12c14c4534e34f06554c4480836e136d0b1931066b7d281810250
    title: "Focus on evals with Logfire, not score metering"
  - id: jev-evals-2026
    resource: ../raw/jev-evals/index.md
    scope: ../raw/jev-evals/
    kind: article
    revision: sha256:c34f4321a3b5786600eeefff3fc14216036d1f0d9c3b4bfba2686aca93241c0a
    title: "Cheap AI scoring with Jev and Pydantic Evals"
---

Once every vendor ships datasets, experiments and a judge, feature checkboxes stop separating LLM evaluation tools; what separates them is where the score lands, what unit it is billed in, and how far the score sits from the trace that produced it[^pydantic-eval-tools-2026] Seven tools are compared on those axes, and the transferable result is not the ranking — Pydantic Logfire is ranked first by a Pydantic article — but the meters: a per-score meter, a per-record meter, a per-span meter and a per-gigabyte-month meter bill the same nightly suite very differently[^pydantic-eval-tools-2026] This page holds the evaluation-specific field; [LLM observability platform comparison](llm-observability-platform-comparison.md) covers the same vendors as observability platforms, and [LLM evaluation modes](llm-eval-modes.md) covers the offline/online/judge vocabulary the table assumes.

## The five criteria

The criteria are ordered by when they start to matter, and only the first three are evaluation-specific[^pydantic-eval-tools-2026]

| Criterion | The question | What a bad answer costs |
| --- | --- | --- |
| Where the score lands | Is an eval result a first-class record beside the trace that produced it, or an object in a separate evaluation database? | A regression becomes a number you cannot navigate back from |
| Billing unit | Scores, traces, units, gigabyte-months or seats? | The habit the vendor's meter rewards is the one that gets expensive |
| Licence, precisely | MIT and Apache 2.0 are open source; the Elastic License 2.0 is source-available — runnable, not resellable as a managed service | Self-hosting plans fail a licence review after the pilot |
| Instrumentation portability | All seven accept OTLP, so traces travel; eval results often do not | Baselines and histories are stranded on migration |
| Scope beyond evals | An evaluation product, or an observability platform with evaluation inside it? | Buying the wrong shape is expensive in either direction |

The portability criterion is the one with no vendor-neutral answer: scores stored as a proprietary object type stay behind when the spans move, so the licence to leave is written in the data model, not the pricing page[^pydantic-eval-tools-2026]

## The seven tools

Prices, licences and allowances are the vendor's own published figures, checked by the author on 2026-08-26[^pydantic-eval-tools-2026]

| Tool | Licence | Self-host | Free tier | Paid entry | Billing unit | OTLP note |
| --- | --- | --- | --- | --- | --- | --- |
| Pydantic Logfire | SDKs MIT; platform proprietary | Enterprise only | Personal $0: 10M records, 30-day retention | Team $49/month: 10M records, then $2/M; Growth $249 with up to 90-day retention | Telemetry records; no separate score fee | Native, and the SDK exports to any OTLP backend |
| Braintrust | Proprietary | Enterprise | Starter $0: 10k scores, 1 GB, 14-day retention | Pro $249/month: 50k scores, 5 GB, 30-day retention | Scores plus processed GB plus retention GB-months | Root span required; child-only traces do not appear |
| [Langfuse](langfuse.md) | Core MIT; `ee/` commercial | Free for the core | Hobby $0: 50k units, 2 users, 30-day access | Core $29/month: 100k units, then $8/100k | Units: traces + observations + scores | HTTP/JSON and HTTP/protobuf; no gRPC |
| LangSmith | Proprietary | Enterprise (self-hosted or hybrid) | Developer $0: 1 seat maximum, 5k base traces | Plus $39/seat/month: 10k base traces | Seats plus base traces, priced in $1.00 storage units | Orphan spans dropped silently |
| Arize Phoenix | Elastic License 2.0, source-available | Free, no licence fees, no usage limits, no feature gates | Self-host $0; AX Free $0: 25k spans, 15-day retention | AX Pro $50/month: 50k spans, 10 GB | Spans and GB on AX; your own hardware self-hosted | Native, OpenInference conventions |
| Confident AI (DeepEval) | DeepEval Apache 2.0; platform proprietary | Enterprise, containerized | $0: 2 seats, 1 project, 5 test runs/week, 1 GB-month | Starter $200/month: 5 GB-months | GB-months of trace spans, $1 per extra | HTTP only, no gRPC |
| Galileo | Proprietary | Enterprise (hosted, VPC, on-premises) | $0: 5,000 traces, unlimited users | Pro $100/month billed yearly: 50k traces | Traces; overage rate not published | Endpoint at `api.galileo.ai/otel/traces` |

Per-tool detail the table compresses, all **Reported**[^pydantic-eval-tools-2026]

- **Logfire** is the only row where the score is not a meter: evaluation records share the store and the record allowance with traces, remain queryable in PostgreSQL-compatible SQL, and a hosted dataset case can be preserved from a production trace with its source link retained.
- **Braintrust** defines a score as the output of an offline *or* online evaluation and charges per score — $2.50 per thousand on Starter, $1.50 per thousand on Pro — so the number the product exists to produce is the number that raises the invoice.
- **LangSmith** splits the bill across seats and traces, keeping base traces 14 days unless they are upgraded to 400-day extended traces, and its online evaluations run judge cost against a configurable sample rate.
- **Arize Phoenix** is the free local-first option, and its commercial AX layer is the only one metered in spans; embedding it in your own product is what the Elastic License 2.0 clause forbids.
- **Confident AI** is the row where the library and the platform have different licences: DeepEval's 50+ metrics (G-Eval, DAG, QAG) are Apache 2.0 in Python and TypeScript whether or not the platform is bought, and the free tier is shaped like a trial — spans are dropped past 1 GB-month, and the first paid step is $200 a month.
- **Galileo** addresses judge cost with Luna-2 small language models trained for evaluation rather than general chat, on the argument that a general-purpose judge is too slow and too expensive to run on everything; Cisco's April 9, 2026 acquisition announcement carries a May 22, 2026 update stating the acquisition completed, which puts the roadmap inside a larger observability portfolio.
- **Langfuse** appears here only as a comparison-table row: the capture has no dedicated Langfuse entry, so its licence, unit and ingest facts on this page come from the table alone.

## The meter, worked through

The examples the author uses are arithmetic, not benchmarks: a nightly benchmark of scored cases is the workload that separates a per-score meter from a per-record one, and the article points to its own worked figures rather than restating them[^pydantic-eval-tools-2026] Those figures exist in the same author's companion article, and they are modelled bills rather than measured ones[^logfire-evals-focus-2026]

Braintrust's Pro plan meters three things at once: scores at $1.50 per thousand after the first fifty thousand, processed data at $3 per gigabyte after the first five, and retention at $0.50 per gigabyte per month after the included thirty days[^logfire-evals-focus-2026] Logfire charges no separate score fee — an evaluation result is an OpenTelemetry event attached to its originating trace and billed with the same records as everything else, at $2 per million after the first ten million each month[^logfire-evals-focus-2026] Both plans start at $249 a month, and model execution is outside both[^logfire-evals-focus-2026]

| Marginal usage past the inclusive allowances | Braintrust Pro | Logfire Growth |
| --- | --- | --- |
| 1M source spans, 90-day retention | About $4 | $2 |
| 1M score results | $1,500 | $2 |
| **Combined** | **About $1,504** | **$4** |

The online case scales with traffic, because an online evaluator scores every production trace rather than a curated set, and Braintrust counts online and offline scores against the same monthly allowance[^logfire-evals-focus-2026] The offline case scales faster: OpenAI's public `simple-evals` MATH runner loads a 5,000-case test set, repeats every case ten times and records one score per attempt, so one complete run writes 50,000 score records and consumes Braintrust Pro's entire monthly score allowance[^logfire-evals-focus-2026]

| Portfolio | Modelled monthly workflow | Scores per month | Braintrust score charge per month | Separate Logfire score fee |
| --- | --- | --- | --- | --- |
| 1 agent | One MATH-sized suite × 30 nights | 1.5M | $2,175 | $0 |
| 10 agents | Ten suites × 30 nights | 15M | $22,425 | $0 |
| 50 agents | Fifty suites × 30 nights | 75M | $112,425 | $0 |

The source annualises the same three rows at $26,100, $269,100 and $1,349,100, and its point is that the difference is not storage: it is the charge for recording each score[^logfire-evals-focus-2026] Three consequences follow that need no trial to check.

- **Scoring more is the point of the tool**, so a meter that counts scores taxes exactly the behaviour the tool exists to encourage; on Langfuse and Braintrust the quality programme is a visible cost line, and on Logfire it is flat but rides the instrumentation volume instead[^pydantic-eval-tools-2026]
- **Free tiers are not comparable**: 10M records a month on Logfire Personal, 50k units on Langfuse Hobby, 25k spans on Arize AX Free and 5,000 traces on Galileo are four different units, and the author's own advice is to compare meters rather than base prices when evaluation-heavy[^pydantic-eval-tools-2026]
- **Judge tokens are outside every price**: model and judge inference is billed separately by every tool in the comparison, so the cheapest platform per record can still be the expensive one at a high judge sample rate[^pydantic-eval-tools-2026]

## When the judge is cheap

Every bill above leaves judge inference out, and one worked case shows how much that omission decides. A Pydantic author scored a million support replies with three results each using TypeSafe's Jev — a structured-decision model at $0.042 per million input tokens with no output charge: $42 of judge inference plus $20 of Logfire telemetry at ten records per reply, against $4,500 of Braintrust Pro score overage plus the same $42, or about 1.4% of the Braintrust subtotal and roughly 73 times less[^jev-evals-2026] The sensitivity checks keep the shape: longer prompts raise both inference columns equally ($188 versus $4,668 at 4,000 tokens per reply), more telemetry raises only Logfire's total ($142 at fifty records per reply), and neither case introduces a score-specific fee[^jev-evals-2026]

**Synthesis:** the meter argument on this page holds for a general-purpose judge, where the token bill can be comparable to the score bill. Replace the judge with a cheap structured model and the per-score fee becomes the dominant line, which reverses the practical advice rather than cancelling it — the platform meter still decides the bill, but the direction of the decision flips. The Jev figures are the vendor's own arithmetic under stated assumptions, so they date this comparison rather than settle it.

## OTLP ingest is not uniform

All seven accept OpenTelemetry, and the edge cases are the ones that silently lose data[^pydantic-eval-tools-2026] Braintrust's OTLP ingest requires a root span, so traces made only of child spans do not appear in the logs table[^pydantic-eval-tools-2026] LangSmith drops a span whose parent is never sent to it — silently, which the author flags as the real risk for teams fanning telemetry to more than one backend[^pydantic-eval-tools-2026] Confident AI accepts HTTP only, not gRPC[^pydantic-eval-tools-2026] Langfuse takes HTTP/JSON and HTTP/protobuf, with no gRPC[^pydantic-eval-tools-2026] Each is a one-line difference with a whole-trace consequence, and none of them was exercised here.

## What survives a migration

Tracing moves easily: redirect the SDK to another OTLP endpoint and re-point a header[^pydantic-eval-tools-2026] Two things do not[^pydantic-eval-tools-2026]

- **Eval history** is stored per vendor, so baselines usually stay behind and an experiment history has to be rebuilt on the new platform.
- **Evaluators** written against a vendor SDK need rewriting, unless the tool runs plain code you own.

The cheap insurance the author names is keeping evaluator logic in your own repository, which is also the property that makes [Pydantic Evals](pydantic-evals.md) and DeepEval portable: both are libraries whose datasets and metrics run locally at no cost[^pydantic-eval-tools-2026]

## Choosing by constraint

- **Shared datasets, candidate-versus-baseline comparison, and the traces behind failing cases on one record allowance:** Pydantic Logfire.
- **Scorers and experiment history already maintained in Braintrust:** weigh migrating that work against the per-score bill.
- **Self-hosting under an OSI-approved licence, non-negotiable:** Langfuse.
- **Telemetry cannot leave the network, with budget for a supported deployment:** Logfire Enterprise, which self-hosts the full platform.
- **The application is LangChain or LangGraph and the native integration matters most:** LangSmith.
- **An evaluation UI on your own hardware today at zero cost, and not reselling it:** Arize Phoenix.
- **A large metric catalog to borrow from before committing to a platform:** DeepEval, hosted or not.
- **Scoring at a volume where the judge model's own token bill is the binding constraint:** Galileo.
- **Cost-driven and evaluation-heavy:** compare the meters, not the base prices[^pydantic-eval-tools-2026]

And the escape hatch the author is careful to leave open: with a handful of CI assertions reviewed once a sprint, a platform adds a vendor before it adds insight, so the failing cases should be written down first[^pydantic-eval-tools-2026]

## Limits

- The source is Pydantic's own comparison article (Bill Easton; published 2026-08-26, evaluation workflows updated 2026-09-12) that ranks Pydantic Logfire first; the criteria, the meters and the recommendation all serve that ranking[^pydantic-eval-tools-2026]
- No price page, licence file, documentation page or acquisition announcement was fetched in this ingest, and no platform was trialled; every price, tier, retention period and licence claim is one dated assertion read once[^pydantic-eval-tools-2026]
- The capture has no dedicated Langfuse entry: numbered sections run 1, 2, 4, 5, 6, 7, so the third-ranked tool is missing from the body and its row here rests on the table alone (**Synthesis**: the missing entry is Langfuse by inference from the frontmatter's seven-name list, not a numbered heading)[^pydantic-eval-tools-2026]
- The worked score arithmetic comes from the author's separate Logfire evals article (2026-08-04), not from this capture, and its caveats travel with it: the dollar figures model a nightly workflow rather than a measured bill, they exclude model and judge inference, they assume each case is scored once, and neither price page was fetched[^logfire-evals-focus-2026] The 5,000-cases-times-ten MATH run is quoted from OpenAI's public `simple-evals` runner by link, not executed[^logfire-evals-focus-2026]
- Galileo's overage rate is unpublished by the vendor and is therefore a quote rather than a calculation past the Pro tier[^pydantic-eval-tools-2026]
- The cheap-judge case is a fourth Pydantic capture (David Montague, 2026-09-23) whose figures are planning assumptions rather than a measured bill: 1,000 billed judge input tokens and ten telemetry records per reply, inclusive allowances already consumed, subscription fees and the application's own inference excluded, and Braintrust's processed-data and retention charges absent from its column[^jev-evals-2026] No price page was fetched and no run was billed here.
- The closing "Try Pydantic Logfire free" block was excluded as promotion except for the free-tier record allowance already in the table; the vendor documentation links throughout were read as links, not followed[^pydantic-eval-tools-2026]
- Evidence class: **Reported**.

## Relationships

- **Surveys the eval half of** [LLM observability platform comparison](llm-observability-platform-comparison.md), which reads the same vendors on licence, self-host and ingest scope rather than on where a score lands.
- **Depends on** [LLM evaluation modes](llm-eval-modes.md) for the offline/online/judge distinction that the table's eval columns assume.
- **Recommends hosting** [Pydantic Evals](pydantic-evals.md) datasets, and separates the library's local scoring from Logfire's shared workspace.
- **Prices the evaluation line inside** [Logfire agent optimization](logfire-agent-optimization.md), where "evaluation billed as observations" is the same flat-record claim.
- **Supplies the bill** for [Logfire Evals workspace review loop](logfire-evals-workspace.md), which takes the same no-separate-score-fee premise and works the review side — run overview, baseline comparison, case, trace.
- **Corroborates** [Langfuse](langfuse.md)'s billable unit and trace-only OTLP path from a second Pydantic article, which is the same publisher and therefore not independent verification.
- **Answers the eval-specialist gap** in [agent optimization platforms](agent-optimization-platforms.md), whose constraint list sends pre-ship regression work to an eval specialist.
- **Is qualified by** [Jev structured scoring judge](jev-structured-scoring-judge.md), the cheap-judge case where the per-score fee outweighs inference and inverts which meter binds.

[^pydantic-eval-tools-2026]: Bill Easton, "Best LLM Evaluation Tools 2026", Pydantic, published 2026-08-26, evaluation workflows updated 2026-09-12, prices checked 2026-08-26, 3,349 words as declared; local capture `raw/best-llm-evaluation-tools/index.md`, content digest sha256:6a9f0092. §"TL;DR" and byline (lines 11–19) for the shared-workspace pitch and the no-separate-score-fee claim; §"Why teams look for a dedicated evaluation tool" (lines 21–26) for the evaluation-has-a-bill argument and the four metering shapes; §"Offline evals, online evals, and LLM-as-a-judge are not three tools" (lines 28–38) for the claim that the checkboxes no longer separate the products; §"How we compared" (lines 40–50) for the five criteria, the Elastic License 2.0 definition and the eval-results-do-not-travel warning; §"The best LLM evaluation tools in 2026" (lines 52–113) for the Logfire hosted-case, baseline-comparison and record-allowance detail, the Braintrust per-score arithmetic and root-span requirement, the LangSmith seat-and-storage-unit bill and orphan-span drop, the Arize Phoenix self-host and AX span tiers, the DeepEval metric catalogue and GB-month meter, and the Galileo Luna-2, overage and Cisco acquisition facts; §"Comparison at a glance" (lines 115–127) for the seven-row table, the Langfuse row and the separate-inference footnote; §"How to choose" (lines 129–139) and §"When your existing setup is still the right call" (lines 141–147) for the constraint list and the write-the-failing-cases-first advice; §"Frequently asked questions" (lines 149–173) for the four free-tier volumes, the open-source licence roll-call and the migration-insurance answer. Evidence class: **Reported** — a vendor comparison article; nothing fetched, trialled or recomputed.

[^jev-evals-2026]: David Montague, "Cheap AI scoring with Jev and Pydantic Evals", Pydantic, published 2026-09-23T16:00Z, 2,416 words as declared; local capture `raw/jev-evals/index.md`, content digest sha256:c34f4321. §"But how much will this cost?" (lines 228–258) for Jev's $0.042-per-million input price with no output-token charge, the 1M-reply/three-results model with its 1,000-token and ten-record assumptions, the $42 Jev + $20 Logfire versus $42 Jev + $4,500 Braintrust score-overage table ($62 against $4,542), the 1.4% and 73× ratios, the 4,000-token ($188 versus $4,668) and fifty-record ($142) sensitivity cases, and the statement that Braintrust's processed-data and retention charges are extra; §"Evaluate a support reply" (lines 19–44) for the article's own framing that an explanation is not needed for every production response. Evidence class: **Reported** — the author's arithmetic against published rates; no price page fetched, no bill measured and no judge run.

[^logfire-evals-focus-2026]: Bill Easton, "Focus on evals with Logfire, not score metering", Pydantic, published 2026-08-04, 806 words as declared; local capture `raw/focus-on-evals-with-logfire/index.md`, content digest sha256:359c59fe. §"Three meters" (lines 14–26) for Braintrust Pro's $249 entry and its three usage charges; §"No score meter" (lines 28–32) for evaluation results as OpenTelemetry events on their originating traces, billed at $2 per million records after ten million; §"Online: score every production trace" (lines 34–48) for the online-versus-offline allowance and the 1M-span/1M-score marginal table with its footnote that both plans start at $249 and model execution is separate; §"Offline: repeat the full benchmark" (lines 50–62) for OpenAI's `simple-evals` MATH runner at 5,000 cases × 10 attempts, the 50,000-record run, the three-portfolio table and its annualised figures. Evidence class: **Reported** — the author's arithmetic against published competitor rates; no price page fetched, no bill measured and no benchmark run.
