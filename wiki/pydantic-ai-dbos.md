---
type: Concept
title: Pydantic AI on DBOS
description: What changes when a Pydantic AI agent runs inside a DBOS workflow — the in-process workflow/step split, agent names and toolset ids as permanent step identity, which calls are checkpointed, pickle payloads and derived run ids, child workflows, and the concurrent-run replay hazard.
tags: [ml, pydantic-ai, agents, durability, dbos]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:15:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-dbos-docs
    resource: ../raw/capabilities/durable_execution/dbos/index.md
    scope: ../raw/capabilities/durable_execution/dbos/
    kind: documentation
    revision: sha256:244a04f5850362a7fba71144476c4757655019e142a4e838712ae39035332862
    title: "Durable Execution with DBOS"
---

**Reported, Pydantic AI version unspecified:** DBOS is the durability engine that never leaves the process. Workflows and steps are ordinary Python functions in the same interpreter as the agent, and the checkpoints go to a Postgres or SQLite database, so `capabilities=[DBOSDurability()]` plus an `@DBOS.workflow()` wrapper makes a run resumable without a separate server, worker or serialization boundary.[^pydantic-dbos-docs] Staying in one process buys simplicity and costs precision: the journal is replayed in start order and matched by name alone, so agent names and toolset ids become permanent, two concurrent runs of one agent can be handed each other's recorded results, and application-owned function tools are left unwrapped unless you decorate them yourself.[^pydantic-dbos-docs]

For the engine table and where each integration ships, see [Pydantic AI durable execution](pydantic-ai-durable-execution.md); for what a stream, cancellation and a deadline do under this engine, see [Pydantic AI DBOS streaming and cancellation](pydantic-ai-dbos-streaming.md). The same integration surface for the other co-maintained engine is in [Pydantic AI on Temporal](pydantic-ai-temporal.md).

## The split, and why it is in-process

DBOS makes a program durable by checkpointing it: a workflow must be deterministic and generally may not perform I/O, while a step may do anything that touches the network, disk or an API and restarts from its own beginning if it fails. Every workflow input and step output lands in the system database, so a crash, a network failure or a server restart resumes each workflow from its last completed step.[^pydantic-dbos-docs]

The source's architecture diagram describes the whole deployment: clients arrive over HTTP, RPC or Kafka; application servers run the Pydantic AI and DBOS libraries together; inside them sit the workflows (the agent run loop), the steps (tool, MCP, model), and DBOS's queues, cron jobs and messaging; the database stores workflow and step state and schedules the tasks.[^pydantic-dbos-docs] Two consequences are worth naming, because they are what separates this engine from Temporal:

- There is no worker/server split and no separate payload boundary, so nothing has to be serialized *between* processes — only into the database.[^pydantic-dbos-docs]
- The database is the whole durable substrate, Postgres or SQLite, and DBOS's queues are offered as database-backed alternatives to Celery or BullMQ with concurrency limits, rate limits, timeouts and prioritisation.[^pydantic-dbos-docs]

## Attaching durability

Install `pydantic-ai[dbos]`, or `pydantic-ai-slim[dbos]` on the slim package, and attach the capability; the durable run itself is a decorated function that calls `agent.run()`.[^pydantic-dbos-docs]

```python
from dbos import DBOS, DBOSConfig

from pydantic_ai import Agent
from pydantic_ai.durable_exec.dbos import DBOSDurability

dbos_config: DBOSConfig = {
    'name': 'pydantic_dbos_agent',
    'system_database_url': 'sqlite:///dbostest.sqlite',
}
DBOS(config=dbos_config)

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions="You're an expert in geography.",
    name='geography',
    capabilities=[DBOSDurability()],
)

@DBOS.workflow()
async def answer(question: str) -> str:
    result = await agent.run(question)
    return result.output

async def main():
    DBOS.launch()
    answer_text = await answer('What is the capital of Mexico?')
    print(answer_text)
```

Four rules in that snippet are load-bearing.[^pydantic-dbos-docs]

| Rule | Why |
| --- | --- |
| The agent's `name` identifies its workflows | It is the durable identity, not a label |
| Attach durability through `capabilities=[...]` | The capability routes model requests and MCP communication through steps only when the run happens inside a workflow |
| Construct the agent before `DBOS.launch()` | DBOS workflows must be registered before launch, and the capability registers the agent's steps |
| Wrap `agent.run()` in your own workflow | Nothing is durable until the call sits inside a workflow |

