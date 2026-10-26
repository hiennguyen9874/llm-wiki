---
type: Concept
title: Pydantic AI realtime voice agents
description: Pydantic AI's realtime interface — one `agent.realtime()` session over OpenAI Realtime, Azure, Gemini Live and xAI Grok Voice, with server-side tools, canonical message history, browser WebRTC sideband audio and Logfire spans.
tags: [pydantic-ai, realtime, voice, agents, observability]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T05:10:00Z }
stale_after: 2027-01-24
sources:
  - id: pydantic-voice-2026
    resource: ../raw/pydantic-ai-voice-agent/index.md
    scope: ../raw/pydantic-ai-voice-agent/
    kind: article
    revision: sha256:ec28218e80b8c5e850b7ea43153de48694567c727ac61b37e8c509dfb2b0a1d1
    title: "Realtime voice agents in Pydantic AI"
---

Realtime voice is **another interface on the agent you already have**, not a new agent type: the same `Agent` object that answers `run()`, serves the terminal and web chat, and streams to your own frontend now also opens a speech-to-speech session with `agent.realtime(...)`[^pydantic-voice-2026] The transport is realtime speech-to-speech — the model hears and speaks directly, with no transcribe-then-generate-then-synthesize pipeline — behind one provider-agnostic API covering OpenAI Realtime, Azure OpenAI, Gemini Live and xAI Grok Voice[^pydantic-voice-2026] The architectural claim the article builds on is that the backend always runs the agent, so tools, message history and the provider API key stay server-side while the audio travels by whichever route the app needs[^pydantic-voice-2026]

## One session, three streams

The install is the framework package plus the realtime extra, and adding Logfire beside it makes the session trace itself[^pydantic-voice-2026]:

```bash
uv add "pydantic-ai[realtime]" logfire
```

A server-captured voice agent is one `RealtimeSession` inside `async with agent.realtime('openai:gpt-realtime-2.1').session()`, with three concurrent streams[^pydantic-voice-2026]:

- `await session.send_audio(chunk)` — caller audio in. Chunks must be 16-bit mono PCM at `session.audio_input_sample_rate`, so capture or resample to that rate first.
- `session.stream_audio()` — the spoken reply out, as an async iterator of PCM chunks.
- `session.stream_transcripts()` — live captions for both sides, each part carrying `.speaker` and `.transcript`.

The documented example runs the microphone loop and the speaker loop as `asyncio` tasks and breaks the transcript loop after one assistant turn; the runnable voice-assistant example fills the two audio placeholders with `sounddevice`[^pydantic-voice-2026] The important negative finding is structural: there is no `VoiceAgent` class, and `get_weather` in the example is the ordinary `@agent.tool_plain` function, called mid-call[^pydantic-voice-2026]

## What carries over from a text agent

The article's argument is that opening a realtime socket is a few lines in any SDK and the work is everything around the model; these are the parts it claims carry over[^pydantic-voice-2026]:

| Concern | Realtime behaviour |
| --- | --- |
| Tools | The same `@agent.tool` functions with their dependencies, validation and retries; each call runs in the background so it does not block the session |
| Capabilities | The same opt-in behaviours, third-party ones included, resolved once at connect time; some run-graph features such as output validators do not apply |
| History | Spoken turns become the same `ModelRequest` / `ModelResponse` messages a text run produces, including tool calls, and transcripts when the provider supplies them |
| Usage | `session.usage` accumulates tokens with audio and cached breakdowns, and `usage_limits` caps a runaway session the way it caps a run |
| Observability | The session emits OpenTelemetry spans as an agent run does, so Logfire or any other OTel backend reads it without special handling |

Whether the model keeps speaking while a tool runs is stated as provider-specific, so "non-blocking" describes the session, not the caller's experience[^pydantic-voice-2026] The capability caveat is one sentence with one named example: which run-graph features are unavailable beyond output validators is not enumerated[^pydantic-voice-2026]

## Voice and text share one history

