---
type: Concept
title: Hy Memory System 2 evolution and cross-domain sweeper
description: Ultra-mode System 2 — explicit evolve() cycles that cluster facts, induce graph schemas with one LLM call per batch, and a cross-domain sweeper for core schemas.
tags: [agent-memory, hy-memory, system2, ultra, schema-induction]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:45:29Z }
sources:
  - id: hy-memory
    resource: ../raw/Hy-Memory/README.md
    scope: ../raw/Hy-Memory/
    kind: code
    revision: 9737431
    title: Hy-Memory monorepo (hy-memory 2.0.14, MemHub 1.0.6)
---

# Hy Memory System 2 evolution and cross-domain sweeper

System 2 is ultra-mode only and **never auto-triggered**: `System2Writer.write()` runs System 1 and returns, there is no in-process queue, and the caller must invoke `client.evolve()` (or the sweeper) explicitly; `evolve` raises outside `ultra` (`pipelines/system2_writer.py` class docstring; `client.py::evolve`; `docs/usage.md::evolve`).[^hy-memory] `evolve()` is synchronous and non-idempotent, and a partial cycle defers the sweeper (Observed in code path).[^hy-memory] MemHub supplies the scheduling, see [modes and write queue](memhub-memory-modes-and-write-queue.md).

## Pipeline

1. `prepare_materials` (hard-coded, no LLM): fetch unprocessed L2/L4 facts, DBSCAN clustering over embeddings (`eps=1-threshold`), graph forward search and reverse lookup (`pipelines/system2_agent.py::prepare_materials`, ~1001–1164).[^hy-memory]
2. Skip gate `s2_agent_skip_reason` (`no_facts`/`no_clusters`).
3. Bounded "evoling" batches — one cluster per call, `MEMORY_EVOLING_MAX_BATCHES`=128, `MEMORY_EVOLING_MAX_FACTS_PER_BATCH`=24, cluster dedup cosine 0.92, max unclustered facts 15 (`system2_agent.py` L43–120).[^hy-memory]
4. `run_system2_agent`: a **single LLM call** returning a JSON operation array, not a multi-turn tool loop; operations run through `System2ToolExecutor` (`system2_agent.py::run_system2_agent`).[^hy-memory]
5. Tools: read `search_vdb`, `search_graph`, `get_node`, `expand_node`; write `create_graph_node`, `update_graph_node`, `add_edge`, `delete_graph_node`, `revise_schema`, `retire_schema`, plus `add_evidence` (`pipelines/system2_tools.py`; docstring says 10 tools, definitions list 9 named — minor drift, Synthesis).[^hy-memory]
6. Optional holistic review, forget retirement, profile-fact promotion, then ultra persona artifacts: balanced catalog (8 domains × 4 ≤ 32 entries) and specific supplement (2/domain ≤ 16), surfaced by `get_user_profile` (`pipelines/balanced_catalog.py`, `specific_supplement.py`; `client.py::get_user_profile`).[^hy-memory]

## Cross-domain sweeper

`CrossDomainSweeper` embeds the "behaviour abstraction" of L6 basic schemas, scans cosine collisions with Union-Find and induces L6 "core" schemas with an LLM. Gates: `MEMORY_CROSS_DOMAIN_MIN_BASICS`=5, behaviour threshold 0.70, concept threshold 0.60 (`pipelines/cross_domain_sweeper.py` docstring). It runs only when the evolve cycle completes (`system2_writer.py::evolve`, `run_sweeper`).[^hy-memory]

## Relationships

- Depends on: [Chat hierarchy and write path](hy-memory-chat-hierarchy-and-write-path.md) (System 1 output) and the graph store ([storage](hy-memory-storage-and-reembed.md)).
- Consumed by: [Chat retrieval](hy-memory-chat-retrieval-pipeline.md) (L6 schema lanes).
- Scheduled by: [MemHub nightly evolve](memhub-memory-modes-and-write-queue.md).

## Coverage and limits

Static inspection (delegated). Schema quality, evolve cost and clustering behaviour were not measured. The EMNLP paper behind this design was not read.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
