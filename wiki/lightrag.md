---
type: Concept
title: LightRAG
description: Code-grounded overview of LightRAG's graph/vector RAG engine, integrated multimodal pipeline, service surfaces, and inspected source snapshot.
tags: [rag, platform, overview]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:08:00Z }
stale_after: 2027-01-24
sources:
  - id: lightrag-aaebfe1
    resource: ../raw/LightRAG/README.md
    scope: ../raw/LightRAG/
    kind: code
    revision: aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a
    title: LightRAG repository
---

**Observed:** LightRAG is a Python RAG engine that compiles text into chunks, entity/relation descriptions and graph/vector indexes, then retrieves graph-oriented and direct-vector context for model generation. This pinned 1.5.8 snapshot also integrates parser routing and image/table/equation analysis, a FastAPI service, dual-entry React WebUI, storage adapters and recovery tooling. **Synthesis:** its distinguishing engineering questions are graph-to-source provenance, cross-store mutation/recovery, and context assembly—not an independently verified promise of better answer quality or lower cost.[^lightrag-aaebfe1]

## Retrieval map

| Question | Concept |
| --- | --- |
| How is the engine composed? | [Architecture and stack](lightrag-architecture.md) |
| What happens after upload/enqueue? | [Document ingestion](lightrag-ingestion.md) |
| How are files and multimodal artifacts handled? | [Parsing and multimodal analysis](lightrag-parsing-multimodal.md) |
| Which chunking algorithms and fallbacks exist? | [Chunking](lightrag-chunking.md) |
| How does the graph get compiled? | [KG extraction and merge](lightrag-extraction.md) |
| How can contributions be deleted or recovered? | [Deletion and recovery](lightrag-deletion.md) |
| What do local/global/hybrid/mix/naive mean? | [Retrieval and ranking](lightrag-retrieval.md) |
| Are references validated, streamed and cached? | [Query contracts](lightrag-query-contracts.md) |
| How are models and providers separated? | [Model roles](lightrag-models.md) |
| Where is data isolated/persisted? | [Storage](lightrag-storage.md) and [concurrency/durability](lightrag-concurrency.md) |
| How can embeddings change? | [Embedding compatibility/recovery](lightrag-embedding-recovery.md) |
| What can clients access? | [API and WebUI](lightrag-api-ui.md) |
| What must be protected? | [Authentication/security](lightrag-security.md) |
| How is it built and deployed? | [Packaging/configuration/deployment](lightrag-deployment.md) |
| What checks and benchmarks are actually established? | [Testing/evaluation limits](lightrag-testing.md) |
| What was read and what remains unknown? | [Source map](lightrag-source-map.md) |

## Snapshot and consequential cautions

- **Observed:** HKUDS LightRAG revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`, committed 2026-10-14; core version 1.5.8, API version 0347; Python ≥3.10; MIT.
- **Observed:** default retrieval is mix; default stores are RAM-resident with local persistence. **Reported:** those stores are for small-scale testing/evaluation, not production.
- **Observed:** authentication is unconfigured by default and the default Ollama whitelist stays open even when other authentication is enabled. The inspected API uses shared credential authorization, not per-document user permissions.
- **Observed reviewer finding:** a tracked compose environment sample contains likely live provider/service-key material. Values are withheld; human permission to continue redacted compilation does not establish credential remediation.
- **Observed:** destructive and recovery tooling exists, including vector-only rebuild; the README's no-reembedding-tool statement conflicts with implemented tooling.
- **Reproduced, syntax only:** all 818 tracked Python files parsed under Python 3.12.3/Linux. No upstream test, model, service, build, database migration or benchmark ran.[^lightrag-aaebfe1]

## Relationships

- **Related:** [RAG-Anything architecture](rag-anything-architecture.md) is a separate pinned multimodal library relying on LightRAG internals. The README reports upstream integration, but neither source review proves the two snapshots are compatible or that the standalone package is superseded.
- **Uses:** [Source map](lightrag-source-map.md) for coverage, trust and idempotent follow-up.
- **Contrasts with:** [Graphiti's context graph model](graphiti-context-graph-model.md): per this overview LightRAG compiles entity/relation descriptions into graph and vector indexes for retrieval, whereas Graphiti's documentation describes LLM-extracted facts that carry validity windows and episode provenance.

## Evidence limits

All pages remain draft because intended broad repository coverage is incomplete. Static observation is not production verification, a security certification, or a reproduced research result. External parser services, database/model implementations and linked paper/dataset artifacts were not fetched or executed.[^lightrag-aaebfe1]

[^lightrag-aaebfe1]: Revision `aaebfe1bb8d55deb6a4304d357a3bf4c92fcd40a`: README “About LightRAG”, feature/configuration/tool sections and related-project news; `lightrag/_version.py::__version__, __api_version__`; `pyproject.toml` project metadata; `LICENSE`; `lightrag/lightrag.py::LightRAG`; `operate.py::kg_query, naive_query, extract_entities, merge_nodes_and_edges`; `pipeline.py::_PipelineMixin`; `llm_roles.py::ROLES`; `api/config.py` defaults and `api/utils_api.py::get_combined_auth_dependency`; `tools/rebuild_vdb.py`; `env.docker-compose-full` key-presence review (values withheld). Revision/date from read-only Git inspection; executed syntax-only method and scope recorded in [testing limits](lightrag-testing.md).
