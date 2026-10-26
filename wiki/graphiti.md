---
type: Concept
title: Graphiti
description: README-grounded overview of Graphiti's temporal context-graph framework, its episode provenance, hybrid retrieval, backend and provider matrix, and snapshot limits.
tags: [rag, platform, overview, knowledge-graph]
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

**Reported:** Graphiti is an open-source Python framework that compiles incoming data ("episodes") into a temporal context graph of entities and time-bounded facts, then serves hybrid retrieval over that graph. It is a library rather than a service: the caller supplies the graph database, LLM, and embedder, and builds ingestion, tenancy, access control, and operations around it; Zep is presented as the packaged platform built on the same framework.[^graphiti-readme] **Synthesis:** within this wiki, Graphiti is the reference case for *fact invalidation with per-episode provenance* — knowledge modelled as versioned claims rather than as a retrieval index over document chunks.[^graphiti-readme]

## Retrieval map

| Question | Concept |
| --- | --- |
| What is a context graph made of, and how do facts expire? | [Context graph data model](graphiti-context-graph-model.md) |
| How does an episode become graph facts? | [Episode ingestion](graphiti-episode-ingestion.md) |
| How are LLMs, embedders, rerankers, and dedupe models configured? | [Model and provider configuration](graphiti-model-providers.md) |
| Which graph databases work, and how is it installed? | [Deployment and graph backends](graphiti-deployment-backends.md) |
| How is the graph queried and ranked? | [Retrieval and ranking](graphiti-retrieval.md) |
| How does it compare with Zep and GraphRAG? | [Positioning versus Zep and GraphRAG](graphiti-positioning.md) |
| What do the reference servers expose, and what telemetry leaves the host? | [Security boundaries and telemetry](graphiti-security-telemetry.md) |

## Snapshot and coverage

- **Observed:** the source is a single documentation artifact, `raw/graphiti.md` — the getzep/graphiti README (881 lines, 18 level-2 sections, 19 level-3 sections), captured 2026-10-26 with content fingerprint `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`.
- **Limit:** the capture carries no commit, release tag, or license statement. The only version reference is "As of v0.17.0" in the database-configuration section, so backend, provider, and model names below should be re-checked before use.
- **Observed coverage:** all sections of the README were read statically. Not fetched or inspected: the arXiv paper (2501.13956), help.getzep.com guides, `examples/` (quickstart, Azure, Jev, OpenAI Decisions), `mcp_server/`, `server/`, `SECURITY.md`, `CONTRIBUTING.md`, and the hotlinked logo/GIF/privacy-screen assets.
- **Reproduced: nothing.** No package was installed, no code was read or executed, and no database, LLM call, benchmark, or security test ran. Every quantitative claim (for example the reported "sub-200ms" Zep retrieval and "typically sub-second" Graphiti latency) is **Reported** vendor material, not a measurement.
- **Packaging note:** because the whole source is one README, this ingest keeps coverage limits on the concepts themselves instead of creating a separate `SourceMap` page.

## Consequential cautions

- **Reported:** the two reference servers (`mcp_server`, `server`) ship without authentication, authorization, or prompt-injection filtering *by design*, and upstream declares security reports and auth PRs against them out of scope. See [security boundaries](graphiti-security-telemetry.md).
- **Reported:** the Kuzu backend is deprecated and slated for removal because upstream Kuzu is unmaintained; new work is steered to Neo4j or FalkorDB.
- **Reported:** structured (JSON) output is a hard dependency of extraction and deduplication, so small or loosely compatible models are a documented failure source rather than a tuning detail.
- **Synthesis:** the README documents configuration surfaces and product positioning in more depth than runtime behaviour — no algorithm, schema, index, scoring formula, or failure-handling path is specified. Treat these pages as an interface map, not as an implementation description.

## Relationships

- **Contains:** [context graph model](graphiti-context-graph-model.md), [episode ingestion](graphiti-episode-ingestion.md), [model and provider configuration](graphiti-model-providers.md), [deployment and graph backends](graphiti-deployment-backends.md), [retrieval and ranking](graphiti-retrieval.md), [security boundaries and telemetry](graphiti-security-telemetry.md).
- **Related:** [txtai semantic graph](txtai-graph.md) also derives a graph, but from embedding similarity rather than LLM-extracted temporal claims. [LightRAG](lightrag.md) compiles entity/relation descriptions into a graph index inside a full platform; Graphiti exposes only the graph-building framework.
- **Documented successor path:** Zep, available managed or bring-your-own-cloud, is the vendor's recommended production route from the same graph model ([positioning](graphiti-positioning.md)).

## Evidence limits

All eight pages remain `draft`. Their claims rest on promotional and instructional README prose; the implementation, paper, examples, and reference servers behind those claims were not examined, and no behaviour was reproduced. Absent licence information also means redistribution terms for reused excerpts are unconfirmed.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): intro block (framework scope, Zep relationship), “What is a Context Graph?”, “Graphiti and Zep”, “Why Graphiti?”, “Installation” requirements, “Reference MCP and REST servers”, “Telemetry”, and “Documentation” sections.
