---
type: Tool
title: Marker
description: Marker is Datalab's open-source document-conversion pipeline that produces Markdown, JSON, HTML, or chunks from PDFs and other document formats using text extraction, layout analysis, and selective VLM OCR.
tags: [ocr, document-parsing, pdf, markdown, layout-analysis, table-recognition]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:14:21Z }
sources:
  - id: marker-readme
    resource: ../raw/marker.md
    title: Marker README
---

# Marker

Marker is Datalab's document-conversion pipeline for PDFs, images, PPTX, DOCX, XLSX, HTML, and EPUB. It emits Markdown, JSON, HTML, or RAG-oriented chunks, combining PDF text-layer extraction, layout analysis, table reconstruction, and selective VLM OCR; it can optionally use an external LLM for further correction.[^marker-readme]

## Conversion pipeline and modes

Marker describes two conversion modes. **Balanced**, its default on GPUs, uses the Surya VLM for layout, inline-math OCR, and whole-page re-OCR when embedded text is poor. **Fast**, its default on CPU and MPS, uses an RF-DETR layout detector and `pdftext`, limits VLM work to equations and suspect blocks, and runs a whole-page VLM pass only for scanned or mostly bad pages. In either mode, `--disable_ocr` disables VLM calls entirely and leaves a text-layer-only path; `--force_ocr` instead re-OCRs every page.[^marker-readme]

The source says digital tables are reconstructed from the PDF text layer, with low-confidence or scanned-table cases falling back to the VLM. It also removes running headers and footers by default, extracts images unless disabled, and supports custom processors and a correction prompt in LLM mode. These are documented implementation behaviors, not independently tested results.[^marker-readme]

## Interfaces and deployment

Install the PDF path with `pip install marker-pdf`; the `[full]` extra is needed for non-PDF formats. `marker_single FILE` converts one file, while `marker DIRECTORY` processes a directory. Both expose options for mode, page range, output format, output directory, OCR, custom processors, and LLM service. The Python API exposes `PdfConverter`, `TableConverter`, and `OCRConverter`; the table converter can emit HTML tables or JSON blocks with page geometry.[^marker-readme]

Layout, OCR, and table recognition use a locally served Surya VLM. Marker starts vLLM in Docker on NVIDIA GPUs or `llama.cpp` elsewhere unless `SURYA_INFERENCE_URL` points to an OpenAI-compatible server already running. Multi-file conversion shares one inference server among conversion workers and automatically budgets VLM concurrency; `--disable_ocr` starts no inference server.[^marker-readme]

With `--use_llm`, the documented services include Gemini, Google Vertex, Ollama, Claude, OpenAI-compatible endpoints, Azure OpenAI, and OpenRouter. The source identifies Gemini as the default service and says LLM mode can improve difficult tables, inline mathematics, and forms; using a third-party service has its own credential, cost, and data-handling implications.[^marker-readme]

## Outputs and reported performance

Markdown output can include image links, formatted tables, LaTeX equations, and fenced code. JSON is a hierarchical page-and-block representation with geometry, HTML, section hierarchy, and optionally encoded images; chunks flatten top-level page blocks for RAG use. Metadata includes a computed table of contents and per-page extraction-method and block-count statistics.[^marker-readme]

All figures below are Datalab-reported olmOCR-bench results, not independently reproduced. The README reports the following pipeline scores and sustained concurrent throughput on one B200 host:[^marker-readme]

| Mode | Overall | Digital-only | Throughput |
|---|---:|---:|---:|
| Balanced (GPU) | 76.0 | 83.5 | 2.9 pages/s |
| Fast (GPU) | 66.6 | 71.6 | 7.4 pages/s |
| Fast, no OCR (CPU) | 43.6 | 55.8 | 23.7 pages/s |

The source compares these results with other systems, but its benchmark version, hardware/configurations for competitors, and methodology should be checked before treating the table as a general leaderboard. It states that the overall score is a macro-average across eight categories and that its no-OCR mode is designed for born-digital text-layer extraction rather than scans or LaTeX-level mathematics.[^marker-readme]

## Licensing and evidence limits

The source states that Marker code is Apache 2.0. It says model weights use a modified AI Pubs Open Rail-M license, are free for research, personal use, and startups under $5M funding or revenue, and require Datalab licensing for broader commercial use.[^marker-readme]

This is a vendor-maintained README rather than an independent evaluation or security review. Its benchmark, throughput, accuracy, licensing, data-retention, and hosted-service claims are source claims. Five referenced local image assets—the logo and four benchmark figures—are absent from `raw/`, so their visual content was not inspected.

## Relationships

- **Uses:** [Surya OCR 2](surya-ocr-2.md) as its layout, OCR, and table-recognition VLM backend; Marker is a selective text-layer/VLM pipeline, whereas the Surya page describes the underlying OCR system.[^marker-readme]
- **Related to:** [Chandra OCR 2](chandra-ocr-2.md), Datalab's separate hosted document-OCR offering named as a higher-accuracy alternative in this source.[^marker-readme]
- **Related to:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md) and [PDF-to-Markdown parser architectures](pdf-to-markdown-parser-architectures.md), which contain earlier source-qualified comparisons involving Marker.

[^marker-readme]: Datalab, *Marker README*, local [marker.md](../raw/marker.md) (accessed 2026-08-21).