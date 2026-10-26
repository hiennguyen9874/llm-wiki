---
type: Concept
title: Logfire agent optimization
description: Pydantic Logfire's optimize-and-ship surface — a trace-grounded optimizer, managed agent configuration with versioning, targeting and label-based rollback, evaluation billed as observations, and the MCP/SQL trace queries — as described by Pydantic itself.
tags: [ml, pydantic-ai, logfire, optimization]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:15:00Z }
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
  - id: logfire-evals-focus-2026
    resource: ../raw/focus-on-evals-with-logfire/index.md
    scope: ../raw/focus-on-evals-with-logfire/
    kind: article
    revision: sha256:359c59fe65f12c14c4534e34f06554c4480836e136d0b1931066b7d281810250
    title: "Focus on evals with Logfire, not score metering"
  - id: sanchez-self-improving-2026
    resource: ../raw/when-agents-improve-agents/index.md
    scope: ../raw/when-agents-improve-agents/
    kind: article
    revision: sha256:3a72d59c7e98809d43fbf8b36a3fb77a26fa72444fb698a84bf5eb2229d9f2b2
    title: "When agents improve agents: loops that improve themselves"
---

Logfire's optimization surface is the write half of the agent loop: an optimizer that reads the runs that scored badly together with the thousands around them, proposes one evidence-cited change, and managed configuration that ships an agent's instructions, model, settings and tool definitions as versioned config with targeting and weighted rollout, where rollback is moving a label[^pydantic-optimization-2026] Diagnosis, proposal and fix share one OpenTelemetry-native trace — browser, services, databases, model and tool calls, plus evaluation scores on the same timeline — so the platform can also report that the agent was never the fault[^pydantic-optimization-2026] This is Pydantic's own account of its own product, and it names no Pydantic AI version, which is why this page is `draft`.

## Managed configuration is the deploy mechanism

The change is shipped as configuration rather than as a code deploy. An agent's instructions, model, settings and tool definitions are described as living in versioned config with cohort targeting and weighted rollouts; rollback is moving a label[^pydantic-optimization-2026]

A later Pydantic article gives the mechanism a name: the versioned object is a **managed variable**, the prompt's is named `prompt__<slug_with_underscores>`, and a `production` label moves between immutable numbered versions so that saving a draft cannot change what production serves[^pydantic-prompt-tools-2026] That article notes saving and promoting both require the `write_variables` permission, so editing and releasing are the same privilege and a reviewer gate is the customer's to build[^pydantic-prompt-tools-2026]

**Synthesis:** those four versioned items map onto the runtime surface Pydantic AI's agent already exposes — instructions, model choice and model settings are the knobs described in [Pydantic AI run controls](pydantic-ai-run-controls.md), and tool definitions belong to the [capability](pydantic-ai-capability-primitive.md) that registers them. The source does not make that connection or state how managed config is represented, fetched or applied to a running `Agent`, so the mapping is inferred, not documented.

## What the optimizer reads and proposes

The optimizer is described as reading the badly scoring runs and their surrounding volume, finding the pattern, and proposing one change with the evidence cited[^pydantic-optimization-2026] Its claimed differentiator is upstream of the fix: because the trace spans retrieval, upstream services and databases, the platform can distinguish an agent fault from a slow retrieval, a rate-limited upstream or a database timeout showing up as a bad answer[^pydantic-optimization-2026] The slogan test the article applies to everyone applies here too — diagnose, propose, ship and roll back over the whole trace — and the article asserts Logfire is the platform that performs all four[^pydantic-optimization-2026]

## The GEPA recipe and the human in the loop

A third account gives the optimizer's loop a name and states its stopping condition. The three surfaces are managed prompts (change instructions without a deploy, versioned so a rollback is a label move), online evaluations (evaluators run in the background on live sampled traffic, so the grade comes from production rather than a test set that stopped being representative the day it was written), and **GEPA** — the model reflects on its eval failures, proposes a better prompt, and the version that measurably wins is kept[^sanchez-self-improving-2026] The vendor then draws its own boundary, which is the most useful sentence in that account: the optimizer already reads eval failures, proposes a prompt and can run on a schedule rather than waiting to be asked, but it will not apply the change on its own; closing the loop without a person is described as near-horizon, with what ships being every piece needed to assemble the loop by hand[^sanchez-self-improving-2026]

That is a narrower claim than "closes the loop", and it is consistent with reported rollout machinery rather than contradicted by it: label movement needs the `write_variables` privilege, so something holding that key could promote a version automatically, and the product's own position is that the decision to spend that privilege stays human[^sanchez-self-improving-2026] **Synthesis:** those two statements can both hold — the platform is technically capable of unattended promotion and the vendor has chosen not to offer it — but no capture states which parts are permission-gated versus unimplemented, so the practical boundary is unverified.

The same account names the piece it says is missing on the agent side: a check that fires when the loop would otherwise go idle and decides continue or done, built by asking a model what the goal was, whether it was implemented, whether it was verified, whether the verification was checked, and whether the outside world changed[^sanchez-self-improving-2026] That belongs to [Self-improving agent loops](self-improving-agent-loops.md).

