---
type: Concept
title: "Task: End-to-end generative OCR"
description: End-to-end generative OCR groups VLMs that map full page images directly to ordered Markdown, JSON, HTML, or other structured outputs.
tags: [task, document-parsing, ocr, vision-language-models, image-to-markdown]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-10-30T02:16:13Z }
sources:
  - id: unlimited-ocr-2-report
    resource: ../raw/Unlimited-OCR-2.pdf
    kind: paper
    title: Unlimited OCR Works 2
  - id: current-ocr-approaches
    resource: ../wiki/current-ocr-approaches.md
    title: Current OCR approaches
  - id: end-to-end-benchmarks
    resource: ../wiki/end-to-end-generative-ocr-vlm-benchmarks.md
    title: End-to-end generative OCR VLM benchmarks
  - id: deepseek-ocr-2-report
    resource: ../raw/2601.20552_DeepSeek-OCR-2/main.tex
    title: DeepSeek-OCR 2 Technical Report
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
  - id: ovisocr3-model-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
  - id: lightonocr-3
    resource: ../wiki/lightonocr-3.md
    title: LightOnOCR-3
  - id: surya-25-card
    resource: ../raw/surya-ocr-2.5-hf.md
    kind: model-card
    title: Surya OCR 2.5 model card
---

# Task: End-to-end generative OCR

End-to-end generative OCR is the task of converting a full document page image (and optional prompt) directly into an ordered structured representation such as Markdown, JSON, HTML, LaTeX, or SVG, unifying text recognition, layout, reading order, and formatting in one autoregressive or diffusion generation pass.[^current-ocr-approaches]

## Models in this task

Core retained models that perform this task as their primary interface:

- [DeepSeek-OCR](deepseek-ocr.md) — DeepEncoder visual compression before 3B MoE decoder
- [DeepSeek-OCR 2](deepseek-ocr-2.md) — DeepEncoder V2 with causal visual token reordering[^deepseek-ocr-2-report]
- [dots.ocr](dots-ocr.md) — 1.7B prompt-controlled layout/content/reading-order
- [FireRed-OCR](firered-ocr.md) — 2B Qwen3-VL adaptation with geometry/semantics-balanced SFT+GRPO
- [HunyuanOCR-1.5](hunyuanocr-1.5.md) — lightweight with DFlash speculative decoding
- [Infinity-Parser](layout-rl-and-infinity-parser.md) (LayoutRL, Qwen2.5-VL-7B) and [Infinity-Parser2](infinity-parser2.md) (Qwen3.5 + task-native GRPO)[^infinity-parser2-report]
- [LightOnOCR](lightonocr.md) — 1B native-resolution ViT + Qwen3 decoder; superseded for deployment by [LightOnOCR-3](lightonocr-3.md), which keeps the 1B architecture and adds a grounding mode over an empty-prompt Markdown transcription default[^lightonocr-3]
- [MinerU-Diffusion](mineru-diffusion.md) — 2.5B block-parallel diffusion decoding
- [Multimodal OCR](multimodal-ocr.md) — 3B typed payloads including SVG for graphics
- [Nanonets-OCR2](nanonets-ocr2.md) — multilingual image-to-Markdown with explicit checkbox/signature/watermark handling
- [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) / [NVIDIA Nemotron Parse 2.0](nemotron-parse-2-0.md) — sub-1B encoder-decoder with boxes and element classes
- [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) — 7B Qwen2.5-VL PDF-page extraction
- [OvisOCR2](ovisocr2.md) — 0.8B with 4B-teacher RL, distillation, and fusion
- [OvisOCR3](ovisocr3.md) — 0.8B prompt-conditioned parsing, OCR, KIE, figure captioning, and cross-page tables[^ovisocr3-model-card]
- [Qianfan-OCR](qianfan-ocr.md) — 4B with optional Layout-as-Thought
- [RolmOCR](rolmocr.md) — 7B metadata-independent with rotated-page training
- [Typhoon OCR](typhoon-ocr.md) — 2B Thai–English image-only prompt
- [Xiaomi-OCR-0](xiaomi-ocr-0.md) — 0.8B prompt-driven page parsing with OTSL tables and LaTeX formulas.[^xiaomi-card]
- [Unlimited OCR](unlimited-ocr.md) — 3B/500M-active with Reference Sliding Window Attention for multi-page one-shot; [Unlimited OCR 2](unlimited-ocr-2.md) adds sparse visual routing and chunked decoding for longer documents.[^unlimited-ocr-2-report]
- [Chandra OCR](chandra-ocr.md) / [Chandra OCR 2](chandra-ocr-2.md) — Datalab Markdown/HTML/JSON conversion
- [Granite Docling 258M](granite-docling-258m.md) — 258M VLM integrated with Docling

