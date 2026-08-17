---
type: Model System
title: Falcon Perception
description: Falcon Perception is a 600M early-fusion dense Transformer that autoregressively emits instance geometry and uses specialized heads for parallel high-resolution masks.
tags: [visual-grounding, instance-segmentation, early-fusion, autoregressive-models, vision-language-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T12:00:00Z }
sources:
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
---

# Falcon Perception

Falcon Perception is a 600M-parameter, promptable open-vocabulary segmentation system built as one early-fusion Transformer rather than a separate vision encoder and decoder. It serializes each detected instance as coordinate, size, and segmentation task tokens, then uses lightweight geometry and mask heads to avoid autoregressively generating dense pixels.[^falcon-perception-report]

## Architecture and interface

Image patches attend bidirectionally to one another; text and task tokens attend to all image tokens and to prior text/task tokens causally. Thus one shared stack has encoder-like visual context and autoregressive prediction behavior. Images retain native aspect ratio up to a token budget; valid patches are scatter-packed and isolated per sample with FlexAttention.[^falcon-perception-report]

Its Chain-of-Perception output order is `<coord> → <size> → <seg>`. Coordinate and size heads predict 1,024 discrete bins, with Fourier-feature coordinate inputs and log-scaled size bins. The predicted geometry is re-injected before the mask token, resolving instance identity before segmentation. A content-aware AnyUp upsampler combines high-resolution image content with output visual features; the projected mask-token state then takes a dot product with those features to generate each high-resolution mask in parallel.[^falcon-perception-report]

## Training and reported results

The 600M model is initialized by multi-teacher distillation from DINOv3 ViT-H and SigLIP2-So400m, then trained on about 685 gigatokens. The source describes 54M images, 195M positive expressions, 488M negatives, and 570M masks, produced through VLM listing, negative mining, model-agreement filtering, and human verification. Training combines language-modeling, coordinate, size, focal/dice mask, and Gram feature-alignment losses; it uses 450GT of autoregressive scene listing, 225GT of independent-query alignment, and 10GT for long-context tuning up to 600 masks per expression.[^falcon-perception-report]

On SA-Co, the authors report 68.0 Macro-F1 against SAM 3's 62.3, but lower presence-calibration metrics (MCC 0.64 versus 0.82). On their [PBench](pbench.md), they report 57.0 average Macro-F1 and 72.6 on the dense split; the reported score exceeds SAM 3 on the dense split (58.4) and PBench spatial level (53.5 versus 31.6). These are author-reported comparisons, not independently reproduced.[^falcon-perception-report]

## Trust limits

- The local bundle provides an author report, bibliography, and qualitative figures, but no weights, implementation, training data, inference configuration, PBench data, or evaluation code. Architectural, data-scale, and performance claims are not independently reproducible from the bundle.[^falcon-perception-report]
- PBench is internally built by members who also trained Falcon Perception. Its construction rules are described, but its examples and annotations are unavailable, so its claimed capability isolation and comparisons cannot be audited independently.[^falcon-perception-report]
- The source explicitly attributes its lower SA-Co calibration to the generative interface and presents reinforcement-learning gains as preliminary; neither the RL procedure nor its results are supplied.[^falcon-perception-report]

## Relationships

- **Uses:** [PBench](pbench.md) for capability-level segmentation evaluation.
- **Related approach:** [Rex-Omni](rex-omni.md) also uses autoregressive structured perception outputs and proposes GRPO for output behavior, but Falcon Perception emits geometry plus parallel masks rather than quantized coordinate sequences.[^falcon-perception-report]
- **Shares architecture with:** [FalconOCR](falcon-ocr.md), which applies the early-fusion stack to element-level OCR in a separate two-stage document pipeline.[^falcon-perception-report]

[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local LaTeX source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), including referenced section files and figures (accessed 2026-08-17).