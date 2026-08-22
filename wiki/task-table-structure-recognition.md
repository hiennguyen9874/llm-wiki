---
type: Concept
title: "Task: Table structure recognition"
description: Table structure recognition groups detectors that localize cells, rows, and columns for downstream OCR-to-Markdown table reconstruction.
tags: [task, table-recognition, document-parsing, layout-analysis]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
sources:
  - id: nemotron-table-card
    resource: ../raw/nemotron-table-structure-v1.md
    title: Nemotron Table Structure v1 model card
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: PaddleOCR-VL-1.6 Technical Report
  - id: pp-structurev3-source
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
---

# Task: Table structure recognition

Table structure recognition recovers the grid of a table (cells, rows, columns, spans) so that cell OCR can be assembled into HTML/Markdown with correct TEDS/TEDS-S structure preservation.

## Models in this task

- [Nemotron Table Structure v1](nemotron-table-structure-v1.md) — YOLOX-based detector for cells/rows/columns, designed for OCR-to-Markdown pipelines (14M–primarily table-focused)
- Specialist table modules inside:
  - [PP-StructureV3](pp-structurev3.md) — dedicated table recognition component
  - [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) / [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) — evaluated on Paddle hard-table set (TEDS 91.71) and OmniDocBench table TEDS
  - [MinerU2.5](mineru2-5.md) / [MinerU2.5-Pro](mineru2-5-pro.md) — native-resolution table-crop recognition
  - [FalconOCR](falcon-ocr.md) — HTML table generation per layout region

Implicit table handling (less explicit detection, more generative):

- Models in [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) that generate HTML/Markdown tables directly (e.g., DeepSeek-OCR 2, OvisOCR2, Qwen-based parsers) — retained for comparison but not primarily table-structure detectors

## Task characteristics

- **Input:** table crop or full page; often evaluated on PubTabNet, FinTabNet, OmniDocBench table blocks.
- **Output:** cell boxes + row/col spanning; downstream assembly to HTML/Markdown via serializers like [Docling serialization](docling-serialization.md) (note: Markdown/LaTeX flatten spans).
- **Strengths:** explicit structure enables faithful reconstruction and downstream data extraction.
- **Limits:** rotated tables, nested headers, and dense formulas remain hard-tail cases targeted by data flywheel mining.

## Relationships

- **Part of:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)
- **Uses:** [Task: Layout analysis and reading order](task-layout-analysis-reading-order.md) for table region proposals
- **Evaluated by:** OmniDocBench table TEDS/TEDS-S and PubTabNet/TEDS_TEST