Outside a DBOS workflow the capability is transparent, so the same agent, model and MCP server work as normal — which is why `DBOSDurability` composes with every other capability without a DBOS-specific wrapper variant.[^pydantic-dbos-docs]

### The deprecated wrapper

`DBOSAgent(agent)` still exists and returns a durable variant that wraps the agent: migrating means attaching `DBOSDurability()` and adding the workflow decorator the wrapper used to apply.[^pydantic-dbos-docs] The deprecated form is also looser in four documented places: it forbids `run_stream()` inside a workflow, rejects `timeout=`, does not reject toolsets registered after wrapping so a late toolset is silently left out of the run, and does not wait a model error's `retry_after`.[^pydantic-dbos-docs]

## Step identity: names and ids are permanent

Because recovery replays recorded steps by name, anything that becomes part of a step name must be unique and must not change after the first production deploy.[^pydantic-dbos-docs]

| Wrapped unit | Where its name comes from | Trap |
| --- | --- | --- |
| Model requests and the agent's other steps | The agent's `name` | Renaming the agent breaks in-flight workflows |
| `MCPToolset` | Its `id`, normally optional and here required | The hostname a URL toolset would take as an `id` does not count |
| `DynamicToolset`, `DynamicCapability` | An explicit `id=` | Discovery, validation and calls become `{name}__dynamic_toolset__{id}.get_tools`, `.validate_args` and `.call_tool` steps |
| Capability-owned toolset (`Capability(tools=[...])`, `MCP(...)`) | The capability's `id` | `MCP` resolves `id=` first, then a `native=MCPServerTool(...)` id, then the URL hostname; two `MCP` capabilities on one host are rejected, and a bare local client needs an explicit `id` |

The `MCPToolset.id` requirement is easy to miss because the field is optional everywhere else, and DBOS derives both the step names and a per-run tool-definitions cache key from it.[^pydantic-dbos-docs]

## What DBOS wraps, and what it leaves to you

The capability's coverage is not uniform, and the gaps are the operational content of this integration.[^pydantic-dbos-docs]

- **MCP tools always run in a step.** Setting a tool's `metadata={'dbos': False}` is rejected rather than run inline in workflow code, because an MCP tool performs I/O.[^pydantic-dbos-docs]
- **An MCP server is connected once per workflow, not once per step.** The first step that needs it connects it — inside a step, so a failed connection is retried like any other step failure — and the workflow holds the session until the run ends; tool discovery still runs its `get_tools` step, and whether that step runs is decided by the run's recorded history rather than by what a warm process happens to hold, so `cache_tools` answers from a session the run already owns.[^pydantic-dbos-docs] Concurrent runs in one process share the session, as they do outside a workflow, and it closes when the last of them ends.[^pydantic-dbos-docs]
- **Dynamic toolsets are wrapped and need a stable id.** A tool's `args_validator` runs inside the `validate_args` step, which re-resolves the toolset the way `call_tool` does; a tool without one schedules no validation step. Validation runs before approval and deferral, so rejected arguments never reach an approver.[^pydantic-dbos-docs] With `per_run_step=False` the run resolves the toolset once and each step reuses it, entering it the first time and holding it for the rest of the run — the non-durable lifecycle, so `cache_tools` keeps working; a `per_run_step=True` factory is re-resolved inside each step.[^pydantic-dbos-docs] The factory runs in workflow code and re-runs on replay, so it must be deterministic given the run's `deps` and must leave its I/O to the steps — and building a toolset is not connecting it, since an `MCPToolset` opens nothing until entered.[^pydantic-dbos-docs]
- **Application function tools and event stream handlers are not wrapped.** This is the difference from every other engine: function tools run in workflow code by default, so one that performs I/O or is non-deterministic must be decorated with `@DBOS.step`, and one that does neither can skip the decorator to avoid a database checkpoint write. A tool that enqueues tasks or invokes other DBOS workflows belongs in the agent's main workflow, not in a step.[^pydantic-dbos-docs]
- **A step cannot load a capability.** A function tool running in workflow code can call `ctx.load_capability()`, but the same code running as a step cannot.[^pydantic-dbos-docs]

