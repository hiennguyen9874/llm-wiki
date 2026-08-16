---
type: Concept
title: SlowFast Networks
description: A two-pathway video architecture that assigns sparse semantic processing and dense lightweight motion processing to separate temporal rates.
tags: [video, action-recognition, action-detection, convnet, temporal-modeling]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:37:18+07:00 }
sources:
  - id: slowfast-paper
    resource: ../raw/SlowFast/slowfast_iccv19_arxiv_final.tex
    title: SlowFast Networks for Video Recognition
---

# SlowFast Networks

SlowFast Networks process the same video clip through a sparse **Slow** pathway for spatial semantics and a dense, low-channel **Fast** pathway for fine motion, then fuse Fast features into Slow features through lateral connections.[^slowfast-paper] This separates temporal refresh rate from spatial capacity, enabling end-to-end RGB motion modeling without precomputed optical flow.[^slowfast-paper]

## Architecture

The Slow pathway samples $T$ frames at a large temporal stride $\tau$; the paper's representative configuration takes four frames at stride 16 from a 64-frame clip.[^slowfast-paper] The Fast pathway samples eight times as many frames from that clip, retains temporal resolution through its intermediate layers, and uses one eighth of the Slow pathway's channel capacity.[^slowfast-paper] Its lower width makes it roughly 20% of the representative model's computation while leaving the Slow pathway to represent detailed spatial content.[^slowfast-paper]

For a ResNet implementation, the source places unidirectional Fast-to-Slow lateral connections after `pool1` and residual stages 2–4, then concatenates globally pooled pathway outputs for classification.[^slowfast-paper] The paper evaluates time-to-channel reshaping, time-strided sampling, and time-strided convolution for temporal alignment; its default is a $5 \times 1 \times 1$ time-strided convolution followed by concatenation.[^slowfast-paper]

## Reported evidence

On the paper's Kinetics-400 ablation with a 4×16 ResNet-50 Slow pathway, SlowFast with time-strided-convolution fusion reported 75.6% top-1 accuracy at 36.1 GFLOPs per 256² view, versus 72.6% and 27.3 GFLOPs for Slow-only.[^slowfast-paper] The Fast pathway alone reached 51.7% top-1, while its fused contribution improved the Slow baseline by 3.0 percentage points in that setup.[^slowfast-paper]

For AVA v2.1 action detection, the paper's 4×16 ResNet-50 ablation increased validation mAP from 19.0 for Slow-only to 24.2 for SlowFast.[^slowfast-paper] Its reported higher-capacity SlowFast + non-local configuration reached 27.1 mAP on the v2.1 test set; these are historical results under the source's Kinetics pretraining, person proposals, and evaluation protocol.[^slowfast-paper]

## Relationships

- **Contrasts with:** [Two-stream ConvNets for action recognition](two-stream-convnets-action-recognition.md). SlowFast separates RGB pathways by temporal rate and channel capacity rather than sending RGB and precomputed optical flow to analogous streams.[^slowfast-paper]
- **Complements:** [Non-local Neural Networks](non-local-neural-networks.md). The source optionally adds non-local blocks to the fused Slow features in deeper configurations.[^slowfast-paper]
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for action classification and person-centric spatiotemporal action detection.[^slowfast-paper]

## Evidence limits

The source is a published-model manuscript with benchmark comparisons on Kinetics, Charades, and AVA; its numerical results are tied to the stated backbones, sampling, training recipes, person proposals, and multi-view evaluation.[^slowfast-paper] It does not establish current state of the art, latency on production hardware, robustness, or performance on arbitrary long videos. The directory also contains an earlier arXiv TeX revision; this concept cites the later `slowfast_iccv19_arxiv_final.tex` revision, whose added material includes updated AVA results and implementation details.

[^slowfast-paper]: [SlowFast Networks for Video Recognition](../raw/SlowFast/slowfast_iccv19_arxiv_final.tex)
