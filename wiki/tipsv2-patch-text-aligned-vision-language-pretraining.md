---
type: Concept
title: TIPSv2 patch–text aligned vision–language pretraining
description: A vision–language encoder recipe that combines contrastive image–text learning with all-token masked-image distillation, head-only EMA, and mixed-granularity captions to improve dense patch–text alignment.
tags: [multimodal-learning, vision-language-models, representation-learning, dense-prediction, self-supervised-learning, knowledge-distillation]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:52:12Z }
sources:
  - id: cao-2026-tipsv2
    resource: ../raw/2604.12012_TIPSv2.md
    title: "TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment"
---

# TIPSv2 patch–text aligned vision–language pretraining

TIPSv2 is a vision–language encoder recipe intended to improve dense alignment between image-patch and text embeddings while retaining global image–text capabilities. It combines a contrastive image–text loss with global self-distillation and iBOT++, a masked-image objective that matches teacher representations for both masked and visible patches; the authors report strong results across their selected nine-task, 20-dataset evaluation suite.[^cao-2026-tipsv2]

## Training recipe

- iBOT++ changes iBOT's patch loss from supervising only masked patches to supervising every patch, while the student still receives a masked image and the teacher receives the unmasked image. The authors attribute their reported dense-alignment improvement to anchoring visible student patches to teacher representations.[^cao-2026-tipsv2]
- The paper retains a 75% masking ratio for iBOT++ pretraining. Its ablation reports that eliminating masking helps during their distillation procedure but performs poorly during iBOT++ pretraining, so the two settings should not be conflated.[^cao-2026-tipsv2]
- Rather than keep an EMA copy of the vision encoder and projection head, head-only EMA shares the student vision encoder with the teacher and applies EMA only to the projection head. The authors argue that the contrastive loss constrains encoder collapse, and report a 42% reduction in training parameters for ViT-B versus full EMA; fully removing EMA caused instability in their preliminary experiments.[^cao-2026-tipsv2]
- The model uses dual CLS embeddings and mixed caption granularity: web alt-text and synthetic captions, with PaliGemma and Gemini captions sampled for the synthetic-caption signal. The paper reports that detailed Gemini captions alone underperformed, and that mixing detailed and simpler captions improved its evaluated dense and global tasks.[^cao-2026-tipsv2]

## Distillation and reported results

The authors report that patch-level distillation without masking can produce a smaller student with better zero-shot segmentation than its larger teacher, even when that teacher has weak patch–text alignment. Their ablations associate the effect with loss on visible tokens and random student-vision initialization.[^cao-2026-tipsv2]

- TIPSv2 pretrains a ViT-g teacher on a 116M-image filtered WebLI subset, then distills ViT-B, ViT-L, and SO-400m variants. The released-family table reports its ViT-L/14 variant at 24.7 mIoU on ADE150 zero-shot segmentation, versus 17.8 for the pretrained ViT-g/14; these scores are specific to the paper's protocol.[^cao-2026-tipsv2]
- In an ablation on the TIPS ViT-g recipe, replacing iBOT with iBOT++ increased ADE150 zero-shot-segmentation mIoU from 3.5 to 17.6. Adding mixed-granularity captions and head-only EMA raised it to 19.1 in that fixed-schedule ablation.[^cao-2026-tipsv2]
- The appendix reports that adding iBOT++ to CLIP improved its evaluated ViT-L and ViT-g image-only, retrieval, and zero-shot-segmentation measures over the corresponding CLIP and CLIP+iBOT baselines. This is experimental evidence for those configurations, not a guarantee for arbitrary CLIP training recipes.[^cao-2026-tipsv2]

## Scope and limits

Reported model comparisons depend on distinct architectures, data volumes, model sizes, and—in some zero-shot-segmentation comparisons—different inference protocols. The authors explicitly note that some competing results use a more expensive sliding-window protocol, and their TIPSv2 training and evaluation results should therefore be read as paper-specific benchmarks.[^cao-2026-tipsv2]

## Relationships

- Uses: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md)'s contrastive image–text objective as one component of a combined contrastive and self-supervised recipe.[^cao-2026-tipsv2]
- Related: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) is a vision–language encoder baseline in the paper's dense and global image–text evaluations.[^cao-2026-tipsv2]

[^cao-2026-tipsv2]: Cao et al., “TIPSv2: Advancing Vision-Language Pretraining with Enhanced Patch-Text Alignment” (2026), [source](../raw/2604.12012_TIPSv2.md).
