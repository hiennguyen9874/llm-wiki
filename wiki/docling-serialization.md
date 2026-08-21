---
type: Concept
title: Docling serialization
description: Docling serializers convert a DoclingDocument and its subcomponents to textual formats, with target-format trade-offs that notably flatten table spans in Markdown and LaTeX.
tags: [docling, serialization, markdown, html, tables, document-parsing]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-serialization-docs
    resource: ../raw/docling-concepts/serialization.md
    title: Docling serialization documentation
---

# Docling serialization

A Docling serializer is initialized with a `DoclingDocument` and produces its textual representation. `BaseDocSerializer.serialize()` also returns metadata identifying the document components that contributed to that serialization.[^docling-serialization-docs]

## Extensible serializer hierarchy

Docling defines document, text, table, picture, list, and inline serializer abstractions, plus a serializer-provider abstraction that separates serialization strategy from the document instance. The documented base types include `BaseDocSerializer`, component-specific base serializers, and `BaseSerializerProvider`; `MarkdownDocSerializer` is one concrete subclass.[^docling-serialization-docs]

`DoclingDocument` provides shorthand export methods for Markdown, HTML, and DocTags. These methods instantiate and delegate to their respective predefined serializers.[^docling-serialization-docs]

## Table-span fidelity by target

`TableData.grid` retains cell-span metadata, including row and column spans and starting offsets. JSON preserves that model losslessly; Docling's Doclang and DocTags encode spans through OTSL continuation tokens; and HTML emits native `rowspan` and `colspan` attributes.[^docling-serialization-docs]

Markdown cannot represent cell spans, so its serializer writes text only at the span origin and renders other covered grid positions as empty cells. The current LaTeX serializer similarly flattens spans because it does not emit `\multirow` or `\multicolumn`; WebVTT does not serialize tables.[^docling-serialization-docs]

For workflows that depend on merged headers or other exact table structure, the documentation recommends HTML or dictionary export rather than Markdown. A caller can alternatively override a format's table serializer by subclassing `BaseTableSerializer` and supplying it when constructing the document serializer.[^docling-serialization-docs]

## Relationships

- **Depends on:** [Docling document representation](docling-document-representation.md).[^docling-serialization-docs]
- **Used by:** [Docling architecture](docling-architecture.md) as a documented downstream conversion operation.[^docling-serialization-docs]
- **Related to:** [Docling native chunking](docling-native-chunking.md), which is the document-structured alternative to exporting text and chunking it afterward.[^docling-serialization-docs]

[^docling-serialization-docs]: Docling, [*Serialization*](../raw/docling-concepts/serialization.md) (accessed 2026-08-21).