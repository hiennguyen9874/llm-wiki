---
type: Concept
title: RealtimeSTT
description: Python speech-to-text library with VAD-gated recording, selectable streaming/offline engines, wake-word activation, and a packaged authenticated production server.
tags: [stt, vad, streaming, library, server]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T12:00:00Z }
stale_after: 2027-10-06
sources:
  - id: realtimestt-readme
    resource: ../raw/RealtimeSTT.md
    kind: documentation
    title: RealtimeSTT README
  - id: realtimevoicechat-readme
    resource: ../raw/RealtimeVoiceChat.md
    kind: documentation
    title: Real-Time AI Voice Chat README
---

RealtimeSTT by Kolja Beigel is an MIT-licensed Python speech-to-text library that gates microphone or fed-audio capture with voice activity detection, produces both realtime hypotheses and a final transcript through selectable engines, and optionally adds wake-word activation and a packaged FastAPI production server (**Reported**).[^realtimestt-readme]

## Identity and scope

- Purpose: assistants, dictation tools, browser streaming servers, and prototypes needing speech-to-text in a few lines of code; default general-purpose path uses `faster_whisper`, with other engines enabled through install extras when optional dependencies and models are present (**Reported**).[^realtimestt-readme]
- Author Kolja Beigel; license MIT; CI release targets Python 3.11 and 3.12, with Python 3.13+ explicitly not a release target until dependency and CI gates exist (**Reported**).[^realtimestt-readme]
- Platform prerequisites: Linux needs `python3-dev` plus `portaudio19-dev`; macOS needs `brew install portaudio`; CUDA and optional engine stacks deferred to `docs/installation.md` (**Reported**).[^realtimestt-readme]

## Recommended engine profiles

- CUDA/GPU: keep the established `faster_whisper` CUDA setup as the recommended general-purpose GPU path (**Reported**).[^realtimestt-readme]
- CPU production streaming on Linux x86-64: strongly recommended pairing is `sherpa-onnx-nemotron-3.5-asr-streaming-0.6b-560ms-int8` for fast replaceable realtime text plus `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` for the single authoritative final transcript; Nemotron processes only new audio frames during the turn and Parakeet refines the complete turn once at finalization, avoiding repeated retranscription of a growing buffer (**Reported**).[^realtimestt-readme]
- Install fence for that CPU stack: `python -m pip install "RealtimeSTT[server,sherpa-onnx]"` then `stt-install-sherpa-models --root ./models/sherpa-onnx --model all`; exact pinned directories deferred to `RealtimeSTT_server/PRODUCTION_SERVER.md` (**Reported**).[^realtimestt-readme]
- Kroko/Banafo native integration: `kroko_onnx` local streaming ASR engine with public Community models for testing and commercial models for production licensing; install fence `pip install "RealtimeSTT[kroko-builder,silero-onnx-cpu]"` then `stt-install-kroko --build`, where the `silero-onnx-cpu` extra supplies a local VAD backend for recorder smoke tests and live microphone use (**Reported**).[^realtimestt-readme]
- Full engine reference set named in the README: faster-whisper, whisper.cpp, OpenAI Whisper, Moonshine, sherpa-onnx, Kroko-ONNX, Parakeet NeMo, Meta Omnilingual ASR, Granite/Qwen Transformers engines, Cohere Transcribe, and FunASR, each with its own `docs/engines/*.md` guide (**Reported**).[^realtimestt-readme]

## Recorder usage

