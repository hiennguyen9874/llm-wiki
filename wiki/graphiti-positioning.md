---
type: Concept
title: Graphiti positioning versus Zep and GraphRAG
description: Vendor-reported boundaries between the Graphiti framework, the Zep platform, and GraphRAG's batch summarization model.
tags: [rag, comparison, architecture, platform]
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

**Reported:** the Graphiti README draws two explicit boundaries — Graphiti versus Zep (framework versus governed context platform, same underlying graph technology) and Graphiti versus GraphRAG (incrementally updated temporal claims versus batch document summarization).[^graphiti-readme] **Synthesis:** the Zep/Graphiti split is the more useful one for platform engineering because it is a division of responsibility (who supplies the database, tenancy, retrieval service, and SLAs); the GraphRAG comparison is a vendor contrast without published benchmark conditions and should be treated as a set of testable hypotheses, not as measured capability.[^graphiti-readme]

## Framework versus platform

| Aspect | Zep (Reported) | Graphiti (Reported) |
| --- | --- | --- |
| Role | Unified enterprise context layer serving agents in production | Open-source framework for building temporal context graphs |
| Scope | Unifies enterprise data into governed context graphs and serves them | Builds and queries graphs inside your own application |
| Graph storage | Konig, Zep's own graph database service, no third-party graph DB | Bring your own: Neo4j, FalkorDB, or Amazon Neptune |
| Users, threads, ingestion | Built in for messages and business data | Build your own |
| Retrieval | Pre-configured, "sub-200ms" at scale | Custom implementation; performance depends on your setup |
| Developer tooling | Dashboard with graph visualization, debug and API logs, CLI, Python/TypeScript/Go SDKs | Build your own |
| Enterprise and deployment | SLAs, support, security guarantees; managed or BYOC | Self-managed, self-hosted only |

The README's decision rule is correspondingly simple: choose Zep to have enterprise context unified, governed, and served without operating that system, and choose Graphiti to embed temporal context graphs in your own system while operating the database, retrieval, and surrounding service yourself.[^graphiti-readme]

**Synthesis:** the boundary maps onto concrete engineering seams this wiki tracks elsewhere — authentication and tenancy, ingestion pipelines, retrieval serving, and observability all move to the integrator when using Graphiti, whereas the Zep path removes them from the inspected scope entirely.[^graphiti-readme]

## Framework versus GraphRAG

| Aspect | GraphRAG (Reported) | Graphiti (Reported) |
| --- | --- | --- |
| Primary use | Static document summarization | Dynamic, evolving temporal knowledge graphs |
| Data handling | Batch-oriented | Continuous, incremental updates |
| Knowledge structure | Entity clusters and community summaries | Entities, facts with validity windows, episodes, communities |
| Retrieval | Sequential LLM summarization | Hybrid semantic, keyword, and graph search |
| Temporal handling | Basic timestamp tracking | "Explicit bi-temporal tracking with automatic fact invalidation" |
| Contradiction handling | LLM-driven summarization judgement | Automatic invalidation with history preserved |
| Query latency | Seconds to tens of seconds | Typically sub-second |
| Custom entity types | Not supported | Supported through Pydantic models |

## Reading these claims

**Unverified, vendor-authored.** No benchmark, corpus, model configuration, or measurement protocol accompanies the latency, adaptability, or scalability verdicts, and the GraphRAG column describes a design the README does not cite a revision of. Per the repository's scope rule, these stay claims: useful for framing comparisons, not for capability decisions. The "bi-temporal" wording is also undefined here (see the [context graph model](graphiti-context-graph-model.md)).[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Depends on:** [security boundaries and telemetry](graphiti-security-telemetry.md) for what "governed" and "managed" remove from the integrator's responsibility, and on [deployment and graph backends](graphiti-deployment-backends.md) for the self-managed side.
- **Contrasts with:** batch-summarization graph pipelines described in the README's GraphRAG column; within this wiki, [RAGFlow knowledge compilation](ragflow-knowledge-compilation.md) and [WeKnora wiki compilation](weknora-wiki-compilation.md) are examples of compiled-knowledge pipelines that are not claimed here to be GraphRAG.

## Evidence limits

**Reported only.** Both tables are the vendor's own positioning, including the "when to choose which" guidance, and none of the competing systems, the paper behind them, or the managed service's performance figures were inspected. No architecture detail of Konig is given beyond being Zep's own graph database service.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): intro block (Zep relationship and arXiv 2501.13956 reference), “Graphiti and Zep”, “Zep vs Graphiti” (comparison table, “When to choose which”), “Why Graphiti?”, and “Graphiti vs. GraphRAG”.
