---
type: Concept
title: CED Audio Tagging Family (CED-Mini)
description: AudioSet audio-tagging family behind CED-Mini — CED-Tiny 5.5M through CED-Base 86M parameters with reported AS-20K/AS-2M mAP (38.5/49.0 for Mini), BatchNorm mel inputs, variable-length non-padded inference at 248 patches per 10 s, Transformers and Optimum-ONNX routes, and a frozen-encoder ESC-50 finetune recipe, but no VAD, streaming, latency or Vietnamese evidence.
tags: [pipeline, vad, audio-tagging, audio-classification, audioset, transformers, onnx, edge-deployment]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:20:00Z }
stale_after: 2027-10-25
sources:
  - id: ced-mini-card
    resource: ../raw/mispeech-ced-mini.md
    kind: documentation
    title: mispeech/ced-mini model card
---

CED is a family of ViT-Transformer audio-tagging models for AudioSet sound-event classification, published in four sizes from CED-Tiny (5.5M parameters) to CED-Base (86M) with reported mAP from 36.5 to 44.0 on AudioSet-20K and 48.1 to 50.0 on AudioSet-2M (**Reported**).[^ced-mini-card] The captured `mispeech/ced-mini` card documents the 9.6M-parameter Mini checkpoint plus a Transformers route, an Optimum ONNX route, and a finetuning notebook. Its selling points are engineering ones rather than accuracy claims: BatchNorm-normalized mel inputs that remove the dataset statistics pass before finetuning, variable-length inputs without padding every clip to 10 s, and a 248-patch budget per 10 s spectrogram against AST's 1212 (**Reported**).[^ced-mini-card] The card gives no latency, throughput, streaming, or frame-level speech/non-speech result, so CED-Mini is a clip-level acoustic-scene labeler and not a drop-in VAD (**Synthesis**).

## Family and reported accuracy

| Model | Parameters (M) | AS-20K mAP | AS-2M mAP |
|---|---|---|---|
| CED-Tiny | 5.5 | 36.5 | 48.1 |
| CED-Mini | 9.6 | 38.5 | 49.0 |
| CED-Small | 22 | 41.6 | 49.6 |
| CED-Base | 86 | 44.0 | 50.0 |

Card table reproduced verbatim; the card prints no protocol, evaluation split, ensemble/single-model flag, or confidence interval (**Reported**).[^ced-mini-card]

- Scale return differs by set: 10.7x parameters from Tiny to Small buys 5.1 mAP on AS-20K but only 1.5 on AS-2M, and Base's 3.9x over Small buys 2.4 and 0.4 respectively (**Observed**, arithmetic over the card's own numbers).[^ced-mini-card]
- The card's headline "10M parameters outperforms the majority of previous approaches (~80M)" can only refer to CED-Mini's 9.6M, since no other row is near 10M (**Synthesis**).[^ced-mini-card] It names no baseline models or figures, so the comparison cannot be checked from this capture (**Unverified**).
- The card states AudioSet as the training set (`datasets: [AudioSet]`) but not whether each size uses AS-20K or AS-2M, making the two mAP columns unreconciled with training data (**Synthesis**).[^ced-mini-card]

## Design choices that affect a pipeline

- **Finetuning without dataset statistics:** mel-spectrograms are BatchNorm-normalized inside the model, so a finetune does not first compute mean/variance over the new dataset — the card contrasts this with AST (**Reported**).[^ced-mini-card]
- **Variable length:** most other models use a static time-frequency position embedding that degrades on segments shorter than 10 s; CED avoids it, while previous transformers pad to 10 s and lose training/inference speed doing so (**Reported**).[^ced-mini-card]
- **Patch budget:** 64-dimensional mel filterbanks with non-overlapping 16x16 patches yield 248 patches from a 10 s spectrogram, against AST's 128 filterbanks with a 16x16 conv and "10x10 overlap" yielding 1212 — a 4.9x difference in sequence length (**Reported**; ratio **Observed**).[^ced-mini-card]
- Arithmetic check: 248 = 4 frequency patches x 62 time patches, which requires roughly 1,000 spectrogram frames — i.e. a 10 ms hop at 16 kHz; 1212 = 12 x 101 requires 128 mels and 1,024 input frames at a stride of 10, so the card's "overlap" wording reads as stride, not overlap (**Synthesis**).[^ced-mini-card] The card prints no hop, frame count, or stride convention, so both counts are consistent-but-unconfirmed reconstructions.
- Speed: CED-Tiny "runs on a common CPU as fast as a comparable MobileNetV3" with no device, batch, clip length, or measurement (**Reported**; not reproducible from the card).[^ced-mini-card]

## Inference routes

