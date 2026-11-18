---
type: Concept
title: Pydantic AI realtime voice agents
description: Pydantic AI's realtime interface — one `agent.realtime()` session over five providers (six products, ElevenLabs counting twice), with server-side tools, canonical message history, browser WebRTC sideband audio, a documented standard-run parity table, numbered limitations and Logfire spans.
tags: [pydantic-ai, realtime, voice, agents, observability]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-11-18T12:20:00Z }
stale_after: 2027-01-24
sources:
  - id: pydantic-voice-2026
    resource: ../raw/pydantic-ai-voice-agent/index.md
    scope: ../raw/pydantic-ai-voice-agent/
    kind: article
    revision: sha256:ec28218e80b8c5e850b7ea43153de48694567c727ac61b37e8c509dfb2b0a1d1
    title: "Realtime voice agents in Pydantic AI"
  - id: pydantic-realtime-docs
    resource: ../raw/realtime/overview/index.md
    scope: ../raw/realtime/overview/
    kind: documentation
    revision: sha256:fb0a3ffd5fc8372f86b5ad0dc7f85dd895134c0438b76d83aa9ec968812422ff
    title: "Realtime (speech-to-speech)"
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

The docs' own quickstart differs in three details worth carrying[^pydantic-realtime-docs]: it installs `pydantic-ai-slim[openai-realtime]` rather than the full package, it passes `send_audio()` an async iterator of chunks (`session.send_audio(microphone_chunks())`) rather than awaiting one chunk at a time, and it awaits `session.wait_for_playback()` before leaving the `async with` block so the speaker drains every generated chunk. Closing the session ends the speaker's stream but cannot stop the microphone, because that read is an external source, so the capture task is cancelled explicitly[^pydantic-realtime-docs] The capture and playback rates come from the model's profile and may differ between input and output[^pydantic-realtime-docs]

A session is also iterable, which is the general form of the two stream views: `send()` carries non-audio content in, and iterating the session yields the typed event stream — content, tool, turn, error and reconnect events[^pydantic-realtime-docs] The docs point at a per-page map for the rest: audio and transcripts, events, turns and interruptions, tools, capabilities and hooks, history and handoff, deployment, connection lifecycle, usage and observability, and a troubleshooting index by symptom[^pydantic-realtime-docs]

## What carries over from a text agent

The article's argument is that opening a realtime socket is a few lines in any SDK and the work is everything around the model; these are the parts it claims carry over[^pydantic-voice-2026]:

| Concern | Realtime behaviour |
| --- | --- |
| Tools | The same `@agent.tool` functions with their dependencies, validation and retries; each call runs in the background so it does not block the session, and [tool hooks](pydantic-ai-lifecycle-hooks.md) run as in a standard run |
| Capabilities | The same opt-in behaviours, third-party ones included, resolved once at connect time and their instructions re-read before each turn; some run-graph features such as output validators do not apply |
| Run hooks | `before_run`, `after_run`, `wrap_run` and `on_run_error` apply once around the whole session, because a session is one run |
| History | Spoken turns become the same `ModelRequest` / `ModelResponse` messages a text run produces, including tool calls, and transcripts when the provider supplies them |
| Event stream | The session is iterable, or a `ProcessEventStream` capability attaches to it — the `event_stream_handler` parameter is not available |
| Usage | `session.usage` accumulates tokens with audio and cached breakdowns, and `usage_limits` caps a runaway session the way it caps a run |
| Observability | The session emits OpenTelemetry spans as an agent run does, so Logfire or any other OTel backend reads it without special handling |

The four negative rows of the docs' parity table matter as much as the positive ones: `output_type` and output validators do not exist in a session and require delegation to a text agent, graph node and `before_model_request` hooks have no agent graph to attach to, history processors do not transform `message_history` at seeding, and `event_stream_handler` is replaced by `ProcessEventStream`[^pydantic-realtime-docs] One provider-specific exception sits on top of the parity: on OpenAI GPT-Live the `instructions` go to the backend model that does the delegated work rather than to the voice model the caller hears, which has its own `openai_live_instructions`[^pydantic-realtime-docs]

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

