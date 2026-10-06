---
type: Concept
title: Cascaded Voice-Agent Blueprint (Silero VAD → Whisper → Qwen3 → Qwen3-TTS)
description: LLM-generated reference blueprint for a cascaded Silero VAD → Whisper → Qwen3 → Qwen3-TTS voice agent with gateway/service split, VAD endpointing defaults, sentence-buffered TTS streaming, hardware tiers, service APIs, a 1–2 s latency budget, and common failure fixes.
tags: [vad, stt, llm, tts, pipeline, streaming, latency, architecture]
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

This blueprint, captured from an undated Vietnamese-language ChatGPT answer, proposes a cascaded voice agent in which Silero VAD v5 segments user turns, Whisper transcribes each complete utterance, Qwen3 in non-thinking mode streams a spoken-style reply, and Qwen3-TTS synthesizes that reply sentence by sentence back to the client; its central optimization is to never wait for the full LLM reply before starting TTS, and it targets roughly 1–2 s from end of user speech to first bot audio for a good MVP. Every parameter, budget, and sizing figure below is the generator's recommendation without measurement, and its upstream citations (openai/whisper, QwenLM/Qwen3, QwenLM/Qwen3-TTS, snakers4/silero-vad, arXiv 2505.09388) were not fetched (**Reported**).[^chatgpt-pipeline-recommend] Barge-in, cancellation, and echo handling are split into [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md).

## Component roles

| Stage | Component | Role in the loop |
| --- | --- | --- |
| VAD | Silero VAD v5 | Detects start and end of user speech; does not recognize content. |
| STT | Whisper | Transcribes the just-captured utterance; the original model works more naturally per audio segment than as true token streaming. |
| LLM | Qwen3 | Understands the dialogue, calls tools, and generates the reply; prefer non-thinking mode or a capped thinking budget for latency. |
| TTS | Qwen3-TTS | Reads the reply aloud; designed for multilingual TTS, voice cloning, and streaming with very low first-packet latency in suitable configurations. |

All four roles are as stated by the source (**Reported**).[^chatgpt-pipeline-recommend]

## Architecture and service split

- Client (web/mobile) captures microphone audio through an AudioWorklet and sends it over WebSocket; the speaker plays PCM or Opus chunks received on the same socket (**Reported**).[^chatgpt-pipeline-recommend]
- A voice gateway owns the session manager, audio buffer, VAD state machine, and barge-in/cancel logic, and fans out to Silero VAD, Whisper ASR, and a conversation path of Qwen3 → sentence buffer → Qwen3-TTS → WebSocket (**Reported**).[^chatgpt-pipeline-recommend]
- Target service split is `gateway-service`, `vad-service`, `asr-service`, `llm-service`, `tts-service`; a single-machine MVP may keep them in one Python process and split into processes or containers only as load grows (**Reported**).[^chatgpt-pipeline-recommend]
- Recommended rollout: start with a half-duplex MVP (user finishes, system answers, no interruption), then add streaming TTS, `generation_id`, AEC, and full-duplex barge-in once the pipeline is stable (**Reported**).[^chatgpt-pipeline-recommend]

## Turn flow and defaults

1. **Client audio:** mono, 16 kHz, signed int16 PCM, 20–32 ms frames, sent as binary WebSocket frames rather than base64 because base64 inflates size; a small JSON control message carries `type` and `sequence` (**Reported**).[^chatgpt-pipeline-recommend]
2. **VAD endpointing:** a gateway state machine moves `IDLE` → `SPEAKING` (speech probability above threshold) → `END_OF_UTTERANCE` (enough silence) → `TRANSCRIBING`, with starting values `VAD_THRESHOLD = 0.5`, `MIN_SPEECH_MS = 250`, `MIN_SILENCE_MS = 500`, `PRE_ROLL_MS = 200`, `MAX_UTTERANCE_MS = 30_000`; keep 200–300 ms of pre-roll audio from before the VAD trigger so the first syllable is not lost. Silero runs as TorchScript or ONNX, with ONNX possibly faster in some configurations (**Reported**).[^chatgpt-pipeline-recommend]
3. **ASR call:** after about 500–700 ms of silence, transcribe `pre_roll_audio + speech_audio` with `language="vi"` and `task="transcribe"`; never call Whisper per 20 ms frame, only per utterance or on a longer sliding window. For lower latency use faster-whisper/CTranslate2 with Whisper small or medium, FP16 on GPU or INT8 on CPU, treating it as an alternative runtime over the official Whisper weights (**Reported**).[^chatgpt-pipeline-recommend]
4. **LLM call:** a voice system prompt states the output will be spoken: natural and brief answers, no complex Markdown, no long URLs/symbols/tables, pronounceable numbers and units, no description of reasoning, short sentences; messages are system prompt + history + transcript, with `thinking = false`, `temperature = 0.4–0.7`, `max_tokens = 200–500`, `stream = true`. Qwen3 dense or MoE size is chosen from VRAM and latency needs (**Reported**).[^chatgpt-pipeline-recommend]
5. **Sentence-buffered TTS:** accumulate streamed tokens into a buffer, pop each complete sentence onto a TTS queue, flush the remainder at stream end, and start playback as soon as the first sentence's audio is ready; the source calls this the single most important optimization (**Reported**).[^chatgpt-pipeline-recommend]

