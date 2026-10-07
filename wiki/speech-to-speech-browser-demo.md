---
type: Concept
title: Speech-to-Speech Browser Demo
description: Deployment, transport, metering, tool, and audio-buffer behavior of the HF Realtime Voice browser demo that speaks the OpenAI Realtime GA protocol to the HF speech-to-speech backend over WebSocket or WebRTC.
tags: [pipeline, streaming, realtime, deployment]
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

The HF Realtime Voice demo is a browser voice-chat UI for the [HF speech-to-speech](speech-to-speech-pipeline.md) backend that speaks the OpenAI Realtime **GA** protocol over WebSocket (default) or WebRTC; both choices run one `RealtimeSession` adapter over the pinned official `@openai/agents` package's stock transport classes, keeping demo-only queue, audio, visualization, device, camera, and metering behavior out of the protocol implementation (**Reported**).[^s2s-supporting-docs]

## Local quick start

- Start the backend from the repo root, for example `uv run speech-to-speech serve --stt parakeet-tdt --llm_backend transformers --tts kokoro --model_name "Qwen/Qwen3-4B-Instruct-2507" --llm_device mps --llm_torch_dtype float16 --enable_live_transcription`; the realtime server listens on `ws://localhost:8765/v1/realtime` by default (**Reported**).[^s2s-supporting-docs]
- Install the pinned browser SDK and start the app: `npm ci --prefix demo`, `uv pip install -r demo/requirements.txt`, export `SPEECH_TO_SPEECH_URL=ws://localhost:8765/v1/realtime`, optionally `SERPER_API_KEY` (web search is disabled without it) and `STARTUP_GREETING`, then `uv run uvicorn --app-dir demo server:app --reload --port 7860`; a Docker build/run path is also documented (**Reported**).[^s2s-supporting-docs]
- Browsers require HTTPS or `localhost` for `getUserMedia()` (mic and camera); `127.0.0.1` and `localhost` both work, but plain `http://192.168.x.y` does not, and `websocat ws://localhost:8765/v1/realtime` should return `session.created` immediately as a backend smoke test (**Reported**).[^s2s-supporting-docs]
- The backend exposes one concurrent session per pipeline unit, expanded with `--num_pipelines` (**Reported**).[^s2s-supporting-docs]

## Response timings panel

- Opening a conversation and expanding **Server timings** beneath a response shows E2E (estimated speech end to first generated audio), VAD end decision, Smart Turn decision, transcription, response generation, voice synthesis to first audio, and hold time before response, with E2E visible in the collapsed summary; MLX lock wait appears only in macOS terminal logs (**Reported**).[^s2s-supporting-docs]
- Tool-only responses get their own timing entry and follow-ups do not repeat STT; these are server measurements excluding browser buffering and playback, stages can overlap and must not be summed, and missing stages display **Unavailable** (**Reported**).[^s2s-supporting-docs]
- Older servers, absent metadata, and unsupported or malformed records leave the transcript unchanged; timings become available when the response finishes, including interrupted, failed, and incomplete responses. Validation is `npm run test:agents:adapter` for parsing/adapter behavior and `npm run test:ui` for the desktop and phone-width history display (**Reported**).[^s2s-supporting-docs]

## Transports and connection modes

