---
type: Concept
title: Multiscale Vision Transformers (MViT)
description: A staged video and image Transformer that pools token resolution while expanding channel capacity through its hierarchy.
tags: [video, image-recognition, action-recognition, transformer, attention, multiscale]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:57:51+07:00 }
sources:
  - id: mvit-paper
    resource: ../raw/MViT/mvit_arxiv.tex
    title: Multiscale Vision Transformers
---

# Multiscale Vision Transformers (MViT)

MViT is a Transformer architecture for video and image recognition that builds a feature pyramid: later stages have fewer spatiotemporal tokens but wider channels. Its multi-head pooling attention (MHPA) pools queries to change output resolution and pools keys and values to reduce attention cost, making a dense early video representation practical without keeping that resolution throughout the network.[^mvit-paper]

## Architecture

MViT divides the network into stages with a constant channel dimension and spatiotemporal resolution within each stage. At a stage transition, it reduces token resolution and increases channel capacity; the paper describes this as moving from fine spacetime/coarse channels to coarse spacetime/richer channels.[^mvit-paper]

MHPA first makes the usual query, key, and value projections, then independently pools them. Query pooling shortens the output sequence and is used at the first block of a new stage. Key–value pooling leaves the output length unchanged but reduces the keys and values participating in attention; it is used to control the quadratic attention term. Because stage transitions change both token count and channel width, the residual path is pooled and, for width changes, projected after layer normalization.[^mvit-paper]

The video input is embedded as overlapping spatiotemporal cubes rather than only per-frame 2D patches. The reported default uses separate spatial and temporal positional embeddings; its ablation found this configuration stronger than no, spatial-only, or joint space-time embeddings under that protocol.[^mvit-paper]

## Paper-specific evidence

The source trains its MViT video models from random initialization on Kinetics without external image pretraining. Its MViT-B 16×4 configuration reported 78.4% Kinetics-400 top-1 at 70.5 GFLOPs per clip and 36.6M parameters; the 32×3 configuration reported 80.2% with higher input/inference cost.[^mvit-paper] These are historical, paper-protocol-specific results rather than a current architecture ranking.

In a Kinetics-400 ablation using max pooling, randomly shuffling input-frame order reduced MViT-B top-1 from 77.2% to 70.1%, while the compared single-scale ViT-B changed from 68.5% to 68.4%.[^mvit-paper] This supports temporal-order sensitivity for these models and data; it does not establish that MViT captures every temporal dependency.

The paper also evaluates MViT as a Kinetics-pretrained backbone for Something-Something-V2 and Charades classification and for AVA human-action detection. Its AVA detector reinterprets MViT tokens as a spatiotemporal feature map and applies a video-adapted RoI head.[^mvit-paper]

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for video classification and frame-centered human-action detection.
- **Supports:** [Long-video temporal modeling](long-video-temporal-modeling.md) with hierarchical token compression, while the source only evaluates fixed clips rather than arbitrary-length video.[^mvit-paper]
- **Contrasts with:** [TimeSformer](timesformer.md) and [ViViT (Video Vision Transformer)](vivit.md), concurrent video-Transformer approaches that the source compares under historical, non-uniform training and inference protocols.[^mvit-paper]

## Evidence limits

The source evaluates fixed-clip video recognition, transfer to selected video tasks, and static ImageNet classification.[^mvit-paper] It does not demonstrate lossless long-video memory, temporal action intervals, streaming inference, production latency, or current state of the art. The manuscript, its tables, and all referenced figure attachments were inspected; figure plots are used only for trends already stated in the manuscript, not for unstated precise values.

[^mvit-paper]: [Multiscale Vision Transformers](../raw/MViT/mvit_arxiv.tex)
