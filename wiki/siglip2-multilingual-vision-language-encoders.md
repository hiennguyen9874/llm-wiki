---
type: Concept
title: SigLIP 2 multilingual vision–language encoders
description: A multilingual, open-weight SigLIP successor that combines sigmoid image–text alignment with auxiliary captioning, self-supervision, and data-curation stages to improve global and dense visual representations.
tags: [multimodal-learning, vision-language-models, multilingual, representation-learning, dense-prediction, localization]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:49:15Z }
sources:
  - id: tschannen-2025-siglip2
    resource: ../raw/2502.14786_SigLIP2/document.tex
    title: SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features
---

# SigLIP 2 multilingual vision–language encoders

SigLIP 2 is an open-weight multilingual successor to SigLIP that retains its dual-encoder sigmoid image–text objective while adding staged decoder-based pretraining, vision self-supervision, and—for its smallest fixed-resolution models—active data curation. The authors report improvements over matching SigLIP variants on evaluated zero-shot, retrieval, VLM-transfer, localization, and dense-prediction tasks; these are benchmark-specific reported results, not a general performance guarantee.[^tschannen-2025-siglip2]

## Training recipe

- Fixed-resolution models retain the SigLIP ViT architecture and MAP pooling, enabling users to substitute weights. The released family comprises B (86M), L (303M), So400m (400M), and g (1B) sizes; the g vision encoder is paired with an So400m text encoder. They use a multilingual Gemma tokenizer with a 256k vocabulary and a 64-token text length.[^tschannen-2025-siglip2]
- The initial stage weights the sigmoid image–text loss and a LocCa-style decoder loss equally. The temporary decoder cross-attends to unpooled visual features and trains image captioning, referring-expression prediction, and grounded captioning; it is used only for representation learning and is not released with the encoder.[^tschannen-2025-siglip2]
- At 80% of training, the recipe adds local-to-global EMA-teacher self-distillation and masked patch prediction. These objectives target unpooled visual features to improve local semantic representations used by dense tasks; the image–text and decoder losses continue on unaugmented images.[^tschannen-2025-siglip2]
- Training uses WebLI image–text data across 109 languages with a 90% English and 10% non-English mixture, plus filtering intended to mitigate representation and association biases. The source reports the data composition and intended mitigation, not an absence of bias.[^tschannen-2025-siglip2]
- B/16 and B/32 fixed-resolution models receive a final ACID active-sample-selection stage, using a curated So400m teacher to implicitly distill through selected data rather than an explicit teacher-output loss.[^tschannen-2025-siglip2]

## NaFlex variable-resolution variant

NaFlex uses a single ViT checkpoint across predefined sequence lengths while resizing images with minimal aspect-ratio distortion. It resizes learned positional embeddings to the non-square patch grid and masks padding tokens, making it suited to inputs such as documents where resolution and aspect ratio matter.[^tschannen-2025-siglip2]

NaFlex omits the self-distillation and masked-prediction stage to constrain implementation and compute complexity. It interpolates reasonably between its training resolutions but, according to the authors, does not extrapolate well beyond them.[^tschannen-2025-siglip2]

## Reported evaluation and limits

- On XM3600, covering 36 languages, SigLIP 2 substantially exceeded SigLIP retrieval performance but slightly trailed mSigLIP; the paper reports that mSigLIP performed substantially worse on its English-focused benchmarks.[^tschannen-2025-siglip2]
- With frozen encoders paired with Gemma 2 for the paper's VLM training and transfer setup, SigLIP 2 outperformed SigLIP across tested model sizes and resolutions; these results depend on that setup and downstream-task protocol.[^tschannen-2025-siglip2]
- The source reports improved dense prediction, open-vocabulary segmentation and detection, and referring-expression comprehension versus its tested baselines. It attributes referring-expression gains in part to decoder-based pretraining, while noting that the English-only LocCa model outperformed SigLIP 2 on the reported referring-expression benchmark.[^tschannen-2025-siglip2]
- De-biasing filters reduced the paper's representation-bias metric for the tested models (for example, from 35.5% to 7.3% for L/16 at 256 px), but income-level and geographic-region performance disparities showed only minor or no matching-model benefit. The fairness findings are metric- and benchmark-bound.[^tschannen-2025-siglip2]

## Relationships

- Extends: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) with multilingual tokenization and a staged auxiliary-training recipe while preserving the core architecture and sigmoid image–text loss.[^tschannen-2025-siglip2]

[^tschannen-2025-siglip2]: Tschannen et al., “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features” (2025), [complete manuscript source](../raw/2502.14786_SigLIP2/document.tex).
