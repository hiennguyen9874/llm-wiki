---
type: Concept
title: Realtime provider support and settings
description: Which realtime providers Pydantic AI supports and what each can do — the six-provider capability matrix, profile resolution for sample rates and feature flags, and the shared `RealtimeModelSettings` a provider may ignore or reject.
tags: [pydantic-ai, realtime, voice, providers, model-settings]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:46:00Z }
stale_after: 2027-02-16
sources:
  - id: pydantic-realtime-docs
    resource: ../raw/realtime/overview/index.md
    scope: ../raw/realtime/overview/
    kind: documentation
    revision: sha256:fb0a3ffd5fc8372f86b5ad0dc7f85dd895134c0438b76d83aa9ec968812422ff
    title: "Realtime (speech-to-speech)"
  - id: pydantic-docs-timeouts
    resource: ../raw/core-concepts/timeouts/index.md
    scope: ../raw/core-concepts/timeouts/
    kind: documentation
    revision: sha256:f05691956599cfeccf1de6aa3383a528e516d06310baf5db2d282edda7bd852f
    title: "Timeouts"
---

Realtime portability in Pydantic AI is a promise about the interface, not about behaviour: every provider implements the same `RealtimeModel`, but the docs publish a seven-column capability matrix showing that audio output is the only column all of them tick, and they direct portable code to branch on `RealtimeModelProfile` flags instead of provider names[^pydantic-realtime-docs]. Settings split along the same seam — `RealtimeModelSettings` carries what providers share, each provider's voice controls live on its own settings class, and a shared setting a provider cannot apply is silently ignored, warned about, or rejected before the connection opens[^pydantic-realtime-docs]. This page covers that matrix and those settings; the session loop itself is compiled in [Pydantic AI realtime voice agents](pydantic-ai-realtime-voice.md).

## The capability matrix

Five provider rows and seven capability columns, as printed[^pydantic-realtime-docs]:

| Provider | Audio out | Image in | Text out | Browser WebRTC | Async tool calls | Thinking | State-restoring reconnect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI | ✓ | ✓ (GPT-Live: backend only) | ✓ (GPT-Live: ✗) | ✓ | ✓ | `gpt-realtime-2*`; GPT-Live's backend | Replays local history (GPT-Live: as text, forks a stored session, or re-attaches a WebRTC sideband) |
| Azure OpenAI | ✓ | ✓ | ✓ | ✓, not on Voice Live | ✓ | `gpt-realtime-2*`, and `gpt-5`-class models on Voice Live | Replays local history |
| Google Gemini | ✓ | ✓ | Vertex `gemini-live-2.5-flash` only | ✗ | Opt-in on native-audio and `gemini-3.8-live`; always on for extended thinking | Native-audio and most 3.x models | ✓, with a `reconnect` policy |
| xAI | ✓ | ✗ | ✗ | ✗ | ✓ | `grok-voice-latest` and `-think-` models | Replays local history |
| ElevenLabs | ✓ | ✗ | Agents only, toggle-gated | ✗ | ✗ | ✗ | Eleven Realtime replays local history; Agents do not |

Two provider families hide a second product behind the name: Azure's Voice Live deployment drops browser WebRTC while extending thinking to `gpt-5`-class models, and ElevenLabs' Agents mode turns on text output while keeping async tool calls and thinking off[^pydantic-realtime-docs]. The provider pages are declared canonical for installation, model names, settings and quirks, and this ingest did not read them[^pydantic-realtime-docs] (**Unverified** beyond the table).

## Profiles carry the sample rates and the flags

`RealtimeModel.profile` and `RealtimeSession.profile` both yield a `RealtimeModelProfile`, which reports the audio sample rates to capture and play back plus one flag per capability in the matrix and beyond — so the same branching that reads `supports_thinking` also fixes the codec rates rather than hard-coding them[^pydantic-realtime-docs]. Resolution follows the standard `Model` path in [Pydantic AI models and providers](pydantic-ai-models-and-providers.md): defaults first, then the provider's knowledge of the model name, then a `profile=` argument on top; a partial dict is merged over the resolved profile, while a callable `(resolved) -> RealtimeModelProfile` replaces it wholesale[^pydantic-realtime-docs].

The documented reason to pass `profile=` is a model name that lies — most often an Azure deployment named something other than its model, where nothing in the name reveals that a reasoning model is being served[^pydantic-realtime-docs]:

```python
from pydantic_ai.realtime.azure import AzureRealtimeModel

model = AzureRealtimeModel('voice-prod', profile={'supports_thinking': True})
```

## Shared settings and their three failure modes

`RealtimeModelSettings` plays the role that model run settings play for a standard run, defining what providers share — `tool_choice` and `turn_detection` are the two named[^pydantic-realtime-docs]. Defaults go on the realtime model constructor with `settings=`, a single session overrides them with `realtime(model_settings=...)`, and per-session values beat model defaults[^pydantic-realtime-docs]. Voices are not shared: `openai_voice`, `google_voice`, `xai_voice`, `elevenlabs_voice` and `elevenlabs_agents_voice_id` "and friends" sit on the provider settings classes, with their defaults and limitations on the provider pages[^pydantic-realtime-docs].

Three distinct failure modes follow from that split, and code must handle all three[^pydantic-realtime-docs]:

