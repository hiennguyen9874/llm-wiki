---
type: Concept
title: FILIP fine-grained interactive language–image pre-training
description: A CLIP-style dual encoder that replaces global image–text similarity with directional token-level late interaction for fine-grained patch–word alignment.
tags: [multimodal-learning, contrastive-learning, late-interaction, retrieval, zero-shot-transfer]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:16:37Z }
sources:
  - id: yao-2022-filip
    resource: ../raw/2111.07783_FILIP/filip_arxiv.tex
    title: "FILIP: Fine-grained Interactive Language-Image Pre-Training"
---

# FILIP fine-grained interactive language–image pre-training

FILIP retains separate image and text encoders but replaces CLIP’s single global pair score with cross-modal late interaction: image patches and text tokens are encoded independently, then each token is scored by its maximum similarity to tokens in the other modality. The directional mean-MaxSim scores train symmetric image-to-text and text-to-image contrastive losses, providing patch–word alignment while retaining offline encoding of each modality.[^yao-2022-filip]

## Method

- A Vision Transformer image encoder and a GPT-like causal text Transformer produce token-level features, which are linearly projected to a shared space and L2-normalized. The image sequence includes a CLS token; text uses a 49,408-item lowercase BPE vocabulary with BOS and EOS tokens.[^yao-2022-filip]
- For image-to-text scoring, every non-padded image token takes its largest dot product with a token in the candidate text, then FILIP averages those maxima. Text-to-image scoring reverses this operation: each non-padded text token selects its highest-scoring image token before averaging. These directional scores substitute for the global similarity in CLIP-style symmetric in-batch contrastive loss.[^yao-2022-filip]
- The method is inspired by ColBERT late interaction but excludes padded text tokens and averages rather than sums token maxima. The authors attribute those changes to avoiding meaningless padding matches and to stabilizing scores across variable text lengths; this is the paper’s experimental design rationale, not a general proof.[^yao-2022-filip]
- To control late-interaction cost in distributed training, the reported recipe uses 256-dimensional projected features, communicates final-layer features in fp16, and retains the top 25% of tokens by maximum-similarity score before cross-worker communication. In its ViT-B/32 YFCC100M study, that configuration used 1.39 seconds per iteration and 16.1 GB versus 1.31 seconds and 14.3 GB for the global-similarity baseline, with 34.3% versus 30.4% ImageNet zero-shot top-1.[^yao-2022-filip]
- Pre-training applies AutoAugment to images and samples either the original English text or a German- or Russian-back-translated version. The reported FILIP340M mix comprises FILIP300M plus filtered YFCC100M, CC12M, and CC3M pairs; it totals about 340 million pairs after filtering.[^yao-2022-filip]

## Reported findings and limits

- On 12 zero-shot classification datasets, the paper reports a 70.9% average top-1 score for FILIP base (ViT-B/32) versus 65.3% for its cited CLIP counterpart, and 78.3% for FILIP large (ViT-L/14) versus 75.3%. ImageNet scores were 68.8% versus 63.2% and 77.1% versus 75.3%, respectively. These are the manuscript’s comparisons and vary both the data recipe and objective; they do not isolate the late-interaction loss.[^yao-2022-filip]
- In an ablation on filtered YFCC100M with ViT-B/32, adding late interaction after image and back-translation augmentation increased MSCOCO zero-shot R@1 from 29.2% to 30.5% for image-to-text and from 17.9% to 18.5% for text-to-image, and ImageNet zero-shot top-1 from 33.9% to 34.3%. Combining all reported components reached 33.4%, 23.0%, and 37.8%, respectively.[^yao-2022-filip]
- The paper visualizes patch tokens selecting class-name tokens and interprets the patterns as localization-like alignment. These visualizations support qualitative correspondence for the selected ImageNet examples, not detection or segmentation performance.[^yao-2022-filip]
- The reported pre-training corpus is English-only after filtering and is assembled from internet data plus public datasets. The manuscript does not establish performance or bias characteristics outside its reported evaluation suite, nor does it evaluate generative tasks; captioning extensions appear only as future work.[^yao-2022-filip]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by retaining independently encoded image and text towers with symmetric contrastive training, but replacing global embedding similarity with token-level directional late interaction.[^yao-2022-filip]

[^yao-2022-filip]: Yao et al., “FILIP: Fine-grained Interactive Language-Image Pre-Training” (2022), [complete source manuscript](../raw/2111.07783_FILIP/filip_arxiv.tex).
