---
type: Concept
title: "Task: Layout-first modular parsing"
description: Layout-first modular parsing groups systems that detect layout regions and reading order before recognizing native-resolution crops with specialist models.
tags: [task, document-parsing, layout-analysis, modular-systems]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-29T05:12:52Z }
stale_after: 2027-04-25
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
  - id: indra-ocr-card
    resource: ../raw/datalab-to-indra-ocr.md
    kind: model-card
    title: Indra OCR model card (datalab-to/indra-ocr)
  - id: omniparsebench
    resource: ../wiki/omniparsebench.md
    title: OmniParseBench
  - id: minicpm-repo
    resource: ../raw/MiniCPM-OCR/README.md
    scope: ../raw/MiniCPM-OCR/
    kind: code
    revision: b33b474136088dc43a2341e94590c804ec0c16a5
    title: MiniCPM-OCR repository
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
  - id: oxr-readme
    resource: ../raw/OXR-1.0.md
    kind: readme
    title: SoMark OXR-1.0 README
---

# Task: Layout-first modular parsing

Layout-first modular parsing first detects document elements (text blocks, tables, formulas, figures, seals) and their reading order, then routes native-resolution crops to specialized recognizers. This preserves small text fidelity and allows type-specific handling at the cost of stage coupling.[^current-ocr-approaches]

## Models in this task

- [PaddleOCR-VL](paddleocr-vl.md) — PP-DocLayoutV2 → 0.9B dynamic-resolution VLM
- [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) — PP-DocLayoutV3 polygonal layout + text spotting/seal + long-doc postprocessing
- [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) — same two-stage path with mined weak-region data and CPT–SFT–GRPO[^paddleocr-vl-1-6-report]
- [GLM-OCR](glm-ocr.md) — PP-DocLayoutV3 → CogViT-GLM recognizer (0.9B)
- [MiniCPM-OCR 1.0](minicpm-ocr-1-0.md) — PP-DocLayoutV3 → 1.3B region recognizer and SDK assembly; crop resolution is not established here[^minicpm-repo]
- [MinerU2.5](mineru2-5.md) / [MinerU2.5-Pro](mineru2-5-pro.md) — 1.2B low-resolution global layout → native-resolution crop recognition
- [TeleOCR](teleocr.md) — 1.2B deformation-aware polygon layout segmentation → crop recognition in one prompted VLM (digital and camera-captured pages)
- [FalconOCR](falcon-ocr.md) — 300M PP-DocLayoutV3 → early-fusion text/LaTeX/HTML-table recognizer
- [PP-StructureV3](pp-structurev3.md) — OCR + layout/article detection + specialist element models + order reconstruction
- [Surya OCR 2](surya-ocr-2.md) — 650M shared VLM for layout/order/OCR/tables (boundary: can operate layout-first block-parallel or end-to-end)

**Optional two-stage path:** [Xiaomi-OCR-0](xiaomi-ocr-0.md) also documents PP-DocLayoutV3 → region recognition → page assembly alongside its whole-page interface. The card points to external repository code, which was not inspected; crop resolution and assembly details are not established here.[^xiaomi-card]

**Related boundary:** [OXR-1.0](oxr-1-0.md) separates a replaceable layout model from recognition, but places reading order in the recognition stage; its README does not establish crop resolution or the complete intermediate flow assumed by the core definition above.[^oxr-readme]

Supporting layout components used by the above:

- [PP-DocLayoutV2](pp-doclayoutv2.md) and [PP-DocLayoutV3](pp-doclayoutv3.md) — RT-DETR layout + pointer-network reading order
- [Surya Layout (fast)](surya-layout-fast.md) — compact layout/reading-order detector alternative

## Boundary: the same decomposition below VLM scale

[Indra OCR](indra-ocr.md) keeps this task's stage order but shrinks every stage: an ONNX layout stage assigns boxes, one of ten block labels, and a reading order, and a line classifier then routes each line to one of four script recognizers instead of sending region crops to a VLM.[^indra-ocr-card] It is layout-first in shape but line-level in recognition, so it marks where this task degenerates into line-level OCR rather than replacing it.

The comparison makes the fidelity cost measurable within one protocol: on the vendor-run [OmniParseBench](omniparsebench.md) tables Indra OCR scores 92.2 on the layout family against 46.7 on text, while [PP-StructureV3](pp-structurev3.md) — a full pipeline of this task — scores 71.7 on layout and 55.6 on text at roughly 190× the reported per-page time.[^indra-ocr-card][^omniparsebench] **Synthesis:** the bottleneck sits in recognition rather than localization for compact pipelines, which is the pressure that drives this task toward larger per-region recognizers.

