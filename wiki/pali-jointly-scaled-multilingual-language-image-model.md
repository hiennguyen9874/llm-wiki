---
type: Concept
title: PaLI jointly scaled multilingual language-image model
description: A 17B multilingual encoder-decoder vision-language model that reuses mT5 and ViT backbones and casts image, language, and image-text tasks as prompted text generation.
tags: [multimodal-learning, vision-language-pretraining, multilingual, image-captioning, visual-question-answering, generative-modeling, scaling]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:30:46Z }
sources:
  - id: chen-2022-pali
    resource: ../raw/2209.06794_PaLI/main.tex
    title: "PaLI: A Jointly-Scaled Multilingual Language-Image Model"
---

# PaLI jointly scaled multilingual language-image model

PaLI (Pathways Language and Image model) is a multilingual, sequence-to-sequence vision-language model that receives an image and a text prompt and generates text. It initializes an mT5 encoder-decoder and a Vision Transformer (ViT), then uses the same prompted interface for image-only, language-only, and image-plus-language tasks.[^chen-2022-pali]

## Architecture and training

- ViT patch features are supplied as visual tokens to the mT5-style encoder; the decoder autoregressively generates text. Prompt templates identify tasks, so the reported model has no task-specific heads.[^chen-2022-pali]
- The reported variants are PaLI-3B (1.2B mT5-L plus 1.8B ViT-G), PaLI-15B (13B mT5-XXL plus 1.8B ViT-G), and PaLI-17B (13B mT5-XXL plus 3.9B ViT-e). ViT-e is a 56-layer, 3.926B-parameter ViT; the authors pretrain it on JFT-3B and average two late-stage training runs.[^chen-2022-pali]
- PaLI pretrains on a 1.6B-example mixture: text span corruption; WebLI split-captioning and OCR; translated CC3M captioning; translated VQ$^2$A-CC3M VQA and visual-question generation; object-aware VQA; and generative detection. Its initial 224px phase freezes the vision component; the reported 17B model then receives a 10k-step, 588px phase with all parameters trainable.[^chen-2022-pali]
- In the paper's controlled 3B ablation, initializing from mT5-Large and ViT-G, rather than training from scratch, improved COCO CIDEr from 72.8 to 141.4 and TextVQA from 12.8 to 41.6. Briefly freezing, rather than tuning, the ViT during pretraining also slightly improved the reported 224px COCO scores for its 3B and 15B configurations; these are configuration-specific findings, not universal rules.[^chen-2022-pali]

## Data and multilingual capabilities

- WebLI is a private web-derived corpus of 9.624B image-text instances (about 260 TB) collected in 2021-2022. It includes image pixels, alt-text, page titles, OCR, and page metadata; the paper describes 12B alt-texts across 109 languages and 29B image-OCR pairs. PaLI retains the top-scoring 10% of original image-alt-text pairs (about 1B) for training and applies image near-deduplication against 68 vision and vision-language datasets.[^chen-2022-pali]
- The data card says collection is from public web pages, OCR and language identification use public automatic services, and automated filters remove detected adult content and text identified as PII. It also states that the corpus remains noisy and potentially redundant, may contain offensive material, is not distributed to third parties, and is not a complete representation of the public web.[^chen-2022-pali]
- In a 1.5B ablation, adding non-English WebLI to the full mixture improved the reported Crossmodal-3600 six-non-English-language average from 39.0 to 41.9 CIDEr and xGQA eight-language average from 40.9 to 41.3; it also improved English COCO CIDEr from 135.3 to 135.4. The authors report much larger multilingual-captioning differences when comparing WebLI-only English and all-language configurations. These results support multilingual data exposure under the tested mixtures, not equal quality across languages.[^chen-2022-pali]

## Reported evaluation and limits

- On the paper's protocols, PaLI-17B reported 149.1 COCO Karpathy-test CIDEr, 84.3 VQAv2 test-standard accuracy, and 72.11% zero-shot ImageNet top-1. Its VQA results use open-vocabulary generation with mT5's 250k-token vocabulary; the cited competing closed-vocabulary results are therefore not identical task formulations.[^chen-2022-pali]
- The paper attributes substantial seven-task gains to both language and vision scaling: replacing mT5-L with mT5-XXL at ViT-G adds 12B parameters and +3.1 average points, while replacing ViT-G with ViT-e at mT5-XXL adds 2B parameters and +6.3; the 588px phase adds another +2.0. These are the authors' selected seven-task score-difference aggregate, not a general return-on-investment estimate.[^chen-2022-pali]
- PaLI-17B reported a 53.6 35-language-average CIDEr on Crossmodal-3600 after COCO-35L fine-tuning, and exact-match scores above the cited baseline on xGQA and MaXM. The paper notes that cross-language CIDEr is not directly comparable across linguistic structures; its back-translation check covers only a 600-example subset in six non-English languages.[^chen-2022-pali]
- OCR-dependent captioning and VQA experiments receive OCR strings from an external automatic service. Without those strings, PaLI-17B's reported TextCaps/TextVQA scores fell from 160.4/73.06 to 135.4/58.80, so the stronger OCR-task results do not isolate end-to-end visual text recognition.[^chen-2022-pali]
- The authors caution that web-derived training data can transmit bias, stereotypes, and harmful or inaccurate content; language quality varies with data coverage, English-only fine-tuning can reduce multilingual capability, and exact-match generative evaluation can score semantically correct paraphrases as wrong. The model card describes PaLI as a research prototype that was not publicly available at publication.[^chen-2022-pali]

## Relationships

- Evaluates with: [LiT locked-image tuning](lit-locked-image-tuning.md). The paper applies LiT to its frozen ViT-e visual component, tuning a text encoder on English or multilingual WebLI and evaluating zero-shot classification and Crossmodal-3600 retrieval.[^chen-2022-pali]
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md). PaLI describes WebLI collection as similar to ALIGN and performs near-deduplication against downstream evaluation data, but PaLI is an encoder-decoder text generator rather than ALIGN's contrastive dual encoder.[^chen-2022-pali]
- Related: [CoCa contrastive captioner image–text foundation model](coca-contrastive-captioner-image-text-foundation-model.md). Both report large image-text models with captioning and VQA transfer, but PaLI reuses pretrained unimodal backbones and uses prompted generative objectives rather than CoCa's joint contrastive-and-captioning objective.[^chen-2022-pali]

## Evidence scope

Claims were compiled from the complete manuscript, appendix, model card, and data card. All eight supplied figure PDFs were rendered and visually inspected; they corroborate the prompted encoder-decoder architecture, WebLI composition, scaling, multilingual captioning and retrieval, sample outputs, and the reported sampled age distribution. Macro, bibliography, style, and generated bibliography files were not independently reviewed because no retained claim depends on them.[^chen-2022-pali]

[^chen-2022-pali]: Chen et al., “PaLI: A Jointly-Scaled Multilingual Language-Image Model” (2022), [complete manuscript source](../raw/2209.06794_PaLI/main.tex), including its [appendix](../raw/2209.06794_PaLI/appendix.tex), [model card](../raw/2209.06794_PaLI/model_card.tex), and [data card](../raw/2209.06794_PaLI/data_card.tex).
