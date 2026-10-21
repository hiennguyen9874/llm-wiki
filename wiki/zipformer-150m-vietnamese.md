---
type: Concept
title: ZipFormer 150M Vietnamese
description: Vietnamese ~153M ZipFormer trained with CR-CTC + CTC + RNN-T loss on 6000 hours, with author-reported VLSP and GigaSpeech2 WER against the 30M sibling, ChunkFormer, PhoWhisper and VietASR, a 0.3 s RTX 3090 figure for 12 s audio, and CC-BY-NC-ND weights with no established streaming protocol.
tags: [stt, asr, vietnamese, zipformer, rnnt, ctc, gpu, k2]
status: stable
created: 2026-10-21
generated: { by: llm-wiki-agent/1, at: 2026-10-21T20:00:00Z }
stale_after: 2027-04-21
sources:
  - id: zip150-card
    resource: ../raw/ZipFormer-150M-CR-CTC-RNNT-6000h.md
    kind: documentation
    title: Vietnamese Speech-to-Text (ASR) — ZipFormer-150M-CR-CTC-RNNT-6000h model card capture
---

ZipFormer-150M-CR-CTC-RNNT-6000h is a Vietnamese ASR checkpoint on the ZipFormer architecture (described as an improved Conformer variant), about 153M parameters, trained in PyTorch + k2 with a combined CR-CTC + CTC + RNN-T loss on roughly 6000 hours of public Vietnamese speech. It is the larger, GPU-oriented sibling of [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md): the author reports clearly lower WER than the 30M model on the VLSP2023, VLSP2025 and GigaSpeech2 test sets, but a higher WER on VLSP2020-T1, and positions it for "cost-efficient GPU" inference. All figures are **Reported** by the author; the card states no streaming, chunk or latency-to-partial protocol, and the weights are CC-BY-NC-ND-4.0.[^zip150-card]

## Identity and architecture

- **Architecture / size:** ZipFormer, "~153M" in the spec list (the prose says "150 million"); Vietnamese only; PyTorch + k2 framework (**Reported**).[^zip150-card]
- **Loss:** CR-CTC + CTC + RNN-T. The card does not define CR-CTC, say which head is used at inference, or give per-head results (**Reported**; gap recorded).[^zip150-card]
- **Training strategy:** careful data preprocessing, augmentation driven by the distribution of out-of-vocabulary (OOV) tokens, and transcript refinement with Whisper (**Reported**).[^zip150-card]
- **License:** frontmatter `license: cc-by-nc-nd-4.0` (**Observed**). Non-commercial and no-derivatives terms make it unsuitable as a default for commercial products, fine-tuning or redistribution without permission; this is **Synthesis**, not legal advice.[^zip150-card]
- **Author and revision:** the card names no author in the capture body beyond first-person text, and gives no revision or date; the same-family checkpoint is attributed to `hynt` elsewhere in the wiki.[^zip150-card]

## Training data

About 6000 hours of "high-quality" Vietnamese speech from public datasets: VLSP2020, VLSP2021, VLSP2023, VLSP2023-voting-pseudo-labeled, FPT, VIET_BUD500, VietSpeech, FLEURS, VietMed_Labeled, Sub-GigaSpeech2-Vi, ViVoice and Sub-PhoAudioBook (**Reported**). The mix includes pseudo-labeled and Whisper-refined material, and the card states no per-dataset hours, filtering or consent terms.[^zip150-card]

## Reported WER (lower is better)

Author-reported in the card's `Evaluation Results` table; normalizer, scoring script and split hygiene are not stated (**Reported**).[^zip150-card]

| Test set | ZipFormer-150M | ZipFormer-30M | ChunkFormer-110M-3000h | PhoWhisper-Large-1.5B-800h | VietASR-ZipFormer-68M-70,000h |
|---|---:|---:|---:|---:|---:|
| VLSP2020-Test-T1 | 13.50 | 12.29 | 14.09 | 13.75 | 14.45 |
| VLSP2023-PublicTest | 6.59 | 10.40 | 16.15 | 16.83 | 14.70 |
| VLSP2023-PrivateTest | 7.80 | 11.10 | 17.12 | 17.10 | 15.07 |
| VLSP2025-PublicTest | 6.69 | 7.97 | 15.55 | 16.14 | 13.55 |
| VLSP2025-PrivateTest | 6.20 | 8.10 | 16.07 | 16.31 | 13.97 |
| GigaSpeech2-Test | 7.10 | 7.56 | 10.35 | 10.00 | 6.88 |

