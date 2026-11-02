---
type: Concept
title: Nemotron Labs Unified ASR 0.6B
description: NVIDIA 600M multilingual FastConformer-RNNT ASR with shared offline and buffered streaming inference, configurable context and reported latency-versus-WER comparisons.
tags: [stt, asr, streaming, multilingual, nvidia]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:33:30Z }
stale_after: 2027-05-02
sources:
  - id: unified-card
    resource: ../raw/nemotron-labs-unified-asr-0.6b.md
    kind: documentation
    title: NVIDIA Nemotron Labs Unified ASR 0.6B model card
---

**Reported:** NVIDIA's 600M-parameter `nvidia/nemotron-labs-unified-asr-0.6b` uses the same multilingual checkpoint for offline and buffered streaming ASR in 25 European languages, with punctuation and capitalization. Its recommended streaming configurations reach 160 ms of algorithmic latency, not necessarily 160 ms end-to-end latency; the card reports an accuracy/compute tradeoff against cache-aware streaming models. Results and implementation have not been independently verified.[^unified-card]

## Model and language selection

**Reported:** The 24-layer Unified FastConformer encoder, RNNT decoder, shared predictor and joint network operate in both modes. Training combines full-context attention and non-causal convolution offline with chunked attention, dynamic chunked convolutions and mode-consistency regularization in streaming; the encoder is initialized from [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md). A shared multilingual SentencePiece tokenizer is paired with a language-ID vector concatenated to encoder representations and projected to the decoder.[^unified-card]

The card lists bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, it, lv, lt, mt, pl, pt, ro, sk, sl, es, sv, ru and uk; Vietnamese is not listed. It recommends explicit `target_lang` for streaming at 560 ms or less: early language mistakes may already be emitted before sufficient context is available. `target_lang=auto` is available; all reported results use explicit language prompts. Input is mono 16 kHz waveform, at least 80 ms; output may be empty on non-speech. Training is reported as 10,000 hours human-transcribed plus 660,000 hours pseudo-labeled, predominantly Granary.[^unified-card]

## Streaming and deployment

**Reported:** Algorithmic latency is chunk plus right context, excluding model execution and other pipeline delays. The card recommends 5.6 s left context (also used in training):[^unified-card]

| Chunk (s) | Right context (s) | Algorithmic latency (s) |
|---:|---:|---:|
| 1.04 | 1.04 | 2.08 |
| 0.56 | 0.56 | 1.12 |
| 0.16 | 0.40 | 0.56 |
| 0.08 | 0.24 | 0.32 |
| 0.08 | 0.16 | 0.24 |
| 0.08 | 0.08 | 0.16 |

The pipeline recomputes left context at every step rather than caching encoder states; this is reportedly costlier than cache-aware streaming at equal algorithmic latency. Reducing left context to 2–3 s may speed inference at an accuracy cost; below 2 s is discouraged. Cache-aware decoding without matched training degrades accuracy, according to the card. Its experimental 80 ms chunk with zero right context is less stable, English-only in evaluation, and not recommended; this qualifies the 160 ms minimum in the headline, rather than establishing 80 ms as the supported minimum across languages.[^unified-card]

The card reports NeMo Speech 3.1.0, Linux and NVIDIA Volta, Ampere, Hopper and Blackwell compatibility. Offline uses `ASRModel.from_pretrained(...)` and `transcribe(..., target_lang=...)`; streaming uses NeMo's stateful chunked RNNT script with `left_context_secs`, `chunk_secs`, `right_context_secs` and `att_context_size_as_chunk=true`, or the buffered RNNT pipeline. These are documented routes, not tested here. The model card names OpenMDW 1.1 and claims commercial and non-commercial use; the actual license terms were not inspected.[^unified-card]

## Reported ASR evaluation

WER (%) is lower-is-better; both reference and prediction are normalized. Streaming uses 5.6 s left context and explicit language ID. The 25-language average is over 44 dataset-language runs across FLEURS, MCV and MLS, not a simple average of language averages. The English seven-set suite includes cleaned AMI, GigaSpeech and VoxPopuli and AA-chunked Earnings22 scored per call; it is not directly comparable to the older uncleaned suite.[^unified-card]

| Suite / model | Offline | 1.12 s | 0.56 s | 0.32 s | 0.16 s |
|---|---:|---:|---:|---:|---:|
| English, unified | 4.68 | 5.41 | 5.68 | 6.27 | 7.87 |
| English, Nemotron 3.5 streaming | — | 7.26 | 7.58 | 7.97 | 8.90 |
| Multilingual HF, 14 runs, unified | 4.61 | 5.69 | 6.36 | 7.27 | 9.95 |
| Multilingual HF, Nemotron 3.5 streaming | — | 7.22 | 7.60 | 8.01 | 8.53 |
| 25 languages, unified | 9.49 | 11.85 | 13.25 | 15.24 | 19.19 |
| 25 languages, Nemotron 3.5 streaming | — | 20.00 | 20.91 | 21.81 | 22.77 |

**Reported:** Parakeet TDT V3 offline scores 4.93, 4.68 and 10.55 respectively on those three suites. The unified model loses to the cache-aware baseline on the 14-run multilingual suite at 160 ms, despite winning the other displayed comparisons. Individual language means vary substantially: Spanish 3.61 offline / 7.15 at 160 ms versus Latvian 21.93 / 47.48. Hardware, runtime throughput, memory, uncertainty and independent reproduction are not supplied with these ASR comparisons.[^unified-card]

## Speech translation cascade

**Reported:** In a FLEURS cascade with Riva-Translate-4B-Instruct-v2, longest-common-prefix policy (`waitk=-1`) and 800 ms end-of-utterance window, 0.56 s chunk plus 0.56 s right context yields COMET 81.4 / LAAL 2.40 s English→X and 81.7 / 2.58 s X→English, averaged over 23 language pairs per direction; Maltese is excluded because the translator does not support it. These lag figures are translation metrics, not ASR algorithmic latency. The example serves the LLM via vLLM and warns to use a separate NeMo environment because of dependency-extra conflicts.[^unified-card]

## Relationships

- **Uses:** [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md) initializes the encoder; the source compares their offline results.[^unified-card]
- **Compared with:** [Nemotron 3.5 ASR Streaming 0.6B](nemotron-3.5-asr-streaming-0.6b.md) is the cache-aware streaming baseline, with different context and compute characteristics.[^unified-card]
- **Cataloged by:** [ASR/STT Model Survey](asr-stt-model-survey.md).

## Evidence and coverage limits

The local model-card capture was inspected statically in full; no revision or capture date is stated. It reports a 2026-10-27 release. The three relative figures under `raw/figures/` are absent; the comparison data and main architecture and cascade claims are available in the card text, but any additional diagram-only detail is unavailable. Remote weights, NeMo scripts/configuration, datasets, license, cited papers and translation model were not inspected; no install, inference, benchmark or hardware measurement was performed. No throughput, VRAM, timestamps, diarization, endpoint latency or Vietnamese capability is established by this capture. The source is a vendor model card, so promotional and numerical claims remain **Reported**, not independent verification.[^unified-card]

[^unified-card]: [NVIDIA model card](../raw/nemotron-labs-unified-asr-0.6b.md), opening and supported languages; Model Architecture and Language-ID prompting; Setting up Streaming Configuration and Streaming Inference Limitation; How to Use, Input, Software Integration and Training Dataset; ASR Performance, Comparison with already released models, Multilingual and English Speech Recognition; Streaming Speech Translation and Running the Cascade; License/Terms of Use.
