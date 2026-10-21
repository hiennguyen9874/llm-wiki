---
type: Concept
title: Sherpa Vietnamese ASR
description: MIT-licensed offline Windows app and web service for Vietnamese file transcription on CPU, combining sherpa-onnx Zipformer 30M/68M (and ROVER), Silero VAD, ONNX speaker diarization, ViBERT-capu punctuation, hotwords and DNSMOS, with no published WER, latency, or streaming evidence.
tags: [stt, asr, vietnamese, sherpa-onnx, zipformer, diarization, punctuation, onnx, windows, edge]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T22:00:00Z }
stale_after: 2027-04-21
sources:
  - id: sherpa-vi-readme
    resource: ../raw/sherpa-vietnamese-asr.md
    kind: documentation
    revision: "2.6.3 (README version badge)"
    title: welcomyou/sherpa-vietnamese-asr README capture
---

`welcomyou/sherpa-vietnamese-asr` is a Windows-first, offline Vietnamese speech-to-text application: a PyQt6 desktop app plus a FastAPI web service (with an offline PWA) that run on CPU by default and send no audio to the internet (**Reported**).[^sherpa-vi-readme] It wraps [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) Zipformer RNN-T Vietnamese models in a file-transcription pipeline with VAD, speaker diarization, overlap separation, punctuation restoration, hotwords and audio-quality scoring. The README publishes no WER, RTF, latency, or streaming evidence, so it is an integration reference for batch and meeting transcription rather than evidence for a realtime voice agent (**Observed** absence, **Synthesis**).[^sherpa-vi-readme] The optional GPU path is covered in [Sherpa Vietnamese ASR GPU Device Calibration](sherpa-vietnamese-asr-gpu-calibration.md).

## Identity and distribution

- Version 2.6.3 per the README badge (a snapshot, no commit hash); Python 3.10+; Windows 10/11 64-bit; code license MIT (**Reported**).[^sherpa-vi-readme]
- Five release zips: desktop (CPU, PyQt6 GUI, ffmpeg/ffprobe, CPU models), web service + PWA (FastAPI, Web UI), two GPU add-ons, and a GPU-models zip. The base zip is the only required download; target machines need no Python (**Reported**; Gói phát hành, Yêu cầu).[^sherpa-vi-readme]
- Requirements: Windows 10 64-bit, 8 GB RAM, Intel i3/Ryzen 3, 2 GB+ storage minimum; 16 GB+, i7/Ryzen 7+, 5 GB+ recommended (**Reported**).[^sherpa-vi-readme]
- Entry points from source: `app.py` (desktop), `server_gui.py`, and `server_launcher.py --no-gui` (web service). Portable builds use `build-portable/*.py` scripts that download models with pinned SHA256 values (**Reported**; Chạy từ source, Build, Model nguồn).[^sherpa-vi-readme]
- The web service defaults to HTTPS on port 8443 and ships a documented default admin account with a trivially weak password. Treat that as a first-run hardening item and change it before exposing the service (**Reported**; the value is deliberately not recorded here).[^sherpa-vi-readme]

## Pipeline components

| Stage | Component stated in the README |
| --- | --- |
| ASR | Sherpa-ONNX with Zipformer RNN-T 30M and 68M; three modes: Zipformer 30M, Zipformer 68M, ROVER |
| VAD | Silero VAD plus Pyannote segmentation ONNX |
| Diarization | Pyannote Community-1 and Senko CAM++ via pure ONNX Runtime; CAM++ 192-dim and Pyannote/WeSpeaker ResNet34-LM embeddings |
| Overlap separation | Conv-TasNet 16 kHz Libri2Mix ONNX (two speakers) |
| Turn analysis | "NaturalTurn" backchannel detection after Cychosz et al. 2025 |
| Punctuation and casing | ViBERT-capu ONNX, FP32 or INT8 |
| Audio quality | Microsoft DNSMOS ONNX |
| Decode and resample | ffmpeg/ffprobe; SoXR HQ/VHQ; per-segment RMS normalization cited to Prabhavalkar et al. 2015 |
| Summarizer | Gemma 4 E2B GGUF via llama-cpp-python (a local post-processing LLM, not a dialogue LLM) |

