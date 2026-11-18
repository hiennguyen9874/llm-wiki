---
type: Concept
title: Pydantic AI IPython Code Mode
description: Local IPython-backed tool execution, kernel lifecycle, host security boundaries, and differences from Monty CodeMode.
tags: [pydantic-ai, agents, python, sandboxing]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:37:16Z }
stale_after: 2027-02-18
sources:
  - id: ipython-code-mode-docs
    resource: ../raw/ipython-code-mode/index.md
    scope: ../raw/ipython-code-mode/
    kind: documentation
    revision: sha256:3bff0e55bb623650df2acb61d8cdfd7adea8913b344d663550a57c6c6ca1e974
    title: IPython Code Mode
---

**Reported, Pydantic AI and Harness versions unspecified:** `IPythonCodeMode` exposes a `run_code` tool backed by a persistent IPython kernel, with selected agent tools available as Python functions. It runs full CPython with the agent process's permissions, **not in a sandbox**. Use it for trusted local agents; do not expose it to other users without isolating the agent itself. For the restricted Monty alternative, see [CodeMode operations](pydantic-ai-code-mode-operations.md).[^ipython-code-mode-docs]

## Setup and security boundary

**Reported, versions unspecified:** install `pydantic-ai-harness[ipython]` and add `IPythonCodeMode()` to `Agent(..., capabilities=[...])`. The Jupyter `ipykernel` process can use installed packages, shell escapes, IPython magics and top-level `await`, and access the host filesystem, network and environment. A kernel normally uses the agent's interpreter; a custom IPython `kernel_name` can select another environment. On Windows, kernel communication uses unencrypted local TCP ports which other machine users can connect to; Unix uses sockets in the temporary directory.[^ipython-code-mode-docs]

**Reported, versions unspecified:** unlike Monty `CodeMode`, IPython has no `mount`, `os_access` or `resource_limits` boundary, no eager or speculative execution, and no `dynamic_catalog`. It does not support Temporal, DBOS or Prefect durable execution: such a run raises `UserError` before executing code. Its tool calls are synchronous and serial, rather than async concurrent calls. A timeout limits code execution, not the privileges of code or the runtime of a called tool.[^ipython-code-mode-docs]

## Tool calls and outputs

**Reported, versions unspecified:** `tools='all'` selects eligible regular tools by default; names, a predicate or metadata can narrow selection. Unselected tools remain native, as do framework controls, undiscovered tools, native fallbacks and other code-execution tools. Non-identifier tool names are normalized to Python names; builtin collisions raise `UserError`. Kernel functions accept keyword-only arguments and dispatch one at a time over Jupyter stdin through Pydantic AI validation, capability hooks and approval or deferral handlers. Failures raise catchable `ToolCallError`.[^ipython-code-mode-docs]

**Reported, versions unspecified:** `max_tool_calls=100` limits nested calls per `run_code`; nested calls and the outer call also count against the run's `tool_calls_limit`. `ToolReturn.return_value` goes to the code and its `content` to the model in call order; nested calls and returns are recorded in result metadata. The final expression returns JSON data when possible or `repr` otherwise. Printed output and non-image displays are combined, capped at 10 MiB per call; displayed or returned images are passed to the model. No result or output returns `{}`. `input()` returns an empty string.[^ipython-code-mode-docs]

## State, errors and lifecycle

**Reported, versions unspecified:** a kernel starts lazily on the first `run_code` call and normally shuts down at run end. State persists between calls; `restart: true` clears it. An application can provide `IPythonKernel` to share state across runs and must manage its lifecycle with `async with` or `shutdown()`. Shared kernels serialize cells and are bound to their starting event loop. `cwd` defaults to the inherited working directory and `startup_timeout` to 60 seconds.[^ipython-code-mode-docs]

**Reported, versions unspecified:** code exceptions return a model retry with traceback and printed output, retaining prior state; `max_retries` defaults to 3. The default 60-second per-call timeout excludes time in tools. It interrupts code with `KeyboardInterrupt`; if the code does not stop within another five seconds the kernel is shut down and the next call starts fresh. A crashed kernel likewise loses state. `timeout=None` removes the time limit. The documentation reports a Python 3.14 output-lock bug that can turn interrupts during printing into kernel shutdowns; it states Python 3.11–3.13 are unaffected and 3.15 fixes it. The reported roughly 3% figure concerns a tight-printing-loop scenario, not all interrupts.[^ipython-code-mode-docs]

**Reported, versions unspecified:** the capability emits no spans of its own; core instrumentation records `run_code` and nested tool calls, while retries report timeouts, crashes and restarts.[^ipython-code-mode-docs]

## Evidence and coverage

The sole local artifact, `index.md`, is a Pydantic vendor documentation capture inspected as text; its inline flowchart repeats the prose. It names no Pydantic AI or Harness release, publication or capture date, author, or license; Harness 0.x APIs may change between minor releases. The external source repository, linked documentation and CPython issue were not fetched. No package, example, kernel, timeout, operating-system transport or instrumentation was executed, so behavior and the Python bug rate are vendor-reported, not independently verified.[^ipython-code-mode-docs]

## Relationships

- **Related:** [Pydantic AI CodeMode operations](pydantic-ai-code-mode-operations.md) covers the Monty alternative's restrictions, tool dispatch and durable replay.[^ipython-code-mode-docs]
- **Uses:** [Pydantic AI Harness](pydantic-ai-harness.md) supplies this capability.[^ipython-code-mode-docs]
- **Related:** [Pydantic AI durable execution](pydantic-ai-durable-execution.md) covers supported durability integrations; this IPython capability does not support them.[^ipython-code-mode-docs]

[^ipython-code-mode-docs]: [IPython Code Mode](../raw/ipython-code-mode/index.md), “Code Mode or IPython Code Mode”, “Installation”, “Selecting tools”, “Calling tools from code”, “Return values”, “Errors, timeouts, and restarts”, “The kernel”, “What carries over from Code Mode”, “Observability”, and “API reference”.
