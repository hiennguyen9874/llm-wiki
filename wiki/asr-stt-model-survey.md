---
type: Concept
title: ASR/STT Model Survey
description: Survey of every ASR/STT model compiled in the wiki — NVIDIA Parakeet, Nemotron, and Canary; Qwen3-ASR; Fun-ASR and SenseVoice; GLM-ASR; AutoArk ARK and Audio8; Hojo-ASR; Higgs Audio STT; IBM Granite; NetEase Confucius4-R2T2; Mistral Voxtral; VibeVoice-ASR; MOSS-Audio and MOSS-Transcribe; Cohere Transcribe; Meta Omnilingual; OpenAI Whisper, Distil-Whisper, and Whisper runtimes; plus Vietnamese PhoWhisper, ChunkFormer, and ZipFormer — compared by architecture, size, languages, streaming mode, license, reported benchmarks, and edge packaging.
tags: [stt, asr, survey, comparison, streaming, multilingual, benchmarks, edge-deployment]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T03:56:09Z }
stale_after: 2027-10-06
sources:
  - id: vi-primary-research
    resource: ../raw/vietnamese-asr-research-2026-10-07/README.md
    scope: ../raw/vietnamese-asr-research-2026-10-07/
    kind: documentation
    title: Vietnamese ASR primary-source follow-up
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
  - id: canary-qwen-2p5b-card
    resource: ../raw/canary-qwen-2.5b.md
    kind: documentation
    title: Canary-Qwen-2.5B model card
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
  - id: qwen3-asr-hf-card
    resource: ../raw/Qwen3-ASR-0.6B-hf.md
    kind: documentation
    title: Qwen3-ASR-0.6B-hf Transformers-native model card
  - id: ark-asr-3b-card
    resource: ../raw/ARK-ASR-3B.md
    kind: documentation
    title: ARK-ASR-3B model card
  - id: ark-asr-06b-card
    resource: ../raw/ARK-ASR-0.6B.md
    kind: documentation
    title: ARK-ASR-0.6B model card
  - id: hojo-asr-v1-doc
    resource: ../raw/Hojo-ASR-V1.md
    kind: documentation
    title: Hojo-ASR-V1 model card
  - id: higgs-v3-stt-card
    resource: ../raw/higgs-audio-v3-stt.md
    kind: documentation
    title: Higgs Audio v3 STT model card
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
  - id: cohere-03-2026-card
    resource: ../raw/cohere-transcribe-03-2026.md
    kind: documentation
    title: Cohere Transcribe model card
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
  - id: moss-transcribe-diarize-card
    resource: ../raw/MOSS-Transcribe-Diarize.md
    kind: documentation
    title: MOSS-Transcribe-Diarize 0.9B HF model card
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
  - id: voxtral-mini-3b-card
    resource: ../raw/Voxtral-Mini-3B-2507.md
    kind: documentation
    title: Voxtral Mini 3B 2507 model card
  - id: voxtral-mini-4b-realtime-card
    resource: ../raw/Voxtral-Mini-4B-Realtime-2602.md
    kind: documentation
    title: Voxtral Mini 4B Realtime 2602 model card
  - id: voxtral-small-24b-card
    resource: ../raw/Voxtral-Small-24B-2507.md
    kind: documentation
    title: Voxtral Small 24B 2507 model card
  - id: fast-gpu-asr-readme
    resource: ../raw/fast-gpu-asr.md
    kind: documentation
    title: Fast GPU ASR README
  - id: omnilingual-readme
    resource: ../raw/omnilingual-asr.md
    kind: documentation
    title: Omnilingual ASR README (1600+ languages)
  - id: thewhisper-turbo-card
    resource: ../raw/thewhisper-large-v3-turbo.md
    kind: documentation
    title: 'Elastic model: thewhisper-large-v3-turbo'
  - id: whisper-v3-card
    resource: ../raw/whisper-large-v3.md
    kind: documentation
    title: Whisper large-v3 model card (Hugging Face)
  - id: whisper-turbo-card
    resource: ../raw/whisper-large-v3-turbo.md
    kind: documentation
    title: Whisper large-v3-turbo model card (Hugging Face)
  - id: distil-large-v3.5-card
    resource: ../raw/distil-large-v3.5.md
    kind: documentation
    title: Distil-Whisper Distil-Large-v3.5 model card
  - id: confucius4-r2t2-readme
    resource: ../raw/Confucius4-R2T2.md
    kind: documentation
    title: Confucius4-R2T2 GitHub README
  - id: phonon-2-card
    resource: ../raw/Phonon-2.md
    kind: documentation
    title: Phonon-2 model card
  - id: granite-turboctc-card
    resource: ../raw/granite-speech-5.0-470m-turboctc.md
    kind: documentation
    title: Granite-Speech-5.0-470M-TurboCTC model card
  - id: indic-conformer-card
    resource: ../raw/indic-conformer-600m-multilingual.md
    kind: documentation
    title: IndicConformer-600M-Multilingual model card
  - id: orukeet-card
    resource: ../raw/orukeet.md
    kind: documentation
    title: Orukeet model card
  - id: parakeet-redux-card
    resource: ../raw/parakeet-redux.md
    kind: documentation
    title: Moondream Parakeet Redux model card
  - id: parakeet-ultra-card
    resource: ../raw/parakeet-ultra.md
    kind: documentation
    title: Moondream Parakeet Ultra model card
  - id: seamless-m4t-v2-card
    resource: ../raw/seamless-m4t-v2-large.md
    kind: documentation
    title: SeamlessM4T v2 model card (facebook/seamless-m4t-v2-large)
  - id: whistle-card
    resource: ../raw/whistle.md
    kind: documentation
    title: 'Whistle: Speech Recognition for Tiny Devices'
  - id: moss-audio-card
    resource: ../raw/MOSS-Audio-4B-Instruct.md
    kind: documentation
    title: MOSS-Audio model card and README (4B/8B Instruct and Thinking)
  - id: transcribe-cpp-readme
    resource: ../raw/transcribe.cpp.md
    kind: documentation
    title: transcribe.cpp README
  - id: nemo-speech-readme
    resource: ../raw/NeMo-Speech.cpp.md
    kind: documentation
    title: NeMo-Speech.cpp README
  - id: speaker-diar-coreml-card
    resource: ../raw/speaker-diarization-coreml.md
    kind: documentation
    title: Speaker Diarization Core ML
---

The master catalog has 52 ASR/STT entries (including newly captured PhoWhisper, Vietnamese ChunkFormer and ZipFormer30M), counting checkpoint families, runtime-backed Whisper, and separately documented packagings rather than 52 unique upstream models (**Observed** catalog count): 12 NVIDIA NeMo checkpoints (Parakeet CTC/RNNT/TDT, Canary-1b-v2, Canary-Qwen-2.5B, Nemotron streaming, the EOU and multitalker variants), plus [Orukeet](orukeet.md) as the Gabor-frozen Parakeet TDT V3 finetune, [Parakeet Redux](parakeet-redux.md) as the ternary 178 MB V3 derivative, and [Parakeet Ultra](parakeet-ultra.md) as the post-trained full-precision V3 derivative, a second group of LLM-decoder or audio-LLM recognizers (Qwen3-ASR, ARK-ASR 3B and 0.6B, Audio8, Hojo-ASR-V1, Higgs Audio v3 STT, Confucius4-R2T2, Voxtral Mini 3B / Small 24B / Mini 4B Realtime, Fun-ASR, GLM-ASR, VibeVoice-ASR, MOSS-Audio, MOSS-Transcribe-Diarize 0.9B plus its GGUF port, Cohere Transcribe 03-2026 multilingual plus Arabic), Meta Omnilingual ASR as the massive-multilingual family, upstream OpenAI Whisper Large v3 and Large v3 Turbo plus Distil-Large-v3.5 and TheWhisper-Large-V3-Turbo as the distilled/optimized-Whisper line, plus IBM Granite Speech 5.0 470M TurboCTC as the compact offline Conformer-CTC edge option, plus AI4Bharat IndicConformer-600M-Multilingual as the 22-Indic-language hybrid CTC plus RNNT option, plus Meta [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) as the mass-multilingual translation-plus-ASR option (2.3B UnitY2, S2ST/S2TT/T2ST/T2TT plus ASR, no numeric benchmark in card), plus Whisper reached through runtimes and a set of GGUF/ONNX edge packages, plus [Whistle](whistle.md) as the 16.9 MB on-device multilingual option sharing the Needle CPU engine. The source cards back three broad findings. First, offline English accuracy clusters between about 5% and 7.7% average WER on the Hugging Face Open ASR Leaderboard sets. ARK-ASR-3B reports 5.04, Parakeet TDT V2 6.05, Parakeet Ultra 5.80, and Phonon-2 5.21, but their card protocols differ; Phonon-2's best-sub-900MB positioning is its vendor's claim, not a wiki-verified ranking.[^ark-asr-3b-card][^parakeet-tdt-card][^parakeet-ultra-card][^phonon-2-card] Second, purpose-built streaming models trade about 1.5 WER points for 80 ms latency (Nemotron) or swap language breadth for native clocked streaming (Audio8 Infinite). Third, coverage, license, and deployment target usually decide the choice more than leaderboard rank, especially for Chinese dialects, Arabic, Vietnamese, speaker attribution, and CPU/edge use. Every number below is a vendor or community claim that this wiki has not reproduced (**Synthesis**).

## Scope and method

