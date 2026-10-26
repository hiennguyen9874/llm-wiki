---
type: Concept
title: LightRAG document ingestion and commit lifecycle
description: SDK versus server enqueue paths, document identity and deduplication, persisted processing options, and flush-before-status completion.
tags: [rag, ingestion, lifecycle]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:55:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a
    title: LightRAG repository
---

**Observed:** the server uses enqueue plus pipeline processing, not simply the embedded `ainsert` convenience method. Enqueued documents persist parse/chunk choices and move through distinct parse, analyze and process queues; successful completion is recorded only after index flushing. **Synthesis:** accepted upload, parsed artifact, and durable processed status are separate events.[^lightrag-aaebfe1]

## Entry points and identity

- **Observed:** `ainsert` is documented in-source as the fixed/legacy chunking convenience path; the server uses `apipeline_enqueue_documents` and `apipeline_process_enqueue_documents` with per-document directives.
- Enqueue deduplicates canonical hint-stripped filenames and normalized-text content hashes before graph/model writes where content is available. Pending-parse files cannot obtain their final text hash until after parsing, so duplicate handling also exists post-parse.
- Caller IDs take precedence; otherwise path, content, or a path/track/index fallback supplies deterministic MD5-based document IDs. Explicit IDs force the raw-content path instead of arbitrary pending-parse interpretation.
- Chunk options are frozen into the document's `full_docs` record at enqueue. Later global/addon changes affect future enqueues, not automatically all stored documents.[^lightrag-aaebfe1]

## Processing and commit order

**Observed:** the status ladder is pending → parsing → analyzing → processing → processed, with failed terminal/error paths. Parse results feed multimodal analysis and then the chunk/extract/merge stage. Source artifacts, sidecars, and source conflicts have their own management paths; parse success alone is not full indexing completion.[^lightrag-aaebfe1]

During document processing, the implementation builds the chunk dictionary, writes processing status and chunk-vector/text data, extracts entities, merges graph contributions, then calls `_insert_done` to flush stores before writing processed status. A flush failure raises `IndexFlushError` and aborts the batch rather than reporting one successful document against uncommitted indexes. The `!` processing option skips KG work but still indexes chunks for naive/mix retrieval.[^lightrag-aaebfe1]

**Synthesis:** document status acts as a completion record over multiple stores, not a demonstrated distributed ACID transaction. Recovery anchors and strict-read/retry logic are needed because intermediate writes and failures can occur across storage boundaries.[^lightrag-aaebfe1]

## Defaults and concurrency

**Observed:** base LLM concurrency defaults to four and parallel insertion to three; embedding concurrency defaults to eight with batches of ten. Per-document extraction/merge fan-out, role request limits, parser queue limits, and document parallelism are different layers. Admission's maximum-pending-documents default is zero, disabling that capacity gate; request body/upload ceilings remain separate.[^lightrag-aaebfe1]

## Documentation reconciliation

**Reported:** the file-pipeline guide describes the LightRAG content hash in terms of the blocks artifact. **Observed:** `_persist_parsed_full_docs` uses sanitized, marker-stripped merged text hashing; an unused file-content helper is not evidence that file bytes define live deduplication. **Synthesis:** file-container changes and normalized-text changes need not have the same deduplication effect.[^lightrag-aaebfe1]

## Relationships

- **Uses:** [Parsing and multimodal analysis](lightrag-parsing-multimodal.md), [chunking](lightrag-chunking.md), and [KG extraction/merge](lightrag-extraction.md).
- **Depends on:** [Concurrency/durability](lightrag-concurrency.md) and [storage](lightrag-storage.md).
- **Repaired by:** [Deletion/recovery](lightrag-deletion.md) when contribution writes must be reversed or rebuilt.
- **Exposed by:** [API/UI](lightrag-api-ui.md) upload, scan, status and retry routes.

## Evidence limits

Targeted static reading only. Upload/queue execution, source-conflict CAS, admission interleavings, all custom-chunk journaling, parser formats and real backend flush failures were not reproduced. See [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/lightrag.py::LightRAG.ainsert, _insert_done, _flush_storages`; `pipeline.py::_PipelineMixin.apipeline_enqueue_documents, apipeline_process_enqueue_documents, _add_content, _run_pipeline_batch, _persist_parsed_full_docs, _mark_duplicate_after_parse` and process-stage writes (5713–5925); `utils_pipeline.py::compute_text_content_hash`; `parser/routing.py::default_chunker_config, resolve_chunk_options`; `base.py::DocStatus`; `constants.py` insert/embedding/admission defaults; `api/routers/document_routes.py::pipeline_enqueue_file, pipeline_index_file`; `docs/FileProcessingPipeline.md` §7.1.
