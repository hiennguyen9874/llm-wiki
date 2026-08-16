---
type: Concept
title: SigLIP sigmoid contrastive language–image pre-training
description: A CLIP-style dual encoder that replaces batch-normalized contrastive softmax with an independently scored pairwise sigmoid loss.
tags: [multimodal-learning, contrastive-learning, sigmoid-loss, representation-learning, zero-shot-transfer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:45:53Z }
sources:
  - id: zhai-2023-siglip
    resource: ../raw/2303.15343_SigLIP.md
    title: Sigmoid Loss for Language Image Pre-Training
  - id: faysse-2024-colpali
    resource: ../raw/2407.01449_ColPali.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: gritsenko-2025-siglip2
    resource: ../raw/2502.14786_SigLIP2.md
    title: SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features
---

# SigLIP sigmoid contrastive language–image pre-training

SigLIP replaces CLIP’s globally normalized softmax contrastive objective with a pairwise sigmoid loss: matched image–text pairs are positive and all in-batch mismatches are negative. This removes the loss’s global normalization dependency, permitting a chunked distributed implementation with lower peak memory while retaining a shared image–text embedding space for zero-shot classification and retrieval.[^zhai-2023-siglip]

## Objective and implementation

- For L2-normalized image and text embeddings, every image–text pair receives a binary label (+1 for its matching pair, −1 otherwise). SigLIP applies logistic loss to the similarity scaled by a learned temperature and shifted by a learned bias; it initializes the log-temperature to $\log 10$ and bias to −10 to start near the highly negative class prior.[^zhai-2023-siglip]
- Unlike CLIP’s two directional softmax normalizations, each pairwise sigmoid-loss term is independent. In distributed training, devices can accumulate local image-by-text loss chunks while permuting text embeddings between devices, rather than all-gathering embeddings and materializing the global batch-squared similarity matrix.[^zhai-2023-siglip]
- The paper calls the frozen-image-tower variant SigLiT: it applies the sigmoid objective to Locked-image Tuning, whose image embeddings can be precomputed.[^zhai-2023-siglip]

## Reported findings

- In the authors’ SigLIP and SigLiT experiments, sigmoid loss outperformed the softmax baseline at batch sizes below 16k, while the difference narrowed at larger sizes. Their sweeps found performance generally saturated around a 32k batch size; still larger batches sometimes reduced performance. This is experimental evidence for the tested data, models, and schedules, not a universal batch-size rule.[^zhai-2023-siglip]
- Chunking enabled a SigLiT run at a one-million-example batch size. A separate frozen ViT-g/14 SigLiT configuration reported 84.5% ImageNet zero-shot accuracy after two days on four TPU v4 chips.[^zhai-2023-siglip]
- For multilingual WebLI training across more than 100 languages, the paper used a bottlenecked token embedding to reduce vocabulary-memory cost. Its 32k-batch mSigLIP run reported the best mean text-to-image recall@1 (34.9%) among its tested batch sizes on XM3600; larger batches worsened the average retrieval metric.[^zhai-2023-siglip]
- In controlled corruptions of images, text, and pair alignment, the sigmoid-trained models retained an advantage over the corresponding softmax baseline as corruption probability grew. This supports robustness to the paper’s synthetic noise settings, not robustness to arbitrary real-world data errors.[^zhai-2023-siglip]

## Training considerations and limits

- The authors observed gradient-norm spikes at large batch sizes and report that reducing Adam/AdaFactor $\beta_2$ from 0.999 to 0.95 stabilized their training; this is a reported recipe rather than a generally validated default.[^zhai-2023-siglip]
- The model card describes research use for zero-shot classification and image–text retrieval. Reported models were trained on WebLI (an English-filtered subset for SigLIP and unfiltered data for mSigLIP), so performance claims are tied to those data and specified benchmarks.[^zhai-2023-siglip]
- Sigmoid loss changes the handling of batch negatives but does not eliminate the noisy-pair assumption: nonmatching items in a batch are still treated as negatives even when they may be semantically related.[^zhai-2023-siglip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) with a pairwise sigmoid objective in place of CLIP’s symmetric globally normalized softmax loss.[^zhai-2023-siglip]
- Extends: [LiT locked-image tuning](lit-locked-image-tuning.md) through SigLiT, which freezes the image tower while training with sigmoid loss.[^zhai-2023-siglip]
- Extended by: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md), which retains SigLIP’s core architecture and sigmoid image–text loss while adding multilingual tokenization and staged auxiliary training.[^gritsenko-2025-siglip2]
- Used by: [ColPali vision-space document retrieval](colpali-vision-space-document-retrieval.md), whose PaliGemma backbone uses a SigLIP vision encoder.[^faysse-2024-colpali]

[^zhai-2023-siglip]: Zhai et al., “Sigmoid Loss for Language Image Pre-Training” (2023), [source](../raw/2303.15343_SigLIP.md).
[^faysse-2024-colpali]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2024), [source](../raw/2407.01449_ColPali.md).
[^gritsenko-2025-siglip2]: Gritsenko et al., “SigLIP 2: Multilingual Vision-Language Encoders with Improved Semantic Understanding, Localization, and Dense Features” (2025), [source](../raw/2502.14786_SigLIP2.md).