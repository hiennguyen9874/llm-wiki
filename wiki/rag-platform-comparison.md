---
type: Synthesis
title: OpenRAG, RAGFlow, WeKnora, LightRAG and txtai compared
description: Cross-platform synthesis of positioning, core-feature maturity, strengths, weaknesses and fit for five open-source RAG systems, derived from their static code-grounded wiki pages.
tags: [rag, comparison, synthesis]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:00:00Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d3ec10
    title: OpenRAG repository
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d5
    title: LightRAG repository
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccb
    title: txtai repository
---

**Synthesis:** the five systems sit at different layers. [RAGFlow](ragflow.md) and [WeKnora](weknora.md) are full multi-service knowledge platforms (Go backends, task queues, connectors, agents, compiled wiki products); [OpenRAG](openrag.md) is an assembly of Langflow, Docling and OpenSearch whose distinctive strength is ACL/DLS-aware enterprise retrieval; [LightRAG](lightrag.md) is a graph-plus-vector RAG engine with an optional server and unusually careful mutation/recovery machinery; [txtai](txtai.md) is an embeddable Python embeddings-database framework rather than a knowledge-management application. Every input page is a `draft` static inspection: nothing below is a measured quality, latency, or scale result, and "maturity" means depth of observed mechanism and safeguards, not verified behavior.[^openrag-repo][^ragflow][^weknora][^lightrag-aaebfe1][^txtai-repo]

## Positioning

| | OpenRAG | RAGFlow | WeKnora | LightRAG | txtai |
| --- | --- | --- | --- | --- | --- |
| Kind | Agentic RAG app over Langflow | Enterprise RAG/context platform | Knowledge platform (RAG + agent + auto-wiki) | Graph/vector RAG engine + server | Embeddable retrieval/AI framework |
| Backend | Python FastAPI | Go (Gin, eino) | Go (Gin, Dig, Asynq) + Python docreader | Python | Python |
| UI | Next.js | React | Vue | React WebUI | Not compiled |
| Licence / version | Apache-2.0, 0.5.0 | Apache-2.0, revision only | MIT, 0.8.3 | MIT, 1.5.8 | Apache-2.0, 9.15.0 |
| Mandatory infra | Langflow, Docling Serve, OpenSearch | MySQL, doc engine, object store, Kvrocks, NATS | PostgreSQL/ParadeDB + Redis (or Lite SQLite) | None (file defaults) | None |

## Core-feature maturity

Scale (Synthesis): **3** deep mechanism with explicit safeguards; **2** present with material limits; **1** basic or heuristic; **–** not compiled in this wiki (not proof of absence).

| Feature | OpenRAG | RAGFlow | WeKnora | LightRAG | txtai |
| --- | --- | --- | --- | --- | --- |
| Parsing/OCR | 2 | 3 | 2 | 2 | 2 |
| Chunking | 1 | 3 | 3 | 3 | 1 |
| Hybrid retrieval/fusion | 2 | 3 | 3 | 2 | 3 |
| Reranking | – | 3 | 3 | 1 | 2 |
| Knowledge graph | – | 2 | 2 | 3 | 2 |
| Citations | 1 | 2 | – | 1 | 1 |
| Agent runtime | 2 | 3 | 3 | – | 2 |
| Compiled wiki/knowledge | – | 3 | 3 | – | – |
| Connectors/sync | 2 | 3 | 2 | – | – |
| Multi-tenant authorization | 2 | 2 | 3 | 1 | 1 |
| API/SDK/MCP | 3 | 2 | 3 | 2 | 2 |
| Operability | 1 | 1 | 2 | 2 | 3 |

Basis per row:

