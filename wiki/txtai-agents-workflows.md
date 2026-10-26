---
type: Concept
title: txtai agents and workflow orchestration
description: Smolagents integration, tools, skills, session memory, batched task execution, scheduling, and execution trust boundaries.
tags: [rag, txtai, agents, workflows]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T09:14:52Z }
stale_after: 2027-01-24
sources:
  - id: txtai-repo
    resource: ../raw/txtai/README.md
    scope: ../raw/txtai/
    kind: code
    revision: 738aac4
    title: txtai repository
---

**Observed:** txtai offers two orchestration models: `Agent` delegates an iterative tool-using loop to smolagents, while `Workflow` runs a preconfigured sequence of batched tasks. Both can compose embeddings, pipelines, and external functions. **Synthesis:** a fixed workflow and an agent loop have different control, reproducibility, and trust boundaries even when configured in the same application.[^txtai-repo]

## Agent runtime, prompts, and memory

`ProcessFactory` selects `ToolCallingAgent` by default or `CodeAgent` for code mode, supplying a `PipelineModel` adapter. Step budgets and other agent parameters pass to the dependency; legacy `max_iterations` maps to `max_steps`. Dependency internals, default step counts, code isolation, and repair behavior were not inspected.[^txtai-repo]

`Agent` renders the request through sandboxed Jinja and can load instruction text from an `agents.md`-style file. The Jinja sandbox constrains template evaluation, not the tool process. `PipelineModel` adapts messages, generation limits, and tool-call extraction; its text parsing includes an `Action:`-style block, making model-output shape part of compatibility.[^txtai-repo]

**Observed:** the memory window defaults to `None`, meaning no txtai-side history is recorded. When a window is configured, bounded deques are keyed by caller-provided `session`; omitting the session shares the `None` key. `reset` resets that session's history. **Synthesis:** session naming is not authenticated tenancy, and callers must isolate it appropriately. This is process memory, not a durable cross-session knowledge store.[^txtai-repo]

## Tool and skill composition

`ToolFactory` accepts tool objects, callables, configuration dictionaries, built-in names, MCP URLs, and Markdown skill paths. `"defaults"` expands the built-in catalog (excluding a compatibility alias); it is an explicit configuration selection, not proof every agent enables every tool. The catalog includes bash, read/write/edit, glob/grep, Python, user questions, web search, and todo output. An embeddings tool calls search with a fixed limit of five; custom tools can implement other behavior.[^txtai-repo]

Callables can use annotations or fall back to docstring-derived schemas. Skill frontmatter supplies name/description and the body is loaded as instructions. MCP tool collections are imported through the external adapter. Instructions, skills, callable targets, MCP servers, and their returned content are trusted/configuration-sensitive inputs, not automatically isolated plugins.[^txtai-repo]

## Execution and filesystem boundary

**Observed:** bash checks the executable against an allowlist and runs an argument list without a shell, with closed stdin and a timeout (default 30 seconds). Its docstring explicitly calls this best effort, not a sandbox. Allowed file-reading commands still have the process's filesystem access. Read uses a default `Textractor` whose library safe-opening mode is off; write/edit have no inspected workspace containment. The catalog also includes an external Python execution tool. Use a least-privilege runtime rather than equating the allowlist or Jinja sandbox with process isolation.[^txtai-repo]

## Workflow engine

**Observed:** `Workflow` defaults to batches of 100. A workflow initializes tasks, optionally transforms the input stream, processes batches through configured tasks, yields output, and finalizes. Worker defaults derive from task action counts; tasks can choose thread/process concurrency. Preconfigured ordering does not make arbitrary model/network/custom actions deterministic.[^txtai-repo]

Tasks operate on identified `(id, data, tag)` elements with selection, unpacking, column choice, merging, and one-to-many expansion. Multi-action task execution rejects iterator inputs, so streaming input and task fan-out must be reconciled. Task families include file/image retrieval, URL/service calls, templates/RAG, storage/export, console, streams, and nested workflows; only selected implementations were inspected.[^txtai-repo]

Scheduling uses `croniter`; scheduled-run errors are logged and the loop can continue. `Application` resolves workflow tasks from configuration and schedules configured jobs through its thread pool. This is not evidence of a durable queue, crash-replay log, or exactly-once execution. Retry/durability must be established for the actual composition.[^txtai-repo]

## Relationships and limits

- **Uses:** [LLM/RAG adapters](txtai-rag.md), [retrieval](txtai-retrieval.md), and [extraction](txtai-pipelines.md).
- **Exposed by:** [API](txtai-api.md); [security](txtai-security.md) covers agent exposure and executable configuration.
- **Part of:** [txtai](txtai.md); [source map](txtai-source-map.md) records inspected versus declaration-only tests and pending task families.

No agent loop, external MCP server, code tool, workflow, schedule, or concurrency test ran. Sampled test names identify intended coverage, not passed security or behavioral guarantees.

[^txtai-repo]: Revision `738aac4`: `src/python/txtai/agent/base.py::Agent.__init__, __call__, prompt, instructions`; `agent/factory.py::ProcessFactory.create`; `agent/model.py::PipelineModel.generate`; `agent/tool/factory.py::ToolFactory.DEFAULTS, create, createtool, fromdocs`; `agent/tool/bash.py::BashTool`, `agent/tool/read.py::ReadTool`, `agent/tool/write.py::WriteTool`, `agent/tool/edit.py::EditTool`, `agent/tool/embeddings.py::EmbeddingsTool`, `agent/tool/skill.py::SkillTool`; `workflow/base.py::Workflow.__init__, __call__, chunk, process, schedule`; `workflow/task/base.py::Task`; `workflow/task/template.py::TemplateTask, RagTask`; `workflow/task/retrieve.py::RetrieveTask`; `workflow/task/service.py::ServiceTask`; `app/base.py::Application.createagents, createworkflows`; `docs/agent/configuration.md`; `test/python/testagent.py`, `test/python/testworkflow.py` test declaration indexes only. Short module paths are relative to `src/python/txtai/`.
