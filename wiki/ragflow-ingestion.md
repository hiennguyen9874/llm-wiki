---
type: Concept
title: "RAGFlow document ingestion"
description: "Canvas-driven file parsing, format-aware chunking, extraction, embeddings, parent chunks, and index-write behavior."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54
    title: RAGFlow repository snapshot
---

# RAGFlow document ingestion

**Observed:** the ingestor consumes tasks, loads a canvas DSL, executes a registered component graph, normalizes terminal output, and persists chunks. In the general template the path is File → Parser → GeneralChunker → Extractor → Tokenizer. The graph permits task-specific component factories; validation enforces at most one Extractor.[^ragflow]

## Orchestration and replay boundary

`NewPipelineFromDSL` unwraps the template envelope and decodes a canvas. `Pipeline.Run` starts at the graph entry; replay decisions belong to components, not a pipeline-level partial-resume API. `PipelineExecutor.Execute` loads the DSL, invokes the pipeline, and processes outputs. Debug collection bypasses normal persistence side effects. The worker records terminal results and stages document-completion events for dataset compilation.[^ragflow]

## Parsing and document understanding

- File resolves metadata; Parser owns binary fetch and dispatch.
- `GetParser` covers PDF, Office/presentations/spreadsheets, CSV, HTML, Markdown, text, EPUB, JSON, email, visual, and aural families. Registry availability does not prove each path is fully enabled in every ingestor configuration.
- The PDF path has page workers, layout construction, OCR/table handling, and document assembly with native DeepDoc sessions. Additional PDF analyzer adapters exist; external models/services were not validated.
- Known-family errors propagate; unknown-family input can fall back to raw text. This is not universal graceful fallback for parse failures.[^ragflow]

## Chunking and enrichment

GeneralChunker dispatches by PDF/DOCX/Markdown/spreadsheet/text shape. Its observed default is 512 tokens with newline delimiters; overlap, child delimiters and table/image context are configurable. Other chunker families include page, hierarchy, table, QA, manual and title, but their semantics were not exhaustively inspected. Extractor can add keywords, questions, summary and metadata; Tokenizer creates searchable token fields and embedding vectors.[^ragflow]

## Index-write contract

`NormalizeChunks` accepts typed and map-based payloads. `ProcessChunksForPipeline` stamps document identity, creation fields, content and positions, turning `text` into `content_with_weight`; the engine stamps `kb_id` at write time. `MaterializeParentChunks` creates hidden parent rows (`available_int=0`) so retrieval can promote matching children to larger context. Chunk writer retries up to three attempts with backoff. Elasticsearch insertion uses bulk batches, inspects per-item failures, and distinguishes no-refresh ingestion from API wait-for-refresh writes.[^ragflow]

## Relationships

- **Depends on:** [persistence and engines](ragflow-persistence.md).
- **Produces inputs for:** [retrieval](ragflow-retrieval.md) and [knowledge compilation](ragflow-knowledge-compilation.md).
- **Uses:** the canvas/component model described in [agent workflows](ragflow-agent-workflows.md), without making document ingestion an unrestricted agent loop.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54`; locators: `internal/ingestion/pipeline/template/ingestion_pipeline_general.json::dsl`; `internal/ingestion/pipeline/pipeline.go::NewPipelineFromDSL / ValidatePipeline / Run`; `internal/ingestion/task/pipeline_executor.go::Execute / collectDebugOutput / processOutput`; `internal/ingestion/service/ingestion_service.go::handleAndExecute / stagePendingCompileEvent / recordTerminalPipelineLog`; `internal/ingestion/component/file.go::FileComponent.Invoke`; `internal/ingestion/component/parser.go::ParserComponent.Invoke`; `internal/parser/parser/parser_type.go::GetParser`; `internal/deepdoc/parser/pdf/parser.go::runPageWorkers / buildLayout / assembleDocument`; `internal/ingestion/component/chunker/general.go::generalChunkerParam.Defaults / generalStrategyForFileType`; `internal/ingestion/component/extractor.go::ExtractorComponent.Invoke`; `internal/ingestion/component/tokenizer.go::TokenizerComponent.Invoke / embedChunks`; `internal/ingestion/task/indexdoc/normalize.go::NormalizeChunks`; `internal/ingestion/task/indexdoc/process.go::ProcessChunksForPipeline`; `internal/ingestion/task/indexdoc/parent_child.go::MaterializeParentChunks`; `internal/ingestion/task/chunk_index_writer.go::chunkIndexWriter.Write`; `internal/engine/elasticsearch/chunk.go::InsertChunks / InsertChunksNoRefresh / insertChunks`.
