---
type: Concept
title: Turn Detection Models
description: Comparison of semantic/prosodic end-of-turn detectors for voice agents — Pipecat Smart Turn v3, LiveKit turn detectors, Namo, and TEN — with language coverage, Vietnamese accuracy, latency, licenses, and fallback-timeout practice.
tags: [vad, endpointing, turn-detection, pipeline, vietnamese]
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

Turn detection (semantic endpointing) decides whether a user who paused has actually finished speaking; it runs after VAD reports silence. Among open options the report finds Pipecat Smart Turn v3 the only small, permissively licensed detector covering Vietnamese, while LiveKit's detectors cover 14 languages without Vietnamese, and it pairs Smart Turn with a silence timeout because its Vietnamese false-positive rate is about one in seven (**Reported**).[^claude-pipeline-report]

## Comparison

| Model | Size | Languages | Vietnamese | Latency | License |
|---|---|---|---|---|---|
| Pipecat Smart Turn v3 / v3.1 / v3.2 | ~8M params; CPU int8 8 MB, GPU fp32 32 MB | 23 | Yes: accuracy 81.27%, FP 14.84%, FN 3.88% (vendor, 1,004 samples) | 12 ms on modern CPU; ~60–65 ms on cloud instances (vendor) | BSD-2; open weights, data, and training script |
| LiveKit Turn Detector (text, multilingual) | <500 MB RAM | 14 | No | ~25 ms | Open weights under LiveKit's own license |
| LiveKit Turn Detector v1 (audio) | — | 14 | No | — | Free on LiveKit Cloud; full self-hosting unverified |
| Namo Turn Detector (community, `dangvansam`) | ~200 MB (VN build) | VN and multilingual | Yes, author-measured | 4–36 ms | LiveKit plugin; no independent benchmark |
| TEN Turn Detection | — | — | Not checked | — | — |

All rows are as reported, with vendor/author origin noted by the report (**Reported**).[^claude-pipeline-report]

## Operating practice

- Smart Turn runs after VAD silence (Pipecat recommends `stop_secs=0.2`) and looks at the last 8 s of audio; it is prosody-based rather than transcript-based, so it does not depend on STT quality (**Reported**).[^claude-pipeline-report]
- Its Vietnamese FP 14.84% means roughly one in seven "turn finished" calls fires while the user is still talking; the report also notes Vietnamese accuracy is below the cross-language average (**Reported**; one-in-seven reading **Synthesis** of the report's own arithmetic).[^claude-pipeline-report]
- Add a fallback timeout that commits the turn after ~1.2–1.5 s of silence (**Reported**).[^claude-pipeline-report]
- Replace Smart Turn with Namo or a fine-tuned model if Vietnamese false-interruption stays above 10%; measure turn-detection false-cutoff rate in evaluation (**Reported**).[^claude-pipeline-report]
- Latency budget share: VAD silence 200–300 ms plus Smart Turn 10–65 ms (**Reported**).[^claude-pipeline-report]

## Relationships

- Depends on [Silero VAD](silero-vad.md) (or another VAD) to signal silence before invocation (**Synthesis**).[^claude-pipeline-report]
- Compare with [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md), which folds end-of-utterance detection into a streaming English ASR model instead of a separate audio classifier (**Synthesis**).[^claude-pipeline-report]
- Used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and integrated in [Voice Agent Frameworks](voice-agent-frameworks.md) (Pipecat `LocalSmartTurnAnalyzerV3`) (**Synthesis**).[^claude-pipeline-report]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): end-of-turn errors and false interruptions are the two turn-taking failure modes measured together (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- All figures are vendor or author claims relayed by an AI-compiled report; Smart Turn, LiveKit, Namo, and TEN primary docs are not in `raw/` (**Synthesis**).[^claude-pipeline-report]
- TEN Turn Detection and LiveKit audio-detector self-hosting were not checked by the report (**Reported**).[^claude-pipeline-report]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` turn-detection bullet; `Key Findings` 4; `PHẦN 1` §3 `Turn detection / semantic endpointing` table and following paragraph (`stop_secs=0.2`, 8 s window, prosody-based, FP 1/7, 1.2–1.5 s timeout); `PHẦN 2` mermaid flowchart (Smart Turn v3 + timeout 1.2s); `Ngân sách độ trễ` table; `Code mẫu` Pipecat note (`LocalSmartTurnAnalyzerV3`); `Recommendations` › `Khi nào nên thay thành phần`; `Caveats`.
