---
type: Concept
title: Speech-to-Speech OpenAI-Compatible STT/TTS Backends
description: Remote-delegation contracts for the HF speech-to-speech pipeline's OpenAI-compatible STT (HTTP, OpenAI Realtime, vLLM Realtime) and TTS backends, covering endpoints, request shapes, auth, setup validation, streaming modes, and cancellation limits.
tags: [stt, tts, pipeline, streaming, deployment]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T14:53:00Z }
stale_after: 2027-10-07
sources:
  - id: s2s-supporting-docs
    resource: ../raw/speech-to-speech-docs/README.md
    scope: ../raw/speech-to-speech-docs/
    kind: documentation
    revision: f9c23282a564cbe5b1f015ccb36d58e941de8520
    title: huggingface/speech-to-speech supporting docs
---

The HF [speech-to-speech pipeline](speech-to-speech-pipeline.md) can keep VAD, turns, sessions, conversation state, and response handling in-process while delegating recognition to an external `/v1/audio/transcriptions` server (`--stt openai`), pushing incremental PCM to an OpenAI-Realtime or vLLM-Realtime transcription socket (`--stt openai-realtime`, `--stt vllm-realtime`), or delegating synthesis to an external `/v1/audio/speech` server (`--tts openai`); the OpenAI-compatible HTTP backends reuse an in-memory 16 kHz mono PCM16 WAV and the `{text}` / plain-text response contract, and all remote backends are validated at startup and remain removable from the local voice loop (**Reported**).[^s2s-supporting-docs]

## OpenAI-compatible STT (`--stt openai`)

- Flow is `VAD audio -> POST /v1/audio/transcriptions`; each request uploads an in-memory mono PCM16 WAV at 16 kHz and accepts either JSON with a string `text` field or a plain-text response (**Reported**).[^s2s-supporting-docs]
- With live transcription enabled, progressive updates upload the accumulated utterance again, increasing request volume and provider usage; the `--openai_stt_response_format` adapter supports `json` and `text` (**Reported**).[^s2s-supporting-docs]
- Self-hosted vLLM path installs `vllm[audio]` in its own environment and serves a supported ASR model, for example `vllm serve Qwen/Qwen3-ASR-1.7B --port 8000`, then selects `--stt openai --openai_stt_base_url http://localhost:8000/v1 --openai_stt_model Qwen/Qwen3-ASR-1.7B`; a `/v1/models` curl checks readiness (**Reported**).[^s2s-supporting-docs]
- Hosted OpenAI path uses the Transcription API with `--openai_stt_model gpt-transcribe`; `gpt-transcribe` sends language hints in the plural `languages[]` request field and reads the first detected code from the plural `languages` response, while older models and compatible servers keep the singular `language` field (**Reported**).[^s2s-supporting-docs]
- Set `--openai_stt_api_key` when the endpoint needs bearer auth. Only when the base URL is `https://api.openai.com/v1` and the flag is omitted does the handler fall back to `OPENAI_API_KEY`; other endpoints never receive that environment credential implicitly (**Reported**).[^s2s-supporting-docs]
- Startup validation transcribes one second of synthetic silence through the configured endpoint, so endpoint, auth, model, or response-format failures prevent the realtime server from accepting sessions; failed final requests do not create LLM work and transport/HTTP errors are sanitized before reaching realtime clients (**Reported**).[^s2s-supporting-docs]
- Server-side inference cancellation is best-effort: closing the client connection does not guarantee the server stops GPU work, so stale-result filtering stays required; STT server capacity, fleet routing, and provider quotas belong to the inference service or its shared proxy, not to client-side queue bounds (**Reported**).[^s2s-supporting-docs]

## STT turn and session lifecycle

- Each pipeline delivers STT results asynchronously so HTTP work does not block session teardown; final requests for distinct turns retain their order within a pipeline and run independently of progressive work (**Reported**).[^s2s-supporting-docs]
- Each pipeline retains at most eight pending finals plus its active final request; once full, additional finals receive a sanitized `TranscriptionFailure` without uploading audio or retrying. Obsolete pending requests are removed before the limit check and accepted finals keep their order — this bounds retained utterances behind a stalled request, not server capacity (**Reported**).[^s2s-supporting-docs]
- Progressive requests are best-effort with one active per pipeline and only the latest waiting cumulative window retained; a final cancels matching active progressive work and discards its pending window, newer turn revisions invalidate older queued work and cancel older active requests, and relevance is checked before dispatch and while running (**Reported**).[^s2s-supporting-docs]
- Session end cancels active and pending work, and results/failures carry a session generation checked atomically with queue publication so old completions cannot surface after teardown or in a reused session; shutdown cancels remaining requests and joins request workers (**Reported**).[^s2s-supporting-docs]
- Cancellation stays active through connection establishment, upload, and response reads, and transport cleanup completes before a worker is reused so an old blocked upload does not delay a new session until HTTP timeout; client-side queue bounds apply per pipeline with no shared admission queue or endpoint concurrency budget (**Reported**).[^s2s-supporting-docs]