Because a session records canonical message history, a finished call can be handed to a text agent for structured extraction: the documented shape is a `support_agent` running the realtime session, then a separate `notetaker = Agent('openai:gpt-5.6-sol', output_type=SupportTicket)` invoked with `message_history=session.all_messages()`[^pydantic-voice-2026] The reverse direction is claimed too — seeding a voice session with `message_history=` from an earlier text conversation — with the framing that the phone bot and the in-app assistant can be the same agent with the same audit trail[^pydantic-voice-2026] The mechanism is message-level, not the serializable thread object described in [Pydantic AI Conversation state](pydantic-ai-conversation-state.md): the source names `all_messages()` and `message_history=` only[^pydantic-voice-2026]

## Provider portability and the capability profile

Every provider implements one `RealtimeModel` interface and normalizes into one typed event vocabulary, so the event loop stays the same across providers[^pydantic-voice-2026] Each model declares its abilities on its `profile` — manual turn-taking, barge-in truncation, non-blocking tool calls, and provider-native tools such as Gemini's search grounding — so code branches on declared capability instead of discovering behaviour mid-call[^pydantic-voice-2026] The source names the profile fields but gives no schema, no per-provider profile table, and no example of the branching code[^pydantic-voice-2026]

## Deployment shape: server-captured audio or browser WebRTC

Two audio routes are described, both with the backend still running the agent[^pydantic-voice-2026]:

- **Server capture** — the backend reads the microphone stream and plays the reply, as in the one-file example.
- **Browser WebRTC with server-side sideband** — audio flows directly between browser and provider, and the backend attaches to the same call as a sideband, so nothing but audio moves client-side.

Browser WebRTC is claimed for OpenAI and Azure OpenAI only, with a runnable FastAPI example to start from; the article names no example or limitation for Gemini Live or xAI over WebRTC[^pydantic-voice-2026]

## Routing voice through the gateway

Realtime sessions route through the [Pydantic AI Gateway](pydantic-ai-gateway.md) by naming the upstream provider in the model string, with no other code change: `agent.realtime('gateway/openai:gpt-realtime-2.1')` and `agent.realtime('gateway/google:gemini-3.1-flash-live-preview')`[^pydantic-voice-2026] Voice traffic then shares the gateway's single key, spend limits and routing with text traffic[^pydantic-voice-2026] The stated reason this matters more for audio than for text is billing shape: realtime usage is metered by each provider's audio-token or per-minute pricing, so an unattended call can run up cost very fast[^pydantic-voice-2026]

## Install extras

Extras differ between the full package and the slim one because `pydantic-ai` already bundles the OpenAI, Google and Azure SDKs[^pydantic-voice-2026]:

| Package | Extras | Covers |
| --- | --- | --- |
| `pydantic-ai` | `[realtime]` | OpenAI, Azure OpenAI, Gemini Live |
| `pydantic-ai` | `[xai-realtime]` | xAI Grok Voice |
| `pydantic-ai-slim` | `[openai-realtime]` | OpenAI and Azure |
| `pydantic-ai-slim` | `[google-realtime]` | Gemini Live |
| `pydantic-ai-slim` | `[xai-realtime]` | xAI Grok Voice |

## What the trace shows

Voice arrives in the trace as text: spoken turns land under `pydantic_ai.all_messages`, the attribute a text run already writes, with transcripts standing in for the audio[^pydantic-voice-2026] One session span holds the whole call, with a `user speech` span for each stretch the caller talked and a `chat` span for each reply; a mid-conversation tool call gets its own span carrying the arguments the model chose and what the function returned[^pydantic-voice-2026] Two counters record what the session could not keep up with — `pydantic_ai.audio_chunks_dropped` and `transcript_items_dropped` — without the source defining the threshold or unit behind either[^pydantic-voice-2026]

The worked call in the article is four questions, three `execute_tool get_weather` spans, 61.87 s and $0.08[^pydantic-voice-2026] The article rounds that to "about $4.50 for an hour of talking at that rate"; recomputing from the two stated numbers gives ≈ $4.65 per hour, so the hourly figure carries the rounding of a sub-cent call duration rather than a measured hourly rate (**Synthesis**)[^pydantic-voice-2026] The session span carries the same `agent_name` the Runs view groups on, which is why Logfire files a call beside the agent's text runs[^pydantic-voice-2026] See [Pydantic AI observability](pydantic-ai-observability.md) for the surrounding instrumentation and [Logfire MCP server](logfire-mcp-server.md) for querying the resulting spans.

## Limits

