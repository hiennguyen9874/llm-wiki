---
type: Concept
title: "Task: Structured extraction and KIE"
description: Structured extraction and KIE groups models that produce schema-constrained JSON or fused answers from document evidence, including visual grounding.
tags: [task, information-extraction, kie, json-extraction, document-understanding]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
sources:
  - id: lift-card
    resource: ../raw/lift.md
    title: lift model card
  - id: paddleocr3-report
    resource: ../raw/2507.05595_PaddleOCR-3.0/main.tex
    title: PaddleOCR 3.0 Technical Report
  - id: glm-ocr-report
    resource: ../raw/2603.10910_GLM-OCR/main.tex
    title: GLM-OCR Technical Report
---

# Task: Structured extraction and KIE

Structured extraction and Key Information Extraction (KIE) go beyond faithful transcription: they return schema-constrained JSON, key-value pairs, or fused answers grounded in document evidence, often with field-level bounding boxes.

## Models in this task

- [lift](lift.md) — Datalab 9B model for schema-constrained JSON from PDFs/images (primary dedicated extraction model)
- [PP-ChatOCRv4](pp-chatocrv4.md) — fuses retrieval-augmented OCR-text answers with direct PP-DocBee2 VLM answers
- [GLM-OCR](glm-ocr.md) — separate full-page KIE path evaluated on Nanonets-KIE (93.7) and Handwritten-KIE (86.1); also private receipt-KIE 94.5
- [Qianfan-OCR](qianfan-ocr.md) — prompt-driven parsing *or* understanding outputs; Layout-as-Thought variant emits boxes/labels/summaries before answering
- [Nanonets-OCR2](nanonets-ocr2.md) — VQA and field-like handling for checkboxes, signatures, watermarks within image-to-Markdown
- [dots.ocr](dots-ocr.md) — grounding-capable VLM that can emit layout detection with coordinates for downstream extraction

## Task characteristics

- **Input:** page image/PDF + schema, keys, or natural-language question; may include retrieval context (PP-ChatOCRv4).
- **Output:** JSON conforming to user schema, or answer with citation/boxes; evaluated on KIE benchmarks (Nanonets-KIE, Handwritten-KIE, private receipt/seal sets).
- **Strengths:** directly consumable for automation; bounding-box grounding aids auditability.
- **Limits:** schema adherence vs. hallucination trade-off; evaluation often private or task-conditioned, not comparable across leaderboards.

## Relationships

- **Uses:** outputs of [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) or [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) as evidence
- **Contrasts with:** pure transcription tasks; overlapped by [Task: Unified perception and grounding](task-unified-perception-grounding.md) when grounding is required
