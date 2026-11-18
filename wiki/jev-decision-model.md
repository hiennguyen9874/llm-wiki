---
type: Concept
title: Jev decision model in Pydantic AI
description: Pydantic AI 2.50's DecisionModel path to TypeSafe Jev — output fields as typed questions, the supported question shapes and the fallback for a free-form field, and why the prompt must stay material-only.
tags: [pydantic-ai, ml, structured-output, classification]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:33:00Z }
stale_after: 2027-03-29
sources:
  - id: jev-live-view-2026
    resource: ../raw/jev-pydantic-ai-live-view/index.md
    scope: ../raw/jev-pydantic-ai-live-view/
    kind: article
    revision: sha256:288f23ddf22c009f4ada93b87fcc6526a089ea7ece6d6c5a229a7dd98e2636f0
    title: "Pydantic AI agents on Jev, traced in Logfire"
  - id: pydantic-openai-2026
    resource: ../raw/models/openai/index.md
    scope: ../raw/models/openai/
    kind: documentation
    revision: sha256:843643d2d611697bb1b730046fa5d0721dc79a32f8665c573769afcbbdc15457
    title: "OpenAI"
  - id: pydantic-google-2026
    resource: ../raw/models/google/index.md
    scope: ../raw/models/google/
    kind: documentation
    revision: sha256:827e192268216b47d986cf2e339ca69639cf0c6618aec8ee216587336f620e44
    title: "Google"
---

TypeSafe's **Jev** is a decision model, not a chat model: it takes material plus a list of typed questions and returns one answer and one probability per question, with no generated text to parse[^jev-live-view-2026] From Pydantic AI 2.50.0 the agent's `output_type` *is* the question set — each field name and description become a question and each field type picks the shape of the answer — and `DecisionModel` is the base class any model speaking TypeSafe's Decisions protocol implements, with `TypeSafeModel` a thin adapter over it[^jev-live-view-2026] The design returns the cost of an agent whose output is a `bool`, a `Literal` or a score to the price of a classifier, but in exchange the prompt stops being instructions and becomes nothing but the material being judged[^jev-live-view-2026]

## The output type is the question sheet

All fields of the output type go out in **one** request, and the prompt is the thing being judged[^jev-live-view-2026]:

```python
class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')
    area: Literal['billing', 'bug', 'account', 'other'] = Field(description='Which team owns it?')

agent = Agent('typesafe:jev-latest', output_type=Ticket)
```

Install with the `typesafe` and `logfire` extras (`uv add "pydantic-ai-slim[typesafe,logfire]"`) and set `TYPESAFE_API_KEY` and `LOGFIRE_TOKEN`[^jev-live-view-2026]

## Question shapes

| Python type | Becomes |
| --- | --- |
| `bool` | a yes or no |
| `Literal` or `Enum` | a pick-one over the declared options |
| `float` with `ge=0, le=1` | the probability itself |
| `IntEnum` mixing in `UseEnumMemberDocstrings` | a rubric, one described level per member |
| a union of output types | routed first, then filled per member |
| a free-form `str` field | a `UserError` before any request is sent |

The shapes are reported from the article, which points at the TypeSafe model docs page for the full list[^jev-live-view-2026] The free-form case is the one that fails loudly: a field Jev cannot answer raises `UserError` before a request leaves the process, except inside a union, where Jev can still pick that member and a `FallbackModel` hands that step to a language model[^jev-live-view-2026] That is the composable pattern — one routed request to the cheap decision model, with the generative model reachable only on the branch that needs text[^jev-live-view-2026]

## The prompt is only material

With a language model the question and the material share the prompt and the model sorts them apart; Jev does not, so a question written into the prompt is merely more text to judge[^jev-live-view-2026] Questions therefore belong in field names and descriptions, and the prompt belongs to the input alone[^jev-live-view-2026] **Synthesis:** this makes the two roles non-portable in one direction — the same agent definition swaps to a language model by changing `'typesafe:jev-latest'` to a model name, but a prompt written for a language model does not carry its questions back to Jev without rewriting them as fields[^jev-live-view-2026]

The swap is nonetheless the intended adoption path: keep Jev and a language model behind the same agent, run the same data through both, and compare the probabilities[^jev-live-view-2026] The alias `'typesafe:jev-latest'` moves, so a pinned version is what keeps such a comparison reproducible across runs[^jev-live-view-2026]

## Role in the wider stack

- **As the agent's model**, the question-sheet schema is the same one used when Jev judges inside [Pydantic Evals](jev-structured-scoring-judge.md)[^jev-live-view-2026]
- **As a judge**, the evals path reuses this mapping; see [Jev structured scoring judge](jev-structured-scoring-judge.md)[^jev-live-view-2026]
- **Through the [Gateway](pydantic-ai-gateway.md)**, the same `TypeSafeModel` is constructed against the gateway's `base_url` so one metered key covers Jev and the language models[^jev-live-view-2026]
- **A new Decisions backend** is, in the article's framing, a matter of translating its transport; `DecisionModel` plus the `decide` span and the Logfire panel come with it[^jev-live-view-2026] See [Logfire decision tracing](logfire-decision-tracing.md).
- **A second backend now exists**: OpenAI's Decisions API is reached as `openai-decisions:gpt-6-luna` through `OpenAIDecisionsModel`, which turns the agent's output type and tools into the same questions — see [OpenAI decision models](openai-decision-models.md)[^pydantic-openai-2026]. That the contract generalises beyond TypeSafe is therefore no longer only the Jev article's projection.
- **A third backend now exists**: Google's Decisions API is reached as `google-decisions:gemini-decision-1` through `GoogleDecisionsModel`, which turns the agent's output type and tools into the same questions over the Gemini API and its `GoogleProvider` — see [Google decision models](google-decisions-model.md)[^pydantic-google-2026] It is also the backend that changes the conversation shape: the API takes no turns, so the history is sent as one text with the latest prompt as what to judge, where OpenAI sends role-preserving input items.

