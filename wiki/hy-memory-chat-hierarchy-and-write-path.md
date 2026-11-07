---
type: Concept
title: Hy Memory chat hierarchy (L0–L7) and System 1 write path
description: The eight-layer chat memory model, the System 1 extract→reconcile→store write chain, multi-speaker ownership rules, and prompt-language handling.
tags: [agent-memory, hy-memory, chat, write-path, reconcile]
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

# Hy Memory chat hierarchy (L0–L7) and System 1 write path

For chat, raw conversations are abstracted layer by layer into facts, summaries, a profile and higher-level structures (`README.md::1. Chat: Memory Hierarchy`).[^hy-memory] "System 1" is the per-write, LLM-light chain in `MemoryWriter`; the slower [System 2](hy-memory-system2-evolution.md) is separate and explicit.

## Layers

Defined in `hy_memory/models/memory.py::MemoryLayer`:

| Layer | Role | Notes |
|---|---|---|
| L0 `BASIC_INFO` | user profile, single evolution chain | placeholder values (用户 / The user / N/A) cannot supersede real values (2.0.9) |
| L1 `RAW` | append-only raw conversation | demoted to `SHADOW` after extraction finishes, even if nothing was extracted |
| L2 `FACT` | atomic, versioned facts | |
| L3 `SUMMARY` | episode/topic summaries | |
| L4 `IDENTITY` | legacy, read-only for old data | README says "Reserved" |
| L5 `KNOWLEDGE` | declared, "not implemented" | README says "Reserved" |
| L6 `SCHEMA` | mental-model schemas in the graph | built by System 2 |
| L7 `INTENTION` | prospective intentions with `valid_until`; demoted to ordinary facts when expired | |

(`models/memory.py::MemoryLayer`; `README.md` layer table; `CHANGELOG.md::2.0.9`.)[^hy-memory] The `MemoryLayer` docstring says L5–L7 live in the graph, but System 1 writes L7 to the vector store (`pipelines/writer.py::_store_intentions`) and `_retrieval/intention.py` reads it from there — documentation drift (Synthesis, from two Observed locations).[^hy-memory]

## Write path (System 1)

`pipelines/writer.py::MemoryWriter.write`:[^hy-memory]

1. Validate; trim raw messages (`utils/raw_trim.py`).
2. Embed (queued) and upsert the `L1_RAW` node.
3. If `agent_mode == "full"` (any mode but `lite`), load the last `history_turns` (default 5) and run `MemAgent.process_add` → `Extractor.extract`, one LLM call returning `memory`, `intentions`, `basic_info` (`agent/extractor.py::extract`).
4. Upsert L0 via `agent/tools/basic_profile.py::upsert_basic_profile` (new version, old `superseded`).
5. Intra-extract cosine dedup (`_dedup_extracted`).
6. Reconcile against existing memories, serialised per user (`MemoryReconciler.reconcile`; `_reconcile_user_lock`). Candidates come from additive vector+BM25 fusion (`_retrieval/reconcile_retrieval.py`).
7. Intentions go straight to L7 with batch-internal cosine dedup, skipping reconcile.
8. `L1_RAW` → `SHADOW`; then episode bookkeeping/summary, graph projection and topic summaries are scheduled.

**Reconcile ops** (`agent/reconciler.py::ReconcileOp`): `ADD`; `SUPERSEDE` (contradiction — old → `SHADOW`, new joins the evolution chain); `UPDATE` (merge/refine — old → `SHADOW`, not chained). Ops carry `layer`, `owner` (`user`/`agent`), `tags`, `topic_paths`, `event_facet`, typed `related` links (`causes`/`elaborates`/`contrasts`/`same_series`) and `speculate`; parsing accepts flat or grouped JSON with `json_repair` fallback.[^hy-memory]

`write_extracted` skips extraction and reconciles caller-provided facts (`writer.py:2426` region). Since 2.0.13 failures fail closed with error codes rather than storing raw as a fallback (`CHANGELOG.md::2.0.13`).[^hy-memory]

## Multi-speaker ownership

`role="user"` (optional `name`) is the memory owner; `role="assistant"` **with** `name` is another named human rendered `[John]`; without `name` it is the AI. Facts from user and named humans get `owner="user"`, AI content `owner="agent"`; prompts forbid cross-subject UPDATE/SUPERSEDE. Boundaries: no participant table, speaker only encoded in fact text, no per-person L0 — use separate `user_id` per perspective (`docs/multi_speaker_design.md` §§1–5; `pipelines/base.py::ChatMessage.speaker_label`; `writer.py::_norm_owner`).[^hy-memory]

## Language

Prompts ship for 11 languages; `get_prompt(name, language)` lazy-loads modules with a mandatory key set `PROMPT_NAMES`; auto-detect only chooses zh or en; an explicit language appends an output-language directive so auto-detected prompts stay byte-identical (`hy_memory/prompts/__init__.py`; `utils/lang_detect.py`).[^hy-memory]

## Dead or weakly used code (Synthesis from grep-level evidence)

`agent/emotion_analyzer.py`, `intention_detector.py` and `abstractor.py` are exported but not instantiated by any pipeline; `Reflector` runs only when `existing_memories` is non-empty, which normal chat writes do not provide (`agent/__init__.py`; `agent/mem_agent.py::process_add`). Treat as unused scaffolding, Unverified beyond a search.[^hy-memory]

## Relationships

- Part of: [Hy Memory overview](hy-memory-overview.md).
- Followed by: [System 2 evolution](hy-memory-system2-evolution.md); read by [Chat retrieval pipeline](hy-memory-chat-retrieval-pipeline.md).
- Parallel: [Working and coding memory](hy-memory-working-coding-memory.md) uses a different pipeline.

## Coverage and limits

Static inspection (delegated). `writer.py` is very large (write path lines ~2570–3660); the step list is a distilled reading, and the paper describing this design (EMNLP 2026) was not read.

[^hy-memory]: Hy-Memory monorepo, revision 9737431. Locators inline per claim. Evidence class Observed (delegated static inspection, unexecuted) unless labelled otherwise.
