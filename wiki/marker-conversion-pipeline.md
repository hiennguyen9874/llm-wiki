---
type: Concept
title: Marker conversion pipeline
description: Marker builds a structured document from provider text and layout, selectively applies OCR, and reconstructs tables before rendering.
tags: [ml, ocr, document-parsing, pdf]
status: draft
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T03:10:11Z }
sources:
  - id: marker-repo
    resource: ../raw/marker/README.md
    scope: ../raw/marker/
    kind: code
    revision: 71dd5fd7e51ab24f8624b6ba2fcb6014b4e40ed4
    title: Marker repository
---

# Marker conversion pipeline

**Observed:** At revision `71dd5fd`, [Marker](marker.md)'s `PdfConverter` chooses a provider, builds pages and layout, assigns text or OCR, groups structure, runs an ordered processor chain, and invokes a renderer. The package is `marker-pdf` 2.1.0 and declares `surya-ocr` 0.23.x and `pdftext` 0.7.x dependencies.[^marker-repo]

## Layout and text routing

**Observed:** Providers dispatch by file content and extension; PDF text and page images feed the document builders. `DocumentBuilder` creates pages, then runs layout, line assignment, high-resolution rendering as needed, and OCR unless disabled. `StructureBuilder` groups captions and lists before the default processors run. Text-layer pages are checked for quality, layout coverage, and problematic overlap; the line builder can flag individual bad blocks. Balanced mode promotes any flagged block to page OCR, while fast mode can repair individual blocks and promotes when the flagged fraction exceeds its configured threshold. The converter defaults to balanced on CUDA and fast otherwise.[^marker-repo]

**Observed:** Equation recognition is separately processed; `disable_ocr` suppresses its recognition calls. Inline math recognition defaults on in balanced mode. The OCR builder can replace page structure from full-page recognition or repair selected blocks.[^marker-repo]

## Tables

**Observed:** `TableProcessor` accepts existing full-page OCR HTML, otherwise attempts CPU text-layer reconstruction and falls back to cropped recognition if reconstruction is absent or scores below 0.75 in balanced or 0.5 in fast mode. OCR-disabled runs skip that fallback. This checkout's processor explicitly says there is no dedicated table-structure model; its score is an internal heuristic, not independent accuracy verification. After table processing it releases cached PDF text pages when tables were found.[^marker-repo]

## Coverage and evidence limits

This is a partial static repository ingest, not a runtime audit. The README, package metadata, converter, provider, builder, table and output paths, configuration, serving code, selected processors and tests, and benchmark documentation were inspected to varying depths; the parallel exploration also sampled services and CI. Individual remaining processors, LLM prompts, tests, dependencies and benchmark competitors remain pending. Decorative images and duplicate example outputs were not visually inspected; generated lockfile details, vendored test PDFs and contributor-signature records were excluded from synthesis. Surya implementation and benchmark datasets are external. No conversion, model, test suite, or benchmark was run; examples and reported metrics are not reproduced. The checkout is a staged, uncommitted submodule pin, so repository distribution requires committing that pin.[^marker-repo]

## Relationships

- **Uses:** [Marker document representation](marker-document-representation.md) as the structured result passed to processors and renderers.
- **Related to:** [Marker deployment and configuration](marker-deployment-and-configuration.md), which describes execution and privacy boundaries.

[^marker-repo]: Datalab, *Marker repository*, revision `71dd5fd`: `pyproject.toml::[project]`; `marker/converters/pdf.py::PdfConverter.build_document`; `marker/providers/registry.py::provider_from_filepath`; `marker/builders/document.py::DocumentBuilder.__call__`; `marker/builders/line.py::LineBuilder.get_all_lines`, `flag_bad_blocks`; `marker/builders/ocr.py::OcrBuilder.__call__`; `marker/builders/structure.py::StructureBuilder.__call__`; `marker/processors/equation.py::EquationProcessor`; `marker/processors/table.py::TableProcessor`; README §§ Installation, How it works, Benchmarks.
