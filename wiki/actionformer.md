---
type: Concept
title: ActionFormer
description: A single-stage, anchor-free Transformer for temporal action localization that classifies every feature-grid moment and regresses its action boundaries.
tags: [video, temporal-action-localization, transformer, anchor-free, local-attention]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:14:02+07:00 }
sources:
  - id: actionformer-paper
    resource: ../raw/ActionFormer/main.tex
    title: "ActionFormer: Localizing Moments of Actions with Transformers"
---

# ActionFormer

ActionFormer is a single-stage, anchor-free temporal action localization (TAL) model. It transforms pre-extracted video-clip features into a multiscale temporal feature pyramid with local self-attention, then gives each pyramid location an action-category score and distances to the action onset and offset.[^actionformer-paper]

## Anchor-free temporal prediction

For every temporal location, the model predicts independent action-category probabilities and, for foreground locations, distances to the action's start and end. These outputs decode directly into labeled intervals, so it does not first generate action proposals or use predefined anchor windows.[^actionformer-paper]

The encoder projects clip features with shallow convolutions and applies Transformer blocks with local multi-head self-attention, 2× depthwise-convolution downsampling, and MLP blocks to form a temporal feature pyramid. Using the same local window at coarser resolutions expands the effective temporal context: the paper gives a window of 19 at a 16×-downsampled level as covering 304 feature-grid steps.[^actionformer-paper]

Shared lightweight 1D-convolution classification and regression heads operate at every pyramid level. Training combines focal classification loss with DIoU boundary-regression loss; center sampling marks only locations around an action center as positive. At inference, Soft-NMS removes highly overlapping decoded intervals.[^actionformer-paper]

## Reported evaluation

On THUMOS14 with two-stream I3D features, the paper reports 71.0% mAP at tIoU 0.5, 43.9% at tIoU 0.7, and 66.8% averaged over tIoU 0.3–0.7. On ActivityNet-1.3 it reports 35.6% average mAP with I3D features and 36.6% with TSP/R(2+1)D features; these are paper-specific benchmark results under its stated feature extractors and evaluation setup.[^actionformer-paper]

On EPIC-Kitchens 100 validation with supplied SlowFast features, the paper reports average mAP of 23.5% for verbs and 21.9% for nouns across tIoU 0.1–0.5.[^actionformer-paper]

## Limits

The method consumes pre-extracted video features rather than learning directly from raw frames. The authors also identify dependence on densely labeled videos and a predefined action vocabulary as limitations. Their error analysis attributes prominent false positives to localization error and background confusion, and reports higher false-negative rates for very short or very long instances and videos with many instances.[^actionformer-paper]

## Evidence scope

This compilation covers the paper's main and included TeX sections, tables, captions, and extractable labels from its figure PDFs. Visual-only example frames were not independently interpreted.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) as interval-level, single-stage temporal action localization.
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) techniques: local temporal attention and a multiscale feature pyramid extend context without full-sequence global attention.
- **Uses:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md), [R(2+1)D](r-2-plus-1-d.md), and [SlowFast Networks](slowfast-networks.md) as reported external feature extractors in its evaluations.

[^actionformer-paper]: [ActionFormer: Localizing Moments of Actions with Transformers](../raw/ActionFormer/main.tex)
