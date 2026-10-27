---
type: Concept
title: Graphiti context graph data model
description: Entities, temporally valid facts, episode provenance, and prescribed or learned ontology as the four parts of a Graphiti context graph.
tags: [rag, knowledge-graph, temporal, data-model]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T12:45:00Z }
sources:
  - id: graphiti-readme
    resource: ../raw/graphiti.md
    kind: documentation
    title: Graphiti README — A Framework for Building Temporal Knowledge Graphs (getzep/graphiti)
---

**Reported:** a Graphiti "context graph" is a temporal graph in which each fact carries a validity window — when it became true and, if applicable, when it was superseded — while entities keep summaries that evolve over time and every derived element traces back to the raw episode that produced it.[^graphiti-readme] **Synthesis:** the model is a claim store with lineage, not a chunk index: the README's four components (entities, facts, episodes, custom types) separate *what is asserted*, *when it held*, and *where it came from*.[^graphiti-readme]

## Components

| Component | What the README says it stores |
| --- | --- |
| Entities (nodes) | People, products, policies, concepts — with summaries that evolve over time |
| Facts / relationships (edges) | Triplets (Entity → Relationship → Entity) carrying temporal validity windows |
| Episodes (provenance) | Raw data as ingested — the ground-truth stream that every derived fact traces back to |
| Custom types (ontology) | Developer-defined entity and edge types declared through Pydantic models |

## Temporal semantics

Facts are added and invalidated, not deleted: when information changes, the earlier fact's window closes and the historical state remains queryable, so a client can ask what is true now or what was true at a chosen time.[^graphiti-readme] Contradiction resolution is described as automatic fact invalidation with temporal history preserved, in contrast to the LLM-summarization judgement the README attributes to GraphRAG.[^graphiti-readme] The comparison table also calls the tracking "bi-temporal", but the README never defines which two timelines are meant (validity versus ingestion, for example), so that term stays an unresolved label rather than a specified contract.[^graphiti-readme]

## Ontology: prescribed versus learned

Entity and edge types can be declared upfront from Pydantic models (prescribed) or left to emerge from the data (learned); the README presents "start simple, evolve as patterns appear" as the intended progression.[^graphiti-readme] **Synthesis:** prescribed types buy schema stability for downstream consumers and learned types buy ingestion flexibility, but the README does not state how a learnt type is later promoted, renamed, or migrated into a prescribed one.[^graphiti-readme]

## Incremental construction

New episodes are integrated immediately without batch recomputation or complete graph recomputation, which the README frames as the difference from batch-oriented document summarization pipelines.[^graphiti-readme] **Synthesis:** incremental construction and neighbour-based deduplication imply that fact identity, resolution order, and invalidation decisions are correctness-critical; see [episode ingestion](graphiti-episode-ingestion.md) for the concurrency and model-routing controls that govern them.[^graphiti-readme]

## Relationships

- **Part of:** [Graphiti](graphiti.md).
- **Depends on:** [model and provider configuration](graphiti-model-providers.md) for the extraction and deduplication decisions that create and invalidate facts, and [deployment and graph backends](graphiti-deployment-backends.md) for where the graph is stored.
- **Contrasts with:** [txtai's semantic graph](txtai-graph.md), whose edges are similarity-derived and whose topics come from community detection — a derived retrieval index rather than a temporal claim store. [LightRAG](lightrag.md) likewise indexes entity/relation descriptions for retrieval; it does not document validity windows or episode-level lineage.

## Evidence limits

**Reported only.** The README supplies no node or edge schema, no storage-level model, no invalidation algorithm or tie-breaking rule, no Cypher or index definitions, and no worked example of history being read back; the linked paper is not part of this snapshot. Whether "invalidation" appends a superseding edge, rewrites an existing one, or something else is therefore unestablished here.

[^graphiti-readme]: `raw/graphiti.md` (unpinned README capture, md5 `53a0b19aa63dd8a4bc1e6d5e3dd90a3d`): “What is a Context Graph?” (component table, validity-window definition, episode provenance), intro block (“Unlike static knowledge graphs…”), “Why Graphiti?” bullets (Temporal Fact Management, Episodes & Provenance, Prescribed & Learned Ontology, Incremental Graph Construction), and the “Graphiti vs. GraphRAG” table rows for temporal and contradiction handling.
