---
type: Concept
title: DeCLIP data-efficient contrastive language–image pre-training
description: A CLIP-style dual encoder that augments paired image–text contrastive learning with unimodal self-supervision, cross-modal multi-view contrast, and text-nearest-neighbor positives.
tags: [multimodal-learning, contrastive-learning, self-supervised-learning, zero-shot-transfer, representation-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:10:43Z }
sources:
  - id: li-2022-declip
    resource: ../raw/2110.05208_DeCLIP/declip.tex
    title: "Supervision Exists Everywhere: A Data Efficient Contrastive Language-Image Pre-training Paradigm"
---

# DeCLIP data-efficient contrastive language–image pre-training

DeCLIP is a CLIP-style dual encoder that seeks greater data efficiency by combining the ordinary paired image–text contrastive objective with image and text self-supervision, augmented cross-modal views, and text-nearest-neighbor positives mined from a feature queue.[^li-2022-declip]

## Method

- It retains normalized image and text embeddings, a learnable temperature, and symmetric InfoNCE contrastive losses over matched versus in-batch mismatched pairs.[^li-2022-declip]
- Image self-supervision uses SimSiam between two augmented image views, with a stop-gradient predictor; text self-supervision uses masked-language modeling. The reported configuration masks 15% of tokens, replacing selected tokens with `[mask]` 80% of the time, random tokens 10%, and unchanged tokens 10%.[^li-2022-declip]
- Cross-modal multi-view supervision forms two augmented image views and two text views, then applies contrastive losses to the three additional image–text view pairings. Image augmentation includes random resized crops, while text augmentation randomly applies EDA synonym replacement, token swaps, or token deletion.[^li-2022-declip]
- For nearest-neighbor supervision, DeCLIP retrieves a text embedding near each text in a 64K FIFO feature queue and uses it as an additional image–text contrastive positive. The overall loss weights the base CLIP, self-supervised, multi-view, and nearest-neighbor terms; the reported default sets each auxiliary-term weight to 0.2.[^li-2022-declip]

## Reported findings and limits

- On the authors’ 88M-pair corpus, DeCLIP reported ImageNet zero-shot top-1 accuracies of 62.5% with ResNet-50 and 66.2% with ViT-B/32, versus the paper’s cited CLIP results of 59.6% and 63.2%, respectively, trained on 400M pairs. The corpus combined about 29M partially retrieved public-dataset pairs with 59M web-crawled pairs, so these cross-paper comparisons also vary training data and are not controlled architecture-only measurements.[^li-2022-declip]
- In a CC3M ResNet-50 ablation, the baseline contrastive model scored 20.6% ImageNet zero-shot top-1; adding multi-view supervision scored 24.8%, then self-supervision 25.4%, and nearest-neighbor supervision 27.2%. These incremental findings are specific to that smaller experimental configuration.[^li-2022-declip]
- Additional views raise cost: the authors estimate one DeCLIP iteration at 1.5 times a CLIP iteration. On their CC3M study, 32-epoch DeCLIP used 304 GPU-hours and 22.7 GB per GPU, compared with 399 GPU-hours and 24.0 GB for a 64-epoch, doubled-batch CLIP baseline; the corresponding reported zero-shot accuracies were 27.2% and 22.3%.[^li-2022-declip]
- The full pre-training corpus and some reported reference models depend on web crawling and partially unavailable downloads. The manuscript has empty ethics and reproducibility statements, and it does not provide evidence of independent reproduction or a broader bias and safety assessment.[^li-2022-declip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) retains its dual-encoder, symmetric contrastive setup but adds self-supervised, multi-view, and nearest-neighbor objectives.[^li-2022-declip]
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) also learns a dual-encoder image–text space from web-scale data, whereas DeCLIP emphasizes auxiliary supervision for a smaller, mixed corpus.[^li-2022-declip]

[^li-2022-declip]: Li et al., “Supervision Exists Everywhere: A Data Efficient Contrastive Language-Image Pre-training Paradigm” (2022), [source manuscript](../raw/2110.05208_DeCLIP/declip.tex).