- **Parsing/chunking.** RAGFlow runs a canvas pipeline with native DeepDoc PDF layout/OCR/table handling and page, hierarchy, table, QA, manual and title chunkers plus hidden parent chunks.[^ragflow] WeKnora validates adaptive chunk candidates before falling back, protects code/math/table spans and keeps parent–child sizes.[^weknora] LightRAG offers fixed/recursive/vector/paragraph/custom strategies frozen per document, with multimodal drawing/table/equation sidecars.[^lightrag-aaebfe1] OpenRAG uses Docling with 1,000-character/200-overlap defaults and OCR off; txtai leaves every splitter off by default.[^openrag-repo][^txtai-repo]
- **Retrieval and reranking.** WeKnora uses normalized weighted RRF (k=60, 0.7/0.3), rerank degradation, composite scoring and MMR, and preserves partial-engine results.[^weknora] RAGFlow combines synonym-expanded lexical queries, kNN, model or engine-specific reranking and parent promotion over six doc engines, with parity unestablished.[^ragflow] txtai selects log-odds, convex or RRF fusion by scoring flags; its `Reranker` is an optional pipeline.[^txtai-repo] OpenRAG applies OpenSearch boosts (0.7/0.3, not normalized), multiple embedding spaces, DLS-aware score filtering and keyword fallback.[^openrag-repo] LightRAG interleaves entity/relation branches round-robin without BM25, and its default server rerank binding is null, so no reranking runs by default.[^lightrag-aaebfe1]
- **Graph.** LightRAG's whole design is LLM entity/relation extraction, merge, summarization and recovery anchors.[^lightrag-aaebfe1] RAGFlow compiles hypergraph structure and RAPTOR trees; WeKnora's Neo4j GraphRAG revalidates cited chunks; txtai builds similarity-inferred graphs with topics and openCypher queries.[^ragflow][^weknora][^txtai-repo]
- **Citations.** RAGFlow has embedding-similarity insertion plus an agentic evidence registry.[^ragflow] OpenRAG and LightRAG rely on prompt instructions; txtai picks one post-hoc best-matching context.[^openrag-repo][^lightrag-aaebfe1][^txtai-repo] None validates entailment.
- **Agents and compiled knowledge.** WeKnora's ReAct engine has explicit loop, stall, overflow and steering guards, skills, sandboxes and cross-session memory; its automatic wiki has durable lanes, revisions and row-loss guards.[^weknora] RAGFlow's eino canvas has checkpoints, interrupts and loop/parallel nodes, plus wiki/structure/tree/mindmap compilation.[^ragflow] OpenRAG uses a 15-iteration Langflow agent; txtai delegates to smolagents.[^openrag-repo][^txtai-repo]
- **Connectors.** RAGFlow has checkpointed, fingerprint-skipping sync with leases and SSRF-pinned egress.[^ragflow] WeKnora defines resumable streaming and cursor-based deletion contracts, with provider bodies uninspected.[^weknora] OpenRAG propagates source ACLs into indexed chunks, but delta and deletion handling are unverified.[^openrag-repo]
- **Security.** WeKnora has four-role RBAC and deny-by-default API-key route policies.[^weknora] OpenRAG has DLS, but RBAC is off by default and gateway JWT signatures go unverified.[^openrag-repo] RAGFlow ships a committed key-and-passphrase pair (redacted) and credential defaults.[^ragflow] LightRAG is open by default with shared-credential auth and a flagged environment sample (redacted).[^lightrag-aaebfe1] txtai offers only a shared hashed token and runs trusted configuration as code.[^txtai-repo]
- **Operability.** txtai and LightRAG run without services. WeKnora adds a Lite SQLite edition. OpenRAG refuses more than one backend worker because its caches are process-local. RAGFlow needs CGO/native assets and five persistence planes.[^txtai-repo][^lightrag-aaebfe1][^weknora][^openrag-repo][^ragflow]

## Fit (Synthesis)

- Enterprise document Q&A with complex PDFs, agent canvases and source sync: RAGFlow, accepting heavy infrastructure and its security findings.
- Multi-workspace team knowledge base with agents, MCP/CLI clients and an auto-maintained wiki: WeKnora.
- Permission-propagating search over Drive/SharePoint/S3 on an OpenSearch stack: OpenRAG, after hardening auth defaults.
- Graph-centric or multi-hop exploration embedded in Python, or as a library under another platform: LightRAG.
- Building a custom pipeline, a local or offline semantic-search service, or a fusion experiment: txtai.

## Relationships

