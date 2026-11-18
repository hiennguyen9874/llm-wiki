---
title: "Durable Execution"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/"
domain: "pydantic.dev"
language: "en"
description: "Add durable execution to Pydantic AI agents so runs survive crashes, restarts and API failures, using Temporal, DBOS, Prefect, Restate or another engine."
word_count: 1028
---

Pydantic AI agents run durably, surviving crashes and restarts, on Temporal, DBOS, Prefect, Restate, AWS Lambda, Absurd, pgtask and Apache Airflow.

Use durable execution in production when a run in flight has to survive its process stopping, through a deploy, a crash or a transient API failure, or when a workflow waits hours or days for a person or another system. A durable engine journals the agent’s model requests and the tool calls it wraps, and a restarted run replays the completed ones from the journal and retries the one in flight. Which tool calls (function tools, [MCP](https://pydantic.dev/docs/ai/mcp/client/) servers) an engine wraps for you and how it delivers [streaming](https://pydantic.dev/docs/ai/core-concepts/agent/#streaming-all-events) differ per engine; each page below says.

Pydantic AI supports nine durable execution engines, plus a [builder](https://pydantic.dev/docs/ai/capabilities/durable_execution/backends/) for any other engine. Each page below has a complete example:

| Engine | Install | Make an agent durable with |
| --- | --- | --- |
| [Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/) | `pydantic-ai-slim[temporal]` | `TemporalDurability` from `pydantic_ai.durable_exec.temporal` |
| [DBOS](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/) | `pydantic-ai-slim[dbos]` | `DBOSDurability` from `pydantic_ai.durable_exec.dbos` |
| [Prefect](https://pydantic.dev/docs/ai/capabilities/durable_execution/prefect/) | `pydantic-ai-slim[prefect]` | `PrefectDurability` from `pydantic_ai.durable_exec.prefect` |
| [Restate](https://pydantic.dev/docs/ai/capabilities/durable_execution/restate/) | `restate_sdk[serde]` | `RestateAgent` from `restate.ext.pydantic` |
| [AWS Lambda](https://pydantic.dev/docs/ai/harness/aws-lambda/) | `pydantic-ai-harness[aws-lambda]` | `AWSLambdaDurability` from `pydantic_ai_harness.aws_lambda` |
| [Absurd](https://pydantic.dev/docs/ai/harness/absurd/) | `pydantic-ai-harness[absurd]` | `AbsurdDurability` from `pydantic_ai_harness.absurd` |
| [pgtask](https://pydantic.dev/docs/ai/harness/pgtask/) | `pydantic-ai-harness[pgtask]` | `PGTaskDurability` from `pydantic_ai_harness.pgtask` |
| [Azure Durable Task](https://pydantic.dev/docs/ai/harness/azure-durable-task/) | `pydantic-ai-harness[azure-durable-task]` | `AzureDurableTaskDurability` from `pydantic_ai_harness.azure_durable_task` |
| [Apache Airflow](https://pydantic.dev/docs/ai/capabilities/durable_execution/airflow/) | `apache-airflow-providers-common-ai` | `AgentOperator(..., durable=True)` from `airflow.providers.common.ai.operators.agent` |

Temporal, DBOS, Prefect, Restate, and AWS Lambda are co-maintained by the Pydantic and vendor teams. AWS Lambda, Absurd, pgtask, and Azure Durable Task ship in [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/); Restate and Airflow ship in the engine’s own package.

[Batched model requests](https://pydantic.dev/docs/ai/core-concepts/batch/#durable-execution) are recorded differently on each engine: see that section before batching under durable execution.

Capability authors can also move custom hook work into engine activities, steps, or tasks with [durable capability operations](https://pydantic.dev/docs/ai/capabilities/custom/#durable-capability-operations).

[Append-on-change instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) derive their baseline and replacements from persisted history. Instruction callbacks still follow the engine’s replay rules: use a durable operation for external reads so replay uses the same values and produces the same history shape.

Third-party runtime authors can use the stable [durable execution backend builder](https://pydantic.dev/docs/ai/capabilities/durable_execution/backends/) to integrate another engine without importing Pydantic AI internals.

Harness workspace capabilities such as `Coder`, `Shell`, and `FileSystem` also run inside a durable agent; the [workspace guide](https://pydantic.dev/docs/ai/core-concepts/workspace/#durable-execution) shows how, and what works on each engine.

## Running a tool outside the durable unit

An engine runs each function tool call in a durable unit (an activity, step or task) so a restarted run reuses its recorded result. To run a tool in the workflow code itself instead, set [`durable=False`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition.durable) on it, as you would `sequential` or `timeout`: on `@agent.tool`, `Tool(...)`, `@toolset.tool` or a `FunctionToolset` for all its tools. The tool then runs again on every replay, so keep it deterministic: no I/O, clock or randomness of its own. What it does through a [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/#durable-execution) call or a durable agent’s run is still recorded, unit by unit. Use it for a tool that has to see live run state, or that starts work which should be recorded step by step rather than as one unit:

durable\_opt\_out.py

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai.toolsets import FunctionToolset

toolset = FunctionToolset(id='files')

@toolset.tool(durable=False)  # (1)
async def copy_file(ctx: RunContext, source: str, destination: str) -> str:
    content = await ctx.workspace.read_bytes(source)  # (2)
    await ctx.workspace.write_bytes(destination, content)
    return f'Copied {source} to {destination}.'

agent = Agent(
    'openai:gpt-6.1-sol',
    name='files',
    toolsets=[toolset],
    capabilities=[LocalWorkspace('.'), TemporalDurability()],  # (3)
)
```

The same setting keeps the tool out of its durable unit on every engine.

Each workspace call is recorded as a unit of its own, so a run that restarts after the read reuses its result and only writes.

Swap in any other engine's durability capability; the tool stays the same.

To set it on function tools you don’t define yourself, such as a capability’s, change the tool definition in a `prepare` function or with [`PrepareTools`](https://pydantic.dev/docs/ai/capabilities/prepare-tools/). `durable=True` undoes an earlier `durable=False`, but not an opt-out in the engine’s own per-tool config, such as Temporal’s `tool_activity_config`:

durable\_prepare\_tools.py

```python
from dataclasses import replace

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import PrepareTools
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai.tools import ToolDefinition

async def keep_in_workflow(ctx: RunContext, tool_defs: list[ToolDefinition]) -> list[ToolDefinition]:
    return [replace(td, durable=False) if td.name == 'plan_next_step' else td for td in tool_defs]

agent = Agent('openai:gpt-6.1-sol', name='planner', capabilities=[PrepareTools(keep_in_workflow), TemporalDurability()])
```

Changing a tool’s placement on an agent that’s already deployed adds or removes a durable unit on every engine except DBOS, which doesn’t wrap function tools, so runs already in flight fail or diverge when they replay. Let them finish first, or deploy the change as a new version of the workflow. For the same reason, a `prepare` function that sets `durable` must be deterministic, like the tool itself: it has to make the same choice when the run replays.

Only async function tools can leave their durable unit this way. On a sync tool, an [MCP](https://pydantic.dev/docs/ai/mcp/client/) tool or a dynamic toolset’s tool that the engine runs in a durable unit, `durable=False` raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) when the tool is called, because those run in a thread or perform I/O. DBOS runs function tools in workflow code without wrapping them, so it doesn’t check them: keep an agent you may move to another engine to async tools.

An engine’s own metadata key wins when a tool sets it, so a tool with `durable=False` and `metadata={'temporal': ActivityConfig(...)}` still runs in a Temporal activity. Engine keys also carry the engine’s own configuration for the unit, which `durable` can’t express, and follow the engine’s own rules on which tools may opt out. `durable=False` in turn wins over per-tool config set in code, such as Azure Durable Task’s and Render Workflows’ `resolve_tool_options`:

| Engine | Where `durable=False` runs the tool | Engine’s own metadata key |
| --- | --- | --- |
| [Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#per-tool-activity-config) | workflow code | `'temporal'` |
| [DBOS](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/) | workflow code, where DBOS already runs function tools, so it doesn’t check the field on them | none; `{'dbos': {'child_workflow': ...}}` selects a [child workflow](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/#child-workflows) |
| [Prefect](https://pydantic.dev/docs/ai/capabilities/durable_execution/prefect/) | flow code | `'prefect'` |
| [AWS Lambda](https://pydantic.dev/docs/ai/harness/aws-lambda/) | handler code, outside any step | `'aws_lambda'` |
| [Azure Durable Task](https://pydantic.dev/docs/ai/harness/azure-durable-task/) | orchestrator code | `'azure_durable_task'` |
| [Absurd](https://pydantic.dev/docs/ai/harness/absurd/) | task handler code, outside any step | none |
| [pgtask](https://pydantic.dev/docs/ai/harness/pgtask/) | task code, outside any step | none |
| [Render Workflows](https://pydantic.dev/docs/ai/harness/render-workflows/) | the parent task run | `'render_workflows'`, whose `False` only lets a per-run toolset through; per tool, `resolve_tool_options` can return `False` |

Restate and Apache Airflow ship their own integrations; see their pages for how they wrap tools.
