---
type: Concept
title: Whisper Hallucination Mitigation for Vietnamese
description: Faster-whisper decoding parameters, post-transcription confidence filters, and a Vietnamese phrase blacklist for suppressing Whisper hallucinations on silence, music, and noise in voice agents.
tags: [stt, whisper, hallucination, vietnamese, noisy-audio]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T18:00:00Z }
stale_after: 2027-10-06
sources:
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
---

Whisper repeatedly hallucinates Vietnamese YouTube-outro phrases such as "Hãy subscribe cho kênh La La School Để không bỏ lỡ những video hấp dẫn" on silence or music (whisperX #1086 across large, large-v2, and large-v3; whisper.cpp #1051 with "Ghiền Mì Gõ"); the report mitigates this with a forced language, conservative faster-whisper decoding parameters, segment-level confidence filters, and a regex blacklist applied to each VAD-cut turn (**Reported**).[^claude-pipeline-report]

## Decoding parameters (per VAD-cut turn)

- `language="vi"` is mandatory because language auto-detection on short noisy clips is error-prone (**Reported**).[^claude-pipeline-report]
- `beam_size=1–3` (greedy fastest; 3 better at ~30–50% more latency); `condition_on_previous_text=False` to stop repetition propagating; `temperature=0.0` to disable temperature fallback and its latency (**Reported**).[^claude-pipeline-report]
- `vad_filter=True` with `vad_parameters=dict(min_silence_duration_ms=500)` as a second filter layer, since faster-whisper's default only cuts silences longer than 2 s (**Reported**).[^claude-pipeline-report]
- `no_speech_threshold=0.6`, `log_prob_threshold=-1.0`, `compression_ratio_threshold=2.4` (**Reported**).[^claude-pipeline-report]
- `hotwords` for product/brand names or a short `initial_prompt` with standard Vietnamese punctuation; never put phrases like "cảm ơn đã xem" into the prompt (**Reported**).[^claude-pipeline-report]
- Model: `large-v3-turbo` (alias `turbo`) with `compute_type="float16"` on GPU or `int8_float16` when VRAM-limited; for better Vietnamese, PhoWhisper-large (convert to CTranslate2) or Qwen3-ASR-1.7B (**Reported**).[^claude-pipeline-report]

## Post-transcription filters

- Drop segments with `no_speech_prob > 0.6` and `avg_logprob < -1.0` (**Reported**).[^claude-pipeline-report]
- Drop the whole turn if `compression_ratio > 2.4`, or if it has fewer than 2 words while VAD reported under 400 ms (**Reported**).[^claude-pipeline-report]
- Regex blacklist: `subscribe`, `đăng k[ýí] (cho )?kênh`, `để không bỏ lỡ những video`, `cảm ơn (các bạn )?đã (xem|theo dõi)`, `La La School`, `Ghiền Mì Gõ`, and any sentence repeated verbatim three times (the heuristic used by the opencode-voice project) (**Reported**).[^claude-pipeline-report]
- Materialize the segment generator immediately (`list(segs)`) inside the worker thread; iterating faster-whisper's lazy generator on the asyncio event loop blocks the pipeline (Pipecat PR #5931) (**Reported**).[^claude-pipeline-report]

## When to stop filtering and replace Whisper

- Replace Whisper when noisy Vietnamese WER exceeds ~15% or hallucinations still pass the filters; candidates are Qwen3-ASR, PhoWhisper, or ChunkFormer, not Parakeet v3 (no Vietnamese) (**Reported**).[^claude-pipeline-report]

## Relationships

- Applies to [Faster-Whisper](faster-whisper.md), whose `vad_filter`, `hotwords`, and threshold parameters carry these settings (**Synthesis**).[^claude-pipeline-report]
- Used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) as its garbage-filter stage (**Synthesis**).[^claude-pipeline-report]
- Alternative path: [Qwen3-ASR family](qwen3-asr-family.md) as the named Whisper replacement for Vietnamese (**Synthesis**).[^claude-pipeline-report]
- Complements [Silero VAD](silero-vad.md) gating, which keeps silence away from Whisper in the first place (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- Parameter values and blacklist come from an AI-compiled report; the cited GitHub issues and PR are not in `raw/`, and no filter was run or tuned on audio here (**Synthesis**).[^claude-pipeline-report]
- The report says the parameter names were checked against official faster-whisper documentation; thresholds should still be calibrated per deployment (**Reported**).[^claude-pipeline-report]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `PHẦN 1` §4 closing paragraph `Hallucination của Whisper với tiếng Việt` (whisperX #1086, whisper.cpp #1051); `PHẦN 2` `Whisper: cấu hình chống hallucination` (model choice, per-turn parameters, post-transcription filters, blacklist regex, opencode-voice heuristic); `Kỹ thuật tối ưu` (Pipecat PR #5931); `Code mẫu` `transcribe()` and `BLACKLIST`; `Recommendations` › `Khi nào nên thay thành phần`; `Caveats` (code-sample verification note).
