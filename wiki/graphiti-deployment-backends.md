---
type: Concept
title: Graphiti deployment and graph backends
description: Supported graph databases and extras, driver-level connection configuration, Compose-based local setup, and the operational gaps Graphiti leaves to the integrator.
tags: [operations, rag, deployment, persistence]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
stale_after: 2027-01-24
sources:
  - id: graphiti-readme
    resource: ../raw/graphiti.md
    kind: documentation
    title: Graphiti README — A Framework for Building Temporal Knowledge Graphs (getzep/graphiti)
---

**Reported:** Graphiti runs as a Python ≥3.10 library over a bring-your-own graph database — Neo4j 5.26, FalkorDB 1.1.2, Amazon Neptune (with an OpenSearch Serverless collection for full-text search), or the deprecated Kuzu 0.11.2 — with backend chosen at install time through pip extras and at runtime through a driver object.[^graphiti-readme] **Synthesis:** deployment responsibility is inverted relative to a platform: Graphiti documents how to attach a database, not how to operate one — no migration, backup, high-availability, or orchestration guidance appears, and the vendor's stated production route is Zep rather than a self-managed Graphiti deployment.[^graphiti-readme]

## Requirements and install surface

- **Base:** Python 3.10 or higher and `pip install graphiti-core` (or `uv add`); an OpenAI API key is assumed because OpenAI is the default LLM and embedding provider.[^graphiti-readme]
- **Backend extras:** `graphiti-core[falkordb]`; `graphiti-core[falkordblite]` for the embedded variant (requires Python 3.12+); `graphiti-core[kuzu]`; `graphiti-core[neptune]`.[^graphiti-readme]
- **Provider extras:** `[anthropic]`, `[groq]`, `[google-genai]`, composable with backend extras in one install string.[^graphiti-readme]
- **Deprecation:** Kuzu is documented as deprecated and scheduled for removal because the upstream project is unmaintained; the driver still ships and emits a `DeprecationWarning`.[^graphiti-readme]

## Driver configuration

Database naming is driver state, not framework configuration. Neo4j defaults to database `neo4j` and FalkorDB to `default_db`, both hardcoded in their drivers; from v0.17.0 a driver instance can be constructed directly and passed as `graph_driver` to the `Graphiti` constructor, which is the documented way to set a custom database, host, or embedded FalkorDB Lite file.[^graphiti-readme]

| Driver | Documented constructor inputs |
| --- | --- |
| `Neo4jDriver` | `uri`, `user`, `password`, `database` |
| `FalkorDriver` | `host`, `port`, optional `username`/`password`, `database`, or an embedded `falkor_db` client |
| `NeptuneDriver` | `host`, `aoss_host`, optional `port` (default 8182) and `aoss_port` (default 443) |
| `KuzuDriver` | `db` path (deprecated) |

The README points contributors to a "Adding a graph driver" section for new backends, implying the driver interface is the extension seam.[^graphiti-readme]

## Local setup

Docker Compose starts the reference stack: `docker compose up` for Neo4j or `docker compose --profile falkordb up` for FalkorDB; a standalone FalkorDB container can be started with `docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest`, and Neo4j Desktop is suggested as the simplest Neo4j route.[^graphiti-readme] The reference MCP server can also be deployed with Docker alongside Neo4j.[^graphiti-readme] **Reported risk:** the example Compose files use default database credentials, which is part of the declared, intentionally unscoped reference-server security posture ([security boundaries](graphiti-security-telemetry.md)).[^graphiti-readme]

## Operational gaps

**Synthesis:** nothing in the capture covers schema migration between Graphiti versions, index or constraint rebuilds on backend change, backup and restore of a context graph, retention or compaction of superseded facts, capacity sizing, or telemetry-free offline operation beyond the opt-out flag. Neptune additionally makes full-text search an external managed dependency rather than a backend-internal capability.[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Hosts:** the [context graph model](graphiti-context-graph-model.md) and whatever [episode ingestion](graphiti-episode-ingestion.md) writes.
- **Constrains:** [retrieval and ranking](graphiti-retrieval.md), since hybrid search depends on the backend's keyword and vector capabilities.
- **Alternatives:** the managed route for the same graph model is Zep/Konig ([positioning](graphiti-positioning.md)).

## Evidence limits

**Reported only.** Version floors, extras, and constructor parameters come from README text and code samples; no package was installed, no container started, no database connected, and no custom database, embedded FalkorDB, or Neptune path was exercised. Feature parity across the four backends — especially keyword search and index behaviour — is not claimed by the README and is unverified here.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “Installation” (requirements list, FalkorDB/Kuzu/Neptune and provider extras, Neo4j Desktop tip, FalkorDB `docker run`), “Running with Docker Compose”, “Optional Environment Variables” → “Database Configuration” (driver constructors, Neo4j/FalkorDB defaults, v0.17.0 `graph_driver`, Neptune parameters), “Reference MCP and REST servers”, and “Zep vs Graphiti” (deployment row).
