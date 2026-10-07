---
type: Concept
title: Speech-to-Speech Realtime Engine
description: Server architecture, OpenAI Realtime GA event surface, tool-calling paths, CancelScope interruption model, and WebSocket/WebRTC transports of the HF speech-to-speech realtime engine.
tags: [pipeline, streaming, realtime, tool-calling, barge-in]
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

The [HF speech-to-speech pipeline](speech-to-speech-pipeline.md) realtime engine is a FastAPI/uvicorn server that exposes the OpenAI Realtime GA protocol over WebSocket and WebRTC, giving each session a queue-backed `PipelineUnit` that owns its `RealtimeService`, turn tracker, and cancellation state while the packaged `local` command composes the same server with a microphone/speaker client over loopback (**Reported**).[^s2s-supporting-docs]

## Architecture and flow

- Per-session pipeline threads are VAD, STT, a `TranscriptionNotifier`, LLM, an `LMOutputProcessor`, and TTS, joined by queues and configured from a shared `RuntimeConfig` Pydantic model that VAD, LLM, and TTS read at processing time; `session.update` deep-merges into it so instructions, tools, voice, turn detection, and audio format change for later turns (**Reported**).[^s2s-supporting-docs]
- Inbound audio: clients send `input_audio_buffer.append` with base64 PCM; `RealtimeService` decodes, resamples to 16 kHz, splits into 512-sample chunks, and queues them for VAD (**Reported**).[^s2s-supporting-docs]
- VAD emits `speech_started` / `speech_stopped` on the text output queue and forwards full utterances to STT; `TranscriptionNotifier` emits `transcription.delta` / `transcription.completed`, after which `RealtimeService` commits the revision to conversation state and creates the LLM request (**Reported**).[^s2s-supporting-docs]
- `LMOutputProcessor` places each generated text/tool part, token usage, and matching TTS input on one queue so later parts and the response terminal cannot overtake them; TTS forwards ordered response events and PCM chunks that the router's `_send_loop` encodes as `response.output_audio.delta` (**Reported**).[^s2s-supporting-docs]

## Protocol event surface

- Client-to-server events: `input_audio_buffer.append`, `session.update`, `conversation.item.create` (inject `input_text` or `function_call_output` without triggering generation), `conversation.item.truncate` (accepted as an acknowledgement-free no-op for stock SDKs, because playback is client-owned and explicit `response.cancel` or server-VAD cancellation already discards provisional generation), `response.create` (with per-response `instructions` and `tool_choice` overrides), and `response.cancel` (**Reported**).[^s2s-supporting-docs]
- Server-to-client events include `session.created` / `session.updated`, `error` (e.g. `session_limit_reached`, `unknown_or_invalid_event`, `invalid_session_type`, `conversation_already_has_active_response`), `input_audio_buffer.speech_started` / `speech_stopped`, `conversation.item.created`, input-audio transcription `delta` / `completed`, the opt-in `speech_to_speech.input_audio_transcription.snapshot`, `response.created`, `response.output_audio.delta` / `.done`, `response.output_audio_transcript.delta` / `.done`, `response.function_call_arguments.done`, and `response.done` (**Reported**).[^s2s-supporting-docs]
- Terminal statuses: an explicit provider token limit or content filter ends a response `incomplete` with `max_output_tokens` / `content_filter`; provider failure ends it `failed` with a top-level `error`; cancellation keeps `cancelled` with reason `turn_detected` or `client_cancelled`. Partial output can reach the client, but the pipeline rolls back history for incomplete and failed responses, and a compatible provider that closes its stream without a terminal signal keeps prior completion behavior with a warning (**Reported**).[^s2s-supporting-docs]

## Transcription semantics

