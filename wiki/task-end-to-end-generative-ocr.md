---
type: Concept
title: "Task: End-to-end generative OCR"
description: End-to-end generative OCR groups VLMs that map full page images directly to ordered Markdown, JSON, HTML, or other structured outputs.
tags: [task, document-parsing, ocr, vision-language-models, image-to-markdown]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T12:00:00+07:00 }
sources:
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
---

# Task: End-to-end generative OCR

End-to-end generative OCR is the task of converting a full document page image (and optional prompt) directly into an ordered structured representation such as Markdown, JSON, HTML, LaTeX, or SVG, unifying text recognition, layout, reading order, and formatting in one autoregressive or diffusion generation pass.

## Models in this task

Core retained models that perform this task as their primary interface:

- [DeepSeek-OCR](deepseek-ocr.md) — DeepEncoder visual compression before 3B MoE decoder
- [DeepSeek-OCR 2](deepseek-ocr-2.md) — DeepEncoder V2 with causal visual token reordering
- [dots.ocr](dots-ocr.md) — 1.7B prompt-controlled layout/content/reading-order
- [FireRed-OCR](firered-ocr.md) — 2B Qwen3-VL adaptation with geometry/semantics-balanced SFT+GRPO
- [HunyuanOCR-1.5](hunyuanocr-1.5.md) — lightweight with DFlash speculative decoding
- [Infinity-Parser](layout-rl-and-infinity-parser.md) (LayoutRL, Qwen2.5-VL-7B) and [Infinity-Parser2](infinity-parser2.md) (Qwen3.5 + task-native GRPO)
- [LightOnOCR](lightonocr.md) — 1B native-resolution ViT + Qwen3 decoder
- [MinerU-Diffusion](mineru-diffusion.md) — 2.5B block-parallel diffusion decoding
- [Multimodal OCR](multimodal-ocr.md) — 3B typed payloads including SVG for graphics
- [Nanonets-OCR2](nanonets-ocr2.md) — multilingual image-to-Markdown with explicit checkbox/signature/watermark handling
- [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) / [NVIDIA Nemotron Parse 2.0](nemotron-parse-2-0.md) — sub-1B encoder-decoder with boxes and element classes
- [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) — 7B Qwen2.5-VL PDF-page extraction
- [OvisOCR2](ovisocr2.md) — 0.8B with 4B-teacher RL, distillation, and fusion
- [Qianfan-OCR](qianfan-ocr.md) — 4B with optional Layout-as-Thought
- [RolmOCR](rolmocr.md) — 7B metadata-independent with rotated-page training
- [Typhoon OCR](typhoon-ocr.md) — 2B Thai–English image-only prompt
- [Unlimited OCR](unlimited-ocr.md) — 3B/500M-active with Reference Sliding Window Attention for multi-page one-shot
- [Chandra OCR](chandra-ocr.md) / [Chandra OCR 2](chandra-ocr-2.md) — Datalab Markdown/HTML/JSON conversion
- [Granite Docling 258M](granite-docling-258m.md) — 258M VLM integrated with Docling

## Task characteristics

- **Input:** single page image at native or dynamic resolution; optional prompt for output format.
- **Output:** ordered Markdown/JSON/HTML/LaTeX/SVG with implicit or explicit reading order; some variants emit bounding boxes.
- **Strengths:** one model handles layout, text, tables, formulas, and figures; flexible prompting.
- **Limits:** long output sequences, hallucination/repetition risk, sensitivity to schema, KV-cache growth for multi-page (addressed by [Optical Context Compression](optical-context-compression.md) and [Reference Sliding Window Attention](reference-sliding-window-attention.md)).

## Relationships

- **Contrasts with:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) which decomposes layout then recognition; [Task: Detector–recognizer OCR](task-detector-recognizer-ocr.md) which targets word/line boxes only.
- **Evaluated by:** [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md)
- **Uses:** [Document-parser data flywheel](document-parser-data-flywheel.md) and [DOM-based document synthesis](dom-based-document-synthesis.md) for long-tail data
