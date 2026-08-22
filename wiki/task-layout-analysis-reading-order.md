---
type: Concept
title: "Task: Layout analysis and reading order"
description: Layout analysis and reading order groups models that localize document regions, classes, masks, and pairwise precedence for ordered reconstruction.
tags: [task, layout-analysis, reading-order, document-parsing]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
sources:
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: pp-doclayoutv3-source
    resource: ../raw/2606.23344_RT-DocLayout/main.tex
    title: RT-DocLayout report (PP-DocLayoutV3)
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: PaddleOCR-VL Technical Report
---

# Task: Layout analysis and reading order

Layout analysis and reading-order prediction localize where content lives on a page (paragraphs, headings, lists, tables, figures, formulas, seals, footnotes) and in what order a human should read them, providing the spatial scaffold for downstream recognition and serialization.

## Models in this task

- [PP-DocLayoutV2](pp-doclayoutv2.md) — RT-DETR layout detector with 6-layer relation-aware pointer network for reading order
- [PP-DocLayoutV3](pp-doclayoutv3.md) — RT-DETR-derived Transformer jointly predicting classes, boxes, instance masks, and pairwise precedence ranking; academic identity RT-DocLayout
- [Surya Layout (fast)](surya-layout-fast.md) — compact object detector alternative to VLM-based layout predictor, emits regions + order
- [Nemotron OCR v2](nemotron-ocr-v2.md) (relational layout module) — grouping and reading-order stage over detected words/lines

Layout-aware training signals that optimize this task end-to-end:

- [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) — GRPO rewards for segment count and reading order (supports [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md))

## Task characteristics

- **Input:** page image; optionally at reduced resolution for global layout.
- **Output:** typed bounding boxes/polygons, instance masks, and directed order graph or ranked sequence.
- **Strengths:** grounds every downstream recognizer; enables block-parallel modular parsing and hierarchy-aware chunking ([Docling native chunking](docling-native-chunking.md)).
- **Limits:** taxonomy varies by dataset (OmniDocBench vs. DocLayNet-style); order evaluation sensitive to NED vs. pairwise metrics.

## Relationships

- **Uses:** outputs consumed by [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) and [Task: Table structure recognition](task-table-structure-recognition.md)
- **Evaluated by:** Real5-OmniDocBench ([Real5-OmniDocBench](real5-omnidocbench.md)) for robustness under scan/warp/photo/illumination/skew; component metrics in OmniDocBench order edit
