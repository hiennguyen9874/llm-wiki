---
type: Concept
title: txtai architecture and feature map
description: Overview of txtai’s embeddings database, pipelines, agents, workflows, serving interfaces, and pinned repository snapshot.
tags: [rag, txtai, architecture]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac498ccb
    title: txtai repository
---

**Observed:** txtai is a Python framework whose core `Embeddings` object combines configurable dense vector search, sparse scoring, relational content storage, and graph analysis. Pipelines, workflows, agents, and an optional FastAPI service compose these capabilities. **Synthesis:** the useful comparison boundary is an embeddable AI/retrieval framework with configurable serving, rather than a mandatory multi-service knowledge-management application.[^txtai-repo]

## Architecture and feature map

- [Architecture and technology stack](txtai-architecture.md) — composition, defaults, factories, public interfaces, and write ordering.
- [Hybrid retrieval and ranking](txtai-retrieval.md) — candidate generation, fusion, SQL search, and ranking constraints.
- [Persistence and index lifecycle](txtai-persistence.md) — content stores, serialization, mutations, archives, and cloud storage.
- [Graph retrieval and topics](txtai-graph.md) — inferred semantic edges, graph queries, topic analysis, and graph-RAG limits.
- [Extraction and multimodal pipelines](txtai-pipelines.md) — document conversion, segmentation, modality processing, and file/URL boundaries.
- [LLM and RAG generation](txtai-rag.md) — generation adapters, context construction, prompt contracts, and attribution.
- [Agents and workflow orchestration](txtai-agents-workflows.md) — smolagents processes, tools, skills, sessions, tasks, and scheduling.
- [API, clustering, and MCP](txtai-api.md) — service lifecycle, route gating, authentication, compatibility routes, and shard fan-out.
- [Security boundaries](txtai-security.md) — deployment-dependent authentication, execution, filesystem/network, and artifact trust.
- [Operations and testing](txtai-operations.md) — packaging, configuration, deployment, CI intent, and unexecuted validation.
- [Source map and coverage](txtai-source-map.md) — pinned identity, artifact ledger, exclusions, and unresolved evidence gaps.

This feature map is **synthesis of static inspection**, not proof that every optional backend or configuration combination works.[^txtai-repo]

## Identity and evidence

The canonical package is `raw/txtai/`, upstream `https://github.com/neuml/txtai`, pinned to `738aac498ccb` (commit timestamp 2026-10-22). The local package declares version `9.15.0`, Python ≥3.11, and Apache-2.0 licensing. `CITATION.cff` names David Mezzetti/NeuML; its 2020 release date is historical citation metadata, not the snapshot date.[^txtai-repo]

The README's “all-in-one” positioning, autonomy claims, and local/scale-out statements are **Reported**, not measurements. Its diagrams depict embeddings as a sparse/dense/database/graph union and documents → extraction/indexing → vector search → LLM → answer/citation; diagrams do not establish answer correctness, isolation, or production readiness.[^txtai-repo]

## Relationships

- **Uses:** [Embeddings architecture](txtai-architecture.md) as the shared retrieval substrate for [RAG](txtai-rag.md), [agents/workflows](txtai-agents-workflows.md), and [API serving](txtai-api.md).
- **Related (Synthesis):** [UltraRAG](ultrarag.md) is another orchestration framework in this wiki, but its inspected architecture organizes components as MCP servers; txtai's local composition does not require that process topology.
- **Related (Synthesis):** [RAG-Anything](rag-anything-architecture.md) illustrates a different boundary—multimodal orchestration delegated to LightRAG—rather than txtai's owned embeddings-database abstraction. These are navigation comparisons, not interoperability claims.

## Limits

Targeted static exploration by four Explore subagents and the curator; no txtai imports, application tests, models, services, builds, or benchmarks ran. All feature pages remain draft because optional-backend, test, example, and runtime coverage is incomplete. See the source map for the distinction between inspected content and syntax-only checks.

[^txtai-repo]: Revision `738aac498ccb`: `README.md` introduction, feature list, Agents, Retrieval augmented generation, Installation; `CITATION.cff` title/authors/license/date-released; `LICENSE` header; `setup.py::setup`, `src/python/txtai/version.py`; `src/python/txtai/__init__.py` exports; `src/python/txtai/embeddings/base.py::Embeddings`; `src/python/txtai/app/base.py::Application`; `docs/images/architecture.png` central embeddings block and `docs/images/rag.png` full left-to-right flow (visually inspected). Cross-platform relationships are synthesis from the linked wiki pages inspected in this session.
