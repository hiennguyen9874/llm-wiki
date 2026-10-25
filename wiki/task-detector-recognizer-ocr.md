---
type: Concept
title: "Task: Detector–recognizer OCR"
description: Detector–recognizer OCR groups lightweight detection plus recognition pipelines for word- or line-level transcription under latency and resource constraints.
tags: [task, ocr, text-detection, text-recognition, lightweight-models]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:42:48Z }
sources:
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: detector-benchmarks
    resource: ../wiki/detector-recognizer-ocr-benchmarks.md
    title: Detector–recognizer OCR benchmarks
  - id: pp-ocrv6-report
    resource: ../raw/2606.13108_PP-OCRv6/main.tex
    title: PP-OCRv6 Technical Report
  - id: nemotron-ocr-v2-card
    resource: ../raw/nemotron-ocr-v2.md
    title: Nemotron OCR v2 model card
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    kind: model-card
    title: Indra OCR model card (datalab-to/indra-ocr)
---

# Task: Detector–recognizer OCR

Detector–recognizer OCR is the classical word- or line-level task: detect text boxes/polygons then transcribe each, optimized for mobile, CPU, high throughput, and low hallucination rather than full document reconstruction. It is the lightweight end of the current OCR landscape, deliberately trading document reconstruction for control and cost.[^current-ocr-approaches]

## Models in this task

- [PP-OCRv5](pp-ocrv5.md) — 0.07B unified ZH/Pinyin/En/JA detection+recognition, server/mobile variants[^detector-benchmarks]
- [PP-OCRv6](pp-ocrv6.md) — 1.5M–34.5M shared reparameterizable MetaFormer backbone across detection and CTC recognition[^pp-ocrv6-report]
- [Nemotron OCR v2](nemotron-ocr-v2.md) — convolutional detector → Transformer recognizer → relational grouping/reading order; English word-level and 6-language line-level (EN/ZH/JA/KO/RU/de-hyphenation) variants; 34.7–40.7 pages/s on A100 in crop mode[^nemotron-ocr-v2-card]

Stage components reused by hybrid parsers but counted here when used standalone:

- Detector + recognizer stages of [PP-StructureV3](pp-structurev3.md) and [PaddleOCR 3.0](paddleocr-3.md)[^detector-benchmarks]

### Extended upward: script-routed line recognition

[Indra OCR](indra-ocr.md) is a boundary case that keeps this task's recognition shape while adding just enough structure to emit Markdown: an ONNX CPU pipeline assigns each line a box, a block label, and a reading order, routes each line to one of four script recognizers, and reuses a digital PDF's text layer where its checks pass. It therefore sits between line-level recognition and layout-first parsing rather than replacing either.[^indra-ocr-card] Its reported per-script scores on [OmniParseBench](omniparsebench.md) are recognizer evidence for this task family, not document-reconstruction evidence.[^indra-ocr-card]

## Task characteristics

- **Input:** page, line, or word crop; often evaluated on cropped benchmarks (COCO-Text, ICDAR, SynthDoG).
- **Output:** polygons/boxes + transcriptions; reading order optionally via relational model.
- **Strengths:** tiny parameters, controllable, fast, minimal hallucination; suitable for plain-text extraction.
- **Limits:** no intrinsic document structure, table/formula/chart reconstruction requires additional layout/specialist stages. The limit is visible in evaluation: line-only engines such as PP-OCR text models and Tesseract 5 score 0 on table tests and are left unscored on layout in Indra OCR's OmniParseBench table, so their headline score is undefined while Indra OCR's own block-and-layout output is scored.[^indra-ocr-card]
- **Evidence class:** every quantitative claim retained here is **Reported** by a vendor or author source; none was reproduced in this wiki.

## Relationships

- **Specializes:** plain-text layer of [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)
- **Contrasts with:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) which generates full structured documents
- **Evaluated by:** [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md)
- **Used by:** [PaddleOCR 3.0](paddleocr-3.md) toolkit and Docling OCR-engine integrations ([Docling OCR engines](docling-ocr-engines.md))
- **Extended by:** [Indra OCR](indra-ocr.md), which wraps line recognition in a minimal layout and reading-order stage for CPU-only Markdown output
- **Benchmarked by:** [OmniParseBench](omniparsebench.md) for per-script line recognition, and [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md) for cropped detection and recognition protocols[^detector-benchmarks]

[^current-ocr-approaches]: Compiled synthesis in this wiki: [Current OCR approaches](current-ocr-approaches.md), § Lightweight detector–recognizer pipelines (accessed 2026-10-25).
[^detector-benchmarks]: Compiled synthesis in this wiki: [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md), § Model coverage for the retained-family classification and its closing exclusion paragraph; per-family architecture details are on the individual model concepts (accessed 2026-10-25).
[^pp-ocrv6-report]: PP-OCRv6 authors, *PP-OCRv6: From 1.5M to 34.5M Parameters*, local LaTeX source at [main.tex](../raw/2606.13108_PP-OCRv6/main.tex), § Improvement Strategies › LCNetV4, Text Detection, and Text Recognition (accessed 2026-10-25).
[^nemotron-ocr-v2-card]: NVIDIA, *Nemotron OCR v2 model card*, local capture at [nemotron-ocr-v2.md](../raw/nemotron-ocr-v2.md), § Model Architecture and § Output (accessed 2026-10-25).
[^indra-ocr-card]: Datalab, *Indra OCR model card*, local capture at [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), § Usage › Output, § Languages, § Benchmarks › OmniParseBench, and § Throughput (accessed 2026-10-25).
