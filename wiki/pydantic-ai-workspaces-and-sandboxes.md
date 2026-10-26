---
type: Concept
title: Pydantic AI workspaces and sandboxes
description: ctx.workspace gives Pydantic AI tools one file-and-command API that runs locally or in a sandbox, including the sandbox list, the Daytona addition, and the execution constraints.
tags: [ml, pydantic-ai, agents, sandboxing]
status: stable
created: 2026-10-26
generated: { by: llm-wiki-agent/1, at: 2026-10-26T04:01:00Z }
stale_after: 2026-12-23
sources:
  - id: dd-v2-tour-2026
    resource: ../raw/pydantic-ai-whats-new-2026/index.md
    scope: ../raw/pydantic-ai-whats-new-2026/
    kind: article
    revision: 836bd3b1cd2de6726899f5766b8f3d40947bc044
    title: "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP"
---

`ctx.workspace`, added in v2.52.0 on 2026-09-29, gives a tool one API for files and commands regardless of where they run: on the local machine or inside a sandbox. The tool code does not change when the backend changes — swap `LocalWorkspace` for a sandbox and the same `ctx.workspace.run(...)` calls apply[^dd-v2-tour-2026]

## Shape of the API

`LocalWorkspace('.', read_only=False)` is attached as a [capability](pydantic-ai-capability-primitive.md). A tool then awaits `ctx.workspace.run([...], timeout=...)`, receives `exit_code`, `stdout` and `stderr`, and can convert a `WorkspaceError` into `ModelRetry` so the model gets a chance to correct itself[^dd-v2-tour-2026]:

```python
@agent.tool
async def run_tests(ctx: RunContext[object], path: str) -> str:
    """Run pytest on a path and return the tail of the output."""
    try:
        result = await ctx.workspace.run(['python', '-m', 'pytest', '-q', path], timeout=120)
    except WorkspaceError as e:
        raise ModelRetry(f'Could not run tests: {e}') from e
    return f'exit={result.exit_code}\n{result.stdout[-2000:]}'
```

Note the `RunContext[object]` annotation: under v2's generic default, `RunContext[None]` fails strict type checking on an agent without `deps_type`[^dd-v2-tour-2026]

## Sandbox catalogue

| Added | Backend |
| --- | --- |
| v2.52.0 | `E2BSandbox`, `SpritesSandbox`, `SSHWorkspace`, `BubblewrapSandbox` |
| v2.56.0 | `SmolSandbox`, a local smolvm microVM |
| v2.59.0 | `DaytonaSandbox`, running `Coder`, `Shell`, `FileSystem` and the other Harness capabilities in a Daytona sandbox |
| Harness | A Modal sandbox |

`SSHWorkspace` is the odd entry: it is a remote workspace reached over SSH rather than an isolated sandbox, so "sandbox" in the API name does not imply a security boundary for every backend[^dd-v2-tour-2026]

## Interaction with durable execution

Workspaces work under durable execution. Under DBOS, each workspace call becomes a step, and a run with a workspace executes its tool calls sequentially[^dd-v2-tour-2026] That sequencing is a real performance consequence for tools that could otherwise run in parallel, and it follows from replay requiring a deterministic order.

## Side effect: Anthropic token defaults

The same v2.52.0 release raised `AnthropicModel`'s default `max_tokens` on Claude Sonnet 4.5 and later, first to 16384 and then to the model's maximum output, streaming those requests behind the scenes. Anyone who relied on the old 4096 default to cap spend must now set `max_tokens` explicitly[^dd-v2-tour-2026]

## Limits

- No workspace or sandbox was executed in this ingest; the article's example was type-checked and run against `TestModel`, which exercises no filesystem[^dd-v2-tour-2026]
- The isolation properties of each backend — resource limits, network policy, credential exposure — are not described, so the security of running model-written commands in any of them is unverified here.
- The sequential-tool-call behaviour under DBOS is the author's reading of the DBOS docs, not an observed run.

## Relationships

- **Uses** the [capability primitive](pydantic-ai-capability-primitive.md): `LocalWorkspace` is a core capability.
- **Depends on** [durable execution](pydantic-ai-durable-execution.md) for step-level replay of workspace calls.
- **Related to** [Pydantic AI run controls](pydantic-ai-run-controls.md): explicit timeouts and token ceilings bound the same spend-and-latency problem.

[^dd-v2-tour-2026]: Developers Digest, "Pydantic AI V2 in Late 2026: Capabilities, Graphs, Evals and MCP", published 2026-10-17, last updated 2026-10-21, §"Workspaces: one API for local and sandboxed tools (v2.52)" (raw lines 330–357) for `ctx.workspace`, the `LocalWorkspace` capability, the `run_tests` sample, the sandbox list, the DBOS sequencing note, and the Anthropic `max_tokens` change; §"What changed in v2.58 and v2.59" for `DaytonaSandbox`. Local capture: `raw/pydantic-ai-whats-new-2026/index.md` (revision 836bd3b1). Evidence class: **Reported** — article-level description with an author-run `TestModel` sample; no sandbox, filesystem, or provider call was exercised here.
