---
type: Concept
title: MaMMUT two-pass multimodal learning
description: A decoder-only vision-language architecture that uses two text-decoder passes to jointly train contrastive retrieval and image-conditioned generation with shared weights.
tags: [vision-language-pretraining, multimodal-learning, contrastive-learning, image-captioning, video-understanding, open-vocabulary-detection]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:46:23Z }
sources:
  - id: kuo-2023-mammut
    resource: ../raw/2303.16839_OneModel/main.tex
    title: "MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks"
---

# MaMMUT two-pass multimodal learning

MaMMUT is a vision encoder plus decoder-only text model that jointly supports image-text contrastive retrieval and image-conditioned text generation. Its two-pass procedure reconfigures one shared text decoder as a bidirectional, image-independent text encoder for contrastive alignment and as a causal, cross-attending decoder for generation.[^kuo-2023-mammut]

## Architecture and objectives

- A ViT image encoder produces image features. A Transformer decoder receives projected visual features through cross-attention layers placed through the decoder; the same decoder weights serve both passes.[^kuo-2023-mammut]
- In the contrastive pass, cross-attention is disabled and self-attention is bidirectional, allowing the decoder to encode the complete text independently of the image. Average-pooled image and text features are optimized with symmetric image-to-text and text-to-image focal contrastive losses.[^kuo-2023-mammut]
- In the generative pass, causal masking and visual cross-attention are enabled, and the decoder is optimized for autoregressive next-token prediction. The total objective is a weighted sum of captioning and focal contrastive losses; the reported main training uses equal weights.[^kuo-2023-mammut]
- The focal contrastive objective up-weights difficult pairwise decisions. The authors use it with cropped positional embeddings during a further 100,000 iterations of training to better match region-level detection transfer.[^kuo-2023-mammut]

## Training and transfer

- The reported large configuration uses a ViT-Huge image encoder and a 1B-parameter text decoder, with cross-attention every two decoder layers. It is trained from scratch for 500,000 steps on the 1.8B-pair ALIGN alt-text corpus, with batch size 16,000; the paper reports roughly 16% pre-training overhead versus its pure contrastive learner.[^kuo-2023-mammut]
- For video, MaMMUT adds TubeViT-style sparse spatiotemporal tube tokens to the shared image encoder. It retains learned positional embeddings and adds fixed embeddings through a weighted connection; the paper directly fine-tunes this image-text-pretrained model on video datasets rather than adding video-text pre-training.[^kuo-2023-mammut]
- The paper’s smaller-model ablations found that jointly training both objectives improved VQA accuracy to 71.7 versus 69.9 for generative-only and 63.5 for contrastive-only training, while the joint model retained retrieval capability. Bidirectional masking improved the reported Flickr30K text-to-image R@1 from 62.5 to 67.3 versus causal masking in the contrastive pass.[^kuo-2023-mammut]

## Reported evaluation and limits

- The paper reports zero-shot COCO R@1 of 70.7 for image-to-text and 54.1 for text-to-image retrieval, and Flickr30K R@1 of 94.9 and 82.5 respectively. These are the paper’s selected zero-shot benchmark protocols, not a general retrieval guarantee.[^kuo-2023-mammut]
- On VQAv2 in an open-vocabulary generation setting, MaMMUT reports 80.8 test-std accuracy. Its reported video fine-tuning results are 49.5 on MSRVTT-QA and 60.2 on MSVD-QA; video-captioning CIDEr is 73.6 on MSRVTT and 195.6 on MSVD.[^kuo-2023-mammut]
- The open-vocabulary detector, initialized from the pretrained ViT and combined with a ViTDet-style feature pyramid and Mask R-CNN heads, reports LVIS rare-category $AP_r$ of 31.0. This is a task-specific fine-tuning result, not evidence that the base model directly produces detections.[^kuo-2023-mammut]
- The authors identify risks from text generation, including off-topic, stereotypical, and unwanted outputs. Training on noisy web image-text pairs may also carry the data-quality and bias limitations of that supervision; the paper reports evaluation and visualization use, not deployment validation.[^kuo-2023-mammut]

## Relationships

- Uses: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) as its sole reported pre-training corpus: 1.8B noisy image-alt-text pairs.[^kuo-2023-mammut]
- Related: [CoCa contrastive captioner image–text foundation model](coca-contrastive-captioner-image-text-foundation-model.md) also combines contrastive alignment and captioning, but CoCa partitions a causal decoder into text-only and cross-attending sections, whereas MaMMUT switches the masking and cross-attention configuration across two passes of its shared decoder.[^kuo-2023-mammut]

## Evidence scope

Claims were compiled from the complete manuscript TeX, including appendix ablations and result tables. All four supplied PNG figures and the three supplied architectural PDF figures were visually inspected; no claim depends on details beyond the source text, tables, or figure captions.[^kuo-2023-mammut]

[^kuo-2023-mammut]: Kuo et al., “MaMMUT: A Simple Architecture for Joint Learning for MultiModal Tasks” (2023), [complete manuscript source](../raw/2303.16839_OneModel/main.tex).
