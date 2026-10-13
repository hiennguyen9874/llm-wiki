---
type: Concept
title: Speaker-Attributed ASR Metrics
description: Definitions, micro aggregation, and comparability caveats for WER, WDER, cpWER, and SpkCntMAE as implemented by the DiarizationLM toolkit, whose text normalization differs from the paper's internal scorer.
tags: [vad, diarization, metrics, evaluation, stt]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:15:00Z }
stale_after: 2027-10-13
sources:
  - id: diarizationlm-readme
    resource: ../raw/DiarizationLM.md
    kind: code
    title: DiarizationLM README (google/speaker-id repository; no revision recorded)
---

Speaker-attributed ASR scoring separates transcript accuracy from speaker-attribution accuracy and speaker-count accuracy. The [DiarizationLM toolkit](diarizationlm-toolkit.md) reports four scores: WER, WDER, cpWER, and SpkCntMAE. Its README names each metric and links a reference, states that WER, WDER, and cpWER are micro metrics over a whole dataset, and says its scorer is a best-effort replication of the paper's internal implementation that differs mainly in text normalization (**Reported**).[^diarizationlm-readme] Numbers from this toolkit are comparable with other papers only after normalization and aggregation are matched (**Synthesis**).

## Definitions

| Metric | Name in README | Reference given by README | Status in this capture |
| --- | --- | --- | --- |
| WER | Word Error Rate | Wikipedia article (not fetched) | Formula not captured |
| WDER | Word Diarization Error Rate | arXiv 1907.05337 | Formula not captured |
| cpWER | Concatenated minimum-permutation Word Error Rate | arXiv 2004.09249 | Formula not captured |
| SpkCntMAE | Speaker Count Mean Absolute Error | arXiv 2210.13690 | Formula not captured |

The README gives names and references only, so formulas are **Unverified** here (**Reported** names).[^diarizationlm-readme]

## Aggregation

- The README says the WER, WDER, and cpWER reported in the paper are micro metrics, with numerators and denominators aggregated over the entire dataset (**Reported**).[^diarizationlm-readme]
- It then presents `compute_metrics_on_json_dict()` for the JSON format, so the toolkit is implied to compute micro scores, but no sentence says so explicitly (**Synthesis**).
- The README describes no macro or per-session averaging (**Observed** absence).

## Computing with the toolkit

- `compute_metrics_on_json_dict(json_dict)` reads an `utterances` list with `utterance_id`, `hyp_text`, `hyp_spk`, `ref_text`, and `ref_spk`, and returns a dictionary with keys `WER`, `WDER`, `cpWER`, and `SpkCntMAE` (**Reported**).[^diarizationlm-readme]
- `compute_metrics_on_json.py --input=... --output=...` writes the same metrics for a JSON file (**Reported**).[^diarizationlm-readme]
- After LLM post-processing, `--hyp_spk_field="hyp_spk_llm"` scores the corrected speakers instead of the original hypothesis speakers (**Reported**).[^diarizationlm-readme]
- The README's example reference text is punctuated and capitalized (`"Hello. Good morning, how are you?"`), so text normalization is part of the scoring path (**Observed**).[^diarizationlm-readme]

## Comparability caveats

- The README attributes the gap between its package and the paper's internal scorer mainly to text normalization, "such as de-punctuation" (**Reported**).[^diarizationlm-readme] It does not give the normalization rules, so a match with a paper's table cannot be confirmed from this capture (**Unverified**).
- The [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md) benchmark table says its scores come from this function with Hungarian matching (**Reported** in that concept). The README never mentions Hungarian matching, so that step is **Unverified** against code.
- Other concepts that report cpWER, such as [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md), used their own scorers. Their normalization and aggregation were not checked here (**Synthesis**).

## Coverage and limits

- Coverage: the README's `### Metrics` section and its usage examples only (**Synthesis**). `metrics.py`, `compute_metrics_on_json.py`, and the cited papers were not captured or fetched, and no metric was recomputed or executed.
- Status is `draft` because formulas, matching, and normalization rules remain outstanding.
- Sensitive values: none (**Observed**).

## Relationships

- Depends on: the [DiarizationLM toolkit](diarizationlm-toolkit.md) `metrics.py` as the reference implementation (**Reported**).[^diarizationlm-readme]

[^diarizationlm-readme]: [DiarizationLM README](../raw/DiarizationLM.md) — locators: `## Overview` (paper and checkpoint links); `## Instructions` > `### Metrics` (WER, WDER, cpWER, SpkCntMAE names and reference links; micro-metric sentence; `compute_metrics_on_json_dict()` example and return keys; `compute_metrics_on_json.py --input --output`; `--hyp_spk_field="hyp_spk_llm"`; "best-effort" and "de-punctuation" normalization sentence; example reference text); `### Data format` (`utterances` fields); `## Citation`. Unavailable: no revision, commit, or version recorded; `metrics.py`, `compute_metrics_on_json.py`, and the linked papers were not captured or fetched.
