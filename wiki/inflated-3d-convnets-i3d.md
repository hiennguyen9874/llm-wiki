---
type: Concept
title: Inflated 3D ConvNets (I3D)
description: A two-stream action-recognition architecture that inflates pretrained 2D image ConvNets into spatiotemporal 3D ConvNets.
tags: [video, action-recognition, convnet, optical-flow, transfer-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T02:03:58Z }
sources:
  - id: i3d-paper
    resource: ../raw/I3D/full_kinetics_update_v0.tex
    title: Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset
---

# Inflated 3D ConvNets (I3D)

Inflated 3D ConvNets (I3D) turn an image-classification ConvNet into a spatiotemporal model by inflating its 2D convolution and pooling operators into 3D, then optionally initialize it from ImageNet weights.[^i3d-paper] The paper combines separately trained RGB and optical-flow I3D networks by averaging their predictions at test time.[^i3d-paper]

## Inflation and initialization

For a 2D $N \times N$ filter, I3D uses an $N \times N \times N$ spatiotemporal filter.[^i3d-paper] To initialize it from a pretrained 2D filter, repeat the 2D weights along the temporal axis $N$ times and divide each copy by $N$. This preserves the response for a temporally repeated static image—the paper’s “boring-video fixed point”—including subsequent pointwise, average-pooling, and max-pooling layers.[^i3d-paper]

This construction transfers both an established image-network design and its parameters; it does not make a 2D model temporal without video training. The reported I3D models are subsequently trained on Kinetics.[^i3d-paper]

## Temporal design and inputs

The reported Inflated Inception-v1 configuration avoids temporal pooling in its first two max-pooling layers, then uses symmetric temporal/spatial pooling later in the network.[^i3d-paper] It trains on 64-frame snippets at 25 FPS (2.56 seconds) and applies the network convolutionally to whole videos at test time, averaging predictions over time.[^i3d-paper]

The RGB stream learns spatiotemporal features directly from video frames. The flow stream receives externally computed TV-L1 optical flow; its separate prediction remains useful in the paper’s experiments and is fused with RGB only at test time.[^i3d-paper]

## Reported transfer evidence

The paper pretrains on Kinetics, whose reported version has 400 human-action classes and about 240,000 training clips.[^i3d-paper] Under its three-split UCF-101/HMDB-51 evaluation, two-stream I3D with Kinetics pretraining reported 97.8% and 80.9% accuracy, respectively; adding ImageNet initialization reported 98.0% and 80.7%.[^i3d-paper] These are historical benchmark results under the paper’s data, flow, and evaluation protocol, not a current deployment comparison.

## Relationships

- **Extends:** [Two-stream ConvNets for action recognition](two-stream-convnets-action-recognition.md) by replacing each 2D stream with a deep spatiotemporal ConvNet.
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for clip-level action recognition.
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through ImageNet initialization and supervised Kinetics video pretraining.

## Evidence limits

The source evaluates trimmed action-classification benchmarks and depends on precomputed TV-L1 flow for its motion stream.[^i3d-paper] It does not establish performance, latency, or robustness for current architectures, untrimmed localization, or production deployments.

[^i3d-paper]: [Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset](../raw/I3D/full_kinetics_update_v0.tex)