(**Reported**; Công nghệ, Papers.)[^sherpa-vi-readme]

Input formats: MP3, WAV, M4A, FLAC, AAC, OGG, MP4, MKV, AVI, MOV, WEBM. Desktop extras: live recording, rename/merge/split speakers, sentence-level seek, light/dark theme. Service extras: Web UI, job queue, accounts, admin GUI, Windows Service, offline PWA that runs ONNX Runtime Web (WASM, with WebGPU where the browser supports it) (**Reported**).[^sherpa-vi-readme]

## Model provenance and licensing

- ASR checkpoints are credited to `hynt/Zipformer-30M-RNNT-6000h` (30M) and `csukuangfj/sherpa-onnx-zipformer-vi-2025-04-20` (68M) (**Reported**; Ghi nhận).[^sherpa-vi-readme] The wiki's own cards for these are [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md) (CC-BY-NC-ND-4.0 weights) and the 68M lineage in [ZZASDF Vietnamese ASR](zzasdf-viet-asr.md) (**Synthesis**: map by repo id).
- Only four converted repos are listed with licenses: ViBERT-capu ONNX (CC-BY-SA-4.0), CAM++ 3D-Speaker ONNX (Apache-2.0), Pyannote Community-1 ONNX split (CC-BY-4.0), Conv-TasNet ONNX (CC-BY-SA-4.0) (**Reported**; Model nguồn).[^sherpa-vi-readme]
- The README does not state ASR weight licenses; the app's MIT badge covers its code, not the models. Anyone redistributing or commercializing must check each model separately, notably the 30M checkpoint's non-commercial, no-derivatives terms recorded elsewhere in this wiki (**Synthesis**, not legal advice).[^sherpa-vi-readme]
- PyQt6 is GPL v3; closed-source commercial use needs a Qt commercial license or a swap to PySide6/LGPL (**Reported**; License).[^sherpa-vi-readme]

## Implications for voice pipelines

- A CPU-only, offline Zipformer pipeline with explicit punctuation/casing, hotword biasing and diarization is a concrete packaging example for Vietnamese transcripts, comparable to the sherpa-onnx route in [Gipformer Inference Repository](gipformer-inference-repo.md) (**Synthesis**).
- ASR encoder, decoder and joiner are kept on CPU by design, so the stated GPU gains apply to surrounding stages, not recognition (**Reported**; see the [GPU page](sherpa-vietnamese-asr-gpu-calibration.md)).[^sherpa-vi-readme]
- No evidence of chunked/streaming recognition, endpointing or partial results appears; do not use this README to claim realtime Vietnamese ASR. See [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) for the streaming criteria (**Observed** absence).[^sherpa-vi-readme]

## Relationships

- Uses [Silero VAD](silero-vad.md) for voice activity detection.
- Related to [Speaker Diarization Core ML](speaker-diarization-coreml.md): both package pyannote speaker-diarization-community-1 for on-device use, here as ONNX for Windows.
- Related to [Punctuation Restoration (base, 307M)](punctuation-restoration-base.md): a different punctuation model for the same post-ASR step; ViBERT-capu here is Vietnamese-specific with casing.
- Uses [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md) as its small ASR mode.

## Coverage and limits

Only the README capture was inspected, statically. Not inspected: the repository code, `LICENSE`, release zips, the four Hugging Face model repos, the pinned-SHA256 script, ROVER implementation details, hotword mechanics, DNSMOS/NaturalTurn thresholds, the cited papers, and the badge images. Nothing was installed or run; no WER, speed, memory, or diarization-error figures exist in the source, so none are recorded. The README does not define ROVER beyond the mode name; the usual meaning is system-output voting, but that is an assumption (**Unverified**). No sensitive values are recorded.

[^sherpa-vi-readme]: [README capture](../raw/sherpa-vietnamese-asr.md) — intro and badges (version 2.6.3); Gói phát hành; Cách chạy bản phát hành; Tính năng chính; Công nghệ; PWA offline; Yêu cầu; Chạy từ source; Build; Model nguồn; Ghi nhận (Thư viện & Models, Papers); License.