- Internal partial transcriptions are cumulative hypotheses; before emitting a delta the server compares consecutive hypotheses at normalized word boundaries and holds back the newest matching word, letting only confirmed growth beyond the per-item committed prefix reach the append-only stream, while unstable casing and edge punctuation wait for the final transcript (**Reported**).[^s2s-supporting-docs]
- Because the protocol has no transcript-retraction event, a partial that revises an already-emitted word is withheld, though later hypotheses can resume once they extend the committed prefix; clients should treat `conversation.item.input_audio_transcription.completed` as authoritative and replace any rendered partial for the same `item_id` (**Reported**).[^s2s-supporting-docs]
- Clients can opt in to `speech_to_speech.input_audio_transcription.snapshot` by advertising it in `session.update` extension list; snapshots carry the latest cumulative hypothesis on every progressive update, are display-only and keyed by `item_id`, and let bundled clients combine append-only deltas with speculative display until the authoritative completion releases per-item memory (**Reported**).[^s2s-supporting-docs]
- Assistant transcript chunks are emitted as `response.output_audio_transcript.delta` whose concatenation reproduces the single terminal `.done.transcript`, which arrives after `response.output_audio.done` and before `response.done`, including when cancellation closes an incomplete item; clients that consumed chunk-level done events must move live rendering to `delta` (**Reported**).[^s2s-supporting-docs]

## Tool calling

- Local LLM path (`transformers` / `mlx-lm`, `LanguageModelHandler`): tools from `session.update` become `FunctionTool` objects, each JSON Schema `parameters` is turned into a Python `inspect.Signature` via `signature_from_schema`, and `to_code_prompt()` renders a `def name(...): """docstring"""` block injected into the system prompt by a Jinja2 template instructing `<code>...</code>` wrapping (**Reported**).[^s2s-supporting-docs]
- After generation, `_extract_tools` regexes `<code>` blocks, `extract_function_calls_from_text` parses and validates each `name(kwargs)` call, and valid calls become `ResponseFunctionToolCall` dicts with generated `call_id`s (**Reported**).[^s2s-supporting-docs]
- The OpenAI API path (`ResponsesApiModelHandler`) passes tools natively as `tools=` to `client.responses.create` and receives structured `function_call` items with no prompt engineering or regex parsing, supporting per-response `tool_choice` overrides (**Reported**).[^s2s-supporting-docs]
- Both handlers yield ordered `AssistantTextPart` / `AssistantToolCallPart` values that `LMOutputProcessor` translates into `response.output_audio_transcript.delta` plus one terminal `.done`, and `response.function_call_arguments.done` per tool call (**Reported**).[^s2s-supporting-docs]
- Tool result flow: the client executes the tool and sends `conversation.item.create` with `type: "function_call_output"`; the service appends it to context and emits `conversation.item.created` without triggering generation; the client sends `response.create` only when the result must be spoken, and fire-and-forget actions (dance, emotion, head movement, stop, idle) can stop after `conversation.item.created` since the assistant should have spoken its lead-in before the call (**Reported**).[^s2s-supporting-docs]
- Packaged Python client contract: an importable module exposes `TOOLS` and an async `execute_tool(name, arguments)` returning `ToolResult(output, create_response=True|False)`; plain return values use the module-wide `CREATE_RESPONSE` fallback defaulting to `True`, and `--tool-module` opts the packaged `talk` / `local` client in (**Reported**).[^s2s-supporting-docs]
- Calls start as soon as `response.function_call_arguments.done` arrives, outputs are submitted in protocol `output_index` order (from `response.output_item.added`, or the terminal `response.output` when a compatible server omits it), and the client waits for the origin `response.done(status="completed")` before sending one public follow-up `response.create`; cancelled or incomplete responses cancel unsubmitted results (**Reported**).[^s2s-supporting-docs]
- Arguments are validated against the declared JSON Schema before the callback; unknown tools, malformed JSON, non-awaitable handlers, and handler failures become `function_call_output` errors that always request a recovery response even under a fire-and-forget default, and outstanding async handlers are cancelled on disconnect or shutdown (**Reported**).[^s2s-supporting-docs]

## Interruption handling

