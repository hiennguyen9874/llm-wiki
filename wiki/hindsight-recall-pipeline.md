---
type: Concept
title: Hindsight recall pipeline
description: How Hindsight retrieves memories with four parallel strategies, reciprocal rank fusion, reranking, boosts and token budgeting, with default parameters.
tags: [agent-memory, hindsight, recall, retrieval]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: retrieval-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/retrieval.md
    kind: documentation
    revision: eb963cb
    title: Retrieval developer doc
  - id: engine
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/search/fusion.py
    kind: code
    revision: eb963cb
    title: Search fusion module
  - id: rag-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/rag-vs-hindsight.md
    kind: documentation
    revision: eb963cb
    title: RAG vs Hindsight
---

`recall` retrieves memories of any type (world, experience, observation) by running four retrieval arms in parallel, fusing them with reciprocal rank fusion (RRF), reranking, applying small multiplicative boosts, and truncating to a token budget.[^readme][^retrieval-doc]

## Pipeline (docs Reported, code Observed)

1. **Four arms:** semantic (pgvector ANN), keyword (BM25), graph (link expansion from seed units), temporal (time-range filtering). Code: `engine/search/retrieval.py`, `engine/memories/pg/recall.py`, `engine/search/graph_retrieval.py`.[^engine]
2. **Fusion:** RRF with `k = 60`, arms equally weighted: `score(d) = Σ 1/(60 + rank_i(d))`. `interleave` (round-robin) exists for consolidation dedup.[^retrieval-doc][^engine]
3. **Rerank:** cross-encoder pre-filtered to top 300 (`HINDSIGHT_API_RERANKER_MAX_CANDIDATES`); batches of 32 (local) / 128 (TEI). Selectable `cross_encoder | rrf | interleave`.[^retrieval-doc][^engine]
4. **Boosts:** each `1 + α(signal − 0.5)` — recency α=0.2 (linear decay over 365 days, clamp 0.1–1.0), temporal proximity α=0.2, proof count α=0.1; combined range ≈ +27% / −23%.[^retrieval-doc]
5. **Token budget:** counts memory text only; the top result is always returned whole. The REST request default `max_tokens` is 4096 (`api/http.py` request model; documented), while `HINDSIGHT_API_RECALL_MAX_TOKENS=2048` (`config.py::DEFAULT_RECALL_MAX_TOKENS`) is the budget for *internal* recall such as reflect's tool — a different path, not a conflict (Observed by curator).[^retrieval-doc][^engine]

## Parameters

| Item | Value |
| --- | --- |
| `budget` low / mid / high | 100 / 300 / 1000 (fixed mode); adaptive mode 2.5% / 7.5% / 25% of `max_tokens`, clamped 20–2000 |
| Similarity gates | semantic 0.3, graph seed 0.3, temporal 0.1, semantic-link creation 0.7 |
| Graph score | additive `tanh(shared_entities × 0.5) + semantic_link + causal_link ∈ [0,3]` |
| BM25 backends | `native` (tsvector, not true BM25), `vchord`, `pg_textsearch`, `pgroonga`, `pg_search` via `HINDSIGHT_API_TEXT_SEARCH_EXTENSION`; only `pg_search` is Citus-compatible |
| Chunks | `include_chunks` + `max_chunk_tokens` return raw source text |

Source: [^retrieval-doc]

Decision-model ranking replaces the cross-encoder, makes its order final, publishes `scores.reranker: null` and rejects `min_scores.reranker` with HTTP 400; see [Decision models](hindsight-decision-models.md).[^retrieval-doc]

## Versus plain RAG (Reported)

The docs contrast RAG (semantic only, no entities, stateless) with Hindsight (four strategies, entity graph, temporal parsing, consolidation, disposition) and recommend RAG for static-corpus Q&A, Hindsight for persistent memory, entity tracking and temporal queries.[^rag-doc]

## Contradictions

- Code docstrings in `engine/memory_engine.py` describe an MMR diversity step ("Diversify: Apply MMR", "MMR with λ=0.5"), but a grep of `hindsight_api/` finds MMR only in those two docstrings; the implemented flow is fusion → rerank → budget selection (`engine/fact_budget.py::select_facts_within_budget`). Observed by curator grep; see [discrepancies](hindsight-doc-code-discrepancies.md).[^engine]

## Relationships

- Reads what [Retain](hindsight-retain-pipeline.md) writes; ranks observations produced by [Consolidation](hindsight-consolidation-and-mental-models.md).
- Used by [Reflect](hindsight-reflect-agent.md) as its `recall` tool.
- Configured via [Storage and configuration](hindsight-storage-and-configuration.md); rerankers listed in [Providers](hindsight-llm-embedding-providers.md).

[^readme]: `README.md` § "Recall".
[^retrieval-doc]: `hindsight-docs/docs/developer/retrieval.md` (strategies, fusion, reranking, boosts, budgets, decision-model ranking sections).
[^engine]: `hindsight-api-slim/hindsight_api/engine/search/{fusion,reranking,retrieval,graph_retrieval,decision_reranker}.py`, `engine/memories/pg/recall.py`, `engine/fact_budget.py`, `engine/memory_engine.py::recall_async` (docstrings near lines 9515 and 10015).
[^rag-doc]: `hindsight-docs/docs/developer/rag-vs-hindsight.md` (comparison table, recommendation).
