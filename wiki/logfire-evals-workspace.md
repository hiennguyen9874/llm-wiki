---
type: Concept
title: Logfire Evals workspace review loop
description: How Logfire's Evals workspace turns an experiment average into evidence — a run overview, a baseline comparison grouped by outcome, and each failing case opening onto the trace that produced it.
tags: [ml, logfire, evaluation, observability]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:05:00Z }
stale_after: 2027-02-04
sources:
  - id: logfire-evals-focus-2026
    resource: ../raw/focus-on-evals-with-logfire/index.md
    scope: ../raw/focus-on-evals-with-logfire/
    kind: article
    revision: sha256:359c59fe65f12c14c4534e34f06554c4480836e136d0b1931066b7d281810250
    title: "Focus on evals with Logfire, not score metering"
---

The Logfire Evals workspace is the read path of an evaluation loop: an experiment's aggregates say where to look, a baseline comparison groups cases by outcome under one primary metric, and every case opens onto the run that produced it — including a link to that run's full trace in Live View[^logfire-evals-focus-2026] It exists because an average tells you that something changed while fixing it needs the cases behind the number[^logfire-evals-focus-2026] The workflow assumes what [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md) measures across vendors — that a score is a record beside the trace that produced it rather than an object in a separate evaluation database — and the source's own thesis is that once that holds, the remaining work is rigour rather than bill arithmetic[^logfire-evals-focus-2026] The UI vocabulary below is **Observed** in the article's three screenshots; the steps are its **Reported** prose, and no Logfire project was opened here.

## Start with the run

The entry path is **AI Evaluations** → **Experiments** → **Review results**[^logfire-evals-focus-2026] The overview reports case completion, assertion pass rate, task errors, average duration, and each evaluator's aggregate result with a **Review cases** step beside it[^logfire-evals-focus-2026] In the captured run — `candidate-action-policy-v2` against the task `customer-support-copilot` — that reads as 6/6 cases completed, assertions 94% (17 of 18 passed), 0 task errors, an 810 ms average across the six completed cases, and three assertion evaluators at 83% (`ActionCoverage`), 100% (`ConciseResponse`) and 100% (`NoOverpromising`)[^logfire-evals-focus-2026] The author's instruction is to use those aggregates to choose what to inspect first, because a high average can still hide one important failure[^logfire-evals-focus-2026]

## Compare one change

**Compare runs** takes an earlier or trusted run as the baseline; on **Cases** you choose the evaluator that should be the **Primary metric**, say whether higher or lower is better, keep **Group by: Outcome** so errors and regressions sit ahead of unchanged cases, and add supporting metrics when one score cannot explain the whole result[^logfire-evals-focus-2026] The captured comparison holds `ActionCoverage` as primary across three metrics: the Error group shows cases marked *Not comparable*, and the Improved group shows per-evaluator transitions, `Fail → Pass` on the primary metric with `Pass → Pass` on the two supporting ones[^logfire-evals-focus-2026]

**Synthesis:** group-by-outcome is what makes the step work. It converts a diff into a triage queue ordered by what needs attention rather than by score, so the cases sharing a failure mode are adjacent whether or not their numbers are.

## Follow a result to its trace

Opening a case shows its input, output and evaluator results together, with the case list filtered by All, Needs review, Passed, Failed, Scored, Errors or Not evaluated[^logfire-evals-focus-2026] The captured case `refund_request` shows a serialized output (`route`, `urgency`, `reply`), the failed `ActionCoverage` assertion marked as the selected evaluator, `NoOverpromising` and `ConciseResponse` passing, and a 601 ms duration[^logfire-evals-focus-2026] When the output does not explain the failure, **Open trace in Live View** shows the prompt, model calls, tool calls and exceptions that produced it[^logfire-evals-focus-2026] That link is the property this page's opening claim rests on: the score and the run it judges are one object, not two systems joined by a copied id.

## Then change one variable

The closing step of the loop is to change one variable, run the same dataset again, and compare the new result against the previous run[^logfire-evals-focus-2026] The source points to Logfire's datasets-and-experiments documentation for dataset creation, case review and troubleshooting; that page was read as a link, not followed[^logfire-evals-focus-2026]

