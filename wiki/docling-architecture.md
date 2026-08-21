---
type: Concept
title: Docling architecture
description: Docling converts each input format through a configurable backend and pipeline into a DoclingDocument, which can then be exported, serialized, or chunked.
tags: [docling, document-parsing, architecture, document-conversion]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-architecture-docs
    resource: ../raw/docling-concepts/architecture.md
    title: Docling architecture documentation
---

# Docling architecture

Docling's document converter selects a format-specific backend and an execution pipeline, with relevant options, then returns a conversion result containing a `DoclingDocument`. That representation is the handoff for export, serialization, and chunking.[^docling-architecture-docs]

## Conversion boundary

- The converter has a default mapping from document format to backend and pipeline, but callers can parameterize that choice; the documentation calls out PDF backends and pipeline options as an example.[^docling-architecture-docs]
- A backend handles format-specific parsing, while a pipeline orchestrates execution. The source's architecture diagram marks some components as subclassable base classes for specialized implementations.[^docling-architecture-docs]
- The conversion result carries the resulting [Docling document representation](docling-document-representation.md), rather than requiring downstream code to begin from an exported text format.[^docling-architecture-docs]

## Downstream paths

A `DoclingDocument` can be exported directly, passed to a [Docling serializer](docling-serialization.md), or passed to [Docling native chunking](docling-native-chunking.md). This preserves a choice between a document-structured workflow and a textual export workflow.[^docling-architecture-docs]

## Relationships

- **Uses:** [Docling document representation](docling-document-representation.md) as the conversion result's fundamental document model.[^docling-architecture-docs]
- **Uses:** [Docling serialization](docling-serialization.md) and [Docling native chunking](docling-native-chunking.md) as documented downstream operations.[^docling-architecture-docs]
- **Related to:** [PDF-to-Markdown parser architectures](pdf-to-markdown-parser-architectures.md), whose retained comparison independently characterizes Docling as a structured-document-IR framework.

[^docling-architecture-docs]: Docling, [*Architecture*](../raw/docling-concepts/architecture.md) (accessed 2026-08-21).