---
type: Concept
title: DNA-VL-STEER-2B
description: A 2.13B-parameter language-bias-calibrated variant of Qwen3-VL-Embedding-2B that adjusts only early residual-stream layers to lift low-resource-language image/text/video retrieval across 36 XM3600 languages, at reported costs on text-only and fine-grained visual tasks.
tags: [embedding, multimodal, multilingual, retrieval, qwen, fine-tune]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T23:59:00Z }
stale_after: 2027-01-20
sources:
  - id: dna-vl-steer-2b-page
    resource: ../raw/dnotitia-DNA-VL-STEER-2B.md
    kind: model-card
    title: dnotitia/DNA-VL-STEER-2B Hugging Face model page (HTML capture)
---

# DNA-VL-STEER-2B

DNA-VL-STEER-2B ("Steering Trajectories onto the Established Residual-stream") is a drop-in, language-bias-calibrated replacement for [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md). It keeps the architecture, the 2,048-dimensional shared text/image/video space, and the instruction-aware interface; per the card only the early residual-stream layers are adjusted, and every other weight, including the entire vision tower, is bit-identical to the base. The goal is to close the cross-lingual retrieval gap: low-resource languages are lifted sharply while English, other high-resource languages, and the vision side are mostly preserved. [^dna-vl-steer-2b-page] All scores below are **Reported** (self-reported by the card, not independently reproduced). The card is the only source; the calibration method itself (data, loss, which layers) is not disclosed beyond "calibrated on XM3600" and a statement that training used image–text pairs only.

## Model facts

| Field | Value |
|---|---|
| Base | Qwen/Qwen3-VL-Embedding-2B (28 layers, 2,048-D, 32K context, Matryoshka 64–2,048), itself fine-tuned from Qwen3-VL-2B-Instruct |
| Parameters | 2,127,532,032, BF16 only; 4,255,140,312-byte safetensors, unsharded (Observed in Hub metadata) |
| Output | 2,048-D, L2-normalized; MRL truncation to 64–2,048 by slice and renormalize |
| Pooling | Last non-pad token of the post-final-RMSNorm hidden state; mean pooling is not a valid substitute |
| Modalities | Text, image, screenshot, video, arbitrary interleaved combinations |
| Calibrated languages (36) | The full XM3600 set: en, fr, de, es, zh, ko, bn, fil, hi, sw, te, ja, ru, ar, vi, tr, th, el, fa, fi, id, he, pl, uk, nl, it, pt, cs, sv, hu, ro, hr, da, no, mi, quz |
| Library / license | sentence-transformers (config copied verbatim from base); Apache 2.0; not gated |
| Page metadata (capture) | Created 2026-07-15, last modified 2026-09-10, 14 likes, 530 downloads last month (3,765 all time); one of 14 listed finetunes of the base and part of a 9-item "DNA-VL-STEER" collection (siblings not supplied) |

The "What's new" section says earlier releases calibrated on 11 languages; this release uses all 36. [^dna-vl-steer-2b-page]

## Reported results

Frozen base → STEER, "official post-norm protocol". [^dna-vl-steer-2b-page]

**XM3600 image↔text R@1** (every caption as a query, ~7,200 per language, against the full 3,600-image pool; a first-caption-only protocol gives lower i→t absolutes but the same deltas):

| Tier | image→text | text→image |
|---|---|---|
| HRL-6 (high-resource) | 75.3 → 77.8 | 64.7 → 67.4 |
| LRL-5 (low-resource) | 32.8 → 51.8 (+19.0) | 21.2 → 41.0 (+19.8) |
| +25 other languages | 61.4 → 72.2 (+10.8) | 50.4 → 61.2 (+10.8) |
| Overall-36 | 59.8 → 70.3 (+10.5) | 48.7 → 59.5 (+10.8) |

The HRL–LRL i→t gap narrows from 42.6 to 25.9. On Flickr30k-1k and XTD-1k the LRL i→t scores rise 48.7 → 74.5 and 42.5 → 63.3, and the HRL–LRL gap falls from 30.4 to 8.4 and 25.1 to 8.1. The 25 languages outside the earlier 11-language calibration had regressed under it; they now improve. [^dna-vl-steer-2b-page]

**Zero-shot video transfer** (trained only on image–text), text→video R@1:

| Dataset | en | ko | zh |
|---|---|---|---|
| MSR-VTT | 53.1 → 50.7 | 39.7 → 43.6 | 47.6 → 49.6 |
| DiDeMo | 54.8 → 53.9 | 38.4 → 43.1 | 48.5 → 49.4 |
| MSVD | 61.1 → 60.8 | 47.4 → 53.7 | 53.6 → 56.8 |
| VATEX | 47.8 → 47.5 | 31.5 → 38.3 | 44.2 → 44.6 |

English drops slightly (−0.3 to −2.4), so "English preserved" is approximate. Korean image retrieval gains +4.8 to +11.1 R@1 across XM3600, Flickr30k-1k, and XTD-1k; Korean video gains appear on all four datasets in both directions. [^dna-vl-steer-2b-page]

