---
type: Concept
title: Pydantic AI tool execution, retries and failures
description: What happens once a Pydantic AI model calls a tool — Pydantic argument validation answered as a retried result, ModelRetry versus ToolFailed, the seven-layer retry precedence and per-tool counters, validators that can defer to a human, timeouts, and parallel calls with their sequential barrier and thread executor.
tags: [pydantic-ai, agents, tools, reliability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:35:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-docs-tool-search-capability
    resource: ../raw/capabilities/tool-search/index.md
    scope: ../raw/capabilities/tool-search/
    kind: documentation
  - id: pydantic-docs-timeouts
    resource: ../raw/core-concepts/timeouts/index.md
    scope: ../raw/core-concepts/timeouts/
    kind: documentation
    revision: sha256:f05691956599cfeccf1de6aa3383a528e516d06310baf5db2d282edda7bd852f
    title: "Timeouts"
    revision: sha256:d7e51e0a242bd9c822cd13fd2f6eb207b5cedc8f5f3ce03e1cab958b55c0fe42
    title: "Tool Search"
---

**Reported, Pydantic AI version unspecified:** a tool call has three distinct fates in Pydantic AI and the framework tells them apart by exception type — a `ValidationError` or `ModelRetry` answers the call with a **retried** result that consumes the tool's retry budget, a `ToolFailed` answers it with a **failed** result that does not, and any other exception leaves the agent run entirely[^pydantic-docs-tools-advanced] The doctrine is one sentence: raise `ModelRetry` when the model should try again with corrections, raise `ToolFailed` when the call is done and the result is a failure[^pydantic-docs-tools-advanced] Around that sit two mechanics that decide how a real agent behaves — retry budgets resolve through seven precedence layers and are counted **per tool**, and parallel tool calls run concurrently unless one declares itself a barrier[^pydantic-docs-tools-advanced]

## Argument validation and the retried result

Tool arguments are validated against the function signature with Pydantic, with the optional [validation context](pydantic-ai-structured-output.md) that output types also accept[^pydantic-docs-tools-advanced] A failure — wrong type, missing required argument — raises a `ValidationError` inside the framework, which answers the call with a `ToolReturnPart` carrying the validation details and `outcome='retried'`, sent back to the model on the provider's error channel so it can correct the arguments[^pydantic-docs-tools-advanced]

The exception choice at that point is the whole failure contract[^pydantic-docs-tools-advanced]:

- `ModelRetry` — the model should try the tool call again with corrected arguments or a different approach.
- `ToolFailed` — the call should be reported as failed without consuming the tool's retry budget.
- Anything else — propagates out of the agent run and is never shown to the model.

## Retry budgets

`ModelRetry` and `ValidationError` share the configured retry limit, which can be set per tool (`Tool(max_retries=N)` or `@agent.tool(retries=N)`), per toolset (`FunctionToolset(max_retries=N)`), or agent-wide (`Agent(retries={'tools': N})`), applied in that order of precedence[^pydantic-docs-tools-advanced] The agent-wide default can be overridden per run through `agent.run(retries=…)` — and `run_sync`, `run_stream`, `iter`, or a block of runs via `agent.override()` — where the per-run value replaces the agent-wide default at the bottom of the chain but never beats an explicit per-tool or per-toolset limit; a bare `int` at those call sites sets both budgets, while a dict such as `{'tools': N}` or `{'output': N}` changes one[^pydantic-docs-tools-advanced]

Retries are tracked **per tool**: every function tool has its own counter and there is no global tool-call budget across the run, so a `ModelRetry` from one tool does not consume another's[^pydantic-docs-tools-advanced] Inside a tool, `ctx.max_retries` is that tool's enforcement limit and `ctx.retry` its counter, and a tool's `prepare` function reads the same counter even when its toolset is prefixed or renamed — unless `prepare` renames the tool itself, in which case it reads the counter for the name the tool would otherwise have[^pydantic-docs-tools-advanced] Exhaustion raises `UnexpectedModelBehavior` with a message naming the tool and limit and pointing at the retry documentation[^pydantic-docs-tools-advanced] User-provided toolsets inherit the agent-wide default, or its per-run override, when they set no value of their own[^pydantic-docs-tools-advanced]

Framework-supplied tools that take a structured argument are on the same ladder: the local `search_tools` tool that [tool search](pydantic-ai-tool-search.md) falls back to spends the agent's tool budget, so `Agent(retries={'tools': N})` is `N` attempts to correct a malformed `queries` argument — but a search that legitimately matches nothing is a successful call and never spends a retry[^pydantic-docs-tool-search-capability]

### Which limit wins

Two independent budgets — the **tool** budget (per function or output tool) and the **output** budget (output validation) — resolve through the same seven layers, first setter wins[^pydantic-docs-tools-advanced]:

| Precedence | Set by | Applies to |
| --- | --- | --- |
| 1 | Per-tool limit — `@agent.tool(retries=N)`, `Tool(max_retries=N)`, `ToolOutput(max_retries=N)` | That one tool |
| 2 | Per-toolset limit — `FunctionToolset(max_retries=N)`, `MCPToolset(max_retries=N)` | Tools in that toolset |
| 3 | Override block — `agent.override(retries=…)` | Tool and/or output |
| 4 | Per-run argument — `agent.run(retries=…)` | Tool and/or output |
| 5 | Per-run spec — `agent.run(spec={'retries': …})` | Tool and/or output |
| 6 | Agent-wide default — `Agent(retries=…)` | Tool and/or output |
| 7 | Built-in default | `1` |

At layers 3–6 a bare `int` sets both budgets while an `AgentRetries` dict sets only the keys it names[^pydantic-docs-tools-advanced]

## ToolFailed

`ToolFailed` is for the complete-but-unsuccessful call: the resource does not exist, the operation is not supported, the upstream service returned a definitive error[^pydantic-docs-tools-advanced] The documented sample raises `ToolFailed(f'File not found: {path}')` after an `is_file()` check[^pydantic-docs-tools-advanced]

What it produces[^pydantic-docs-tools-advanced]:

- A `ToolReturnPart` with `outcome='failed'` in message history.
- The model API's native error or failed-status field where one exists; where it does not, content JSON-framed as `{"error": …}` so the failure is still explicit.
- An error-status span in telemetry.
- No consumption of the per-tool retry budget. Bounding repeated failures is the job of `UsageLimits` at run level — specifically `request_limit`, because `tool_calls_limit` counts only successful invocations.

Two qualifications matter. The failed outcome survives in Pydantic AI history, but protocol adapters may need their own carrier when that history is round-tripped — the page cites AG-UI's preserving-failed-tool-outcomes note[^pydantic-docs-tools-advanced] And the handling is narrower than `ModelRetry`'s: `ToolFailed` is honoured for function tools, their `args_validator`, and tool validation or execution hooks, plus a tool that [Code Mode](pydantic-ai-code-mode.md) calls from a snippet (reported as a failed `run_code` result); for output functions and output validators it is an ordinary exception that aborts the run unless an output-process error hook recovers from it[^pydantic-docs-tools-advanced]

Either exception may also be raised from tool validation and execution hooks, which is the documented way to convert a third-party exception once instead of in every tool[^pydantic-docs-tools-advanced] MCP server tool errors offer the same choice as the `tool_error_behavior` setting recorded in [MCP client](pydantic-ai-mcp-client.md)[^pydantic-docs-tools-advanced]

## Timeouts

`Agent(tool_timeout=N)` sets a default per-tool deadline and `@agent.tool(timeout=N)` overrides it for one tool[^pydantic-docs-tools-advanced] A timeout is treated as a retryable failure: the model receives a retried result reading `Timed out after {timeout} seconds.` and the tool's retry limit is consumed like a validation error or an explicit `ModelRetry`[^pydantic-docs-tools-advanced]

Both settings are enforced by `FunctionToolset`, which backs an agent's own tools[^pydantic-docs-tools-advanced] Tools served by an MCP server, an external toolset, or a custom `AbstractToolset` **do not read them**, so their deadlines belong at the server or transport level[^pydantic-docs-tools-advanced] How a tool deadline relates to the other deadlines in a run is covered by [run controls](pydantic-ai-run-controls.md)[^pydantic-docs-tools-advanced]

Two properties of the deadline are easy to miss, and both come from the timeouts page rather than from this one[^pydantic-docs-timeouts]:

- **A `def` tool is not actually stopped.** The deadline is enforced around the await, so the worker thread runs to completion and its side effects land after the model has already been told the call timed out.
- **A `TimeoutError` you raise yourself is indistinguishable from expiry.** With a timeout configured, the call runs inside `anyio.fail_after(timeout)`, which signals its own expiry the same way, so a self-raised `TimeoutError` becomes the same `'Timed out after N seconds.'` retried result and reports a deadline that may never have passed. Catch it and re-raise `ModelRetry` or `ToolFailed` instead; with no timeout on the tool or its toolset, a bare `TimeoutError` is an ordinary exception that propagates out of the run unless a capability implementing `on_tool_execute_error` converts it.
- **A toolset's own timeout is separate from the agent's.** `Agent(tool_timeout=...)` does not reach a `FunctionToolset` you constructed and passed via `toolsets=[...]`; give that toolset its own `FunctionToolset(timeout=...)` or set `timeout=` per tool.

## Cancelling a run from a tool

`RunContext.cancel()` aborts the whole run from inside a tool, and from outside any run method accepts a `CancellationToken`; either way the caller sees `RunCancelled`[^pydantic-docs-tools-advanced] The consequences are worth stating precisely[^pydantic-docs-tools-advanced]:

- Async tool tasks running in parallel are cancelled and drained.
- Python cannot forcibly stop a synchronous tool's worker thread: cancellation may wait for the worker or let it finish in the background, and either way its result is discarded while its side effects remain.
- Tool calls that already completed keep their results in history, and a call that never produced a result is repaired automatically when that history is reused — the repair path recorded in [history repair](pydantic-ai-history-repair.md).
- Both cancellation surfaces require being in the same process as the run, so they do not cross a [durable execution](pydantic-ai-durable-execution.md) serialization boundary such as a Temporal activity.

## Argument validators

`args_validator` adds a validation step between schema validation and execution, for business rules, cross-field checks, or deciding about [human approval](pydantic-ai-deferred-approvals.md) before anyone is asked[^pydantic-docs-tools-advanced] Its signature is `RunContext` first, then the same parameters as the tool, and its outcomes are the failure vocabulary of this page plus two deferral signals[^pydantic-docs-tools-advanced]:

| Returns or raises | Effect |
| --- | --- |
| `None` | Valid; the tool proceeds |
| `ModelRetry` | The model is asked to correct the arguments; the tool's retry budget is consumed |
| `ToolFailed` | The model receives a failed result it should adapt to; the retry budget is untouched |
| `ApprovalRequired` / `CallDeferred` | The call is deferred — the tool does not run and no budget is consumed |

The placement is the design point: validation runs **before** approval is requested, so the model can fix bad arguments without bothering the user, and for deferred tools validation runs at deferral time, so only calls with valid arguments are deferred[^pydantic-docs-tools-advanced] A validator that defers joins the run's other deferred calls — resolved inline by a `HandleDeferredToolCalls` handler or surfaced in `DeferredToolRequests` — and, once the call is approved, **runs again** with `RunContext.tool_call_approved` set to `True` before the tool executes[^pydantic-docs-tools-advanced] The documented `validate_transfer` sample shows both branches: an impossible amount raises `ModelRetry` and the model fixes it, while a large-but-possible amount raises `ApprovalRequired` and reaches a human[^pydantic-docs-tools-advanced]

The parameter is available on `@agent.tool`, `@agent.tool_plain`, `Tool`, `Tool.from_schema` and `FunctionToolset`, and validators may be sync or async[^pydantic-docs-tools-advanced] Under durable execution a tool with a validator gains a dedicated validation activity, step or task wherever the engine wraps that toolset — it may perform I/O and can retry, fail or defer — while a tool without one schedules no extra durable unit[^pydantic-docs-tools-advanced] The combined result is exposed as `args_valid` on `FunctionToolCallEvent`: `True` passed, `False` failed, `None` not performed, as with calls skipped by the `'early'` end strategy or deferred calls resolved without execution[^pydantic-docs-tools-advanced]

## Parallel tool calls

When a response carries several tool calls, Pydantic AI schedules them concurrently with `asyncio.create_task`, in the order the model emitted them[^pydantic-docs-tools-advanced] Marking one tool `sequential=True` makes it a barrier: tools emitted before it finish first, it runs alone, and tools emitted after it start only once it finishes[^pydantic-docs-tools-advanced] The documented `fetch_record`/`write_to_database` sample prints the two calls in order because the write is sequential and the fetch is not[^pydantic-docs-tools-advanced]

The same barrier is available for output tools via `ToolOutput(sequential=True)`, for a whole run through the `with agent.parallel_tool_call_execution_mode('sequential')` context manager, or by setting `parallel_tool_calls=False` in model settings[^pydantic-docs-tools-advanced]

Async functions run on the event loop and sync functions are offloaded to threads, so the documented performance advice is to *always* use an async function unless the work is blocking I/O with no non-blocking library available, or CPU-bound[^pydantic-docs-tools-advanced]

### The thread executor

By default sync functions go through `anyio.to_thread.run_sync`, which creates ephemeral threads on demand — and in a long-running server under sustained traffic those threads can accumulate into memory growth[^pydantic-docs-tools-advanced] Two documented ways to bound them[^pydantic-docs-tools-advanced]:

- **Per agent:** the `UseThreadExecutor(executor)` capability with a bounded `ThreadPoolExecutor(max_workers=16, thread_name_prefix=…)`.
- **Globally:** `Agent.using_thread_executor(executor)` around a server lifespan, shutting the pool down with `shutdown(wait=True)`.

### Output calls and end_strategy

A final result can arrive in parallel with other tools, and the agent's `end_strategy` decides what still executes[^pydantic-docs-tools-advanced] The default `'graceful'` runs every function tool even after a final result is found while skipping remaining output tools; `'exhaustive'` also executes all output tools[^pydantic-docs-tools-advanced] Both exist for tools with side effects — logging, notifications, metrics — that must always run, and the strategy's full behaviour with function tools, output tools and non-tool output is recorded in [structured output](pydantic-ai-structured-output.md)[^pydantic-docs-tools-advanced]

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, default, error message and precedence layer here is version-unknown, and its samples pin `openai:gpt-6.1-sol` and `google:gemini-3.8-flash`, which no other capture here corroborates. Every external link — the `ModelRetry`, `ToolFailed`, `Tool`, `ToolDefinition`, `FunctionToolset`, `Agent`, `Agent.retries`, `AgentRetries`, `Agent.override`, `RunContext.max_retries`, `RunContext.retry`, `RunContext.cancel`, `RunContext.tool_call_approved`, `CancellationToken`, `UnexpectedModelBehavior`, `UsageLimits`, `AbstractToolset`, `UseThreadExecutor`, `HandleDeferredToolCalls` and `FunctionToolCallEvent` API pages, the hooks, timeouts, output, deferred-tools, MCP client, AG-UI, durable-execution and Code Mode pages, and issue #10435 — was read as a link, not followed. Nothing was installed, no tool registered or called, no retry exhausted, no timeout induced, no run cancelled and no concurrency measured, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because retry defaults, the precedence chain and the cancellation surfaces are release-sensitive.

## Relationships

- **Takes its definitions from** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md): a `from_schema` tool has no argument validation, a `strict` tool fails a violation during generation, and `prepare` reads the same per-tool retry counter this page enforces.
- **Owns the function-tool half of** [Pydantic AI structured output](pydantic-ai-structured-output.md): output functions and output validators use `ModelRetry`, treat `ToolFailed` as fatal, and share the output budget in this page's precedence table.
- **Defers through** [Pydantic AI deferred tool approval](pydantic-ai-deferred-approvals.md): an `args_validator` may raise `ApprovalRequired` or `CallDeferred`, and it runs a second time after approval with `tool_call_approved` set.
- **Repairs its interrupted calls with** [Pydantic AI history repair](pydantic-ai-history-repair.md), which synthesizes the tool return a cancelled run never wrote.
- **Is bounded by** [Pydantic AI run controls](pydantic-ai-run-controls.md) for `usage_limits`, `request_limit` and the run and request deadlines a tool timeout nests inside.
- **Has its deadline mapped at** [Pydantic AI timeouts](pydantic-ai-timeouts.md), which owns the per-unit table this page's `## Timeouts` section only enters one row of, along with the `anyio.fail_after` indistinguishability and the `def`-tool-runs-to-completion rule.
- **Differs on MCP tools at** [Pydantic AI MCP client](pydantic-ai-mcp-client.md): `tool_error_behavior` chooses between a retried and a failed result, and neither `tool_timeout` nor a per-tool limit is read by a remote toolset.
- **Gains a durable unit from** [Pydantic AI durable execution](pydantic-ai-durable-execution.md) when a validator is present, and loses cross-activity cancellation there.
- **Leaves its rejected calls in** [retry records in message history](pydantic-ai-retry-history.md), which owns the `RetryInfo` audit fields on the retried part this page creates, the framework-side causes that reach no tool hook, and the `is_retry`/`ERROR_OUTCOMES` queries over a stored history.
- **Contributes two terms to** [retry layers and multiplication](pydantic-ai-retry-layers.md): every retried tool call is another model request, and its follow-up request carries the SDK and transport attempt budgets beneath it.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Tool Execution, Retries, and Failures" (raw lines 556–566) for argument validation, the retried `ToolReturnPart`, and the `ModelRetry`/`ToolFailed`/propagate rule; §"Requesting a Tool Retry" (567–585) for the retry-limit setters and precedence, `ctx.max_retries`/`ctx.retry`, the `prepare` counter rule, `UnexpectedModelBehavior` and toolset inheritance; §"Which retry limit wins" (586–601) for the seven-layer table and the `int`-versus-`AgentRetries` rule; §"Reporting a Failed Tool Result" (602–627) for the `outcome='failed'` result, the native versus `{"error": …}` carrier, the AG-UI caveat, the telemetry error, the `UsageLimits` bound, the hook and Code Mode handling and the output-function exception; §"Tool Timeout" (628–658) for `tool_timeout`, per-tool `timeout`, the retried result text and the `FunctionToolset` scope; §"Cancelling the Run from a Tool" (659–664) for `RunContext.cancel`, `CancellationToken`, `RunCancelled`, the drained tasks, the worker-thread caveat and the same-process limit; §"Custom Args Validator" (665–755) for the signature, the four outcomes, pre-approval placement, the `validate_sum_limit` and `validate_transfer` samples, the deferral re-run, the registration surfaces, the durable unit and `args_valid`; §"Parallel tool calls & concurrency" (756–803) for `asyncio.create_task`, the `sequential=True` barrier, the sample, the run-wide switches and the async-versus-thread advice; §"Thread executor for long-running servers" (804–829) for the ephemeral-thread growth and the `UseThreadExecutor`/`using_thread_executor` remedies; §"Output Tool Calls" (830–835) for `end_strategy`. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.

