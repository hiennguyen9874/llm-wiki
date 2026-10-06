---
type: Concept
title: Cohere Transcribe Arabic 07-2026
description: Open-source 2B-parameter Conformer encoder-decoder ASR model for Arabic, dialects, and English with Transformers and vLLM serving and best-average WER/CER on the Open Universal Arabic ASR Leaderboard as of 07.07.2026.
tags: [stt, asr, arabic, english, conformer]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T21:00:00Z }
stale_after: 2027-10-06
sources:
  - id: cohere-arabic-card
    resource: ../raw/cohere-transcribe-arabic-07-2026.md
    kind: documentation
    title: Cohere Transcribe Arabic model card
---

Cohere Transcribe Arabic (`CohereLabs/cohere-transcribe-arabic-07-2026`) is an open-source 2B-parameter Arabic automatic speech recognition model with a Conformer encoder plus lightweight Transformer decoder, natively supported in Transformers with a vLLM serving path, covering Arabic, Arabic dialects, and English, and reported as the best-average system on the Open Universal Arabic ASR Leaderboard as of 07.07.2026 with 25.87% WER and 11.80% CER average (**Reported**).[^cohere-arabic-card]

## Model identity and lineage

- Model name is `cohere-transcribe-arabic-07-2026`; developers are Cohere and Cohere Labs; contact is `labs@cohere.com`; license is Apache 2.0; base model is `CohereLabs/cohere-transcribe-03-2026`; citation revision is `0a8193c` via the card BibTeX (doi `10.57967/hf/9549`) (**Reported**).[^cohere-arabic-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, languages `ar` and `en`, and tags including `arabic-asr` and `arabic-dialect` (**Observed** by static inspection).[^cohere-arabic-card]
- Intro positions it for Arabic ASR, Arabic audio transcription, dialectal Arabic speech recognition, and English speech-to-text, including Arabic-English code-switched speech — but the Limitations section qualifies this, stating single-language in-distribution use performs best, there is no explicit automatic language detection, and code-switched performance is inconsistent; treat the intro code-switch claim as qualified by that limitation (**Reported**, with qualification as **Synthesis**).[^cohere-arabic-card]

## Architecture and I/O

- Architecture is a conformer-based encoder-decoder: a large Conformer encoder extracts acoustic representations followed by a lightweight Transformer decoder for token generation, trained with supervised cross-entropy on output tokens (**Reported**).[^cohere-arabic-card]
- Input is an audio waveform converted to log-Mel spectrogram, automatically resampled to 16 kHz when necessary, with multi-channel (stereo) inputs averaged to a single channel; output is transcribed text (**Reported**).[^cohere-arabic-card]

## Inference and serving

- Transformers is the recommended offline path (`transformers>=5.4.0` plus `torch`, `huggingface_hub`, `soundfile`, `librosa`, `sentencepiece`, `protobuf`, `accelerate`): `AutoProcessor.from_pretrained(...)` plus `CohereAsrForConditionalGeneration.from_pretrained(..., device_map="auto")`, then `processor(audio, sampling_rate=16000, return_tensors="pt", language="ar")` moved to the model device/dtype and `model.generate(**inputs, max_new_tokens=256)` with `processor.decode(outputs, skip_special_tokens=True)`; English uses `language="en"` (**Reported**).[^cohere-arabic-card]
- Long-form audio beyond the feature extractor's `max_audio_clip_s` is automatically split into chunks, and the processor reassembles per-chunk transcriptions using the returned `audio_chunk_index` (passed back into `processor.decode(..., audio_chunk_index=audio_chunk_index, language="ar")`); the card's example also computes RTFx as audio duration divided by elapsed time (**Reported**).[^cohere-arabic-card]
- vLLM is the recommended production path: install `vllm==0.19.0` plus `vllm[audio]` and `librosa` (Python 3.12 venv in the example), serve with `vllm serve CohereLabs/cohere-transcribe-arabic-07-2026 --trust-remote-code`, and transcribe via the OpenAI-compatible `POST /v1/audio/transcriptions` endpoint with `file` and `model` form fields (**Reported**).[^cohere-arabic-card]
- A commented-out `punctuation=False/True` control block is present in the card source but not rendered, so punctuation control is not documented as an available option; a Hugging Face demo Space is linked but not evaluated here (**Observed** by static inspection).[^cohere-arabic-card]

## Benchmarks

All numbers below are source assertions from the card's leaderboard table dated 07.07.2026; nothing was executed or reproduced for this wiki (**Synthesis**).[^cohere-arabic-card]

- Open Universal Arabic ASR Leaderboard average (WER down, CER second row): Cohere Transcribe Arabic 07-2026 leads at 25.87 / 11.80, ahead of OmniASR LLM 7B at 28.32 / 12.52, OmniASR LLM 3B at 29.96 / 13.77, OmniASR LLM 1B at 29.96 / 13.40, Cohere Transcribe 03-2026 at 30.67 / 16.37, Qwen3-Omni 30B at 30.71 / 13.67, NVIDIA Conformer-CTC with LM at 32.91 / 13.84, OmniASR LLM 300M at 32.96 / 14.84, Gemma 4 E4B at 32.98 / 13.71, Qwen3-ASR 1.7B at 33.36 / 12.33, Voxtral-Small 24B at 34.47 / 15.29, NVIDIA Conformer-CTC greedy at 34.74 / 13.37, Gemma 4 E2B at 35.87 / 15.34, and Whisper Large v3 at 36.86 / 17.21 (**Reported**).[^cohere-arabic-card]
- Per-subset wins (WER / CER): SADA 37.47 / 23.53, Common Voice 5.82 / 1.62, and Casablanca 49.71 / 20.66 are best-in-table for this model; MASC clean 19.60 / 6.45, MASC noisy 27.07 / 10.13, and MGB-2 15.54 / 8.40 are not — MASC clean/noisy are led by Cohere Transcribe 03-2026 at 8.66 / 2.97 and 19.01 / 7.71, and MGB-2 by Qwen3-Omni 30B at 13.09 / 6.20 (**Reported**).[^cohere-arabic-card]
- Live leaderboard and write-ups live outside `raw/`: the Open Universal Arabic ASR Leaderboard Space, technical release post, and Cohere announcement post are referenced but unfetched (**Synthesis**).[^cohere-arabic-card]

## Strengths and limitations

- Stated strengths: strong transcription accuracy for Arabic and English, and efficient inference as a dedicated Conformer encoder-decoder recognition model (**Reported**).[^cohere-arabic-card]
- Stated limitations: best in a single pre-specified language with no explicit automatic language detection and inconsistent code-switched performance; no timestamps and no speaker diarization; eager transcription of non-speech (hallucinates low-volume floor noise), so the card recommends prepending a noise gate or VAD model (**Reported**).[^cohere-arabic-card]

## Relationships

- Alternative to [Qwen3-ASR family](qwen3-asr-family.md): that family covers Arabic among 30 languages with streaming/offline inference and timestamp prediction via a forced aligner, while this concept is the Arabic-specialized option with the leaderboard evidence above; the card's table carries a `Qwen3-ASR 1.7B` column as a baseline, so cross-read both when choosing between multilingual and Arabic-focused ASR (**Synthesis**).[^cohere-arabic-card]
- Preceded by [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) (declared `base_model`): the base leads the MASC clean/noisy subsets while this Arabic-tuned model leads the average, SADA, Common Voice, and Casablanca subsets — compare per-subset rows rather than averages alone when the deployment dialect mix is known (**Synthesis**).[^cohere-arabic-card]

## Coverage and limits

- Source inspected statically only; no package installed, no model downloaded, no audio transcribed, and no WER, CER, or RTFx figure reproduced (**Synthesis**).[^cohere-arabic-card]
- Linked but unfetched and absent from `raw/`: Hugging Face demo Space, vLLM installation docs, technical and announcement blog posts, leaderboard Space, and every benchmark dataset (SADA, Common Voice, MASC clean/noisy, MGB-2, Casablanca); install, inference, and serving fences are transcribed, not executed (**Synthesis**).[^cohere-arabic-card]
- All capability, accuracy, and ranking claims are source assertions without independent verification in this wiki; model-release and benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^cohere-arabic-card]

