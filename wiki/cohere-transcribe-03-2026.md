---
type: Concept
title: Cohere Transcribe 03-2026
description: Open-source 2B-parameter Conformer encoder-decoder ASR model covering 14 languages with Transformers and vLLM serving and best-average 5.42% WER on the English Open ASR Leaderboard snapshot of 03.26.2026.
tags: [stt, asr, multilingual, conformer]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T21:00:00Z }
stale_after: 2027-10-06
sources:
  - id: cohere-03-2026-card
    resource: ../raw/cohere-transcribe-03-2026.md
    kind: documentation
    title: Cohere Transcribe model card
---

Cohere Transcribe 03-2026 (`CohereLabs/cohere-transcribe-03-2026`) is an open-source 2B-parameter multilingual automatic speech recognition model with a Conformer encoder plus lightweight Transformer decoder, natively supported in Transformers with a vLLM serving path, covering 14 languages, and reported as the best-average system (5.42% WER) on the English Open ASR Leaderboard snapshot dated 03.26.2026 (**Reported**).[^cohere-03-2026-card]

## Model identity and lineage

- Model name is `cohere-transcribe-03-2026`; developers are Cohere and Cohere Labs; contact is `labs@cohere.com`; license is Apache 2.0; citation revision is `d96e814` via the card BibTeX (doi `10.57967/hf/8653`) (**Reported**).[^cohere-03-2026-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, 14 language codes (`ar de el en es fr it ja ko nl pl pt vi zh`), and tags including `hf-asr-leaderboard` (**Observed** by static inspection).[^cohere-03-2026-card]
- Language scope: 9 European (English, French, German, Italian, Spanish, Portuguese, Greek, Dutch, Polish), 4 APAC (Chinese Mandarin, Japanese, Korean, Vietnamese), and Arabic — 14 total (**Reported**).[^cohere-03-2026-card]

## Architecture and I/O

- Architecture is a conformer-based encoder-decoder: a large Conformer encoder extracts acoustic representations followed by a lightweight Transformer decoder for token generation, trained from scratch with supervised cross-entropy on output tokens (**Reported**).[^cohere-03-2026-card]
- Input is an audio waveform converted to log-Mel spectrogram, automatically resampled to 16 kHz when necessary, with multi-channel (stereo) inputs averaged to a single channel; output is transcribed text (**Reported**).[^cohere-03-2026-card]

## Inference and serving

- Transformers is the recommended offline path (`transformers>=5.4.0` plus `torch`, `huggingface_hub`, `soundfile`, `librosa`, `sentencepiece`, `protobuf`, `accelerate`; `datasets` only for long-form and non-English examples; tested with `torch==2.10.0`): `AutoProcessor.from_pretrained(...)` plus `CohereAsrForConditionalGeneration.from_pretrained(..., device_map="auto")`, then `processor(audio, sampling_rate=16000, return_tensors="pt", language="en")` moved to the model device/dtype and `model.generate(**inputs, max_new_tokens=256)` with `processor.decode(outputs, skip_special_tokens=True)` (**Reported**).[^cohere-03-2026-card]
- Long-form audio beyond the feature extractor's `max_audio_clip_s` is automatically split into chunks, and the processor reassembles per-chunk transcriptions using the returned `audio_chunk_index` (passed back into `processor.decode(..., audio_chunk_index=audio_chunk_index, language="en")`); the card's 55-minute earnings-call example computes RTFx as audio duration divided by elapsed time (**Reported**).[^cohere-03-2026-card]
- Punctuation is controllable and enabled by default: `punctuation=True` keeps casing and punctuation, while `punctuation=False` yields lower-cased output without punctuation marks (**Reported**).[^cohere-03-2026-card]
- Batched inference accepts multiple files in one call; when the batch mixes short-form and long-form audio, the processor handles chunking and reassembly (decode again takes `audio_chunk_index` and `language`) (**Reported**).[^cohere-03-2026-card]
- Non-English transcription selects any of the 14 supported languages via the `language` code (card example transcribes Japanese FLEURS audio with `language="ja"`) (**Reported**).[^cohere-03-2026-card]
- vLLM is the recommended production path: install `vllm==0.19.0` plus `vllm[audio]` and `librosa` (Python 3.12 venv in the example), serve with `vllm serve CohereLabs/cohere-transcribe-03-2026 --trust-remote-code`, and transcribe via the OpenAI-compatible `POST /v1/audio/transcriptions` endpoint with `file` and `model` form fields (**Reported**).[^cohere-03-2026-card]

## Benchmarks

All numbers below are source assertions from the card's English leaderboard table dated 03.26.2026; nothing was executed or reproduced for this wiki (**Synthesis**).[^cohere-03-2026-card]

- Average WER (lower is better): Cohere Transcribe 5.42 leads Zoom Scribe v1 at 5.47, IBM Granite 4.0 1B Speech at 5.52, NVIDIA Canary Qwen 2.5B at 5.63, Qwen3-ASR-1.7B at 5.76, ElevenLabs Scribe v2 at 5.83, Kyutai STT 2.6B at 6.40, OpenAI Whisper Large v3 at 7.44, and Voxtral Mini 4B Realtime 2602 at 7.68 (**Reported**).[^cohere-03-2026-card]
- Per-set WERs for Cohere Transcribe: AMI 8.15, Earnings22 10.84, Gigaspeech 9.33, LibriSpeech clean 1.25, LibriSpeech other 2.37, SPGISpeech 3.08, Tedlium 2.49, Voxpopuli 5.87; best-in-table cells are its average, AMI, and both LibriSpeech splits, while Earnings22 (IBM Granite 8.48), Gigaspeech (Qwen3-ASR 8.74), SPGISpeech (Zoom Scribe 1.59), Tedlium (Qwen3-ASR 2.28), and Voxpopuli (Zoom Scribe 5.37) go to competitors (**Reported**).[^cohere-03-2026-card]
- Human-preference evaluation (head-to-head annotator judgments on accuracy, coherence, usability, hallucination avoidance, named entities, and verbatim formatting; 50%+ means preferred on average) and per-language error rates (averaged over FLEURS, Common Voice 17.0, MLS, and Wenet where relevant; CER for zh/ja/ko, WER otherwise) are presented as images only, so no numeric values are recorded here (**Observed** by static inspection; image content excluded).[^cohere-03-2026-card]
- Live leaderboard and write-ups live outside `raw/`: the Open ASR Leaderboard Space, technical release post, and Cohere announcement post are referenced but unfetched (**Synthesis**).[^cohere-03-2026-card]

## Strengths and limitations

- Stated strengths: best-in-class transcription accuracy in 14 languages as a dedicated model, trained from scratch for accuracy with production readiness in mind, and efficient inference with a real-time factor up to three times faster than other dedicated ASR models in the same size range — stated without hardware or protocol detail (**Reported**).[^cohere-03-2026-card]
- Stated limitations: best in a single pre-specified language with no explicit automatic language detection and inconsistent code-switched performance; no timestamps and no speaker diarization; eager transcription of non-speech (hallucinates low-volume floor noise), so the card recommends prepending a noise gate or VAD model (**Reported**).[^cohere-03-2026-card]

## Ecosystem

- Supported or packaged outside the card's own fences: `transformers`, `vLLM`, `mlx-audio` for Apple Silicon, Rust `cohere_transcribe_rs`, an in-browser WebGPU demo via `transformers.js`, a Chrome extension, `nano-cohere-transcribe` for fast long-form audio, iOS Whisper Memos, Android Whisperian, and Linux `hyprwhspr` — all linked but unfetched and unevaluated here (**Reported**, with availability as **Synthesis**).[^cohere-03-2026-card]

## Relationships

- Followed by [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md): that model declares this one as its `base_model`; the base leads the English 8-set average and LibriSpeech splits here, while the Arabic-tuned model leads the Open Universal Arabic average — compare per-subset rows rather than averages alone when the deployment language mix is known (**Synthesis**).[^cohere-03-2026-card]
- Alternative to [Canary-Qwen-2.5B](canary-qwen-2.5b.md): that English-only SALM reports 5.63 mean WER at RTFx 418 in the same table band, while this concept covers 14 languages with a punctuation toggle and no timestamps — cross-read both when choosing between multilingual breadth and English-only SALM reuse (**Synthesis**).[^cohere-03-2026-card]
- Uses [Silero VAD](silero-vad.md): the card's silence limitation recommends a noise gate or VAD frontend, and Silero VAD is the wiki's compiled CPU-first VAD option (**Synthesis**).[^cohere-03-2026-card]

## Coverage and limits

- Source inspected statically only; no package installed, no model downloaded, no audio transcribed, and no WER or RTFx figure reproduced (**Synthesis**).[^cohere-03-2026-card]
- Linked but unfetched and absent from `raw/`: Hugging Face demo Space and demo WAV, vLLM installation docs, technical and announcement blog posts, leaderboard Space, benchmark datasets (AMI, Earnings22, Gigaspeech, LibriSpeech, SPGISpeech, Tedlium, Voxpopuli, FLEURS, Common Voice, MLS, Wenet), the two benchmark figures (human-preference and per-language plots, image-only with no extractable numbers), and all ten ecosystem integrations; install, inference, and serving fences are transcribed, not executed (**Synthesis**).[^cohere-03-2026-card]
- All capability, accuracy, ranking, and speed claims are source assertions without independent verification in this wiki; model-release and benchmark details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^cohere-03-2026-card]

