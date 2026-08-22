---
type: Concept
title: "Task: Layout-first modular parsing"
description: Layout-first modular parsing groups systems that detect layout regions and reading order before recognizing native-resolution crops with specialist models.
tags: [task, document-parsing, layout-analysis, modular-systems]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
sources:
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: hybrid-benchmarks
    resource: ../wiki/hybrid-ocr-systems-and-benchmarks.md
    title: Hybrid OCR systems and benchmarks
  - id: layout-first-benchmarks
    resource: ../wiki/layout-first-modular-ocr-benchmarks.md
    title: Layout-first modular OCR benchmarks
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: PaddleOCR-VL-1.6 Technical Report
---

# Task: Layout-first modular parsing

Layout-first modular parsing first detects document elements (text blocks, tables, formulas, figures, seals) and their reading order, then routes native-resolution crops to specialized recognizers. This preserves small text fidelity and allows type-specific handling at the cost of stage coupling.

## Models in this task

- [PaddleOCR-VL](paddleocr-vl.md) — PP-DocLayoutV2 → 0.9B dynamic-resolution VLM
- [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) — PP-DocLayoutV3 polygonal layout + text spotting/seal + long-doc postprocessing
- [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) — same two-stage path with mined weak-region data and CPT–SFT–GRPO
- [GLM-OCR](glm-ocr.md) — PP-DocLayoutV3 → CogViT-GLM recognizer (0.9B)
- [MinerU2.5](mineru2-5.md) / [MinerU2.5-Pro](mineru2-5-pro.md) — 1.2B low-resolution global layout → native-resolution crop recognition
- [FalconOCR](falcon-ocr.md) — 300M PP-DocLayoutV3 → early-fusion text/LaTeX/HTML-table recognizer
- [PP-StructureV3](pp-structurev3.md) — OCR + layout/article detection + specialist element models + order reconstruction
- [Surya OCR 2](surya-ocr-2.md) — 650M shared VLM for layout/order/OCR/tables (boundary: can operate layout-first block-parallel or end-to-end)

Supporting layout components used by the above:

- [PP-DocLayoutV2](pp-doclayoutv2.md) and [PP-DocLayoutV3](pp-doclayoutv3.md) — RT-DETR layout + pointer-network reading order
- [Surya Layout (fast)](surya-layout-fast.md) — compact layout/reading-order detector alternative

## Task characteristics

- **Input:** page image; global layout at low/reduced resolution plus high-res crops per region.
- **Output:** JSON/Markdown with region types, boxes/masks, reading order, and per-region transcription (including HTML tables, LaTeX formulas).
- **Strengths:** high fidelity on dense/small text, explicit grounding, specialist routing for tables/formulas/seals.
- **Limits:** error propagation across stages, deployment complexity, need for coordinated training data flywheel.

## Relationships

- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md), [Surya Layout (fast)](surya-layout-fast.md)
- **Contrasts with:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md)
- **Evaluated by:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) and [Hybrid OCR systems and benchmarks](hybrid-ocr-systems-and-benchmarks.md)
- **Synthesized in:** [Current OCR approaches](current-ocr-approaches.md)
