---
type: Concept
title: Community-Reported Voice-Agent Latency Measurement and Tuning
description: Community-reported ~600 ms Pipecat voice-agent latency thread covering clock-start definitions, percentile reporting, a disclosed Pipecat/Silero/Flux-or-Ink/Gemini Flash Lite configuration, endpointing versus VAD, tool/KB latency, barge-in at the media edge, and provider-specific caveats.
tags: [pipeline, vad, stt, llm, tts, latency, endpointing, pipecat, streaming]
status: draft
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T12:00:00Z }
stale_after: 2027-04-21
sources:
  - id: reddit-600ms-voice-agent
    resource: ../raw/i_built_a_voice_ai_agent_with_600ms_latency_heres.md
    kind: documentation
    title: I built a voice AI agent with ~600ms latency. Here's what I learned. (r/VoiceAutomationAI thread capture)
---

A practitioner post claims about 600 ms end-to-end latency for a Pipecat-based phone voice agent, and the comments turn it into a discussion of what a latency number means: where the clock starts, whether the figure is a median or a tail percentile, and how much of the real caller experience (endpointing wait, tool calls, carrier leg, barge-in) sits outside it. The most reusable content is the **clock-boundary checklist**, the disclosed default stack and VAD/end-of-turn parameters, and field reports that turn detection and tool calls, not LLM time-to-first-token, dominated delay. All of it is anonymous or vendor-adjacent anecdote (**Reported**, **Unverified**).[^reddit-600ms-voice-agent]

## The headline claim and what is disclosed

- The original post reports ~600 ms end-to-end latency using Pipecat for the pipeline, credits streaming everything, and names the voice model, LLM, TTS, STT, and networking as joint contributors; it gives no architecture breakdown in the post itself (**Reported**).[^reddit-600ms-voice-agent]
- Follow-up replies attributed to the poster by content (bylines are `unknown`) qualify the figure: 600 ms without a knowledge base and about 800 ms with one; later "full turn" 600 ms rising to 700–800 ms with knowledge base or tool calls; target 500 ms p90 by year end. One reply answers "P90" to a median/percentile question, but the reply chain is ambiguous about which question it answers (**Reported**).[^reddit-600ms-voice-agent]
- The poster's stated clock is **user turn committed → first bot audio**, explicitly excluding the Flux/VAD silence that decides the caller has finished. The same poster later calls it "full turn latency", which is not the same boundary; the thread does not reconcile this (**Reported**; tension is **Synthesis**).[^reddit-600ms-voice-agent]
- Commenters contest the figure without a shared boundary: one says 600 ms is poor and under 400 ms is needed for anything acceptable; others cite 300 ms P50 or sub-200 ms P99 for vendor realtime STT APIs and about 100 ms as a "lowest clocked" figure. None of these state a comparable clock or protocol (**Reported**; vendor-promotional).[^reddit-600ms-voice-agent]

## Disclosed default stack and parameters

Reply attributed to the poster by content (a multi-tenant Pipecat deployment on Twilio/phone transport) (**Reported**):[^reddit-600ms-voice-agent]

