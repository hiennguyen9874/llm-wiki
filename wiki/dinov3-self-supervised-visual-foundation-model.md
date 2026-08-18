---
type: Concept
title: DINOv3 self-supervised visual foundation model
description: A 7B self-supervised visual foundation-model family that preserves dense patch consistency through Gram-matrix regularization, then supports high-resolution use, distillation, and optional post-hoc text alignment.
tags: [self-supervised-learning, vision-foundation-models, dense-prediction, knowledge-distillation, representation-learning]
status: stable
created: 2026-08-18
generated: { by: llm-wiki-agent/1, at: 2026-08-18T10:30:22Z }
sources:
  - id: simeoni-2025-dinov3
    resource: ../raw/2508.10104_dinov3/main.tex
    title: DINOv3
---

# DINOv3 self-supervised visual foundation model

DINOv3 is a self-supervised visual-encoder family built around a 6.7B-parameter ViT teacher. Its central intervention, Gram regularization, matches the student’s within-image patch-similarity matrix to an earlier teacher’s matrix so extended training can retain dense-feature locality. The report then applies mixed-resolution adaptation, distills ViT and ConvNeXt students, and optionally aligns a frozen DINOv3 ViT-L to text; all performance claims below are author-reported results from this technical report.[^simeoni-2025-dinov3]

## Training and representation recipe

- The initial objective combines global DINO, patch-level iBOT, and distributed KoLeo losses. The 7B teacher uses 40 ViT blocks, 16-pixel patches, axial RoPE with coordinate-box jitter, four register tokens, and constant learning rate, weight decay, and teacher-EMA schedules after warm-up.[^simeoni-2025-dinov3]
- The reported web-data mixture combines a 1.689B-image hierarchical-clustering subset from an approximately 17B-image pool of public Instagram posts, retrieval-curated images, and ImageNet-1k/22k plus Mapillary data. Ten percent of iterations use homogeneous ImageNet-1k batches; the rest use heterogeneous batches. The paper’s 200k-step ablation reports that this mixture outperformed its raw, clustering-only, and retrieval-only alternatives on its selected downstream measures.[^simeoni-2025-dinov3]
- During long training, the authors observe global classification rising while dense-task performance and patch locality degrade. Gram regularization penalizes the squared Frobenius distance between the student and an earlier Gram teacher’s pairwise dot-product matrices of L2-normalized patch features. It starts after 1M iterations; the Gram teacher is refreshed every 10k steps. A 2×-resolution teacher followed by downsampling is reported to improve the dense-task refinement further.[^simeoni-2025-dinov3]
- A 10k-step mixed-resolution adaptation stage uses larger global/local crops and Gram regularization. The report attributes its stable high-resolution dense features to this stage and reports visualizations above 4k resolution; these are qualitative and paper-specific evidence, not a tested deployment limit.[^simeoni-2025-dinov3]

## Family and interfaces

- The fixed 7B teacher is distilled into ViT-S (21M), S+ (29M), B (86M), L (300M), H+ (840M), and ConvNeXt Tiny through Large models. Its multi-student procedure performs one teacher inference across the global GPU group, all-gathers results, then trains separately sized student groups in parallel to share teacher compute.[^simeoni-2025-dinov3]
- For optional image-text alignment, the report freezes a DINOv3 ViT-L, adds two transformer layers on its vision side, and contrastively trains a text encoder from scratch. It concatenates mean-pooled patch embeddings and the CLS token before matching text embeddings; this is a LiT-style application, not native image-text pretraining.[^simeoni-2025-dinov3]
- The authors recommend final-layer normalization for last-layer downstream features because training produces feature-dimension outliers. They use batch normalization or other scaling for intermediate-layer features; geometry-sensitive probes reportedly peak around layer 32 rather than the final layer.[^simeoni-2025-dinov3]

## Reported evaluation

- With frozen patch features and linear probes, the 7B model reports 55.9 ADE20k mIoU and NYUv2/KITTI depth RMSE of 0.309/2.346; it also reports leading scores among the compared encoders for NAVI/SPair correspondence and high-resolution video-mask propagation. Those comparisons use the paper’s resolutions, selected baselines, and evaluation protocols.[^simeoni-2025-dinov3]
- With task decoders on a frozen 7B backbone, the report gives 66.1 COCO detection mAP with test-time augmentation, 63.0 ADE20k segmentation mIoU, and relative-depth results that exceed its listed baselines on most measures. A DINOv3 ViT-L replacement in the VGGT pipeline also improves the paper’s listed 3D pose, multiview, and matching measures.[^simeoni-2025-dinov3]
- The text-aligned ViT-L is reported to improve the paper’s dense open-vocabulary segmentation comparison (24.7 ADE20k and 36.9 Cityscapes mIoU) while remaining below SigLIP 2 and Perception Encoder on several listed global alignment and retrieval measures.[^simeoni-2025-dinov3]
- A satellite-specific DINOv3 training run uses 493M Maxar RGB image chips and the same basic recipe. The report finds task-dependent specialization: the satellite model is stronger for canopy-height estimation, while the web model is competitive or stronger on several semantic geospatial benchmarks.[^simeoni-2025-dinov3]

## Limits and evidence boundaries

- This source is a technical report whose supplied LaTeX includes draft-only `\omitme` material. Its benchmark results are self-reported and vary in backbone size, training data, resolution, downstream head, tuning, and test-time augmentation; they do not establish a general cross-paper ranking.[^simeoni-2025-dinov3]
- The training corpus is described but not supplied in this bundle. The report says its Instagram pool comes from public posts and had platform-level content moderation; that does not establish independent reproducibility, dataset access, representativeness, or absence of privacy, copyright, or harmful-content risks.[^simeoni-2025-dinov3]
- The report’s OCR-heavy evaluation still trails its weakly supervised Perception Encoder baseline on most listed datasets, consistent with the stated absence of image-text supervision during visual pretraining.[^simeoni-2025-dinov3]
- The reported geographical analysis retains a 23% performance gap between low- and high-income buckets and more than 14% relative difference between Africa and Europe. Its environmental estimates depend on assumed PUE and US-average carbon intensity; the report estimates 18 tCO2eq for one 7B pretraining run and roughly 2,600 tCO2eq for the full project.[^simeoni-2025-dinov3]

## Relationships

- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) supplies the frozen-vision, contrastive text-alignment pattern that DINOv3 adapts with a small vision-side module and combined CLS/patch representation.[^simeoni-2025-dinov3]
- Related: [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) and [TIPSv2 patch–text aligned vision–language pretraining](tipsv2-patch-text-aligned-vision-language-pretraining.md) also target dense visual representations, but they learn image-text-aligned encoders during pretraining rather than adding text alignment after self-supervised visual pretraining.[^simeoni-2025-dinov3]
- Used by: [Vision-language task-to-model map](vision-language-task-to-model-map.md) as a vision-first option for dense prediction, geometry, and vision-to-text-alignment workflows.
- Related: [Mage-VL codec-native streaming vision-language model](mage-vl-codec-native-streaming-vision-language-model.md) is another vision-first model trained from scratch, but applies codec-guided sparse video tokenization and a Qwen3 interface rather than DINOv3’s self-distillation and optional post-hoc text alignment.
- Synthesized by: [Recent vision-language research directions](recent-vision-language-research-directions.md) as evidence for a vision-first global–dense encoder direction.

[^simeoni-2025-dinov3]: Siméoni et al., “DINOv3” (technical report, 2025), [complete supplied manuscript source](../raw/2508.10104_dinov3/main.tex).
