---
type: Concept
title: Graphiti episode ingestion
description: Episode-first ingestion, index initialization, incremental graph integration, LLM concurrency limits, and overridable extraction prompts.
tags: [rag, ingestion, knowledge-graph, concurrency]
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

**Reported:** Graphiti ingests *episodes* — text or structured JSON payloads — and integrates them into the existing graph as they arrive, extracting entities and relationships, deduplicating against what is already stored, and invalidating superseded facts instead of rewriting over them.[^graphiti-readme] **Synthesis:** the unit of ingest and the unit of provenance are the same object, which is what makes later "why is this fact in my graph?" questions answerable; the cost is that every episode runs through LLM extraction and resolution stages, so throughput and failure behaviour are dominated by provider limits and structured-output reliability.[^graphiti-readme]

## Documented sequence

The quickstart describes five steps in order: connect to a Neo4j, Amazon Neptune, FalkorDB, or Kuzu database; initialize Graphiti indices and constraints; add episodes (both text and structured JSON); search relationships (edges) with hybrid search and rerank by graph distance; and search nodes with predefined search recipes.[^graphiti-readme] **Synthesis:** index and constraint initialization is a separate, explicit step, so a fresh deployment must run it before the first episode rather than relying on implicit migration.[^graphiti-readme]

Episodes double as the tenancy-adjacent grouping primitive in the reference MCP server, which exposes "group management for organizing related data"; the README's own service guidance places tenancy and access control on the integrator, not on the framework.[^graphiti-readme]

## Throughput and provider limits

The ingestion pipelines are described as designed for high concurrency, but the default is deliberately low: `SEMAPHORE_LIMIT` defaults to **10** concurrent operations to avoid provider 429 rate-limit errors, and the README advises lowering it further on 429s and raising it only when the provider allows more throughput.[^graphiti-readme] For local or small models the same advice is repeated, because local servers and some providers have limited concurrency.[^graphiti-readme]

## Extraction quality controls

- **Structured output is load-bearing:** Graphiti depends on structured (JSON) output for entity/edge extraction and deduplication, and works best with OpenAI, Anthropic, and Gemini; other services "may result in incorrect output schemas and ingestion failures", especially with smaller models.[^graphiti-readme]
- **Prompt overrides:** per-client prompt builders can replace extraction prompts by returning a `ChatPrompt` (system + user) through `create_prompt_library`, for example `extract_nodes.extract_message`; unspecified prompts keep built-in defaults.[^graphiti-readme]
- **Fixed schemas:** response schemas are explicitly not overridable, and returning `list[Message]` from an override raises `TypeError` — the documented migration is to return `ChatPrompt(system=..., user=...)`.[^graphiti-readme]
- **Model routing:** prompt-level model choice (including routing dedupe to a decision model) is configured through `llm_runtime`; see [model and provider configuration](graphiti-model-providers.md).[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md); produces the [context graph model](graphiti-context-graph-model.md) and feeds [retrieval and ranking](graphiti-retrieval.md).
- **Depends on:** [model and provider configuration](graphiti-model-providers.md) for extraction/dedupe models, [deployment and graph backends](graphiti-deployment-backends.md) for storage, and [security boundaries](graphiti-security-telemetry.md) for which external services see episode content.

## Evidence limits

**Reported only.** The README shows the `create_prompt_library` override and states the fixed-schema rule but documents no extraction schema, episode chunking or splitting policy, retry/backoff behaviour, deduplication algorithm, contradiction resolution order, batching, error taxonomy, or idempotency guarantee for re-ingested episodes. Ingestion throughput, 429 behaviour, and failure modes were not reproduced.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “Quick Start” (five-step list), “Default to Low Concurrency; LLM Provider 429 Rate Limit Errors” (`SEMAPHORE_LIMIT` default 10), “Installation” IMPORTANT note on structured output, “Structured output and small models”, “Configurable Prompts” (prompt library, fixed schemas, `TypeError` migration), “Reference MCP and REST servers” → “MCP Server” (group management), and “Why Graphiti?” (incremental construction).