| Situation | Behaviour |
| --- | --- |
| Tuning knob a provider cannot apply (`max_tokens`, `thinking`) | Ignored silently, the way a request-response model treats it, so one settings object spans providers |
| `parallel_tool_calls=False` | Emits `UnsupportedSettingWarning` |
| A `tool_choice` that forces a tool call | Raises `UserError` before connecting, on every provider |
| A setting whose requirement cannot be met (`turn_detection=False` where the provider owns turn-taking) | Raises, with each provider's cases listed on its page |

The sharpest consequence is that the agent's own `model_settings` and a capability's `get_model_settings()` do **not** configure a realtime session at all — realtime is configured only through `RealtimeModelSettings`, on the model or on the session[^pydantic-realtime-docs]. That differs from the shared settings the same capability system supplies to [standard runs](pydantic-ai-run-controls.md), where `UnsupportedSettingWarning` is likewise the signal for a setting a model dropped.

### Opening a session has its own deadline

One shared setting is a timeout rather than a tuning knob: `handshake_timeout` on `RealtimeModelSettings`, default `30` seconds, bounds opening a session on OpenAI, Azure OpenAI, xAI and Gemini[^pydantic-docs-timeouts]. When it passes, opening raises `RealtimeError` — and on a reconnect it consumes a `ReconnectPolicy` attempt instead of failing outright[^pydantic-docs-timeouts] The capture is silent on whether a session inherits a run's own `timeout=`, so it is recorded here as the session-opening deadline only, with [Pydantic AI timeouts](pydantic-ai-timeouts.md) carrying the row[^pydantic-docs-timeouts]

## Limits

- The page names **no Pydantic AI version, publication date, author or licence**, so every API name here is version-unknown and the page stays `draft` under the `pydantic-ai` domain rule[^pydantic-realtime-docs].
- The matrix is prose rendered as a table, not a schema: it gives no per-model accepted-value list, no `RealtimeModelProfile` field list beyond "one flag per capability", and no example of the branching it recommends[^pydantic-realtime-docs].
- No package was installed, no model or session constructed, no provider connected, and no setting sent, ignored, warned about or rejected — every claim is **Reported**[^pydantic-realtime-docs].
- Coverage: the package is one `index.md` capture with no attachments, includes or supporting files; the five provider pages and the audio-wire, tools, events and API-reference pages were read as links, not followed.

## Relationships

- **Configures** [Pydantic AI realtime voice agents](pydantic-ai-realtime-voice.md): the session loop, streams and history handoff live there; the provider matrix, profiles and settings live here.
- **Extends** [Pydantic AI models and providers](pydantic-ai-models-and-providers.md)' profile-resolution rules — defaults, name knowledge, then an override — from `Model` to `RealtimeModel`, with partial dicts merged and callables replacing.
- **Shares** the `UnsupportedSettingWarning` mechanism recorded in [Pydantic AI run controls](pydantic-ai-run-controls.md), but not the settings themselves: run settings never reach a session.
- **Completes** the provider list in [Pydantic AI realtime voice agents](pydantic-ai-realtime-voice.md), whose vendor article names four providers against this page's five, ElevenLabs and Voice Live included.
- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) only indirectly: capability-contributed model settings are among the inputs that do not configure a session.
- **Shares one row with** [Pydantic AI timeouts](pydantic-ai-timeouts.md): `handshake_timeout` is the session-opening entry in that page's per-unit map, with `RealtimeError` as its expiry and the `ReconnectPolicy` attempt it spends on a reconnect.

[^pydantic-realtime-docs]: Pydantic Docs, "Realtime (speech-to-speech)", <https://pydantic.dev/docs/ai/realtime/overview/>, 1,948 words as declared and 2,125 by local `wc -w` including frontmatter and markup, no publication date, author, licence or Pydantic AI version named; local capture `raw/realtime/overview/index.md`, 205 lines, content digest sha256:fb0a3ffd5fc8. §"Provider support" (raw lines 111–131) for the `RealtimeModel` interface, the seven-column matrix and its five provider rows with the Azure Voice Live, Gemini `gemini-live-2.5-flash`, async-tool opt-in, ElevenLabs Agents and per-provider reconnect cells, the canonical-provider-pages statement, and profile-based branching; §"Shared settings" (134–150) for `RealtimeModelSettings`, `settings=` versus `realtime(model_settings=...)` precedence, the provider voice settings list, the rule that agent `model_settings` and `get_model_settings()` do not configure a session, silent ignoring of `max_tokens` and `thinking`, `UnsupportedSettingWarning` for `parallel_tool_calls=False`, the pre-connect `UserError` for a forcing `tool_choice`, and the raising `turn_detection=False` case; the profile paragraphs before that heading (123–132) for `RealtimeModel.profile`/`RealtimeSession.profile`, `RealtimeModelProfile`, sample rates, the three-step resolution, partial-dict merge versus callable replacement, and the Azure deployment example. Evidence class: **Reported** — vendor documentation for its own feature; nothing was installed, connected or measured, and the five provider pages it declares canonical were not read.

[^pydantic-docs-timeouts]: Pydantic Docs, "Timeouts" (<https://pydantic.dev/docs/ai/core-concepts/timeouts/>; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/timeouts/index.md`, content digest sha256:f0569195. §"Bounding how long a step takes" (raw lines 15–27) for the session-opening row — `handshake_timeout` on `RealtimeModelSettings`, default `30` seconds, on OpenAI, Azure OpenAI, xAI and Gemini, raising `RealtimeError` and consuming a `ReconnectPolicy` attempt on a reconnect. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
