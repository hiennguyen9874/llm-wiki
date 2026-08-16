---
type: Concept
title: Video Swin Transformer
description: A hierarchical video Transformer that uses alternating local and shifted 3D attention windows to model spacetime efficiently.
tags: [video, action-recognition, transformer, attention, local-attention, transfer-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:03:14+07:00 }
sources:
  - id: video-swin-paper
    resource: ../raw/VideoSwin/main.tex
    title: Video Swin Transformer
---

# Video Swin Transformer

Video Swin Transformer adapts image Swin Transformer to video by restricting self-attention to local non-overlapping 3D windows and alternating regular with shifted window partitions. This provides cross-window spatiotemporal connections without global attention over every video token, while preserving Swin's hierarchical stages and ability to initialize from image-pretrained weights.[^video-swin-paper]

## Architecture

The input is partitioned into $2 \times 4 \times 4$ RGB tubelets and linearly embedded. The architecture has four stages; each patch-merging transition downsamples only spatially by $2 \times 2$, leaving temporal resolution unchanged. A block applies layer-normalized 3D window multi-head self-attention, a residual connection, then a layer-normalized two-layer GELU MLP and another residual connection.[^video-swin-paper]

For a token volume of $T' \times H' \times W'$ and a window of $P \times M \times M$, attention is computed independently inside non-overlapping 3D windows. The following block shifts its partition by $(P/2, M/2, M/2)$ along time, height, and width, allowing neighboring regular windows to exchange information across the pair of blocks. The paper follows Swin's efficient batch computation so the shifted configuration retains the original number of windows for computation.[^video-swin-paper]

Each head adds a learned 3D relative-position bias. Rather than store the full pairwise bias, the model parameterizes a $(2P-1) \times (2M-1) \times (2M-1)$ table indexed by temporal and spatial relative offsets.[^video-swin-paper] The reported default has temporal window size $P=8$, spatial window size $M=7$, head query dimension 32, and MLP expansion ratio 4.[^video-swin-paper]

## Image-to-video initialization

To transfer image-pretrained Swin weights, the 2D patch-embedding weights are duplicated along the two-frame tubelet dimension and scaled by one half; 2D relative-position biases are duplicated along the temporal-relative-position axis. The paper reports better Kinetics-400 results when the pretrained backbone learning rate is one tenth of the newly initialized classifier head's rate, an observation limited to its training setup.[^video-swin-paper]

## Paper-specific evidence

On the source's Kinetics-400 Swin-T ablation, joint local 3D attention achieved 78.8% top-1 at 88 GFLOPs, versus 78.5% at 95 GFLOPs for its factorized variant and 76.4% at 83 GFLOPs for a spatial-Swin-plus-temporal-encoder split variant.[^video-swin-paper] Removing all 3D shifting reduced Swin-T top-1 from 78.8% to 78.1%; retaining spatial but not temporal shifting yielded 78.5%.[^video-swin-paper]

For its historical multi-view evaluation, ImageNet-21K-pretrained Swin-L at 384-pixel resolution reported 84.9% Kinetics-400 and 86.1% Kinetics-600 top-1, and Kinetics-400-pretrained Swin-B reported 69.6% on Something-Something-V2.[^video-swin-paper] These results are protocol-specific historical measurements, not a current benchmark ranking or evidence for temporal localization or arbitrary-length-video memory.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) as a fixed-clip backbone for video-level action recognition.[^video-swin-paper]
- **Supports:** [Long-video temporal modeling](long-video-temporal-modeling.md) through local spatiotemporal attention, although the source evaluates clips rather than persistent memory or retrieval over arbitrary-duration videos.[^video-swin-paper]
- **Contrasts with:** [TimeSformer](timesformer.md) and [ViViT (Video Vision Transformer)](vivit.md). Those approaches reduce global attention by factorizing temporal and spatial attention, whereas Video Swin jointly attends within local 3D neighborhoods.[^video-swin-paper]

## Evidence limits

The source evaluates action classification on Kinetics-400, Kinetics-600, and Something-Something-V2. It does not evaluate temporal action intervals, frame-level segmentation, streaming inference, production latency, or contemporary state of the art.[^video-swin-paper] The manuscript, included tables, 3D-shift image, and all referenced architecture PDFs were inspected; PDF text was extracted for the architecture and block diagrams, while visual geometry is represented by the manuscript's accompanying prose and captions.

[^video-swin-paper]: [Video Swin Transformer](../raw/VideoSwin/main.tex)