## Stateful streaming STT

- `--stt openai-realtime` and `--stt vllm-realtime` send incremental PCM over a persistent WebSocket; local VAD controls which audio is sent and when an utterance is committed, preserving pre-speech padding, trailing silence, and short-fragment merge gaps while idle microphone audio is not uploaded (**Reported**).[^s2s-supporting-docs]
- Both streaming backends forward provider partial transcripts as they arrive regardless of `--enable_live_transcription`; that flag only enables repeated whole-utterance requests for non-streaming backends (**Reported**).[^s2s-supporting-docs]
- OpenAI Realtime transcription (`--openai_realtime_stt_model gpt-live-transcribe`) uses a transcription session with `intent=transcription` and configures the model in the session rather than the WebSocket URL; hosted OpenAI requires 24 kHz PCM, so the handler resamples the pipeline's 16 kHz audio and `--openai_realtime_stt_audio_sample_rate` must stay at its `24000` default or setup fails (**Reported**).[^s2s-supporting-docs]
- vLLM Realtime transcription is experimental and uses vLLM's separate protocol at 16 kHz PCM; `--vllm_realtime_stt_model` must match a Realtime-capable identifier served by the endpoint (the default `Qwen/Qwen3-ASR-1.7B` only works when that identifier is served), e.g. `--vllm_realtime_stt_model mistralai/Voxtral-Mini-4B-Realtime-2602` against `ws://localhost:8000/v1` (**Reported**).[^s2s-supporting-docs]
- `--openai_realtime_stt_api_key` / `--vllm_realtime_stt_api_key` accept explicit bearer tokens, with `OPENAI_API_KEY` used only for the official hosted endpoint when omitted (**Reported**).[^s2s-supporting-docs]

## OpenAI-compatible TTS (`--tts openai`)

- Flow is `LLM text -> POST /v1/audio/speech -> PCM16 at 16 kHz`; the client resamples and forwards audio incrementally as the HTTP response body arrives (**Reported**).[^s2s-supporting-docs]
- vLLM-Omni serving of Qwen3-TTS keeps the installed vLLM and vLLM-Omni versions aligned (`vllm==0.24.0` plus `vllm-omni`), e.g. `vllm serve Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --deploy-config vllm_omni/deploy/qwen3_tts.yaml --omni --port 8091 --trust-remote-code --enforce-eager`, checked with `curl /v1/audio/voices` (**Reported**).[^s2s-supporting-docs]
- Selecting it uses `--tts openai --openai_tts_base_url http://localhost:8091/v1 --openai_tts_model Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice --openai_tts_voice aiden --openai_tts_sample_rate 24000 --openai_tts_stream true`; the 24 kHz Qwen3-TTS output is converted incrementally to the pipeline's mono signed-int16 16 kHz 512-sample chunks (**Reported**).[^s2s-supporting-docs]
- `--openai_tts_language` is forwarded unchanged with every speech request and is never inferred by the TTS handler; a server needing an explicit value (e.g. `English` for Qwen3-TTS) must be given it (**Reported**).[^s2s-supporting-docs]
- Standard OpenAI-compatible servers do not need the vLLM streaming extension: the default request uses the standard `stream_format=audio` field and consumes the body incrementally, while `stream=true` is a vLLM-Omni extension disabled by default and enabled with `--openai_tts_stream true` (**Reported**).[^s2s-supporting-docs]
- The client accepts raw signed PCM16 with `--openai_tts_sample_rate`, or a WAV response with `--openai_tts_stream false --openai_tts_response_format wav`; `--openai_tts_api_key` is the explicit bearer token and `OPENAI_API_KEY` is used when it is omitted (**Reported**).[^s2s-supporting-docs]
- A short synthesis request at startup validates endpoint, authentication, model, voice, request, and audio-response configuration before the Realtime server accepts sessions (**Reported**).[^s2s-supporting-docs]
- TTS cancellation is best-effort only: barge-in and session teardown close the client's active HTTP response and stop local audio publication, but the standard `/v1/audio/speech` interface has no portable server-side cancellation operation, so a disconnected client does not guarantee endpoint computation stops immediately (**Reported**).[^s2s-supporting-docs]

## Playback buffering for remote TTS

