---
type: Concept
title: Voice-Agent Barge-in and Echo Handling
description: LLM-generated guidance for interrupting a speaking voice agent via generation_id cancellation across LLM, TTS, and client, three echo-avoidance tiers, duration-gated noise-robust barge-in with speaker lock and backchannel exemption, and WebSocket-versus-WebRTC transport tradeoffs.
tags: [vad, tts, pipeline, barge-in, echo-cancellation, streaming]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: chatgpt-pipeline-recommend
    resource: ../raw/ChatGPT-pipeline-recommend.md
    kind: llm-response
    title: ChatGPT voice-agent pipeline recommendation (Vietnamese)
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Barge-in lets a user interrupt a cascaded voice agent mid-reply: the microphone stays open while the bot speaks, VAD keeps scoring speech, and once the user is detected the system stops bot audio, cancels the in-flight LLM and TTS work, and starts buffering the new turn; an undated ChatGPT answer recommends implementing this with a monotonically increasing `generation_id` carried by every LLM and TTS chunk, and pairing it with acoustic echo cancellation so the bot does not hear itself. All guidance below is the generator's unmeasured recommendation (**Reported**).[^chatgpt-pipeline-recommend] The surrounding pipeline is described in [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md).

## Interruption procedure

1. Keep the client microphone open during bot playback, and keep Silero VAD scoring incoming audio (**Reported**).[^chatgpt-pipeline-recommend]
2. When speech probability stays above threshold for about 100–200 ms: increment `generation_id`, clear the stale TTS queue, send `audio_cancel` to the client, cancel the running Qwen3 request if the backend supports it, and begin buffering the new utterance (**Reported**).[^chatgpt-pipeline-recommend]
3. Tag every LLM and TTS chunk with its generation, e.g. `{"type": "audio_chunk", "generation_id": 42}`; the client discards chunks from older generations (**Reported**).[^chatgpt-pipeline-recommend]
4. Propagate `generation_id` or an equivalent cancellation token end to end through ASR → LLM → TTS → client; the source names missing propagation as the cause of turns that cannot be cancelled (**Reported**).[^chatgpt-pipeline-recommend]

In the source's async sketch, the LLM worker breaks its token loop when its captured generation is superseded and skips appending the abandoned reply to history, and the TTS worker drops queued sentences from stale generations and emits `audio_cancel` if superseded mid-stream (**Reported**).[^chatgpt-pipeline-recommend] The sketch bumps `generation_id` on the first above-threshold frame rather than after the 100–200 ms sustained-speech window, and does not itself clear the TTS queue, so a real implementation must add both (**Observed**).[^chatgpt-pipeline-recommend]

## Echo-avoidance tiers

| Tier | Mechanism | Tradeoff |
| --- | --- | --- |
| Simple | Stop sending microphone audio while the bot speaks. | Easy, but no barge-in. |
| Better | Browser AEC via `getUserMedia` constraints `echoCancellation`, `noiseSuppression`, `autoGainControl` all `true`, with VAD still detecting interruptions. | Keeps barge-in with browser-grade echo removal. |
| Production | WebRTC-layer AEC plus retaining the bot's just-played audio, comparing it with the microphone, and triggering barge-in only when new speech differs substantially from the TTS audio. | Most robust; most engineering. |

The tiers and tradeoffs are as stated by the source (**Reported**).[^chatgpt-pipeline-recommend]

## Noise-robust gating (Claude report)

A second LLM-generated source, a Vietnamese report self-dated 10/2026 targeting noisy environments, adds gating and rejection rules on top of AEC (**Reported**).[^claude-pipeline-report]

- Soft half-duplex: while the bot speaks, raise the Silero threshold to 0.7 and require ≥300–500 ms of continuous user speech before treating it as an interruption; optionally require a quick ASR pass yielding ≥2 words that do not match the sentence being played (**Reported**).[^claude-pipeline-report]
- Adaptive threshold: measure VAD probability and RMS over the first 2–3 s before the user speaks; if mean background probability exceeds 0.3, raise the threshold to 0.65–0.7 and raise the barge-in gate (**Reported**).[^claude-pipeline-report]
- Short noises (coughs, typing) are blocked by the duration gate; background voices are rejected by speaker lock, comparing cosine similarity of an ECAPA/CAM++ embedding of the new segment with the user's embedding (from the first turn, updated gradually) and ignoring segments below ~0.5–0.6, a threshold to calibrate on own data (**Reported**).[^claude-pipeline-report]
- Backchannels such as "ừ", "vâng", "ok" while the bot talks do not interrupt (**Reported**).[^claude-pipeline-report]
- Interrupt sequence: cancel the LLM stream, cancel the TTS HTTP/WebSocket request, clear queued sentences, send `{"type":"clear"}` so the client flushes its AudioWorklet buffer, and store only the actually played part of the reply in history tagged `[bị ngắt]`; the report's reference server gates at `speech_ms >= 400` while `bot_speaking` (**Reported**).[^claude-pipeline-report]
- Denoise (RNNoise/DeepFilterNet 3) is applied to this VAD/barge-in branch only, not to ASR input, see [Speech Enhancement Before ASR](speech-enhancement-before-asr.md); measure barge-in rate and false-interruption rate under background-noise playback (**Reported**).[^claude-pipeline-report]

