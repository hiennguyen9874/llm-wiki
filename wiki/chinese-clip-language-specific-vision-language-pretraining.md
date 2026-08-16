---
type: Concept
title: Chinese CLIP language-specific vision–language pre-training
description: A Chinese CLIP adaptation that aligns a Chinese text encoder to a locked pretrained vision encoder before jointly tuning both towers on Chinese image–text pairs.
tags: [multimodal-learning, contrastive-learning, transfer-learning, chinese-language, retrieval, zero-shot-transfer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:37:55Z }
sources:
  - id: yang-2022-chinese-clip
    resource: ../raw/2211.01335_Chinese-CLIP.md
    title: "Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese"
  - id: chen-2022-altclip
    resource: ../raw/2211.06679_AltCLIP.md
    title: "AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities"
---

# Chinese CLIP language-specific vision–language pre-training

Chinese CLIP transfers a CLIP-style dual encoder to Chinese through two contrastive-pretraining stages: locked-image tuning first aligns a Chinese text encoder to a pretrained vision encoder, then joint tuning adapts both encoders to Chinese image–text data. The authors report that this initialization-and-unlocking sequence outperforms either from-scratch training or direct joint tuning in their evaluated settings, particularly on translated Chinese retrieval data.[^yang-2022-chinese-clip]

## Method

- The image tower is initialized from OpenAI CLIP (or LAION CLIP for ViT-H/14), while the text tower is initialized from Chinese RoBERTa variants; the architecture retains CLIP's contrastive two-tower interface.[^yang-2022-chinese-clip]
- **Stage 1:** freeze the image encoder and train only the text encoder with contrastive loss, applying the LiT idea to teach the Chinese text tower to read out the pretrained visual representation.[^yang-2022-chinese-clip]
- **Stage 2:** unfreeze both towers and continue contrastive pre-training so the vision tower can adapt to images from Chinese-language domains. The source reports a performance jump when switching stages in its ablation, while noting that direct joint tuning was nearly as good on the Chinese-native MUGE dataset.[^yang-2022-chinese-clip]
- The released family spans five models from 77M (ResNet-50 plus RBT3) to 958M parameters (ViT-H/14 plus RoBERTa-wwm-Large).[^yang-2022-chinese-clip]

## Data and reproducibility boundary

- The authors describe roughly 200M pre-training pairs: about 108M recoverable Chinese LAION-5B samples, 72M recoverable Wukong samples, and translated Visual Genome and MSCOCO training data. They filter LAION samples by mCLIP score, blacklist, and caption length; inaccessible URLs already reduced the obtainable source sets.[^yang-2022-chinese-clip]
- A footnote says the corpus also includes about 20M high-quality internal pairs. Thus the paper's model and reported results are not fully reproducible solely from the named public datasets, despite its stated focus on public data.[^yang-2022-chinese-clip]

## Reported evidence and limits

- The paper reports state-of-the-art zero-shot and fine-tuned retrieval results on MUGE, Flickr30K-CN, and COCO-CN across its comparisons. MUGE is Chinese-native e-commerce data, whereas Flickr30K-CN and COCO-CN use translated captions; these are benchmark-specific author reports, not a general cross-lingual guarantee.[^yang-2022-chinese-clip]
- The source flags a contamination caveat: translated COCO is included in pre-training, so its COCO-CN zero-shot results are not a clean held-out evaluation.[^yang-2022-chinese-clip]
- Zero-shot classification requires translated Chinese class names and prompts. Results are sensitive to prompt wording and translations of proper names; in the reported tests, replacing an "other" label with a negated label substantially reduced accuracy, consistent with weak negation handling.[^yang-2022-chinese-clip]
- The authors report that ONNX and TensorRT conversions on a T4 GPU made inference roughly 2–10× faster than PyTorch, with MUGE mean-recall differences no greater than 0.1 for the converted models.[^yang-2022-chinese-clip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) supplies the dual-encoder contrastive architecture and initializes Chinese CLIP's visual tower.[^yang-2022-chinese-clip]
- Uses: [LiT locked-image tuning](lit-locked-image-tuning.md) supplies the first, locked-image stage; Chinese CLIP adds a second joint-tuning stage to adapt the visual encoder to Chinese-domain imagery.[^yang-2022-chinese-clip]
- Related: [AltCLIP multilingual text-encoder alignment](altclip-multilingual-text-encoder-alignment.md) also adapts CLIP to Chinese; unlike Chinese CLIP, it distills an XLM-R text encoder with parallel text and leaves the image encoder frozen during contrastive tuning.[^chen-2022-altclip]

[^yang-2022-chinese-clip]: Yang et al., “Chinese CLIP: Contrastive Vision-Language Pretraining in Chinese” (2022), [source](../raw/2211.01335_Chinese-CLIP.md).

[^chen-2022-altclip]: Chen et al., “AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities” (2022), [source](../raw/2211.06679_AltCLIP.md).
