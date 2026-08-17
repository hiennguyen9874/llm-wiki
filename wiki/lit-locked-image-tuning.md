---
type: Concept
title: LiT locked-image tuning
description: A contrastive-tuning method that freezes a pretrained image encoder and trains a text encoder to enable efficient zero-shot vision transfer.
tags: [multimodal-learning, contrastive-learning, transfer-learning, zero-shot-transfer, representation-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:40:28Z }
sources:
  - id: zhai-2021-lit
    resource: ../raw/2111.07991_Vision Text Dual Encoder/c.tex
    title: LiT: Zero-Shot Transfer with Locked-image Text Tuning
  - id: zhai-2021-lit-appendix
    resource: ../raw/2111.07991_Vision Text Dual Encoder/appendix.tex
    title: LiT: Zero-Shot Transfer with Locked-image Text Tuning — appendix
  - id: yang-2022-chinese-clip
    resource: ../raw/2211.01335_Chinese-CLIP/acl2023.tex
    title: "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese"
  - id: chen-2022-altclip
    resource: ../raw/2211.06679_AltCLIP/main.tex
    title: "AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities"
  - id: zhai-2023-siglip
    resource: ../raw/2303.15343_SigLIP.md
    title: Sigmoid Loss for Language Image Pre-Training
---

# LiT locked-image tuning

Locked-image Tuning (LiT) is a contrastive-tuning method that freezes a strong pretrained image encoder and trains a text encoder to align with its embedding space. It decouples visual-representation learning from image–text alignment, allowing existing vision backbones to gain zero-shot classification and retrieval while avoiding image-tower backpropagation.[^zhai-2021-lit]

## Method

- LiT uses the standard contrastive objective over matched and mismatched image–text pairs, with optional linear projection heads mapping both towers to a shared dimensionality. It uses a global, cross-device loss because the authors found it consistently better than per-device loss.[^zhai-2021-lit]
- Its `Lu` configuration locks a pretrained image tower (`L`) and trains a randomly initialized text tower (`u`); this is LiT. The paper also distinguishes trainable pretrained towers (`U`) and from-scratch towers (`u`).[^zhai-2021-lit]
- At inference, class descriptions are embedded by the text tower and compared with an image embedding for zero-shot classification; the same shared space supports image–text retrieval.[^zhai-2021-lit]

## Findings

- Across supervised and self-supervised vision pretraining, architectures (Vision Transformers, ResNets, and MLP-Mixers), and several image–text datasets, locking the pretrained image tower generally produced the strongest reported zero-shot classification. The authors attribute this to preserving a general visual representation while training the text tower to read it out, rather than specializing the image encoder to the alignment corpus.[^zhai-2021-lit]
- In the paper's private-data experiment, a ViT-g/14 LiT model reported 85.2% ImageNet zero-shot top-1 accuracy and 82.5% ObjectNet accuracy. With public YFCC100m-CLIP plus CC12M data and a pretrained ViT-L/16, it reported 75.7% ImageNet zero-shot accuracy; these are reported experimental results, not directly comparable deployment guarantees.[^zhai-2021-lit]
- A locked image tower removes its gradient cost and, without image augmentation, permits precomputing image embeddings. The paper reports that this can reduce tuning time and memory use and enable larger text models or batch sizes.[^zhai-2021-lit]
- More generally pretrained image models—including DINO and MoCo-v3—were better LiT inputs than narrowly pretrained ones when evaluated across image–text tasks. Text-model pretraining had smaller and dataset-dependent benefits; multilingual data, multilingual text pretraining, and multilingual tokenization improved reported long-tail-language results without materially reducing English performance.[^zhai-2021-lit]

## Limits

- LiT's advantage was clearer for zero-shot classification than retrieval: for sufficiently long tuning schedules, configurations that train the image tower sometimes surpassed `Lu` on retrieval. The authors therefore recommend considering trainable-image variants when retrieval, rather than zero-shot classification, is the primary objective.[^zhai-2021-lit]
- The study evaluates classification and retrieval, not detection, segmentation, visual question answering, or captioning. Its private-data results depend on a non-public image–text corpus, limiting independent reproduction of those numbers.[^zhai-2021-lit]
- The reported VTAB evaluations selected image preprocessing, prompt templates, and often task-specific class names on an 800-image validation set before testing. The authors therefore characterize this protocol as arguably not strict zero-shot transfer; structured-task performance did not significantly exceed random guessing despite prompt engineering.[^zhai-2021-lit-appendix]
- The multilingual evaluation has additional confounds: translated prompts can be imperfect, and WIT examples often retain proper nouns across languages, which can overstate a monolingual model’s multilingual performance. The reported multilingual gains should therefore not be treated as a comprehensive language-understanding evaluation.[^zhai-2021-lit-appendix]
- The authors note that attaching an open-vocabulary text tower to existing image models can facilitate harmful or offensive applications; their conclusion calls for further work on desired model behavior.[^zhai-2021-lit]

## Relationships

- Related: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) jointly trains image and text towers from scratch, whereas LiT reuses a frozen pretrained image tower.
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) trains both towers from scratch on web-scale alt-text, while LiT tests whether locking a pretrained image tower improves transfer.
- Used by: [Chinese CLIP language-specific vision–language pre-training](chinese-clip-language-specific-vision-language-pretraining.md) uses LiT as an initial Chinese text-alignment stage before jointly tuning both encoders.[^yang-2022-chinese-clip]
- Used by: [AltCLIP multilingual text-encoder alignment](altclip-multilingual-text-encoder-alignment.md) freezes CLIP's image tower during contrastive tuning, but first distills a multilingual XLM-R text encoder from CLIP using parallel text.[^chen-2022-altclip]
- Extended by: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) as SigLiT, which retains LiT’s locked image tower but uses the pairwise sigmoid objective.[^zhai-2023-siglip]

[^zhai-2021-lit]: Zhai et al., “LiT: Zero-Shot Transfer with Locked-image Text Tuning” (2021), [source manuscript](../raw/2111.07991_Vision%20Text%20Dual%20Encoder/c.tex).

[^zhai-2021-lit-appendix]: Zhai et al., “LiT: Zero-Shot Transfer with Locked-image Text Tuning” (2021), [appendix source](../raw/2111.07991_Vision%20Text%20Dual%20Encoder/appendix.tex).

[^yang-2022-chinese-clip]: Yang et al., “Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese” (2022), [source manuscript](../raw/2211.01335_Chinese-CLIP/acl2023.tex).

[^chen-2022-altclip]: Chen et al., “AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities” (2022), [source manuscript](../raw/2211.06679_AltCLIP/main.tex).

[^zhai-2023-siglip]: Zhai et al., “Sigmoid Loss for Language Image Pre-Training” (2023), [source](../raw/2303.15343_SigLIP.md).