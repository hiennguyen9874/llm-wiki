---
type: Concept
title: LoopWM evaluation and evidence limits
description: LoopWM reports five-action textual world-modelling scores on ScienceWorld and AlfWorld, but incomplete disclosure, missing ablations, and an unrelated evaluation artifact prevent reliable attribution or independent validation.
tags: [world-models, evaluation, scienceworld, alfworld, reproducibility, evidence-limits]
status: draft
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:54:29Z }
sources:
  - id: loopwm-2026
    resource: ../raw/arXiv-2606.18208v1/draft.tex
    title: "Looped World Models"
  - id: loopwm-human-eval-2026
    resource: ../raw/arXiv-2606.18208v1/human_eval_combined.pdf
    title: "Human evaluation results on Danmaku Chan"
---

# LoopWM evaluation and evidence limits

The LoopWM manuscript reports five-action textual world-modelling results for an approximately 1B-parameter model on ScienceWorld and AlfWorld. The reported scores compare an unspecified LoopWM configuration with proprietary API models, but missing experimental detail, no LoopWM ablations, explicitly selective disclosure, and a mismatched evaluation attachment mean they are author-reported observations rather than validated evidence for the proposed mechanisms.[^loopwm-2026][^loopwm-human-eval-2026]

## Reported results

On ScienceWorld, the source reports aggregate five-action scores of 68.4% exact match, 85.3% token F1, 80.7% BLEU-4, and 83.9% entity score. Its reported Claude Opus 4.6 Max comparison is 47.2%, 72.8%, 64.4%, and 72.3%, respectively; Qwen 3.5 Flash and Gemini 3 Flash Preview are also reported at lower aggregate scores. The comparison does not document prompts, model snapshots, API settings, evaluation harnesses, sample counts, or uncertainty.[^loopwm-2026]

On AlfWorld, LoopWM is reported at 51.6% exact match, 80.4% token F1, 71.6% BLEU-4, and 81.1% entity score. The same table reports Claude at 53.0%, 72.6%, 66.8%, and 77.0%, and Gemini at 50.0%, 83.5%, 71.0%, and 90.2%. Thus, even within the reported table, LoopWM is not uniformly best across metrics or baselines.[^loopwm-2026]

The manuscript also tabulates ScienceWorld scores separately for rollout steps 1–5, but does not compare those measurements with a non-deferred-decoding LoopWM. Consequently, they do not isolate a causal benefit from deferred decoding, adaptive inner-loop depth, parameter sharing, or the retention parameterization.[^loopwm-2026]

## Evaluation limitations

The limitations section says the manuscript is "intentionally selective in disclosure scope" and defers broader validation, explicit gain decomposition, scaling-law characterization, and optimization details. It also claims additional continuous visual-environment validation without providing those results. These are disclosure limits, not evidence that omitted results support the architecture.[^loopwm-2026]

The attached human-evaluation PDF is unrelated to the reported ScienceWorld and AlfWorld evaluations: it is titled “Human evaluation results on Danmaku Chan” and compares a “Baseline VLM” with “LWM” on appropriateness, informativeness, engagingness, and human-likeness. Its presence, together with the manuscript's unrelated danmaku figure captions, makes it unusable as LoopWM evaluation evidence.[^loopwm-human-eval-2026][^loopwm-2026]

## Relationships

- **Evaluates:** [Looped World Models](looped-world-models.md).

[^loopwm-2026]: FaceMind Research Asia, “Looped World Models,” arXiv:2606.18208v1, [source](../raw/arXiv-2606.18208v1/draft.tex), Results, included `results_main_science.tex`, `results_main_alfworld.tex`, `deferred.tex`, and `limitations.tex`.

[^loopwm-human-eval-2026]: “Human evaluation results on Danmaku Chan,” [source PDF](../raw/arXiv-2606.18208v1/human_eval_combined.pdf), one rendered page, inspected 2026-08-01.
