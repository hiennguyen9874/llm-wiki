---
type: Concept
title: Granite Docling 258M
description: Granite Docling 258M is IBM's 258M-parameter document-conversion VLM, integrated with Docling to produce structured document outputs.
tags: [document-parsing, vision-language-model, ocr, docling, granite]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:05:31Z }
sources:
  - id: granite-docling-model-card
    resource: ../raw/granite-docling-258m.md
    title: granite-docling-258m model card
---

# Granite Docling 258M

Granite Docling 258M is IBM Research's English image-and-text-to-text model for document conversion. It is intended as a compact component of Docling pipelines rather than as a general image-understanding model.[^granite-docling-model-card]

## Design and scope

- The model builds on Idefics3, replacing its vision encoder with SigLIP2 base patch-16 512 and its language model with Granite 165M; its connector is an Idefics3-style pixel-shuffle projector.[^granite-docling-model-card]
- Its supervised fine-tuning includes DocTags, which can be converted through `docling-core` into a `DoclingDocument` and then exported to Markdown, HTML, and other formats.[^granite-docling-model-card]
- IBM describes its training corpus as public data plus internally constructed synthetic data. Named public sources include SynthCodeNet, SynthFormulaNet, SynthChartNet, and DoclingMatix.[^granite-docling-model-card]

## Document-conversion capabilities

The model supports full-page conversion and targeted chart-to-table, formula-to-LaTeX, code-to-text, table-to-OTSL, and location- or element-oriented prompts. IBM also lists full-page and bounding-box-guided region inference, document-element questions, improved inline-equation recognition, and experimental Japanese, Arabic, and Chinese support.[^granite-docling-model-card]

## Integration and deployment

- The documented default path is Docling's VLM pipeline with `--vlm-model granite_docling`; the model can also be used through Transformers, vLLM, ONNX, or MLX-VLM.[^granite-docling-model-card]
- The Transformers example uses `AutoModelForVision2Seq` and decodes a DocTags response from a single page image. The vLLM batch example limits each request to one image.[^granite-docling-model-card]
- For vLLM versions that do not support the model's tied weights, IBM provides an `untied` model revision. On older GPUs without `bfloat16` support, the card recommends `float32` to avoid exclamation-mark-only output.[^granite-docling-model-card]

## Reported evaluation

Compared with SmolDocling-256M-preview in the model card, Granite Docling 258M reports higher scores for layout (mAP 0.27 vs. 0.23; F1 0.86 vs. 0.85), full-page OCR (F1 0.84 vs. 0.80), code recognition (F1 0.988 vs. 0.915), equation recognition (F1 0.968 vs. 0.947), FinTabNet table TEDS with content (0.96 vs. 0.76), MMStar (0.30 vs. 0.17), and OCRBench (500 vs. 338). These are source-reported results; the card directs readers to an earlier publication for methodology.[^granite-docling-model-card]

## Limitations

The card cautions that the model can produce inaccurate, biased, offensive, or otherwise unwanted output, with the impact of small model size on hallucination still uncertain. IBM recommends use through Docling, reserves general image tasks for Granite Vision models, and suggests Granite Guardian as an additional safety layer.[^granite-docling-model-card]

[^granite-docling-model-card]: [granite-docling-258m model card](../raw/granite-docling-258m.md).
