---
type: Concept
title: "Task: Table structure recognition"
description: Table structure recognition groups detectors that localize cells, rows, and columns for downstream OCR-to-Markdown table reconstruction.
tags: [task, table-recognition, document-parsing, layout-analysis]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-29T05:12:52Z }
sources:
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
  - id: nemotron-table-card
    resource: ../raw/nemotron-table-structure-v1.md
    title: Nemotron Table Structure v1 model card
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: PaddleOCR-VL-1.6 Technical Report
  - id: pp-structurev3-source
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: liteparse-readme
    resource: ../raw/liteparse.md
    kind: readme
    title: LiteParse README
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    kind: model-card
    title: Indra OCR model card (datalab-to/indra-ocr)
---

# Task: Table structure recognition

Table structure recognition recovers the grid of a table (cells, rows, columns, spans) so that cell OCR can be assembled into HTML/Markdown with correct TEDS/TEDS-S structure preservation.

## Models in this task

- [Nemotron Table Structure v1](nemotron-table-structure-v1.md) — YOLOX-based detector for cells/rows/columns, designed for OCR-to-Markdown pipelines (14M–primarily table-focused). It predicts three object classes — cell (including merged cells), row, and column — and its own card says it is not robust to rotated tables and sometimes misses cells near the bottom of a table.[^nemotron-table-card]
- Specialist table modules inside:
  - [PP-StructureV3](pp-structurev3.md) — dedicated table recognition component: PP-TableMagic chains a table-orientation classifier, a frame-type classifier, a cell-detection model, and a structure recognizer that emits HTML.[^pp-structurev3-source]
  - [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) / [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) — evaluated on Paddle hard-table set (TEDS 91.71) and OmniDocBench table TEDS; the 1.6 report lists Table-TEDS 94.76 and Table-TEDS-S 97.11 on OmniDocBench v1.6, and its post-processing engine performs cross-page table merging.[^paddleocr-vl-1-6-report]
  - [MinerU2.5](mineru2-5.md) / [MinerU2.5-Pro](mineru2-5-pro.md) — native-resolution table-crop recognition
  - [FalconOCR](falcon-ocr.md) — HTML table generation per layout region
  - [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md) — prompted table-region recognition; the SDK converts OTSL to HTML. Its optional rule-based cross-page merge is documented under [cross-page table reconstruction](task-cross-page-table-reconstruction.md), not as a cell-box detector.[^minicpm-repo]

Implicit table handling (less explicit detection, more generative):

- Models in [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) that generate HTML/Markdown tables directly (e.g., DeepSeek-OCR 2, OvisOCR2, OvisOCR3, Qwen-based parsers) — retained for comparison but not primarily table-structure detectors.
- [Xiaomi-OCR-0](xiaomi-ocr-0.md) — its table-region prompt requests OTSL, not cell boxes; its authors report 92.27 on PubTabNet, without enough protocol detail for a controlled comparison. Neither inference nor evaluation was reproduced.[^xiaomi-card]

## Rule-based and block-level extraction without a learned table model

Two document parsers in this batch reach table output without a learned table-structure model. They are listed separately because their cell geometry comes from rules or block labels, not from a trained detector, so their failure modes differ from the detectors above.

- [LiteParse](liteparse.md) — classifies each page into `table` and `grid_fallback` blocks and emits cells as objects with their own `bbox`: the drawn grid cell for ruled tables, the span extent for borderless ones. The README describes this path as pure heuristics, and explicitly defers dense tables to a commercial service.[^liteparse-readme]
- [Indra OCR](indra-ocr.md) — a `Table` block label plus HTML in its Markdown output, from a layout stage rather than a table specialist. Its card names merged or spanning cells, wrapped cell text, nested headers, and tables without ruling lines as the cases that land in wrong rows or columns.[^indra-ocr-card]

Both statements are **reported** vendor documentation; neither was reproduced against a table benchmark here.

## Task characteristics

