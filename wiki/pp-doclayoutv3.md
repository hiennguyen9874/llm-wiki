---
type: Model
title: PP-DocLayoutV3
description: PP-DocLayoutV3 jointly predicts layout classes, regions, instance masks, and reading order with an RT-DETR-derived Transformer and pairwise precedence ranking.
tags: [layout-analysis, reading-order, document-parsing, instance-segmentation, object-detection]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:32:39Z }
sources:
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: "PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training"
  - id: paddleocr-vl-1-5-report
    resource: ../raw/2601.21957_PaddleOCR-VL-1.5/main.tex
    title: "PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing"
  - id: glm-ocr-report
    resource: ../raw/2603.10910_GLM-OCR/main.tex
    title: GLM-OCR Technical Report
  - id: falcon-perception-report
    resource: ../raw/2603.27365_FalconPerception/main.tex
    title: Falcon Perception
  - id: rt-doclayout-report
    resource: ../raw/2606.23344_RT-DocLayout/main.tex
    title: "RT-DocLayout: Real-Time End-to-End Document Layout Analysis with Reading Order in the Wild"
---

# PP-DocLayoutV3

PP-DocLayoutV3 is the layout-analysis stage of [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md). Its academic report calls it **RT-DocLayout**; it extends RT-DETR to jointly classify, localize, segment, and order document elements, including distorted page regions, in one non-autoregressive forward pass.[^rt-doclayout-report]

## Architecture and ordering

The model uses a PP-HGNetV2 backbone and Transformer layers with class, box, mask, and order heads. Each object query produces a class, axis-aligned box, pixel-level instance mask, and order relations; separate post-processing converts these outputs into filtered layout results.[^rt-doclayout-report]

For reading order, final-layer object-query embeddings are projected to query and key spaces, whose antisymmetrized dot products score pairwise precedence. At inference, sigmoid-transformed precedence relations are summed as incoming votes, then elements are sorted ascending by vote total.[^rt-doclayout-report]

Training uses Hungarian matching and a weighted classification, box, GIoU, binary-mask, Dice-mask, and pairwise-order objective. The order term uses generalized cross entropy with label smoothing, upweights order-neighbor pairs, and is computed only at the final decoder layer; the other tasks receive intermediate-layer supervision.[^rt-doclayout-report]

## Reported training, augmentation, and results

The authors initialize from PP-DocLayout-plus-L and jointly train detection, segmentation, and ordering for 150 epochs on more than 38,000 manually annotated document samples across 25 element categories. They use AdamW with $2×10^{-4}$ learning rate, 0.0001 weight decay, and total batch size 32.[^rt-doclayout-report]

Their online augmentation first applies intrinsic surface deformation: smooth sinusoidal mesh displacement, either along one axis or both. It then applies an extrinsic projective transform combining rotation, shear, and perspective, while retaining pixel masks and re-extracting axis-aligned boxes from transformed masks.[^rt-doclayout-report]

All results are author-reported and not independently reproduced. With PaddleOCR-VL-1.5-0.9B as recognizer, the report gives 94.50 overall on OmniDocBench v1.5 and 92.05 overall on Real5-OmniDocBench; the latter consists of 93.43 scanning, 91.25 warping, 91.76 screen-photography, 92.16 illumination, and 91.66 skew. The stated 132.1 FPS is measured on an NVIDIA A100 with batch size 32.[^rt-doclayout-report]

## Trust limits

- The bundle supplies the report, bibliography, and result/architecture figures, but no model weights, code, data, annotations, train/validation split, or evaluated outputs. The reported performance cannot be independently reproduced from local evidence.[^rt-doclayout-report]
- Although the report specifies its heads, losses, and high-level augmentation, it omits the model configuration, data split and annotation protocol, augmentation ranges, and evaluation implementation needed to reconstruct the system.[^rt-doclayout-report]

## Relationships

- **Part of:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md), supplying regions and reading order before element recognition.
- **Used by:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), which retains it unchanged for layout analysis, multipoint localization, and reading order.[^paddleocr-vl-1-6-report]
- **Supersedes:** [PP-DocLayoutV2](pp-doclayoutv2.md), replacing its separate pointer-network order stage with joint detection, segmentation, and ordering.
- **Used by:** [GLM-OCR](glm-ocr.md), which uses it for layout detection, region cropping, and reading order before parallel recognition.[^glm-ocr-report]
- **Used by:** [FalconOCR](falcon-ocr.md), which uses it for page-region detection and reading order before crop-level text, formula, and table recognition.[^falcon-perception-report]

[^paddleocr-vl-1-5-report]: Cui et al., *PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing*, local LaTeX source at [main.tex](../raw/2601.21957_PaddleOCR-VL-1.5/main.tex), including [PP-DocLayoutV3 architecture](../raw/2601.21957_PaddleOCR-VL-1.5/images/PP-DocLayoutV3.png) (accessed 2026-08-17).
[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training*, local LaTeX source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex) (accessed 2026-08-17).
[^glm-ocr-report]: Duan et al., *GLM-OCR Technical Report*, local LaTeX source at [main.tex](../raw/2603.10910_GLM-OCR/main.tex) (accessed 2026-08-17).
[^falcon-perception-report]: Falcon Vision Team, *Falcon Perception*, local LaTeX source at [main.tex](../raw/2603.27365_FalconPerception/main.tex), especially `sections/ocr.tex` (accessed 2026-08-17).
[^rt-doclayout-report]: Cui et al., *RT-DocLayout: Real-Time End-to-End Document Layout Analysis with Reading Order in the Wild*, local LaTeX source at [main.tex](../raw/2606.23344_RT-DocLayout/main.tex), including the [architecture](../raw/2606.23344_RT-DocLayout/images/RT-DocLayout.png), [augmentation diagram](../raw/2606.23344_RT-DocLayout/images/dataaug.pdf), [comparison](../raw/2606.23344_RT-DocLayout/images/RT-DocLayout-Comparison.pdf), and [robustness chart](../raw/2606.23344_RT-DocLayout/images/RT-DocLayout_radar_chart.pdf) (rendered and inspected, accessed 2026-08-17).