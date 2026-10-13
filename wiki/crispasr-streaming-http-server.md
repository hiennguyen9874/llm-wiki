---
type: Concept
title: CrispASR Streaming and HTTP Server
description: CrispASR's live and streaming modes (sliding-window streaming, microphone, live translation, progressive flush) and its OpenAI-compatible HTTP server for ASR and TTS, including the serialized-inference default and unsupported batched multi-stream inference.
tags: [pipeline, streaming, server, openai-compatible, asr, tts, latency]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:45:00Z }
stale_after: 2027-10-13
sources:
  - id: crispasr-readme
    resource: ../raw/CrispASR.md
    kind: documentation
    title: CrispASR README
---

CrispASR offers live use through `--stream`, `--mic`, `--live`, and `--live-translate`, plus progressive output for non-Whisper backends. Its OpenAI-compatible HTTP server exposes ASR and, for any loaded TTS backend, speech synthesis. The README says inference on one loaded model is serialized by default, and that batched multi-stream inference is not supported (**Reported**).[^crispasr-readme]

## Live and streaming modes

- The streaming section lists `--stream`, `--mic`, and `--live`, with sliding-window chunking and per-token confidence. Microphone example: `crispasr --mic -m model.gguf` (**Reported**).[^crispasr-readme]
- `--live-translate` gives the transcript and its translation, sentence by sentence, using m2m100 or a translation LLM such as Hy-MT2. Example: `crispasr --live-translate -l de --tr-tl en -m auto --backend parakeet --translate-model hy-mt2` (**Reported**).[^crispasr-readme]
- Progressive output: by default non-Whisper backends buffer all segments and print at the end. `--flush-after 1` prints each SRT entry as its VAD segment finishes, which suits subtitle players (**Reported**).[^crispasr-readme]
- `-pp` or `--print-progress` shows per-slice progress for every backend. Whisper reports encoder-level progress instead (**Reported**).[^crispasr-readme]

### Streaming mechanisms named in the ASR table

The matrix marks streaming ✔ for every ASR column, but the README names specific mechanisms for only a few backends (**Reported**).[^crispasr-readme]

- **voxtral4b:** native incremental encoder; the README gives about 2× realtime feed and an open target for sub-second token latency (**Reported**).[^crispasr-readme]
- **xasr:** streaming Zipformer2 transducer, 160, 480, 960, or 1920 ms chunks, realtime WebSocket session (**Reported**).[^crispasr-readme]
- **confucius4-r2t2:** append-only realtime session with prefix rollback (**Reported**).[^crispasr-readme]
- **vibevoice-streaming:** persistent-KV 2.93 s chunks with 0.53 s lookahead (**Reported**).[^crispasr-readme]
- **omniasr-llm (Unlimited):** 15 s segment protocol with unlimited audio (**Reported**).[^crispasr-readme]
- **moonshine-streaming:** sliding-window encoder with autoregressive decoder (**Reported**).[^crispasr-readme]
- **hikari:** one token, or WAIT, per 80 ms; simultaneous English-to-DE/JA/RU translation, and `--stream` emits while the speaker talks (**Reported**).[^crispasr-readme]

## HTTP server

- Start: `crispasr --server -m model.gguf --port 8080`. ASR is then available at `POST /v1/audio/transcriptions`, OpenAI-compatible, with the audio sent as a multipart `file` (**Reported**).[^crispasr-readme]
- TTS: `POST /v1/audio/speech` and `/v1/voices` appear automatically for any loaded backend with the TTS capability. Requests can set voice, speed, and instructions per call, and `language` and `source_lang` fields control language (**Reported**).[^crispasr-readme]
- Voice example: `crispasr --server --backend qwen3-tts-customvoice -m auto --voice-dir ./voices --port 8080`, then a JSON request with `"input"` and `"voice"` fields (**Reported**).[^crispasr-readme]
- Other listed features: CORS, long-form sentence chunking for TTS, API keys through the `CRISPASR_API_KEYS` environment variable, Docker Compose, and prebuilt CUDA images (**Reported**).[^crispasr-readme]
- `response_format=diarized_json` returns speaker-labelled output. See [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) (**Reported**).[^crispasr-readme]

## Concurrency

- The server accepts concurrent requests but serializes inference on one model by default (**Reported**).[^crispasr-readme]
- `--server-workers N` runs N model instances, so pure-ASR requests can run in parallel (**Reported**).[^crispasr-readme]
- For bulk throughput the README recommends process fan-out (`xargs -P` or GNU parallel), or N replicas behind a load balancer (**Reported**).[^crispasr-readme]
- Not supported: batched multi-stream inference and PagedAttention. The README gives the reasons in `docs/concurrency.md`, which was not captured (**Reported**).[^crispasr-readme]

## Coverage and limits

- `docs/streaming.md`, `docs/server.md`, `docs/concurrency.md`, and `docs/bindings.md` were not captured, so per-backend streaming behavior, server auth details, and binding APIs are unexamined (**Synthesis**).[^crispasr-readme]
- The matrix's streaming ✔ does not separate native from windowed streaming. The README's own description of streaming is sliding-window chunking (**Synthesis**).[^crispasr-readme]
- Latency figures (2× realtime feed, 2.93 s chunks, 80 ms token steps) are README assertions. No server was started and no request was sent (**Synthesis**).[^crispasr-readme]

## Relationships

- Compared with: [Parakeet ASR Server](parakeet-asr-server.md), a Go server that also exposes an OpenAI Whisper-compatible REST and SSE API for Parakeet (**Synthesis**).
- Relates to: [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md), which describes remote-delegation contracts that call OpenAI-compatible STT and TTS endpoints (**Synthesis**).
- Depends on: [CrispASR VAD and Language Identification](crispasr-vad-language-id.md) for the VAD segmentation that drives progressive flush (**Synthesis**).
- Part of: [CrispASR](crispasr.md) (**Synthesis**).

[^crispasr-readme]: [CrispASR README](../raw/CrispASR.md) — locators: `Streaming, TTS, and HTTP server` (streaming, TTS, and server bullets; `--mic`, `--live-translate`, `/v1/audio/transcriptions`, and `/v1/audio/speech` quick-start block; CosyVoice3 note); `Progressive subtitle output` (`--flush-after 1`); `CPU performance tips` (`-pp`, `--flush-after`); `Supported backends` ASR table rows for voxtral4b, xasr, confucius4-r2t2, vibevoice-streaming, omniasr-llm (Unlimited), moonshine-streaming, and hikari; `Which backend should I pick?` (realtime streaming row); `Feature matrix` (Streaming row); `CLI reference` table (`--vad`, `-ck`); `Quick start` Voxtral and TTS HTTP notes.
