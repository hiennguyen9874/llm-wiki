---
type: Concept
title: KVoiceWalk Scoring Function
description: KVoiceWalk's hybrid candidate score, which combines Resemblyzer target similarity, self-similarity, and audio-feature similarity through a harmonic mean, with the author's rationale, example sub-scores, and an unstated formula.
tags: [tts, kokoro, voice-cloning, scoring, resemblyzer, harmonic-mean]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T05:00:07Z }
stale_after: 2027-04-13
sources:
  - id: kvoicewalk-readme
    resource: ../raw/kvoicewalk.md
    kind: documentation
    title: KVoiceWalk README capture
---

KVoiceWalk ranks each candidate voice tensor with one Score built from three sub-scores: **Target Sim** (similarity of the synthesized speech to the target recording, measured with Resemblyzer), **Self Sim** (consistency of the voice across different texts), and **Feature Sim** (similarity of audio features to the target). The author says the terms are combined by a harmonic mean that tolerates some backsliding on any one term while the others improve, and that Feature Sim carries a lower weight (**Reported**).[^kvoicewalk-readme] The README gives no formula, weights, feature set, or score scale, so this concept cannot recompute the Score. It stays `draft` until the scoring code is inspected.

## Components

| Term | What the README says it measures | Author's reason | Locator |
| --- | --- | --- | --- |
| Target Sim | Similarity to the target audio, via Resemblyzer | The walk's objective; Resemblyzer-only scoring produced "overfitted garbage" | lines 2, 102 |
| Self Sim | Consistency of the voice across inputs; the second passage is `--other_text` | Keeps the model producing the same-sounding voice for different inputs, and marks stability | lines 102, 149 |
| Feature Sim | Audio-feature comparison to the target; the features are not named | Blocks poor-quality audio that passes the first two checks; weighted lower so the voice stays in bounds | lines 104, 106 |
| Harmonic mean | Combines the three terms into the Score | Lets one term backslide while others improve, avoiding "quick and sad stagnation" | line 106 |

All entries are **Reported**.[^kvoicewalk-readme]

## Example values

The README's three example rows (see [KVoiceWalk](kvoicewalk.md#reported-example-run)) are the only numeric evidence for the Score. Under an unweighted harmonic mean of the three sub-scores, the rows give 0.658 (`af_heart.pt`), 0.571 (interpolated voice), and 0.755 (walked tensor). Their README Scores are 81.22, 84.20, and 92.99, which are about 123, 147, and 123 times those values. A fixed scale would give a constant ratio, so the README's weights, extra terms, or scaling must differ from the unweighted form (**Synthesis** from the listed numbers).[^kvoicewalk-readme]

The log line also reports `Diversity:0.01` at step 9371 (line 97). The README does not define Diversity or say whether it affects selection.[^kvoicewalk-readme]

## Interpretation

- Scores compare candidates within one run, against one target and one `--other_text` passage. The README gives no scale that holds across targets, so Scores from different targets should not be compared (**Synthesis**).
- Target Sim is a [Resemblyzer](resemblyzer.md) speaker-similarity measure. Its numbers are not comparable with the speaker-similarity percentages in [CosyVoice2-0.5B](cosyvoice2-0.5b.md), which come from a different evaluation protocol and test set (**Synthesis**).
- The README says `--target_text` must contain the words spoken in the target audio (line 146). Target Sim therefore assumes the synthesized text matches the target's content (**Synthesis**).

## Contradictions

- **Harmonic mean versus example Scores.** The author says the Score uses a harmonic mean (line 106). The example sub-scores (lines 89–97) do not reproduce the Scores under an unweighted harmonic mean, and the README gives no weights or scale. Neither the stated form nor a fitted form is chosen here.[^kvoicewalk-readme]

## Coverage and limits

- **Inspected statically:** the README lines that describe the score (lines 2, 24–35, 86–106, 109, 146–149). No code was inspected, so the feature set, Resemblyzer settings, weights, and Diversity definition are unknown.
- **Not executed:** no scoring was run, and no sub-score was reproduced.
- **Blocking gap:** the scoring implementation is not captured. Inspecting it (and the related `main.py` path) is needed before this concept can move to `stable`.

## Relationships

- Part of [KVoiceWalk](kvoicewalk.md). The Score decides which candidate replaces the current voice during the walk (line 95) (**Reported**).[^kvoicewalk-readme]
- Uses [Resemblyzer](resemblyzer.md) for Target Sim (lines 2, 102). The library's own README is compiled in that concept.
- Scores the output of [Kokoro-82M](kokoro-82m.md) synthesis (line 179) (**Synthesis**).

[^kvoicewalk-readme]: [KVoiceWalk README capture](../raw/kvoicewalk.md) — locators: line 2 scoring-method summary; lines 25–33 example audio labels; lines 86–99 example outputs with Target, Self, Feature, Score, and Diversity values; lines 101–106 design (Resemblyzer-only failure, self similarity, feature similarity, harmonic mean, lowered feature weight); line 109 early returns on bad tensors; lines 146–149 `--target_text` and `--other_text` help; line 179 device support across Resemblyzer scoring.
