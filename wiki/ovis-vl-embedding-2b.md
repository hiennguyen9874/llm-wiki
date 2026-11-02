---
type: Concept
title: Ovis-VL-Embedding-2B
description: A 2B Qwen3.5-2B-initialized vision-language embedding model with 2,048-dimensional last-token embeddings and a self-reported 77.46 on the 78-dataset MMEB-v2, without audio support.
tags: [embedding, retrieval, multimodal, vision-language, qwen]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:55:00Z }
stale_after: 2027-01-20
sources:
  - id: ovis-vl-figure
    resource: ../raw/benchmark-figures-2026-11-02/ovis-vl.png
    kind: image
    title: Ovis-VL MMEB-v2 comparison table
  - id: ovis-vl-card
    resource: ../raw/ATH-MaaS-Ovis-VL-Embedding-2B.md
    kind: model-card
    title: ATH-MaaS/Ovis-VL-Embedding-2B Hugging Face model page (HTML capture)
---

# Ovis-VL-Embedding-2B

Ovis-VL-Embedding-2B is a compact bi-encoder that maps text, images, visual documents, video, and interleaved multimodal inputs into one space. It is initialized from Qwen3.5-2B, keeps the native text and vision encoders and the shared multimodal language backbone, removes the LM head, and uses the final-layer hidden state at the last non-padding token as the embedding; there are no modality-specific projection heads. [^ovis-vl-card] All scores below are **Reported** (self-reported by the model card); the technical report (arXiv:2609.25165) was not supplied.

## Model facts

| Field | Value |
|---|---|
| Backbone | Qwen3.5-2B: 24 language layers, hidden size 2,048; hybrid stack repeating three Gated DeltaNet layers then one gated full-attention layer; multimodal positional encoding for temporal and 2D spatial coordinates |
| Pooling / output | Last non-padding token; native width 2,048 (no projection head); L2-normalized; cosine or dot product |
| Reduced widths | None documented (unlike the [Omni sibling](ovis-omni-embedding-3b.md)) |
| Modalities | text, image, visual document, video, interleaved; **no native audio** |
| License | Apache 2.0 |
| Page metadata | Created 2026-09-21, last modified 2026-09-24, 40 likes, 797 downloads at capture |

Not stated on the card: exact parameter count (the "2B" is the name/backbone class), context length, language coverage, training-data names or sizes, hyperparameters, and quantizations. [^ovis-vl-card]

## Retrieval interface

Bi-encoder, not a cross-encoder: pair the query with a task instruction and format it with the native processor and chat template; encode queries and candidates independently; take the last non-padding hidden state; L2-normalize; rank by cosine. No generation or cross-attention at retrieval time. Labels, passages, images, documents, videos, and interleaved items are all candidates in one space. Queries and candidates must share preprocessing, pooling, dimensionality, and normalization. [^ovis-vl-card]

## Training (reported)

1. **Multimodal contrastive pretraining:** large multi-task data across text, image, document, and video; difficulty-aware focal contrastive loss plus similarity-distribution distillation.
2. **Full-parameter homogeneous finetuning:** each micro-batch comes from one dataset so gathered candidates are task-consistent negatives.
3. **Annealing Embedding Distillation:** teacher-correct examples kept, unresolved student examples emphasized, confidence-adaptive forward-KL supervision from complementary experts.

The three-stage recipe matches the [Omni sibling's](ovis-omni-embedding-3b.md) minus the audio components; data and mixtures are undisclosed. [^ovis-vl-card]

## Reported results

**MMEB-v2 (78 datasets: image, video, visual document; unweighted average over datasets):** [^ovis-vl-card]

| Group | Ovis-VL-Embedding-2B | Best compared baseline | Delta |
|---|---|---|---|
| Image | 80.62 | 77.41 | +3.21 |
| Video | 67.12 | 68.84 | −1.72 |
| Visual document | 80.47 | 79.86 | +0.61 |
| All 78 | 77.46 | 75.42 | +2.04 |

The card says it ranks first on all four image sub-tasks, video classification, video moment retrieval, the visual-document aggregate, ViDoRe-V1, and out-of-distribution visual-document retrieval. The retrieved comparison figure identifies the baselines and their 78-dataset Overall scores: UEmbed-2B dense **66.49**, Qwen3-VL-Embedding-2B **73.25**, DME-Small **74.75**, and Octen-VL-Embedding **75.42**. The best baseline varies by group: Octen-VL for Image and Video, DME-Small for VisDoc and Octen-VL for Overall. These are author-reported values, not independently reproduced.[^ovis-vl-card][^ovis-vl-figure]

**Cross-document context (Synthesis):** on the same 78-dataset benchmark, the wiki records [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) at 73.2 (technical report) / 73.4 (card), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) at 77.8–77.9, and [WeMM-Embedding](wemm-embedding.md) 2B at 77.9. Ovis-VL-2B's 77.46 is thus well above Qwen 2B but about 0.4 below WeMM-2B and Qwen 8B in their own tables. The figure's baseline columns do not include WeMM or Qwen3-VL-8B, so its lead claim does not extend to them.[^ovis-vl-figure] All sources are author-reported and no variance is supplied, so statistical significance of small differences is unknown.

## Limitations and cautions

- No native audio; the card directs audio and omni-modal retrieval to the Omni model (named there "Ovis-Embedding-Omni-3B").
- Embedding model only, not generative; quality depends on task-appropriate instructions and the native processor/chat template.
- Self-reported gaps: video question answering, general video retrieval, and ViDoRe-V2 trail the strongest specialist baselines.
- The card advises evaluating on representative queries, candidates, and metrics before deployment. [^ovis-vl-card]
- Coverage: the MMEB-v2 comparison figure linked from the HTML capture was downloaded and visually read on 2026-11-02; the mutable upstream `main` revision was not pinned. Architecture figures, report, and GitHub repositories were not inspected.[^ovis-vl-figure]

## Relationships

- **Sibling of:** [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), the audio-capable Qwen2.5-Omni-based model from the same team and report. [^ovis-vl-card]
- **Built on:** Qwen3.5-2B, a backbone also used by [WeMM-Embedding](wemm-embedding.md) and [UEmbed](uembed.md). [^ovis-vl-card]
- **Compared with:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) and the other models in [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md) (Synthesis; same MMEB-v2 benchmark, different tables).

[^ovis-vl-figure]: [MMEB-v2 figure](../raw/benchmark-figures-2026-11-02/ovis-vl.png), columns and Overall rows; downloaded 2026-11-02 from the [model's linked `main` figure](https://huggingface.co/ATH-MaaS/Ovis-VL-Embedding-2B/resolve/main/figures/ovis_blog_table3.png). Author-reported; SHA-256 `53b014097fc05c45d6adbb97fee5ed85fa99a909b6a884355162596e1fc0e807`.
[^ovis-vl-card]: [ATH-MaaS/Ovis-VL-Embedding-2B model page](../raw/ATH-MaaS-Ovis-VL-Embedding-2B.md), README sections Architecture, Training, Retrieval interface, Performance (MMEB-v2), Embedding dimensions, Limitations, Citation, License; page metadata JSON (createdAt, lastModified, downloads, likes). Author-reported, not independently reproduced.
