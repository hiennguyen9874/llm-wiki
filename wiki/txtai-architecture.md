---
type: Concept
title: txtai architecture and technology stack
description: Factory-based composition, component defaults, write ordering, public interfaces, and optional technology dependencies.
tags: [rag, txtai, architecture]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:18:00Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccbba7c4bff51886e660edd5241d04e
    title: txtai repository
---

**Observed:** txtai composes an embeddings database from independently configurable dense ANN, sparse scoring, relational content, and graph components. `Embeddings` owns the indexing/query lifecycle; `Application` composes embeddings with pipelines, agents, and workflows from configuration. **Synthesis:** factories and optional dependencies, rather than mandatory external services, define most architectural boundaries.[^txtai-repo]

## Core components and defaults

| Component | Mechanism and default |
| --- | --- |
| Dense vectors | `VectorsFactory` selects a model adapter; empty/default-enabled embeddings configuration selects `sentence-transformers/all-MiniLM-L6-v2` |
| ANN | `ANNFactory` selects a backend; Faiss by default when importable, otherwise NumPy |
| Sparse scoring | `ScoringFactory` supports keyword/neural sparse scoring as well as term-weighting uses; sparse search is conditional, not always enabled |
| Content database | Absent unless `content` is enabled; SQLite is the default content backend, with DuckDB and client/custom alternatives |
| Graph | Optional `GraphFactory` component; NetworkX or relational implementations |
| Subindexes | Child `Embeddings` instances wrapped by `Indexes`, sharing a model cache |

These are **Observed configuration/implementation defaults**, not a claim that model assets are bundled or every backend is installed. Factories accept resolvable custom classes, so configuration is a trusted extension boundary.[^txtai-repo]

## Write and query flow

**Observed:** `index` initializes components, transforms/streams documents into a temporary NumPy memmap, creates vectors, optionally applies dimensionality reduction, writes ANN data, indexes scoring, indexes children, and finally indexes the graph. The scoring-before-graph order is explicit: semantic edge inference searches the same embeddings index. `upsert` reuses the transformation path with an upsert action. This does not establish a transaction spanning all components.[^txtai-repo]

**Observed:** `search` delegates through `batchsearch` to `Search`: graph-query recognition, database-backed query handling, or plain index search. Hybrid retrieval, SQL similarity clauses, and graph execution are separate mechanisms over the same underlying components; see their dedicated pages.[^txtai-repo]

## Interfaces and technology stack

- **Observed:** top-level Python exports include `Agent`, `Application`, `Embeddings`, `LLM`, `RAG`, `Textractor`, and `Workflow`. The console is a separate interactive entry point.
- **Observed:** `Application` accepts a mapping, YAML text, or a path. It resolves dependent pipelines after the initial pipeline pass; a FastAPI adapter adds HTTP/OpenAI-compatible/MCP surfaces. This repository does not require a first-party browser application for local Python use.
- **Observed:** package `txtai` version `9.15.0` requires Python ≥3.11. Declared default dependencies include Faiss CPU, Hugging Face Hub, MessagePack, NumPy, regex, PyYAML, safetensors, tqdm, PyTorch ≥2.4, and Transformers ≥5.9.0; installability was not verified. Sentence Transformers, ONNX, llama.cpp, LiteLLM, LiteRT, Model2Vec, additional ANN/database/graph backends, FastAPI/Uvicorn, and smolagents are available through optional feature dependencies/adapters, not all mandatory default-install components.
- **Reported:** README links JavaScript, Java, Rust, and Go bindings. Those separate repositories were not inspected.[^txtai-repo]

## Relationships

- **Uses:** [Retrieval and ranking](txtai-retrieval.md), [persistence](txtai-persistence.md), and [graph analysis](txtai-graph.md) as distinct parts of the embeddings abstraction.
- **Used by:** [Pipelines](txtai-pipelines.md), [RAG](txtai-rag.md), [agents/workflows](txtai-agents-workflows.md), and [API serving](txtai-api.md).
- **Depends on:** [Operations](txtai-operations.md) for optional dependency selection and [security boundaries](txtai-security.md) for trusted configuration and artifact handling.
- **Part of:** [txtai overview](txtai.md).

## Limits

Static inspection only. No index was built and no optional backend was exercised; compatibility, recall, throughput, atomicity under failure, and practical read/write concurrency remain unverified. The [source map](txtai-source-map.md) records targeted and pending coverage.

[^txtai-repo]: Revision `738aac498ccbba7c4bff51886e660edd5241d04e`: `src/python/txtai/embeddings/base.py::Embeddings.__init__, configure, defaults, defaultsparse, createann, createdatabase, creategraph, createindexes, createscoring, index, upsert, search, batchsearch`; `embeddings/index/transform.py::Transform`, `embeddings/index/stream.py::Stream`, `embeddings/index/indexes.py::Indexes`; `embeddings/search/base.py::Search.__call__`; `ann/dense/factory.py::ANNFactory.create`; `database/factory.py::DatabaseFactory.create`; `scoring/factory.py::ScoringFactory.create, issparse`; `graph/factory.py::GraphFactory.create`; `vectors/dense/factory.py::VectorsFactory.create`; `graph/base.py::Graph.index, inferedges`; `src/python/txtai/app/base.py::Application.read, createpipelines`; `src/python/txtai/__init__.py` exports; `setup.py` dependencies/extras and `setup`; `src/python/txtai/version.py`; `README.md` feature list. Short module paths after the first source prefix are relative to `src/python/txtai/`.
