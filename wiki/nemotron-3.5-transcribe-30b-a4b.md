---
type: Concept
title: Nemotron 3.5 Transcribe 30B-A4B
description: NVIDIA offline multilingual speech-LLM with speaker-attributed transcription, long-form audio, CTC timestamps, reported benchmark results, and H100 serving options.
tags: [stt, asr, nemotron, multilingual, diarization]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:30:00Z }
stale_after: 2027-05-02
sources:
  - id: nemotron-transcribe-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B.md
    kind: documentation
    title: NVIDIA Nemotron 3.5 Transcribe model card
---

NVIDIA describes Nemotron 3.5 Transcribe as an **offline**, instruction-conditioned speech-language model for up to one-hour recordings, with multilingual ASR, speaker-attributed transcription and optional word alignment. Its 34B total / approximately 4.3B active parameters include a speaker-aware audio encoder; the card reports BF16, FP8 and NVFP4 variants and OpenMDW-1.1 licensing. Internal audio chunking is not native realtime streaming (**Reported**).[^nemotron-transcribe-card]

## Architecture, tasks and limits

- Hybrid Mamba-2–Transformer MoE language backbone, Transformer ASR encoder, approximately 99M [Nemotron 3 Diarization](nemotron-3-diarization.md) speaker encoder, projection and CTC timestamp heads; 65,536-token context. Input is 16 kHz mono PCM; the 30-second encoder chunks do not imply streaming or a 30-second recording limit (**Reported**).[^nemotron-transcribe-card]
- The card claims 40 languages, with transcription, code-switching, language ID, contextual terms, speaker tags, translation and audio questions. Vietnamese is listed as supported for ASR and code-switching, not specified for English translation or multispeaker ASR. Audio understanding and spoken instructions were evaluated only in English. Speaker tags distinguish voices within a recording, not identity (**Reported**).[^nemotron-transcribe-card]
- The model can hallucinate speech, misattribute speakers or be biased by misleading contextual terms; prompt injection and sensitive audio require application-level controls and representative evaluation. Training includes personal data, and synthetic PII tasks do not establish reliable redaction (**Reported**).[^nemotron-transcribe-card]
- Training is reported as approximately 1.72M unique indexed audio hours and 6.53M exposure hours; indexed records are not deduplicated recordings. Public, vendor, pseudo-labeled and synthetic mixtures were used, including meeting sources also named among evaluation datasets; overlap at recording level is not resolved by the card (**Reported**).[^nemotron-transcribe-card]

## Quality and comparability

NVIDIA's results were captured 2026-10-12; ASR uses temperature 0, reasoning off, and the card's generation-loop cleanup. The card says ASR benchmark execution used vLLM 0.28.0 and MTP2; its deployment quick start uses vLLM 0.32.0. These are vendor results, not independently reproduced (**Reported**).[^nemotron-transcribe-card]

| Evaluation | Reported result | Conditions |
| --- | ---: | --- |
| English Open ASR | 4.71% WER | Equal mean of nine datasets |
| Long-form Open ASR | 10.98% WER | Equal mean of three sets; 55-minute chunks with 5-second overlap |
| Multilingual Open ASR | 4.62% WER | Equal mean of seven language means, not Vietnamese |
| Vietnamese FLEURS | 2.90% CER | Standalone FLEURS, not the multilingual leaderboard protocol |
| Multispeaker | 15.80% mean cpWER | Full-session AMI, CALLHOME, Mixer 6 and NOTSOFAR-1 |
| ContextASR-Bench | 3.33% / 1.71% WER | No context / fine context |

Metrics, normalization and datasets differ; do not directly compare WER to CER or the standalone FLEURS scores to leaderboard scores. The card lists AMI among training families without establishing recording-level overlap (**Reported**).[^nemotron-transcribe-card]

## Deployment and prompting

- NVIDIA's vLLM 0.32.0 / latest NeMo Speech example uses one H100 80 GB, an OpenAI-compatible chat completions endpoint, BF16 and MTP8; it requires remote code trust. For transcription, omit the system message, use a task-specific user prompt, temperature 0 and reasoning disabled. Increase completion limits for dense long recordings (**Reported**).[^nemotron-transcribe-card]
- CTC timestamp capture needs the V1 model runner and timestamp middleware; requests use one recording, `stream=false`, `n=1`, and must check the alignment `error`. Diarization segments, not word timestamps, are recommended for diarization scoring (**Reported**).[^nemotron-transcribe-card]
- SGLang-Omni 0.2.0 / SGLang 0.5.22 offers whole-file transcription on one GPU, but this integration does not provide word timestamps, speaker-attributed output, translation or speculative decoding. Transformers and selected GGML hardware routes are also documented (**Reported**).[^nemotron-transcribe-card]
- The vendor reports up to 2,238 audio seconds/s and 0.13 s for a 30 s clip on an RTX PRO 6000 Blackwell NIM with optimized NVFP4 / speculative decoding; those optimizations are not in the open-source release, and throughput is not live end-to-end latency. [DFlash2 and MTP](nemotron-3.5-transcribe-speculative-decoding.md) have different workload and timestamp tradeoffs (**Reported**).[^nemotron-transcribe-card]

## Contradictions and evidence limits

The language matrix labels Norwegian “Supported” while marking ASR, translation, multispeaker and code-switching as unspecified, despite an explicit 40-language claim; FLEURS Norwegian WER is 63.76%. The matrix also omits translation support for Vietnamese and several other languages while its evaluation table reports translation scores for them; measured experimental scores do not establish supported production behavior (**Observed**, **Reported**).[^nemotron-transcribe-card]

The card states that the “Exact Understanding and Reasoning Prompts” were used, but several corresponding entries in “All Evaluated Prompts” have different system text; precise reproduction requires resolving which instructions were actually run (**Observed**).[^nemotron-transcribe-card]

Coverage: the full local card was inspected statically. Relative `hero.png`, `architecture.png`, `serving_performance.png`, `THIRD_PARTY_NOTICES.md` and `CONTRIBUTING.md` are absent beside the capture; the throughput figure may contain additional conditions unavailable here. The remote technical report, model weights, code, license text, datasets, benchmarks and serving integrations were not inspected. No code, model or benchmark was run; source revision and capture timestamp are unknown. Draft reflects those material evidence limits.

## Relationships

- Uses [Nemotron 3 Diarization](nemotron-3-diarization.md) as its speaker encoder (**Reported**).[^nemotron-transcribe-card]
- Uses optional [DFlash2 speculative decoding](nemotron-3.5-transcribe-speculative-decoding.md); unlike the separate [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md), this model is offline (**Synthesis**).[^nemotron-transcribe-card]

[^nemotron-transcribe-card]: [NVIDIA model card](../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B.md), Model Summary; Model Architecture; Language Support Matrix; Inputs; Training, Testing, and Evaluation Datasets; Benchmark Results; Efficiency; Inference Setup and Prompts; Bias, Explainability and Privacy.
