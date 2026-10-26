---
type: Concept
title: Jev structured scoring judge
description: TypeSafe Jev as a cheap structured judge inside Pydantic Evals — questions described as Python output types, one request for several judgments, probability and threshold semantics, and the measured cost of scoring a million replies.
tags: [ml, pydantic-ai, evaluation, judging, cost]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:50:00Z }
stale_after: 2027-03-23
sources:
  - id: jev-evals-2026
    resource: ../raw/jev-evals/index.md
    scope: ../raw/jev-evals/
    kind: article
    revision: sha256:c34f4321a3b5786600eeefff3fc14216036d1f0d9c3b4bfba2686aca93241c0a
    title: "Cheap AI scoring with Jev and Pydantic Evals"
  - id: jev-gateway-2026
    resource: ../raw/jev-pydantic-ai-gateway/index.md
    scope: ../raw/jev-pydantic-ai-gateway/
    kind: article
    revision: sha256:cd20eca277244de9ee4f24d189acc0b1cde2b11ee3bc5796fc8422bae7e11c6d
    title: "TypeSafe Jev in Pydantic AI Gateway"
  - id: jev-live-view-2026
    resource: ../raw/jev-pydantic-ai-live-view/index.md
    scope: ../raw/jev-pydantic-ai-live-view/
    kind: article
    revision: sha256:288f23ddf22c009f4ada93b87fcc6526a089ea7ece6d6c5a229a7dd98e2636f0
    title: "Pydantic AI agents on Jev, traced in Logfire"
---

TypeSafe's **Jev** is a structured-decision model rather than a chat model: it takes material plus a set of typed questions and returns one answer and one probability per question rather than prose[^jev-evals-2026] Its published input price is $0.042 per million tokens with no output-token charge, and Pydantic AI 2.46.0 can run it as an agent whose `output_type` *is* the question set — described string enums, an ordered `IntEnum` rubric, and a bounded float for a yes/no probability[^jev-evals-2026] Wrapped in a Pydantic Evals evaluator, those answers become labels, scores and assertions, which — against the per-score prices recorded in [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md) — is the cheapest scoring path this wiki documents for a large volume of responses (**Synthesis**)[^jev-evals-2026]

## What the model returns

