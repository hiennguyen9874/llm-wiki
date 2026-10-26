---
type: Concept
title: "OpenRAG document ingestion"
description: "Docling parsing, chunking, delegated chunk callbacks, indexed metadata, and ingestion limits and discrepancies."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:03:52Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

**Observed:** the standard file-ingestion path runs Docling Serve parsing and Markdown export in Langflow, splits text, generates embeddings, and can post chunks back to a token-protected backend writer. Backend configuration supplies runtime tweaks, ownership/ACL metadata, and service URLs; raw flow-template values alone are not the complete effective configuration.[^openrag-repo]

## Pipeline and defaults

`DoclingRemote → ExportDoclingDocument → metadata operations → SplitText → OpenSearch component`, with an embedding component feeding the vector-store input. The inspected flow has eight nodes. Defaults include chunk size **1000 characters**, overlap **200**, table structure on, OCR off, and picture descriptions off. Settings validation requires `chunk_overlap < chunk_size`.[^openrag-repo]

The backend chooses `ocrmac` on Darwin and `easyocr` elsewhere and maps OCR language codes to the engine; the committed JSON's `ocrmac` value is not a portable effective default. `ExportDoclingDocument` probes for `traverse_pictures` compatibility: older Docling APIs can omit OCR text nested under picture items. The component accepts 30 extensions; accepted extension is not evidence of tested conversion quality.[^openrag-repo]

`DISABLE_INGEST_WITH_LANGFLOW=true` selects the documented direct processor alternative. Its processor bodies are not fully covered by this ingest, so equivalent behavior across both paths is **Unverified**.[^openrag-repo]

## Write boundary and chunk schema

The callback handler `/internal/ingest/chunks` validates a per-run token and rejects run mismatch before invoking `DocumentIndexWriter`. Chunk `_id`s combine ownership scope with document/batch identity; `ingest_run_id` is stored as a field so a failed run can be deleted by term query. The run ID is not an ID-prefix namespace. The backend-routed path must not be confused with legacy/direct-write and IBM compatibility paths visible in the component/header code.[^openrag-repo]

Indexed fields include document/chunk identity, filename, MIME type, page, text, embedding model/dimensions/provider/space, file size, connector/source URL, owner identity, allowed users/groups/principals, parser/chunking settings, timestamps, and ingest-run identity. ACL metadata is part of indexed content, not merely UI state.[^openrag-repo]

## Failures, limits, and side effects

- Upload cap defaults to **100 MiB**; per-file ingestion timeout **3600 s**, Langflow timeout **2400 s**, callback-token TTL **3900 s**. Reverse-proxy limits can be lower.
- Docling distinguishes transient/network/5xx failures from payload-too-large (413). The component retries HTTP 500 up to five times; this is not a claim every ingestion action is safely replayable.
- Generic Langflow request retries exclude non-idempotent flow-run POSTs: replay can re-embed content or re-poll an already-deleted Docling task.
- Docling picture-description API configuration sends vendor credentials to Docling Serve. Treat it as trusted infrastructure, not an untrusted conversion utility.
- **Reported:** changing ingestion/embedding settings does not reprocess existing documents; reupload is required to regenerate embeddings. Chat-context uploads are documented as conversation-only, unlike permanent knowledge uploads.[^openrag-repo]

## Contradictions and numerical limits

- Docs describe ten tested file types; implementation accepts a wider set. These have different meanings, so do not promote all accepted extensions to tested support.
- Docs tie picture descriptions to OCR and a specific small local model; code supports independent VLM configuration and several provider paths.
- The ingestion-flow partial describes additional secret/data nodes and JWT defaults not matching the inspected eight-node template and current runtime callback design.
- **Reported benchmark:** docs give 1,083 files, 5,026,474,862 bytes, about 2,535 s, and claim 2.4 documents/s. **Synthesis:** 1,083 / 2,535 ≈ **0.427 documents/s**, while 2.34 s/document is the reciprocal. Logs show 1,082 processed files, 1,070 successes, 12 errors, and timestamps spanning about 39 minutes rather than the stated 42 minutes. No benchmark was reproduced; the inconsistent rate is not a usable performance guarantee.[^openrag-repo]

## Relationships

- Uses [Langflow workflows](openrag-langflow-workflows.md); supplies [hybrid retrieval](openrag-hybrid-retrieval.md).
- Receives source permissions from [connectors](openrag-connectors.md); depends on [security boundaries](openrag-auth-security.md).

## Coverage limits

Direct processor internals, cancellation/rollback under failure, Docling compatibility, actual OCR quality, and performance remain untested or partly pending. See [source map](openrag-source-map.md).

[^openrag-repo]: `6fc819d`: `flows/ingestion_flow.json::data.nodes/data.edges`; `custom_components/openrag/{docling_remote,export_docling_document}.py::{VALID_EXTENSIONS,MAX_500_RETRIES}` and export compatibility probe; `src/config/config_manager.py::KnowledgeConfig`; `src/api/settings/endpoints.py` chunk-overlap validation; `src/services/{langflow_file_service,docling_service,document_index_writer,langflow_ingest_token_service}.py::{run_ingestion_flow,get_docling_preset_configs,_build_chunk_document,_scoped_chunk_id,delete_ingest_run}`; `src/api/langflow_ingest.py::_authorized_chunk_id` and callback handler; `src/config/settings.py::{OPENRAG_MAX_UPLOAD_MB,INGESTION_TIMEOUT,LANGFLOW_TIMEOUT,LANGFLOW_REQUEST_RETRIES}`; `docs/docs/core-components/{ingestion,ingestion-configure}.mdx` §§ Supported file types, Ingestion performance expectations, Select a Docling implementation, Documents aren't reingested; `docs/docs/_partial-ingestion-flow.mdx`; `docs/docs/_partial-temp-knowledge.mdx`.
