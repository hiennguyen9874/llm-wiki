---
type: Concept
title: NeMo-Speech.cpp Server and Deployment
description: The NeMo-Speech.cpp `serve` and `riva_server` binaries, engine/listener configuration precedence, HTTP listener and capability enablement, the loopback/api-key/TLS security posture, health and readiness routes, and upload, timeout, worker-pool and shutdown limits.
tags: [pipeline, stt, tts, server, deployment, streaming]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:14:00Z }
stale_after: 2027-10-07
sources:
  - id: nemo-speech-cpp-docs
    resource: ../raw/nemo-speech-cpp-docs/README.md
    scope: ../raw/nemo-speech-cpp-docs/
    kind: documentation
    revision: 8642eaa5cc51efbc17ad0f3e433944ba858a873f
    title: NVIDIA/NeMo-Speech.cpp supporting docs
---

[NeMo-Speech.cpp](nemo-speech-cpp.md) serves two executables over the same core runtime: `nemo-speech serve` hosting HTTP, realtime WebSocket, and the browser playground, and `riva_server` hosting Riva-compatible gRPC; they are separate processes that do **not** share loaded models, both accept the same dotted `asr.*`/`tts.*`/`nmt.*` engine keys, and the HTTP server binds `127.0.0.1:8080` by default with deliberately loopback-only, unauthenticated-unless-configured exposure intended for local use and direct integration rather than production, where NVIDIA NIM is the stated path (**Reported**).[^nemo-speech-cpp-docs]

## Binaries and build presets

- `nemo-speech serve` loads each configured model once and hosts HTTP, realtime WebSocket, and the browser playground; `riva_server` hosts the Riva-compatible gRPC services. Full-duplex VoiceChat is available only through the realtime WebSocket API hosted by `nemo-speech serve`, and every client connection owns independent conversation state (**Reported**).[^nemo-speech-cpp-docs]
- The `*-server` presets include HTTP support for ASR, diarization, NMT, and TTS without gRPC; `cuda-s2s` builds the VoiceChat realtime server, `cuda-full` adds gRPC, text normalization, and optional TTS language frontends, and `developer` also adds examples, tests, and tools (**Reported**).[^nemo-speech-cpp-docs]
- Typical launches: `nemo-speech serve --asr-model models/asr.q8_0.gguf ... --open`; `nemo-speech serve --diar-model sortformer` for standalone diarization, which downloads the indexed model if needed; `nemo-speech serve --config config/voicechat.yaml` for a converted VoiceChat model; and `riva_server --asr.model.path models/asr.q8_0.gguf --bind 0.0.0.0:50051` (**Reported**).[^nemo-speech-cpp-docs]

## Engine and listener configuration

- Settings apply in the order `built-in defaults < --config FILE.yaml < NEMO_SPEECH_<KEY> env < CLI option`; nested YAML maps mirror the dotted keys and unknown keys are errors (**Reported**).[^nemo-speech-cpp-docs]
- The HTTP server additionally accepts top-level `diar.*` keys for standalone diarization, while `asr.diar.*` adds speaker labels to ASR results. Checked-in examples cover `config/asr.example.yaml`, `diar.example.yaml`, `tts.example.yaml`, `nmt.example.yaml`, `server.example.yaml` (combined), and `voicechat.yaml` (**Reported**).[^nemo-speech-cpp-docs]
- `riva_server` does not accept HTTP listener settings; it takes `--bind HOST:PORT` (default `0.0.0.0:50051`) and an engine-only YAML file. Both binaries accept the same `asr.*`, `tts.*`, and `nmt.*` engine settings, and the gRPC binary does not accept the `nemo-speech serve` CLI aliases (**Reported**).[^nemo-speech-cpp-docs]

