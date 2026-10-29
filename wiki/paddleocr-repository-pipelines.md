---
type: Software
title: PaddleOCR repository pipelines
description: PaddleOCR's repository exposes PaddleX-backed OCR and document pipelines alongside a separate classic detector–recognizer implementation.
tags: [ml, ocr, document-ai, pipelines]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T14:03:42+07:00 }
stale_after: 2027-04-29
sources:
  - id: paddleocr-repo
    resource: ../raw/PaddleOCR/README.md
    scope: ../raw/PaddleOCR/
    kind: code
    revision: dab3fe3
    title: PaddleOCR repository
---

# PaddleOCR repository pipelines

**Observed:** At this snapshot, the Python `paddleocr` package wraps external PaddleX pipelines, while `ppocr/` and `tools/` contain a separate configuration-driven training and classic inference stack. The package pins `paddlex[ocr-core]>=3.7.0,<3.8.0`. This is implementation evidence for, rather than a replacement for, the report-based [PaddleOCR 3.0 overview](paddleocr-3.md).[^paddleocr-repo]

## Wrapper and configuration

`PaddleXPipelineWrapper` loads a named or supplied PaddleX configuration, recursively merges wrapper overrides, and calls `create_pipeline`; it can export the merged configuration to YAML. The concrete wrappers expose parameters, but PaddleX owns the downstream pipeline implementation. The standalone OCR wrapper defaults to `PP-OCRv6_medium_det` and `PP-OCRv6_medium_rec` when neither language nor version is specified. If a model name or directory is provided, `lang` and `ocr_version` are ignored with a warning. **Observed:** the OCR wrapper accepts v3–v6, whereas the `PPStructureV3` version selector accepts only v3–v5; this does not establish whether custom v6 models work there.[^paddleocr-repo]

## OCR and document flows

- **Observed:** the C++ OCR configuration enables document orientation and unwarping, text detection, text-line orientation, and text recognition. It specifies PP-OCRv6 medium models and batch size six for recognition and text-line orientation. These are values in this specific configuration, not universal defaults.[^paddleocr-repo]
- **Observed:** classic `TextSystem.__call__` detects and sorts boxes, crops each region, optionally classifies text-line orientation, recognizes crops, and filters by recognition score; optional slicing merges detected fragments. This code is not evidence that PaddleX uses the identical implementation.[^paddleocr-repo]
- **Reported:** the [PaddleOCR-VL](paddleocr-vl.md) tutorial describes page layout detection and reading order followed by per-region VLM recognition and merging. Running only the VLM component is not equivalent to running the full pipeline; layout detection is also configurable in the wrapper. [PP-StructureV3](pp-structurev3.md) instead exposes configurable layout, general OCR, table, seal, formula, and other modules.[^paddleocr-repo]

## Output and cross-page API

**Reported:** README “Intelligent Document Parsing” says PP-StructureV3 supplies finer-grained text and table-cell coordinates than the VL series; this is not a measured localization comparison. **Observed:** `PaddleOCRVL.restructure_pages` delegates to PaddleX with `merge_tables=True`, `relevel_titles=True`, and `concatenate_pages=False` defaults. The API surface establishes configurable postprocessing, not its correctness; external implementation and inference were not checked.[^paddleocr-repo]

## Source coverage and limits

The source is the Apache-2.0 upstream repository snapshot at the revision above. **Inspected:** README; 3.x OCR, VL, and Structure wrappers and PaddleX base; classic inference `TextSystem`; selected PP-OCRv6 configurations, model composition and engine documentation; C++ OCR configuration. `docs/` was inventoried: 621 files, including 381 Markdown documents; selected English 3.x OCR, VL, structure and inference documentation was explored. Model and deployment exploration also inspected selected files in `configs/`, `ppocr/`, `tools/`, `deploy/`, SDKs and tests. The 2.x documentation, most algorithms, training configurations, platform ports, integrations, tests and supporting material remain **pending**, not exhaustively covered. Translated duplicate docs and decorative images were not compiled; `.git` history and generated, cached or vendored material were excluded. External PaddleX internals and model weights were not inspected. No model, training, inference, benchmark, or repository test was executed; performance claims remain author-reported. The source directory was untracked in the parent repository during this ingest, so future provenance depends on preserving it.[^paddleocr-repo]

## Relationships

- **Compared by:** [PaddleOCR vs MinerU vs Docling](paddleocr-mineru-docling-comparison.md), a version-aware architecture and selection synthesis.
- **Uses:** [PaddleOCR inference engines](paddleocr-inference-engines.md) for backend configuration and deployment.
- **Uses:** [PaddleOCR model and training architecture](paddleocr-model-training-architecture.md) for the source-tree model building and training path.
- **Includes:** [PP-OCRv6](pp-ocrv6.md), [PP-StructureV3](pp-structurev3.md), and [PaddleOCR-VL 1.6](paddleocr-vl-1.6.md) as documented model and pipeline families.[^paddleocr-repo]

[^paddleocr-repo]: [Repository README](../raw/PaddleOCR/README.md), “Key Features” and “Quick Start”; revision `dab3fe3`: `pyproject.toml::project.dependencies`; `paddleocr/_pipelines/base.py::PaddleXPipelineWrapper`; `paddleocr/_pipelines/ocr.py::PaddleOCR.__init__` and `_get_ocr_model_names`; `paddleocr/_pipelines/pp_structurev3.py::_SUPPORTED_OCR_VERSIONS` and `_get_paddlex_config_overrides`; `paddleocr/_pipelines/paddleocr_vl.py::PaddleOCRVL` and `::PaddleOCRVL.restructure_pages`; `tools/infer/predict_system.py::TextSystem.__call__`; `deploy/cpp_infer/src/configs/OCR.yaml`; `docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md`, introduction.
