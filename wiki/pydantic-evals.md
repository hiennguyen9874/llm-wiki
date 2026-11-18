---
type: Concept
title: Pydantic Evals
description: Pydantic's code-first evaluation library — deterministic agentic evaluators over local OpenTelemetry spans, offline datasets, and background online grading.
tags: [ml, pydantic-ai, agents, evaluation]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:49:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
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
  - id: pydantic-production-docs
    resource: ../raw/production/index.md
    scope: ../raw/production/
    kind: documentation
    revision: sha256:37a18c9b248bb378966b18d9fd89501679796e9a5548f1b240bfa3095cf36e42
    title: "Going to Production"
---

Pydantic Evals is a code-first evaluation library: it grades final outputs and tool-call trajectories against datasets, or against sampled live traffic, in Python and in the same test suite as the agent. Its distinguishing feature is a set of deterministic agentic evaluators that never call an LLM — `ToolCorrectness`, `TrajectoryMatch`, `ArgumentCorrectness`, `MaxToolCalls`, `MaxModelRequests` — which read the local OpenTelemetry span tree instead[^dd-v2-tour-2026]

## What the evaluators need

They require the `logfire` SDK installed and configured, but not a Logfire account: `logfire.configure(send_to_logfire=False)` plus `logfire.instrument_pydantic_ai()` captures spans locally[^dd-v2-tour-2026] The dependency is easy to miss in the failure direction:

> With the `logfire.configure(...)` and `instrument_pydantic_ai()` lines removed, the same dataset scored `TrajectoryMatch: 0.000` and failed both assertions, with no exception.

A pipeline that runs green-looking but scores zero usually means no spans were captured[^dd-v2-tour-2026]

## Offline grading

A `Dataset` holds named cases and a list of evaluators; `dataset.evaluate_sync(handle)` returns a report. In V2 `Dataset` requires a keyword-only `name=`, and v2.57.0 added `dataset_name` to `EvaluationReport`[^dd-v2-tour-2026]

Scoring semantics matter before thresholds are set: `TrajectoryMatch(order='in_order')` computes F1 from the longest common subsequence — precision is LCS divided by actual length, recall is LCS divided by expected length. The docs' worked example, expected `['a', 'b', 'c']` against actual `['a', 'x', 'b']`, gives LCS 2, so precision and recall are 2/3 and F1 is about 0.667: extra calls lower the score without zeroing it, while `'exact'` is all or nothing[^dd-v2-tour-2026]

## Built-in LLM judges

The evaluator list also accepts two shipped judge evaluators: `LLMJudge` takes a rubric, a model, model settings and an assertion name, while `GEval` takes criteria, evaluation steps and a `score_range` and returns an integer level[^jev-evals-2026] Neither asks the judge for an explanation, and each makes its own model call, so two built-in checks cost two requests per reply[^jev-evals-2026] The extension point underneath them is ordinary Python: an `Evaluator` subclass receives `ctx.inputs` and `ctx.output` and returns a dict in which strings become labels, numbers become scores and booleans become assertions[^jev-evals-2026]

**Synthesis:** this is the layer the deterministic evaluators above cannot cover. Tool correctness and trajectory shape can be checked without a model; "does this reply follow the supplied policy" cannot, so a real suite mixes both — and the opening claim about evaluators that never call an LLM describes only the deterministic set.

## Online grading

The `OnlineEvaluation` capability grades runs in the background after each completed run. It takes evaluators and an `OnlineEvalConfig` with a sampling rate, and emits `gen_ai.evaluation.result` OpenTelemetry events under `gen_ai.evaluation.target`, which is set to the agent's `name`[^dd-v2-tour-2026] Results therefore land in the same [observability](pydantic-ai-observability.md) pipeline as traces. The vendor's later evals article states the storage from the platform side: an evaluation result is an OpenTelemetry event attached to its originating trace, billed with the same records as other telemetry and carrying no separate score fee[^logfire-evals-focus-2026]

Three operational rules decide whether online grading survives production[^pydantic-production-docs]:

