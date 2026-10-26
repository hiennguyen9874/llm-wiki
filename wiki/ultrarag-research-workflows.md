---
type: Concept
title: UltraRAG research workflows, prompts, and memory
description: Reusable iterative RAG examples, prompt rendering, citation transformations, routers, and persistent user memory.
tags: [ml, ultrarag, prompts, agentic-rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T07:55:24Z }
stale_after: 2027-01-26
sources:
  - id: ultrarag
    resource: ../raw/UltraRAG/README.md
    scope: ../raw/UltraRAG/
    kind: code
    revision: 185e203
    title: UltraRAG repository
---

**Observed:** UltraRAG supplies YAML compositions for iterative reasoning and research agents, backed by prompt functions, custom transforms, and routing tools. These are implementation examples, not independently reproduced papers or measured evidence that a named method matches its publication. Their shared mechanism is explicit state and variable wiring through the [pipeline DSL](ultrarag-pipelines.md).[^ultrarag]

## Workflow families

| Retrieval purpose | Local examples |
| --- | --- |
| Baselines and control-flow demonstrations | `vanilla_llm`, `vanilla_rag`, `rag_full`, `rag_loop`, `rag_branch` |
| Mixed retrieval and answer refinement | `hybrid_search`, `ircot`, `iterretgen`, `rankcot` |
| Search-integrated reasoning | `search_r1`, `r1_searcher`, `search_o1` |
| Structured research and reporting | `webnote`, `webnote_websearch`; demos `LightResearch`, `AgentCPM-Report`, `AgentCPM-Report_web` |
| Multimodal and dialogue tasks | `visrag`, `evisrag`, `multimodal_rag`, `multiturn_chat`; memory-enabled demos |

The experiment pipelines live under `examples/experiments/`; deployable/demo variants and their parameter/server snapshots live under `examples/demos/`. Names indicate intended workflow families, not runtime validation or benchmark equivalence.[^ultrarag]

## Prompt and citation mechanism

The prompt server loads external Jinja templates and exposes named prompt functions for QA, retrieval-augmented QA, memory, reasoning, WebNote, and SurveyCPM. Templates are not embedded into the orchestration language. The renderer uses a sandboxed Jinja environment with autoescaping and explicit string escaping; model inputs can therefore contain HTML entities for special characters. The effect on answer quality remains **unverified**.[^ultrarag]

Custom tools handle boxed-answer extraction, query extraction, passage merging, search-state/list transformations, and citation assignment. SurveyCPM adds a structured action/state machine: search, initial planning, writing, plan extension, and completion; committed bounds are `140` total steps and `12` extension steps, with optional stricter action/language validation. Citation IDs can be assigned statefully to keep references consistent across iterations; this is document bookkeeping, not external factual verification. Citation registries are process-global dictionaries keyed by query index rather than run ID; concurrent reuse/reset requires care (**synthesis** from their state scope). Router tools return wrapped data with named states such as `complete`/`incomplete`, `retrieve`/`stop`, or `continue`/`stop`; these strings must match branch keys. Completion decisions use method-specific text/state heuristics.[^ultrarag]

## Persistent memory versus execution history

**Observed:** the memory server reads a user's `MEMORY.md` and appends project/day records under `memory/<user_id>/project/<YYYY-MM-DD>.md`. A new global-memory file is seeded with a fictional profile template, not an empty or user-attested biography. Its root is derived from `ULTRARAG_UI_STORAGE_ROOT` or defaults to the repository's `ui/storage`; user IDs must match an alphanumeric/underscore/hyphen pattern. The client's automatic end-of-turn saver consumes the first question/answer entries when a memory server is configured. This persistence is separate from `UltraData`'s in-run histories and JSON snapshots. Within `servers/`, writing Markdown does not itself populate the Milvus `user_<id>` collection queried by project-memory search; indexing must be supplied through another integration.[^ultrarag]

**Synthesis:** memory-enabled batch pipelines deserve particular review because automatic saving is turn-oriented rather than a general persistence guarantee for every row. Prompt sandboxing also does not neutralize prompt injection from retrieved text or confer trust on generated citations.[^ultrarag]

## Coverage and limits

Draft because the 55-template collection and large custom SurveyCPM state machine received selective rather than exhaustive semantic inspection. Workflow names and wiring were inspected, but no models, research pipelines, citation-quality evaluations, or memory sessions were run. See [coverage](ultrarag-source-map.md) for remaining attachments and exclusions.[^ultrarag]

## Relationships

- **Uses:** [retrieval](ultrarag-retrieval.md) and [generation](ultrarag-generation.md) as composable tools.
- **Depends on:** [pipeline state semantics](ultrarag-pipelines.md) for branch-aware iteration.
- **Uses:** [UI storage](ultrarag-ui.md) as the persistent-memory root, even outside a browser session.

[^ultrarag]: Revision `185e203`: `examples/experiments/*.yaml` server/step mappings, especially `hybrid_search.yaml`, `ircot.yaml`, `rankcot.yaml`, `search_o1.yaml`, `webnote.yaml`; `examples/demos/{LightResearch,AgentCPM-Report,LLM_memory,RAG_memory}.yaml`; `servers/prompt/src/prompt.py` Jinja environment, `_safe_render`, QA/WebNote/SurveyCPM prompt registrations; `prompt/{qa_boxed,qa_rag_boxed}.jinja`; `servers/custom/src/custom.py::CitationRegistry`, `assign_citation_ids`, `assign_citation_ids_stateful`, `merge_passages`, `output_extract_from_boxed`, `surveycpm_state_init`, `surveycpm_validate_action`, `surveycpm_update_state`; `servers/custom/parameter.yaml` SurveyCPM limits; `servers/router/src/router.py::ircot_check_end`, `search_o1_check`, `check_model_state`; `servers/memory/src/memory.py` storage-root/user-ID helpers, `get_global_memory`, `save_memory`; `src/ultrarag/client.py::_auto_save_memory_turn`.
