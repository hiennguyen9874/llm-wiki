---
type: Concept
title: RAG-Anything document ingestion
description: Single-document ingestion, parse identity, text completion, page provenance, and best-effort multimodal status semantics.
tags: [ml, rag, ingestion, provenance]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:43:55Z }
stale_after: 2027-01-24
sources:
  - id: rag-anything-3a14ecb
    resource: ../raw/RAG-Anything/README.md
    scope: ../raw/RAG-Anything/
    kind: code
    revision: 3a14ecb66fb3
    title: RAG-Anything repository
---

**Observed:** the ordinary ingestion entry points wait for LightRAG's text indexing before adding multimodal chunks, but multimodal processing is best-effort and can mark a document complete after item failures. **Synthesis:** document status is an orchestration marker, not proof that every visual or media element was indexed. Parse-cache reuse, content-derived document identity, and multimodal completion are separate mechanisms.[^rag-anything-3a14ecb]

## Entry points and ordering

| API | Observed contract |
| --- | --- |
| `process_document_complete` | Initialize → parse → separate text/modal items → insert/wait for text → annotate text pages → process modal items → completion callback; exceptions persist `FAILED` best-effort and re-raise |
| `insert_content_list` | Same core sequence without parsing; rejects an empty list; accepts caller `doc_id` and citation `file_path` |
| `process_document_complete_lightrag_api` | Server-oriented path with separate `doc-pre-<file>` status, temporary `scan_disabled` flag restored in `finally`, and insertion delegated to LightRAG with `multimodal_content` if its signature supports it; most failures return `False` |

**Observed:** for text-bearing documents the ordinary path deliberately avoids pre-registering a duplicate document status before LightRAG insertion. For modal-only documents it creates `HANDLING` status. `_drop_placeholder_doc_status` removes stale placeholder status only when no stored full-document text exists. The server variant does not offer the ordinary path's same text-wait guarantee.[^rag-anything-3a14ecb]

`_wait_for_text_processing` polls document and shared pipeline status, backs off from 0.2 to 2 seconds while busy, can restart processing when queued work is idle, and raises on terminal failure or a pipeline-cancelled marker. This is why returning from the ordinary API means more than merely enqueuing text.[^rag-anything-3a14ecb]

## Parse cache versus document identity

- **Observed:** `_generate_cache_key` hashes absolute path, mtime, SHA-256 of input bytes, parser, parse method, and recognized parser options. Stored `parse_config` and mtime must also match for a hit. `_store_cached_result` records content, `doc_id`, version/config/time metadata and flushes the KV cache.
- **Observed:** shared `parse_options.py::PARSER_CACHE_KWARGS` includes language/device/page range/formula/table/backend/source, `include_layout_blocks`, and Docling options `table_mode`, `tables`, `allow_ocr`, `artifacts_path`. Explicit `include_layout_blocks=False` and path-like artifacts are normalized.
- **Observed:** `_generate_content_based_doc_id` hashes a content signature: text, image path, table body, equation `text`, or stringified other items. **Synthesis:** this is not a universal digest of every semantic field or attachment byte. In particular image identity is path-based in this function, and equation identity does not explicitly hash `latex`.
- **Observed:** direct audio/video routing adds `media_sha256` to the content item, so replacing media bytes changes its content identity.
- **Observed:** `force_multimodal_reprocess=True` bypasses the modal-completion short circuit for storage migrations or deliberate rebuilding; it does not independently force reindexing all text.[^rag-anything-3a14ecb]

## Text and page provenance

**Observed:** `utils.py::separate_content_with_page_map` joins text with blank lines and records character intervals with zero-based page indexes. `_annotate_text_chunk_pages` only annotates the current successful insertion (`track_id` matches, status `PROCESSED`), with the default LightRAG chunker and matching sanitized stored text/chunk IDs. It replays chunk spans instead of searching for repeated strings.[^rag-anything-3a14ecb]

**Observed:** token-window replay requires positionally lossless tokenizer decoding; character splitting can be mapped separately. Ambiguous repeated chunks, custom chunkers, duplicate inserts, incompatible queued split settings, or mismatched chunk IDs leave pages unset rather than guessed. Spanning chunks may receive `page_idx_end`. Annotation failures warn without breaking ingestion. Fixed-schema storage may discard these extra fields; that backend behavior was not executed here.[^rag-anything-3a14ecb]

## Completion and partial failure

- **Observed:** `_process_multimodal_content_batch_type_aware` catches item-generation failures and skips those items. A batch-level error invokes an individual fallback, which also catches item errors; completion marking still occurs.
- **Observed:** `_mark_multimodal_processing_complete` sets `multimodal_processed=True` and normally `PROCESSED`, preserving existing `FAILED`. If the backend rejects the custom flag it uses a compatibility `multimodal_status` namespace.
- **Observed:** failure to initialize inside `_process_multimodal_content` logs and returns instead of raising. **Synthesis:** if this occurs after text indexing, the outer function can finish without a complete modal stage and leave `HANDLING` state.
- **Observed:** missing document status during modal chunk-list update logs and returns, potentially leaving stored chunks unlisted in document status.
- **Synthesis:** verify expected item/chunk counts and logs when completeness matters; do not use `PROCESSED` alone as an all-modalities success assertion.[^rag-anything-3a14ecb]

## Relationships

- **Uses:** [Parsing](rag-anything-parsing.md) for file normalization.
- **Uses:** [Multimodal grounding](rag-anything-multimodal-grounding.md) for chunk/entity construction.
- **Used by:** [Batch processing](rag-anything-batch-processing.md), which must distinguish parsed from indexed state.
- **Depends on:** [Architecture](rag-anything-architecture.md) for shared storage and context isolation.

## Evidence limits

Static inspection plus selected test assertions, not executed ingestion. External LightRAG queue/storage semantics and real-provider error behavior remain unverified; [source map](rag-anything-source-map.md) records coverage.

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb3`: `raganything/processor.py::_generate_cache_key` (94), `_drop_placeholder_doc_status` (168), `_wait_for_text_processing` (193), `_annotate_text_chunk_pages` (258), `_text_chunk_page_labels` (329), `_generate_content_based_doc_id` (458), `_get_cached_result` (497), `_store_cached_result` (561), `parse_document` (614; media branch 709–731), `_process_multimodal_content` (867–998), `_process_multimodal_content_individual` (999–1130), `_process_multimodal_content_batch_type_aware` (1132), `_update_doc_status_with_chunks_type_aware` (1795), `_mark_multimodal_processing_complete` (1857), `process_document_complete` (1979), `process_document_complete_lightrag_api` (2174), `insert_content_list` (2483); `parse_options.py::PARSER_CACHE_KWARGS`; `utils.py::separate_content_with_page_map`, `build_sanitized_page_map`, `replay_chunk_spans`, `annotate_chunks_with_page_idx`; README “Content List Format” and “Re-processing Multimodal Content After a Storage Backend Change”; tests `testparse_cache_key.py`, `test_processor_lightrag_api.py`, and sampled `test_text_chunk_page_idx_pipeline.py` (assertions inspected, not run).
