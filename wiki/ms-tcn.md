---
type: Concept
title: MS-TCN (Multi-Stage Temporal Convolutional Network)
description: A full-resolution frame-level action-segmentation network that sequentially refines temporal class probabilities with stacked dilated-convolution stages.
tags: [video, action-segmentation, temporal-convolution, dilated-convolution]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T02:46:34Z }
sources:
  - id: ms-tcn-paper
    resource: ../raw/MS-TCN/egpaper_final.tex
    title: MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation
---

# MS-TCN (Multi-Stage Temporal Convolutional Network)

MS-TCN performs fully supervised action segmentation by assigning a class to every video frame. Its first temporal-convolution stage consumes frame features; later stages consume only the preceding stage's class-probability sequence and refine it, reducing fragmented, over-segmented predictions.[^ms-tcn-paper]

## Architecture

A single stage starts with a $1 \times 1$ temporal convolution and follows it with residual, acausal dilated 1D convolutions with kernel size 3. The dilation doubles by layer (1, 2, 4, ..., 512), giving an exponentially growing receptive field without temporal pooling or a proportional parameter increase.[^ms-tcn-paper]

Stages are composed sequentially: the first receives frame-wise video features, while each higher stage receives the previous stage's frame-wise probabilities rather than the original features. The source reports that passing probabilities alone lets higher stages model neighboring label context; concatenating intermediate features increased over-segmentation in its 50Salads experiment.[^ms-tcn-paper]

## Training objective

Each stage is supervised with cross-entropy plus a truncated mean-squared smoothing loss over adjacent frames' log-probabilities. The smoothing term is capped by threshold $\tau$ and differentiates only through the current frame's probability; the total objective sums the per-stage losses.[^ms-tcn-paper]

In the reported four-stage configuration, each stage has ten dilated layers, 64 filters, and dropout; the source sets $\lambda=0.15$ and $\tau=4$.[^ms-tcn-paper] The truncation is important: excessively strong smoothing can suppress true action boundaries.[^ms-tcn-paper]

## Reported evaluation

Using I3D features at 15 FPS, the paper reports on 50Salads, GTEA, and Breakfast. On 50Salads, its four-stage model reported F1@{10,25,50} of 76.3, 74.0, and 64.5, edit score 67.9, and frame accuracy 80.7; these are paper-specific historical results under its features and evaluation protocol.[^ms-tcn-paper]

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for frame-level action segmentation.
- **Uses:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) features in the paper's experiments.
- **Part of:** [Video temporal learning](video-temporal-learning.md).

## Evidence limits

The source studies fully supervised segmentation, three specific action datasets, and fixed pre-extracted feature protocols. It does not establish weakly supervised, online/causal, long-context, or production performance.[^ms-tcn-paper]

[^ms-tcn-paper]: [MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation](../raw/MS-TCN/egpaper_final.tex)
