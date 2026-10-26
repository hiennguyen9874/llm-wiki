---
type: Concept
title: Offline, online and LLM-as-a-judge evals
description: The three-layer evaluation model — offline datasets and experiments for changes you made, online scoring for changes you did not, and LLM-as-a-judge as a scoring method rather than a third product.
tags: [ml, agents, evaluation, judging]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:25:00Z }
sources:
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
  - id: sanchez-self-improving-2026
    resource: ../raw/when-agents-improve-agents/index.md
    scope: ../raw/when-agents-improve-agents/
    kind: article
    revision: sha256:3a72d59c7e98809d43fbf8b36a3fb77a26fa72444fb698a84bf5eb2229d9f2b2
    title: "When agents improve agents: loops that improve themselves"
---

Offline evals, online evals and LLM-as-a-judge are not three competitor products: two of them are places an evaluation runs and the third is a way a score is computed[^pydantic-eval-tools-2026] Offline evals push a fixed dataset through the system deliberately, online evals attach evaluators to sampled production traffic, and LLM-as-a-judge is a scoring method available in either mode — which makes their combination a workflow choice rather than a purchasing one[^pydantic-eval-tools-2026] The decision rule the source gives is one sentence: offline is for changes you make, online is for changes you did not make[^pydantic-eval-tools-2026] Because the distinction is framework-neutral, this page carries the vocabulary that [Pydantic Evals](pydantic-evals.md) implements in code and that [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md) uses to read vendor feature tables.

## Why a test suite is not an evaluation

`pytest` returns pass or fail, and most of the questions worth asking about model output are graded rather than binary: is this summary faithful to the source, did the agent pick the right tool, was the refusal appropriate[^pydantic-eval-tools-2026] Some of those are assertions and some need a scoring model, so a green CI run does not describe quality.

The second reason is that regressions arrive without a deploy. A provider ships a new model snapshot, a retrieval index refreshes, users change how they phrase things — nothing in the repository changed and the quality did[^pydantic-eval-tools-2026] Only scoring traffic that was not curated catches that class of change.

The third is diagnostic: a score with no trace behind it is a dead end. "Faithfulness dropped to 0.71" is a starting point, and fixing it means reading the prompt, the retrieved chunks and the tool calls from the run that produced that number[^pydantic-eval-tools-2026]

## Offline: datasets and experiments

A dataset is a reusable collection of cases, each with an input, an optional expected output and metadata; one run of the system over that dataset is an experiment, and experiments are compared against each other to decide whether a change helped[^pydantic-eval-tools-2026] The question offline evals answer is therefore "did this change improve my test set", asked before a prompt or model change is promoted — which makes offline the pre-deploy gate[^pydantic-eval-tools-2026] The workload is heavier than a case count suggests: OpenAI's public `simple-evals` MATH runner repeats a 5,000-case test set ten times and records one score per attempt, so a single complete run of one benchmark writes 50,000 score records[^logfire-evals-focus-2026]

**Synthesis:** the vocabulary maps onto the code-first libraries rather than onto a vendor: [Pydantic Evals](pydantic-evals.md) `Dataset`/`evaluate_sync` and DeepEval's test runs are both dataset-over-system experiments in this sense, while the hosted products add shared case curation and experiment history on top of it.

## Online: scoring traffic nobody curated

Online evals attach evaluators to real production traffic, usually sampled, so the question changes from "did this change improve my test set" to "is the thing users actually send still working"[^pydantic-eval-tools-2026] The sample rate is the cost control, because judge inference is billed separately by every tool in this category[^pydantic-eval-tools-2026] The rule the vendor gives is asymmetric: deterministic checks can run on every case without an extra evaluation fee, and only LLM judges are sampled, once their model cost or latency warrants it[^logfire-evals-focus-2026]

**Synthesis:** the split is the same one [agent observability requirements](agent-observability-requirements.md) makes when it argues that production failures are the source material for the next test case: online scoring is what turns an uncurated failure into a candidate dataset entry.

## LLM-as-a-judge is a scoring method

The alternatives to a judge are deterministic checks — the JSON validates, the citation is present, the latency is under a bound — and human labels; combining all three is a design choice, illustrated in the source's reference to Airbnb's three-layer approach[^pydantic-eval-tools-2026] The source's position on judge quality is qualified rather than promotional: useful, yes; unsupervised, no[^pydantic-eval-tools-2026]