One compatibility patch rides on this scheme: `FunctionToolset` applies its `sequential=True` and `defer_loading=True` to the `Tool` instances it holds, and workflows started before Pydantic AI did so keep listing those tools without them, so a run holding such a tool patches its workflow when it starts and a workflow without the patch marker gets the old listing.[^pydantic-dbos-docs]

## Payloads, deps and derived ids

DBOS pickles workflow inputs and outputs and step outputs into the database by default; a custom serializer can replace pickle through DBOS configuration.[^pydantic-dbos-docs] The practical rules that follow:

- The `deps` object passed to `Agent.run()`/`run_sync()` and every tool output must be serializable.[^pydantic-dbos-docs]
- Keep inputs and outputs small — the source's guidance is under about 2 MB, although Postgres and SQLite accept up to 1 GB per field and large objects hurt performance.[^pydantic-dbos-docs]
- If `run_id` or `conversation_id` is not passed inside a workflow, the defaults derive from the workflow ID rather than being generated at random, so a recovered workflow keeps the ids its completed steps already saw.[^pydantic-dbos-docs]

## Workspaces

Attach the workspace capability, such as `LocalWorkspace`, when constructing the agent and use `ctx.workspace` as usual. Every workspace call made in workflow code — including from function tools, which DBOS runs in the workflow — is a step, so file contents and command output count toward the size guidance above; a tool that runs in a child workflow records its workspace calls as steps of the child instead, after one further step that reattaches to the workspace.[^pydantic-dbos-docs]

Two hazards come from history rather than from payload size. Workspace arguments on the workflow side — commands, `env=`, file contents — are stored in workflow history, so secrets belong in the workspace capability's `env=` rather than passed to a call, and stored history should sit behind an appropriate payload codec.[^pydantic-dbos-docs] And adding a workspace to an agent changes its workflows' steps, which DBOS cannot recover across: let in-flight workflows finish or deploy as a new application version.[^pydantic-dbos-docs]

## Models, capabilities and toolsets chosen at runtime

`Agent.run(model=...)` accepts a model string or a model instance, but only the string crosses cleanly: an instance cannot be serialized across the step boundary, and rebuilding one from its `model_id` would build a *different* model — the same name on whatever provider the worker's environment implies, with other credentials. An unregistered instance is therefore rejected with `UserError`.[^pydantic-dbos-docs] The two documented ways to use one are to pre-register instances in a `models` dict on `DBOSDurability` and reference them by key, or to pass a string and build the instance inside the step with a `ResolveModelId` capability — the case where the model depends on the run's `deps`, such as per-user credentials. `ResolveModelId` goes before `DBOSDurability` so it gets first crack at every string, re-runs inside the step with the real deps, and must be deterministic for a given `(model_id, deps)` without external I/O. The agent's construction-time model is always the default.[^pydantic-dbos-docs]

Capabilities and executing toolsets are stricter than in an ordinary run, because their steps must exist before the workflow starts:[^pydantic-dbos-docs]

| What arrives | Where it may arrive | What happens late |
| --- | --- | --- |
| Capability | Constructor, so `DBOSDurability.for_agent()` registers its steps | `agent.run(capabilities=[...])` inside a workflow raises `UserError` |
| Observing-only capability | Per run | Allowed; `Instrumentation` is the built-in example and is exempt |
| `DynamicToolset` or other executing toolset | `Agent(toolsets=[...])` with an explicit `id` | `@agent.toolset` inside a workflow, or `agent.run(toolsets=...)`/`agent.override(toolsets=...)` with an MCP or dynamic toolset, raises `UserError` |
| Non-executing toolset (`ExternalToolset`, inline `FunctionToolset`) | Constructor or per run | Supported |

The per-run capability restriction is conceded to be conservative: third-party capabilities cannot yet declare that they only observe the run, and deriving the rule from overridden hooks is tracked in pydantic-ai#5477.[^pydantic-dbos-docs] A toolset added at run time also may not reuse the `id` of one the agent was constructed with, since the id is what routes a call to a registered step.[^pydantic-dbos-docs]

## Child workflows

