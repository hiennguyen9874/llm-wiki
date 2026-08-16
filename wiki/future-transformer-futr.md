---
type: Concept
title: Future Transformer (FUTR)
description: An encoder-decoder Transformer for long-term action anticipation that predicts an ordered sequence of future action labels and durations in parallel.
tags: [video, action-anticipation, long-term-anticipation, transformer, parallel-decoding]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:17:50+07:00 }
sources:
  - id: futr-paper
    resource: ../raw/FutureTransformer/main.tex
    title: Future Transformer for Long-term Action Anticipation
---

# Future Transformer (FUTR)

Future Transformer (FUTR) is an end-to-end model for long-term action anticipation. Given observed video features, it globally attends over sampled past-frame tokens and a fixed ordered set of future-action queries, then predicts all future action labels and normalized durations in parallel rather than generating actions autoregressively.[^futr-paper]

## Task and outputs

For a video of $T$ frames, the paper observes the first $\alpha T$ frames and anticipates framewise actions over the next $\beta T$ frames. It represents that future as an ordered sequence of action segments: each segment has a class and a duration, and the predicted segments are decoded into framewise labels for evaluation.[^futr-paper]

FUTR uses $M$ learned action queries whose fixed order corresponds to the future-action order. Each query emits one of $K$ action classes or `NONE`, plus a duration; `NONE` pads unused queries. This ordered formulation differs from a DETR-style unordered set with Hungarian matching.[^futr-paper]

## Architecture and training

The encoder projects sampled, pre-extracted visual features and applies global self-attention with learned one-dimensional positional embeddings. An auxiliary action-segmentation head classifies observed frames, so segmentation loss teaches the encoder to distinguish past actions.[^futr-paper]

The decoder starts from zero states plus learned action queries. Its self-attention models relations among potential future actions, and cross-attention reads the encoder's past-frame representations. The model jointly optimizes past-frame segmentation cross-entropy, future-action cross-entropy, and L2 duration regression; predicted durations are Gaussian-normalized to sum to one.[^futr-paper]

## Reported evidence and limits

On Breakfast using I3D features, FUTR reports mean-over-classes accuracy of 32.27%, 29.88%, 27.49%, and 25.87% for prediction ratios $\beta=0.1, 0.2, 0.3, 0.5$ after observing $\alpha=0.3$ of a video. On 50 Salads, it leads the reported visual-feature comparisons in six of eight $(\alpha,\beta)$ settings, but does not lead every setting.[^futr-paper]

Its Breakfast ablation reports 3.91 ms per-video inference for parallel, bidirectional query decoding versus 14.68 ms for its autoregressive variant on one RTX 3090, excluding loading and after warm-up. This is implementation- and hardware-specific rather than a general latency guarantee.[^futr-paper]

The paper uses pre-extracted I3D features for its two long-term benchmarks and global attention over sampled inputs. It therefore does not establish raw-frame end-to-end efficiency or scalable full attention over arbitrary-duration video. The authors also identify attention computation and memory as efficiency limits and suggest linear or sparse attention as future work.[^futr-paper]

## Evidence scope

This compilation covers `main.tex`, all included main and supplementary TeX sections, tables, and figure captions. Visual-only figure PDFs were not independently interpreted.

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) as long-term, framewise action anticipation.
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through global temporal attention over sampled observed features; this differs from arbitrary-duration memory or retrieval.
- **Uses:** [Inflated 3D ConvNets (I3D)](inflated-3d-convnets-i3d.md) as the reported pre-extracted feature source for Breakfast and 50 Salads.[^futr-paper]

[^futr-paper]: [Future Transformer for Long-term Action Anticipation](../raw/FutureTransformer/main.tex)