- **Uses:** each platform overview and its linked feature pages; see the per-feature basis above.
- **Related:** [Agent loop versus single-shot pipeline](agent-loop-vs-rag-pipeline.md) frames why the agent-runtime row matters for multi-hop questions; [grounded-accuracy evaluation](grounded-accuracy-evaluation.md) is the method needed to turn this maturity matrix into measured quality.

## Limits

Coverage is partial and uneven: targeted inspections covered roughly 276 of 1,574 OpenRAG paths, 241 of 5,482 RAGFlow paths, 230 of 5,664 WeKnora artifacts, and 302 of 658 txtai artifacts; LightRAG has a 1,331-file ledger. Scores are the curator's judgement over those pages. A dash means "not compiled", and unequal coverage can bias the scores. No platform was run, benchmarked or penetration-tested.[^openrag-repo][^ragflow][^weknora][^lightrag-aaebfe1][^txtai-repo]

[^openrag-repo]: Revision `6fc819d3ec10`, via compiled pages [overview](openrag.md), [ingestion](openrag-document-ingestion.md) (`flows/ingestion_flow.json`), [hybrid retrieval](openrag-hybrid-retrieval.md) (`src/services/search_service.py::_search`), [chat](openrag-chat-streaming.md) (`flows/openrag_agent.json`), [connectors](openrag-connectors.md), [auth/security](openrag-auth-security.md) (`rbac_service.py::is_rbac_enforced`), [backend architecture](openrag-backend-architecture.md) (worker/cache startup guard), [public API](openrag-public-api.md), [MCP](openrag-mcp.md), [source map](openrag-source-map.md).
[^ragflow]: Revision `1731e54b3aa0`, via [overview](ragflow.md), [ingestion](ragflow-ingestion.md) (`internal/ingestion/pipeline`), [retrieval](ragflow-retrieval.md) (`internal/service/nlp/retrieval.go::Retrieval`), [citations](ragflow-citations.md), [agent workflows](ragflow-agent-workflows.md), [knowledge compilation](ragflow-knowledge-compilation.md), [connectors](ragflow-connectors.md), [persistence](ragflow-persistence.md), [security](ragflow-security.md), [operations](ragflow-operations.md), [source map](ragflow-source-map.md).
[^weknora]: Revision `fd7a2586fd58`, via [overview](weknora.md), [ingestion](weknora-document-ingestion.md) (`chunker/strategy.go`), [hybrid retrieval](weknora-hybrid-retrieval.md) (`knowledgebase_search_fusion.go::fuseWithRRF`), [graph/multimodal](weknora-graph-multimodal-retrieval.md), [agent runtime](weknora-agent-runtime.md) (`internal/agent/engine.go`), [wiki compilation](weknora-wiki-compilation.md), [memory](weknora-memory.md), [datasource sync](weknora-datasource-sync.md), [security](weknora-security.md), [deployment](weknora-deployment.md), [MCP](weknora-mcp-servers.md), [source map](weknora-source-map.md).
[^lightrag-aaebfe1]: Revision `aaebfe1bb8d5`, via [overview](lightrag.md), [ingestion](lightrag-ingestion.md), [chunking](lightrag-chunking.md), [parsing/multimodal](lightrag-parsing-multimodal.md), [KG extraction](lightrag-extraction.md) (`operate.py::merge_nodes_and_edges`), [retrieval](lightrag-retrieval.md) (`operate.py::_perform_kg_search`, rerank binding default), [query contracts](lightrag-query-contracts.md), [storage](lightrag-storage.md), [deletion](lightrag-deletion.md), [security](lightrag-security.md), [source map](lightrag-source-map.md).
[^txtai-repo]: Revision `738aac498ccb`, via [overview](txtai.md), [architecture](txtai-architecture.md), [retrieval](txtai-retrieval.md) (`embeddings/search/hybrid.py::Hybrid`), [pipelines](txtai-pipelines.md) (`segmentation.py`), [RAG](txtai-rag.md) (`rag.py::reference`), [graph](txtai-graph.md), [agents/workflows](txtai-agents-workflows.md), [security](txtai-security.md) (`api/authorization.py`), [operations](txtai-operations.md), [source map](txtai-source-map.md).
