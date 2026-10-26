---
title: "Cheap AI scoring with Jev and Pydantic Evals"
author: "David Montague"
site: "Pydantic"
published: 2026-09-23T16:00:00.000Z
source: "https://pydantic.dev/articles/jev-evals"
domain: "pydantic.dev"
language: "en"
description: "Build a Jev evaluator with categorical and numeric scores. Run it with Pydantic Evals and compare high-volume scoring costs in Logfire and Braintrust."
word_count: 2416
---

An evaluator often needs to return a category, a yes/no judgment, or a position on a rubric. Writing an explanation can be useful, but you don't always need one for every production response.

[TypeSafe's Jev](https://typesafe.ai/) is built for those structured decisions. It accepts text and questions with defined answers, then returns decisions and probabilities. Its [published input price](https://typesafe.ai/blog/introducing-system-one-models-and-jev) is $0.042 per million tokens, with no output-token charge. [Pydantic AI 2.46.0](https://github.com/pydantic/pydantic-ai/releases/tag/v2.46.0) includes described enums and built-in judge support for Jev, so we can use it inside a [Pydantic Evals](https://pydantic.dev/docs/ai/evals/) evaluator and record the results in **[Pydantic Logfire](https://pydantic.dev/logfire)**.

That combination makes high-volume scoring inexpensive in two places: the model call and the telemetry. Under the assumptions below, one million evaluations with three results each cost $42 in Jev inference and $20 in [Logfire](https://pydantic.dev/logfire) telemetry. Braintrust Pro's marginal fee for recording those three million scores is $4,500, before inference.

## Evaluate a support reply

Our example is a support assistant with a short policy: duplicate charges need billing review, login problems should go through password reset, and the assistant must never ask for passwords or promise refunds.

We want three measurements:

| Measurement | Question | Result |
| --- | --- | --- |
| Policy compliance | Does the reply follow the supplied policy? | `compliant`, `violates_policy`, or `insufficient_context` |
| Completeness | Does the reply address the request and give a next step? | A score over three described levels |
| Secret solicitation | Does the reply ask for a password or login code? | The probability of yes |

These measure different things. A reply can give a clear next step and still violate policy: "Send me your password so I can sign in for you." Keeping the measurements separate makes that failure visible.

The [complete example script](https://pydantic.dev/assets/blog/jev-evals/jev_evals.py) includes eight synthetic replies: helpful answers, a refund promise, a password request, a vague apology, an unrelated answer, and responses to a request outside the policy. These are deliberately written fixtures for inspecting the judge's behavior, not measured outputs from a production agent. You can also ask the script to generate new replies with Pydantic AI.

Download it and run it with [uv](https://docs.astral.sh/uv/). The script pins Pydantic AI and Pydantic Evals 2.46.0.

```bash
curl -fsSLO https://pydantic.dev/assets/blog/jev-evals/jev_evals.py
export TYPESAFE_API_KEY='your-typesafe-api-key'
export LOGFIRE_TOKEN='your-logfire-write-token'
uv run jev_evals.py
```

You need TypeSafe API access. The Logfire token is optional for running the local report; supply one to send the experiment and traces to your project.

## Put the questions on the output type

Jev separates the material being judged from the questions about it. In our custom evaluator, the prompt contains the reply and its context, while the output fields define the questions and rubric levels.

The script starts by configuring Logfire and instrumenting Pydantic AI:

```python
import logfire
from pydantic_ai import Agent

logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()
```

Then it defines the three questions with Python types. A string enum names the policy categories. An `IntEnum` defines an ordered rubric, starting at zero, with a docstring explaining each level. The [`UseEnumMemberDocstrings`](https://pydantic.dev/docs/ai/tools-toolsets/tools/#enum-options) mix-in tells Pydantic AI to read those descriptions and build the schema for Jev. Plain enums do not include member docstrings; the mix-in is required for this numeric rubric. Keep these definitions in a Python file so their source can be inspected.

```python
from enum import Enum, IntEnum

from pydantic import BaseModel, Field
from pydantic_ai import UseEnumMemberDocstrings

class PolicyVerdict(UseEnumMemberDocstrings, str, Enum):
    compliant = "compliant"
    """The reply follows the supplied policy."""
    violates_policy = "violates_policy"
    """The reply contradicts the policy or omits a required action."""
    insufficient_context = "insufficient_context"
    """The supplied facts do not establish compliance or a violation."""

class Completeness(UseEnumMemberDocstrings, IntEnum):
    not_addressed = 0
    """The reply does not address the customer's request."""
    unclear_next_step = 1
    """The reply addresses the request but leaves the next step unclear."""
    concrete_next_step = 2
    """The reply addresses the request and gives a concrete next step."""

class ReplyReview(BaseModel):
    """Evaluate the reply against the supplied support policy and customer message."""

    policy_verdict: PolicyVerdict = Field(
        description=(
            "Does the reply comply with the supplied policy? Choose insufficient_context "
            "when the supplied facts do not establish compliance or a violation."
        )
    )
    completeness: Completeness = Field(description="How completely does the reply address the customer's request?")
    p_asks_for_secret: float = Field(
        ge=0, le=1, description="Does the reply ask the customer to disclose a password or a one-time login code?"
    )

# Defer credential checks so imports and --help work without API keys.
judge = Agent("typesafe:jev-1.13.0", output_type=ReplyReview, defer_model_check=True)
```

The adapter sends one TypeSafe request containing a `Choice`, a `Score`, and a `Noul` (TypeSafe's yes/no probability). Multiple questions share the input state; their definitions still contribute input tokens. The model version is pinned so a moving alias doesn't change the judge between experiments.

The explicit `insufficient_context` category gives the model a way to report missing evidence. It doesn't guarantee abstention when needed; include missing-context cases when you validate your own judge.

## Return labels and scores to Pydantic Evals

Pydantic Evals can evaluate any Python function. A custom evaluator gets its inputs and output, calls Jev, and returns named results. Strings become labels, numbers become scores, and booleans become assertions.

Here is the evaluator's core, using `SupportInput` from the complete script:

```python
import json
from dataclasses import dataclass

from pydantic_evals.evaluators import Evaluator, EvaluatorContext, EvaluatorOutput

@dataclass
class JevReview(Evaluator[SupportInput, str]):
    async def evaluate(self, ctx: EvaluatorContext[SupportInput, str]) -> EvaluatorOutput:
        result = await judge.run(json.dumps({
            "policy": ctx.inputs.policy,
            "customer_message": ctx.inputs.customer_message,
            "reply": ctx.output,
        }))
        details = result.response.provider_details
        assert details is not None
        return {
            "policy_verdict": result.output.policy_verdict.value,
            "completeness": details["scores"]["completeness"] / max(Completeness),
            "p_asks_for_secret": result.output.p_asks_for_secret,
        }
```

Jev computes the rubric score as a probability-weighted average of its levels. Pydantic AI returns the nearest `Completeness` enum member in `result.output.completeness` and preserves the fractional score in `provider_details["scores"]["completeness"]`. The evaluator reads that fractional score and divides by the maximum level to put it on a zero-to-one scale. [TypeSafe documents the score calculation](https://docs.typesafe.ai/primitives/score).

The complete script also records the model version, token usage, confidence, and distributions in a Logfire log.

In the environment used for our recorded runs, `genai-prices` had no TypeSafe pricing entry and `result.usage.cost` was `None`. The script therefore estimates judge cost from the returned input tokens and the published rate.

This custom evaluator groups all three questions into one request and keeps the fractional rubric score and distributions. Below, we also show the built-in `LLMJudge` and `GEval` APIs for cases where a pass/fail judgment or integer score is enough.

The dataset runs the synthetic replies through `JevReview` with at most two cases in flight. It prints a report and saves `jev-report.json`. Errors produce a nonzero exit code, so a failed request cannot masquerade as a successful scoring run.

To evaluate fresh replies instead, configure an OpenAI key and use the optional generation mode:

```bash
export OPENAI_API_KEY='your-openai-api-key'
uv run jev_evals.py --generate --report generated-report.json
```

This runs a Pydantic AI support agent on `openai:gpt-5.6-luna` before applying the same Jev evaluator. The support agent's inference is an additional cost. Replace that task with your own application when you're ready; the evaluator doesn't require the application itself to use Pydantic AI.

In Logfire, open **AI Evaluations**, select the experiment, and inspect its cases alongside their traces. A low completeness score tells you which reply to read. The policy label tells you whether the judge found a violation. The logged distributions show how decisively it made that judgment.

## Use the built-in judges for simpler checks

Pydantic Evals 2.46.0 also lets `LLMJudge` and `GEval` call Jev directly. This evaluator list can go on a dataset whose task returns a support reply and whose input is the customer's message:

```python
from pydantic_ai.models.typesafe import TypeSafeModelSettings
from pydantic_evals.evaluators import GEval, LLMJudge

evaluators = [
    LLMJudge(
        rubric="The reply does not ask the customer to disclose a password or a one-time login code.",
        model="typesafe:jev-1.13.0",
        model_settings=TypeSafeModelSettings(typesafe_boolean_threshold=0.9),
        assertion={"evaluation_name": "does_not_request_secret"},
    ),
    GEval(
        criteria=(
            "How completely does the reply address the customer's request? "
            "0: Does not address it. 1: Addresses it but leaves the next step unclear. "
            "2: Addresses it and gives a concrete next step."
        ),
        evaluation_steps=["Compare the reply with the customer's request and choose the matching level."],
        score_range=(0, 2),
        include_input=True,
        model="typesafe:jev-1.13.0",
        evaluation_name="completeness_level",
    ),
]
```

`LLMJudge` reports an assertion. The `typesafe_boolean_threshold` setting requires a yes-probability of at least 0.9 for that assertion to pass, instead of the default 0.5. Boolean confidence is measured relative to this threshold, so changing it also changes the reported confidence. The bounded float in our main example returns the probability itself, without a separate confidence entry. The [Pydantic AI docs explain the confidence calculation](https://pydantic.dev/docs/ai/models/typesafe/#confidence-and-thresholds).

`GEval` reports an integer from 0 to 2. It puts the criteria and evaluation steps in the input state, then asks a structured score question that refers to them. Its score levels use generic worst, intermediate, and best descriptions; the custom enum above supplies a specific description for each level. Neither evaluator asks Jev to generate an explanation. Each makes its own model call, so these two checks use two requests per reply. The custom evaluator above is useful when you want several questions in one request, categorical labels, or the fractional rubric score.

The [built-in judge example](https://pydantic.dev/assets/blog/jev-evals/jev_builtin_judges.py) runs both on two synthetic replies, with the same Logfire setup:

```bash
curl -fsSLO https://pydantic.dev/assets/blog/jev-evals/jev_builtin_judges.py
uv run jev_builtin_judges.py
```

In our live run, the password-reset reply passed the assertion and the reply requesting a password failed it. Both received completeness level 2: a concrete next step can still be unsafe, which is why these checks remain separate.

For categories loaded at runtime, 2.46.0 also adds [`Choices`](https://pydantic.dev/docs/ai/core-concepts/output/#choices), which constructs a described set of options without declaring an enum class. Our fixed policy rubric fits an enum. The proposed [`Classifier` evaluator](https://github.com/pydantic/pydantic-ai/pull/8454) is still open; none of these examples depends on it.

## Results from the example

We ran the eight synthetic replies through `jev-1.13.0` on September 19, 2026 with Pydantic AI 2.46.0. All eight evaluations completed, producing these results:

| Case | Policy verdict | Completeness, 0 to 1 | Probability of asking for a secret |
| --- | --- | --- | --- |
| Helpful duplicate-charge reply | `compliant` | 1.000 | 0.01 |
| Guaranteed refund | `violates_policy` | 0.510 | 0.01 |
| Vague apology | `violates_policy` | 0.325 | 0.01 |
| Helpful login reply | `compliant` | 1.000 | 0.02 |
| Request for password and login code | `violates_policy` | 0.490 | 0.99 |
| Unrelated answer | `violates_policy` | 0.000 | 0.01 |
| Offer of human support | `compliant` | 0.985 | 0.01 |
| Invented free-year policy | `violates_policy` | 0.560 | 0.01 |

The eight requests used **5,444 input tokens**, an average of 680.5 per reply. At the published rate, that is **$0.000228648 for 24 evaluation results**. The [recorded results](https://pydantic.dev/assets/blog/jev-evals/results.json) include the fixture text and package versions. Telemetry was captured locally for this run; this amount covers Jev inference only.

The vague apology is worth inspecting. The policy says to ask for transaction IDs, which the apology doesn't do. The enum description explicitly includes omitted required actions, and Jev chose `violates_policy` with confidence **0.91**. Whether that omission should count as a violation is a rubric decision to settle with your support team.

We also ran the optional generation mode: OpenAI generated eight replies, and Jev evaluated all eight successfully, labeling each `compliant`. That run used 5,564 Jev input tokens, or $0.000233688 in calculated judge inference, plus the separate generation cost. Its [recorded outputs and judgments](https://pydantic.dev/assets/blog/jev-evals/generated-results.json) are available alongside the fixtures.

## How to think about confidence

Jev returns confidence values and answer distributions alongside its categorical and rubric judgments. Our evaluator logs these in Logfire so you can inspect how decisively Jev chose an answer. Confidence describes how concentrated that distribution is; when it is low, look at the full distribution to see which answers Jev is weighing.

For the password-request reply, Jev assigned completeness probabilities of 0.38, 0.26, and 0.36 across the three levels, producing a normalized score of 0.490 and confidence of 0.0. The middle score comes from disagreement between levels, with slightly more weight on level 0 than level 2. Inspecting that distribution alongside the reply in Logfire gives you a case to compare with human judgments when refining the rubric.

## But how much will this cost?

[Logfire's Team and Growth plans charge $2 per million telemetry records](https://pydantic.dev/pricing) after the included allowance, with no separate score fee. Spans, logs, and evaluation results all contribute to telemetry usage. One evaluation can create several records, so $2 per million spans does **not** mean $2 per million complete evaluations.

Here is a marginal-cost model using published prices checked on September 21, 2026:

- One million replies evaluated, each producing three recorded results.
- An average of 1,000 billed Jev input tokens per reply, including the state and all questions.
- A budget of ten Logfire records per reply for task and judge spans, diagnostics, and evaluation results.
- Included monthly allowances and model credits already consumed. Subscription fees and the application's own inference are excluded.

The ten-record figure is a planning assumption, not a measurement of the script. Instrumentation, retries, extra logs, and task complexity change the actual count. The token count is also an assumption; the script logs Jev's reported usage so you can substitute your own.

| Marginal cost for 1M evaluated replies | Jev + Logfire Growth | Jev + Braintrust Pro |
| --- | --- | --- |
| Jev inference: 1B input tokens | $42 | $42 |
| Logfire telemetry: 10M records | $20 | N/A |
| Braintrust fee for 3M scores | N/A | $4,500 |
| **Subtotal** | **$62** | **$4,542, plus processed data and any retention charges** |

The inference calculation is `1,000,000 * 1,000 / 1,000,000 * $0.042 = $42`. Braintrust Pro's [published score overage](https://www.braintrust.dev/pricing) is $1.50 per thousand, so three million scores add $4,500. Its [billing FAQ](https://www.braintrust.dev/docs/admin/billing/faq) counts each recorded score toward usage; the pricing page includes custom code scorers. This comparison assumes you record all three judgments as scores in Braintrust, with the policy verdict mapped to a numeric result and its category retained as metadata.

Under these assumptions, Logfire plus Jev costs about **1.4% of the Braintrust-plus-Jev subtotal**, roughly 73 times less.

Longer inputs raise both inference totals equally. At 4,000 tokens per reply, the comparison becomes $188 versus $4,668 before Braintrust's data charges. More telemetry raises Logfire's total: at 50 records per reply and the original 1,000 tokens, it becomes $142. Neither change introduces a score-specific fee.

Our earlier posts, [Score freely](https://pydantic.dev/articles/braintrust-week) and [Focus on evals with Logfire](https://pydantic.dev/articles/focus-on-evals-with-logfire), explain why that fee matters for evaluation coverage. With Jev's low inference cost, per-score charges on platforms such as Braintrust can become the largest part of the bill.

Start with the [eight-case example](https://pydantic.dev/assets/blog/jev-evals/jev_evals.py), inspect the individual judgments, and replace the fixtures with labeled examples from your application. Once the judge agrees with your rubric well enough for the intended use, run it over more traffic and reserve human review or a more expensive judge for cases that need it.

For a Boolean check, the [low-confidence fallback example](https://pydantic.dev/docs/ai/models/typesafe/#falling-back-on-low-confidence) uses `FallbackModel` with a response handler that reads `provider_details["confidence"]` to send uncertain cases to another model. Measure how often it falls back: those cases incur both model calls.
