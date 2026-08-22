---
type: Concept
title: "Task: Detector–recognizer OCR"
description: Detector–recognizer OCR groups lightweight detection plus recognition pipelines for word- or line-level transcription under latency and resource constraints.
tags: [task, ocr, text-detection, text-recognition, lightweight-models]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
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
---

# Task: Detector–recognizer OCR

Detector–recognizer OCR is the classical word- or line-level task: detect text boxes/polygons then transcribe each, optimized for mobile, CPU, high throughput, and low hallucination rather than full document reconstruction.

## Models in this task

- [PP-OCRv5](pp-ocrv5.md) — 0.07B unified ZH/Pinyin/En/JA detection+recognition, server/mobile variants
- [PP-OCRv6](pp-ocrv6.md) — 1.5M–34.5M shared reparameterizable MetaFormer backbone across detection and CTC recognition
- [Nemotron OCR v2](nemotron-ocr-v2.md) — convolutional detector → Transformer recognizer → relational grouping/reading order; English word-level and 6-language line-level (EN/ZH/JA/KO/RU/de-hyphenation) variants; 34.7–40.7 pages/s on A100 in crop mode

Stage components reused by hybrid parsers but counted here when used standalone:

- Detector + recognizer stages of [PP-StructureV3](pp-structurev3.md) and [PaddleOCR 3.0](paddleocr-3.md)

## Task characteristics

- **Input:** page, line, or word crop; often evaluated on cropped benchmarks (COCO-Text, ICDAR, SynthDoG).
- **Output:** polygons/boxes + transcriptions; reading order optionally via relational model.
- **Strengths:** tiny parameters, controllable, fast, minimal hallucination; suitable for plain-text extraction.
- **Limits:** no intrinsic document structure, table/formula/chart reconstruction requires additional layout/specialist stages.

## Relationships

- **Specializes:** plain-text layer of [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md)
- **Contrasts with:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) which generates full structured documents
- **Evaluated by:** [Detector–recognizer OCR benchmarks](detector-recognizer-ocr-benchmarks.md)
- **Used by:** [PaddleOCR 3.0](paddleocr-3.md) toolkit and Docling OCR-engine integrations ([Docling OCR engines](docling-ocr-engines.md))
