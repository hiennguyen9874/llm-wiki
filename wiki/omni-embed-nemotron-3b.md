---
type: Concept
title: Omni-Embed-Nemotron-3B
description: A 4.703B-parameter Qwen2.5-Omni Thinker-based multimodal bi-encoder for text, image, audio, and video retrieval, producing 2,048-dimensional embeddings.
tags: [embedding, retrieval, multimodal, qwen, nemotron, nvidia]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T10:04:01Z }
sources:
  - id: omni-embed-nemotron-3b-card
    resource: ../raw/omni-embed-nemotron-3b.md
    title: Omni-Embed-Nemotron-3B model card
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
---

# Omni-Embed-Nemotron-3B

Omni-Embed-Nemotron-3B is NVIDIA's dense multimodal retrieval model for independently or jointly supplied text, image, audio, and video. It adapts the Thinker component of Qwen2.5-Omni-3B into a contrastively trained bi-encoder, keeps audio and video streams separate, and emits one normalized 2,048-dimensional vector per input. Despite “3B” in its name, the card reports 4.7B parameters and its ViDoRe table gives the more precise count of 4,703M. [^omni-embed-nemotron-3b-card]

## Benchmarks

The model card reports these aggregate retrieval results; they were not independently reproduced here. [^omni-embed-nemotron-3b-card]

| Evaluation | Metric | Omni result | Comparison stated by source |
|---|---|---:|---|
| LPM + FineVideo average | nDCG@10 | **0.7064** | Highest of four listed models; Qwen3-Embedding-4B scores 0.7020 |
| LPM + FineVideo average | nDCG@5 | **0.6921** | Highest of four listed models; Qwen3-Embedding-4B scores 0.6891 |
| 10 text-retrieval datasets | mean nDCG@10 | 0.6059 | Below Qwen3-Embedding-4B (0.6654), slightly above Stella 1.5B v5 (0.6050) |
| ViDoRe V1, 10 tasks | mean nDCG@5 | 85.7 | Lowest of eight listed visual-document models; listed leader scores 91.0 |

For video retrieval, the card's aggregate Omni scores use **audio and video encoded separately**: LPM 0.8465 and FineVideo 0.5662 nDCG@10. Its text-input variant scores 0.8636 and 0.6082 respectively, so the reported multimodal aggregate does not beat its own transcript/OCR input on either set. On LPM, separate audio/video encoding beats fused audio+video (0.8465 versus 0.8373); on FineVideo it also beats fusion (0.5662 versus 0.4700). Text-only baselines were evaluated on transcripts, while Omni's modality variants used audio or video, so cross-modality comparisons do not hold inputs constant. LPM and FineVideo are custom evaluation sets rather than established video benchmarks according to the card. [^omni-embed-nemotron-3b-card]

A separate local MMEB v3 snapshot lists the model at reported rank 12 of 89 with Overall **42.83**, Overall-V3 **36.35**, Text **36.15**, Audio **36.52**, and Agent **36.53**. That snapshot lacks metric definitions and evaluation protocol, so these values support only within-snapshot comparison. [^mmeb-v3-ranking]

## Model size and architecture

- **Size:** **4.7B parameters**, reported precisely as **4,703M** in the ViDoRe comparison. The “3B” name refers to the Qwen2.5-Omni-3B foundation, not the reported total count. [^omni-embed-nemotron-3b-card]
- **Backbone:** transformer built from the **Thinker** component of `Qwen/Qwen2.5-Omni-3B`; the generative Talker component is omitted. [^omni-embed-nemotron-3b-card]
- **Modality components:** a Qwen LLM plus vision and audio encoders process text, image, video, and audio. Unlike the base Omni design's TMRoPE interleaving, this retrieval encoder preserves audio and video as separate temporal streams. The card claims this improves retrieval but does not provide an architecture ablation beyond the modality-result tables. [^omni-embed-nemotron-3b-card]
- **Retrieval design:** bi-encoder with independently embedded queries and candidates, trained through a contrastive objective. Queries and documents may each contain one modality or any combination of the four. [^omni-embed-nemotron-3b-card]
- **Output and limits:** mean pooling over final hidden states followed by L2 normalization yields one **2,048-dimensional** vector. The stated maximum context is **32,768 tokens**. [^omni-embed-nemotron-3b-card]

## Language support

The model card metadata declares only **English (`en`)**. It makes no multilingual-support claim, enumerates no additional languages, and provides no per-language evaluation. MIRACL appears in the training-data list, but that alone does not establish operational support for its languages. Language support beyond English is therefore undocumented by the supplied source. [^omni-embed-nemotron-3b-card]

## Training data

The card reports **1M samples** from public datasets, collected and labeled through a hybrid of automated, human, and synthetic methods. It characterizes the training modalities as **image and text**, with between 1M and 1B images and fewer than 1B text tokens. The named datasets are HotpotQA, MIRACL, Natural Questions, Stack Exchange, SQuAD, Tiger Math/Stack (`WebInstructSub`), DocMatix-IR, ViDoRe ColPali training, and Wiki-SS-NQ. [^omni-embed-nemotron-3b-card]

The source does not disclose dataset mixture weights, exact image or token counts, language distribution, filtering, deduplication, contamination controls, or train/evaluation overlap analysis. It also names no audio or video training dataset despite supporting and evaluating those modalities; consequently, how audio/video capability was trained or inherited is not established by this artifact. [^omni-embed-nemotron-3b-card]

## Relationships

- **Evaluated in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md), an unauthenticated local ranking artifact. [^mmeb-v3-ranking]

[^omni-embed-nemotron-3b-card]: [Omni-Embed-Nemotron-3B model card](../raw/omni-embed-nemotron-3b.md). Architecture, size, language, training, and benchmark claims are self-reported by the card; its externally linked technical report, datasets, code, and live leaderboards were not inspected.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv), as compiled in the [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md). This supplied ranking artifact is unauthenticated and omits metric definitions and evaluation protocol.
