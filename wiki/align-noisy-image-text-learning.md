---
type: Concept
title: ALIGN noisy image–text representation learning
description: A dual-encoder contrastive approach showing that web-scale, lightly filtered image alt-text can support transferable multimodal representations.
tags: [multimodal-learning, contrastive-learning, representation-learning, retrieval]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:26:31Z }
sources:
  - id: align-2021
    resource: ../raw/2102.05918_ALIGN/align.tex
    title: Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision
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

## Capabilities and limits

- The shared space supports text-to-image and image-to-text retrieval, zero-shot classification by comparing image embeddings with prompted class-name embeddings, and compositional image-plus-text queries formed by embedding arithmetic.[^align-2021]
- A multilingual variant trained on 1.8 billion pairs across 100+ languages used a 250k wordpiece vocabulary and reported zero-shot Multi30K retrieval results in English, German, French, and Czech.[^align-2021]
- The paper reports stronger cross-modal than intra-modal similarity performance on CxC, consistent with its cross-modal matching objective. It also identifies web-data bias, harmful text, cultural and demographic skew, and surveillance misuse as deployment risks requiring further analysis and mitigation.[^align-2021]

[^align-2021]: Jia et al., “Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision” (2021), [source](../raw/2102.05918_ALIGN/align.tex).
