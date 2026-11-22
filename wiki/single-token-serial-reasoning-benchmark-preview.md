---
type: Concept
title: Single-token serial reasoning benchmark preview
description: An unfinished Epoch AI benchmark preview reports normalized serial-reasoning steps achievable in one output token, with task and methodology details not yet disclosed in the capture.
tags: [reasoning, implicit-reasoning, benchmarks, monitorability]
status: draft
created: 2026-11-22
generated: { by: llm-wiki-agent/1, at: 2026-11-22T10:16:08Z }
stale_after: 2027-02-22
sources:
  - id: epoch2026serial
    resource: ../raw/2122762411287748696/index.md
    scope: ../raw/2122762411287748696/
    kind: social-media
    title: Epoch AI post on single-token serial reasoning
  - id: chavez2026astra
    resource: ../raw/gpt-6-2-astra-system-card-safety/index.md
    scope: ../raw/gpt-6-2-astra-system-card-safety/
    kind: article
    title: "GPT 6.2 Astra's System Card Shows a Model That Hides Its Own Failures"
---

# Single-token serial reasoning benchmark preview

**Reported:** Epoch AI's unfinished benchmark estimates how many complexity-normalized serial reasoning steps a model can perform in a single output token, without chain-of-thought. The post reports higher scores for GPT-6.2 Astra than for its selected predecessors, and suggests that complex reasoning without visible chain-of-thought may be harder to monitor. The preview does not establish that any architecture caused the scores or that monitoring actually fails.[^epoch2026serial]

## Measure and reported results

The post defines the score as the number of steps achievable at an accuracy “25% above chance,” with each step normalized for complexity. It reports 12.3 for GPT-6.2 Astra, 10.5 for GPT-6 Astra, 8.6 for GPT-6.1 Sol, 4.2 for Claude Fable 5.1, and 2.3 for Claude Opus 3. It calls the latter two, respectively, the highest-scoring model before GPT-6 Astra's release and the oldest model evaluated; these are claims about its assessed set, not all models.[^epoch2026serial]

**Observed:** The attached scatterplot compares the serial-step score against SimpleQA Verified score on a logit-scaled horizontal axis, described as a proxy for model knowledge/size; points are colored by provider. It also labels models not enumerated in the post, including Claude Fable 5.2, Gemini 4 Argon and GPT-6.1 Terra. The chart calls the results an early preview of a not-yet-finalized benchmark. No exact additional scores are transcribed from the plot.[^epoch2026serial]

## Interpretation and limits

- The capture does not specify the task family (synthetic versus natural), task examples, normalization formula, whether “25% above chance” means percentage points or a relative increase, chance baseline, sample sizes, uncertainty, prompting, model versions, or evaluation protocol. Results cannot be independently reproduced from it. The post says Epoch AI hopes to finalize and release measurements in the coming weeks; no later release was checked.[^epoch2026serial]
- **Synthesis:** Single-token performance measures the benchmark's operationalized capability, not a literal independently verified count of internal reasoning operations. A cross-model comparison does not isolate recurrence, compute, model size, or training as its cause. SimpleQA Verified is a proxy, not a direct measurement of size or of all knowledge.[^epoch2026serial]
- **Reported:** Epoch AI raises a potential monitorability concern, not a direct experiment on monitoring effectiveness. See [Looped computation and chain-of-thought monitorability](looped-computation-and-chain-of-thought-monitorability.md) for the distinction between hidden computation and trace faithfulness.[^epoch2026serial]

## Contradictions

- The Epoch AI preview assigns a score of 4.2 to **Claude Fable 5.1**.[^epoch2026serial] The MindStudio article assigns 4.2 to **Claude Opus 4.1** while reporting the same 12.3 and 10.5 Astra figures.[^chavez2026astra] The capture does not resolve whether this is a misattribution or a different result; neither model label is silently substituted for the other.

## Relationships

- Related to: [OpenAI GPT-6 Astra looped-architecture report](openai-astra-looped-architecture-report.md); the reported architecture is unconfirmed and the benchmark is not evidence of it.
- Related to: [Looped computation and chain-of-thought monitorability](looped-computation-and-chain-of-thought-monitorability.md); the preview concerns a possible capability relevant to monitoring, not a demonstrated causal effect.

[^epoch2026serial]: Epoch AI (@EpochAIResearch), [post on X](https://x.com/EpochAIResearch/status/2122762411287748696), 2026-11-17, post text and attached `assets/HXWRKfna8AAtzo6.jpg` (scatterplot, axes, labels and caption). Both locally captured artifacts inspected; no benchmark methods or underlying data are included. The figure is marked CC-BY; the post's license is not specified.

[^chavez2026astra]: Luis Chavez-Mattos, *GPT 6.2 Astra's System Card Shows a Model That Hides Its Own Failures*, MindStudio, 2026-11-19, local web capture `raw/gpt-6-2-astra-system-card-safety/index.md`, §§“TL;DR,” “What is ‘blocker deception’ and why does it matter here?”, “Why does chain-of-thought density make monitoring harder?”, and “Is the model actually lying, or just bad at communicating?” The capture contains promotional material but no locally attached system card, underlying transcripts, or benchmark methods; these were not independently checked. The article's license and capture date are not stated.
