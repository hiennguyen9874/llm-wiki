---
type: Synthesis
title: R(2+1)D, SlowFast, and TCN comparison
description: A task-aware comparison of R(2+1)D and SlowFast RGB video backbones with TCN temporal sequence models.
tags: [video, action-recognition, action-segmentation, temporal-modeling, comparison]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T11:08:09+07:00 }
sources:
  - id: r2plus1d-paper
    resource: ../raw/R(2+1)D/res2_plus_1d.pdf
    title: A Closer Look at Spatiotemporal Convolutions for Action Recognition
  - id: slowfast-paper
    resource: ../raw/SlowFast/slowfast_iccv19_arxiv_final.tex
    title: SlowFast Networks for Video Recognition
  - id: ms-tcn-paper
    resource: ../raw/MS-TCN/egpaper_final.tex
    title: MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation
  - id: production-temporal-overview
    resource: ../raw/TongQuanCacPhuongPhapTemporal.md
    title: Tổng quan các phương pháp temporal
---

# R(2+1)D, SlowFast, and TCN comparison

R(2+1)D and SlowFast are end-to-end RGB video backbones principally evaluated for clip/video action recognition; SlowFast also targets person-centric action detection. TCN operates over an ordered feature sequence; the specific [MS-TCN](ms-tcn.md) model performs frame-level action segmentation. Thus their benchmark scores are not directly comparable: choose by output granularity and input pipeline, not a single accuracy ranking.[^r2plus1d-paper][^slowfast-paper][^ms-tcn-paper]

| Dimension | [R(2+1)D](r-2-plus-1-d.md) | [SlowFast](slowfast-networks.md) | TCN / [MS-TCN](ms-tcn.md) |
| --- | --- | --- | --- |
| Primary input | Short RGB clip (optionally optical-flow stream) | RGB clip at two sampling rates | Per-timestep features, e.g. I3D features in MS-TCN |
| Core temporal mechanism | 3D convolution factorized into spatial 2D then temporal 1D convolution, with ReLU | Sparse, high-capacity Slow semantics + dense, low-channel Fast motion; lateral fusion | Dilated 1D temporal convolutions; MS-TCN stacks probability-refinement stages |
| Native output/task | Clip/video action class | Clip/video class; person-centric spatiotemporal action detection | Class for every frame/timestep (segmentation) |
| Temporal detail | Learns local motion within the sampled clip | Better explicit fine-motion sampling than a single sparse pathway | Preserves full sequence resolution; receptive field is finite but grows exponentially with dilation |
| Pipeline implication | One raw-video backbone; relatively simple conceptual design | One raw-video backbone but dual-rate data path and fusion | Usually a temporal head after feature extraction, rather than a replacement for RGB backbone |
| Best fit | Strong conventional baseline for trimmed-clip recognition | Recognition/detection where fine motion is material and added compute is acceptable | Boundary-aware, framewise labeling; track-feature real-time pipelines when raw RGB semantics are already extracted |

## Evidence and trade-offs

- **R(2+1)D:** factorization approximately preserves a comparable 3D-layer parameter budget while adding a nonlinearity. In the source's 16-frame Kinetics comparison, it reports 68.0% top-1 versus 64.2% for parameter-matched R3D; this is historical, setup-specific recognition evidence.[^r2plus1d-paper]
- **SlowFast:** the representative Fast pathway uses 8× the Slow sampling rate and 1/8 its channel capacity. In a Kinetics-400 ablation, fusion improved 4×16 R50 Slow-only from 72.6% to 75.6% top-1, while increasing cost from 27.3 to 36.1 GFLOPs/view; on AVA v2.1 it improved validation mAP from 19.0 to 24.2. These results support its motion-sensitive recognition/detection role, not segmentation performance.[^slowfast-paper]
- **TCN / MS-TCN:** MS-TCN uses acausal dilated convolutions and future frames, so the cited model is not an online/causal solution as-is. Its multi-stage probability refinement and smoothing loss directly address over-segmentation; the cited 50Salads results use pre-extracted I3D features at 15 FPS.[^ms-tcn-paper]

## Selection guide

1. Need **one label for a short trimmed clip**: start with R(2+1)D for a straightforward factorized-3D baseline; prefer SlowFast when rapid motion is important and its extra dual-path computation is justified.
2. Need **a label and boundary at each frame**: use a TCN segmentation head such as MS-TCN, with a visual feature backbone. Do not substitute R(2+1)D or SlowFast alone and expect framewise segments.
3. Need **real-time behavior over detector/tracker trajectories**: a generic TCN over per-track features is documented as a parallel, real-time-friendly option, but its reach is bounded by receptive field. This is draft operational guidance, not a measured comparison with the two RGB backbones.[^production-temporal-overview]
4. Need **strict online inference**: neither the cited MS-TCN configuration nor arbitrary clip models automatically satisfies causality; constrain temporal convolutions/sampling to past context and measure latency separately.

## Relationships

- **Compares:** [R(2+1)D](r-2-plus-1-d.md), [SlowFast Networks](slowfast-networks.md), and [MS-TCN](ms-tcn.md).
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md), whose recognition, detection, and segmentation outputs are distinct.
- **Uses:** [Production temporal video analytics](production-temporal-video-analytics.md) for the draft per-track TCN deployment guidance.

[^r2plus1d-paper]: [A Closer Look at Spatiotemporal Convolutions for Action Recognition](../raw/R\(2+1\)D/res2_plus_1d.pdf)
[^slowfast-paper]: [SlowFast Networks for Video Recognition](../raw/SlowFast/slowfast_iccv19_arxiv_final.tex)
[^ms-tcn-paper]: [MS-TCN: Multi-Stage Temporal Convolutional Network for Action Segmentation](../raw/MS-TCN/egpaper_final.tex)
[^production-temporal-overview]: [Tổng quan các phương pháp temporal](../raw/TongQuanCacPhuongPhapTemporal.md)