An async function tool can run as a DBOS child workflow instead of inside the parent's journal, which is the documented shape for a tool that runs a nested agent with its own `DBOSDurability`: the nested model requests and tool calls are recorded in the child's history, and recovery resumes the child from its own checkpoints.[^pydantic-dbos-docs] Select it through the tool's metadata, either inline or with `SetToolMetadata`:[^pydantic-dbos-docs]

```python
@delegation.tool_plain(
    metadata={'dbos': {'child_workflow': ChildWorkflowConfig(workflow_timeout_sec=600)}}
)
async def research(topic: str) -> str:
    """Research a topic in depth."""
    result = await researcher.run(f'Research: {topic}')
    return result.output
```

The integration details that decide whether this works:[^pydantic-dbos-docs]

- Each call starts a workflow named for its toolset — `lead__function_toolset__delegation.call_tool__child_workflow`, or `lead__function_toolset__<agent>.call_tool__child_workflow` for tools registered with `Agent(tools=...)`.[^pydantic-dbos-docs]
- The tool arguments, the serialized run context and `deps` are the child's inputs, so all three must be serializable; `ctx.messages`, `ctx.emit()` and `ctx.enqueue()` raise `UserError` in the tool, because those fields are not serialized.[^pydantic-dbos-docs]
- An exception in the tool body fails the child and reaches the parent's tool call.[^pydantic-dbos-docs]
- Only async tools inside a `FunctionToolset` with a unique `id` qualify, and the choice must be made before the agent is constructed — that is when the toolset registers the child workflow, which DBOS needs before `DBOS.launch()` in order to recover it. A tool decorated with `@agent.tool` after construction raises `UserError` inside a workflow, and `SetToolMetadata` passed at run time, or a `prepare` function that adds the metadata, is honoured only in a toolset that already registers a child workflow; anywhere else the tool just runs in the parent.[^pydantic-dbos-docs]
- DBOS hashes registered workflows into the application version it computes, so adding a child workflow or renaming its toolset `id` or agent `name` is a version change: let in-flight workflows finish or pin `application_version` before deploying it.[^pydantic-dbos-docs]

## Concurrent runs: same step names, wrong results

Every run of an agent records its model requests and tool calls under the same step names, and DBOS replays a recovered workflow's steps in the order they start, checking only the names.[^pydantic-dbos-docs] Two runs of the same agent inside one workflow — `asyncio.gather(agent.run(...), agent.run(...))`, or parallel tool calls that each run the same nested agent — can therefore start their steps in a different order on recovery, and recovery then hands each run the results the other recorded while the workflow carries on with them.[^pydantic-dbos-docs]

A second failure shares the trigger: a run holding a `Tool` that a `FunctionToolset` made sequential or deferred patches its workflow when it starts, and if another run starts a step at that moment the workflow lists those tools without `sequential` and `defer_loading`; if the patch was recorded, recovery can fail with `DBOSUnexpectedStepError` while it checks for a step another run just started.[^pydantic-dbos-docs]

The remedy is one workflow per run, so each has a journal of its own: call a `@DBOS.workflow` function that runs the agent once, and when the second run happens inside a tool, give that tool a child workflow.[^pydantic-dbos-docs]

```python
@DBOS.workflow()
async def answer(question: str) -> str:
    result = await agent.run(question)
    return result.output

@DBOS.workflow()
async def answer_both(first: str, second: str) -> list[str]:
    return list(await asyncio.gather(answer(first), answer(second)))
```

Called from another workflow, `answer` runs as a child workflow with steps of its own.[^pydantic-dbos-docs]

## Parallel tool execution

Under DBOS, tools execute in parallel by default to minimise latency, and tool result events are emitted in tool-call order once all parallel calls finish, which is equivalent to `parallel_tool_call_execution_mode('parallel_ordered_events')`.[^pydantic-dbos-docs] A run with a workspace executes tool calls sequentially except for tools in a child workflow, whose workspace calls belong to the child and still run in parallel; tool hooks such as `before_tool_execute` still run in the parent workflow and therefore should not make workspace calls.[^pydantic-dbos-docs]

## Step configuration and one retry owner

Step behaviour is configured on `DBOSDurability` itself, not per tool:[^pydantic-dbos-docs]

| Key | Applies to |
| --- | --- |
| `mcp_step_config` | MCP server communication |
| `model_step_config` | Model request steps, which also carry the durable-execution retry layer |
| `event_stream_handler_step_config` | Event stream handler steps |

