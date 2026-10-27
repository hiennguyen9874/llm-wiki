---
type: Concept
title: WeKnora agent turn runtime
description: ReAct orchestration, tool capability gates, loop budgets, recovery, and mid-turn steering in WeKnora.
tags: [ml, weknora, agents]
status: draft
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T08:11:38Z }
stale_after: 2027-01-26
sources:
  - id: weknora
    resource: ../raw/WeKnora/README.md
    scope: ../raw/WeKnora/
    kind: code
    revision: fd7a2586fd58
    title: WeKnora v0.8.3 repository snapshot
---

WeKnora implements a guarded ReAct turn engine: caller-supplied conversation history enters a think/analyze/act/observe loop, with explicit budgets and recovery paths for empty output, repeated failures, truncation, context overflow, and user steering. **Observed:** “stateless across turns” means the engine does not own a conversation-history cache, not that its struct has no calibration state.[^weknora]

## Loop and recovery

**Observed** in `internal/agent/engine.go::Execute`, `executeLoop`, and `runReActIteration`, with defaults in `internal/agent/const.go`:[^weknora]

| Control | Inspected behavior/default |
| --- | --- |
| Iteration budget | 20 by default; negative values allow unlimited iterations via `withinIterationBudget` |
| Empty natural-stop response | Up to 2 retries before fallback |
| Repeated no-tool content | Stops after 2 consecutive identical rounds, including repeated emptiness |
| Repeated failed tool call | After 3 identical failures, prompts the model to change approach |
| Completion-limit streak | Stops after 3 consecutive `length` finishes |
| Context overflow | One compact-and-retry recovery per turn |
| Mid-run steering | Drained at a round boundary after compaction and before the next model call; at most one extra round beyond the budget |

These are different budgets: the default model stream timeout is a **120-second no-output stall budget**, not a total turn duration. Ordinary tools default to 60 seconds; `shell_exec` gets 10 minutes plus 5 seconds, `web_fetch` gets its page-fetch budget plus 5 seconds, and `work_wait` gets its requested wait plus 30 seconds (`const.go::toolExecutionTimeout`). **Synthesis:** tool-specific slack lets a tool report its own structured timeout before the wrapper cancels it.[^weknora]

## Tool surface and evidence

**Observed:** `internal/agent/tools/capabilities.go::ToolCapabilityRequirements` ties tools to vector, keyword, wiki, graph, or FAQ capabilities. Document readers are auxiliary: they should not themselves pull wiki-only bases into a RAG scope. The file warns that its capability map must remain synchronized with the frontend map; synchronization was not independently established in this pass.[^weknora]

The engine has suspension/resume hooks and cancellation salvage paths, but the approval, HITL, collaboration, tool decoding, and compaction implementations were not fully reviewed. Test names such as `TestWithinIterationBudgetUnlimited` and `TestExecuteLoopPromptsForAlternativeAfterRepeatedFailedToolCall` were inspected; **no tests were run**. Their presence is not evidence that the runtime behavior passes.[^weknora]

## Relationships

- Uses [skills and session sandboxes](weknora-skills-sandboxes.md) for executable work.
- Uses [cross-session memory](weknora-memory.md) for resident context and on-demand recall.
- Uses the shared knowledge pipeline described by [WeKnora](weknora.md); the automatic wiki is a separate [compilation workflow](weknora-wiki-compilation.md).

## Coverage limits

Static, selected-section inspection only. Tool act/observe implementations, approval correctness, model-provider behavior, and concurrent turn races remain pending; see the [source map](weknora-source-map.md). No end-to-end agent execution or token/cost measurement was performed.

[^weknora]: Snapshot `fd7a2586fd58`: `internal/agent/engine.go::AgentEngine`, `Execute`, `executeLoop`, `runReActIteration`, `withinIterationBudget`, `loopGuards.recordFailedToolCall`, `drainSteerMessages`; `internal/agent/const.go::DefaultAgentMaxIterations`, `defaultLLMStallTimeout`, `maxEmptyResponseRetries`, `maxRepeatedResponseRounds`, `maxConsecutiveFailedToolCalls`, `maxConsecutiveLengthRounds`, `toolExecutionTimeout`; `internal/agent/tools/capabilities.go::ToolCapabilityRequirements`, `documentReaderRequirement`; test-name inventories in `internal/agent/engine_test.go` and `failed_tool_loop_test.go`. Canonical package entry: [README](../raw/WeKnora/README.md), “Overview” and “Features.”
