---
type: Concept
title: BridgeTower layer-wise vision–language fusion
description: A vision–language architecture that injects successive high-level image and text encoder features into every cross-modal layer through lightweight bridge connections.
tags: [multimodal-learning, vision-language-pretraining, cross-modal-fusion, representation-learning, transformer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:34:16Z }
sources:
  - id: xu-2022-bridgetower
    resource: ../raw/2206.08657_BridgeTower.md
    title: Building Bridges Between Encoders in Vision-Language Representation Learning
---

# BridgeTower layer-wise vision–language fusion

BridgeTower is a vision–language architecture that preserves deep unimodal image and text encoders while adding a lightweight bridge at each cross-modal layer. Each bridge injects a different high-level encoder representation into the corresponding cross-modal layer, supporting bottom-up alignment and fusion across semantic levels rather than only fusing the encoders’ final outputs.[^xu-2022-bridgetower]

## Architecture

- The reported base configuration uses CLIP ViT-B/16 as the visual encoder, RoBERTa-Base as the text encoder, and a six-layer co-attention cross-modal encoder. Its six bridge layers connect the top six layers of each unimodal encoder to successive cross-modal layers.[^xu-2022-bridgetower]
- For each modality, a bridge combines the previous cross-modal representation with the projected, type-embedded representation from the matching unimodal layer. The selected default is an Add-and-Norm operation, rather than a learned fusion module.[^xu-2022-bridgetower]
- Pre-training uses conditional masked language modeling (masking 15% of text tokens while retaining the image) and image–text matching. For retrieval fine-tuning, the model jointly uses image–text contrastive and matching losses, with contrastive retrieval followed by matching-score reranking.[^xu-2022-bridgetower]

## Findings

- In the paper's no-pretraining ablation, simple Add-and-Norm bridges achieved 75.18 VQAv2 test-dev accuracy and 533.8 Flickr30K recall sum, while more complex interpolation, projection, cross-attention, or feed-forward bridge designs did not improve those results.[^xu-2022-bridgetower]
- With 4 million unique pre-training images from CC, SBU, MSCOCO, and Visual Genome, the base model reported 78.73% VQAv2 test-standard accuracy and a 576.6 Flickr30K recall sum. These are paper-reported benchmark results under its stated comparison settings, not current state-of-the-art claims.[^xu-2022-bridgetower]
- Compared with the authors’ Meter reimplementation without pre-training, the base BridgeTower added 18.4K parameters and increased reported VQA inference time by under 0.5 ms, while improving VQAv2 test-dev by 1.14 points and Flickr30K recall sum by 3.1 points.[^xu-2022-bridgetower]

## Limits

- The study evaluates discriminative vision–language tasks; image captioning and other generative tasks were proposed as future work rather than evaluated.[^xu-2022-bridgetower]
- After vision–language pre-training, the retained unimodal encoders declined slightly on the reported CIFAR and GLUE evaluations, although less than the Meter comparison. This does not establish preservation of unimodal capabilities outside those benchmarks.[^xu-2022-bridgetower]
- Reported comparisons cover particular encoders, datasets, and fine-tuning configurations. The paper's claim that bridge layers improve performance across tested backbones should not be generalized to arbitrary encoders or tasks without further evidence.[^xu-2022-bridgetower]

## Relationships

- Uses: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) supplies the visual encoder in the paper's reported base and large configurations; BridgeTower differs from CLIP by using a deep cross-modal encoder for fusion rather than a dual-encoder similarity score.[^xu-2022-bridgetower]

[^xu-2022-bridgetower]: Xu et al., “Building Bridges Between Encoders in Vision-Language Representation Learning” (2022), [source](../raw/2206.08657_BridgeTower.md).