| Layer | Setting |
| --- | --- |
| Pipeline | Pipecat run directly, one multi-tenant pipeline (not Dograh) |
| STT | Cartesia Ink-2 (streaming, using Cartesia's turn API) as default; Deepgram Flux also used |
| LLM | Gemini 3.1 Flash Lite default; temperature 0.7; max 1024 tokens (Gemini uncapped, brevity enforced in prompt) |
| TTS | Cartesia Sonic 3.5; sentence-level text on phone, token-level on web |
| VAD | Silero on phone transport; `confidence` left at Pipecat default 0.7 |
| VAD (Deepgram profile) | `start_secs=0.2`, `stop_secs=0.2`, `min_volume=0.5` |
| VAD (Cartesia profile) | `start_secs=0.25`, `stop_secs=0.2`, `min_volume=0.6` |
| End of turn (Twilio + Deepgram Flux) | `eot_threshold=0.5`, `eot_timeout_ms=700`, `eager_eot_threshold=0.4` |
| Interruptions | `allow_interruptions` on by default; no minimum word count |

- **Turn closing belongs to STT, not VAD:** with Deepgram Flux and Cartesia Ink-2 the VAD no longer closes the turn; Silero stays in the pipeline but is not the turn-end source (**Reported**).[^reddit-600ms-voice-agent]
- **Eager end-of-turn:** the turn is committed on the eager EOT signal so the LLM starts immediately, and the speculative response is cancelled if the caller keeps talking (**Reported**).[^reddit-600ms-voice-agent]
- **Sentence-level TTS on phone:** avoids audible crackle from fragments such as `"I'"`; token-level streaming is kept on web only for the live transcript (**Reported**).[^reddit-600ms-voice-agent]
- **Prompts are model-specific:** write for the ear, one or two sentences, one question at a time, no markdown; tool filler phrases are spoken by the server, not the model; a prompt tuned for one LLM does not carry over as-is to another (**Reported**, independently echoed by a second team).[^reddit-600ms-voice-agent]
- **LLM choice:** one commenter reports GPT-4o mini at around 800 ms latency and is advised to try Gemini 3.1 Flash Lite; another reports being unable to get below 900 ms without OpenAI Realtime using Kokoro TTS, Claude, and a VAD named Silencio (**Reported**; no measured protocol).[^reddit-600ms-voice-agent]

## How to report a latency number (consolidated checklist)

Several independent commenters converge on the same instrumentation advice (**Reported**; consolidation is **Synthesis**):[^reddit-600ms-voice-agent]

1. State the **start boundary**: caller speech end / VAD stop, STT final, or committed turn. Committed-turn → first audio hides the endpointing wait, which one commenter says can be 700–1000 ms and one team measured at ~1.8 s after short answers such as "yes" or "four people".
2. State the **stop boundary**: first TTS frame generated, first audio byte at the websocket, or first audible audio on the caller's phone. A commenter notes the carrier leg and 8 kHz transcode add time invisible inside Pipecat, and checks by streaming a pre-recorded WAV into a live call and listening to the recording.
3. Report **percentiles** (p90/p95/p99), not only a median, and separate ordinary turns from tool/graph-transition turns.
4. Break the path into stages: speech end → turn detection → STT final → LLM request → first useful model output → TTS request → first audio → playback.
5. **Listen to recordings.** Mid-turn stalls of a couple hundred milliseconds during tool calls vanish in averages.

Example stage figures from commenters, each on different clocks and stacks, not comparable to each other or to the 600 ms claim (**Reported**):[^reddit-600ms-voice-agent]

- Real-telephony cascade: ~280 ms to STT final, ~537 ms LLM request to first output, ~82 ms TTS request to first audio, yet complete normal turns of about 1.45–1.95 s; warm LLM requests occasionally taking ~8–10 s after earlier fast ones, so prewarming does not cure every long tail.
- Dutch phone receptionist (LiveKit + Deepgram + ElevenLabs over SIP): median ~1.1 s measured from end of speech with the fastest model; end-of-turn wait was a larger delay than the gap between tested models.

## Findings that generalize beyond the number

- **Tool and retrieval latency can dominate:** one team cut booking-backend calls from 4–6 database round trips to 2, moving 1.1–2.3 s to ~0.3 s; a knowledge base added roughly 200 ms to the poster's pipeline (**Reported**).[^reddit-600ms-voice-agent]
- **Speed versus reliability:** over-optimizing by switching to a smaller ASR/LLM/TTS yields fast but inaccurate replies and transcripts that break in non-ideal audio; the target depends on the use case. One team added a code-level check that blocks "your table is booked" unless the booking actually happened; faster models were not always the most reliable (**Reported**).[^reddit-600ms-voice-agent]
- **Noise and early turn closure:** on loud mobile calls the STT can close the turn on half a sentence and the agent then talks over the caller; this is logged as a "barge-in bug" although the cause is premature turn detection (**Reported**).[^reddit-600ms-voice-agent]
- **Barge-in at the media edge:** with a media server such as FreeSWITCH, drop queued audio at the edge instead of waiting for the pipeline to unwind; slow queue flushing makes 600 ms feel slow (**Reported**; the commenter works on a phone-layer vendor).[^reddit-600ms-voice-agent]
- **Deterministic state machine around the LLM:** code owns state, routing, transfers, and business rules; each turn the model sees only the instructions and tools for the current state, which is more predictable and also shrinks per-turn context (**Reported**, design advice).[^reddit-600ms-voice-agent]
- **Protocol abstraction:** exposing the cascade behind an OpenAI-Realtime-compatible interface makes cascade versus end-to-end (OpenAI Realtime, Gemini Live) a configuration choice (**Reported**, design advice).[^reddit-600ms-voice-agent]
- **Knowledge-base stack:** one reply describes a Postgres `pgvector` store (1024-dim, HNSW) with Bedrock Titan v2 embeddings and hybrid vector plus full-text search merged with reciprocal rank fusion (RRF); no latency figure is given for it separately (**Reported**).[^reddit-600ms-voice-agent]
- **Regional languages:** a commenter building Hindi/Bhojpuri agents reports English at 600–800 ms across clients but latency roughly doubling or tripling and WER above 40% for some regional languages, and cloud GPU capacity gaps adding cross-region latency; anecdotal and unmeasured (**Reported**).[^reddit-600ms-voice-agent]

## Second disclosed stack (pre-production, GDPR-driven)

A French-SMB team reports an unfinished first deployment: Twilio over WebSocket, Dograh (open-source layer on Pipecat adding a web UI, visual flow editor, wired telephony, and account management) on Railway, Deepgram EU endpoint STT, Mistral LLM, Voxtral (Mistral) TTS, n8n actions, and PostgreSQL. GDPR was the reason for EU-hosted providers, which they say rules out some faster options. They run a fork of Dograh for multi-tenant, bring-your-own-key clients and UI-exposed provider settings. They report no production latency numbers (**Reported**).[^reddit-600ms-voice-agent]

## Contradictions

- **Clock definition:** the poster says the 600 ms starts at turn commit and excludes Flux/VAD silence, but a later reply calls it "full turn latency"; other commenters measure from speech end and report 1.1 s or more. Neither is chosen (**Reported**).[^reddit-600ms-voice-agent]
- **Acceptable latency:** one commenter claims under 400 ms is the minimum acceptable; another argues a single number is unhelpful without cost/accuracy trade-offs and use-case targets. Neither is chosen (**Reported**).[^reddit-600ms-voice-agent]
- **Percentile:** answers are "P90" in one reply to a P50/P99 question and a 500 ms p90 goal elsewhere, but the headline figure's percentile is not stated in the post (**Reported**).[^reddit-600ms-voice-agent]

## Relationships

- Complements [Voice Agent Frameworks](voice-agent-frameworks.md): a field report of Pipecat run directly (multi-tenant) and of Dograh as a Pipecat-based layer, compared there only by AI-compiled report (**Synthesis**).[^reddit-600ms-voice-agent]
- Complements [Turn Detection Models](turn-detection-models.md) and [Smart Turn v3.2](smart-turn.md): the thread's provider-side EOT parameters (Flux, Ink-2) are an alternative to a separate semantic turn model, and commenters rank turn detection as a main latency source (**Synthesis**).[^reddit-600ms-voice-agent]
- Uses [Silero VAD](silero-vad.md) as the audio-level speech gate whose `start_secs`/`stop_secs`/`min_volume` values are disclosed above (**Synthesis**).[^reddit-600ms-voice-agent]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): the thread adds field reports of premature turn closure in noise and media-edge audio drop (**Synthesis**).[^reddit-600ms-voice-agent]
- Compare with [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md) for sentence-chunked TTS practice, and with [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md), whose 1–2 s local latency budget is a different (self-hosted, unmeasured) scenario than this hosted-API stack (**Synthesis**).[^reddit-600ms-voice-agent]
- The second stack's TTS relates to [Voxtral 4B TTS 2603](voxtral-4b-tts-2603.md); the thread does not state which Mistral checkpoint is used (**Synthesis**).[^reddit-600ms-voice-agent]

