---
type: Concept
title: MinerU 4 OCR pipeline
description: MinerU 4's PDF pipeline combines layout-driven OCR, native PDF text, formulas, tables, and optional VLM processing according to tier and parse mode.
tags: [ml, ocr, document-parsing, pdf]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T13:55:01+07:00 }
stale_after: 2027-04-29
sources:
  - id: mineru-repo
    resource: ../raw/MinerU/README.md
    scope: ../raw/MinerU/
    kind: code
    revision: b7f3dd0c5f6e6d66a298239ffd02b328b873918e
    title: MinerU repository 4.0.12
---

# MinerU 4 OCR pipeline

**Observed:** MinerU 4 processes PDF pages through different paths depending on tier and whether text is native or requires OCR. It combines layout blocks with specialized OCR and formula/table processing, and adds VLM inference for higher efforts. Flash text-mode PDFs use a separate native path, not the neural OCR path.[^mineru-repo]

## PDF stages

1. Open the PDF; `auto` classifies it as `txt` or `ocr`. Flash + `txt` delegates native analysis to DocVortex. Other paths initialize a local model context, and `high`/`xhigh` additionally initialize a VLM predictor.[^mineru-repo]
2. **Observed:** model-backed processing is windowed, defaulting to 64 pages. The prepare phase renders pages, runs layout inference, and performs tier-dependent table preparation. The VLM runs outside the local-model stage lock; finishing assembles model results and image assets.[^mineru-repo]
3. Flash OCR runs detection, recognition, text fill, and table content fill. At `medium` (public `basic`), formula recognition and table recognition precede OCR and text filling. At `high`/`xhigh`, the detected OCR block types and whether small-model formula recognition runs depend on text versus OCR mode.[^mineru-repo]

## Detection and recognition

**Observed:** OCR detection crops eligible layout regions, masks overlapping formula areas, batches crops, sorts and merges detected boxes, and adjusts boxes around formulas. In medium OCR mode, crop images are recognized in a later batch; recognition count mismatch raises an error and low-confidence text is filtered. In text mode, the pipeline can fill spans from native PDF characters and use post-OCR for remaining spans. These are source-code observations, not measured quality guarantees.[^mineru-repo]

Medium table processing uses table classification and wired/wireless recognition; dedicated seal OCR is applied on the medium/high paths. OCR models and execution choices are described in [MinerU 4 models and inference engines](mineru-4-models-and-engines.md).[^mineru-repo]

## Limits

Static inspection only: no sample PDF or model was run, and classification, native text extraction and deterministic postprocessing rely on the external DocVortex dependency. Detailed table, text and cancellation paths were sampled rather than exhaustively audited; output quality, performance and language coverage need empirical verification. Broader package coverage is pending as recorded in [MinerU 4 architecture](mineru-4-architecture.md).[^mineru-repo]

## Relationships

- **Depends on:** [MinerU 4 models and inference engines](mineru-4-models-and-engines.md) for OCR, layout and formula models.
- **Related to:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md); this pipeline uses detected regions for specialist recognition.[^mineru-repo]

[^mineru-repo]: [MinerU repository README](../raw/MinerU/README.md), “MinerU 4.0” and “Quality Tiers”; `mineru/backend/analysis/pdf/pipeline.py::_prepare_analysis`; `mineru/backend/analysis/pdf/window.py::_configured_window_size`, `::_prepare_pdf_window`, `::_process_flash_ocr`, `::_process_text_and_formulas`, `::_process_pdf_window`, `::process_pdf_windows`; `mineru/backend/analysis/pdf/ocr.py::_build_ocr_det_type_and_mfr_enable`, `::_collect_ocr_det_crops`, `::_ocr_det`, `::_apply_ocr_rec_results`, `::_apply_seal_ocr`; `mineru/backend/analysis/pdf/text/content.py::_fill_window_block_content_and_lines`; `mineru/backend/analysis/pdf/tables.py::_apply_medium_table_recognition`; revision `b7f3dd0c5f6e6d66a298239ffd02b328b873918e`.