- **The background work lives in your process, not on a job queue.** There is nothing to drain after the process exits, so the shutdown path has to wait.
- **Sample, and cap the concurrency** of expensive evaluators such as an LLM judge; otherwise the grader scales with traffic.
- **Await `wait_for_evaluations()` on shutdown** so pending evaluations finish instead of being killed mid-score.

## Rolling out a change

Evaluation is the comparison step of a rollout rather than only a check: run the same dataset against the changed prompt or model and compare the reports, and send experiments to Logfire so every run sits side by side with the trace of its case[^pydantic-production-docs] Three vendor features move the change out of code — a Harness `ManagedPrompt` backs instructions with a Logfire-managed prompt you version, label and roll out without a redeploy; an [agent spec](pydantic-ai-agent-specs.md) keeps model, instructions and capabilities in YAML or JSON; and the Harness `TrajectoryJudge` reviews a long run every few model requests while it happens[^pydantic-production-docs] The same features are listed as names in the [capability catalog](pydantic-ai-capability-catalog.md), which is where their package attribution lives.

## Blind spot

Native provider tools run on the provider's side and produce no local spans, so the agentic evaluators cannot see them. A tool-correctness score says nothing about calls the provider executed itself[^dd-v2-tour-2026]

## Limits

- The author's run used `TestModel`, which calls every registered tool, so the reported `TrajectoryMatch: 1.00` was trivially earned; a real model "has to earn that score"[^dd-v2-tour-2026]
- A report is only as useful as the route from it to the failing run. The hosted review path — experiment overview, baseline comparison grouped by outcome, case view, and **Open trace in Live View** — is described in [Logfire Evals workspace review loop](logfire-evals-workspace.md), which is UI prose and three screenshots rather than library behaviour[^logfire-evals-focus-2026]
- No threshold calibration, dataset size, cost, or benchmark appears in that source. The pricing and hosting comparison it lacked now lives in [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), which prices Pydantic Evals' hosted path — dataset cases kept in the web UI or in code, hosted cases preserved from a production trace with the source link retained, candidate-versus-baseline review, and evaluation records billed on the same record allowance as traces with no separate score fee[^pydantic-eval-tools-2026] That page is a Pydantic article too, so the cost case is the vendor's own[^pydantic-eval-tools-2026]
- The library's licence boundary is stated only from the vendor's table: the Logfire SDKs are MIT, and the local-run claim is that Pydantic Evals and DeepEval both evaluate at no cost[^pydantic-eval-tools-2026] No licence file or package metadata was opened here.
- The unconfigured-Logfire failure mode was observed by the author, not reproduced here.
- The three online-grading rules and the rollout paragraph come from the vendor's production page, which names no version or date; `wait_for_evaluations()` was not called, no sampling rate or concurrency figure is given, and `ManagedPrompt` and `TrajectoryJudge` are names with no configuration, pricing or prompt behaviour described in this capture[^pydantic-production-docs]
- Evidence class: **Reported**.

## Relationships

- **Complements** [Pydantic AI AgentEnv evaluation](pydantic-ai-agentenv-evaluation.md): **Synthesis**, seeded environment outcome verification is a separate evaluation route, not a documented use of this library.
- **Accepts judges from** [Jev structured scoring judge](jev-structured-scoring-judge.md), whose custom evaluator groups several questions into one judge request while the built-in `LLMJudge` and `GEval` spend one request per check.
- **Is graded through** [Pydantic AI observability](pydantic-ai-observability.md): both depend on the same local OpenTelemetry spans.
- **Attaches as** a [capability](pydantic-ai-capability-primitive.md) in its online form.
- **Closes the loop from** [agent observability requirements](agent-observability-requirements.md), whose Vstrom-sourced flywheel pitches captured production traces as the dataset an evaluation suite is built from.
- **Complements** [Pydantic AI run controls](pydantic-ai-run-controls.md): one bounds a run, the other scores how it went.
- **Is priced and placed against rivals in** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), and its offline/online split is the worked implementation of [LLM evaluation modes](llm-eval-modes.md).
- **Scores retrieval as well as answers in** [RAG retrieval pipeline design](rag-retrieval-pipeline.md), whose guide names this library for tracking whether the right chunks are retrieved, not only whether the reply is good.
- **Is reviewed through** [Logfire Evals workspace review loop](logfire-evals-workspace.md) once its reports reach the hosted platform, where each score opens onto the trace that produced it.