- **Transformers:** `AutoFeatureExtractor.from_pretrained("mispeech/ced-mini", trust_remote_code=True)` plus `AutoModelForAudioClassification` with the same flag; audio must be 16 kHz (`assert sampling_rate == 16000`), and the label comes from `argmax(logits)` mapped through `model.config.id2label` (**Reported**).[^ced-mini-card]
- **Optimum ONNX:** `ORTModelForAudioClassification`, the session's first input name fed a `torch.randn(1, 16000)` tensor, and top-2 logits printed via `argsort` (**Reported**).[^ced-mini-card]
- The ONNX example's quoted output `Finger snapping: 0.9155` / `Slap: 0.0567` is produced from a one-second random-noise tensor in the same snippet, so it is an illustrative print rather than evidence that CED rejects noise (**Observed**, reading the snippet; the alternative reading is an unstated separate run).[^ced-mini-card]
- `trust_remote_code=True` on both routes means the feature extractor and model code live in the repository; that code is not in `raw/`, so the preprocessing pipeline (mel parameters, normalization, class count, label order) is not inspectable here (**Synthesis**).[^ced-mini-card]
- The card names no number of output classes, no label taxonomy, no probability thresholding guidance, no ONNX file names or sizes, and no quantization or half-precision variant (**Synthesis**).[^ced-mini-card]

## Fine-tuning

- The linked notebook `example_finetune_esc50.ipynb` trains a linear head on ESC-50 with the CED encoder frozen — head-only adaptation, not full finetuning (**Reported**).[^ced-mini-card]
- The notebook lives in a third-party repository (`jimbozhang/hf_transformers_custom_model_ced`), not the model repository, and is not captured; its optimizer, schedule, and reported ESC-50 accuracy are unknown (**Synthesis**).[^ced-mini-card]

## Fit in a voice loop, and what it is not

- CED-class tagging is the sound-event channel that [parakeet.cpp](parakeet-cpp.md) wires into its scene stream beside words and speakers, where the runtime ships CED files of 6-88 MB across 527 sound classes (**Reported** in that source; the 6-88 MB range brackets this family's 5.5M-86M parameter span, though neither capture states the stored precision) (**Synthesis**).[^ced-mini-card]
- It is not a VAD and not an endpointing model: it emits clip-level AudioSet labels, the card documents no frame-level speech probability, no streaming state, and no look-ahead, so it cannot by itself decide when a turn starts or ends (**Synthesis**).[^ced-mini-card]
- Practical constraints inherited from the card: 16 kHz input, a 10 s design point for the 248-patch count, clip-level argmax output, and no measured cost — enough to label an environment or a segment, not to gate per-frame audio in a realtime loop without separate benchmarking (**Synthesis**).[^ced-mini-card]

## Relationships

- Upstream model behind the CED sound tagger compiled in [parakeet.cpp Bundles, VAD, Diarization and Scene Stream](parakeet-cpp-bundle-vad-scene.md) (**Synthesis**).
- Alternative audio-event detection rather than tagging: [FireRedVAD](firered-vad.md) ships speech/singing/music AED at ~0.59M parameters, i.e. two orders of magnitude smaller and with a narrower label set (**Synthesis**).
- Sits on the same "pre-ASR audio understanding" shelf as [Speech Enhancement Before ASR](speech-enhancement-before-asr.md), but labels content instead of cleaning it; no evidence in either direction links tagging accuracy to downstream WER (**Synthesis**).
- Depends on the paper `CED: Consistent ensemble distillation for audio tagging` (arXiv 2308.11957) for its training mechanism, which this card never describes beyond the title (**Synthesis**).

## Coverage and limits

- Single source: the `mispeech/ced-mini` model-card capture (75 lines), read in full and inspected statically; no install, download, inference, finetune, or timing was run (**Synthesis**).[^ced-mini-card]
- The card carries no revision, commit, release date, or capture date, and frontmatter declares only `license: apache-2.0`, `datasets: [AudioSet]`, `metrics: [mAP]`, `pipeline_tag: audio-classification`; weight-license terms beyond that tag are unstated (**Reported**; freshness **Unverified**).[^ced-mini-card]
- Not covered anywhere in the capture: training data volume or recipe, the ensemble-distillation teacher, augmentation, class count or label list, latency/RTF/throughput, memory, quantization, streaming, long-audio chunking, multilingual or Vietnamese evaluation, and any comparison to other open taggers (**Synthesis**).[^ced-mini-card]
- Excluded from compilation: the demo Space, `github.com/RicherMans/CED`, arXiv 2308.11957, the ESC-50 notebook, and the repository's remote code — all uninspected, so every mechanism claim that depends on them stays Reported at best (**Synthesis**).
- Every figure above is Reported except the arithmetic checks, which are Observed/Synthesis; no contradiction or supersession was established, and no sensitive values were compiled.
- Time-sensitive model and benchmark content; `stale_after: 2027-10-25` under the `pipeline` domain rule.

[^ced-mini-card]: [mispeech/ced-mini model card](../raw/mispeech-ced-mini.md) — locators: YAML frontmatter (`license`, `datasets`, `metrics`, `pipeline_tag`); `# CED-Mini Model` intro sentence; the four-row size/mAP table; `Notable differences from other available models` items 1-4 (BatchNorm mels, variable length, 64-mel/16x16 patch budget, CPU speed and 10M-versus-80M claim); `### Model Sources` (repository, paper arXiv 2308.11957, demo Space); `## Inference` Transformers snippet; `## Inference (Onnx)` Optimum snippet and its top-2 print; `## Fine-tuning` ESC-50 notebook link.
