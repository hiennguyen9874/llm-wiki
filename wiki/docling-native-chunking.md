---
type: Concept
title: Docling native chunking
description: Docling native chunkers operate on a DoclingDocument to emit text chunks with metadata, preserving document structure before optional token-aware splitting and merging.
tags: [docling, chunking, rag, document-parsing, embeddings]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:17:04Z }
sources:
  - id: docling-chunking-docs
    resource: ../raw/docling-concepts/chunking.md
    title: Docling chunking documentation
---

# Docling native chunking

Docling's native chunkers take a `DoclingDocument` and emit a stream of text chunks with metadata. This differs from exporting Markdown first and applying arbitrary post-processing chunking, because native chunkers can operate on the document structure directly.[^docling-chunking-docs]

## Base interface

A `BaseChunker` implementation supplies `chunk(dl_doc, **kwargs)`, which returns `Iterator[BaseChunk]`, and `contextualize(chunk)`, which returns a potentially metadata-enriched serialization intended for embedding or generation inputs. Framework integrations such as LlamaIndex use this interface, allowing built-in, custom, and third-party chunkers.[^docling-chunking-docs]

## Built-in strategies

- **HierarchicalChunker** creates a chunk for each detected document element using structural information and relevant metadata such as headings and captions. It merges list items by default, with an option to disable that behavior.[^docling-chunking-docs]
- **HybridChunker** begins with hierarchical chunks, splits only chunks oversized for a user-provided tokenizer, then optionally merges undersized successive peers sharing headings and captions. `merge_peers` defaults to `True`.[^docling-chunking-docs]
- For tables that span chunks, HybridChunker repeats headers by default. Its optional overflow behavior can omit a repeated header for a row that fits only without it.[^docling-chunking-docs]
- **LineBasedTokenChunker** is token-aware while preserving line boundaries where possible, making it suited to tables, code, logs, and lists. It supports a repeated prefix and can omit it for otherwise-overflowing lines.[^docling-chunking-docs]

## Selection boundary

Use native chunking when the structure and metadata of a [Docling document representation](docling-document-representation.md) should inform chunks. Exporting through [Docling serialization](docling-serialization.md) and then chunking remains the documented alternative when a downstream system owns the text-level policy.[^docling-chunking-docs]

## Relationships

- **Depends on:** [Docling document representation](docling-document-representation.md).[^docling-chunking-docs]
- **Used by:** [Docling architecture](docling-architecture.md) as a documented downstream operation.[^docling-chunking-docs]
- **Related to:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md), which discusses Docling in a RAG-oriented conversion context.

[^docling-chunking-docs]: Docling, [*Chunking*](../raw/docling-concepts/chunking.md) (accessed 2026-08-21).