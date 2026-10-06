---
type: Concept
title: Community-Reported Noisy On-Premise STT Selection
description: Community-reported on-premise noisy call-transcription tradeoffs comparing Parakeet and Whisper with preprocessing, diarization, CPU/quantization, and formatting caveats.
tags: [stt, vad]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T10:00:32Z }
stale_after: 2027-10-06
sources:
  - id: reddit-noisy-stt
    resource: ../raw/best_speechtotext_in_2025.md
    kind: documentation
    title: Best Speech-to-Text in 2025? r/LocalLLaMA thread capture
---

This thread collects community-reported tactics for in-house transcription of noisy calls on a single-GPU Ubuntu server, centering on Whisper-large-v3 versus NVIDIA Parakeet plus a preprocessing, vocal-isolation, and diarization frontend, with side notes on CPU/INT8 deployment, number-formatting post-processing, verbatim-versus-corrective behavior for pronunciation scoring, and multimodal LLM cleanup; every comparative or performance claim below is an unverified anecdote from anonymous commenters, not a measured result (**Reported**).[^reddit-noisy-stt]

## Source scope and request

- The starter reports an in-house-only call-transcription requirement (no third party) on a server described as 26 GB VRAM (GeForce GTX 4090) with 64 GB RAM on Ubuntu server, reports Whisper at about 75% accurate and fragile under background voices, and asks for best local STT models or techniques; the VRAM figure is inconsistent with a stock RTX 4090 (24 GB) and is preserved here as reported (**Reported**).[^reddit-noisy-stt]
- The capture holds the prompt plus 53 comments with anonymous authors, no capture date, and upstream links to the subreddit thread, Handy, Ultimate Vocal Remover, whisper.cpp, a Modal batch-transcription post, Talo, Palabra, and a TextSpeak promo; per-comment vote tallies are omitted here as volatile and non-durable (**Reported**, with omission **Synthesis**).[^reddit-noisy-stt]

## ASR selection tradeoffs

- Parakeet is repeatedly recommended over Whisper for English: one report calls it amazing with about 100x realtime on an M3 MacBook Air via MacWhisper, another calls it better than Whisper in everything at 400%–500% faster, and another calls it very good and pretty fast on CPU alone (**Reported**).[^reddit-noisy-stt]
- The counter-position is that Whisper-large-v3 plus preprocessing and diarization remains viable in noise, and that Whisper Turbo resolves one commenter's number-formatting pain enough to accept its extra latency; one production baseline reports whisper.cpp and faster-whisper each taking about 30 minutes for 30 minutes of audio (about 1x realtime) (**Reported**).[^reddit-noisy-stt]
- Other named options carry no in-thread measurement: per-language NVIDIA ASR models, Canary and Granite-based ASR as more robust alternatives, Voxtral Small (multimodal, system-prompted cleanup or translation plus an untested transcription-only variant), Qwen3 Omni (suggested once, with a follow-up saying no good reviews seen), and Gemini-Flash or GPT-4o-transcribe named from memory as implicit LLM-cleanup examples (**Reported**).[^reddit-noisy-stt]
- Language scope is flagged as the missing requirement: one commenter asks which language is most important, with a reply arguing the post language (English) is a reasonable default; treat all English-favoring Parakeet claims as language-conditional (**Reported**).[^reddit-noisy-stt]

## Noise-robustness pipeline

- Standard frontend before Whisper-large: noise reduction (e.g. `noisereduce`), high-pass filter, and compressor, plus speaker diarization to isolate one speaker when overlapping voices confuse the model (**Reported**).[^reddit-noisy-stt]
- Vocal isolation with Ultimate Vocal Remover as a prefilter: extract a vocal-only file before ASR, optionally with ensemble mode averaging several models; the reporter notes CUDA acceleration, an AMD beta used on a 7900 XTX, a built-in model download manager, batch file lists, and in-memory model caching for bulk conversion (**Reported**).[^reddit-noisy-stt]
- A mixed-stack suggestion chains noise suppression, VAD, and beamforming in front of ASR, or moves to Canary, Granite-based ASR, or enterprise options; Talo and Palabra are suggested only for prototyping or testing accuracy in noise under a cloud-only or hybrid stack, which conflicts with the starter's in-house-only constraint (**Reported**).[^reddit-noisy-stt]

