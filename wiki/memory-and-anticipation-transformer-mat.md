---
type: Concept
title: Memory-and-Anticipation Transformer (MAT)
description: A unified Transformer for online action detection and fixed-gap anticipation that compresses historical memory and iteratively exchanges it with latent future features.
tags: [video, online-action-detection, action-anticipation, transformer, memory, long-context]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:24:49+07:00 }
sources:
  - id: mat-paper
    resource: ../raw/Memory-and-AnticipationTransformer/main.tex
    title: Memory-and-Anticipation Transformer for Online Action Understanding
---

# Memory-and-Anticipation Transformer (MAT)

Memory-and-Anticipation Transformer (MAT) is an encoder–decoder Transformer that uses only cached historical video features at inference, while jointly producing a current-action prediction and a prediction at a selected future gap. It compresses long-term history into segment-level tokens, enhances recent history from that summary, then iteratively cross-attends between that memory and learned latent future features.[^mat-paper]

## Task and outputs

Given feature vectors through the present time, MAT defines online action detection as the zero-gap case ($\tau=0$) and anticipation as classification after a specified future gap ($\tau>0$). It does not access future video features or labels at inference. The final short-term-memory token supplies the current prediction, and the future-feature token aligned to $\tau$ supplies the anticipation prediction.[^mat-paper]

This dense, per-timestep notion of online detection is distinct from interval-level temporal action localization: MAT predicts a current class, not a start–end action interval.[^mat-paper]

## Architecture

- **Progressive Memory Encoder:** partitions cached history into a long-term region and recent short-term region. Shared learned long-memory queries cross-attend to each non-overlapping long-memory segment; the resulting segment summaries are pooled and further encoded. A causal decoder then uses recent tokens to retrieve from that compressed long-term representation.[^mat-paper]
- **Latent anticipation:** learned future queries cross-attend to the combined compressed-long and enhanced-short memory. During training, the resulting future features receive future-label supervision; at inference they are generated only from history.[^mat-paper]
- **Conditional circular interaction:** first short-term memory cross-attends to the concatenated long-term, short-term, and future features; then future features cross-attend to the representation containing the updated short-term memory. The model repeats this pair of updates, with deep classification supervision and a shared classifier for memory and future features.[^mat-paper]

The source reports its best THUMOS'14 ablation at eight long-memory segments and two circular-interaction rounds. This is a task-specific reported result, not a general selection rule.[^mat-paper]

## Reported evaluation and limits

MAT was evaluated with pre-extracted features on online detection in THUMOS'14, TVSeries, and HDD, and on both online detection and 1-second-gap anticipation in EPIC-Kitchens-100. Its reported detection scores include 70.4 mAP on THUMOS'14 with ActivityNet-pretrained features, 88.6 mcAP on TVSeries with the same feature source, and 32.7 mAP on HDD; its EPIC-Kitchens-100 RGB-plus-optical-flow anticipation result is 19.5 class-mean action recall@5.[^mat-paper]

These results establish benchmark evidence for a bounded cached-memory architecture using pre-extracted features. They do not establish end-to-end raw-video efficiency or behavior over arbitrary-duration histories. The reported THUMOS comparison attributes the total pipeline bottleneck largely to optical-flow calculation and feature extraction, not solely to MAT.[^mat-paper]

## Evidence scope

This compilation covers `main.tex`, all six included TeX sections, tables, and figure captions. The seven referenced figure PDFs were text-inspected to confirm their architectural, ablation, prediction, and attention-visualization roles; visual layouts were not independently interpreted. Bibliographic and TeX-style files were excluded because they add no material method evidence.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) as unified online current-action detection and fixed-gap anticipation.
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through bounded-memory segmentation and compression rather than full-history global attention.
- **Uses:** [Temporal Segment Networks](temporal-segment-networks.md) as the reported two-stream feature extractor for TVSeries, THUMOS'14, and EPIC-Kitchens-100 experiments.[^mat-paper]

[^mat-paper]: [Memory-and-Anticipation Transformer for Online Action Understanding](../raw/Memory-and-AnticipationTransformer/main.tex)
