---
type: Concept
title: ViViT (Video Vision Transformer)
description: A family of pure-Transformer video classifiers that tokenizes video as frames or tubelets and offers four space–time attention designs.
tags: [video, action-recognition, transformer, attention, transfer-learning]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T09:54:47+07:00 }
sources:
  - id: vivit-paper
    resource: ../raw/ViViT/main_arxiv.tex
    title: "ViViT: A Video Vision Transformer"
---

# ViViT (Video Vision Transformer)

ViViT is a family of pure-Transformer models for video classification. It represents a clip as either independently embedded frame patches or spatiotemporal tubelets, then trades full space–time attention for several spatial/temporal factorization designs when the video token sequence is too costly.[^vivit-paper]

## Tokenization and model variants

Uniform frame sampling applies a shared ViT-style 2D patch embedding to sampled frames and concatenates the resulting tokens. Tubelet embedding instead linearly projects non-overlapping $t \times h \times w$ video volumes; smaller tubelets yield more tokens and more computation, while allowing temporal fusion during tokenization.[^vivit-paper]

The paper evaluates four variants:

1. **Spatiotemporal attention (Model 1):** every layer attends jointly over all video tokens, giving direct global interactions but quadratic token cost.
2. **Factorised encoder (Model 2):** a spatial Transformer encodes each frame or temporal index, then a temporal Transformer combines the resulting per-index representations. This is late temporal fusion, with attention scaling as $\mathcal{O}((n_h n_w)^2 + n_t^2)$ rather than $\mathcal{O}((n_t n_h n_w)^2)$.[^vivit-paper]
3. **Factorised self-attention (Model 3):** each layer applies spatial attention and then temporal attention, retaining per-layer spatiotemporal interaction at the factorised complexity but adding an attention module and parameters.[^vivit-paper]
4. **Factorised dot-product attention (Model 4):** attention heads are split between spatial and temporal neighborhoods, preserving Model 1's parameter count at factorised complexity.[^vivit-paper]

## Initialization and regularization

To transfer an image-pretrained ViT to video, the paper repeats 2D positional embeddings over time. For tubelets, its *central-frame initialization* places the pretrained 2D embedding filter only at the central temporal position and zeroes the others; on the reported ViViT-B Kinetics experiment, it reached 79.2% top-1, versus 77.6% for inflated filters and 78.5% for uniform frame sampling.[^vivit-paper]

The source also reports that ImageNet-pretrained ViViT still overfit smaller Epic Kitchens and Something-Something-V2 datasets. In its Epic Kitchens factorised-encoder ablation, progressive Kinetics initialization, stochastic depth, temporally consistent RandAugment, label smoothing, and Mixup increased action top-1 from 38.4% to 43.7%.[^vivit-paper] These are training-recipe results under the paper's models and protocols, not a general ranking of tokenizers or regularizers.

## Accuracy–efficiency evidence

With a ViViT-B/16x2 configuration, Model 1 reported 80.0% Kinetics-400 top-1 at 455.2 GFLOPs and 58.9 ms TPU-v3 inference time; the factorised encoder reported 78.8%, 284.4 GFLOPs, and 17.4 ms. On Epic Kitchens action accuracy, the factorised encoder reported 43.7%, slightly above Model 1's 43.1%.[^vivit-paper] The factorised encoder's temporal Transformer also outperformed its average-pooling counterpart by 3.0 points on Kinetics-400 and 4.9 points on Epic Kitchens in that ablation.[^vivit-paper]

For the source's historical multi-view benchmarks, ViViT-L/16x2 Factorised Encoder reported 81.7% Kinetics-400 top-1, 82.9% on Kinetics-600, 44.0% Epic Kitchens action top-1, and 65.9% Something-Something-V2 top-1.[^vivit-paper] The source directly compares its SSv2 result with concurrent TimeSformer-HR (62.5%); this is a protocol-specific historical comparison, not a current model ranking.[^vivit-paper]

## Relationships

- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) for clip-level action recognition.
- **Supports:** [Long-video temporal modeling](long-video-temporal-modeling.md) by separating per-index spatial processing from temporal aggregation so longer clips can be processed; it does not model an unbounded video in one pass.[^vivit-paper]
- **Contrasts with:** [TimeSformer](timesformer.md). Both are pure video Transformers with factorized space–time computation, but ViViT's factorised encoder first reduces each temporal index to one representation whereas TimeSformer applies divided attention over patch tokens.[^vivit-paper]
- **Uses:** [Video temporal representation learning](video-temporal-representation-learning.md) through ImageNet-21K or JFT image-pretrained ViT initialization.[^vivit-paper]

## Evidence limits

The source evaluates video classification on Kinetics-400/600, Epic Kitchens-100, Moments in Time, and Something-Something-V2.[^vivit-paper] It does not evaluate temporal localization, action segmentation, streaming inference, production latency, or arbitrary-length-video memory. The manuscript source, its included tables, and all referenced figure PDFs were inspected; figure PDFs supplied architecture diagrams and plotted trends, while their precise plotted values are not treated as claims unless stated in the manuscript text or tables.

[^vivit-paper]: [ViViT: A Video Vision Transformer](../raw/ViViT/main_arxiv.tex)
