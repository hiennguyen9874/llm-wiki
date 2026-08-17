---
type: Concept
title: VideoMAE V2
description: A scalable video masked-autoencoder framework that masks both encoder and decoder tokens, then progressively adapts a billion-parameter ViT through unlabeled and labeled hybrid video datasets.
tags: [video, representation-learning, self-supervised-learning, masked-autoencoder, transformer, foundation-models]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:34:53+07:00 }
sources:
  - id: videomaev2-paper
    resource: ../raw/2303.16727_VideoMAEV2/videomae_v2.tex
    title: "VideoMAE V2: Scaling Video Masked Autoencoders with Dual Masking"
  - id: internvideo2-paper
    resource: ../raw/InternVideo2/main.tex
    title: "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
---

# VideoMAE V2

VideoMAE V2 scales masked video pretraining by retaining VideoMAE's 90% encoder tube masking while also reducing decoder tokens. A running-cell decoder mask selects a spatially and temporally distributed subset for reconstruction, and loss is applied only where selected decoder targets were hidden from the encoder. The framework combines this dual masking with a 1.011B-parameter ViT-g and progressive training on mixed unlabeled and labeled video datasets.[^videomaev2-paper]

## Dual masking

The encoder processes visible tube tokens as in [VideoMAE](videomae.md). The decoder concatenates encoder outputs with learned mask tokens only at locations selected by its running-cell pattern; the default decoder mask ratio is 50%. Unlike encoder masking, which removes temporally correlated tubes to limit information leakage, decoder masking aims to retain a distributed subset that covers the clip while avoiding full reconstruction.[^videomaev2-paper]

In the paper's ViT-B Something-Something-V2 ablation, dual masking reduced pretraining cost from 35.48 to 25.87 GFLOPs, feature-map memory from 631M to 328M, and 64-GPU runtime from 28.4 to 15.9 hours, while reported top-1 changed from 70.28% to 70.15%. For ViT-g, reported runtime fell from an estimated 356 hours to 241 hours and feature-map memory from 1753M to 1050M. These are training measurements under the paper's implementation, not general inference-speed results; the decoder is discarded for downstream use.[^videomaev2-paper]

## Scaling and progressive training

The largest encoder is a joint space-time-attention ViT-g with 40 blocks, width 1408, 16 heads, 14×14 spatial patches, and 1,011M parameters. Its pretraining decoder remains shallow at four blocks and 512 channels.[^videomaev2-paper]

Training proceeds in three stages:[^videomaev2-paper]

1. **Self-supervised pretraining:** 1,200 epochs on UnlabeledHybrid, reported as 1.348M clips: Kinetics-710 (658k), Something-Something-V2 (169k), AVA cuts (21k), a 250k subset of WebVid2M, and 250k self-collected Instagram videos.
2. **Supervised post-pretraining:** intermediate fine-tuning on LabeledHybrid/Kinetics-710, formed by merging Kinetics-400/600/700 labels and deduplicating videos; the paper reports 658k training videos across 710 categories.
3. **Task-specific fine-tuning:** adaptation to action classification, spatial action detection, or temporal action detection.

The source reports that Kinetics post-pretraining improved Kinetics-400 results but worsened Something-Something-V2, so progressive supervised adaptation is not uniformly beneficial across target domains.[^videomaev2-paper]

## Reported transfer evidence

At the standard 16×224² input, VideoMAE V2-g reports 88.5% multi-view top-1 on Kinetics-400 after K710 post-pretraining and 77.0% on Something-Something-V2 without that post-pretraining. The 90.0% Kinetics-400 result uses a much larger 64×266² input and six inference views at a reported 160.30 TFLOPs, so it should not be compared as the standard model configuration.[^videomaev2-paper]

For spatial action detection, the source reports 42.6 mAP on AVA and 43.9 mAP on AVA-Kinetics using a person-detection-plus-action-classification pipeline. For temporal action detection, it replaces ActionFormer's I3D features with VideoMAE V2 features and reports average mAP of 69.6 on THUMOS14 and 18.2 on FineAction without optical flow. These values support the specific backbone/head pipelines; VideoMAE V2 itself does not decode person boxes or temporal intervals.[^videomaev2-paper]

## Evidence and governance limits

The manuscript supplies no matched ablation that isolates dual masking, model size, corpus scale/diversity, and progressive supervision as independent causes of the final transfer gains. Its large-scale results therefore support the combined training system rather than a clean scaling law.[^videomaev2-paper]

UnlabeledHybrid includes scraped WebVid and Instagram material, but the source does not provide enough licensing, consent, filtering, or demographic detail to audit the full corpus. The benchmark evidence covers sampled clips and downstream heads, not streaming latency, persistent long-video memory, or direct interval decoding.[^videomaev2-paper]

## Relationships

- **Extends:** [VideoMAE](videomae.md) with decoder masking, larger mixed-source pretraining, and progressive supervised adaptation.[^videomaev2-paper]
- **Instantiates:** [Video temporal representation learning](video-temporal-representation-learning.md) through scalable masked pixel reconstruction.[^videomaev2-paper]
- **Supports:** [Temporal action understanding](temporal-action-understanding.md) as a pretrained backbone transferred to recognition, spatial detection, and temporal localization heads.[^videomaev2-paper]
- **Uses:** [ActionFormer](actionformer.md) as the temporal action localization head in THUMOS14 and FineAction evaluations.[^videomaev2-paper]
- **Used by:** [InternVideo2](internvideo2.md), which reports VideoMAE V2-g as a motion-aware stage-1 teacher.[^internvideo2-paper]
- **Compared in:** [Video backbones and encoders comparison](video-backbones-and-encoders-comparison.md).

[^videomaev2-paper]: [VideoMAE V2: Scaling Video Masked Autoencoders with Dual Masking](../raw/2303.16727_VideoMAEV2/videomae_v2.tex)
[^internvideo2-paper]: [InternVideo2: Scaling Foundation Models for Multimodal Video Understanding](../raw/InternVideo2/main.tex)
