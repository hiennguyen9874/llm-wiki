---
type: Concept
title: Pydantic AI dynamic workflows
description: The Harness DynamicWorkflow capability — one run_workflow tool over a catalog of sub-agents, the script the model writes in the Monty sandbox, exact call and token budgets, how results come back, and what changes under Temporal, DBOS and AWS Lambda.
tags: [pydantic-ai, harness, agents, orchestration, durability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:44:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-dynamic-workflow-docs
    resource: ../raw/harness/dynamic-workflow/index.md
    scope: ../raw/harness/dynamic-workflow/
    kind: documentation
    revision: sha256:378df905c512638ee867631fdaf64f467c7171b8b0d03a857dbb24ba48fac24c
    title: "Dynamic Workflow"
---

`DynamicWorkflow` is the [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md) that moves multi-agent coordination out of the conversation and into a script: you hand it a catalog of named sub-agents, the orchestrator model receives a single `run_workflow` tool, and each call runs Python the model writes — every sub-agent an `async` function — to completion in the [Monty](pydantic-ai-code-mode.md) sandbox, with only the script's final value returning to the model's context[^pydantic-dynamic-workflow-docs] It exists for the case where the choreography *between* sub-agents is the actual work: review three files at once, keep only the reports that found something, summarize those, hand the summary to the writer. Fan-out, chaining, voting and retry loops all run inside one tool call instead of one model turn each[^pydantic-dynamic-workflow-docs] The page names no Pydantic AI or Harness version, so every API below is version-unknown, and the Harness's 0.x policy means the shape may move between minor releases[^pydantic-dynamic-workflow-docs] It installs through its own extra, `pip install "pydantic-ai-harness[dynamic-workflow]"`[^pydantic-dynamic-workflow-docs]

## Why code instead of a turn per step

The default coordination is one tool call per step: the orchestrator calls the reviewer, waits, reads the result back into its context, calls the reviewer again, waits again[^pydantic-dynamic-workflow-docs] Every intermediate result crosses into the context and every step that depends on the previous one costs another model turn. `DynamicWorkflow` inverts that: the model writes ordinary Python against your catalog, the script runs to completion in one tool call, and only what the script returns or prints — plus bounded previews of completed results on failure or budget exhaustion — reaches the parent[^pydantic-dynamic-workflow-docs]

It is the same bargain as [code mode](pydantic-ai-code-mode.md) — the same Monty sandbox, the same "write a script instead of many tool calls" move — with one difference in what the script may call: in code mode it calls the agent's own tools, here it calls whole sub-agents[^pydantic-dynamic-workflow-docs]

## Against `SubAgents`: two altitudes

The Harness ships two delegation capabilities over the same currency, named isolated sub-agent runs, at different altitudes[^pydantic-dynamic-workflow-docs] [`SubAgents`](pydantic-ai-subagents.md) exposes one `delegate_task(agent_name, task)` tool, so each delegation is its own tool call and its own model turn — the right fit when delegations are occasional or when each result needs the parent's judgment before the next one is picked. `DynamicWorkflow` moves the choreography into a script, so a fan-out is one tool call rather than one per branch.

The controls cover the same ground at different levels, because one script fans out over the whole catalog while `SubAgents` lets the parent pick one delegate per call:

| Control | `DynamicWorkflow` | `SubAgents` |
| --- | --- | --- |
| Retries of the parent's tool | `max_retries`, as other script tools such as `CodeMode` | `tool_retries` |
| Number of sub-agent runs | `max_agent_calls`, across the catalog | `SubAgent.max_calls`, per delegate |
| Usage limits of one sub-agent run | `sub_agent_usage_limits`, for every run | `SubAgent.usage_limits`, per delegate |
| Shared usage accounting | `forward_usage` | `forward_usage` |
| Sub-agent model | `inherit_model`, for every run | the `models` menu and `SubAgent.models` |

The vendor's migration advice is to start with `SubAgents` if unsure: a `delegate_task` orchestrator converts to a workflow catalog without changing the sub-agents themselves[^pydantic-dynamic-workflow-docs]

## The catalog and the script

`reviewer` and `summarizer` are ordinary agents; the catalog is the only new object[^pydantic-dynamic-workflow-docs]

```python
from pydantic_ai import Agent
from pydantic_ai_harness import DynamicWorkflow

reviewer = Agent('openai:gpt-6.1-sol', name='reviewer', description='Reviews code for bugs.')
summarizer = Agent('openai:gpt-6.1-sol', name='summarizer', description='Summarizes findings.')

orchestrator = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[DynamicWorkflow(agents=[reviewer, summarizer])],
)
```

An agent's `name` becomes the **function name** the model calls in the script, so it has to be a valid Python identifier; its `description` becomes the documentation the model reads, so it should be written the way a function's docstring would be[^pydantic-dynamic-workflow-docs] What the model then writes looks like this:

```python
import asyncio

reports = await asyncio.gather(
    reviewer(task="Review auth.py for bugs:\n<file contents>"),
    reviewer(task="Review parser.py for bugs:\n<file contents>"),
)
await summarizer(task="Summarize these review findings:\n" + "\n\n".join(reports))
```

Four properties matter[^pydantic-dynamic-workflow-docs]:

- Each sub-agent is an `async` function called with `await`, and the work is always passed as the single keyword argument `task` — `reviewer(task="...")`, never positionally.
- `asyncio.gather(...)` runs the two reviews concurrently rather than one after the other, except in a DBOS workflow where the sub-agents carry `DBOSDurability` (below).
- The value of the script's **last expression** is what the model sees; the intermediate `reports` list never leaves the sandbox.
- Each call is a full `Agent.run` with its own model loop, history, tools and typed output, so calls are **isolated** — a sub-agent remembers nothing from an earlier call, and everything it needs must be in `task` — and they **cost tokens and take time**, which is why the budgets below exist.

### Structured sub-agent output

A sub-agent returns whatever its `output_type` produces: a string by default, but a Pydantic output type arrives in the script as a `dict` read by subscript, `result["value"]` rather than `result.value`, because the catalog the model sees renders each output type as a `TypedDict`[^pydantic-dynamic-workflow-docs]

An `output_type` may include [`DeferredToolRequests`](pydantic-ai-deferred-approvals.md) so a top-level caller can approve tools and resume, or `PendingModelResponse` so a caller can check on a request the provider is still processing. A workflow script can do neither, so the catalog leaves both out of the sub-agent's return type, and a sub-agent run that ends with one raises a `RuntimeError` in the script like any other sub-agent failure; a model request left pending is cancelled best effort, and a batch is only cancelled once no other request in it is still waiting[^pydantic-dynamic-workflow-docs]

## How results come back

The last expression carries the real result — `print()` is debug logging that stringifies, and the model does not receive a printed value in its place[^pydantic-dynamic-workflow-docs]

| The script… | The model receives |
| --- | --- |
| ends in a value, no print | that value directly (or `{}` if it is `None`) |
| prints and ends in a value | `{"output": "<printed text>", "result": <value>}` |
| prints and ends in `None` | `{"output": "<printed text>"}` |

## Budgets

A sub-agent is non-deterministic, costs tokens and can fan out further, so the capability ships three kinds of ceiling plus the tool's own retry count[^pydantic-dynamic-workflow-docs]

**`max_agent_calls`** (default `50`) is the only knob that bounds the number of runs *exactly*: a hard host-enforced ceiling on sub-agent runs per parent run, one budget shared across every `run_workflow` call in that run, holding exactly even when the script fans out with `asyncio.gather`. When it runs out the workflow stops calling sub-agents and returns a terminal result with bounded previews of up to the 20 most recent completed results[^pydantic-dynamic-workflow-docs]

**`sub_agent_usage_limits`** is a `UsageLimits` applied to each sub-agent run, and **`forward_usage`** decides whether the tree shares one counter:

| `forward_usage` | Counter | What the limit means |
| --- | --- | --- |
| `True` (default) | the parent's `usage` is shared across the tree | a tree-wide cap — best-effort under concurrent fan-out, since several sub-agents can pass the check before any of them adds to the count |
| `False` | each sub-agent run counts on its own | per-run limits — a per-run `total_tokens_limit` of `T` with `max_agent_calls` of `N` bounds the tree to roughly `N * T` tokens |

Without `sub_agent_usage_limits`, sub-agents sharing the counter run under the `usage_limits` passed to the parent `run()`, so the parent's budget bounds the whole tree; with `forward_usage=False` they fall back to Pydantic AI's default `request_limit` of 50 per run[^pydantic-dynamic-workflow-docs]

**`resource_limits`** guards the orchestration script's own memory rather than the sub-agents it calls: the default backstop is 256 MB with no time limit, and printed output is collected separately under Monty's 10 MiB cap[^pydantic-dynamic-workflow-docs] Three details decide whether it helps or misleads:

- `max_duration_seconds` measures time spent running **sandbox code**, not wall-clock time. While the script waits on a sub-agent it is suspended and that time does not count, so the cap will not fire on a normal workflow however long the sub-agents take; its one job is a pure-CPU runaway — a `while True:` loop that never awaits, which no sub-agent budget can stop because it never calls a sub-agent[^pydantic-dynamic-workflow-docs]
- `'unlimited'` removes every sandbox resource limit while the separate 10 MiB print cap remains, and a partial dict merges onto the backstop so only the named caps are overridden[^pydantic-dynamic-workflow-docs]
- `max_duration_secs` is the deprecated name of `max_duration_seconds` and still works, with a warning[^pydantic-dynamic-workflow-docs]

`max_retries` (default `3`) is the parent tool's own retry count, which is also what a static type error costs — see [the sandbox](#what-runs-in-the-sandbox).

**Workflows do not nest.** A sub-agent cannot start its own workflow: a sub-agent that carries `DynamicWorkflow` is not offered `run_workflow` while it runs inside one, so the practical rule is not to give the catalog's sub-agents that capability — they are the leaves of the orchestration, not orchestrators[^pydantic-dynamic-workflow-docs]

## Reshaping the catalog

**Renaming for one workflow.** A bare agent is shorthand for wrapping it in a `WorkflowAgent`, which overrides the sandbox function name and docstring — `WorkflowAgent(reviewer, name='check', description='...')` while leaving the agent itself untouched, with `None` falling back to `agent.name`/`agent.description` and `''` hiding the description[^pydantic-dynamic-workflow-docs] That is how one reviewer becomes `reviewer` in one workflow and `check` in another.

**`reveal()`.** The catalog is fixed when the run starts, which is what keeps it inside the [prompt-cached](pydantic-ai-prompt-caching.md) prefix across turns. To make a new sub-agent available mid-run — say once a fixer agent has been provisioned — keep a reference to the `DynamicWorkflow` instance and call `workflow.reveal(fixer)`[^pydantic-dynamic-workflow-docs] The revealed agent becomes callable on the next step, announced by a short `AgentRevealPart` (a capability part in the application's voice, whose `agent_name` field names the sub-agent) carrying the new function's signature; the `run_workflow` description itself stays frozen at the agents present when the run started, so a reveal never moves the cache prefix, and if compaction or a history processor removes the announcement the capability announces it again on the next step. `reveal()` is append-only and validates at the call site: a missing name, an invalid identifier, a reserved keyword or a name collision raises `UserError`[^pydantic-dynamic-workflow-docs]

**`defer_loading=True`.** `DynamicWorkflow` carries a fair amount of instruction text and most turns do not need it, so it can be collapsed to a one-line entry until the model loads it — which requires a stable `id`, per [on-demand capabilities](pydantic-ai-on-demand-capabilities.md)[^pydantic-dynamic-workflow-docs]

## What runs in the sandbox

The script is Monty, a subset of Python, and the edges matter[^pydantic-dynamic-workflow-docs]:

- No third-party libraries. Importable standard-library modules include `sys`, `typing`, `asyncio`, `math`, `json`, `re`, `unicodedata`, `datetime`, `time` and `random`; import what you use. There is no filesystem or environment access.
- No clock and no unseeded randomness: `datetime.datetime.now()`, `datetime.date.today()`, `time.time()` and unseeded `random` fail. `time.sleep` and `asyncio.sleep` really wait, and with `max_duration_seconds` set a script may sleep for at most that long in total.
- `asyncio.gather(...)` takes positional awaitables but **no keyword arguments**, including `return_exceptions=True`, and runs sub-agents and `asyncio.sleep` calls concurrently except in the DBOS case below. Other task creation and wait APIs are unavailable.
- Before a script runs it is **statically type-checked** against the sub-agent signatures, so a misspelled function, a positional `task` or a wrong-typed argument costs one retry but no sub-agent budget and no sandbox execution. Values typed `Any` can reach runtime validation, but are still rejected before a sub-agent runs.

## Durable engines

Under a durable engine the script is workflow code, and each engine changes what a fan-out means[^pydantic-dynamic-workflow-docs] The engines themselves are in [Pydantic AI durable execution](pydantic-ai-durable-execution.md).

**Temporal.** Attach [`TemporalDurability`](pydantic-ai-temporal.md) alongside `DynamicWorkflow` on the orchestrator, and to each sub-agent whose model requests should run as activities, then register every agent with its own `AgentPlugin`. The script runs in workflow code like code mode's `run_code` and is re-executed during replay against the recorded sub-agent results. Unlike code mode, a `max_duration_seconds` you set still applies inside the workflow, so a script that runs close to it can stop at a different point on replay and raise `NondeterminismError`[^pydantic-dynamic-workflow-docs]

**DBOS.** [`DBOSDurability`](pydantic-ai-dbos.md) numbers a workflow's steps in the order they start, so concurrent sub-agents would interleave by timing and recovery could replay one sub-agent's results into another call. When *any* sub-agent in the catalog carries it, every sub-agent call the script makes — including calls to sub-agents without `DBOSDurability` — runs one at a time inside a DBOS workflow, as does every `asyncio.sleep` the script gathers, so an `asyncio.gather` over sub-agents takes the **sum** of their run times rather than the longest[^pydantic-dynamic-workflow-docs] Each call then runs as ordinary workflow code: a sub-agent carrying `DBOSDurability` keeps checkpoints for its model requests, MCP tool calls and `@DBOS.step` tools, and DBOS checks the roles those step tools require, while other function tools run as workflow code again on recovery — so side effects belong in `@DBOS.step` tools. A sub-agent without it keeps no checkpoints for its model requests. Recording each call as one DBOS step would let calls overlap, but DBOS runs a step called from inside another step as a plain function call without its own checkpoint or role check.

**AWS Lambda.** `AWSLambdaDurability` also numbers a context's steps in start order: the calls a script makes before it next waits run as the branches of one Lambda `parallel` operation, named after the tool, in the order the script made them, and the sub-agents still run concurrently[^pydantic-dynamic-workflow-docs] Each branch gets a child context whose step IDs derive from the branch position, so a sub-agent's model requests and tool calls keep their own checkpoints, and a branch's output is checkpointed with the `serdes` in the sub-agent's `step_config`. Recovery returns each finished branch's recorded output, and an unfinished branch replays its checkpoints and runs on. Under other engines sub-agents simply run concurrently.

### Scheduling the calls yourself

`call_scheduler` decides when the script's sub-agent calls start. It is called with the run context once per `run_workflow` call and returns a `WorkflowCallScheduler`: each call reaches its `run` as a `WorkflowCall` carrying the sub-agent's `agent_name`, and starts when `run` awaits `call.start()`; `flush` is awaited each time the script waits on its calls, once every call made before the wait has reached `run` — which lets an engine integration register a whole batch, in script order, before any of them starts[^pydantic-dynamic-workflow-docs] Three constraints come with it:

- A call only completes after `run` awaits `call.start()`, so a scheduler that holds calls back has to release them in `flush`.
- Under `AWSLambdaDurability`, the calls that have started when `flush` returns run as one `parallel` operation, so a released call must await `call.start()` without suspending first; one that waits on something else first, such as a concurrency limit, misses the operation and the script waits on it indefinitely.
- An exception `run` raises itself reaches the script as a `RuntimeError` naming only its type. Under `DBOSDurability` the calls already start one at a time in dispatch order and the `call_scheduler` factory is not called at all.

## Observability

The Logfire trace is the best view, traced as described in [Pydantic AI observability](pydantic-ai-observability.md): each sub-agent run appears nested under the `run_workflow` span, and that span carries the exact `code` argument the model wrote, so the script actually executed is readable after the fact[^pydantic-dynamic-workflow-docs] To watch sub-agent runs inside the single tool call, set `event_stream_handler` on each sub-agent `Agent`.

## API

Every parameter is keyword-only[^pydantic-dynamic-workflow-docs]:

```python
DynamicWorkflow(
    agents=[...],                 # Sequence[AbstractAgent | WorkflowAgent], required
    tool_name='run_workflow',
    max_agent_calls=50,
    max_retries=3,
    forward_usage=True,
    inherit_model=False,          # True -> sub-agents run with the parent run's resolved model
    sub_agent_usage_limits=None,  # UsageLimits per sub-agent run
    resource_limits=None,         # None -> backstop (256 MB, no time cap); 'unlimited'; dict merges
    call_scheduler=None,          # (RunContext) -> WorkflowCallScheduler
    id=None,                      # required when defer_loading=True
    description=None,             # one-line catalog entry shown while deferred
    defer_loading=False,
)

workflow.reveal(agent)            # AbstractAgent | WorkflowAgent; validates before appending

WorkflowAgent(agent, name=None, description=None)
```

`inherit_model` fixes which model the leaves use: by default each sub-agent uses the model it was constructed with, and `True` makes every dispatch follow a per-run model override the host passed to the parent (for example from a `/model` command) — leave it `False` when a sub-agent is deliberately pinned[^pydantic-dynamic-workflow-docs] `DynamicWorkflowToolset`, `WorkflowCall`, `WorkflowCallScheduler` and `WorkflowResourceLimits` are exported for advanced use.

## Limits

- The page is vendor documentation for its own package with **no Pydantic AI or Harness version, date, author or licence**, so every API name, default and error here is version-unknown; the new page is `draft` under the `pydantic-ai` domain rule[^pydantic-dynamic-workflow-docs]
- Every code sample pins `openai:gpt-6.1-sol`, a model name no other capture in this wiki corroborates — it is the vendor's placeholder, not a model whose availability was checked[^pydantic-dynamic-workflow-docs]
- Nothing was installed, no script was compiled, type-checked or run in Monty, no sub-agent budget was exhausted, no `reveal()` announced, no engine was attached and no trace opened, so every claim is **Reported** and none **Observed** or **Reproduced**[^pydantic-dynamic-workflow-docs]
- Unstated: what the bounded previews of completed results contain when a budget or a failure ends a workflow, the full `WorkflowCallScheduler` protocol beyond `run` and `flush`, whether `max_retries` re-runs the whole script or only the check that rejected it, and how a sub-agent's own `print()` behaves — only the script's print is described[^pydantic-dynamic-workflow-docs]
- The comparison with [`SubAgents`](pydantic-ai-subagents.md) is the vendor's own, and neither capability was benchmarked here; the claim that a workflow script cannot approve deferred tools is a documented restriction, not a measured failure mode[^pydantic-dynamic-workflow-docs]

## Relationships

- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md) under the 0.x version policy, attached through `capabilities=[DynamicWorkflow(...)]`.
- **Is the sibling of** [Harness subagents](pydantic-ai-subagents.md): `SubAgents` trades one delegation per turn for the parent's judgment, `DynamicWorkflow` trades the parent's judgment for one script of fan-out, chaining, voting and retry.
- **Is the documented form of** the `run_workflow` sketch in [Code as the agent graph](code-as-agent-graph.md), and the same Monty-sandbox bargain as [code mode](pydantic-ai-code-mode.md) — one script instead of many tool calls, differing in what the script may call.
- **Protects** [prompt caching](pydantic-ai-prompt-caching.md): the catalog is frozen at run start, a `reveal()` is appended as a capability part rather than rewriting the tool description, and `defer_loading` keeps the instruction text out of the prefix until loaded.
- **Uses** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md) for `defer_loading=True`, which is what the stable `id` it requires is for.
- **Runs its scripts as workflow code under** [durable execution](pydantic-ai-durable-execution.md) — [Temporal](pydantic-ai-temporal.md) replaying the script against recorded results, [DBOS](pydantic-ai-dbos.md) serializing the calls so step numbering stays deterministic, AWS Lambda folding the pre-wait calls into one `parallel` operation.
- **Traces into Logfire and** [Pydantic AI observability](pydantic-ai-observability.md): one `run_workflow` span per call carrying the executed script, with each sub-agent run nested inside it.
- **Cannot approve or resume through** [deferred tool approval](pydantic-ai-deferred-approvals.md): `DeferredToolRequests` and `PendingModelResponse` are stripped from a sub-agent's return type inside a workflow and fail the call instead.

