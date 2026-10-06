---
type: Concept
title: Speaches
description: OpenAI API-compatible self-hosted server for streaming faster-whisper transcription and Piper/Kokoro speech synthesis with dynamic model loading, Docker deployment, and a Realtime API.
tags: [stt, tts, server, streaming, whisper-compatible]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T17:40:00Z }
stale_after: 2027-10-06
sources:
  - id: speaches-readme
    resource: ../raw/speaches.md
    kind: documentation
    title: Speaches README (overview excerpt)
---

Speaches is an OpenAI API-compatible self-hosted server for streaming transcription, translation, and speech generation: speech-to-text runs on faster-whisper, text-to-speech on Piper and Kokoro, and the project positions itself as Ollama-style dynamic model management for TTS/STT models, with per-request model loading and offloading, SSE streaming transcription, GPU and CPU support, and Docker deployment (**Reported**).[^speaches-readme]

## Identity and positioning

- OpenAI API-compatible server: tools and SDKs built for OpenAI's API are stated to work with Speaches (**Reported**).[^speaches-readme]
- Self-declared goal is to be Ollama, but for TTS/STT models: models load automatically per request and unload after a period of inactivity (**Reported**).[^speaches-readme]
- Canonical documentation lives at `speaches.ai` (installation, usage, Realtime API, configuration pages), all linked but not captured in this source (**Synthesis**).[^speaches-readme]

## Engines

- STT is powered by faster-whisper; see [Faster-Whisper](faster-whisper.md) for the engine's quantization, VAD filtering, and benchmark detail (**Reported**).[^speaches-readme]
- TTS is served via Piper models and Kokoro (`hexgrad/Kokoro-82M`); Kokoro is described in the source as ranked number one in the TTS Arena (**Reported**).[^speaches-readme]

## Features (as listed)

- Audio generation through the chat-completions endpoint, covering three directions: text-in/audio-out spoken summaries, audio-in/text-out sentiment analysis, and async audio-in/audio-out speech-to-speech interaction with a model (**Reported**).[^speaches-readme]
- Streaming support: transcription is sent via SSE as audio is transcribed, without waiting for the full audio to finish (**Reported**).[^speaches-readme]
- Dynamic model loading and offloading driven by the request's model choice, with unload after inactivity (**Reported**).[^speaches-readme]
- GPU and CPU support; deployable via Docker and Docker Compose; a Realtime API; and stated high configurability, each pointing to `speaches.ai` pages not captured here (**Reported**).[^speaches-readme]

## Demos and gaps

- Demos section links a Realtime API video and a speech-generation video, with an aside apologizing for audible breathing in the former; neither video's content is transcribed in the source (**Reported**).[^speaches-readme]
- The streaming-transcription demo is an explicit `TODO` in the source, so no streaming demo evidence is available from this ingest (**Reported**).[^speaches-readme]

## Relationships

- Uses [Faster-Whisper](faster-whisper.md): this server's STT backend; that page already names Speaches as a downstream OpenAI-compatible serving option and now links here (**Synthesis**).[^speaches-readme]
- Compare self-hosted serving with [Parakeet ASR Server](parakeet-asr-server.md) (Go-based Whisper-compatible server for a fixed Parakeet TDT checkpoint) and [WhisperLiveKit](whisperlivekit.md) (streaming STT/translation pipeline with diarization): Speaches differentiates by combining faster-whisper STT with Piper/Kokoro TTS plus a Realtime API behind one OpenAI-compatible surface (**Synthesis**).[^speaches-readme]
- Compare client-side realtime use with [RealtimeSTT](realtimestt.md): that page's VAD-gated Python library and server address the capture-and-transcribe half, while Speaches addresses the serve-STT-and-TTS half (**Synthesis**).[^speaches-readme]
- For GGUF-packaged edge alternatives to the server-hosted Kokoro and Piper weights, see [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md), which rows `Kokoro-82M-GGUF` and `Piper-TTS-GGUF` (**Synthesis**).[^speaches-readme]

## Coverage and limits

- Source inspected statically only; no server install, model download, transcription, synthesis, streaming, Docker run, or Realtime API call was executed (**Synthesis**).[^speaches-readme]
- Referenced but unfetched and absent from `raw/`: all `speaches.ai` pages (installation, usage, Realtime API, configuration), the faster-whisper, Piper, and Kokoro implementations and weights, the TTS Arena ranking page, both demo videos, and the missing streaming-transcription demo; install, run, and API behavior above is transcribed, not executed (**Synthesis**).[^speaches-readme]
- The source states no version, revision, license, model list, API surface detail, latency figure, or benchmark; all capability and ranking claims are source assertions without independent verification, and API/deployment detail carries `stale_after: 2027-10-06` per the `stt`/`tts` domain rules (**Synthesis**).[^speaches-readme]

[^speaches-readme]: [Speaches](../raw/speaches.md) — locators: title plus intro paragraph (OpenAI API-compatible server; streaming transcription, translation, speech generation; faster-whisper STT; Piper plus `hexgrad/Kokoro-82M` TTS; Ollama-for-TTS/STT positioning; `speaches.ai` docs link); `Features` list (OpenAI-compat claim; chat-completions audio-generation bullets for text-in/audio-out summary, audio-in/text-out sentiment, async audio-in/audio-out; SSE streaming sentence; dynamic load/offload with inactivity unload; Kokoro TTS Arena number-one note; GPU/CPU, Docker Compose/Docker, Realtime API, configurability links); `Demos` (Realtime API video link with breathing aside; Streaming Transcription `TODO`; Speech Generation video link).