[^cohere-arabic-card]: [Cohere Transcribe Arabic model card](../raw/cohere-transcribe-arabic-07-2026.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, `language`, `tags`, `base_model`); spec table (Name, Architecture, Input, Output, Model, Training objective, Languages, License rows); header intro (2B-parameter claim, Arabic/dialects/English/code-switch scope, Conformer encoder-decoder plus Transformers support, Cohere/Cohere Labs credit); `Usage` install fence and Quick Start fence (`AutoProcessor`, `CohereAsrForConditionalGeneration`, `device_map="auto"`, `language="ar"`, `max_new_tokens=256`); `Long-form transcription` details fence (`max_audio_clip_s`, `audio_chunk_index`, RTFx computation); commented `Punctuation control` block; `English transcription` details (`language="en"`); `vLLM Integration` details (`vllm==0.19.0`, `vllm[audio]`, `vllm serve ... --trust-remote-code`, `POST /v1/audio/transcriptions` curl); `Results` leaderboard details dated 07.07.2026 (Average/SADA/Common Voice/MASC clean/MASC noisy/MGB-2/Casablanca WER plus CER table with 14-model comparison); `Resources` (technical post, announcement post, leaderboard links); `Strengths and Limitations` (accuracy/efficiency bullets; single-language/code-switch, timestamps/diarization, silence/VAD bullets); `Model Card Contact` and Terms (`labs@cohere.com`, Apache 2.0); `Citation` BibTeX (authors, revision `0a8193c`, year 2026, doi `10.57967/hf/9549`).
