---
type: Concept
title: VieNeu-TTS OpenAI-Compatible Speech API
description: The VieNeu-TTS `apps/openai_speech.py` server contract — `POST /v1/audio/speech` fields, `pcm`/`wav` chunked or SSE streaming, the models/voices/health endpoints, environment configuration, warm-up, and OpenAI-framework client integration.
tags: [tts, vietnamese, streaming, api, openai-compatible]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:30:00Z }
stale_after: 2027-10-07
sources:
  - id: vieneu-tts-docs
    resource: ../raw/vieneu-tts-docs/README.md
    scope: ../raw/vieneu-tts-docs/
    kind: documentation
    revision: 85344322b7258b4e25479b692e8e3396baf9db34
    title: VieNeu-TTS supporting docs (streaming guide and Docker Compose)
---

VieNeu-TTS v3 Turbo ships an OpenAI-compatible HTTP server, `apps/openai_speech.py`, whose `POST /v1/audio/speech` accepts OpenAI's TTS fields plus audio-specific extras and returns chunked raw audio or Server-Sent Events, so existing OpenAI clients and frameworks such as Pipecat, LiveKit Agents, and the Vercel AI SDK can reach it by changing `base_url` (**Reported**).[^vieneu-tts-docs] The same process picks its backend itself (`VIENEU_BACKEND=auto`: CUDA → PyTorch, otherwise ONNX), runs **one** uvicorn worker that owns the model and scheduler — scaling out means running several containers, one GPU each, not forking — and warms up at start-up by synthesizing a short sentence so the first client does not pay CUDA-graph capture or ONNX session load (**Reported**).[^vieneu-tts-docs] This page covers the HTTP contract; the streaming engine, latency figures, and sizing rules are in [VieNeu-TTS Streaming Runtime and Performance](vieneu-tts-streaming-runtime.md), and the container profiles in [VieNeu-TTS Docker Compose Deployment](vieneu-tts-docker-deployment.md).

## `POST /v1/audio/speech`

JSON body — OpenAI's fields plus a few extras (**Reported**).[^vieneu-tts-docs]

