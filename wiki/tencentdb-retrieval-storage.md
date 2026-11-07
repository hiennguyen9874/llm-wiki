---
type: Concept
title: TencentDB memory retrieval and storage
description: MemoryCore search strategies, storage abstractions, backend differences, and isolation caveats.
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

**Observed:** MemoryCore separates database-backed L0/L1 records from file-like storage for conversation files, scenes, personas and checkpoints. Its recall path supports keyword, embedding and hybrid search; hybrid combines results using reciprocal rank fusion unless a backend supplies native hybrid search.[^tencentdb]

SQLite uses FTS5 and vector-related tables where available; Tencent Cloud VectorDB supports native hybrid capabilities; the MongoDB implementation differs, including a no-op dense-vector search in this snapshot. Missing embedding availability can cause a keyword fallback, while unavailable SQLite FTS affects keyword search. These are static implementation observations, not tested guarantees.[^tencentdb]

## Isolation discrepancy

**Observed:** `assertIsolation` documents throwing for missing required fields with enforcement enabled, but its body substitutes the default bucket instead. The v3 router separately checks required identity fields; do not infer equivalent enforcement on every route from that check alone. SQLite search implementations post-filter over-retrieved candidates, unlike MongoDB search filters. Audit access boundaries before deployment.[^tencentdb]

See [memory pipeline](tencentdb-memory-pipeline.md), [security](tencentdb-security-deployment.md) and [source map](tencentdb-source-map.md).

[^tencentdb]: Revision `2002196`: `MemoryCore/src/core/hooks/auto-recall.ts::searchMemories`, `::searchHybrid`; `MemoryCore/src/core/store/factory.ts::createStoreBundle`; `MemoryCore/src/core/store/sqlite/memory-store.ts::VectorStore.searchL1Fts`; `MemoryCore/src/core/store/mongodb/memory-store.ts::MongoMemoryStore.searchL1Vector`; `MemoryCore/src/core/storage/types.ts::StoragePaths`; `MemoryCore/src/core/store/isolation.ts::assertIsolation`; `MemoryCore/src/gateway/v2-router.ts::collectV3Missing`.