## Deployment notes

- Reported Parakeet quantization/latency on a 12th-gen i3 Intel NUC for one voice command: FP16 on GPU about 0.1 s, FP16 on CPU about 0.42 s, INT8 on GPU about 0.25 s, with INT8-on-CPU motivated by freeing about 3.5 GB of VRAM; command length, audio duration, and measurement protocol are absent, and longer-term quantization degradation is left as an open feel-for-it question (**Reported**).[^reddit-noisy-stt]
- Realtime typing gap: MacWhisper is reported as lacking realtime transcription typing even for fast models such as Parakeet, with Handy (`handy.computer`) suggested as the tool for that need; no version, config, or latency figure is given (**Reported**).[^reddit-noisy-stt]
- One Audio8 ASR Infinite configuration report states that a short transcription delay ends sentences with a period and no trailing space (`output.Looks quite.Ridiculous` pattern); no fix is given in the capture (**Reported**).[^reddit-noisy-stt]

## Output formatting and downstream use

- Parakeet number-formatting complaint: it spells out numbers even for years and very large numbers where digits are expected; proposed fixes are regex rules converting words back to digits or small-LLM post-processing, both adding latency, while one commenter prefers Whisper Turbo output that avoids the fixup step and plans to check the next NVIDIA ASR model (**Reported**).[^reddit-noisy-stt]
- Pronunciation-evaluation constraint from a thesis use case: Wav2Vec2 is reported as verbatim (transcribes exactly what it hears, with errors even on correct pronunciation) while Whisper Tiny is reported as context-correcting (unsuitable when scoring pronunciation); phoneme comparison and IPA-to-Whisper plus phoneme-based Wav2Vec2 loading are reported as tried and still inaccurate, with no solution in-thread (**Reported**).[^reddit-noisy-stt]
- Multimodal cleanup idea: chain the audio stage implicitly or explicitly to a small LLM (Wav2Vec-era code recalled), or use an audio-input LLM such as Voxtral Small with a system prompt like "Take the audio input and create correct english phrases out of it", which then translates recognized speech to English rather than producing a pure transcript (**Reported**).[^reddit-noisy-stt]

## Contradictions

- Whisper versus Parakeet for noisy calls: preprocessing-plus-Whisper-large advocates report accuracy recovery in noise, while Parakeet advocates report across-the-board superiority plus 4–5x speed; no shared audio, config, or WER protocol resolves the pick, so it stays requirement- and hardware-dependent (**Reported**).[^reddit-noisy-stt]
- Instant-result versus correctable output: one commenter prioritizes time-to-result and fixes errors later, another accepts extra latency from Whisper Turbo because manual number fixup is slower; no latency-versus-error measurement is given (**Reported**).[^reddit-noisy-stt]
- Language-default dispute: one side demands the target language before recommending, the other treats the post language as the default; the Parakeet-favoring claims are therefore only interpretable as English-conditional (**Reported**).[^reddit-noisy-stt]

## Relationships

- Uses [Parakeet TDT 0.6B V2](parakeet-tdt-0.6b-v2.md): the thread's Parakeet speed, accuracy, CPU, and next-NVIDIA-model remarks relate to the offline Parakeet TDT lineage covered there; no thread remark maps to a specific checkpoint or version (**Synthesis**).[^reddit-noisy-stt]
- Uses [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): the multilingual and next-model remarks relate to the newer multilingual Parakeet checkpoint covered there; the thread gives no version-to-checkpoint mapping (**Synthesis**).[^reddit-noisy-stt]
- Uses [Canary-1b-v2](canary-1b-v2.md): the thread names Canary as a more robust alternative for noisy calls; read that concept for verified language scope and published benchmarks (**Synthesis**).[^reddit-noisy-stt]
- Uses [Qwen3-ASR family](qwen3-asr-family.md): the thread's Qwen3 Omni suggestion relates to that family; the thread provides no evaluation, and the only follow-up reports seeing no good reviews (**Synthesis**).[^reddit-noisy-stt]
- Uses [Audio8 ASR Infinite](audio8-asr-infinite.md): the thread's short-delay sentence-splitting report concerns that model's configurable transcription delay; read that concept for the verified clock and delay mechanism (**Synthesis**).[^reddit-noisy-stt]
- Uses [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md): the thread's speaker-diarization-before-ASR advice relates to the offline diarization approach covered there; the thread names no diarization checkpoint (**Synthesis**).[^reddit-noisy-stt]
- Uses [Community-Reported Local ASR/TTS Selection](community-asr-tts-selection.md): the companion thread concept covers the same Whisper-versus-Parakeet, VAD-frontend, leaderboard, and Handy/audio.cpp practices from a different capture; read both as unverified community reports, not measurements (**Synthesis**).[^reddit-noisy-stt]

