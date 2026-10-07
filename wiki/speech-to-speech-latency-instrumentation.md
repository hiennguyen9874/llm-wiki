---
type: Concept
title: Speech-to-Speech Response Latency Instrumentation
description: Version-2 per-response latency record of the HF speech-to-speech realtime server, defining E2E, STT, LLM, TTS-TTFA, VAD-decision, Smart Turn, and hold measurements, their coverage matrix, and their overlap caveats.
tags: [pipeline, streaming, evaluation, realtime]
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

The [HF speech-to-speech](speech-to-speech-pipeline.md) server writes one INFO record per finished Realtime response carrying its turn, revision, `response_key`, terminal status, and available stage durations, and mirrors the same record into the terminal `response.done` event under the reserved metadata key `response.metadata["speech_to_speech.turn_latency"]`; version 2 redefined E2E from VAD handoff to **estimated speech end to first generated audio** and renamed `smart_wait_s` to `hold_s` (**Reported**).[^s2s-supporting-docs]

## Recording and transport

- The human-readable log line looks like `Turn turn_3 rev=0 latency: stt=0.18s llm=1.24s tts_ttfa=0.12s e2e=2.01s vad_decision=0.36s hold=0.24s smart_turn_status=complete status=completed response_key=...` and is produced by both `speech-to-speech local` and `speech-to-speech serve` (**Reported**).[^s2s-supporting-docs]
- `response_key` distinguishes a tool call from its spoken follow-up, which can share a turn and revision; a follow-up does not repeat the original STT duration (**Reported**).[^s2s-supporting-docs]
- The metadata value is compact JSON (Realtime metadata values are strings) with schema version 2 and keys `e2e_s`, `hold_s`, `llm_s`, `response_key`, `smart_status`, `status`, `stt_s`, `tts_ttfa_s`, `turn_id`, `turn_revision`, `vad_decision_s`, and `version` (**Reported**).[^s2s-supporting-docs]
- Version 2 removes `llm_ttft_s`, `smart_analysis_s`, `smart_grace_s`, `smart_delay_s`, and `mlx_lock_wait_s` from metadata; `mlx_lock_wait` appears only in terminal logs on macOS, never in response metadata or the demo (**Reported**).[^s2s-supporting-docs]
- Durations are seconds; existing fields keep their precision while new VAD/Smart Turn fields use nanosecond precision in metadata, and the human-readable log rounds to two decimals with unavailable measurements as JSON `null` (**Reported**).[^s2s-supporting-docs]
- Client metadata is preserved except that a terminal response removes any client-supplied reserved latency key before adding the server measurement; `response.created` still carries client metadata unchanged, and the reserved value is included only when it fits Realtime's 512-character metadata value limit without shortening client metadata (**Reported**).[^s2s-supporting-docs]
- The measurement is omitted when no attributed turn exists or when all 16 Realtime metadata slots are occupied by other client keys; an abandoned response has no terminal record (**Reported**).[^s2s-supporting-docs]

## Stage definitions

- `stt` covers final transcription processing only, excluding repeated progressive HTTP transcriptions and Realtime partial deltas: for HTTP STT it runs from the final request worker's start to before its result is published, for Realtime STT from queueing the final VAD commit to receiving the provider's final transcript, and for local models from the start of final transcription to before the transcript is yielded (**Reported**).[^s2s-supporting-docs]
- `llm` covers full generation from serialization and provider request through consumption of provider output, and is recorded even when the request fails (**Reported**).[^s2s-supporting-docs]
- `tts_ttfa` starts when synthesis of the first text segment begins and ends when the first provider audio samples arrive; for HTTP TTS, WAV headers are excluded and resampling and output-block assembly happen afterward (**Reported**).[^s2s-supporting-docs]
- `e2e` runs from estimated speech end to the first audio block yielded by TTS and includes VAD decision time, Smart Turn analysis, audio enhancement, and subsequent hold time; the speech-end timestamp is propagated separately from `VADAudio.created_at_s`, later synthesis segments cannot overwrite first audio, and it is unavailable when no speech-end estimate exists with no fallback to the old handoff boundary. It measures generated audio, not browser playback (**Reported**).[^s2s-supporting-docs]
- `vad_decision_s` starts at an estimated end of voiced audio and ends immediately when the VAD iterator returns the final segment, before Smart Turn analysis: Silero uses the first low-confidence chunk's start and FireRed uses its last speech frame's end, each mapped by subtracting remaining audio samples from the worker's start time. Upstream queue time, network jitter, chunking, model frame resolution, and audio captured before processing limit its accuracy, and it is `null` when the iterator provides no speech-end sample position (**Reported**).[^s2s-supporting-docs]
- `smart_status` is the Smart Turn decision (`complete`, `incomplete`, `failed`, or `disabled`); a failure still falls back to the ordinary short reopen grace without changing inference or speculation policy (**Reported**).[^s2s-supporting-docs]
- `hold_s` is actual elapsed time blocked at processing or response-release gates with overlapping worker waits counted once; useful work during a configured grace window is not hold time, disabled Smart Turn has `null`, and an enabled decision with no blocked gate is zero (**Reported**).[^s2s-supporting-docs]
- Configured grace/delay and Smart Turn analysis are no longer part of the terminal timing record, stages overlap and must not be summed to reconstruct E2E, and remote timings measured by this server include network transfer and provider waits rather than provider-only inference time (**Reported**).[^s2s-supporting-docs]

