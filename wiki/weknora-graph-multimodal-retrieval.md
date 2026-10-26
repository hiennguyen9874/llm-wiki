---
type: Concept
title: WeKnora graph and multimodal retrieval boundaries
description: Graph evidence validation and image-aware retrieval exceptions, distinguished from the wiki-page link graph.
tags: [ml, weknora, graph, multimodal, retrieval]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd5855fc4ded5c981a92dcb82a455246
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora has distinct graph and image-aware evidence paths in addition to text/vector retrieval. **Observed:** graph search checks access and validates cited chunks; shared reranking has exceptions for graph hits and sufficiently strong image-vector evidence. The document entity graph is not the same structure as the automatic wiki's page-link graph.[^weknora]

## Graph evidence boundary

Selected `graphSearchService.Search` code checks the knowledge-base read grant, API-key retrieve capability, and graph-enabled setting. An absent backend produces a service-unavailable outcome rather than silently presenting an empty graph. Request normalization declares a ten-second timeout and bounded graph/evidence sizes; initial defaults include 50 nodes, 100 relationships, and 200 source chunks.[^weknora]

**Observed:** source chunks are revalidated as enabled, live, and belonging to the same knowledge/document and KB. This matters because graph attributes aggregate at document level: a graph association alone should not establish that every listed chunk supports the answer. Extraction accuracy and Neo4j query completeness were not checked.[^weknora]

## Image evidence and shared reranking

**Observed:** image payload sanitization replaces inline base64 data URLs before textual embedding so encoded pixels are not fed as enormous text. `reranking/image.go` declares a minimum image-keep score of 0.25; the shared reranker can preserve bounded image hits using vector evidence even when a text reranker rejects pictorial content. Graph candidates also receive special handling because they lack ordinary retrieval scores.[^weknora]

**Reported:** v0.8.3 advertises multimodal embedding into a shared text/image vector space, opt-in image-vector retrieval, compatible reranking, and an image gallery. Provider implementations, image-index construction, and gallery behavior were not inspected sufficiently to promote those claims to reproduced or end-to-end observed behavior.[^weknora]

## Relationships

- Extends [hybrid retrieval/reranking](weknora-hybrid-retrieval.md).
- Depends on [parsing and image extraction](weknora-document-ingestion.md).
- Distinct from the [wiki-page link graph](weknora-wiki-compilation.md), which represents page references rather than extracted document entities.

## Coverage limits

Selected graph service logic, type/limit symbols, embedding sanitization, and reranking exceptions were inspected. Neo4j query bodies, graph extraction, image enrichment/indexing, model adapters, image-keep bounds, and multimodal quality evaluations remain pending. No model, database, or image retrieval was run. See the [source map](weknora-source-map.md).

[^weknora]: Snapshot `fd7a2586fd5855fc4ded5c981a92dcb82a455246`: `internal/application/service/graph_search.go::graphSearchService.Search`; `internal/types/graph_search.go::GraphSearchTimeout`, `GraphSearchRequest.Normalize` and cap symbols; `internal/application/service/retriever/keywords_vector_hybrid_indexer.go::embeddingImagePayloadPatterns`, `sanitizeForEmbedding`; `internal/reranking/image.go::MinImageKeepScore`, `ImageKeepScoreFor`; `internal/reranking/rerank.go::Rerank`, `topByScore`, `keptImages`, `scoredCopy`. Package entry: [README](../raw/WeKnora/README.md), v0.8.3 “Multimodal Embedding,” “Image gallery,” and “Retrieval.”
