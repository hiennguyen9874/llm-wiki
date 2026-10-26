---
type: Concept
title: UltraRAG retrieval and reranking
description: Embedding, index, web-search, and reranking backends behind UltraRAG's retrieval tools.
tags: [ml, ultrarag, retrieval, vector-search]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e2032d9f1
    title: UltraRAG repository
---

**Observed:** UltraRAG separates embedding generation, index storage/search, external web search, and reranking. Its MCP retrieval tools can build/search a local corpus, query a deployed retrieval service, or search the web. These are separate paths with different dependencies and persistence/network boundaries, not interchangeable implementations with established equal quality.[^ultrarag]

## Backend matrix

| Concern | Implementations in the snapshot |
| --- | --- |
| Embeddings/retrieval initialization | Infinity, Sentence Transformers, OpenAI, LiteLLM, BM25 |
| Dense index | FAISS, Milvus, Qdrant |
| Web search | Tavily, Exa, ZhipuAI, Serply |
| Reranking | Infinity, Sentence Transformers, OpenAI-compatible path |

The committed retrieval parameters select FAISS and Sentence Transformers with `openbmb/MiniCPM-Embedding-Light`; top-k is `5` and batch size is `16`. These are file defaults; pipeline parameter blocks can replace them. Embedding credentials can come from `RETRIEVER_API_KEY`; web providers have separate environment-variable/configuration channels.[^ultrarag]

## Data and service flow

1. Load a JSONL corpus with `contents` text; multimodal paths also require image information.
2. Initialize the selected backend, compute corpus embeddings, and build or open the selected index.
3. Search with queries/top-k and pass retrieved passages onward to prompt or reranker tools.
4. For API/deployed modes, send requests to configured external endpoints instead of assuming local in-process model/index execution.[^ultrarag]

The FAISS backend uses `IndexFlatIP` with `IndexIDMap2`, manages index files, and optionally uses GPU support, falling back to CPU when unavailable. **Synthesis:** inner-product ranking is cosine-equivalent only with normalized embeddings; the committed Sentence Transformers encode configuration disables normalization. Its search implementation filters invalid `-1` padding labels rather than interpreting them as Python negative indices; a regression test targets that failure mode. Milvus and Qdrant adapters provide separate collection/connection handling. Their existence does not establish availability of a running database or schema compatibility with an existing collection.[^ultrarag]

The separate retrieval service script exposes a FastAPI `/search` endpoint; the corresponding MCP tool calls a configured URL. The committed service default is port `64501`. Web search adapters return provider results through a common interface, but provider-specific options, retry behavior, credentials, billing, and output quality still differ. They project results to text and discard URLs/titles; terminal transient failures can yield empty lists, so “no passages” does not necessarily mean no search hits.[^ultrarag]

## Hybrid search and constraints

The `hybrid_search.yaml` example aliases the same retriever implementation as dense and BM25 servers and combines passages through custom tools. **Synthesis:** this demonstrates composition, not a universally optimal fusion strategy. Inspect per-alias parameter blocks and downstream merging when reproducing it.[^ultrarag]

**Observed:** demo-mode retrieval has additional Milvus/OpenAI assumptions; do not infer that a demo configuration runs under the default FAISS/local-embedding setup. GPU enablement is best-effort, and local model files, provider access, and database services are external prerequisites.[^ultrarag]

## Backend-specific pitfalls

- Non-demo Milvus indexing does not receive `contents` through the inspected `retriever_index` call path, whereas `MilvusIndexBackend.build_index` requires it. This is an **observed static incompatibility**, not a reproduced failure. Demo-mode behavior is a separate path.
- The file named `examples/demos/parameter/milvus_index_parameter.yaml` selects FAISS, despite its name. `examples/demos/qdrant_index.yaml` lacks the matching generated parameter/server companions. Do not choose a database backend from the filename alone.
- API embedding has a zero-vector fallback enabled in demo indexing; failed chunks can therefore become zero vectors rather than stopping the build.
- Reranking returns passage text and drops relevance scores across all three backends. Score fusion or thresholding needs a different interface.
- Project-memory search uses a collection name, but FAISS ignores that argument. **Synthesis:** default FAISS search is not a per-user collection-isolation mechanism; review [security boundaries](ultrarag-security.md) before multi-user use.[^ultrarag]

## Coverage and limits

Draft because backend internals and provider edge cases were selectively inspected rather than exhaustively audited. No corpus was embedded, no index was built, no search/reranker/provider request was run, and no retrieval latency/recall was measured. The exact return representation of the direct `bm25s.retrieve` path was not established by execution; do not treat it as a confirmed defect.[^ultrarag]

## Relationships

- **Depends on:** [corpus schemas](ultrarag-corpus.md).
- **Used by:** [research workflows](ultrarag-research-workflows.md) and [UI knowledge bases](ultrarag-ui.md).
- **Depends on:** [optional dependencies and services](ultrarag-deployment.md).

[^ultrarag]: Revision `185e2032d9f1`: `servers/retriever/parameter.yaml`; `servers/retriever/src/retriever.py::retriever_init`, `retriever_embed`, `retriever_index`, `retriever_search`, `retriever_deploy_search`, `retriever_websearch`, `bm25_index`, `bm25_search`; `servers/retriever/src/index_backends/{base,faiss_backend,milvus_backend,qdrant_backend}.py` backend classes, FAISS `search`/`_maybe_to_gpu`; `servers/retriever/src/websearch_backends/__init__.py` factory and provider adapter constructors; `servers/reranker/src/reranker.py::reranker_init`, `reranker_rerank`; `script/deploy_retriever_server.py` `/search` and CLI defaults; `tests/servers/retriever/test_faiss_search_padding.py`; `examples/experiments/hybrid_search.yaml` server aliases and pipeline; `examples/demos/parameter/milvus_index_parameter.yaml` `retriever.index_backend`; `examples/demos/qdrant_index.yaml` and companion-directory inventory; `retriever.py::_api_embed_texts`, `retriever_index`, `retriever_project_memory_search`; `MilvusIndexBackend.build_index`; `FaissIndexBackend.search`.