## Coverage and limits

- Entire single capture inspected statically (post plus 55-comment section); no execution, no measurement, no linked page fetched. Bylines on comments are `unknown`, so replies are attributed by content and the poster's identity for follow-ups is inferred (**Synthesis**).[^reddit-600ms-voice-agent]
- The capture is undated; vote counts omitted as volatile. The thread revolves around cloud providers and model names (Cartesia Ink-2/Sonic 3.5, Deepgram Flux, Gemini 3.1 Flash Lite) that change quickly, hence `stale_after` 2027-04-21 (**Synthesis**).[^reddit-600ms-voice-agent]
- Several commenters are vendors (speech API, phone layer, evaluation, agency-platform, retrieval, and memory products); their figures and recommendations are promotional-adjacent and are kept as Reported without endorsement (**Synthesis**).[^reddit-600ms-voice-agent]
- Excluded as non-durable: the author's biography, client count and credit/subsidy margin claims (commercial and unverified), the bot's community invitation, product plugs without technical content, and requests for breakdowns that were not answered. The promised architecture breakdown is absent from the capture (**Synthesis**).[^reddit-600ms-voice-agent]

[^reddit-600ms-voice-agent]: [I built a voice AI agent with ~600ms latency (r/VoiceAutomationAI thread capture)](../raw/i_built_a_voice_ai_agent_with_600ms_latency_heres.md) — locators: post body (600 ms claim, Pipecat, streaming lessons); `Comments 55` section — poster follow-ups on 600 ms without KB / ~800 with KB, model choice (4o mini ~800 ms, Gemini 3.1 Flash Lite), pgvector/Titan/RRF KB reply, "P90" reply, "Full turn latency" 600→700–800 ms and 500 ms p90 goal; the French-SMB Dograh stack comment and its five questions; the poster's reply with VAD/Flux/Ink-2/TTS/LLM parameters and "600 ms clock"; default stack reply (Ink-2, Gemini 3.1 Flash Lite, Sonic 3.5, Silero); commenters on clock boundaries (FreeSWITCH, FreJun Teler carrier/transcode and WAV test, LiveKit/Deepgram/ElevenLabs Dutch receptionist, stage-breakdown comments incl. 280/537/82 ms and 8–10 s warm-request outliers), FSM and OpenAI-Realtime-compatible interface advice, regional-language/Hindi comment, and the "under 400" versus "single number unhelpful" exchange.
