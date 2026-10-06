---
type: Concept
title: Omnilingual ASR
description: Open-source multilingual ASR family covering 1600+ languages with W2V, CTC, and LLM checkpoints plus unlimited-length variants, reporting CER below 10 for 78% of languages at 7B scale.
tags: [stt, asr, multilingual, low-resource-languages, zero-shot, fairseq2, offline, long-form]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: omnilingual-readme
    resource: ../raw/omnilingual-asr.md
    kind: documentation
    title: Omnilingual ASR README (1600+ languages)
---

Omnilingual ASR is Meta's open-source multilingual speech-recognition family covering 1600+ languages — including hundreds never previously covered by any ASR technology — built on fairseq2 with W2V self-supervised, CTC, and LLM-ASR checkpoints from 300M to 7B scales, whose 7B LLM-ASR system is reported as state of the art across those languages with character error rate (CER) below 10 for 78% of them (**Reported**).[^omnilingual-readme]

## Model identity and release

- Identity: `Omnilingual ASR: Open-Source Multilingual Speech Recognition for 1600+ Languages` from the Omnilingual ASR team (Meta); code and models are released under Apache 2.0 (**Reported**).[^omnilingual-readme]
- Upstream pointers named in the source: Hugging Face demo (`facebook/omniasr-transcriptions`), Hugging Face dataset (`facebook/omnilingual-asr-corpus`), paper (arXiv `2511.09690`, 2025), and blogpost (**Reported**).[^omnilingual-readme]
- Positioning claim: new languages can be added with just a few paired examples without requiring specialized expertise or large datasets, combining scalable zero-shot learning with a flexible model family (**Reported**).[^omnilingual-readme]
- No streaming/chunk-latency knob, timestamp, punctuation, hotword, diarization, or VAD claim appears in this source (**Synthesis**).[^omnilingual-readme]

## December 2025 update

- Two suites were released: accuracy-improved (CER) v2 checkpoints for the CTC and LLM-ASR models (`omniASR_{CTC,LLM}_{300M,1B,3B,7B}_v2`), and a new LLM-ASR variant supporting decoding on unlimited audio length (`omniASR_LLM_Unlimited_{300M,1B,3B,7B}_v2`) (**Reported**).[^omnilingual-readme]
- The unlimited-length models are briefly described in the linked architecture overview; their accuracy is described as comparable to the limited-length models, but finetuning recipes for the unlimited variant are currently not supported (**Reported**).[^omnilingual-readme]

## Model family and deployment figures

- Families: `omniASR_W2V` self-supervised checkpoints (300M/1B/3B/7B); `omniASR_CTC` ASR checkpoints (300M/1B/3B/7B, plus v2); `omniASR_LLM` ASR-with-optional-language-conditioning checkpoints (300M/1B/3B/7B, plus v2); `omniASR_LLM_Unlimited` v2 checkpoints (300M/1B/3B/7B); one `omniASR_LLM_7B_ZS` zero-shot ASR checkpoint; and three tokenizers (**Reported**).[^omnilingual-readme]
- Tokenizer mapping: `omniASR_tokenizer_v1` for all non-v2 models except `omniASR_LLM_7B`; `omniASR_tokenizer_v1_variant7` for the `omniASR_LLM_7B` architecture; `omniASR_tokenizer_written_v2` for all v2 architectures (each ~100 KiB) (**Reported**).[^omnilingual-readme]
- Measurement conditions for the table below: batch=1, 30 s audio, BF16, A100 for VRAM and real-time factor (RTF); relative speed is stated against `omniASR_LLM_7B`; parenthesized unlimited-variant figures use 15 min audio instead (**Reported**).[^omnilingual-readme]