[^cohere-03-2026-card]: [Cohere Transcribe model card](../raw/cohere-transcribe-03-2026.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, `language` codes, `tags`); spec table (Name, Architecture, Input, Output, Model size 2B, Model, Training objective, Languages 14-group list, License rows); header intro (2B claim, 14-language scope, Conformer encoder-decoder plus Transformers support, Cohere/Cohere Labs credit, demo link); `Usage` install fence (`transformers>=5.4.0`, `torch==2.10.0` tested) and Quick Start fence (`AutoProcessor`, `CohereAsrForConditionalGeneration`, `device_map="auto"`, `language="en"`, `max_new_tokens=256`, `voxpopuli_test_en_demo.wav`); `Long-form transcription` details fence (`max_audio_clip_s`, `audio_chunk_index`, 55-minute earnings22 RTFx computation); `Punctuation control` details fence (`punctuation=True/False`, default enabled); `Batched inference` details fence (mixed short/long chunking, `audio_chunk_index` decode); `Non-English transcription` details fence (FLEURS `ja_jp`, `language="ja"`); `vLLM Integration` details (`vllm==0.19.0`, `vllm[audio]`, `vllm serve ... --trust-remote-code`, `POST /v1/audio/transcriptions` curl); `Results` English leaderboard details dated 03.26.2026 (Average/AMI/Earnings22/Gigaspeech/LS clean/LS other/SPGISpeech/Tedlium/Voxpopuli WER table with 9-model comparison; human-preference figure; per-language figure with CER-for-zh-ja-ko note); `Resources` (technical post, announcement post, leaderboard links); `Strengths and Limitations` (accuracy/efficiency bullets incl. 3x RTF claim; single-language/code-switch, timestamps/diarization, silence/VAD bullets); `Ecosystem support` (transformers, vLLM, mlx-audio, cohere_transcribe_rs, WebGPU demo, Chrome extension, nano-cohere-transcribe, Whisper Memos, Whisperian, hyprwhspr); `Model Card Contact` and Terms (`labs@cohere.com`, Apache 2.0); `Citation` BibTeX (authors, revision `d96e814`, year 2026, doi `10.57967/hf/8653`).
