---
type: Concept
title: PP-LCNet lightweight CPU convolutional neural network
description: A CPU-oriented lightweight CNN that combines depthwise-separable blocks with tail-localized accuracy enhancements for an Intel oneDNN/MKLDNN deployment target.
tags: [computer-vision, convolutional-neural-networks, efficient-inference, hardware-aware-design, lightweight-models]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T15:30:33Z }
sources:
  - id: cui-2021-pp-lcnet
    resource: ../raw/2109.15099_PP-LCNet.md
    title: PP-LCNet: A Lightweight CPU Convolutional Neural Network
---

# PP-LCNet lightweight CPU convolutional neural network

PP-LCNet is a lightweight CNN designed around Intel CPU inference with oneDNN/MKLDNN acceleration. It starts from stacked depthwise-separable convolutions and concentrates accuracy-oriented changes near the network tail, where the authors report a better accuracy–latency trade-off than applying those changes throughout the network.[^cui-2021-pp-lcnet]

## Architecture and design rules

- The base network has a $3 \times 3$ convolutional stem followed by depthwise-separable convolution blocks. The authors select this block because their Intel CPU acceleration stack had optimized it and because it avoids shortcut, concatenation, and elementwise-add operations.[^cui-2021-pp-lcnet]
- PP-LCNet replaces ReLU with H-Swish, uses $5 \times 5$ depthwise kernels in tail blocks, and adds squeeze-and-excitation (SE) modules only to the final two blocks. Its head uses global average pooling followed by a 1,280-channel $1 \times 1$ convolution without batch normalization before classification.[^cui-2021-pp-lcnet]
- The paper's ablations place the SE modules or larger kernels at different depths. For PP-LCNet-0.5x, tail-only SE reached 63.14% ImageNet top-1 at 2.05 ms, versus 62.17% at 2.03 ms for a mid-network placement; tail-only large kernels reached the same accuracy and latency, close to using large kernels throughout (63.22%, 2.08 ms).[^cui-2021-pp-lcnet]

## Reported measurements

- On the authors' Intel Xeon Gold 6148 setup (batch size 1, 10 threads, MKLDNN enabled), PP-LCNet-1x has 3.0M parameters, 161M FLOPs, 71.32% ImageNet top-1 accuracy, and 2.46 ms latency. An SSLD-distilled 1x variant reports 74.39% top-1 at the same stated latency.[^cui-2021-pp-lcnet]
- Under that same measurement configuration, the paper compares PP-LCNet-1x with MobileNetV2-1x: PP-LCNet reports lower top-1 accuracy (71.32% vs. 72.15%) but lower latency (2.46 ms vs. 4.26 ms). These values are architecture and deployment-stack specific, not a general ordering of the models.[^cui-2021-pp-lcnet]
- With PicoDet on COCO validation, the PP-LCNet-1x backbone reports 26.9% mAP and 7.9 ms latency, versus 25.8% and 11.1 ms for MobileNetV3-large-0.75x. With DeepLabv3+ on Cityscapes validation, PP-LCNet-1x reports 66.03% mIoU and 96 ms, versus 64.53% and 151 ms for MobileNetV3-large-0.75x.[^cui-2021-pp-lcnet]

## Limits

The paper's design recommendations are empirical for its selected Intel CPU, oneDNN/MKLDNN configuration, batch size, and training recipes. They should be re-benchmarked for another processor, inference runtime, input shape, or task rather than treated as hardware-independent lightweight-CNN rules.[^cui-2021-pp-lcnet]

[^cui-2021-pp-lcnet]: Cui et al., “PP-LCNet: A Lightweight CPU Convolutional Neural Network” (2021), [source](../raw/2109.15099_PP-LCNet.md).