- WebRTC uses the SDK's stock transport, adding the mic track and a data channel to an `RTCPeerConnection` and POSTing the SDP offer to a same-origin `/api/calls` proxy that forwards to the backend's `POST /v1/realtime/calls`; the proxy exists because the s2s server has no CORS middleware and forwards only to the env-pinned URL, never a client-supplied one, so it cannot be an open proxy (**Reported**).[^s2s-supporting-docs]
- Only the handshake goes through the proxy: negotiated audio (Opus RTP both ways) and the data channel flow directly browser↔backend, JSON events use the same GA protocol as WebSocket, mic audio rides the media track (never `input_audio_buffer.append`, which the backend rejects over WebRTC), the assistant voice arrives as a remote track, and barge-in flushing is server-side. The backend needs the `webrtc` extra or `/v1/realtime/calls` answers 501 (**Reported**).[^s2s-supporting-docs]
- WebRTC caveats versus WebSocket: user-recording replay uses the exact `input_audio_buffer.append` frames so it is WebSocket-only; NAT uses host ICE candidates by default with `RTC_ICE_SERVERS` on the demo and `SPEECH_TO_SPEECH_ICE_SERVERS` on the backend and no TURN relay fallback; the noise gate is in the WebSocket capture worklet so WebRTC sends the raw mic track; camera snapshots are re-encoded to about 60 KB per data-channel message; and load-balancer mode is WebSocket-only (**Reported**).[^s2s-supporting-docs]
- Connection mode is picked by environment: `SPEECH_TO_SPEECH_URL` (highest priority, browser connects directly to a read-only locked URL, WS or WebRTC, disables LB/queue/metering/sign-in); neither env set (user-pasted URL, WS only); `LOAD_BALANCER_URL` plus `SPACE_ID` (LB `/api/session` proxy, hidden URL field, WS only, metering on, OAuth HF token forwarded via `X-Reachy-Mini-Authorization`); or `LOAD_BALANCER_URL` alone (LB proxy, WS only, metering off) (**Reported**).[^s2s-supporting-docs]
- **Docker + host backend**: WebRTC is dialed server-side from inside the container, so `host.docker.internal` resolves and works, while WebSocket is dialed client-side by the host browser where `host.docker.internal` is not a real DNS name and the connection silently fails; a single `SPEECH_TO_SPEECH_URL` can therefore make only one transport work (`localhost:8765` for WebSocket, `host.docker.internal:8765` for WebRTC), and running the demo without Docker collapses the namespaces so `ws://localhost:8765/v1/realtime` works for both (**Reported**).[^s2s-supporting-docs]
- **Settings → Restart** reconnects with the current voice, instructions, and URL; settings are stored in `localStorage` (server URL, transport, mic, speakers, Qwen3-TTS voice name, and instructions), and Chrome/Edge can switch output devices live via `AudioContext.setSinkId` while other browsers keep the system default (**Reported**).[^s2s-supporting-docs]

## Greeting, tools, and usage limits

- By default each connection creates one hidden user item asking the model for a brief greeting and then requests a response, which opens the conversation naturally and warms the same prompt prefix used by the first spoken turn; `STARTUP_GREETING` customizes it and an empty value disables automatic generation (**Reported**).[^s2s-supporting-docs]
- The assistant can call a web-search tool (Google results via Serper.dev, proxied server-side so the key never reaches the browser) and a camera tool (while enabled, a live self-view sends the current frame to the vision-language model) (**Reported**).[^s2s-supporting-docs]
- Conversation time is metered per UTC day by sign-in tier **only on the deployed Space**, when both `LOAD_BALANCER_URL` and `SPACE_ID` are present; running locally leaves it unmetered even with `LOAD_BALANCER_URL` exported (**Reported**).[^s2s-supporting-docs]
- Limit environment variables: `LIMIT_ANON_SEC=300`, `LIMIT_FREE_SEC=600`, `LB_HF_TOKEN` falls back to user OAuth, `UNLIMITED_ORGS` adds unlimited orgs, and `USAGE_HASH_SECRET` HMACs identity keys and signs the anonymous cookie; PRO members are always unlimited and `cerebras`, `HuggingFaceM4`, `smolagents`, and `pollen-robotics` are unlimited out of the box, shown as "Team" (**Reported**).[^s2s-supporting-docs]

## Audio pipeline notes

