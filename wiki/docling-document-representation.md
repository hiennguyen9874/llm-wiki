---
type: Concept
title: Docling document representation
description: DoclingDocument is Docling's Pydantic document intermediate representation, combining typed content items, hierarchical body and furniture trees, layout, and provenance when available.
tags: [docling, document-parsing, intermediate-representation, pydantic, provenance]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-document-docs
    resource: ../raw/docling-concepts/docling_document.md
    title: DoclingDocument documentation
---

# Docling document representation

`DoclingDocument` is Docling v2's Pydantic document representation. It can encode typed document content, sections and groups, main-body versus header/footer furniture, layout bounding boxes when available, and provenance.[^docling-document-docs]

## Content and structure

Its content-item collections are `texts`, `tables`, `pictures`, and `key_value_items`. The items inherit from `DocItem`; text items have a `TextItem` base, while tables and pictures use `TableItem` and `PictureItem` and can carry structure annotations.[^docling-document-docs]

The structural layer consists of a `body` root for the main content, a `furniture` root for items outside that body, and `groups` that act as non-content containers such as lists or chapters. These fields contain `NodeItem` instances; parents and children are represented through JSON pointers.[^docling-document-docs]

Reading order is encoded by the body tree and the order of each item's children. The documentation's examples show ordinary content items nested under a title or heading, with list containers held in the top-level `groups` collection.[^docling-document-docs]

## Construction and use

The Pydantic types live in `docling_core.types.doc`, and the format provides APIs for constructing a document from scratch.[^docling-document-docs] It is the input to [Docling native chunking](docling-native-chunking.md) and the model serialized by [Docling serialization](docling-serialization.md).

## Relationships

- **Used by:** [Docling architecture](docling-architecture.md) as the conversion result's fundamental representation.[^docling-document-docs]
- **Used by:** [Docling serialization](docling-serialization.md) and [Docling native chunking](docling-native-chunking.md).[^docling-document-docs]
- **Related to:** [Granite Docling 258M](granite-docling-258m.md), whose retained model card says DocTags output can be converted to this representation.

[^docling-document-docs]: Docling, [*Docling Document*](../raw/docling-concepts/docling_document.md) (accessed 2026-08-21).