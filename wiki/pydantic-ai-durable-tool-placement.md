---
type: Concept
title: Pydantic AI durable tool placement
description: How Pydantic AI decides which tool calls a durability engine wraps — the durable=False opt-out, its determinism and async-only rules, the per-engine placement table, and why moving a tool breaks in-flight runs.
tags: [pydantic-ai, agents, durability, tools]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T02:54:20Z }
stale_after: 2027-02-18
sources:
  - id: durable-exec-docs
    resource: ../raw/capabilities/durable_execution/overview/index.md
    scope: ../raw/capabilities/durable_execution/overview/
    kind: documentation
    revision: sha256:3601b2702b26f347d71e6b5a302b709d9bc87e177fba35c85eaaf7be1cf45333
    title: "Durable Execution"
  - id: pydantic-dbos-docs
    resource: ../raw/capabilities/durable_execution/dbos/index.md
    scope: ../raw/capabilities/durable_execution/dbos/
    kind: documentation
    revision: sha256:244a04f5850362a7fba71144476c4757655019e142a4e838712ae39035332862
    title: "Durable Execution with DBOS"
---

**Reported, Pydantic AI and Harness versions unspecified:** a durability engine runs each function tool call in a durable unit — an activity, step or task — so a restarted run reuses the result it recorded instead of calling the tool again. Setting `durable=False` moves a tool back into the workflow code, where it runs again on every replay and must therefore be deterministic. The setting is accepted on every engine, but where the tool then runs, whether the engine honours it, and what wins when other configuration disagrees, all differ per engine. The engines themselves are listed in [Pydantic AI durable execution](pydantic-ai-durable-execution.md).[^durable-exec-docs]

## What the default buys

By default an engine wraps each function tool call in a durable unit, and that wrapping is what makes recovery reuse a recorded result rather than repeat its side effect. The documented reasons to opt out are narrow: a tool that has to see live run state, or one that starts work which should be recorded step by step rather than as one unit.[^durable-exec-docs]

## Setting the flag

The flag sits where `sequential` and `timeout` sit — on `@agent.tool`, on `Tool(...)`, on `@toolset.tool`, or on a `FunctionToolset` to cover all of its tools. The tool then runs in workflow code and must be deterministic: no I/O, clock or randomness of its own. The documented sample is a `copy_file` tool in a `FunctionToolset` that still reaches the outside world, but through `ctx.workspace`, whose calls remain recorded units:[^durable-exec-docs]

```python
toolset = FunctionToolset(id='files')

@toolset.tool(durable=False)
async def copy_file(ctx: RunContext, source: str, destination: str) -> str:
    content = await ctx.workspace.read_bytes(source)
    await ctx.workspace.write_bytes(destination, content)
    return f'Copied {source} to {destination}.'
```

A run that restarts after the read reuses the recorded read and only performs the write, so a workspace call is the documented way to keep granular durability inside a tool that has opted out of its own unit.[^durable-exec-docs]

## Tools you do not define

Function tools owned by a capability are changed in a `prepare` function or with `PrepareTools`, replacing the `ToolDefinition` where its name matches. The same determinism rule applies, and for the same reason: the `prepare` function has to make the same choice when the run replays, so the documented form is a name test rather than state read at deployment time.[^durable-exec-docs]

## What cannot opt out

Only async function tools can leave their durable unit. On a sync tool, an MCP tool, or a dynamic toolset's tool that the engine would wrap, `durable=False` raises a `UserError` when the tool is called, because those run in a thread or perform I/O. DBOS is the exception in the other direction — it runs function tools in workflow code without wrapping them, so it does not check the field on them at all, which is why the documentation advises keeping an agent you might move to another engine on async tools.[^durable-exec-docs] The DBOS page adds that a tool's `metadata={'dbos': False}` is rejected on an MCP tool rather than running the call inline, and that tool metadata other than `child_workflow` is ignored outright, so the engine offers no per-tool opt-out to reach for.[^pydantic-dbos-docs]

## Where the tool lands, per engine

| Engine | Where `durable=False` runs the tool | Engine's own metadata key |
| --- | --- | --- |
| Temporal | workflow code | `'temporal'` |
| DBOS | workflow code, where DBOS already runs function tools, so the field isn't checked | none; `{'dbos': {'child_workflow': ...}}` selects a child workflow, and no per-tool step config or opt-out exists[^pydantic-dbos-docs] |
| Prefect | flow code | `'prefect'` |
| AWS Lambda | handler code, outside any step | `'aws_lambda'` |
| Azure Durable Task | orchestrator code | `'azure_durable_task'` |
| Absurd | task handler code, outside any step | none |
| pgtask | task code, outside any step | none |
| Render Workflows | the parent task run | `'render_workflows'`, whose `False` only lets a per-run toolset through; per tool, `resolve_tool_options` can return `False` |

Restate and Apache Airflow ship their own integrations, so the documentation defers their tool wrapping to those pages rather than to this table.[^durable-exec-docs]

## Which setting wins

Three precedence rules pull in different directions:[^durable-exec-docs]