[^pydantic-dynamic-workflow-docs]: Pydantic Docs, "Dynamic Workflow", <https://pydantic.dev/docs/ai/harness/dynamic-workflow/>; local capture `raw/harness/dynamic-workflow/index.md`, content digest sha256:378df905, 3,182 words as declared (3,288 by `wc -w`), language `en`, no publication date, author, licence or Pydantic AI/Harness version. Locators are line ranges in that capture: 11–30 for the coordination problem, the version-policy warning and the sequence diagram; 32–38 for code-instead-of-turns and the Monty/code-mode comparison; 40–57 for the two delegation capabilities and the control table; 59–70 for the extra install; 72–89 for the catalog example and the `name`/`description` roles; 91–112 for the sample script, `task`-by-keyword, `gather`, last-expression return and call isolation; 114–137 for structured sub-agent output, `TypedDict` rendering and the `DeferredToolRequests`/`PendingModelResponse` restrictions; 139–149 for the result-shape table; 151–153 for `inherit_model`; 155–190 for `max_agent_calls`, the `forward_usage` table and its fallbacks, `resource_limits` and its three notes, and the no-nesting rule; 192–210 for `WorkflowAgent`; 212–224 for `reveal`, the frozen description and the `UserError` validations; 226–238 for `defer_loading` and the required `id`; 240–249 for the sandbox's modules, clock and randomness rules, the `gather` keyword restriction and the static type check; 251–253 for the Temporal attachment, replay and the `NondeterminismError` risk; 255–261 for the DBOS serialization, checkpoints and `@DBOS.step` rule (line 257) and the AWS Lambda `parallel` branches (line 259); 263–295 for `call_scheduler`, the `AWSLambdaDurability` release hazard and the `RuntimeError` typing; 297–299 for the Logfire span carrying `code` and `event_stream_handler`; 301–329 for the keyword-only API surface, `reveal`, `WorkflowAgent` and the four advanced exports; 331 for the repository source link. Evidence class: **Reported** — vendor documentation for its own package; nothing was installed or executed.