Per-token TTS is rejected because prosody becomes unnatural, the TTS lacks context, request count explodes, and gaps become audible; the best unit is usually one sentence or about 20–60 characters (**Reported**).[^chatgpt-pipeline-recommend]

## Reference async worker layout

The source sketches a `VoiceSession` holding four `asyncio.Queue`s (audio, utterance, text, TTS) plus `generation_id` and `assistant_speaking`, driven by five coroutines: `audio_receiver` (binary WebSocket frames → audio queue), `vad_worker` (ring-buffer pre-roll of 250 ms, speech threshold 0.5, 550 ms silence closes the utterance), `asr_worker` (Whisper via `asyncio.to_thread`, empty transcripts dropped), `llm_worker` (streams Qwen3 with `enable_thinking=False`, enqueues `(generation_id, sentence)` pairs, appends the full reply to history only if not superseded), and `tts_worker` (skips stale generations, streams audio chunks, emits `audio_cancel` when superseded mid-sentence); the source labels it illustrative and states real package interfaces differ (**Reported**).[^chatgpt-pipeline-recommend]

Static reading of the sketch shows it diverges from the prose defaults: it uses 250 ms pre-roll and a 550 ms silence cutoff rather than 200 ms and 500 ms, never applies `MIN_SPEECH_MS` or `MAX_UTTERANCE_MS`, increments `generation_id` on the first above-threshold frame rather than after the 100–200 ms sustained-speech rule, does not clear the TTS queue, and passes raw PCM bytes to `whisper.transcribe`; treat it as a control-flow outline, not runnable code (**Observed**).[^chatgpt-pipeline-recommend]

## Hardware tiers and placement

| Tier | Silero VAD | Whisper | Qwen3 | Qwen3-TTS |
| --- | --- | --- | --- | --- |
| MVP | ONNX on CPU | small/medium on GPU | 4B or 8B quantized | 0.6B |
| High quality | CPU | large-v3 or an inference-optimized variant | 14B or 30B-A3B | 1.7B |

- The tiers are recommendations without measured VRAM or latency (**Reported**).[^chatgpt-pipeline-recommend]
- On one GPU, do not co-host large Whisper, large Qwen3, and large TTS in VRAM without measuring first; a single-GPU layout is Silero on CPU, small Whisper on GPU, Qwen3 quantized through llama.cpp or vLLM, and 0.6B TTS on GPU, while a three-GPU layout places Whisper + Silero, Qwen3, and Qwen3-TTS on separate devices (**Reported**).[^chatgpt-pipeline-recommend]
- Qwen3-TTS Base variants serve voice cloning by passing `ref_audio` with its transcript `ref_text` (**Reported**).[^chatgpt-pipeline-recommend]

## Inter-service APIs

- ASR: `POST /transcribe` with `Content-Type: audio/wav`, returning JSON `text`, `language`, `duration_ms` (**Reported**).[^chatgpt-pipeline-recommend]
- LLM: OpenAI-style `POST /v1/chat/completions` streamed via Server-Sent Events or streaming HTTP (**Reported**).[^chatgpt-pipeline-recommend]
- TTS: `POST /synthesize` with JSON `text`, `language`, `voice`, `stream: true`, responding with streaming PCM or Opus (**Reported**).[^chatgpt-pipeline-recommend]

## Latency budget

