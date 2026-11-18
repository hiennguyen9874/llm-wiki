---
type: Concept
title: Logfire decision tracing
description: The decide span Pydantic AI 2.50 adds under every DecisionModel request and the Classifier output panel it fills in Logfire Live view — the documented attribute table with its keying and hand-off rules, per-question probabilities, a rubric's level distribution, the two-step union view, and what survives when content capture is off.
tags: [pydantic-ai, ml, observability, logfire]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:05:00Z }
stale_after: 2027-03-29
sources:
  - id: jev-live-view-2026
    resource: ../raw/jev-pydantic-ai-live-view/index.md
    scope: ../raw/jev-pydantic-ai-live-view/
    kind: article
    revision: sha256:288f23ddf22c009f4ada93b87fcc6526a089ea7ece6d6c5a229a7dd98e2636f0
    title: "Pydantic AI agents on Jev, traced in Logfire"
  - id: pydantic-logfire-docs
    resource: ../raw/integrations/logfire/index.md
    scope: ../raw/integrations/logfire/
    kind: documentation
    revision: sha256:5ea6a3e098a0dc8e4c1337ae9bebbef2d5489cc135597569711c1a96e77d6381
    title: "Pydantic Logfire Debugging and Monitoring"
---

A classifier that answers `area='billing'` and gets it wrong raises a question the `chat` span could not answer: how sure was it, what did it almost pick, and which route was being filled[^jev-live-view-2026] Pydantic AI 2.50.0 closes that gap with two changes — `DecisionModel`, a base class for any model speaking TypeSafe's Decisions protocol, and a `decide` span nested under the `chat` span for every request such a model sends, recording the questions, the answers with their probabilities, the thresholds applied and the route being filled[^jev-live-view-2026] Logfire renders that span as a **Classifier output** panel on the **Agent Run** tab, so the decision is inspectable at the granularity it was made[^jev-live-view-2026]

## What the decide span carries

