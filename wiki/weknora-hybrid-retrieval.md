---
type: Concept
title: WeKnora hybrid retrieval and reranking
description: Store-bound fan-out, normalized weighted RRF, rerank degradation, composite scoring, and MMR diversity selection.
tags: [ml, weknora, rag, retrieval]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora fans knowledge searches across store-bound vector/keyword engines, fuses candidate lists, and applies shared reranking and diversity selection. **Observed:** the pipeline distinguishes partial retrieval errors from total engine failures and treats rerank-model failure as a degradation to retrieval order. Static mechanisms establish implementation intent, not retrieval quality or backend equivalence.[^weknora]

## Candidate retrieval and fusion

Store creation verifies tenant ownership and distinguishes missing, unavailable, and forbidden bindings. Multi-KB search rejects differing embedding models; the query embedding can be computed once and reused in fan-out. Candidate over-retrieval uses `max(matchCount*5, 50)` per KB, with a total cap of 500; API requested result counts cap at 200.[^weknora]

**Observed default weighted reciprocal rank fusion:** `k=60`, vector weight 0.7, keyword weight 0.3. Using best 1-based rank per retriever:

`score = (wv/(k+rv) + wk/(k+rk)) / ((wv+wk)/(k+1))`.

`GetEffectiveRRFK` replaces non-positive `k` with 60; `GetEffectiveRRFWeights` replaces each non-positive weight with its default. Setting a weight to zero therefore does **not** disable that retriever. A missing retriever contribution is absent rather than assigned rank zero. Top rank in both lists normalizes to 1. Vector-only paths preserve their scores; keyword-only paths rescale unbounded per-list scores when necessary instead of treating raw BM25 as a probability.[^weknora]

`CompositeRetrieveEngine.Retrieve` distinguishes engine-level errors (discard results) from result-level errors (return hits **and** an error). **Synthesis:** a caller that treats every non-nil error as an empty result would erase useful partial evidence.[^weknora]

## Rerank and diversity

**Observed:** rerank takes up to `max(top_k, 50)` available fused candidates after raising retrieval depth to match `top_k`. The enclosing candidate-retrieval and requested-`top_k` caps supply the 500 bound, rather than the slicing expression independently enforcing it. Effective configuration defaults include retrieval depth 50, vector threshold 0.15, keyword threshold 0.3, and rerank output 10. Rerank threshold falls back to 0.2 for a nil configuration; a non-nil configuration preserves its threshold, including zero (`GetEffectiveRerankThreshold`).[^weknora]

When no candidate passes a high threshold (>0.3), the shared stage relaxes it to `max(threshold*0.7, 0.3)`. If still empty, a best candidate can survive at fallback score 0.15; explicit document/tag scope relaxes that fallback. Model failure returns input retrieval order with diagnostics rather than inventing model scores.[^weknora]

Composite score weights are 0.6 model + 0.3 retrieval + 0.1 source, clamped to `[0,1]`; graph results have special missing-score handling. MMR defaults to lambda 0.7 and token-set Jaccard redundancy. Passage fitting bounds vendor input size. Image hits have a separate evidence-preservation exception; these paths are described in [graph and multimodal retrieval](weknora-graph-multimodal-retrieval.md).[^weknora]

## Backend constraints

Selected PostgreSQL code lazily detects a compatible ParadeDB/pg_search score function: vector-only use can remain possible, but keyword queries need that extension/function. Selected Milvus code separates collections by embedding dimension and distinguishes absent collections from partial keyword-search failures. Other registered backends were inventoried, not audited for identical semantics.[^weknora]

## Relationships

- Consumes [parsed and chunked documents](weknora-document-ingestion.md).
- Uses [workspace/store bindings](weknora-persistence.md).
- Complements, rather than replaces, [wiki-page retrieval](weknora-wiki-compilation.md).

## Coverage limits

Fusion/shared rerank code received deeper inspection than backend drivers. SQLite, Qdrant, Weaviate, Elasticsearch, OpenSearch, Doris, Tencent VectorDB, embedding providers, and rerank vendor adapters remain pending. Test names were inspected but no searches, benchmarks, or tests ran. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd58`: `internal/application/service/retriever/factory.go::VerifyBinding`, `CreateRetrieveEngineForKB` and error sentinels; `retriever/composite.go::CompositeRetrieveEngine.Retrieve`; `knowledgebase_search.go::hybridSearchCandidates`, `validateSameEmbeddingModel`; `knowledgebase_search_fusion.go::fuseWithRRF`, `bestRanks`, `fuseOrDeduplicate`, `rescaleUnboundedScores`; `knowledgebase_search_rerank.go::HybridSearchWithRerank`; `internal/types/retrieval_config.go` effective defaults/caps; `internal/reranking/rerank.go::Rerank`, `applyThreshold`, `FallbackMinScore`, `CompositeScore`, `fitPassages`; `reranking/mmr.go::SelectMMR`; `internal/application/repository/retriever/postgres/repository.go::resolveKeywordScoreFunction`; `retriever/milvus/repository.go::getCollectionName`, `VectorRetrieve`, `KeywordsRetrieve`. Package entry: [README](../raw/WeKnora/README.md), “Retrieval” and “Supported backends.”
