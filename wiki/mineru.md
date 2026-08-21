---
type: Project
title: MinerU
description: MinerU is an OpenDataLab document-parsing project that converts PDFs, office documents, images, and web pages into structured Markdown and JSON through pipeline, VLM, and hybrid backends.
tags: [ocr, document-parsing, pdf, markdown, json, document-ai]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T10:11:40+07:00 }
sources:
  - id: mineru-readme
    resource: ../raw/MinerU.md
    title: "MinerU README"
---

# MinerU

MinerU is OpenDataLab's document-parsing project for converting PDF, images, DOCX, PPTX, XLSX, and web-page inputs into structured Markdown or JSON for retrieval and downstream processing. Its retained README documents three local inference families—`pipeline`, VLM, and hybrid—plus CLI, API, WebUI, and router deployment interfaces.[^mineru-readme]

## Parsing capabilities

The project reports reading-order reconstruction, removal of headers, footers, footnotes, and page numbers, and preservation of headings, paragraphs, lists, images, tables, and formulas. It converts formulas to LaTeX and tables to HTML, detects scanned or garbled PDFs for OCR, and states OCR support for 109 languages.[^mineru-readme]

The README presents three backend families:

| Backend | Documented role | Reported constraints |
| --- | --- | --- |
| `pipeline` | Compatibility-oriented layout/OCR pipeline that can run on CPU or GPU. | The table lists 86.47 OmniDocBench v1.6 overall accuracy, 4 GB minimum VRAM for acceleration, and 16 GB minimum RAM. |
| `vlm-engine` | Higher-accuracy VLM parsing using local inference ecosystems such as vLLM, LMDeploy, or MLX. | The table lists 95.30 accuracy, no pure-CPU support, 8 GB minimum VRAM, and 16 GB minimum RAM. |
| `hybrid-engine` | Higher-accuracy parsing that combines VLM inference with native text extraction to reduce hallucination. | The table lists 95.39 accuracy at `high` effort and 95.26 at `medium`; `medium` is the stated default and does not support image analysis. |

These accuracy, resource, and feature figures are project-reported. The README identifies the accuracy figures as OmniDocBench v1.6 end-to-end overall scores, but does not retain the benchmark protocol or reproduce the measurements.[^mineru-readme]

## Deployment and operation

The documented general installation path is `uv pip install -U "mineru[all]"`; source installation uses `uv pip install -e .[all]`. The simple local CLI form is `mineru -p <input_path> -o <output_path>`; adding `-b pipeline` selects the CPU-capable backend.[^mineru-readme]

The README says the `mineru` CLI acts as an orchestration client for `mineru-api`: without `--api-url`, it starts a temporary local service. `mineru-api` provides asynchronous `POST /tasks` submission, status, and result retrieval, while retaining synchronous `POST /file_parse` compatibility. `mineru-router` presents API-compatible routing and load balancing across multiple services and GPUs.[^mineru-readme]

## Release and licensing notes

The retained README's newest changelog entry is version 3.4, dated 2026-06-18. It reports a `pipeline` OCR upgrade to PP-OCRv6, an approximately 11% OCR-accuracy improvement on OmniDocBench v1.6, roughly doubled OCR processing speed, automatic model-source selection, and reuse of local model caches.[^mineru-readme]

MinerU is stated to use the MinerU Open Source License, described as based on Apache 2.0 with additional conditions. The license text itself was not retained or inspected, so its precise permissions and obligations are not established here.[^mineru-readme]

## Relationships

- **Uses:** [MinerU2.5](mineru2-5.md) and [MinerU2.5-Pro](mineru2-5-pro.md) as the VLM releases named in the project's changelog.[^mineru-readme]
- **Related to:** [MinerU-Diffusion](mineru-diffusion.md), a separately documented OCR model in the same project family.
- **Related to:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md), which recommends evaluating MinerU for difficult PDF conversion; that recommendation is separate source-level synthesis.

## Scope and trust limits

This compilation is based only on the retained project README. Its linked documentation, technical reports, source code, hosted demos, package artifacts, benchmark, and license were not inspected. The source's capabilities, performance, release, hardware, and licensing claims are therefore attributed to the project rather than independently verified.[^mineru-readme]

[^mineru-readme]: OpenDataLab, [*MinerU README*](../raw/MinerU.md) (accessed 2026-08-21). Linked external resources and embedded remote assets were not inspected.
