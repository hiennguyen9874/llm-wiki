---
type: Concept
title: LightRAG retrieval modes and ranking
description: Dual-level graph retrieval, vector-chunk mixing, keyword routing, chunk selection, reranking, and token-budget ordering.
tags: [rag, retrieval, ranking]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:15:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
---

**Observed:** LightRAG combines entity-vector retrieval, relation-vector retrieval, graph expansion, and optionally direct chunk-vector search. Its default `mix` mode combines these branches; `hybrid` combines only the two graph-oriented branches. **Synthesis:** this is graph-plus-vector hybrid retrieval, not lexical BM25 fusion or guaranteed multi-hop reasoning. Mode quality and latency claims in the README remain Reported, not measured here.[^lightrag-aaebfe1]

## Query-mode matrix

| Mode | Entity branch | Relationship branch | Direct chunk vectors |
| --- | --- | --- | --- |
| `local` | Low-level keywords | Edges expanded from entity hits | No |
| `global` | Endpoints expanded from relation hits | High-level keywords | No |
| `hybrid` | Yes | Yes | No |
| `mix` | Yes | Yes | Yes |
| `naive` | No | No | Query directly |
| `bypass` | No | No | No; direct query-role generation |

**Observed:** `_perform_kg_search` gates branches on available keyword lists and stores. Local/global results are interleaved round-robin, then deduplicated by entity name or canonical endpoint pair: this is not weighted-score normalization or reciprocal-rank fusion. Local entity-derived relations are sorted by degree/rank and weight; global relation hits retain vector-search ordering. Similar mode names therefore do not imply identical graph ordering.[^lightrag-aaebfe1]

## Keywords and embeddings

- **Observed:** providing either caller keyword list suppresses automatic extraction for both lists. Otherwise the `keyword` role is asked for high/low-level JSON keywords; tolerant parsing removes reasoning/fences and can repair JSON. Invalid cached keyword payloads trigger a fresh call.
- If both extracted lists are empty, queries shorter than 50 raw characters fall back to using the full query as low-level keywords; longer queries return a no-context response without retrieval.
- The graph path batches query/low/high keyword embeddings actually needed by the selected mode with `context="query"`. A failed batch warns and leaves downstream stores to embed independently; this is a fallback path, not a measured equivalence result.
- Defaults: `top_k=40`, `chunk_top_k=20`, cosine threshold `0.2`. Query/request ceilings are separate from these defaults.[^lightrag-aaebfe1]

## Four-stage context construction

1. **Search:** gather graph entities, relations and optional vector chunks.
2. **Entity/relation truncation:** select and order records under independent budgets, default 6,000 entity and 8,000 relation tokens.
3. **Chunk merge:** recover source chunks from retained graph records and merge them with directly retrieved chunks.
4. **Context render:** rerank/filter/limit chunks and fit the final context under the default 30,000-token total budget.[^lightrag-aaebfe1]

**Observed:** graph-derived chunk picking defaults to `VECTOR`, retrieving stored chunk vectors and cosine-ranking against the query; unavailable/incomplete vectors can trigger `WEIGHT` polling. Weight polling allocates position-biased quotas; the default related-chunk number is five. A zero limit remains a kill switch. Entity-first dedup means a shared chunk may be attributed to its earliest group; stage-two output order must propagate into chunk allocation.[^lightrag-aaebfe1]

**Observed:** available chunk tokens are computed as total budget minus actual system-prompt estimate, graph context, query tokens, and a 200-token reference/safety reserve. Naive mode omits graph context. Parent headings are attached before truncation and counted, not free metadata. The final renderer rechecks candidate counts because reference numbering depends on surviving chunks. Debug/context-only paths still charge prompt overhead to preview real generation budgets.[^lightrag-aaebfe1]

## Rerank ordering and degradation

**Observed:** the unified chunk funnel applies rerank → positive minimum-score filter → `chunk_top_k` slice → token truncation → chunk renumbering. `QueryParam`'s `RERANK_BY_DEFAULT` flag defaults on, but the server binding defaults to `null`; a missing reranker warns and returns the original ordering. A default deployment therefore performs no reranking despite the enabled flag. Empty/unusable results or exceptions also fall back to original chunks. Minimum score defaults to `0.0`, so score filtering is normally disabled. A hand-built `global_config` missing `min_rerank_score` instead takes the funnel's `0.5` fallback, a distinct embedded-caller trap. Malformed individual rank entries are rejected; fallback is not proof that reranking succeeded.[^lightrag-aaebfe1]

**Observed:** server-selectable rerank bindings are null, Cohere, Jina and Aliyun. Cohere's optional long-document chunking parameters are not uniformly forwarded to every adapter. Rerank concurrency and timeout are separately queued from query-role LLM calls. **Reported:** README rerank latency and quality improvements were not tested.[^lightrag-aaebfe1]

## Relationships

- **Uses:** [Storage backends](lightrag-storage.md) for branch-specific vector and graph behavior.
- **Uses:** [Model roles](lightrag-models.md) for keyword, embedding and rerank calls.
- **Produces:** [Query contexts and citations](lightrag-query-contracts.md).
- **Depends on:** [Ingestion](lightrag-ingestion.md) for chunk IDs and graph-to-source anchors.

## Evidence limits

Targeted static code and selected test-assertion inspection only. No retrieval request, quality benchmark, provider call, latency measurement, or backend comparison ran. Missing-backend and token-boundary branches are not integration-verified; see [coverage](lightrag-source-map.md).

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`: `lightrag/lightrag.py::LightRAG.aquery_llm`; `operate.py::kg_query, naive_query, get_keywords_from_query, extract_keywords_only, _perform_kg_search, _apply_token_truncation, _merge_all_chunks, _build_context_str, _get_node_data, _get_edge_data, _vector_chunk_quota`; `utils.py::pick_by_vector_similarity, pick_by_weighted_polling, process_chunks_unified, apply_rerank_if_enabled, normalize_rerank_result, _truncate_chunks_for_unified_context`; `base.py::QueryParam`; `constants.py::DEFAULT_TOP_K, DEFAULT_CHUNK_TOP_K, DEFAULT_MAX_ENTITY_TOKENS, DEFAULT_MAX_RELATION_TOKENS, DEFAULT_MAX_TOTAL_TOKENS, DEFAULT_COSINE_THRESHOLD, DEFAULT_RELATED_CHUNK_NUMBER`; `rerank.py::generic_rerank_api, cohere_rerank, jina_rerank, ali_rerank`; `api/config.py` rerank choices; `api/lightrag_server.py::initialize_rag`; selected assertions in `tests/test_kg_vector_chunk_quota.py`, `tests/test_operate_truncation_order.py`, `tests/utils/test_pick_by_vector_similarity.py`, `tests/utils/test_normalize_rerank_result.py`; README query/rerank guidance.
