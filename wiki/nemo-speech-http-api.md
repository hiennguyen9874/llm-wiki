---
type: Concept
title: NeMo-Speech.cpp HTTP and Realtime API
description: The NeMo-Speech.cpp `nemo-speech serve` HTTP API — service, transcription, speech, translation, and diarization routes, the realtime transcription and VoiceChat WebSocket event protocols, and the OpenAI SDK and curl client-compatibility caveats.
tags: [pipeline, stt, tts, streaming, server, openai-compatible]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:16:00Z }
stale_after: 2027-10-07
sources:
  - id: nemo-speech-cpp-docs
    resource: ../raw/nemo-speech-cpp-docs/README.md
    scope: ../raw/nemo-speech-cpp-docs/
    kind: documentation
    revision: 8642eaa5cc51efbc17ad0f3e433944ba858a873f
    title: NVIDIA/NeMo-Speech.cpp supporting docs
---

The [NeMo-Speech.cpp server](nemo-speech-server.md) exposes an HTTP surface whose OpenAI SDK compatibility is deliberately limited to model listing plus the documented subsets of `/v1/audio/transcriptions` and `/v1/audio/speech`, with translation and diarization as project extensions and two WebSocket contracts — a project-specific PCM16 realtime transcription protocol and the full-duplex Riva VoiceChat session protocol on `/v1/realtime` (**Reported**).[^nemo-speech-cpp-docs]

## Conventions

- If the server was started with an API key, `/v1` routes require `Authorization: Bearer <key>` (WebSocket clients may use `?api_key=<key>`); the playground, health, readiness, and version routes are intentionally unauthenticated (**Reported**).[^nemo-speech-cpp-docs]
- Non-2xx responses carry `{"error": {"message": "...", "type": "invalid_request_error" | "server_error"}}` (**Reported**).[^nemo-speech-cpp-docs]
- Audio uploads are multipart with the uncompressed RIFF/WAVE file in `file`; mono or stereo PCM16 and float32 WAVs from 8–96 kHz are accepted and stereo is downmixed to mono. Endpoints return 501 when their capability is not in the build and a `server_error` when the model is not loaded (**Reported**).[^nemo-speech-cpp-docs]
- `GET /v1/models` lists loaded models and capabilities and is the way to inspect the active model IDs (**Reported**).[^nemo-speech-cpp-docs]

## Service routes

| Method + path | Purpose |
|---|---|
| `GET /` | bundled playground UI |
| `GET /health`, `GET /ready` | compact health / detailed readiness |
| `GET /version` | build version |
| `GET /v1/models` | loaded models and capabilities |
| `GET /v1/realtime/health` | VoiceChat WebSocket readiness |
| `POST /v1/audio/transcriptions` | speech-to-text (OpenAI-compatible multipart subset) |
| `POST /v1/audio/speech` | text-to-speech (OpenAI-compatible JSON subset) |
| `POST /v1/translations` | text translation |
| `POST /v1/audio/translations` | speech translation (ASR → NMT) |
| `POST /v1/audio/speech/translations` | speech-to-speech translation (ASR → NMT → TTS, extension) |
| `POST /v1/audio/diarizations` | speaker segments (`/v1/diarizations` alias) |
| WebSocket `/v1/audio/transcriptions/realtime` | live PCM16 transcription |
| WebSocket `/v1/realtime`, `/realtime` | full-duplex VoiceChat when loaded |

## POST /v1/audio/transcriptions

Fields beyond the required `file` include `model` (accepted for compatibility; the server uses its one loaded ASR model), `language`, `response_format` (`json` default, `verbose_json`, `text`, `srt`, `vtt`), `automatic_punctuation` (default true), `verbatim` (skip ITN, default false), `profanity_filter`, `diarization` (requires `verbose_json` and a diarizer), `max_speaker_count` (deprecated/ignored; capacity comes from the loaded Sortformer model), `speech_contexts` (word boosting, `[{"phrases": ["..."], "boost": N}]`), and `prompt` (one boosted phrase at boost 10) (**Reported**).[^nemo-speech-cpp-docs]

