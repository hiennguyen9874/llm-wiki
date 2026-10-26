---
title: "Realtime voice agents in Pydantic AI"
author: "Douwe Maan"
site: "Pydantic"
published: 2026-08-26T09:00:00.000Z
source: "https://pydantic.dev/articles/pydantic-ai-voice-agent"
domain: "pydantic.dev"
language: "en"
description: "Pydantic AI supports realtime speech-to-speech with server-side tools, shared history, browser WebRTC, and Logfire tracing across OpenAI, Azure, Gemini, and xAI."
word_count: 1247
---

A Pydantic AI [agent](https://ai.pydantic.dev/agent/) is a plain Python object with no interface baked in. The same agent already runs [as an object you call `run()` on](https://ai.pydantic.dev/agent/#running-agents), [in the terminal](https://ai.pydantic.dev/cli/), [behind a built-in web chat](https://ai.pydantic.dev/web/), and [streamed to your own frontend](https://ai.pydantic.dev/ui/overview/). Now it can hold a live, spoken conversation too. [Voice is just another interface](https://ai.pydantic.dev/interfaces/) on the agent you already have.

Under the hood it's realtime speech-to-speech: [OpenAI Realtime](https://ai.pydantic.dev/realtime/openai/), [Azure OpenAI](https://ai.pydantic.dev/realtime/azure/), [Gemini Live](https://ai.pydantic.dev/realtime/gemini/), and [xAI Grok Voice](https://ai.pydantic.dev/realtime/xai/), behind one provider-agnostic API. The model hears and speaks directly, with no transcribe-then-generate-then-synthesize pipeline in between, so latency is low and interruptions feel natural.

Your backend always runs the agent, so tools, history, and your API key stay server-side. The audio travels however suits your app: captured on the server, or, for a browser, [directly between the browser and the provider over WebRTC](https://ai.pydantic.dev/realtime/deployment/#browser-webrtc-server-sideband), with your backend attached to the same call as a sideband so nothing moves client-side but the audio. Browser WebRTC works on OpenAI and Azure OpenAI, with a [runnable FastAPI example](https://ai.pydantic.dev/examples/realtime-webrtc/) to start from.

## A voice agent in one file

Realtime lives behind an extra. Install [Logfire](https://pydantic.dev/logfire) next to it and the session traces itself:

```bash
uv add "pydantic-ai[realtime]" logfire
```

With the audio captured on the server, a voice agent is one session and three small loops (microphone in, speaker out, and a live transcript):

```python
import asyncio
import contextlib
from collections.abc import AsyncIterator

import logfire
from pydantic_ai import Agent
from pydantic_ai.realtime import RealtimeSession

logfire.configure()
logfire.instrument_pydantic_ai()

agent = Agent(instructions='You are a helpful voice assistant.')

@agent.tool_plain
async def get_weather(city: str) -> str:
    return f'Sunny in {city}'

async def stream_microphone(session: RealtimeSession) -> None:
    ...  # capture or resample 16-bit mono PCM at \`session.audio_input_sample_rate\` and \`await session.send_audio(chunk)\`

async def play_audio(chunks: AsyncIterator[bytes]) -> None:
    async for chunk in chunks:
        ...  # write the PCM chunk to your speaker

async def main():
    async with agent.realtime('openai:gpt-realtime-2.1').session() as session:
        mic = asyncio.create_task(stream_microphone(session))
        speaker = asyncio.create_task(play_audio(session.stream_audio()))

        async for part in session.stream_transcripts():  # live captions
            print(f'{part.speaker}: {part.transcript}')
            #> user: What's the weather like in Paris?
            #> assistant: It's sunny in Paris right now.
            if part.speaker == 'assistant':
                break  # one exchange; a real call keeps listening

    mic.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await mic
    await speaker

asyncio.run(main())
```

`send_audio()` streams the caller's microphone in, `stream_audio()` streams the spoken reply back, and `stream_transcripts()` gives you a live transcript of both sides. The [voice assistant example](https://ai.pydantic.dev/examples/realtime-voice/) fills the two audio placeholders in with `sounddevice`. That `agent` is not a new `VoiceAgent` type: it's the same `Agent`, and `get_weather` is your ordinary server-side tool, called mid-call. The two `logfire` lines are the whole of the observability setup.

## What carries over

Opening a realtime socket to a provider is a few lines in any SDK. The work is everything around the model: tools that actually run, history you can trust, costs you can see, and a security model that keeps your API key off the browser. That's the part Pydantic AI does, and it works the way it does for text agents:

- **Your typed tools run server-side.** The same tools you registered with `@agent.tool`, with their dependencies, validation, and retries. Each call runs in the background so it never blocks the session; whether the model keeps speaking while it waits is provider-specific.
- **Your [capabilities](https://ai.pydantic.dev/capabilities/overview/) carry over.** The same opt-in behaviors you compose onto a text agent, including third-party ones, resolve once at connect time. ([Some run-graph features](https://ai.pydantic.dev/realtime/capabilities/) like output validators don't apply.)
- **The session builds real message history.** Spoken turns become the same `ModelRequest` / `ModelResponse` messages a text run produces, including tool calls, and transcripts when the provider supplies them.
- **Usage and limits work.** `session.usage` accumulates tokens with audio and cached breakdowns; `usage_limits` caps a runaway session the same way it caps a run.
- **It's [instrumented](https://ai.pydantic.dev/realtime/observability/).** A realtime session emits OpenTelemetry spans the way an agent run does, so [Logfire](https://pydantic.dev/logfire) or any other OTel backend reads it without special handling.

## One agent, many modalities

Because a voice session records canonical message history, voice and text compose. Hand a finished call to a text agent for structured extraction:

```python
from typing import Literal

import logfire
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.realtime import RealtimeSession

logfire.configure()
logfire.instrument_pydantic_ai()

class SupportTicket(BaseModel):
    summary: str
    severity: Literal['low', 'medium', 'high']
    next_action: str

support_agent = Agent(instructions='You are a friendly support line. Keep replies short.')
notetaker = Agent('openai:gpt-5.6-sol', output_type=SupportTicket)

async def take_call(session: RealtimeSession) -> None:
    ...  # stream the caller's mic in and play replies back until they hang up

async def main():
    async with support_agent.realtime('openai:gpt-realtime-2.1').session() as session:
        await take_call(session)

    ticket = await notetaker.run(
        'Summarize this call as a support ticket.',
        message_history=session.all_messages(),
    )
    print(ticket.output)
```

The voice call and the text summary are two agents sharing one message history. It goes the other way too: seed a voice session with `message_history=` from an earlier text conversation and the caller picks up where they left off. The phone bot and the assistant in your app can be the same `Agent` with the same audit trail.

## Portable across providers, and through the gateway

Every provider implements the same `RealtimeModel` interface and normalizes into one typed event vocabulary, so the core of your event loop stays the same when your provider changes. Each model declares its capabilities on its `profile`: manual turn-taking, barge-in truncation, non-blocking tool calls, and the provider-native tools it supports, like Gemini's search grounding. You branch on what a model can do instead of discovering it mid-call.

Portability includes the [Pydantic AI Gateway](https://pydantic.dev/ai-gateway). Route a session through it by naming the upstream provider, and nothing else about your code changes:

```python
from pydantic_ai import Agent

agent = Agent(instructions='You are a helpful voice assistant.')

agent.realtime('gateway/openai:gpt-realtime-2.1')
agent.realtime('gateway/google:gemini-3.1-flash-live-preview')
```

Your voice traffic then gets the same single key, spend limits, and routing as your text traffic. Apart from obvious reasons, this matters for audio because realtime usage is billed by each provider's audio-token or per-minute pricing, so an unattended call can run up cost *very* fast.

## Try it

Realtime support ships in `pydantic-ai` today:

```bash
uv add "pydantic-ai[realtime]"
```

That covers OpenAI, Azure OpenAI, and Gemini Live, because the `pydantic-ai` package already bundles those SDKs. Add `[xai-realtime]` for xAI Grok Voice. On the lean `pydantic-ai-slim` package, name the provider yourself: `pydantic-ai-slim[openai-realtime]` (also covers Azure), `[google-realtime]`, or `[xai-realtime]`.

Start with the [realtime docs](https://ai.pydantic.dev/realtime/overview/), then pick an example: a [terminal voice assistant](https://ai.pydantic.dev/examples/realtime-voice/), the [browser WebRTC app](https://ai.pydantic.dev/examples/realtime-webrtc/), a [camera agent that watches and narrates](https://ai.pydantic.dev/examples/realtime-camera/), or [handing a call off to a text agent](https://ai.pydantic.dev/examples/realtime-handoff/).

## See what the call did

Voice arrives in the trace as text. Spoken turns land under `pydantic_ai.all_messages`, the attribute a text run already writes, with transcripts standing in for the audio.

One session span holds the whole call, with a `user speech` span for each stretch the caller talked and a `chat` span for each reply. A tool call mid-conversation gets its own span, with the arguments the model chose and what your function returned. `pydantic_ai.audio_chunks_dropped` and `transcript_items_dropped` count what the session could not keep up with.

Below is the agent trace from this post on a real call: four questions, three `execute_tool get_weather` spans, 61.87s costing $0.08, or about $4.50 for an hour of talking at that rate.

<iframe title="A realtime voice session in Pydantic Logfire" height="600" src="https://logfire-us.pydantic.dev/public-trace/8e71780e-c85f-402d-9653-532957a98e02?spanId=58d41866223b2e5a&amp;embedded=true&amp;theme=light"></iframe>

[Pydantic Logfire](https://pydantic.dev/logfire) files each session alongside your other agent runs, since the session span carries the same `agent_name` its Runs view groups on.

If you build something with it, or hit something that doesn't feel right, we want to hear about it, on [GitHub](https://github.com/pydantic/pydantic-ai) or in [Slack](https://logfire.pydantic.dev/docs/join-slack/).