## How a promoted prompt reaches the run

The delivery path is the part [prompt management tools](prompt-management-tools.md) scores other vendors against, and here it is explicit. Applications read the value through `pip install 'logfire[variables]'` or the `@pydantic/logfire-node` package; an instrumented resolution emits a span, and using the resolved value as a context manager sets baggage, so the label and version that served a run land on that run's trace next to its cost, latency and outcome[^pydantic-prompt-tools-2026] If Logfire is unreachable the SDK returns the default that shipped in the code, which is the middle path that article recommends as the default shape: the repository remains the source of truth for what happens on a bad day[^pydantic-prompt-tools-2026]

Scenarios are saved test cases that sweep a dataset, up to 500 cases per batch, and a batch run calls the gateway once per case, so prompt testing spends gateway budget rather than record allowance[^pydantic-prompt-tools-2026]

## Evaluation billed as observations

Evaluation runs online and offline on the traces already emitted, with no separate per-score meter: a score is treated as an observation billed at the same flat rate as any span, with a free tier[^pydantic-optimization-2026] The article puts the contrast at three million scored runs a month costing roughly $4,400 in score charges on a competitor against a few dollars here, but states Logfire's rates only in passing — a flat $2 per million records inside the Arize comparison, and a ten-million-record free tier inside the closing promotional block[^pydantic-optimization-2026] See [agent optimization platforms](agent-optimization-platforms.md) for the pricing table this sits in.

A later Pydantic article supplies the arithmetic the first one gestures at[^logfire-evals-focus-2026] Braintrust Pro meters scores at $1.50 per thousand after its first fifty thousand, on top of processed-data and retention charges, while Logfire bills an evaluation result as an OpenTelemetry event on its originating trace, at the same $2 per million records after ten million[^logfire-evals-focus-2026] Past the inclusive allowances, a million spans retained ninety days plus a million score results comes to about $1,504 on Braintrust and $4 on Logfire, and the same article's nightly MATH-sized workflow puts one agent at 1.5M scores a month ($2,175 on Braintrust, no separate Logfire score fee) and fifty agents at 75M ($112,425)[^logfire-evals-focus-2026] Its practical advice follows from that asymmetry: run deterministic checks on every case and sample the LLM judges when their model cost or latency warrants it[^logfire-evals-focus-2026] The review path from those scores to the failing case and its trace is [Logfire Evals workspace review loop](logfire-evals-workspace.md).

## Query surface and framework coverage

A coding agent can query the complete trace over an MCP server in PostgreSQL-compatible SQL and act on what it finds[^pydantic-optimization-2026]; the server's tool surface, setup routes and limits are in [Logfire MCP server](logfire-mcp-server.md). Any framework that emits OpenTelemetry appears in Live and Explore, with recognized agent and model telemetry promoted into purpose-built views; Pydantic AI is stated to record the richest fields, and a published framework support matrix shows the experience for other frameworks[^pydantic-optimization-2026] This is the same SQL-and-MCP access described from an independent guest post in [Pydantic AI observability](pydantic-ai-observability.md).

## Limits

- The delivery detail above comes from a second Pydantic article (2026-08-26) that ranks Logfire first again; the SDK call, span, baggage and fallback behaviour are documented prose, and no package was installed or resolution executed[^pydantic-prompt-tools-2026]
- The vendor concedes against itself that this prompt-workflow surface is younger than Langfuse's or LangSmith's, that promotion shares `write_variables` with editing, and that self-hosting stays Enterprise-only[^pydantic-prompt-tools-2026]
- The source is Pydantic's own comparison article and ranks its own product first; the accompanying claim that nothing in Logfire is being absorbed or sunset is the vendor's, offered in the same year the article reports rivals being acquired[^pydantic-optimization-2026]
- No Pydantic AI version, Logfire SDK call, config schema, CLI or docs reference is given for managed configuration, the optimizer or the rollout mechanics; the whole mechanism is prose[^pydantic-optimization-2026]
- How the optimizer selects runs, how many it reads, what it costs, and what a proposal looks like are all unspecified[^pydantic-optimization-2026]
- Pricing appears only incidentally, is dated 2026-07-29, and was not checked against Logfire's price page[^pydantic-optimization-2026] A later Pydantic article (2026-08-26, compiled as [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md)) restates the same flat-record model with current figures — 10M records on both Personal and Team, $49/month Team then $2 per million, Growth at $249 with up to 90-day retention, evaluation records sharing the store and queried in PostgreSQL-compatible SQL, and no separate score fee — which dates the claim rather than verifying it, since the publisher is the same[^pydantic-optimization-2026]
- The "evaluation billed as observations" wording here should be read against the later articles' more careful phrasing: evaluation *records* count toward the record allowance, and model and judge inference is billed separately, which this page's flat-rate sentence leaves implicit[^pydantic-optimization-2026] The 2026-08-04 companion article goes further and states that model execution is outside both vendors' plans, with the scores-versus-records arithmetic worked through[^logfire-evals-focus-2026]
- The GEPA name, the online-evaluation placement and the won't-apply-on-its-own boundary come from a third Pydantic article (2026-07-31) that also names no version and gives GEPA no algorithm, cost or win threshold, so "measurably wins" is undefined here[^sanchez-self-improving-2026]
- Nothing was trialled: no account, agent, trace or rollout was exercised in this ingest[^pydantic-optimization-2026]
- Status is `draft` under the `pydantic-ai` domain rule — behaviour claims rest on vendor material only and name no framework version — and the page is expected to change when the [observability](pydantic-ai-observability.md) docs surface or an independent source covers the same optimizer.
- Evidence class: **Reported**.

