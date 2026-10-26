---
type: Concept
title: WeKnora document parsing and adaptive chunking
description: Parser-engine routing, streaming docreader output, validated chunking strategies, and parent-child indexing inputs.
tags: [ml, weknora, ingestion, chunking]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a258
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora separates document parsing from application-side chunking and indexing. **Observed:** Python docreader turns file/URL requests into structured parse output with Markdown and image references; the Go ingestion service chooses chunking configuration and writes indexing inputs. Adaptive chunking tries structural strategies and validates their output before falling back to a legacy splitter.[^weknora]

## Parser routing and streaming

`docreader/parser/registry.py::ParserEngineRegistry.get_parser_class` tries a requested engine, then a file-type default, then builtin support; unsupported requests return an error listing compatible engines. PPT/PPTX/CSV have a MarkItDown default. Magic-byte detection can correct a mislabeled OLE file's type. **Synthesis:** accepted engine preferences do not necessarily imply that exact engine produced the content; fallback can affect parsing quality.[^weknora]

**Observed:** `DocReaderServicer` exposes unary and streaming reads; empty parse output becomes a response error field. Streaming emits metadata then images individually, releasing source image entries as it goes. Parsers without a lazy stream implementation may still materialize images first. Large-request cleanup is a separate worker-return mechanism, not proof of constant-memory parsing.[^weknora]

`docreader/config.py` declares four gRPC workers, port 50051, and a 50 MB file limit. HTML main-content extraction is off by default. The parser registry covers builtin, MarkItDown, and OpenDataLoader routes; Go-side converter internals and individual format parsers were not audited.[^weknora]

## Chunking contracts

**Observed defaults:** base size 512 characters, overlap 80; parent size 4,096 and child size 384. Parent/child overlap derives from child size, and the token limit applies to children. Chunk content retains source rune offsets; contextual heading breadcrumbs are separate and are prepended for embedding rather than silently changing the source slice.[^weknora]

The `auto` strategy profiles headings and structural markers, tries heading/heuristic splitting where appropriate, and always retains legacy splitting as a fallback (`strategy.go::resolveChainWithProfile`). `ValidateChunks` rejects degenerate candidates such as empty output, implausibly tiny chunks, oversized chunks, or one chunk for an overly long document. Protected spans cover code, math, Markdown links/images, and tables, but large spans still have a hard split bound.[^weknora]

Token limits use language-dependent character estimates with a 0.9 safety factor, **not** exact tokenization. `knowledge_process.go::processChunks` checks aborted/superseded attempts and resolves indexing dependencies before removing old chunks. Only selected guards were read; this is not a complete transactional-index replacement guarantee.[^weknora]

## Relationships

- Feeds [hybrid retrieval](weknora-hybrid-retrieval.md) and [automatic wiki compilation](weknora-wiki-compilation.md).
- External [datasource sync](weknora-datasource-sync.md) supplies another ingestion path.
- Parsing/indexing stages use [worker queues](weknora-task-queues.md).

## Coverage limits

Parser facade/registry/configuration, chunking framework, and selected ingestion guards were inspected; most format parsers, heading/heuristic bodies, Go AnyDoc/MinerU/PaddleOCR converters, OCR/VLM enrichment, upload handlers, and full reparse lifecycle remain pending. Test names were inspected, not executed. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a258`: `docreader/main.py::DocReaderServicer.Read`, `ReadStream`, `_parse_request`, `_iter_image_refs`; `docreader/parser/parser.py::Parser`, `detect_effective_file_type`, `parse_file_stream`; `docreader/parser/registry.py::ParserEngineRegistry.get_parser_class`, `_DEFAULT_ENGINE_BY_TYPE`, `_build_default_registry`; `docreader/config.py::load_config`; `docreader/utils/request_memory.py::RequestThreadPoolExecutor`; `internal/infrastructure/chunker/splitter.go` defaults, protected patterns and `Chunk.EmbeddingContent`; `chunker/strategy.go::resolveChainWithProfile`, `SplitWithDiagnostics`, `DeriveParentChildConfigs`; `chunker/profiler.go::SelectStrategy`; `chunker/validator.go::ValidateChunks`; `chunker/tokens.go::CharsForTokenLimit`; `internal/application/service/knowledge_process.go::processChunks`. Package entry: [README](../raw/WeKnora/README.md), “Data sources and formats.”
