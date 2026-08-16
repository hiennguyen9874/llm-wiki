---
type: Concept
title: CLIP natural-language image pre-training
description: A contrastive image–text pre-training method that uses language prompts to synthesize zero-shot image classifiers.
tags: [multimodal-learning, contrastive-learning, zero-shot-transfer, prompt-engineering, representation-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:40:00Z }
sources:
  - id: radford-2021-clip
    resource: ../raw/2103.00020_CLIP.md
    title: Learning Transferable Visual Models From Natural Language Supervision
  - id: xu-2022-bridgetower
    resource: ../raw/2206.08657_BridgeTower.md
    title: Building Bridges Between Encoders in Vision-Language Representation Learning
  - id: yang-2022-chinese-clip
    resource: ../raw/2211.01335_Chinese-CLIP.md
    title: "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese"
  - id: chen-2022-altclip
    resource: ../raw/2211.06679_AltCLIP.md
    title: "AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities"
  - id: zhai-2023-siglip
    resource: ../raw/2303.15343_SigLIP.md
    title: Sigmoid Loss for Language Image Pre-Training
  - id: li-2025-meta-clip-2
    resource: ../raw/2507.22062_MetaCLIP2.md
    title: "Meta CLIP 2: A Worldwide Scaling Recipe"
---

# CLIP natural-language image pre-training

CLIP (Contrastive Language–Image Pre-training) jointly trains image and text encoders to match paired images and natural-language text. At inference, class descriptions embedded by the text encoder provide the weights of a zero-shot linear image classifier, making the output vocabulary configurable through language rather than a fixed training label set.[^radford-2021-clip]

## Method

- The authors trained from scratch on WIT, a 400-million image–text-pair dataset collected from public internet sources. Dataset construction sought broad visual-concept coverage using a 500,000-query list and capped results per query; the paper does not release WIT itself.[^radford-2021-clip]
- For a batch of $N$ paired examples, separate image and text encoders project L2-normalized features into a shared embedding space. A learned temperature scales the $N \times N$ pairwise cosine-similarity matrix, and symmetric image-to-text and text-to-image cross-entropy losses make matched pairs more similar than in-batch mismatches.[^radford-2021-clip]
- The paper evaluates modified ResNets and Vision Transformers as image encoders and a causal text Transformer. Its largest reported model, ViT-L/14@336px, was pre-trained for 32 epochs plus one higher-resolution epoch.[^radford-2021-clip]

## Zero-shot transfer and prompting

- To classify an image, CLIP compares its embedding with embeddings of candidate class texts and selects the highest-similarity text. This yields a multinomial logistic-regression classifier with normalized features and weights, no bias, and temperature scaling.[^radford-2021-clip]
- Context changes performance: the default template “A photo of a {label}.” improved ImageNet accuracy over bare labels, while task-specific templates and averaging text embeddings from multiple prompts improved it further. The paper reports that prompt engineering and ensembling improved ImageNet zero-shot accuracy by nearly five points over contextless class names.[^radford-2021-clip]
- The best model reported 76.2% ImageNet top-1 zero-shot accuracy, matching the original supervised ResNet-50 benchmark cited by the authors. Across 27 datasets, its zero-shot classifier exceeded a supervised linear classifier on ResNet-50 features on 16 datasets; these evaluations are evidence from the paper’s selected benchmark suite, not a universal capability claim.[^radford-2021-clip]

## Findings and limits

- Average zero-shot error followed a smooth log–log trend across a 44-fold span of model compute, but individual task results were noisier. The authors also reported stronger natural-distribution-shift robustness for zero-shot CLIP than comparable ImageNet-trained models; adapting CLIP features to ImageNet improved in-distribution accuracy while slightly reducing average shift accuracy.[^radford-2021-clip]
- Zero-shot performance was weak on some specialized, abstract, or underrepresented tasks, including several fine-grained classifications, satellite imagery, counting, traffic signs, and distance estimation. It also generalized poorly to handwritten MNIST digits, which the authors attributed to their absence from pre-training-like data.[^radford-2021-clip]
- The paper’s overlap analysis detected a median 2.2% evaluation-set overlap across 35 datasets and reported that detected overlap rarely shifted overall accuracy by more than 0.1%; imperfect duplicate detection and distribution differences between overlap and clean subsets limit that estimate.[^radford-2021-clip]

## Risks and governance

The authors report that unfiltered internet image–text data can transmit social biases. Their exploratory probes found that classifications can vary materially with the supplied label set, wording, and thresholds, including denigrating and gendered associations. They also identify zero-shot identity recognition and bespoke surveillance classification as socially sensitive capabilities; reported results are characterization exercises, not evidence that these applications are appropriate or safe to deploy.[^radford-2021-clip]

## Relationships

- Used by: [BridgeTower layer-wise vision–language fusion](bridgetower-layerwise-vision-language-fusion.md) uses CLIP visual encoders in its reported configurations, but applies deep cross-modal fusion rather than CLIP's dual-encoder similarity scoring.[^xu-2022-bridgetower]
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) independently documents a dual-encoder, contrastive image–text approach at a larger scale with lightly filtered alt-text.
- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) retains the contrastive dual-encoder interface but freezes a pretrained image tower rather than jointly training both towers from scratch.
- Extended by: [Chinese CLIP language-specific vision–language pre-training](chinese-clip-language-specific-vision-language-pretraining.md) initializes a Chinese text encoder alongside a CLIP vision tower, then unlocks both towers for Chinese-domain adaptation.[^yang-2022-chinese-clip]
- Extended by: [AltCLIP multilingual text-encoder alignment](altclip-multilingual-text-encoder-alignment.md) retains CLIP's image encoder, but distills an XLM-R text encoder from CLIP before contrastive text-only tuning for bilingual or multilingual support.[^chen-2022-altclip]
- Extended by: [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) replaces CLIP's symmetric global-softmax objective with independently scored sigmoid-loss terms for every image–text pair.[^zhai-2023-siglip]
- Extended by: [Meta CLIP 2 worldwide CLIP scaling](meta-clip-2-worldwide-clip-scaling.md) retains the CLIP-style dual-encoder setting while scaling metadata, curation, tokenization, training exposure, and capacity for native-language worldwide image–text data.[^li-2025-meta-clip-2]

[^radford-2021-clip]: Radford et al., “Learning Transferable Visual Models From Natural Language Supervision” (2021), [source](../raw/2103.00020_CLIP.md).

[^xu-2022-bridgetower]: Xu et al., “Building Bridges Between Encoders in Vision-Language Representation Learning” (2022), [source](../raw/2206.08657_BridgeTower.md).

[^yang-2022-chinese-clip]: Yang et al., “Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese” (2022), [source](../raw/2211.01335_Chinese-CLIP.md).

[^chen-2022-altclip]: Chen et al., “AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities” (2022), [source](../raw/2211.06679_AltCLIP.md).

[^zhai-2023-siglip]: Zhai et al., “Sigmoid Loss for Language Image Pre-Training” (2023), [source](../raw/2303.15343_SigLIP.md).

[^li-2025-meta-clip-2]: Li et al., “Meta CLIP 2: A Worldwide Scaling Recipe” (2025), [source](../raw/2507.22062_MetaCLIP2.md).
