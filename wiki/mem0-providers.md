---
type: Concept
title: Mem0 provider architecture
description: Factory-based LLM, embedding, vector-store, and reranking adapters and their optional capability boundaries.
tags: [agent-memory, mem0]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T17:08:00Z }
stale_after: 2027-02-06
sources:
  - id: mem0
    resource: ../raw/mem0/README.md
    scope: ../raw/mem0/
    kind: code
    revision: d16b8df
    title: Mem0 repository
---

**Observed:** Mem0 uses separate factories for LLM, embedding, vector-store and reranker adapters, with provider-specific dependencies in optional dependency groups. The base vector-store interface defines similarity-oriented scores and offers optional keyword search; implementations without it cannot supply that signal. Registry membership alone does not establish feature parity among providers.[^mem0]

The snapshot's OSS configuration has no external graph-store configuration; the entity collection supplies a distinct retrieval boost. Default library setup uses OpenAI services and a Qdrant vector store; verify credentials, model availability, embedding dimensions and provider behavior against the deployed revision.[^mem0]

See [retrieval](mem0-retrieval.md). Adapter internals and live service compatibility were not exhaustively audited or executed.

[^mem0]: Revision `d16b8df6`; `mem0/utils/factory.py::LlmFactory`, `EmbedderFactory`, `VectorStoreFactory`, `RerankerFactory`; `mem0/vector_stores/base.py::VectorStoreBase`; `mem0/configs/base.py::MemoryConfig`; `mem0/configs/vector_stores/qdrant.py::QdrantConfig`; `pyproject.toml::project.optional-dependencies`; `README.md::Basic Usage`.