## Transport and playback

- WebRTC suits production voice calls better than WebSocket when jitter buffering, echo cancellation, packet-loss handling, Opus transport, or stable mobile connectivity are needed; an MVP can stay on WebSocket (**Reported**).[^chatgpt-pipeline-recommend]
- Choppy audio is fixed by a client-side playback queue rather than playing each chunk the instant it arrives (**Reported**).[^chatgpt-pipeline-recommend]
- The source recommends deferring barge-in: ship a half-duplex MVP first, then add streaming TTS, `generation_id`, AEC, and full-duplex barge-in (**Reported**).[^chatgpt-pipeline-recommend]

## Relationships

- Part of [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md): the gateway's barge-in/cancel module and the full-duplex phase of that blueprint (**Synthesis**).[^chatgpt-pipeline-recommend]
- Uses [Silero VAD](silero-vad.md): the interruption detector running during bot playback; its sub-1 ms per-chunk CPU cost on that page is what makes always-on scoring cheap (**Synthesis**).[^chatgpt-pipeline-recommend]
- Compare with [RealtimeVoiceChat](realtime-voice-chat.md), an implemented browser WebSocket pipeline with interruption support and dynamic silence detection, and with full-duplex speech-to-speech models [NVIDIA NemotronLabs VoiceChat 11B](nvidia-nemotronlabs-voicechat-11b.md) and [PersonaPlex 7B v1](personaplex-7b-v1.md) that handle turn-taking inside the model instead of via cascade cancellation (**Synthesis**).[^chatgpt-pipeline-recommend]
- Evaluated with [Community-Reported Usable STT for Voice Agents](community-usable-stt-voice-agents.md): that checklist names barge-in timing and endpointing as production metrics to measure for the mechanism described here (**Synthesis**).[^chatgpt-pipeline-recommend]

- Gating companion [Turn Detection Models](turn-detection-models.md): premature end-of-turn and false interruption are the paired turn-taking errors; used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md), and Pipecat provides built-in interruption handling per [Voice Agent Frameworks](voice-agent-frameworks.md) (**Synthesis**).[^claude-pipeline-report]

## Contradictions

- Interruption trigger window: the ChatGPT answer fires barge-in after about 100–200 ms of above-threshold speech, while the Claude report requires ≥300–500 ms of continuous speech at a raised 0.7 threshold (400 ms in its reference server) to reject noise in loud environments; both are unmeasured design values for different priorities (responsiveness versus false-interruption rejection), so neither is chosen (**Reported**).[^chatgpt-pipeline-recommend] [^claude-pipeline-report]

## Coverage and limits

- Source inspected statically; no AEC, VAD, or cancellation path was implemented or measured, and the 100–200 ms trigger window has no stated basis (**Synthesis**).[^chatgpt-pipeline-recommend]
- The Claude report's thresholds are likewise engineering recommendations from an AI-compiled report, not measured results (**Synthesis**).[^claude-pipeline-report]
- The source is an LLM-generated answer without author, date, or cited evidence for this section, so the guidance is a design starting point, not a validated practice (**Synthesis**).[^chatgpt-pipeline-recommend]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `PHẦN 1` §2 AEC and speaker-verification rows; `PHẦN 2` mermaid flowchart (denoise only for VAD branch, barge-in node ≥300ms); `Silero VAD: tham số đề xuất` › `Ngưỡng thích ứng`; `Barge-in và echo` items 1–3; `Code mẫu` `Session.on_audio`/`interrupt`/`respond` (400 ms gate, `{"type":"clear"}`, `[bị ngắt]`); `Triển khai` monitoring and evaluation bullets.

[^chatgpt-pipeline-recommend]: [ChatGPT voice-agent pipeline recommendation (Vietnamese)](../raw/ChatGPT-pipeline-recommend.md) — locators: `## 5. Pipeline async mẫu` (`VoiceSession.generation_id`/`assistant_speaking`, `vad_worker` interrupt increment, `llm_worker` stale-generation break and history skip, `tts_worker` stale skip plus `audio_cancel`); `## 6. Barge-in: người dùng ngắt lời bot` (interrupt flow fence, numbered steps with 100–200 ms window, `audio_chunk` JSON with `generation_id`, client discard rule); `## 7. Tránh bot nghe lại chính giọng của mình` (Phương án đơn giản / tốt hơn with `getUserMedia` fence / production, WebRTC-versus-WebSocket list); `## 11. Những lỗi thường gặp` (cancellation and choppy-audio items); `## 12. Stack triển khai đề xuất` closing half-duplex-first paragraph.
