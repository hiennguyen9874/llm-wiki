---
type: Concept
title: GBrain retrieval pipeline
description: Stage order, search modes, reranking, readiness and failure behavior of GBrain's hybrid search, plus what text reaches providers.
tags: [agent-memory, gbrain, retrieval, hybrid-search]
status: draft
created: 2026-11-06
stale_after: 2027-02-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:00:00Z }
sources:
  - id: readme
    resource: ../raw/gbrain/README.md
    scope: ../raw/gbrain/
    kind: code
    revision: 27f8b9d
    title: GBrain README (repository root)
  - id: retrieval-doc
    resource: ../raw/gbrain/docs/architecture/RETRIEVAL.md
    kind: code
    revision: 27f8b9d
    title: Retrieval architecture
  - id: search-modes
    resource: ../raw/gbrain/docs/guides/search-modes.md
    kind: code
    revision: 27f8b9d
    title: Search modes guide
  - id: search-explain
    resource: ../raw/gbrain/docs/guides/search-explain.md
    kind: code
    revision: 27f8b9d
    title: Search explain guide
  - id: hybrid-ts
    resource: ../raw/gbrain/src/core/search/hybrid.ts
    kind: code
    revision: 27f8b9d
    title: Hybrid search orchestration
  - id: mode-ts
    resource: ../raw/gbrain/src/core/search/mode.ts
    kind: code
    revision: 27f8b9d
    title: Search mode bundles
  - id: vector-pool
    resource: ../raw/gbrain/src/core/search/vector-pool.ts
    kind: code
    revision: 27f8b9d
    title: Bounded vector pool
  - id: planner-stats
    resource: ../raw/gbrain/docs/guides/planner-stats.md
    kind: code
    revision: 27f8b9d
    title: Planner statistics guide
  - id: exact-search
    resource: ../raw/gbrain/docs/guides/exact-search.md
    kind: code
    revision: 27f8b9d
    title: Exact search guide
---

GBrain search fuses four recall arms — vector (HNSW on pgvector chunks), BM25 keyword (`tsvector`), title-phrase, and a relational typed-edge arm — at *page grain* with reciprocal rank fusion, blends in cosine, applies source-aware boosts, optionally reranks with a cross-encoder, and finally applies a token budget. A separate verb, `think`, gathers streams and writes a cited answer (see [knowledge graph](gbrain-knowledge-graph.md)). Keyless installs get keyword retrieval only.[^retrieval-doc][^readme] Embedding choices are in [embeddings and providers](gbrain-embeddings-and-providers.md); benchmark numbers are in [evals and benchmarks](gbrain-evals-and-benchmarks.md).

## Stage order (Observed by subagent in code and doc)

intent classify → expansion (off by default) → hybrid recall (vector / keyword / title / relational) → source-aware SQL re-rank → page-grain RRF (`k = 60`) → cosine blend `0.7 × normalized RRF + 0.3 × cosine` → post-fusion boosts (backlink, salience, recency, graph, exact-match; gated by `metadata_boost_gate = lexical`) → graph augment (when walk depth > 0) → dedup → **rerank** → feedback → relational re-pin → alias hop → exact-lookup tier → evidence stamp → autocut → limit slice → token budget. Dedup precedes the reranker; the alias hop follows it; the token budget is last.[^hybrid-ts][^retrieval-doc]

- **Page-grain RRF:** each arm votes for a page at its best chunk rank; votes sum per `(source_id, slug)` and the lead chunk carries the sum.[^hybrid-ts]
- **Reranker:** cross-encoder over `chunk_text || title`, fails open to RRF order when no key is configured (stamped `reranker_skipped (no_key)`). A **relational re-pin** (`search.relational_rerank_pin = 3`) stops the reranker from burying typed-edge answers.[^retrieval-doc]
- **Exact search:** `search --exact` matches identifiers; credential values are masked in the index so a secret never matches (Reported).[^exact-search]

## Modes (Observed in `MODE_BUNDLES`; table also in the guide)

| Knob | conservative | balanced (default) | tokenmax |
| --- | --- | --- | --- |
| token budget | 4,000 | 12,000 | off |
| search limit | 10 | 25 | 50 |
| reranker | off | `voyage:rerank-3-lite`, top-N-in 25 | on, larger top-N-in |
| relational retrieval and planner | off | on | on |
| expansion, autocut, reranker gate | off | off | off |

