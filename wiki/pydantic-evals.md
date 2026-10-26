---
type: Concept
title: Pydantic Evals
description: Pydantic's code-first evaluation library — deterministic agentic evaluators over local OpenTelemetry spans, offline datasets, and background online grading.
tags: [ml, pydantic-ai, agents, evaluation]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:04:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

Pydantic Evals is a code-first evaluation library: it grades final outputs and tool-call trajectories against datasets, or against sampled live traffic, in Python and in the same test suite as the agent. Its distinguishing feature is a set of deterministic agentic evaluators that never call an LLM — `ToolCorrectness`, `TrajectoryMatch`, `ArgumentCorrectness`, `MaxToolCalls`, `MaxModelRequests` — which read the local OpenTelemetry span tree instead[^dd-v2-tour-2026]

## What the evaluators need

They require the `logfire` SDK installed and configured, but not a Logfire account: `logfire.configure(send_to_logfire=False)` plus `logfire.instrument_pydantic_ai()` captures spans locally[^dd-v2-tour-2026] The dependency is easy to miss in the failure direction:

> With the `logfire.configure(...)` and `instrument_pydantic_ai()` lines removed, the same dataset scored `TrajectoryMatch: 0.000` and failed both assertions, with no exception.

A pipeline that runs green-looking but scores zero usually means no spans were captured[^dd-v2-tour-2026]

## Offline grading

A `Dataset` holds named cases and a list of evaluators; `dataset.evaluate_sync(handle)` returns a report. In V2 `Dataset` requires a keyword-only `name=`, and v2.57.0 added `dataset_name` to `EvaluationReport`[^dd-v2-tour-2026]

Scoring semantics matter before thresholds are set: `TrajectoryMatch(order='in_order')` computes F1 from the longest common subsequence — precision is LCS divided by actual length, recall is LCS divided by expected length. The docs' worked example, expected `['a', 'b', 'c']` against actual `['a', 'x', 'b']`, gives LCS 2, so precision and recall are 2/3 and F1 is about 0.667: extra calls lower the score without zeroing it, while `'exact'` is all or nothing[^dd-v2-tour-2026]

## Online grading

The `OnlineEvaluation` capability grades runs in the background after each completed run. It takes evaluators and an `OnlineEvalConfig` with a sampling rate, and emits `gen_ai.evaluation.result` OpenTelemetry events under `gen_ai.evaluation.target`, which is set to the agent's `name`[^dd-v2-tour-2026] Results therefore land in the same [observability](pydantic-ai-observability.md) pipeline as traces.

## Blind spot

Native provider tools run on the provider's side and produce no local spans, so the agentic evaluators cannot see them. A tool-correctness score says nothing about calls the provider executed itself[^dd-v2-tour-2026]

## Limits

- The author's run used `TestModel`, which calls every registered tool, so the reported `TrajectoryMatch: 1.00` was trivially earned; a real model "has to earn that score"[^dd-v2-tour-2026]
- No threshold calibration, dataset size, cost, or comparison against Braintrust, Promptfoo or DeepEval is covered; the source only links its own comparison post.
- The unconfigured-Logfire failure mode was observed by the author, not reproduced here.
- Evidence class: **Reported**.

## Relationships

- **Is graded through** [Pydantic AI observability](pydantic-ai-observability.md): both depend on the same local OpenTelemetry spans.
- **Attaches as** a [capability](pydantic-ai-capability-primitive.md) in its online form.
- **Complements** [Pydantic AI run controls](pydantic-ai-run-controls.md): one bounds a run, the other scores how it went.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Pydantic Evals: grade the trajectory, offline and online" (raw lines 482–559) for the evaluator list, the Logfire requirement and the zero-score failure mode, `Dataset` naming, LCS scoring, `OnlineEvaluation` events and sampling, and the native-tool blind spot. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — the author ran this against `TestModel`; no eval suite was executed in this ingest.