- **No version is named anywhere in the source**, so every API name here is version-unknown; the page stays `draft` under the `pydantic-ai` domain rule rather than being pinned to a release[^pydantic-voice-2026]
- The article is dated 2026-08-26, before the v2.59.0 point release that [Pydantic AI v2 release](pydantic-ai-v2-release.md) records as adding `ElevenLabsRealtimeModel` — a realtime model this provider list does not mention (**Synthesis**): the provider set here is the article's, not a current one.
- Model identifiers (`openai:gpt-realtime-2.1`, `openai:gpt-5.6-sol`, `gemini-3.1-flash-live-preview`) are quoted as written and were not checked against any provider's model list[^pydantic-voice-2026]
- Nothing was installed, no session opened, no audio captured or played, no tool called, and the embedded public Logfire trace was read as a link, not fetched; every runtime claim is **Reported**[^pydantic-voice-2026]
- Latency, interruption quality and per-provider audio fidelity are asserted qualitatively ("low latency", "interruptions feel natural") with no measurement, and the cost claim rests on one call[^pydantic-voice-2026]
- Coverage: the source package is a single `index.md` capture with no attachments, includes, or downloads; its documentation and example links were read as links, not followed.

## Relationships

- **Is an interface on** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md)'s `Agent`: capabilities resolve at connect time, with run-graph features such as output validators excluded.
- **Traced by** [Pydantic AI observability](pydantic-ai-observability.md), which receives a session span, `user speech` and `chat` spans, and drop counters on the same wire format as a text run.
- **Routes through** [Pydantic AI Gateway](pydantic-ai-gateway.md), where a `gateway/<provider>:` model string adds one key, spend limits and routing to audio traffic billed per audio token or per minute.
- **Exchanges message history with** text runs, at the `all_messages()` / `message_history=` level that [Pydantic AI Conversation state](pydantic-ai-conversation-state.md) wraps in a serializable object.
- **Bounded by** the `usage_limits` mechanism in [Pydantic AI run controls](pydantic-ai-run-controls.md), which caps a session the way it caps a run.
- **Contradicts no concept**, but its four-provider list predates the `ElevenLabsRealtimeModel` recorded in [Pydantic AI v2 release](pydantic-ai-v2-release.md).

[^pydantic-voice-2026]: Douwe Maan, "Realtime voice agents in Pydantic AI", Pydantic, published 2026-08-26T09:00Z, 1,247 words as declared (1,299 by local `wc -w`), content digest sha256:ec28218e. Locators: opening paragraphs (raw lines 11–17) for voice-as-interface, the four providers, speech-to-speech without a pipeline, the backend-runs-the-agent rule and the two audio routes with WebRTC limited to OpenAI and Azure; §"A voice agent in one file" (lines 19–74) for `uv add "pydantic-ai[realtime]" logfire`, the `RealtimeSession` / `agent.realtime(...).session()` shape, `send_audio` / `stream_audio` / `stream_transcripts`, the PCM rate and mono format, `sounddevice` in the runnable example, and the "not a new `VoiceAgent` type" statement; §"What carries over" (lines 76–84) for server-side typed tools, background tool execution and the provider-specific speaking-while-waiting caveat, capabilities resolved at connect time with output validators excluded, canonical `ModelRequest` / `ModelResponse` history, `session.usage` with audio and cached breakdowns, `usage_limits`, and OTel instrumentation; §"One agent, many modalities" (lines 86–124) for the `SupportTicket` handoff, `message_history=session.all_messages()` and the reverse seeding claim; §"Portable across providers, and through the gateway" (lines 126–141) for the `RealtimeModel` interface, the normalized event vocabulary, the `profile` capability fields, and the two `gateway/` model strings with the audio-billing argument; §"Try it" (lines 143–153) for the extras table and the four example programs; §"See what the call did" (lines 155–165) for `pydantic_ai.all_messages`, the session / `user speech` / `chat` / tool spans, `pydantic_ai.audio_chunks_dropped` and `transcript_items_dropped`, the 61.87 s and $0.08 call, the "about $4.50" hourly figure, and the `agent_name` grouping. Local capture: `raw/pydantic-ai-voice-agent/index.md`. Evidence class: **Reported** — a vendor article about its own feature; no package installed, session opened, audio captured, tool called, or trace fetched, and the source names no Pydantic AI or Logfire version.
