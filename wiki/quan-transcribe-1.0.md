---
type: Concept
title: QUAN-Transcribe-1.0
description: Vietnamese 356M EmbeddingGemma 2 plus CTC ASR model with 0.48 s chunked streaming, reported 6.87% average Vietnamese WER, and Gemma-governed weights.
tags: [stt, asr, vietnamese, ctc, streaming]
status: stable
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T05:00:50Z }
stale_after: 2027-04-15
sources:
  - id: quan-captures
    resource: ../raw/QUAN-Transcribe-1.0/README-hf.md
    scope: ../raw/QUAN-Transcribe-1.0/
    kind: documentation
    title: QUAN-Transcribe-1.0 model card and inference README captures
---

QUAN-Transcribe-1.0 (`qnguyen3/QUAN-Transcribe-1.0`) is a Vietnamese-only 356M-parameter recognizer combining an EmbeddingGemma 2 audio encoder with a CTC reader: one forward pass per utterance rather than autoregressive decoding. The same weights support full-context and 0.48 s chunked streaming. Its card reports 6.87% average WER and 3,713× realtime on one H100; these are **Reported**, not independently verified results or live microphone latency measurements.[^quan-captures]

## Architecture, training, and output

**Reported:** the USM-style Conformer encoder has 12 layers, with only its top two fine-tuned. A learned mixture of encoder layer outputs feeds a six-layer Transformer reader (`d=768`) trained with CTC. Output vocabulary is 14,917 Gemma tokenizer tokens, approximately one token per Vietnamese syllable. Dynamic reader chunk sizes during training enable streaming atop the encoder's chunked attention.[^quan-captures]

Training used about 2,800 hours from Bud500, viVoice, VLSP2020, FPT FOSD, InfoRe 1/2, LSVSC, ViMD, Common Voice 17, FLEURS, and PhoAudiobook, including numbers spelled as words; the card claims about three hours on 8×H100. Output is lowercase Vietnamese without punctuation and with numbers as words. Inputs are converted to 16 kHz mono by the inference package (**Reported**).[^quan-captures]

## Reported Vietnamese benchmark

The card says all models used the same utterances, normalization and scoring, greedy decoding, and one H100 per model at bf16/fp16. Speed is audio duration divided by waveform-to-text wall time. API rows nevertheless show hardware-independent `N/A` speed; their actual execution setup is not explained. Batch size, exact normalization rules, dataset splits/counts and uncertainty are not provided in this table (**Observed documentation limits**).[^quan-captures]

| QUAN test set label | WER |
|---|---:|
| bud500 | 1.62% |
| cv17 | 10.19% |
| fleurs | 6.75% |
| gigaspeech2 | 12.34% |
| lsvsc | 5.48% |
| phoaudiobook | 1.35% |
| vimd | 9.05% |
| VIVOS | 8.15% |
| **Average** | **6.87%** |

All values are **Reported**. Within this vendor table QUAN's average is below Gemini-Flash-3.8 (6.92%), MAI-Transcribe-2.0 (6.96%), Cohere Transcribe 03-2026 and Qwen3-ASR-1.7B (both 7.01%), and PhoWhisper-large (7.21%). However Qwen3-ASR-1.7B has lower fleurs/gigaspeech2 WER (4.88%/8.47%), while PhoWhisper-large has lower cv17/phoaudiobook/VIVOS (9.12%/0.87%/4.52%). This is not an independently established universal SOTA ranking (**Synthesis**).[^quan-captures]

The table reports speeds of 3,713× for QUAN, 430× for Cohere, 224× for Qwen3-ASR-1.7B and 197× for PhoWhisper-large. These throughput figures do not establish time-to-stable-text or endpoint-to-final latency, CPU performance, concurrency capacity or a VRAM budget (**Reported** figures; distinction **Synthesis**).[^quan-captures]

## Greedy, streaming, and optional LM evaluation

The inference README reports FLEURS `vi_vn` valid greedy WER of **6.71% full context versus 8.40% streaming**. Separately, its optional four-gram KenLM evaluation uses beam 32, alpha 0.3, beta 1.0, tuned on valid sets:[^quan-captures]

| Digit-filtered subset | Utterances | Greedy WER | + LM WER |
|---|---:|---:|---:|
| FLEURS valid | 317 | 6.71% | 4.79% |
| FLEURS test | 679 | 7.10% | 5.03% |
| Common Voice 17 valid | 641 | 6.58% | 5.05% |
| Common Voice 17 test | 1,274 | 9.64% | 7.32% |

These subsets exclude references containing digits. Do not silently replace the card's fleurs 6.75%/cv17 10.19% with these filtered-test values or compare LM decoding to greedy as the same operating point (**Synthesis**). Training and evaluation name some of the same corpora; split disjointness cannot be established from these captures, which is not proof of leakage. No confidence intervals or matched streaming LM results are supplied.[^quan-captures]

## License and deployment relevance

The weights derive from EmbeddingGemma 2 and are subject to **Gemma Terms of Use**, not an asserted MIT/Apache weight license. The base encoder is gated: accept its model-page terms and authenticate before first-use download. Code licensing is not separately established by the captured README; the linked terms themselves were not inspected.[^quan-captures]

**Synthesis:** this is a candidate for specialized Vietnamese chunked partial transcription plus final re-decoding, not yet a validated replacement for a cache-aware recognizer. Its lack of punctuation and written-form numerals needs downstream handling for entity-critical voice-agent tasks. See [inference and live streaming](quan-transcribe-inference.md) for recomputation, endpointing and LM costs.[^quan-captures]

## Relationships

- Uses [QUAN-Transcribe Inference and Live Streaming](quan-transcribe-inference.md) as its documented deployment interface.[^quan-captures]
- Compared in [ASR/STT Model Survey](asr-stt-model-survey.md) and [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md); selection remains conditional on target-hardware and live-text evaluation (**Synthesis**).

## Coverage and limits

- **Observed:** both local files, `README-hf.md` (canonical entry point) and `README-github.md` (supporting inference documentation), were read completely. They form one source package; no commit, publication date or capture timestamp is supplied. Upstream identities are the `qnguyen3` Hugging Face model and `qnguyen3/QUAN-Transcribe` GitHub repository.[^quan-captures]
- Not captured/inspected: upstream implementation, dependency manifest, tests, weights/tokenizer, base encoder, `lm/` binary and training text, benchmark scripts/data, and license terms. No installation, authentication, download, transcription or benchmark was executed. Instructions and snippets were inspected only as documentation.
- Excluded: repeated quick-start examples and exhaustive rival rows already resolvable in the raw benchmark; no material local attachments exist beyond the two READMEs. Corpus consent, data rights, robustness to noisy calls/code-switching, detailed training hyperparameters and checkpoint-selection procedure are not established by these captures.
- `stable` means the intended documentation synthesis is complete, not independently verified capability; no `verified` metadata is set.

[^quan-captures]: [Model card](../raw/QUAN-Transcribe-1.0/README-hf.md) — opening bullets; `Quick start`; `Model` (architecture and training corpora); `Benchmark` protocol and table; `License`. Supporting [inference README](../raw/QUAN-Transcribe-1.0/README-github.md) — opening architecture summary; `Install`; `Usage` I/O; `Streaming mode`; `Live microphone`; `Optional n-gram language model`; `Accuracy check` filtered subsets, tuning and timings; `License`.
