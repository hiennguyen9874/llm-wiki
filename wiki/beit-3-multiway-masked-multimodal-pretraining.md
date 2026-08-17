---
type: Concept
title: BEiT-3 multiway masked multimodal pretraining
description: A 1.9B-parameter Multiway Transformer that unifies masked prediction over images, text, and image-text pairs through shared attention and modality-specific feed-forward experts.
tags: [multimodal-learning, vision-language-pretraining, masked-modeling, cross-modal-fusion, transformer, representation-learning]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:28:57Z }
sources:
  - id: wang-2022-beit-3
    resource: ../raw/2208.10442_BEiT-3/main.tex
    title: "Image as a Foreign Language: BEiT Pretraining for All Vision and Vision-Language Tasks"
---

# BEiT-3 multiway masked multimodal pretraining

BEiT-3 treats images as a second, tokenized language and uses one masked-data-modeling objective for image-only, text-only, and paired image-text inputs. Its Multiway Transformer shares self-attention across modalities while routing tokens to modality-specific feed-forward experts, allowing the same backbone to serve unimodal encoders, fusion encoders, dual encoders, and conditional generation.[^wang-2022-beit-3]

## Architecture and objective

- Every block shares multi-head self-attention but routes tokens to vision or language feed-forward experts; the top three layers also provide vision-language experts for fused inputs. This separates modality-specific feed-forward computation from the shared attention intended to learn cross-modal alignment.[^wang-2022-beit-3]
- For pretraining, it predicts masked discrete tokens: 15% of tokens in text-only data, 50% of text tokens in paired data, and 40% of image patches with block-wise masking. Text uses a 64K-vocabulary SentencePiece tokenizer; image reconstruction targets use the BEiT v2 visual tokenizer.[^wang-2022-beit-3]
- The reported giant model has 40 layers, 1,408 hidden dimensions, 16 attention heads, and 1.9B total parameters. It combines 692M-parameter vision and language expert pools, 52M vision-language experts, and 317M shared-attention parameters; vision-only transfer activates about 1B parameters.[^wang-2022-beit-3]

## Training and transfer

- The reported pretraining corpus comprises 21M public image-text pairs from CC12M, CC3M, SBU, COCO, and Visual Genome; 14M ImageNet-21K images; and 160GB of English text from Wikipedia, BookCorpus, OpenWebText, CC-News, and Stories. Training runs for 1M steps with 6,144 examples per batch, equally divided among image, text, and paired inputs.[^wang-2022-beit-3]
- With task-specific attention masks and heads, the shared backbone is used as an image encoder for classification and dense prediction, a fusion encoder for VQA and NLVR2, separate image and text encoders for retrieval, and a conditional sequence model for caption generation.[^wang-2022-beit-3]
- Although the pretraining objective has no image-text contrastive term, the paper reports retrieval after an optional five-epoch intermediate contrastive fine-tuning stage on the pretraining pairs. That stage improves the reported COCO image-to-text/text-to-image R@1 from 82.7/65.1 to 84.8/67.2, so those improved retrieval results are not evidence for masked pretraining alone.[^wang-2022-beit-3]

## Reported evaluation and limits

- On the paper's selected protocols, the model reports 84.03 VQAv2 test-standard accuracy, 92.58 NLVR2 public-test accuracy, 147.6 COCO Karpathy-split CIDEr without CIDEr optimization, and 89.6% ImageNet-1K top-1 after ImageNet-21K intermediate fine-tuning. It also reports 63.7 COCO box AP, 54.8 mask AP, and 62.8 ADE20K multi-scale mIoU after task-specific fine-tuning.[^wang-2022-beit-3]
- The reported benchmark values depend on a 2022 comparison set, specified intermediate fine-tuning, task heads, and evaluation protocols; they do not establish current state of the art or general-purpose reliability. The paper's public-source description establishes academic accessibility as reported by the authors, not that every dataset is independently reproducible or free of web-data bias.[^wang-2022-beit-3]

## Relationships

- Related: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) learns aligned dual-encoder representations through image-text contrastive loss, whereas BEiT-3 pretrains with masked token recovery and adds a fusion-encoder mode; BEiT-3 uses contrastive learning only in its optional retrieval intermediate fine-tuning.[^wang-2022-beit-3]

## Evidence scope

Claims were compiled from the complete manuscript source, including its appendix and result tables. All four supplied figures were rendered and visually inspected; they corroborate the shared-attention/modality-expert architecture and transfer layouts. The included bibliography and TeX style or macro files were not independently compiled because no retained claim depends on them.[^wang-2022-beit-3]

[^wang-2022-beit-3]: Wang et al., “Image as a Foreign Language: BEiT Pretraining for All Vision and Vision-Language Tasks” (2022), [complete manuscript source](../raw/2208.10442_BEiT-3/main.tex).
