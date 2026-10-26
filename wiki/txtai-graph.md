---
type: Concept
title: txtai semantic graph and topic analysis
description: Similarity-derived edges, explicit relationships, community topics, graph queries, and backend-specific lifecycle constraints.
tags: [rag, txtai, graph]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccbba7c4bff51886e660edd5241d04e
    title: txtai repository
---

**Observed:** txtai's optional graph combines index-position nodes, explicit relationships, and edges inferred by searching each node's text against the embeddings index. Community detection supplies topics, and openCypher-style queries can incorporate similarity matches. **Synthesis:** the default semantic graph is a model/configuration-dependent derived index, not inherently an LLM-extracted factual knowledge graph.[^txtai-repo]

## Construction and updates

Nodes use internal `indexid` values with original IDs/data and optional copied attributes. Manual `relationships` resolve external IDs to graph nodes; their default weight is 1. Inferred edges use similarity scores, skip self-loops, and require scores strictly above the configured threshold.[^txtai-repo]

**Observed defaults:** inference batch size **256**, search limit **15**, minimum score **0.1**, approximate mode **true**. Approximate mode skips nodes that already have edges; existing edge sets are therefore not guaranteed to be globally recomputed on each update. Scoring must be indexed before graph inference because the graph queries the same embeddings database. Changes to model, fusion, thresholds, or insertion/update sequence can affect graph shape.[^txtai-repo]

## Topics and analysis

The NetworkX backend supports Louvain, greedy, and label-propagation community detection. Louvain defaults include resolution 100 and level `best`; topic labels use term scoring (normally BM25, four terms), optionally followed by embedding-based category assignment. Unmatched members can be retained and ranked by centrality rather than simply dropped.[^txtai-repo]

Degree centrality, weighted PageRank, path queries, and graph filtering are available. The shortest-path helper transforms edge weights into distances and specially handles near-duplicate similarity. These are analysis conventions, not demonstrated factual importance or causal relationships.[^txtai-repo]

## Query and persistence boundaries

`Query.isquery` recognizes a batch as graph queries only when all members match its `MATCH … RETURN …` shape. GrandCypher executes the graph query. `similar(...)` can add match attributes and filter a subgraph before graph evaluation. Similarity-candidate pagination has score-order constraints; do not infer that every arbitrary graph ordering expands its candidate set correctly for SKIP.[^txtai-repo]

NetworkX persists nodes, edges, categories, and topics through serialization, with gated legacy pickle compatibility. The relational graph backend uses grand/SQLAlchemy and remote table state; `save` commits and `load` reconnects rather than exporting an interchangeable local graph artifact. **Observed:** relational `create` clears configured node/edge tables, while `load` reconnects without that deletion. It can also expose string node IDs where NetworkX uses integers.[^txtai-repo]

## Relationships and limits

- **Depends on:** [Retrieval scores](txtai-retrieval.md) as its inferred-edge oracle and [persistence](txtai-persistence.md) for backend lifecycle.
- **Can feed:** [RAG](txtai-rag.md) through an appropriate retrieval composition; graph storage alone is not proof every RAG request traverses the graph.
- **Part of:** [txtai architecture](txtai-architecture.md); see [source map](txtai-source-map.md).

Static code and sampled graph-test inspection only. Graph completeness, community quality, factual relation extraction, backend equivalence, practical scalability, and runtime correctness were not measured.

[^txtai-repo]: Revision `738aac498ccbba7c4bff51886e660edd5241d04e`: `src/python/txtai/graph/base.py::Graph.insert, resolverelations, inferedges, addbatch, addtopics, delete`; `graph/networkx.py::NetworkX.louvain, centrality, pagerank, showpath, distance, save, load`; `graph/topics.py::Topics.score`; `graph/query.py::Query.isquery, parse, build, filter`; `graph/rdbms.py::RDBMS.create, load, save, connect`; `graph/factory.py::GraphFactory`; `embeddings/search/base.py::Search.graphsearch`; `embeddings/base.py::Embeddings.index, batchsearch`; `docs/embeddings/configuration/graph.md`; `test/python/testgraph.py::testDatabase, testCommunityUnmatchedNodes, testSearchSkip, testUpsert` (sampled statically). Short module paths are relative to `src/python/txtai/`.
