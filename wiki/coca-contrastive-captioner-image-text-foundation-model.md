---
type: Concept
title: CoCa contrastive captioner image–text foundation model
description: A single-stage image–text encoder–decoder that combines contrastive alignment and captioning through a decoupled text decoder.
tags: [vision-language-pretraining, multimodal-learning, contrastive-learning, image-captioning, zero-shot-transfer]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:30:00Z }
sources:
  - id: yu-2022-coca
    resource: ../raw/2205.01917_CoCa/main.tex
    title: "CoCa: Contrastive Captioners are Image-Text Foundation Models"
  - id: kuo-2023-mammut
    resource: ../raw/2303.16839_OneModel/main.tex
    title: "MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks"
---

# CoCa contrastive captioner image–text foundation model

CoCa (Contrastive Captioners) is a single-stage image–text foundation-model design that combines CLIP-style contrastive alignment with autoregressive captioning. Its text decoder is split into a text-only lower portion and an image-cross-attending upper portion, so one model produces aligned unimodal embeddings as well as fused multimodal representations.[^yu-2022-coca]

## Architecture and objectives

- An image Transformer encodes images. The bottom half of the causal text decoder has no cross-attention and produces a text-only representation; the top half cross-attends to image features and predicts caption tokens. A learned `[CLS]` token appended to the text is the contrastive text embedding.[^yu-2022-coca]
- CoCa jointly minimizes symmetric image–text contrastive loss between one pooled image representation and the unimodal text embedding, plus autoregressive captioning loss from the multimodal decoder. In the reported default, captioning and contrastive loss weights are 2:1.[^yu-2022-coca]
- Separate attentional poolers produce one image query for contrastive alignment and a sequence of image features for captioning. In the authors’ ablation, cascading the contrastive pooler on the generative pooler outperformed their parallel design; the full model uses a 256-query generative pooler.[^yu-2022-coca]
- The paper reports Base (383M), Large (787M), and 2.1B-parameter variants. The largest combines a 1B-parameter image encoder with a 1.1B-parameter text decoder.[^yu-2022-coca]

## Training and transfer

- The model is trained from scratch for one stage on JFT-3B annotations rendered as prompted text and noisy ALIGN alt-text, with half of each 65,536-pair batch drawn from each source. Training ran for 500,000 steps, followed by one higher-resolution epoch; near-domain evaluation examples were filtered using the cited de-duplication procedure.[^yu-2022-coca]
- The shared contrastive interface supports zero-shot image classification and image–text or video–text retrieval. The image encoder alone can be frozen with a learned attentional pooler and classifier for image or frame-based video recognition; the multimodal decoder supports captioning and image–text understanding after task-specific fine-tuning.[^yu-2022-coca]
- In the paper’s smaller-model ablation, combining the losses improved ImageNet zero-shot accuracy from 70.7% for contrastive-only training to 71.6% and VQA score from 59.2% to 69.0%, at 1.18 times the reported contrastive-only TPU cost. Captioning-only training did not furnish a retrieval-style zero-shot classifier. These are controlled results for that configuration, not general cost or performance guarantees.[^yu-2022-coca]

## Reported evaluation and limits

- The largest model reported 86.3% ImageNet zero-shot top-1, 90.6% with a frozen encoder and learned head, and 91.0% after finetuning. It also reported zero-shot Flickr30K/MSCOCO retrieval R@1 of 92.5/80.4 for image-to-text and 80.4/51.2 for text-to-image, respectively.[^yu-2022-coca]
- CoCa reported fine-tuned VQA test-dev/test-std scores of 82.3/82.3, SNLI-VE dev/test scores of 87.0/87.1, and NoCaps test CIDEr/SPICE of 120.6/15.5 without CIDEr-specific optimization. These are results on the paper’s selected benchmarks and protocols, not evidence of broad multimodal reasoning or caption-quality guarantees.[^yu-2022-coca]
- Its video results use independently encoded frames and pooling rather than temporal early fusion. MSR-VTT retrieval was computed only over videos still publicly available, so the subset results are not directly comparable to full-split results.[^yu-2022-coca]
- CoCa inherits web-scale and image-annotation-data concerns: the authors state that more analysis is needed before use in practice and that robustness to their corruption tests does not establish robustness to unrepresented corruptions, fairness, social bias, or misuse.[^yu-2022-coca]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining contrastive image–text embeddings while adding an image-conditioned generative decoder and fused representations.[^yu-2022-coca]
- Uses: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) as one of its two reported pre-training data sources; CoCa combines ALIGN alt-text with prompted JFT annotation text in a single from-scratch stage.[^yu-2022-coca]
- Related: [BLIP bootstrapping language–image pre-training](blip-bootstrapping-language-image-pre-training.md) also combines alignment and generation capabilities, but CoCa’s reported design shares a causal decoder split by cross-attention and does not use BLIP’s caption-and-filter bootstrapping.[^yu-2022-coca]
- Related: [MaMMUT two-pass multimodal learning](mammut-two-pass-multimodal-learning.md) also jointly trains contrastive and generative objectives, but MaMMUT switches its shared decoder between a bidirectional text-only pass and a causal cross-attending pass rather than partitioning a causal decoder into fixed portions.[^kuo-2023-mammut]

## Evidence scope

Claims were compiled from the complete manuscript TeX, all included section and result-table TeX files, and visual checks of the architecture and overview figures. Other result and illustrative figures were not visually inspected; no claim depends on visual details absent from their captions or tables.[^yu-2022-coca]

[^yu-2022-coca]: Yu et al., “CoCa: Contrastive Captioners are Image-Text Foundation Models” (2022), [complete manuscript source](../raw/2205.01917_CoCa/main.tex).

[^kuo-2023-mammut]: Kuo et al., “MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks” (2023), [complete manuscript source](../raw/2303.16839_OneModel/main.tex).