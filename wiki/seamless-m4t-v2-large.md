---
type: Concept
title: SeamlessM4T v2 Large
description: 2.3B-parameter massively multilingual speech/text translation model with UnitY2 architecture covering 101 speech-input languages and 35 speech-output languages across S2ST, S2TT, T2ST, T2TT, and ASR tasks.
tags: [stt, tts, speech-translation, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T23:45:00Z }
stale_after: 2027-10-06
sources:
  - id: seamless-m4t-v2-card
    resource: ../raw/seamless-m4t-v2-large.md
    kind: documentation
    title: SeamlessM4T v2 model card (facebook/seamless-m4t-v2-large)
---

SeamlessM4T v2 Large (`facebook/seamless-m4t-v2-large`) is Meta's 2.3B-parameter foundational all-in-one massively multilingual and multimodal translation model for speech and text in nearly 100 languages, supporting speech-to-speech (S2ST), speech-to-text (S2TT), text-to-speech (T2ST), text-to-text (T2TT), and automatic speech recognition (ASR), built as a multitask adaptation of the novel UnitY2 architecture with hierarchical character-to-unit upsampling and non-autoregressive text-to-unit decoding that improves over v1 in quality and speech-generation inference speed (**Reported**).[^seamless-m4t-v2-card]

## Model identity and lineage