## Relationships

- **Extends** [Pydantic AI observability](pydantic-ai-observability.md): that page covers what Pydantic AI emits, this one what Logfire does with it.
- **Operationalizes** [agent optimization platforms](agent-optimization-platforms.md): Logfire is that page's top-ranked example of closing the loop.
- **Delivers through the surface compared in** [prompt management tools](prompt-management-tools.md), which scores the same managed variable against six competitors and names the SDK, span and baggage mechanics.
- **Exposes its trace store through** [Logfire MCP server](logfire-mcp-server.md), which lets a coding agent query the same runs in SQL.
- **Scores with** [Pydantic Evals](pydantic-evals.md): scores attached to the same trace are the eval half the optimizer reads.
- **Hands the score-to-case loop to** [Logfire Evals workspace review loop](logfire-evals-workspace.md), which covers the experiment overview, baseline comparison and trace link that follow a scoring run.
- **Prices the same claim as** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), which restates the flat-record, no-score-fee model with 2026-08-26 figures.
- **Names the optimizer's recipe for** [Self-improving agent loops](self-improving-agent-loops.md): GEPA plus managed prompts plus online evaluations, with promotion kept human.

[^sanchez-self-improving-2026]: David Sanchez, "When agents improve agents: loops that improve themselves", Pydantic, published 2026-07-31T12:00Z; local capture `raw/when-agents-improve-agents/index.md`, content digest sha256:3a72d59c. §"The payoff" (raw lines 69–77) for managed prompts, online evaluations on sampled production traffic, GEPA's reflect-propose-keep loop, the optimizer running on a schedule, and the stated refusal to apply a change without a person; §"The loop supplies its own continue" (lines 17–27) for the idle-edge check. Evidence class: **Reported** — vendor article; no optimizer, prompt version or rollout was exercised.

[^pydantic-optimization-2026]: Bill Easton, "Best AI agent optimization platforms in 2026", Pydantic, published 2026-07-29; local capture `raw/best-ai-agent-optimization-platforms-2026/index.md`, content digest sha256:da4298d9. §"1. Pydantic Logfire: best overall for agent optimization" (lines 33–43) for the whole-trace scope, the optimizer's evidence-cited proposal, the fault-attribution argument, managed configuration and label-based rollback, flat-rate score billing, Live/Explore coverage, the richest-fields claim for Pydantic AI, the MCP SQL surface, the independence claim and the Braintrust concession; §"3. Arize AX" (lines 53–59) for the flat $2 per million records figure; §"Try Pydantic Logfire free" (lines 119–125) for the ten-million-record free tier. Evidence class: **Reported** — vendor material; no account, trace or rollout was exercised.

[^pydantic-prompt-tools-2026]: Bill Easton, "Best Prompt Management Tools 2026", Pydantic, published 2026-08-26, 3,421 words as declared; local capture `raw/best-prompt-management-tools/index.md`, content digest sha256:db5ee87b. §"1. Pydantic Logfire: best prompt management tool overall" (lines 44–52) for immutable numbered versions, "A version freezes the template, nothing else", the `prompt__<slug_with_underscores>` managed variable and `production` label, promotion without redeploy, `targeting_key` stickiness, the `logfire[variables]` and `@pydantic/logfire-node` packages, the resolution span and baggage, the code-shipped default when unreachable, Scenarios at 500 cases per batch with one gateway call per case, the shared `write_variables` privilege and the Enterprise-only self-hosting; §"Comparison at a glance" (lines 102–114) for the Personal 10M-record tier and the $49 Team entry. Evidence class: **Reported** — vendor material; no package installed, no resolution executed.

[^logfire-evals-focus-2026]: Bill Easton, "Focus on evals with Logfire, not score metering", Pydantic, published 2026-08-04, 806 words as declared; local capture `raw/focus-on-evals-with-logfire/index.md`, content digest sha256:359c59fe. §"Three meters" (lines 14–26) for Braintrust's per-score, per-gigabyte and retention charges; §"No score meter" (lines 28–32) for evaluation results as events on their originating traces and the $2-per-million-record rate after ten million; §"Online: score every production trace" (lines 34–48) for the $1,504-versus-$4 marginal comparison and the both-plans-$249 footnote; §"Offline: repeat the full benchmark" (lines 50–62) for the 50,000-records-per-run MATH instance and the 1.5M/15M/75M portfolio table; §"Focus on the eval" (lines 90–94) for deterministic checks on every case with sampled judges. Evidence class: **Reported** — vendor material; no account, bill or benchmark was measured.
