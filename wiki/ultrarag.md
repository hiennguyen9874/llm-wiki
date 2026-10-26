---
type: Concept
title: UltraRAG architecture and feature map
description: MCP-based RAG framework with YAML orchestration, modular servers, and a visual development UI.
tags: [ml, ultrarag, rag, architecture]
status: stable
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

UltraRAG separates RAG components into MCP servers and orchestrates them through a YAML-driven client. **Observed:** the package exposes a CLI, a Python calling API, and a UI adapter around the pipeline engine. **Reported:** its authors position it for research and industrial prototyping; the README's “first” and performance/productivity language is promotional, not independently established here.[^ultrarag]

## Architecture

| Layer | Responsibility | Main implementation |
| --- | --- | --- |
| Interfaces | CLI commands; Python tool/pipeline calls; visual builder and chat | `src/ultrarag/client.py::main`, `src/ultrarag/api.py`, `ui/backend/pipeline_manager.py` |
| Orchestration | Compile server metadata, resolve variables, execute sequences/loops/branches, emit progress | `client.py::build`, `UltraData`, `load_pipeline_context`, `execute_pipeline` |
| Execution | Independently registered MCP tools and prompts | `src/ultrarag/server.py::UltraRAG_MCP_Server`; `servers/*/src/` |

**Observed:** local CLI servers are subprocesses using `sys.executable` and inherited environment; remote endpoints are bridged through `npx -y mcp-remote`, with a Node.js ≥20 check. This is component/process separation, not a sandbox for untrusted code. The Python `initialize()` path still launches bare `python`, unlike the CLI, so interpreter selection differs between interfaces.[^ultrarag]

## Feature map

- [Pipeline DSL and configuration](ultrarag-pipelines.md): variable wiring, loops, branches, generated metadata, and extension contracts.
- [Retrieval and reranking](ultrarag-retrieval.md): dense/BM25 retrieval, FAISS/Milvus/Qdrant, web search, and reranking.
- [Generation backends](ultrarag-generation.md): local and API inference, multimodal and conversational calls.
- [Corpus processing](ultrarag-corpus.md): document parsing, JSONL corpus production, and chunking.
- [Research workflows and prompts](ultrarag-research-workflows.md): reusable reasoning pipelines, citation transforms, routers, and persistent memory.
- [Benchmarking and evaluation](ultrarag-evaluation.md): aligned dataset loading and answer/retrieval metrics.
- [UI and persistence](ultrarag-ui.md): builder, chat, knowledge bases, streaming, and filesystem stores.
- [Installation and deployment](ultrarag-deployment.md): Python/frontend stack, optional dependencies, Docker, and CI.
- [Security and operational limits](ultrarag-security.md): credential channels, execution boundaries, and deployment caveats.

The feature map is **synthesis** of static implementation inspection, not proof that every combination works. See the [source coverage ledger](ultrarag-source-map.md) for inspected versus sampled artifacts and unavailable runtime evidence.[^ultrarag]

## Identity and limits

The README identifies THUNLP, NEUIR, OpenBMB, and AI9stars as collaborators and links upstream `https://github.com/OpenBMB/UltraRAG`. The inspected package version is `0.3.0.2`, and the local license is Apache-2.0. These pages describe commit `185e2032d9f1`, not the moving upstream branch. No framework services, model inference, benchmarks, or repository tests were executed.[^ultrarag]

## Relationships

- **Uses:** [YAML pipeline orchestration](ultrarag-pipelines.md) to compose [retrieval](ultrarag-retrieval.md) with [generation](ultrarag-generation.md).
- **Uses:** [UI](ultrarag-ui.md) as another adapter to the shared engine rather than an independent RAG runtime.

[^ultrarag]: Inspected revision `185e2032d9f1`: `README.md` §§ About UltraRAG, UltraRAG UI; `pyproject.toml` `[project]`, `[project.scripts]`; `LICENSE.txt` heading; `src/ultrarag/client.py::local_server_launch_config`, `remote_server_launch_config`, `build`, `execute_pipeline`; `src/ultrarag/mcp_exceptions.py::check_node_version`; `src/ultrarag/api.py::initialize`, `PipelineCall`; `ui/backend/pipeline_manager.py` imports of the client engine.