Reading notes (**Synthesis**):

- The 150M model beats every listed competitor on the four VLSP2023/2025 sets, but is behind the 30M sibling on VLSP2020-T1 and behind VietASR-68M on GigaSpeech2.
- The card's bolding does not match the numbers: it bolds both 150M and 30M on VLSP2023/2025 rows and bolds 30M on VLSP2020, so rely on the numeric values rather than the highlighting.
- VLSP2020, VLSP2021, VLSP2023 and a VLSP2023 pseudo-labeled set are listed as training data, and sub-sets of GigaSpeech2 and FLEURS are too. The card does not say whether any evaluated split overlaps them, so the VLSP2023 and GigaSpeech2 scores are not shown to be held-out (**Unverified**).
- The competitor columns use different training sizes (3000 h, 800 h, 70,000 h) and the card gives no evidence that all systems were scored under the same normalizer.

## Competition claim

The card says a ZipFormer trained "with 30M parameters" on 4,000 hours won first place in VLSP 2025; the 150M checkpoint is not the competition model. Details on data, optimization, architecture and evaluation are deferred to the ACL paper at `aclanthology.org/2025.vlsp-1.4` (**Reported**; paper not fetched).[^zip150-card]

## Inference speed and deployment

| Device | Audio | Time |
|---|---|---|
| CPU (Hugging Face Basic) | 12 s | 1.0 s |
| GPU (RTX 3090) | 12 s | < 0.3 s |

(**Reported**.) These are whole-file times, equivalent to a real-time factor of roughly 0.08 on CPU and below 0.025 on the 3090 (**Synthesis**, arithmetic from the table). They are not partial-result latency, endpoint-to-final delay or concurrency measurements, and no batch size or precision is given. The 30M sibling reports 0.3 s on the same CPU class and below 0.1 s on the RTX 3090 for the same 12 s clip, so the 150M model is about 3× slower on both devices in the author's own figures.[^zip150-card]

The card points to the k2-fsa **sherpa** guides for Torch JIT Script (`k2-fsa.github.io/sherpa/`) and ONNX (`k2-fsa.github.io/sherpa/onnx/`) deployment; it supplies no commands itself and a Hugging Face Space demo is linked (**Reported**; none fetched).[^zip150-card]

## Voice-pipeline fit

- The card calls the model suited to "real-time speech recognition, callbots and embedded speech interfaces", but states no streaming architecture, chunk size, cache or lookahead setting, and no first-partial latency. Native streaming is **Unverified**; treat it as a turn-final or buffered-chunk candidate until sherpa streaming support for this checkpoint is confirmed (**Synthesis**).[^zip150-card]
- The practical niche versus the 30M model is higher accuracy on newer VLSP sets at small GPU cost, whereas the 30M is the CPU option. It remains unmeasured against [Qwen3-ASR](qwen3-asr-family.md), [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md) or [Gipformer 1.5 68M RNNT](gipformer1.5-68m-rnnt.md) under a shared protocol (**Synthesis**).
- The non-commercial license is the main gating issue for production use, as with the 30M sibling.

## Relationships

- Sibling of [ZipFormer 30M Vietnamese](zipformer-30m-vietnamese.md): same data recipe and 6000-hour label, different size, loss and device target.
- Compared in its own table against [ChunkFormer Vietnamese](chunkformer-vietnamese.md), [PhoWhisper](phowhisper.md) and the 70,000-hour [VietASR (zzasdf)](zzasdf-viet-asr.md) checkpoint.
- Listed in [ASR/STT Model Survey](asr-stt-model-survey.md) and [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md).
- Uses the k2 / sherpa toolchain; compare the English Zipformer CR-CTC Transducer GPU runtime in [Fast GPU ASR](fast-gpu-asr.md), a separate 290M English model family.

## Coverage and limits

The whole single-file card was read statically. Not inspected: the ACL paper, the Hugging Face demo Space, sherpa guides, weights, ONNX/TorchScript exports, datasets, the `qr.jpg` donation image (excluded as non-technical), and any license file beyond the frontmatter field. No model was downloaded or run, no audio was transcribed, and no benchmark was reproduced. The card gives no revision, so the capture is undated.

[^zip150-card]: [ZipFormer-150M-CR-CTC-RNNT-6000h card](../raw/ZipFormer-150M-CR-CTC-RNNT-6000h.md) — frontmatter `license`; `Overview`; `Model Architecture and Training strategy`; `Training Data`; `Evaluation Results`; `Achievements`; `Inference Speed`; `How to Run This Model`; `Summary`.
