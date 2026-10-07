---
type: Concept
title: Voice Agent Frameworks
description: Comparison of open-source realtime voice-agent orchestration frameworks — Pipecat, LiveKit Agents, TEN Framework, FastRTC — by license, built-in VAD/STT/LLM/TTS support, Qwen3-TTS integration, and transport.
tags: [pipeline, orchestration, webrtc, frameworks]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T04:37:10Z }
stale_after: 2027-10-06
sources:
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Voice-agent frameworks supply transport, turn-taking, interruption, and service plumbing around VAD → STT → LLM → TTS. For a Silero + Whisper + Qwen3 + Qwen3-TTS stack the report rates Pipecat as needing the least code, because it already ships Silero VAD, faster-whisper, Smart Turn, and OpenAI-compatible LLM services, leaving only a custom `TTSService` for Qwen3-TTS or VieNeu; no surveyed framework has an official Qwen3-TTS service (**Reported**).[^claude-pipeline-report]

## Comparison (mid-2026)

| Framework | Stars (third-party blogs) | License | Silero VAD | Local Whisper | Qwen via OpenAI API | Qwen3-TTS | Transport |
|---|---|---|---|---|---|---|---|
| Pipecat (Daily) | ~13–14k; v1.0 04/2026 | BSD-2 | Yes, `SileroVADAnalyzer` | Yes, `WhisperSTTService` (faster-whisper), MLX | Yes | No official service (issue #2126 open); community Qwen3-TTS-OpenAI-FastAPI repo with Pipecat pipeline | WebRTC (Daily, SmallWebRTC), WebSocket, telephony |
| LiveKit Agents | ~11–14k | Apache-2.0 | Yes | Via OpenAI-compatible plugin or custom | Yes | No, custom | WebRTC SFU, SIP |
| TEN Framework | ~11k | Apache-2.0 "with conditions" | TEN VAD | Extension | Yes | No | Agora RTC, WebSocket |
| FastRTC (Hugging Face) | — | MIT | Yes | Yes | Yes | vLLM-Omni ships a FastRTC demo | WebRTC via Gradio |

Telephony-leaning: Bolna, Dograh, Vocode. Listed but not re-checked: RealtimeSTT/TTS/VoiceChat (KoljaB), HF speech-to-speech, Unmute, Open WebUI voice, Wyoming/Home Assistant, sherpa-onnx, Speaches, LocalAI, OpenVoiceOS, xiaozhi-esp32(-server). All cells as reported; star counts vary across sources (**Reported**).[^claude-pipeline-report]

## Pipecat composition for the recommended stack

- `SileroVADAnalyzer()` + `LocalSmartTurnAnalyzerV3` + `WhisperSTTService` (faster-whisper) + `OpenAILLMService(base_url=vLLM)` + a custom `TTSService` whose `run_tts()` calls `/v1/audio/speech` and yields audio frames; Pipecat then provides interruption handling, per-service TTFB metrics, and WebRTC transport (**Reported**).[^claude-pipeline-report]
- MVP route: Pipecat + SmallWebRTC (**Reported**).[^claude-pipeline-report]
- Known pitfall: Pipecat once blocked its event loop by iterating faster-whisper's lazy `transcribe` generator; segments must be collected inside `asyncio.to_thread` (PR #5931) (**Reported**).[^claude-pipeline-report]

## Relationships

- Compared in [So sánh công cụ triển khai speech](speech-deployment-tools-comparison.md): these frameworks belong to the orchestration tier, not the ASR/TTS inference-engine tier; this table remains secondary AI-report evidence, not primary-project verification (**Synthesis**).[^claude-pipeline-report]

- Used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) as its orchestration layer (**Synthesis**).[^claude-pipeline-report]
- Integrates [Silero VAD](silero-vad.md), [Faster-Whisper](faster-whisper.md), and Smart Turn from [Turn Detection Models](turn-detection-models.md) (**Synthesis**).[^claude-pipeline-report]
- Listed-but-unchecked projects with their own wiki concepts: [RealtimeSTT](realtimestt.md), [RealtimeVoiceChat](realtime-voice-chat.md), [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md), and [Speaches](speaches.md) (**Synthesis**).[^claude-pipeline-report]
- [VieNeu-TTS v3 Turbo](vieneu-tts-v3-turbo.md) exposes an OpenAI-style `/v1/audio/speech` server, which is what makes a thin custom `TTSService` sufficient (**Synthesis**).[^claude-pipeline-report]
- [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md) names Pipecat and LiveKit as good but optional end-to-end pipelines versus hand-wired HTTP services (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- Framework facts are relayed by an AI-compiled report from third-party comparison blogs and project docs not in `raw/`; star counts are volatile and the report notes inter-source disagreement (**Synthesis**).[^claude-pipeline-report]
- TEN's "with conditions" license and LiveKit plugin details were not resolved by the report (**Reported**).[^claude-pipeline-report]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` framework bullet; `PHẦN 1` §8 `Framework / sản phẩm hoàn chỉnh` table and closing Pipecat paragraph; `PHẦN 2` `Kỹ thuật tối ưu` (PR #5931); `Code mẫu` Pipecat usage note; `Recommendations` › `Lộ trình` MVP; `Caveats` (stars from mid-2026 blogs; unchecked small frameworks).
