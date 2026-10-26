---
type: Concept
title: WeKnora knowledge framework
description: Code-grounded overview and navigation for WeKnora's shared RAG, agent, automatic wiki, and integration platform.
tags: [ml, weknora, rag, knowledge-systems]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora is Tencent's open-source knowledge framework combining retrieval-augmented Q&A, multi-step agents, and automatic wiki generation over shared knowledge bases. **Reported:** the README positions it for enterprise document understanding and private deployment. **Observed/Synthesis:** the inspected code organizes these capabilities around a Go service, shared tenant-scoped persistence and asynchronous pipelines, with a Vue UI and optional parsing, model, vector, graph, storage, and sandbox services.[^weknora]

## Snapshot and trust

This compilation describes version-file value **0.8.3**, inspected on **2026-10-26** at commit `fd7a2586fd58`. The source checkout had one pre-existing tracked modification: `.gitignore` adds `.pi/`. That non-product change was not normalized or reverted. No upstream code, tests, services, migrations, or model calls were executed.[^weknora]

**Observed license:** WeKnora's own code is MIT, with separate third-party obligations. `THIRD_PARTY_NOTICES.md` explicitly says MIT does not replace component licenses and describes required notice/source bundles. This is source identification, not a complete redistribution/license audit.[^weknora]

## Capability map

The following links are this ingest's maintained synthesis boundaries, grounded in the corresponding source families rather than copied release marketing:[^weknora]

| Question | Maintained concept |
| --- | --- |
| How is the application assembled, and what is the stack? | [Backend architecture](weknora-backend-architecture.md) |
| What data is persisted and scoped to a workspace? | [Persistence and migrations](weknora-persistence.md) |
| How does work run asynchronously? | [Task queues](weknora-task-queues.md) |
| How do documents become indexing inputs? | [Parsing and chunking](weknora-document-ingestion.md) |
| How do external sources synchronize? | [Datasource sync](weknora-datasource-sync.md) |
| How are candidates fused and reranked? | [Hybrid retrieval](weknora-hybrid-retrieval.md) |
| What differs for graphs and images? | [Graph and multimodal retrieval](weknora-graph-multimodal-retrieval.md) |
| How does an agent turn stop, recover, or accept steering? | [Agent runtime](weknora-agent-runtime.md) |
| How are instructions and executable work isolated? | [Skills and sandboxes](weknora-skills-sandboxes.md) |
| How do documents become interlinked revisioned pages? | [Wiki compilation](weknora-wiki-compilation.md) |
| What survives across conversations? | [Memory](weknora-memory.md) |
| How does the UI reconstruct live responses? | [Frontend streaming](weknora-frontend-streaming.md) |
| How do programs and coding agents connect? | [CLI/SDK](weknora-cli-sdk.md), [MCP](weknora-mcp-servers.md), [publishing channels](weknora-publishing-channels.md) |
| What must an operator configure and protect? | [Deployment](weknora-deployment.md), [configuration](weknora-configuration.md), [security](weknora-security.md) |

## Relationships

- Uses one shared knowledge pipeline for RAG, agent access, and wiki generation; the architecture SVG explicitly connects all three modes to the same knowledge bases.[^weknora]
- Depends on edition-specific infrastructure: standard deployments use external database/queue services, while Lite substitutes local implementations. See [deployment](weknora-deployment.md).
- Audited by the [source coverage map](weknora-source-map.md), which records inspected sections, exclusions, unresolved drift, and pending artifacts.

## Coverage limits

All pages are **draft**, reflecting a bounded static reconnaissance rather than a complete code audit. Detailed provider adapters, connectors, parsers, migrations, platform-specific behavior, and runtime quality remain partly or wholly unreviewed. Backend counts and performance claims are not treated as verified compatibility or benchmark evidence.[^weknora]

[^weknora]: Snapshot `fd7a2586fd58`: [README](../raw/WeKnora/README.md), “Overview,” “Architecture,” “Features,” “Clients and Integrations,” and “Other ways to deploy”; `VERSION`; `LICENSE`, opening MIT terms; `THIRD_PARTY_NOTICES.md`, introductory redistribution requirements and component sections; `docs/images/readme/architecture-en-light.svg`, access/app/services/storage panels and shared-knowledge-bases caption (SVG source inspected, not visually rendered); `cmd/server/main.go::main`; `internal/container/container.go::BuildContainer`; source checkout `git status --short` and `.gitignore` diff inspected during this operation.
