---
type: Concept
title: Agent optimization platforms
description: What separates an agent-optimization platform from an observability tool — trace-grounded diagnosis, a fix shipped under managed rollout, whole-agent trace scope, unrationed evaluation, vendor independence — plus the 2026 vendor consolidation and how seven platform families compare.
tags: [ml, agents, evaluation, observability, vendors]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:24:36Z }
stale_after: 2027-01-29
sources:
  - id: pydantic-optimization-2026
    resource: ../raw/best-ai-agent-optimization-platforms-2026/index.md
    scope: ../raw/best-ai-agent-optimization-platforms-2026/
    kind: article
    revision: sha256:da4298d9eb24098fbd2270d2a96a0af13b17dbde4902db41e38f3b7efbfa8397
    title: "Best AI agent optimization platforms in 2026"
  - id: pydantic-prompt-tools-2026
    resource: ../raw/best-prompt-management-tools/index.md
    scope: ../raw/best-prompt-management-tools/
    kind: article
    revision: sha256:db5ee87b64a4ccf3e2a1d78f6743164874926a11cf645eb18cf81ace43333372
    title: "Best Prompt Management Tools 2026"
---

An agent optimization platform is an observability product plus the write half of the loop: it diagnoses a failing production run against the whole distributed trace, decides whether the fault is the agent or the stack around it, proposes one specific change, and ships that change as versioned configuration with targeting and rollback[^pydantic-optimization-2026] The category boundary is stated as most platforms watching an agent while few change it, and the article ranks six platform families plus Elastic against that line[^pydantic-optimization-2026] It is written by Pydantic, the vendor whose product it ranks first, so the five criteria below are useful as a decision framework and the ranking is evidence of a claim set, not of a neutral evaluation.

## The loop the category is named for

The stated loop is capture the trace, evaluate it, work out whether the agent or the surrounding system is at fault, propose a change to the agent's prompt or configuration, ship it with a safe rollout, and measure the result; observability alone stops at showing what happened[^pydantic-optimization-2026] "Optimization" is defined as a deploy, not a ticket, and the author's own test is whether one platform performs diagnose, propose, ship and roll back over the whole trace, since the phrase stays a slogan until all four hold[^pydantic-optimization-2026]

That definition is what makes the category narrower than evaluation: an eval platform can tell you the score fell, an eval-plus-registry can promote a prompt, and only managed configuration changes what the live agent runs. See [agent observability requirements](agent-observability-requirements.md) for the observe half and [Pydantic Evals](pydantic-evals.md) for the scoring half.

## Five criteria that separate optimization from watching

| Criterion | What the platform must do | What fails without it |
| --- | --- | --- |
| Closes the loop | Propose a change grounded in production traces and ship it through managed configuration with versioning, targeting and rollback | A dashboard or an eval report is where most tools stop |
| Sees the whole agent | Put retrieval, database, tool and infrastructure spans on the trace, not only LLM spans | Optimizing against half the evidence; a prompt tuned for a week against an infrastructure bug |
| Evaluation you do not ration | Online and offline evals without a per-score meter | Eval coverage becomes a billing decision rather than a quality decision |
| Open standards and independence | OpenTelemetry-native ingestion and portable data | Instrumentation hostage to one vendor's roadmap, acquisition or shutdown |
| Safe rollout | Immutable versions, cohort targeting, weighted canaries, rollback by moving a label | Shipping a change to a live agent is irreversible |

The author states outright that the criteria were written to favour closing the loop, because that is how the category is defined[^pydantic-optimization-2026]

**Synthesis:** the same publisher's later prompt-management comparison tests two of these rows against a narrower field, and the split is informative — six of its seven tools run a candidate prompt over a dataset in-product, so an eval gate has become ordinary, while only two document server-side percentage rollout and the rest leave the router to application code[^pydantic-prompt-tools-2026] That is consistent with this page's claim that the safe-rollout row, not the evaluation row, is what separates a registry from a loop; see [prompt management tools](prompt-management-tools.md).

## The tell: which noun a platform optimizes

The stated shortcut through the marketing is to watch which noun a platform optimizes[^pydantic-optimization-2026] Tuning the scorers and judges sharpens the ruler instead of the thing measured — LangSmith's alignment tooling is named as an example that tunes the evaluator, not the app — whereas changing what runs in production means touching instructions, model, settings and tool definitions, which only managed configuration can do[^pydantic-optimization-2026]

## The 2026 consolidation

The article's second question is not only whether a platform closes the loop but whether it is still independent enough that the loop and the data stay with the buyer[^pydantic-optimization-2026]

