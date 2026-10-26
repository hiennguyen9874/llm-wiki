---
type: Concept
title: UltraRAG UI architecture and persistence
description: React builder and chat UI over Flask APIs, shared pipeline execution, filesystem artifacts, and SQLite state.
tags: [ml, ultrarag, ui, persistence]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e203
    title: UltraRAG repository
---

**Observed:** UltraRAG UI is a React/TypeScript SPA served by Flask, with a visual builder and chat/knowledge-base workspace. Its backend imports the existing pipeline engine rather than implementing a second RAG executor. **Reported:** the README describes a RAG IDE with bidirectional canvas/code editing and an AI assistant; corresponding source surfaces exist, but their end-to-end behavior was not exercised.[^ultrarag]

## Frontend and backend responsibilities

- `/chat` renders chat, knowledge-base, Explore, and Memory views. `/settings` renders the builder; `/` redirects to chat and legacy `/config` redirects to settings.
- `BuilderPage` contains canvas/code editing, parameter and prompt management, and the AI helper; `PipelineCanvas` uses React Flow (`@xyflow/react`). The helper calls separate `/api/ai/*` endpoints, not the MCP pipeline engine.
- TanStack Query manages API data, Zustand stores UI preferences, React Router handles navigation, and Radix supplies UI primitives. English/Chinese dictionaries coexist with fallback strings; some text remains hardcoded.
- Chat streaming uses `fetch` and `ReadableStream` with an SSE-style `data:` parser. The markdown path uses `marked`, citation markup, DOMPurify, KaTeX, and highlighting. This is static evidence of a sanitization path, not a completed XSS audit.
- Flask exposes pipeline editing/build/run, chats, prompts, knowledge-base tasks, memory, AI-helper, and system endpoints. Authorization differs by route; see [access control](ultrarag-auth.md).[^ultrarag]

## Storage model

`ULTRARAG_UI_STORAGE_ROOT` overrides the default `<repo>/ui/storage`; relative overrides resolve against the project root. Storage is local rather than a managed cloud database:[^ultrarag]

| Artifact | Location or mechanism |
| --- | --- |
| Accounts and model settings | `db/users.sqlite3`, users table |
| Saved chat sessions/messages | Same SQLite file, separate tables with ownership checks |
| Knowledge-base visibility | Same SQLite file, collection visibility table |
| Knowledge-base files | `knowledge_base/{raw,corpus,chunks,index}` and `kb_config.json` |
| User memory | `memory/<user>/MEMORY.md` and dated project-memory files |
| Uploaded batches | Timestamp/UUID subdirectories under raw storage |
| Runtime sessions/task state | Process-local managers/dictionaries, not fully durable |

Tables are created and adjusted through ad-hoc SQLite initialization/column checks, not a separate migration framework. Saved chats and runtime demo sessions are distinct: saved-chat ownership checks do not imply ownership binding on process-local execution sessions.[^ultrarag]

## Operational constraints

**Observed:** chat preparation writes a temporary one-row dataset and rewrites shared pipeline parameter files, then restores them. **Synthesis:** concurrent chats using one pipeline can race on those files; no per-pipeline lock was identified in the inspected path. Runtime sessions are keyed by caller-supplied IDs, while task status lives in process-local state and can be lost on restart.[^ultrarag]

The largest page components (`ChatPage`, `BuilderPage`) and `pipeline_manager.py` were inspected by region. Committed `dist/` is generated output; its repository convention requires rebuilding it with frontend changes, but source/build equivalence was not verified here. No browser render, streaming session, storage migration, upload, or multi-user run was tested. These coverage limits make this concept **draft**.[^ultrarag]

## Relationships

- **Depends on:** [pipeline compilation and execution](ultrarag-pipelines.md).
- **Uses:** [corpus processing](ultrarag-corpus.md) and [retrieval](ultrarag-retrieval.md) for knowledge-base workflows.
- **Constrained by:** [authentication](ultrarag-auth.md) and [security boundaries](ultrarag-security.md).

[^ultrarag]: Revision `185e203`: `README.md` UltraRAG UI; `ui/frontend/package.json`; `ui/frontend/src/app/{App,router}.tsx`; `pages/{ChatPage,BuilderPage}.tsx` view/editor/chat regions; `features/pipeline/components/PipelineCanvas.tsx`; `shared/api/streaming.ts::streamPipelineChat`; `shared/lib/chatMarkdown.ts::renderChatMarkdown`; `shared/i18n/provider.tsx`; `ui/backend/app.py::create_app`, SPA/API routes, `KB_TASKS`; `ui/backend/storage_paths.py::_resolve_ui_storage_root`; `ui/backend/{auth,chat_store,kb_visibility_store}.py` table initialization/ownership helpers; `ui/backend/pipeline_manager.py::_ensure_client_funcs`, `SessionManager`, `_prepare_chat_context`, `save_parameters`, `upload_kb_files_batch`; `ui/frontend/README.md` Repository Convention. Large UI modules sampled, not exhaustively audited.
