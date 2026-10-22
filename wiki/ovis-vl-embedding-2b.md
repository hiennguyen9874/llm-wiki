---
type: Concept
title: Ovis-VL-Embedding-2B
description: A 2B Qwen3.5-2B-initialized vision-language embedding model with 2,048-dimensional last-token embeddings and a self-reported 77.46 on the 78-dataset MMEB-v2, without audio support.
tags: [embedding, retrieval, multimodal, vision-language, qwen]
status: stable
created: 2026-10-22
generated: { by: llm-wiki-agent/1, at: 2026-10-22T18:00:00Z }
stale_after: 2027-01-20
sources:
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

The card says it ranks first on all four image sub-tasks, video classification, video moment retrieval, the visual-document aggregate, ViDoRe-V1, and out-of-distribution visual-document retrieval. The baselines per row are unnamed in the text (the full table is an image absent from `raw/`), so the "best baseline" may differ per row and cannot be mapped to a specific model. [^ovis-vl-card]

**Cross-document context (Synthesis):** on the same 78-dataset benchmark, the wiki records [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) at 73.2 (technical report) / 73.4 (card), [Qwen3-VL-Embedding-8B](qwen3-vl-embedding-8b.md) at 77.8–77.9, and [WeMM-Embedding](wemm-embedding.md) 2B at 77.9. Ovis-VL-2B's 77.46 is thus well above Qwen 2B but about 0.4 below WeMM-2B and Qwen 8B in their own tables. Its card's "best baseline 75.42" evidently excludes those models or uses a different evaluation set (the Qwen 8B card value, 77.8, exceeds it), so the card's lead claim does not extend to them. All sources are author-reported, so differences under about 1 point are not reliable.

## Limitations and cautions

- No native audio; the card directs audio and omni-modal retrieval to the Omni model (named there "Ovis-Embedding-Omni-3B").
- Embedding model only, not generative; quality depends on task-appropriate instructions and the native processor/chat template.
- Self-reported gaps: video question answering, general video retrieval, and ViDoRe-V2 trail the strongest specialist baselines.
- The card advises evaluating on representative queries, candidates, and metrics before deployment. [^ovis-vl-card]
- Coverage limit: the captured page is HTML; its figures (architecture, MMEB-v2 table image) are not in `raw/` and were not inspected. The report and GitHub repositories were not supplied.

## Relationships

- **Sibling of:** [Ovis-Omni-Embedding-3B](ovis-omni-embedding-3b.md), the audio-capable Qwen2.5-Omni-based model from the same team and report. [^ovis-vl-card]
- **Built on:** Qwen3.5-2B, a backbone also used by [WeMM-Embedding](wemm-embedding.md) and [UEmbed](uembed.md). [^ovis-vl-card]
- **Compared with:** [Qwen3-VL-Embedding-2B](qwen3-vl-embedding-2b.md) and the other models in [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md) (Synthesis; same MMEB-v2 benchmark, different tables).

[^ovis-vl-card]: [ATH-MaaS/Ovis-VL-Embedding-2B model page](../raw/ATH-MaaS-Ovis-VL-Embedding-2B.md), README sections Architecture, Training, Retrieval interface, Performance (MMEB-v2), Embedding dimensions, Limitations, Citation, License; page metadata JSON (createdAt, lastModified, downloads, likes). Author-reported, not independently reproduced.
