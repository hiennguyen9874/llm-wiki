---
type: Concept
title: "OpenRAG"
description: "Overview and navigation for OpenRAG's agentic RAG platform, implementation boundaries, and inspected repository snapshot."
tags: [ml, openrag, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:56:21Z }
stale_after: 2027-01-24
sources:
  - id: openrag-repo
    resource: ../raw/openrag/README.md
    scope: ../raw/openrag/
    kind: code
    revision: 6fc819d
    title: OpenRAG repository
---

OpenRAG combines a browser workspace, Python API, Langflow orchestration, Docling parsing, and OpenSearch-backed document retrieval. **Observed:** these components and their wiring exist in the inspected snapshot. **Reported:** the README describes enterprise-scale search, re-ranking, and multi-agent coordination; those marketing claims are not established as measured capabilities by this ingest.[^openrag-repo]

## Snapshot and technology

- Upstream: `langflow-ai/openrag`; package version `0.5.0`; Apache-2.0 license, with an IBM copyright notice. Snapshot commit: `6fc819d`, committed 2026-10-23.[^openrag-repo]
- Backend: Python ≥3.13, FastAPI/Starlette/Uvicorn, SQLModel/SQLAlchemy/Alembic, OpenSearch client, LiteLLM, FastMCP, and a Textual terminal launcher. These are declared requirements, not a resolved-environment compatibility guarantee.[^openrag-repo]
- Frontend: Next.js 16, React 19, TypeScript, Tailwind 4, TanStack Query, Zustand, Radix, and AG Grid. Langflow and Docling Serve are separate runtime services in the application topology.[^openrag-repo]

## Retrieval map

| Question | Maintained concept |
| --- | --- |
| How is the backend composed and where is state stored? | [Backend architecture](openrag-backend-architecture.md) |
| Which identities and trust boundaries matter? | [Authentication and security](openrag-auth-security.md) |
| How do files become indexed chunks? | [Document ingestion](openrag-document-ingestion.md) |
| How do vector and keyword search interact? | [Hybrid retrieval](openrag-hybrid-retrieval.md) |
| How are visual flows provisioned and customized? | [Langflow workflows](openrag-langflow-workflows.md) |
| How do chat, streaming, IDs, and nudges work? | [Chat and streaming](openrag-chat-streaming.md) |
| How are external document sources connected? | [Connectors and ACL propagation](openrag-connectors.md) |
| What does the browser implement? | [Frontend](openrag-frontend.md) |
| How should applications integrate? | [Public API](openrag-public-api.md), [SDKs](openrag-sdks.md), [MCP](openrag-mcp.md) |
| How is it run and tested? | [Deployment](openrag-deployment.md), [Testing and checks](openrag-testing.md) |
| What was actually inspected? | [Source map](openrag-source-map.md) |

## Evidence limits

This is a code-grounded, targeted static ingest, not an exhaustive audit, performance evaluation, or deployment certification. All concepts remain draft because material implementation/test/attachment coverage is outstanding; see the source map before treating a missing feature as absent. No vendor API calls, application execution, migrations, builds, or application tests were performed.

[^openrag-repo]: `6fc819d`: `README.md` §§ Highlight Features, SDKs, Model Context Protocol; `pyproject.toml` `[project]`, dependencies, `[project.scripts]`; `LICENSE` title and appendix; `frontend/package.json::dependencies`; `docker-compose.yml::services`. Local repository identity and clean working-tree state were inspected with Git.
