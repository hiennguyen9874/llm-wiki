---
type: Concept
title: Temporal Segment Networks
description: A video-level action-recognition framework that samples snippets across equal temporal segments and learns their consensus.
tags: [video, action-recognition, temporal-learning, sparse-sampling, convnet]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-15T10:23:21Z }
sources:
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
---

# Temporal Segment Networks

Temporal Segment Networks (TSN) model an entire video at fixed per-example cost: divide it into $K$ equal-duration segments, randomly sample one short snippet from each, apply a shared ConvNet to every snippet, and aggregate their class scores before the video-level softmax and loss.[^temporal-segment-networks] This sparse, global sampling trades dense local coverage for temporal coverage across the video.

## Consensus learning

The segmental consensus function combines the $K$ snippet-score vectors, so backpropagation updates the shared ConvNet using video-level rather than isolated-snippet supervision.[^temporal-segment-networks]

- **Max pooling** selects one highest-scoring snippet per class; it can ignore useful complementary snippets.
- **Average pooling** uses all sampled snippets, but background snippets can dilute a class signal.
- **Top-$\mathcal{K}$ pooling** averages only the highest-scoring snippets; max and average pooling are its $\mathcal{K}=1$ and $\mathcal{K}=K$ cases.
- **Linear weighting** learns fixed position weights, while **attention weighting** derives snippet weights from each video’s learned features.[^temporal-segment-networks]

In the paper’s experiments, average consensus was best on the trimmed UCF101 benchmark, while top-$\mathcal{K}$ pooling and attention were stronger than basic pooling on ActivityNet’s more complex untrimmed videos. This is evidence for those benchmark settings, not a universal aggregation ranking.[^temporal-segment-networks]

## Untrimmed-video classification

For untrimmed classification, TSN evaluates snippets at a fixed rate, applies sliding windows at multiple temporal scales, max-pools scores within each window, uses top-$\mathcal{K}$ pooling across same-scale windows, and averages the scale-level scores. The paper calls this Multi-scale Temporal Window Integration (M-TWI).[^temporal-segment-networks] M-TWI produces a video-level class prediction; it is not temporal action localization because it does not return action start/end intervals.

## Training and inputs

The paper transfers an ImageNet-pretrained RGB first-layer filter to flow or RGB-difference inputs by averaging the RGB-channel weights and replicating the average to the temporal input’s channel count. It also freezes batch-normalization statistics except in the first layer during fine-tuning (*partial BN*) and uses high dropout to limit overfitting on small action datasets.[^temporal-segment-networks]

TSN retains RGB and optical flow as appearance and motion inputs, evaluates camera-motion-compensated warped flow, and proposes stacked RGB differences as a cheaper motion cue. On UCF101, the reported RGB-plus-RGB-difference TSN reached 91.0% at 340 FPS, whereas RGB-plus-flow TSN reached 94.9% at 14 FPS; these paper-specific measurements depend on its hardware and protocol.[^temporal-segment-networks]

## Evidence limits

The source reports 2016-era benchmark and challenge results using two-stream CNN backbones, optical-flow extraction, and specified train/test splits. They establish the paper’s empirical findings, not current state of the art or production latency.

## Relationships

- **Extends:** [Two-stream ConvNets for action recognition](two-stream-convnets-action-recognition.md) with video-level temporal sampling and additional training practices.
- **Supports:** [Long-video temporal modeling](long-video-temporal-modeling.md) through fixed-cost, globally distributed snippet sampling.
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for trimmed and untrimmed video classification.
- **Part of:** [Video temporal learning](video-temporal-learning.md).

[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
