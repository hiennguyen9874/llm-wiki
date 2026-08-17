---
type: Concept
title: ALIGN noisy image–text representation learning
description: A dual-encoder contrastive approach showing that web-scale, lightly filtered image alt-text can support transferable multimodal representations.
tags: [multimodal-learning, contrastive-learning, representation-learning, retrieval]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:30:00Z }
sources:
  - id: align-2021
    resource: ../raw/2102.05918_ALIGN/align.tex
    title: Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision
  - id: wortsman-2021-wise-ft
    resource: ../raw/2109.01903_WiSE-FT/main.tex
    title: Robust fine-tuning of zero-shot models
  - id: li-2022-blip
    resource: ../raw/2201.12086_BLIP/main.tex
    title: "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation"
  - id: yu-2022-coca
    resource: ../raw/2205.01917_CoCa/main.tex
    title: "CoCa: Contrastive Captioners are Image-Text Foundation Models"
  - id: kuo-2023-mammut
    resource: ../raw/2303.16839_OneModel/main.tex
    title: "MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks"
---

# ALIGN noisy image–text representation learning

ALIGN is a vision–language representation-learning method that trains image and text encoders from scratch on 1.8 billion lightly filtered image–alt-text pairs. Its central result is that data scale can compensate substantially for noisy text supervision, yielding embeddings useful for cross-modal retrieval, zero-shot image classification, and visual transfer.[^align-2021]

## Method

- An EfficientNet image encoder and BERT text encoder project images and text into a shared, L2-normalized embedding space. The model uses cosine similarity and symmetric normalized-softmax losses for image-to-text and text-to-image matching.[^align-2021]
- Matched image–text pairs are positives; all other pairs in the global batch are negatives. Gathering embeddings across compute cores increases the effective negative set, and the softmax temperature is learned.[^align-2021]
- The training corpus applies limited filtering: image size/aspect-ratio and pornography filters, removal of images with many alt-texts and evaluation-set near duplicates, plus frequency and length filters on text. It remains intentionally noisy relative to curated caption datasets.[^align-2021]

## Scaling finding

For the authors’ EfficientNet-B7/BERT-Base ablation, 3 million noisy ALIGN pairs underperformed cleaned CC-3M, while 12 million noisy pairs outperformed CC-3M on the reported MSCOCO retrieval and ImageNet KNN measures. Larger models also benefited more from the full ALIGN corpus than from a 10% sample; this is evidence for a scale–quality tradeoff, not a claim that noise is universally harmless.[^align-2021]

## Relationships

- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) uses contrastive image–text data for alignment but freezes a pretrained image tower, instead of training ALIGN's image and text encoders from scratch.
- Evaluated by: [WiSE-FT robust zero-shot fine-tuning](wise-ft-robust-zero-shot-fine-tuning.md), which reports that interpolating ALIGN’s zero-shot and fine-tuned weights followed similar accuracy--robustness trends; this is evidence about downstream adaptation, not ALIGN pre-training.[^wortsman-2021-wise-ft]
- Related: [BLIP bootstrapping language–image pre-training](blip-bootstrapping-language-image-pre-training.md) also learns from web image–text pairs, but uses generated captions and an image–text-matching filter to improve the text supervision rather than relying on data scale and light filtering alone.[^li-2022-blip]
- Used by: [CoCa contrastive captioner image–text foundation model](coca-contrastive-captioner-image-text-foundation-model.md), which combines ALIGN alt-text with prompted JFT annotation text in one from-scratch contrastive-and-captioning stage.[^yu-2022-coca]
- Used by: [MaMMUT two-pass multimodal learning](mammut-two-pass-multimodal-learning.md), which reports from-scratch joint contrastive-and-generative pre-training solely on ALIGN’s 1.8B image-alt-text pairs.[^kuo-2023-mammut]

## Capabilities and limits

- The shared space supports text-to-image and image-to-text retrieval, zero-shot classification by comparing image embeddings with prompted class-name embeddings, and compositional image-plus-text queries formed by embedding arithmetic.[^align-2021]
- A multilingual variant trained on 1.8 billion pairs across 100+ languages used a 250k wordpiece vocabulary and reported zero-shot Multi30K retrieval results in English, German, French, and Czech.[^align-2021]
- The paper reports stronger cross-modal than intra-modal similarity performance on CxC, consistent with its cross-modal matching objective. It also identifies web-data bias, harmful text, cultural and demographic skew, and surveillance misuse as deployment risks requiring further analysis and mitigation.[^align-2021]

[^align-2021]: Jia et al., “Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision” (2021), [source](../raw/2102.05918_ALIGN/align.tex).

[^wortsman-2021-wise-ft]: Wortsman et al., “Robust fine-tuning of zero-shot models” (2021), [source manuscript](../raw/2109.01903_WiSE-FT/main.tex).

[^li-2022-blip]: Li et al., “BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation” (2022), [complete manuscript source](../raw/2201.12086_BLIP/main.tex).

[^yu-2022-coca]: Yu et al., “CoCa: Contrastive Captioners are Image-Text Foundation Models” (2022), [complete manuscript source](../raw/2205.01917_CoCa/main.tex).

[^kuo-2023-mammut]: Kuo et al., “MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks” (2023), [complete manuscript source](../raw/2303.16839_OneModel/main.tex).