**MIEB (Multilingual), 130 tasks:** Overall (mean of 10 category means) 66.71 → 67.86; multilingual-retrieval category 64.80 → 71.98 (+7.18). 9 of 10 categories improve; the only decline is document understanding (−0.33). A flat mean over tasks gives 60.06 → 60.53. The card says an earlier version's English visual-STS row (77.2 → 80.2) was a mis-slice and corrects it to 79.88 → 80.24. **ViDoRe v3** nDCG: 52.9 → 53.2 (preservation check). [^dna-vl-steer-2b-page]

## Honest limitations (from the card)

The card revises an earlier claim that nothing regresses relative to the frozen base. Measured regressions: [^dna-vl-steer-2b-page]

| Workload | STEER vs frozen |
|---|---|
| Multilingual retrieval (XM3600; ko/zh video) | +5 to +11 |
| Abstract text retrieval (Wikipedia multilingual) | −7.9 R@1 (2B), −4.1 (8B) |
| Video action classification | −4 to −9 |
| Fine-grained visual (logo retrieval) | −3.1 mAP |

- The calibration is visual-vocabulary specific: it helps caption-like multilingual retrieval and costs abstract text and fine-grained visual discrimination. For English, text-only, or fine-grained classification workloads the card recommends the frozen base. Gains attenuate with size; at 8B several tasks turn net-negative. Languages outside the 36 should see little change.
- Breadth trades against per-language peak: each low-resource language gets a smaller boost than under a narrow calibration.
- Composed queries ("this video, but with X changed") are unsupported (Dense-WebVid-CoVR: below using the edit target's caption alone).
- Matryoshka truncation is task-dependent: text retrieval keeps 99.6% of its score at 64 dims, fine-grained logo retrieval only 49.5%; at 512 dims the median cost over 15 benchmarks is 1.6%.

## Usage and reproduction cautions

Usage is identical to the base, only the model id changes. Procedure and pitfalls recorded by the card: [^dna-vl-steer-2b-page]

- **Requires `transformers >= 5.0`.** On 4.57.x and earlier, `Qwen3VLModel.base_model_prefix` is `""` while the checkpoint stores its 625 tensors under a `model.` prefix, so no keys match and the model is **silently randomly initialized**; the card says this affects the base model identically. The repo's `config_sentence_transformers.json` declares a `requirements` field so recent sentence-transformers raise an error first; older versions or non-ST loading skip the check. Card-provided sanity test: embeddings of "a photo of a cat" and "a picture of a cat" should score >0.1 higher than versus "quarterly earnings fell".
- **Instructions:** write in English even for non-English inputs; reuse the same instruction on both sides being compared. Measured gain from a task instruction on video classification: Kinetics-700 +3.8, SomethingSomethingV2 +3.7, Breakfast +1.8, UCF101 +0.1, HMDB51 0.0 (scales with label ambiguity). CLIP-style templates do not help.
- **Label casing:** UCF101 `ApplyEyeMakeup` 94.3 > `apply eye makeup` 91.4 > `applyeyemakeup` 88.9; keep original capitalization.
- **Video input:** an `.mp4` path samples at 1 fps capped at 64 frames (close to, not identical to, reported numbers); a list of frame paths uses uniform 64 frames plus a pixel budget (the benchmarked protocol). **Never pass a directory path:** the error is swallowed and the embedding is input-independent (measured cosine 1.0000 across three different clips, versus 0.57–0.67 for the same clips as frame lists), silently corrupting an index.
- **Reproduction:** bfloat16, L2-normalize, image budget min_pixels = 4·32², max_pixels = 1800·32², patch size 16 with no pre-downscaling; do not use a harness default `max_length` of 8,192 on long documents (the card measured 13.5 versus a published 94.4 because of truncation); fix batch size for exact repeatability (right padding plus last-token pooling gives ~5e-3 batch-dependence, ±0.2–0.7 on a small benchmark).

## Relationships

- **Derived from / drop-in replacement for:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md); the 8B sibling [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) is mentioned only as having a smaller reported STEER effect (its model is not supplied). [^dna-vl-steer-2b-page]
- **Compared with (Synthesis):** other multilingual multimodal embedders in [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md). STEER reports no MMEB number, so it is not comparable with the MMEB-v2/v3 values there; its evidence is XM3600/Flickr30k/XTD/MIEB.

## Coverage and limits

The captured HTML model page is the sole source; its README prose and tables were fully read. Not inspected or not supplied: the benchmark report "attached to this repo", the repository file tree and `config_sentence_transformers.json`, the sibling collection models, the 8B variant, and the training/calibration method. Per-language XM3600 results are not in the page. Evidence class: Reported, except the parameter count and file size (Observed from Hub JSON metadata).

[^dna-vl-steer-2b-page]: [dnotitia/DNA-VL-STEER-2B model page](../raw/dnotitia-DNA-VL-STEER-2B.md), README sections "What's new", Usage (1–7, Pro tip), Performance (Korean capability, XM3600, cross-benchmark, video transfer, MIEB, document retrieval), Honest limitations; embedded Hub JSON (`safetensors`, `createdAt`, `lastModified`, `downloads`, `likes`, `cardData`) and Model tree. Author-reported; not independently reproduced.