The docs draw the deployment as `device ↔ media bridge ↔ RealtimeSession ↔ provider`, with typed tools and message history hanging off the backend, and define the media bridge as whatever moves audio between the user's device and the backend — a browser WebSocket or a telephony bridge[^pydantic-realtime-docs] Their provider matrix narrows the WebRTC route: supported on OpenAI and on Azure except Voice Live, and absent on Gemini, xAI and ElevenLabs[^pydantic-realtime-docs]

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

## What a session cannot do

The docs keep a limitation table with issue numbers, which is the most concrete negative surface either source offers[^pydantic-realtime-docs]:

| Limitation | Tracking |
| --- | --- |
| SIP is not built in; telephony is bridged through a provider such as Twilio | Deployment page |
| A session's tools are fixed at connect, so `defer_loading=True` tools and tool-contributing capabilities are rejected (OpenAI and xAI accept mid-session tool updates) | [#7288](https://github.com/pydantic/pydantic-ai/issues/7288) |
| Realtime-specific exchange hooks do not exist yet; run and tool hooks plus session events are the substitutes | [#7190](https://github.com/pydantic/pydantic-ai/issues/7190) |
| Provider resumption handles cannot be persisted and resumed in another process | [#7302](https://github.com/pydantic/pydantic-ai/issues/7302) |
| Dynamic native-tool functions are resolved once, at connect | [#7288](https://github.com/pydantic/pydantic-ai/issues/7288) |
| History processors skip `message_history` at seeding; preprocess before opening when filtering or redaction is required | [#7299](https://github.com/pydantic/pydantic-ai/issues/7299) |
| A session cannot pause for tool approval: a `HandleDeferredToolCalls` handler resolves each request during the call, which can include waiting for a person | [#7301](https://github.com/pydantic/pydantic-ai/issues/7301) |
| `enqueue()` takes text and system-prompt parts, joined into one live-input turn; multimodal content and model responses are unsupported | [#7300](https://github.com/pydantic/pydantic-ai/issues/7300) |
| GPT-Live sends no end-of-turn frame, so `RealtimeTurnCompleteEvent` is inferred from silence | GPT-Live turn-boundary section |
| GPT-Live bills audio duration, and no `UsageLimits` field caps a session by duration; `cost_limit` bounds it once the duration is priced | [#8371](https://github.com/pydantic/pydantic-ai/issues/8371) |
| GPT-Live speaks only while receiving audio, so a session without a microphone needs `openai_live_idle_audio=True` or a typed turn runs the backend silently | GPT-Live text-input section |

The deferred row is narrower than it reads: per [on-demand capabilities](pydantic-ai-on-demand-capabilities.md), what a session rejects is a tool-contributing deferred capability and a `ctx.load_capability()` call, while the model can still load an instructions-only on-demand capability there with the `load_capability` tool.

The approval row is the one that changes an architecture: [deferred tool approval](pydantic-ai-deferred-approvals.md) normally returns a `DeferredToolRequests` to the caller and resumes later, which a live call cannot do, so the reviewer has to answer inside the session[^pydantic-realtime-docs] The seeding row cuts the other way — [capabilities](pydantic-ai-capability-primitive.md) whose instructions are re-read per turn still cannot filter the history a session starts from[^pydantic-realtime-docs]

## Other ways to build voice

The docs name two alternatives that sit outside the realtime loop[^pydantic-realtime-docs]:

- **Batch STT → text agent → TTS** — compose a standard agent with your own speech-to-text and text-to-speech services when a specific text model, structured output or independently chosen speech components matter.
- **Browser straight to the provider** — a provider-native, UI-only experience on an ephemeral token, where the provider's own SDK owns the session and there is no server-side agent loop, no tools and no shared history; this is not the WebRTC sideband route, where the browser owns only the media and the backend still runs the agent.

The provider matrix's `output_type` gap is what points at the first alternative: a call that must return validated structured data hands its history to a text agent instead[^pydantic-realtime-docs]

## Contradictions

The two captures disagree about the audio library in the runnable voice example, and neither names a version that would date the change:

- **Vendor article (2026-08-26):** the voice-assistant example fills its two audio placeholders with `sounddevice`[^pydantic-voice-2026]
- **Vendor docs overview (undated):** the same example fills them with [`listentome`](https://github.com/Kludex/listentome)[^pydantic-realtime-docs]

Neither is chosen here; the docs page is the likely later capture, since its installation command also differs from the article's, but it carries no date to prove it[^pydantic-realtime-docs] The structural point both agree on — the example is a runnable loop with two audio placeholders, not a `VoiceAgent` type — is unaffected[^pydantic-voice-2026][^pydantic-realtime-docs]

## Limits

- **Neither capture names a version** — the article names none, and the docs page names no Pydantic AI version, date, author or licence — so every API name here is version-unknown and the page stays `draft` under the `pydantic-ai` domain rule rather than being pinned to a release[^pydantic-voice-2026][^pydantic-realtime-docs]
- The article is dated 2026-08-26, before the v2.59.0 point release that [Pydantic AI v2 release](pydantic-ai-v2-release.md) records as adding `ElevenLabsRealtimeModel`: its four-provider sentence does not mention ElevenLabs. The docs page does, so the provider set above is the article's and the fuller set is the docs matrix[^pydantic-realtime-docs]
- Model identifiers (`openai:gpt-realtime-2.1`, `openai:gpt-5.6-sol`, `gemini-3.1-flash-live-preview`) are quoted as written and were not checked against any provider's model list[^pydantic-voice-2026]
- Nothing was installed, no session opened, no audio captured or played, no tool called, and the embedded public Logfire trace was read as a link, not fetched; every runtime claim is **Reported** in both captures[^pydantic-voice-2026][^pydantic-realtime-docs]
- Latency, interruption quality and per-provider audio fidelity are asserted qualitatively ("low latency", "interruptions feel natural") with no measurement, and the cost claim rests on one call[^pydantic-voice-2026]
- The docs parity and limitation tables are prose, not schema: no `RealtimeModelProfile` field list, no event-type enumeration, no per-provider accepted setting values, and the eleven limitations name issue numbers rather than fixes[^pydantic-realtime-docs]
- Coverage: the article package is a single `index.md` capture and the docs package a single `index.md` capture, neither with attachments, includes, downloads or supporting files; the docs page's own per-task sub-pages (audio, events, turns, tools, capabilities, history, deployment, lifecycle, observability, troubleshooting, API reference) were read as links, not followed[^pydantic-realtime-docs]

## Relationships

- **Is an interface on** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md)'s `Agent`: capabilities resolve at connect time, with run-graph features such as output validators excluded.
- **Traced by** [Pydantic AI observability](pydantic-ai-observability.md), which receives a session span, `user speech` and `chat` spans, and drop counters on the same wire format as a text run.
- **Routes through** [Pydantic AI Gateway](pydantic-ai-gateway.md), where a `gateway/<provider>:` model string adds one key, spend limits and routing to audio traffic billed per audio token or per minute.
- **Exchanges message history with** text runs, at the `all_messages()` / `message_history=` level that [Pydantic AI Conversation state](pydantic-ai-conversation-state.md) wraps in a serializable object.
- **Bounded by** the `usage_limits` mechanism in [Pydantic AI run controls](pydantic-ai-run-controls.md), which caps a session the way it caps a run, and by the exception that GPT-Live's duration billing has no `UsageLimits` field to cap it[^pydantic-realtime-docs]
- **Configured by** [Realtime provider support and settings](pydantic-ai-realtime-provider-support.md), which holds the six-provider capability matrix, profile resolution and the `RealtimeModelSettings` a provider may ignore, warn about or reject.
- **Deviates from** [deferred tool approval](pydantic-ai-deferred-approvals.md): a session cannot return `DeferredToolRequests` to a caller, so the reviewer answers during the call.
- **Contradicts** the docs page on the voice example's audio library (`sounddevice` versus `listentome`), recorded above, while both agree the provider set has grown past the article's four.

[^pydantic-voice-2026]: Douwe Maan, "Realtime voice agents in Pydantic AI", Pydantic, published 2026-08-26T09:00Z, 1,247 words as declared (1,299 by local `wc -w`), content digest sha256:ec28218e. Locators: opening paragraphs (raw lines 11–17) for voice-as-interface, the four providers, speech-to-speech without a pipeline, the backend-runs-the-agent rule and the two audio routes with WebRTC limited to OpenAI and Azure; §"A voice agent in one file" (lines 19–74) for `uv add "pydantic-ai[realtime]" logfire`, the `RealtimeSession` / `agent.realtime(...).session()` shape, `send_audio` / `stream_audio` / `stream_transcripts`, the PCM rate and mono format, `sounddevice` in the runnable example, and the "not a new `VoiceAgent` type" statement; §"What carries over" (lines 76–84) for server-side typed tools, background tool execution and the provider-specific speaking-while-waiting caveat, capabilities resolved at connect time with output validators excluded, canonical `ModelRequest` / `ModelResponse` history, `session.usage` with audio and cached breakdowns, `usage_limits`, and OTel instrumentation; §"One agent, many modalities" (lines 86–124) for the `SupportTicket` handoff, `message_history=session.all_messages()` and the reverse seeding claim; §"Portable across providers, and through the gateway" (lines 126–141) for the `RealtimeModel` interface, the normalized event vocabulary, the `profile` capability fields, and the two `gateway/` model strings with the audio-billing argument; §"Try it" (lines 143–153) for the extras table and the four example programs; §"See what the call did" (lines 155–165) for `pydantic_ai.all_messages`, the session / `user speech` / `chat` / tool spans, `pydantic_ai.audio_chunks_dropped` and `transcript_items_dropped`, the 61.87 s and $0.08 call, the "about $4.50" hourly figure, and the `agent_name` grouping. Local capture: `raw/pydantic-ai-voice-agent/index.md`. Evidence class: **Reported** — a vendor article about its own feature; no package installed, session opened, audio captured, tool called, or trace fetched, and the source names no Pydantic AI or Logfire version.
[^pydantic-realtime-docs]: Pydantic Docs, "Realtime (speech-to-speech)", <https://pydantic.dev/docs/ai/realtime/overview/>, 1,948 words as declared and 2,125 by local `wc -w` including frontmatter and markup, no publication date, author, licence or Pydantic AI version named; local capture `raw/realtime/overview/index.md`, 205 lines, content digest sha256:fb0a3ffd5fc8. §"Quickstart" (raw lines 17–82) for `pip install "pydantic-ai-slim[openai-realtime]"`, `OPENAI_API_KEY`, the `openai:gpt-realtime-2.1` session, `send_audio(microphone_chunks())` as an async iterator, `stream_audio()`, `stream_transcripts()`, `wait_for_playback()`, the close-versus-external-microphone cancellation, the profile-reported sample rates that may differ between input and output, and the `listentome` and text-to-audio example pointers; §"How sessions work" (84–95) for `RealtimeSession`, `send()`/`send_audio()`, the content/tool/turn/error/reconnect event stream, the `stream_audio()`/`stream_transcripts()` views, the `device ↔ media bridge ↔ RealtimeSession ↔ provider` diagram, and the media bridge and WebRTC-sideband descriptions; §"Learn by task" (97–109) for the eleven sub-page map including the troubleshooting index; §"Provider support" (111–131) for the seven-column matrix across OpenAI, Azure, Gemini, xAI and ElevenLabs, the canonical-provider-pages statement, and profile-based branching; §"Shared settings" (134–150) for `RealtimeModelSettings`, the construction and per-session precedence, the provider voice settings, the rule that agent `model_settings` and `get_model_settings()` do not configure a session, silent ignoring of `max_tokens`/`thinking`, the `UnsupportedSettingWarning` on `parallel_tool_calls=False`, the pre-connect `UserError` on a forcing `tool_choice`, and the raising `turn_detection=False` case; §"Relationship to standard agent runs" (152–182) for the `realtime()` parameter mirror, the GPT-Live instruction routing to the backend model with `openai_live_instructions`, and the parity table's run hooks, capabilities, event stream, `output_type` and validator, graph hook, history-processor and `event_stream_handler` rows; §"Other ways to build voice" (184–189) for the batch STT/agent/TTS composition and the browser-direct-to-provider ephemeral-token mode with no server-side loop; §"Limitations" (191–204) for the eleven rows and their issue numbers (#7288 twice, #7190, #7302, #7299, #7301, #7300, #8371) plus the unnumbered SIP, GPT-Live turn-boundary and `openai_live_idle_audio` rows. Evidence class: **Reported** — vendor documentation for its own feature; nothing installed, connected, captured or measured, and the per-task and provider sub-pages it declares canonical were read as links, not followed.