## Limits

- One vendor article by a Pydantic developer, published 2026-09-29, announcing a feature of its own ecosystem product[^jev-live-view-2026]
- Version gap: the claim is that `DecisionModel`, the `decide` span and the `TypeSafeModel` refactor all landed in v2.50.0[^jev-live-view-2026] The wiki's [Pydantic AI v2 release](pydantic-ai-v2-release.md) timeline, taken from a third-party tour, dates v2.50.0 to Sep 24 but lists only `RunContext.in_durable_context` as its headline — so the attribution of this feature to that patch release rests on the vendor article alone
- The shape table is the article's prose, not a schema reference; the "full list" it points at (the Typesafe model docs page) was read as a link, not followed[^jev-live-view-2026]
- No agent was run, no TypeSafe key supplied, no model called, and no `UserError` or `FallbackModel` path exercised in this ingest; every API name and behaviour is dated to the article[^jev-live-view-2026]
- The article gives no price, latency, rate limit, or accuracy comparison between Jev and a language model on the same task; the cost case for Jev lives, from a different article, on [Jev structured scoring judge](jev-structured-scoring-judge.md)
- Evidence class: **Reported**, with **Synthesis** where marked.

## Relationships

- **Shares its question schema with** [Jev structured scoring judge](jev-structured-scoring-judge.md), where the same output-type mapping is used to score replies rather than to run an agent.
- **Is traced by** [Logfire decision tracing](logfire-decision-tracing.md), the `decide` span and Agent Run panel that record the questions, probabilities and thresholds behind each answer.
- **Is reachable through** [Pydantic AI Gateway](pydantic-ai-gateway.md) as a base-URL change on the same model adapter.
- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) only insofar as it is a model implementation: capabilities, tools and instructions are unchanged by swapping in a decision model.
- **Attributed to** v2.50.0 in [Pydantic AI v2 release](pydantic-ai-v2-release.md), on this article's authority rather than the release tour's.
- **Implemented for a second provider** by [OpenAI decision models](openai-decision-models.md), whose route names no version, so this page's 2.50.0 attribution stays TypeSafe-specific.

[^jev-live-view-2026]: Marcelo Trylesinski, "Pydantic AI agents on Jev, traced in Logfire", Pydantic, published 2026-09-29T09:00Z, 872 words as declared; local capture `raw/jev-pydantic-ai-live-view/index.md`, content digest sha256:288f23dd. §"Your output type is the question" (raw lines 17–44) for `TypeSafeModel`, fields-as-questions, the single request, the `Ticket` example and its printed `urgent=True area='billing'`; lines 46–52 for the `typesafe`/`logfire` extras, `TYPESAFE_API_KEY`/`LOGFIRE_TOKEN` and the model-name swap; line 54 for the `bool`/`Literal`/`Enum`/`float`/`IntEnum`/union/free-form shapes, the `UserError` before the request, the union-plus-`FallbackModel` exception, and the pointer to the TypeSafe docs page; §"The chat span wasn't enough" (lines 59–68) for `DecisionModel` as the base class, `TypeSafeModel` as a thin adapter, PRs #8696/#8698 and the 2.50.0 release; §"Where else you can use Jev" (lines 84–90) for the Pydantic Evals judge, the Gateway route, and `DecisionModel` generalizing to other Decisions backends. The `[!warn]` callout (lines 56–57) is the source of the prompt-is-only-material rule. Attachments `assets/support-triage.png` and `assets/route-then-fill.png` were inspected but carry no claim on this page; both are cited on [Logfire decision tracing](logfire-decision-tracing.md). Evidence class: **Reported** — vendor article; nothing was installed, keyed, run or measured.

[^pydantic-openai-2026]: Pydantic Docs, "OpenAI", <https://pydantic.dev/docs/ai/models/openai/>, no publication date and no Pydantic AI version named; local capture `raw/models/openai/index.md`, content digest sha256:843643d2. §"Decisions API" (raw lines 690–733) for `OpenAIDecisionsModel`, the `'openai-decisions:gpt-6-luna'` prefix, and the statement that an agent's output type and tools become the questions described on the Decision models page. Evidence class: **Reported** — vendor documentation; no decision model was constructed or called.

[^pydantic-google-2026]: Pydantic Docs, "Google", <https://pydantic.dev/docs/ai/models/google/>, 4,106 words as declared and 4,177 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/google/index.md`, content digest sha256:827e1922. §"Decisions API" (raw lines 529–568) for `GoogleDecisionsModel`, the `google-decisions:gemini-decision-1` example, and the statement that an agent's output type and tools become the questions. Evidence class: **Reported** — vendor documentation; no decision model was constructed or called.
