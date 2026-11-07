---
type: Concept
title: Hy Memory working and coding scenes (two-layer memory)
description: The facts + experiences memory used for working and coding scenes — schema, write and search flow, scene routing, workspace/branch isolation, and reconciliation rules.
tags: [agent-memory, hy-memory, working-memory, coding-memory, reconcile]
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

# Hy Memory working and coding scenes (two-layer memory)

Working and coding share one productivity pipeline: a session with a tool-call trace yields exactly one **fact** (what this session did) and zero or more reusable **experiences**; coding differs by a software-engineering extraction spec, isolated storage, and an optional [version-evolution diff chain](hy-memory-coding-diff-chain.md) (`README.md::2. Working`, `3. Coding`; `hy_memory/coding/__init__.py` docstring).[^hy-memory]

## Schema

- **Experience** (`CodingMemory`, `coding/types.py`; DDL `coding/store.py::_CREATE_TABLE_SQL`): `experience_id, task, search_keys[], solution, boundary_envs, workspace_id, branch, session_id, files[], source_fact_ids[], confidence, memory_at …`. Embedded as task + search keys.[^hy-memory]
- **Fact** (`WorkingFact`, `coding/types.py`; `_CREATE_FACT_TABLE_SQL`): `statement` (embedded text, `subject: statement`), `files`, `subject`, `details` (verbatim from raw messages, *not* embedded), `fact_link`, `derived_experience_ids`, `status ∈ {active, superseded}`, `fact_chain_summary` (also not embedded). No TTL; `session_id` is stored but not an isolation boundary; lineage walks capped at `MAX_FACT_CHAIN_ENTRIES=8`.[^hy-memory]
- Layers cross-link: `fact.derived_experience_ids ↔ experience.source_fact_ids` (`coding/writer.py::_crosslink`). `memory_at` is retained since 2.0.7 (`CHANGELOG.md::2.0.7`).[^hy-memory]

## Write flow (`coding/writer.py::CodingWriter.write`)

1. Load last 5 turns as context (tool results capped at 2048 bytes, `coding/preproc.py`); the extractor sees all new turns.
2. One LLM call yields both layers; 0 or 1 fact per trace.
3. Experience reconcile plan (ADD/UPDATE/DELETE/SKIP) and fact reconcile plan (INSERT/SUPERSEDE); **both decisions must succeed before anything is persisted**.
4. Apply both, cross-link, append trace.
5. Failures raise `CodingWriteError` (`LLM_ERROR`, `EMPTY_RESPONSE`, `JSON_PARSE_FAILED`, `EMBEDDING_FAILED`, `RECONCILE_FAILED`) returned as `success=False, error_code=502`; failed writes do not append the trace.

(`coding/writer.py`, `coding/types.py::CodingWriteError`; `coding/extractor.py`.)[^hy-memory]

## Search flow (`client.py::_search_coding`)

One query embedding serves both layers. Facts are the primary index (default gate 0.30); experiences are pulled along `derived_experience_ids` and supplemented by a direct vector search (`via: "fact_link" | "direct"`), same threshold (fact + 0.10); `limit` applies per layer. BM25Plus rerank over `subject: statement` happens when candidates exceed top-k but the returned score stays the dense cosine (`coding/lexical.py::rerank`; `coding/store.py::search_facts`). Result keys: `facts`, `experiences`, and coding-only `chain_block`.[^hy-memory]

## Scene routing

- Write: explicit `chat` strips tools; explicit `working|coding` skips the judge but **falls back to chat when there is no tool message/`tool_calls`**; `scene=None` without tools goes to chat with zero LLM calls, with tools runs a 3-way classifier (fail-safe chat) (`client.py::async_add` routing block; `coding/judge.py::classify_messages_scene`).[^hy-memory]
- Read: explicit scene ⇒ no judge/rewrite LLM; `search_mode="default"` single query ⇒ chat, zero LLM; `agentic` ⇒ judge + rewrite + time parsing; `scene="all"` fuses lanes by RRF (`docs/scene_coding_usage.md` §2).[^hy-memory]

## Storage and isolation

Files: `coding_memory.db` (working), `coding_memory_cv.db` (coding), shared `coding_memory_trace.db`, `hy_code_chain/hy_code.db`; collections `{base}_coding_keys(_cv)`, `{base}_working_facts(_cv)`. Variants use separate DBs because retrieval hits the vector store before SQLite filtering (`coding/store.py::__init__`; `docs/scene_coding_usage.md` §5).[^hy-memory] Scope: no `workspace_id` ⇒ no filter; with it, exact match; `branch` stacks only on `workspace_id` and **keeps `branch IS NULL` rows** (loose by design). Vector filtering isn't pushed down, so SQLite is authoritative and vector fetch is over-fetched by the selection ratio, capped at 2000 rows (`store.py::_scope_where`, `_scope_overfetch`).[^hy-memory]

## Reconciliation rules

- **Experiences** (`coding/reconciler.py`): top-3 candidates per draft; one LLM call returns `{"ops": [...]}`; UPDATE/DELETE must target an offered candidate; UPDATE keeps `source_fact_ids` and `memory_at=max(prev,new)`; unhandled drafts get a fallback ADD.[^hy-memory]
- **Facts** (`coding/fact_reconciler.py`): top-5 active candidates, no min score; none ⇒ no LLM call; INSERT always, plus SUPERSEDE for the same user task. Subject gate `HY_FACT_SUBJECT_GATE` is **off by default**; empty `session_id` disables supersede; the new fact is embedded before the old is superseded; chain summary regenerated from ≤8 generations; ancestor `details` inherited under `HY_FACT_INHERIT_DETAILS` (default on, 4000 chars total / 1200 per ancestor).[^hy-memory]

## Limits

Chroma scope filtering is approximate; the loose branch rule and default-off subject gate permit cross-subject merges; lexical rerank effects are visible only in logs (`coding/lexical.py`; `store.py`; `fact_reconciler.py`). Behavioural pins are in `tests/coding/` (e.g. `test_fact_reconciler.py`, `test_scene_coding_variant.py`).[^hy-memory]

## Relationships

- Part of: [Hy Memory overview](hy-memory-overview.md). Extended by: [Diff chain](hy-memory-coding-diff-chain.md).
- Evaluated by: [CMB benchmark](cmb-coding-memory-benchmark.md).
- Differs from: [Chat write path](hy-memory-chat-hierarchy-and-write-path.md).

## Coverage and limits

Static inspection (delegated); `tests/coding/` read only for named behaviours. `scripts/dump_coding_db.py` exists for DB inspection but was not run.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