The practical hygiene it recommends:

- keep each judge narrow;
- ask for a recorded reason, so a score can be reviewed rather than taken on faith;
- calibrate the judge against human labels on a small gold set;
- let deterministic checks carry every question they can answer, because they are cheaper, faster and not subject to drift[^pydantic-eval-tools-2026]

**Synthesis:** "recorded reason" is the property that makes a judge verdict auditable at all, and it is also what ties judging back to the trace: a reason with no run behind it is the dead-end score again. The source does not develop that link.

### What makes a judge unsafe to optimize against

A second Pydantic article states the failure modes rather than the aspiration, because its context is a loop that keeps a change whenever the grade improves — which turns any stable bias into an objective[^sanchez-self-improving-2026]:

| Failure mode | Behaviour |
| --- | --- |
| Position bias | Swapping the order of two candidates flips the verdict toward whichever came first |
| Self-disagreement | Two runs of the same judge on the same input can disagree |
| Self-enhancement | Given its own output beside another model's, the judge prefers its own |
| Consistent but wrong | A judge can be perfectly stable and still grade badly, so a rising score is not proof of better work |

The defenses it lists are concrete and mostly about constraint rather than model choice: calibrate against a person who knows the domain, grade one dimension at a time instead of asking for one overall score, prefer a binary pass or fail over a five-point scale, randomize order so position cannot pick the winner, and version the rubric — because grading criteria drift as reviewers learn what they are really grading, and an unversioned rubric is a judge that drifts without a trace[^sanchez-self-improving-2026] The same article ties this back to the earlier hygiene: it calls checking the grader "did we verify the verification", and observes that a loop optimizing against a biased judge only learns to satisfy the bias[^sanchez-self-improving-2026]

**Synthesis:** the two hygiene lists overlap on calibration and on narrowness but not on the scale: the earlier comparison article stops at "calibrate against a small gold set", while this one rules out a five-point scale outright and adds order randomization, which costs a second judge call per comparison if it is implemented as swap-and-average. That cost is not in the source.

The judge's **call shape** is part of the design rather than an implementation detail. A Pydantic Evals setup can group several questions into one judge request, or use one built-in evaluator per check, which spends one request per check on every scored item[^jev-evals-2026] A worked example groups three measurements — a policy category, a rubric level and a yes/no probability — into a single call, and notes that the definitions of its questions still count toward the input[^jev-evals-2026] Its judge is a structured-decision model billed per input token with no output charge, and the author's framing is that an explanation is useful but not needed for every production response[^jev-evals-2026]

**Synthesis:** grouping questions, sampling and judge choice are three levers on one bill. The sample rate sets the multiplier, while questions per item and the judge's token price set the cost of each sampled case — and none of the three shows up in a platform's per-record price, which is why this page's mode choice and [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md)'s meter choice are separate decisions.

## Choosing the mode

| Situation | Mode | Why |
| --- | --- | --- |
| A prompt, model or implementation change is about to be promoted | Offline | The dataset is the same before and after, so the delta is attributable |
| A provider ships a new snapshot, an index refreshes, or user phrasing drifts | Online | Nothing in the repository changed, so nothing in CI will notice |
| The question is binary and mechanically checkable | Deterministic check in either mode | Cheaper and drift-free; a judge would only add noise |
| The question is graded and no stable rule exists | LLM-as-a-judge in either mode | The only option left, and calibrated against human labels |

## Limits