- The WebSocket playback startup buffer (Settings → Playback startup buffer, ms) defaults to 0 (immediate playback), is saved per browser and applies on the next conversation, and does not affect WebRTC or the Python client's `--playback-buffer-ms`; missing, invalid, or negative values fall back to the default (**Reported**).[^s2s-supporting-docs]
- Buffering counts PCM samples, not elapsed time; after the threshold later chunks stream immediately without rebuffering, completed short and valid incomplete responses release their remaining audio, and interruption/cancellation/failure/disconnect discard pending audio. In upstream issue #557, 1200 ms resolved glitches in the reporter's local TTS setup, presented explicitly as a tuning example rather than a universal optimum because larger values add startup latency and no finite reserve prevents all underruns from sustained slower-than-realtime generation (**Reported**).[^s2s-supporting-docs]
- Input uses `getUserMedia({ echoCancellation, noiseSuppression, autoGainControl })` feeding the `mic-capture` worklet, which resamples the `AudioContext` rate to 24 kHz and packs Int16 LE; the entry module, realtime client, and both worklet URLs share the `audio-24k-v2` cache key, and the client waits for the capture worklet to report the same version and a 24 kHz output rate before opening a session, so the key and `AUDIO_WORKLET_VERSION` must be bumped together when the browser-audio contract changes (**Reported**).[^s2s-supporting-docs]
- User replay keeps a bounded in-memory copy of PCM actually sent, selects each utterance with `speech_started` / `speech_stopped` timestamps, and wraps it as an in-memory WAV; output decodes `response.output_audio.delta` to Int16 → Float32 and posts to the `audio-playback` worklet, which uses a per-context ring buffer, linearly interpolates 24 → 48, and applies short 32-frame fades to suppress clicks (**Reported**).[^s2s-supporting-docs]
- Barge-in: server VAD and explicit SDK interruptions clear the WebSocket playback queue; the worklet acknowledges with rendered PCM counts per item/content part (excluding startup delay and underrun silence) and the client sends `conversation.item.truncate` for unheard audio using those counts, retaining identities after audio/response done and overriding the SDK's receipt-time interruption clock; the local server currently accepts truncation events without changing conversation history, so these client counts do not establish server-side truncation (**Reported**).[^s2s-supporting-docs]

## Relationships

- Client for [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) and exercises [Speech-to-Speech Response Latency Instrumentation](speech-to-speech-latency-instrumentation.md) through its Server timings panel (**Synthesis**).[^s2s-supporting-docs]
- Its WebRTC/WebSocket plumbing and server-side barge-in flushing are described in [Speech-to-Speech Realtime Engine](speech-to-speech-realtime-engine.md), and its WebRTC ICE environment pairs with that engine's `SPEECH_TO_SPEECH_ICE_SERVERS` (**Synthesis**).[^s2s-supporting-docs]
- Compare with [RealtimeVoiceChat](realtime-voice-chat.md) as another browser-facing Realtime voice UI over a different backend stack (**Synthesis**).[^s2s-supporting-docs]

## Coverage and limits

- Source inspected statically only: the demo README was read as captured Markdown; no browser, Docker image, backend server, or SDK test was run and no microphone session or latency panel was exercised, so deployment, transport, metering, and buffer claims are source assertions transcribed without independent verification (**Synthesis**).[^s2s-supporting-docs]
- The README documents behavior but publishes no measured browser-side E2E, jitter, or underrun statistics; the only quantitative tuning datum is the issue #557 example, which the source itself labels non-universal (**Reported**).[^s2s-supporting-docs]
- Environment-variable names, limit defaults, the `audio-24k-v2` cache key, the pinned `@openai/agents` dependency, and the `ws://localhost:8765/v1/realtime` endpoint carry `stale_after: 2027-10-07` under the `pipeline` domain rule (**Synthesis**).[^s2s-supporting-docs]

[^s2s-supporting-docs]: [huggingface/speech-to-speech supporting docs](../raw/speech-to-speech-docs/README.md) — a capture at upstream revision `f9c23282a564cbe5b1f015ccb36d58e941de8520` (2026-10-07). Locators: `demo/README.md` → Hugging Face Space frontmatter, "Response timings" (tool-only entries, overlap caveat, `npm run test:*` validation), "Quick start (local)" (backend fence, npm/uvicorn env, HTTPS/mic requirement, websocat smoke test), "How it works" (five steps, one session per pipeline unit), Docker + host backend blockquote (WebRTC server-side vs WebSocket client-side dialing), "WebRTC transport" (SDK transport, `/api/calls` proxy scope, caveats list), "Connecting to a backend" mode table, "Startup greeting", "Tools", "Usage limits (deployed Space only)" table and tier list, "Settings (stored in `localStorage`)" table, and "Audio pipeline notes" (startup buffer, issue #557, `audio-24k-v2` cache key, user replay, output worklet, barge-in/truncation). Limitations: `demo/CONTEXT.md`, `demo/DESIGN.md`, `demo/docs/adr/`, `docs/releases/`, `examples/`, and implementation sources are excluded by the capture, so the adapter and server internals beyond the README description are not established here.
