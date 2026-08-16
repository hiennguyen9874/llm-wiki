---
type: Concept
title: Non-local Neural Networks
description: Neural-network blocks that directly aggregate pairwise feature relations across all spatial, temporal, or spacetime positions.
tags: [video, action-recognition, long-range-dependencies, attention, convnet]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:37:18+07:00 }
sources:
  - id: slowfast-paper
    resource: ../raw/SlowFast/slowfast_iccv19_arxiv_final.tex
    title: SlowFast Networks for Video Recognition
  - id: nonlocal-paper
    resource: ../raw/Non-localNeuralNetworks/nonlocal.tex
    title: Non-local Neural Networks
---

# Non-local Neural Networks

Non-local Neural Networks augment a vision backbone with residual blocks that compute each position’s feature as a weighted aggregation of features from all positions in space, time, or spacetime.[^nonlocal-paper] Unlike repeated local convolution or recurrence, one block directly connects distant positions and can be inserted into pretrained 2D or 3D ConvNets with an identity-preserving initialization.[^nonlocal-paper]

## Non-local operation

For output position $i$, the operation is:

$$
y_i = \frac{1}{\mathcal{C}(x)} \sum_{\forall j} f(x_i, x_j) g(x_j).
$$

The pairwise function $f$ supplies an affinity between positions, $g$ embeds the feature at $j$, and the normalization makes the aggregation usable with variable-sized inputs.[^nonlocal-paper] The source evaluates Gaussian, embedded-Gaussian, dot-product, and concatenation affinities. The embedded-Gaussian form is self-attention over positions; its softmax normalizes affinities across $j$.[^nonlocal-paper]

## Residual block and efficiency

A non-local block produces $z_i = W_z y_i + x_i$.[^nonlocal-paper] Initializing the final projection (and its following batch-normalization scale in the reported implementation) to zero makes the block initially an identity mapping, allowing insertion into a pretrained backbone without changing its initial behavior.[^nonlocal-paper]

The reported implementation halves the embedding channel dimension for $g$, $\theta$, and $\phi$, and can spatially subsample the keys and values before pairwise aggregation.[^nonlocal-paper] These are practical reductions for the source’s high-level feature maps, not a claim that unrestricted global pairwise computation is inexpensive at arbitrary video resolution or duration.

## Video-classification evidence

On the source’s Kinetics ResNet-101 ablation, five non-local blocks added to a 2D baseline reported 75.1% top-1 accuracy, compared with 73.1% for C2D and 74.4% for its inflated 3D baseline; the non-local C2D model used 1.2× baseline parameters and FLOPs, versus 1.2× parameters and 1.5× FLOPs for that I3D configuration.[^nonlocal-paper] Adding five blocks to the source’s I3D produced 76.0% top-1, which the experiment treats as evidence that global non-local and local 3D-convolutional interactions are complementary.[^nonlocal-paper]

The source also reports a 39.5% Charades test mAP for its non-local I3D, versus 37.2% for its I3D baseline.[^nonlocal-paper] In the SlowFast source's Kinetics-400 table, adding non-local blocks to its 16×8 ResNet-101 configuration increased reported top-1 accuracy from 78.9% to 79.8%; this is another architecture- and protocol-specific historical result.[^slowfast-paper] These are not current performance, deployment-cost, or long-video evidence.

## Relationships

- **Complements:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) by adding direct global spacetime interactions to local 3D convolutions.
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for video classification.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through the source’s ImageNet initialization and Kinetics supervised pretraining.
- **Complements:** [SlowFast Networks](slowfast-networks.md), whose source adds non-local blocks to fused Slow features in some deeper configurations.[^slowfast-paper]

## Evidence limits

The source evaluates Kinetics and Charades clip/video classification, plus COCO detection, instance segmentation, and keypoint detection.[^nonlocal-paper] It does not evaluate temporal localization or segmentation, current architectures, production latency, or a scalable strategy for arbitrarily long videos.

[^slowfast-paper]: [SlowFast Networks for Video Recognition](../raw/SlowFast/slowfast_iccv19_arxiv_final.tex)
[^nonlocal-paper]: [Non-local Neural Networks](../raw/Non-localNeuralNetworks/nonlocal.tex)