### Boundary: shared full-page and layout-first VLM

[Surya OCR 2.5](surya-ocr-2-5.md) defaults to one full-page VLM call yielding ordered HTML blocks with labels and geometry, while its optional block mode first runs layout and then OCR per region. Its separate line detector is not required by the documented full-page example; classify it as a boundary system rather than assuming every operation is a single call.[^surya-25-card]

## Task characteristics

- **Input:** single page image at native or dynamic resolution; optional prompt for output format.
- **Output:** ordered Markdown/JSON/HTML/LaTeX/SVG with implicit or explicit reading order; some variants emit bounding boxes.
- **Strengths:** one model handles layout, text, tables, formulas, and figures; flexible prompting.
- **Limits:** long output sequences, hallucination/repetition risk, sensitivity to schema, KV-cache growth for multi-page (addressed by [Optical Context Compression](optical-context-compression.md) and [Reference Sliding Window Attention](reference-sliding-window-attention.md)).
- **Multi-task and multi-page extensions:** task prompts can select parsing, OCR, extraction, captioning, or table reconstruction; two-image requests extend the same checkpoint to page-pair table merging.[^ovisocr3-model-card] The smaller form of the same trend is a two-prompt contract: [LightOnOCR-3](lightonocr-3.md) keeps an empty prompt for Markdown transcription and reserves the literal `grounding` prompt for labelled boxes, image descriptions, and chart-to-table output, warning that other instructions are out of distribution and reporting roughly 25% more output tokens in grounding mode.[^lightonocr-3]

## Relationships

- **Contrasts with:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) which decomposes layout then recognition; [Task: Detector–recognizer OCR](task-detector-recognizer-ocr.md) which targets word/line boxes only.
- **Evaluated by:** [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md)[^end-to-end-benchmarks]
- **Uses:** [Document-parser data flywheel](document-parser-data-flywheel.md) and [DOM-based document synthesis](dom-based-document-synthesis.md) for long-tail data
- **Extended by:** [Task: Cross-page table reconstruction](task-cross-page-table-reconstruction.md) for tables that continue across page boundaries.

[^surya-25-card]: Datalab, [Surya OCR 2.5 model card](../raw/surya-ocr-2.5-hf.md), §§ Usage, OCR (text recognition) › From python, and Training (inspected 2026-10-30); reported interface, not executed.
[^xiaomi-card]: [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), §§ About the model and Usage › Task prompts (inspected 2026-10-29).
[^unlimited-ocr-2-report]: Baidu ERNIE Team, [Unlimited OCR Works 2](../raw/Unlimited-OCR-2.pdf), §§3.2–3.4.
[^current-ocr-approaches]: Compiled synthesis in this wiki: [Current OCR approaches](current-ocr-approaches.md), § End-to-end generative document VLMs and § Cross-cutting technical directions (accessed 2026-10-25).
[^end-to-end-benchmarks]: Compiled synthesis in this wiki: [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md), § Scope and model coverage, § Benchmark and metric map, and § Trust limits; that page is the retained catalog of this family's datasets, metrics, and protocol conflicts (accessed 2026-10-25).
[^deepseek-ocr-2-report]: DeepSeek-AI, *DeepSeek-OCR 2 Technical Report*, local LaTeX source at [main.tex](../raw/2601.20552_DeepSeek-OCR-2/main.tex), § Methodology (causal visual token reordering) and § Evaluation (accessed 2026-10-25).
[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX sources at [latex/introduction.tex](../raw/2607.07836_Infinity-Parser2/latex/introduction.tex) and [latex/experiments.tex](../raw/2607.07836_Infinity-Parser2/latex/experiments.tex), with the task-native GRPO description in [latex/method.tex § Model Training](../raw/2607.07836_Infinity-Parser2/latex/method.tex) (accessed 2026-10-25).
[^lightonocr-3]: Compiled synthesis in this wiki: [LightOnOCR-3](lightonocr-3.md), § Prompt modes and § Grounding output contract; the 25% figure is vendor-reported and the family publishes no benchmark table (accessed 2026-10-25).
[^ovisocr3-model-card]: ATH-MaaS, *OvisOCR3 model card*, local source at [ATH-MaaS-OvisOCR3.md](../raw/ATH-MaaS-OvisOCR3.md), § Introduction, § Capabilities, and § Task-Specific Usage (accessed 2026-10-25).
