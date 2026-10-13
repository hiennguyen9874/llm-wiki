---
type: Concept
title: DiarizationLM Toolkit
description: Google speaker-id `diarizationlm` package for LLM speaker-turn post-processing of ASR transcripts, with its JSON data format, transcript-preserving speaker transfer, LLM training-data preparation, completion parser, metrics, and links to the released Gemma and Llama checkpoints.
tags: [vad, diarization, speaker-tagging, stt, llm, post-processing, tooling]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:15:00Z }
stale_after: 2027-10-13
sources:
  - id: diarizationlm-readme
    resource: ../raw/DiarizationLM.md
    kind: code
    title: DiarizationLM README (google/speaker-id repository; no revision recorded)
---

DiarizationLM uses a large language model to post-process the speaker labels of an ASR transcript. The `diarizationlm` Python package, published from the `google/speaker-id` repository, releases only some of the paper's functions and tools: a JSON data format, word-to-text speaker conversion, transcript-preserving speaker transfer (TPST), a prompt builder for LLM training data, a completion parser, and speaker-attributed metrics. The README also links open checkpoints fine-tuned on Fisher and multi-domain telephone and meeting corpora, but the paper's PaLM 2 models and internal tooling are not disclosed (**Reported**).[^diarizationlm-readme]

## Identity

- Package `diarizationlm` on PyPI, installed with an unpinned `pip install diarizationlm`; repository `google/speaker-id` per the README badges (**Reported**).[^diarizationlm-readme]
- Disclaimer: "This is NOT an official Google product" (**Reported**).[^diarizationlm-readme]
- Paper: Wang et al., "DiarizationLM: Speaker Diarization Post-Processing with Large Language Models", Interspeech 2024, pp. 3754–3758, DOI 10.21437/Interspeech.2024-209; arXiv 2401.03506 (**Reported**).[^diarizationlm-readme]
- No revision, commit, or version is recorded in the README (**Observed**).

## Pipeline

The README sections run in this order (**Synthesis** from section order; its pipeline diagram is not captured):

1. An ASR hypothesis with per-word speaker labels is stored in the JSON data format.
2. Word and speaker sequences are converted to the text representation, which serves as the LLM prompt material.
3. The LLM produces completions for each segment.
4. The completion parser truncates the output, joins segments per utterance, and transfers speakers back onto the original hypothesis.
5. Metrics compare the corrected speakers with the reference.

## Data format and representations

- Data is a JSON object whose `utterances` list holds `utterance_id`, `hyp_text` and `hyp_spk` (space-joined word and speaker sequences), `hyp_diarized_text` (for debugging and prompt construction), and `ref_*` counterparts (**Reported**).[^diarizationlm-readme]
- Word sequence `["good", "morning", "how", "are", "you"]` with speakers `[1, 1, 2, 2, 2]` converts to the text form `<spk:1> good morning <spk:2> how are you` (**Reported**).[^diarizationlm-readme]
- `create_diarized_text()` converts word and speaker sequences to text, and `extract_text_and_spk()` converts text back, both in `diarizationlm/utils.py` (**Reported**).[^diarizationlm-readme]

## Transcript-preserving speaker transfer (TPST)

- `transcript_preserving_speaker_transfer(src_text, src_spk, tgt_text, tgt_spk) -> str`, in `diarizationlm/utils.py`, takes speaker labels from a source hypothesis and applies them to a target transcript. The README calls it a "critical" algorithm used in several places in the paper (**Reported**).[^diarizationlm-readme]
- The name suggests the target transcript's words are kept, but the README prints no output for its example (source 9 words, target 8 words), so word preservation is **Unverified**.[^diarizationlm-readme]
- The example is not executed here. Its algorithm figure (`resources/TPST_algorithm.png`) is not captured, so the matching rules are **Unverified**.
- The completion parser's third step transfers speakers to the original hypothesis, but the README does not name the function it calls (**Unverified**).

## Training data preparation

- `train_data_prep.py` segments prompts and completions to input and output length limits, optionally adds prefix and suffix, and writes prompt–completion pairs as `tfrecord`, `json`, `csv`, or `jsonl` (**Reported**).[^diarizationlm-readme]
- The README example sets `--prompt_suffix=" --> "` and `--completion_suffix=" [eod]"`, the separator and end marker that the [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md) card describes (**Observed** match).
- Length units are not stated (**Unverified**). Segmentation parameters can also be set in Python through `PromptOptions` in `utils.py` (**Reported**).[^diarizationlm-readme]

## Fine-tuning and inference paths

| Checkpoint (per README) | Training data | Repository named in README | Wiki concept |
| --- | --- | --- | --- |
| Gemma 4 E4B, "best overall" | Fisher, Callhome, ICSI, AMI | `diarizers-community/DiarizationLM-Gemma-4-E4B-v1` | [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md) |
| Llama 3 8B | Fisher | `google/DiarizationLM-8b-Fisher-v2` | none |
| Llama 2 13B | Fisher | `google/DiarizationLM-13b-Fisher-v1` | none |