| flag / key | default | meaning |
|---|---|---|
| `--host` / `http.host` | `127.0.0.1` | HTTP bind address |
| `--port` / `http.port` | `8080` | HTTP port |
| `--api-key` / `http.api-key` | none | require `Authorization: Bearer <key>` on API routes |
| `--tls-cert` / `http.tls-cert` | none | TLS certificate (with `--tls-key`; requires `NEMO_SPEECH_HTTP_TLS=ON`) |
| `--cors-origin` / `http.cors-origin` | none | allowed browser origin |
| `--no-ui` / `http.playground` | playground on | disable the embedded playground |
| `--threads` / `http.threads` | `4` | bounded worker pool |
| `--max-upload-mb` / `http.max-upload-mb` | `512` | request-body limit |
| `--read-timeout` / `--write-timeout` | `30` each | socket read / write timeout (s) |
| `--access-log` / `--log-format` | false / `text` | completed-request logging; `text` or `json` |

- Capabilities auto-enable when their required model paths are present; an explicit `asr.enabled`/`tts.enabled`/`nmt.enabled` can be `true`, `false`, or `auto` (default), and starting with no enabled capability is an error (**Reported**).[^nemo-speech-cpp-docs]

## Security posture

- The default loopback binding is intentional; for remote access the source requires setting `--host 0.0.0.0`, TLS (`--tls-cert` + `--tls-key`), and an API key explicitly. TLS must be enabled at source-build time with `NEMO_SPEECH_HTTP_TLS=ON` and is not part of the default server presets (**Reported**).[^nemo-speech-cpp-docs]
- Prefer the `NEMO_SPEECH_HTTP_API_KEY` environment variable over a command-line secret. API routes require `Authorization: Bearer <key>`; browser WebSockets may supply `?api_key=<key>`, but that query credential is not accepted on non-realtime routes. The playground, health, readiness, and version routes remain unauthenticated (**Reported**).[^nemo-speech-cpp-docs]
- Cross-origin browser access is disabled by default; `--cors-origin ORIGIN` allows one explicit origin, and `*` should be used only for an intentionally public API (**Reported**).[^nemo-speech-cpp-docs]
- `--access-log` logs completed requests without headers or query strings; `--log-format json` emits one JSON object per request, and the global `--json` option also makes listener-ready events and enabled access logs machine-readable (**Reported**).[^nemo-speech-cpp-docs]

## Health and readiness

- `GET /health` returns compact engine status and runtime version; `GET /ready` returns readiness, selected device, and loaded capabilities. Both return HTTP 503 when no engine is ready, and the CLI can check either with `nemo-speech health --url http://127.0.0.1:8080/ready`, using `/ready` by default (**Reported**).[^nemo-speech-cpp-docs]
- `GET /v1/realtime/health` reports VoiceChat WebSocket readiness (**Reported**).[^nemo-speech-cpp-docs]

## Limits and lifecycle

- Uploads are capped at 512 MiB by default (`--max-upload-mb`), and the same limit applies to cumulative audio on a realtime WebSocket stream; socket reads and writes time out after 30 s by default, and inference work runs on the bounded `--threads` worker pool (**Reported**).[^nemo-speech-cpp-docs]
- VoiceChat sessions accept 300 seconds of input audio by default, configurable with `s2s.max_session_seconds`; unless `http.threads` is set explicitly the server reserves enough workers for `s2s.max_streams` plus listener work. The NMT context pool stays an engine setting (`nmt.pool.contexts`) and is not silently expanded to match HTTP workers (**Reported**).[^nemo-speech-cpp-docs]
- SIGINT/SIGTERM stops HTTP admission and releases loaded models; `--no-warmup` exists for HTTP diagnostics but is not recommended when startup readiness matters (**Reported**).[^nemo-speech-cpp-docs]
- The separate `riva_server` accepts messages up to gRPC's signed 32-bit limit and drains active RPCs for up to 10 seconds on SIGINT/SIGTERM; it currently uses plaintext server credentials, so TLS should be terminated in a trusted proxy when exposing it outside a controlled network (**Reported**).[^nemo-speech-cpp-docs]

## Relationships

