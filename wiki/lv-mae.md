---
type: Concept
title: LV-MAE
description: A self-supervised long-video representation learner that reconstructs masked sequences of frozen short-video embeddings.
tags: [video, long-context, representation-learning, self-supervised-learning, masked-autoencoder, transformer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:33:34+07:00 }
sources:
  - id: lv-mae-paper
    resource: ../raw/LV-MAE/main.tex
    title: "LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders"
---

# LV-MAE

LV-MAE learns a long-video representation in two stages: a frozen short-video encoder maps consecutive segments to one embedding each, then an asymmetric masked autoencoder reconstructs masked embeddings across the segment sequence. This separates short-span visual semantics from long-range dependency modeling and makes the Transformer operate on clip tokens rather than frame patches.[^lv-mae-paper]

## Architecture and objective

The source partitions a video into consecutive five-second segments and extracts one embedding per segment with a frozen video–text model such as LanguageBind or InternVideo2. During pretraining, the Transformer encoder receives only the unmasked embeddings; the shallower decoder combines the visible latent tokens, learned mask tokens, and positional embeddings to reconstruct the full sequence. Training minimizes MSE only on the masked target embeddings, and the decoder is discarded for downstream use.[^lv-mae-paper]

The reported implementation caps a sequence at 256 segment tokens, pads shorter videos with attention-masked `[PAD]` tokens, and adds a `[CLS]` token for downstream classification. At the stated five-second segment length, that cap represents about 21 minutes 20 seconds; the authors describe increasing it as a possible extension rather than evaluating it.[^lv-mae-paper]

LV-MAE compares random masking with a semantic strategy that masks embeddings having the lowest cosine similarity to their immediately preceding embedding. In the reported LVU attentive-probing ablation, random masking peaked at 40% and semantic masking at 50%; these are paper- and dataset-specific settings, not general masking-ratio guidance.[^lv-mae-paper]

## Reported transfer evidence

With frozen-backbone attentive probing, the LanguageBind variant reports 63.4 average classification accuracy across the seven classification tasks in LVU, while the InternVideo2 variant reports 92.72% on COIN and 93.24% on Breakfast. The LanguageBind variant's 91.55% Breakfast result is below the cited VideoMamba result of 96.9%; these benchmark values do not establish a general ranking because feature encoders, pretraining data, task heads, and fine-tuning budgets differ.[^lv-mae-paper]

The source's ablation reports that capping pretraining clips at five minutes reduced LVU average accuracy from 63.4 to 55.58, and that its five-second segments outperformed the tested 10-second, 15-second, and shot-based variants. This supports the authors' design under their LVU protocol; it does not show retention of every short event or arbitrary-duration operation.[^lv-mae-paper]

## Reconstruction inspection

Because embedding targets are not directly visualizable, the source uses a proxy: it generates captions for short MovieClips segments, embeds captions with LanguageBind, and retrieves nearest captions for reconstructed embeddings by cosine similarity. The examples show semantically related but more abstract captions; this is qualitative inspection of an embedding-space proxy, not direct evidence that each reconstruction faithfully preserves the original video content.[^lv-mae-paper]

## Relationships

- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through masked reconstruction of clip-level embeddings.[^lv-mae-paper]
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) through hierarchical temporal compression from video segments to one embedding token each.[^lv-mae-paper]
- **Uses:** [InternVideo2](internvideo2.md) as one reported frozen short-video embedding encoder.[^lv-mae-paper]
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) through long-video action and procedural classification benchmarks, not temporal interval localization or framewise segmentation.[^lv-mae-paper]
- **Contrasts with:** [VideoMAE](videomae.md): both use asymmetric masked autoencoding, but LV-MAE reconstructs clip embeddings across a long video whereas VideoMAE reconstructs masked video cubes from a short clip.[^lv-mae-paper]

## Evidence limits

The source reports classification and regression experiments on LVU plus classification on COIN and Breakfast. It does not evaluate streaming use, temporal action intervals, framewise segmentation, or a sequence longer than the approximately 20-minute benchmark inputs under its 256-token setting.[^lv-mae-paper] The manuscript text and its five figure PDFs plus one PNG were inspected; figure examples are treated as qualitative evidence and exact results are taken from the paper's tables and prose.

[^lv-mae-paper]: [LV-MAE: Learning Long Video Representations through Masked-Embedding Autoencoders](../raw/LV-MAE/main.tex)