Each defaults to no retries when omitted. Unlike Temporal and Prefect, DBOS takes no per-tool step configuration: tool metadata other than `child_workflow` is ignored and there is no way to opt an individual tool out of step wrapping. For custom tools the documented alternative is the `@DBOS.step` and `@DBOS.workflow` decorators themselves, which have no effect outside DBOS workflows, so the tool stays usable in non-durable agents.[^pydantic-dbos-docs]

On retries, DBOS sits on top of two other retry layers — Pydantic AI's transport retries and the provider SDK client's — so the recommendation is to turn both off, in particular with `ModelSettings['max_retries'] = 0`, and let the engine be the one retry owner, with the policy set through step configuration.[^pydantic-dbos-docs] The mechanics that differ from a non-durable run:

- DBOS retries a step inside the step, after sleeping its backoff in the process that runs it.[^pydantic-dbos-docs]
- A model step whose error carries `retry_after` (read from a `Retry-After` or `retry-after-ms` header, for example) behaves differently when `model_step_config` allows another attempt: the step records the failed attempt, the workflow waits that long in a durable `DBOS.sleep` that a recovered workflow does not repeat, and the request runs again in a new step with the attempts the step had left — so the journal shows the model step, a sleep, and the model step again. The wait is capped at DBOS's own backoff for that attempt or a minute, whichever is longer, so a provider asking for hours does not park the workflow for hours.[^pydantic-dbos-docs]
- A model error without `retry_after` gets DBOS's backoff as before, and the deprecated `DBOSAgent` does not wait `retry_after` at all.[^pydantic-dbos-docs]
- There is no selective non-retryable-exception support, so enabling `retries_allowed` means framework misconfiguration errors such as `UserError` are retried along with everything else — Temporal and Prefect mark those non-retryable, while on DBOS a misconfigured agent burns its whole retry budget before failing.[^pydantic-dbos-docs]

## Observability

DBOS can emit OpenTelemetry spans for each workflow and step execution, and Pydantic AI already emits spans for each agent run, model request and tool invocation; `uvx logfire-cli wizard --task pydantic-ai` is the documented one-command setup for sending both to Logfire as one end-to-end view.[^pydantic-dbos-docs] Nothing in the source describes replay-safe span generation or duplicated spans, which the Temporal integration does document, so that property is unknown here.[^pydantic-dbos-docs]

## Coverage and limits

The package is one `index.md` capture, 4,754 words as declared and 4,758 by local `wc -w` including frontmatter, content digest sha256:244a04f5; it has no attachments, includes, imports, downloads or supporting files, and its architecture diagram is printed as ASCII text rather than shipped as an image.[^pydantic-dbos-docs]

- The page names no Pydantic AI, DBOS or Logfire release version, author, publication date or licence, so every API and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule.[^pydantic-dbos-docs]
- Every external link — the DBOS architecture, queue, Python guide, workflow-upgrade, custom-serialization, decorator, `DBOS.sleep`, context and tracing pages; the Pydantic AI API references for `DBOSDurability`, `DBOSAgent`, `ChildWorkflowConfig` and `StepConfig`; and the Pydantic blog walkthrough — was read as a link, not followed.[^pydantic-dbos-docs]
- The sample programs are as printed; the source adds that the first one needs `asyncio` imported and `asyncio.run(main())` added, which is not in the listing.[^pydantic-dbos-docs]
- Nothing was installed, no database created, no application launched, no workflow started, recovered or cancelled, no step retried, no payload stored and no span opened, so every claim is **Reported** and none **Observed** or **Reproduced**; the source states no price, latency or scaling figure.[^pydantic-dbos-docs]
- Evidence class: **Reported**.

## Relationships

