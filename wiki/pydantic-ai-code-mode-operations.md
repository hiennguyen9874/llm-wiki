---
type: Concept
title: Pydantic AI CodeMode operations
description: CodeMode tool selection, execution limits, state, speculative execution, and Temporal replay boundaries.
tags: [pydantic-ai, agents, sandboxing]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:37:16Z }
stale_after: 2027-02-18
sources:
  - id: code-mode-docs
    resource: ../raw/code-mode/index.md
    scope: ../raw/code-mode/
    kind: documentation
    revision: sha256:74afcb21ea60bb2499a5665e428583b1fc950ddc8b160e383d9011e82c7c16e9
    title: Code Mode
---

**Reported, Pydantic AI and Harness versions unspecified:** `CodeMode` makes eligible tools callable from a model-written Python program in Monty, while the tools themselves retain host-side authority. The vendor documentation describes selection, resource and replay boundaries below; none was independently executed. For the performance tradeoffs, see [Pydantic AI code mode](pydantic-ai-code-mode.md).[^code-mode-docs]

## Selection and results

**Reported, version unspecified:** install `pydantic-ai-harness[codemode]` and add `CodeMode()` to the agent's capabilities. `tools='all'` selects eligible regular tools; names, predicates or metadata selectors narrow the selection, leaving others native. Control tools, undiscovered deferred tools and code-execution tools such as shell commands normally stay native. Deferred tools join the sandbox after discovery. With `dynamic_catalog=True`, the catalog is appended to instructions rather than rewriting the tool description, preserving the cached prefix when the selector's decision remains stable. Provider-native `bm25` and `regex` search have different declaration behavior and can still invalidate that prefix.[^code-mode-docs]

**Reported, version unspecified:** the final non-`None` expression is the result; an assignment alone returns `{}`. Printed output is surfaced separately; nested `ToolReturn.content` goes directly to the model rather than the sandbox. Uncaught nested `ToolFailed` ends the call as a failure; uncaught `ModelRetry` requests a retry. Approval or deferred tools need a capability that resolves them inline. Tool results generally use JSON-schema shapes, with binary values an exception; tools named after Python builtins are rejected.[^code-mode-docs]

## Limits, side effects and state

**Reported, version unspecified:** defaults are 30 seconds of sandbox execution per snippet, 256 MiB heap, 1,000 cumulative Monty suspensions per session and 100 nested tool calls per `run_code`. Awaiting a nested tool is excluded from execution time; sleep has a separate equal allowance. The agent's `tool_calls_limit` also counts nested calls and the outer call. Timeouts and worker failures can reset state; exhaustion or failure reports started calls but does not undo their effects or automatically replay them. Inspect partial results before retrying writes. Eager fragments have separate time and sleep allowances, so total eager execution can exceed a single ordinary snippet's allowance.[^code-mode-docs]

**Reported, version unspecified:** variables persist across snippets in an agent run; `restart: true` clears them. An optional `repl_store` loads and saves opaque state across runs, normally keyed by conversation ID, but is not used during durable execution. Dumps are unauthenticated: accept only application-saved state from protected storage. Incompatible resource limits or dumps cause a fresh REPL; load and save errors are warnings, not failed runs. Make saves atomic because timed-out thread work may still finish.[^code-mode-docs]

**Reported, version unspecified:** Monty has no default host filesystem, environment, clock or network access, but exposed tools can do host-side work. `mount` exposes host directories, not a remote workspace: its default `overlay` discards writes after each call, while `read-write` persists them. `os_access` answers OS requests; `os_policy` can configure clock behavior. Construct the capability per request when access differs. Sandbox access is not a substitute for authorizing tools.[^code-mode-docs]

## Eager and speculative execution

**Reported, version unspecified:** `eager=True` executes completed streamed statements early; `speculate` launches allowlisted or declared-read-only tools with literal keyword arguments ahead of use. Speculation can run even in untaken branches or for text in comments, and read-only calls can still cost money, leak arguments, or observe state too early. Unclaimed launches are extra work, capped at `max_tool_calls` and at most 32; they do not reserve the snippet's dispatch budget. Neither mechanism is active under durable execution. Hooks around the nested tool run at launch, but hooks and approvals around `run_code` occur too late to prevent early work. Measure end-to-end latency and cost: `hidden_ms` is not elapsed time saved.[^code-mode-docs]

## Remote workers and Temporal

**Reported, version unspecified:** `monty_sandbox` points to a remote Monty server root or a pool factory; the documentation requires server `pydantic-monty>=1.5.0`. Use TLS on untrusted networks and put authentication in the pool factory, not prompts. Only execution moves: tools, mounts, OS access and printed output remain in the application process. Configuration and checkout failures reach the caller rather than becoming model retries; execution failures can reset the session.[^code-mode-docs]

**Reported, version unspecified:** with `TemporalDurability`, `run_code` runs again in workflow replay while model requests and normally nested tools cross activity boundaries. A remote worker must be reachable during replay. Direct mount access, OS callbacks and host-clock reads recur during replay and can break determinism; place external reads, writes and clock access behind recorded tools. The snippet execution timer is disabled in Temporal, while memory and suspension limits remain; activity timeouts do not bound pure sandbox computation. Concurrent nested activity ordering can change after recovery; sequential execution avoids that ordering hazard. Eager execution and speculation are disabled.[^code-mode-docs]

## Evidence and coverage

The sole local artifact is the Pydantic documentation capture `index.md`, inspected as text; its diagram duplicates the prose. It gives no Pydantic AI or Harness version, publication or capture date, author or license, and warns Harness 0.x APIs may change between minor releases. External documentation, repository, trace and cited speculation article were not fetched; no package, example, worker or Temporal workflow was run. The API reference calls the discovery announcement a `SystemPromptPart`, whereas the guide calls it a `DiscoveryAnnouncementPart`; the precise part type is therefore unresolved in this capture.[^code-mode-docs]

## Relationships

- **Related:** [Pydantic AI IPython Code Mode](pydantic-ai-ipython-code-mode.md) describes the full-CPython, unsandboxed alternative and its different kernel lifecycle.
- **Uses:** [Pydantic AI Harness](pydantic-ai-harness.md) provides the capability.[^code-mode-docs]
- **Uses:** [Pydantic AI durable execution](pydantic-ai-durable-execution.md) supplies activity and replay boundaries for Temporal.[^code-mode-docs]
- **Related:** [Pydantic AI code mode](pydantic-ai-code-mode.md) covers the benchmark and workspace distinction.

[^code-mode-docs]: [Code Mode](../raw/code-mode/index.md), “Installation”, “Selective tool sandboxing”, “Tool Search interaction”, “Return values”, “Concurrent tool calls”, “REPL state”, “Eager execution”, “Speculative execution”, “Remote workers”, “Temporal durability”, “Filesystem and OS access”, “Sandbox restrictions”, and “API reference”.