Three question shapes appear in the worked example: a `Choice` (a categorical label), a `Score` (an ordered rubric), and a `Noul` (TypeSafe's yes/no probability)[^jev-evals-2026] One TypeSafe request may carry all three, since multiple questions share the input state — but their definitions still contribute input tokens[^jev-evals-2026]

The rubric answer arrives twice, which is easy to miss: Jev computes the `Score` as a probability-weighted average of its levels, Pydantic AI returns the **nearest** `IntEnum` member in `result.output`, and the fractional value is preserved in `result.output.provider_details["scores"]`[^jev-evals-2026] The example reads the fractional score and divides by the maximum level to put it on a zero-to-one scale, so a reply can score 0.49 while its enum says "level 1"[^jev-evals-2026]

Confidence is not a single universal number, and the two shapes disagree:

- For an assertion, confidence is measured **relative to the threshold**. `TypeSafeModelSettings(typesafe_boolean_threshold=0.9)` requires a yes-probability of at least 0.9 instead of the default 0.5, and because the confidence is defined against that threshold, changing it also changes the confidence reported for the same answer[^jev-evals-2026]
- For a bounded float field, the probability itself is the output and there is no separate confidence entry, so no threshold is involved[^jev-evals-2026]

A low confidence means the answer distribution is not concentrated: the password-request reply drew completeness probabilities of 0.38, 0.26 and 0.36 over the three levels, giving a normalized 0.490 — a middle score produced by disagreement, not by a middling judgement[^jev-evals-2026]

## Describing the questions in Python types

The string enum names the policy categories, the `IntEnum` defines the rubric from zero with a docstring per level, and the float field carries the secret-solicitation probability[^jev-evals-2026] Two details make the schema work:

- Member docstrings only reach Jev through the [`UseEnumMemberDocstrings`](https://pydantic.dev/docs/ai/tools-toolsets/tools/#enum-options) mix-in; plain enums do not include them, and the numeric rubric depends on them for its level descriptions[^jev-evals-2026]
- The judge model is pinned — `Agent("typesafe:jev-1.13.0", output_type=ReplyReview, defer_model_check=True)` — because a moving alias would change the judge between experiments, and `defer_model_check=True` keeps imports and `--help` working without API keys[^jev-evals-2026]

Pydantic AI 2.46.0 also adds `Choices`, which builds a described option set at runtime without declaring an enum class, for categories that are not fixed in source[^jev-evals-2026] A proposed `Classifier` evaluator was still an open pull request at the time of writing, and none of the example code depends on it[^jev-evals-2026]

The same mapping also runs an agent whose deliverable *is* the decision rather than a score on someone else's: from Pydantic AI 2.50.0 `DecisionModel` is the base class for any model speaking TypeSafe's Decisions protocol and `TypeSafeModel` is a thin adapter over it, so a `Ticket` output type with `urgent: bool` and a four-value `area` literal is one request answering both fields[^jev-live-view-2026] [Jev decision model in Pydantic AI](jev-decision-model.md) covers that role, including the rule this page never hits — for a decision model the prompt must carry only the material, because a question written into it is just more text to judge[^jev-live-view-2026]

## Reaching the model directly or through the Gateway

The same model can be called two ways, and the difference is operational. The evals example calls TypeSafe directly; putting the [Gateway](pydantic-ai-gateway.md) in front keeps one gateway key in the application, meters Jev into the same spend view and limits as the language models, and runs input guardrails over the `state`, the instructions and the criteria before the request goes upstream — while, per the gateway article, leaving Jev's cost and latency unchanged[^jev-gateway-2026] The gateway forwards System One natively instead of translating it to the OpenAI chat format, refuses streaming requests for this model, and reaches Pydantic AI as a `TypeSafeProvider` pointed at the gateway's `base_url`[^jev-gateway-2026] The two access paths leave the evaluator design on this page unchanged; what the gateway changes is who holds the credential and what wraps the request[^jev-gateway-2026]

The Connect dialog defaults to `jev-latest`, which is the moving alias this page pins away from with `typesafe:jev-1.13.0`; the defaults are compatible, but a judge whose scores are compared across runs should pin[^jev-gateway-2026]

## Three routes through Pydantic Evals

| Route | Returns | Judge requests per reply | Use when |
| --- | --- | --- | --- |
| Custom `Evaluator` subclass | a dict whose strings become labels, numbers scores and booleans assertions | one, carrying all questions | several questions, categorical labels, the fractional rubric score |
| `LLMJudge` | an assertion | one per rubric | a pass/fail judgment is enough |
| `GEval` | an integer inside `score_range` | one per criteria set | a coarse ordinal level is enough |

The custom path is the one this source develops: `Evaluator[SupportInput, str].evaluate(ctx)` receives `ctx.inputs` and `ctx.output`, runs the judge over the serialized policy, customer message and reply, and returns `policy_verdict`, a normalized `completeness` and `p_asks_for_secret`[^jev-evals-2026] It also records the model version, token usage, confidence and distributions in a Logfire log, which is what makes the judgement inspectable later[^jev-evals-2026]

The built-in judges are simpler but costlier per scored reply. `LLMJudge` takes a rubric, the model, the threshold settings and an assertion name; `GEval` takes criteria, evaluation steps, a `score_range`, `include_input=True` and an evaluation name, placing the criteria and steps in the input state and asking a structured score question that refers back to them[^jev-evals-2026] `GEval`'s levels use generic worst, intermediate and best descriptions, whereas the hand-written enum supplies a specific description per level — so the built-ins trade rubric expressiveness for brevity[^jev-evals-2026] Neither asks Jev for an explanation, and each makes its own model call, so two built-in checks use two requests per reply[^jev-evals-2026]

## What the eight fixtures showed

The author ran eight deliberately written synthetic support replies through `jev-1.13.0` with Pydantic AI 2.46.0 on 2026-09-19 — not outputs from a production agent[^jev-evals-2026] All eight completed:

| Case | Policy verdict | Completeness, 0 to 1 | P(asks for secret) |
| --- | --- | --- | --- |
| Helpful duplicate-charge reply | `compliant` | 1.000 | 0.01 |
| Guaranteed refund | `violates_policy` | 0.510 | 0.01 |
| Vague apology | `violates_policy` | 0.325 | 0.01 |
| Helpful login reply | `compliant` | 1.000 | 0.02 |
| Request for password and login code | `violates_policy` | 0.490 | 0.99 |
| Unrelated answer | `violates_policy` | 0.000 | 0.01 |
| Offer of human support | `compliant` | 0.985 | 0.01 |
| Invented free-year policy | `violates_policy` | 0.560 | 0.01 |

The eight requests used 5,444 input tokens — 680.5 per reply, or $0.000228648 for 24 recorded results at the published rate[^jev-evals-2026] Two cases carry the durable lessons. The vague apology was labelled `violates_policy` at confidence 0.91 because the policy requires asking for a transaction ID and the enum description covers omitted required actions; whether an omission is a violation is a rubric decision for the owning team, not a property of the judge[^jev-evals-2026] The password-request reply shows why the measurements stay separate: it received a high secret-solicitation probability and a mid completeness score, so "clear next step" and "safe" are different questions[^jev-evals-2026]

The optional generation mode, which runs a support agent on `openai:gpt-5.6-luna` before judging, labelled all eight generated replies `compliant` on 5,564 Jev input tokens ($0.000233688) plus the separate generation cost[^jev-evals-2026] The evaluator does not require the application being scored to use Pydantic AI[^jev-evals-2026]

## Cost at volume

`genai-prices` had no TypeSafe entry in the recorded environment, so `result.usage.cost` was `None` and the script estimates judge cost from the returned input tokens and the published rate rather than trusting the usage object[^jev-evals-2026] Under the article's assumptions — 1,000 billed input tokens and ten telemetry records per reply, allowances already consumed — one million replies with three recorded results cost $42 in Jev inference plus $20 in Logfire telemetry, against $4,500 in Braintrust Pro score overage plus the same inference: about 1.4%, or roughly 73 times less[^jev-evals-2026] The worked bill, its assumptions and the sensitivity cases (4,000 tokens per reply gives $188 versus $4,668; 50 records per reply gives $142) live in [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md)[^jev-evals-2026]

**Synthesis:** the transferable point is not that Logfire is cheaper but that a cheap structured judge moves the binding meter away from per-score platform fees and back to inference and telemetry volume — the opposite direction from a generative judge, which spends output tokens on an explanation that this design never asks for. The source does not make that comparison itself.

## Limits

- Three vendor articles by Pydantic authors: the evaluator pattern is one account from 2026-09-23, the Gateway route is a separate 2026-09-25 announcement compiled on [Pydantic AI Gateway](pydantic-ai-gateway.md), and running an agent directly on Jev is a 2026-09-29 article compiled on [Jev decision model in Pydantic AI](jev-decision-model.md)[^jev-evals-2026][^jev-gateway-2026][^jev-live-view-2026]
- Every number here is **Reported** from the author's executed run: no script was downloaded, no API key supplied, and no evaluation re-run in this ingest, and the linked `results.json` artifacts were not fetched[^jev-evals-2026]
- Version gap: the APIs described are Pydantic AI 2.46.0 (September 2026) while the wiki's release page is current at v2.59.0, and the point-release table in [Pydantic AI v2 release](pydantic-ai-v2-release.md) starts at v2.50.0 — so `UseEnumMemberDocstrings`, `Choices` and the TypeSafe judge path are outside that table and may have moved[^jev-evals-2026] The 2.50.0 article confirms `TypeSafeModel` still exists but describes it as an adapter on `DecisionModel`, and it never mentions `Choices`, so whether the runtime option set survived that refactor is unconfirmed[^jev-live-view-2026]
- The explicit `insufficient_context` category gives the judge a way to report missing evidence, but the author states plainly that it does not guarantee abstention; missing-context cases belong in the validation set of any judge built this way[^jev-evals-2026]
- Both cost figures are models, not bills: tokens per reply and records per reply are planning assumptions, inclusive allowances are assumed consumed, subscription fees and the application's own inference are excluded, and Braintrust's processed-data and retention charges are excluded from its column[^jev-evals-2026]
- Evidence class: **Reported**, with **Synthesis** where marked.

## Relationships

- **Is scored through** [Pydantic Evals](pydantic-evals.md): the custom evaluator is the library's extension point, and the built-in `LLMJudge` and `GEval` are its shipped judges.
- **Implements the judge layer of** [LLM evaluation modes](llm-eval-modes.md), where LLM-as-a-judge is a scoring method usable offline or online rather than a third product.
- **Is priced in** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), whose per-score-versus-per-record meter argument changes shape once judge inference is this cheap.
- **Logs its judgements into** [Pydantic AI observability](pydantic-ai-observability.md): model version, usage, confidence and distributions are written to Logfire beside the traces.
- **Is routed through** [Pydantic AI Gateway](pydantic-ai-gateway.md), which adds metering, input guardrails and a single key without changing the judge's semantics.
- **Depends on version-specific Pydantic AI output features** tracked in [Pydantic AI v2 release](pydantic-ai-v2-release.md) — described enum members and `Choices` at 2.46.0.
- **Shares its question-sheet schema with** [Jev decision model in Pydantic AI](jev-decision-model.md), which runs an agent on Jev and traces each answer, while this page uses the same mapping to score another agent's output.
- **Is traced by** [Logfire decision tracing](logfire-decision-tracing.md) whenever the judge runs through Pydantic AI's own instrumentation rather than inside an evaluator.

[^jev-evals-2026]: David Montague, "Cheap AI scoring with Jev and Pydantic Evals", Pydantic, published 2026-09-23T16:00Z, 2,416 words as declared; local capture `raw/jev-evals/index.md`, content digest sha256:c34f4321. §"Evaluate a support reply" (lines 19–44) for the three measurements, the eight synthetic fixtures, the pinned 2.46.0 packages and the `--generate` mode; §"Put the questions on the output type" (lines 46–104) for `Choice`/`Score`/`Noul`, the shared input state, `UseEnumMemberDocstrings`, the pinned `typesafe:jev-1.13.0` model, `defer_model_check`, `insufficient_context`, and the cost estimate replacing the absent `genai-prices` entry; §"Return labels and scores to Pydantic Evals" (lines 106–154) for the custom `Evaluator`, label/score/assertion typing, the fractional score in `provider_details`, the zero-to-one normalization, Logfire logging of version/usage/confidence/distributions, the `gpt-5.6-luna` generation run at 5,564 tokens, and the statement that the scored application need not use Pydantic AI; §"Use the built-in judges for simpler checks" (lines 156–199) for `LLMJudge`, `typesafe_boolean_threshold`, threshold-relative boolean confidence, `GEval` criteria/steps/score_range and its generic level wording, two requests per reply, `Choices`, and the open `Classifier` pull request; §"Results from the example" (lines 201–220) for the eight-row verdict table, 5,444 input tokens, the 680.5 average, $0.000228648 for 24 results, the vague-apology 0.91 confidence and the generated-run 5,564 tokens; §"How to think about confidence" (lines 222–226) for the 0.38/0.26/0.36 distribution behind the 0.490 score; §"But how much will this cost?" (lines 228–258) for the $0.042-per-million input price, the 1M-reply model and its assumptions, the $42/$20/$4,500/$62 versus $4,542 table, the 1.4% and 73× ratios, and the 4,000-token and 50-record sensitivity figures. Evidence class: **Reported** — the author's own executed run is quoted; nothing was downloaded, keyed, re-run or price-checked in this ingest.
[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"Your output type is the question" (raw lines 17–44) for `TypeSafeModel` turning each output field into one question in one request; §"The chat span wasn't enough" (lines 59–68) for `DecisionModel` as the base class in 2.50.0 and `TypeSafeModel` as a thin adapter; the `[!warn]` callout (lines 56–57) for the prompt-carries-only-material rule; §"Where else you can use Jev" (lines 84–90) for Jev as an existing Pydantic Evals judge. Evidence class: **Reported** — vendor article; nothing installed or run here.
[^jev-gateway-2026]: Marcelo Trylesinski, "TypeSafe Jev in Pydantic AI Gateway", Pydantic, published 2026-09-25T09:00Z, 565 words as declared; local capture `raw/jev-pydantic-ai-gateway/index.md`, content digest sha256:cd20eca2. §"Set it up" (lines 17–71) for the BYOK provider registration, the provider name as route name, the `jev-latest` Connect default, and the System One endpoint; §"What you get from the Gateway" (lines 73–82) for metering into the spend view and limits, guardrails over `state`/instructions/criteria, the single gateway key, unchanged Jev cost and latency, and refused streaming; §"Using it from Pydantic AI" (lines 84–117) for `TypeSafeProvider` with a gateway key and `base_url`, and `TypeSafeModel('jev-latest', ...)`. Evidence class: **Reported** — vendor article; nothing executed.
