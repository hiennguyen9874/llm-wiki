---
type: Concept
title: "Task: Layout analysis and reading order"
description: Layout analysis and reading order groups models and rule-based pipelines that detect document regions and their classes and assign an order for ordered reconstruction.
tags: [task, layout-analysis, reading-order, document-parsing]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-30T02:16:13Z }
stale_after: 2027-04-25
sources:
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: pp-doclayoutv3-source
    resource: ../raw/2606.23344_RT-DocLayout/main.tex
    title: RT-DocLayout report (PP-DocLayoutV3)
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: PaddleOCR-VL Technical Report
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    kind: model-card
    title: Indra OCR model card (datalab-to/indra-ocr)
  - id: ovisocr3-model-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
  - id: groundanything-card
    resource: ../raw/GroundingPI-GroundAnything.md
    kind: model-card
    title: GroundAnything model card
  - id: liteparse-readme
    resource: ../raw/liteparse.md
    kind: readme
    title: LiteParse README
  - id: surya-25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
  - id: mdpbench-paper
    resource: ../raw/2603.28130_MDPBench/main.tex
    kind: paper
    title: "MDPBench: A Benchmark for Multilingual Document Parsing in Real-World Scenarios"
---

# Task: Layout analysis and reading order

Layout analysis and reading-order prediction localize where content lives on a page (paragraphs, headings, lists, tables, figures, formulas, seals, footnotes) and in what order a human should read them, providing the spatial scaffold for downstream recognition and serialization.[^current-ocr-approaches]

## Models in this task

- [PP-DocLayoutV2](pp-doclayoutv2.md) — RT-DETR layout detector with 6-layer relation-aware pointer network for reading order
- [PP-DocLayoutV3](pp-doclayoutv3.md) — RT-DETR-derived Transformer jointly predicting classes, boxes, instance masks, and pairwise precedence ranking; academic identity RT-DocLayout
- [Surya Layout (fast)](surya-layout-fast.md) — compact object detector alternative to VLM-based layout predictor, emits regions + order
- [Surya OCR 2.5](surya-ocr-2-5.md) — shared VLM layout mode returns labeled polygons and boxes in reading order with explicit zero-indexed positions; OCR can also generate ordered blocks directly.[^surya-25-card]
- [Nemotron OCR v2](nemotron-ocr-v2.md) (relational layout module) — grouping and reading-order stage over detected words/lines
- [Indra OCR](indra-ocr.md) (layout stage) — CPU ONNX pipeline whose layout stage assigns every line and block a box, one of ten block labels, and a reading order before script-routed recognition[^indra-ocr-card]

Layout-aware training signals that optimize this task end-to-end:

- [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) — GRPO rewards for segment count and reading order (supports [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md))

## Detection without an order model

Three retained systems place layout detection outside a dedicated layout-and-order architecture, which marks the boundary of what this task requires:[^ovisocr3-model-card][^groundanything-card][^liteparse-readme]

- [OvisOCR3](ovisocr3.md) — a prompt-selected `document_layout.txt` mode emits `bbox` and `category` JSON only; order appears in its Markdown mode as generated text, not as a separate order output.
- [GroundAnything](groundanything.md) — one prompt template detects document layout elements by category inside a unified grounding interface, emitting boxes rather than an order graph.
- [LiteParse](liteparse.md) — a rule- and geometry-based block classifier emits classified blocks in reading order with no learned layout model at all, so its order is a heuristic over extracted text boxes rather than a predicted relation.[^liteparse-readme]

## Task characteristics

