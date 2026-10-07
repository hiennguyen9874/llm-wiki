---
type: Concept
title: Turn Detection Models
description: Comparison of semantic/prosodic end-of-turn detectors for voice agents — Pipecat Smart Turn v3, LiveKit turn detectors, Namo, and TEN — with language coverage, Vietnamese accuracy, latency, licenses, and fallback-timeout practice.
tags: [vad, endpointing, turn-detection, pipeline, vietnamese]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T15:04:00Z }
stale_after: 2027-10-06
sources:
  - id: claude-pipeline-report
    resource: ../raw/Claude-pipeline-recommend.md
    kind: llm-response
    title: Claude voice-pipeline research report
  - id: smart-turn-v3.2
    resource: ../raw/smart-turn/README.md
    scope: ../raw/smart-turn/
    kind: documentation
    revision: github 4786657e242dfe77dd138699ac564ee074a2a543; hf f766f81d3cfdf7737ac64aad813d91bbfd56bf93
    title: Smart Turn v3.2 (pipecat-ai) capture
---

Turn detection (semantic endpointing) decides whether a user who paused has actually finished speaking; it runs after VAD reports silence. Among open options the report finds Pipecat Smart Turn v3 the only small, permissively licensed detector covering Vietnamese, while LiveKit's detectors cover 14 languages without Vietnamese; a silence fallback timeout remains advisable because Vietnamese is Smart Turn v3.2's weakest language in its own vendor benchmark (**Reported**).[^claude-pipeline-report][^smart-turn-v3.2]

## Comparison

| Model | Size | Languages | Vietnamese | Latency | License |
|---|---|---|---|---|---|
| Pipecat Smart Turn v3 / v3.1 / v3.2 | ~8M params; CPU int8 8 MB, GPU fp32 32 MB | 23 | Yes: v3.2 accuracy 82.47% (GPU) / 79.38% (CPU), FPR 9.56/8.86%, FNR 7.97/11.75% (vendor, 1,004 samples) | 10 ms on some CPUs, under 100 ms on most cloud instances; ~65 ms on Pipecat Cloud (vendor) | BSD-2; open weights, data, and training script |
| LiveKit Turn Detector (text, multilingual) | <500 MB RAM | 14 | No | ~25 ms | Open weights under LiveKit's own license |
| LiveKit Turn Detector v1 (audio) | — | 14 | No | — | Free on LiveKit Cloud; full self-hosting unverified |
| Namo Turn Detector (community, `dangvansam`) | ~200 MB (VN build) | VN and multilingual | Yes, author-measured | 4–36 ms | LiveKit plugin; no independent benchmark |
| TEN Turn Detection | — | — | Not checked | — | — |

All rows are as reported, with vendor/author origin noted by the report (**Reported**); Smart Turn's architecture, input protocol, and per-language figures come from the captured primary package (**Reported**).[^claude-pipeline-report][^smart-turn-v3.2]

## Operating practice

- Smart Turn runs after VAD silence (Pipecat recommends `stop_secs=0.2`) and looks at the last 8 s of audio; it is prosody-based rather than transcript-based, so it does not depend on STT quality (**Reported**).[^claude-pipeline-report]
- On the captured v3.2 benchmark its Vietnamese FPR is 9.56% (GPU fp32) / 8.86% (CPU int8), accuracy 82.47% / 79.38%, and FNR 7.97% / 11.75% over 1,004 samples — the weakest of its 23 languages, so roughly one in ten "turn finished" calls fires while the user is still talking on GPU (**Reported**; one-in-ten reading **Synthesis**).[^smart-turn-v3.2]
- Add a fallback timeout that commits the turn after ~1.2–1.5 s of silence (**Reported**).[^claude-pipeline-report]
- Replace Smart Turn with Namo or a fine-tuned model if Vietnamese false-interruption stays above 10%; measure turn-detection false-cutoff rate in evaluation (**Reported**).[^claude-pipeline-report]
- Latency budget share: VAD silence 200–300 ms plus Smart Turn 10–65 ms (**Reported**).[^claude-pipeline-report]

## Contradictions

- **Smart Turn Vietnamese figures:** the AI report states accuracy 81.27%, FP 14.84%, FN 3.88% over 1,004 samples for "Smart Turn v3", while the captured v3.2 vendor benchmark reports 82.47%/9.56%/7.97% (GPU fp32) and 79.38%/8.86%/11.75% (CPU int8) over the same 1,004 Vietnamese samples. The v3.0/v3.1 benchmark files were excluded from the capture as superseded, so which revision the report's figures describe is unresolved; the v3.2 capture is the current primary and neither claim is chosen (**Reported/Unverified**).[^claude-pipeline-report][^smart-turn-v3.2]

## Relationships

- Depends on [Silero VAD](silero-vad.md) (or another VAD) to signal silence before invocation (**Synthesis**).[^claude-pipeline-report]
- Compare with [Parakeet Realtime EOU 120M v1](parakeet-realtime-eou-120m-v1.md), which folds end-of-utterance detection into a streaming English ASR model instead of a separate audio classifier (**Synthesis**).[^claude-pipeline-report]
- Details of Pipecat Smart Turn's own architecture, input protocol, CPU/GPU variants, and per-language benchmark are in [Smart Turn v3.2](smart-turn.md) (**Synthesis**).[^smart-turn-v3.2]
- Used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) and integrated in [Voice Agent Frameworks](voice-agent-frameworks.md) (Pipecat `LocalSmartTurnAnalyzerV3`) (**Synthesis**).[^claude-pipeline-report]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md): end-of-turn errors and false interruptions are the two turn-taking failure modes measured together (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- Smart Turn v3.2 now has a captured primary package (GitHub README, model card, and CPU/GPU benchmark reports), inspected statically; its architecture, input protocol, and per-language figures come from that capture rather than the report (**Observed** capture integrity; figures **Reported**).[^smart-turn-v3.2]
- LiveKit, Namo, and TEN remain relayed by the AI-compiled report; their primary docs are not in `raw/` (**Synthesis**).[^claude-pipeline-report]
- TEN Turn Detection and LiveKit audio-detector self-hosting were not checked by the report; no Smart Turn weights, code, or benchmark was executed or reproduced here (**Reported**).[^claude-pipeline-report][^smart-turn-v3.2]

[^smart-turn-v3.2]: [Smart Turn v3.2](smart-turn.md) — Identity and license (BSD-2, Open weights/datasets/training script); Architecture and variants (Whisper Tiny + linear classifier, ~8M params, 8 MB int8 CPU / 32 MB fp32 GPU); Input and operating protocol (16 kHz mono PCM, 8 s window, leading padding, re-run whole turn, VAD-gated); Benchmark (31,527 samples, overall CPU/GPU and Vietnamese 1,004-sample tables); Relationships; Contradictions (GitHub v3.2 vs HF card v3.1 dataset naming); Coverage and limits.

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` turn-detection bullet; `Key Findings` 4; `PHẦN 1` §3 `Turn detection / semantic endpointing` table and following paragraph (`stop_secs=0.2`, 8 s window, prosody-based, FP 1/7, 1.2–1.5 s timeout); `PHẦN 2` mermaid flowchart (Smart Turn v3 + timeout 1.2s); `Ngân sách độ trễ` table; `Code mẫu` Pipecat note (`LocalSmartTurnAnalyzerV3`); `Recommendations` › `Khi nào nên thay thành phần`; `Caveats`.
