---
type: Concept
title: "Task: Structured extraction and KIE"
description: Structured extraction and KIE groups models that produce schema-constrained JSON or fused answers from document evidence, including visual grounding.
tags: [task, information-extraction, kie, json-extraction, document-understanding]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-29T05:11:26Z }
sources:
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
  - id: lift-card
    resource: ../raw/lift.md
    title: lift model card
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: glm-ocr-report
    resource: ../raw/2603.10910_GLM-OCR/main.tex
    title: GLM-OCR Technical Report
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474
    title: MiniCPM-OCR repository
  - id: ovisocr3-model-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
---

# Task: Structured extraction and KIE

Structured extraction and Key Information Extraction (KIE) go beyond faithful transcription: they return schema-constrained JSON, key-value pairs, or fused answers grounded in document evidence, often with field-level bounding boxes.

## Models in this task

- [lift](lift.md) — Datalab 9B model for schema-constrained JSON from PDFs/images (primary dedicated extraction model)[^lift-card]
- [PP-ChatOCRv4](pp-chatocrv4.md) — fuses retrieval-augmented OCR-text answers with direct PP-DocBee2 VLM answers[^paddleocr3-report]
- [GLM-OCR](glm-ocr.md) — separate full-page KIE path evaluated on Nanonets-KIE (93.7) and Handwritten-KIE (86.1); also private receipt-KIE 94.5[^glm-ocr-report]
- [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md) — directly prompts an image for named JSON fields without first generating full-document Markdown; the example requests `###` for absent fields, and the guide says to parse and validate the generated text.[^minicpm-repo]
- [Xiaomi-OCR-0](xiaomi-ocr-0.md) — prompts with an example JSON schema for key information extraction; schema compliance is not guaranteed.[^xiaomi-card]
- [Qianfan-OCR](qianfan-ocr.md) — prompt-driven parsing *or* understanding outputs; Layout-as-Thought variant emits boxes/labels/summaries before answering
- [Nanonets-OCR2](nanonets-ocr2.md) — VQA and field-like handling for checkboxes, signatures, watermarks within image-to-Markdown
- [dots.ocr](dots-ocr.md) — grounding-capable VLM that can emit layout detection with coordinates for downstream extraction
- [OvisOCR3](ovisocr3.md) — prompt-selected open, field-list, and schema-example KIE; the card reports 90.50/83.01/88.69/77.73 on OCRBench KIE, OCRBench v2 KIE, CC-OCR KIE, and an in-house set[^ovisocr3-model-card]

## Task characteristics

- **Input:** page image/PDF + schema, keys, or natural-language question; may include retrieval context (PP-ChatOCRv4).
- **Output:** JSON conforming to user schema, or answer with citation/boxes; evaluated on KIE benchmarks (Nanonets-KIE, Handwritten-KIE, private receipt/seal sets).
- **Strengths:** directly consumable for automation; bounding-box grounding aids auditability.
- **Limits:** schema adherence vs. hallucination trade-off; evaluation often private or task-conditioned, not comparable across leaderboards. A schema may be an output example rather than a formal JSON Schema, and prompted adherence does not enforce validity.[^ovisocr3-model-card]

## Relationships

- **Uses:** outputs of [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) or [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) as evidence
- **Contrasts with:** pure transcription tasks; overlapped by [Task: Unified perception and grounding](task-unified-perception-grounding.md) when grounding is required

[^xiaomi-card]: [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), §§ Usage › Task prompts and Use Examples › Key information extraction (inspected 2026-10-29).
[^lift-card]: Datalab, [lift model card](../raw/lift.md), §§ lift and Features (schema-constrained extraction).
[^paddleocr3-report]: PaddleOCR Team, [PaddleOCR 3.0 report](../raw/2507.05595_PaddleOCR-3.0/main.tex), § PP-ChatOCRv4 (OCR, retrieval and VLM answer fusion).
[^glm-ocr-report]: GLM-OCR authors, [report entry point](../raw/2603.10910_GLM-OCR/main.tex), `sections/3_evaluation.tex` § Overall Benchmark Performance and `tables/docparse.tex` (KIE results); values are author-reported, not reproduced.
[^minicpm-repo]: [MiniCPM-OCR repository](../raw/MiniCPM-OCR/README.md), revision `b33b474`, [model guide § Key Information Extraction](../raw/MiniCPM-OCR/docs/minicpm_ocr_1dot0_en.md#key-information-extraction-kie) (reported interface, not executed).
[^ovisocr3-model-card]: ATH-MaaS, *OvisOCR3 model card*, local source at [ATH-MaaS-OvisOCR3.md](../raw/ATH-MaaS-OvisOCR3.md), § Capabilities, § Performance › Key Information Extraction, and § Task-Specific Usage › Key Information Extraction (accessed 2026-10-25).
