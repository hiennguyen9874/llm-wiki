---
type: Concept
title: Logfire decision tracing
description: The decide span Pydantic AI 2.50 adds under every DecisionModel request and the Classifier output panel it fills in Logfire Live view — per-question probabilities, a rubric's level distribution, the two-step union view, and what survives when content capture is off.
tags: [pydantic-ai, ml, observability, logfire]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:48:00Z }
stale_after: 2027-03-29
sources:
  - id: jev-live-view-2026
    resource: ../raw/jev-pydantic-ai-live-view/index.md
    scope: ../raw/jev-pydantic-ai-live-view/
    kind: article
    revision: sha256:288f23ddf22c009f4ada93b87fcc6526a089ea7ece6d6c5a229a7dd98e2636f0
    title: "Pydantic AI agents on Jev, traced in Logfire"
---

A classifier that answers `area='billing'` and gets it wrong raises a question the `chat` span could not answer: how sure was it, what did it almost pick, and which route was being filled[^jev-live-view-2026] Pydantic AI 2.50.0 closes that gap with two changes — `DecisionModel`, a base class for any model speaking TypeSafe's Decisions protocol, and a `decide` span nested under the `chat` span for every request such a model sends, recording the questions, the answers with their probabilities, the thresholds applied and the route being filled[^jev-live-view-2026] Logfire renders that span as a **Classifier output** panel on the **Agent Run** tab, so the decision is inspectable at the granularity it was made[^jev-live-view-2026]

## What the decide span carries

