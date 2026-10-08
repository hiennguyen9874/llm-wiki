---
type: Concept
title: Gipformer 1.5 68M RNNT
description: 68M Zipformer-RNNT Vietnamese ASR (ONNX int8, MIT) reporting best WER on call-center and four domain test sets versus PhoWhisper, ChunkFormer, Qwen3-ASR and Zipformer-30M, with no streaming, latency, or training-data details in the card.
tags: [stt, asr, vietnamese, zipformer, rnnt, onnx, int8, edge, call-center]
status: stable
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T12:00:00Z }
stale_after: 2027-10-07
sources:
  - id: gipformer-card
    resource: ../raw/gipformer1.5-68M-rnnt.md
    kind: documentation
    title: Gipformer 1.5 - Efficient Vietnamese Speech Recognition (Hugging Face model card)
---

`g-group-ai-lab/gipformer1.5-68M-rnnt` is a 68M-parameter Vietnamese ASR model from G-Group AI Lab, based on the Zipformer Transducer (RNN-T) architecture, shipped for ONNX Runtime with int8 quantization and positioned for offline on-device and edge use under the MIT license (**Reported**).[^gipformer-card] Its card claims best WER on call-center and domain-specific test sets; the numbers are vendor-run and not reproduced (**Reported**).

## Identity

- Developer G-Group AI Lab; library `onnxruntime`; language `vi`; tags include `rnnt`, `zipformer`, `int8`, `edge-device`; MIT license (frontmatter **Observed**; card links a LICENSE file not captured).[^gipformer-card]
- Source code at `ggroup-ai-lab/gipformer` (Quick Start) and a browser demo Space; neither captured.[^gipformer-card]
- Sibling predecessor in the same table: `gipformer-68M-rnnt`, see [Gipformer 68M RNNT](gipformer-68m-rnnt.md) (its card gives slightly different figures for some shared rows).

## Reported benchmark (WER %, lower is better)

Predictions and labels are lowercased, punctuation-stripped, and numbers converted to spoken form before scoring; the test-set hygiene is not described (**Reported**).[^gipformer-card]

| Test set | gipformer1.5-68M | gipformer-68M | Zipformer-30M-6000h | chunkformer-large-vie | Qwen3-ASR-1.7B | PhoWhisper-large |
|---|---:|---:|---:|---:|---:|---:|
| tele-medium (private) | **15.44** | 15.53 | 19.53 | 27.60 | 26.34 | 26.82 |
| tele-hard-north (private) | 26.24 | **25.10** | 38.13 | 46.30 | 46.80 | 50.39 |
| tele-hard-middle (private) | 33.31 | **32.27** | 44.73 | 51.91 | 59.85 | 59.44 |
| tele-hard-south (private) | **32.48** | 32.62 | 41.58 | 49.09 | 51.84 | 56.70 |
| vi-asr-tech | **27.49** | 36.59 | 29.77 | 39.81 | 27.95 | 42.94 |
| vi-asr-edu | **23.32** | 29.81 | 25.91 | 37.20 | 29.93 | 44.99 |
| vi-asr-finance | **22.34** | 29.67 | 25.86 | 34.31 | 34.09 | 40.54 |
| vi-asr-pubadmin | **14.82** | 20.09 | 17.92 | 29.30 | 31.83 | 33.78 |
| vivos | 4.25 | **4.12** | 4.55 | 4.18 | 7.17 | 4.73 |
| Common-Voice | 6.45 | 6.63 | **4.16** | 6.94 | 10.76 | 8.60 |
| vlsp-t1 | 13.37 | 13.39 | **11.78** | 14.09 | 16.29 | 13.70 |
| VietMed | **19.23** | 19.41 | 19.91 | 19.59 | 20.21 | 24.37 |
| MultiMED | **19.17** | 19.35 | 19.88 | 22.60 | 20.11 | 24.47 |
| LSVSC | 8.97 | 9.04 | 9.04 | 8.85 | 9.64 | 10.08 (best: PhoASR-whisper-small 7.59) |
| Fleurs | 12.65 | 12.92 | 13.03 | 14.17 | **10.13** | 12.62 |
| ViMD | **7.00** | 7.17 | 7.18 | 11.77 | 11.16 | 11.18 |

Reading (**Synthesis** from the table): the 1.5 release's gain over gipformer-68M is concentrated in the four domain sets (tech 36.59→27.49, pubadmin 20.09→14.82); on private call-center sets it is within about one WER point of the predecessor, and slightly worse on north and middle. It does not win every column: Zipformer-30M leads Common-Voice and vlsp-t1, Qwen3-ASR-1.7B leads Fleurs, and PhoASR-whisper-small leads LSVSC. The card's "best on all four call-center sets" refers to the gipformer family, not strictly to 1.5 (north and middle are won by the predecessor).[^gipformer-card]

The card also claims no other model comes within 9 WER points on any of the three hard call-center subsets; checked against the table, the nearest non-gipformer entry is Zipformer-30M (38.13 vs 26.24 north, 44.73 vs 33.31 middle, 41.58 vs 32.48 south), gaps of about 9–12 points (**Observed** arithmetic on **Reported** figures).[^gipformer-card]

Private call-center sets (tele-*) are not published, so those results cannot be independently checked; the four vi-asr-* sets are public datasets on Hugging Face under `g-group-ai-lab`.[^gipformer-card]

## Deployment relevance

- Small size and ONNX int8 packaging suit CPU/edge and local-privacy deployments (**Reported**); no RTF, CPU model, memory, or latency figure is given.[^gipformer-card]
- The card does not state whether the model streams, chunk/lookahead settings, endpointing, hotwords, punctuation, or ITN. RNN-T architecture alone does not establish native streaming (**Unverified**; see [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md) for the same caveat).[^gipformer-card]
- Training data, model scale-up steps relative to gipformer-68M, and version changes are not described.

## Relationships

- Compared against [ChunkFormer Vietnamese](chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md), [PhoWhisper](phowhisper.md), [Qwen3-ASR family](qwen3-asr-family.md), and [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md) (Vietnamese checkpoint listed as `nvidia/parakeet-ctc-0.6b-Vietnamese`) in the card's own table.
- Same developer as [Gwen-TTS 0.6B](gwen-tts-0.6b.md) and [G-OmniVoice](g-omnivoice.md) (G-Group AI Lab).
- Reference inference code: [Gipformer Inference Repository](gipformer-inference-repo.md) (sherpa-onnx offline recognizer and icefall PyTorch scripts; no streaming code).
- Candidate for [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) only after streaming behavior is verified.

## Coverage and limits

The single model-card capture was read fully and statically. Weights, GitHub repo, Quick Start, demo Space, datasets, LICENSE file, and the cited papers were not fetched; no inference or benchmark was run. Benchmark figures are vendor-reported; cross-model comparison depends on the vendor's own normalizer and runs.[^gipformer-card]

[^gipformer-card]: [Gipformer 1.5 model card](../raw/gipformer1.5-68M-rnnt.md) — frontmatter (license, language, tags); Highlights; Benchmark Results (WER%) table and Normalization note; Dataset Descriptions; "Call Center Domain" section.