- **Included:** every concept whose primary job is turning speech into text: model cards, GGUF/ONNX packagings of those models, and the runtimes that serve them. Retrieval used the root index, `stt`/`asr` tag search, and exact search for model names inside pipeline and community pages (**Synthesis**).
- **Adjacent, not surveyed as standalone ASR:** diarization-only models, speech-to-speech systems, translation-only packages, turn detection, and noise preprocessing. Multitask models with explicit ASR capability (MOSS-Audio and SeamlessM4T v2) remain in the catalog. They are listed under [Adjacent concepts](#adjacent-concepts) (**Synthesis**).
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
| [Phonon-2](phonon-2.md) | Fermion Research (base: NVIDIA) | ~0.6B quantized, 164 MB download, ~2.1-bit encoder | FastConformer-TDT (parakeet-tdt-0.6b-v3 lineage) | en, PnC | offline throughput; MLX / CPU / CUDA Docker | CC-BY-4.0 (CLI/code Apache-2.0) | 5.21 mean over 7 Open ASR splits; 174x realtime M5 Air, 6680x H100 batch-128[^phonon-2-card] |
| [Orukeet](orukeet.md) | Oruk AI (base: NVIDIA) | 627M (626.9M trainable, 12,288 frozen Gabor taps) | FastConformer-TDT + frozen Gabor depthwise filters | 25 European, auto language ID | offline/batch; NeMo / Transformers / sherpa-onnx INT8 / native Q8-F16 / transcribe.cpp Q8 / Core ML preview | CC-BY-SA-4.0 weights (code MIT) | FLEURS pooled 9.85 vs 11.01 (10.6% rel); LS clean 1.46 / other 2.86[^orukeet-card] |
| [Parakeet Redux](parakeet-redux.md) | Moondream (base: NVIDIA) | ~0.6B ternary, 178 MB weights, 1.58-bit encoder | FastConformer-TDT (parakeet-tdt-0.6b-v3 lineage) | 25 European, same tokenizer/conventions as V3 | offline via Photon (x86 AVX-512-VNNI / ARM NEON / Apple Metal) | CC-BY-4.0 | en 6.55 7-set avg; FLEURS 10.56 vs 11.62; TED-LIUM 2.51 vs 2.71; 113× on 8 x86 cores[^parakeet-redux-card] |
| [Parakeet Ultra](parakeet-ultra.md) | Moondream (base: NVIDIA) | ~0.6B full precision | FastConformer-TDT (parakeet-tdt-0.6b-v3 lineage) | 25 European, same tokenizer/conventions as V3 | offline via Photon on NVIDIA GPU | CC-BY-4.0 | en 5.80 7-set avg; FLEURS 9.55 vs 11.62; TED-LIUM 1.94 vs 2.71; B200 9,743× LibriSpeech[^parakeet-ultra-card] |
| [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) | IBM Granite | 470M | Conformer encoder + 16,384-BPE CTC head, 8x downsampling, greedy non-autoregressive | en | offline; Transformers / mlx-audio / transcribe.cpp GGUF | Apache-2.0 | no numeric WER in card; Open ASR + FFASR plots image-only[^granite-turboctc-card] |
| [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) | AI4Bharat | 600M | Conformer hybrid CTC + RNNT | 22 Indic (IN-22) | offline (Transformers `AutoModel`, CTC/RNNT decode) | MIT | no numeric WER in card; dual CTC/RNNT inference[^indic-conformer-card] |
| [Canary-1b-v2](canary-1b-v2.md) | NVIDIA NeMo | 978M | FastConformer encoder + Transformer decoder (multitask) | 25 European + X↔En translation | offline, auto-chunked long-form | CC-BY-4.0 | Open ASR mean 7.15 at RTFx 749; FLEURS 8.40[^canary-1b-v2-card] |
| [Canary-Qwen-2.5B](canary-qwen-2.5b.md) | NVIDIA NeMo | 2.5B | SALM (FastConformer encoder + Qwen3-1.7B decoder + LoRA) | en, PnC | offline | CC-BY-4.0 | Open ASR mean 5.63 at RTFx 418; dual ASR/LLM modes[^canary-qwen-2p5b-card] |
| [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) | NVIDIA | 600M | cache-aware FastConformer-RNNT | en, PnC | streaming 80–1120 ms | NVIDIA Open Model License | 6.93 at 1.12 s → 8.43 at 80 ms[^nemotron-en-stream-card] |
| [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) | NVIDIA | 600M | cache-aware FastConformer-RNNT + language-ID prompt | 40 locales (19 ready, 13 broad, 8 adaptation) | streaming 80–1120 ms | OpenMDW-1.1 | FLEURS ready-tier avg 8.84 at 1.12 s / 10.38 at 80 ms[^nemotron-35-asr-card] |
| [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md) | NVIDIA | 120M | cache-aware FastConformer-RNNT + `<EOU>` token | en | streaming 80–160 ms | NVIDIA Open Model License | 9.30 avg at 160 ms; EOU P50 160 ms[^parakeet-eou-card] |
| [Multitalker Parakeet Streaming 0.6B v1](multitalker-parakeet-streaming-0.6b-v1.md) | NVIDIA | 600M per speaker instance | FastConformer + speaker-kernel injection | en | streaming (benchmarked at 1.12 s) | NVIDIA Open Model License | cpWER AMI IHM 21.26; single-speaker 7.44[^multitalker-parakeet-card] |
| [Qwen3-ASR family](qwen3-asr-family.md) | Qwen | 1.7B / 0.6B (+ 0.6B forced aligner) | Qwen3-Omni-based audio LLM | 30 languages + 22 Chinese dialects | unified offline/streaming | Apache-2.0 | 1.7B LibriSpeech 1.63 / 3.38; Open ASR HF snapshot 5.59 / 6.31 (1.7B / 0.6B); language ID 97.9%[^qwen3-asr-readme][^qwen3-asr-hf-card] |
| [ARK-ASR-3B](ark-asr-3b.md) | AutoArk | 3B (0.6B sibling) | Whisper-style encoder + MLP + Qwen decoder | 19 | offline, 30 s window | Apache-2.0 | 5.04 Open ASR 7-split avg; RTFx 490.98[^ark-asr-3b-card] |
| [ARK-ASR-0.6B](ark-asr-0.6b.md) | AutoArk | 0.6B decoder + Whisper-style encoder | Whisper-style encoder (RoPE) + MLP + Qwen2 decoder; TD + OPD distillation | 19 | offline, 30 s window | Apache-2.0 | own card: en 6.55 / zh 4.30 avg (`open-audio-opd`); 3B card: en 5.97 (see [Contradictions](#contradictions))[^ark-asr-06b-card][^ark-asr-3b-card] |
| [Hojo-ASR-V1](hojo-asr-v1.md) | Hojo AI | 4B | Encoder-Adapter-Qwen3 LLM + multi-frame acoustic fusion, RL-tuned | Mandarin, en, Cantonese, Sichuan dialect | offline batch (`hojo-asr`) | Apache-2.0 | 8-set English WER, 5.28 mean (*computed*; protocol not stated)[^hojo-asr-v1-doc] |
| [Higgs Audio v3 STT](higgs-audio-v3-stt.md) | Boson AI | 2.68B | Whisper-Large-v3 encoder + Qwen3-1.7B decoder, thinking mode | en | offline, 30 s chunks | Apache-2.0 | no numeric WER in card; June 2026 retrain awaits leaderboard re-evaluation[^higgs-v3-stt-card] |
| [Audio8-ASR-0.1B](audio8-asr-0.1b.md) | AutoArk | 0.104B LM / 0.324B total | Qwen3-ASR encoder + 8-layer Qwen LM | 7 | offline short-form, 30 s cap | CC-BY-NC-4.0 | 7.03 Open ASR 7-split mean; RTFx 741 on H200[^audio8-asr-01b-card] |
| [Audio8 ASR Infinite](audio8-asr-infinite.md) | Edge0 | Voxtral-Realtime-4B audio tower + Qwen2.5-3B decoder (8.17 GB bf16) | native streaming (DSM-style) + semantic VAD heads | zh, en | streaming: 80/120/160 ms clock, 240–560 ms delay, 24/7 rolling KV | Apache-2.0 | AISHELL-1 CER 1.75; LibriSpeech 3.04 / 6.81 at 480 ms[^audio8-infinite-card] |
| [Confucius4-R2T2](confucius4-r2t2.md) | NetEase Youdao | ~1.7B (Qwen3-ASR-1.7B base) | Qwen3-ASR audio LLM + Longest Stable Prefix training | zh + en primary, plus fr, de, it, ja, ko, pt, ru, es, ar, etc. | true streaming, append-only, 80 ms–2 s chunks | code Apache-2.0, weights NetEase Model Use License Agreement | EN 160 ms: AMI 11.37 / Earnings22 9.36 / TED-LIUM 3.34; ZH 160 ms: Wenet-net 5.87 / Wenet-meeting 7.27 / CN-RealSI 3.48[^confucius4-r2t2-readme] |
| [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) | Mistral AI | ~3.4B LM + ~970M causal audio encoder | native streaming, sliding-window attention | 13 | streaming: configurable 80–2400 ms delay (480 ms recommended) | Apache-2.0 | FLEURS avg 8.72 at 480 ms; long/short-form English near offline Transcribe 2.0[^voxtral-mini-4b-realtime-card] |
| [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md) | Mistral AI | 3B (Ministral 3B) | audio-text LLM (transcription + audio Q&A + voice function calling) | 8 (en, fr, de, es, it, pt, nl, hi), auto LID | offline; 30 min transcription / 40 min understanding in 32k context | Apache-2.0 | WER figures image-only, none recorded; ~9.5 GB GPU RAM bf16[^voxtral-mini-3b-card] |
| [Voxtral Small 24B 2507](voxtral-small-24b-2507.md) | Mistral AI | 24B (Mistral Small 3) | audio-text LLM (as Mini 3B; function calling experimental) | 8, auto LID | offline; 30 / 40 min in 32k context | Apache-2.0 | WER figures image-only, none recorded; ~55 GB GPU RAM, TP-2 vLLM[^voxtral-small-24b-card] |
| [Fun-ASR-Nano-2512](fun-asr-nano-2512.md) | Tongyi Lab / FunAudioLLM | 0.8B | end-to-end LLM-based ASR | zh/en/ja + 7 dialects, 26 accents, lyrics/rap | real-time claimed | Apache-2.0 | AISHELL-1 1.80; industry-set avg 16.72[^fun-asr-nano-card] |
| [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md) | FunAudioLLM | 0.8B | same family | 31 (East/Southeast Asian focus, incl. vi) | offline (optional FSMN-VAD segmentation) | Apache-2.0 | no checkpoint-specific results published[^fun-asr-mlt-nano-card] |
| [GLM-ASR-Nano-2512](glm-asr-nano-2512.md) | zai-org | 1.5B | Transformers seq2seq ASR | en, zh, Cantonese/dialects | offline | MIT | claimed 4.10 avg error (figure only)[^glm-asr-nano-card] |
| [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md) | Cohere / Cohere Labs | 2B | Conformer encoder + light Transformer decoder | ar (+ dialects), en | offline, auto-chunked long-form | Apache-2.0 | Open Universal Arabic leaderboard avg 25.87 WER / 11.80 CER[^cohere-arabic-card] |
| [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) | Cohere / Cohere Labs | 2B | Conformer encoder + light Transformer decoder | 14 (9 EU + zh, ja, ko, vi + ar) | offline, auto-chunked long-form | Apache-2.0 | Open ASR English avg 5.42, best in its card table[^cohere-03-2026-card] |
| [VibeVoice-ASR](vibevoice-asr.md) | Microsoft Research | not stated | unified ASR + diarization + timestamps | 50+, code-switching | offline, 60 min single pass | MIT | no numeric results in card text[^vibevoice-asr-card] |
| [VibeVoice-ASR-Streaming-1.5B](vibevoice-asr-streaming-1.5b.md) | Microsoft Research | 1.5B | unified streaming speaker-attributed ASR | 10 | streaming | MIT | no numeric results in card text[^vibevoice-asr-streaming-1-5b-card] |
| [VibeVoice-ASR-Streaming-7B](vibevoice-asr-streaming-7b.md) | Microsoft Research | 7B | unified streaming speaker-attributed ASR | 10 | streaming | MIT | no numeric results; card text identical to 1.5B[^vibevoice-asr-streaming-7b-card] |
| [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) | OpenMOSS / MOSI.AI | 0.9B | joint transcription + diarization + timestamps + acoustic events | 50+ (14 MLC-SLM challenge langs incl. vi) | offline long-form, 90 min single pass | Apache-2.0 | AISHELL-4 14.84 CER / 15.83 cpCER, Alimeeting 24.86 / 22.17, Podcast 5.97 / 7.37[^moss-transcribe-diarize-card] |
| [MOSS-Transcribe-Diarize GGUF](moss-transcribe-cpp-gguf.md) | OpenMOSS (port: moss-transcribe.cpp) | 3.4 GB F32 reference | joint transcription + diarization + timestamps | not stated in package card | long-form, CPU | Apache-2.0 | Q4_0 511 MB, 2.2x F32 speed, word-identical output[^moss-transcribe-cpp-gguf-card] |
| [MOSS-Audio family](moss-audio.md) | OpenMOSS / MOSI.AI | 4.6B (4B) / 8.6B (8B), Instruct + Thinking | dedicated 12.5 Hz encoder + adapter + Qwen3 LLM, DeepStack + time tokens | en, zh (frontmatter; full list unstated) | offline (no streaming claim), SGLang serving | Apache-2.0 | ASR overall CER 11.30 (8B-Instruct); timestamp AAS 35.77 zh / 131.61 en; captioning avg 3.7252; general-audio 71.08 in-table (70.80 prose)[^moss-audio-card] |
| [SenseVoiceSmall GGUF](sensevoice-small-gguf.md) | FunAudioLLM (audio.cpp export) | 254 MB Q8_0 file | SenseVoice | zh, en, yue, ja, ko | offline CPU | Apache-2.0 | exact-match Mandarin parity with original Q8[^sensevoice-small-gguf-card] |
| [Omnilingual ASR](omnilingual-asr.md) | Meta | W2V 0.3–6.5B / CTC 0.3–6.5B / LLM 1.6–7.8B | W2V SSL + CTC + LLM with optional language conditioning (+ Unlimited v2, 7B zero-shot) | 1600+, `{lang}_{script}` IDs | offline; Unlimited v2 for unbounded length | Apache-2.0 | 7B LLM-ASR SOTA claim, CER below 10 for 78% of languages[^omnilingual-readme] |
| [PhoWhisper](phowhisper.md) | VinAI | 39M–1.55B, five variants | finetuned multilingual Whisper | vi | offline/turn-final; no native-streaming evidence | BSD-3-Clause | large VIVOS4.67 / CMV8.14 / VLSP2020T1 13.75 / T2 26.68[^vi-primary-research] |
| [ChunkFormer Vietnamese](chunkformer-vietnamese.md) | Khanh Le et al. | CTC110M / RNNT113M | masked chunk-wise Conformer + CTC/RNNT | vi | large long-form; ONNX streaming requires streaming-trained checkpoint | CTC CC-BY-NC-4.0; RNNT large CC-BY-4.0 | RNNT VIVOS2.49 / CMV5.18 / VLSP2020T1 12.75 / T2 20.47; small streaming card unavailable[^vi-primary-research] |
| [ZipFormer30M Vietnamese](zipformer-30m-vietnamese.md) | hynt (ONNX: sherpa community) |30M| ZipFormer-RNNT |vi| CPU file throughput; native-streaming protocol unestablished | CC-BY-NC-ND-4.0 | VLSP2020T1 12.29; 12s audio/0.3s CPU claimed[^vi-primary-research] |
| Whisper via [Faster-Whisper](faster-whisper.md) | OpenAI weights / SYSTRAN CTranslate2 runtime | tiny … large-v3, turbo, distil-large-v3 | encoder-decoder | multilingual | offline; streaming only via wrappers | not compiled | large-v2: 13 min audio in 59 s int8, 2926 MB VRAM (RTX 3070 Ti)[^faster-whisper-readme] |
| [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) | TheStage AI (base: OpenAI whisper-large-v3-turbo) | S/M/L/XL Elastic tiers | Whisper encoder-decoder, ANNA-compressed | 28 frontmatter codes; benched en + DE/ES/FR/IT/PT | batch + push streaming (Apple SDK); Docker streaming server | CC-BY-4.0 | en mean 5.88 (L) vs 5.80 original; H100 bs=1 RTFx ~304 vs 109 original[^thewhisper-turbo-card] |
| [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) | OpenAI | 809M (decoder 32→4 layers) | Whisper encoder-decoder | 90-plus frontmatter codes | offline + sequential/chunked 30 s long-form; not natively streaming | MIT (card frontmatter) | no numeric WER/RTFx in card; qualitative faster/minor-degradation claim[^whisper-turbo-card] |
| [Distil-Large-v3.5](distil-large-v3.5.md) | Distil-Whisper (HF collaboration) | 756M | distilled Whisper-Large-v3 (2 decoder layers) | en | offline; sequential or chunked long-form; speculative-decoding draft for large-v3 | MIT | short-form avg 7.10 (OOD 7.08) vs turbo 7.25; long-form OOD 11.39 vs turbo 10.25; RTFx 1.46x turbo[^distil-large-v3.5-card] |
| [Whisper Large v3](whisper-large-v3.md) | OpenAI | 1550M | Whisper encoder-decoder (128 mel bins, Cantonese token) | ~99 frontmatter codes | offline + sequential/chunked 30 s long-form; not natively streaming | Apache-2.0 (card frontmatter) | no numeric WER/RTFx in card; 10–20% error reduction over large-v2 claim[^whisper-v3-card] |
| [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) | Meta Seamless | 2.3B | multitask UnitY2 (hierarchical char-to-unit upsampling, NAR text-to-unit) | ~100 (101 speech-in, 96 text, 35 speech-out claimed; incl. vi Sp+Tx both directions) | offline via Transformers; no streaming claim | CC-BY-NC-4.0 | no numeric WER/BLEU in card; metrics live in external zips[^seamless-m4t-v2-card] |
| [Whistle](whistle.md) | Cactus Compute | 16.9 MB single `.cact` | log-mel + conv stem + audio encoder + Needle-shaped decoder (gated cross-attention, laddered `--audio-depth`) | en, de, fr, es, it, nl, pl (auto LID) | offline, 30 s per pass, 16 kHz mono | Apache-2.0 | no numeric WER in text; WER/speed figures image-only (`whistle-benchmarks.svg` not compiled)[^whistle-card] |

## English accuracy (Open ASR Leaderboard)

Averages as published or *computed* from per-set cells; lower is better (**Reported** per row; ordering is **Synthesis**):

| Rank | Model | Avg WER | Sets | Notes |
| ---: | --- | ---: | --- | --- |
| 1 | ARK-ASR-3B | 5.04 | 7 splits | AMI 8.79 in this card; not a matched cross-card meeting ranking[^ark-asr-3b-card] |
| 2 | [Hojo-ASR-V1](hojo-asr-v1.md) (4B) | 5.28 | 8 (*computed*) | card prints no average, protocol, or normalization; AMI 8.64[^hojo-asr-v1-doc] |
| 3 | Cohere Transcribe 03-2026 | 5.42 | 8 | best avg in its card table dated 03.26.2026; LS clean 1.25 / LS other 2.37 best-in-table[^cohere-03-2026-card] |
| 4 | Qwen3-ASR-1.7B-hf | 5.59 | 7 | HF Open ASR Leaderboard snapshot dated 26 June 2026[^qwen3-asr-hf-card] |
| 5 | Canary-Qwen-2.5B | 5.63 | 8 | RTFx 418; dual ASR/LLM modes[^canary-qwen-2p5b-card] |
| 6 | [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) (size L) | 5.88 | 8 | S 6.12 / M 5.90 / XL 5.89; original 5.80 in the same card[^thewhisper-turbo-card] |
| 7 | [ARK-ASR-0.6B](ark-asr-0.6b.md) | 5.97 | 7 splits | sibling row in the 3B card; its own card reports 6.55 under `open-audio-opd` (see [Contradictions](#contradictions))[^ark-asr-3b-card][^ark-asr-06b-card] |
| 8 | Parakeet TDT 0.6B V2 | 6.05 | 8 | SNR 0 dB → 11.88; μ-law telephony 6.32[^parakeet-tdt-card] |
| 9 | Qwen3-ASR-0.6B-hf | 6.31 | 7 | same HF leaderboard snapshot, 26 June 2026[^qwen3-asr-hf-card] |
| 10 | Parakeet TDT 0.6B V3 | 6.34 | 8 | multilingual model, small English penalty[^parakeet-v3-card] |
| 11 | Nemotron Speech Streaming EN 0.6B | 6.93 | 8 | **streaming** at 1.12 s; 7.67 at 160 ms[^nemotron-en-stream-card] |
| 12 | Audio8-ASR-0.1B | 7.03 | 7 splits | 0.1B-LM, H200 RTFx 741[^audio8-asr-01b-card] |
| 13 | Canary-1b-v2 | 7.15 | 8 | also does translation; RTFx 749[^canary-1b-v2-card] |
| 14 | Parakeet RNNT 1.1B | 7.19 | 8 (*computed*) | lowercase output[^parakeet-rnnt-11-card] |
| 15 | Parakeet CTC 1.1B | 7.40 | 8 (*computed*) | lowercase output[^parakeet-ctc-11-card] |
| 16 | Multitalker Parakeet (single-speaker mode) | 7.44 | 8 | base reported at 7.16 in the same card[^multitalker-parakeet-card] |
| 17 | Parakeet RNNT 0.6B | 7.56 | 8 (*computed*) | [^parakeet-rnnt-card] |
| 18 | Parakeet CTC 0.6B | 7.66 | 8 (*computed*) | [^parakeet-ctc-card] |
| 19 | Parakeet Realtime EOU 120M | 9.30 | 8 | **streaming** at 160 ms, 120M params[^parakeet-eou-card] |

- Qwen3-ASR now has an Open ASR average from its Transformers-native card snapshot (26 June 2026): 1.7B-hf 5.59 and 0.6B-hf 6.31, slotting fourth and ninth in the table above; its LibriSpeech figures in the family README (1.7B: 1.63 clean / 3.38 other) sit in the same band as the leaders (**Reported**; ordering is **Synthesis**).[^qwen3-asr-readme][^qwen3-asr-hf-card]
- Not ranked: [Distil-Large-v3.5](distil-large-v3.5.md) reports a 7-set short-form average of 7.10 under its own post-normalization protocol, against 7.14 for Whisper-large-v3 and 7.25 for large-v3-turbo in the same table. It prints no 8-set Open ASR average.[^distil-large-v3.5-card] [Higgs Audio v3 STT](higgs-audio-v3-stt.md) declares its earlier card figures superseded and defers to a pending leaderboard re-evaluation. Voxtral Mini 3B and Small 24B publish WER only as images, as does [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) for its Open ASR and FFASR plots (**Reported**).[^higgs-v3-stt-card][^voxtral-mini-3b-card][^voxtral-small-24b-card][^granite-turboctc-card] [Confucius4-R2T2](confucius4-r2t2.md) reports its own 6-set English streaming table at 160 ms (AMI 11.37, Giga-clean 9.60, LS-clean 2.13, Earnings22 9.36, TED-LIUM 3.34, EN-RealSI 8.40) rather than the Open ASR 8-set protocol, so it is not ranked either (**Reported**).[^confucius4-r2t2-readme]
- Hojo-ASR-V1's second place rests on a mean computed from a table whose protocol the card does not state, so treat it as provisional (**Synthesis**).[^hojo-asr-v1-doc]
- [Phonon-2](phonon-2.md) reports a 5.21 mean over 7 Open ASR splits (LS clean/other, AMI, Earnings-22, GigaSpeech, SPGI, VoxPopuli) from a vendor-run table using the Open ASR Leaderboard code on the full test sets, with the teacher at 4.96 in the same table. It is not inserted in the ranked table because that table mixes 7- and 8-split card protocols (no TEDLIUM here) with different scoring; its card claims the most accurate open English ASR under 900 MB; that size-class ranking is unverified here (**Reported**; comparability is **Synthesis**).[^phonon-2-card]
- [Parakeet Ultra](parakeet-ultra.md) reports a 5.80 mean over the same 7 Open ASR splits (LS clean 1.41 / other 2.98, AMI 9.77, Earnings-22 9.76, GigaSpeech 7.71, SPGI 3.34, VoxPopuli 5.65) against 6.26 for the teacher in the same card, plus FLEURS 25-language average 9.55 vs 11.62 and TED-LIUM 1.94 vs 2.71. It is likewise not ranked for the 7/8-split protocol reason; its differentiator is beating the teacher on every headline suite at full precision with higher B200 batch throughput (LibriSpeech 9,743× vs 6,005×, AMI 6,688× vs 4,394×) (**Reported**; comparability is **Synthesis**).[^parakeet-ultra-card]
- The older Parakeet CTC/RNNT generation (64K-hour English, lowercase output) is 1.1–1.6 points behind TDT V2 (~120K-hour Granary, punctuated output) at the same 0.6B size. Doubling to 1.1B recovers only about 0.3–0.4 points (**Synthesis** from the per-card tables).[^parakeet-tdt-card][^parakeet-rnnt-11-card]

## Chinese accuracy (CER, lower is better)

| Model | AISHELL-1 | WenetSpeech meeting | WenetSpeech net | Source |
| --- | ---: | ---: | ---: | --- |
| Audio8 ASR Infinite (streaming, 480 ms) | **1.75** | — | — | [^audio8-infinite-card] |
| ARK-ASR-3B | 1.80 | **4.97** | **4.58** | [^ark-asr-3b-card] |
| Fun-ASR-nano (0.8B) | 1.80 | 6.60 | 6.01 | [^fun-asr-nano-card] |
| GLM-ASR-nano (1.5B, in Fun-ASR table) | 1.81 | 6.73 | — | [^fun-asr-nano-card] |
| ARK-ASR-0.6B | 2.02 | 5.92 | 4.96 | [^ark-asr-3b-card][^ark-asr-06b-card] |
| Confucius4-R2T2 (streaming, 160 ms) | — | 7.27 | 5.87 | [^confucius4-r2t2-readme] |
| Qwen3-ASR-1.7B | — (AISHELL-2 2.71) | 5.88 | 4.97 | [^qwen3-asr-readme] |
| Qwen3-ASR-0.6B | — (AISHELL-2 3.15) | 6.88 | 5.97 | [^qwen3-asr-readme] |
| Audio8-ASR-0.1B (internal eval) | — | 8.84 | 7.98 | [^audio8-asr-01b-card] |
| Whisper-large-v3 (in Fun-ASR table) | 4.72 | 18.39 | 11.89 | [^fun-asr-nano-card] |

- For dialects and hard conditions, the Fun-ASR card's industry sets (dialect, accent, lyrics, hip-hop, far-field) give Fun-ASR-nano a 16.72 average against 26.13 for GLM-ASR-Nano and 33.39 for Whisper-large-v3 (**Reported**).[^fun-asr-nano-card] Qwen3-ASR-1.7B reports KeSpeech 5.10 and 15.94 on its internal Chinese-dialect dialog set (**Reported**).[^qwen3-asr-readme]
- Nemotron 3.5 tiers Mandarin as broad-coverage, not transcription-ready. In Audio8 Infinite's table its AISHELL-1 CER is 12.93 at 560 ms, so the NVIDIA streaming line is not a Chinese choice (**Reported**; recommendation is **Synthesis**).[^nemotron-35-asr-card][^audio8-infinite-card]

## Multilingual coverage

| Model | Languages | Notable coverage |
| --- | --- | --- |
| [Omnilingual ASR](omnilingual-asr.md) | 1600+ | broadest in wiki; few-paired-examples extension claim; per-language CER in linked CSV, not compiled[^omnilingual-readme] |
| [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) | ~100 (101 speech-in / 96 text / 35 speech-out claimed) | S2ST/S2TT/T2ST/T2TT plus ASR; vie Sp+Tx both directions; 7 speech-only sources, zsm text-only[^seamless-m4t-v2-card] |
| VibeVoice-ASR | 50+ | code-switching, no language setting needed[^vibevoice-asr-card] |
| [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) | 50+ | 14 MLC-SLM challenge langs (en, fr, de, it, pt, es, ja, ko, ru, th, vi, tl, ur, tr); frontmatter lists en/zh only[^moss-transcribe-diarize-card] |
| Nemotron 3.5 ASR | 40 locales (32 usable out of the box) | streaming; vi, ar, hi, ja, ko ready; auto language detection appends an `<xx-XX>` tag[^nemotron-35-asr-card] |
| Fun-ASR-MLT-Nano | 31 | vi, id, th, ms, fil, ar, hi plus EU languages[^fun-asr-mlt-nano-card] |
| Qwen3-ASR | 30 + 22 Chinese dialects | singing and BGM audio; language ID 97.9% (1.7B) vs Whisper-large-v3 94.1%[^qwen3-asr-readme] |
| Canary-1b-v2 / Parakeet TDT V3 | 25 European | Canary adds En↔24 translation; V3 auto-detects language[^canary-1b-v2-card][^parakeet-v3-card] |
| [Orukeet](orukeet.md) | 25 European (same codes as V3) | Gabor-frozen V3 finetune; FLEURS pooled 9.85 vs 11.01 teacher[^orukeet-card] |
| [Parakeet Redux](parakeet-redux.md) | 25 European (same codes as V3) | ternary 1.58-bit V3 derivative; FLEURS 25-language average 10.56 vs 11.62, TED-LIUM 2.51 vs 2.71[^parakeet-redux-card] |
| [Parakeet Ultra](parakeet-ultra.md) | 25 European (same codes as V3) | post-trained full-precision V3 derivative; FLEURS 25-language average 9.55 vs 11.62, TED-LIUM 1.94 vs 2.71[^parakeet-ultra-card] |
| [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) | 22 Indic | as, bn, brx, doi, gu, hi, kn, kok, ks, mai, ml, mni, mr, ne, or, pa, sa, sat, sd, ta, te, ur; tokenizers linked externally[^indic-conformer-card] |
| ARK-ASR-3B | 19 | zh, en, ja, ko + 15 European[^ark-asr-3b-card] |
| [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) | 14 | en, fr, de, it, es, pt, el, nl, pl, zh, ja, ko, vi, ar[^cohere-03-2026-card] |
| [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) | 13 | en, fr, es, de, ru, zh, ja, it, pt, nl, ar, hi, ko[^voxtral-mini-4b-realtime-card] |
| [Voxtral Mini 3B](voxtral-mini-3b-2507.md) / [Small 24B](voxtral-small-24b-2507.md) 2507 | 8 | en, fr, de, es, it, pt, nl, hi with auto language detection[^voxtral-mini-3b-card][^voxtral-small-24b-card] |
| VibeVoice-ASR-Streaming | 10 | zh, en, fr, de, it, ja, ko, pt, ru, es[^vibevoice-asr-streaming-1-5b-card] |
| Audio8-ASR-0.1B | 7 | en, zh, fr, ja, yue, de, ko[^audio8-asr-01b-card] |
| [Whistle](whistle.md) | 7 | en, de, fr, es, it, nl, pl with auto language detection; silence returns empty transcript[^whistle-card] |
| SenseVoiceSmall | 5 | zh, en, yue, ja, ko[^sensevoice-small-gguf-card] |
| [Hojo-ASR-V1](hojo-asr-v1.md) | 4 | Mandarin, English, Cantonese, Sichuan dialect; zh-en code-switching focus, no Chinese numbers published[^hojo-asr-v1-doc] |
| [Confucius4-R2T2](confucius4-r2t2.md) | zh + en primary, others useful | fr, de, it, ja, ko, pt, ru, es, ar, etc.; true-streaming optimization targets Chinese and English[^confucius4-r2t2-readme] |

- **Vietnamese:** Qwen3-ASR FLEURS-vi5.55/8.52 (1.7B/0.6B) is now directly inspected in primary-paper AppendixTableA.2, not the family README; MLC-SLM-vi14.92/17.67 is also offline. Qwen streaming Table8 uses2s chunks/5-token fallback/four unfixed chunks and does not evaluate vi. Nemotron3.5 FLEURS-vi13.41→11.18 at80→1120ms is streaming. These are not a matched latency/normalization ranking (**Reported/Synthesis**).[^vi-primary-research][^nemotron-35-asr-card] Fun-ASR-MLT-Nano lists vi without a score; SeamlessM4Tv2 lists `vie` Sp+Tx without figures; compiled ParakeetV3/Canary do not cover vi.[^fun-asr-mlt-nano-card][^seamless-m4t-v2-card] [PhoWhisper](phowhisper.md), [ChunkFormer Vietnamese](chunkformer-vietnamese.md) and [ZipFormer30M](zipformer-30m-vietnamese.md) now have primary-source concepts; checkpoint-specific licenses and streaming limits matter more than the old AI-report labels.[^vi-primary-research]
- **Arabic:** Cohere Transcribe Arabic leads the Open Universal Arabic leaderboard average (25.87 / 11.80), ahead of Qwen3-ASR-1.7B (33.36 / 12.33) and Whisper-large-v3 (36.86 / 17.21) in the card's table. It has no language auto-detection, timestamps, or diarization (**Reported**).[^cohere-arabic-card]

## Streaming and latency

| Model | Streaming mechanism | Latency knob | Accuracy cost of low latency |
| --- | --- | --- | --- |
| Nemotron Speech Streaming EN 0.6B | cache-aware FastConformer, no overlapping recompute | `att_context_size` 80/160/560/1120 ms at inference | 6.93 → 8.43 avg WER from 1.12 s to 80 ms; AMI is worst hit (11.73 → 18.29)[^nemotron-en-stream-card] |
| Nemotron 3.5 ASR Streaming 0.6B | cache-aware + language-ID prompt | 80/160/320/560/1120 ms | ready-tier FLEURS 8.84 → 10.38; one H100 sustains ~240 streams at 80 ms and ~2,400 at 1.12 s[^nemotron-35-asr-card] |
| Parakeet Realtime EOU 120M | cache-aware, 17 layers | 80–160 ms | 9.30 at 160 ms; inline `<EOU>` P50/P90/P95 160/280/320 ms[^parakeet-eou-card] |
| Audio8 ASR Infinite | native one-token-per-clock streaming, rolling 30 s KV with RoPE re-basing | clock 80/120/160 ms × delay 240–560 ms | evaluated at 480 ms delay; semantic VAD distinguishes pauses from end of turn[^audio8-infinite-card] |
| Confucius4-R2T2 | Longest Stable Prefix training, append-only stable-prefix emission | decode chunks 80 ms–2 s (evaluated at 160 ms) | 200–600 ms average latency claimed; Qwen3-ASR base forced to 160 ms collapses (e.g. AMI 24.79 vs R2T2 11.37)[^confucius4-r2t2-readme] |
| Voxtral Mini 4B Realtime 2602 | native streaming, causal encoder + sliding-window attention | `transcription_delay_ms` multiples of 80 ms (80–1200) + 2400 | FLEURS 12.60 → 6.73 avg from 160 ms to 2400 ms; 8.72 at 480 ms[^voxtral-mini-4b-realtime-card] |
| Qwen3-ASR | unified offline/streaming in one model | not exposed as chunk table | 1.7B 2.69 → 3.33, 0.6B 3.48 → 4.40 (offline → streaming)[^qwen3-asr-readme] |
| Multitalker Parakeet | one cache-aware instance per speaker, fed by streaming diarization | same 80–1120 ms table | benchmarked only at 1.12 s[^multitalker-parakeet-card] |
| VibeVoice-ASR-Streaming 1.5B / 7B | streaming who-said-what | not published | not published[^vibevoice-asr-streaming-7b-card] |
| Whisper (any size) | not natively streaming | wrapper policy (SimulStreaming/LocalAgreement in WhisperLiveKit; VAD-gated realtime/final engines in RealtimeSTT) | wrapper-dependent[^wlk-readme][^realtimestt-readme] |
| [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) | chunked batch (10–15 s) + Apple push streamer with monotonic partials | `flush()` at VAD pauses; `use_internal_vad`; Docker dynamic-batching queue delays | H100 bs=1 RTFx ~304 (S) vs 109 original; H100 bs=64 ~2033 vs 967; Apple M2 Max RTFx 16.7 guidance[^thewhisper-turbo-card] |

## Capability matrix

| Capability | Models documented with it |
| --- | --- |
| Punctuation + capitalization | Parakeet TDT V2/V3, [Orukeet](orukeet.md) (casing/punct-preserving targets), [Parakeet Redux](parakeet-redux.md) (original PnC/casing/numerals), [Parakeet Ultra](parakeet-ultra.md) (original PnC/casing/numerals), Canary-1b-v2, Canary-Qwen-2.5B, Nemotron EN / 3.5, Cohere Transcribe 03-2026 (`punctuation` toggle, on by default). Parakeet CTC/RNNT output lowercase text[^parakeet-tdt-card][^nemotron-en-stream-card][^parakeet-ctc-card][^canary-qwen-2p5b-card][^cohere-03-2026-card][^orukeet-card][^parakeet-redux-card] |
| Word/segment timestamps | Parakeet TDT V2/V3, [Parakeet Redux](parakeet-redux.md) (segment + word via Photon), [Parakeet Ultra](parakeet-ultra.md) (segment + word via Photon), Canary (ASR word + segment), Parakeet RNNT via Transformers, Qwen3-ForcedAligner (11 languages, ≤5 min, 42.9 ms mean shift), VibeVoice-ASR, MOSS, [Whistle](whistle.md) (word start/end/probability from decoder attention). Cohere Transcribe pair: none; Fun-ASR: TODO[^canary-1b-v2-card][^parakeet-rnnt-card][^qwen3-asr-readme][^cohere-arabic-card][^cohere-03-2026-card][^fun-asr-nano-card][^parakeet-redux-card][^whistle-card] |
| Speaker attribution in the ASR model | VibeVoice-ASR (offline, 60 min), VibeVoice-ASR-Streaming, MOSS-Transcribe-Diarize 0.9B (offline, 90 min, `[S01]` labels), Multitalker Parakeet (needs an external diarizer)[^vibevoice-asr-card][^moss-transcribe-diarize-card][^moss-transcribe-cpp-gguf-card][^multitalker-parakeet-card] |
| Hotwords / context biasing | Audio8-ASR-0.1B (decode-time logit boost), Fun-ASR Nano/MLT (`hotwords` + ITN), VibeVoice-ASR family, MOSS-Transcribe-Diarize 0.9B (prompt-suffix hotwords), Confucius4-R2T2 (native `context` prompt), [Whistle](whistle.md) (`keywords=[...]` search bias)[^audio8-asr-01b-card][^fun-asr-nano-card][^vibevoice-asr-card][^moss-transcribe-diarize-card][^confucius4-r2t2-readme][^whistle-card] |
| Timestamp ASR plus audio understanding | [MOSS-Audio family](moss-audio.md): word/sentence timestamps, audio QA, speech captioning, speaker/emotion/event analysis; no streaming or full language list established[^moss-audio-card] |
| Audio understanding / LLM mode in the same weights | Canary-Qwen-2.5B (`disable_adapter` LLM mode); Voxtral Mini 3B and Small 24B (audio Q&A, summarization, voice-triggered function calling)[^canary-qwen-2p5b-card][^voxtral-mini-3b-card][^voxtral-small-24b-card] |
| Hallucination / loop control in the pipeline | Higgs Audio v3 STT (deterministic phrase- and word-level repetition-loop collapse in `transcribe.py`)[^higgs-v3-stt-card] |
| Speculative decoding | Distil-Large-v3.5 as a draft model for Whisper-large-v3: about 2x faster with identical outputs[^distil-large-v3.5-card] |
| End-of-turn signal | Parakeet Realtime EOU (`<EOU>` token), Audio8 Infinite (semantic VAD heads)[^parakeet-eou-card][^audio8-infinite-card] |
| Speech translation | Canary-1b-v2 (X↔En, 25 European languages); [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) (S2ST/S2TT/T2ST/T2TT plus ASR, ~100 languages, 35–37 speech-output targets); [Whisper Large v3](whisper-large-v3.md) and [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) (`task: translate` to English)[^canary-1b-v2-card][^seamless-m4t-v2-card][^whisper-v3-card][^whisper-turbo-card] |
| Language conditioning | Omnilingual LLM-ASR (optional `{lang}_{script}` conditioning); Nemotron 3.5 ASR (language-ID prompt); Qwen3-ASR (language ID 97.9% on 1.7B)[^omnilingual-readme][^nemotron-35-asr-card][^qwen3-asr-readme] |
| Long audio (single-pass or segmented, as noted) | MOSS-Transcribe-Diarize 0.9B 90 min single pass; VibeVoice-ASR 60 min; Parakeet TDT 24 min (V3 up to 3 h local attention); [Parakeet Redux](parakeet-redux.md) TED-LIUM full talks via Photon ≤30 s VAD segmentation; [Parakeet Ultra](parakeet-ultra.md) TED-LIUM 1.94 via Photon ≤30 s VAD segmentation; Audio8 Infinite unbounded (rolling KV); Voxtral Mini 3B / Small 24B 30 min transcription (40 min understanding); Omnilingual LLM-Unlimited v2 unbounded decoding (no finetuning recipes; CTC/LLM suites capped at 40 s in this source)[^vibevoice-asr-card][^parakeet-v3-card][^audio8-infinite-card][^voxtral-mini-3b-card][^omnilingual-readme][^parakeet-redux-card] |
| Noise robustness figures | Parakeet TDT V2/V3, [Parakeet Redux](parakeet-redux.md) (9-condition MUSAN table, avg 9.04 vs 6.72), [Parakeet Ultra](parakeet-ultra.md) (9-condition MUSAN table, avg 5.82 vs 6.72), and Canary MUSAN SNR tables; Canary hallucination rate 134.7 chars/min[^parakeet-v3-card][^canary-1b-v2-card][^parakeet-redux-card] |

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
| [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) Apple CoreML / NVIDIA Docker | Apple SDK (ANE/GPU/CPU auto) / CUDA Docker | Apple ~96 MB process mem (M2 Max guidance); NVIDIA L40s/4090/5090/H100, CUDA 12.8+ | Apple RTFx 16.7 + 233 tok/s guidance; NVIDIA H100 bs=64 ~2033 RTFx[^thewhisper-turbo-card] |
| [Distil-Large-v3.5](distil-large-v3.5.md) GGML / CT2 | whisper.cpp / Faster-Whisper | 756M params | GGML `distil-large-v3.5-ggml` and CTranslate2 `distil-large-v3.5-ct2` weights; no edge speed figures[^distil-large-v3.5-card] |
| [Phonon-2](phonon-2.md) | MLX (Apple silicon) / Linux-Arm-x86-64 + Windows CPU / CUDA Docker | 164 MB download | 1 h audio in ~20 s on M5 Air (174x); 143x on 8 Zen 5 cores; 6680x on H100 batch-128; `--json` word timings[^phonon-2-card] |
| [Parakeet Redux](parakeet-redux.md) | Photon (x86 AVX-512-VNNI / ARM NEON / Apple Metal; `pip install moondream`) | 178 MB weights | 113× on 8 x86 cores (EPYC 9575F); 38× CPU / 43× GPU on M2 Air; segment + word timestamps; ≤30 s VAD segmentation, no external VAD[^parakeet-redux-card] |
| [Orukeet](orukeet.md) sherpa-onnx INT8 + native/Handy GGUF + Core ML preview | sherpa-onnx / native Python / transcribe.cpp-Handy / Core ML (FluidAudio, TapTalk) | NeMo 2.51 GB; Q8 714 MB; transcribe.cpp Q8 740 MB; F16 1.30 GB; ONNX archive 487 MB (672 MB extracted); Core ML ~467 MB each | 640 application-check transcripts match prior export; 160-clip median 390 ms vs 432 ms prior and 428 ms stock Parakeet on M5 Max; greedy Core ML −9.5% batch latency with matched transcripts on 128 FLEURS clips[^orukeet-card] |
| [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) transcribe.cpp GGUF / mlx-audio | transcribe.cpp (Metal, Vulkan, CUDA, ROCm, CPU; no Python at runtime) / mlx-audio ≥0.5.1 (Apple silicon) | Q8_0 GGUF via handy-computer repo | usage commands only; no edge speed figures in card[^granite-turboctc-card] |
| [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) | audio.cpp | — | catalog ASR rows: Qwen3-ASR 0.6B/1.7B + ForcedAligner, Parakeet-TDT-0.6B-v3, Nemotron-3.5-ASR, Canary-180M-Flash, Cohere-Transcribe, Fun-ASR-Nano, VibeVoice-ASR, MOSS-Transcribe-Diarize, Moonshine-Streaming, Granite-Speech-5.0-470M, GigaAM, CrisperWhisper, Citrinet, Kroko, Hviske, Niagara, MMS-Forced-Aligner[^audio-cpp-gguf-readme] |
| [Whistle](whistle.md) (`whistle.cact`) | shared Needle C++ engine (CPU, no GPU; `.cact` container, `--audio-depth` ladder) + Python `cactus-needle` / C API / platform binaries | 16.9 MB single file | M4 Pro speed figures image-only, none recorded; `--audio-word-timestamps` CLI flag[^whistle-card] |

[NeMo-Speech.cpp](nemo-speech-cpp.md) documents GGUF inference for Parakeet CTC 1.1B, Parakeet TDT V3, Nemotron 3.5, and Nemotron EN. Its Nemotron EN Q8_0 benchmark uses 160 ms input chunks: RTX 4090 2.3 ms compute/chunk (67× realtime), unnamed CPU 27 ms/chunk (6×). These are **Reported** runtime results, not endpoint-to-final latency or measurements of Nemotron 3.5; `BENCHMARK.md` and CPU/thread details are unavailable.[^nemo-speech-readme]

**Synthesis:** GGUF is a container, not an interchangeability guarantee. Orukeet explicitly distinguishes native NeMo-Speech.cpp layouts from its Handy/transcribe.cpp export; choose a runtime-matched artifact before comparing quantization or speed.[^orukeet-card]

## Licensing

| License | Models | Commercial-use reading |
| --- | --- | --- |
| Apache-2.0 | Qwen3-ASR, ARK-ASR-3B / 0.6B, Hojo-ASR-V1, Higgs Audio v3 STT, Granite Speech 5.0 470M TurboCTC, Audio8 ASR Infinite, Voxtral Mini 3B / Small 24B / Mini 4B Realtime, Whisper Large v3 (card frontmatter), Fun-ASR Nano/MLT, Cohere Transcribe 03-2026, Cohere Transcribe Arabic, MOSS-Transcribe-Diarize, SenseVoiceSmall, Omnilingual ASR, [Whistle](whistle.md) | permissive |
| MIT | GLM-ASR-Nano, VibeVoice-ASR family, Whisper Large v3 Turbo (card frontmatter), Distil-Large-v3.5, IndicConformer-600M-Multilingual | permissive |
| CC-BY-4.0 | Parakeet CTC/RNNT/TDT, [Parakeet Redux](parakeet-redux.md), [Parakeet Ultra](parakeet-ultra.md), Phonon-2 (CLI/code Apache-2.0), Canary-1b-v2, Canary-Qwen-2.5B, TheWhisper-Large-V3-Turbo | permissive with attribution |
| CC-BY-SA-4.0 | [Orukeet](orukeet.md) weights and fitted kernels (code MIT; metric records CC-BY-4.0) | permissive with attribution and share-alike |
| NVIDIA Open Model License | Nemotron Speech Streaming EN, Parakeet Realtime EOU, Multitalker Parakeet | vendor license, check terms |
| OpenMDW-1.1 | Nemotron 3.5 ASR | card states ready for commercial use |
| CC-BY-NC-4.0 | Audio8-ASR-0.1B, [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) | **non-commercial** |
| NVIDIA OneWay Noncommercial | Audio Flamingo 3 / Next | **non-commercial** |
| NetEase Model Use License Agreement | Confucius4-R2T2 (weights; code is Apache-2.0) | vendor license, check terms[^confucius4-r2t2-readme] |

The license column follows each concept's compiled card frontmatter (**Reported**). The commercial reading is **Synthesis**, not legal advice.[^audio8-asr-01b-card][^audio-flamingo-gguf-card][^nemotron-35-asr-card][^hojo-asr-v1-doc][^distil-large-v3.5-card]

## Serving runtimes

| Runtime | ASR engines | Interface |
| --- | --- | --- |
| [Faster-Whisper](faster-whisper.md) | Whisper / distil-Whisper (CTranslate2, incl. `distil-large-v3.5-ct2`), Silero VAD filter, batched pipeline | Python library[^faster-whisper-readme][^distil-large-v3.5-card] |
| [WhisperLiveKit](whisperlivekit.md) | faster-whisper, mlx-whisper, Whisper, FunASR, Voxtral, Qwen3 (vLLM / streaming), Canary, OpenAI API | WebSocket + OpenAI/Deepgram-compatible; SimulStreaming or LocalAgreement policy[^wlk-readme] |
| [RealtimeSTT](realtimestt.md) | selectable realtime + final engines behind VAD gating | Python library + FastAPI server[^realtimestt-readme] |
| [Speaches](speaches.md) | faster-whisper | OpenAI-compatible server, SSE streaming[^speaches-readme] |
| [Parakeet ASR Server](parakeet-asr-server.md) | Parakeet TDT 0.6B (ONNX) | Whisper-compatible REST/SSE[^parakeet-readme] |
| [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) Docker + Apple SDK | TheWhisper S/M/L/XL (Triton ensemble) + CoreML engines | OpenAI-compatible `POST /v1/audio/transcriptions` (Docker); Swift `infer`/`open_streamer` + Flutter `infer` (Apple)[^thewhisper-turbo-card] |
| [Fast GPU ASR](fast-gpu-asr.md) | Zipformer Transducer/CTC, Parakeet TDT/CTC (TensorRT, NVIDIA GPU only) | Python library; B300 FP16 beam-6 batch-256 reports 25,108.6 RTFx at 5.261% mean WER (Zipformer CR-CTC Transducer) and 19,398.7 RTFx at 4.810% (Parakeet V3 TDT) over 157.8 h of English audio[^fast-gpu-asr-readme] |
| vLLM / [SGLang-Omni](sglang-omni.md) / [vLLM-Omni](vllm-omni.md) | Qwen3-ASR (`qwen-asr-serve`), ARK-ASR, Cohere Transcribe 03-2026 + Arabic (`/v1/audio/transcriptions`), MOSS-Transcribe-Diarize 0.9B (SGLang Omni `verbose_json` segments, vLLM `--trust-remote-code`), Voxtral Mini 4B Realtime (`/v1/realtime`), Voxtral Mini 3B / Small 24B (`audio.transcriptions` + chat completions with tools; Small needs TP-2) | OpenAI-compatible[^qwen3-asr-readme][^ark-asr-3b-card][^cohere-03-2026-card][^cohere-arabic-card][^moss-transcribe-diarize-card][^voxtral-mini-4b-realtime-card][^voxtral-mini-3b-card][^voxtral-small-24b-card] |
| [Confucius4-R2T2](confucius4-r2t2.md) `ws_server.py` | Confucius4-R2T2 (vLLM + FireRedVAD Stream-VAD) | WebSocket `/asr_stream_api_v1` with incremental `text`; 16 kHz int16 frames[^confucius4-r2t2-readme] |
| [audio.cpp Framework](audio-cpp-framework.md) | 17+ ASR GGUF families | CLI / server / WebUI[^audio-cpp-gguf-readme] |
| [NeMo-Speech.cpp](nemo-speech-cpp.md) | Nemotron EN / 3.5, Parakeet TDT V3 / CTC 1.1B; standalone or ASR-combined Sortformer v2 / Nemotron 3 diarization | Native ggml CLI, HTTP/OpenAI-compatible subsets, realtime WebSocket, separate Riva gRPC binary, C SDK; Apache-2.0 runtime code (weights retain their own terms)[^nemo-speech-readme] |
| [transcribe.cpp](transcribe-cpp.md) | 20 STT families in the support tables (header says 16), plus streaming diarizer (Parakeet, Canary, Nemotron, Qwen3-ASR, Voxtral, Whisper, Granite TurboCTC, MOSS-Transcribe-Diarize, Moonshine, GigaAM-v3, MedASR) via GGUF on ggml | CLI (`transcribe-cli`) plus Python/TypeScript/Rust/Swift bindings; Metal/Vulkan/CUDA/ROCm/CPU[^transcribe-cpp-readme] |

## Selection guide

This section is agent **Synthesis** from the evidence above. Validate any choice on in-domain audio, because no figure here has been reproduced.

- **English realtime voice agent:** [Nemotron Speech Streaming EN 0.6B](nemotron-speech-streaming-en-0.6b.md) at 160–560 ms. Use [Parakeet Realtime EOU 120M](parakeet-realtime-eou-120m-v1.md) when budget is tight or you want ASR-native endpointing.
- **English batch/offline, best small model:** [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md), with very high RTFx and published noise and telephony rows. Move to [ARK-ASR-3B](ark-asr-3b.md) when meeting/AMI accuracy matters more than speed; use [Canary-Qwen-2.5B](canary-qwen-2.5b.md) (5.63 mean, 2.5B, English-only) when the budget allows a larger SALM and transcript summarization/Q&A in the same weights matters. Use [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) (5.42 mean, 14 languages) when multilingual coverage matters more than timestamps.[^parakeet-tdt-card][^ark-asr-3b-card][^canary-qwen-2p5b-card][^cohere-03-2026-card]
- **English, staying in the Whisper ecosystem:** [Distil-Large-v3.5](distil-large-v3.5.md) as a faster short-form drop-in for large-v3-turbo with whisper.cpp and CT2 weights. For long-form OOD audio, keep turbo or run v3.5 as a speculative draft for exact large-v3 output.[^distil-large-v3.5-card]
- **Voice commands that should trigger tools directly:** [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md) (~9.5 GB) or [Voxtral Small 24B 2507](voxtral-small-24b-2507.md) (~55 GB) for transcription, audio Q&A, and function calling in one model. Benchmark WER first, because no numeric figure is compiled.[^voxtral-mini-3b-card][^voxtral-small-24b-card]
- **Multilingual realtime:** [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md) for its 19 transcription-ready locales. Use [Qwen3-ASR](qwen3-asr-family.md) for broader and Asian coverage with a unified streaming mode. Use [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) for 13-language transcription with a tunable 80–2400 ms delay knob and vLLM realtime serving.
- **European multilingual offline or translation:** [Parakeet TDT V3](parakeet-tdt-0.6b-v3.md) for speed, [Parakeet Ultra](parakeet-ultra.md) as the accuracy-improved full-precision GPU drop-in from the same lineage (English 5.80, FLEURS 25-language average 9.55, TED-LIUM 1.94), [Orukeet](orukeet.md) as the accuracy-improved Gabor-frozen drop-in from the same r3 checkpoint (FLEURS pooled 9.85 vs 11.01), [Parakeet Redux](parakeet-redux.md) as the 178 MB ternary CPU/edge drop-in (113× on eight x86 cores, FLEURS 25-language average 10.56), [Canary-1b-v2](canary-1b-v2.md) when you also need X↔En translation. These cross-card numbers are not a matched ranking.[^parakeet-redux-card][^parakeet-ultra-card][^orukeet-card]
- **Chinese, dialects, Cantonese:** Qwen3-ASR-1.7B, [Fun-ASR-Nano](fun-asr-nano-2512.md) (dialect, lyrics, hip-hop), or ARK-ASR-3B. [Hojo-ASR-V1](hojo-asr-v1.md) targets Cantonese, Sichuan dialect, and zh-en code-switching but publishes no Chinese figures. Use [Audio8 ASR Infinite](audio8-asr-infinite.md) for 24/7 zh/en streaming. For low-latency zh/en streaming with stable no-revision output, use [Confucius4-R2T2](confucius4-r2t2.md) (160 ms chunks, vendor-reported 200–600 ms latency).[^confucius4-r2t2-readme]
- **Vietnamese:** start with Qwen3-ASR or faster-whisper `large-v3-turbo` with hallucination filters, as recommended in the [Vietnamese stack](vietnamese-realtime-voice-agent-stack.md). Use Nemotron 3.5 as a streaming alternative and benchmark on noisy in-house audio.
- **Arabic:** [Cohere Transcribe Arabic](cohere-transcribe-arabic-07-2026.md) behind a VAD/noise gate.
- **Indic (22 official Indian languages):** [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) with dual CTC/RNNT decoding under MIT terms; benchmark WER first because the card publishes no numeric results.[^indic-conformer-card]
- **Massive multilingual / low-resource:** [Omnilingual ASR](omnilingual-asr.md) for 1600+ languages and few-example extension; use the Unlimited v2 variant for long audio, and validate per-language CER in the linked table before relying on the 78%-below-10 headline.[^omnilingual-readme]
- **Meetings with speakers:** [VibeVoice-ASR](vibevoice-asr.md) (offline, 60 min) or [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) (offline, 90 min; [GGUF CPU port](moss-transcribe-cpp-gguf.md)). Alternatively, pair streaming ASR with a diarizer through [Multitalker Parakeet](multitalker-parakeet-streaming-0.6b-v1.md).
- **English compact turn-final:** [Phonon-2](phonon-2.md) (164 MB, MLX/CPU/CUDA, vendor 5.21 WER) is an additional offline candidate; 174× M5 Air throughput does not establish incremental partial latency.[^phonon-2-card]
- **CPU/edge:** Fun-ASR-Nano GGUF or SenseVoiceSmall GGUF for CJK, Parakeet via ONNX or NeMo-Speech.cpp for English/European, [Parakeet Redux](parakeet-redux.md) via Photon for ternary 178 MB multilingual CPU/GPU with built-in VAD segmentation, faster-whisper int8 as the general fallback.[^parakeet-redux-card] For English greedy-CTC edge packaging with no Python at runtime, use [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) via transcribe.cpp (Q8_0 GGUF) or mlx-audio on Apple silicon.[^granite-turboctc-card] For Apple on-device (iOS/macOS, no server), use [TheWhisper-Large-V3-Turbo](thewhisper-large-v3-turbo.md) CoreML via the TheStage Apple SDK (10 s window, monotonic partials, `flush()` at VAD pauses).[^thewhisper-turbo-card] For tiny multilingual on-device STT sharing one CPU runtime with its LLM, use [Whistle](whistle.md) (16.9 MB single `.cact`, 7 languages, word timestamps plus keyword biasing; WER and speed figures image-only).[^whistle-card]
- **Commercial license constraint:** avoid Audio8-ASR-0.1B and Audio Flamingo, review NVIDIA Open Model License terms, and review the NetEase Model Use License Agreement before shipping Confucius4-R2T2 weights.

## Vietnamese primary-source follow-up

[Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) adds native-vs-buffered-vs-turn-final filtering and conditional two-pass design. Qwen92ms TTFT belongs to concurrency1 with ~2min complete inputs; concurrency128 TTFT is3210ms while throughput is2000 audio-seconds/second. Neither figure establishes Vietnamese mic latency. ChunkFormer ONNX streaming uses a distinct small checkpoint whose card returned401; large RNNT113M has CC-BY-4.0 while CTC110M has NC. ZipFormer30M upstream license is NC-ND, not the AI-report Apache label, and its CPU throughput does not establish native streaming (**Reported/Synthesis**). Capture ledger lists pending weights/code/images/papers; no model executed.[^vi-primary-research]

## Community-reported field notes

These are unverified anecdotes from community threads, kept apart from vendor evidence (**Reported**):

- For English short utterances, Parakeet v2 is recommended over Whisper at about 5x speed. V3 is described as slower because of its multilingual breadth.[^reddit-stt-llm-tts-thread]
- Two commenters rank Qwen3-ASR (including 0.6B) above Parakeet, Whisper, and FunASR because it hallucinates least and rejects non-speech better. Whisper large-v3-turbo is described as almost as accurate as large-v3 but much faster. Moonshine is named for the lowest-latency English-only use.[^reddit-open-stt]
- Qwen3-ASR is called heavier on VRAM, and one commenter says it streams worse than Parakeet. Commenters advise pairing it with a VAD frontend to suppress false triggers. One commenter picks Nemotron 3.5 streaming as their best ASR.[^reddit-asr-tts-thread]
- For noisy calls, Parakeet is reported as 4–5x faster than Whisper for English. Whisper-large-v3 with preprocessing and diarization is defended as still viable, and Canary and Granite are named as more robust alternatives without measurements.[^reddit-noisy-stt]
- Agent-grade STT evaluation should measure first stable text, partial stability, endpointing, barge-in, and entity accuracy, not WER alone.[^reddit-usable-stt]

## Adjacent concepts

- Deployment-tool comparison: [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md) separates native engines, GPU optimizers, API servers, streaming STT policies and voice-agent orchestration; read it before equating an SSE server with native streaming (**Synthesis**).[^parakeet-readme][^wlk-readme]

- Realtime selection synthesis: [Phân nhóm ASR/STT và shortlist realtime](realtime-asr-selection.md) groups the catalog by architecture and streaming semantics, with conditional size tiers, language filters, and an unvalidated deployment shortlist (**Synthesis**).

- Synthesis side of the voice loop: [TTS Model Survey](tts-model-survey.md) compares every compiled TTS model.
- Apple diarization-only packaging: [Speaker Diarization Core ML](speaker-diarization-coreml.md) uses FluidAudio on iOS 17/macOS 14+, returns speaker segments without text, and has no numeric DER/latency evidence in the card. Community-1 licensing/provenance excludes legacy online artifacts; it is not a demonstrated drop-in frontend for Multitalker Parakeet.[^speaker-diar-coreml-card]
- Diarization only: [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md), [Streaming Sortformer v2](diar-streaming-sortformer-4spk-v2.md) / [v2.1](diar-streaming-sortformer-4spk-v2-1.md), [Nemotron 3 Diarization](nemotron-3-diarization.md) and its [GGUF](nemotron-3-diarization-gguf.md). Streaming Sortformer v2 is the frontend in Multitalker Parakeet's cpWER table.[^multitalker-parakeet-card]
- Speech translation: [Index-Echo S2TT GGUF](index-echo-s2tt-gguf.md) produces timestamped Chinese source transcripts plus English, Spanish, or Japanese translations.[^index-echo-s2tt-gguf] Mass-multilingual translation plus ASR is [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) (S2ST/S2TT/T2ST/T2TT, ~100 languages, Transformers inference).[^seamless-m4t-v2-card]
- Speech LLM / speech-to-speech without a separate ASR stage: [Ultravox](ultravox.md), [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md), [PersonaPlex 7B v1](personaplex-7b-v1.md), [Step-Audio-R1.1](step-audio-r1-1.md).
- ASR hygiene: [Whisper Hallucination Mitigation for Vietnamese](whisper-hallucination-mitigation.md), [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), [Turn Detection Models](turn-detection-models.md), [Silero VAD](silero-vad.md).
- Community syntheses: [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md), [Noisy On-Premise STT Selection](community-noisy-call-stt.md), [Open STT and Realtime Diarization Selection](community-open-stt-diarization.md), [Local ASR/TTS Selection](community-asr-tts-selection.md), [STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md).

## Contradictions

- **Nemotron Speech Streaming EN 0.6B English average:** its own card reports 6.93 at 1.12 s (AMI 11.73, GigaSpeech 9.66, TEDLIUM 3.50).[^nemotron-en-stream-card] The Multitalker Parakeet card lists the same base model at 7.16 (AMI 11.58, GigaSpeech 11.45, TEDLIUM 4.5) and does not state that table's chunk size or checkpoint revision.[^multitalker-parakeet-card] Neither value is chosen here.
- **Audio8 Infinite vs Nemotron 3.5:** Audio8's comparison table runs itself at 480 ms delay and Nemotron 3.5 at 560 ms on AISHELL and LibriSpeech. The settings differ, and the table covers Nemotron's broad-coverage Mandarin tier, so the gap does not reflect Nemotron's transcription-ready languages (**Reported**; interpretation is **Synthesis**).[^audio8-infinite-card][^nemotron-35-asr-card]
- **ARK-ASR-0.6B English average:** its own card reports 6.55 across 7 sets under the `open-audio-opd` harness.[^ark-asr-06b-card] The sibling 3B card reports 5.97 for the same checkpoint and set names under the Open ASR Leaderboard protocol, with per-set gaps largest on AMI and Earnings22. The Chinese CER components match.[^ark-asr-3b-card] Neither value is chosen here; the ranking above uses the Leaderboard-protocol row only for comparability with other leaderboard rows.
- **Parakeet Redux cross-card English average:** the Phonon-2 card lists Redux at 5.69 and its teacher at 4.96; Redux's own card reports 6.55 and its teacher at 6.26. Both name seven English sets, but the evaluation pipelines and normalizers have not been reconciled here; neither cross-card value overrides the other's provenance (**Reported**; comparison is **Synthesis**).[^phonon-2-card][^parakeet-redux-card]
- **Qwen3-ASR streaming quality:** the vendor reports a small offline-to-streaming gap (2.69 → 3.33), while one community commenter says it streams worse than Parakeet. No shared measurement resolves this.[^qwen3-asr-readme][^reddit-asr-tts-thread]

## Coverage and limits

- Index-diff reconciliation: the new ASR checkpoint/family entries already have catalog rows; NeMo-Speech.cpp and transcribe.cpp are runtimes, and Speaker Diarization Core ML is adjacent rather than an additional recognizer (**Observed**). This update inspected their compiled pages and the NeMo/Core ML raw captures; no remote docs, weights, or missing benchmark figures were fetched. Runtime support/verification claims remain **Reported**, not wiki reproduction.[^nemo-speech-readme][^transcribe-cpp-readme][^speaker-diar-coreml-card]
- Orukeet's final adaptation and checkpoint selection use LibriSpeech test-other, so its gain on that split is selection-adjacent. Its pooled FLEURS WER is not automatically comparable to Moondream's 25-language averages (**Synthesis**).[^orukeet-card][^parakeet-redux-card][^parakeet-ultra-card]
- This survey reads only the compiled concepts and their declared raw sources. No model was downloaded, run, or benchmarked, and no figure was reproduced (**Synthesis**).
- No numeric benchmark exists in the wiki for VibeVoice-ASR, VibeVoice-ASR-Streaming, GLM-ASR-Nano (figure-only), Fun-ASR-MLT-Nano, Voxtral Mini 3B / Small 24B (figure-only), or the current Higgs Audio v3 STT checkpoint (earlier figures superseded), or [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) (Open ASR + FFASR plots image-only), or [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) (no WER/CER table in card), or [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) (metrics in external zips, none printed in card), or [Whistle](whistle.md) (WER and M4 Pro speed figures image-only in `whistle-benchmarks.svg`, not compiled). Their rank is unknown, not low.[^vibevoice-asr-card][^glm-asr-nano-card][^fun-asr-mlt-nano-card][^voxtral-mini-3b-card][^voxtral-small-24b-card][^higgs-v3-stt-card][^granite-turboctc-card][^seamless-m4t-v2-card][^whistle-card]
- Hojo-ASR-V1's card gives no model URL, release date, evaluation protocol, or Chinese/dialect numbers, so its English mean and dialect positioning are unaudited (**Synthesis**).[^hojo-asr-v1-doc]
- Omnilingual ASR's headline figure (7B LLM-ASR, CER below 10 for 78% of 1600+ languages) is recorded, but its per-language CER plus training-hours CSV and result figure were unavailable in `raw/` and are not compiled; rank comparisons against Open ASR WER averages should not include it.[^omnilingual-readme]
- No concept page exists for other upstream OpenAI Whisper size cards (tiny through large-v2), whisper.cpp, Moonshine, Canary-180M-Flash, GigaAM, other Zipformer checkpoints, Kyutai, or proprietary APIs. Vietnamese PhoWhisper, ChunkFormer and ZipFormer30M are now captured separately.[^vi-primary-research] Upstream [Whisper Large v3 Turbo](whisper-large-v3-turbo.md) is now compiled from its Hugging Face card (no numeric WER/RTFx in that source), joined by [Whisper Large v3](whisper-large-v3.md) from its Hugging Face card (no numeric table, 10–20% over large-v2 claim). Their remaining appearance here comes from catalogs, comparison columns, or anecdotes. Compile their primary sources before relying on them.[^audio-cpp-gguf-readme][^claude-pipeline-report][^whisper-turbo-card][^whisper-v3-card] The Voxtral line (Mini 3B, Small 24B, Mini 4B Realtime) and Distil-Large-v3.5 now have their own concepts, which are linked from the catalog above. Distil-Whisper predecessors such as `distil-large-v3` do not. [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) now has its own concept; its Open ASR and FFASR figures stay image-only with no numeric WER compiled.[^voxtral-mini-3b-card][^voxtral-small-24b-card][^voxtral-mini-4b-realtime-card][^distil-large-v3.5-card][^granite-turboctc-card]
- Confucius4-R2T2's English/Chinese tables and latency Pareto figures are vendor self-reports at 160 ms chunks with undisclosed hardware and protocol; the card names anonymous `Commercial A/B` baselines, marks some rivals pseudo-streaming (revising partials), and its latency SVGs were not parsed for numbers here — only the 200–600 ms claim and the chunk range are compiled (**Synthesis**).[^confucius4-r2t2-readme]
- Benchmarks and releases are time-sensitive; `stale_after: 2027-10-06` follows the `stt` domain rule.

[^parakeet-ctc-card]: [Parakeet CTC 0.6B](../raw/parakeet-ctc-0.6b.md) — locators: frontmatter `license`, `model-index`; body `Performance` WER table (9 sets incl. Common Voice; this page averages the 8 Open ASR sets excluding Common Voice); `Model Architecture`; `Training` (64K hours).
[^parakeet-ctc-11-card]: [Parakeet CTC 1.1B](../raw/parakeet-ctc-1.1b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table; `How to Use` NeMo-Speech.cpp GGUF path.
[^parakeet-rnnt-card]: [Parakeet RNNT 0.6B](../raw/parakeet-rnnt-0.6b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table; Transformers RNNT usage with timestamps.
[^parakeet-rnnt-11-card]: [Parakeet RNNT 1.1B](../raw/parakeet-rnnt-1.1b.md) — locators: frontmatter `license`, `model-index`; `Performance` WER table.
[^parakeet-tdt-card]: [Parakeet TDT 0.6B V2](../raw/parakeet-tdt-0.6b-v2.md) — locators: `Model Architecture` (24-minute single pass, RTFx 3380 at batch 128); `Training` (~120K-hour Granary); `Performance` base table (avg 6.05), MUSAN SNR table, telephony table; `License` CC-BY-4.0.
[^parakeet-v3-card]: [Parakeet TDT 0.6B V3](../raw/parakeet-tdt-0.6b-v3.md) — locators: intro (25 languages, auto LID); `Model Architecture` (24 min full attention / 3 h local attention); `Performance` multilingual averages (FLEURS 11.97, MLS 7.83, CoVoST 11.98), English Open ASR row (avg 6.34), MUSAN table; NeMo-Speech.cpp usage; frontmatter `license`.
[^canary-1b-v2-card]: [Canary-1b-v2 model card](../raw/canary-1b-v2.md) — locators: `Key Features`; `Model Architecture` (978M, FastConformer + Transformer decoder); `Benchmark Results` (ASR aggregate table, HF Leaderboard mean 7.15 / RTFx 749, AST tables, MUSAN SNR table, hallucination 134.7 chars/min); `How to Use` timestamps; `License/Terms`.
[^canary-qwen-2p5b-card]: [Canary-Qwen-2.5B model card](../raw/canary-qwen-2.5b.md) — locators: header badges (2.5B, SALM, 418 RTFx); `Model Architecture` (SALM, FastConformer + Qwen3-1.7B, projection + LoRA, `Transcribe the following` prompt); `Limitations` (40 s / 1024 tokens, English-only); `Training` (90k steps, 32×A100, 234K hrs, AMI 15% oversample); `Performance` (Leaderboard mean 5.63 table, MUSAN 138.1 chars/min, SNR table); `Model Fairness Evaluation` (CasualConversations gender/age tables); `How to Use` (SALM ASR vs `disable_adapter` LLM fences, `salm_generate.py` manifest); `Software Integration` (NeMo 2.5.0+, Ampere–Volta, Linux/L4T/Windows).
[^nemotron-en-stream-card]: [Nemotron Speech Streaming EN 0.6B card](../raw/nemotron-speech-streaming-en-0.6b.md) — locators: `Model Architecture` (600M, cache-aware FastConformer-RNNT); `att_context_size` latency table; WER tables at 1.12/0.56/0.16/0.08 s (line ~620 for 6.93); `License`.
[^nemotron-35-asr-card]: [Nemotron 3.5 ASR model card](../raw/nemotron-3.5-asr-streaming-0.6b.md) — locators: `License` (OpenMDW-1.1, commercial use); supported-language tier lists; automatic language detection section; `att_context_size` table; H100 throughput comparison; FLEURS LangID/auto tables (ready-tier averages, vi-VN row); NeMo-Speech.cpp `q8_0.gguf` usage.
[^parakeet-eou-card]: [Parakeet Realtime EOU 120M v1 card](../raw/parakeet_realtime_eou_120m-v1.md) — locators: frontmatter `license`; `Model Architecture` (120M, 17 layers, `[70, 1]`); EOU latency percentiles; 160 ms Open ASR WER table (avg 9.30).
[^multitalker-parakeet-card]: [Multitalker Parakeet Streaming 0.6B v1 card](../raw/multitalker-parakeet-streaming-0.6b-v1.md) — locators: `Model Architecture` (speaker-kernel injection, multi-instance); latency mapping; multitalker cpWER table with Streaming Sortformer v2 frontend; `Evaluation: Single-speaker Mode ASR Performance` table (base 7.16, single-speaker 7.44, ~line 437); license.
[^qwen3-asr-readme]: [Qwen3-ASR README and model card](../raw/Qwen3-ASR-0.6B.md) — locators: frontmatter `license`; model/language table (30 languages, 22 dialects, ForcedAligner 11 languages); `Key capabilities`; `qwen-asr-serve` / vLLM serving fences; evaluation tables (public-set WER, internal sets incl. dialect dialog, language-ID accuracy, streaming vs offline, forced-alignment shift).
[^qwen3-asr-hf-card]: [Qwen3-ASR-0.6B-hf Transformers-native model card](../raw/Qwen3-ASR-0.6B-hf.md) — locators: `Usage` (Transformers `apply_transcription_request`, `transformers>=5.13.0`); `Speed & Memory Improvements` (A100 `torch.compile` 2.5x aligner / 2.4x ASR at batch size 4); `Evaluation` (HF Open ASR Leaderboard table dated 26 June 2026: 1.7B-hf mean 5.59, 0.6B-hf mean 6.31 with per-set cells).
[^ark-asr-3b-card]: [ARK-ASR-3B model card](../raw/ARK-ASR-3B.md) — locators: frontmatter `license`; `Supported Languages`; `Model Overview`; `Performance > English WER` (3B and 0.6B rows); `Performance > Chinese CER`; RTFx statement; `vLLM Online Serving`.
[^ark-asr-06b-card]: [ARK-ASR-0.6B model card](../raw/ARK-ASR-0.6B.md) — locators: frontmatter (`license`, `language`); `Abstract` (`Ark-Base+TD+OPD`, TD + OPD recipe, 19 languages); `Model Overview` (Whisper-style encoder + MLP + Qwen2 decoder, 30 s / 16 kHz); `Performance > English WER` (avg 6.55 vs Qwen3-ASR 0.6B 6.93 / 1.7B 6.25); `Performance > Chinese CER` (avg 4.30); `Inference` (Transformers fence, batch JSONL command).
[^hojo-asr-v1-doc]: [Hojo-ASR-V1 model card](../raw/Hojo-ASR-V1.md) — locators: frontmatter (`license: apache-2.0`); `Overview > Introduction` (Encoder-Adapter-Qwen3 LLM, multi-frame acoustic fusion, RL, Mandarin/English/Cantonese/Sichuan, code-switching focus); `Quickstart` (`hojo-asr` package, `run_infer`); `Evaluation` (8-cell English WER table, no average or protocol); `Roadmap`; `Licence`.
[^higgs-v3-stt-card]: [Higgs Audio v3 STT model card](../raw/higgs-audio-v3-stt.md) — locators: frontmatter (`license: apache-2.0`, `language: [en]`); `Architecture` (Whisper-Large-v3 encoder, Qwen3-1.7B decoder, 2.68B, 16 kHz, thinking mode); `Update (June 2026)` (retrain splits, repetition-loop collapse in `transcribe.py`, superseded figures, Open ASR Leaderboard re-evaluation pointer); `Usage` (30 s chunk collator, `enable_thinking=True`, lowercase prompt).
[^voxtral-mini-3b-card]: [Voxtral Mini 3B 2507 model card](../raw/Voxtral-Mini-3B-2507.md) — locators: frontmatter (8-code `language`, `license: apache-2.0`); `Key Features` (auto-LID transcription, 32k context with 30/40-minute limits, Q&A/summarization, voice function calling); `Benchmark Results` (image-only figures); `vLLM > Serve` (~9.5 GB GPU RAM, Small-24B server recommendation); `Transcription` (`TranscriptionRequest` fence).
[^distil-large-v3.5-card]: [Distil-Whisper Distil-Large-v3.5 model card](../raw/distil-large-v3.5.md) — locators: header (756M, 1.46x turbo RTFx, 7.08 short-form / 11.39 long-form OOD WER); `Performance` (short-form 7-set table: overall 7.10 vs large-v3 7.14 / turbo 7.25; long-form WER and RTFx tables); `Transformers Usage` (sequential, chunked `chunk_length_s=25`, speculative-decoding fences); `Library Integrations` (whisper.cpp GGML, Faster-Whisper `distil-large-v3.5-ct2`, OpenAI format); `License` (MIT).
[^audio8-asr-01b-card]: [Audio8-ASR-0.1B model card](../raw/Audio8-ASR-0.1B.md) — locators: frontmatter `license` (cc-by-nc-4.0), `language`; `Model Overview` (103,502,336 / 323,990,528 params); `Evaluation Results` table (7-split mean 7.03, RTFx 741.15, WenetSpeech CER); `Related Releases` (ONNX ~1.1 GB, iOS ~200 MB); `Hotword Boosting`.
[^voxtral-mini-4b-realtime-card]: [Voxtral Mini 4B Realtime 2602 model card](../raw/Voxtral-Mini-4B-Realtime-2602.md) — locators: frontmatter (13-code `language` list, Apache-2.0, Ministral-3-3B-Base-2512 base, `pipeline_tag`); header (<500 ms claim, 13-language and 4B on-device positioning, >12.5 tok/s, BF16); `Key Features` (3.4B LM + 970M causal encoder, sliding-window infinite streaming, 80 ms–2.4 s delay range, use-case list); `Recommended Settings` (temperature 0.0, 80 ms-per-token sizing with 45000/131072 figures, websockets, 480 ms sweet spot, `tekken.json` multiples rule); `Benchmark Results` (FLEURS 6-row × 13-language table, long-form and short-form tables vs Transcribe 2.0); `Usage` (vLLM realtime endpoint, Transformers >= 5.2.0 fence, untested ExecuTorch and community ports).
[^voxtral-small-24b-card]: [Voxtral Small 24B 2507 model card](../raw/Voxtral-Small-24B-2507.md) — locators: frontmatter (8-code `language` list, Apache-2.0, Mistral-Small-24B-Base-2501 base, `pipeline_tag` audio-text-to-text); `Key Features` (transcription with auto LID, 32k context with 30/40-minute limits, Q&A/summarization, 8-language list, experimental voice function calling, Small-3 text retention); `Benchmark Results` (FLEURS/Common Voice/MLSI WER figure and text figure, both image-only); `Usage` (vLLM/Transformers frameworks, `temperature`/`top_p` defaults, no-system-prompts note); `vLLM > Serve` (TP-2 serve command with mistral tool-call parser, ~55 GB VRAM note).
[^audio8-infinite-card]: [Audio8 ASR Infinite model card](../raw/Audio8-ASR-Infinite.md) — locators: frontmatter `license`, `language`; `Highlights` (clock, rolling KV, semantic VAD); `Optimized operation points` table; `Architecture` component table; `Checkpoint specification` (8.17 GB); `Evaluation` table at 480 ms vs Voxtral and Nemotron 3.5 at 560 ms.
[^fun-asr-nano-card]: [Fun-ASR-Nano-2512 model card](../raw/Fun-ASR-Nano-2512.md) — locators: model family table (0.8B; zh/en/ja; dialects/accents); `TODO` (timestamps, diarization unchecked); `Performance` open-source WER table (AISHELL-1, WenetSpeech, incl. GLM-ASR-nano and Whisper-large-v3 columns) and industry WER table (averages 16.72 / 26.13 / 33.39).
[^fun-asr-mlt-nano-card]: [Fun-ASR-MLT-Nano-2512 model card](../raw/Fun-ASR-MLT-Nano-2512.md) — locators: frontmatter `license`; supported-languages list (31); inference fence with `hotwords`, `itn`, `vad_model="fsmn-vad"`; `Performance` scope note (no MLT-specific column).
[^fun-asr-nano-gguf-card]: [Fun-ASR-Nano GGUF model card](../raw/Fun-ASR-Nano-GGUF.md) — locators: `Files` table (encoder 470 MB; Q4_K_M 484 MB, Q8_0 805 MB); quantization tier table (CER 8.35/8.25/8.30, speed); CPU claim vs whisper.cpp 22–31%.
[^glm-asr-nano-card]: [GLM-ASR-Nano-2512 model card](../raw/GLM-ASR-Nano-2512.md) — locators: frontmatter `license` (mit), `language`; `Model Introduction` (1.5B, dialects, low-volume, 4.10 average); `Benchmark` (`bench.png` only).
[^cohere-arabic-card]: [Cohere Transcribe Arabic model card](../raw/cohere-transcribe-arabic-07-2026.md) — locators: spec table (2B, Conformer encoder-decoder, Apache 2.0); `vLLM Integration`; `Results` leaderboard table dated 07.07.2026 (Average WER/CER rows incl. Qwen3-ASR 1.7B and Whisper Large v3); `Strengths and Limitations`.
[^cohere-03-2026-card]: [Cohere Transcribe model card](../raw/cohere-transcribe-03-2026.md) — locators: spec table (2B, Conformer encoder-decoder, 14 languages, Apache 2.0); Quick Start / long-form (`audio_chunk_index`, RTFx) / punctuation / batched / non-English fences; `vLLM Integration` (`vllm==0.19.0`, `POST /v1/audio/transcriptions`); `Results` English leaderboard table dated 03.26.2026 (average plus 8 per-set WER columns, 9-model comparison); `Strengths and Limitations` (3x RTF claim, single-language, timestamps/diarization, silence/VAD).
[^vibevoice-asr-card]: [VibeVoice-ASR model card](../raw/VibeVoice-ASR.md) — locators: frontmatter `license`, `language`; feature list (60-minute single pass in 64K tokens, hotwords, Who/When/What, 50+ languages, code-switching); `Evaluation` (figures only, no text values).
[^vibevoice-asr-streaming-1-5b-card]: [VibeVoice-ASR-Streaming-1.5B model card](../raw/VibeVoice-ASR-Streaming-1.5B.md) — locators: frontmatter `license`, 10-language list; intro (streaming who-said-what, hotwords); `Evaluation` (figure only).
[^vibevoice-asr-streaming-7b-card]: [VibeVoice-ASR-Streaming-7B model card](../raw/VibeVoice-ASR-Streaming-7B.md) — locators: frontmatter; H2 checkpoint title; intro and `Evaluation` (figure only; text identical to the 1.5B card apart from the title).
[^vibevoice-asr-streaming-7b-gguf-card]: [VibeVoice ASR Streaming 7B GGUF for audio.cpp](../raw/VibeVoice-ASR-Streaming-7B-GGUF.md) — locators: file list (BF16, Q8_0 recommended, Q4_K); `Use with audio.cpp` (model manager, CLI, server, live streaming).
[^moss-transcribe-diarize-card]: [MOSS-Transcribe-Diarize 0.9B HF model card](../raw/MOSS-Transcribe-Diarize.md) — locators: header (0.9B, 90-minute single pass, 50+ languages, hotwords); `News` (2026-07-09 release, 2026-07-14 MLC-SLM win with 14 listed languages); `Evaluation` (AISHELL-4 14.84/15.83/0.99, Alimeeting 24.86/22.17/−2.69, Podcast 5.97/7.37/1.40, Movies 6.36/12.76/6.40); `Serve with SGLang and VLLM` (SGLang Omni `verbose_json`, vLLM `--trust-remote-code`); `Subtitle Web App`; `Output Format` (`[start][Sxx]text[end]`).
[^moss-transcribe-cpp-gguf-card]: [MOSS-Transcribe-Diarize GGUF](../raw/moss-transcribe.cpp-gguf.md) — locators: intro (joint transcription + diarization + timestamps, CPU, no Python); F32 3.4 GB note; file/size/wall-time/transcript-identity table on the 11 s JFK clip; frontmatter `license`.
[^sensevoice-small-gguf-card]: [SenseVoiceSmall GGUF for audio.cpp](../raw/SenseVoiceSmall-GGUF-audiocpp.md) — locators: frontmatter `license`, `language`; `File` (254,211,200 bytes); `Usage`; export and parity-check section.
[^audio-flamingo-gguf-card]: [Audio Flamingo 3 and Next GGUF](../raw/Audio-Flamingo-GGUF.md) — locators: frontmatter `license` / `license_name: nvidia-oneway-noncommercial`; `Usage` ASR CLI; CUDA performance table (RTX 5090, RTF, peak VRAM).
[^faster-whisper-readme]: [Faster-Whisper README](../raw/faster-whisper.md) — locators: header (CTranslate2, up to 4x claim); `Benchmark` (Large-v2 GPU table, distil-large-v3 table, small model CPU table); `Usage` (`BatchedInferencePipeline`, `turbo`, `distil-large-v3`, VAD filter).
[^audio-cpp-gguf-readme]: [audio.cpp GGUF Model Packages](../raw/audio.cpp-gguf.md) — locators: package table rows (Canary-180M-Flash, Citrinet, Cohere-Transcribe, CrisperWhisper2.0, Fun-ASR-Nano-2512, GigaAM, Granite-Speech-5.0-470M-TurboCTC, Hviske-v5.3, Kroko, MMS-Forced-Aligner, MOSS-Transcribe-Diarize, Moonshine-Streaming, Nemotron-3.5-ASR, Niagara, Parakeet-TDT-0.6B-v3, Qwen3-ASR-0.6B/1.7B, Qwen3-ForcedAligner, VibeVoice-ASR); ASR CLI example.
[^parakeet-readme]: [Parakeet ASR server README](../raw/parakeet.md) — locators: intro (Go, ONNX Runtime, Parakeet TDT 0.6B, Whisper-compatible API, SSE); Docker CPU/CUDA images; license section.
[^fast-gpu-asr-readme]: [Fast GPU ASR README](../raw/fast-gpu-asr.md) — locators: header (SoundsGoodAI, Zipformer plus Parakeet, TensorRT, GPU beam search); `Batched speech recognition at up to 25,000 RTFx on B300` (FP16 beam-6 A100/H200/B300 table; B300 batch-256 25,108.6 RTFx Zipformer / 19,398.7 Parakeet V3 TDT; Open ASR Leaderboard reproduction, 157.8 h); `Models and Inference Precision` (family/checkpoint/decoder table); `Transcribe` (`ASR` fence, word timestamps).
[^omnilingual-readme]: [Omnilingual ASR README](../raw/omnilingual-asr.md) — locators: header (1600+ languages, few-paired-examples claim, 7B-LLM-ASR SOTA with CER below 10 for 78%); `December 2025 Update` (v2 accuracy suite, Unlimited-length suite, no-finetuning-recipes note); `Model Architectures` table (W2V/CTC/LLM/Unlimited/ZS params, download, VRAM, RTF; footnotes 1–3; tokenizer rows); `Inference` (40-second warning, `ASRInferencePipeline` fence); `Supported Languages` (`{lang}_{script}` format, `lang_ids.py::supported_langs`); `Using the HuggingFace Dataset` (CC-BY-4.0 corpus, `lij_Latn` fence); `Model Download & Storage`; `Training`; `License` (Apache 2.0).
[^thewhisper-turbo-card]: [Elastic model: thewhisper-large-v3-turbo](../raw/thewhisper-large-v3-turbo.md) — locators: frontmatter (`base_model`, `cc-by-4.0`, 28-code `language` list); `Overview` (ANNA XL/L/M/S bounds); `System Requirements` + `Access Token Setup`; `TheStage Apple SDK` (SwiftPM 1.1.0, batch/streaming fences, 10 s window, audio contract, M2 Max RTFx 16.7 table); `ElasticModels` + `TheWhisper SpeechKit` (JFrog install, `mode='S'`, `chunk_length_s` 15/10, streaming fences); `Quality Benchmarks` (English 9-row and multilingual 16-row WER tables with Mean rows); `Latency Benchmarks` + `Benchmarking Methodology` (batch-1 and batched RTFx tables, 10-minute 16 kHz method); `Serving with Docker Image` + `Invocation` + `Endpoint Parameters` (ECR tag, env-var table, `X-Model-Name` format).
[^wlk-readme]: [WhisperLiveKit README](../raw/WhisperLiveKit.md) — locators: intro; `--backend-policy` (SimulStreaming / LocalAgreement); `--backend` selector list; API compatibility section.
[^realtimestt-readme]: [RealtimeSTT README](../raw/RealtimeSTT.md) — locators: intro (VAD-gated recording, realtime + final transcription engines, wake word); server section.
[^speaches-readme]: [Speaches README](../raw/speaches.md) — locators: overview excerpt (OpenAI-compatible, faster-whisper STT, SSE streaming, dynamic model loading).
[^index-echo-s2tt-gguf]: [Index-Echo S2TT GGUF](../raw/Index-Echo-S2TT-GGUF.md) — locators: intro (2B/9B, Chinese speech → timestamped transcript + en/es/ja translation, audio.cpp).
[^vi-primary-research]: [Primary research capture](../raw/vietnamese-asr-research-2026-10-07/README.md) — `qwen-report.html` §2.4/Table2, §4.5/Table8 and AppendixTableA.2 vi; PhoWhisper README WER/card license; ChunkFormer CTC/RNNT cards Benchmark Results/frontmatter and ONNX guide Export/Online streaming; ZipFormer30M upstream card license/Evaluation Results/Inference Speed. Package ledger records unavailable small-card fetch and pending assets.

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `PHẦN 1` §4 STT/ASR table (PhoWhisper, ChunkFormer-large-vie, sherpa-onnx Zipformer VN, Qwen3-ASR and Nemotron Vietnamese rows); `PHẦN 2` hardware tiers. LLM-generated report; figures are its citations, not verified here.
[^reddit-asr-tts-thread]: [Good ASR and TTS models? thread capture](../raw/good_asr_and_tts_models.md) — locators: `Comments 51` (Nemotron 3.5 streaming pick; Qwen3-ASR VRAM, streaming-vs-Parakeet, VAD-frontend remarks).
[^reddit-noisy-stt]: [Best Speech-to-Text in 2025? thread capture](../raw/best_speechtotext_in_2025.md) — locators: `Comments 53` (Parakeet 400–500% faster remark; Whisper-large-v3 plus preprocessing defence; Canary/Granite mentions).
[^reddit-open-stt]: [What's the best open speech to text today? thread capture](../raw/whats_the_best_open_speech_to_text_today.md) — locators: `Comments 36` (Qwen3-ASR least-hallucination remarks; turbo vs large-v3; Moonshine English low-latency remark).
[^reddit-stt-llm-tts-thread]: [STT -> LLM -> TTS pipeline thread capture](../raw/stt_llm_tts_pipeline.md) — locators: replies on Parakeet v2 vs Whisper (~5x) and v3 multilingual slowdown.
[^reddit-usable-stt]: [Best STT API for voice agents? thread capture](../raw/best_stt_api_for_voice_agents_i_care_more_about.md) — locators: prompt and top replies (first stable text, partial stability, endpointing, barge-in, entity accuracy checklist).
[^whisper-v3-card]: [Whisper large-v3 model card](../raw/whisper-large-v3.md) — locators: header (128 mel bins, Cantonese token; 1M weakly + 4M large-v2 pseudo-labeled hours, 2.0 epochs, 10–20% over large-v2); `Model details` (7-row size/parameter table); `Usage` (pipeline, decoding, language/task, timestamp fences); `Additional Speed & Memory Improvements` (sequential vs chunked, torch.compile, Flash-Attention 2, SDPA); `Performance and Limitations` (no numeric table; hallucination/unevenness/repetition notes); frontmatter (`license: apache-2.0`, ~99-code `language` list).
[^whisper-turbo-card]: [Whisper large-v3-turbo model card](../raw/whisper-large-v3-turbo.md) — locators: header (32→4 decoder-layer pruning, 809M, minor-degradation/faster claim); `Model details` (8-row size/parameter table); `Usage` (pipeline, decoding, language/task, timestamp fences); `Additional Speed & Memory Improvements` (sequential vs chunked, torch.compile, Flash-Attention 2, SDPA); `Performance and Limitations` (no numeric table; hallucination/unevenness/repetition notes); frontmatter (`license: mit`, 90-plus-code `language` list).
[^confucius4-r2t2-readme]: [Confucius4-R2T2 GitHub README](../raw/Confucius4-R2T2.md) — locators: frontmatter (`base_model`, `pipeline_tag`, `license_name`); intro (append-only output, 80 ms–2 s chunks, 200–600 ms latency, LSP paradigm, hotwords, zh/en plus others); `Evaluation` (160 ms English WER and Chinese CER tables, ※ pseudo-streaming note, Figures 3–5 fuzzy-latency Pareto); `Installation` / `Docker` / `Quick Start` (env-var table); `Python API` (offline and streaming fences); `WebSocket Server` (launcher flags, Stream-VAD download, `/asr_stream_api_v1`, message JSON, client flags); `Supported Languages`; `License` (dual Apache-2.0 / NetEase).
[^phonon-2-card]: [Phonon-2 model card](../raw/Phonon-2.md) — locators: frontmatter (`base_model: nvidia/parakeet-tdt-0.6b-v3`, `base_model_relation: quantized`, `language: en`, `library_name: mlx`, `metrics: wer`); `# Phonon-2` intro (sub-900MB claim, 5.21% seven-set average, 100.8% teacher word accuracy on parliamentary speech, meetings win, 15x smaller download, five learned levels in ~2.1 bits, M5 174x / Zen 5 143x / H100 6,680x batch-128 throughput); `## Benchmarks` (8-row vendor-run WER table, teacher 4.96 in-table); `## Run it` (Detta app, pip/MLX fences, `--json` word timings, docs URL, Linux/Windows engines, Docker `phonon-cpu:2.0.6` / `phonon-cuda:1.0.5` fences); `## Notes` (tokenizer/output conventions, CC-BY-4.0 + NOTICE, CLI Apache-2.0).

[^granite-turboctc-card]: [Granite-Speech-5.0-470M-TurboCTC](../raw/granite-speech-5.0-470m-turboctc.md) — locators: header badges (apache-2.0, en, automatic-speech-recognition, transformers); Model Summary (470M, edge deployment, conformer encoder with block self-attention/self-conditioning/temporal downsampling, 16,384 BPE head, ~60,000 h English, greedy non-autoregressive CTC); Release Date Aug 25 2026; Intended Use (enterprise low-latency/high-throughput STT); Usage (transformers>=5.16.0 `AutoModelForCTC` fence; mlx-audio>=0.5.1 fence; transcribe.cpp Q8_0 GGUF fence); Model Architecture (16 conformer blocks, 8x subsampling 100 Hz to 12.5 Hz, 128-frame block attention, 8-row config table); Training Data (7-row table totaling 57,710 h + 2,000 h / 500 h concatenations + 240 h gpt-oss/StyleTTS2 numerics); Infrastructure (Blue Vela H100, 10 days on 8 H100); Evaluations (Open ASR plots as of Oct 2 2026 RTFx on 1 H200; FFASR plots as of Aug 25 2026 RTFx on 1 L4 — all image-only, no numeric WER/RTFx in text).
[^indic-conformer-card]: [IndicConformer-600M-Multilingual](../raw/indic-conformer-600m-multilingual.md) — locators: frontmatter (`license: mit`, `pipeline_tag`); header intro (22 official Indian languages, first open-source claim); `Model Details` (600M, hybrid CTC plus RNNT, IN-22, repository link); `Model Usage` (CTC/RNNT bullets; pip install fence; `AutoModel.from_pretrained` plus 16 kHz/`hi`/ctc/rnnt inference fence); `Supported Languages` (22 codes `as` through `ur`; external `IndicVoices/artifacts/tokenizers` link).
[^orukeet-card]: [Orukeet model card](../raw/orukeet.md) — locators: intro (25-language V3 finetune, 12,288 Gabor kernels, 61/74 wins, LS/FLEURS/pooled WERs, r3 checkpoint); `Architecture` (627M params, Gabor equation, 626.9M trainable); `Evaluation` (6-row table with recording counts); `sherpa-onnx`/`Native`/`transcribe.cpp`/`Core ML` (file layout, 390 ms timing, OpenWhispr 1.10.0, GGUF sizes, 9.5% Core ML cut); `Model files` (byte table, revision pins, SHA-256s); `License` (CC BY-SA 4.0 weights, MIT code).
[^parakeet-redux-card]: [Moondream Parakeet Redux model card](../raw/parakeet-redux.md) — locators: intro (1.58-bit ternary `parakeet-tdt-0.6b-v3`, 178 MB, 113× on eight x86 cores, 2.5× fastest other runtime); `Usage` (Photon `pip install moondream`, `cpu/mps/cuda` devices, segment/word timestamps; encoder-subsampler VAD head, ≤30 s segmentation); `Performance` (x86 EPYC 9575F and M2 Air tables; one-utterance method); `Benchmarks` (Open ASR 7-set 6.55 vs 6.26, 25-language FLEURS 10.56 vs 11.62, AA-WER business 6.96 vs 6.15, 9-condition MUSAN noise 9.04 vs 6.72, TED-LIUM 2.51 vs 2.71); `Notes` (original tokenizer/conventions, CC-BY-4.0).
[^parakeet-ultra-card]: [Moondream Parakeet Ultra model card](../raw/parakeet-ultra.md) — locators: intro (post-trained `parakeet-tdt-0.6b-v3`, same architecture/tokenizer/0.6B full precision, 5-row headline table with Open ASR 5.80 vs 6.26 / FLEURS 9.55 vs 11.62 / business 5.79 vs 6.15 / noise 5.82 vs 6.72 / TED-LIUM 1.94 vs 2.71); `Usage` (`pip install moondream`, `md.photon("moondream/parakeet-ultra")`, segment/word timestamps; encoder-subsampler VAD head, ≤30 s segmentation); `Performance` (B200 128-in-flight, LibriSpeech 9,743× vs 6,005× and AMI 6,688× vs 4,394×); `Benchmarks` (7-row Open ASR, 25-row FLEURS, 3-row AA-WER business, 9-row MUSAN noise, TED-LIUM 1.94 vs 2.71 tables).
[^seamless-m4t-v2-card]: [SeamlessM4T v2 model card](../raw/seamless-m4t-v2-large.md) — locators: header (2.3B Large v2, UnitY2, 101 speech-in / 96 text / 35 speech-out; S2ST/S2TT/T2ST/T2TT/ASR); `SeamlessM4T models` table (v2/v1/medium sizes, checkpoints, metrics zips, FLEURS/CoVoST2/CVSS-C IDs); `Transformers usage` (Transformers + sentencepiece install, `SeamlessM4Tv2Model` text/audio fences, 16 kHz resample, `sampling_rate`); `Supported Languages` table (`Sp`/`Tx` Source/Target, `vie` row, speech-only/text-only rows, medium-200/NLLB-200 note); frontmatter (`cc-by-nc-4.0`, `pipeline_tag`, `transformers`).
[^whistle-card]: [Whistle: Speech Recognition for Tiny Devices](../raw/whistle.md) — locators: frontmatter (`library_name: cactus-needle`, `pipeline_tag`, `license: apache-2.0`, 7-code `language` list); intro (16.9 MB single file, shared Needle CPU engine/container/quantisation, no dependencies/GPU, three on-device jobs); section `Model` (log-mel front end, convolutional stem, Needle-shaped decoder, gated cross attention, `.cact`/Cactus Quants/SIMD/KV cache, laddered `--audio-depth`); section `Benchmarks` (full-split WER with Whisper normalizers, 86,174 utterances, M4 Pro 10 s method at 5 beams, TTFB/decode definitions, 2–4-bit vs fp32 vs int8, AMI/TED-LIUM/FLEURS/MLS scoring notes, checksum plus speaker-ID leak check; figures image-only in `whistle-benchmarks.svg`); sections `Get started` / `With Needle` / `Deploy` (pip/`[mic]` extra, `transcribe`/`Whistle`/`playground`/`compare`, joint `audio_`-prefixed JSON, `needle download` fences, C API, no-env-var determinism).
[^moss-audio-card]: [MOSS-Audio model card and README](../raw/MOSS-Audio-4B-Instruct.md) — locators: `Released Models` 4-row table (Qwen3-4B/8B, ~4.6B/~8.6B); `Evaluation` general-audio table (8B-Thinking 71.08 in-table vs 70.80 prose), captioning table (8B-Instruct 3.7252, 11/13 claim), ASR 13-column CER table (8B-Instruct 11.30 overall), timestamp-AAS table (8B-Instruct 35.77 / 131.61); `Model Architecture` (12.5 Hz, DeepStack, time tokens); `Quickstart` (conda 3.12, cu128 install, `infer.py`, `app.py`, `moss-audio` SGLang branch).
[^nemo-speech-readme]: [NeMo-Speech.cpp README](../raw/NeMo-Speech.cpp.md) — locators: `Models and applications` (four ASR checkpoints, combined diarization); `Performance` (Nemotron EN Q8_0, 160 ms chunks, RTX 4090/CPU table, unavailable `BENCHMARK.md`); `Quick start`; `Local server and playground`; `Native SDK`; `License`.
[^speaker-diar-coreml-card]: [Speaker Diarization Core ML](../raw/speaker-diarization-coreml.md) — locators: intro (FluidAudio, scoped CC-BY-4.0); `Supported Community-1 artifacts`; `Provenance status`; `Legacy compatibility artifacts`; `Technical specifications` (16 kHz mono, segments, iOS 17/macOS 14); `Usage`. DER and latency are not supplied; linked binaries and provenance records were not inspected.
[^transcribe-cpp-readme]: [transcribe.cpp](../raw/transcribe.cpp.md) — locators: header tagline (C/C++ STT, GGUF on ggml, Metal/Vulkan/CUDA, tinyBLAS CPU, handy-computer verification); `Supported models` family-index tables (20 STT families + diarization-only table); `Model catalog` (`catalog.db`, `_benchmark_profiles.json`, `render.py` markers); `Build` (Metal/Vulkan/CUDA/HIP fences, openblas ~10-15x, tinyBLAS); `Models`/`Quantize`/`Usage` (handy-computer GGUFs, `convert-parakeet.py`, `F16/Q8_0/Q6_K/Q5_K_M/Q4_K_M`, `transcribe-cli`, 16 kHz mono); `Bindings`/`Tests` (4 bindings, `--device 0` migration, `ctest` + real-model flag); `Sponsors`/`Project layout`/`License` (MIT).