The pair of upstream changes is reported as PR [#8696](https://github.com/pydantic/pydantic-ai/pull/8696) for `DecisionModel` and PR [#8698](https://github.com/pydantic/pydantic-ai/pull/8698) for the `decide` span, both released in 2.50.0[^jev-live-view-2026] The span's payload is the whole decision rather than only the winner: every question, every answer with its probability, the thresholds applied, and the route in flight[^jev-live-view-2026]

Answers obey the same `include_content` setting as every other Pydantic AI span[^jev-live-view-2026] With content capture off, the span still carries the question **types** and the routes, but neither the judged text nor the answers — so a content-restricted deployment keeps the shape of a decision and loses its substance[^jev-live-view-2026] **Synthesis:** that split is the privacy/forensics trade-off in one setting; the questions a decision model asks are metadata, and the answers are content.

## The Classifier output panel

Selecting an agent run, a model run, or a `decide` span in Live view opens **Agent Run → Classifier output**, beside the existing **Details**, **Metrics** and **Raw Data** tabs[^jev-live-view-2026] The article's capture is a support-triage agent asking 15 questions about one made-up ticket, with the first five shown[^jev-live-view-2026] That screenshot shows the panel's layout (**Observed**):

- An **Input** block with the judged text truncated and a **Show full input** control, then an **Answers** list in which each row is one question, its chosen answer, and the probability for yes/no rows (`Does this need a reply within the hour? → 62% yes`)[^jev-live-view-2026]
- Pick-one rows collapse to their choice and a **Probability** (`Which area is this about? → billing`, `Probability 60%`) and expand to the alternatives[^jev-live-view-2026]
- A rubric row shows a weighted **Score** (`How severe is the problem? → Score 1.6`) and expands to the level distribution with each level's docstring and a bar — 5% "Annoying, but nothing is blocked", 30% "Something works badly, and there is a workaround", 65% "The customer cannot do their job" — plus a displayed **Model confidence 0.5**[^jev-live-view-2026]
- Below the rows: **Show all 15 questions (5 shown)**, a collapsed **Thresholds** section, and **View decision span**[^jev-live-view-2026]
- A **Final output** block prints the typed result — 10 fields in the capture, including `urgent: true`, `area: "billing"`, `reply_by: "email"`, `churn_risk: 0.62` and `severity: 2`[^jev-live-view-2026]

The article reads the severity example as 65% "cannot do their job", 30% "works badly" and 5% "annoying" behind a score of 1.6[^jev-live-view-2026] **Synthesis:** the displayed score is the probability-weighted mean of those levels (0×0.05 + 1×0.30 + 2×0.65 = 1.60), which is why the score can carry a decimal while the final output's `severity` is the integer `2`; the meaning of the separate **Model confidence 0.5** figure is not stated in the source.

## A union output type takes two steps

A union output type produces two decisions against the same input, and the panel shows both plus the final output[^jev-live-view-2026] The second capture (**Observed**) labels them **Initial classification** and **Fill fields for final_result_Refund**: the first block's single answer is `Selected route → final_result_Refund` at 60% probability, the second asks `Why is the refund due? → duplicate_charge` (60%) and `Should the whole charge be refunded? → 62% yes`, each block carrying its own **Thresholds** and **View decision span**, and the **Final output** printing `reason: "duplicate_charge"` with `full_refund: true`[^jev-live-view-2026] The article's prose describes the same sequence as Jev first picking the union member and then filling its fields[^jev-live-view-2026] The route label carries the member's schema name (`final_result_Refund`), so the panel exposes the generated type name rather than a friendly title[^jev-live-view-2026]

**View decision span** jumps to the `decide` span behind each step, and **Raw Data** still holds every attribute as recorded[^jev-live-view-2026] A run with no decision telemetry falls back to the conversation view the user already knows[^jev-live-view-2026]

## What generalizes beyond Jev

The panel and the spans are keyed to the protocol, not the vendor: `DecisionModel` makes a new Decisions backend a matter of translating its transport, and the `decide` span and Agent Run panel come with it[^jev-live-view-2026] **Synthesis:** decision observability is therefore a property of the model interface a backend implements, which is the reason to route a new classifier through `DecisionModel` rather than through a bespoke tool call — a bespoke decision arrives at Logfire as a tool result with no probabilities, no alternatives and no thresholds.

## Limits

- Single vendor article by a Pydantic developer, published 2026-09-29, describing a feature built by Pydantic and TypeSafe; no independent account of the panel exists in this wiki[^jev-live-view-2026]
- The panel's labels and values are **Observed** from two screenshots; every event, attribute and PR claim is **Reported** prose. No Logfire project, span or trace was opened in this ingest[^jev-live-view-2026]
- The captures are undated beyond the article and unversioned; the stack is implied to be Pydantic AI 2.50.0, and neither the Logfire version nor the UI path to the tab is given[^jev-live-view-2026]
- The 15-question example is one made-up ticket, and the article shows 5 of its rows; the union example is a second, separate ticket, so neither is a benchmark of decision accuracy[^jev-live-view-2026]
- Not covered anywhere in the source: what the span costs in Logfire records, retention of judged content, or whether the panel works for decision models outside Pydantic AI's own instrumentation
- Evidence class: **Reported**, **Observed** for screenshot labels, **Synthesis** where marked.

## Relationships

- **Traces** the model described in [Jev decision model in Pydantic AI](jev-decision-model.md): `decide` spans exist because a `DecisionModel` sends them.
- **Extends** [Pydantic AI observability](pydantic-ai-observability.md), adding a nested span kind and a content-capture rule beside the run, model-request and cache attributes.
- **Sits beside** the [Logfire Evals workspace](logfire-evals-workspace.md): that surface reviews an experiment, this one inspects a single decision behind a failing case.
- **Depends on** content-capture policy as a configuration decision, since `include_content` decides whether the answers are recoverable at all.

[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"The chat span wasn't enough" (raw lines 59–68) for the missing-probability problem, PRs #8696 (`DecisionModel`) and #8698 (`decide` span) in 2.50.0, the span's contents (questions, answers with probabilities, thresholds, route), and the `include_content` behaviour; §"Seeing it in Live view" (lines 70–82) for the Agent Run tab and its **Details**/**Metrics**/**Raw Data** siblings, the **Classifier output** panel, the 15-question ticket with five shown, per-question probabilities, the expanding rubric and severity levels, **View decision span**, **Raw Data**, the union two-step, and the conversation-view fallback; §"Where else you can use Jev" (line 88) for `DecisionModel` generalizing to other Decisions backends with the panel intact. Attachments inspected for **Observed** labels and values: `assets/support-triage.png` (Agent Run/Details/Metrics/Raw Data tabs, Input with **Show full input**, five answer rows at 62%/60%/60%/62%, the expanded severity rubric at 5%/30%/65% with **Model confidence 0.5**, **Show all 15 questions (5 shown)**, **Thresholds**, **View decision span**, and the 10-field final output) and `assets/route-then-fill.png` (**Initial classification** with `Selected route → final_result_Refund` at 60%, **Fill fields for final_result_Refund** with `duplicate_charge` at 60% and `62% yes`, two **View decision span** links, the 2-field final output, and the collapsed **Conversation**). Evidence class: **Reported**, **Observed** for screenshot labels, **Synthesis** where marked; nothing was executed or opened in Logfire.
