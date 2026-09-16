---
type: Concept
title: TBPS-CLIP empirical person-search baseline
description: TBPS-CLIP systematically combines CLIP fine-tuning tricks, task-compatible augmentation, and complementary contrastive losses into a simple text-based person-search baseline.
tags: [cross-modal-retrieval, clip, data-augmentation, person-reidentification, few-shot-learning, model-compression]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:06:45Z }
sources:
  - id: arxiv-2308.10045
    resource: ../raw/papers/arxiv-2308.10045/arxiv.tex
    title: An Empirical Study of CLIP for Text-based Person Search
---

# TBPS-CLIP empirical person-search baseline

TBPS-CLIP is an empirical recipe for adapting CLIP to text-based person search without adding a task-specific cross-modal encoder. It combines full dual-encoder fine-tuning, carefully selected image and text augmentations, and multiple complementary objectives. The paper's main value is diagnostic: it identifies which common interventions help or hurt this fine-grained retrieval task, then packages the effective choices into a five-epoch baseline.[^arxiv-2308.10045]

## Training recipe

- **Fine-tuning tricks:** propagate gathered gradients across all GPUs, apply 0.05 dropout in text self-attention, freeze the image encoder's initial patch-projection convolution, and average model pseudo-labels with ground-truth labels for soft supervision.[^arxiv-2308.10045]
- **Image augmentation:** an augmentation pool randomly applies two operations drawn from RandomResizedCrop, RandomErasing, RandomGrayscale, brightness/contrast/saturation ColorJitter, horizontal flip, and rotation. On CUHK-PEDES with ViT-B/32, this pool improves Rank-1 from 64.34 to 66.13. Gaussian blur, hue jitter, and vertical flip reduce performance in the reported ablations.[^arxiv-2308.10045]
- **Text augmentation:** back translation through French and random deletion are beneficial when combined, raising Rank-1 from 64.34 to 65.72. Synonym replacement, random insertion, random swap, and EDA reduce performance in the reported setting.[^arxiv-2308.10045]
- **Losses:** normalized image-text contrastive loss (N-ITC) treats all same-identity examples in a batch as normalized positives. Image self-supervision (SS-I) aligns augmented views; image multi-view supervision (MVS-I) adds contrastive supervision from another image view; reversed image-text contrastive loss (R-ITC) minimizes the reverse KL direction to emphasize negative separation; and cyclic image-text contrastive loss (C-ITC) regularizes within- and cross-modal geometry.[^arxiv-2308.10045]

**Synthesis:** the ablations indicate that augmentation must preserve person-description semantics. Occlusion, modest geometric change, grayscale, paraphrase, and token deletion can regularize training, whereas transformations that alter described color, destroy syntax, or erase fine detail can introduce false invariances.

## Reported evidence

On CUHK-PEDES with ViT-B/32, the active ablation tables report the following cumulative progression: vanilla CLIP reaches 60.67 Rank-1; four training tricks reach 64.34; selected image and text augmentation reaches 66.78; and the combined TBPS-CLIP losses reach 69.54 Rank-1 and 61.57 mAP.[^arxiv-2308.10045]

Using ViT-B/16, the paper reports:[^arxiv-2308.10045]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP |
|---|---:|---:|---:|---:|
| CUHK-PEDES | 73.54 | 88.19 | 92.35 | 65.38 |
| ICFG-PEDES | 65.05 | 80.34 | 85.47 | 39.83 |
| RSTPReid | 61.95 | 83.55 | 88.75 | 48.26 |

A simplified version retaining only N-ITC and R-ITC reports Rank-1 of 72.66, 64.52, and 62.10 on the same datasets. Replacing CLIP with TBPS-CLIP as IRRA's baseline raises reported Rank-1 from 73.38 to 74.97 on CUHK-PEDES, 63.46 to 65.64 on ICFG-PEDES, and 60.20 to 63.40 on RSTPReid.[^arxiv-2308.10045]

These results are author-reported and were not independently reproduced here. The implementation is linked at <https://github.com/Flame-Chasers/TBPS-CLIP>.[^arxiv-2308.10045]

## Few-shot and compression findings

With 1%, 5%, and 10% of CUHK-PEDES training data, simplified TBPS-CLIP reports Rank-1 of 30.05, 43.65, and 50.26 respectively. CoOp and CLIP-Adapter remain around 11-13 Rank-1 because their locked CLIP backbones do not adapt well to this person-specific fine-grained domain in the reported experiments.[^arxiv-2308.10045]

Module-contribution analyses suggest that the text encoder's middle layers are less important than its first and last layers, while image-layer contributions are more evenly distributed. Freezing up to five selected text layers reduces trainable parameters by 11% with only a small reported Rank-1 decrease, whereas dropping those layers sharply degrades performance. This is training-time parameter reduction, not demonstrated inference-time compression.[^arxiv-2308.10045]

## Implementation and limitations

The reported system uses CLIP ViT-B/16 or ViT-B/32, $224\times224$ images, 77-token text, AdamW with linear warm-up and cosine decay, and five training epochs on four Nvidia A40 GPUs.[^arxiv-2308.10045]

- Most intervention selection is performed on CUHK-PEDES, so the extensive search may specialize the recipe to that benchmark even though final results cover three datasets.
- The manuscript does not report repeated-run variance or independent reproduction, and its few-shot study is limited to random fractions of one dataset.
- The augmentation explanations are plausible interpretations of ablations, not isolated causal demonstrations.
- Freezing parameters reduces training updates but does not reduce the stored architecture or inference compute; layer dropping does, but performs poorly.
- The architecture overview uses earlier labels (`n-ITC`, `CMPM`, and `CM`) where the active manuscript uses N-ITC, R-ITC, and C-ITC. Implementations should follow the equations and released code rather than infer exact objectives from that figure alone.

## Relationships

- **Uses:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) is a comparison point and is also evaluated with TBPS-CLIP replacing its original CLIP baseline.

[^arxiv-2308.10045]: Min Cao, Yang Bai, Ziyin Zeng, Mang Ye, and Min Zhang, “An Empirical Study of CLIP for Text-based Person Search,” AAAI 2024 manuscript, [`arxiv.tex`](../raw/papers/arxiv-2308.10045/arxiv.tex). The architecture overview, augmentation examples, layer-contribution heatmaps, and freeze-versus-drop plots in the same source bundle were also visually inspected.
