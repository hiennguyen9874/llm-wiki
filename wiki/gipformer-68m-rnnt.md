---
type: Concept
title: Gipformer 68M RNNT
description: 68M Zipformer-RNNT Vietnamese ASR (ONNX int8, MIT) from G-Group AI Lab reporting #1 WER on 9 of 12 benchmarks including four private call-center sets, with no streaming, latency, or training-data details in the card.
tags: [stt, asr, vietnamese, zipformer, rnnt, onnx, int8, edge, call-center]
status: stable
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-08T12:00:00Z }
stale_after: 2027-10-08
sources:
  - id: gipformer-68m-card
    resource: ../raw/gipformer-68M-rnnt.md
    kind: documentation
    title: Gipformer - Efficient Vietnamese Speech Recognition (Hugging Face model card, gipformer-68M-rnnt)
---

`g-group-ai-lab/gipformer-68M-rnnt` is the original 68M-parameter Vietnamese ASR model from G-Group AI Lab, based on the Zipformer Transducer (RNN-T) architecture, shipped for ONNX Runtime with int8 quantization and positioned for offline on-device and edge use under the MIT license (**Reported**).[^gipformer-68m-card] Its card claims best WER on 9 of 12 benchmarks, led by call-center sets; figures are vendor-run and not reproduced. The successor is [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md).

## Identity

- Developer G-Group AI Lab; library `onnxruntime`; language `vi`; tags include `rnnt`, `zipformer`, `int8`, `edge-device`; MIT license (frontmatter **Observed**; the linked LICENSE file was not captured).[^gipformer-68m-card]
- Source code (`ggroup-ai-lab/gipformer`, Quick Start), a browser demo Space and an AI-skills page are linked; none captured. The card gives no usage commands itself.[^gipformer-68m-card]

## Reported benchmark (WER %, lower is better)

Predictions and labels are lowercased, punctuation-stripped, and numbers converted to spoken form (**Reported**). The card compares against 10 other Vietnamese models on 12 test sets.[^gipformer-68m-card]

| Test set | gipformer-68M | Zipformer-30M-6000h | chunkformer-large-vie | VietASR-zipformer (68M) | Qwen3-ASR-1.7B | PhoWhisper-large |
|---|---:|---:|---:|---:|---:|---:|
| tele-medium (private) | **15.53** | 19.95 | 27.60 | 20.30 | 26.34 | 26.82 |
| tele-difficult-north (private) | **25.10** | 38.77 | 46.30 | 42.21 | 46.80 | 50.39 |
| tele-difficult-middle (private) | **32.27** | 45.19 | 51.91 | 49.01 | 59.85 | 59.44 |
| tele-difficult-south (private) | **32.62** | 43.89 | 49.09 | 47.86 | 51.84 | 56.70 |
| MultiMED | **19.35** | 19.85 | 22.60 | 22.05 | 20.11 | 24.47 |
| VietMed | **19.41** | 19.93 | 19.59 | 21.90 | 20.21 | 24.37 |
| vlsp-t1 | 13.39 | **11.76** | 14.09 | 14.54 | 16.29 | 13.70 |
| vlsp-t2 | **20.40** | 28.63 | 25.81 | 31.18 | 34.26 | 27.45 |
| LSVSC | 8.96 | 9.12 | **8.85** | 10.23 | 9.64 | 10.08 |
| Fleurs | 12.92 | 13.16 | 14.17 | 14.76 | **10.13** | 12.62 |
| ViMD | **7.17** | 7.28 | 11.77 | 10.15 | 11.16 | 11.18 |
| vivos | **4.12** | 4.60 | 4.18 | 6.92 | 7.17 | 4.73 |

Other rows in the card: PhoWhisper small/medium, wav2vec2-base-vi (95M), Qwen3-ASR-0.6B and `nvidia/parakeet-ctc-0.6b-Vietnamese`; none beats gipformer on the private call-center sets.[^gipformer-68m-card]

The card's rankings summary: #1 on 9/12 (the four tele sets, MultiMED, VietMed, vlsp-t2, ViMD, vivos), #2 on LSVSC, #3 on vlsp-t1 and Fleurs (**Reported**; consistent with the table, **Observed**).[^gipformer-68m-card] The call-center gain is large (about 10–13 WER points over the next-best model on the hard sets, **Synthesis** from the table); on public read/broadcast sets margins are small or negative.

## Deployment relevance

- Small size and ONNX int8 packaging suit CPU/edge and local-privacy use (**Reported**); no RTF, hardware, memory, or latency figure is given.[^gipformer-68m-card]
- The card does not state whether the model streams, chunk/lookahead settings, endpointing, hotwords, punctuation or ITN. RNN-T alone does not establish native streaming (**Unverified**).
- Training data, data volume and data rights are not described; the private call-center test sets are unpublished and cannot be independently checked.

## Contradictions

- Figures for the same models differ between cards: [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md) lists gipformer-68M LSVSC as 9.04 and Zipformer-30M tele-medium as 19.53, while this card gives 8.96 and 19.95 (tele-hard-north 38.13 vs 38.77 likewise). Neither is chosen; the cards may use different runs or normalization.

## Relationships

- Superseded in the vendor line by [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md), which gains mainly on domain sets, not on private call-center sets.
- Compared against [ChunkFormer Vietnamese](chunkformer-vietnamese.md), [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md), [PhoWhisper](phowhisper.md), [Qwen3-ASR family](qwen3-asr-family.md) and [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md).
- Shortlist context: [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md).

## Coverage and limits

The single model-card capture was read fully and statically. Weights, GitHub repo, demo, LICENSE, datasets and any paper were not fetched; no inference or benchmark was run.[^gipformer-68m-card]

[^gipformer-68m-card]: [Gipformer model card](../raw/gipformer-68M-rnnt.md) — frontmatter; Highlights; Benchmark Results table, Normalization note and Rankings Summary; Dataset Descriptions; Call Center Domain; Resources; License.
