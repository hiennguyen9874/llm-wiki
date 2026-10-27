---
type: Concept
title: "RAGFlow"
description: "Overview of RAGFlow\u2019s Go-based RAG platform, feature families, technology stack, and inspected source snapshot."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow

RAGFlow combines document parsing and chunk indexing, hybrid retrieval, chat and agent workflows, and structured knowledge compilation. **Observed:** this snapshot implements its active backend in Go and its browser application in React/TypeScript; this is not the older Python-server architecture often associated with the project. **Reported:** the README presents these facilities as an enterprise RAG/context engine; quality and scale claims were not benchmarked here.[^ragflow]

## Retrieval map

| Question | Concept |
| --- | --- |
| How do processes start and compose services? | [Server architecture](ragflow-architecture.md) |
| Where are metadata, files, vectors, tasks, and leases stored? | [Persistence and engines](ragflow-persistence.md) |
| How do files become indexed chunks? | [Document ingestion](ragflow-ingestion.md) |
| How are hybrid results selected and ranked? | [Retrieval and ranking](ragflow-retrieval.md) |
| How are reference markers attached to answers? | [Citation mechanisms](ragflow-citations.md) |
| How are wiki/graph/tree products compiled? | [Knowledge compilation](ragflow-knowledge-compilation.md) |
| Which runtime executes agent canvases? | [Agent workflows](ragflow-agent-workflows.md) |
| What is the separate harness library? | [Harness boundary](ragflow-harness.md) |
| What powers the browser and streaming UI? | [Frontend and API](ragflow-frontend.md) |
| How do external sources synchronize? | [Connectors](ragflow-connectors.md) |
| How are MCP requests served and external tools called? | [MCP boundaries](ragflow-mcp.md) |
| What security findings and permission limits matter? | [Security](ragflow-security.md) |
| What are the build, deployment, and test constraints? | [Operations](ragflow-operations.md) |
| What was inspected and what remains unknown? | [Source map](ragflow-source-map.md) |

## Technology stack

**Observed:** `go.mod` declares Go 1.27, Gin 1.12.0, CloudWeGo eino 0.10.0-alpha.33, Viper, GORM-related dependencies, NATS, Redis-compatible clients, ONNX Runtime bindings, and native PDF/Office libraries. `web/package.json` declares React 18.2, TypeScript, Vite, TanStack Query, Zustand, XYFlow, and Tailwind-based UI dependencies. Dependency declarations are not proof that every dependency is used in production.[^ragflow]

## Snapshot and trust boundary

The source is pinned to `1731e54b3aa0`; its repository license is Apache-2.0. The README's release examples and the frontend package version describe different version surfaces, so use the revision—not a guessed product release—as this ingest's identity. A committed private key and loader passphrase were found; the human authorized continuing, but their deployment use remains unknown. No values are compiled here.[^ragflow]

## Relationships

- **Uses:** [document ingestion](ragflow-ingestion.md), [hybrid retrieval](ragflow-retrieval.md), and [agent workflows](ragflow-agent-workflows.md); these are independently retrievable implementation subsystems.
- **Uses:** [source map](ragflow-source-map.md) for provenance, partial coverage, and future idempotent ingestion.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `README.md::What is RAGFlow? / Key Features / Local Deployment`; `LICENSE::Apache License Version 2.0`; `go.mod::module / go / require`; `web/package.json::version / dependencies / devDependencies`; `cmd/ragflow_server.go::main`; `internal/common/password.go::LoadPrivateKey`.
