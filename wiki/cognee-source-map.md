---
type: SourceMap
title: Cognee source map and coverage limits
description: Coverage ledger, static-inspection boundaries, and pending work for the Cognee repository snapshot.
tags: [agent-memory, cognee, provenance]
status: draft
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: '2026-11-06T17:06:51Z' }
sources:
  - id: cognee
    resource: ../raw/cognee/README.md
    scope: ../raw/cognee/
    kind: code
    revision: 525b1d1
    title: Cognee repository
---

This ledger identifies the Cognee snapshot compiled into the wiki and records incomplete coverage. **Observed:** `pyproject.toml` identifies the package and `README.md` is its entry point; the repository revision is pinned in the source metadata. Four parallel static reviews and curator spot checks informed this ingestion; no source code, tests, services, models, or benchmarks were run.[^cognee]

## Coverage ledger

- **Inspected:** `README.md`, `pyproject.toml`, `docs/recall-vs-search.md`; representative `cognee/api/v1/` remember, add, cognify, recall, search, improve, forget and routing modules; `cognee/modules/` cognify, search, retrieval, improve, pipeline and session-lifecycle modules; code-graph tasks; database, cache, file-storage and auth configuration; `cognee-mcp/src/server.py`; BEAM report. Details and locators appear in the linked concepts.[^cognee]
- **Partially inspected:** database adapter internals, API routers, MCP and CLI implementation, deployment definitions, tests, CI configuration, LoCoMo and archived evaluations. Findings not substantiated in linked concepts remain pending; test existence is not a passing test result.[^cognee]
- **Pending:** comprehensive imports and dependency closure across the large repository, frontend, connectors, integrations, migrations, examples, notebooks, benchmarks and their full artifact sets, all runtime behavior, and external websites, models and services. Future ingestion must reconcile this ledger rather than assume complete coverage.[^cognee]
- **Excluded:** logo and demo media are decorative to this synthesis; lockfile and generated artifacts are not exhaustively analyzed; cached, binary and vendored content was not treated as primary implementation evidence. Some excluded trees were only enumerated, not completely inventoried.[^cognee]
- **Safety:** repository data was handled read-only. Pattern-based secret screening by reviewers is not proof that the entire package is free of sensitive material; no credential values are compiled. No deployment's privacy or security properties were independently tested.

## Relationships

- **Covers:** [Overview](cognee-overview.md), [ingestion](cognee-ingestion-and-code-graphs.md), [retrieval](cognee-retrieval.md), [sessions](cognee-sessions-and-improvement.md), [security](cognee-storage-and-security.md), [interfaces](cognee-interfaces-and-deployment.md), and [benchmarks](cognee-benchmarks.md).

[^cognee]: Revision `525b1d1`, `README.md::Choose your starting point`, `pyproject.toml::[project]`, `cognee/modules/cognify/memory_pipelines.py::run_memory_pipelines`, `cognee/api/v1/recall/query_router.py::_RULES`, `cognee/modules/improve/registry.py::DEFAULT_STAGES`, `cognee/eval_framework/beam/REPORT.md::1. Introduction`.