| Checkpoint group | Parameters | Download (FP32) | Inference VRAM | RTF (relative speed) |
| --- | ---: | ---: | ---: | --- |
| W2V 300M / 1B / 3B / 7B (SSL) | 317,390,592 / 965,514,752 / 3,064,124,672 / 6,488,487,168 | 1.2 / 3.6 / 12.0 / 25.0 GiB | not stated | not stated [^omnilingual-readme] |
| CTC 300M / 1B / 3B / 7B (v1 and v2 share sizes) | 325,494,996 / 975,065,300 / 3,080,423,636 / 6,504,786,132 | 1.3 / 3.7 / 12.0 / 25.0 GiB | ~2 / ~3 / ~8 / ~15 GiB | 0.001 (96x) / 0.002 (48x) / 0.003 (32x) / 0.006 (16x) [^omnilingual-readme] |
| LLM 300M / 1B / 3B / 7B (v1 and v2 share sizes) | 1,627,603,584 / 2,275,710,592 / 4,376,679,040 / 7,801,041,536 | 6.1 / 8.5 / 17.0 / 30.0 GiB | ~5 / ~6 / ~10 / ~17 GiB | 0.090 (~1x) / 0.091 (~1x) / 0.093 (~1x) / 0.092 (~1x) [^omnilingual-readme] |
| LLM Unlimited 300M / 1B / 3B / 7B v2 | same as LLM row above | same as LLM row above | ~5 / ~6 / ~10 / ~17 GiB | 0.092 (~1x) (0.206) / 0.097 (~1x) (0.207) / 0.095 (~1x) (0.208) / 0.097 (~1x) (0.208) [^omnilingual-readme] |
| LLM 7B ZS (zero-shot ASR) | 7,810,900,608 | 30.0 GiB | ~20 GiB | 0.194 (~0.5x) [^omnilingual-readme] |

- Distribution: models download automatically on first use during training or inference and are stored under `~/.cache/fairseq2/assets/` (**Reported**).[^omnilingual-readme]
- Audio-length constraint: the source warns that currently only audio files shorter than 40 seconds are accepted for inference on the CTC and LLM model suites; whether that cap also binds the Unlimited variant is not stated in this capture, so the Unlimited variant's only firm long-form evidence here is its name plus the 15-minute RTF column (**Reported**; scope of the cap is **Unverified**).[^omnilingual-readme]

## Accuracy

- Headline result: the 7B LLM-ASR system achieves claimed state-of-the-art performance across 1600+ languages, with CER below 10 for 78% of those languages; per-language CER results plus training hours are deferred to a linked CSV (**Reported**).[^omnilingual-readme]
- The supporting result figure (`result_table.png`) and the per-language CSV were not present in `raw/` and were not inspected, so no per-language figure is recorded in this wiki (**Synthesis**).[^omnilingual-readme]

## Inference and language conditioning

- Runtime basis: models were developed with fairseq2 (reference inference pipeline works across platforms); audio support requires libsndfile (`brew install libsndfile` on Mac; extra Windows setup linked) (**Reported**).[^omnilingual-readme]
- Install: `pip install omnilingual-asr` or `uv add omnilingual-asr`; dataset extras via `pip install "omnilingual-asr[data]"` (**Reported**).[^omnilingual-readme]
- Minimal inference fence: `ASRInferencePipeline(model_card="omniASR_LLM_Unlimited_7B_v2")`, then `pipeline.transcribe(audio_files, lang=lang, batch_size=2)` over FLAC/WAV paths (**Reported**).[^omnilingual-readme]
- Language conditioning: languages follow `{language_code}_{script}` (e.g. `eng_Latn` for English/Latin, `cmn_Hans` for Mandarin/Simplified); the full 1600+ list is read programmatically from `supported_langs` in `src/omnilingual_asr/models/wav2vec2_llama/lang_ids.py`, and the worked example transcribes `eng_Latn` plus `deu_Latn` files (**Reported**).[^omnilingual-readme]

## Data and training

- Dataset: `facebook/omnilingual-asr-corpus` on Hugging Face under CC-BY-4.0, usable directly with the inference pipeline for evaluation or testing; the worked fence streams one language split (e.g. Ligurian `lij_Latn`), converts `audio` entries to `{waveform, sample_rate}` inputs, transcribes with `omniASR_LLM_7B_v2` at `batch_size=2`, and compares against `raw_text` (**Reported**).[^omnilingual-readme]
- Corpus-creation context: the header collage shows on-the-ground transcription-gathering photos from Pakistan and Liberia (**Reported**; images not in `raw/`, treated as decorative).[^omnilingual-readme]
- Finetuning path: released checkpoints are finetuned via the data-preparation guide plus the wav2vec2 CTC/LLM finetuning-recipe guide (both linked local workflow paths, not in `raw/` and not inspected) (**Reported**).[^omnilingual-readme]
- Documentation map (linked, not inspected): inference pipeline, architecture overview, asset/card configuration system, data preparation, and training recipes (**Reported**).[^omnilingual-readme]