## Coverage and limits

- Source inspected statically only; no model installed, no audio transcribed, no latency, VRAM, WER, or quality claim reproduced, and no linked repository, leaderboard, or model page fetched beyond the URLs quoted above (**Synthesis**).[^reddit-noisy-stt]
- Authors are anonymous in the capture (`unknown` except the prompt author), with no capture date, no hardware details for most claims, no model versions or configs, no audio or measurement protocol, and no locator beyond comment text; all comparative and performance claims are therefore **Reported** and **Unverified**, and this concept stays `draft` until primary sources or reproductions corroborate them (**Synthesis**).[^reddit-noisy-stt]
- Excluded as non-durable: pleasantries and follow-up asks without answers (preprocessing-tool options, VOIP-versus-physical-infra question, Qwen3 Omni test status), exact vote tallies, the closed-source trust aside without an identifiable funded entity, the TextSpeak promo, the unevaluated Modal blog link, and the third-party mobile-app suggestion that conflicts with the in-house-only constraint (**Synthesis**).[^reddit-noisy-stt]
- Model-release and performance remarks carry `stale_after: 2027-10-06` per the `stt` and `vad` domain rules (**Synthesis**).[^reddit-noisy-stt]

[^reddit-noisy-stt]: [Best Speech-to-Text in 2025? r/LocalLLaMA thread capture](../raw/best_speechtotext_in_2025.md) — locators: title plus upstream link `https://www.reddit.com/r/LocalLLaMA/comments/1prmjt3/best_speechtotext_in_2025/` and prompt paragraph (in-house transcription, 26GB VRAM GeForce GTX 4090, 64GB RAM Ubuntu server, Whisper about 75% accurate, background-noise fragility); `Comments 53` section — Whisper-large-v3 plus noisereduce/high-pass and diarization remarks; preprocessing-plus-compressor agreement; Parakeet 100x-realtime M3 MacBook Air via MacWhisper remark; MacWhisper realtime-typing gap plus `handy.computer` remark; Parakeet number-spelling plus regex/small-LLM fixup plus Whisper-Turbo-latency remarks; Audio8 short-delay `output.Looks quite.Ridiculous` remark; Parakeet 400%–500% faster remark; INT8/FP16 GPU/CPU timings plus 3.5GB VRAM remark on 12th-gen i3 NUC; whisper.cpp plus faster-whisper 30-min-for-30-min remark; Ultimate Vocal Remover ensemble/CUDA/AMD-7900XTX/batch/cache remarks plus `https://github.com/Anjok07/ultimatevocalremovergui`; language-question dispute; Wav2Vec-plus-small-LLM, Gemini-Flash/GPT-4o-transcribe, and Voxtral-Small system-prompt remarks; per-language NVIDIA ASR remark; English Parakeet CPU remark; Qwen3-Omni suggestion plus no-good-reviews follow-up; Wav2Vec2-verbatim versus Whisper-Tiny-corrective pronunciation-evaluation plus IPA-to-Whisper remarks; VAD/beamforming plus Canary/Granite plus Talo/Palabra-prototyping remarks; TextSpeak `https://textspeakpro.com` promo; Modal `https://modal.com/blog/fast-cheap-batch-transcription` link.
