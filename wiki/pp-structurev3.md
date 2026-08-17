---
type: Model System
title: PP-StructureV3
description: PP-StructureV3 is a modular document parser that combines OCR, layout and article-region detection, specialized element recognition, and reading-order reconstruction to produce JSON and Markdown.
tags: [document-parsing, layout-analysis, tables, formulas, charts]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:38:17Z }
sources:
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: "PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model"
---

# PP-StructureV3

PP-StructureV3 is a multi-model pipeline for converting document images and PDFs into structured JSON and Markdown. It combines preprocessing and OCR with layout-aware routing to specialized recognizers, then reconstructs element relationships and reading order.[^paddleocr3-report]

## Pipeline

1. **Preprocessing:** page orientation classification and UVDoc-based unwarping.
2. **OCR:** [PP-OCRv5](pp-ocrv5.md), with its own preprocessing disabled, extracts page text.
3. **Layout analysis:** PP-DocLayout-plus detects document elements; a separate region detector groups elements into distinct articles, especially on newspaper-like pages.
4. **Item recognition:** PP-TableMagic selects table handling using orientation and frame classifiers, cell detection, and HTML structure recognition; PP-FormulaNet-plus emits LaTeX with a 2,560-token limit; PP-Chart2Table emits Markdown tables from charts; PP-OCRv4-seal handles curved seal text.
5. **Postprocessing:** an improved X-Y Cut associates figures and tables with captions and recovers reading order for complex and vertical layouts.[^paddleocr3-report]

## Reported results

On OmniDocBench, the report gives PP-StructureV3 edit distances of **0.145 English** and **0.206 Chinese** (equivalently 1-edit-distance scores of 0.855 and 0.794 in its figure). These are better than every listed pipeline, expert VLM, and general VLM in the report's table; Gemini 2.5 Pro is closest at 0.148/0.212. For context, [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md), reported in a separate source, later gives 0.141/0.197 on OmniDocBench, but cross-paper rank comparisons require matched evaluation versions and protocols.[^paddleocr3-report]

## Trust limits

- Results are author-reported and not reproduced from this source bundle. The report lists tool versions for some baselines but not a full common inference configuration, hardware setup, or statistical uncertainty.[^paddleocr3-report]
- The benchmark figure says the pipeline has approximately 5/1000 the parameters of Qwen2.5-VL-72B, implying roughly 0.36B, while the abstract broadly describes the introduced models as below 100M parameters. The report does not define which components are counted, so PP-StructureV3's total size is unresolved.[^paddleocr3-report]
- Performance is reported at aggregate English/Chinese level; the source does not isolate the contribution of region detection, specialized recognizers, or reading-order postprocessing.[^paddleocr3-report]

## Relationships

- **Part of:** [PaddleOCR 3.0](paddleocr-3.md).
- **Uses:** [PP-OCRv5](pp-ocrv5.md) for text detection and recognition.
- **Compared with:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) addresses the same page-to-structured-document task with an end-to-end 7B VLM rather than a modular pipeline.
- **Used by:** [PaddleOCR-VL](paddleocr-vl.md) supplies pseudo-labels in its automatic data-annotation workflow.[^paddleocr-vl-report]

[^paddleocr3-report]: Cui et al., *PaddleOCR 3.0 Technical Report*, local LaTeX source at [main.tex](../raw/2507.05595_PaddleOCR-3.0/main.tex), including `images/pp_structurev3_benchmark.pdf` and `images/pp_structurev3_framwork2.pdf` (accessed 2026-08-17).
[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model*, local LaTeX source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex) (accessed 2026-08-17).