## Relationships

- Uses fairseq2 as the modeling toolkit and libsndfile for audio support, with Hugging Face (`datasets`, model demo, corpus dataset) as the distribution and evaluation surface (**Synthesis**).[^omnilingual-readme]
- Contrasts with the wiki's mid-coverage multilingual ASR lines — [Qwen3-ASR family](qwen3-asr-family.md) (30 languages plus dialects), Fun-ASR-MLT-Nano (31 languages), Nemotron 3.5 ASR (40 locales), and VibeVoice-ASR (50+ languages) — as the broadest-coverage option here by an order of magnitude, at the cost of larger downloads (up to 30 GiB FP32) and A100-class VRAM figures rather than CPU/edge packaging (**Synthesis**).[^omnilingual-readme]
- Complements long-form options such as [Audio8 ASR Infinite](audio8-asr-infinite.md) (native clocked streaming with rolling KV) and [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) (tunable streaming delay): the Unlimited variant addresses unbounded-length decoding inside an offline LLM-ASR family, but this source publishes no chunk/latency knob or streaming evaluation for it (**Synthesis**).[^omnilingual-readme]

## Coverage and limits

- Source inspected statically only; no `pip install`, checkpoint download, transcription, or benchmark was executed, and no CER, VRAM, or RTF figure was reproduced (**Synthesis**).[^omnilingual-readme]
- Not in `raw/` and not inspected: header/result images, the per-language CER-plus-training-hours CSV, the `src/omnilingual_asr/...` model and inference trees, the `workflows/...` dataprep/recipe trees, the LICENSE file, and all external targets (Hugging Face demo, dataset, paper, blogpost, fairseq2, libsndfile, checkpoint URLs) (**Synthesis**).[^omnilingual-readme]
- All capability, accuracy, speed, and finetuning claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^omnilingual-readme]

[^omnilingual-readme]: [Omnilingual ASR README](../raw/omnilingual-asr.md) — locators: header (1600+ languages, few-paired-examples claim, HF demo/dataset/paper/blogpost links, 7B-LLM-ASR SOTA caption with CER-below-10-for-78% and per-language CSV pointer); `December 2025 Update` (`omniASR_{CTC,LLM}_{300M,1B,3B,7B}_v2` accuracy suite, `omniASR_LLM_Unlimited_{300M,1B,3B,7B}_v2` unlimited suite, comparable-accuracy and no-finetuning-recipes notes, architecture-overview pointer); `Installation` (fairseq2 basis, libsndfile fences, `pip install omnilingual-asr` / `uv add omnilingual-asr`); `Inference` (`ASRInferencePipeline(model_card="omniASR_LLM_Unlimited_7B_v2")` + `transcribe(audio_files, lang, batch_size=2)` fence, 40-second warning); `Supported Languages` (`{language_code}_{script}` format, `eng_Latn`/`cmn_Hans` examples, `lang_ids.py::supported_langs`); `Using the HuggingFace Dataset` (CC-BY-4.0 `facebook/omnilingual-asr-corpus`, `omnilingual-asr[data]` extra, `lij_Latn` streaming fence with `waveform`/`sample_rate`/`raw_text`); `Model Architectures` table (W2V/CTC/LLM/Unlimited/ZS parameter, download, VRAM, RTF columns; footnotes 1 batch-1/30 s/BF16/A100, 2 relative to `omniASR_LLM_7B`, 3 15 min numbers; tokenizer rows); `Model Download & Storage` (`~/.cache/fairseq2/assets/`); `Architecture Documentation` (W2V/CTC/LLM directory pointers); `Training` (dataprep + finetuning-recipe pointers); `License` (Apache 2.0); `Citation` (team/author list, arXiv 2511.09690).
