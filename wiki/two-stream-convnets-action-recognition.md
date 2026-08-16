---
type: Concept
title: Two-stream ConvNets for action recognition
description: A late-fusion video classifier that separates appearance in RGB frames from motion in stacked optical flow.
tags: [video, action-recognition, convnet, optical-flow, multi-task-learning]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:37:18+07:00 }
sources:
  - id: slowfast-paper
    resource: ../raw/SlowFast/slowfast_iccv19_arxiv_final.tex
    title: SlowFast Networks for Video Recognition
  - id: two-stream-convnets
    resource: ../raw/Two-StreamConvNets/flow_net.tex
    title: Two-Stream Convolutional Networks for Action Recognition in Videos
  - id: temporal-segment-networks
    resource: ../raw/TemporalSegmentNetworks/tsn_pami.tex
    title: Temporal Segment Networks for Action Recognition in Videos
  - id: i3d-paper
    resource: ../raw/I3D/full_kinetics_update_v0.tex
    title: Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset
---

# Two-stream ConvNets for action recognition

Two-stream ConvNets classify video by separating static appearance from motion: a spatial ConvNet processes individual RGB frames, a temporal ConvNet processes a stack of dense optical-flow fields, and their class scores are fused late.[^two-stream-convnets] The separation makes motion explicit rather than requiring a network trained on limited video data to infer it from stacked RGB frames.

## Architecture

- The **spatial stream** applies an image ConvNet to sampled video frames. It can be pretrained on ImageNet, then adapted to the action dataset.[^two-stream-convnets]
- The **temporal stream** receives $L$ consecutive flow fields as $2L$ channels: horizontal and vertical displacement for each field. In the reported architecture, it otherwise closely follows the spatial network’s convolutional and fully connected layers.[^two-stream-convnets]
- At video level, sample and crop scores are averaged within each stream; the two softmax-score vectors are fused either by averaging or by a linear SVM trained on stacked, $L_2$-normalized scores.[^two-stream-convnets]

## Motion representation choices

The paper evaluates flow sampled at fixed image locations (*optical-flow stacking*) and along estimated trajectories (*trajectory stacking*). It also evaluates bidirectional flow and subtracting the per-field mean displacement, a simple mitigation for dominant camera motion.[^two-stream-convnets]

On UCF-101 split 1, ten stacked flows with mean subtraction reached 81.0% temporal-stream accuracy, compared with 73.9% for one flow; bidirectional flow reached 81.2%, and trajectory stacking reached 80.2%.[^two-stream-convnets] These are paper-specific experimental results, not a general ranking across contemporary architectures.

## Limited-data training

The temporal stream cannot use still-image pretraining in the same way as the spatial stream. To share video training data from UCF-101 and HMDB-51 despite different class sets, the paper uses a shared network body with one dataset-specific softmax head and loss per dataset; each example activates only its dataset’s loss.[^two-stream-convnets]

On HMDB-51 split 1, this multi-task setup reported 55.4% temporal-stream accuracy, versus 46.6% when training on HMDB-51 alone. On UCF-101 split 1, fusing the multi-task temporal stream with the spatial stream via an SVM reported 87.0% accuracy.[^two-stream-convnets]

## TSN refinements

Temporal Segment Networks retain the RGB and flow streams but sample snippets across equal-duration video segments and train on a consensus of their scores, rather than treating snippets independently.[^temporal-segment-networks] For temporal-stream initialization, the paper averages an ImageNet-pretrained RGB filter’s three input channels and replicates that average to the flow or RGB-difference input channels; it then freezes batch-normalization statistics except in the first layer during fine-tuning (*partial BN*).[^temporal-segment-networks]

The same work evaluates stacked RGB differences as a motion representation that avoids optical-flow extraction. Its reported accuracy/throughput trade-off is specific to the paper’s UCF101 protocol and TitanX hardware, not a current deployment comparison.[^temporal-segment-networks]

## I3D extension

I3D preserves the two-stream separation but replaces each 2D ConvNet with an inflated 3D ConvNet that learns spatiotemporal features over a 64-frame input; the separately trained RGB and flow predictions are averaged at test time.[^i3d-paper] This makes temporal feature extraction internal to both streams rather than limiting motion processing to the flow input and late score fusion.

## SlowFast contrast

SlowFast retains two pathways but feeds both with RGB frames sampled at different temporal rates, making the high-rate pathway narrow rather than supplying a second, precomputed motion modality.[^slowfast-paper] Its source reports end-to-end action-classification and detection experiments, but this is a distinct architecture from two-stream late fusion.

## Evidence limits

The reported full three-split results are 88.0% on UCF-101 and 59.4% on HMDB-51 with SVM fusion.[^two-stream-convnets] They rely on precomputed Brox optical flow and the paper’s benchmark protocols, so they do not establish current deployment cost, robustness, or superiority to later end-to-end video models.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for clip-level action recognition.
- **Part of:** [Video temporal learning](video-temporal-learning.md).
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) in the limited sense of spatial ImageNet pretraining.
- **Extended by:** [Temporal Segment Networks](temporal-segment-networks.md) for sparse video-level sampling and consensus learning.
- **Extended by:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md), which replaces each 2D stream with an inflated 3D ConvNet.
- **Contrasted with:** [SlowFast Networks](slowfast-networks.md), which separates two RGB pathways by temporal rate and channel capacity rather than RGB and optical-flow modality.[^slowfast-paper]

[^slowfast-paper]: [SlowFast Networks for Video Recognition](../raw/SlowFast/slowfast_iccv19_arxiv_final.tex)
[^two-stream-convnets]: [Two-Stream Convolutional Networks for Action Recognition in Videos](../raw/Two-StreamConvNets/flow_net.tex)
[^temporal-segment-networks]: [Temporal Segment Networks for Action Recognition in Videos](../raw/TemporalSegmentNetworks/tsn_pami.tex)
[^i3d-paper]: [Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset](../raw/I3D/full_kinetics_update_v0.tex)
