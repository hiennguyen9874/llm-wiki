---
type: Concept
title: Nemotron 3.5 ASR Streaming 0.6B
description: NVIDIA 600M-parameter cache-aware FastConformer-RNNT streaming multilingual ASR model covering 40 language-locales with language-ID prompting, configurable 80 ms–1.12 s chunks, and published FLEURS WER plus H100 throughput figures.
tags: [stt, asr, streaming, multilingual, fastconformer, rnnt, nemo]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: nemotron-35-asr-card
    resource: ../raw/nemotron-3.5-asr-streaming-0.6b.md
    kind: documentation
    title: Nemotron 3.5 ASR model card
---

Nemotron 3.5 ASR (`nvidia/nemotron-3.5-asr-streaming-0.6b`) is NVIDIA's 600M-parameter multilingual streaming ASR model that transcribes 40 language-locales from a single cache-aware FastConformer-RNNT checkpoint via language-ID prompt conditioning, with native punctuation and capitalization, configurable 80/160/320/560/1120 ms operating points, optional automatic language detection with emitted language tags, and published FLEURS accuracy plus single-H100 concurrency curves (**Reported**).[^nemotron-35-asr-card]

## Identity and lineage

- Card title is `Nemotron 3.5 ASR`; model version is `nemotron-3.5-asr-streaming-0.6b-v1`; Hugging Face release is 06/04/2026; license is OpenMDW-1.1; deployment geography is Global; use case is transcription of multilingual audio; card states the model is ready for commercial use (**Reported**).[^nemotron-35-asr-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: nemo`, languages covering 40 locales (en, es, de, fr, it, ar, ja, ko, pt, ru, hi, zh, vi, he, nl, cs, da, pl, no, sv, th, tr, bg, el, et, fi, hr, hu, lt, lv, ro, sk, uk, mt, sl), datasets `nvidia/Granary`, `multilingual_librispeech`, `fleurs`, `common_voice_8_0`, `voxpopuli`, `europarl`, and tags including `streaming-asr`, `cache-aware ASR`, `FastConformer`, `RNNT`, `Parakeet`, `NeMo`, and `multilingual` (**Observed** by static inspection).[^nemotron-35-asr-card]
- Multilingual extension of `nvidia/nemotron-speech-streaming-en-0.6b`, adding language-ID prompt conditioning to reach 40 language-locales from one model; the card recommends the English-only predecessor for English-only transcription and Nemotron 3.5 ASR for all other transcription-ready locales (**Reported**).[^nemotron-35-asr-card]

## Architecture and I/O

- Architecture type is FastConformer-CacheAware-RNNT with Prompt: cache-aware streaming Parakeet (FastConformer) encoder with 24 layers plus an RNN-T decoder and language-ID prompt conditioning (**Reported**).[^nemotron-35-asr-card]
- Fusion path: FastConformer encoder emits an acoustic embedding of shape (D=1024, T); a 128-dim one-hot language vector is expanded across time to (K=128, T); concatenation gives (D+K, T); a projection layer maps the fused features to the RNNT decoder (**Reported**).[^nemotron-35-asr-card]
- Streaming mechanism maintains caches for all encoder self-attention and convolution layers so only new non-overlapping audio chunks are processed while cached context is reused, eliminating the redundant overlapping computation of traditional buffered streaming (**Reported**).[^nemotron-35-asr-card]
- Input is mono audio (`wav`, 1D) plus a language ID string; maximum audio length is GPU-memory bound with no preprocessing needed; output is a 1D text string in the input language with punctuation and capitalization and no maximum character length; card notes faster training/inference on NVIDIA GPUs via CUDA versus CPU-only (**Reported**).[^nemotron-35-asr-card]

## Supported languages and language detection

- 40 language-locales in three tiers; 32 produce out-of-box transcription and 8 require fine-tuning (**Reported**).[^nemotron-35-asr-card]
- Transcription-ready (19 locales): English en-US/en-GB, Spanish es-US/es-ES, French fr-FR/fr-CA, Italian it-IT, Portuguese pt-BR/pt-PT, Dutch nl-NL, German de-DE, Turkish tr-TR, Russian ru-RU, Arabic ar-AR, Hindi hi-IN, Japanese ja-JP, Korean ko-KR, Vietnamese vi-VN, Ukrainian uk-UA (**Reported**).[^nemotron-35-asr-card]
- Broad-coverage (13 locales): Polish pl-PL, Swedish sv-SE, Czech cs-CZ, Norwegian Bokmål nb-NO, Danish da-DK, Bulgarian bg-BG, Finnish fi-FI, Croatian hr-HR, Slovak sk-SK, Mandarin zh-CN, Hungarian hu-HU, Romanian ro-RO, Estonian et-EE (**Reported**).[^nemotron-35-asr-card]
- Adaptation-ready (8 locales, tokenizer-recognized only): Greek el-GR, Lithuanian lt-LT, Latvian lv-LV, Maltese mt-MT, Slovenian sl-SI, Hebrew he-IL, Thai th-TH, Norwegian Nynorsk nn-NO; fine-tune on in-domain data to unlock full transcription (**Reported**).[^nemotron-35-asr-card]
- Automatic detection via `target_lang=auto` / `language="auto"`: the model detects the spoken language and appends an `<xx-XX>` tag after the terminal punctuation, so mixed-language traffic is transcribed and labeled without a separate language-ID component; NeMo controls this with `strip_lang_tags` (`false` keeps the tag, `true` strips it) and Transformers controls it with `skip_special_tokens` (`False` keeps the tag, `True` strips it) (**Reported**).[^nemotron-35-asr-card]

## Streaming operating points

- Five runtime chunk sizes, switchable at inference without retraining to move along the latency–accuracy Pareto curve: 80, 160, 320, 560, and 1120 ms (**Reported**).[^nemotron-35-asr-card]
- NeMo `att_context_size` mapping in 80 ms frames with left context 56 (**Reported**):[^nemotron-35-asr-card]

| `att_context_size` | Chunk size | Latency |
| --- | --- | --- |
| [56, 0] | 1 frame | 0.08 s |
| [56, 1] | 2 frames | 0.16 s |
| [56, 3] | 4 frames | 0.32 s |
| [56, 6] | 7 frames | 0.56 s |
| [56, 13] | 14 frames | 1.12 s |

## Throughput and efficiency

All figures below are source assertions measured on a single H100; throughput is sustainable parallel real-time streams and latency is median final-token latency at a given concurrency; nothing was reproduced for this wiki (**Synthesis**).[^nemotron-35-asr-card]

- Despite roughly half the parameters (0.6B vs 1.1B), Nemotron 3.5 ASR sustains far more concurrent streams than buffered Parakeet RNNT 1.1B multilingual: about 17x more at 80 ms (240 vs 14) and 6x more at 1120 ms (2,400 vs 400); Nemotron holds low final-token latency past 1,000 parallel requests while the Parakeet curve saturates after a few hundred (**Reported**).[^nemotron-35-asr-card]

## Benchmarks (FLEURS)

All numbers below are source assertions from the card's FLEURS test-set tables in LangID-provided and auto-detect modes across the five chunk sizes; WER in percent except Japanese, Korean, and Mandarin which use CER; normalization aligns casing, punctuation, numerals, and formatting before scoring and the card warns residual mismatches can inflate error rates; nothing was executed or reproduced for this wiki (**Synthesis**).[^nemotron-35-asr-card]

- Transcription-ready average (15 locales incl. CER languages): LangID 10.38 / 10.00 / 9.49 / 9.12 / 8.84 from 80 ms to 1.12 s; auto-detect 11.14 / 10.67 / 10.05 / 9.63 / 9.21 (**Reported**).[^nemotron-35-asr-card]
- Broad-coverage average (12 of 13 locales tabulated): LangID 25.86 / 25.14 / 24.11 / 23.09 / 22.13; auto-detect 27.62 / 26.65 / 25.41 / 24.44 / 23.09 (**Reported**).[^nemotron-35-asr-card]
- Retrieval anchors at 1.12 s LangID: Spanish 4.11, Italian 4.25, Portuguese 5.48, Hindi 6.81, Korean CER 7.12, English 7.91, German 8.31, French 9.03; Vietnamese 11.18 (80 ms: 13.41); Japanese CER 11.48; Arabic 12.03; Ukrainian 13.07; broad-coverage best Polish 15.15 and worst Hungarian 28.68 / Danish 27.49 / Estonian 26.35 / Romanian 25.90 (**Reported**).[^nemotron-35-asr-card]
- Auto-detect penalty is small on high-resource Latin-script languages (Spanish 4.13, Italian 4.32, Portuguese 5.47, French 9.02 at 1.12 s) and larger where language confusion costs more (Hindi 8.23 vs 6.81, Russian 10.03 vs 9.17, Ukrainian 14.59 vs 13.07, Bulgarian 21.84 vs 20.53, Croatian 27.46 vs 23.97 at 1.12 s) (**Reported**).[^nemotron-35-asr-card]
- Frontmatter `model-index` spot-checks match the 1.12 s LangID column for English 7.91, Spanish 4.11, French 9.03, Italian 4.25, Portuguese 5.48, German 8.31, Hindi 6.81, and Korean 7.12 (**Observed** by static inspection).[^nemotron-35-asr-card]

## Training data and procedure

- Trained on speech across 40 language-locales (10,000 to 1M hours, audio modality) as a dynamic blend normalized to spoken-form text with punctuation and capitalization: proprietary NVIDIA Riva multilingual ASR training set plus NVIDIA Granary, Multilingual LibriSpeech, Mozilla Common Voice, FLEURS, and VoxPopuli / Europarl-ASR; collection method listed as Human (**Reported**).[^nemotron-35-asr-card]
- Labeling is Human plus Synthetic: synthetic labels come from an ensemble of Canary, Parakeet Multilingual 1.1B RNNT, Parakeet CTC 1.1B, Whisper-large-v3, and FunASR, with punctuation and capitalization generated by Qwen3-32B (**Reported**).[^nemotron-35-asr-card]
- Evaluation sets named in the card are FLEURS, Mozilla Common Voice, Multilingual LibriSpeech, and NVIDIA internal multilingual sets, with Human collection and labeling (**Reported**).[^nemotron-35-asr-card]

## Inference and usage

- NeMo-Speech.cpp local path: download `nemotron-3.5-asr-streaming-0.6b.q8_0.gguf` into `models/` and run `nemo-speech transcribe audio.wav --model <gguf> --language en-US` (or another locale, or `auto`) (**Reported**).[^nemotron-35-asr-card]
- NeMo path (Python 3.11+, Cython, recent PyTorch; `libsndfile1 ffmpeg`; `nemo_toolkit[asr]` from GitHub main): `ASRModel.from_pretrained(model_name="nvidia/nemotron-3.5-asr-streaming-0.6b")`, then the cache-aware streaming script `examples/asr/asr_cache_aware_streaming/speech_to_text_cache_aware_streaming_infer.py` with `target_lang` locale or `auto`, `att_context_size`, `strip_lang_tags`, batch size, manifest, and output path (**Reported**).[^nemotron-35-asr-card]
- Transformers path (requires `transformers>=5.13.0`, class `Nemotron3_5Asr` / `AutoModelForRNNT`): `pipeline("automatic-speech-recognition", model=...)` defaulting to the index-0 `en-US` prompt, offline `AutoProcessor` plus `generate` with `language="en-US"` or `"auto"`, and chunked streaming with `set_num_lookahead_tokens(6)` / `streaming_latency_ms`, per-chunk `language` prompt, `TextIteratorStreamer`, and a generator-threaded `model.generate` loop (**Reported**).[^nemotron-35-asr-card]
- Software/hardware envelope: runtime NeMo 26.06; microarchitectures Ampere, Blackwell, Hopper, Jetson, Lovelace, Turing, Volta; operating systems Linux and Linux 4 Tegra; card adds V-model unit/system testing guidance for deployment (**Reported**).[^nemotron-35-asr-card]

## Trust, license, and limits

- License is OpenMDW-1.1; ethical framing is NVIDIA Trustworthy AI shared responsibility with developer-side fitness-for-use testing and a security-vulnerability reporting link (**Reported**).[^nemotron-35-asr-card]
- Fine-tuning pointer: the card links a fine-tuning blog post with before/after results for improving covered languages (**Reported**).[^nemotron-35-asr-card]
- Sibling pointers in the card: English-only Nemotron ASR Streaming, Multitalker Parakeet Streaming, and [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md) (now ingested here), plus Speech NIM, NeMo documentation, and Nemotron developer pages (**Reported**).[^nemotron-35-asr-card]

## Relationships

- Extends [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md): that concept covers the English-only 0.6B cache-aware base; use it when tracing the 0.6B lineage, and treat this concept as the multilingual successor (**Synthesis**).[^nemotron-35-asr-card]
- Compared as a baseline in [Audio8 ASR Infinite](audio8-asr-infinite.md): that concept's evaluation table reports Nemotron 3.5 ASR at 560 ms on Aishell and LibriSpeech sets against Audio8 and Voxtral realtime; read both when contrasting bilingual native-streaming (Audio8) against multilingual cache-aware chunked streaming (Nemotron) (**Synthesis**).[^nemotron-35-asr-card]
- Shares the 0.6B cache-aware FastConformer streaming lineage with [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md), which fine-tunes the English 0.6B streaming base for overlapped multitalker transcription fronted by streaming diarization (**Synthesis**).[^nemotron-35-asr-card]
- Contrast endpointing strategy with [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md): that concept covers the lightweight 120M English streaming model with inline `<EOU>`-token turn-taking at 80–160 ms latency, versus this page's 0.6B punctuated multilingual transcription with inference-time chunk-size selection (**Synthesis**).[^nemotron-35-asr-card]
- Compare multilingual ASR coverage and accuracy with [Canary-1b-v2](canary-1b-v2.md), [Qwen3-ASR family](qwen3-asr-family.md), and [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md): Nemotron 3.5 ASR's differentiator in this wiki is streaming-first cache-aware inference with inference-time chunk-size selection and H100 concurrency figures over 40 locales (**Synthesis**).[^nemotron-35-asr-card]

## Coverage and limits

- Source inspected statically only; no NeMo / NeMo-Speech.cpp / Transformers install, no model or GGUF download, no audio transcribed, and no WER/CER, throughput, or final-token-latency figure reproduced (**Synthesis**).[^nemotron-35-asr-card]
- Referenced but unfetched and absent from `raw/`: `model_overview.png`, `throughput_vs_chunk.png`, `model_architecture.png`, `fleurs_wer_vs_chunk_size.png`, `fleurs_langid_vs_auto.png`, `latency_vs_parallel.png`; Hugging Face model page, NeMo-Speech.cpp repository, NeMo repository and streaming inference script, Transformers docs, fine-tuning blog post, Granary / MLS / Common Voice / FLEURS / VoxPopuli / Europarl-ASR datasets, Parakeet RNNT 1.1B comparator page, and the four numbered paper/framework references; all install and inference fences are transcribed, not executed (**Synthesis**).[^nemotron-35-asr-card]
- Full per-language evidence is the card's two FLEURS matrices (15 transcription-ready plus 12 broad-coverage locales × 5 chunk sizes × LangID/auto); this concept keeps tier lists, averages, retrieval anchors, auto-detect gaps, and the Vietnamese/English operating curve for triage and points to the card for the complete matrix; adaptation-ready locales have no accuracy figures in the source (**Synthesis**).[^nemotron-35-asr-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^nemotron-35-asr-card]

[^nemotron-35-asr-card]: [Nemotron 3.5 ASR model card](../raw/nemotron-3.5-asr-streaming-0.6b.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, `language` list, `datasets`, `tags`, `model-index` 1.12 s LangID spot WERs); header badges (600M params, multilingual, OpenMDW-1.1); intro (600M, multilingual streaming plus batch, PnC, 80/160/320/560/1120 ms chunks, cache-aware reuse claim, commercial-use line); `Release Date` (06/04/2026 HF link); `Why Choose` (single-model 40 locales, streaming, throughput/cost, runtime Pareto, PnC, fine-tune blog link); `Supported Languages` (3-tier table with all locale codes; 32-out-of-box vs 8-finetune notes; English-only recommendation; `target_lang=auto` language-tag tip); `Model Architecture` (FastConformer-CacheAware-RNNT with Prompt, 24 layers, RNNT decoder, D=1024 / K=128 fusion equations, non-overlapping-cache claim, English-base lineage); `Results at a Glance` and `Throughput & Efficiency` (FLEURS WER-vs-chunk trend, LangID-vs-auto chart, 0.6B-vs-1.1B 240-vs-14 @80 ms and 2400-vs-400 @1120 ms with ~17x/6x ratios, H100 single-GPU note, final-token-latency-vs-concurrency chart); `How to Use` (NeMo-Speech.cpp `hf download` + `nemo-speech transcribe` fences with `--language`; NeMo install + `from_pretrained` + `speech_to_text_cache_aware_streaming_infer.py` fences with `target_lang`/`att_context_size`/`strip_lang_tags`; Transformers `>=5.13.0` pipeline/offline/streaming fences with `language`, `set_num_lookahead_tokens`, `TextIteratorStreamer`); `Input(s)`/`Output` (mono wav + lang-ID string, GPU-memory max length, punctuated string, CUDA note); `Software Integration` (NeMo 26.06, 7 microarchitectures, Linux/Linux4Tegra, V-model note); `Model Version(s)` (v1); `Training and Evaluation Datasets` (40 locales, Riva + Granary + MLS + Common Voice + FLEURS + VoxPopuli/Europarl list, 10k–1M hours, Human collection/labeling, Canary/Parakeet-RNNT/Parakeet-CTC/Whisper/FunASR ensemble plus Qwen3-32B PnC, eval-set list); `Performance` (transcription-ready 15-row and broad-coverage 12-row FLEURS WER/CER matrices × 5 chunks × LangID/auto with averages, ja/ko CER note, normalization caveat); `Adaptation-ready` (8-locale list + finetune note); `License/Terms` (OpenMDW-1.1), `Deployment Geography` (Global), `Use Case`; `References [1]-[4]`; `Ethical Considerations` (Trustworthy AI + vulnerability link).
