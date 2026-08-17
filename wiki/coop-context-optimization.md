---
type: Concept
title: CoOp context optimization
description: A parameter-efficient CLIP adaptation method that learns continuous prompt-context vectors from few labeled examples while freezing the pretrained model.
tags: [multimodal-learning, prompt-learning, few-shot-learning, transfer-learning, efficient-adaptation]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:00:00Z }
sources:
  - id: zhou-2021-coop
    resource: ../raw/2109.01134_CoOp/main.tex
    title: Learning to Prompt for Vision-Language Models
  - id: wortsman-2021-wise-ft
    resource: ../raw/2109.01903_WiSE-FT/main.tex
    title: Robust fine-tuning of zero-shot models
  - id: zhou-2022-cocoop
    resource: ../raw/2203.05557_CoCoOp/arxiv.tex
    title: Conditional Prompt Learning for Vision-Language Models
  - id: zhang-2022-tip-adapter
    resource: ../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex
    title: "Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling"
  - id: khattak-2023-maple
    resource: ../raw/2210.03117_MaPLe/PaperForReview.tex
    title: "MaPLe: Multi-modal Prompt Learning"
  - id: wu-2024-caspl
    resource: ../raw/2409.17805_CasPL/main.tex
    title: Cascade Prompt Learning for Vision-Language Model Adaptation
---

# CoOp context optimization

Context Optimization (CoOp) replaces hand-written CLIP prompt context with a small set of learned continuous vectors while freezing the image encoder, text encoder, and other pretrained parameters. The learned vectors form class-text-conditioned zero-shot classifier weights, making CLIP adaptation a few-shot prompt-learning problem rather than a full-model fine-tuning problem.[^zhou-2021-coop]

## Method

- For each class, CoOp inserts $M$ learnable vectors with CLIP word-embedding dimensionality around the class-name tokens. The text encoder embeds the resulting sequence, and its end-of-text representation becomes that class's classifier weight; prediction retains CLIP's cosine-similarity softmax and learned temperature.[^zhou-2021-coop]
- Unified context shares one set of $M$ vectors across all classes. Class-specific context (CSC) instead learns a separate set for every class, increasing its parameter count; the class name may appear after the context or in its middle.[^zhou-2021-coop]
- Training minimizes classification cross-entropy over the labeled examples, back-propagating through the frozen text encoder only to update the context vectors. The reported default uses 16 randomly initialized context vectors and a frozen ResNet-50 CLIP backbone.[^zhou-2021-coop]

## Reported findings

- On 11 image-classification datasets with 1, 2, 4, 8, or 16 labeled examples per class, the paper reports that CoOp exceeded its hand-crafted-prompt baseline on average from two shots and gained about 15 percentage points at 16 shots. The largest reported 16-shot gains were on EuroSAT (over 45 points) and DTD (over 20 points); these are results for the paper's datasets and protocols, not a general few-shot guarantee.[^zhou-2021-coop]
- In the reported ImageNet comparison across four CLIP image backbones, 16-context-token CoOp outperformed both prompt engineering and the selected prompt ensemble. For example, with ResNet-50 it scored 62.95%, versus 58.18% and 60.41%, respectively.[^zhou-2021-coop]
- CSC was more competitive on several fine-grained or specialized tasks at 16 shots, whereas shared context was generally stronger for generic-object, scene, and action recognition and in lower-shot settings. The source attributes the low-shot CSC weakness to its greater number of learned parameters.[^zhou-2021-coop]
- ImageNet-to-ImageNetV2/Sketch/A/R tests found that CoOp could improve transfer relative to zero-shot CLIP, especially with four rather than 16 context tokens. Outcomes vary by target and backbone, so the experiments do not establish that learned prompts always improve distribution-shift robustness.[^zhou-2021-coop]

## Limits and trade-offs

