---
type: Concept
title: Hindsight reflect agent
description: "The agentic reflect operation: its tool loop, hierarchical retrieval order, disposition traits, directives and structured output."
tags: [agent-memory, hindsight, reflect, agents]
status: stable
created: 2026-11-06
generated: { by: llm-wiki-agent/1, at: 2026-11-06T16:50:00Z }
sources:
  - id: readme
    resource: ../raw/hindsight/README.md
    scope: ../raw/hindsight/
    kind: code
    revision: eb963cb
    title: Hindsight README (monorepo root)
  - id: reflect-doc
    resource: ../raw/hindsight/hindsight-docs/docs/developer/reflect.mdx
    kind: documentation
    revision: eb963cb
    title: Reflect developer doc
  - id: agent-code
    resource: ../raw/hindsight/hindsight-api-slim/hindsight_api/engine/reflect/agent.py
    kind: code
    revision: eb963cb
    title: Reflect agent loop
---

`reflect` performs a deeper analysis than recall: an LLM agent loops over memory-search tools, gathers evidence, and answers a question that needs reasoning rather than lookup (for example risk analysis or "why did outreach fail").[^readme]

## Loop (docs Reported, code Observed)

- **Retrieval hierarchy:** mental models → observations (stale ones verified against facts) → raw facts via `recall`.[^reflect-doc][^agent-code]
- **Tools:** `search_mental_models`, `read_mental_models`, `search_observations`, `recall`, `expand` (depth `chunk` or `document`), and terminal `done`. Citations are validated against retrieved IDs.[^reflect-doc][^agent-code]
- **Limits:** max 10 iterations (`HINDSIGHT_API_REFLECT_MAX_ITERATIONS`), 100k context tokens, 300 s wall timeout (`HINDSIGHT_API_REFLECT_WALL_TIMEOUT`; HTTP 504 on expiry).[^reflect-doc][^agent-code]
- Code: `engine/reflect/agent.py::run_reflect_agent`; tools in `engine/reflect/tools.py` and `tools_schema.py`; prompts in `engine/reflect/prompts.py`.[^agent-code]

## Steering

- **Disposition traits** `skepticism`, `literalism`, `empathy`, each 1–5, default 3/3/3. Documented presets include customer support 2/2/5, code review 4/5/2, legal 5/5/2, therapist 2/2/5, research assistant 4/3/3. Code shows traits only shape prompt hedging via `bank_disposition_line` (Observed).[^reflect-doc][^agent-code]
- **Directives** are hard rules: untagged = global; tagged apply only with matching reflect tags; `apply_all_directives: true` forces all. See [Memory banks](hindsight-memory-banks.md).[^reflect-doc]
- **`response_schema`** returns prose plus `structured_output` via a second extraction pass; failure yields HTTP 200 with `structured_output_error`.[^reflect-doc]
- With a [decision model](hindsight-decision-models.md) (providers `hindsight`, `typesafe`) reflect orchestrates in parallel layers instead of agent turns.[^reflect-doc]

## Relationships

- Uses [Recall](hindsight-recall-pipeline.md) and the outputs of [Consolidation and mental models](hindsight-consolidation-and-mental-models.md).
- A mental model is effectively a stored reflect answer that refreshes on a trigger.

## Limits

Behaviour not executed. The README's "forms opinions" framing is outdated: the `opinion` fact type was removed (see [discrepancies](hindsight-doc-code-discrepancies.md)).

[^readme]: `README.md` § "Reflect".
[^reflect-doc]: `hindsight-docs/docs/developer/reflect.mdx` (agent loop, disposition, directives, structured output sections).
[^agent-code]: `hindsight-api-slim/hindsight_api/engine/reflect/{agent,tools,tools_schema,prompts}.py`; `engine/memory_engine.py::reflect_async`.