**Synthesis:** this is the hosted implementation of the offline half of [LLM evaluation modes](llm-eval-modes.md) — a dataset, an experiment per run, and a baseline for the "did this change help" question — with [Pydantic Evals](pydantic-evals.md) as the code-first path that produces the same datasets and reports.

## Limits

- The source is Pydantic's own article (Bill Easton, published 2026-08-04, 806 words as declared), day two of a five-post series that starts from a piece titled "Score freely" and argues against a competitor's per-score pricing; it therefore selects the workflow that makes its own cost argument[^logfire-evals-focus-2026]
- Nothing was exercised: no Logfire account, project, dataset, experiment or trace, and no Live View link followed. The three screenshots were inspected statically, so the labels above are what one capture renders, not a documented contract — a different account may show different tabs or metrics[^logfire-evals-focus-2026]
- The captured example is a support-triage agent (`agent-dogfood/support-response-quality`, run `candidate-action-policy-v2`, timestamped "Jul 29" with no year), so evaluator names, task naming and the metric count are that example's, not defaults[^logfire-evals-focus-2026]
- No Logfire or Pydantic AI version is named, and no SDK call, config key or API is described: the article is UI prose plus screenshots. The premise that evaluation results are OpenTelemetry events attached to their originating traces is the vendor's own statement, unverified here[^logfire-evals-focus-2026]
- Status is `draft` under the `pydantic-ai` domain rule — the workflow claims rest on a single vendor article that names no version — not because a section is missing.
- Evidence class: **Reported** for the procedure and its rationale; **Observed** only where a screenshot is named.

## Relationships

- **Reads what** [Pydantic Evals](pydantic-evals.md) **writes**: datasets, evaluators and evaluation reports are the code-first objects this workspace renders and compares.
- **Depends on** [Pydantic AI observability](pydantic-ai-observability.md): the trace behind **Open trace in Live View** is the same OpenTelemetry data the app already emits.
- **Implements the offline layer of** [LLM evaluation modes](llm-eval-modes.md), adding shared case review and experiment history on top of a dataset run.
- **Assumes the meter** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md) **compares**: score results stored as ordinary records carry no separate score charge, which is what makes reviewing every case affordable.
- **Sits downstream of** [Logfire agent optimization](logfire-agent-optimization.md), where the optimizer reads the badly scoring runs this workspace pins down to a case and a trace.

[^logfire-evals-focus-2026]: Bill Easton, "Focus on evals with Logfire, not score metering", Pydantic, published 2026-08-04, 806 words as declared; local capture `raw/focus-on-evals-with-logfire/index.md`, content digest sha256:359c59fe. §"No score meter" (lines 28–32) for evaluation results as OpenTelemetry events attached to their originating traces; §"From scores to evidence" (lines 64–66) for the claim that fixing a change needs the cases behind the number; §"Start with the run" (lines 68–74) for the AI Evaluations → Experiments → Review results path and the overview signals; §"Compare one change" (lines 76–80) for Compare runs, Primary metric, higher-or-lower direction, Group by: Outcome and supporting metrics; §"Follow a result to its trace" (lines 82–88) for the case view and **Open trace in Live View**; §"Focus on the eval" (lines 90–94) for change-one-variable, rerun and compare. Screenshots inspected: `raw/focus-on-evals-with-logfire/assets/experiment-overview.webp` (run `candidate-action-policy-v2`, 6/6 cases, 94% assertions with 17 of 18 passed, 0 task errors, 810 ms, three evaluators at 83/100/100%); `assets/comparison-cases.webp` (`ActionCoverage` primary across three metrics, Group by Outcome, two Error cases marked *Not comparable*, two Improved cases showing `Fail → Pass`); `assets/case-review.webp` (case `refund_request`, output fields `route`/`urgency`/`reply`, `ActionCoverage` failing and selected, two passing evaluators, 601 ms, the case-list filters). Evidence class: **Reported** for the procedure, **Observed** for the screenshot details — no workspace was opened, no experiment run, and the linked datasets-and-experiments documentation was read as a link only.