- Basic microphone turn: `with AudioToTextRecorder() as recorder: recorder.text()` waits for speech, stops after the detected utterance, and prints the final transcript; scripts should use the `if __name__ == "__main__":` guard because model work uses multiprocessing, especially on Windows (**Reported**).[^realtimestt-readme]
- Continuous dictation: pass a callback to `text()` (e.g. `recorder.text(process_text)` in a `while True` loop) so transcription completes asynchronously while listening continues (**Reported**).[^realtimestt-readme]
- External audio: set `use_microphone=False` and feed 16-bit mono PCM chunks at 16 kHz via `recorder.feed_audio(...)`, passing `original_sample_rate` for resampling; close with `recorder.shutdown()` (**Reported**).[^realtimestt-readme]
- Full `AudioToTextRecorder` parameter reference deferred to `docs/configuration.md`, covering model/engine selection, realtime transcription, VAD timing, wake words, callbacks, external audio, logging, and executor injection (**Reported**).[^realtimestt-readme]

## Capabilities

- Voice activity detection with WebRTC VAD and Silero VAD; final plus realtime transcription with selectable engines; wake-word activation via Porcupine or OpenWakeWord (**Reported**).[^realtimestt-readme]
- Input paths: direct microphone or application-fed chunks; event callbacks for recording, VAD, realtime text, transcription, and wake-word state (**Reported**).[^realtimestt-readme]
- Complete user-guide set named: quick-start, installation, configuration, transcription engines, custom transcription engines (public base class, executor integration, streaming sessions, contribution guide), wake words, external audio, testing (fast unit versus opt-in golden/model tests), test scripts under `tests/`, FastAPI server, production server, troubleshooting, and engine licenses (**Reported**).[^realtimestt-readme]

## Production server

- Packaged optional install binds to loopback by default and exposes versioned health, readiness, capabilities, raw-PCM final transcription, and ordered streaming WebSocket endpoints; the interactive browser reference app stays in `example_fastapi_server` for source checkouts (**Reported**).[^realtimestt-readme]
- Remote-access rule: direct non-loopback binds require both a bearer token and Uvicorn TLS certificate/key files; reverse-proxy deployments keep the server on loopback and terminate TLS at the proxy (**Reported**).[^realtimestt-readme]
- Start fence: `python -m pip install "RealtimeSTT[server,faster-whisper]"` then `stt-server-production --host 127.0.0.1 --port 8010`; CPU INT8 deployments install `RealtimeSTT[server,sherpa-onnx]` plus both pinned model bundles into persistent storage before following the server recipe (**Reported**).[^realtimestt-readme]
- Server turn-state note: the versioned production WebSocket path owns its turn state and does not derive finalization from recorder VAD, so production startup needs no interactive Torch Hub download; the `server` extra still includes the local Silero ONNX VAD runtime used by legacy recorder-backed paths (**Reported**).[^realtimestt-readme]
- Authoritative recipe deferred to `RealtimeSTT_server/PRODUCTION_SERVER.md` (authenticated HTTP/WebSocket deployment, limits, pinned model directories); browser-server UI/protocol/metrics deferred to `docs/fastapi-server.md` (**Reported**).[^realtimestt-readme]

## Relationships

- Uses [Silero VAD](silero-vad.md): WebRTC/Silero gating plus the `silero-onnx-cpu` extra supply the VAD backend for recorder tests and live-microphone use; consult that page for model footprint, runtimes, and sampling-rate scope (**Synthesis**).[^realtimestt-readme]
- Uses [Faster-Whisper](faster-whisper.md): the default general-purpose engine path is `faster_whisper`; consult that page for the CTranslate2 runtime, batched inference, quantization, VAD filter, and benchmark figures (**Synthesis**).[^realtimestt-readme]
- Uses [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md): RealtimeSTT's recommended CPU live-hypothesis bundle is the sherpa-onnx INT8 packaging of this streaming model family; consult that page for chunk/latency operating points and FLEURS figures (**Synthesis**).[^realtimestt-readme]
- Uses [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): RealtimeSTT's recommended CPU authoritative-final bundle is the sherpa-onnx INT8 packaging of this offline TDT model; consult that page for multilingual coverage and WER tables (**Synthesis**).[^realtimestt-readme]
- Uses [Qwen3-ASR family](qwen3-asr-family.md), [Fun-ASR-Nano-2512](fun-asr-nano-2512.md), and [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md): these correspond to the Granite/Qwen Transformers, FunASR, and Cohere engine options RealtimeSTT lists; compare those pages when selecting a non-default engine (**Synthesis**).[^realtimestt-readme]
- Used by [RealtimeVoiceChat](realtime-voice-chat.md): that cascaded STT–LLM–TTS pipeline names `RealtimeSTT` as its transcription stage with browser WebSocket capture, Ollama/OpenAI reasoning, `RealtimeTTS` synthesis, and interruption support (**Reported**).[^realtimevoicechat-readme]
- Complements [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md): that draft's checklist (first stable text, partial stability, endpointing, barge-in, per-turn logs) is the evaluation lens for RealtimeSTT's realtime-plus-final, VAD-gated, callback-driven design (**Synthesis**).[^realtimestt-readme]

