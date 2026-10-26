---
type: Concept
title: "RAGFlow agent workflows and agentic retrieval"
description: "The shipping eino-based canvas runtime composes typed components, streaming events, tools, interruptions, and multi-step retrieval."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:16:02Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow agent workflows and agentic retrieval

**Observed:** the shipping agent path uses `internal/agent` and CloudWeGo eino, not the separate `internal/harness` library. Canvas DSLs compile to executable graphs; registered components implement invocation/streaming contracts. Agentic RAG uses eino ADK and specialized retrieval/navigation tools to gather evidence across steps.[^ragflow]

## Canvas execution model

- `canvas.Compile` builds `CompiledCanvas` with checkpoint, serializer and interrupt options.
- `Runner.Run` forwards workflow events (`workflow_started`, `node_started`/`node_finished`, `message`/`message_end`, `workflow_finished`) and emits `waiting_for_user`, `error` or `cancelled` on the corresponding run outcomes, plus a done terminator.
- `Component` defines Name, Invoke, Stream, Inputs and Outputs. The runtime registry stores metadata/categories and normalizes component lookup.
- Components include LLM/Agent, retrieval, switch/category, loop/parallel, code execution, browser, data/string/list operations and user fill-up. Presence in a registry is not an endorsement of sandbox isolation.
- Loop and parallel helpers wrap eino compose behavior, including interrupt/checkpoint state and fan-out resume handling. The Agent component itself configures an eino ReAct agent.[^ragflow]

## Agentic RAG

`agentic_rag.Run` has lexical and semantic chunk tools, metadata search, navigation/structure and task-planning helpers. Compiled-knowledge tools are conditional on dataset products. Evidence identity and citation handling are explicit subsystems. The README advertises thinking-depth modes; their exact budget/quality behavior was not exhaustively traced, so the claim remains **Reported**, not a measured capability.[^ragflow]

## Integration surface

Agent routes expose templates, CRUD, run/publish/reset, component forms/debugging, versions, sessions, logs, webhook operations and OpenAI-compatible completion paths. `AgentHandler.RunAgent` emits SSE and ensures a terminal done event. Public webhook routes and authenticated interactive routes are separate trust surfaces; code execution/browser/tool access requires a deployment-specific security review.[^ragflow]

## Relationships

- **Uses:** [hybrid retrieval](ragflow-retrieval.md), [compiled knowledge](ragflow-knowledge-compilation.md) and [citation mechanisms](ragflow-citations.md).
- **Excludes as production runtime:** [separate harness](ragflow-harness.md), based on the inspected import boundary.
- **Exposed by:** [frontend and API](ragflow-frontend.md).

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `go.mod::github.com/cloudwego/eino`; `internal/agent/canvas/compile.go::Compile / CompiledCanvas`; `internal/agent/canvas/runner.go::Runner.Run / RunEvent`; `internal/agent/component/base.go::Component`; `internal/agent/runtime/registry.go::Register`; `internal/agent/component/registry.go::Register`; `internal/agent/component/agent.go::eino ReAct integration`; `internal/agent/workflowx/loop.go::AddLoopNode`; `internal/agent/workflowx/parallel.go::AddParallelNode`; `internal/agentic_rag/agent.go::Run`; `internal/agentic_rag/compiled_knowledge.go::compiledKnowledgeTools`; `README.md::Agentic Retrieval`; `internal/router/agent_routes.go::RegisterAgentRoutes / RegisterPublicAgentWebhookRoutes / RegisterAgentCancelRoutes`; `internal/handler/agent.go::RunAgent`.