[^pydantic-docs-tool-search-capability]: Pydantic Docs, "Tool Search" (<https://pydantic.dev/docs/ai/capabilities/tool-search/>; 213 words as declared, 252 by local `wc -w`; no publication date, author or Pydantic AI version); local capture `raw/capabilities/tool-search/index.md`, content digest sha256:d7e51e0a. Line 26 only, for the local `search_tools` tool's retry budget following the agent's tool budget, the `Agent(retries={'tools': N})` reading as attempts to correct a malformed `queries` argument on the same precedence ladder, and a no-match search returning normally without spending a retry. Evidence class: **Reported** — vendor documentation naming no version or date; no search was run.

[^pydantic-docs-timeouts]: Pydantic Docs, "Timeouts" (<https://pydantic.dev/docs/ai/core-concepts/timeouts/>; no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/timeouts/index.md`, content digest sha256:f0569195. §"Bounding how long a step takes" (raw lines 15–27) for the tool row of the unit/setting/on-expiry table — `Agent(tool_timeout=...)` or a per-tool `timeout=`, enforced by `FunctionToolset`, answered with the retried `'Timed out after N seconds.'` result and a spent retry budget; lines 36–43 for the `def` tool whose worker thread runs to completion past the deadline, the `anyio.fail_after(timeout)` indistinguishability of a self-raised `TimeoutError`, the `on_tool_execute_error` recovery when no timeout is configured, and `Agent(tool_timeout=...)` not reaching a `FunctionToolset` passed via `toolsets=[...]`. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
