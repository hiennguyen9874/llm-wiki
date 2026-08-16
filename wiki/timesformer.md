---
type: Concept
title: TimeSformer
description: A video Transformer that factorizes temporal and spatial self-attention over frame patches to make long-clip action recognition practical.
tags: [video, action-recognition, transformer, attention, long-context]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:03:14+07:00 }
sources:
  - id: vivit-paper
    resource: ../raw/ViViT/main_arxiv.tex
    title: "ViViT: A Video Vision Transformer"
  - id: timesformer-paper
    resource: ../raw/TimeSformer/TimeSformer_arxiv_v17.tex
    title: Is Space-Time Attention All You Need for Video Understanding?
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
---

# TimeSformer

TimeSformer adapts Vision Transformer-style patch tokens to video and uses **divided space-time attention**: temporal attention at each spatial location followed by spatial attention within each frame.[^timesformer-paper] This factorization retains cross-frame interaction while avoiding the full joint-attention cost, allowing the paper to evaluate substantially longer clips for action recognition.[^timesformer-paper]

## Architecture

A clip of $F$ RGB frames is split into $N = HW/P^2$ non-overlapping $P \times P$ patches per frame. Each patch is linearly embedded, receives a learned spatiotemporal positional embedding, and is processed with a classification token by stacked Transformer blocks.[^timesformer-paper]

In divided attention, each patch first attends to patches at the same spatial position across frames, then to patches in its own frame. The two stages have distinct query/key/value projections. Per patch, this requires $N + F + 2$ query-key comparisons rather than the $NF + 1$ comparisons of joint space-time attention.[^timesformer-paper] The paper found temporal-then-spatial ordering slightly better than the reverse order in its ablation.[^timesformer-paper]

## Attention-design evidence

On the paper's $8 \times 224 \times 224$ experiments, divided attention reported 78.0% top-1 on Kinetics-400 and 59.5% on Something-Something-V2, compared with 77.4% and 58.5% for joint space-time attention and 76.9% and 36.6% for spatial-only attention.[^timesformer-paper] These results support temporal modeling particularly on the temporally demanding SSv2 benchmark; they are paper- and protocol-specific rather than a general ranking.

The paper reports that joint space-time attention exhausted GPU memory at 448-pixel spatial crops or 32-frame inputs, whereas the factorized design was used for later high-resolution and long-clip experiments.[^timesformer-paper] Its default model depends on ImageNet-pretrained ViT weights: the reported Kinetics-400 from-scratch result was 64.8% top-1, versus 75.8% with ImageNet-1K pretraining and 78.0% with ImageNet-21K pretraining.[^timesformer-paper]

## Long-clip evidence

The long configuration uses 96 frames at $224 \times 224$ sampled at one frame per four original frames; on Kinetics-400 it reported 80.7% top-1.[^timesformer-paper] On the paper's filtered HowTo100M long-term task-classification subset, 96-frame TimeSformer clips spanned 102.4 seconds and reported 62.6% top-1, versus 51.2% for the corresponding SlowFast configuration; videos were still covered by averaging predictions from multiple non-overlapping clips.[^timesformer-paper] This is evidence for longer clip-level context, not evidence that the architecture preserves every event across an arbitrary-length video.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for video-level action recognition.
- **Supports:** [Long-video temporal modeling](long-video-temporal-modeling.md) through factorized attention over longer clips.
- **Contrasts with:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) and [SlowFast Networks](slowfast-networks.md), which are convolutional video backbones; the source compares their historical action-recognition costs and accuracies.[^timesformer-paper]
- **Contrasts with:** [ViViT (Video Vision Transformer)](vivit.md). ViViT's paper directly compares its factorised-encoder classification result with TimeSformer-HR on Something-Something-V2; this is a historical, protocol-specific comparison.[^vivit-paper]
- **Contrasts with:** [Video Swin Transformer](video-swin-transformer.md), which jointly attends inside shifted local 3D windows rather than factorizing globally scoped temporal and spatial attention.[^video-swin-paper]

## Evidence limits

The source evaluates action classification on Kinetics-400/600, Something-Something-V2, Diving-48, and a paper-defined HowTo100M subset.[^timesformer-paper] It does not evaluate temporal localization, segmentation, streaming inference, production latency, or current state of the art. Its resource is manuscript source plus figure attachments; text was extracted from the referenced PDFs, while the attention-example PDF contains no extractable text and is represented by its manuscript caption.

[^vivit-paper]: [ViViT: A Video Vision Transformer](../raw/ViViT/main_arxiv.tex)
[^timesformer-paper]: [Is Space-Time Attention All You Need for Video Understanding?](../raw/TimeSformer/TimeSformer_arxiv_v17.tex)
[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