## Coverage and limits

- Source inspected statically only; no `pip install`, model download, microphone capture, server launch, or WebSocket session was executed, and no latency or accuracy claim was reproduced (**Synthesis**).[^realtimestt-readme]
- Referenced but unfetched and absent from `raw/`: `docs/*.md` guides, `docs/engines/*.md` references, `RealtimeSTT_server/PRODUCTION_SERVER.md`, `tests/realtimestt_test.py` demo code, `example_fastapi_server`, install extras' dependency closures, and pinned sherpa-onnx model bundles; all install, Python, and server fences above are transcribed, not executed (**Synthesis**).[^realtimestt-readme]
- All capability, compatibility, performance, and recommendation claims are source assertions without independent verification in this wiki; engine recommendations and install/API details carry `stale_after: 2027-10-06` per the `stt`/`vad` domain rules (**Synthesis**).[^realtimestt-readme]

[^realtimestt-readme]: [RealtimeSTT README](../raw/RealtimeSTT.md) — locators: intro (`faster_whisper` default path, install extras); `Recommended Engine Profiles` (CUDA `faster_whisper`; CPU `sherpa-onnx-nemotron-3.5-asr-streaming-0.6b-560ms-int8` + `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` pairing and rationale; `RealtimeSTT[server,sherpa-onnx]` + `stt-install-sherpa-models` fence; `PRODUCTION_SERVER.md` pointer); `Featured Integration: Kroko/Banafo ASR` (`kroko_onnx`, Community vs commercial models, `kroko-builder,silero-onnx-cpu` + `stt-install-kroko` fence, engine/docs links); `Install` (Python 3.11/3.12 matrix, 3.13 exclusion, `RealtimeSTT[faster-whisper]` fence, PortAudio fences, `docs/installation.md` pointer); `Microphone Example`, `Automatic Recording Loop`, `External Audio` (`AudioToTextRecorder`, `__main__` guard, `text()` callback loop, `use_microphone=False` + `feed_audio(original_sample_rate=16000)` + `shutdown()` fences); `Configuration Reference`; `Features` (WebRTC/Silero VAD, final+realtime engines, Porcupine/OpenWakeWord, mic/fed audio, callbacks, packaged FastAPI server properties, browser reference app); `Documentation` (14 guide bullets + 11 engine-specific bullets); `Production Server` (loopback default, endpoint list, token+TLS rule, proxy guidance, `server,faster-whisper` + `stt-server-production` fence, CPU INT8 pairing + model-install fence, Silero ONNX VAD note, turn-state/Torch-Hub note, recipe pointers); `Contributing`, `License` (MIT), `Author` (Kolja Beigel).

[^realtimevoicechat-readme]: [Real-Time AI Voice Chat README](../raw/RealtimeVoiceChat.md) — locators: `What's Under the Hood?` 7-step pipeline (browser capture, WebSocket chunks, `RealtimeSTT`, LLM, `RealtimeTTS`, return playback, interrupt); `Key Features` (Ollama/OpenAI via `llm_module.py`, interruption support).
