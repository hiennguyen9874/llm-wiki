---
type: Concept
title: parakeet.cpp Bundles, VAD, Diarization and Scene Stream
description: parakeet.cpp's non-ASR features — Silero and Moondream-head VAD with pause-based long-audio cutting, single-file bundle GGUFs, Sortformer diarization, CED sound tagging, speaker enrollment, and a combined words/speakers/sounds scene stream — with README-reported limits.
tags: [vad, stt, diarization, ggml, gguf, parakeet, edge-deployment, endpointing]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T12:00:00Z }
stale_after: 2027-04-21
sources:
  - id: parakeet-cpp-readme
    resource: ../raw/mudler-parakeet.cpp.md
    kind: documentation
    title: mudler/parakeet.cpp README
---

Beyond transcription, [parakeet.cpp](parakeet-cpp.md) adds voice activity detection, diarization, sound-event tagging, speaker identification, and one-file model bundles, all master-branch features at capture (not in v0.5.0) and all reported without independent verification (**Reported**).[^parakeet-cpp-readme] This page keeps the pieces that matter for turn-taking and pre-segmentation in a voice pipeline.

## VAD and long-audio cutting

- Two detectors: Silero VAD (a 1.3 MB GGUF, 16 kHz and 8 kHz, MIT) and the VAD head of Moondream's [Parakeet Ultra](parakeet-ultra.md)/[Parakeet Redux](parakeet-redux.md); a streaming VAD API exists in the C API (**Reported**).[^parakeet-cpp-readme]
- `parakeet-cli vad --model M --input A.wav [--mode segments] [--probabilities] [--run-gate P]` emits JSON with `mode`, `duration`, `frame_sec` (0.032 in the example), `backend`, and `segments[{start,end}]` (**Reported**).[^parakeet-cpp-readme]
- `transcribe --vad [--vad-model silero.gguf]` cuts long audio at pauses then transcribes each piece with any ASR model; `--vad-trim SEC` trims each piece to its speech plus SEC (default 0.3, 0 = whole cuts); it is offline and greedy-decoding only (**Reported**).[^parakeet-cpp-readme]
- Noise handling: the Ultra/Redux head gives false alarms on audio without speech, so the README advises Silero as an always-on gate. The opt-in `--run-gate` / `--vad-run-gate` (example 0.92) drops speech runs with low median probability and removes most noise false alarms but not music; `--min-local-conf 0.5` drops words invented on noise (**Reported**).[^parakeet-cpp-readme]
- VAD-only GGUF slices (6–10 MB) of the Ultra/Redux head run `vad` but cannot transcribe (**Reported**).[^parakeet-cpp-readme]
- VAD accuracy/speed/size comparisons against Silero and whisper.cpp live in an uncaptured `docs/vad-benchmarks.md`; some runs were not on a quiet machine, per the README. No VAD numbers are therefore recorded here (**Synthesis**).[^parakeet-cpp-readme]

## Bundle GGUF

- One GGUF can hold ASR, VAD, diarization, sound-event, and speaker-voice components with one licence per component; `parakeet-cli info` lists components, licences, and sizes (**Reported**).[^parakeet-cpp-readme]
- Published bundles: `parakeet-bundle-small` (110M ASR, 338 MB; also Silero, diarization, CED, speaker encoder), `parakeet-bundle-standard` (0.6B v3 ASR, 1.1 GB), `parakeet-bundle-moondream-redux` (packed Redux plus Silero, 215 MB); each has a `NOTICE-*.txt` with credits and licences (**Reported**).[^parakeet-cpp-readme]
- Limits: `bench` and the streaming ASR modes do not accept a bundle; no bundle was run on a GPU (**Reported**).[^parakeet-cpp-readme]

## Diarization and speaker identification

- Nemotron-3-Diarization (Sortformer; up to 8 speakers; OpenMDW-1.1) answers who spoke when; speaker-attributed ASR says who said what (see [Nemotron 3 Diarization](nemotron-3-diarization.md) for the upstream model and [Nemotron 3 Diarization GGUF](nemotron-3-diarization-gguf.md) for another ggml packaging) (**Reported**).[^parakeet-cpp-readme]
- Speaker identification: `parakeet-cli enroll --model SPK.gguf --name Ada --input ada.wav --registry R` enrolls from short clips, and `scene --speakers SPK.gguf --registry R` names speakers. The registry records which encoder made each voice print and refuses a model mismatch before naming (the "speaker fingerprint") (**Reported**).[^parakeet-cpp-readme]
- C API `parakeet_capi_speaker_embed_pcm` returns a clip's voice embedding from a standalone encoder or a bundle `voice` component (**Reported**).[^parakeet-cpp-readme]
- Evidence limit: speaker identification was measured on one two-voice fixture (**Reported**).[^parakeet-cpp-readme]

## Sound events and the scene stream

- CED tags 527 sound classes (6–88 MB models from `ced.cpp`; compile option `PARAKEET_WITH_CED`; the upstream tagging family is compiled in [CED Audio Tagging Family](ced-audio-tagging-family.md)). `parakeet-cli scene --model ASR --diar DIAR --sound CED --input A.wav` produces one time-ordered feed of words, speakers, and sounds, shown on CPU with lines like `[00:00.4 - 00:05.4]  Speaker 0: ...` (**Reported**).[^parakeet-cpp-readme]

## Relationships

- Part of [parakeet.cpp](parakeet-cpp.md); uses [Silero VAD](silero-vad.md) as the recommended always-on gate, compare its VAD-in-ASR-engine counterpart [CrispASR VAD and Language Identification](crispasr-vad-language-id.md) (**Synthesis**).
- The EOU model [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md) is the runtime's end-of-utterance path for streaming; the VAD here is pause-based cutting for offline audio, not turn-taking, and the README reports no endpointing-latency measurements (**Synthesis**).[^parakeet-cpp-readme]
- Diarization post-processing alternatives: [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) (**Synthesis**).

## Coverage and limits

- Same single README capture as [parakeet.cpp](parakeet-cpp.md), inspected statically; no command run. Uncaptured: `docs/vad.md`, `vad-benchmarks.md`, `bundle.md`, `diarization.md`, `sound.md`, `speaker.md`, `ultra-redux.md`, and the demo MP4s/GIFs, so option semantics, DER, tagging accuracy, and speaker-ID accuracy are unestablished (**Synthesis**).[^parakeet-cpp-readme]
- Time-sensitive master-branch features; `stale_after: 2027-04-21` under the `vad` and `stt` domain rules.

[^parakeet-cpp-readme]: [mudler/parakeet.cpp README](../raw/mudler-parakeet.cpp.md) — locators: `What is new` (VAD-only files, standalone VAD, bundle GGUF, speaker fingerprint and embeddings, diarization, sound events); `Quick start` (Find speech with VAD, Use a bundle); `Models` (Silero, CED, Nemotron-3-Diarization rows); `CLI cheat sheet` (`vad`, `scene`, `enroll`, `--vad*` flags); `C API` Surface bullet; `Limits` bullets on VAD head, `transcribe --vad`, bundles, speaker identification.