- Card title is `SeamlessM4T v2`; Hugging Face checkpoint is `facebook/seamless-m4t-v2-large` at 2.3B parameters; sibling rows are `SeamlessM4T-Large (v1)` at 2.3B and `SeamlessM4T-Medium (v1)` at 1.2B; license frontmatter is `cc-by-nc-4.0` (**Observed** by static inspection of frontmatter and model table).[^seamless-m4t-v2-card]
- Publisher lineage is Meta Seamless Communication; v2 is explicitly an updated version over SeamlessM4T v1 with the UnitY2 architecture; citation is the Seamless 2023 paper (`Seamless: Multilingual Expressive and Streaming Speech Translation`, arXiv) (**Reported**).[^seamless-m4t-v2-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, `inference: False`, metrics `bleu`, `wer`, `chrf`, and `audio-to-audio`, `text-to-speech`, `seamless_communication` tags; widget examples are two LibriSpeech FLAC samples with English transcripts (**Observed**).[^seamless-m4t-v2-card]

## Tasks and language coverage

- Five tasks: S2ST, S2TT, T2ST, T2TT, and ASR (**Reported**).[^seamless-m4t-v2-card]
- Header coverage claim: 101 languages for speech input, 96 languages for text input/output, 35 languages for speech output (**Reported**).[^seamless-m4t-v2-card]
- Language table uses `Sp` (speech) and `Tx` (text) markers with `Source` and `Target` columns; Vietnamese (`vie`, Latn) is `Sp, Tx` source and `Sp, Tx` target, so it is supported for speech and text input plus speech and text output (**Reported**).[^seamless-m4t-v2-card]
- Speech-output target set parsed from the table is 37 codes: arb, ben, cat, ces, cmn, cmn_Hant, cym, dan, deu, eng, est, fin, fra, hin, ind, ita, jpn, kor, mlt, nld, pes, pol, por, ron, rus, slk, spa, swe, swh, tel, tgl, tha, tur, ukr, urd, uzn, vie (*computed* from the table; header claims 35 — see [Contradictions](#contradictions)) (**Synthesis**).[^seamless-m4t-v2-card]
- Speech-only sources with no text and no target entry: ast, kam, kea, ltz, oci, xho, zlm (`Sp` source, `--` target); text-only entry: zsm (`Tx` source, `Tx` target) (**Reported**).[^seamless-m4t-v2-card]
- `seamlessM4T-medium` supports 200 text-modality languages based on NLLB-200 with a separate asset card pointer; that broader text coverage is not part of the Large v2 language table (**Reported**).[^seamless-m4t-v2-card]

## Architecture

- Multitask adaptation of the UnitY2 architecture with hierarchical character-to-unit upsampling and non-autoregressive text-to-unit decoding; the card states this considerably improves over SeamlessM4T v1 in quality and inference speed, with the speed claim scoped to speech generation tasks (**Reported**).[^seamless-m4t-v2-card]
- Architecture diagram `seamlessm4t_arch.svg` is referenced in the card but absent from `raw/` and was not inspected (**Synthesis**).[^seamless-m4t-v2-card]

## Checkpoints, metrics, and eval tooling

- Checkpoint pointers: Large v2 `seamlessM4T_v2_large.pt`, Large v1 `multitask_unity_large.pt`, Medium v1 `multitask_unity_medium.pt`; metrics bundles: `seamlessM4T_large_v2.zip`, `seamlessM4T_large.zip`, `seamlessM4T_medium.zip`; evaluation data IDs for FLEURS, CoVoST2, and CVSS-C via `evaluation_data_ids.zip` (**Reported**).[^seamless-m4t-v2-card]
- Extensive evaluation results for Large and Medium reported in the paper as averages are said to live in the `metrics` files above; no numeric WER, BLEU, chrF, or COMET table is printed in the card text itself (**Reported**).[^seamless-m4t-v2-card]
- Reproduction pointers: Evaluation README (`cli/m4t/evaluate`) and Finetuning README (`cli/m4t/finetune`) in the `seamless_communication` repository; neither was fetched or executed (**Reported**, with unfetched-pointer limit).[^seamless-m4t-v2-card]

## Inference and usage

- Transformers path requires installing 🤗 Transformers from main plus `sentencepiece`: `pip install git+https://github.com/huggingface/transformers.git sentencepiece` (**Reported**).[^seamless-m4t-v2-card]
- Text-to-speech-translation fence: `AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")` plus `SeamlessM4Tv2Model.from_pretrained(...)`, then `processor(text="Hello, my dog is cute", src_lang="eng", return_tensors="pt")` and `model.generate(**text_inputs, tgt_lang="rus")` (**Reported**).[^seamless-m4t-v2-card]
- Speech-input fence: load any waveform with `torchaudio`, resample to 16 kHz (`torchaudio.functional.resample(..., new_freq=16_000)`), then `processor(audios=audio, return_tensors="pt")` and `model.generate(**audio_inputs, tgt_lang="rus")` (**Reported**).[^seamless-m4t-v2-card]
- Playback uses `model.config.sampling_rate` via `IPython.display.Audio` or `scipy.io.wavfile.write`; pointers for more detail are the SeamlessM4T v2 Transformers docs and a hands-on Google Colab; install, download, transcription, synthesis, and listening steps were transcribed, not executed (**Reported**, with no-execution limit).[^seamless-m4t-v2-card]

## Trust, license, and limits

- License frontmatter is `cc-by-nc-4.0` (non-commercial); commercial voice-agent use needs a license review before shipping these weights (**Reported**; reading is **Synthesis**).[^seamless-m4t-v2-card]
- No training-data composition, compute, evaluation protocol, latency figures, VRAM requirements, streaming mode, timestamp support, punctuation behavior, voice-cloning controls, or safety/bias statement is given in this card; do not rely on this concept for those properties (**Synthesis**).[^seamless-m4t-v2-card]
- All capability, coverage, and quality/speed-improvement claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `stt`/`tts` domain rules (**Synthesis**).[^seamless-m4t-v2-card]

## Relationships

- Compared with [Canary-1b-v2](canary-1b-v2.md): Canary covers 25 European languages with X↔En translation and published WER/BLEU tables, while SeamlessM4T v2 Large covers ~100 languages with five translation/ASR directions but no numeric table in this card; Canary's card explicitly excludes Latvian because `seamless-m4t-v2-large`/`medium` lack it — cross-read both when scoping European translation pairs (**Synthesis**).[^seamless-m4t-v2-card]
- Compared with [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): that concept is an English/European offline ASR model whose card carries the same Latvian-exclusion note against Seamless; use Parakeet V3 for speed and Seamless v2 Large for mass-multilingual translation breadth (**Synthesis**).[^seamless-m4t-v2-card]
- Compared with [Index-Echo S2TT GGUF](index-echo-s2tt-gguf.md): that concept is Chinese-speech to English/Spanish/Japanese translation packaging for audio.cpp, while Seamless v2 Large is the native mass-multilingual S2ST/S2TT/T2ST/T2TT model; use both when scoping translation language pairs (**Synthesis**).[^seamless-m4t-v2-card]
- Compared with [Whisper Large v3](whisper-large-v3.md) and [Whisper Large v3 Turbo](whisper-large-v3-turbo.md): those concepts offer `task: translate` to English as an ASR-adjacent capability, while Seamless v2 Large offers dedicated many-to-many speech and text translation plus speech output; prefer Seamless when the target is non-English speech or text (**Synthesis**).[^seamless-m4t-v2-card]

## Contradictions

- **Speech-coverage counts:** the header claims 101 speech-input, 96 text in/out, and 35 speech-output languages, while a static count of the printed language table yields about 103 `Sp` source rows and 37 `Sp` target codes (list under [Tasks and language coverage](#tasks-and-language-coverage)). Neither value is chosen here; the gap may reflect counting of `cmn`/`cmn_Hant` variants or header rounding.[^seamless-m4t-v2-card]

## Coverage and limits

- Source inspected statically only; no Transformers install, no checkpoint download, no audio transcribed or synthesized, and no WER, BLEU, chrF, or latency figure reproduced (**Synthesis**).[^seamless-m4t-v2-card]
- Referenced but unfetched and absent from `raw/`: `seamlessm4t_arch.svg`; v2/v1/medium checkpoint `.pt` files; all three `metrics` zips; `evaluation_data_ids.zip`; Evaluation and Finetuning READMEs; Transformers docs page; Google Colab notebook; `facebook/seamless-m4t-v2-large` repository; FLEURS, CoVoST2, CVSS-C, and NLLB-200 assets; LibriSpeech widget clips (**Synthesis**).[^seamless-m4t-v2-card]
- Full per-language direction support is the card's language table (about 100 rows); this concept keeps the header aggregates, the 37-code speech-output list, the Vietnamese row, the speech-only/text-only outliers, and a pointer to the card for the complete matrix (**Synthesis**).[^seamless-m4t-v2-card]

[^seamless-m4t-v2-card]: [SeamlessM4T v2 model card](../raw/seamless-m4t-v2-large.md) — locators: frontmatter (`license: cc-by-nc-4.0`, `pipeline_tag`, `library_name: transformers`, `inference: False`, `metrics: bleu/wer/chrf`, `tags`, 100-plus-code `language` list, LibriSpeech widget samples); header intro (foundational all-in-one M4T, nearly 100 languages); task list (S2ST, S2TT, T2ST, T2ST, T2TT, ASR); coverage claim (101 speech-input, 96 text, 35 speech-output); v2/UnitY2 paragraph (hierarchical character-to-unit upsampling, non-autoregressive text-to-unit decoding, quality plus speech-generation speed over v1); `SeamlessM4T models` table (Large v2 2.3B `seamlessM4T_v2_large.pt` + `seamlessM4T_large_v2.zip`, Large v1 2.3B, Medium v1 1.2B, averages-in-metrics note, `evaluation_data_ids.zip` for FLEURS/CoVoST2/CVSS-C); `Evaluating`/`Finetuning` README pointers; `Transformers usage` (pip install fence, `AutoProcessor` + `SeamlessM4Tv2Model` text/audio fences with `src_lang`/`tgt_lang`, 16 kHz resample, `sampling_rate` playback, scipy save, docs + Colab links); `Supported Languages` table (`code/language/script/Source/Target`, `Sp`/`Tx` markers, `vie` Sp-Tx/Sp-Tx row, speech-only and `zsm` rows, medium-200/NLLB-200 note); `Citation` (Seamless 2023 bibtex).