- An engine's own metadata key wins over the tool: a tool with `durable=False` and `metadata={'temporal': ActivityConfig(...)}` still runs in a Temporal activity. The key also carries configuration `durable` cannot express, and follows the engine's own rules on which tools may opt out.
- `durable=True` undoes an earlier `durable=False`, but not an opt-out in the engine's own per-tool configuration, such as Temporal's `tool_activity_config`.
- `durable=False` does win over per-tool configuration set in code, such as Azure Durable Task's and Render Workflows' `resolve_tool_options`.

## The redeploy hazard

Changing a tool's placement on an agent that is already deployed adds or removes a durable unit on every engine except DBOS, so runs already in flight fail or diverge when they replay. The documented remedies are to let those runs finish or to deploy the change as a new version of the workflow. The `prepare`-function determinism rule is the same hazard seen from the replay side: the choice has to be reproducible, not evaluated once at deployment.[^durable-exec-docs]

## Evidence and coverage

The sole artifact is the Pydantic documentation capture `index.md`, inspected as text; there are no attachments, includes, downloads or supporting files. It names no Pydantic AI or Harness version, author, publication date or licence, and its samples pin `openai:gpt-6.1-sol`, a model name recorded nowhere else in this wiki. Every engine link (Temporal, DBOS, Prefect, Restate, AWS Lambda, Absurd, pgtask, Azure Durable Task, Airflow, Render Workflows), the backend-builder page, the batch and custom-capability pages and the workspace guide were read as links and not followed, so each engine's own wrapping, streaming and opt-out rules remain unverified here. Nothing was installed, no agent was made durable, no workflow was replayed and no tool was called, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule, and `stale_after` is set because the flag and the per-engine table are release-sensitive. A second capture, the DBOS integration page (4,754 words as declared, content digest sha256:244a04f5), was read for the DBOS row and the DBOS paragraph above; it names no version either and was likewise not executed, and its own full treatment is on [Pydantic AI on DBOS](pydantic-ai-dbos.md).[^pydantic-dbos-docs]

## Relationships

- **Constrains** [Pydantic AI durable execution](pydantic-ai-durable-execution.md): that page lists the engines and their shipping location; this one decides which call sites inside them are recorded as units.[^durable-exec-docs]
- **Applies to** [Pydantic AI workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md): an opted-out tool's workspace calls are still recorded separately, so a workspace preserves durable granularity that the tool itself gave up.[^durable-exec-docs]
- **Extends** the [capability primitive](pydantic-ai-capability-primitive.md): tools a capability defines are re-placed from a `prepare` function or `PrepareTools`, and capability hook work can move into engine activities as durable capability operations.[^durable-exec-docs]
- **Related to** [Pydantic AI CodeMode operations](pydantic-ai-code-mode-operations.md): `run_code` re-executes on replay while the tools nested inside it cross unit boundaries, which is the same placement question for model-written code.
- **Is specialised for one engine in** [Pydantic AI on Temporal](pydantic-ai-temporal.md): what Temporal's own `'temporal'` metadata value accepts, including per-tool activity configuration and the child-workflow route, and why it wins over `durable=False`.[^durable-exec-docs]
- **Is specialised for a second engine in** [Pydantic AI on DBOS](pydantic-ai-dbos.md): DBOS wraps MCP and dynamic toolsets but never application function tools, so its opt-out surface is the `@DBOS.step` decorator rather than a per-tool setting.[^pydantic-dbos-docs]

[^durable-exec-docs]: Pydantic, "Durable Execution" (docs.pydantic.dev, `/docs/ai/capabilities/durable_execution/overview/`), 1,028 words as declared; local capture `raw/capabilities/durable_execution/overview/index.md`, content digest sha256:3601b270. Opening paragraphs for the default durable unit per function tool call, the per-engine difference in which tools are wrapped and how streaming is delivered, and the narrow cases where opting out is intended; "Running a tool outside the durable unit" for the four places `durable=False` is accepted, the determinism requirement, the `durable_opt_out.py` `copy_file` sample and its workspace-call commentary, the `PrepareTools`/`prepare` route for tools defined elsewhere, the `durable=True` and engine-metadata-key precedence rules, the async-only rule with the sync/MCP/dynamic-toolset `UserError`, the DBOS non-checking exception, the per-engine placement table including Render Workflows and the deferral for Restate and Airflow, and the redeploy hazard. Evidence class: **Reported** — vendor reference page naming no version; no engine, workflow, activity or tool was exercised.
[^pydantic-dbos-docs]: Pydantic, "Durable Execution with DBOS" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/dbos/`), 4,754 words as declared, no version or date stated; local capture `raw/capabilities/durable_execution/dbos/index.md`, content digest sha256:244a04f5. §"Agent and Toolset Requirements" (raw lines 161–186) for MCP tools always running in their step, the rejection of `metadata={'dbos': False}` on an MCP tool, and the unwrapped application function tools with the `@DBOS.step` decision; §"Step Configuration" (336–347) for the absent per-tool step config, the ignored tool metadata other than `child_workflow`, and the decorators' no-op nature outside DBOS workflows. Evidence class: **Reported** — vendor reference page naming no version; nothing was installed or executed.