[^pydantic-production-docs]: Pydantic Docs, "Going to Production", <https://pydantic.dev/docs/ai/production/>; local capture `raw/production/index.md`, content digest sha256:37a18c9b, 3,774 words as declared and 3,836 by `wc -w`, 335 lines, no publication date, author, licence or Pydantic AI version. §"How do I test and evaluate changes?" (raw lines 259–289) for `TestModel`/`FunctionModel`, `Agent.override` and `ALLOW_MODEL_REQUESTS = False` with `defer_model_check=True`, the offline-versus-online split, trajectory evaluators, the dataset comparison and Logfire experiment upload, `ManagedPrompt` and agent specs, the in-process background evaluation work with sampling, a concurrency cap and `wait_for_evaluations()`, and `TrajectoryJudge`. Evidence class: **Reported** — vendor documentation; no eval suite, experiment or shutdown path was exercised.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Pydantic Evals: grade the trajectory, offline and online" (raw lines 482–559) for the evaluator list, the Logfire requirement and the zero-score failure mode, `Dataset` naming, LCS scoring, `OnlineEvaluation` events and sampling, and the native-tool blind spot. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — the author ran this against `TestModel`; no eval suite was executed in this ingest.

[^pydantic-eval-tools-2026]: Bill Easton, "Best LLM Evaluation Tools 2026", Pydantic, published 2026-08-26 with prices checked 2026-08-26; local capture `raw/best-llm-evaluation-tools/index.md`, content digest sha256:6a9f0092. §"1. Pydantic Logfire: best LLM evaluation tool overall" (lines 54–62) for the hosted-or-in-code datasets, trace-linked hosted cases, candidate-versus-baseline comparison, the Pydantic Evals and TypeScript SDK entry points, and the no-separate-score-fee pricing; §"Comparison at a glance" (lines 115–127) for the SDK-MIT and not-a-meter claims; §"Frequently asked questions" (lines 167–169) for the local-at-no-cost claim about Pydantic Evals and DeepEval. Evidence class: **Reported** — vendor material; no library was installed and no eval run was costed.

[^jev-evals-2026]: David Montague, "Cheap AI scoring with Jev and Pydantic Evals", Pydantic, published 2026-09-23T16:00Z, 2,416 words as declared; local capture `raw/jev-evals/index.md`, content digest sha256:c34f4321. §"Return labels and scores to Pydantic Evals" (lines 106–154) for the `Evaluator` subclass receiving `EvaluatorContext` and returning an `EvaluatorOutput` dict whose strings become labels, numbers scores and booleans assertions; §"Use the built-in judges for simpler checks" (lines 156–199) for `LLMJudge`'s rubric/model/model_settings/assertion arguments, `GEval`'s criteria, evaluation_steps, score_range and evaluation_name, the absence of an explanation request, and the note that each evaluator makes its own model call so two checks use two requests per reply. Evidence class: **Reported** — vendor article; no evaluator was instantiated or run in this ingest.

[^logfire-evals-focus-2026]: Bill Easton, "Focus on evals with Logfire, not score metering", Pydantic, published 2026-08-04, 806 words as declared; local capture `raw/focus-on-evals-with-logfire/index.md`, content digest sha256:359c59fe. §"No score meter" (lines 28–32) for evaluation results stored as OpenTelemetry events attached to their originating traces and billed as ordinary records; §"From scores to evidence" (lines 64–88) for the experiment-overview, comparison and case-to-trace review path summarised in the limits above. Evidence class: **Reported** — vendor material; no evaluation was run, and the workspace steps were read as prose plus screenshots.