- **Instance of** [Pydantic AI durable execution](pydantic-ai-durable-execution.md), whose engine table records DBOS as a core, co-maintained integration shipped in `pydantic_ai.durable_exec.dbos`.[^pydantic-dbos-docs]
- **Constrains** [Pydantic AI durable tool placement](pydantic-ai-durable-tool-placement.md): DBOS is the engine that does not wrap application function tools at all, so `durable=False` is meaningless there while `metadata={'dbos': ...}` carries only `child_workflow`.[^pydantic-dbos-docs]
- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for attachment, and on construction-time capability and toolset registration for durable steps.[^pydantic-dbos-docs]
- **Bound by** [Pydantic AI dependencies](pydantic-ai-dependencies.md): `deps` is pickled into the database and must stay serializable and small.[^pydantic-dbos-docs]
- **Keeps** [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) in process, with every workspace call as its own step and workflow-side arguments visible in history.[^pydantic-dbos-docs]
- **Changes** [MCP integration](pydantic-ai-mcp-integration.md) behaviour: one session per workflow instead of one per step, and a required toolset `id`.[^pydantic-dbos-docs]
- **Splits its streaming, event delivery, cancellation and deadline behaviour into** [Pydantic AI DBOS streaming and cancellation](pydantic-ai-dbos-streaming.md).[^pydantic-dbos-docs]
- **Differs from** [Pydantic AI on Temporal](pydantic-ai-temporal.md) on the payload boundary: DBOS serializes into its own database and runs steps in process, so a `RunContext` mutation is not the cross-process accounting problem it is in an activity.[^pydantic-dbos-docs]
- **Shares its replay model with** [Pydantic AI durable execution](pydantic-ai-durable-execution.md)'s replay-instead-of-snapshots account: deterministic code replayed against recorded step results, with the journal order doing the work a snapshot would do.[^pydantic-dbos-docs]
- **Feeds** [Pydantic AI observability](pydantic-ai-observability.md) through DBOS's per-workflow and per-step OTel spans beside Pydantic AI's own run and tool spans.[^pydantic-dbos-docs]

[^pydantic-dbos-docs]: Pydantic, "Durable Execution with DBOS" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/dbos/`), 4,754 words as declared, 4,758 by local `wc -w`, no version, date or author stated; local capture `raw/capabilities/durable_execution/dbos/index.md`, content digest sha256:244a04f5. §"Durable Execution" (lines 13–51) for the checkpointing model, the workflow/step determinism split, persisted inputs and outputs, the queues claim, and the ASCII architecture diagram; §"Durable Agent" (53–129) for the install extras, the `DBOSConfig`/`geography` sample and its four inline annotations, the agent-before-`DBOS.launch()` rule, transparency outside workflows and capability composition; §"Wrapper-agent path (deprecated)" (130–156) for `DBOSAgent`, the migration diff and the wrapper's four looser behaviours; §"Agent and Toolset Requirements" (161–186) for the agent-name and toolset-id permanence rules, the MCP-always-a-step and `metadata={'dbos': False}` rejection, the per-workflow MCP session and `cache_tools` behaviour, the dynamic-toolset step names and `per_run_step` rules, capability-derived ids and `MCP` id precedence, the unwrapped function tools and event handlers with the `@DBOS.step` decision, `ctx.load_capability()` in workflow code versus steps, and the `FunctionToolset` patch marker; §"Agent Run Context and Dependencies" (187–192) for pickle, custom serializers, deps and tool-output serializability, the ~2 MB guidance and derived ids; §"Workspaces" (193–200) for per-call steps, child-workflow placement, history-stored arguments and the redeploy rule; §"Model Selection at Runtime" (201–206) for rejected model instances, the `models` dict and `ResolveModelId`; §"Capabilities at Runtime" (207–212) for constructor-time steps, the per-run `UserError`, the `Instrumentation` exemption and issue #5477; §"Child workflows" (249–289) for the tool metadata form, workflow naming, child inputs, `ctx` restrictions, exception propagation, registration constraints and the application-version hash; §"Concurrent Agent Runs" (290–321) for the name-only replay ordering, the crossed-results failure, the patch/`DBOSUnexpectedStepError` case and the per-run workflow remedy; §"Parallel Tool Execution" (322–327); §"Toolsets at Runtime" (328–335) for the toolset table and the no-id-reuse rule; §"Step Configuration" (336–347) for the three config keys, the absent per-tool config and the decorators' no-op nature outside DBOS; §"Step Retries" (348–359) for retry ownership, in-step retries, the `retry_after`/`DBOS.sleep` sequence and its cap, the wrapper's exception, and the missing non-retryable classification; §"Observability with Logfire" (360–364). Evidence class: **Reported** — vendor reference page naming no version; nothing was installed or executed.
