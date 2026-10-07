---
type: Concept
title: Parakeet ASR Server
description: Go-based self-hosted ASR server serving NVIDIA Parakeet TDT 0.6B via ONNX Runtime behind an OpenAI Whisper-compatible REST/SSE API, with CPU/CUDA images, ffmpeg audio conversion, and silence-aware long-audio chunking.
tags: [stt, asr, parakeet, server, onnx, whisper-compatible]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:37:10Z }
stale_after: 2027-10-06
sources:
  - id: parakeet-readme
    resource: ../raw/parakeet.md
    kind: documentation
    title: Parakeet ASR server README (achetronic/parakeet)
---

Parakeet ASR Server (`achetronic/parakeet`) is a lightweight, production-ready self-hosted speech-recognition service written in Go with no Python runtime dependency: it runs NVIDIA's Parakeet TDT 0.6B model through ONNX Runtime on CPU (or CUDA) and exposes an OpenAI Whisper-compatible REST API with SSE streaming, optional API-key auth, and ffmpeg-based audio conversion, making it a drop-in replacement for Whisper-API clients (**Reported**).[^parakeet-readme]

## Identity and model lineage

- Repository `achetronic/parakeet`; Go service; inference via ONNX Runtime over the [istupakov ONNX conversion](https://huggingface.co/istupakov/parakeet-tdt-0.6b-v3-onnx) of [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) (**Reported**).[^parakeet-readme]
- Licenses: code MIT, Parakeet model CC-BY-4.0 (**Reported**).[^parakeet-readme]
- Underlying model serves [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) weights; prefer that page for model training data, multilingual benchmarks, and NeMo/Transformers inference, and this page for self-hosted Go-server deployment and operations (**Synthesis**).[^parakeet-readme]

## Architecture (as bundled)

- Encoder: Conformer-based, 1024-dimensional output, 128-dimensional mel filterbank input with 8x temporal subsampling; decoder: Token-and-Duration Transducer (TDT) with 2-layer LSTM (640-dim hidden) jointly predicting tokens and frame-advance durations; vocabulary: 8193 SentencePiece tokens including blank (**Reported**).[^parakeet-readme]
- Non-autoregressive parallel TDT decoding is stated to be faster than Whisper-style autoregressive decoding at competitive accuracy; TDT timestamps are duration-based versus Whisper's attention-based alignment (**Reported**).[^parakeet-readme]
- Source-stated contrast with OpenAI Whisper: 0.6B params vs 0.04B–1.5B; NeMo ASR training data vs 680K hours web audio; accuracy/speed balance vs multilingual robustness (**Reported**).[^parakeet-readme]

## Model files and footprint

- Required files in the models directory: `config.json` (97 B), `vocab.txt` (94 KB), `nemo128.onnx` (140 KB), `encoder-model.int8.onnx` (652 MB), `decoder_joint-model.int8.onnx` (18 MB), plus optional `silero_vad.onnx` (2.3 MB, Silero VAD v6.2.1, MIT, checksum-verified by `make models`, long-audio chunking only) (**Reported**).[^parakeet-readme]
- Full-precision alternative: `encoder-model.onnx` (+ `.data`, 2.5 GB total) and `decoder_joint-model.onnx` (72 MB); int8 totals ~670 MB disk / ~2 GB inference RAM versus ~6 GB for fp32 (**Reported**).[^parakeet-readme]
- Each concurrent inference worker costs ~670 MB RAM for int8; default 4 workers (**Reported**).[^parakeet-readme]

## Requirements and installation

- Runtime requires ONNX Runtime 1.25.x or later (`ONNXRUNTIME_LIB` override for non-standard paths); ffmpeg optional (non-WAV conversion); build requires Go 1.25+ (**Reported**).[^parakeet-readme]
- Release binary: download `parakeet-linux-amd64`, `make models` (int8, recommended) or `make models-fp32`, then `./parakeet -port 5092 -models ./models`; source: clone, `make models`, `make build`, `./bin/parakeet` (**Reported**).[^parakeet-readme]
- Docker: `ghcr.io/achetronic/parakeet:latest` ships ONNX Runtime, models, and ffmpeg (`docker run -d --name parakeet -p 5092:5092 ...`); compose example sets `PARAKEET_API_KEY`/`PARAKEET_WORKERS` with a `/health` curl healthcheck (**Reported**).[^parakeet-readme]
- CUDA image (`:latest-cuda`, linux/amd64 only, fp32 default): needs NVIDIA drivers + Container Toolkit, `--gpus all`, GPU enabled by default (`-gpu cuda`); non-Docker GPU selection via `-gpu cuda -gpu-device 0` or `PARAKEET_GPU`/`PARAKEET_GPU_DEVICE`; a failed CUDA provider fails startup loudly rather than silently falling back to CPU (**Reported**).[^parakeet-readme]

## Configuration

- CLI flags with env equivalents (`PARAKEET_` + uppercased flag, dashes→underscores); precedence CLI flag > env var > default; invalid env values ignored with a warning (**Reported**).[^parakeet-readme]
- Flags: `-port` (5092), `-models` (`./models`), `-log-level` (info), `-log-format` (text), `-workers` (4), `-ffmpeg` (true), `-ffmpeg-path` (empty = PATH), `-ffmpeg-timeout` (60s), `-gpu` (cpu), `-gpu-device` (0), `-long-audio` (false), `-chunk-seconds` (300), `-chunk-overlap-seconds` (15), `-disable-vad-based-chunking`/`-disable-mel-based-chunking` (false), `-vad-model-path` (`<models>/silero_vad.onnx`) (**Reported**).[^parakeet-readme]
- Flag-less variables: `ONNXRUNTIME_LIB` (auto-detected path) and `PARAKEET_API_KEY` (empty = auth disabled) (**Reported**).[^parakeet-readme]
- Logging via `slog` with text/JSON formats and configurable level; Docker images bake operational defaults as `PARAKEET_*` env vars (**Reported**).[^parakeet-readme]

## Long-audio handling

- Encoder single-pass limit is 400 s: longer input is rejected with an error by default; `-long-audio` splits into overlapping windows (`-chunk-seconds` 300, overlap 15), transcribes each, and stitches while dropping overlap to avoid seam duplication (**Reported**).[^parakeet-readme]
- Chunk-boundary cascade inside each overlap: Silero VAD picks the center of the longest silence → mel-energy quietest point → midpoint fallback; a missing VAD model warns once and falls back; an always-on seam safety net removes duplicate/colliding tokens at each join (**Reported**).[^parakeet-readme]
- GPU VRAM bound: encoder runs whole-file single pass, so very long inputs (~1 h+ on 24 GB) can OOM; mitigation is pre-segmenting (e.g. `ffmpeg -i in.wav -f segment -segment_time 300 -ar 16000 -ac 1 chunk_%03d.wav`) or using a CPU image bounded by system RAM (**Reported**).[^parakeet-readme]

## API reference

- `POST /v1/audio/transcriptions` (multipart): `file` required (WAV native; MP3/OGG/WebM/FLAC/M4A/AAC/Opus via ffmpeg; 25 MB max); `language` (default en), `response_format` (json, text, srt, vtt, verbose_json); `model`, `prompt`, `temperature` accepted but ignored; `stream=true` selects SSE (**Reported**).[^parakeet-readme]
- Default JSON returns `{"text": ...}`; verbose_json adds `task`, `language`, `duration`, and `segments[]` (`id`, `start`, `end`, `text`) (**Reported**).[^parakeet-readme]
- **Streaming boundary:** the complete audio file is uploaded before the server emits incremental decoded text; SSE output streaming is not native continuous microphone/audio-input streaming (**Observed** wording in README; capability interpretation **Synthesis**).[^parakeet-readme]
- Streaming follows OpenAI's streaming transcription protocol over `text/event-stream`: `transcript.text.delta` events per decoded chunk, then one `transcript.text.done` with the full text; compatible with clients such as Wyoming OpenAI for Home Assistant (**Reported**).[^parakeet-readme]
- `GET /v1/models` returns `parakeet-tdt-0.6b` plus `whisper-1` alias; `GET /health` returns `{"status": "ok"}` and is always unauthenticated (**Reported**).[^parakeet-readme]
- Auth: when `PARAKEET_API_KEY` is set, all `/v1/*` endpoints require `Authorization: Bearer <key>` (**Reported**).[^parakeet-readme]
- Audio is detected by content (magic bytes), not filename extension, so extensionless uploads work (**Reported**).[^parakeet-readme]

## Audio conversion and troubleshooting

- Non-WAV input is transcoded on the fly to 16 kHz mono WAV when ffmpeg is present; without ffmpeg only WAV is accepted and other formats get HTTP 400; startup logs either `ffmpeg conversion enabled binary=... timeout=...` or `ffmpeg not found, non-WAV inputs will be rejected` (**Reported**).[^parakeet-readme]
- `400 Unsupported or malformed audio` remedy order: install ffmpeg / set `-ffmpeg-path`, check startup log line, or convert client-side (`ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav`) (**Reported**).[^parakeet-readme]
- `ONNX Runtime library not found`: install it or export `ONNXRUNTIME_LIB=/path/to/libonnxruntime.so`; missing encoder model: `make models`; OOM: prefer int8 over fp32 (**Reported**).[^parakeet-readme]
- Multilingual support stated as English plus 25+ languages; supported response formats json/text/srt/vtt (**Reported**).[^parakeet-readme]

## Development targets

- `make build/run/run-dev/clean`, `fmt/vet/lint/test/test-coverage`, `models/models-int8/models-fp32`, `docker-build-int8/docker-build-fp32/docker-build-cuda` + matching `docker-run-*`, `release` for all platforms, `help` (**Reported**).[^parakeet-readme]

## Relationships

- Compared in [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md): this is an API server over fixed Parakeet weights, not a general inference runtime; full-upload SSE belongs to a different streaming class from microphone WebSocket sessions (**Synthesis**).[^parakeet-readme]

- Uses [Silero VAD](silero-vad.md): optional `silero_vad.onnx` (2.3 MB) supplies the VAD-based chunk-boundary stage with mel-energy and midpoint fallbacks; consult that page for model footprint, runtimes, and sampling-rate scope (**Synthesis**).[^parakeet-readme]
- Uses [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): this server is a deployment vehicle for those weights via the istupakov ONNX conversion; model-level accuracy, language, and training questions belong on that page (**Synthesis**).[^parakeet-readme]
- Compare self-hosted serving with [Faster-Whisper](faster-whisper.md) (CTranslate2 Whisper reimplementation), [RealtimeSTT](realtimestt.md) (Python VAD-gated library + server), and [WhisperLiveKit](whisperlivekit.md) (streaming pipeline with diarization): this page's differentiator is Go-based Whisper-compatible batch/SSE transcription of a fixed 0.6B TDT checkpoint with optional CUDA and long-audio chunking (**Synthesis**).[^parakeet-readme]
- Complements [Community-Reported Noisy On-Premise STT Selection](community-noisy-call-stt.md): that page's Parakeet-vs-Whisper anecdotes now have a concrete self-hosted deployment target on this page (**Synthesis**).[^parakeet-readme]

## Coverage and limits

- Source inspected statically only; no checkout, build, model download, server run, or transcription executed, and no latency/accuracy figure reproduced (**Synthesis**).[^parakeet-readme]
- Referenced but unfetched and absent from `raw/`: `docs/img/parakeet.png` header image (decorative, excluded), upstream model/ONNX/VAD repos, ONNX Runtime release tarballs, Docker/CUDA images, linked docs (SSE spec, Container Toolkit); all install/run/curl fences transcribed, not executed (**Synthesis**).[^parakeet-readme]
- All capability, sizing, default, and behavior claims are source assertions without independent verification; API surface and release/install details carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^parakeet-readme]

