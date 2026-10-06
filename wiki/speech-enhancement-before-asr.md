---
type: Concept
title: Speech Enhancement Before ASR
description: Conflicting evidence on whether denoising or speech enhancement placed before ASR helps or hurts recognition in noise, with the practice of denoising only the VAD branch and A/B testing.
tags: [pipeline, stt, noisy-audio, speech-enhancement, denoising]
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

Placing a speech-enhancement (denoising) model in front of ASR is not a safe default: two reported studies found enhancement degraded Whisper and other ASR systems in every tested configuration, while a third found its enhancement models improved ASR on CHiME-4, so the effect depends on the enhancement model and data and must be A/B tested; the report's working practice is to denoise only the VAD/barge-in branch and feed ASR the original AEC-processed audio (**Reported**).[^claude-pipeline-report]

## Evidence that enhancement hurts ASR

- "When De-noising Hurts" (arXiv 2512.17562, 12/2025) applied MetricGAN-plus-voicebank before Whisper, Parakeet, Gemini Flash 2.0, and Parrotlet-a on 500 medical recordings under 9 noise conditions and concluded "speech enhancement preprocessing degrades ASR performance across all noise conditions and models"; original noisy audio had lower semWER than enhanced audio in all 40 configurations, with absolute degradation 1.1%–46.6% semWER, and Whisper at 10 dB SNR went from 8.82% to 25.83% semWER (**Reported**).[^claude-pipeline-report]
- Islam, Nahar, and Hamid (University of Rajshahi, arXiv 2603.04710) used SAM-Audio before Whisper on Bengali and English and reported "WER and CER increase in every evaluated model–dataset configuration": Whisper large-v3 Bengali WER 65.83% → 77.35%, Whisper base English WER 10.53% → 21.66% (**Reported**).[^claude-pipeline-report]

## Evidence that enhancement helps ASR

- Yang, Pandey, and DeLiang Wang (arXiv 2403.06387) concluded "ARN and CrossNet enhanced speech both translate to improved ASR results", reaching 3.32% (simulated) and 4.44% (real) WER on single-channel CHiME-4 with an ASR backend trained on clean speech, and ARN also improved Whisper in most configurations they tried (**Reported**).[^claude-pipeline-report]

## Practice

- Default: no denoise on the ASR branch; optional light denoise (RNNoise, DeepFilterNet 3) only on the VAD/barge-in branch; A/B test enhancement with Vietnamese WER/CER at SNR 0/5/10/20 dB (**Reported**).[^claude-pipeline-report]
- Higher-leverage noise measures named instead: acoustic echo cancellation (WebRTC AEC3 via browser `echoCancellation: true`, SpeexDSP — mandatory with loudspeakers), speaker lock with ECAPA-TDNN/WeSpeaker/CAM++/TitaNet embeddings, duration-gated barge-in, confidence gating, and a hallucination blacklist (**Reported**).[^claude-pipeline-report]
- Open-source enhancement options listed: RNNoise (CPU-light), DeepFilterNet 2/3, GTCRN, DTLN, ClearerVoice-Studio (FRCRN, MossFormer2, target-speaker extraction), Resemble Enhance (offline); Krisp is closed/commercial; diarization (pyannote, NVIDIA Sortformer streaming, diart) only when several speakers are present (**Reported**).[^claude-pipeline-report]

## Contradictions

- Enhancement before ASR: arXiv 2512.17562 and arXiv 2603.04710 report consistent degradation (Whisper, Parakeet, Gemini Flash 2.0, Parrotlet-a; MetricGAN+ and SAM-Audio enhancers), while arXiv 2403.06387 reports improvement (ARN, CrossNet on CHiME-4, also with Whisper); the studies differ in enhancer, ASR backend, language, and domain, and none covers Vietnamese, so neither conclusion is chosen (**Reported**; resolution **Synthesis**).[^claude-pipeline-report]

## Relationships

- Used by [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md), which routes denoised audio only to VAD and raw AEC audio to ASR (**Synthesis**).[^claude-pipeline-report]
- Related to [SAM Audio GGUF](sam-audio-gguf.md): SAM-Audio is the separation model whose use before Whisper raised WER in arXiv 2603.04710 (**Synthesis**).[^claude-pipeline-report]
- Related to [Community-Reported Noisy On-Premise STT Selection](community-noisy-call-stt.md), which covers community preprocessing practice for noisy call transcription (**Synthesis**).[^claude-pipeline-report]
- Related to [Voice-Agent Barge-in and Echo Handling](voice-agent-barge-in-and-echo-handling.md) for AEC and speaker lock (**Synthesis**).[^claude-pipeline-report]

## Coverage and limits

- All three studies are cited secondhand by an AI-compiled report; none of the papers is in `raw/`, so quotes, numbers, and protocols are unverified here (**Synthesis**).[^claude-pipeline-report]
- None of the studies is on Vietnamese; the report itself notes this (**Reported**).[^claude-pipeline-report]

[^claude-pipeline-report]: [Claude voice-pipeline research report](../raw/Claude-pipeline-recommend.md) — locators: `TL;DR` noisy-environment bullets; `PHẦN 1` §2 `Tiền xử lý cho môi trường ồn` (AEC/noise-suppression/target-speaker/speaker-verification/diarization table and `Phát hiện quan trọng` paragraph on arXiv 2512.17562, 2603.04710, 2403.06387); `PHẦN 2` mermaid flowchart (denoise only for VAD branch); `Triển khai` evaluation bullet; `Recommendations` › `Lộ trình` Beta; `Caveats` (no Vietnamese denoise study).
