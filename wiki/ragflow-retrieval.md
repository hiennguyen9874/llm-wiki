---
type: Concept
title: "RAGFlow hybrid retrieval and ranking"
description: "Hybrid candidate generation, backend-specific score recomputation, parent-child promotion, filters, and retrieval defaults."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:16:02Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa024356711dc86de2e231afb0e4bf1
    title: RAGFlow repository snapshot
---

# RAGFlow hybrid retrieval and ranking

**Observed:** the NLP retrieval service combines query construction, dense vector search, backend fusion, result pruning and reranking. Dataset search, retrieval-debug APIs, and agent tools adapt requests into this shared service. Backend ranking paths differ; a single “hybrid weight” is not a complete description of every engine's scoring behavior.[^ragflow]

## Shared request defaults and constraints

At `RetrievalService.Retrieval`, absent values become kNN top-k 1024, kNN candidates 2048, similarity threshold 0.2, vector weight 0.3 (1.0 for vector-only), rerank pool 64, and pagerank feature weight 10. Page/page-size are normalized; the candidate pool must cover `page × page_size`. A model reranker is only accepted with page 1. These are service-local defaults and can be overridden by upstream callers.[^ragflow]

## Candidate generation and scoring

1. QueryBuilder normalizes text, expands synonyms and weighted phrases, and builds lexical expressions.
2. Search applies dataset/document/availability filters and optionally obtains a query embedding; engine adapters translate text/vector fusion into backend-specific expressions.
3. Empty-result retry relaxes match/similarity parameters; dense-only fallback depends on `AllowDenseFallback` rather than being unconditional.
4. Scoring uses a configured model or engine-specific alternatives: native Infinity scores, local hybrid scoring for OceanBase/Vastbase, direct vector-only scores, or Elasticsearch kNN/term scores with fallback.
5. Deleted chunks are pruned, thresholds applied, and optional child hits can be promoted to hidden parents through `mom_id` plus document identity.[^ragflow]

## Weight and field semantics

Reranking can weight titles, important keywords, generated questions and content differently. ES query field boosts also operate before final score recomputation; they are not interchangeable with the user-facing vector/keyword balance. `NormalizeSimilarityWeights` requires vector and keyword weights to sum to one within tolerance (1e-9) when both are supplied, deriving the missing complement when only one is supplied. **Synthesis:** compare end-to-end retrieval quality per engine/configuration rather than assuming equal weights imply equal ranking.[^ragflow]

## Compiled knowledge boundary

By default, dataset search includes ordinary chunks plus dataset-scoped compiled rows and filters out document-scoped compiled rows: unset compilation scope resolves to `dataset`. Explicit `include_knowledge_compilation=false` excludes all compiled rows; `knowledge_compilation_scope=all` applies no compilation filter unless that exclusion flag is set. Agentic RAG can add navigation/graph tools when compiled rows exist. Product scope and request options therefore determine which compiled knowledge is searched.[^ragflow]

## Relationships

- **Depends on:** [indexed ingestion products](ragflow-ingestion.md) and [engine adapters](ragflow-persistence.md).
- **Used by:** [agent workflows](ragflow-agent-workflows.md).
- **Provides evidence for:** [answer citations](ragflow-citations.md), not a proof that the answer itself is correct.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa024356711dc86de2e231afb0e4bf1`; locators: `internal/service/nlp/retrieval.go::Retrieval / Search / scoreSearchResult / RetrievalByChildren / GetFilters / buildRetrievalFusionExpr`; `internal/service/nlp/query_builder.go::Question`; `internal/service/nlp/reranker.go::RerankStandard / RerankWithKNN / HybridSimilarity`; `internal/service/similarity_weight.go::NormalizeSimilarityWeights`; `internal/engine/elasticsearch/chunk.go::buildQueryStringQuery`; `internal/service/dataset/search.go::SearchDatasets / knowledgeCompilationFilter`; `internal/service/chunk/chunk.go::RetrievalTest`; `internal/agent/tool/retrieval_nlp.go::NLPRetrievalAdapter.Search`; `internal/agentic_rag/compiled_knowledge.go::compiledKnowledgeTools`.
