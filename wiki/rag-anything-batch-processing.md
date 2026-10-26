---
type: Concept
title: RAG-Anything batch processing
description: Parse-only worker pools, incremental manifests, RAG-state-aware retries, and multiplicative concurrency limits.
tags: [ml, rag, batch, concurrency]
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

**Observed:** RAG-Anything separates parse-only batches from batches that also index into LightRAG. An incremental parse manifest proves only that a parser previously succeeded, not that the current workspace has indexed text and multimodal data. **Synthesis:** reliable restarts require checking both parse state and destination RAG state.[^rag-anything-3a14ecb]

## APIs and results

| Layer/API | Observed behavior |
| --- | --- |
| `batch_parser.py::BatchParser` | Thread-pool parsing, progress, per-file output directories, timeout reporting, optional incremental manifest; returns `BatchProcessingResult` |
| `process_documents_batch` / `_async` | Synchronous/asynchronous wrappers around parse-only batches |
| `process_documents_with_rag_batch` | Parse phase followed by per-file RAG ingestion, with successful/failed/skipped RAG counters and batch callbacks |
| `process_folder_complete` | Legacy concurrent ingestion interface; logs results but returns `None`, unlike the structured batch-result API |

**Observed:** direct `BatchParser` defaults are four workers and 300 seconds per file; non-positive workers are rejected. `RAGAnythingConfig.max_concurrent_files` defaults to one, not the four shown in some documentation examples. `dry_run` returns before LightRAG initialization and manifest writes in the combined batch flow.[^rag-anything-3a14ecb]

## Incremental manifest

**Observed:** `<output_dir>/.raganything_batch_manifest.json` is keyed by resolved input path. Signatures include path, size, nanosecond mtime, MD5, and a SHA-256 digest of parser/method/options. Raw option values are not stored in the manifest. Writes use a temporary file and atomic replacement; corrupt/missing manifests warn and behave as an empty manifest.[^rag-anything-3a14ecb]

- Matching configuration, size, and mtime with an existing MD5 take a fast reuse path without rehashing bytes. **Synthesis:** unlike the per-document parse cache, this fast path cannot detect a same-size change with preserved mtime.
- If metadata changed, the implementation hashes and compares the full signature.
- Missing output directories invalidate manifest entries. Non-incremental runs invalidate their inputs before parsing, even if the ensuing parse fails; failed reparses are not retained as successes.
- Non-serializable option objects disable incremental reuse for that run.
- Output directories are `<stem>_<md5(resolved_path)[:8]>`, avoiding ordinary same-stem collisions across directories.[^rag-anything-3a14ecb]

## Parse reuse is not RAG reuse

**Observed:** `process_documents_with_rag_batch` considers both parse-successful and parse-skipped inputs. For parse-skipped files it resolves document identity and checks current LightRAG status: only text `PROCESSED` plus modal completion, with no forced reprocess, counts as RAG-skipped. Parse-only history, another workspace, and earlier initialization/indexing failures do not justify skipping ingestion. Ingestion-only arguments are filtered before parser/manifest configuration is computed.[^rag-anything-3a14ecb]

## Concurrency and timeout semantics

- **Observed:** each modal batch creates its own semaphore using `lightrag.max_parallel_insert`, falling back to 2 only when the attribute is absent. There is no single global caption semaphore across files.
- **Synthesis from implementation and documentation:** concurrent files multiply caption concurrency: approximately files × per-document modal limit. Video adds a per-video frame-call semaphore using the same limit, so nested video processing can multiply it again. This is an upper-bound planning model, not a throughput measurement.
- **Observed:** a file timeout is measured from worker start rather than from submission. Reporting a timeout does **not** forcibly stop the worker; thread-pool shutdown can still wait for it, and it may continue writing outputs.
- **Observed:** the mixin does not expose every direct `BatchParser` constructor setting; its construction uses the default timeout. The combined batch start callback counts supplied path arguments, which need not equal expanded input files.[^rag-anything-3a14ecb]

## Documentation reconciliation

**Observed:** the shared option whitelist has 13 entries, including Docling's `table_mode`, `tables`, `allow_ocr`, and `artifacts_path`; the incremental section of `docs/batch_processing.md` enumerates only nine. Use `parse_options.py::PARSER_CACHE_KWARGS` for the actual implementation contract. The docs correctly distinguish parser manifests from RAG indexing and warn that timeout does not kill a thread.[^rag-anything-3a14ecb]

## Relationships

- **Uses:** [Document ingestion](rag-anything-ingestion.md) for each RAG-stage document.
- **Depends on:** [Runtime operations](rag-anything-stack-operations.md) for concurrency and parser configuration.
- **Uses:** [Audio/video processing](rag-anything-audio-video.md), which introduces nested frame-call concurrency.

## Evidence limits

Static implementation and selected regression-test inspection only. No batch, timeout, cancellation, manifest recovery, or load test was executed; see [source map](rag-anything-source-map.md).

[^rag-anything-3a14ecb]: Revision `3a14ecb66fb3`: `raganything/batch_parser.py::BatchProcessingResult` (29), `BatchParser.__init__` (70–107), `_file_output_dir` (231), `_manifest_path` (244), manifest load/write (247–302), `_file_metadata`/`_file_signature`/`_filter_incremental_files` (305–398), `_parse_config_signature` (399–422), `process_batch` (including dry-run/invalidation 479–520, worker clock 538–601, success recording 622–633); `batch.py::process_folder_complete` (35), `process_documents_batch` (186), `process_documents_batch_async` (241), `process_documents_with_rag_batch` (324–528); `processor.py::_process_multimodal_content_batch_type_aware` (1158); `modalprocessors_video.py` frame semaphore (345–347); `config.py::RAGAnythingConfig`; `parse_options.py::PARSER_CACHE_KWARGS`; `docs/batch_processing.md`, incremental processing and multimodal ingestion concurrency sections; tests `test_batch_parser_workers.py`, `test_multimodal_concurrency.py`, and sampled `test_batch_rag_incremental.py` (not executed).