- For `speech-to-speech local --tts openai` the packaged client's startup playback buffer defaults to 196 ms (other local TTS backends and `talk` start at 0 ms) because the HTTP `/audio/speech` path can deliver an uneven first burst; the buffer absorbs early jitter and is reused if playback catches up (**Reported**).[^s2s-supporting-docs]
- `--playback-buffer-ms` overrides either default, and an explicit `0` disables buffering even for `local --tts openai`; the buffer is downstream of TTS and does not alter the TTS request, synthesis, resampling, or server deployment (**Reported**).[^s2s-supporting-docs]
- Responses shorter than the configured buffer are played as soon as the audio response completes, and browser, WebRTC, and third-party Realtime clients use their own playback behavior unaffected by this option (**Reported**).[^s2s-supporting-docs]

## Relationships

- Part of [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md): these are the remote-delegation backends of that pipeline's STT and TTS slots (**Synthesis**).[^s2s-supporting-docs]
- Uses [Qwen3-ASR family](qwen3-asr-family.md) and [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) as examples of models served behind the vLLM STT endpoints; consult those pages for checkpoint-level language and streaming detail (**Synthesis**).[^s2s-supporting-docs]
- Uses [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) and [vLLM-Omni](vllm-omni.md) for the documented TTS server pairing, and [Faster Qwen3-TTS](faster-qwen3-tts.md) for the in-process alternative to delegating synthesis (**Synthesis**).[^s2s-supporting-docs]
- Compare with [Speaches](speaches.md) and [WhisperLiveKit](whisperlivekit.md), which are themselves OpenAI/Deepgram-compatible servers this backend could call, and with [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md) for the independent-service pattern (**Synthesis**).[^s2s-supporting-docs]

## Coverage and limits

- Source inspected statically only: the two STT/TTS guides were read as captured Markdown; no vLLM, vLLM-Omni, or OpenAI server was started, no model was downloaded, and no transcription or synthesis request was issued, so all endpoint, resampling, queue-bound, and cancellation behavior is a source assertion transcribed here without independent verification (**Synthesis**).[^s2s-supporting-docs]
- The guides describe HTTP and WebSocket protocols but do not publish measured latency, throughput, or quality figures for the remote paths; the only latency-relevant statement is the 196 ms packaged-client buffer default (**Reported**).[^s2s-supporting-docs]
- Model identifiers, API paths, default ports, and framework versions (`vllm==0.24.0`, `gpt-transcribe`, `gpt-live-transcribe`, `Qwen/Qwen3-ASR-1.7B`, `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`) carry `stale_after: 2027-10-07` under the `stt`/`tts`/`pipeline` domain rules (**Synthesis**).[^s2s-supporting-docs]

[^s2s-supporting-docs]: [huggingface/speech-to-speech supporting docs](../raw/speech-to-speech-docs/README.md) — a capture at upstream revision `f9c23282a564cbe5b1f015ccb36d58e941de8520` (2026-10-07). Locators: `docs/openai-compatible-stt.md` → title plus flow fence, "vLLM with Qwen3-ASR", "OpenAI-hosted transcription", "Authentication and compatibility" (`languages[]` plural, one-second silence check), "Turn and session lifecycle" (eight-pending-final bound, session generation, best-effort server cancellation), "Stateful streaming STT" plus "OpenAI Realtime transcription" (`intent=transcription`, 24 kHz requirement) and "vLLM Realtime transcription (experimental)" (Voxtral example, served-identifier requirement); `docs/openai-compatible-tts.md` → title plus flow fence, "vLLM-Omni with Qwen3-TTS" (`vllm==0.24.0`, `/v1/audio/voices`, 24 kHz→16 kHz conversion, `--openai_tts_language` forwarding), "OpenAI and standard-compatible servers" (`stream_format=audio` vs `stream=true`), "Playback buffering" (196 ms default, `--playback-buffer-ms`), "Authentication and compatibility" (startup synthesis check, PCM16/WAV formats, best-effort cancellation); `src/speech_to_speech/STT/README.md` → "OpenAI-compatible endpoint"; `src/speech_to_speech/TTS/README.md` → "OpenAI-compatible endpoint"; `src/speech_to_speech/arguments_classes/{openai_stt,openai_realtime_stt,openai_tts}_arguments.py` → dataclass defaults for base URLs, model, voice, sample rate, response format, timeouts. Limitations: `demo/CONTEXT.md`, `demo/DESIGN.md`, `demo/docs/adr/`, `docs/releases/`, `examples/`, `archive/`, `AGENTS.md`, tests, implementation sources, and non-PoC argument classes are excluded by the capture; the root repo README is byte-identical to [Speech To Speech README](../raw/speech-to-speech.md) and excluded from this package.