| Stage | Budget |
| --- | --- |
| VAD end-of-speech | 400–600 ms |
| Whisper | 200–700 ms |
| Qwen3 first token | 100–500 ms |
| First-sentence split | 100–400 ms |
| TTS first audio | 100–500 ms |
| Network/buffering | 50–200 ms |

The source sets about 1–2 s from user stop to bot audio as a good MVP; going lower requires speculative/partial ASR, LLM streaming, true TTS streaming, warm connections, models resident in VRAM, no per-request model loading, and no temporary WAV files on disk (**Reported**).[^chatgpt-pipeline-recommend] The listed stage ranges sum to roughly 0.95–2.9 s, so the 1–2 s target implicitly assumes stages land near their lower bounds or overlap (**Synthesis**).[^chatgpt-pipeline-recommend]

## Common failures and fixes

- **Premature cut-off:** VAD treats a short pause as end of turn; raise `min_silence` to about 500–800 ms, adapted to speaking rate (**Reported**).[^chatgpt-pipeline-recommend]
- **Whisper text from noise:** call ASR only after VAD confirms enough speech, and check `no_speech_prob`, transcript length, and confidence; Whisper can fabricate content under poor audio or silence, so its transcripts are not authoritative for high-risk tasks (**Reported**).[^chatgpt-pipeline-recommend]
- **TTS reads Markdown:** strip `#`, `**`, tables, and URLs before synthesis (**Reported**).[^chatgpt-pipeline-recommend]
- **Over-long replies:** limit to 2–4 sentences in the system prompt and set `max_tokens` (**Reported**).[^chatgpt-pipeline-recommend]
- **Stale turns not cancellable** and **choppy playback:** see [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) for `generation_id` propagation and client playback queues (**Reported**).[^chatgpt-pipeline-recommend]

## Suggested stack and repository layout

- Frontend: React/Next.js, AudioWorklet, WebSocket or WebRTC. Backend: Python 3.11+, FastAPI, asyncio, PyTorch/ONNX Runtime. Inference: Silero VAD ONNX, faster-whisper, Qwen3 via vLLM, SGLang, or llama.cpp, and a separate Qwen3-TTS service. Infrastructure: Redis for session/events, Prometheus + Grafana, Docker Compose for MVP, Kubernetes when scaling (**Reported**).[^chatgpt-pipeline-recommend]
- Repository skeleton: `frontend/`; `gateway/` with `websocket.py`, `session.py`, `vad_state.py`, `cancellation.py`; `services/asr|llm|tts/`; `shared/protocols.py` and `shared/audio.py`; `docker-compose.yml` (**Reported**).[^chatgpt-pipeline-recommend]

## Relationships

- Uses [Silero VAD](silero-vad.md): the endpointing stage; that page holds the primary-source runtime, footprint, and 8/16 kHz scope behind this blueprint's ONNX-on-CPU recommendation (**Synthesis**).[^chatgpt-pipeline-recommend]
- Uses [Faster-Whisper](faster-whisper.md): the recommended low-latency Whisper runtime; note its built-in `vad_filter` defaults to a conservative 2 s silence for offline filtering, whereas this blueprint's 500–800 ms gateway endpointing targets interactive turns (**Synthesis**).[^chatgpt-pipeline-recommend]
- Uses [Qwen3-TTS-12Hz-0.6B-CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md) and [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md): the 0.6B/1.7B tiers map to that family, whose card documents Base-model cloning via `ref_audio`/`ref_text` and streaming claimed down to 97 ms; [Faster Qwen3-TTS](faster-qwen3-tts.md) is a candidate runtime for the TTS service (**Synthesis**).[^chatgpt-pipeline-recommend]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): the interruption, cancellation, and AEC layer this blueprint defers to its full-duplex phase (**Synthesis**).[^chatgpt-pipeline-recommend]
- Compare with [Community-Reported STT-LLM-TTS Pipeline Wiring](community-stt-llm-tts-pipeline.md) (same HTTP-service split and sentence-chunked TTS streaming, reported by humans for a single 3090), [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md) (implemented VAD → STT → LLM → TTS with Qwen3-TTS as default voice), and [RealtimeVoiceChat](realtime-voice-chat.md) (implemented browser WebSocket pipeline with interruption): this page is an unimplemented design blueprint, those are working systems or field reports (**Synthesis**).[^chatgpt-pipeline-recommend]
- Compare with [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md): a second LLM-generated report on the same Silero VAD → Whisper → Qwen3 → Qwen3-TTS request that adds Smart Turn turn detection, Vietnamese hallucination filtering, VieNeu-TTS routing for Vietnamese, and per-stage latency/VRAM budgets (**Synthesis**).[^claude-pipeline-report]

