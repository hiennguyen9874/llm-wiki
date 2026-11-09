---
type: Concept
title: Italian translation weight-edit experiment
description: A reported sparse Gemma weight edit targets an Italian tense preference while comparing related and unrelated translation side effects.
tags: [ml, translation, interpretability]
status: draft
created: 2026-11-09
generated: { by: llm-wiki-agent/1, at: 2026-11-09T08:27:44Z }
sources:
  - id: reddit-italian-edit
    resource: ../raw/i_tried_mits_weightspace_programming_on_my_own.md
    kind: article
    title: "I tried MIT's weight-space programming on my own use case"
---

**Reported:** A Reddit author used Claude Opus 5.5 to edit Gemma 4 12B weights for a contextual English-to-Italian tense preference, without gradients or training. The author reports improved target-sentence results and fewer changes to unrelated translations than several baselines, but the result is one self-reported experiment, not a general demonstration of safe or superior editing.[^reddit-italian-edit]

## Task and intervention

**Reported:** The target is a past ongoing situation interrupted by another event, where the author prefers an Italian imperfect construction such as “si nascondeva ... da mesi” to “si era nascosto ... per mesi.” For an already-ended period the prior tense should remain; the aim is a context-sensitive preference rather than a blanket tense substitution. The author says a middle-layer linear probe almost perfectly separated ongoing from ended cases and that Claude rewrote eight MLP neurons as a conditional switch to nudge verb choice. The setup offered a Python kernel over weights and 50 forward passes on practice sentences, without gradients. The author reports approximately 92,000 of 11.9 billion parameters changed and a roughly 100 KB diff; the capture does not explain the diff encoding.[^reddit-italian-edit]

**Synthesis:** Probe separability alone does not establish that the model uses the probed distinction causally in its original verb selection, or that the proposed switch is the unique explanation for the edited behavior.[^reddit-italian-edit]

## Reported evaluation

The first two columns are the percentage of unseen target sentences still using the old form (lower matches the author's preference); broken controls are related sentences pushed into a wrong reading (lower is better); unrelated unchanged counts identical outputs among 200 translations (higher is more unchanged, not necessarily better quality).[^reddit-italian-edit]

| Method | Test 1 old form | Independent test 2 old form | Controls broken | Unrelated unchanged / 200 |
| --- | ---: | ---: | ---: | ---: |
| Base Gemma | 26% | 32% | — | 200 |
| System prompt | 4% | 2% | 49 | 82 |
| Difference-of-means ablation | 49% | 75% | 53 | 43 |
| LoRA | 12% | 23% | 0 | 120 |
| Hand edit | 5% | 16% | 2 | 182 |

**Reported:** The author says LoRA performed better inside paragraphs. Two of three runs reportedly succeeded and independently arrived at a similar switch design; the third crashed, which the author attributes to their own harness. The capture does not specify test sample sizes, control denominator, model and decoding settings, annotation procedure, uncertainty, or baseline tuning budgets. The stated 50-pass budget is not enough to infer equal compute or search effort across methods.[^reddit-italian-edit]

## Disputed interpretation

The author's preference treats the imperfect example as expressing ongoing hiding at discovery. A commenter identifying as a northern Italian native instead argues that this wording suggests repeated acts of hiding and that the past-perfect form describes hiding once and remaining hidden. These are competing interpretations of the example; this capture does not adjudicate Italian usage or establish that the preferred form is universally better.[^reddit-italian-edit]

## Relationships

- **Uses:** [Weight-space programming](weight-space-programming.md) describes the broader direct-weight-editing approach, including bounded feedback.
- **Related:** [LLM-directed neural weight editing](llm-directed-neural-weight-editing.md) covers other model repairs and cautions about side effects.

## Evidence and coverage

The inspected source is a standalone English Reddit capture by u/FeydRowan with comments and a canonical Reddit link. It provides no publication or capture date, license, immutable model revision, or local attachments. The linked experiment repository, code, edits, agent logs, baselines, MIT source, and other external links were not inspected; no experiment was executed or independently verified. A commenter explicitly notes that limited controls cannot rule out distant regressions. Speculative comments and unrelated discussions were excluded. Draft status reflects these evidence and coverage limits.[^reddit-italian-edit]

[^reddit-italian-edit]: Reddit capture, opening example and setup, “Results on sentences it never saw,” and comments beginning “Maybe I'm missing something here” and “Si nascondeva da mesi is the wrong translation.”