- Serves [NeMo-Speech.cpp](nemo-speech-cpp.md): this is the process/operations sibling of that page's runtime identity; request and event contracts live in [NeMo-Speech.cpp HTTP and Realtime API](nemo-speech-http-api.md) and recognizer keys in [NeMo-Speech.cpp ASR Configuration](nemo-speech-asr-configuration.md) (**Synthesis**).[^nemo-speech-cpp-docs]
- Compare with [Parakeet ASR Server](parakeet-asr-server.md), [Speaches](speaches.md), and [WhisperLiveKit](whisperlivekit.md), which are self-hosted recognition servers for different runtimes and fixed checkpoints; this page's differentiator is a native ggml runtime hosting ASR, diarization, NMT, TTS, and full-duplex VoiceChat behind one loopback-first HTTP/WebSocket server plus a separate Riva-compatible gRPC binary (**Synthesis**).[^nemo-speech-cpp-docs]
- Compare with [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and [RealtimeVoiceChat](realtime-voice-chat.md) for the orchestration layer that would call this server or its realtime socket, and with [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md) for the deployment-tool grouping (**Synthesis**).[^nemo-speech-cpp-docs]
- Uses [Silero VAD](silero-vad.md) and Sortformer diarization as optional loaded capabilities; checkpoint-level behavior belongs on those pages (**Synthesis**).[^nemo-speech-cpp-docs]

## Coverage and limits

- Source inspected statically only; the capture's five documents were read as captured Markdown and their SHA-256 digests re-computed to match `checksums.json` (**Observed** for capture integrity; the manifest is a local capture record, not independent provenance). Binding, auth, timeout, and lifecycle claims are documentation assertions (**Reported**).[^nemo-speech-cpp-docs]
- No binary was built or run, no listener was bound, no TLS build was produced, no API key or CORS origin was exercised, and no SIGINT/SIGTERM drain was observed, so all operational behavior is unverified (**Synthesis**).[^nemo-speech-cpp-docs]
- `config/*.example.yaml`, the build guide `docs/build.md`, and the TTS/NMT/S2S configuration references are outside this capture and were not fetched; preset-to-feature mapping and TLS setup detail are therefore not independently confirmed (**Synthesis**).[^nemo-speech-cpp-docs]
- Default host/port, limits, and preset behavior are version-sensitive and carry `stale_after: 2027-10-07` under the `pipeline` domain rule (**Synthesis**).[^nemo-speech-cpp-docs]

[^nemo-speech-cpp-docs]: [NVIDIA/NeMo-Speech.cpp supporting docs](../raw/nemo-speech-cpp-docs/README.md) — capture at upstream revision `8642eaa5cc51efbc17ad0f3e433944ba858a873f` (2026-10-07). Locators: `docs/server.md` → opening fence (`nemo-speech serve` vs `riva_server`, one load per process, independent conversation state), preset paragraph (`*-server`, `cuda-s2s`, `cuda-full`, `developer`), launch fences, `Engine and listener configuration` (precedence chain, `diar.*`/`asr.diar.*`, example-config table, YAML fence, unknown-keys error, aliases, boolean negation, HTTP listener settings table), capability auto-enable paragraph, loopback/security paragraphs (`NEMO_SPEECH_HTTP_API_KEY`, bearer header, `?api_key`, unauthenticated routes, NIM production path), CORS paragraph, access-log/`--json` paragraph, `Health and readiness`, `HTTP endpoints`, `Limits and lifecycle` (512 MiB, 30 s timeouts, 300 s VoiceChat, `s2s.max_streams`/`nmt.pool.contexts`, SIGINT/SIGTERM, `--no-warmup`), `riva_server` limits paragraph (32-bit message cap, 10 s drain, plaintext credentials); `docs/api.md` → `Service` table (`GET /v1/realtime/health`). Limitations: `config/*.example.yaml`, `docs/build.md`, and TTS/NMT/S2S configuration references are outside this capture.
