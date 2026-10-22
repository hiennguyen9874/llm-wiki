---
type: Concept
title: Ovis-Omni-Embedding-3B
description: A 3B Qwen2.5-Omni-initialized universal omni-modal embedding model with 2,048-dimensional last-token embeddings and a self-reported 58.46 on the 190-dataset MMEB-v3.
tags: [embedding, retrieval, multimodal, omni-modal, qwen, matryoshka]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T12:00:00Z }
stale_after: 2027-01-20
sources:
  - id: ovis-omni-card
    resource: ../raw/ATH-MaaS-Ovis-Omni-Embedding-3B.md
    kind: model-card
    title: ATH-MaaS/Ovis-Omni-Embedding-3B Hugging Face model page (HTML capture)
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    kind: dataset
    title: MMEB v3 ranking CSV
---

# Ovis-Omni-Embedding-3B

Ovis-Omni-Embedding-3B is a 3B-parameter bi-encoder that maps text, images, visual documents, video, audio, and interleaved inputs into one space for any-to-any retrieval. It is initialized from Qwen2.5-Omni-3B, keeps the native tokenizer, vision encoder, audio encoder, and shared Thinker backbone, and removes the speech Talker and LM head; there are no modality-specific projection heads. [^ovis-omni-card] All scores below are **Reported** (self-reported by the model card; the technical report arXiv:2609.25165 was not supplied).

## Model facts

| Field | Value |
|---|---|
| Backbone | Qwen2.5-Omni-3B (Thinker with TMRoPE) |
| Pooling / output | Final-layer hidden state at the last non-padding token; native width 2,048; L2-normalized; cosine ranking |
| Reduced widths | 1,024 / 512 / 256 / 128 via a post-hoc elastic-dimension module (shared modality-balanced PCA rotation + zero-initialized residual linear adapter, folded into one projection matrix) |
| Modalities | text, image, visual document, video, audio, interleaved |
| License | Apache 2.0 |
| Library / head | `transformers` (`AutoModelForMultimodalLM`), feature-extraction; architecture `Qwen2_5OmniForConditionalGeneration` |
| Page metadata | Created 2026-09-20, last modified 2026-10-10, 64 likes, 911 downloads last month at capture; 2 quantizations listed |

Not stated on the card: exact parameter count, context length, language coverage, and training-data names or sizes. [^ovis-omni-card]

## Retrieval interface

The query is paired with a task instruction and formatted with the native processor and chat template; queries and candidates are encoded independently, the last-token state is extracted and L2-normalized, and candidates are ranked by cosine. Classification labels, passages, images, documents, video, audio, and multimodal items are all candidates in one space. Queries and candidates must use the same dimensionality and transformation, with re-normalization after projection. [^ovis-omni-card]

## Training (reported)

1. **Omni-modal contrastive pretraining:** globally mixed candidates and cross-device in-batch negatives; difficulty-aware focal contrastive loss plus similarity-distribution distillation from complementary modality experts.
2. **Full-parameter homogeneous finetuning:** each micro-batch is drawn from one dataset, with candidate deduplication to avoid positive collisions and false in-batch negatives.
3. **Annealing embedding distillation:** teacher-correct examples retained, unresolved student examples upsampled, confidence-adaptive forward-KL supervision; adds no inference-time towers.

[^ovis-omni-card] Datasets, mixture ratios, and hyperparameters are not disclosed in the supplied page.

## Reported results

- **MMEB-v3 (190 datasets; image, video, visual document, text, audio, agent):** overall **58.46** versus 53.27 for the best compared baseline (+5.19). Group scores (Ovis / best baseline): Image 77.55/73.83, Video 64.99/59.37, Visual document 78.26/75.37, Text 47.15/43.62, Audio 50.08/43.17, Agent 45.52/39.42. It reports ranking first on 22 and second on 8 of 31 aggregate and sub-task entries; MultiConIR is the only entry outside the top two. Metrics are mainly Hit@1 (image, video, audio, agent) and nDCG@5 (text, visual document); overall is an unweighted average over datasets. The baseline names behind each “best compared” value are not given in the text (the comparison table is an image absent from `raw/`). [^ovis-omni-card]
- **Other benchmarks (own aggregation procedures; do not average):** MAEB (beta, 30 audio tasks) 57.29 vs LCO-Embedding-Omni-7B 53.54; MVEB (beta, 23 video and audio-video tasks) 61.77 vs LCO-Embedding-Omni-7B 57.58; RTEB (15-task English public split) 67.35 vs Qwen3-Embedding-4B 67.27. MAEB and MVEB are local evaluations inserted into leaderboard snapshots. [^ovis-omni-card]

## Limitations and cautions

- Produces retrieval embeddings only; not a generative model. Quality depends on task-appropriate instructions and the native preprocessing/chat template.
- Self-reported weaknesses: MultiConIR, several established visual-document suites, and memory retrieval trail the best specialist.
- The card advises domain evaluation, access controls, and a second-stage reranker for high-stakes use. [^ovis-omni-card]
- Coverage limit: the captured page is HTML; its figures (architecture, data pipeline, training/inference, MMEB-v3 table image) are not in `raw/` and were not inspected. The linked report and GitHub repositories were not supplied.

## Contradictions

The local MMEB v3 snapshot lists **Ovis-Omni-Embedding-v0.1-3B** (size 3.0, date `26-08-03`) with Overall 52.55, Overall-V3 39.90, Text 41.81, Audio 47.82, Agent 35.90. [^mmeb-v3-ranking] The model card reports 58.46 overall, Text 47.15, Audio 50.08, Agent 45.52 for Ovis-Omni-Embedding-3B on MMEB-v3. [^ovis-omni-card] These likely come from different checkpoint versions, benchmark versions, or aggregation conventions (the snapshot's columns are undefined and the card does not mention v0.1), so neither is chosen and they must not be merged. Whether the snapshot's v0.1 entry is a predecessor of this checkpoint is Unverified (Synthesis from naming).

## Relationships

- **Built on:** Qwen2.5-Omni-3B, the same backbone as [e5-omni](e5-omni.md) 3B; the two use different training recipes. [^ovis-omni-card]
- **Evaluated in:** [MMEB v3 ranking snapshot](mmeb-v3-ranking-snapshot.md) (as v0.1 entry). [^mmeb-v3-ranking]
- **Compared in:** [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).
- **Sibling of:** [Ovis-VL-Embedding-2B](ovis-vl-embedding-2b.md), the audio-free Qwen3.5-2B-based vision-language model from the same team and report.
- **Similar omni scope:** [Tianmu-Emb-Uni-8B](tianmu-emb-uni-8b.md), [Omni-Embed-Nemotron-3B](omni-embed-nemotron-3b.md), [Jina Embeddings v5 Omni Small](jina-embeddings-v5-omni-small.md).

[^ovis-omni-card]: [ATH-MaaS/Ovis-Omni-Embedding-3B model page](../raw/ATH-MaaS-Ovis-Omni-Embedding-3B.md), README sections Architecture, Training, Retrieval interface, Performance (MMEB-v3, Additional benchmark results), Embedding dimensions, Limitations, License; page metadata JSON (createdAt, lastModified). Author-reported, not independently reproduced.
[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv), row 2 (`Ovis-Omni-Embedding-v0.1-3B`). Supplied, unauthenticated artifact with undefined columns.
