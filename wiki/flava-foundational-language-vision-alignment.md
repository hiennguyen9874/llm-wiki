---
type: Concept
title: FLAVA foundational language and vision alignment
description: A vision-language foundation model that joins separate image and text transformers with a multimodal fusion transformer and trains them with paired and unpaired data.
tags: [multimodal-learning, vision-language-pretraining, contrastive-learning, cross-modal-fusion, representation-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:35:29Z }
sources:
  - id: singh-2022-flava
    resource: ../raw/2112.04482_FLAVA/arxiv_strip.tex
    title: "FLAVA: A Foundational Language And Vision Alignment Model"
---

# FLAVA foundational language and vision alignment

FLAVA is a transformer vision-language foundation model designed to retain separate image and text representations for unimodal tasks while also producing fused representations for multimodal reasoning. It combines contrastive alignment with masked and matching objectives, and jointly uses public paired image-text data with unpaired image and text data.[^singh-2022-flava]

## Architecture and training

- Separate ViT-B/16 image and text encoders produce unimodal token sequences. A six-layer multimodal transformer receives linearly projected image and text states plus a multimodal classification token, allowing cross-attention for fused tasks.[^singh-2022-flava]
- On paired data, global contrastive loss aligns unmasked image and text classification states across workers; masked multimodal modeling predicts dVAE image-codebook tokens and masked text tokens; and image-text matching classifies matched versus unmatched pairs.[^singh-2022-flava]
- On unpaired inputs, the image encoder learns masked-image modeling and the text encoder learns masked-language modeling. The reported full recipe initializes the image encoder from DINO ImageNet-1K pretraining and the text encoder from MLM pretraining on CCNews and BookCorpus, then jointly samples paired, image-only, and text-only data.[^singh-2022-flava]
- Its Public Multimodal Datasets corpus contains 70 million image-text pairs (68 million unique images) from nine public datasets. For YFCC100M, the authors retain English captions longer than two words, preferring description and then title; they report no other filtering for that dataset.[^singh-2022-flava]

## Findings

- Across the paper's 35-task vision, language, and multimodal suite, the full model reports a 75.85 macro-average score in its ablation. Adding masked multimodal modeling and image-text matching to contrastive-only pretraining increased the reported multimodal average from 66.25 to 69.11 and language average from 64.80 to 74.22.[^singh-2022-flava]
- Back-propagating the contrastive loss through gathered cross-worker embeddings, rather than only local-worker embeddings, increased the paper's reported macro average by 1.65 points in its controlled comparison.[^singh-2022-flava]
- Against the released CLIP ViT-B/16 trained on 400 million pairs, FLAVA trained on 70 million public pairs performed substantially better on the paper's language and multimodal tasks but was slightly worse on some vision-only tasks. These are benchmark-specific comparisons, not a general ordering of the models.[^singh-2022-flava]

## Limits

- The paper attributes weak performance on image-rendered sentiment text (SST) to insufficient scene text in the paired corpus. Its 72.49 VQAv2 accuracy was below the then state of the art, and the authors expect more pretraining data to help; neither observation establishes how the model will scale.[^singh-2022-flava]
- Public web and benchmark data can retain bias. Combining public datasets may improve diversity, but the authors state that harmful biases still require identification and mitigation.[^singh-2022-flava]
- Reported results use the authors' selected datasets, training configurations, and aggregate metrics. They support the stated multi-domain recipe under those conditions, not general-purpose reliability or safety.

## Relationships

- Related: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) uses a contrastive dual encoder for alignment; FLAVA retains that retrieval-capable interface but adds a fusion encoder and multimodal masked and matching objectives.[^singh-2022-flava]
- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) also finds a global cross-device contrastive loss useful, but freezes a pretrained image tower whereas FLAVA jointly trains its encoders after initialization.[^singh-2022-flava]

[^singh-2022-flava]: Singh et al., “FLAVA: A Foundational Language And Vision Alignment Model” (2022), [source manuscript](../raw/2112.04482_FLAVA/arxiv_strip.tex).