- **Input:** table crop or full page; often evaluated on PubTabNet, FinTabNet, OmniDocBench table blocks.
- **Output:** cell boxes + row/col spanning; downstream assembly to HTML/Markdown via serializers like [Docling serialization](docling-serialization.md) (note: Markdown/LaTeX flatten spans).
- **Strengths:** explicit structure enables faithful reconstruction and downstream data extraction.
- **Limits:** rotated tables, merged or spanning cells, nested headers, and dense formulas remain hard-tail cases. The sources name the same tail from two directions: the Nemotron card excludes rotated tables and low-confidence bottom cells, while the PaddleOCR-VL-1.6 report adds an OmniDocBench v1.6 Hard subset of 296 pages of nested tables and dense formula layouts and targets the remaining under-optimized regions with data-engine mining.[^nemotron-table-card][^paddleocr-vl-1-6-report] Indra OCR's card independently reports the merged-cell and no-ruling-line failure for its block-level path.[^indra-ocr-card] **Synthesis:** the tail is consistent across detectors, generative parsers, and rule-based parsers, which suggests it is a property of table geometry rather than of one architecture.

## Relationships

- **Part of:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)
- **Uses:** [Task: Layout analysis and reading order](task-layout-analysis-reading-order.md) for table region proposals
- **Evaluated by:** OmniDocBench table TEDS/TEDS-S and PubTabNet/TEDS_TEST; also the table test family of [OmniParseBench](omniparsebench.md), which contributes a third of that benchmark's headline score.
- **Extended by:** [Task: Cross-page table reconstruction](task-cross-page-table-reconstruction.md), which merges table fragments across page boundaries after per-page parsing.
- **Implemented without a table model by:** [LiteParse](liteparse.md) via grid and span heuristics, and [Indra OCR](indra-ocr.md) via layout block labels.[^liteparse-readme][^indra-ocr-card]

[^xiaomi-card]: [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), §§ Benchmark results and Usage › Task prompts (inspected 2026-10-29).
[^nemotron-table-card]: NVIDIA, *Nemotron Table Structure v1 model card*, local source at [nemotron-table-structure-v1.md](../raw/nemotron-table-structure-v1.md), locators: § Model Overview (cell/row/column components), § Model Card › Technical Limitations ("not robust to rotated tables"), § Limitations (low-confidence bottom cells) (accessed 2026-10-25).
[^pp-structurev3-source]: PaddleOCR Team, *PaddleOCR 3.0 Technical Report*, local source at [2507.05595_PaddleOCR-3.0/main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), § PP-StructureV3 › Document Items Recognition › Table Recognition (PP-TableMagic stages) (accessed 2026-10-25).
[^paddleocr-vl-1-6-report]: PaddleOCR Team, *PaddleOCR-VL-1.6 Technical Report*, local source at [2606.03264_PaddleOCR-VL-1.6/main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), locators: § Document parsing framework (PP-DocLayoutV3 plus post-processing with cross-page table merging); § OmniDocBench v1.6 (296-page Hard subset); Table `tab:omni16_full_performance` (Table-TEDS 94.76, Table-TEDS-S 97.11) (accessed 2026-10-25).
[^liteparse-readme]: run-llama, *LiteParse README*, local source at [liteparse.md](../raw/liteparse.md), § Markdown output block types and § table-cell bbox semantics (ruled versus borderless), plus the complexity warning deferring dense tables (accessed 2026-10-25). The parser was not run.
[^minicpm-repo]: [MiniCPM-OCR repository](../raw/MiniCPM-OCR/README.md), revision `b33b474`, `docs/minicpm_ocr_1dot0_en.md` §§ Document Parsing Workflow and Single-Region Recognition; `sdk/minicpmvocr/postprocess/crosspage.py::merge_cross_page_tables` (static inspection, not executed).
[^indra-ocr-card]: Datalab, *Indra OCR model card*, local source at [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), locators: § JSON output block labels (`Table`), § Limitations › Complex tables (accessed 2026-10-25). No benchmark run was reproduced.
