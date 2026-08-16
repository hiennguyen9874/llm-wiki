---
type: Concept
title: R(2+1)D
description: A ResNet video architecture that factorizes each 3D convolution into spatial 2D and temporal 1D convolutions separated by a nonlinearity.
tags: [video, action-recognition, convnet, 3d-convolution, resnet]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T02:17:23Z }
sources:
  - id: r2plus1d-paper
    resource: ../raw/R(2+1)D/res2_plus_1d.pdf
    title: A Closer Look at Spatiotemporal Convolutions for Action Recognition
---

# R(2+1)D

R(2+1)D is a residual video-classification architecture that replaces each full 3D convolution with a 2D spatial convolution followed by a 1D temporal convolution, with a ReLU between them.[^r2plus1d-paper] The factorization preserves temporal feature propagation while separating appearance and motion computation; the paper reports lower training and test error than a parameter-matched 3D ResNet in its experiments.[^r2plus1d-paper]

## Factorized convolution block

For a 3D layer with $N_i$ filters of size $N_{i-1} \times t \times d \times d$, the block first projects with $M_i$ spatial filters of size $N_{i-1} \times 1 \times d \times d$, then applies $N_i$ temporal filters of size $M_i \times t \times 1 \times 1$.[^r2plus1d-paper] It selects $M_i = \left\lfloor\frac{t d^2 N_{i-1}N_i}{d^2N_{i-1}+tN_i}\right\rfloor$ to approximately match the full 3D layer's parameter count.[^r2plus1d-paper]

The intervening ReLU adds a nonlinearity without the full-3D baseline's parameter increase. The authors attribute the reported optimization benefit partly to this extra rectification and partly to the separated spatial–temporal parameterization; these are the paper's experimental interpretation, not a general guarantee.[^r2plus1d-paper]

## Reported findings and use

On the paper's Kinetics validation comparison using 18-layer models and 16-frame clips, R(2+1)D reported 68.0% video top-1 accuracy, versus 64.2% for R3D; comparisons use the source's training and evaluation setup.[^r2plus1d-paper] A 34-layer RGB model trained from scratch reported 72.0% top-1 on Kinetics, while the paper's cited no-pretraining I3D-RGB result was 67.5%.[^r2plus1d-paper]

The architecture can be trained on RGB or optical flow, with separate streams fused by averaging predictions.[^r2plus1d-paper] The source found that longer training clips improved its reported clip-level accuracy, while video-level accuracy peaked at 32 frames in that setting; testing an 8-frame-trained model on 32-frame clips did not recover the benefit of long-clip training.[^r2plus1d-paper]

## Relationships

- **Compared with:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) in the source's historical Kinetics results.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through supervised Sports-1M or Kinetics pretraining before transfer.
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for clip- and video-level action recognition.

## Evidence limits

All reported results are historical benchmark results from one study, including particular clip lengths, pretraining data, optical-flow method, and test-time clip averaging.[^r2plus1d-paper] They do not establish current state of the art, performance on temporal localization or segmentation, or deployment latency and robustness.

[^r2plus1d-paper]: [A Closer Look at Spatiotemporal Convolutions for Action Recognition](../raw/R\(2+1\)D/res2_plus_1d.pdf)
