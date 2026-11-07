---
type: Concept
title: Mem0 overview
description: Mem0's open-source memory SDK, self-hosted server, managed platform, and the boundaries between their capabilities.
tags: [agent-memory, mem0]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:08:00Z }
stale_after: 2027-02-06
sources:
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
---

Mem0 is an agent-memory project offering Python and TypeScript libraries, a self-hosted server and a managed platform. The README's platform benchmarks and temporal features must not be assumed to describe the OSS implementation. **Reported:** the managed stack includes proprietary optimizations not available in the OSS SDK.[^mem0]

**Observed:** OSS extraction is additive and search uses semantic candidates with optional keyword and entity boosts; external graph-store integration was removed in this snapshot. The server is a separate authenticated API and dashboard, not the hosted platform.[^mem0]

## Relationships

- Uses [Mem0 OSS write and storage](mem0-write-and-storage.md) and [Mem0 retrieval](mem0-retrieval.md) for local memory operations.
- See [Mem0 server and security](mem0-server-and-security.md), [clients and integrations](mem0-clients-and-integrations.md), and [benchmarks](mem0-benchmarks.md).
- Compared in [Agent memory landscape survey](agent-memory-landscape-survey.md) (cross-system synthesis).
- [Source map and discrepancies](mem0-source-map.md) records coverage and unresolved documentation drift.

[^mem0]: Revision `d16b8df6`; `README.md::Introduction`, `README.md::New Memory Algorithm (April 2026)`, `mem0/memory/main.py::Memory._add_to_vector_store`, `docs/migration/oss-v2-to-v3.mdx::Overview`, `server/main.py::app`.
