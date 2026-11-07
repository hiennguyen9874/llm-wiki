---
type: Concept
title: Hy Memory chat retrieval pipeline and graph rerank
description: How chat search works — readers, multi-channel recall, additive BM25/tag fusion with RRF, schema and intention lanes, rerank, return channels, and graph projection and rerank.
tags: [agent-memory, hy-memory, retrieval, bm25, rrf, graph]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory chat retrieval pipeline and graph rerank

Chat search embeds the query, recalls from several channels in parallel, fuses scores additively with an RRF blend, adds schema and intention lanes, optionally reranks, and returns channel-bucketed results; documentation lives in `docs/hy_memory_search_skill.md` and `docs/pro_graph_design.md`.[^hy-memory]

## Readers

`MemoryReader` delegates to `LegacyReadPipeline` (keyword recall off) or `HybridReadPipeline` (on) selected via `HY_MEMORY_READER`; everything after recall is shared in `BaseReadPipeline` (`pipelines/reader.py`, `reader_base.py`, `_retrieval/config.py::resolve_reader_name`). Chroma returns no keyword hits, so hybrid degrades to vector-only there.[^hy-memory]

## Stages (`reader_base.py::_read_once`)

1. Embed and lemmatise (spaCy + jieba with fallback); `query_expand.py` widens brittle lexical patterns.
2. Isolation key `user_id:agent_id` (`base.py::PipelineContext.isolation_key`).
3. Parallel recall: vector semantic, vector keyword, hidden L0 (user-level only), retrieval-clause aliases, graph L6 forward, tag-index nominees, episode semantic/keyword, intentions (if `intention_limit>0`).
4. Semantic gate, BM25 normalisation (sigmoid unless the backend already normalises).
5. Additive fusion `final = sem + 1[bm25]·W_BM25·bm25_norm + 1[tag]·W_TAG·max(tag_cos, entity_hit)` plus `blend_rrf_into_scores` (`RRF_K`=60) and optional light temporal boosts.
6. L6 forward with evidence-count boost; L6 reverse lookup with RRF fusion; intention list; evolution-chain expansion and `created_after` end-gate.
7. Assembly with graph rerank before truncation, owner gate on schemas, near-dup/social-boilerplate demotion, MMR, lexical-survival guards, episode capsules, multi-seed and hierarchy bundles, optional local cross-encoder rerank, strength decay `(1+log(access_count))·exp(-idle_days/180)`, then underflow fill when `MEMORY_HYBRID_V2_FILL_UNDERFLOW=1`.

(`pipelines/reader_base.py` stage markers; `_retrieval/scoring.py`, `rrf.py`, `diversity.py`, `candidate_guards.py`, `session_episode.py`, `local_rerank.py`, `strength.py`, `underflow.py`.)[^hy-memory]

Default weights: BM25 0.35, tag 0.3, tag cosine threshold 0.5, RRF blend 0.4, vector pool 30, keyword max 10; BM25 k1 1.5, b 0.75. Local rerank is off by default (`MEMORY_LOCAL_RERANK_ENABLED`), model `nreimers/mmarco-mMiniLMv2-L6-H384-v1`, requires the `rerank` extra. `search(rerank=False)` bypasses all rerank stages (2.0.6) (`reader_base.py` ~1154–1200; `_retrieval/config.py`; `CHANGELOG.md::2.0.6`).[^hy-memory] The `reader_base.py` docstring says `w_bm25=0.2` while the code default is 0.35 (reconcile retrieval still uses 0.2) — doc/code divergence (Synthesis).[^hy-memory]

## Return channels

The reader emits one flat list (`normal + schema + intention`); the client re-buckets into `normal`, `schema`, `proactive`. **`profile` is not a search bucket** — L0 is served only by `client.get_user_profile()` (`client.py::_search_memory_channel`, `get_user_profile`; `docs/hy_memory_search_skill.md`). The README example still describes "profile / normal / proactive" channels (`README.md::Chat Memory`), which conflicts with the code reading; prefer the code and search-skill doc (Observed disagreement).[^hy-memory]

## Graph projection and rerank (pro with graph, ultra)

- **Projection**: L2 facts become `Memory(layer=l2_fact)` nodes (not `VdbRef`) with edges from `co_occurs`, `semantic_neighbor` (≥0.55), LLM-typed relations, `TAGGED_WITH`→Topic, `MENTIONS`→Entity and optional `TEMPORAL_NEXT`; no embeddings on graph nodes; lifecycle sync on supersede/shadow (`pipelines/_graph/projector.py::project_memories_to_graph`).[^hy-memory]
- **Rerank**: A support propagation (in-pool only), B bounded relation expansion gated by `sim(cand) ≥ sim(seed) − 0.2`, C relation paths in `extra["related_paths"]`; `TYPE_PRIOR` ranks `causes`/`elaborates` 0.9 down to `semantic_neighbor` 0.35. Fail-open, gated by `MEMORY_GRAPH_RERANK_ENABLED` (`_graph/rerank.py`; `docs/pro_graph_design.md` §§1–7).[^hy-memory]

## Relationships

- Reads output of: [Chat write path](hy-memory-chat-hierarchy-and-write-path.md), [System 2](hy-memory-system2-evolution.md).
- Depends on: [Storage backends](hy-memory-storage-and-reembed.md).
- Part of: [Hy Memory overview](hy-memory-overview.md).

## Coverage and limits

Static inspection (delegated); `_retrieval/` has ~45 modules, read at module-docstring/stage level. No recall-quality measurements were run (Unverified).

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
