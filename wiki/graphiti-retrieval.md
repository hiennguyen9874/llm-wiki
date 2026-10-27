---
type: Concept
title: Graphiti retrieval and ranking
description: Hybrid semantic, keyword, and graph-traversal search with graph-distance reranking and search recipes, as documented rather than measured.
tags: [rag, retrieval, ranking, knowledge-graph]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
stale_after: 2027-01-24
sources:
  - id: graphiti-readme
    resource: ../raw/graphiti.md
    kind: documentation
    title: Graphiti README — A Framework for Building Temporal Knowledge Graphs (getzep/graphiti)
---

**Reported:** Graphiti answers queries by combining semantic embeddings, BM25 keyword matching, and graph traversal, then reranking the retrieved relationships by graph distance, with the stated intent of low-latency, high-precision answers that do not depend on LLM summarization at query time.[^graphiti-readme] **Synthesis:** because retrieval runs over the same timed edges that ingestion wrote, the query surface can be filtered by validity rather than only by similarity — that is the architectural difference from chunk-based hybrid search, but the README does not specify the mechanism or its costs.[^graphiti-readme]

## Documented mechanics

- **Three signals:** semantic embeddings, keyword (BM25), and graph traversal are combined for "low-latency, high-precision queries without reliance on LLM summarization".[^graphiti-readme]
- **Edge-first search:** the quickstart's retrieval steps search relationships (edges) with hybrid search, rerank those results using graph distance, then search nodes using predefined "search recipes".[^graphiti-readme]
- **Temporal filtering:** the stated purpose of the temporal model is querying what is true now or what was true at a chosen point in time, and facts are invalidated rather than deleted so that history stays queryable.[^graphiti-readme]
- **Contradictions:** the README describes automatic fact invalidation with temporal history preserved, contrasted with LLM-driven summarization judgements.[^graphiti-readme]

## Reported performance claims

| Claim | Value in README | Status |
| --- | --- | --- |
| Graphiti query latency | "Typically sub-second" | Reported, unmeasured |
| GraphRAG query latency (comparison) | "Seconds to tens of seconds" | Reported, unmeasured |
| Zep retrieval at scale | "Sub-200ms" | Reported vendor figure for the managed platform |

Neither figure has a stated benchmark, corpus, hardware, or configuration behind it, so none should be used as an engineering input without independent measurement.[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Reads:** the [context graph model](graphiti-context-graph-model.md) produced by [episode ingestion](graphiti-episode-ingestion.md); embeddings and reranking come from [model and provider configuration](graphiti-model-providers.md).
- **Depends on:** [deployment and graph backends](graphiti-deployment-backends.md) for vector, keyword, and traversal capability.
- **Related:** [LightRAG retrieval modes](lightrag-retrieval.md) fuse entity/relation graph branches with vector search rather than BM25, and [OpenRAG hybrid retrieval](openrag-hybrid-retrieval.md) combines per-model vector clauses with keyword matching. **Synthesis:** neither concept documents validity-window filtering, so Graphiti's distinguishing retrieval input is the timed edge, not its fusion formula.

## Evidence limits

**Reported only, and thin.** The README names no search functions, parameters, fusion or normalization scheme, recipe catalogue, candidate limits, embedding dimensions, index configuration, caching, or evaluation results; the quickstart example that would demonstrate them was not inspected. Treat this page as an interface-level map: neither ranking quality nor latency was reproduced.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “Why Graphiti?” (Hybrid Retrieval bullet, Temporal Fact Management), “Quick Start” steps 4–6 (edge hybrid search, graph-distance reranking, node search recipes), “What is a Context Graph?” (validity windows), “Graphiti vs. GraphRAG” rows on retrieval method, contradiction handling and query latency, and “Zep vs Graphiti” row on retrieval and performance.