## Task characteristics

- **Input:** page image; global layout at low/reduced resolution plus high-res crops per region.[^layout-first-benchmarks]
- **Output:** JSON/Markdown with region types, boxes/masks, reading order, and per-region transcription (including HTML tables, LaTeX formulas); [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) adds cross-page table merging and heading-hierarchy refinement in post-processing.[^paddleocr-vl-1-6-report]
- **Strengths:** high fidelity on dense/small text, explicit grounding, specialist routing for tables/formulas/seals.
- **Limits:** error propagation across stages, deployment complexity, need for coordinated training data flywheel.[^current-ocr-approaches]
- **Evidence class:** every quantitative claim retained here is **Reported** by a vendor, paper, or compiled-synthesis source; none was reproduced in this wiki, and the benchmark protocols behind the numbers differ, so scores are not transferable across the cited benchmark pages.[^layout-first-benchmarks][^hybrid-benchmarks][^omniparsebench]

## Relationships

- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md), [Surya Layout (fast)](surya-layout-fast.md)
- **Contrasts with:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md)
- **Evaluated by:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) and [Hybrid OCR systems and benchmarks](hybrid-ocr-systems-and-benchmarks.md), which keep benchmark-version and protocol differences separate[^layout-first-benchmarks][^hybrid-benchmarks]
- **Evaluated by:** [MiniCPM-OCR evaluation](minicpm-ocr-evaluation.md), which retains vendor-reported parsing and throughput comparisons separately from other protocols.[^minicpm-repo]
- **Evaluated by:** [OmniParseBench](omniparsebench.md), a vendor-run third protocol in which [PP-StructureV3](pp-structurev3.md) is scored as one of three baselines; its page-eligible engines differ from this task, so the numbers stay on that page[^omniparsebench]
- **Extended below VLM scale by:** [Indra OCR](indra-ocr.md), which preserves the layout-then-route shape with line hypotheses and script-specialist recognizers
- **Synthesized in:** [Current OCR approaches](current-ocr-approaches.md)[^current-ocr-approaches]

[^current-ocr-approaches]: Compiled synthesis in this wiki: [Current OCR approaches](current-ocr-approaches.md), § Modular layout-first document parsing and § Practical selection (accessed 2026-10-25).
[^hybrid-benchmarks]: Compiled synthesis in this wiki: [Hybrid OCR systems and benchmarks](hybrid-ocr-systems-and-benchmarks.md), § Scope and complete retained model roster, § Benchmark and metric map, and § Trust limits (accessed 2026-10-25).
[^layout-first-benchmarks]: Compiled synthesis in this wiki: [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md), § Scope and model coverage, § Benchmark and metric map, and § OmniDocBench v1.6 (accessed 2026-10-25).
[^paddleocr-vl-1-6-report]: PaddleOCR Team, *PaddleOCR-VL-1.6 Technical Report*, local LaTeX source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), § PaddleOCR-VL-1.6 Overview (two-stage framework and post-processing engine) and § Evaluation › Document Parsing (accessed 2026-10-25).
[^indra-ocr-card]: Datalab, *Indra OCR model card* (`datalab-to/indra-ocr`), local capture [datalab-to-indra-ocr.md](../raw/datalab-to-indra-ocr.md), § Indra OCR (layout, line-classifier, and recognizer stages), § Output (block labels and reading order), and § Benchmarks › OmniParseBench (accessed 2026-10-25).
[^minicpm-repo]: [MiniCPM-OCR repository](../raw/MiniCPM-OCR/README.md), revision `b33b474136088dc43a2341e94590c804ec0c16a5`, `docs/minicpm_ocr_1dot0_en.md` §§ Model Base and Architecture, Document Parsing Workflow, Evaluation and Throughput; `docs/benchmark_reproduction_en.md` §§ Scoring Methods and Parsing Efficiency Test (inspected 2026-10-28).
[^xiaomi-card]: [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), §§ Usage › Ollama and Use Examples › More code (inspected 2026-10-29); linked repository implementation was not inspected.
[^oxr-readme]: SoMark, [OXR-1.0 README](../raw/OXR-1.0.md), § How it works › Technical Architecture (inspected 2026-10-27).
[^omniparsebench]: Compiled synthesis in this wiki: [OmniParseBench](omniparsebench.md), § Reported structure, § Reported comparison, and § Protocol caveats; the underlying source is a vendor model card and was not run here (accessed 2026-10-25).