[^parakeet-readme]: [Parakeet ASR server README](../raw/parakeet.md) — locators: header (Go server, Parakeet TDT 0.6B via ONNX Runtime, Whisper-compatible API); `Overview` (feature list: REST API, optional API-key auth, SSE `transcript.text.delta/done`, CPU ONNX Runtime, no Python, `slog` text/JSON, json/text/srt/vtt formats, 25+ languages, quantized models, ffmpeg conversion); `Model Architecture` (Conformer-1024 encoder, 128-dim mel, 8x subsampling, TDT 2-layer LSTM-640, SentencePiece-8193, int8 670 MB disk / 2 GB RAM); `Parakeet vs Whisper` table (architecture, decoding, speed, size 0.6B vs 0.04–1.5B, training data, focus, timestamps); `Requirements` + `Installing ONNX Runtime` (1.25.x, ffmpeg optional, Go 1.25, per-distro fences, `ONNXRUNTIME_LIB`, `ldconfig -p` verify); `Installation` (binary/source/Docker fences, `make models` vs `models-fp32`, compose with `PARAKEET_API_KEY`/`PARAKEET_WORKERS` + `/health` healthcheck); `GPU Inference (CUDA)` (`-cuda` tag, Toolkit prereqs, amd64-only, `-gpu`/`-gpu-device` flags, `PARAKEET_GPU*` env, fail-fast, fp32 default, VRAM/audio-length note with `ffmpeg -segment_time 300` fence); `Command Line Flags` table (all 16 flags + defaults) and `Examples` fences; `Long Audio` (400 s limit, `-long-audio` windowing/stitching, VAD→mel→midpoint cascade, seam dedup, disable flags); `Environment Variables` (prefix rule, CLI > env > default precedence, invalid-env warning, `ONNXRUNTIME_LIB`/`PARAKEET_API_KEY` table); `Model Files` table (6 files + sizes, fp32 pair, Silero v6.2.1 note); `API Reference` (auth header, transcription param table incl. 25 MB max and ignored `model/prompt/temperature`, json + verbose_json fences, SSE `stream=true` protocol with full-audio-upload sentence plus delta/done fence, `/v1/models` pair, `/health`); `Available Make Targets` + `Running Tests`; `Troubleshooting` (library path, `make models`, int8-vs-fp32 2 GB/6 GB RAM, magic-byte detection, 400-error ffmpeg remedies, startup log lines, client-side `ffmpeg -ar 16000 -ac 1` fence); `License` (MIT code, CC-BY-4.0 model) + `Credits` (NVIDIA, istupakov).