- Open checkpoints: the Gemma and Llama fine-tuning and inference scripts live in an `unsloth` folder that is not captured (**Reported**).[^diarizationlm-readme]
- OpenAI path: the README warns that fine-tuning is "very costly" and that reproducibility "is not guaranteed". It converts CSV with `openai tools fine_tunes.prepare_data` and then runs `openai api fine_tunes.create`. `run_finetuned_gpt.py` requires `--api_key` and `--engine` (**Reported**).[^diarizationlm-readme] The legacy CLI syntax is **Unverified** against current OpenAI tooling.

## Completion parser

`postprocess_completions.py` performs three steps (**Reported**).[^diarizationlm-readme]

1. Truncate the completion suffix and any text after it.
2. Concatenate the completions of all segments from the same utterance.
3. Transfer the speakers to the original hypothesis ASR transcript.

The metrics section expects the parser's output in a field named `hyp_spk_llm` (**Reported**).[^diarizationlm-readme]

## Metrics

`metrics.py` implements WER, WDER, cpWER, and SpkCntMAE. See [Speaker-Attributed ASR Metrics](speaker-attributed-asr-metrics.md) for definitions, aggregation, and comparability caveats (**Reported**).[^diarizationlm-readme]

## Contradictions

- **Speaker tag format.** The Gemma card describes input with `<speaker:N>` tags, while this README's text representation writes `<spk:N>` and presents `create_diarized_text()` as the route for building prompts (**Observed** difference). Neither tag is chosen here, and the effect on model outputs is **Unverified**. See [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md#contradictions).
- **Output format count.** The README says "3 different output file formats" and then lists four: `tfrecord`, `json`, `csv`, and `jsonl` (**Observed**).[^diarizationlm-readme]
- **Repository owner.** The README links the Gemma 4 E4B weights and GGUF demo Space under `diarizers-community/`, while the Gemma card's code uses `google/`. The owner is unresolved (**Observed**). See the Gemma concept's contradictions.

## Coverage and limits

- Coverage: one README (`raw/DiarizationLM.md`) inspected statically across badges, overview, disclaimer, install, data format, representations, TPST, training preparation, both fine-tuning paths, completion parser, metrics, and citation. Nothing was installed, imported, executed, tested, or downloaded (**Synthesis**).
- Not captured: the `diarizationlm` source (`utils.py`, `train_data_prep.py`, `postprocess_completions.py`, `metrics.py`, `compute_metrics_on_json.py`, `run_finetuned_gpt.py`), `testdata/example_data.json`, the `unsloth` scripts, the paper, the PyPI and Hugging Face pages, and the demo Space. The TPST internals and parser behavior therefore remain **Unverified**.
- Figures excluded: `resources/diagram.png`, `resources/TPST_algorithm.png`, and `resources/DiarizationLM_Bard_demo.gif` are not in `raw/`, and the prose does not reproduce the diagram or algorithm, so pipeline and TPST claims rest on text alone.
- License: the README states none (**Observed** absence). The Gemma card's Apache-2.0 declaration covers its weights, not this package, so the package license is unresolved.
- Badges, CI and coverage links, and download counters are decorative and excluded.
- Sensitive values: none. `--api_key` is named as a flag with no value (**Observed**).

## Relationships

- Owned by: the `google/speaker-id` GitHub repository, per the README badges, with the disclaimer above (**Reported**).[^diarizationlm-readme]
- Checkpoint usage: the Gemma concept records that its usage path relies on this package for speaker transfer and metrics (**Reported** there). See [DiarizationLM-Gemma-4-E4B-v1](diarizationlm-gemma-4-e4b-v1.md).
- Metric definitions and comparability live in [Speaker-Attributed ASR Metrics](speaker-attributed-asr-metrics.md); the cpWER-reporting [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md) must be checked for normalization before any numeric comparison (**Synthesis**).

[^diarizationlm-readme]: [DiarizationLM README](../raw/DiarizationLM.md) — locators: badges (PyPI, GitHub Actions, Hugging Face, arXiv); `## Overview` (paper and checkpoint links, GGUF demo Space, `diarizers-community/` Gemma link, "some functions and tools" sentence); `## Disclaimer`; `## Instructions` > `### Install the package` (`pip install diarizationlm`, TPST example), `### Data format` (field table), `### Conversion between representations` (`create_diarized_text()`, `extract_text_and_spk()`, `<spk:N>` example), `### Transcript-preserving speaker transfer (TPST)` (signature in `diarizationlm/utils.py`, algorithm figure reference), `### Training data preparation` (`train_data_prep.py` flags, formats list, "3 different output file formats", `PromptOptions`), `### LLM finetuning and inference (OpenAI)` (cost and reproducibility warnings, `fine_tunes` commands, `run_finetuned_gpt.py`), `### LLM finetuning and inference (Gemma & Llama)` (checkpoint list, `unsloth` folder), `### Completion parser` (three steps), `### Metrics` (WER, WDER, cpWER, SpkCntMAE; micro-metric sentence; `compute_metrics_on_json_dict()`; `compute_metrics_on_json.py`; `--hyp_spk_field="hyp_spk_llm"`; normalization caveat); `## Citation` (Interspeech 2024 BibTeX). Unavailable: no revision, commit, or version recorded; `resources/` figures, the package source, `testdata/`, `unsloth/` scripts, and linked pages were not captured or fetched.
