---
type: Concept
title: VideoMAE
description: A self-supervised video-pretraining method that reconstructs heavily tube-masked video cubes with an asymmetric Vision Transformer autoencoder.
tags: [video, representation-learning, self-supervised-learning, masked-autoencoder, transformer]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:34:53+07:00 }
sources:
  - id: videomae-paper
    resource: ../raw/VideoMAE/main.tex
    title: "VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training"
  - id: videomaev2-paper
    resource: ../raw/2303.16727_VideoMAEV2/videomae_v2.tex
    title: "VideoMAE V2: Scaling Video Masked Autoencoders with Dual Masking"
---

# VideoMAE

VideoMAE pretrains a plain Vision Transformer on unlabeled video by reconstructing normalized pixels of heavily masked spatiotemporal cubes. It combines temporal downsampling, a tube mask shared across frames, and an asymmetric encoder–decoder: only the visible tokens enter the encoder during pretraining, and the decoder is discarded for downstream fine-tuning.[^videomae-paper]

## Pretraining design

A video is temporally sampled, split into $2 \times 16 \times 16$ cubes, and embedded as tokens. For the paper's 16-frame ViT-B example, this produces $8 \times 196$ tokens; the encoder has 12 joint space–time-attention blocks and the decoder has four smaller blocks.[^videomae-paper]

Tube masking samples each spatial mask location once and applies that mask across the temporal axis. The authors use 90% masking by default on Kinetics-400 and Something-Something-V2 (and 75% on UCF101 and HMDB51). Their stated rationale is that video redundancy permits a much higher masking ratio than image MAE, while sharing the mask over time removes adjacent-frame copies of a masked cube that could otherwise make reconstruction a low-level correspondence shortcut.[^videomae-paper]

The decoder receives encoded visible tokens plus learned mask tokens and predicts the masked, normalized cube pixels. The pretraining loss is MSE over masked tokens; extreme masking also reduces the number of tokens processed by the encoder, mitigating its joint-attention cost during pretraining.[^videomae-paper]

## Paper-specific evidence

In the source's 16-frame ViT-B, 800-epoch ablation, 90% tube masking reported 69.6% top-1 on Something-Something-V2 and 80.0% on Kinetics-400. At the same 90% ratio, random masking reported 68.3% and 79.5%; frame masking reported 61.5% and 76.5%, respectively.[^videomae-paper]

Using only each target dataset's unlabeled training clips for pretraining, the same ViT-B configuration reported 91.3% on UCF101 and 62.6% on HMDB51, versus 81.7% and 39.2% for the paper's MoCo v3 comparison. These are paper- and protocol-specific results, not a general ranking of self-supervised methods.[^videomae-paper]

The source also transfers a Kinetics-400-pretrained ViT-B to AVA action detection, reporting 26.7 mAP without an intervening labeled-Kinetics fine-tuning stage and 31.8 mAP with it. This supports use as a pretrained backbone for frame-centered human-action detection, not native temporal-interval localization.[^videomae-paper]

## Relationships

- **Extended by:** [VideoMAE V2](videomae-v2.md), which adds decoder masking, mixed-source scaling, and progressive supervised adaptation while retaining encoder tube masking.[^videomaev2-paper]
- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through masked pixel reconstruction on unlabeled clips.[^videomae-paper]
- **Applies to:** [Temporal action understanding](temporal-action-understanding.md) through downstream action classification and AVA human-action detection.[^videomae-paper]
- **Contrasts with:** [ViViT (Video Vision Transformer)](vivit.md). Both can use joint space–time attention over video tokens, but VideoMAE specifies a self-supervised pretraining objective and asymmetric reconstruction architecture rather than a family of supervised video-classification encoders.[^videomae-paper]
- **Contrasts with:** [Video Swin Transformer](video-swin-transformer.md), whose architecture limits attention to shifted local 3D windows; VideoMAE's described ViT encoder uses joint attention over its retained visible tokens.[^videomae-paper]

## Evidence limits

The manuscript evaluates fixed clips on Kinetics-400, Something-Something-V2, UCF101, HMDB51, and AVA. It does not establish streaming latency, arbitrary-duration memory, framewise segmentation, or temporal action intervals, and its 2022 comparisons are not evidence of current state of the art.[^videomae-paper] The manuscript text, bibliography files, and all 17 supplied figure PDFs were inspected; plot values are used only where extractable or corroborated by tables/text.

[^videomae-paper]: [VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training](../raw/VideoMAE/main.tex)
[^videomaev2-paper]: [VideoMAE V2: Scaling Video Masked Autoencoders with Dual Masking](../raw/2303.16727_VideoMAEV2/videomae_v2.tex)
