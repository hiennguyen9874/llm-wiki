---
type: Model System
title: Surya OCR 2
description: Surya OCR 2 is a 650M document-OCR system whose shared VLM produces layout, reading order, OCR content, and table-recognition outputs.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, table-recognition, multilingual]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:20:00Z }
sources:
  - id: surya-ocr-2-model-card
    resource: ../raw/surya-ocr-2.md
    title: Surya OCR 2 model card
---

# Surya OCR 2

Surya OCR 2 is Datalab's 650M-parameter document-OCR system. A shared Qwen3.5-style vision-language model performs page layout, reading order, OCR, and table recognition, while a separate small Torch line-detection model handles text detection.[^surya-ocr-2-model-card]

## Capabilities and outputs

The supplied model card positions Surya for document images and PDFs, including layout classes, ordered content blocks, HTML tables, and KaTeX-compatible LaTeX for inline mathematical content. Full-page OCR returns an HTML sequence of labeled blocks; block mode first runs layout and then recognizes each layout region. Layout output includes canonical labels, geometry, reading-order position, confidence, and raw model output. Table recognition can either derive row-by-column cells or generate full HTML for spanning cells and headers.[^surya-ocr-2-model-card]

The `surya_ocr`, `surya_detect`, `surya_layout`, and `surya_table` CLIs each accept an image, PDF, or directory and write `results.json`. OCR page results include ordered blocks with canonical and raw labels, HTML content, polygons and bounding boxes, confidence, skip/error flags, and page-image geometry.[^surya-ocr-2-model-card]

## Operation

The documented installation is `pip install surya-ocr`. Layout, OCR, and table recognition use a shared VLM served through vLLM on GPUs or llama.cpp on CPUs and Apple Silicon; `SuryaInferenceManager` starts a server unless `SURYA_INFERENCE_URL` names an existing OpenAI-compatible endpoint. The documented automatic backend selects vLLM on NVIDIA hardware and llama.cpp otherwise. Text-line detection is a separate Torch model and does not need this inference backend.[^surya-ocr-2-model-card]

For throughput, the card advises increasing vLLM sequence or token limits, or client-side `SURYA_INFERENCE_PARALLEL`; for llama.cpp, client parallelism should match `llama-server --parallel`. It suggests image preprocessing or resizing toward a maximum 2,048-pixel width for difficult OCR, and documents detector blank/text thresholds as a way to tune line joining.[^surya-ocr-2-model-card]

## Reported evaluation and performance

All results in this section are Datalab-reported and have not been independently reproduced:[^surya-ocr-2-model-card]

- The card reports **83.3** on olmOCR-bench, calling it the highest listed score below 3B parameters. Its table lists Chandra OCR 2 at 85.9, dots.mocr at 83.9, and LightOnOCR 2-1B at 83.2; comparison requires matched benchmark versions and methodology.
- On its 8,413-test `default` preset, the card reports per-source pass rates of 88.3 (arXiv), 99.7 (base), 92.5 (headers/footers), 93.7 (tiny text), 82.4 (multi-column), 41.8 (old scans), 81.4 (old math), and 86.6 (tables).
- Its internal benchmark reports **87.2%** overall across 91 languages, with 38 languages at or above 90% and 76 at or above 80%; its language-specific scores are not an independent multilingual evaluation.
- For full-page OCR at 96 DPI and about 2,400 output tokens per page, the card reports 5.35 pages/s (12,884 tokens/s) at concurrency 128 on one RTX 5090 using vLLM. On Apple Silicon with Metal llama.cpp at parallelism 8, it reports 0.108 pages/s and about 30 W. These are client-side measurements against a running inference server.[^surya-ocr-2-model-card]

The Chandra OCR 2 card instead gives its own overall result as 85.8 ± 0.8. The 85.9 figure in this source is within that stated uncertainty, but the local cards do not provide enough methodology to determine why the displayed values differ.[^surya-ocr-2-model-card]

## Licensing and trust limits

The source says the code is Apache 2.0, while model weights use a modified AI Pubs Open Rail-M license. It describes weights as free for research, personal use, and startups below $5M in funding or revenue; broader commercial use requires Datalab licensing.[^surya-ocr-2-model-card]

This local source is a vendor model card, not an independent technical report. It lacks weights, training data, evaluation code, full benchmark methodology, prompts, and independently reproduced results. All 29 locally referenced image assets—including the size chart and visual examples—are absent from `raw/`, so their visual content was not inspected. Performance, coverage, and licensing claims should be treated as source claims.[^surya-ocr-2-model-card]

## Relationships

- **Compared with:** [Chandra OCR 2](chandra-ocr-2.md), [Multimodal OCR](multimodal-ocr.md)'s dots.mocr implementation, and [LightOnOCR](lightonocr.md) in the source's olmOCR-bench table; these values are not a general ranking without matched evaluation conditions.[^surya-ocr-2-model-card]

[^surya-ocr-2-model-card]: Datalab, *Surya OCR 2 model card*, local [surya-ocr-2.md](../raw/surya-ocr-2.md) (accessed 2026-08-17). The 29 referenced local image assets are absent and were not inspected.