- The three-mode model, the decision rule and the judge-hygiene advice are one vendor's framing in a comparison article that ranks its own product first; no eval suite, judge calibration or gold set was built or measured here[^pydantic-eval-tools-2026]
- The article supplies no accuracy figures for judges, no cost model for judge inference and no sample-size guidance for online sampling, so "calibrate on a small gold set" is stated without a definition of small[^pydantic-eval-tools-2026]
- Airbnb's three-layer approach is referenced by link only; that article was not read, so the layers are not described here[^pydantic-eval-tools-2026]
- Evidence class: **Reported**, with **Synthesis** where the mapping to Pydantic Evals or to the observability failure model is inferred.
- The benchmark shape and the sampling rule come from a second Pydantic article (2026-08-04); its MATH figure is quoted from OpenAI's public `simple-evals` runner by link and was not executed, and the "no extra evaluation fee" claim is the vendor's pricing statement[^logfire-evals-focus-2026]
- The judge failure modes and the five calibration measures come from a third Pydantic article (2026-07-31) written to argue for a self-improving loop, not from a calibration experiment; its own citations (Wang et al. ACL 2024, Zheng et al. NeurIPS 2023, Anthropic's agent-evals guide with Hamel Husain, Shankar et al. UIST 2024) were read as links, not opened[^sanchez-self-improving-2026]

## Relationships

- **Is implemented by** [Pydantic Evals](pydantic-evals.md), whose `Dataset` runs are the offline mode and whose `OnlineEvaluation` capability is the sampled online mode.
- **Gains a failure model from** [Self-improving agent loops](self-improving-agent-loops.md), which names the biases that make a rising score unsafe as an objective and the calibration measures that constrain them.
- **Shares its judge layer with** [Jev structured scoring judge](jev-structured-scoring-judge.md), a worked cheap-judge design that groups several questions into one request.
- **Supplies the vocabulary for** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), where the three modes stop separating products and the differentiators become billing and trace proximity.
- **Explains the regression class** that [agent observability requirements](agent-observability-requirements.md) argues a request-scoped APM stack cannot see.
- **Gains a measured shape from** [LLM evaluation tool comparison](llm-evaluation-platform-comparison.md), whose worked bills count the nightly offline suite; the hosted review loop over the same experiments is [Logfire Evals workspace review loop](logfire-evals-workspace.md).

[^sanchez-self-improving-2026]: David Sanchez, "When agents improve agents: loops that improve themselves", Pydantic, published 2026-07-31T12:00Z; local capture `raw/when-agents-improve-agents/index.md`, content digest sha256:3a72d59c. §"Can you trust the judge?" (raw lines 61–67) for the four failure modes, the "consistent and still wrong" warning, the verify-the-verification reading, and the five calibration measures. Evidence class: **Reported** — vendor essay; no judge was calibrated or compared.

[^jev-evals-2026]: David Montague, "Cheap AI scoring with Jev and Pydantic Evals", Pydantic, published 2026-09-23T16:00Z, 2,416 words as declared; local capture `raw/jev-evals/index.md`, content digest sha256:c34f4321. §"Evaluate a support reply" (lines 19–44) for the framing that an explanation is useful but not needed for every production response, and the three separate measurements; §"Put the questions on the output type" (lines 46–104) for the single TypeSafe request carrying several questions and the note that their definitions still contribute input tokens; §"Use the built-in judges for simpler checks" (lines 156–199) for one model call per built-in evaluator, hence two requests per reply for two checks; §"But how much will this cost?" (lines 228–258) for the $0.042-per-million input price with no output-token charge. Evidence class: **Reported** — a vendor article; no judge was called and no request counted.

[^logfire-evals-focus-2026]: Bill Easton, "Focus on evals with Logfire, not score metering", Pydantic, published 2026-08-04, 806 words as declared; local capture `raw/focus-on-evals-with-logfire/index.md`, content digest sha256:359c59fe. §"Offline: repeat the full benchmark" (lines 50–62) for the 5,000-case MATH set repeated ten times and the resulting 50,000 score records per run; §"No score meter" (lines 28–32) for deterministic checks running on every case with no extra evaluation fee and LLM judges being sampled. Evidence class: **Reported** — vendor material; the runner was read as a link and not executed, and no judge was sampled.

[^pydantic-eval-tools-2026]: Bill Easton, "Best LLM Evaluation Tools 2026", Pydantic, published 2026-08-26 with evaluation workflows updated 2026-09-12 and prices checked 2026-08-26; local capture `raw/best-llm-evaluation-tools/index.md`, content digest sha256:6a9f0092. §"Why teams look for a dedicated evaluation tool" (lines 21–26) for the pass/fail limits of a test suite, the without-a-deploy regression list, and the score-without-a-trace argument; §"Offline evals, online evals, and LLM-as-a-judge are not three tools" (lines 28–38) for the dataset/experiment definition, the online question, the judge-as-method framing, the deterministic-check and human-label alternatives, and the Airbnb three-layer reference; §"Frequently asked questions" (lines 151–157) for the offline-is-changes-you-make rule, the provider-snapshot and index-refresh examples, and the narrow-judge/recorded-reason/gold-set advice. Evidence class: **Reported** — a vendor comparison article; no evaluation was run.