Resolution order: per-call options → per-key `search.*` config → `MODE_BUNDLES[search.mode]` → `balanced`. Non-TTY init picks tokenmax with a chat key, balanced with a ready reranker, else conservative. Semantic result caching is temporarily disabled in every mode even though bundles keep `cache_enabled: true`.[^mode-ts][^search-modes]

## Readiness and failure modes

- **Index rebuilding (Reported):** `projection_readiness` reports `projection_pending | projection_status_unknown | projection_by_design`. A text-ready index does not guarantee every page has a vector; remote reads withhold a page's chunks until a rebuild stamps the current chunker version and surface `degraded: [safe_index_pending]`. `gbrain repair safe-chunks` reseals. Vectors are preserved across rebuilds only when `embedding_input_hash` matches.[^retrieval-doc]
- **Bounded vector scan (Observed):** per-page max-pool CTE; pool escalation ×4 up to three times; hard cap `POOL_MAX_SCAN_TUPLES = 20,000`. Shortfalls surface as `vector_candidates_incomplete` and `vector_pool_underfilled`; `search.hnsw_iterative_scan` is latched once per engine (restart `serve` to change).[^vector-pool]
- **Keyword arm:** default statement timeout 8,000 ms (Postgres); CJK deadline 3,000 ms; CJK queries always use an `ILIKE` fallback even with `pgroonga`/`zhparser` installed (Reported). If both lexical arms fail with an access-class error the call raises `database_error` rather than returning "no results".[^retrieval-doc]
- **Planner statistics (Reported):** PGLite has no autovacuum, so a 40 ms search can become tens of seconds without stats; delta-tracked tables auto-ANALYZE at `max(500, 10%)` churn, and `pg_upgrade` can lose stats (50–60 s searches at 5k pages) — guarded by background refresh and a `planner_stats_stale` signal.[^planner-stats]
- **Provider failures:** reranker fails open; a slow local embedder yields `embed_timeout` in `degraded[]` and keyword-only fallback (`GBRAIN_QUERY_EMBED_TIMEOUT_MS`, default 6 s); an embedding job is quarantined after 3 zero-progress attempts.[^retrieval-doc]
- **Incomplete-result signaling:** search reports when results are incomplete so an empty result is not proof a page is missing (README advice: ask the agent to check whether the index is ready).[^readme]

## What text reaches providers (Observed unless noted)

Chunk text is credential-sanitized before chunking; embeddings send `chunk_text` with an optional just-in-time `<context>` title/synopsis prefix that is never persisted; the reranker sends capped `chunk_text || title` and logs only a SHA-256 prefix of the query; expansion and `think` send the query and gathered page text to the configured model. `search-explain` marks the expansion fix as consent-requiring (`consent: ["paid","egress"]`). Query embeddings are cached per process by exact string; retrieval feedback stores no query text and expires answer rows after 30 days by default.[^retrieval-doc][^search-explain] See also [memory trust and egress](gbrain-memory-trust-and-egress.md).

## Other documented knobs

Entity anchoring and CRAG escalation default off; the facts arm is on for `query`; `search.remote_page_cap` defaults to 3 pages for remote callers (Observed).[^mode-ts]

## Relationships

- Depends on: [data model](gbrain-data-model-and-system-of-record.md) (chunks, links), [architecture](gbrain-architecture-and-engines.md) (engine SQL).
- Part of: [GBrain overview](gbrain-overview.md).

[^readme]: `README.md` "Two ways to query your brain" (search vs think; incomplete-result paragraph).
[^retrieval-doc]: `docs/architecture/RETRIEVAL.md` "Putting it together", "Source-aware ranking", "Relational re-pin", "Chunk rebuilds after upgrading", "How to verify".
[^search-modes]: `docs/guides/search-modes.md` mode table, "Setting and resolving", "The mode picker".
[^search-explain]: `docs/guides/search-explain.md` (cosine blend; expansion consent).
[^hybrid-ts]: `src/core/search/hybrid.ts` ~lines 58 (RRF k), 1098–1300 (stage order), 1296 (token budget); `src/core/search/rrf-page-fusion.ts:22-44`.
[^mode-ts]: `src/core/search/mode.ts::MODE_BUNDLES`; `src/core/search/entity-anchor.ts:165`.
[^vector-pool]: `src/core/search/vector-pool.ts` lines 58, 85, 121–135.
[^planner-stats]: `docs/guides/planner-stats.md`.
[^exact-search]: `docs/guides/exact-search.md` "What matches".
