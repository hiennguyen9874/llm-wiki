---
type: Concept
title: "RAGFlow standalone harness boundary"
description: "A separate graph/ADK/event-replay harness exists in the tree but was not found wired into the shipping server runtime."
tags: [ml, ragflow, rag]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:13:34Z }
stale_after: 2027-01-26
sources:
  - id: ragflow
    resource: ../raw/ragflow/README.md
    scope: ../raw/ragflow/
    kind: code
    revision: 1731e54b3aa0
    title: RAGFlow repository snapshot
---

# RAGFlow standalone harness boundary

**Observed:** `internal/harness` contains graph execution, typed agent interfaces, loop orchestration, workflow combinators and event/replay/metrics facilities. A module-wide import search found its references confined to the harness subtree; no external production consumer was found. **Synthesis:** describe it as a separate library present in this snapshot, not as the runtime powering the shipping RAGFlow agent UI.[^ragflow]

## Library layers

| Layer | Actual source location | Representative API |
| --- | --- | --- |
| Graph engine | `internal/harness/graph/` | Pregel, graph, channels, checkpoints, interrupts, store |
| Typed agent layer | `internal/harness/core/` | `TypedAgent`, `TypedRunner`, `ReActConfig` |
| Push loop and workflows | `internal/harness/core/` | `AgentLoop`, sequential/parallel/loop constructors |
| Events, replay, metrics | `internal/harness/events`, `replay`, `metrics` | `EventType`, `ReplayEngine`, `NewAgentMetrics` |

Middleware directories cover dynamic tool search, filesystem, tool-call patching, planning, reduction, skills, subagents, summarization and telemetry. Implementations were not deeply audited. Provider and harness profiles are distinct configuration inputs.[^ragflow]

## Documentation drift

The harness README describes `graphengine` and `agentcore` paths and other files absent from the actual tree. The real package path is `core` (sometimes imported with the `agentcore` alias), and the graph packages are under `graph`. Use current symbol locations rather than treating the README file map as authoritative.[^ragflow]

## Negative-evidence limit

The import search is static negative evidence, not an executed reachability proof. It does not establish that the harness is buildable, correct, or ready for integration. Future revisions may connect it to the application, so recheck imports before reusing this conclusion.[^ragflow]

## Relationships

- **Contrasts with:** [shipping agent workflows](ragflow-agent-workflows.md), which use eino.
- **Related to:** [operations/test coverage](ragflow-operations.md); library tests were not executed during this ingest.

## Evidence and limits

**Observed** means static inspection, not demonstrated runtime behavior. This page is **draft** because package coverage is sampled; builds, application tests, external services, model execution, and performance claims were not verified. See the [source map](ragflow-source-map.md) for the coverage ledger and redacted security boundary.

[^ragflow]: [RAGFlow source](../raw/ragflow/README.md), revision `1731e54b3aa0`; locators: `internal/harness/harness.go::package documentation / re-exports`; `internal/harness/core/contracts.go::TypedAgent`; `internal/harness/core/runner.go::TypedRunner / NewTypedRunner`; `internal/harness/core/react_agent.go::ReActConfig`; `internal/harness/core/agent_loop.go::AgentLoop / NewAgentLoop`; `internal/harness/core/workflow.go::NewSequential / NewParallel / NewLoop`; `internal/harness/core/profile/profile.go::ProviderProfile / HarnessProfile`; `internal/harness/events/event.go::EventType`; `internal/harness/replay/replay.go::ReplayEngine`; `internal/harness/metrics/metrics.go::NewAgentMetrics`; `internal/harness/README.md::Project Structure`; `internal/agent/canvas/compile.go::eino imports`; `go.mod::module ragflow; static import search for ragflow/internal/harness outside internal/harness (2026-10-26)`.