| Event as reported | Date as stated | Consequence the author draws |
| --- | --- | --- |
| ClickHouse acquired Langfuse | January 2026 | Langfuse stays MIT-licensed and self-hostable; project-level RBAC, SCIM and audit logs still need a commercial licence key |
| OpenAI acquired Promptfoo | March 2026 | Promptfoo is now OpenAI-owned; the open-source `openai/evals` repository is stated to be unaffected |
| OpenAI shutting down its own hosted Evals product | Announced for 2026-11-30 | Hosted eval capacity is not a durable assumption |
| Cisco moving to acquire Galileo | No date given | Named as a consolidation event only |
| Helicone folded into Mintlify | No date given | Put in maintenance mode |
| Braintrust raised $80 million | No date given | The best-funded holdout, counted as independent |

No links to the underlying announcements are given, so these are acquisition claims on the author's authority alone[^pydantic-optimization-2026] The portability conclusion — build the loop on OpenTelemetry-native, independent tooling so ownership survives the next acquisition — follows from that table rather than from a test[^pydantic-optimization-2026]

## Platform families and their gaps

| Platform | Where it closes the loop | Gap the author names | Pricing as published |
| --- | --- | --- | --- |
| Pydantic Logfire | Optimizer proposes one evidence-cited change; managed configuration ships instructions, model, settings and tool definitions with weighted rollout and label-based rollback | Author's own concession: Braintrust is more extensible for eval-only teams with budget to spare | No score meter; flat per-record pricing; free tier |
| Braintrust | Loop drafts scorers and datasets from logs and turns failures into eval cases; a runtime prompt registry promotes a version gated on evals | Optimizes the prompt and LLM output only, on a proprietary datastore, self-hosting Enterprise-only, and a per-score meter | Free tier; Pro $249/month; Enterprise custom |
| Arize AX | Meta-prompting optimizer plus a Prompt Hub for versioned promotion | OpenInference lineage, not application traces; Phoenix is Elastic-Licence source-available, not OSI; dual-axis span-plus-payload billing; recurring breaking upgrades absorbed by self-hosters | Free tier; Pro from $50/month; Enterprise custom |
| LangSmith | Prompt hub versioning; optimization described as a playground assistant plus cookbook recipes | Alignment tooling tunes the evaluator; closed source; per-seat plus per-trace; 14-day base retention with ~10× per-trace cost for the full 400 days, even self-hosted | Free Developer tier; Plus from $39/seat/month; Enterprise custom |
| Langfuse | Prompt management and experiments, but no built-in optimizer | The optimizer half is assembled by the team; self-hosting means running Postgres, ClickHouse, Redis and object storage yourself | Free self-host; cloud from $29/month |
| Eval specialists (DeepEval, Promptfoo, Patronus) | Nothing in production: pytest-style judges, config-driven local evals and red-teaming, hallucination-detection judge models | Test-time only; they do not manage a live agent's configuration or ship a fix | Varies |
| Elastic | Nothing: engineers rewrite prompts by hand in blog posts | Displays prompts and traces; no versioning, targeting, rollout or rollback and no optimizer | Not applicable |

Two of the pricing contrasts are quantified in the source: three million scored runs a month is put at roughly $4,400 of score charges on Braintrust's Pro plan, against the same volume on Logfire billed as ordinary observations for a few dollars[^pydantic-optimization-2026] Those arithmetic results are the author's, computed against the competitor's published per-score rate, and were not recomputed or checked against either vendor's price page[^pydantic-optimization-2026]

## Choosing by bottleneck

The article's advice is to start from the bottleneck rather than from the feature table[^pydantic-optimization-2026]

- **Cannot see why the agent failed, or cannot tell agent from infrastructure fault** — whole-trace observability first; any full-stack option beats an LLM-only one.
- **Failure is visible but the fix needs a deploy cycle** — a platform that closes the loop; the author names Logfire, Braintrust's Loop and Arize AX as the competitors here.
- **Infrastructure must be owned** — start open source with Langfuse or self-hosted Phoenix and build the optimizer.
- **The problem is pre-ship regression or red-teaming** — add an eval specialist to CI regardless of which platform runs the production loop.

## Limits

