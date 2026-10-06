---
type: Concept
title: ASR/STT Model Survey
description: Survey of every ASR/STT model compiled in the wiki — NVIDIA Parakeet, Nemotron, and Canary; Qwen3-ASR; Fun-ASR and SenseVoice; GLM-ASR; AutoArk ARK and Audio8; VibeVoice-ASR; MOSS-Transcribe; Cohere Arabic; Whisper runtimes — compared by architecture, size, languages, streaming mode, license, reported benchmarks, and edge packaging.
tags: [stt, asr, survey, comparison, streaming, multilingual, benchmarks, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:10:21Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-ctc-card
    resource: ../raw/parakeet-ctc-0.6b.md
    kind: documentation
    title: Parakeet CTC 0.6B (en)
  - id: parakeet-ctc-11-card
    resource: ../raw/parakeet-ctc-1.1b.md
    kind: documentation
    title: Parakeet CTC 1.1B (en)
  - id: parakeet-rnnt-card
    resource: ../raw/parakeet-rnnt-0.6b.md
    kind: documentation
    title: Parakeet RNNT 0.6B (en)
  - id: parakeet-rnnt-11-card
    resource: ../raw/parakeet-rnnt-1.1b.md
    kind: documentation
    title: Parakeet RNNT 1.1B (en)
  - id: parakeet-tdt-card
    resource: ../raw/parakeet-tdt-0.6b-v2.md
    kind: documentation
    title: Parakeet TDT 0.6B V2 (En)
  - id: parakeet-v3-card
    resource: ../raw/parakeet-tdt-0.6b-v3.md
    kind: documentation
    title: Parakeet TDT 0.6B V3 multilingual model card
  - id: canary-1b-v2-card
    resource: ../raw/canary-1b-v2.md
    kind: documentation
    title: Canary-1b-v2 model card
  - id: nemotron-en-stream-card
    resource: ../raw/nemotron-speech-streaming-en-0.6b.md
    kind: documentation
    title: Nemotron ASR Streaming model card
  - id: nemotron-35-asr-card
    resource: ../raw/nemotron-3.5-asr-streaming-0.6b.md
    kind: documentation
    title: Nemotron 3.5 ASR model card
  - id: parakeet-eou-card
    resource: ../raw/parakeet_realtime_eou_120m-v1.md
    kind: documentation
    title: Parakeet Realtime EOU 120M v1 model card
  - id: multitalker-parakeet-card
    resource: ../raw/multitalker-parakeet-streaming-0.6b-v1.md
    kind: documentation
    title: Multitalker Parakeet Streaming 0.6B v1
  - id: qwen3-asr-readme
    resource: ../raw/Qwen3-ASR-0.6B.md
    kind: documentation
    title: Qwen3-ASR README and model card (family)
  - id: ark-asr-3b-card
    resource: ../raw/ARK-ASR-3B.md
    kind: documentation
    title: ARK-ASR-3B model card
  - id: audio8-asr-01b-card
    resource: ../raw/Audio8-ASR-0.1B.md
    kind: documentation
    title: Audio8-ASR-0.1B model card
  - id: audio8-infinite-card
    resource: ../raw/Audio8-ASR-Infinite.md
    kind: documentation
    title: Audio8 ASR Infinite model card
  - id: fun-asr-nano-card
    resource: ../raw/Fun-ASR-Nano-2512.md
    kind: documentation
    title: Fun-ASR-Nano-2512 model card
  - id: fun-asr-mlt-nano-card
    resource: ../raw/Fun-ASR-MLT-Nano-2512.md
    kind: documentation
    title: Fun-ASR-MLT-Nano-2512 model card
  - id: fun-asr-nano-gguf-card
    resource: ../raw/Fun-ASR-Nano-GGUF.md
    kind: documentation
    title: Fun-ASR-Nano GGUF model card
  - id: glm-asr-nano-card
    resource: ../raw/GLM-ASR-Nano-2512.md
    kind: documentation
    title: GLM-ASR-Nano-2512 model card
  - id: cohere-arabic-card
    resource: ../raw/cohere-transcribe-arabic-07-2026.md
    kind: documentation
    title: Cohere Transcribe Arabic model card
  - id: vibevoice-asr-card
    resource: ../raw/VibeVoice-ASR.md
    kind: documentation
    title: VibeVoice-ASR model card
  - id: vibevoice-asr-streaming-1-5b-card
    resource: ../raw/VibeVoice-ASR-Streaming-1.5B.md
    kind: documentation
    title: VibeVoice-ASR-Streaming-1.5B model card
  - id: vibevoice-asr-streaming-7b-card
    resource: ../raw/VibeVoice-ASR-Streaming-7B.md
    kind: documentation
    title: VibeVoice-ASR-Streaming-7B model card
  - id: vibevoice-asr-streaming-7b-gguf-card
    resource: ../raw/VibeVoice-ASR-Streaming-7B-GGUF.md
    kind: documentation
    revision: 60d858b518b4e19d404af3737f848fc185b30177
    title: VibeVoice ASR Streaming 7B GGUF for audio.cpp
  - id: moss-transcribe-cpp-gguf-card
    resource: ../raw/moss-transcribe.cpp-gguf.md
    kind: documentation
    title: MOSS-Transcribe-Diarize GGUF (for moss-transcribe.cpp)
  - id: sensevoice-small-gguf-card
    resource: ../raw/SenseVoiceSmall-GGUF-audiocpp.md
    kind: documentation
    title: SenseVoiceSmall GGUF for audio.cpp
  - id: audio-flamingo-gguf-card
    resource: ../raw/Audio-Flamingo-GGUF.md
    kind: documentation
    title: Audio Flamingo 3 and Next GGUF
  - id: faster-whisper-readme
    resource: ../raw/faster-whisper.md
    kind: documentation
    title: Faster-Whisper README
  - id: audio-cpp-gguf-readme
    resource: ../raw/audio.cpp-gguf.md
    kind: documentation
    title: audio.cpp GGUF Model Packages
  - id: parakeet-readme
    resource: ../raw/parakeet.md
    kind: documentation
    title: Parakeet ASR server README (achetronic/parakeet)
  - id: wlk-readme
    resource: ../raw/WhisperLiveKit.md
    kind: documentation
    title: WhisperLiveKit README
  - id: realtimestt-readme
    resource: ../raw/RealtimeSTT.md
    kind: documentation
    title: RealtimeSTT README
  - id: speaches-readme
    resource: ../raw/speaches.md
    kind: documentation
    title: Speaches README (overview excerpt)
  - id: index-echo-s2tt-gguf
    resource: ../raw/Index-Echo-S2TT-GGUF.md
    kind: documentation
    title: Index-Echo-S2TT GGUF
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
  - id: reddit-asr-tts-thread
    resource: ../raw/good_asr_and_tts_models.md
    kind: documentation
    title: Good ASR and TTS models? r/LocalLLaMA thread capture
  - id: reddit-noisy-stt
    resource: ../raw/best_speechtotext_in_2025.md
    kind: documentation
    title: Best Speech-to-Text in 2025? r/LocalLLaMA thread capture
  - id: reddit-open-stt
    resource: ../raw/whats_the_best_open_speech_to_text_today.md
    kind: documentation
    title: What's the best open speech to text today? r/LocalLLaMA thread capture
  - id: reddit-stt-llm-tts-thread
    resource: ../raw/stt_llm_tts_pipeline.md
    kind: documentation
    title: STT -> LLM -> TTS pipeline r/LocalLLaMA thread capture
  - id: reddit-usable-stt
    resource: ../raw/best_stt_api_for_voice_agents_i_care_more_about.md
    kind: documentation
    title: Best STT API for voice agents? r/AI_Agents thread capture
---

The wiki compiles 25 distinct ASR/STT model lines: 11 NVIDIA NeMo checkpoints (Parakeet CTC/RNNT/TDT, Canary, Nemotron streaming, the EOU and multitalker variants), and a second group of LLM-decoder or audio-LLM recognizers (Qwen3-ASR, ARK-ASR, Audio8, Fun-ASR, GLM-ASR, VibeVoice-ASR, MOSS-Transcribe, Cohere Arabic), plus Whisper reached through runtimes and a set of GGUF/ONNX edge packages. The source cards back three broad findings. First, offline English accuracy clusters between about 5% and 7.7% average WER on the Hugging Face Open ASR Leaderboard sets. ARK-ASR-3B reports the lowest figure and Parakeet TDT V2 the best small-model figure. Second, purpose-built streaming models trade about 1.5 WER points for 80 ms latency (Nemotron) or swap language breadth for native clocked streaming (Audio8 Infinite). Third, coverage, license, and deployment target usually decide the choice more than leaderboard rank, especially for Chinese dialects, Arabic, Vietnamese, speaker attribution, and CPU/edge use. Every number below is a vendor or community claim that this wiki has not reproduced (**Synthesis**).

## Scope and method

- **Included:** every concept whose primary job is turning speech into text: model cards, GGUF/ONNX packagings of those models, and the runtimes that serve them. Retrieval used the root index, `stt`/`asr` tag search, and exact search for model names inside pipeline and community pages (**Synthesis**).
- **Adjacent, not surveyed as ASR:** diarization-only models, speech-to-speech or speech-LLM systems, speech translation, turn detection, and noise preprocessing. They are listed under [Adjacent concepts](#adjacent-concepts) (**Synthesis**).
- **Evidence:** model rows are **Reported** by the cited card. Averages that the cards do not print are marked *computed*: the arithmetic mean of the card's eight Open ASR Leaderboard WER cells, which is **Synthesis**. Community and LLM-report claims are anecdotal and kept in their own section.
- **Comparability warning:** the source cards do not share one protocol. Some average 7 Open ASR splits (ARK, Audio8) and others 8 (NeMo, adding TEDLIUM). Some score lowercase output without punctuation (Parakeet CTC/RNNT) and others normalize punctuated output. Chunk size, decoding, and hardware also differ. A gap of less than about 0.5 WER points between rows from different cards should not drive a decision on its own (**Synthesis**).

## Master catalog

| Model (concept) | Developer | Size | Architecture | Languages | Mode | License | Headline reported result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md) | NVIDIA NeMo + Suno | ~0.6B | FastConformer-CTC | en (lowercase, no PnC) | offline | CC-BY-4.0 | 7.66 mean of 8 Open ASR sets (*computed*)[^parakeet-ctc-card] |
| [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) | NVIDIA NeMo + Suno | ~1.1B | FastConformer-CTC | en (lowercase, no PnC) | offline; NeMo-Speech.cpp GGUF | CC-BY-4.0 | 7.40 (*computed*)[^parakeet-ctc-11-card] |
| [Parakeet RNNT 0.6B](parakeet-rnnt-0.6b.md) | NVIDIA NeMo + Suno | ~0.6B | FastConformer-RNNT | en (lowercase, no PnC) | offline | CC-BY-4.0 | 7.56 (*computed*)[^parakeet-rnnt-card] |
| [Parakeet RNNT 1.1B](parakeet-rnnt-1.1b.md) | NVIDIA NeMo + Suno | ~1.1B | FastConformer-RNNT | en (lowercase, no PnC) | offline | CC-BY-4.0 | 7.19 (*computed*)[^parakeet-rnnt-11-card] |
| [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md) | NVIDIA | ~0.6B | FastConformer-TDT | en, PnC, word timestamps | offline, ≤24 min per pass | CC-BY-4.0 | 6.05 avg; RTFx 3380 at batch 128[^parakeet-tdt-card] |
| [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) | NVIDIA | ~0.6B | FastConformer-TDT | 25 European, auto language ID | offline, ≤24 min (≤3 h local attention) | CC-BY-4.0 | en 6.34 avg; FLEURS 11.97 / MLS 7.83 / CoVoST 11.98[^parakeet-v3-card] |
| [Canary-1b-v2](canary-1b-v2.md) | NVIDIA NeMo | 978M | FastConformer encoder + Transformer decoder (multitask) | 25 European + X↔En translation | offline, auto-chunked long-form | CC-BY-4.0 | Open ASR mean 7.15 at RTFx 749; FLEURS 8.40[^canary-1b-v2-card] |
| [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) | NVIDIA | 600M | cache-aware FastConformer-RNNT | en, PnC | streaming 80–1120 ms | NVIDIA Open Model License | 6.93 at 1.12 s → 8.43 at 80 ms[^nemotron-en-stream-card] |
| [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) | NVIDIA | 600M | cache-aware FastConformer-RNNT + language-ID prompt | 40 locales (19 ready, 13 broad, 8 adaptation) | streaming 80–1120 ms | OpenMDW-1.1 | FLEURS ready-tier avg 8.84 at 1.12 s / 10.38 at 80 ms[^nemotron-35-asr-card] |
| [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md) | NVIDIA | 120M | cache-aware FastConformer-RNNT + `<EOU>` token | en | streaming 80–160 ms | NVIDIA Open Model License | 9.30 avg at 160 ms; EOU P50 160 ms[^parakeet-eou-card] |
| [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md) | NVIDIA | 600M per speaker instance | FastConformer + speaker-kernel injection | en | streaming (benchmarked at 1.12 s) | NVIDIA Open Model License | cpWER AMI IHM 21.26; single-speaker 7.44[^multitalker-parakeet-card] |
| [Qwen3-ASR family](qwen3-asr-family.md) | Qwen | 1.7B / 0.6B (+ 0.6B forced aligner) | Qwen3-Omni-based audio LLM | 30 languages + 22 Chinese dialects | unified offline/streaming | Apache-2.0 | 1.7B LibriSpeech 1.63 / 3.38; language ID 97.9%[^qwen3-asr-readme] |
| [ARK-ASR-3B](ark-asr-3b.md) | AutoArk | 3B (0.6B sibling) | Whisper-style encoder + MLP + Qwen decoder | 19 | offline, 30 s window | Apache-2.0 | 5.04 Open ASR 7-split avg; RTFx 490.98[^ark-asr-3b-card] |
| [Audio8-ASR-0.1B](audio8-asr-0.1b.md) | AutoArk | 0.104B LM / 0.324B total | Qwen3-ASR encoder + 8-layer Qwen LM | 7 | offline short-form, 30 s cap | CC-BY-NC-4.0 | 7.03 Open ASR 7-split mean; RTFx 741 on H200[^audio8-asr-01b-card] |
| [Audio8 ASR Infinite](audio8-asr-infinite.md) | Edge0 | Voxtral-Realtime-4B audio tower + Qwen2.5-3B decoder (8.17 GB bf16) | native streaming (DSM-style) + semantic VAD heads | zh, en | streaming: 80/120/160 ms clock, 240–560 ms delay, 24/7 rolling KV | Apache-2.0 | AISHELL-1 CER 1.75; LibriSpeech 3.04 / 6.81 at 480 ms[^audio8-infinite-card] |
| [Fun-ASR-Nano-2512](fun-asr-nano-2512.md) | Tongyi Lab / FunAudioLLM | 0.8B | end-to-end LLM-based ASR | zh/en/ja + 7 dialects, 26 accents, lyrics/rap | real-time claimed | Apache-2.0 | AISHELL-1 1.80; industry-set avg 16.72[^fun-asr-nano-card] |
| [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md) | FunAudioLLM | 0.8B | same family | 31 (East/Southeast Asian focus, incl. vi) | offline (optional FSMN-VAD segmentation) | Apache-2.0 | no checkpoint-specific results published[^fun-asr-mlt-nano-card] |
| [GLM-ASR-Nano-2512](glm-asr-nano-2512.md) | zai-org | 1.5B | Transformers seq2seq ASR | en, zh, Cantonese/dialects | offline | MIT | claimed 4.10 avg error (figure only)[^glm-asr-nano-card] |
| [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md) | Cohere / Cohere Labs | 2B | Conformer encoder + light Transformer decoder | ar (+ dialects), en | offline, auto-chunked long-form | Apache-2.0 | Open Universal Arabic leaderboard avg 25.87 WER / 11.80 CER[^cohere-arabic-card] |
| [VibeVoice-ASR](vibevoice-asr.md) | Microsoft Research | not stated | unified ASR + diarization + timestamps | 50+, code-switching | offline, 60 min single pass | MIT | no numeric results in card text[^vibevoice-asr-card] |
| [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) | Microsoft Research | 1.5B | unified streaming speaker-attributed ASR | 10 | streaming | MIT | no numeric results in card text[^vibevoice-asr-streaming-1-5b-card] |
| [VibeVoice-ASR-Streaming-7B](vibevoice-asr-streaming-7b.md) | Microsoft Research | 7B | unified streaming speaker-attributed ASR | 10 | streaming | MIT | no numeric results; card text identical to 1.5B[^vibevoice-asr-streaming-7b-card] |
| [MOSS-Transcribe-Diarize GGUF](moss-transcribe-cpp-gguf.md) | OpenMOSS (port: moss-transcribe.cpp) | 3.4 GB F32 reference | joint transcription + diarization + timestamps | not stated in package card | long-form, CPU | Apache-2.0 | Q4_0 511 MB, 2.2x F32 speed, word-identical output[^moss-transcribe-cpp-gguf-card] |
| [SenseVoiceSmall GGUF](sensevoice-small-gguf.md) | FunAudioLLM (audio.cpp export) | 254 MB Q8_0 file | SenseVoice | zh, en, yue, ja, ko | offline CPU | Apache-2.0 | exact-match Mandarin parity with original Q8[^sensevoice-small-gguf-card] |
| Whisper via [Faster-Whisper](faster-whisper.md) | OpenAI weights / SYSTRAN CTranslate2 runtime | tiny … large-v3, turbo, distil-large-v3 | encoder-decoder | multilingual | offline; streaming only via wrappers | not compiled | large-v2: 13 min audio in 59 s int8, 2926 MB VRAM (RTX 3070 Ti)[^faster-whisper-readme] |

## English accuracy (Open ASR Leaderboard)

Averages as published or *computed* from per-set cells; lower is better (**Reported** per row; ordering is **Synthesis**):

| Rank | Model | Avg WER | Sets | Notes |
| ---: | --- | ---: | --- | --- |
| 1 | ARK-ASR-3B | 5.04 | 7 splits | AMI 8.79 is the best meeting figure in the wiki[^ark-asr-3b-card] |
| 2 | ARK-ASR-0.6B | 5.97 | 7 splits | sibling row in the ARK card[^ark-asr-3b-card] |
| 3 | Parakeet TDT 0.6B V2 | 6.05 | 8 | SNR 0 dB → 11.88; μ-law telephony 6.32[^parakeet-tdt-card] |
| 4 | Parakeet TDT 0.6B V3 | 6.34 | 8 | multilingual model, small English penalty[^parakeet-v3-card] |
| 5 | Nemotron Speech Streaming EN 0.6B | 6.93 | 8 | **streaming** at 1.12 s; 7.67 at 160 ms[^nemotron-en-stream-card] |
| 6 | Audio8-ASR-0.1B | 7.03 | 7 splits | 0.1B-LM, H200 RTFx 741[^audio8-asr-01b-card] |
| 7 | Canary-1b-v2 | 7.15 | 8 | also does translation; RTFx 749[^canary-1b-v2-card] |
| 8 | Parakeet RNNT 1.1B | 7.19 | 8 (*computed*) | lowercase output[^parakeet-rnnt-11-card] |
| 9 | Parakeet CTC 1.1B | 7.40 | 8 (*computed*) | lowercase output[^parakeet-ctc-11-card] |
| 10 | Multitalker Parakeet (single-speaker mode) | 7.44 | 8 | base reported at 7.16 in the same card[^multitalker-parakeet-card] |
| 11 | Parakeet RNNT 0.6B | 7.56 | 8 (*computed*) | [^parakeet-rnnt-card] |
| 12 | Parakeet CTC 0.6B | 7.66 | 8 (*computed*) | [^parakeet-ctc-card] |
| 13 | Parakeet Realtime EOU 120M | 9.30 | 8 | **streaming** at 160 ms, 120M params[^parakeet-eou-card] |

- Qwen3-ASR does not publish an Open ASR average. Its LibriSpeech figures (1.7B: 1.63 clean / 3.38 other; 0.6B: 2.11 / 4.55) and GigaSpeech 8.45 sit in the same band as the leaders above (**Reported**; comparison is **Synthesis**).[^qwen3-asr-readme]
- The older Parakeet CTC/RNNT generation (64K-hour English, lowercase output) is 1.1–1.6 points behind TDT V2 (~120K-hour Granary, punctuated output) at the same 0.6B size. Doubling to 1.1B recovers only about 0.3–0.4 points (**Synthesis** from the per-card tables).[^parakeet-tdt-card][^parakeet-rnnt-11-card]

## Chinese accuracy (CER, lower is better)

| Model | AISHELL-1 | WenetSpeech meeting | WenetSpeech net | Source |
| --- | ---: | ---: | ---: | --- |
| Audio8 ASR Infinite (streaming, 480 ms) | **1.75** | — | — | [^audio8-infinite-card] |
| ARK-ASR-3B | 1.80 | **4.97** | **4.58** | [^ark-asr-3b-card] |
| Fun-ASR-nano (0.8B) | 1.80 | 6.60 | 6.01 | [^fun-asr-nano-card] |
| GLM-ASR-nano (1.5B, in Fun-ASR table) | 1.81 | 6.73 | — | [^fun-asr-nano-card] |
| ARK-ASR-0.6B | 2.02 | 5.92 | 4.96 | [^ark-asr-3b-card] |
| Qwen3-ASR-1.7B | — (AISHELL-2 2.71) | 5.88 | 4.97 | [^qwen3-asr-readme] |
| Qwen3-ASR-0.6B | — (AISHELL-2 3.15) | 6.88 | 5.97 | [^qwen3-asr-readme] |
| Audio8-ASR-0.1B (internal eval) | — | 8.84 | 7.98 | [^audio8-asr-01b-card] |
| Whisper-large-v3 (in Fun-ASR table) | 4.72 | 18.39 | 11.89 | [^fun-asr-nano-card] |

- For dialects and hard conditions, the Fun-ASR card's industry sets (dialect, accent, lyrics, hip-hop, far-field) give Fun-ASR-nano a 16.72 average against 26.13 for GLM-ASR-Nano and 33.39 for Whisper-large-v3 (**Reported**).[^fun-asr-nano-card] Qwen3-ASR-1.7B reports KeSpeech 5.10 and 15.94 on its internal Chinese-dialect dialog set (**Reported**).[^qwen3-asr-readme]
- Nemotron 3.5 tiers Mandarin as broad-coverage, not transcription-ready. In Audio8 Infinite's table its AISHELL-1 CER is 12.93 at 560 ms, so the NVIDIA streaming line is not a Chinese choice (**Reported**; recommendation is **Synthesis**).[^nemotron-35-asr-card][^audio8-infinite-card]

## Multilingual coverage

| Model | Languages | Notable coverage |
| --- | --- | --- |
| VibeVoice-ASR | 50+ | code-switching, no language setting needed[^vibevoice-asr-card] |
| Nemotron 3.5 ASR | 40 locales (32 usable out of the box) | streaming; vi, ar, hi, ja, ko ready; auto language detection appends an `<xx-XX>` tag[^nemotron-35-asr-card] |
| Fun-ASR-MLT-Nano | 31 | vi, id, th, ms, fil, ar, hi plus EU languages[^fun-asr-mlt-nano-card] |
| Qwen3-ASR | 30 + 22 Chinese dialects | singing and BGM audio; language ID 97.9% (1.7B) vs Whisper-large-v3 94.1%[^qwen3-asr-readme] |
| Canary-1b-v2 / Parakeet TDT V3 | 25 European | Canary adds En↔24 translation; V3 auto-detects language[^canary-1b-v2-card][^parakeet-v3-card] |
| ARK-ASR-3B | 19 | zh, en, ja, ko + 15 European[^ark-asr-3b-card] |
| VibeVoice-ASR-Streaming | 10 | zh, en, fr, de, it, ja, ko, pt, ru, es[^vibevoice-asr-streaming-1-5b-card] |
| Audio8-ASR-0.1B | 7 | en, zh, fr, ja, yue, de, ko[^audio8-asr-01b-card] |
| SenseVoiceSmall | 5 | zh, en, yue, ja, ko[^sensevoice-small-gguf-card] |

- **Vietnamese:** the wiki has vendor figures for Qwen3-ASR (Fleurs-vi 5.55 for 1.7B, 8.52 for 0.6B) and Nemotron 3.5 (FLEURS-vi 11.18 at 1.12 s, 13.41 at 80 ms). Fun-ASR-MLT-Nano lists Vietnamese without a score. Parakeet V3 and Canary do not cover it (**Reported**).[^qwen3-asr-readme][^nemotron-35-asr-card][^fun-asr-mlt-nano-card] An AI-compiled report also names PhoWhisper-large, ChunkFormer-large-vie (110M), and sherpa-onnx Zipformer VN. None of these has a concept page in this wiki (**Reported**, LLM-generated).[^claude-pipeline-report]
- **Arabic:** Cohere Transcribe Arabic leads the Open Universal Arabic leaderboard average (25.87 / 11.80), ahead of Qwen3-ASR-1.7B (33.36 / 12.33) and Whisper-large-v3 (36.86 / 17.21) in the card's table. It has no language auto-detection, timestamps, or diarization (**Reported**).[^cohere-arabic-card]

## Streaming and latency

| Model | Streaming mechanism | Latency knob | Accuracy cost of low latency |
| --- | --- | --- | --- |
| Nemotron Speech Streaming EN 0.6B | cache-aware FastConformer, no overlapping recompute | `att_context_size` 80/160/560/1120 ms at inference | 6.93 → 8.43 avg WER from 1.12 s to 80 ms; AMI is worst hit (11.73 → 18.29)[^nemotron-en-stream-card] |
| Nemotron 3.5 ASR Streaming 0.6B | cache-aware + language-ID prompt | 80/160/320/560/1120 ms | ready-tier FLEURS 8.84 → 10.38; one H100 sustains ~240 streams at 80 ms and ~2,400 at 1.12 s[^nemotron-35-asr-card] |
| Parakeet Realtime EOU 120M | cache-aware, 17 layers | 80–160 ms | 9.30 at 160 ms; inline `<EOU>` P50/P90/P95 160/280/320 ms[^parakeet-eou-card] |
| Audio8 ASR Infinite | native one-token-per-clock streaming, rolling 30 s KV with RoPE re-basing | clock 80/120/160 ms × delay 240–560 ms | evaluated at 480 ms delay; semantic VAD distinguishes pauses from end of turn[^audio8-infinite-card] |
| Qwen3-ASR | unified offline/streaming in one model | not exposed as chunk table | 1.7B 2.69 → 3.33, 0.6B 3.48 → 4.40 (offline → streaming)[^qwen3-asr-readme] |
| Multitalker Parakeet | one cache-aware instance per speaker, fed by streaming diarization | same 80–1120 ms table | benchmarked only at 1.12 s[^multitalker-parakeet-card] |
| VibeVoice-ASR-Streaming 1.5B / 7B | streaming who-said-what | not published | not published[^vibevoice-asr-streaming-7b-card] |
| Whisper (any size) | not natively streaming | wrapper policy (SimulStreaming/LocalAgreement in WhisperLiveKit; VAD-gated realtime/final engines in RealtimeSTT) | wrapper-dependent[^wlk-readme][^realtimestt-readme] |

## Capability matrix

| Capability | Models documented with it |
| --- | --- |
| Punctuation + capitalization | Parakeet TDT V2/V3, Canary-1b-v2, Nemotron EN / 3.5. Parakeet CTC/RNNT output lowercase text[^parakeet-tdt-card][^nemotron-en-stream-card][^parakeet-ctc-card] |
| Word/segment timestamps | Parakeet TDT V2/V3, Canary (ASR word + segment), Parakeet RNNT via Transformers, Qwen3-ForcedAligner (11 languages, ≤5 min, 42.9 ms mean shift), VibeVoice-ASR, MOSS. Cohere Arabic: none; Fun-ASR: TODO[^canary-1b-v2-card][^parakeet-rnnt-card][^qwen3-asr-readme][^cohere-arabic-card][^fun-asr-nano-card] |
| Speaker attribution in the ASR model | VibeVoice-ASR (offline, 60 min), VibeVoice-ASR-Streaming, MOSS-Transcribe-Diarize, Multitalker Parakeet (needs an external diarizer)[^vibevoice-asr-card][^moss-transcribe-cpp-gguf-card][^multitalker-parakeet-card] |
| Hotwords / context biasing | Audio8-ASR-0.1B (decode-time logit boost), Fun-ASR Nano/MLT (`hotwords` + ITN), VibeVoice-ASR family[^audio8-asr-01b-card][^fun-asr-mlt-nano-card][^vibevoice-asr-card] |
| End-of-turn signal | Parakeet Realtime EOU (`<EOU>` token), Audio8 Infinite (semantic VAD heads)[^parakeet-eou-card][^audio8-infinite-card] |
| Speech translation | Canary-1b-v2 (X↔En, 25 European languages)[^canary-1b-v2-card] |
| Long audio in one pass | VibeVoice-ASR 60 min; Parakeet TDT 24 min (V3 up to 3 h local attention); Audio8 Infinite unbounded (rolling KV)[^vibevoice-asr-card][^parakeet-v3-card][^audio8-infinite-card] |
| Noise robustness figures | Parakeet TDT V2/V3 and Canary MUSAN SNR tables; Canary hallucination rate 134.7 chars/min[^parakeet-v3-card][^canary-1b-v2-card] |

## Edge, CPU, and packaged deployment

| Package / path | Runtime | Size / footprint | Reported result |
| --- | --- | --- | --- |
| [Fun-ASR-Nano GGUF](fun-asr-nano-gguf.md) | FunASR llama.cpp CLI, zero Python | 470 MB encoder + 484–805 MB Qwen3-0.6B decoder | 8.25–8.35% CER on 184 Mandarin clips across Q4_K_M/Q5_K_M/Q8_0 vs whisper.cpp 22–31%[^fun-asr-nano-gguf-card] |
| [SenseVoiceSmall GGUF](sensevoice-small-gguf.md) | audio.cpp `sense_asr` | 254 MB Q8_0 | exact-match Mandarin parity[^sensevoice-small-gguf-card] |
| [MOSS-Transcribe-Diarize GGUF](moss-transcribe-cpp-gguf.md) | moss-transcribe.cpp (CPU) | 511 MB (Q4) – 1.8 GB (F16) | 11 s clip in 3.57–4.96 s on 8 CPU threads; Q5 and above byte-identical[^moss-transcribe-cpp-gguf-card] |
| Audio8-ASR-0.1B ONNX / iOS ANE | ONNX Runtime / Apple Neural Engine | ~1.1 GB / ~200 MB peak | releases linked, not compiled[^audio8-asr-01b-card] |
| [Parakeet ASR Server](parakeet-asr-server.md) | Go + ONNX Runtime, CPU or CUDA | — | OpenAI Whisper-compatible REST/SSE for Parakeet TDT 0.6B[^parakeet-readme] |
| [VibeVoice-ASR-Streaming-7B GGUF](vibevoice-asr-streaming-7b-gguf.md) | audio.cpp | BF16 / Q8_0 (recommended) / Q4_K | no quality or speed figures[^vibevoice-asr-streaming-7b-gguf-card] |
| [Audio Flamingo 3 and Next GGUF](audio-flamingo-3-and-next-gguf.md) | audio.cpp (CUDA) | Q4_K: 6.3 GB peak VRAM | 10 s clip RTF 0.013–0.015 on RTX 5090; non-commercial license[^audio-flamingo-gguf-card] |
| [Faster-Whisper](faster-whisper.md) int8 | CTranslate2 CPU/GPU | small int8 on CPU: 1477 MB RAM | 13 min audio in 1m42s on an i7-12700K with 8 threads[^faster-whisper-readme] |
| [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) | audio.cpp | — | catalog ASR rows: Qwen3-ASR 0.6B/1.7B + ForcedAligner, Parakeet-TDT-0.6B-v3, Nemotron-3.5-ASR, Canary-180M-Flash, Cohere-Transcribe, Fun-ASR-Nano, VibeVoice-ASR, MOSS-Transcribe-Diarize, Moonshine-Streaming, Granite-Speech-5.0-470M, GigaAM, CrisperWhisper, Citrinet, Kroko, Hviske, Niagara, MMS-Forced-Aligner[^audio-cpp-gguf-readme] |

NeMo-Speech.cpp GGUF paths are documented for Parakeet CTC 1.1B, Parakeet TDT V3, and Nemotron 3.5 (`nemotron-3.5-asr-streaming-0.6b.q8_0.gguf`) (**Reported**).[^parakeet-ctc-11-card][^parakeet-v3-card][^nemotron-35-asr-card]

## Licensing

| License | Models | Commercial-use reading |
| --- | --- | --- |
| Apache-2.0 | Qwen3-ASR, ARK-ASR-3B, Audio8 ASR Infinite, Fun-ASR Nano/MLT, Cohere Transcribe Arabic, MOSS-Transcribe-Diarize, SenseVoiceSmall | permissive |
| MIT | GLM-ASR-Nano, VibeVoice-ASR family | permissive |
| CC-BY-4.0 | Parakeet CTC/RNNT/TDT, Canary-1b-v2 | permissive with attribution |
| NVIDIA Open Model License | Nemotron Speech Streaming EN, Parakeet Realtime EOU, Multitalker Parakeet | vendor license, check terms |
| OpenMDW-1.1 | Nemotron 3.5 ASR | card states ready for commercial use |
| CC-BY-NC-4.0 | Audio8-ASR-0.1B | **non-commercial** |
| NVIDIA OneWay Noncommercial | Audio Flamingo 3 / Next | **non-commercial** |

The license column follows each concept's compiled card frontmatter (**Reported**). The commercial reading is **Synthesis**, not legal advice.[^audio8-asr-01b-card][^audio-flamingo-gguf-card][^nemotron-35-asr-card]

## Serving runtimes

| Runtime | ASR engines | Interface |
| --- | --- | --- |
| [Faster-Whisper](faster-whisper.md) | Whisper / distil-Whisper (CTranslate2), Silero VAD filter, batched pipeline | Python library[^faster-whisper-readme] |
| [WhisperLiveKit](whisperlivekit.md) | faster-whisper, mlx-whisper, Whisper, FunASR, Voxtral, Qwen3 (vLLM / streaming), Canary, OpenAI API | WebSocket + OpenAI/Deepgram-compatible; SimulStreaming or LocalAgreement policy[^wlk-readme] |
| [RealtimeSTT](realtimestt.md) | selectable realtime + final engines behind VAD gating | Python library + FastAPI server[^realtimestt-readme] |
| [Speaches](speaches.md) | faster-whisper | OpenAI-compatible server, SSE streaming[^speaches-readme] |
| [Parakeet ASR Server](parakeet-asr-server.md) | Parakeet TDT 0.6B (ONNX) | Whisper-compatible REST/SSE[^parakeet-readme] |
| vLLM / [SGLang-Omni](sglang-omni.md) / [vLLM-Omni](vllm-omni.md) | Qwen3-ASR (`qwen-asr-serve`), ARK-ASR, Cohere Arabic (`/v1/audio/transcriptions`) | OpenAI-compatible[^qwen3-asr-readme][^ark-asr-3b-card][^cohere-arabic-card] |
| [audio.cpp Framework](audio-cpp-framework.md) | 17+ ASR GGUF families | CLI / server / WebUI[^audio-cpp-gguf-readme] |

## Selection guide

This section is agent **Synthesis** from the evidence above. Validate any choice on in-domain audio, because no figure here has been reproduced.

- **English realtime voice agent:** [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) at 160–560 ms. Use [Parakeet Realtime EOU 120M](parakeet-realtime-eou-120m-v1.md) when budget is tight or you want ASR-native endpointing.
- **English batch/offline, best small model:** [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md), with very high RTFx and published noise and telephony rows. Move to [ARK-ASR-3B](ark-asr-3b.md) when meeting/AMI accuracy matters more than speed.
- **Multilingual realtime:** [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md) for its 19 transcription-ready locales. Use [Qwen3-ASR](qwen3-asr-family.md) for broader and Asian coverage with a unified streaming mode.
- **European multilingual offline or translation:** [Parakeet TDT V3](parakeet-tdt-0.6b-v3.md) for speed, [Canary-1b-v2](canary-1b-v2.md) when you also need X↔En translation.
- **Chinese, dialects, Cantonese:** Qwen3-ASR-1.7B, [Fun-ASR-Nano](fun-asr-nano-2512.md) (dialect, lyrics, hip-hop), or ARK-ASR-3B. Use [Audio8 ASR Infinite](audio8-asr-infinite.md) for 24/7 zh/en streaming.
- **Vietnamese:** start with Qwen3-ASR or faster-whisper `large-v3-turbo` with hallucination filters, as recommended in the [Vietnamese stack](vietnamese-realtime-voice-agent-stack.md). Use Nemotron 3.5 as a streaming alternative and benchmark on noisy in-house audio.
- **Arabic:** [Cohere Transcribe Arabic](cohere-transcribe-arabic-07-2026.md) behind a VAD/noise gate.
- **Meetings with speakers:** [VibeVoice-ASR](vibevoice-asr.md) (offline, 60 min) or [MOSS-Transcribe-Diarize](moss-transcribe-cpp-gguf.md) (CPU). Alternatively, pair streaming ASR with a diarizer through [Multitalker Parakeet](multitalker-parakeet-streaming-0.6b-v1.md).
- **CPU/edge:** Fun-ASR-Nano GGUF or SenseVoiceSmall GGUF for CJK, Parakeet via ONNX or NeMo-Speech.cpp for English/European, faster-whisper int8 as the general fallback.
- **Commercial license constraint:** avoid Audio8-ASR-0.1B and Audio Flamingo, and review NVIDIA Open Model License terms.

## Community-reported field notes

These are unverified anecdotes from community threads, kept apart from vendor evidence (**Reported**):

- For English short utterances, Parakeet v2 is recommended over Whisper at about 5x speed. V3 is described as slower because of its multilingual breadth.[^reddit-stt-llm-tts-thread]
- Two commenters rank Qwen3-ASR (including 0.6B) above Parakeet, Whisper, and FunASR because it hallucinates least and rejects non-speech better. Whisper large-v3-turbo is described as almost as accurate as large-v3 but much faster. Moonshine is named for the lowest-latency English-only use.[^reddit-open-stt]
- Qwen3-ASR is called heavier on VRAM, and one commenter says it streams worse than Parakeet. Commenters advise pairing it with a VAD frontend to suppress false triggers. One commenter picks Nemotron 3.5 streaming as their best ASR.[^reddit-asr-tts-thread]
- For noisy calls, Parakeet is reported as 4–5x faster than Whisper for English. Whisper-large-v3 with preprocessing and diarization is defended as still viable, and Canary and Granite are named as more robust alternatives without measurements.[^reddit-noisy-stt]
- Agent-grade STT evaluation should measure first stable text, partial stability, endpointing, barge-in, and entity accuracy, not WER alone.[^reddit-usable-stt]

## Adjacent concepts

- Diarization only: [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md), [Streaming Sortformer v2](diar-streaming-sortformer-4spk-v2.md) / [v2.1](diar-streaming-sortformer-4spk-v2-1.md), [Nemotron 3 Diarization](nemotron-3-diarization.md) and its [GGUF](nemotron-3-diarization-gguf.md). Streaming Sortformer v2 is the frontend in Multitalker Parakeet's cpWER table.[^multitalker-parakeet-card]
- Speech translation: [Index-Echo S2TT GGUF](index-echo-s2tt-gguf.md) produces timestamped Chinese source transcripts plus English, Spanish, or Japanese translations.[^index-echo-s2tt-gguf]
- Speech LLM / speech-to-speech without a separate ASR stage: [Ultravox](ultravox.md), [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md), [PersonaPlex 7B v1](personaplex-7b-v1.md), [Step-Audio-R1.1](step-audio-r1-1.md).
- ASR hygiene: [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md), [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), [Turn Detection Models](turn-detection-models.md), [Silero VAD](silero-vad.md).
- Community syntheses: [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md), [Noisy On-Premise STT Selection](community-noisy-call-stt.md), [Open STT and Realtime Diarization Selection](community-open-stt-diarization.md), [Local ASR/TTS Selection](community-asr-tts-selection.md), [STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md).

## Contradictions

- **Nemotron Speech Streaming EN 0.6B English average:** its own card reports 6.93 at 1.12 s (AMI 11.73, GigaSpeech 9.66, TEDLIUM 3.50).[^nemotron-en-stream-card] The Multitalker Parakeet card lists the same base model at 7.16 (AMI 11.58, GigaSpeech 11.45, TEDLIUM 4.5) and does not state that table's chunk size or checkpoint revision.[^multitalker-parakeet-card] Neither value is chosen here.
- **Audio8 Infinite vs Nemotron 3.5:** Audio8's comparison table runs itself at 480 ms delay and Nemotron 3.5 at 560 ms on AISHELL and LibriSpeech. The settings differ, and the table covers Nemotron's broad-coverage Mandarin tier, so the gap does not reflect Nemotron's transcription-ready languages (**Reported**; interpretation is **Synthesis**).[^audio8-infinite-card][^nemotron-35-asr-card]
- **Qwen3-ASR streaming quality:** the vendor reports a small offline-to-streaming gap (2.69 → 3.33), while one community commenter says it streams worse than Parakeet. No shared measurement resolves this.[^qwen3-asr-readme][^reddit-asr-tts-thread]

## Coverage and limits

- This survey reads only the compiled concepts and their declared raw sources. No model was downloaded, run, or benchmarked, and no figure was reproduced (**Synthesis**).
- No numeric benchmark exists in the wiki for VibeVoice-ASR, VibeVoice-ASR-Streaming, GLM-ASR-Nano (figure-only), or Fun-ASR-MLT-Nano. Their rank is unknown, not low.[^vibevoice-asr-card][^glm-asr-nano-card][^fun-asr-mlt-nano-card]
- No concept page exists for upstream OpenAI Whisper model cards, whisper.cpp, Moonshine, Voxtral, Granite Speech, Canary-180M-Flash, GigaAM, PhoWhisper, ChunkFormer, Zipformer, Kyutai, or proprietary APIs. Their appearance here comes from catalogs, comparison columns, or anecdotes. Compile their primary sources before relying on them.[^audio-cpp-gguf-readme][^claude-pipeline-report]
- Benchmarks and releases are time-sensitive; `stale_after: 2027-10-06` follows the `stt` domain rule.

[^parakeet-ctc-card]: [Parakeet CTC 0.6B](../raw/parakeet-ctc-0.6b.md) — locators: frontmatter `license`, `model-index`; body `Performance` WER table (9 sets incl. Common Voice; this page averages the 8 Open ASR sets excluding Common Voice); `Model Architecture`; `Training` (64K hours).
[^parakeet-ctc-11-card]: [Parakeet CTC 1.1B](../raw/parakeet-ctc-1.1b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table; `How to Use` NeMo-Speech.cpp GGUF path.
[^parakeet-rnnt-card]: [Parakeet RNNT 0.6B](../raw/parakeet-rnnt-0.6b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table; Transformers RNNT usage with timestamps.
[^parakeet-rnnt-11-card]: [Parakeet RNNT 1.1B](../raw/parakeet-rnnt-1.1b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table.
[^parakeet-tdt-card]: [Parakeet TDT 0.6B V2](../raw/parakeet-tdt-0.6b-v2.md) — locators: `Model Architecture` (24-minute single pass, RTFx 3380 at batch 128); `Training` (~120K-hour Granary); `Performance` base table (avg 6.05), MUSAN SNR table, telephony table; `License` CC-BY-4.0.
[^parakeet-v3-card]: [Parakeet TDT 0.6B V3](../raw/parakeet-tdt-0.6b-v3.md) — locators: intro (25 languages, auto LID); `Model Architecture` (24 min full attention / 3 h local attention); `Performance` multilingual averages (FLEURS 11.97, MLS 7.83, CoVoST 11.98), English Open ASR row (avg 6.34), MUSAN table; NeMo-Speech.cpp usage; frontmatter `license`.
[^canary-1b-v2-card]: [Canary-1b-v2 model card](../raw/canary-1b-v2.md) — locators: `Key Features`; `Model Architecture` (978M, FastConformer + Transformer decoder); `Benchmark Results` (ASR aggregate table, HF Leaderboard mean 7.15 / RTFx 749, AST tables, MUSAN SNR table, hallucination 134.7 chars/min); `How to Use` timestamps; `License/Terms`.
[^nemotron-en-stream-card]: [Nemotron Speech Streaming EN 0.6B card](../raw/nemotron-speech-streaming-en-0.6b.md) — locators: `Model Architecture` (600M, cache-aware FastConformer-RNNT); `att_context_size` latency table; WER tables at 1.12/0.56/0.16/0.08 s (line ~620 for 6.93); `License`.
[^nemotron-35-asr-card]: [Nemotron 3.5 ASR model card](../raw/nemotron-3.5-asr-streaming-0.6b.md) — locators: `License` (OpenMDW-1.1, commercial use); supported-language tier lists; automatic language detection section; `att_context_size` table; H100 throughput comparison; FLEURS LangID/auto tables (ready-tier averages, vi-VN row); NeMo-Speech.cpp `q8_0.gguf` usage.
[^parakeet-eou-card]: [Parakeet Realtime EOU 120M v1 card](../raw/parakeet_realtime_eou_120m-v1.md) — locators: frontmatter `license`; `Model Architecture` (120M, 17 layers, `[70, 1]`); EOU latency percentiles; 160 ms Open ASR WER table (avg 9.30).
[^multitalker-parakeet-card]: [Multitalker Parakeet Streaming 0.6B v1 card](../raw/multitalker-parakeet-streaming-0.6b-v1.md) — locators: `Model Architecture` (speaker-kernel injection, multi-instance); latency mapping; multitalker cpWER table with Streaming Sortformer v2 frontend; `Evaluation: Single-speaker Mode ASR Performance` table (base 7.16, single-speaker 7.44, ~line 437); license.
[^qwen3-asr-readme]: [Qwen3-ASR README and model card](../raw/Qwen3-ASR-0.6B.md) — locators: frontmatter `license`; model/language table (30 languages, 22 dialects, ForcedAligner 11 languages); `Key capabilities`; `qwen-asr-serve` / vLLM serving fences; evaluation tables (public-set WER, internal sets incl. dialect dialog, language-ID accuracy, streaming vs offline, forced-alignment shift).
[^ark-asr-3b-card]: [ARK-ASR-3B model card](../raw/ARK-ASR-3B.md) — locators: frontmatter `license`; `Supported Languages`; `Model Overview`; `Performance > English WER` (3B and 0.6B rows); `Performance > Chinese CER`; RTFx statement; `vLLM Online Serving`.
[^audio8-asr-01b-card]: [Audio8-ASR-0.1B model card](../raw/Audio8-ASR-0.1B.md) — locators: frontmatter `license` (cc-by-nc-4.0), `language`; `Model Overview` (103,502,336 / 323,990,528 params); `Evaluation Results` table (7-split mean 7.03, RTFx 741.15, WenetSpeech CER); `Related Releases` (ONNX ~1.1 GB, iOS ~200 MB); `Hotword Boosting`.
[^audio8-infinite-card]: [Audio8 ASR Infinite model card](../raw/Audio8-ASR-Infinite.md) — locators: frontmatter `license`, `language`; `Highlights` (clock, rolling KV, semantic VAD); `Optimized operation points` table; `Architecture` component table; `Checkpoint specification` (8.17 GB); `Evaluation` table at 480 ms vs Voxtral and Nemotron 3.5 at 560 ms.
[^fun-asr-nano-card]: [Fun-ASR-Nano-2512 model card](../raw/Fun-ASR-Nano-2512.md) — locators: model family table (0.8B; zh/en/ja; dialects/accents); `TODO` (timestamps, diarization unchecked); `Performance` open-source WER table (AISHELL-1, WenetSpeech, incl. GLM-ASR-nano and Whisper-large-v3 columns) and industry WER table (averages 16.72 / 26.13 / 33.39).
[^fun-asr-mlt-nano-card]: [Fun-ASR-MLT-Nano-2512 model card](../raw/Fun-ASR-MLT-Nano-2512.md) — locators: frontmatter `license`; supported-languages list (31); inference fence with `hotwords`, `itn`, `vad_model="fsmn-vad"`; `Performance` scope note (no MLT-specific column).
[^fun-asr-nano-gguf-card]: [Fun-ASR-Nano GGUF model card](../raw/Fun-ASR-Nano-GGUF.md) — locators: `Files` table (encoder 470 MB; Q4_K_M 484 MB, Q8_0 805 MB); quantization tier table (CER 8.35/8.25/8.30, speed); CPU claim vs whisper.cpp 22–31%.
[^glm-asr-nano-card]: [GLM-ASR-Nano-2512 model card](../raw/GLM-ASR-Nano-2512.md) — locators: frontmatter `license` (mit), `language`; `Model Introduction` (1.5B, dialects, low-volume, 4.10 average); `Benchmark` (`bench.png` only).
[^cohere-arabic-card]: [Cohere Transcribe Arabic model card](../raw/cohere-transcribe-arabic-07-2026.md) — locators: spec table (2B, Conformer encoder-decoder, Apache 2.0); `vLLM Integration`; `Results` leaderboard table dated 07.07.2026 (Average WER/CER rows incl. Qwen3-ASR 1.7B and Whisper Large v3); `Strengths and Limitations`.
[^vibevoice-asr-card]: [VibeVoice-ASR model card](../raw/VibeVoice-ASR.md) — locators: frontmatter `license`, `language`; feature list (60-minute single pass in 64K tokens, hotwords, Who/When/What, 50+ languages, code-switching); `Evaluation` (figures only, no text values).
[^vibevoice-asr-streaming-1-5b-card]: [VibeVoice-ASR-Streaming-1.5B model card](../raw/VibeVoice-ASR-Streaming-1.5B.md) — locators: frontmatter `license`, 10-language list; intro (streaming who-said-what, hotwords); `Evaluation` (figure only).
[^vibevoice-asr-streaming-7b-card]: [VibeVoice-ASR-Streaming-7B model card](../raw/VibeVoice-ASR-Streaming-7B.md) — locators: frontmatter; H2 checkpoint title; intro and `Evaluation` (figure only; text identical to the 1.5B card apart from the title).
[^vibevoice-asr-streaming-7b-gguf-card]: [VibeVoice ASR Streaming 7B GGUF for audio.cpp](../raw/VibeVoice-ASR-Streaming-7B-GGUF.md) — locators: file list (BF16, Q8_0 recommended, Q4_K); `Use with audio.cpp` (model manager, CLI, server, live streaming).
[^moss-transcribe-cpp-gguf-card]: [MOSS-Transcribe-Diarize GGUF](../raw/moss-transcribe.cpp-gguf.md) — locators: intro (joint transcription + diarization + timestamps, CPU, no Python); F32 3.4 GB note; file/size/wall-time/transcript-identity table on the 11 s JFK clip; frontmatter `license`.
[^sensevoice-small-gguf-card]: [SenseVoiceSmall GGUF for audio.cpp](../raw/SenseVoiceSmall-GGUF-audiocpp.md) — locators: frontmatter `license`, `language`; `File` (254,211,200 bytes); `Usage`; export and parity-check section.
[^audio-flamingo-gguf-card]: [Audio Flamingo 3 and Next GGUF](../raw/Audio-Flamingo-GGUF.md) — locators: frontmatter `license` / `license_name: nvidia-oneway-noncommercial`; `Usage` ASR CLI; CUDA performance table (RTX 5090, RTF, peak VRAM).
[^faster-whisper-readme]: [Faster-Whisper README](../raw/faster-whisper.md) — locators: header (CTranslate2, up to 4x claim); `Benchmark` (Large-v2 GPU table, distil-large-v3 table, small model CPU table); `Usage` (`BatchedInferencePipeline`, `turbo`, `distil-large-v3`, VAD filter).
[^audio-cpp-gguf-readme]: [audio.cpp GGUF Model Packages](../raw/audio.cpp-gguf.md) — locators: package table rows (Canary-180M-Flash, Citrinet, Cohere-Transcribe, CrisperWhisper2.0, Fun-ASR-Nano-2512, GigaAM, Granite-Speech-5.0-470M-TurboCTC, Hviske-v5.3, Kroko, MMS-Forced-Aligner, MOSS-Transcribe-Diarize, Moonshine-Streaming, Nemotron-3.5-ASR, Niagara, Parakeet-TDT-0.6B-v3, Qwen3-ASR-0.6B/1.7B, Qwen3-ForcedAligner, VibeVoice-ASR); ASR CLI example.
[^parakeet-readme]: [Parakeet ASR server README](../raw/parakeet.md) — locators: intro (Go, ONNX Runtime, Parakeet TDT 0.6B, Whisper-compatible API, SSE); Docker CPU/CUDA images; license section.
[^wlk-readme]: [WhisperLiveKit README](../raw/WhisperLiveKit.md) — locators: intro; `--backend-policy` (SimulStreaming / LocalAgreement); `--backend` selector list; API compatibility section.
[^realtimestt-readme]: [RealtimeSTT README](../raw/RealtimeSTT.md) — locators: intro (VAD-gated recording, realtime + final transcription engines, wake word); server section.
[^speaches-readme]: [Speaches README](../raw/speaches.md) — locators: overview excerpt (OpenAI-compatible, faster-whisper STT, SSE streaming, dynamic model loading).
[^index-echo-s2tt-gguf]: [Index-Echo S2TT GGUF](../raw/Index-Echo-S2TT-GGUF.md) — locators: intro (2B/9B, Chinese speech → timestamped transcript + en/es/ja translation, audio.cpp).
[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `PHẦN 1` §4 STT/ASR table (PhoWhisper, ChunkFormer-large-vie, sherpa-onnx Zipformer VN, Qwen3-ASR and Nemotron Vietnamese rows); `PHẦN 2` hardware tiers. LLM-generated report; figures are its citations, not verified here.
[^reddit-asr-tts-thread]: [Good ASR and TTS models? thread capture](../raw/good_asr_and_tts_models.md) — locators: `Comments 51` (Nemotron 3.5 streaming pick; Qwen3-ASR VRAM, streaming-vs-Parakeet, VAD-frontend remarks).
[^reddit-noisy-stt]: [Best Speech-to-Text in 2025? thread capture](../raw/best_speechtotext_in_2025.md) — locators: `Comments 53` (Parakeet 400–500% faster remark; Whisper-large-v3 plus preprocessing defence; Canary/Granite mentions).
[^reddit-open-stt]: [What's the best open speech to text today? thread capture](../raw/whats_the_best_open_speech_to_text_today.md) — locators: `Comments 36` (Qwen3-ASR least-hallucination remarks; turbo vs large-v3; Moonshine English low-latency remark).
[^reddit-stt-llm-tts-thread]: [STT -> LLM -> TTS pipeline thread capture](../raw/stt_llm_tts_pipeline.md) — locators: replies on Parakeet v2 vs Whisper (~5x) and v3 multilingual slowdown.
[^reddit-usable-stt]: [Best STT API for voice agents? thread capture](../raw/best_stt_api_for_voice_agents_i_care_more_about.md) — locators: prompt and top replies (first stable text, partial stability, endpointing, barge-in, entity accuracy checklist).