The pair of upstream changes is reported as PR [#8696](https://github.com/pydantic/pydantic-ai/pull/8696) for `DecisionModel` and PR [#8698](https://github.com/pydantic/pydantic-ai/pull/8698) for the `decide` span, both released in 2.50.0[^jev-live-view-2026] The span's payload is the whole decision rather than only the winner: every question, every answer with its probability, the thresholds applied, and the route in flight[^jev-live-view-2026]

Answers obey the same `include_content` setting as every other Pydantic AI span[^jev-live-view-2026] With content capture off, the span still carries the question **types** and the routes, but neither the judged text nor the answers — so a content-restricted deployment keeps the shape of a decision and loses its substance[^jev-live-view-2026] **Synthesis:** that split is the privacy/forensics trade-off in one setting; the questions a decision model asks are metadata, and the answers are content.

### The attribute table

The integration docs enumerate what a `decide` span records, which turns the article's summary into a checkable surface[^pydantic-logfire-docs]:

| Attribute | Value |
| --- | --- |
| `gen_ai.operation.name` | `decide` |
| `gen_ai.provider.name`, `gen_ai.request.model`, `server.address`, … | The same model attributes as the model request span above it |
| `gen_ai.response.model` | The model that answered |
| `gen_ai.response.id` | The provider's request id, when it returns one |
| `pydantic_ai.decision.thresholds` | `{"boolean": …}` for `decision_boolean_threshold`, plus `"route"` for `decision_route_threshold` when set |
| `pydantic_ai.decision.usage.input_tokens`, `pydantic_ai.decision.usage.output_tokens` | This request's usage |
| `pydantic_ai.decision.questions` | The questions as sent: `{name: {"type": …, "instructions": …, "criteria": …}}`, with `type` one of `noul` (yes/no), `choice` or `score` |
| `pydantic_ai.decision.state` | The state built for the backend — the text being judged, or a JSON object adding the conversation's `history`; a backend that takes the conversation natively, such as OpenAI Decisions, is sent the messages instead and the model request span records them |
| `pydantic_ai.decision.answers` | The answers as received: `{"type": "noul", "noul": …}` for a yes/no whose `noul` is the probability of yes, `{"type": "choice", "choice": …, "confidence": …, "probabilities": {…}}` for a pick, `{"type": "score", "score": …, "confidence": …, "probabilities": {…}, "legend": {…}}` for a rubric |
| `pydantic_ai.decision.route` | When the request fills a route picked by an earlier request, or the one route left: that route's label |
| `pydantic_ai.decision.confidence` | When field questions were asked and their answers used: each question's confidence after `decision_boolean_threshold`, keyed like the questions — a `list` or mapping option gets its own `field.option` entry given by `provider_details['confidence']` on the response, and a `float` field asking for a probability has no entry |
| `pydantic_ai.decision.route_question` | When the request asks which route to take: that question's key, `route` |
| `pydantic_ai.decision.route_options` | When the request asks which route to take: the offered labels, in order, as a JSON array |
| `pydantic_ai.decision.route_questions` | When routes' fields are asked beside the route question: each route's question keys, by route label |

Route attributes name a route by its **label** — the name the route question offered it under, which is an output type's class name such as `Refund`, `None` for the `None` member of a union, or a tool's or output function's name[^pydantic-logfire-docs] Those are the names `provider_details['route']` carries on the response, whose `choice` and `offered` match the route answer and `pydantic_ai.decision.route_options`[^pydantic-logfire-docs] Questions and answers share keys, keyed by field name, nested models as `outer.inner`, and a `list` or options-to-`bool` mapping as `field.option`; the route question is keyed by `pydantic_ai.decision.route_question`, while a field asked beside it is keyed under its route's label as `Refund.reason`[^pydantic-logfire-docs] Because a label and a nested field name can both contain dots, the docs say to use `pydantic_ai.decision.route_questions` to tell which route a question belongs to rather than splitting its key[^pydantic-logfire-docs]

### When a span exists, and what it records on the way out

A `decide` span is emitted only inside an instrumented model request, and only for a request that is actually sent — with one route left and nothing to fill in, the model takes it without asking and no span appears[^pydantic-logfire-docs] Under [durable execution](pydantic-ai-durable-execution.md) it sits inside the engine's step, task or activity span for the model request, which with Temporal takes the `LogfirePlugin` to carry the trace into the activity[^pydantic-logfire-docs]

The route the model picks is the route the step takes unless the step cannot: a pick less likely than `decision_route_threshold` raises `UnsureRoute`, and a picked route whose fields cannot be filled raises `UnfillableRoute`, both before any request to fill it and both hand-offs[^pydantic-logfire-docs] Either is recorded on the `decide` span that asked the route question as an error with an `exception` event carrying the picked route's label as `pydantic_ai.decision.route`[^pydantic-logfire-docs] With a `FallbackModel` behind the decision model the model behind it takes the step and the model request span ends without an error, so the `decide` span is where the hand-off shows; without one, the model request span records the same error[^pydantic-logfire-docs]

Fields asked beside the route question are asked before it is known which route will be picked, and only the picked route's answers are used — `pydantic_ai.decision.confidence` covers only its questions and the other routes' answers were discarded[^pydantic-logfire-docs] A route picked in one request and filled in the next gets a second `decide` span beside the first, whose `route` is the first span's pick[^pydantic-logfire-docs]

Usage is recorded under `pydantic_ai.decision.usage.*` rather than `gen_ai.usage.*`, and no metrics are recorded for `decide` spans, since the model request span above them already reports the total and a backend that adds usage across spans would count it twice[^pydantic-logfire-docs]

With `include_content=False` the strings go and the numbers stay[^pydantic-logfire-docs]: `pydantic_ai.decision.state` is left out; `pydantic_ai.decision.questions` keeps only each question's `type`; `pydantic_ai.decision.answers` keeps only `type` and numbers — a yes/no's `noul`, a pick's `confidence`, a rubric's `score`, `confidence` and `probabilities` — dropping a pick's `choice` and option-keyed `probabilities` and a rubric's `legend`. The answer to the route question keeps its `choice` and `probabilities`, since its options are route labels, but only under the labels the request offered[^pydantic-logfire-docs] Question keys, route labels and option names are identifiers from your own schema, so they are always recorded, including the options of a run-time `Choices` set[^pydantic-logfire-docs]

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
- The attribute table, the keying rules and the hand-off recording come from the vendor Logfire integration page, which names **no Pydantic AI version and no date** — so the table is reported rather than checked against a version's API reference, and nothing was asked, decided, fallen back or inspected[^pydantic-logfire-docs]
- Evidence class: **Reported**, **Observed** for screenshot labels, **Synthesis** where marked.

## Relationships

- **Traces** the model described in [Jev decision model in Pydantic AI](jev-decision-model.md): `decide` spans exist because a `DecisionModel` sends them.
- **Extends** [Pydantic AI observability](pydantic-ai-observability.md), adding a nested span kind and a content-capture rule beside the run, model-request and cache attributes.
- **Sits beside** the [Logfire Evals workspace](logfire-evals-workspace.md): that surface reviews an experiment, this one inspects a single decision behind a failing case.
- **Depends on** content-capture policy as a configuration decision, since `include_content` decides whether the answers are recoverable at all.
- **Is shaped by** [Pydantic AI instrumentation format](pydantic-ai-instrumentation-format.md), which owns the format version the span is emitted under, the aggregated-usage naming that excludes `decide` usage from `gen_ai.*`, and the metrics rule that gives this span none.

[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"The chat span wasn't enough" (raw lines 59–68) for the missing-probability problem, PRs #8696 (`DecisionModel`) and #8698 (`decide` span) in 2.50.0, the span's contents (questions, answers with probabilities, thresholds, route), and the `include_content` behaviour; §"Seeing it in Live view" (lines 70–82) for the Agent Run tab and its **Details**/**Metrics**/**Raw Data** siblings, the **Classifier output** panel, the 15-question ticket with five shown, per-question probabilities, the expanding rubric and severity levels, **View decision span**, **Raw Data**, the union two-step, and the conversation-view fallback; §"Where else you can use Jev" (line 88) for `DecisionModel` generalizing to other Decisions backends with the panel intact. Attachments inspected for **Observed** labels and values: `assets/support-triage.png` (Agent Run/Details/Metrics/Raw Data tabs, Input with **Show full input**, five answer rows at 62%/60%/60%/62%, the expanded severity rubric at 5%/30%/65% with **Model confidence 0.5**, **Show all 15 questions (5 shown)**, **Thresholds**, **View decision span**, and the 10-field final output) and `assets/route-then-fill.png` (**Initial classification** with `Selected route → final_result_Refund` at 60%, **Fill fields for final_result_Refund** with `duplicate_charge` at 60% and `62% yes`, two **View decision span** links, the 2-field final output, and the collapsed **Conversation**). Evidence class: **Reported**, **Observed** for screenshot labels, **Synthesis** where marked; nothing was executed or opened in Logfire.

[^pydantic-logfire-docs]: Pydantic Docs, "Pydantic Logfire Debugging and Monitoring", <https://pydantic.dev/docs/ai/integrations/logfire/>, `domain: pydantic.dev`, `language: en`, 5,651 words as declared and 5,851 by local `wc -w`, 565 lines, no publication date, author, licence or Pydantic AI version; local capture `raw/integrations/logfire/index.md`, content digest sha256:5ea6a3e0. §"Decision model spans" (raw lines 518–558) for the emission rule (instrumented model request, sent request only, one-route-left shortcut), the `decide` span's attribute table, route labels and their match to `provider_details['route']`, the question/answer keying with `outer.inner` and `field.option`, `route_questions` for dotted labels, `UnsureRoute` and `UnfillableRoute` recorded on the route-question span with `pydantic_ai.decision.route`, the `FallbackModel` case where only the `decide` span shows the hand-off, the second span for a route filled in the next request, the no-metrics and `pydantic_ai.decision.usage.*` rule, the `include_content=False` reduction of state/questions/answers with the route answer exempt, and the always-recorded identifier keys. Evidence class: **Reported** — vendor documentation; no decision request was made and no span inspected.
