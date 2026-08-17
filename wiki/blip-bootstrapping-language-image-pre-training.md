---
type: Concept
title: BLIP bootstrapping language–image pre-training
description: A unified vision–language pre-training framework that combines multimodal encoder–decoder modes with caption generation and filtering to improve noisy web image–text data.
tags: [vision-language-pretraining, multimodal-learning, data-curation, image-captioning, image-text-retrieval]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:43:14Z }
sources:
  - id: li-2022-blip
    resource: ../raw/2201.12086_BLIP/main.tex
    title: "BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation"
  - id: yu-2022-coca
    resource: ../raw/2205.01917_CoCa/main.tex
    title: "CoCa: Contrastive Captioners are Image-Text Foundation Models"
  - id: li-2023-blip2
    resource: ../raw/2301.12597_BLIP-2/main.tex
    title: "BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models"
---

# BLIP bootstrapping language–image pre-training

BLIP unifies vision–language understanding and text generation in one pre-training framework. Its multimodal mixture of encoder–decoder (MED) shares most text-transformer parameters across contrastive, matching, and image-conditioned language-modeling modes; its Captioning and Filtering (CapFilt) pipeline generates diverse synthetic captions and discards image–text mismatches before training a new model on the bootstrapped corpus.[^li-2022-blip]

## Architecture and objectives

- A ViT image encoder feeds a text transformer that can act as: a unimodal encoder for image–text contrastive learning (ITC); an image-grounded bidirectional text encoder with inserted cross-attention layers for image–text matching (ITM); or an image-grounded causal text decoder for image-conditioned language modeling (LM).[^li-2022-blip]
- The text encoder and decoder share embedding, cross-attention, and feed-forward parameters, but use separate self-attention layers to avoid conflict between bidirectional encoding and causal next-token prediction. In the paper’s 14M-image ablation, this configuration had 252M parameters and outperformed sharing all layers and fully separate models on the reported retrieval and captioning measures.[^li-2022-blip]
- For retrieval, the paper first ranks candidates using ITC embedding similarity and re-ranks the top candidates with ITM scores. For open-ended VQA, it encodes the image–question pair and uses the decoder to rank or generate answers.[^li-2022-blip]

## CapFilt data bootstrapping

- A captioner, fine-tuned from MED’s image-grounded decoder on COCO with LM, produces one synthetic caption for each web image. A separately fine-tuned image-grounded encoder serves as a filter: its ITM head removes unmatched original and synthetic captions. The filtered results are combined with human-annotated pairs and used to pre-train a new model.[^li-2022-blip]
- On the 14M-image corpus, applying both components improved COCO fine-tuned text-retrieval/image-retrieval R@1 from 78.4/60.7 to 80.6/63.1 and NoCaps zero-shot CIDEr from 102.2 to 105.1 in the paper’s experiment.[^li-2022-blip]
- Nucleus sampling ($p=0.9$) produced a higher filter-reported noise ratio than beam search (25% versus 19%) but better reported downstream scores. The authors attribute this to more diverse captions, so this is experimental evidence for the recipe rather than a general guarantee that noisier captions help.[^li-2022-blip]
- Matching the original corpus’s sample count by replicating web text did not reproduce CapFilt’s gains. Continuing from the initial model also did not improve over training a new model on the bootstrapped corpus in the reported ablation.[^li-2022-blip]

## Reported scope and limits

- BLIP pre-trains on 14M images from COCO, Visual Genome, SBU, CC3M, and CC12M; its larger setting adds 115M LAION images, using one fifth of that dataset per epoch. The paper initializes the image transformer from ImageNet-pretrained ViT and the text transformer from BERT-base.[^li-2022-blip]
- The paper reports strong results on its selected retrieval, captioning, VQA, NLVR2, VisDial, and zero-shot video benchmarks. Its video transfer concatenates uniformly sampled frame features and explicitly ignores temporal information; those results do not establish temporal video understanding.[^li-2022-blip]
- CapFilt’s filter is fine-tuned on COCO. The paper does not evaluate whether the pipeline removes biased or unsafe web data, so its results do not establish reliable removal of those properties.[^li-2022-blip]

## Relationships

- Related: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) uses global contrastive image–text alignment, whereas BLIP retains an ITC mode and adds image-grounded matching and generation modes for tasks beyond dual-encoder retrieval.[^li-2022-blip]
- Related: [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) finds that web-scale lightly filtered alt-text can be useful, while BLIP investigates improving noisy web text through generated captions and matching-based filtering.[^li-2022-blip]
- Related: [FLAVA foundational language and vision alignment](flava-foundational-language-vision-alignment.md) also combines contrastive and matching objectives with cross-modal representations, but BLIP shares parameters between encoder and decoder modes and trains image-conditioned language modeling for generation.[^li-2022-blip]

- Related: [CoCa contrastive captioner image–text foundation model](coca-contrastive-captioner-image-text-foundation-model.md) also unifies image–text alignment and generation, but uses a cross-attention-decoupled causal decoder trained jointly from scratch rather than BLIP’s encoder/decoder modes and caption-and-filter bootstrapping.[^yu-2022-coca]
- Extended by: [BLIP-2 bootstrapping frozen vision–language models](blip-2-bootstrapping-frozen-vision-language-models.md) retains BLIP’s ITC, ITM, and ITG objectives and its 129M-image CapFilt-derived corpus, but uses Q-Former to connect frozen pretrained image and language backbones.[^li-2023-blip2]

## Evidence scope

Claims were compiled from the manuscript’s section, appendix, table, and figure-caption TeX sources. The embedded figure PDFs were not visually inspected; no claims depend on visual details absent from their captions.[^li-2022-blip]

[^li-2022-blip]: Li et al., “BLIP: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation” (2022), [complete manuscript source](../raw/2201.12086_BLIP/main.tex).

[^yu-2022-coca]: Yu et al., “CoCa: Contrastive Captioners are Image-Text Foundation Models” (2022), [complete manuscript source](../raw/2205.01917_CoCa/main.tex).

[^li-2023-blip2]: Li et al., “BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models” (2023), [complete manuscript source](../raw/2301.12597_BLIP-2/main.tex).