## Coverage matrix

- `stt` has a measured field for `parakeet-tdt`, `openai`, `openai-realtime`, `vllm-realtime`, `whisper`, `whisper-mlx`, `mlx-audio-whisper`, `faster-whisper`, and `qwen3-asr`, with `parakeet-unified` and `paraformer` marked `n/a` pending coverage (**Reported**).[^s2s-supporting-docs]
- `llm` is measured for every built-in LLM backend (`transformers`, `mlx-lm`, `responses-api`, `chat-completions`) (**Reported**).[^s2s-supporting-docs]
- `tts_ttfa` and `e2e` are measured only for `qwen3` and `openai`; `chatTTS`, `facebookMMS`, `omnivoice`, `pocket`, `kokoro`, and `supertonic` are `n/a` pending coverage (**Reported**).[^s2s-supporting-docs]
- `--stt none` deliberately has no STT measurement, and any field is `n/a` when its stage did not run, produced no audio, or its measurement was unavailable (**Reported**).[^s2s-supporting-docs]
- Tool follow-ups have separate response keys and do not repeat the originating turn's VAD/Smart Turn measurements, while their E2E keeps the originating speech-end timestamp and therefore includes intervening tool work (**Reported**).[^s2s-supporting-docs]

## Relationships

- Part of [HF Speech-to-Speech Pipeline](speech-to-speech-pipeline.md): this defines the per-response latency fields that pipeline logs and echoes in Realtime metadata (**Synthesis**).[^s2s-supporting-docs]
- Measured through the [Speech-to-Speech Realtime Engine](speech-to-speech-realtime-engine.md), whose `_send_loop` emits the terminal event carrying the record, and surfaced by the [Speech-to-Speech Browser Demo](speech-to-speech-browser-demo.md) timings panel (**Synthesis**).[^s2s-supporting-docs]
- Compare with the latency budgets in [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and [Cascaded Voice-Agent Blueprint](cascaded-voice-agent-blueprint.md), which state target budgets rather than measured per-stage server timings (**Synthesis**).[^s2s-supporting-docs]

## Coverage and limits

- Source inspected statically only: the latency guide was read as captured Markdown; no server was run and no latency record was produced or measured, so the schema, stage boundaries, and coverage matrix are source assertions transcribed without independent verification (**Synthesis**).[^s2s-supporting-docs]
- The guide defines measurement semantics but publishes no numeric latency results, so it cannot support cross-backend latency comparisons by itself (**Reported**).[^s2s-supporting-docs]
- The schema `version: 2`, reserved metadata key, 512-character and 16-slot Realtime limits, and the backend coverage list carry `stale_after: 2027-10-07` under the `pipeline` domain rule (**Synthesis**).[^s2s-supporting-docs]

[^s2s-supporting-docs]: [huggingface/speech-to-speech supporting docs](../raw/speech-to-speech-docs/README.md) — a capture at upstream revision `f9c23282a564cbe5b1f015ccb36d58e941de8520` (2026-10-07). Locators: `docs/response-latency.md` → title plus example log line, `response.done` metadata key `speech_to_speech.turn_latency`, version-2 schema JSON, version-2 rename/removal paragraph, precision paragraph, 512-character/16-slot limits, `stt`/`llm`/`tts_ttfa` coverage table, and the bulleted stage definitions for `stt`, `llm`, `tts_ttfa`, `e2e`, `vad_decision_s`, `smart_status`, and `hold_s` plus the overlap/remote-timing closing paragraph. Limitations: the guide is a single captured file; no `serve`/`local` run, log capture, or metadata round-trip was performed, and `examples/` and implementation sources that emit the record are excluded by the capture.
