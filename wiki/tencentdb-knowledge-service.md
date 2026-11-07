---
type: Concept
title: TencentDB knowledge service and wiki ingestion
description: Wiki and CodeGraph ingestion, indexing, incremental updates, and agent tool access in MemoryKnowledge.
tags: [agent-memory, tencentdb]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:17:35Z' }
stale_after: 2027-05-06
sources:
  - id: tencentdb
    resource: ../raw/TencentDB-Agent-Memory/README.md
    scope: ../raw/TencentDB-Agent-Memory/
    kind: code
    revision: 2002196
    title: TencentDB Agent Memory repository
---

**Observed:** MemoryKnowledge manages wiki and CodeGraph assets and exposes agent-facing discovery and invocation through `/v3/tools/list` and `/v3/tools/call`. Skills are a separate asset type in the wider system, not the wiki/CodeGraph engine itself.[^tencentdb]

## Wiki and code

The wiki pipeline hashes raw sources, extracts candidate pages using an LLM, merges pages serially and rebuilds its index. Changed or removed inputs are reconciled; byte-hash idempotency means a converter-only change does not itself change the source hash. Search uses FTS and can expand a page-link graph. Model-generated page paths are constrained to the wiki root, and manually written pages can be locked against later automated merge.[^tencentdb]

CodeGraph wraps a third-party codegraph package to index or sync repositories and exposes search, exploration, caller/callee and impact operations. Repository fetching and credential handling introduce separate trust boundaries; see [security](tencentdb-security-deployment.md). Implementation findings are **Observed**, not execution-verified.[^tencentdb]

## Documentation limit

The checked-in API documentation and OpenAPI do not fully enumerate the routes observed in code. Refer to the implementation for this revision and re-check later revisions; [coverage](tencentdb-source-map.md) remains partial.[^tencentdb]

[^tencentdb]: Revision `2002196`: `MemoryKnowledge/src/module.ts::createKnowledgeModule`; `MemoryKnowledge/src/engines/wiki/manager.ts::runIngestIncremental`, `::ftsSearch`; `MemoryKnowledge/src/engines/wiki/ingest-v2/index.ts::extractSource`, `::commitCandidates`; `MemoryKnowledge/src/engines/wiki/ingest-v2/safe-path.ts::isInsideRoot`; `MemoryKnowledge/src/store/wiki-service.ts::injectLockedTrue`; `MemoryKnowledge/src/engines/code/bridge.ts::indexProject`, `::executeTool`; `MemoryKnowledge/src/routes/tools.ts::createToolsRoutes`; `MemoryKnowledge/openapi.yaml`; `MemoryKnowledge/v3-api-memoryknowledge-doc.md` §2.