- `json` returns `{"text": "..."}`; `verbose_json` adds `task`, `language`, `duration`, and `words[]` (`word`, `start`, `end`, `confidence`, and `speaker` when diarization is on); SRT/WebVTT use the same readable, punctuation-aware cue grouping as the file CLI (**Reported**).[^nemo-speech-cpp-docs]
- Word-boosting scoring semantics live in [ASR configuration](nemo-speech-asr-configuration.md#word-boosting) (**Reported**).[^nemo-speech-cpp-docs]

## Realtime transcription WebSocket

- `/v1/audio/transcriptions/realtime` is a project-specific event protocol, not the OpenAI Realtime API. The server sends `session.created` on connect; a single optional `session.update` (rejected once audio has started) sets session options; then binary little-endian PCM16 frames (or base64 chunks in `input_audio_buffer.append`) carry audio, and `input_audio_buffer.commit` finishes. `input_audio_buffer.clear` or `response.cancel` discards buffered audio (`input_audio_buffer.cleared`) (**Reported**).[^nemo-speech-cpp-docs]
- `session.update.session` fields: `sample_rate` (`16000` for the shipped models, 8000–96000), `language`, `automatic_punctuation` (true), `verbatim` (false), `profanity_filter` (false), `word_timestamps` (false), `speaker_diarization` (false; requires a loaded diarizer), `max_speaker_count` (deprecated/ignored), `endpointing_ms` (server default), `speech_contexts`, and `prompt` (**Reported**).[^nemo-speech-cpp-docs]
- Server events: `session.created`, `session.updated`, `conversation.item.input_audio_transcription.delta` (partials), the matching `.completed` (finals, with `words` when requested), `input_audio_buffer.committed`, `input_audio_buffer.cleared`, and `error` (**Reported**).[^nemo-speech-cpp-docs]
- For backward compatibility `/v1/realtime` serves this transcription protocol when VoiceChat is not loaded; new transcription clients should use the explicit audio-namespaced path so their route stays unambiguous (**Reported**).[^nemo-speech-cpp-docs]

## VoiceChat WebSocket /v1/realtime and /realtime

- When a VoiceChat model is loaded, both paths expose the full-duplex Riva VoiceChat session protocol. The server sends `session.created` on connection; `session.update` is sent before audio begins and session configuration is immutable after the first audio frame (**Reported**).[^nemo-speech-cpp-docs]
- `session.audio.input.format` accepts `"pcm16"` or an object such as `{"type":"audio/pcm","rate":24000}`, with mono little-endian PCM16 at 16–48 kHz; `session.audio.output.format` must select PCM16 at 24 kHz. Audio may be sent as binary frames or base64 in `input_audio_buffer.append`, and output is base64 PCM16 in 80 ms `response.output_audio.delta` packets (**Reported**).[^nemo-speech-cpp-docs]
- Other session fields: `instructions` (defaults to the server VoiceChat prompt, including conversational policy) and `tools` (OpenAI-format definitions, default `[]`, with `ack_messages` supported) (**Reported**).[^nemo-speech-cpp-docs]
- Response events include `response.created`, `response.output_audio.delta`, `response.output_audio.done`, `response.output_audio_transcript.delta`, `response.output_audio_transcript.done`, and `response.done`; user turns emit `input_audio_buffer.speech_started`, transcription delta/completed events, and `input_audio_buffer.speech_stopped`. Every event includes an `event_id` (**Reported**).[^nemo-speech-cpp-docs]
- Tool requests arrive as `response.function_call_arguments.done` with `call_id`, `name`, and JSON-encoded `arguments`; the result is returned on the same socket as a `conversation.item.create` item of type `function_call_output`. `session.close` finishes cleanly: the server drains residual input, emits response completion events, then sends `session.end` with received, sent, dropped, inference, and audio-duration counters (**Reported**).[^nemo-speech-cpp-docs]

## POST /v1/audio/speech

- OpenAI-compatible JSON subset: `input` (required), `model` (accepted for compatibility), `voice`, `language`, `speed` (only `1.0` is accepted; other values return 400), `sample_rate` (8000 Hz through the model rate — 22050 Hz for the supported NanoCodec model), and `response_format` (`wav` default or `pcm`) (**Reported**).[^nemo-speech-cpp-docs]
- The response is mono signed PCM16 in a WAV container or raw little-endian bytes with the matching content type; the complete audio is buffered before the HTTP response, so streaming synthesis is **not** part of this compatibility subset (**Reported**).[^nemo-speech-cpp-docs]
- Local voice names are case-insensitive, listed in the `voices` field of the speech entry from `GET /v1/models`, and also accepted as `<model-id>.<voice>`. `default` and OpenAI aliases such as `alloy` select the server's configured default local speaker and do not provide hosted OpenAI voices; an unrecognized local name returns 400 (**Reported**).[^nemo-speech-cpp-docs]

## Translation and diarization extensions

- `/v1/translations` (JSON) takes `input`, required `source_language`, and required `target_language`, returning `{"translations": [{"text": "..."}]}` (**Reported**).[^nemo-speech-cpp-docs]
- `/v1/audio/translations` (multipart) accepts the ASR common fields (`automatic_punctuation`, `verbatim`, `profanity_filter`, `speech_contexts`, `prompt`) plus `file`, `language` (auto), `target_language` (default `en-US`), and `response_format` (`json`, `verbose_json`, or `text`); `verbose_json` adds `task`, `language`, and `duration` (**Reported**).[^nemo-speech-cpp-docs]
- `/v1/audio/speech/translations` composes ASR → NMT → TTS with `target_language` required and audio `response_format` (`wav`/`pcm`) plus `voice` and `sample_rate`, returning translated mono signed PCM16 (**Reported**).[^nemo-speech-cpp-docs]
- `/v1/audio/diarizations` segments speakers without transcription with `mode` `streaming` (default, long-form) or full-attention `offline` (recordings up to about 6.6 minutes), returning `{"segments": [{"start": s, "end": s, "speaker": n}]}` with 1-based speaker ids. Request `mode=offline` is distinct from `diar.preset: offline`, which still uses the streaming path (**Reported**).[^nemo-speech-cpp-docs]

## Client integration

- The OpenAI Python and JavaScript SDKs work against `http://127.0.0.1:8080/v1`; an API key is only required when the server was started with `--api-key`, though SDKs still require a nonempty placeholder locally. SDKs also require a `model` argument, but because the server loads one model per capability that field does not switch models — use `GET /v1/models` to inspect the active IDs (**Reported**).[^nemo-speech-cpp-docs]
- Browser code should use the playground's realtime WebSocket protocol rather than placing an API key in a public page (**Reported**).[^nemo-speech-cpp-docs]
- Riva-compatible gRPC clients use NVIDIA Riva's existing Python or C++ clients against the `riva_server` address (`riva_server --asr.model.path models/asr.q8_0.gguf --bind 0.0.0.0:50051`); no NeMo-Speech.cpp-specific client is required. In-process C and C++ embedding is delegated to `docs/sdk.md`, which is outside this capture (**Reported**, with unfetched-pointer limit).[^nemo-speech-cpp-docs]

## Relationships

- Exposes [NeMo-Speech.cpp Server and Deployment](nemo-speech-server.md): this page holds the request/event contracts while that page holds listener, auth, and lifecycle operations; both are served by [NeMo-Speech.cpp](nemo-speech-cpp.md) (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md), and [Parakeet CTC 1.1B](parakeet-ctc-1.1b.md) as the ASR checkpoints behind `/v1/audio/transcriptions`, and the Sortformer models ([Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md), [Nemotron 3 Diarization](nemotron-3-diarization.md)) behind diarization; checkpoint detail lives on those pages (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) for the full-duplex realtime protocol; consult that page for the model-level latency and full-duplex behavior (**Synthesis**).[^nemo-speech-cpp-docs]
- Compare the realtime event surface with the OpenAI Realtime contracts in [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and [Speech-to-Speech Realtime Engine](speech-to-speech-realtime-engine.md), and the OpenAI-compatible subsets with [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md), [Parakeet ASR Server](parakeet-asr-server.md), [Speaches](speaches.md), and [WhisperLiveKit](whisperlivekit.md) (**Synthesis**).[^nemo-speech-cpp-docs]

## Coverage and limits

- Source inspected statically only; the capture's five documents were read as captured Markdown and their SHA-256 digests re-computed to match `checksums.json` (**Observed** for capture integrity; the manifest is a local capture record, not independent provenance). Route, field, and event claims are documentation assertions (**Reported**).[^nemo-speech-cpp-docs]
- No server was started, no HTTP request or WebSocket session was issued, no audio was transcribed or synthesized, and no SDK client was run, so every request shape, event sequence, limit, and compatibility statement is unverified (**Synthesis**).[^nemo-speech-cpp-docs]
- `docs/sdk.md` (in-process C/C++ embedding) and `docs/s2s/clients.md` (the complete VoiceChat event flow, including a reference client) are outside this capture and were not fetched; the VoiceChat event flow here is limited to the API reference summary (**Synthesis**).[^nemo-speech-cpp-docs]
- Field defaults, route names, and OpenAI-compatibility boundaries are version-sensitive and carry `stale_after: 2027-10-07` under the `pipeline`/`stt`/`tts` domain rules (**Synthesis**).[^nemo-speech-cpp-docs]

[^nemo-speech-cpp-docs]: [NVIDIA/NeMo-Speech.cpp supporting docs](../raw/nemo-speech-cpp-docs/README.md) — capture at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f` (2026-10-07). Locators: `docs/api.md` → intro bullet list (auth, error shape, multipart audio, 501/server_error, OpenAI-compatibility scope), `Service` table, `POST /v1/audio/transcriptions` (field table, `verbose_json` fields, SRT/VTT grouping, `speech_contexts` shape, `prompt` boost 10), `WebSocket /v1/audio/transcriptions/realtime` (event flow, `session.update` field table, server-event list, `/v1/realtime` alias), `VoiceChat WebSocket /v1/realtime and /realtime` (`session.audio.input/output.format`, 16–48 kHz in / 24 kHz PCM16 out, 80 ms packets, `instructions`/`tools`, response-event list, `response.function_call_arguments.done` + `conversation.item.create` fence, `session.close`/`session.end` counters), `POST /v1/audio/speech` (field table, buffering, voice naming + `voices` from `/v1/models`), `POST /v1/translations`, `POST /v1/audio/translations`, `POST /v1/audio/speech/translations`, `POST /v1/audio/diarizations` (streaming vs offline mode, `mode=offline` vs `diar.preset`); `docs/clients.md` → intro, `OpenAI Python SDK` fence, `OpenAI JavaScript SDK` fence, `curl` fences, `Riva-compatible gRPC clients` (`riva_server --bind 0.0.0.0:50051`, NVIDIA Riva clients), `In-process C and C++` (`docs/sdk.md` pointer); `docs/server.md` → `HTTP endpoints` (route list, OpenAI-compatibility limit, `/v1/realtime` alias) and playground paragraph. Limitations: `docs/sdk.md` and `docs/s2s/clients.md` are outside this capture.