- More context tokens improved average in-distribution score in the paper's 11-dataset study, while fewer tokens were often more robust under ImageNet distribution shift. Context length is therefore an accuracy--robustness and parameter-count choice, not a universally optimal setting.[^zhou-2021-coop]
- CoOp showed weak or saturating gains on Food101, which the authors associate with noisy labels, and the method remains sensitive to the task distribution used to learn its prompt.[^zhou-2021-coop]
- Continuous context vectors are not reliably interpretable as words: nearest-vocabulary tokens were often incoherent, and the authors caution that proximity in the embedding space need not reveal a vector's semantics.[^zhou-2021-coop]
- The study covers downstream image classification and selected domain shifts. It does not establish behavior for retrieval, generation, or other vision-language tasks.[^zhou-2021-coop]

## Relationships

- Extends: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) by learning prompt context from labeled downstream examples while retaining CLIP's frozen dual encoders and text-derived classifier weights.[^zhou-2021-coop]
- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) also preserves a pretrained visual representation during adaptation, but CoOp freezes both CLIP towers and learns prompt embeddings rather than training a text encoder.[^zhou-2021-coop]
- Extended by: [CoCoOp conditional context optimization](cocoop-conditional-context-optimization.md), which adds an image-conditioned offset to CoOp's static context vectors to improve base-to-new-class generalization at a higher training and memory cost.[^zhou-2022-cocoop]
- Extended by: [MaPLe multimodal prompt learning](maple-multimodal-prompt-learning.md), which makes prompt learning deep and adds vision prompts coupled to language prompts; its deep language prompting reduces to CoOp when prompt depth is one.[^khattak-2023-maple]
- Compared with: [WiSE-FT robust zero-shot fine-tuning](wise-ft-robust-zero-shot-fine-tuning.md) in an ImageNet 16-shot-per-class experiment. WiSE-FT interpolates model weights after fine-tuning, whereas CoOp learns prompt context; their combination was not evaluated.[^wortsman-2021-wise-ft]
- Compared with: [Tip-Adapter cache-based few-shot CLIP adaptation](tip-adapter-cache-based-few-shot-clip-adaptation.md) in few-shot image classification. Tip-Adapter retrieves labeled visual-feature cache entries alongside CLIP logits, whereas CoOp learns continuous prompt context.[^zhang-2022-tip-adapter]
- Extended by: [CasPL cascade prompt learning](caspl-cascade-prompt-learning.md), which first learns frozen multimodal boosting prompts through unlabeled-domain teacher distillation, then cascades them with CoOp's adapting prompts.[^wu-2024-caspl]

[^zhou-2021-coop]: Zhou et al., “Learning to Prompt for Vision-Language Models” (2021), [source manuscript](../raw/2109.01134_CoOp/main.tex). The manuscript’s supporting result figures were visually inspected; the paper source also includes them as `main_results.pdf`, `various_archs_detailed.pdf`, `ctx_len_detailed.pdf`, and `study_ctxlen_visarch.pdf` in the same source directory.

[^wortsman-2021-wise-ft]: Wortsman et al., “Robust fine-tuning of zero-shot models” (2021), [source manuscript](../raw/2109.01903_WiSE-FT/main.tex).

[^zhou-2022-cocoop]: Zhou et al., “Conditional Prompt Learning for Vision-Language Models” (2022), [source manuscript](../raw/2203.05557_CoCoOp/arxiv.tex).

[^zhang-2022-tip-adapter]: Zhang et al., “Tip-Adapter: Training-free CLIP-Adapter for Better Vision-Language Modeling” (2022), [source manuscript](../raw/2111.03930_Tip-Adapter/ReviewTemplate.tex).

[^khattak-2023-maple]: Khattak et al., “MaPLe: Multi-modal Prompt Learning” (2023), [complete source manuscript](../raw/2210.03117_MaPLe/PaperForReview.tex).

[^wu-2024-caspl]: Wu et al., “Cascade Prompt Learning for Vision-Language Model Adaptation” (2024), [complete source manuscript](../raw/2409.17805_CasPL/main.tex).
