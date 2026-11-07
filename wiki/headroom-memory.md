---
type: Concept
title: Headroom memory architecture and retrieval
description: Hierarchical memory, persistence, project partitioning, retrieval, and injection in Headroom.
tags: [agent-memory, memory-retrieval]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:19:57Z }
stale_after: 2027-05-06
sources:
  - id: headroom
    resource: ../raw/headroom/README.md
    scope: ../raw/headroom/
    kind: code
    revision: 2b0315b
    title: Headroom repository
---

**Observed:** `HierarchicalMemory` coordinates a memory store, vector and text indexes, an embedder and a cache. Memories carry user, session, agent and turn identifiers, temporal validity and lineage. Writes update components sequentially, so a failure between updates can leave indexes out of sync.[^headroom]

- Important lower-scope memories may bubble into a new user-scope copy; supersession preserves history but removes the old item from search indexes.[^headroom]
- Vector search and FTS5 text search are separate paths. The proxy has an injection budget and can instead disable automatic injection in favor of tool use. An adjacent hybrid scorer exists, but its connection to this memory path was not established.[^headroom]
- Project storage routing resolves a project from request signals; the default unresolved-project fallback is empty rather than a shared global database. Explicit global fallback trades isolation for legacy behavior.[^headroom]
- The MCP memory server exposes search and save; its save description says similar saves do not replace an existing memory, so corrections require an explicit update path.[^headroom]

## Relationships

- Complements [failure learning](headroom-learning.md); project storage and injection have [privacy implications](headroom-privacy-and-security.md).

[^headroom]: `headroom/memory/core.py::HierarchicalMemory.add`, `search`, `text_search`, `supersede`, `_maybe_bubble`; `headroom/memory/models.py::Memory`; `headroom/memory/adapters/fts5.py::FTS5TextIndex`; `headroom/memory/storage_router.py::BackendRouterConfig`, `ProjectResolver.resolve`; `headroom/proxy/memory_handler.py::MemoryHandler.search_and_format_context`; `headroom/proxy/memory_injection.py::MemoryInjectionBudget`; `headroom/memory/mcp_server.py::_TOOLS`; `headroom/relevance/hybrid.py::HybridScorer`; revision `2b0315b`.
