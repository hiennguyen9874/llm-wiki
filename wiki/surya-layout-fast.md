---
type: Model
title: Surya Layout (fast)
description: Surya Layout (fast) is a compact object detector for document regions and reading order that can replace Surya's VLM-based layout predictor.
tags: [layout-analysis, object-detection, document-parsing, reading-order, ocr]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:15:39Z }
sources:
  - id: surya-layout-fast-card
    resource: ../raw/surya_layout2.md
    title: Surya Layout (fast) model card
---

# Surya Layout (fast)

Surya Layout (fast) is a compact document-layout object detector for the Surya OCR package. It identifies page regions and returns their labels, bounding boxes, and reading-order positions; the model card positions it as a faster drop-in alternative to Surya's VLM-based layout predictor.[^surya-layout-fast-card]

## Capabilities and output

The predictor detects document regions including text, tables, figures, headers, captions, and equations. For each bounding box, its documented Python interface exposes `label`, `bbox` as `[x0, y0, x1, y1]`, and `position` as the reading-order index.[^surya-layout-fast-card]

## Operation

Install the package with `pip install surya-ocr`, then initialize `FastLayoutPredictor` with the checkpoint `hf://datalab-to/surya_layout2` and pass it page images. The card also documents `FAST_LAYOUT_MODEL_CHECKPOINT` as the environment variable for making this checkpoint the default for Surya's CLI and library.[^surya-layout-fast-card]

The source states that the detector runs on CPU or GPU, but supplies no hardware configuration, latency, throughput, accuracy, training-data, or evaluation results.[^surya-layout-fast-card]

## Licensing and trust limits

The model card says the weights use the AI Pubs OpenRAIL-M license, the same license it identifies for `surya-ocr-2` weights. It is a short vendor model card and does not establish comparative speed or accuracy, supported file formats, complete label taxonomy, model architecture, or independent evaluation.[^surya-layout-fast-card]

## Relationships

- **Alternative to:** [Surya OCR 2](surya-ocr-2.md)'s VLM-based layout capability when a compact detector is preferred; the source calls this a drop-in alternative but does not provide a direct comparison.[^surya-layout-fast-card]

[^surya-layout-fast-card]: Datalab, *Surya Layout (fast) model card*, local [surya_layout2.md](../raw/surya_layout2.md) (accessed 2026-08-21).
