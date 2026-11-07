---
type: Concept
title: Mem0 OSS retrieval and ranking
description: Semantic candidate generation, optional BM25 and entity boosts, threshold behavior, expiration, and graph boundaries in Mem0 OSS.
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

**Observed:** OSS search first obtains semantic candidates, then adds available normalized BM25 and entity signals. These boosts rank semantic hits rather than introducing independent keyword-only or entity-only candidates. The threshold applies to the semantic score before combining; the returned combined score can consequently fall below that threshold.[^mem0]

The combined score is `(semantic + BM25 + entity boost) / max_possible`, clamped to one, with a query-level divisor that depends on active signals. **Synthesis:** scores are not necessarily comparable across queries with different active signals. `explain=True` exposes components. Stores without a keyword implementation degrade gracefully; NLP-dependent extraction also depends on available model support.[^mem0]

**Observed:** `search` and `get_all` take entity scoping inside `filters`. Expired results are filtered after retrieval unless requested; direct `get` has different expiry behavior. External graph-store integration is absent from the current OSS configuration; the entity collection is a retrieval index, not a typed relationship graph.[^mem0]

See [write and storage](mem0-write-and-storage.md), [provider architecture](mem0-providers.md), and [documentation discrepancies](mem0-source-map.md). No retrieval experiments were run.

[^mem0]: Revision `d16b8df6`; `mem0/memory/main.py::Memory.search`, `Memory._search_vector_store`, `Memory._compute_entity_boosts`, `Memory.get`, `_payload_is_expired`; `mem0/utils/scoring.py::score_and_rank`; `mem0/vector_stores/base.py::VectorStoreBase.keyword_search`; `docs/migration/oss-v2-to-v3.mdx::Breaking Changes`.
