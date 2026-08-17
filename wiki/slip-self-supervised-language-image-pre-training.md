---
type: Concept
title: SLIP self-supervised language-image pre-training
description: A multi-task CLIP variant that jointly optimizes image-text contrastive alignment and image-only self-supervision through a shared image encoder.
tags: [multimodal-learning, contrastive-learning, self-supervised-learning, zero-shot-transfer, representation-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:18:42Z }
sources:
  - id: mu-2022-slip
    resource: ../raw/2112.12750_SLIP/slip.tex
    title: "SLIP: Self-supervision Meets Language-Image Pre-training"
---

# SLIP self-supervised language-image pre-training

SLIP jointly trains a CLIP-style image-text objective and an image-only self-supervised objective through one image encoder. In the paper’s YFCC15M experiments, this multi-task training improved both zero-shot transfer and linear-probe performance over its CLIP and self-supervised baselines, while retaining the post-training interface of either representation.[^mu-2022-slip]

## Method

- For each image-caption pair, the CLIP branch encodes a global image crop and its caption with separate image and text encoders, then applies CLIP’s symmetric contrastive loss. The self-supervised branch passes two augmented views through the same image encoder and applies a second objective; the losses are summed.[^mu-2022-slip]
- The default SLIP implementation uses SimCLR, with an unscaled self-supervised loss. Its image and text projections are 512-dimensional for CLIP; the SimCLR projection head has three MLP layers with 4,096-dimensional hidden layers and a 256-dimensional output.[^mu-2022-slip]
- The authors also substituted MoCo v3, BYOL, and BEiT as the self-supervised branch. In their ViT-B/16, 25-epoch YFCC15M configuration, all variants exceeded the paper’s CLIP baseline, while SLIP-SimCLR was the strongest reported variant; this does not establish an ordering for other data, architecture, or tuning choices.[^mu-2022-slip]
- Self-supervision need not operate on the image-caption examples: a variant trained its image-only objective on a disjoint 15M-image set and reported nearly identical ImageNet results to ordinary SLIP. Conversely, initializing CLIP from self-supervised weights then training CLIP sequentially underperformed joint training in the paper’s ViT-B/16 comparison.[^mu-2022-slip]

## Reported findings and limits

- On YFCC15M with ViT-B/16 trained for 25 epochs, SLIP reported ImageNet zero-shot, linear-probe, and end-to-end-finetuning top-1 accuracy of 42.8%, 72.1%, and 82.6%, respectively. The matching CLIP baseline reported 37.6%, 66.5%, and 80.5%; the SimCLR baseline did not support zero-shot transfer and reported 64.0% linear and 82.5% finetuned accuracy. These are the authors’ experimental results, not general guarantees.[^mu-2022-slip]
- Across its ViT-S/B/L YFCC15M runs, SLIP improved the paper’s CLIP baseline by 4.8–5.6 points in ImageNet zero-shot accuracy and the stronger unimodal or multimodal baseline by 5.5–7.1 points in linear accuracy after 25 epochs. Longer training generally improved zero-shot and finetuning results, but linear-probe performance for ViT-L declined from 76.0% at 25 epochs to 75.1% at 100 epochs.[^mu-2022-slip]
- The study evaluates uncurated YFCC15M, CC3M, and CC12M pre-training data, but its downstream suite remains classification-oriented. The authors report weak or near-chance zero-shot performance on concepts poorly represented in pre-training data, including OCR-dependent tasks, and caution that uncurated-web pre-training is inefficient for specialized concepts without relevant pre-training coverage or downstream adaptation.[^mu-2022-slip]
- Training uses three image views per example, increasing activations and memory. The authors report 30.5 hours for SLIP versus 22.3 hours for CLIP to train ViT-B/16 on 64 V100 GPUs; after pre-training, they report no extra cost because the vision backbone is used like a CLIP or self-supervised backbone.[^mu-2022-slip]

## Risks and governance

SLIP inherits the risks of CLIP-style training on noisy, minimally filtered internet data, including harmful applications and the amplification of problematic real-world behavior. The authors recommend more cautious and responsible training-data selection but do not supply a comprehensive mitigation or deployment-safety evaluation.[^mu-2022-slip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) retains its image-text contrastive branch and adds an image-only self-supervised objective through the shared image encoder.[^mu-2022-slip]

[^mu-2022-slip]: Mu et al., “SLIP: Self-supervision Meets Language-Image Pre-training” (2022), [complete source manuscript](../raw/2112.12750_SLIP/slip.tex).