- Barge-in is cooperative across VAD, the router's `_send_loop`, and LLM/TTS via a shared `CancelScope` that replaces an older cancel-event-plus-discard-flag pair with a generation counter (`cancel_scope.generation`) plus a discard flag (`cancel_scope.discarding`) (**Reported**).[^s2s-supporting-docs]
- Pipeline threads capture the generation at response start and check `cancel_scope.is_stale(gen)` per streaming token; `cancel()` increments the generation so all prior generations become stale, and `response_done(gen)` clears the discard flag only for a matching-generation sentinel while `new_response()` / `reset()` also clear it (**Reported**).[^s2s-supporting-docs]
- Output is generation-tagged (`AudioOutput` chunks and `AssistantOutputEvent`s carry `cancel_generation`) and response-keyed: the send loop drops stale or non-current output while `discarding` is set, preserves provider-reported usage for billing, and lets output for a different key wait only while that key is pending; a superseded speculative response still sends a keyed lifecycle-only terminal so the router can cancel the active response without exposing stale content (**Reported**).[^s2s-supporting-docs]
- On `speech_started` while a response is active or pending, the send loop first emits `response.output_audio.done`, then a transcript `.done` when transcript text existed, then `response.done(status="cancelled", reason="turn_detected")`, then `input_audio_buffer.speech_started`, and only then increments the generation, flushes the output and text queues (preserving usage, sentinels, and user-side events), and clears `response_playing` (**Reported**).[^s2s-supporting-docs]
- The cancel fires only when the `SpeechStartedEvent.interrupt_response` flag is set and the session config's `turn_detection.interrupt_response` (default true) allows it; when disabled, speech during a response is transcribed but the response keeps playing (**Reported**).[^s2s-supporting-docs]
- Client `response.cancel` runs the same cancel when a response is active or queued, removes queued model requests while preserving pipeline-control sentinels, flushes queues with the same preservation rules, finishes the opened response with `status="cancelled"`, `reason="client_cancelled"`, and re-enables listening; with no active response, `cancel()` is not called so the discard guard cannot be set without a sentinel to clear it (**Reported**).[^s2s-supporting-docs]

## WebRTC transport

- The GA WebRTC handshake is `POST /v1/realtime/calls` with an SDP offer, answered `201` with a `Location: /v1/realtime/calls/{call_id}` header; audio then flows over RTP media tracks (Opus at 48 kHz, resampled to and from the 16 kHz pipeline with a stateful resampler) while all JSON events use the same protocol as WebSocket on the `oai-events` data channel (**Reported**).[^s2s-supporting-docs]
- A WebRTC session claims a pipeline unit from the same pool as WebSocket clients, and the per-unit send loop remains the sole consumer of pipeline output queues, handing PCM to the transport which paces 20 ms RTP frames and sends silence when idle (**Reported**).[^s2s-supporting-docs]
- Differences from WebSocket: `input_audio_buffer.append` is rejected with `invalid_event_for_transport` because audio arrives on the media track; `output_audio_buffer.clear` is WebRTC-only and flushes server-buffered unplayed audio on barge-in, cancellation, `response.cancel`, and VAD interruption; `session.created` is sent when the data channel opens rather than on connection (**Reported**).[^s2s-supporting-docs]
- ICE servers (STUN/TURN) are configured with a JSON `SPEECH_TO_SPEECH_ICE_SERVERS` env var; without it aiortc defaults apply (host candidates plus Google STUN), and deployments where clients cannot reach the server directly (symmetric NAT, containers without exposed UDP) need a TURN server (**Reported**).[^s2s-supporting-docs]
- The extra `pip install 'speech-to-speech[webrtc]'` is required, otherwise the handshake endpoint fails (**Reported**).[^s2s-supporting-docs]

## Official Agents SDK compatibility