## Contradictions

- Vietnamese in the TTS stage: the blueprint's examples set `language="vi"` throughout, including the `/synthesize` request feeding Qwen3-TTS, while the [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) card lists ten supported languages (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian) without Vietnamese; neither claim is chosen here, but a Vietnamese deployment should verify Qwen3-TTS language support before adopting this stack (**Synthesis**).[^chatgpt-pipeline-recommend] The Claude report independently states official Qwen3-TTS has no Vietnamese, that a community request (GitHub Discussion #274) is unanswered, and recommends VieNeu-TTS v3 Turbo or an unbenchmarked community Vietnamese fine-tune instead (**Reported**).[^claude-pipeline-report]

## Coverage and limits

- Single-file source inspected statically in full; no code run, no model loaded, and no latency, VRAM, or quality figure reproduced (**Synthesis**).[^chatgpt-pipeline-recommend]
- Authority is low: the source is an LLM-generated answer with no author, capture date, model version, prompt, or hardware context; its inline citations are `utm_source=chatgpt.com` links to upstream repositories and arXiv 2505.09388 that were not fetched, so claims attributed to them remain second-hand (**Synthesis**).[^chatgpt-pipeline-recommend]
- Excluded as non-durable: the decorative ASCII architecture box (its content is captured as prose), the full code listings (summarized above), and the example Vietnamese transcript strings (**Synthesis**).[^chatgpt-pipeline-recommend]
- Qwen3 LLM sizes, thinking modes, and inference backends have no primary-source concept in this wiki, so model-size recommendations are unanchored; model and latency guidance carries `stale_after: 2027-10-06` per the `vad`, `stt`, `llm`, and `tts` domain rules (**Synthesis**).[^chatgpt-pipeline-recommend]

[^chatgpt-pipeline-recommend]: [ChatGPT voice-agent pipeline recommendation (Vietnamese)](../raw/ChatGPT-pipeline-recommend.md) — locators: opening pipeline fence (Microphone → Silero VAD → Whisper → Qwen3 → Qwen3-TTS → speaker); `## 1. Vai trò từng mô hình` (roles, Whisper per-segment note, Qwen3 thinking/non-thinking, Qwen3-TTS streaming claim); `## 2. Kiến trúc sản phẩm nên dùng` (client/gateway box, five-service list, single-process MVP); `## 3. Luồng xử lý một lượt nói` Bước 1–4 (16 kHz int16 20–32 ms binary frames, VAD state machine and `VAD_THRESHOLD`/`MIN_SPEECH_MS`/`MIN_SILENCE_MS`/`PRE_ROLL_MS`/`MAX_UTTERANCE_MS` fence, pre-roll 200–300 ms, TorchScript/ONNX note, 500–700 ms silence plus `whisper.transcribe` fence, faster-whisper/CTranslate2 small/medium FP16/INT8 fence, voice system prompt, `thinking`/`temperature`/`max_tokens`/`stream` fence, dense/MoE note); `## 4. Không đợi Qwen3 trả lời xong mới chạy TTS` (wrong/right fences, sentence-buffer fence, per-token rejection list, 20–60 characters); `## 5. Pipeline async mẫu` (`VoiceSession`, `audio_receiver`, `vad_worker`, `asr_worker`, `llm_worker`, `tts_worker`, illustrative-interface caveat); `## 8. Chọn model theo phần cứng` (MVP and high-quality fences, Base `ref_audio`/`ref_text`, GPU 0/1/2 and single-GPU fences); `## 9. API giữa các service`; `## 10. Latency mục tiêu`; `## 11. Những lỗi thường gặp`; `## 12. Stack triển khai đề xuất` (stack fence, repository tree, half-duplex-first closing paragraph).

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: opening paragraph (Qwen3-TTS lacks Vietnamese, VieNeu recommendation); `Key Findings` 1 (10-language list, Discussion #274, `ShiniChien` fine-tunes); `PHẦN 2` `Qwen3-TTS: chọn model và cách dùng` › `Tiếng Việt` options (a)–(c).