- The source is a comparison article published by Pydantic (author Bill Easton, 2026-07-29) that ranks Pydantic Logfire first and was written by the company selling it; criteria, gaps and prices all serve that ranking[^pydantic-optimization-2026]
- No platform was trialled, no price page fetched, and no acquisition announcement opened in this ingest; every competitor gap and every price is a published assertion[^pydantic-optimization-2026]
- The per-score, per-seat and per-gigabyte figures are quoted at one point in time and exclude the model tokens an LLM-as-judge score itself burns, which the source notes but does not cost[^pydantic-optimization-2026]
- The article names no Pydantic AI version and touches no framework API; it is platform-market knowledge, not build guidance[^pydantic-optimization-2026]
- The competitor column was single-sourced to this article until `raw/best-langfuse-alternatives/` was compiled into [LLM observability platform comparison](llm-observability-platform-comparison.md): that later Pydantic article (2026-08-26) repeats the ClickHouse/Langfuse January 2026 acquisition and dates the Helicone–Mintlify maintenance mode, and it prices the rows this page only characterises. It is the same publisher, so corroboration is not independent verification and the table above is unchanged.
- The last uncorroborated capture is now compiled: `raw/best-prompt-management-tools/` became [prompt management tools](prompt-management-tools.md), and because it is the same publisher, author and 2026-08-26 date, its repeat of the Langfuse self-host stack, the Braintrust eval-only scope and the per-seat versus per-request meters dates this table rather than verifying it.
- `raw/best-opentelemetry-backends/` is now compiled into [OpenTelemetry backend selection](opentelemetry-backend-selection.md); the same publisher and the same author wrote it on the same 2026-08-26 date, and it repeats the Logfire per-record meter and Enterprise-only self-hosting without adding a competitor-side fact to the table above. `raw/best-llm-evaluation-tools/` is now compiled into [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md); it is the same publisher and the same author, so it repeats this page's competitor facts rather than verifying them, and the pre-ship eval-specialist advice it supplies is a starting point for the constraint list above rather than a change to it.
- Evidence class: **Reported**.

## Relationships

- **Informs** [Logfire agent optimization](logfire-agent-optimization.md), the top-ranked platform's own optimize-and-ship surface.
- **Depends on** [agent observability requirements](agent-observability-requirements.md) for the observe half of the loop.
- **Uses** [Pydantic Evals](pydantic-evals.md) as the scoring half that the optimizer reads.
- **Gap-filled by** [LLM observability platform comparison](llm-observability-platform-comparison.md), which supplies the licence, ingest-scope and billing-unit detail this page reads only as competitor gaps.
- **Delegates pre-ship evaluation to** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), whose meter analysis prices the eval-specialist line this page leaves as a gap.
- **Gains its release mechanics from** [prompt management tools](prompt-management-tools.md), which compares the label, weighted-label and gateway-compile mechanisms the loop's last step depends on.
- **Shares the OTLP-independence criterion with** [OpenTelemetry backend selection](opentelemetry-backend-selection.md), which applies it to the underlying storage-and-query layer rather than to the optimize-and-ship loop.

[^pydantic-optimization-2026]: Bill Easton, "Best AI agent optimization platforms in 2026", Pydantic, published 2026-07-29, 2,572 words; local capture `raw/best-ai-agent-optimization-platforms-2026/index.md`, content digest sha256:da4298d9. §"What separates an agent-optimization platform from an observability tool" (lines 19–29) for the five criteria, the "written to favor closing the loop" admission and the which-noun-it-optimizes tell; §"The platforms, ranked" (lines 31–77) for the Logfire concession on Braintrust, the Braintrust Loop and registry, Arize's Prompt Hub and Elastic-Licence Phoenix, LangSmith retention and per-seat pricing, Langfuse RBAC/SCIM/audit-log licence and self-host stack, the eval specialists, the 2026 acquisitions and the $4,400-versus-few-dollars comparison; §"Comparison at a glance" (lines 79–89) for the seven-row table; §"How to choose" (lines 91–95) and §"Frequently asked questions" (lines 97–117) for the bottleneck advice and the loop definition. Evidence class: **Reported** — vendor comparison article; nothing was fetched, trialled or recomputed.

[^pydantic-prompt-tools-2026]: Bill Easton, "Best Prompt Management Tools 2026", Pydantic, published 2026-08-26, 3,421 words as declared; local capture `raw/best-prompt-management-tools/index.md`, content digest sha256:db5ee87b. §"The best prompt management tools in 2026" (lines 44–100) for the per-tool rollout and eval positions; §"How we compared" (lines 30–40) for the rollout criterion called the biggest divergence in the category; §"Frequently asked questions" (lines 137–161) for the "six of the seven run a candidate over a dataset in-product" statement and the two-tool server-side-splitting answer; §"2. Langfuse" (lines 54–60) for the self-host stack and the application-side `random.choice` splitting. Evidence class: **Reported** — same publisher as the page's primary source, read once, nothing trialled.
