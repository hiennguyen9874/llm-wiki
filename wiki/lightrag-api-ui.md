---
type: Concept
title: LightRAG API server and WebUI
description: FastAPI route families, upload and request limits, dual React entries, browser state, and NDJSON client behavior.
tags: [rag, api, frontend]
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

**Observed:** FastAPI exposes document management, queries, graph administration, session/auth, health and a limited Ollama-compatible surface. Two React entry points share one build: `/webui` is the admin console and `/workspace` is query-focused. **Synthesis:** the UI split is an experience distinction, not an authorization boundary or separate knowledge-base tenancy.[^lightrag-aaebfe1]

## Service and request pipeline

**Observed:** `create_app` registers routers, error handlers, request limiting/admission middleware, CORS and static mounts. Root-path normalization precedes route-sensitive limits; CORS wraps refusals. Ordinary request-body default is 1 MiB, text ingestion 50 MiB, upload maximum 100 MB, and pending-document admission is off by default (`0`). These controls protect different boundaries, not one interchangeable upload-size knob.[^lightrag-aaebfe1]

| Family | Inspected surfaces |
| --- | --- |
| Documents | Upload, text/texts, scan/status, track/pipeline status, pagination/counts, source-conflict repair, delete/clear, reprocess, cancel, force-reset |
| Query | JSON answer, NDJSON stream, structured retrieval data |
| Graph | Read, edit, create, delete and merge |
| Session/health | Auth status, login, credential verification, health |
| UI customization | Public customization manifest/assets |
| Ollama | version, tags, ps, generate, chat—not full model management or embeddings emulation |

**Observed:** `/api/generate` bypasses RAG; `/api/chat` normally invokes RAG with supported mode/context prefixes, except bypass and selected title-generation handling. Version/model metadata are compatibility shims, not live Ollama model inventory. Unexpected server errors are sanitized; failures after stream headers use in-band NDJSON errors.[^lightrag-aaebfe1]

## Upload boundary

**Observed:** uploads reject unsafe filenames, resolve parser rules/hints, validate engine/suffix compatibility, bound streamed writes, and open files with exclusive/no-follow semantics. Duplicate canonical basenames in document status or input files produce conflicts. A background task subsequently enqueues/processes the file, so HTTP upload completion is not indexing completion. Registry-derived type capabilities feed UI prevalidation. **Observed mismatch:** the UI's 200 MB cap exceeds the server's 100 MB default.[^lightrag-aaebfe1]

## Browser architecture and state

**Observed:** React/Vite uses HashRouter, Zustand, axios, Tailwind, i18next and graph visualization dependencies. Admin and workspace HTML entry points receive request-time `window.__LIGHTRAG_CONFIG__`; relative assets support reverse-proxy prefixes. Built UI files are absent from the tracked source snapshot; the service can degrade to API-only until a build supplies them.[^lightrag-aaebfe1]

JWT and API-key state persist in browser localStorage; local token checks decode payload/expiry, while server validation remains authoritative. Axios sends bearer and API-key headers when both exist, adopts renewed tokens, retries guest renewal once, and handles non-guest auth failure. An invalid bearer can win over a valid API key because server credential resolution checks bearer first.[^lightrag-aaebfe1]

**Observed:** workspace queries inherit same-browser admin query settings read-only, with its own history key and context/prompt-only debug flags clamped. They are not server-wide enforced policy. The session hook manages optimistic messages, progress, time-to-first-token, reasoning/LaTeX rendering state, aborts, persistence and auth-failure rollback. Fetch-based NDJSON parsing handles partial lines, in-band errors and user cancellation; reconnect semantics were not runtime-tested.[^lightrag-aaebfe1]

## Rendering and entry limits

**Observed:** chat Markdown allows raw HTML through a sanitizer with an allowlist; customization Markdown drops raw HTML and hardens external-link attributes. The login agreement checkbox is a UI gate, not server enforcement. The default root UI setting changes a redirect only; both UI URLs remain mounted.[^lightrag-aaebfe1]

## Relationships

- **Depends on:** [Authentication/security](lightrag-security.md).
- **Uses:** [Query/stream/cache contracts](lightrag-query-contracts.md) and [ingestion](lightrag-ingestion.md).
- **Depends on:** [Deployment/build](lightrag-deployment.md) for packaged frontend assets and proxy configuration.

## Evidence limits

Static selected routes, frontend modules and test assertions only. No browser, frontend build, HTTP server, multipart attack, disconnect timing or XSS exploit test ran. Graph-view internals and other admin pages remain pending in the [source map](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: `lightrag/api/lightrag_server.py::create_app, SmartStaticFiles, check_frontend_build, check_workspace_frontend_build`; `api/{admission_middleware,body_limit_middleware,input_limits,utils_api}.py`; `api/routers/document_routes.py::create_document_routes, DocumentManager, upload_file_opener, pipeline_enqueue_file`; `query_routes.py::create_query_routes`; `graph_routes.py::create_graph_routes`; `ollama_api.py::OllamaAPI.setup_routes, parse_query_mode`; `lightrag_webui/package.json`; `src/api/lightrag.ts::queryTextStream, _readNdjsonStream` and interceptors; `src/features/retrieval/useQuerySession.ts`; `src/features/workspace/WorkspaceQueryView.tsx`; `src/features/workspace/querySettingsSnapshot.ts`; `src/stores/{state,settings,querySettings}.ts`; `src/utils/markdownSanitizeSchema.ts`; `src/components/customization/CustomizedMarkdown.tsx`; `src/components/documents/UploadDocumentsDialog.tsx`; `src/features/LoginPage.tsx`; `vite.config.ts`; `docs/{MultiSiteDeployment,UserDefinedUI,FrontendBuildGuide}.md`; selected assertions in `tests/api/routes/test_query_stream_routes.py`, `test_document_routes_docx_archive.py`, `test_supported_file_types_endpoint.py`.
