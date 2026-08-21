---
type: Synthesis
title: PDF-to-Markdown parser architectures
description: MinerU, Marker, Docling, and OpenDataLoader-PDF occupy distinct model-first, modular, document-IR, and deterministic-geometry positions in a PDF-to-Markdown pipeline.
tags: [ocr, document-parsing, pdf, markdown, architecture]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T10:10:29+07:00 }
sources:
  - id: architecture-comparison
    resource: ../raw/ocr-tool-architecture-chatgpt.md
    title: Architectural comparison of MinerU, Marker, Docling, and OpenDataLoader-PDF
---

# PDF-to-Markdown parser architectures

MinerU, Marker, Docling, and OpenDataLoader-PDF should not be treated as interchangeable PDF parsers: the source characterizes MinerU as a specialized-model document-reconstruction pipeline, Marker as a modular pipeline built around Surya, Docling as a structured-document-IR framework, and OpenDataLoader-PDF as a deterministic geometry-first parser with optional AI. These are source-level architectural descriptions, not independently verified implementation audits.[^architecture-comparison]

## Architectural roles

| System | Architectural role reported by the source | Practical implication (synthesis) |
|---|---|---|
| MinerU | Uses layout analysis, text extraction/OCR, specialized table and formula recognition, and reading-order recovery to reconstruct semantic document blocks. | Prefer evaluation on scientific, scanned, or layout-heavy material where recognizing regions matters more than minimal compute. |
| Marker | Combines native PDF extraction with Surya layout/OCR/table components and processors that transform document blocks; it can use an LLM/VLM to correct difficult extracted blocks. | Its modular stages make it a candidate where an application needs controllable processing or selective expensive correction. |
| Docling | Centers conversion on a `DoclingDocument` intermediate representation that serializes to Markdown, JSON, or HTML; the source identifies TableFormer for table structure. | Retaining the IR can avoid parsing Markdown again before hierarchy-aware chunking or RAG processing. |
| OpenDataLoader-PDF | Starts from PDF objects and geometry, using XY-Cut++-style whitespace segmentation for reading order, with optional AI for harder cases. | A geometry-first path can be attractive for clean digital-born PDFs and CPU-bound volume, but should be evaluated on scans and unusual layouts. |

## Extraction is not figure reconstruction

The source distinguishes extracting an embedded PDF image object from exporting the complete visual region a reader recognizes as a figure. A figure may combine raster images, vector graphics, labels, and arrows; extracting only an image object can omit the other components. A parser that detects a figure bounding box can instead render or crop the entire region, which better preserves the visible figure.[^architecture-comparison]

## Routing pattern

The source proposes a hybrid production design: classify a PDF, use a fast deterministic or document-IR path for suitable digital PDFs, apply quality checks, and escalate suspicious or scan/complex pages to a model-heavy parser or VLM. This is an architectural recommendation rather than a reported, validated performance result.[^architecture-comparison]

```text
PDF → classify / fast parse → quality checks → accept
                                      └──────→ model-heavy escalation → accept
```

## Evidence limits

- This source is a ChatGPT-generated comparison. Its linked repositories and product documentation were not inspected in this ingest, so component names, dependency assignments, and current capabilities remain unverified.[^architecture-comparison]
- The source gives no controlled benchmark demonstrating that the proposed routing design improves accuracy, cost, or throughput.
- Individual product versions may change their model stacks and export behavior; do not infer current operational compatibility from this architectural summary alone.

## Relationships

- **Related to:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md), which compares the same tools by use case and source-reported output characteristics.
- **Uses:** [Current OCR approaches](current-ocr-approaches.md) for the broader distinction between modular layout-first and end-to-end document-processing approaches.

[^architecture-comparison]: User-supplied [*Architectural comparison of MinerU, Marker, Docling, and OpenDataLoader-PDF*](../raw/ocr-tool-architecture-chatgpt.md), accessed 2026-08-21. Its external links were not independently inspected for this compilation.
