---
type: Concept
title: Marker document representation
description: Marker represents pages as typed, geometrically located block trees and renders them as Markdown, HTML, hierarchical JSON, or flattened chunks.
tags: [ml, ocr, document-parsing, document-representation]
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

# Marker document representation

**Observed:** [Marker](marker.md) builds a document of pages and typed blocks with geometry and child references; the same representation supports several output renderers. Blocks may hold HTML or recursively refer to children, and page structure records their order.[^marker-repo]

## Rendering and extraction

- **Observed:** JSON preserves a tree with block IDs, types, polygons, HTML, children, section hierarchy and images. Some HTML contains `content-ref` placeholders; `marker.output.json_to_html` resolves references for consumers needing assembled HTML.[^marker-repo]
- **Observed:** Chunk output flattens top-level page blocks, assembling child HTML and retaining page number, geometry, hierarchy and images. It is a block-oriented output, not inherently a token-sized or semantic chunking algorithm.[^marker-repo]
- **Reported:** Markdown can include image links, formatted tables, math and fenced code; metadata includes table of contents and page statistics. Image extraction and page-header/footer retention are configurable.[^marker-repo]
- **Observed:** `OCRConverter` forces OCR configuration, uses an OCR JSON renderer and skips the normal structure builder; `TableConverter` restricts output structure to table-related blocks. Their output should not be assumed identical to the full PDF pipeline.[^marker-repo]

Static reading only: rendering, round trips and bounding-box fidelity were not tested. Additional schema classes, edge cases and renderer tests remain pending.[^marker-repo]

## Relationships

- **Depends on:** [Marker conversion pipeline](marker-conversion-pipeline.md) for the block tree that renderers consume.
- **Related to:** [Docling document representation](docling-document-representation.md), another structured representation for document parsing.

[^marker-repo]: Datalab, *Marker repository*, revision `71dd5fd`: README §§ Extract blocks, Output Formats; `marker/schema/blocks/base.py::Block`, `BlockId`; `marker/schema/document.py::Document`; `marker/renderers/json.py::JSONRenderer.extract_json`; `marker/renderers/chunk.py::json_to_chunks`; `marker/output.py::json_to_html`; `marker/converters/ocr.py::OCRConverter`; `marker/converters/table.py::TableConverter`.