- **Input:** page image; optionally at reduced resolution for global layout.
- **Output:** typed bounding boxes/polygons, instance masks, and directed order graph or ranked sequence; some systems emit detection only, and others bake order into generated markup.
- **Order mechanisms:** pairwise precedence heads ([PP-DocLayoutV2](pp-doclayoutv2.md)'s bilinear pairwise logits with win-accumulation decoding, and [PP-DocLayoutV3](pp-doclayoutv3.md)'s pairwise precedence ranking), order implicit in generated Markdown, RL order rewards ([LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md)), causal visual queries ([DeepSeek-OCR 2](deepseek-ocr-2.md)), and heuristic geometry when no model is used.[^paddleocr-vl-report][^pp-doclayoutv3-source][^liteparse-readme] Indra OCR exposes the order explicitly as a per-block field, which makes the stage inspectable.[^indra-ocr-card]
- **Strengths:** grounds every downstream recognizer; enables block-parallel modular parsing and hierarchy-aware chunking ([Docling native chunking](docling-native-chunking.md)).
- **Limits:** taxonomy varies by dataset (OmniDocBench vs. DocLayNet-style); order evaluation sensitive to NED vs. pairwise metrics. Ordering errors concentrate on non-Latin reading directions and on layouts that do not reduce to columns: [Indra OCR](indra-ocr.md) reports that a newspaper whose articles wind across tiers can come out in the wrong article order, and MDPBench shows [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) and [dots.ocr](dots-ocr.md) reading two-column Arabic left-to-right.[^indra-ocr-card][^mdpbench-paper]

## Relationships

- **Uses:** outputs consumed by [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) and [Task: Table structure recognition](task-table-structure-recognition.md)
- **Evaluated by:** Real5-OmniDocBench ([Real5-OmniDocBench](real5-omnidocbench.md)) for robustness under scan/warp/photo/illumination/skew; component metrics in OmniDocBench order edit
- **Evaluated by:** the layout test family of [OmniParseBench](omniparsebench.md), whose vendor-run rows report 92.2 for [Indra OCR](indra-ocr.md) in its default `auto` mode and 71.7 for [PP-StructureV3](pp-structurev3.md) under one scorer and page set[^indra-ocr-card], and by [MDPBench](mdpbench.md), whose annotation pipeline verifies reading order element by element against human reading logic[^mdpbench-paper]
- **Related to:** [Task: Unified perception and grounding](task-unified-perception-grounding.md), which shares the localization capability but treats category-prompted detection as an end in itself rather than a scaffold for serialization

[^surya-25-card]: Datalab, [Surya OCR 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ OCR (text recognition) and Layout and reading order (inspected 2026-10-30); reported outputs, not independently tested.
[^current-ocr-approaches]: Compiled synthesis in this wiki: [Current OCR approaches](current-ocr-approaches.md), § Modular layout-first document parsing and § Cross-cutting technical directions (reading order as a first-class target) (accessed 2026-10-25).
[^indra-ocr-card]: Datalab, *Indra OCR* model card (`datalab-to/indra-ocr`), local capture [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), § Indra OCR (the *Layout* bullet), § Output, § Limitations (*Geometry*), and § Benchmarks › OmniParseBench (accessed 2026-10-25).
[^ovisocr3-model-card]: ATH-MaaS, *OvisOCR3 model card*, local source at [ATH-MaaS-OvisOCR3.md](../raw/ATH-MaaS-OvisOCR3.md), § Document Parsing (three-mode table), § Task-Specific Usage › Document Parsing, and § Limitations (accessed 2026-10-25).
[^groundanything-card]: GroundingPI, *GroundAnything* model card, local capture at [GroundingPI-GroundAnything.md](../raw/GroundingPI-GroundAnything.md), § Supported Tasks & Prompt Templates (document layout template) and § Output(s) (accessed 2026-10-25).
[^liteparse-readme]: run-llama, *LiteParse README*, local capture [liteparse.md](../raw/liteparse.md), § Layout blocks (`blocks` array in reading order; heuristic, rule-based rendering) and § Benchmarks (reading-order columns) (accessed 2026-10-25).
[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL Technical Report*, local LaTeX source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex), § Method › Layout Analysis (RT-DETR detector plus six-layer pointer network, pairwise logits, win-accumulation decoding) (accessed 2026-10-25).
[^pp-doclayoutv3-source]: RT-DocLayout authors, *RT-DocLayout: Real-Time End-to-End Document Layout Analysis with Reading Order in the Wild*, local LaTeX source at [main.tex](../raw/2606.23344_RT-DocLayout/main.tex), § Reading Order Prediction and § Method (joint detection, masks, and reading-order queries) (accessed 2026-10-25).
[^mdpbench-paper]: Li et al., *MDPBench: A Benchmark for Multilingual Document Parsing in Real-World Scenarios*, local LaTeX source at [main.tex](../raw/2603.28130_MDPBench/main.tex), § Annotation (reading-order verification) and § *Models Struggle with Reading Order in Right-to-Left Scripts* (accessed 2026-10-25).
