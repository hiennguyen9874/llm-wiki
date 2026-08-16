---
type: Concept
title: AltCLIP multilingual text-encoder alignment
description: A two-stage method that replaces CLIP's text encoder with XLM-R, distills its aligned text space from CLIP, then contrastively tunes the text tower against a frozen CLIP image encoder.
tags: [multimodal-learning, multilingual, contrastive-learning, knowledge-distillation, transfer-learning, zero-shot-transfer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:37:55Z }
sources:
  - id: chen-2022-altclip
    resource: ../raw/2211.06679_AltCLIP.md
    title: "AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities"
---

# AltCLIP multilingual text-encoder alignment

AltCLIP makes CLIP bilingual or multilingual by replacing its text encoder with multilingual XLM-R, first distilling CLIP's text–image-aligned embeddings using parallel text and then contrastively tuning the new text encoder on image–text pairs while the CLIP image encoder remains frozen. The authors report near-CLIP English results and strong Chinese and nine-language benchmark results, but these are evaluations under their specified data and prompts rather than general guarantees.[^chen-2022-altclip]

## Method

- A projection maps the XLM-R-Large student encoder's `[CLS]` output to the CLIP ViT-L/14 teacher text-embedding dimension. In the teacher-learning stage, mean squared error matches the student embedding for a translated or parallel sentence to the frozen CLIP teacher embedding for its English counterpart; the teacher is discarded at inference.[^chen-2022-altclip]
- Teacher learning includes English–English pairs, machine-translated English–Chinese captions from CC3M and a 28M LAION-400M subset, and 5M human English–Chinese translations from TSL2019. The multilingual M9 variant applies the same approach to English, Chinese, Spanish, French, Russian, Arabic, Japanese, Korean, and Italian.[^chen-2022-altclip]
- In stage two, AltCLIP applies the usual image–text contrastive loss to the learned text encoder and CLIP's ViT image encoder, but freezes the image encoder following LiT. The bilingual model uses 2M filtered Chinese and English image–text pairs; the multilingual model uses 100M multilingual pairs.[^chen-2022-altclip]

## Reported evidence and limits

- On the paper's ViT-L comparisons, the final bilingual model reports ImageNet top-1 accuracy of 74.5% in English and 59.6% with Chinese labels, compared with 75.5% and 1.9% for CLIP, respectively. Its reported Flickr30K mean recall is 90.4% (English) and 89.2% (Chinese).[^chen-2022-altclip]
- The M9 model reports the highest image-to-text Recall@10 among the table's baselines for seven of eight reported XTD languages; it excludes German, Polish, and Turkish even though XTD contains captions in eleven languages.[^chen-2022-altclip]
- The authors' ablation attributes English classification retention to including English–English teacher pairs, Chinese performance to English–Chinese pairs, and further Chinese ImageNet improvement to human translations. These are empirical results in their ten-epoch ablation, not evidence that each data choice transfers unchanged to other encoders or datasets.[^chen-2022-altclip]
- The source's text-to-image extension (AltDiffusion) replaces Stable Diffusion's language encoder and tunes only cross-attention key/value projections. It presents qualitative multilingual examples, so it does not establish quantitative image-generation quality or safety.[^chen-2022-altclip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) provides both the frozen teacher text encoder and the ViT image encoder that AltCLIP retains.[^chen-2022-altclip]
- Uses: [LiT locked-image tuning](lit-locked-image-tuning.md) motivates freezing the CLIP image encoder during contrastive tuning, while AltCLIP additionally uses an embedding-distillation stage.[^chen-2022-altclip]
- Related: [Chinese CLIP language-specific vision–language pre-training](chinese-clip-language-specific-vision-language-pretraining.md) also adapts CLIP to Chinese, but it contrastively aligns and then jointly unfreezes both towers instead of distilling a multilingual text encoder and keeping the image tower locked.[^chen-2022-altclip]

[^chen-2022-altclip]: Chen et al., “AltCLIP: Altering the Language Encoder in CLIP for Extended Language Capabilities” (2022), [source](../raw/2211.06679_AltCLIP.md).