- CI pins `@openai/agents` 0.14.3 and runs independent integration jobs against the SDK's stock `OpenAIRealtimeWebSocket` and `OpenAIRealtimeWebRTC` transports using a normal `RealtimeSession` with only its endpoint URL changed; no custom SDK transport is used (**Reported**).[^s2s-supporting-docs]
- The tested GA surface covers `session.update` with instructions, voice, tools, server VAD, and 24 kHz PCM config; microphone input and assistant audio on the transport's own channel; input and output transcription events; explicit cancellation; server-VAD barge-in; and function-call execution with follow-up — for both WebSocket and WebRTC (**Reported**).[^s2s-supporting-docs]
- This is the tested core GA surface, not full API equivalence: unlisted events, hosted features, and future SDK behaviors are not implied; one pinned-SDK gap is handled in the browser demo by using the stock transport's `sendEvent` hook to send an explicit `session.update` with `tools: []`, since 0.14.3 omits `tools` when the updated list is empty (**Reported**).[^s2s-supporting-docs]

## Relationships

- Part of [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md): this is the protocol/server layer of that pipeline's Realtime API (**Synthesis**).[^s2s-supporting-docs]
- Depends on [Silero VAD](silero-vad.md) for speech boundaries and [turn-detection models](turn-detection-models.md) / Smart Turn for speculative-turn gating; consult those pages for detector-level behavior (**Synthesis**).[^s2s-supporting-docs]
- Compare with [RealtimeVoiceChat](realtime-voice-chat.md) and [Voice Agent Frameworks](voice-agent-frameworks.md) for alternative browser-facing realtime stacks, and see [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) for transport-level interruption tradeoffs (**Synthesis**).[^s2s-supporting-docs]
- Produces measurements defined in [Speech-to-Speech Response Latency Instrumentation](speech-to-speech-latency-instrumentation.md), and its OpenAI-compatible backends are described in [Speech-to-Speech OpenAI-Compatible STT/TTS Backends](speech-to-speech-openai-compatible-backends.md) (**Synthesis**).[^s2s-supporting-docs]

## Coverage and limits

- Source inspected statically only: the engine README was read as captured Markdown; no server was launched, no WebSocket/WebRTC session was opened, no SDK test was executed, and no tool call was run, so architecture, event, cancellation, and compatibility claims are source assertions transcribed without independent verification (**Synthesis**).[^s2s-supporting-docs]
- The README documents the tested GA subset and its interruption model but publishes no measured barge-in latency, cancellation-loss, or concurrency figures; the pinned-SDK matrix is a per-release test claim and can drift with `@openai/agents` versions (**Reported**).[^s2s-supporting-docs]
- Protocol field names, event names, error codes, the `@openai/agents` 0.14.3 pin, and `SPEECH_TO_SPEECH_ICE_SERVERS` carry `stale_after: 2027-10-07` under the `pipeline` domain rule (**Synthesis**).[^s2s-supporting-docs]

[^s2s-supporting-docs]: [huggingface/speech-to-speech supporting docs](../raw/speech-to-speech-docs/README.md) — a capture at upstream revision `f9c23282a564cbe5b1f015ccb36d58e941de8520` (2026-10-07). Locators: `src/speech_to_speech/api/openai_realtime/README.md` → "Realtime Engine -- High-Level Architecture" (mermaid flow plus six-step key flow), "Supported OpenAI Realtime Events" (client-to-server and server-to-client tables), "Terminal status details", "Official Agents SDK compatibility" matrix plus pinned-0.14.3 gap, "Input transcription semantics", "Speculative input transcription snapshots", "Transcript event compatibility", "WebRTC Transport" (`POST /v1/realtime/calls`, `oai-events`, `output_audio_buffer.clear`, `SPEECH_TO_SPEECH_ICE_SERVERS`), "Tool Calling Design" (local vs API paths, common output, tool result flow, packaged Python client tools, ordering rules), "Interruption Handling" (`CancelScope` design, sequence diagram, eight numbered steps), and "Testing" fences; `src/speech_to_speech/LLM/README.md` → backend list and language-control behavior; `src/speech_to_speech/arguments_classes/realtime_server_arguments.py` → `host`/`port` defaults. Limitations: `examples/`, `archive/`, `demo/CONTEXT.md`, `demo/DESIGN.md`, `demo/docs/adr/`, `docs/releases/`, `AGENTS.md`, tests, and implementation sources are excluded by the capture, so internal implementation beyond the README descriptions is not established here.