| Field | Default | Notes |
|---|---|---|
| `input` | required | Text up to 20,000 chars; split into chunks ≤ `max_chars` at sentence boundaries |
| `model` | `vieneu-v3-turbo` | Any string; kept for compatibility only |
| `voice` | default voice | A preset from `GET /v1/voices` or one added with `POST /v1/voices` |
| `response_format` | `wav` | `pcm` (s16le mono, headerless) · `wav` (header with "unknown" length so players start at once); `mp3`/`opus`/`aac`/`flac` → `400` |
| `stream_format` | `audio` | `audio`: raw bytes, chunked transfer · `sse`: Server-Sent Events |
| `sample_rate` | `48000` | `48000` native · `24000` (OpenAI's `pcm` rate) · `16000` · `8000`; resampled per chunk with soxr, no added latency |
| `speed`, `instructions` | — | Accepted for compatibility, **ignored** (`X-VieNeu-Ignored` header says so) |
| `temperature`, `top_k`, `top_p`, `repetition_penalty` | 0.8 / 25 / 0.95 / 1.2 | Sampling; allowed 0–2 / 1–1024 / (0, 1] / 1–2, anything else (or NaN) → `400` |
| `max_chars` | `256` | Max text chunk length, 64–512 |

- A success is `200` with `Transfer-Encoding: chunked` and headers `X-Request-Id` and `X-Sample-Rate`. Errors use OpenAI's shape `{"error": {"message", "type", "code"}}`: `400` bad parameter, `401` bad key, and `429` when no slot is free (with `Retry-After`) (**Reported**).[^vieneu-tts-docs]
- With `stream_format=sse` the response is `text/event-stream`, one `data:` line per event: repeated `{"type":"speech.audio.delta","audio":"<base64 PCM s16le>"}` and a final `{"type":"speech.audio.done","usage":{"output_samples":…,"sample_rate":…,"seconds":…}}`. With `response_format=wav` plus `sse`, the first event is the base64 WAV header (**Reported**).[^vieneu-tts-docs]

## Other endpoints

| Endpoint | Behavior |
|---|---|
| `GET /v1/models` | Model, `sample_rate`, `backend`, `max_streams`, supported formats |
| `GET /v1/voices` | Presets (`id`, `name`, `description`, `gender`) |
| `POST /v1/voices` | multipart `name`, `file` (3–8 s clip), `denoise`; clones a voice into process memory; a built-in voice name or alias → `409` |
| `GET /health` | `active` (playing), `waiting` (queued), `max_streams`; `503` once the GPU stream scheduler has died (it does not recover — the Docker healthcheck restarts the container) |

## Server configuration

Environment variables, with their defaults (**Reported**).[^vieneu-tts-docs]

| Variable | Default | Meaning |
|---|---|---|
| `VIENEU_BACKEND` | `auto` | `pytorch` (GPU) · `onnx` (CPU) |
| `VIENEU_DEVICE` | `auto` | `cuda` · `cpu` |
| `VIENEU_PRECISION` | `fp32` | CPU: `fp32` · `int8` |
| `VIENEU_MAX_STREAMS` | GPU 16 · CPU 1 (int8: 2) | Streams served at once; on GPU this is the continuous-batch size and should match real load |
| `VIENEU_QUEUE` | = `MAX_STREAMS` | Requests allowed to wait for a slot; beyond that → immediate `429` |
| `VIENEU_QUEUE_TIMEOUT` | 10 | Max seconds in the queue, then `429` |
| `VIENEU_API_KEY` | empty | If set, requires `Authorization: Bearer <key>`; unset on a non-loopback `HOST` logs a start-up warning |
| `VIENEU_WATERMARK` | 1 | Perth audio watermark, applied per chunk |
| `HOST` / `PORT` | `127.0.0.1` / 8000 | `HOST=0.0.0.0` to serve other machines (the Docker profiles set it) — pair it with `VIENEU_API_KEY` |
| `VIENEU_FUSED_FRAME` | 1 | `0` disables the CUDA-graph path for debugging (falls back to a single stream, ~300 ms TTFA) |

Launch variants, all listening on `http://0.0.0.0:8000` (**Reported**).[^vieneu-tts-docs]

```bash
uv run python -m apps.openai_speech                                              # (a) GPU when CUDA is present, else CPU
VIENEU_BACKEND=onnx VIENEU_PRECISION=int8 uv run python -m apps.openai_speech    # (b) CPU int8 (~2x fp32; needs VNNI)
docker compose -f docker/docker-compose.yml --profile api-gpu up                 # (c) Docker GPU container
docker compose -f docker/docker-compose.yml --profile api-cpu up                 # (d) Docker CPU container
```

- Warm-up finishes in roughly 12 s on the test machine with the model already in the Hugging Face cache (GPU CUDA-graph capture ~0.7 s; CPU ONNX session load); wait for `/health` to return `ok` before sending traffic (**Reported**).[^vieneu-tts-docs]

## Clients

- **Python (OpenAI SDK):** point `base_url` at `http://localhost:8000/v1`, set `api_key` to `VIENEU_API_KEY` if configured, and iterate `with_streaming_response.create(...)` with `response_format="pcm"` for s16le 48 kHz mono bytes (**Reported**).[^vieneu-tts-docs]
- **curl:** `curl -N …/v1/audio/speech -d '{"input":…,"voice":"Mai Anh","response_format":"wav"}' | ffplay -i - -nodisp -autoexit` plays wav as it streams (**Reported**).[^vieneu-tts-docs]
- **Browser (SSE):** `fetch` the endpoint with `stream_format="sse"`, split events on `\n\n`, strip `data: `, and play each `speech.audio.delta` payload (**Reported**).[^vieneu-tts-docs]
- **Pipecat / LiveKit Agents / Vercel AI SDK:** use their OpenAI TTS plugin, change `base_url`, set `response_format="pcm"`, and add `sample_rate: 24000` as an extra body field (or set the framework's rate to 48,000) when the framework assumes 24 kHz (**Reported**).[^vieneu-tts-docs]
- `examples/openai_speech_client.py` is the bundled client: it reports TTFA/RTF and has a `--bench N` mode for concurrent-request benchmarking (**Reported**).[^vieneu-tts-docs]

## Relationships

- Uses [VieNeu-TTS Streaming Runtime and Performance](vieneu-tts-streaming-runtime.md): the API's per-request queue, slot, and format behavior is the HTTP surface over the GPU/CPU streaming engine documented there (**Synthesis**).[^vieneu-tts-docs]
- Deployed by [VieNeu-TTS Docker Compose Deployment](vieneu-tts-docker-deployment.md): the `api-gpu`/`api-cpu` services launch exactly this server with overridden environment and a `/health` healthcheck (**Synthesis**).[^vieneu-tts-docs]
- Serves [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md): the endpoint's model/voice behavior is that family's serving interface (**Synthesis**).[^vieneu-tts-docs]
- Transport contrast with [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md): both expose OpenAI-shaped TTS, but this server streams raw `pcm`/`wav` or SSE deltas under a per-backend stream cap, whereas that pipeline adapts external OpenAI-compatible TTS providers inside a full speech-to-speech loop (**Synthesis**).

## Coverage and limits

- Inspected statically as the captured `docs/streaming.md` (SHA-256 `7d20149c…` matching `checksums.json`) plus the package README ledger; no server was started, no request was sent, no container was built, and no response format, field default, status code, or endpoint behavior was reproduced (**Synthesis**).[^vieneu-tts-docs]
- The server implementation `apps/openai_speech.py`, `examples/openai_speech_client.py`, the Dockerfiles, and the upstream repository/package are not in `raw/` and were not inspected, so implementation details (chunk-boundary splitting, watermark internals, SSE framing quirks) are the documentation's claims, not verified behavior (**Synthesis**).[^vieneu-tts-docs]
- Endpoint fields, defaults, and the environment table are version-specific and carry `stale_after: 2027-10-07` per the `tts` domain rule (**Synthesis**).[^vieneu-tts-docs]

[^vieneu-tts-docs]: [VieNeu-TTS supporting docs](../raw/vieneu-tts-docs/README.md) — locators: package README coverage ledger; `docs/streaming.md` §Running the server (launch variants `(a)`–`(d)`, environment table, one-worker/warm-up paragraph); §API (`POST /v1/audio/speech` field table, response headers and errors, `stream_format=sse` event shapes, other-endpoints table, Python/curl/browser/Pipecat client fences, `examples/openai_speech_client.py`); §Tuning and troubleshooting (`VIENEU_FUSED_FRAME=0`, `/health` readiness); SHA-256 recorded in `checksums.json`.
