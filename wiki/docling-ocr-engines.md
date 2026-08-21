---
type: Concept
title: Docling OCR engines
description: Docling offers optional OCR-engine integrations including RapidOCR, Nemotron-OCR, EasyOCR, ocrmac, and Tesseract-based engines, with engine-specific platform, runtime, model, and language constraints.
tags: [docling, ocr, rapidocr, easyocr, nemotron, tesseract]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-ocr-docs
    resource: ../raw/docling-concepts/OCR.md
    title: Docling OCR engines documentation
---

# Docling OCR engines

Docling documents optional integrations for RapidOCR, Nemotron-OCR, EasyOCR, ocrmac, the Tesseract CLI, and tesserocr. Engine selection is constrained by each integration's installed extras, runtime, model version, language handling, and operating-system support.[^docling-ocr-docs]

## RapidOCR

For RapidOCR 3.9.1–3.9.2, the documentation lists `onnxruntime` as the default backend and also supports OpenVINO, Paddle, and Torch. It lists PP-OCR v4, v5, and v6 support for the first three backends; Torch supports v4, Chinese-only v5, and v6.[^docling-ocr-docs]

The listed PP-OCR language sets differ by version and include both language and script-family identifiers. For v6, Docling also documents aliases such as `zh` → `ch`, `zh_tw` → `chinese_cht`, `ja` → `japan`, and `ko` → `korean`; however, it explicitly notes that Korean is not supported in PP-OCR v6 despite that alias.[^docling-ocr-docs]

## EasyOCR and Nemotron-OCR

EasyOCR accepts a language list and resolves a recognition checkpoint that supports all requested languages. The documentation recommends keeping that list short and specific: requesting English alone selects `english_g2.pth`, whereas adding German selects the wider Latin model, which it says is generally less accurate for English.[^docling-ocr-docs]

Nemotron-OCR 2.0.0–2.0.2 is documented as Linux- and CUDA-only, with Docling enforcing CUDA 13.x. Version 2.0.0 supports Python 3.12, while 2.0.2 supports Python 3.11–3.13; both expose English and multilingual inputs, with multilingual covering English, simplified/traditional Chinese, Japanese, Korean, and Russian.[^docling-ocr-docs]

## System-provided engines

Tesseract must be installed as a system package; tesserocr is its Python wrapper. Ocrmac is a macOS-only wrapper around Apple's Vision framework, ships no model artifacts, and therefore inherits its language support from the macOS release rather than the ocrmac version.[^docling-ocr-docs]

## Relationships

- **Used by:** [Docling architecture](docling-architecture.md) through configurable conversion backends and pipeline options.[^docling-ocr-docs]
- **Related to:** [Docling confidence grades](docling-confidence-grades.md), whose report includes OCR quality.[^docling-ocr-docs]
- **Related to:** [Nemotron OCR v2](nemotron-ocr-v2.md), the separately documented model family integrated by this source.

[^docling-ocr-docs]: Docling, [*OCR engines in Docling*](../raw/docling-concepts/OCR.md) (accessed 2026-08-21). Version-specific statements reflect the retained documentation, including its 2026-07-28 RapidOCR support snapshot.