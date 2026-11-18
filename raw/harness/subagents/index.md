---
title: "Subagents"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/harness/subagents/"
domain: "pydantic.dev"
language: "en"
description: "Let a Pydantic AI agent delegate tasks to named subagents through one delegate_task tool, with per-subagent budgets, model choice, and Markdown agent files."
word_count: 18887
---

`SubAgents` lets an agent delegate self-contained tasks to named child agents. It takes a sequence of `SubAgent` entries and exposes a single `delegate_task(agent_name, task)` tool. Each delegation runs the chosen sub-agent in its own run — with its own message history, so it never sees the parent conversation — and returns its output to the parent.

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/sub_agents/)

> While Pydantic AI Harness is on 0.x releases, the API may change between minor releases; when it does, deprecation warnings and release-note migration guidance tell you (or your agent) exactly how to upgrade. See the [version policy](https://pydantic.dev/docs/ai/harness/#version-policy).

```
flowchart TB
    accTitle: Subagents: hand a task to another agent run
    accDescr: The parent model calls delegate_task and gets a result. The SubAgents capability passes the task to researcher, writer or self, a new run with its own message history, and gets str(result.output) back. It does not run the child on an unknown agent name, max_calls used up or max_depth reached, and a child stops early if timeout_seconds or usage_limits is reached or it failed.
    model(["parent model"])
    subagents["SubAgents()<br/>delegate_task"]:::capability
    child["researcher, writer or self<br/>a new run with its<br/>own message history"]
    refused["unknown agent name,<br/>max_calls used up,<br/>or max_depth reached"]:::blocked
    stopped["timeout_seconds or<br/>usage_limits reached,<br/>or the child failed"]:::blocked
    model <-->|"tool call, result"| subagents
    subagents <-->|"task, str(result.output)"| child
    subagents -.-x|"does not run the child"| refused
    child -.-x|"stopped early"| stopped
    classDef capability stroke:#E520E9,stroke-width:2px
    classDef blocked stroke:#E5533D,stroke-width:2px,stroke-dasharray:4 3
```

## The problem

A single agent that does everything accumulates a large tool set and a long context. Splitting the work across specialized sub-agents keeps each context focused, but wiring up delegation by hand means writing a tool per agent, forwarding deps, threading usage limits, and telling the model what it can delegate to.

## The solution

`SubAgents` takes a sequence of `SubAgent` entries and exposes a single `delegate_task(agent_name, task)` tool. Each delegation runs the chosen sub-agent in its own run — with its own message history, so it never sees the parent conversation — and returns its output to the parent. The available sub-agents are listed in the system prompt, so the listing stays in the cached prefix; if it changes between runs of the same conversation, the change is [appended](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) instead of rewriting the prefix.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent, SubAgents

researcher = Agent('anthropic:claude-opus-5-5', name='researcher', description='Researches a topic and reports findings')
writer = Agent('anthropic:claude-opus-5-5', name='writer', description='Turns notes into polished prose')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agents=[SubAgent(researcher), SubAgent(writer)])],
)

result = orchestrator.run_sync('Research the history of TLS and write a one-paragraph summary.')
print(result.output)
```

A delegate’s name — how the parent model refers to it, and how it is listed in the prompt — is the agent’s own `name`, or a `SubAgent(name=...)` override. Two delegates resolving to the same name is an error, and an agent with no name and no override is rejected.

## The tool

| Tool | Purpose |
| --- | --- |
| `delegate_task(agent_name, task)` | Run the named sub-agent on a self-contained task and return its output. |

- The sub-agent runs with its own message history, so `task` must be self-contained.
- An unknown `agent_name` raises `ModelRetry`, so the model can correct itself.
- The result returned to the parent is `str(result.output)`.
- With a `models` menu configured, the tool takes an extra `model` argument (see below).

## Deps, usage, tools, and capabilities

- **Deps are forwarded.** The parent run’s `deps` are passed to each sub-agent, so sub-agents share the parent’s `AgentDepsT` (enforced by the type signature — every sub-agent is an `AbstractAgent[AgentDepsT, Any]`).
- Delegated agents inherit the parent’s workspace unless `workspace_resolver` selects another directory. Parent read-only restrictions still apply.
- **Usage is shared by default.** The parent’s `usage` is passed to each sub-agent run, so token usage aggregates and a parent `usage_limits` applies across the whole agent tree. Set `forward_usage=False` to give each sub-agent run its own accounting.
- **The parent’s tools are not passed on.** A sub-agent runs with its own tools. To delegate to an agent that has all of the parent’s tools and capabilities, use `include_self=True` (see “Delegating to the agent itself” below).
- **Capabilities can be shared.** `shared_capabilities` are applied to every sub-agent run — e.g. give all sub-agents a common guardrail, memory, or planning capability without rebuilding each `Agent`.
- **Sub-agent events can be streamed.** Pass an `event_stream_handler` and it’s forwarded to each sub-agent run, so the sub-agent’s model-streaming and tool events surface to the caller (the handler receives the sub-agent’s own `RunContext`).

`inherit_tools=True` is deprecated and emits a `HarnessDeprecationWarning`. It adds the parent agent’s own tools (registered via `tools=` or `toolsets=`) to each sub-agent run, minus the delegate tool, but not the tools contributed by the parent’s capabilities. Bind the tools an explicit sub-agent needs directly to its `Agent`, use `include_self=True` to delegate to a fresh run of the agent with everything bound to it, or use a `tool_resolver` to give disk-loaded agents tools.

## Delegating to the agent itself

With `include_self=True`, the roster also lists the running agent itself, as `self`. A delegation to `self` starts a fresh run of that agent (`RunContext.agent`) on the parent run’s model (or the `models` option the parent picks), with no parent conversation. Because the child is the same `Agent`, it has every capability, toolset, and instruction bound to it, and they register again in the child run: a guardrail, approval gate, or audit hook bound next to `SubAgents` sees the tool calls the delegate makes, not only the `delegate_task` call. This is what [`Coder`](https://pydantic.dev/docs/ai/harness/coder/) uses by default.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgents

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(include_self=True)],
)
```
- **Only what is bound to the `Agent` carries over.** Capabilities, toolsets, instructions, and model settings passed to the parent’s `run()` are not part of the agent, so the delegate does not get them. Passing `SubAgents(include_self=True)` itself to `run()` raises a `UserError` when the run starts, since the delegate would come up without it.
- **Delegation depth is capped.** The delegate carries `delegate_task` too, so `max_depth` (default `3`, counting the top-level run) bounds the tree: the top-level run delegates, its delegates delegate once more, and a run at the limit gets neither `delegate_task` nor the sub-agent listing. The limit applies to every delegation through `SubAgents`, including explicit rosters.
- **Delegates inherit everything, including what may not suit a sub-task.** An `AskUser` capability bound to the agent can prompt the user from inside a delegation, and the delegate returns the agent’s own `output_type`, rendered with `str()` (a delegate run that ends with [`DeferredToolRequests`](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) or [`PendingModelResponse`](https://pydantic.dev/docs/ai/core-concepts/batch/#ending-a-run-while-it-waits) returns a steering message instead, as described under failure handling).
- The deprecated `inherit_tools` does not apply to `self`, whose tools are already the parent’s. The name `self` is reserved: an explicit delegate with that name is an error, and a disk definition with that name is skipped with a warning.
- **On Temporal, `agent_folders` is not supported.** Sub-agents read from `agent_folders` add a toolset at run time, which Temporal refuses, so pass `agent_folders=None`. When `self` is the only delegate, it runs in the workflow, so register a `Model` instance from `models` with `TemporalDurability(models=...)`. Otherwise delegations run in an activity, or in a child workflow when you opt in (see [Delegates as child workflows](#delegates-as-child-workflows)), neither of which has access to the parent run’s model, so a delegate needs a model of its own (or, in an activity, a `models` option); see [delegation on Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#harness-workspace-capabilities).

## Per-delegate run controls

Each `SubAgent` carries its own budgets, so one delegate’s controls do not touch the others. A `SubAgent` with no controls set runs with the `SubAgents` defaults.

```python
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai_harness import SubAgent, SubAgents

reproducer = Agent('anthropic:claude-opus-5-5', instructions='Reproduce the reported bug from a minimal script.')
librarian = Agent('anthropic:claude-opus-5-5', instructions='Find relevant docs, issues, and prior art.')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        SubAgents(
            agents=[
                SubAgent(reproducer, usage_limits=UsageLimits(request_limit=35), timeout_seconds=600, max_calls=1),
                SubAgent(librarian, usage_limits=UsageLimits(request_limit=18), timeout_seconds=300, max_calls=2),
            ]
        )
    ],
)
```

| Field | Effect |
| --- | --- |
| `models` | Which keys of the `SubAgents` model menu this delegate may run on, and which one it runs on by default: the first key listed. See “Per-delegation model selection” below. |
| `usage_limits` | A request/token budget for one delegation. The child runs with its own usage accounting, so the budget counts only that child’s requests and tokens (not the parent’s or siblings’). With `forward_usage=True`, the child’s usage is added to the parent’s usage after the delegation. Reaching the budget is a soft outcome (see below), not a run-stopping `UsageLimitExceeded`. |
| `timeout_seconds` | A wall-clock budget for one delegation. When the child exceeds it, its run is cancelled and the parent gets a soft steering message instead of hanging on the child. The cancelled child’s `event_stream_handler` (if any) stops receiving events without a terminal event. |
| `max_calls` | The maximum number of delegations to this sub-agent per parent run. Once reached, further delegations return a soft budget-exhausted message without running the child. Counts are scoped to one `Agent.run` (a `run_id`) and cleared when it ends, so each parent run and each level of a nested tree budgets independently. |
| `on_failure` | A steering message returned to the parent for any soft degradation of this delegate, in place of the built-in default. While `on_model_error` is unset, setting it also makes child failures soft (see below). |
| `on_model_error` | What the parent gets when the child fails with a soft model error: `'retry'` raises a parent `ModelRetry`, `'return'` returns the error and the steering message as a normal tool result (see below). Unset keeps `'return'` with the `on_failure` message alone when `on_failure` is set, and `'retry'` otherwise. |
| `contain_errors` | Whether an unexpected crash in this delegate is caught and returned to the parent as a bounded `ModelRetry` instead of aborting the parent run (see below). Unset inherits the `SubAgents(contain_errors=...)` default (off). |
| `keep_partial_output` | Whether a child stopped by `timeout_seconds` or its own `usage_limits` passes on its last text response to the parent (see below). Off by default. |

## Per-delegation model selection

The orchestrator knows how hard a task is at the moment it writes the brief, so it is the right place to decide which model runs it. Configure a `models` menu and the delegate tool gains a `model` argument that names one of its keys.

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai_harness import SubAgent, SubAgents
from pydantic_ai_harness.sub_agents import ModelOption

reviewer = Agent('anthropic:claude-opus-5-5', name='reviewer', description='Reviews a diff')
linter = Agent('anthropic:claude-opus-5-5', name='linter', description='Runs the linter and reports failures')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        SubAgents(
            agents=[SubAgent(reviewer), SubAgent(linter, models=['fast'])],
            models={
                'fast': 'anthropic:claude-haiku-5-5',
                'standard': 'anthropic:claude-sonnet-5-5',
                'deep': ModelOption(
                    'anthropic:claude-opus-5-5',
                    description='hard reasoning, multi-file changes',
                    settings=ModelSettings(thinking='xhigh'),
                ),
            },
        )
    ],
)
```
- **Off by default.** With no `models` menu the `model` argument is not in the tool schema at all, and every delegation runs exactly as it did before.
- **The keys are the interface.** They are listed in the system prompt with each entry’s model and description, and the tool schema offers them as an enum, so the model picks from the menu instead of inventing a model name. Name them for the job (`'fast'`, `'deep'`), not for the vendor.
- **An entry is a model or a `ModelOption`.** `ModelOption(model, description=..., settings=...)` adds a routing hint and per-option `ModelSettings`, so one key can mean “same model, more thinking”. Those settings merge over the sub-agent’s own `model_settings`, which keeps the parts the option does not set.
- **Resolution order.** The key the parent passed, else the delegate’s first allowed key (see below), else the delegate’s own model, else the parent run’s model.
- **A delegate can be restricted.** `SubAgent(linter, models=['fast'])` pins that delegate to `fast`: the first listed key is what it runs on when the parent passes no `model`, and the others are refused with a `ModelRetry`. The restriction is rendered in the prompt listing (`- linter: Runs the linter (models: fast)`). Restricting to a key the menu does not define is a `ValueError` at construction.
- **A rejected key costs nothing.** An unknown or unavailable key comes back as a `ModelRetry` listing the valid options, before the delegate’s `max_calls` budget is charged.

## Per-delegation working directory

Set `workspace_resolver` to offer `delegate_task(working_directory=...)`. The async callback receives the parent `RunContext` and a `DelegationWorkspaceRequest` with the delegate name and requested directory, and returns a `Workspace`. The host validates the request and decides which delegates may use another workspace. Without this option, the tool omits `working_directory` and children inherit the parent’s workspace.

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.exceptions import ModelRetry
from pydantic_ai.workspaces import LocalWorkspaceBackend, Workspace
from pydantic_ai_harness.file_system import FileSystem
from pydantic_ai_harness.sub_agents import DelegationWorkspaceRequest, SubAgent, SubAgents

workspaces: dict[str, Workspace] = {'/repos/policy': Workspace(LocalWorkspaceBackend('/repos/policy'))}

async def resolve_workspace(ctx: RunContext[object], request: DelegationWorkspaceRequest) -> Workspace:
    if request.agent_name != 'reviewer' or request.directory not in workspaces:
        raise ModelRetry('Choose the reviewer and a configured directory.')
    return workspaces[request.directory]

reviewer = Agent(name='reviewer', deps_type=object, capabilities=[FileSystem(read_only=True)])
delegation = SubAgents(
    agents=[SubAgent(reviewer, read_only=True)],
    workspace_resolver=resolve_workspace,
)
```

The child runs with the returned workspace, so its relative file paths and repository instructions use that directory. Read-only restrictions from the parent or `SubAgent(read_only=True)` still apply. Also limit the delegate to trusted read-only tools: arbitrary Python tools can bypass the workspace API. The resolver must preserve any additional backend restrictions the application requires.

The caller owns the returned workspace and keeps its resources alive until background children finish. Managed tasks record the resolved directory in `DelegationTask.working_directory`. On resume, omitting the argument resolves that saved directory again; changing it is rejected. The resolver must therefore accept its own resolved directory spelling. Older tasks without this field inherit the parent workspace. Remote and durable delegations reject directory overrides. This option does not change where disk agent definitions are discovered: `SubAgents.workspace` controls that separately.

## Failure handling

A *soft outcome* returns a steering message to the parent as a normal tool result, so its model reads the message and decides what to do next (rather than immediately re-delegating, which a `ModelRetry` invites). A timeout, a reached `usage_limits` budget, and an exhausted `max_calls` budget are always soft. When `on_failure` is set, the message it carries replaces the built-in default for these outcomes.

With `keep_partial_output=True`, a delegation stopped by its timeout or its own usage budget also hands the parent the child’s last text response, so the work the child did before it stopped reaches the parent. It follows the steering message (or `on_failure`), framed as `<partial_output>...</partial_output>`, and the outcome stays `timeout` or `budget`. `DelegationFinishedEvent.output` carries the same text, bounded like any other output. The text has not passed the child’s output validation. It is the last thing the child said, not an answer it approved, and can be text the child’s output validator or `OutputGuardrail` rejected, so leave this off for a child whose guardrails keep content from its parent. Text from a response the child answered with a retry is skipped, as is a final response the run stopped before acting on, or one with an output tool call the stop cut off before its verdict. A child with no such text returns the steering message alone.

A sub-agent run that ends with `DeferredToolRequests` (its `output_type` includes it and a tool needed approval or was deferred) is a soft outcome too. The parent cannot approve the child’s tool calls or resume its run, and delegating the same task again would most likely stop the same way, so instead of returning the marker as output the delegation returns a steering message naming the sub-agent and why it stopped, or the `on_failure` message when that is set. A sub-agent that resolves its own deferred calls, for example with [`HandleDeferredToolCalls`](https://pydantic.dev/docs/ai/capabilities/handle-deferred-tool-calls/), never ends this way and returns its output as usual. A run that ends with `PendingModelResponse` (its `output_type` includes it and a model request was left waiting on the provider, for example in a batch) returns a steering message the same way, including on a remote worker, and the request is cancelled, since nobody will check on it later. Cancelling is best effort, and a [batch](https://pydantic.dev/docs/ai/core-concepts/batch/) is only cancelled once no other request in it is still waiting.

A sub-agent run that fails with a *soft model error* (`ModelRetry`, `UnexpectedModelBehavior`, e.g. it exhausted its own retries) is, by default, converted into a `ModelRetry` for the parent — so the parent’s model sees `Sub-agent '<name>' failed: ...` and can react by re-delegating. The delegate tool defaults to `tool_retries=2`, so the parent aborts only after that many consecutive delegate failures; the counter resets after any successful delegation. Raise `tool_retries` to tolerate a flakier sub-agent, or set `None` to inherit the parent agent’s default tool retries. Set `on_model_error='return'` for a delegate to make its failures soft instead: the child error comes back as a normal tool result, `Sub-agent '<name>' failed: ...` followed by the `on_failure` message or a default steering message. `on_model_error='retry'` keeps the parent `ModelRetry` even when `on_failure` is set, so `on_failure` only customizes the other soft outcomes. With `on_model_error` unset, setting `on_failure` makes failures soft and returns the `on_failure` message alone, without the error.

Hard errors propagate to stop the whole run. A `UsageLimitExceeded` from a child that has *no* per-delegate `usage_limits` (so it shares the parent’s accounting) means the whole tree is out of budget and propagates; a child reaching its *own* `usage_limits` is soft, as above.

An *unexpected crash* — any other exception the child raises, such as a provider `ModelAPIError`/`FallbackExceptionGroup` or a plain `ValueError` from a bad tool argument — propagates by default and aborts the parent run. Set `contain_errors=True` (per delegate, or as the `SubAgents` default) to catch it and return it to the parent as a bounded `ModelRetry` instead, so one delegate crash cannot kill the whole run. Containment stays loud: the exception rides the retry message (`Sub-agent '<name>' crashed: ...`), it is logged via the standard `logging` module, and `tool_retries` still bounds consecutive crashes into an abort. This is orthogonal to `on_failure` — a contained crash always raises the loud retry, never the soft `on_failure` return, so a genuine bug is never masked as success. Cancellation, a shared `UsageLimitExceeded`, pydantic-ai control-flow signals (`CallDeferred`, `ApprovalRequired`, the `Skip*` signals), and `UserError` bypass containment regardless of `contain_errors`. Cancellation covers both kinds: external cancellation (`asyncio.CancelledError`) propagates as-is, and a child’s own first-party cancellation (`RunContext.cancel()` inside the child, raising `RunCancelled`) leaves the delegate tool uncontained, after which pydantic-ai isolates it as a failed `delegate_task` return the parent model can react to, not a crash retry that invites re-delegation.

## Events

`SubAgents` emits typed capability events in the `sub_agents` namespace so a host can show a delegation as it runs, and how it ended, without parsing the delegate tool’s arguments and result:

| Event | Dispatch | When | Payload |
| --- | --- | --- | --- |
| `DelegationStartedEvent` | stream | a delegation passed every check and the child run is about to start | `agent_name`, `task`, `truncated`, `model` (the menu key, or `None`), `inherits_tools` |
| `DelegationFinishedEvent` | stream | the delegation settled into what the parent receives | `agent_name`, `outcome`, `output`, `truncated`, `usage`, `duration_ms` |

Both are notifications. One delegation is one `delegate_task` call, so a start and its end share the `tool_call_id` core stamps on every event; that is how a subscriber pairs them when the model delegates in parallel. `duration_ms` is in milliseconds. `duration_seconds` is its deprecated name: it still reads, in seconds and with a warning, and a payload saved under it still loads.

`outcome` follows the failure handling above: `ok` (the child’s output went back to the parent), `timeout`, `budget` (the child’s own `usage_limits`), `failed` (a soft model error, returned as a tool result or raised as a `ModelRetry` per `on_model_error`, or a child run that ended with `DeferredToolRequests` or `PendingModelResponse`, returned as a steering message), or `contained` (a crash `contain_errors` caught). `output` is what the delegate tool hands back to the parent in each case: the child’s output, the steering message, or the retry text. It is emitted from inside the tool, before any `ToolGuardrail` result guard screens that text for the model; a host that needs the screened version reads the `ToolReturnPart` in core’s `FunctionToolResultEvent`. `usage` is the child’s own `RunUsage` when it has separate accounting (`usage_limits` set, or `forward_usage=False`) and `None` when it accrues into the parent’s usage, where its share is not separable.

A delegation refused before the child runs (an unknown sub-agent, a model key off the menu, an exhausted `max_calls` budget) emits nothing; the tool result says why. An exception that propagates out of the delegate tool (a shared usage limit, an uncontained crash, a cancellation) ends without an end event. A `SubAgentToolset` registered directly in `Agent(toolsets=[...])` has no owning capability and emits nothing. As with any capability event, a listener that raises aborts the parent run.

Their `task` and `output` are cut at `MAX_EVENT_TEXT_CHARS` (4096) with a `truncated` flag, so these two events cannot flood a persisted or forwarded event stream with one verbose delegation. The [task events](#task-events) and `AgentCreatedEvent` are not cut.

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability, on_event
from pydantic_ai_harness.sub_agents import DelegationFinishedEvent, SubAgent, SubAgents

class ReportDelegations(AbstractCapability):
    @on_event(DelegationFinishedEvent)
    async def on_delegation_end(self, ctx, event: DelegationFinishedEvent) -> None:
        print(f'{event.agent_name}: {event.outcome} in {event.duration_ms / 1000:.1f}s')

researcher = Agent('anthropic:claude-opus-5-5', name='researcher')
agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agents=[SubAgent(researcher)]), ReportDelegations()],
)
```

Nested model streaming from the child run is not an event concern; pass an `event_stream_handler` for that.

See [capability events](https://pydantic.dev/docs/ai/capabilities/overview/#capability-events) for how `@on_event` works.

`SubAgents` emits no OpenTelemetry spans for plain delegation: the child run is a core agent run with its own spans nested under the parent’s tool-call span, and the events above carry the outcome a trace would only show as an exception or a tool result.

Task control records its own decisions, which core’s spans don’t show, as zero-duration spans on the delegating run’s tracer, with `sub_agents.`\-prefixed attributes, including `sub_agents.agent_name` (for a created agent, whose name the model chose, only as content) and, for a task, `sub_agents.task_id`:

| Span | When | Attributes |
| --- | --- | --- |
| `sub_agents vetoed` | a listener vetoed a task, message, answer, cancellation, or created agent | `sub_agents.event` (the vetoed event’s kind), `sub_agents.veto_reason` |
| `sub_agents task backgrounded` | a task moved to the background | `sub_agents.reason`: `requested`, `auto`, or `question` |
| `sub_agents question answered` | a listener answered a task’s question, not the model | `sub_agents.question`, `sub_agents.answer` |
| `sub_agents task refused` | `max_running_tasks` refused a delegation | `sub_agents.running_tasks`, `sub_agents.max_running_tasks` |
| `sub_agents task not accepted` | no worker picked a remote task up within `accept_timeout` | `sub_agents.accept_timeout` |
| `sub_agents remote task stopped` | a remote task ended without its worker’s report, and its worker was told to stop it |  |

A veto reason, question, or answer, and the name a vetoed `create_agent` call asked for, are attached only when the run’s instrumentation includes content. While a top-level run waits for its background tasks, a `sub_agents wait for tasks` span covers the wait, with `sub_agents.running_tasks`.

## Task control

By default a delegation finishes inside the `delegate_task` call that started it. With `task_control=TaskControl()`, delegations become tasks the model manages: they can run in the background, ask questions, be steered or cancelled, and be resumed.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent, SubAgents
from pydantic_ai_harness.sub_agents import TaskControl

researcher = Agent('anthropic:claude-opus-5-5', name='researcher', description='Researches a topic and reports findings')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agents=[SubAgent(researcher)], task_control=TaskControl(auto_background_after=60))],
)
```

| Tool | Purpose |
| --- | --- |
| `delegate_task(agent_name, task, background=False, resume=None)` | Start a task, or resume a finished one with its task ID. `background=True` returns a receipt right away. |
| `list_tasks()` | The tasks this run started and the tasks they started, with status and IDs (the 50 most relevant). |
| `check_task(task_id)` | What one of those tasks is doing now, without waiting for it: its elapsed time, the model requests, last five tool calls and latest text of its current run, and any question it waits on. A finished task shows only its outcome. |
| `message_task(task_id, message)` | Steer a running task; it reads the message, as sent, at its next model request. A task’s instructions tell it its delegating agent may send it messages. A finished task resumes with the message as its prompt, in the background if it ran there, through a `delegate_task(resume=...)` call that the delegate tool’s hooks and approvals see and that counts as a second tool call. |
| `answer_task(task_id, answer)` | Answer the question a task is waiting on. |
| `cancel_task(task_id, force=False)` | Stop a task before its next model request, or right away with `force=True`, together with the tasks it started. |

- **Reports and questions arrive as messages.** A background task’s report is `<task_output>` data, and a task’s question `<task_question>` data, on the user channel; the task-control instructions tell the model both are untrusted task data. A top-level run whose model ends while its background tasks still run waits for them, so their reports become its next request.
- **Questions.** Each sub-agent gets an `ask_parent(question)` tool. A question moves its task to the background, because the delegating model can only answer once `delegate_task` returns, and reaches that model as a message. Turn it off per delegate with `SubAgent(can_ask_questions=False)`. A task that can’t run in the background (a run-owned workspace that isn’t local) gets no `ask_parent`.
- **Limits.** `TaskControl(auto_background_after=...)` moves a task still running after that many seconds to the background. `TaskControl(max_running_tasks=...)` caps how many tasks a conversation runs at once, across its whole delegation tree. `SubAgent(resumable=False)` makes a delegate one-shot (see [Managed delegation sessions](#managed-delegation-sessions) for `one_shot`). All are off by default.
- **Who controls a task.** Only the run that started a task can message, answer, or resume it. Any run above it can cancel it.
- **Each run gets an owner.** When no `DelegationTasks` is bound, `SubAgents` opens one for the run and cancels the tasks still running when the run ends. Delegations then follow the owner’s rules in [Managed delegation sessions](#managed-delegation-sessions), including how a delegate’s `usage_limits` apply. Another agent’s run that one of the run’s tools starts is not a task, and doesn’t share the owner. Bind your own owner to keep tasks across runs, persist them, and observe them.
- Only one `SubAgents` on an agent can set `task_control`. The deprecated wrapper agents, such as `TemporalAgent`, give a run no durability capability, so the checks below can’t catch them; don’t use task control or `dynamic_agents` with them.
- On Temporal and DBOS, task control keeps the tasks in the workflow and runs each in a durable unit of its own, so recovery replays a background task’s events and reuses its result. On replay, a task sent to the background on request can get its `TaskBackgroundedEvent` after it settles. A durable task can’t ask questions, take messages, or be resumed, `cancel_task` stops it right away, and its report reaches the model when the run would otherwise end, not at its next request. On DBOS, a replayed `list_tasks` can show a task’s status as of a different moment. A durable task’s history is not updated while it runs, so `check_task` shows only its status and elapsed time. Under durable execution, these raise a `UserError`:
	- task control with `include_self`, `remote_agents` or `forward_events`
		- task control with `auto_background_after` or `max_running_tasks` outside Temporal
		- task control or `dynamic_agents` on another durable engine, or within a bound `DelegationTasks` owner
- On Temporal and DBOS, `dynamic_agents` keeps the roster in the workflow and runs each delegation other than to `self` in a durable unit of its own, on the parent run’s model unless the created agent has one, so recovery rebuilds the created agents and reuses each delegation’s result. The `factory` runs again on replay, so keep it deterministic. Engines that record each tool call in a unit of its own would lose the roster on replay, so they raise a `UserError`. Under any durability capability, `SubAgents` needs an `id`, which it has by default; `id=None` raises a `UserError`.
- Task control and `DelegationTasks` run tasks as asyncio tasks, so they need the asyncio event loop: AnyIO’s Trio backend is not supported.

### Task events

With task control, every step of a task is a typed capability event in the `sub_agents` namespace. A task’s events go into the event stream of the run that started it, so a nested task’s events reach its own parent’s run. A bound `DelegationTasks` observer also receives them as `DelegationTaskEvent(event=...)`, including those of a task that settles after its delegating run ended. In place of `TaskProgressEvent`, it receives the task run’s own events, as it always did.

| Event | When | A listener can |
| --- | --- | --- |
| `TaskAssignedEvent`, `TaskResumedEvent` (`TaskRequestEvent` matches both) | a task is about to start, or to resume | rewrite `prompt`, or `veto()` it |
| `TaskStartedEvent` | the task’s run is starting, locally or on a worker |  |
| `TaskBackgroundedEvent` | the task moved to the background; `reason` is `requested`, `auto`, or `question` |  |
| `TaskProgressEvent` | an event of the task’s own run, with `TaskControl(forward_events=True)` |  |
| `TaskQuestionAskedEvent` | the task asked a question | set `answer`, so the model is not asked |
| `TaskAnsweredEvent` | an answer is about to reach the task | rewrite `answer`, or `veto()` it |
| `TaskSteeredEvent` | a steering message is about to reach the task | rewrite `message`, or `veto()` it |
| `TaskCancelRequestedEvent`, `TaskForceCancelRequestedEvent` | a cancellation is about to reach the task | `veto()` it |
| `TaskRetriedEvent` | a worker is running a failed remote task again |  |
| `TaskCompletedEvent`, `TaskFailedEvent`, `TaskCancelledEvent` | the task settled | rewrite `output` of a completed task |

Unlike `DelegationStartedEvent` and `DelegationFinishedEvent`, these events are not cut at `MAX_EVENT_TEXT_CHARS`: each is the message itself, which a transport carries to the other side, so a prompt, question, answer, or output arrives whole. Nor is `AgentCreatedEvent`. A listener that persists or forwards them bounds them itself.

Events listeners can change are dispatched immediately, so their decisions take effect. A vetoed message is not sent, and the model is told why. With a bound `DelegationTasks`, `DelegationStartedEvent` and `DelegationFinishedEvent` go to its observer only, as in [Managed delegation sessions](#managed-delegation-sessions); with the run’s own owner, they go to the run as before.

Earlier releases named some of these differently. The old class names still import from the deprecated `pydantic_ai_harness.subagents` path, with a `HarnessDeprecationWarning`: `SubAgentMessage`, `ParentMessage` and `ChildMessage` (each now ends in `Event`), `TaskFollowUpEvent` (`TaskResumedEvent`), `TaskMessageEvent` (`TaskSteeredEvent`), `TaskAnswerEvent` (`TaskAnsweredEvent`), `TaskCancelRequestEvent` (`TaskCancelRequestedEvent`), `TaskForceCancelEvent` (`TaskForceCancelRequestedEvent`), `TaskQuestionEvent` (`TaskQuestionAskedEvent`) and `TaskRetryEvent` (`TaskRetriedEvent`). Each event’s `kind` is unchanged. `AgentCreatedEvent.name` is now `agent_name`, and `parent_id` on `DelegationStartedEvent` and `DelegationFinishedEvent` is now `parent_task_id`: the old attributes still read, with the same warning, and an event serialized under an old key still loads. Constructing one of these events takes the new keyword only. They serialize under the new keys: update code that reads a serialized event by key, and upgrade any process that loads events this release writes.

```python
from pydantic_ai.capabilities import AbstractCapability, on_event
from pydantic_ai_harness.sub_agents import TaskAssignedEvent, TaskQuestionAskedEvent

class DelegationPolicy(AbstractCapability):
    @on_event(TaskAssignedEvent)
    async def check_task(self, ctx, event: TaskAssignedEvent) -> None:
        if 'production' in event.prompt:
            event.veto('ask the user before touching production')

    @on_event(TaskQuestionAskedEvent)
    async def answer_known(self, ctx, event: TaskQuestionAskedEvent) -> None:
        if event.question == 'Which branch?':
            event.answer = 'main'
```

### Remote sub-agents

A `SubAgentWorker` serves agents to delegating agents in other processes. The delegating side lists them as `RemoteSubAgent`s, by name, and reaches them through a `SubAgentTransport`:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.sub_agents import RemoteSubAgent, SubAgents, SubAgentWorker, TaskControl

transport = ...  # a SubAgentTransport both processes reach

# In the process that hosts the agent:
async def serve():
    researcher = Agent('anthropic:claude-opus-5-5', name='researcher')
    await SubAgentWorker(agents={'researcher': researcher}, transport=transport, deps=None).serve()

# In the delegating process:
orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        SubAgents(
            task_control=TaskControl(
                remote_agents=[RemoteSubAgent(name='researcher', description='Researches a topic')],
                transport=transport,
            )
        )
    ],
)
```
- **A transport is a set of mailboxes.** Implement `send`, `receive`, and optionally `release` over a WebSocket, a Redis list, or anything else that moves bytes, using `serialize_message` and `deserialize_message` at the boundary. Every message is one of the `SubAgentMessageEvent`s above. `InMemoryTransport` serves a worker in the same process.
- **The transport is the trust boundary.** Anyone who can send to it can run the served agents, with their tools and `deps`, and read what they return. Put authentication, authorization, and network binding in your transport. A worker’s output and errors reach the delegating model like a local delegate’s: in the foreground as tool results, in the background as framed reports.
- **A transport reports a lost worker.** A worker that stops sends `TaskFailedEvent` for the tasks it was running. One that dies without doing so can’t: the delegating run then waits for its report until the run is cancelled, unless `receive` raises when the worker is gone. Heartbeats are not part of the protocol.
- **The worker runs the agent** with its own model, tools, and `deps`, which never cross the transport. It takes the agents it serves by name, without per-delegate run controls: those belong to the delegating side’s `SubAgents`. It applies the delegating run’s usage limits to the task’s own usage, and continues the delegating run’s trace. The usage it reports with the settled event is added to the delegating run’s usage, unless `forward_usage=False`.
- **A task nobody picks up fails.** The worker sends `TaskStartedEvent` when it starts a task. A remote task that no worker picks up within `TaskControl.accept_timeout` seconds (default `30`) fails, and a remote task that stops without its worker’s report, for example because its delegating run ended, is force-cancelled on the worker.
- `SubAgentWorker(retries=...)` runs a failed task again from its prompt, with a `TaskRetriedEvent`. The worker keeps up to `max_conversations` task conversations (default `1000`) so they can be resumed. The conversation stays in that worker, so serve each remote agent name from one worker: a follow-up that reaches another worker fails, since it has no conversation to resume.
- A remote agent runs on its worker’s model, so `delegate_task` refuses a `model` for it, and its delegations emit no `DelegationStartedEvent` or `DelegationFinishedEvent`.

### Agents the model creates

With `dynamic_agents`, the model gets a `create_agent(name, description, instructions, model=None)` tool and can delegate to the agents it creates until the run ends. This works with or without task control.

```python
from pydantic_ai_harness.sub_agents import DynamicAgents, SubAgents

SubAgents(models={'fast': 'anthropic:claude-haiku-5-5'}, dynamic_agents=DynamicAgents(models=['fast'], max_agents=3))
```
- A created agent is an `Agent` with the model-written instructions and no tools, on the `models` key it was created with, or on the delegating run’s model when `DynamicAgents.models` is empty. It has no `name` or `description` of its own, since tracing records those even without content. The model delegates to it by the name it gave in `create_agent`. The description goes only to a custom factory, as `DynamicAgentSpec.description`, and is never shown to the model: created agents aren’t added to the cache-stable roster. Pass `DynamicAgents(factory=...)` to build it yourself from the `DynamicAgentSpec`.
- An `AgentCreatedEvent` is dispatched immediately before the agent is created: a listener can rewrite its `instructions` (and its `description`, which only a custom factory reads), or `veto()` it.
- `max_agents` (default `5`) caps how many agents one run creates. Only one `SubAgents` on an agent can set `dynamic_agents`.

Task control, remote agents, and created agents are a port of [`subagents-pydantic-ai`](https://github.com/vstorm-co/subagents-pydantic-ai), a community package by [Vstorm](https://vstorm.co/) (MIT licensed).

## Managed delegation sessions

`SubAgents` delegates in the foreground only, unless a caller opens and binds a `DelegationTasks` owner. The owner adds `background` and `resume` to the delegate tool’s schema, gives every child a stable conversation ID, and owns every worker, an asyncio task, until shutdown. No extra agent loop is implemented.

Use `DelegationReports` on the parent run to deliver settled background reports through core’s queued-message API. Each report is a `TaskOutputPart` holding the child’s output as `<task_output task_id="..." agent_name="...">` data on the user channel, with `outcome="..."` added when the task didn’t succeed, like a background tool’s `<tool_result>`. The output was written by a model, so it never enters system voice: a note in the application’s voice says the sub-agent wrote it, not the user or the application. The output goes out as the child wrote it; text in it that looks like the frame’s own tag or an application frame such as `<system>` gets a further note naming the sub-agent as its author, so it can’t end the frame early or speak as the application. Nothing else precedes the frame: the acceptance receipt the parent got at launch already said a report would follow.

Reports default to `priority='when_idle'` so active parents finish their current work first. A host that starts an idle continuation should use `DelegationReports(..., priority='asap')` and `agent.run(None, ...)`: pending reports then enter the first model request, with no synthetic user prompt. The host owns wake-up scheduling between runs. A report or question that arrives after a run has read its last queued messages is kept for the conversation’s next run.

A task’s question arrives the same way, as a `TaskQuestionPart` framed as `<task_question task_id="..." agent_name="...">`. Find reports and questions in history by these types, or with `is_task_report(part)`, which also recognizes the user text an earlier version delivered them as, for example to keep them out of a transcript of what the user typed. The Vercel AI and AG-UI message conversions leave capability parts out, so reports and questions stay in server-side history.

```python
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai_harness.sub_agents import DelegationReports, DelegationTasks, SubAgents

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[SubAgents(include_self=True)])
tasks = DelegationTasks(directory=Path('.task-history'))

async def converse():
    async with tasks.opened():
        with tasks.bind():
            result = await agent.run(
                'Delegate an independent investigation in the background.',
                conversation_id='review',
                capabilities=[DelegationReports(tasks, conversation_id='review')],
            )
            print(result.output)
            # Keep this owner open across subsequent parent turns.
```

`opened()` cancels and drains workers on exit. If a child hasn’t released its resources within ten seconds, `opened()` raises `RuntimeError`, or only logs it when an error is already closing the owner, so that error isn’t masked. A task still running when its process exited is loaded as cancelled when the owner next opens; if it was waiting for an answer, its output names the question, so the parent can resume it with the answer. Keep workspace and plugin resources alive outside that scope. Detached execution is refused for run-owned non-local workspaces; foreground delegation still works. `max_depth=4` counts the main run and allows three child layers. An explicitly configured non-default `SubAgents.max_depth` still takes precedence. Ordinary `SubAgents` retains its original depth default.

`restore(task)` adds a finished `DelegationTask` made elsewhere, such as one imported from another agent’s session, so the parent can resume it by ID. It works before `opened()` too; the owner loads the task when it opens. A task with the same ID that has run since, under a different `run_id`, is kept rather than replaced, and `restore` returns `False`.

`background(task_id)` releases a foreground waiter without restarting the child. `await cancel(task_id)` stops and drains that child and its descendants. A user stop blocks model-requested resume until the application explicitly calls `await allow_resume(task_id)`. `one_shot` names never resume. `SubAgent(resumable=False)` does the same for one delegate, also with the owner `SubAgents(task_control=...)` opens: use `one_shot` when the application binds the owner and decides by agent name, and `resumable` where the delegate is declared. Either one makes the task one-shot. A resume uses the same child ID and its independent history, a new run ID, and the current direct parent. A child waits for its own descendants and consumes their reports before its final output settles. Reports are routed to the direct parent; an idle parent receives pending reports on its next explicitly started run. Enqueue delivery is acknowledged only when core emits `EnqueuedMessagesEvent`, and acknowledgements are persisted. With task control, a child’s `ask_parent` question is routed the same way: `questions(conversation_id=...)` lists the children whose question awaits delivery, and the observer is notified when one starts waiting, so an application can start its idle parent’s next run to answer it.

`steer(task_id, text)` sends a running child a user message on its own run’s queue with `priority='asap'`: the child reads it at its next model request, and one about to finish goes on with it instead. It returns `False` when the child is not running, so an application can offer to resume it. A message sent before the child’s run starts waits for it; one sent as the child’s final response settles may arrive too late for it to read.

An observer receives `DelegationTaskEvent`, with the task identity and an optional correlated child stream event. Events from the child’s own stream also carry the `model_name` and `context_window` of the model streaming that request, so a UI can show the child’s context usage. Managed start/end events carry `task_id` and `parent_task_id`. Managed cancellation and uncontained exceptions produce terminal outcomes; unmanaged events and exception propagation keep their original contract. Metadata and final/interrupted histories are atomically saved under `directory`. Once a task settles and is saved, the owner keeps its history in that file only, so a directory of long-finished tasks doesn’t fill memory: an observer is told a task settled with its history, and after that the task in `records` has empty `messages`. `history(task_id)` reads its history from the file (from async code, call it in a worker thread, as `anyio.to_thread.run_sync(owner.history, task_id)`), and a resume loads it back. To copy a settled task with its history, use `replace(task, messages=owner.history(task.id))`. `snapshot(task_id)` returns a `DelegationSnapshot` of a running task, read from its live history without waiting on it: status, `elapsed_seconds`, the `usage` of its current run’s model responses, its `recent_tool_calls` as `DelegationToolCall`s, and its `latest_text` and `pending_question`, both cut at `MAX_EVENT_TEXT_CHARS`. The child’s final result is left out, so a snapshot doesn’t show a result before `TaskCompletedEvent` listeners process it. A host can render a task list or status line from it, for example on each `DelegationTaskEvent`. `usage` is `None`, with no tool calls or text, when the owner doesn’t see the run’s history as it streams: before the child’s first model request, for a remote task (its history stays on its worker) or a durable one, and once the task settles (its history is in its file). `check_task` gives the model the same view. Pass `step_store` to checkpoint through `StepPersistence` and recover a process-killed child’s latest frontier. Loading an interrupted record never executes its tools. Inspect possible partial effects before an explicit resume. A resume closes out tool calls the interruption left unanswered with an `interrupted` tool return, so the child sees they did not complete.

Each saved file loads on its own. A file that cannot be read or validated, whose name does not match its task ID, or whose saved ancestry loops is skipped and left on disk: `opened()` logs a warning and lists it in `problems` as a `SavedTaskProblem` (its path and the reason), and the other tasks still load. To list a saved task tree without opening an owner or resuming anything, for example from a dashboard or another process, call `DelegationTasks.discover(directory)`. It returns `SavedTasks`, with the loaded `tasks` by ID (follow `parent_id` for the tree) and the same `problems`. `discover()` writes nothing, and returns a task saved as `running` unchanged, since the process that owns it may still be running it.

```python
from pathlib import Path

from pydantic_ai_harness.sub_agents import DelegationTasks

async def show_saved_tasks():
    saved = await DelegationTasks.discover(Path('.task-history'))
    for task in saved.tasks.values():
        print(task.id, task.parent_id, task.agent_name, task.status, task.outcome)
    for problem in saved.problems:
        print(f'Skipped {problem.path}: {problem.reason}')
```

Managed children with `forward_usage=True` share live usage accounting and inherit parent ceilings. A per-child budget is converted to an absolute ceiling at launch; concurrent sibling spend may reach that ceiling earlier, but cannot bypass the parent’s budget. The ordinary unmanaged per-child accounting contract is unchanged.

A locally run child that inherits `count_tokens_before_request=True` from the run’s limits checks each child request against the token and cost ceilings before it is sent when its model implements `count_tokens`. When a child run raises `NotImplementedError` before its first request (such as a child model that does not implement `count_tokens`), the delegation starts the child once more without the up-front count (under a new run ID when the delegation is recorded as a task), so those ceilings are checked against each response’s usage instead. There is no second start once the `usage` the child counts into has counted a request since the child started, so a tool that raises `NotImplementedError` does not run twice; when `forward_usage=True`, a sibling’s request in that window also rules it out. A per-child `usage_limits` that sets `count_tokens_before_request=True` itself is kept, so on such a model the child fails as a top-level run would. A remote worker applies the announced limits as received, so on a model without `count_tokens` the remote task fails.

`agents`, `aliases`, and `instructions` extend the roster and guidance only inside the bound scope; they do not add delegation to an agent without `SubAgents`. `SubAgent(read_only=True)` wraps the child’s workspace in `ReadOnlyWorkspace`. Also give that agent only trusted read-only capabilities: arbitrary Python tools can bypass the workspace API. CLAI’s Explore and Plan specialists use filesystem readers and expose no shell, code execution, or parent plugin tools.

Core’s agent/model/tool spans provide execution telemetry; task IDs, parent IDs, and child run IDs provide correlation. This owner adds no logging exporter.

## Durable execution

### Delegates as child workflows

By default, on Temporal a delegation to an agent other than `self` runs in an activity, and on DBOS it runs inline in the parent workflow, so a delegate’s own durability does nothing. To keep it, run the delegate tool as a child workflow ([Temporal](https://pydantic.dev/docs/ai/capabilities/durable_execution/temporal/#child-workflows), [DBOS](https://pydantic.dev/docs/ai/capabilities/durable_execution/dbos/#child-workflows)) with [`SetToolMetadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.SetToolMetadata):

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import SetToolMetadata
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai_harness.sub_agents import SubAgent, SubAgents

worker = Agent('anthropic:claude-opus-5-5', name='worker', capabilities=[TemporalDurability()])

lead = Agent(
    'anthropic:claude-opus-5-5',
    name='lead',
    capabilities=[
        SubAgents(agents=[SubAgent(worker)]),
        SetToolMetadata(tools=['delegate_task'], temporal={'child_workflow': {}}),
        TemporalDurability(),
    ],
)
```

On DBOS, use `DBOSDurability()` and `SetToolMetadata(tools=['delegate_task'], dbos={'child_workflow': {}})`. The delegate’s model requests and tool calls are then recorded in the child’s history rather than the parent’s.

- Every delegate must be durable on the parent’s engine: the tool body runs as workflow code.
- On Temporal, register each delegate with the worker too, for example with an [`AgentPlugin`](https://pydantic.dev/docs/ai/api/pydantic-ai/durable_exec/#pydantic_ai.durable_exec.temporal.AgentPlugin).
- `include_self`, `inherit_tools`, `models`, `shared_capabilities`, `event_stream_handler`, `dynamic_agents`, `task_control`, and a delegate’s `max_calls` rely on parent-run state the child workflow doesn’t receive, so a delegation with any of them raises a `UserError`.
- The delegate’s usage isn’t reliably counted in the parent run’s usage, and the parent’s usage limits don’t bound it.
- The delegation depth isn’t carried into the child workflow, so if a delegate’s own `SubAgents` also opts in, `max_depth` counts again from each child workflow and no longer bounds the tree.

## Discovery

The sub-agents are listed in the system prompt via `get_instructions`, using each agent’s `description` (or a `SubAgent(description=...)` override). A sub-agent with no description is listed by name alone.

## Loading sub-agents from disk

A repo’s agent definitions can become delegates without writing any `Agent` code. With `agent_folders` set, every Claude-style `*.md` file and Codex-style `*.toml` file under those folders is loaded as a sub-agent, alongside the explicitly-passed `agents`. Files are read in sorted filename order.

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgents

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agent_folders='agents')],  # loads .agents/agents/ from the run's workspace
)
```

Definitions are read at the start of every run from the run’s [workspace](https://pydantic.dev/docs/ai/core-concepts/workspace/), so a sandbox’s agent files are found and nothing is read from your home directory. To read them from somewhere else, such as definitions that ship with your application, pass `workspace=LocalWorkspaceBackend('/app')`.

`agent_folders` controls which folders are read:

- A folder-name `str` (`'agents'` is the conventional layout): load from `.agents/<name>/`, `.claude/<name>/`, and `.codex/<name>/` under the workspace’s working directory, in that order, so a workspace that uses `.agents/` for something else (such as skills) still loads agents from the others. A run without a workspace skips them.
- A sequence of workspace paths, absolute or relative to the working directory, loads from exactly those folders, in order.
- `None`, the default, disables disk loading, exposing only the explicitly-passed `agents`.

Folders are read only through a workspace. A run without a workspace fails at its start when given a path sequence. Convention discovery warns once when it skips a `.agents/` or `.claude/` folder in the current or home directory that the workspace does not reach, naming the folder and the `workspace=` that reads it.

### Definition format

A definition is a Claude-style markdown file with optional frontmatter, or a Codex-style TOML file. Markdown:

```markdown
---
name: researcher
description: Researches a topic and reports findings
tools: Read, Grep
---
You research topics. Report your findings, each with a source.
```
- `name` is the delegate name (how the parent refers to it and how it is listed). It falls back to the filename stem when absent.
- `description` drives the prompt listing.
- The markdown body becomes the agent’s instructions.
- `tools` (or `allowed-tools`) is a comma-separated string or a YAML block list. See “Tools” below.
- `model` and `color` are ignored: the model is inherited from the parent (see below), and `color` has no pyai equivalent.

Frontmatter is read by a small, dependency-free parser limited to those keys (`pyyaml` is not a harness dependency). Full YAML frontmatter is not supported.

A Codex-style standalone TOML file:

```toml
name = "reviewer"
description = "Reviews code for bugs"
developer_instructions = "Inspect the code and report findings. Do not edit files."
tools = ["Read", "Grep"]
```
- `name`, `description`, and `developer_instructions` are required nonempty strings.
- `tools` (or `allowed-tools`) is optional: a list of strings or a comma-separated string, not both keys.
- `model`, `effort`, `model_reasoning_effort`, and `color` are ignored with a warning; use `agent_overrides` for models and effort.
- Any other key, including sandbox or permission settings, skips that file with a warning rather than silently granting broader tools. The older `[agents.<name>] config_file` layout is not supported.
- TOML files are parsed with the standard-library `tomllib` module.

Nothing in a definition file is executed. A malformed or invalid file is skipped with a warning without blocking the others.

### Models and effort

Disk agents inherit the parent run’s model by default. Per agent, the caller can override the model and set a thinking/effort level via `agent_overrides`, keyed by the agent’s name:

```python
from pydantic_ai_harness import SubAgents
from pydantic_ai_harness.sub_agents import AgentOverride

SubAgents(
    agent_folders='agents',
    agent_overrides={'researcher': AgentOverride(model='anthropic:claude-opus-5-5', effort='high')},
)
```

When `effort` is unset, the disk agent adds no thinking setting, so the inherited model’s defaults apply. An explicit value, including `False` or `'minimal'`, is passed through unchanged via Pydantic AI’s `ModelSettings.thinking`.

`MINIMUM_EFFORT_FLOOR` and `clamp_effort(level, floor=...)` remain importable from the deprecated `pydantic_ai_harness.subagents` path, with a `HarnessDeprecationWarning`. `SubAgents` no longer uses them. Pass `AgentOverride(effort=...)` when a disk agent needs an explicit level, or apply an application-specific floor outside the capability.

### Tools

Without a `tool_resolver`, a disk agent gets no tools and its `tools` frontmatter is ignored. To map the frontmatter tool names to toolsets, pass a `tool_resolver`: it receives each tool name (so it can honor entries like `Bash(git:*)`) and returns the toolsets that provide it, or `None` for an unknown name, which is skipped with a warning.

```python
from collections.abc import Sequence

from pydantic_ai.toolsets import AgentToolset
from pydantic_ai_harness import SubAgents

TOOLSETS: dict[str, Sequence[AgentToolset[object]]] = {}  # your tool name -> toolsets mapping

def resolve(tool_name: str) -> Sequence[AgentToolset[object]] | None:
    return TOOLSETS.get(tool_name)

SubAgents(agent_folders='agents', tool_resolver=resolve)
```

### Precedence

When the same name appears in more than one source, the higher-precedence one wins and the others are skipped with a warning: explicitly-passed `agents` first; for convention discovery, the workspace’s `.agents/` folder, then `.claude/`, then `.codex/`; and for an explicit path sequence, earlier folders before later ones. A duplicate name within the explicitly-passed `agents` list is still an error.

## Configuration

```python
from pydantic_ai_harness import SubAgents

SubAgents(
    agents=(),             # Sequence[SubAgent[AgentDepsT]] -- each pairs an agent with its run controls
    models={},             # Mapping[str, Model | str | ModelOption] -- per-delegation model menu (off when empty)
    agent_folders=None,    # folder-name str ('agents' is conventional) | Sequence[str | Path] workspace paths | None
    agent_overrides={},    # Mapping[str, AgentOverride] -- per-disk-agent model/effort override
    tool_resolver=None,    # Callable[[str], Sequence[AgentToolset[object]] | None] -- disk-agent tool mapping
    forward_usage=True,    # share the parent's usage with sub-agent runs
    inherit_tools=False,   # deprecated: use include_self=True, or tool_resolver for disk agents
    shared_capabilities=(),# capabilities applied to every sub-agent run
    event_stream_handler=None,  # forwarded to each sub-agent run to stream its events
    tool_name='delegate_task',
    tool_retries=2,        # extra delegate-tool attempts after a sub-agent error before aborting (None inherits the agent default)
    contain_errors=False,  # default for SubAgent.contain_errors: contain an unexpected crash as a bounded retry
    workspace=None,        # WorkspaceBackend to read agent_folders from instead of the run's workspace
    workspace_resolver=None,  # async (ctx, request: DelegationWorkspaceRequest) -> Workspace
    include_self=False,    # also list the running agent itself as the delegate `self`
    max_depth=3,           # delegation levels, counting the top-level run
    task_control=None,     # TaskControl -- background tasks, task-control tools, questions, and task events
    dynamic_agents=None,   # DynamicAgents -- let the model create sub-agents with `create_agent`
)
```
```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent

agent = Agent('anthropic:claude-opus-5-5')

SubAgent(
    agent,                 # AbstractAgent[AgentDepsT, Any] -- the child agent to run
    name=None,             # delegate name; defaults to the agent's own `name`
    description=None,      # prompt-listing description; defaults to the agent's own `description`
    models=None,           # Sequence[str] -- menu keys this delegate may run on; the first is its default
    usage_limits=None,     # per-delegation request/token budget (isolated accounting)
    timeout_seconds=None,  # per-delegation wall-clock budget
    max_calls=None,        # max delegations to this sub-agent per parent run
    on_failure=None,       # steering message for soft degradations of this delegate
    contain_errors=None,   # contain an unexpected crash as a bounded retry; None inherits the SubAgents default
    on_model_error=None,   # 'retry' or 'return' for a child ModelRetry/UnexpectedModelBehavior; None: 'return' iff on_failure is set
    resumable=True,        # whether a finished task can be resumed, with a task owner
    can_ask_questions=True,  # give the sub-agent `ask_parent`, with task_control
    keep_partial_output=False,  # pass on the child's last text when its timeout or usage budget stops it
)
```
```python
from pydantic_ai_harness.sub_agents import TaskControl

TaskControl(
    remote_agents=(),      # Sequence[RemoteSubAgent] -- agents a SubAgentWorker serves
    transport=None,        # SubAgentTransport reaching that worker, required with remote_agents
    accept_timeout=30.0,   # seconds a remote task waits for a worker to pick it up
    auto_background_after=None,  # seconds a delegation waits before its task moves to the background
    max_running_tasks=None,      # tasks a conversation may run at once, across its delegation tree
    forward_events=False,  # forward the events of task runs as TaskProgressEvent
)
```

`SubAgents` is not serializable via the [agent spec](https://pydantic.dev/docs/ai/core-concepts/agent-spec/) (it holds live `Agent` instances), so `get_serialization_name()` returns `None`.

## Notes

- Sub-agents can themselves have `SubAgents`, forming a tree. Each `SubAgents` stops offering delegation once the run is at its own `max_depth`, so a delegate with a higher limit can go deeper than its parent’s. Share `usage` (the default) and set a `usage_limits` on the top-level run to bound the whole tree.
- Delegations the model issues in parallel run as independent sub-agent runs.
- [Pydantic AI capabilities](https://pydantic.dev/docs/ai/capabilities/overview/)
- [Multi-agent applications](https://pydantic.dev/docs/ai/guides/multi-agent-applications/)

## API reference

### SubAgents

**Bases:** `AbstractCapability[AgentDepsT]`

Let an agent delegate self-contained tasks to named sub-agents.

Exposes a single `delegate_task(agent_name, task)` tool. Each delegation runs the chosen sub-agent in a fresh run that does not see the parent conversation. The available sub-agents are listed in the system prompt; a change to the listing between runs of a conversation is appended rather than rewritten.

Delegates come from `agents`, from Markdown or TOML definitions under `agent_folders`, and, with `include_self=True`, from the running agent itself. With a `models` menu, `delegate_task` also takes a `model` argument naming one of its keys. The parent’s `deps` are forwarded to each sub-agent, and delegations nest at most `max_depth` levels.

```python
from pydantic_ai import Agent
from pydantic_ai_harness.sub_agents import SubAgent, SubAgents

researcher = Agent('anthropic:claude-sonnet-4-6', name='researcher', description='Researches topics')
writer = Agent('anthropic:claude-sonnet-4-6', name='writer', description='Writes prose')

orchestrator = Agent(
    'anthropic:claude-opus-4-7',
    capabilities=[SubAgents(agents=[SubAgent(researcher), SubAgent(writer)])],
)
```

#### Attributes

##### agents

The sub-agents to expose, each a `SubAgent` pairing an agent with its per-delegate run controls. See `SubAgent`. These take precedence over any disk-loaded agents of the same name.

**Type:** [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[`SubAgent`\[`AgentDepsT`\]\] **Default:** `()`

##### models

A menu of models the parent can route an individual delegation to, keyed by the name the parent uses to pick one. Off by default: with no menu the delegate tool has no `model` argument and every delegation runs the way it always did.

Each value is a model reference, or a `ModelOption` carrying a routing hint and its own `ModelSettings` (so one key can mean “same model, more thinking”). The keys and their descriptions are listed in the system prompt, so name them for the job — `'fast'`, `'deep'` — rather than for the vendor. `SubAgent.models` restricts which of them a given delegate accepts.

```python
from pydantic_ai_harness.sub_agents import SubAgents

SubAgents(models={'fast': 'anthropic:claude-haiku-4-5', 'deep': 'anthropic:claude-opus-4-7'})
```

**Type:** [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), `Model` | `KnownModelName` | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | `ModelOption`\] **Default:** `field(default_factory=(dict[str, 'Model | KnownModelName | str | ModelOption']))`

##### agent\_folders

Where to load Markdown and standalone Codex TOML definitions from, in addition to `agents`. Off by default: only `agents` are exposed unless this is set. Every folder is read at the start of each run through the run’s workspace (`ctx.workspace`), or through `workspace` when set.

- a folder-name `str` (`'agents'` is the conventional layout): load from `.agents/<name>/`, `.claude/<name>/`, and `.codex/<name>/` under the workspace’s working directory, in that order. Skipped when the run has no workspace.
- a sequence of paths in the workspace, absolute or relative to its working directory: load from exactly those folders, in order. A run with no workspace fails at its start; pass `workspace=LocalWorkspaceBackend('.')` to read them from this machine.
- `None`: no disk loading (the default).

Missing folders are skipped. Within a folder every `*.md` and `*.toml` file is a candidate.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | `Path`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### agent\_overrides

Per-disk-agent overrides keyed by the agent’s name. An entry can set the agent’s `model` (otherwise the parent’s model is inherited) and its `effort` (otherwise no thinking setting is added). Has no effect on explicitly-passed `agents`.

**Type:** [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), `AgentOverride`\] **Default:** `field(default_factory=(dict[str, AgentOverride]))`

##### tool\_resolver

Optional override for how a disk agent gets its tools. When set, each tool name in a definition’s `tools`/`allowed-tools` frontmatter is passed to this resolver and the returned toolsets are attached to that agent; an unknown name (resolver returns `None`) is skipped with a warning. When unset, the frontmatter tool list is ignored and disk agents have no tools of their own.

**Type:** `ToolResolver` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### forward\_usage

If `True`, the parent run’s `usage` is shared with each sub-agent run, so token usage aggregates and usage limits apply across the whole agent tree.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### inherit\_tools

Deprecated: setting it to `True` emits a `HarnessDeprecationWarning`.

If `True`, the parent agent’s own tools (registered via `tools=` or `toolsets=`, not those contributed by capabilities) are exposed to each sub-agent run, minus the delegate tool. Bind required tools directly to explicit sub-agents, use `include_self=True` to delegate to an agent with all of the parent’s tools and capabilities, or use `tool_resolver` to give disk agents tools.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### shared\_capabilities

Capabilities applied to every sub-agent run, in addition to whatever each sub-agent already has.

**Type:** [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[[`AgentCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AgentCapability) \[`AgentDepsT`\]\] **Default:** `()`

##### event\_stream\_handler

If set, this handler is passed to each sub-agent run, so the sub-agent’s model-streaming and tool events surface to the caller. The handler receives the sub-agent’s own `RunContext` and event stream.

**Type:** `EventStreamHandler`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

Name of the delegate tool exposed to the model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `'delegate_task'`

##### id

Fixed, since an agent exposes a single delegate tool. Durable execution requires one.

Two `SubAgents` capabilities would register the same `tool_name` and collide. The shared id makes them merge instead, unioning their rosters, so a packaged harness that delegates can compose with another that does the same.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default='sub_agents', kw_only=True)`

##### tool\_retries

Retries for the delegate tool — how many extra attempts it gets after a sub-agent error before the parent run aborts. A sub-agent failure (e.g. it exhausts its own output retries) surfaces to the parent as a tool retry it can react to by re-delegating with a corrected task. The retry counter resets after any successful delegation, so this bounds consecutive failures, not total ones. Defaults to `2` (pydantic-ai’s per-tool default is `1`) so a repeated flaky sub-agent does not abort the parent run on its first repeat; set `None` to inherit the parent agent’s default tool retries instead.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `2`

##### contain\_errors

Default for `SubAgent.contain_errors`: whether an unexpected sub-agent crash is caught and returned to the parent as a bounded `ModelRetry` instead of aborting the parent run. Off by default, so a crash propagates. Any `SubAgent` can override this per delegate. See `SubAgent.contain_errors` for the containment contract and what always propagates regardless.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### workspace

A workspace to read `agent_folders` from instead of the run’s, such as `LocalWorkspaceBackend('/app')` for definitions that ship with the application.

A backend, not the `LocalWorkspace` capability. It is used in-process only: a durable engine does not route it through its workflow machinery.

**Type:** `WorkspaceBackend` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, kw_only=True)`

##### workspace\_resolver

Opt into `delegate_task(working_directory=...)` with an async callback receiving the parent context and a `DelegationWorkspaceRequest` with the delegate name and requested directory. Return the child’s `Workspace`; the caller owns its resources, including keeping it alive for background tasks. Omission keeps the parent workspace. The callback validates paths and decides which delegates and backends may change directory. Parent and delegate read-only restrictions still apply. Tools that bypass the workspace API need their own restrictions. Remote and durable delegations cannot request another directory. Resuming a task keeps its saved directory; the resolver is called again for that directory. This does not change where `agent_folders` are discovered (see `workspace`).

**Type:** `WorkspaceResolver`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, kw_only=True)`

##### include\_self

If `True`, the roster also lists the running agent itself, as `self`.

A delegation to `self` starts a fresh run of `RunContext.agent` on the parent run’s model (or the `models` option the parent picks), so the delegate has every capability, toolset, and instruction bound to that `Agent` — guardrails, approval gates, and audit hooks included, since they are registered again in the child run. What was passed to the parent’s `run()` rather than bound to the `Agent` (run-level `capabilities`, `toolsets`, `instructions`, `model_settings`) does not carry over, so this capability has to be bound to the `Agent` itself; passing it to `run()` raises a `UserError` when the run starts.

`inherit_tools` does not apply to `self`, whose tools are already the parent’s. The delegate can delegate in turn, up to `max_depth`.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### max\_depth

How many levels a delegation tree may have, counting the top-level run as the first.

The default of `3` lets the top-level run delegate, and its delegates delegate once more. A run at the limit gets neither the delegate tool nor the sub-agent listing. The level is tracked per task tree, across every `SubAgents` capability, and each capability enforces its own limit. This bounds `include_self`, whose delegate carries the delegate tool again, and a roster that reaches the same agent through another path.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `DEFAULT_MAX_DEPTH`

##### task\_control

Let delegations outlive the tool call, and give the model tools to manage them. Off by default.

See `TaskControl`. Only one `SubAgents` on an agent can set it. On Temporal and DBOS, each task runs in a durable unit of its own, which can’t ask questions, take messages, or be resumed. Under durable execution, `include_self`, `remote_agents`, `forward_events`, `auto_background_after` or `max_running_tasks` outside Temporal, other durable engines, and a bound `DelegationTasks` owner raise a `UserError`.

**Type:** `TaskControl` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, kw_only=True)`

##### dynamic\_agents

Let the model create sub-agents during a run, with a `create_agent` tool. Off by default. Only one `SubAgents` on an agent can set it. On Temporal and DBOS, every delegation other than to `self` runs in a durable unit of its own, so recovery rebuilds the created agents and reuses the delegations’ results. Other durable engines, and a bound `DelegationTasks` owner under any of them, raise a `UserError`.

**Type:** `DynamicAgents`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `field(default=None, kw_only=True)`

#### Methods

##### for\_run

`@async`

```python
def for_run(ctx: RunContext[AgentDepsT]) -> SubAgents[AgentDepsT]
```

A per-run copy when agent folders are read; otherwise `self`.

A run at `max_depth` gets a copy without the delegate tool and listing instead. The per-run copy starts from the explicit roster; `before_run` adds the folders’ definitions. Its instructions and toolset are read after that, so they list the delegates this run has.

###### Returns

`SubAgents`\[`AgentDepsT`\]

##### before\_run

`@async`

```python
def before_run(ctx: RunContext[AgentDepsT]) -> None
```

Read the agent folders’ definitions through the workspace and rebuild this run’s roster.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### wrap\_run

`@async`

```python
def wrap_run(
    ctx: RunContext[AgentDepsT],
    *,
    handler: WrapRunHandler,
) -> AgentRunResult[Any]
```

Run the parent agent, then drop this run’s delegation counts so they don’t accumulate.

With `task_control` set, the run gets a `DelegationTasks` owner unless the application bound one, and the task events of its children are published into its event stream.

###### Returns

[`AgentRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult) \[[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)\]

##### after\_output\_process

`@async`

```python
def after_output_process(
    ctx: RunContext[AgentDepsT],
    *,
    output_context: OutputContext,
    output: Any,
) -> Any
```

Keep a top-level run with its own owner going while its background tasks work.

The run waits until they settle, or one asks a question, and their reports become its next request.

###### Returns

[`Any`](https://docs.python.org/3/library/typing.html#typing.Any)

##### get\_instructions

```python
def get_instructions() -> AgentInstructions[AgentDepsT] | None
```

Cache-stable listing of the available sub-agents and models.

A per-run copy returns it as a function, rendered after `before_run` has read the workspace’s definitions; it is the same text on every step of the run.

###### Returns

`AgentInstructions`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### get\_toolset

```python
def get_toolset() -> AgentToolset[AgentDepsT] | None
```

Toolset providing the delegate tool, or `None` when no sub-agents are configured.

A per-run copy returns a function yielding the toolset `before_run` settled on, the same instance for every step of the run.

###### Returns

[`AgentToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AgentToolset) \[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### get\_serialization\_name

`@classmethod`

```python
def get_serialization_name(cls) -> str | None
```

Not spec-serializable — the capability holds live `Agent` instances.

###### Returns

[`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### combine

`@classmethod`

```python
def combine(
    cls,
    capabilities: Sequence[AbstractCapability[AgentDepsT]],
) -> AbstractCapability[AgentDepsT]
```

Compose the rosters, and require everything else to already agree.

Two packaged harnesses on one agent each bring their delegates, and composing them is what the shared `id` is for. Only `agents`, `models`, and `include_self` are composed. Every other field decides how the delegates *run* — what capabilities they are handed, whether they see the parent’s tools, what the delegate tool is called, where delegates are loaded from — so merging it would apply one harness’s policy to the other’s sub-agents, which neither author asked for. Those must agree, and say so when they do not.

Disk definitions are not part of the merge: the per-run copy reads them in `before_run`, after run-level capabilities are combined.

###### Returns

`AbstractCapability`\[`AgentDepsT`\]

### SubAgent

**Bases:** `Generic[AgentDepsT]`

One delegate: a child agent plus its per-delegate run controls.

Pass a sequence of these as `SubAgents(agents=[...])`. The delegate’s name — how the parent model refers to it, and how it is listed in the system prompt — is `name` when set, otherwise the agent’s own `name`. An agent with neither is rejected by `SubAgents`.

Every control below is optional; an unset field leaves the corresponding behaviour at the `SubAgents` default.

#### Attributes

##### agent

The agent that runs when this delegate is invoked.

**Type:** `AbstractAgent`\[`AgentDepsT`, [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)\]

##### name

Name the parent model uses to delegate to this agent. Defaults to the agent’s own `name` when unset.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### description

Description for the system-prompt listing. Defaults to the agent’s own `description` when unset; a delegate with neither is listed by name alone.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### models

Which of `SubAgents.models` this delegate may run on, as menu keys, and which one it runs on by default: the first key listed. Leave it unset to let the parent pick any configured option and to fall back to the delegate’s own model when it picks none. Set it to pin a delegate to one option (`models=['fast']`) or to bound an expensive delegate to a subset. Naming a key the menu does not define is an error.

**Type:** [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### usage\_limits

Request/token budget for one delegation. When set, the child runs with its own usage accounting so the budget counts only the child’s own requests and tokens (not the parent’s or siblings’). When `forward_usage=True`, that usage is added to the parent’s usage after the delegation. Hitting this budget is a soft outcome (steering message), not a run-stopping `UsageLimitExceeded`.

**Type:** [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### timeout\_seconds

Wall-clock budget for one delegation. When the child exceeds it, the run is cancelled and the parent gets a soft steering message instead of hanging on the child.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### max\_calls

Maximum number of delegations to this sub-agent per parent run. Once reached, further delegations return a soft budget-exhausted message without running the child.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### on\_failure

Steering message returned to the parent for any soft degradation of this delegate (timeout, child failure, a child run ending with `DeferredToolRequests` or `PendingModelResponse`, usage budget reached, call budget exhausted), in place of the built-in default. While `on_model_error` is unset, setting it also makes child failures soft: a child error returns this message as a normal tool result instead of raising a parent `ModelRetry`.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### contain\_errors

Whether an unexpected sub-agent crash is contained instead of aborting the parent run. When `True`, an exception the child raises that is not an expected soft degradation (a provider `ModelAPIError`/`FallbackExceptionGroup`, a plain `ValueError` from a bad tool argument, etc.) is caught and returned to the parent as a bounded `ModelRetry`, so one delegate crash cannot kill the whole run. It stays loud: the exception rides the retry message and is logged, and `tool_retries` still bounds consecutive crashes into an abort. Cancellation, a shared usage-limit, pydantic-ai control-flow signals, and `UserError` always propagate regardless. Unset inherits `SubAgents.contain_errors` (default off). Orthogonal to `on_failure`, which only sets the message for expected soft degradations; a contained crash always raises the loud `ModelRetry`.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### on\_model\_error

What the parent gets when the child fails with `ModelRetry` or `UnexpectedModelBehavior`.

`'retry'` raises a parent `ModelRetry` naming the error, bounded by `SubAgents.tool_retries`. `'return'` returns the error followed by the `on_failure` message, or a default steering message, as a normal tool result. Either way `on_failure` only sets message text. Unset keeps the earlier coupling: `'return'` with the `on_failure` message alone when `on_failure` is set, `'retry'` otherwise.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘retry’, ‘return’\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `dataclass_field(default=None, kw_only=True)`

##### read\_only

Run in a `ReadOnlyWorkspace`; supply only trusted read-only tools as well.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `dataclass_field(default=False, kw_only=True)`

##### resumable

Whether a finished task can be resumed, within a `DelegationTasks` owner or with `SubAgents.task_control` set. Set this to `False` for a one-shot agent. `DelegationTasks(one_shot=...)` does the same by name, for an owner the application binds.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `dataclass_field(default=True, kw_only=True)`

##### can\_ask\_questions

Whether the sub-agent gets an `ask_parent` tool to ask the delegating agent a question, with `SubAgents.task_control` set. Not offered when the task can’t run in the background.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `dataclass_field(default=True, kw_only=True)`

##### keep\_partial\_output

Whether a child stopped by `timeout_seconds` or its own `usage_limits` passes on its last text response. The parent gets it after the steering message, in a `<partial_output>` frame. It has not passed the child’s output validation and can be text the child rejected, so leave this off for a child whose guardrails keep content from its parent.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `dataclass_field(default=False, kw_only=True)`

##### resolved\_name

The delegate’s name: `name` if set, else the agent’s own `name`.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### ModelOption

One entry on the model menu, as a model plus how it should run.

Pass bare model references when the menu keys speak for themselves, and a `ModelOption` when an entry needs a routing hint or its own settings:

```python
from pydantic_ai.settings import ModelSettings
from pydantic_ai_harness.sub_agents import ModelOption, SubAgents

SubAgents(
    models={
        'fast': 'anthropic:claude-haiku-4-5',
        'deep': ModelOption(
            'anthropic:claude-opus-4-7',
            description='hard reasoning, multi-file changes',
            settings=ModelSettings(thinking='xhigh'),
        ),
    },
)
```

#### Attributes

##### model

The model a delegation routed to this option runs on.

**Type:** `Model` | `KnownModelName` | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### description

What this option is for, listed in the prompt next to the key so the parent can route on task difficulty rather than on model names alone.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### settings

Settings for a delegation routed to this option — thinking effort, temperature, and so on. They merge over the sub-agent’s own `model_settings`, which keeps whatever the sub-agent set and is not overridden here.

**Type:** [`ModelSettings`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

### AgentOverride

Per-agent override for a disk-loaded sub-agent, keyed by the agent’s name.

Both fields are optional. An unset `model` inherits the parent run’s model; an unset `effort` leaves the inherited model’s thinking setting unchanged.

#### Attributes

##### model

Model to run this disk agent with, in place of inheriting the parent’s.

**Type:** `Model` | `KnownModelName` | [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### effort

Thinking/reasoning level for this disk agent, passed through unchanged.

**Type:** `ThinkingLevel` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

### DelegationStartedEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

A sub-agent run is about to start for one delegation.

Emitted once the delegation has passed every check that could refuse it (an unknown sub-agent, a model key off the menu, an exhausted `max_calls` budget), immediately before the child run starts.

#### Attributes

##### model

The menu key the delegation runs on, or `None` when no option was selected: there is no menu, or the delegate allows the whole menu and the parent named no key.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### parent\_task\_id

The task whose run started this one, or `None` when the top-level run did.

**Type:** `_ParentTaskId` **Default:** `None`

##### inherits\_tools

Whether the parent’s own tools were passed to the child run (`SubAgents.inherit_tools`).

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

### DelegationFinishedEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

A delegation settled into what the parent receives.

`output` is what the delegate tool hands back to the parent: the child’s output on `ok`, otherwise the steering message it returns or the `ModelRetry` it raises. An exception that propagates out of the delegate tool (a shared usage limit, an uncontained crash, a cancellation) ends without this event for ordinary `SubAgents` users. An opt-in `DelegationTasks` owner emits terminal `cancelled` or `error` outcomes with stable task identity.

#### Attributes

##### usage

The child’s own usage when it has separate accounting (`SubAgent.usage_limits` set, or `forward_usage` off); `None` when it accrues into the parent’s usage.

**Type:** [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### parent\_task\_id

The task whose run started this one, or `None` when the top-level run did.

**Type:** `_ParentTaskId` **Default:** `None`

##### duration\_ms

Wall-clock milliseconds from just after the start event was emitted until the delegation settled.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float)

##### duration\_seconds

Deprecated: `duration_ms` in seconds.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float)

### TaskControl

Lets delegations outlive the tool call, and gives the model tools to manage them.

Every run gets a `DelegationTasks` owner unless the application bound one, so `delegate_task` takes `background` and `resume`, and the model gets `list_tasks`, `message_task`, `answer_task` and `cancel_task`. A sub-agent gets an `ask_parent` tool (`SubAgent.can_ask_questions`). Each step of a task is a `SubAgentMessageEvent` that listeners can rewrite or veto, and the reports of background tasks arrive as messages: a top-level run that would end while its own background tasks work waits for them.

#### Attributes

##### remote\_agents

Sub-agents a `SubAgentWorker` in another process serves, reached through `transport`.

**Type:** [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[`RemoteSubAgent`\] **Default:** `()`

##### transport

How messages reach the `SubAgentWorker` serving `remote_agents`. Required with `remote_agents`.

**Type:** `SubAgentTransport` | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### accept\_timeout

How many seconds a remote task waits for a worker to pick it up before it fails, or `None` to wait indefinitely.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `30.0`

##### auto\_background\_after

How many seconds `delegate_task` waits for a task before it returns a receipt and lets the task continue in the background. `None` waits until the task settles.

**Type:** [`float`](https://docs.python.org/3/builtins/functions.html#float) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### max\_running\_tasks

The most tasks a conversation may have running when it starts another, across its whole delegation tree, or `None` for no limit.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### forward\_events

Forward the events of every task’s run into the delegating run’s event stream, as `TaskProgressEvent`s.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

### RemoteSubAgent

A sub-agent that a `SubAgentWorker` in another process serves, reached through `TaskControl.transport`.

The worker runs the agent with its own model, tools and deps; this side only knows its name and what it is for.

#### Attributes

##### name

The name the model delegates to, and the worker serves it under. 1 to 64 letters, digits, `_` or `-`.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### description

What the agent is good at, for the system-prompt listing.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### resumable

Whether a finished task can be resumed, continuing the conversation the worker keeps.

The conversation lives in the worker that ran the task, so serve each remote agent name from one worker: another worker that picks up the follow-up fails the task, having no conversation to resume.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### can\_ask\_questions

Whether the agent gets an `ask_parent` tool to ask the delegating agent a question.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

### SubAgentWorker

**Bases:** `Generic[AgentDepsT]`

Serves sub-agents to delegating agents in other processes, over a transport.

Run `serve` in the process that hosts the agents. The delegating agent’s `SubAgents` lists them as `RemoteSubAgent`s with the same names, and reaches them through the same transport.

The worker keeps the conversations of tasks, up to `max_conversations`, so a delegating run can resume them.

#### Attributes

##### agents

The agents this worker serves, by the name delegating agents reach them by.

Run controls such as usage limits or timeouts belong to the agent, or to the delegating run’s `SubAgents`, which applies its own to the task.

**Type:** [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), `AbstractAgent`\[`AgentDepsT`, [`object`](https://docs.python.org/3/glossary.html#term-object)\]\]

##### transport

The transport the delegating agents send tasks over.

**Type:** `SubAgentTransport`

##### deps

The deps every task’s run gets. Deps never cross the transport.

**Type:** `AgentDepsT`

##### retries

How many times to run a task again when its run raises an error, starting over from its prompt.

Cancellation, usage limits, and `UserError` are not retried.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `0`

##### max\_conversations

How many task conversations to keep for resuming; the least recently used is forgotten first.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `1000`

#### Methods

##### serve

`@async`

```python
def serve() -> None
```

Receive and run tasks for every agent, until cancelled.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

### SubAgentTransport

**Bases:** `ABC`

Carries `SubAgentMessageEvent`s between a delegating run and the `SubAgentWorker` serving its remote agents.

A transport is a set of mailboxes. `send` delivers a message to the mailbox named by its `mailbox` property, and `receive` waits for the next message in a mailbox. Messages a mailbox receives before anyone waits on it are kept, in order.

The delegating run relays a task’s messages until the task settles, so the worker must end every task it picks up with one `TaskSettledEvent` (`TaskCompletedEvent`, `TaskFailedEvent` or `TaskCancelledEvent`) to its parent mailbox. `SubAgentWorker` does, including when it stops.

Implement this class to reach agents in other processes or machines, over a WebSocket, gRPC, a Redis list, or anything else that can move bytes: use `serialize_message` and `deserialize_message` at the boundary. `InMemoryTransport` serves a worker in the same process.

The transport is the trust boundary: anyone who can send to it can run the served agents, with their tools and dependencies. Authenticate and authorize senders in the transport.

#### Methods

##### send

`@abstractmethod`

`@async`

```python
def send(message: SubAgentMessageEvent) -> None
```

Deliver `message` to `message.mailbox`, without waiting for anyone to receive it.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### receive

`@abstractmethod`

`@async`

```python
def receive(mailbox: str) -> SubAgentMessageEvent
```

Wait for the next message delivered to `mailbox` and return it, in the order they were sent.

A stopping worker reports its running tasks as failed. Raise once a worker is gone without doing so, if the transport can tell: otherwise its delegating run waits for the task until it is cancelled.

###### Returns

`SubAgentMessageEvent`

##### release

`@async`

```python
def release(mailbox: str) -> None
```

Discard `mailbox` and any messages left in it, once no one will receive from it again.

Called when a task settles, for its two task mailboxes. The default does nothing.

A message sent after the release, such as the late reply of a worker to a task that timed out, starts the mailbox again, and nobody may receive it. A transport that serves many tasks should expire such messages, for example with a time to live.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

### InMemoryTransport

**Bases:** `SubAgentTransport`

A transport whose mailboxes are in-process queues, for a worker in the same process.

Messages are passed by reference, not serialized.

#### Methods

##### \_\_init\_\_

```python
def __init__() -> None
```

Create a transport with no mailboxes; each is created when first sent to or received from.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### send

`@async`

```python
def send(message: SubAgentMessageEvent) -> None
```

Append `message` to its mailbox’s queue and wake whoever waits on that mailbox.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### receive

`@async`

```python
def receive(mailbox: str) -> SubAgentMessageEvent
```

Take the oldest message in `mailbox`, waiting until one arrives.

###### Returns

`SubAgentMessageEvent`

##### release

`@async`

```python
def release(mailbox: str) -> None
```

Drop `mailbox` and any messages still queued in it.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

### serialize\_message

```python
def serialize_message(message: SubAgentMessageEvent) -> bytes
```

Serialize a sub-agent message to JSON, for a transport that crosses a process boundary.

#### Returns

[`bytes`](https://docs.python.org/3/builtins/stdtypes.html#bytes)

### deserialize\_message

```python
def deserialize_message(data: str | bytes) -> SubAgentMessageEvent
```

Deserialize a sub-agent message serialized by `serialize_message`.

#### Returns

`SubAgentMessageEvent`

#### Raises

- `ValueError` — If `data` is not a sub-agent message.

### DynamicAgents

**Bases:** `Generic[AgentDepsT]`

Lets the model create sub-agents during a run, with a `create_agent` tool.

A created sub-agent is delegated to like any other, by the run that created it, until that run ends.

#### Attributes

##### models

The `SubAgents.models` keys the model may run a created sub-agent on; the first is the default. Empty: created sub-agents run on the delegating run’s model.

**Type:** [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `()`

##### max\_agents

How many sub-agents one run may create.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `5`

##### factory

Builds the agent. The default is an `Agent` with the requested instructions and no tools, on the model `SubAgents` routes the delegation to.

The model wrote the spec’s name and description. Tracing records an agent’s own `name` and `description` even without content, so the default agent has neither.

**Type:** `DynamicAgentFactory`\[`AgentDepsT`\] | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

### DynamicAgentSpec

What the model asked for when it called `create_agent`.

#### Attributes

##### name

The new sub-agent’s name.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### description

What the sub-agent is for.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### instructions

The sub-agent’s instructions, written by the model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### model

The `SubAgents.models` key the sub-agent runs on, or `None` for the delegating run’s model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

### DynamicAgentFactory

Builds the agent for a sub-agent the model created with `create_agent`.

**Type:** [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) **Default:** `'Callable[[DynamicAgentSpec], AbstractAgent[AgentDepsT, Any]]'`

### SubAgentMessageEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

A message between a delegating run and one of its tasks, with `SubAgents(task_control=...)`.

Messages are dispatched immediately: listeners run before the message takes effect, so they can rewrite its fields or, for a `ParentMessageEvent`, veto it. A `SubAgentTransport` carries them to and from a `SubAgentWorker` in another process.

#### Attributes

##### recipient

Which side of the task receives this message.

**Type:** `Recipient`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### ParentMessageEvent

**Bases:** `_Vetoable`, `SubAgentMessageEvent`

A message from a delegating run to its task. A listener can veto it, and then it has no effect.

### ChildMessageEvent

**Bases:** `SubAgentMessageEvent`

A message from a task to its delegating run.

### Recipient

Which side of a task a message is for: the worker serving the agent, the running task, or its parent.

**Type:** [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) **Default:** `Literal['worker', 'task', 'parent']`

### TaskSettledEvent

**Bases:** `ChildMessageEvent`

The task’s run ended. This is the task’s report to its delegating run.

#### Attributes

##### usage

The sub-agent’s usage when a worker in another process counted it separately.

`None` for a sub-agent that ran in the delegating run’s process: its usage was counted the way `SubAgents.forward_usage` and `SubAgent.usage_limits` decide.

**Type:** [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

### BackgroundReason

Why a task moved to the background.

- `requested`: the model delegated with `background=True`.
- `auto`: the task ran longer than `TaskControl.auto_background_after`.
- `question`: the task asked a question, which the delegating model can only answer once the delegation tool returns.

**Type:** [`TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias) **Default:** `Literal['requested', 'auto', 'question']`

### TaskRequestEvent

**Bases:** `ParentMessageEvent`

A request to a worker to start a run of the sub-agent: a new task or a follow-up.

Not to be confused with `TaskStartedEvent`, the worker’s reply once the run started.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### prompt

What the sub-agent is asked to do. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### parent\_task\_id

The task whose run started this one, or `None` when the top-level run did.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### depth

The delegation level the task runs at, counting the top-level run as 1, like `SubAgents.max_depth`.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `2`

##### can\_ask\_questions

Whether the sub-agent gets an `ask_parent` tool.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### forward\_events

Whether the sub-agent’s stream events are forwarded as `TaskProgressEvent`s.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### usage\_limits

The delegating run’s usage limits, which a worker in another process applies to the sub-agent’s own usage.

**Type:** [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### trace\_context

W3C trace context of the delegation, so a worker in another process continues the delegating run’s trace.

**Type:** [`dict`](https://docs.python.org/3/reference/expressions.html#dict) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `field(default_factory=(dict[str, str]))`

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskAssignedEvent

**Bases:** `TaskRequestEvent`

The delegating run assigns a new task to a sub-agent.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### prompt

What the sub-agent is asked to do. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### parent\_task\_id

The task whose run started this one, or `None` when the top-level run did.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### depth

The delegation level the task runs at, counting the top-level run as 1, like `SubAgents.max_depth`.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `2`

##### can\_ask\_questions

Whether the sub-agent gets an `ask_parent` tool.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### forward\_events

Whether the sub-agent’s stream events are forwarded as `TaskProgressEvent`s.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### usage\_limits

The delegating run’s usage limits, which a worker in another process applies to the sub-agent’s own usage.

**Type:** [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### trace\_context

W3C trace context of the delegation, so a worker in another process continues the delegating run’s trace.

**Type:** [`dict`](https://docs.python.org/3/reference/expressions.html#dict) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `field(default_factory=(dict[str, str]))`

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskResumedEvent

**Bases:** `TaskRequestEvent`

The delegating run resumes a finished task’s conversation with a new prompt.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### prompt

What the sub-agent is asked to do. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### parent\_task\_id

The task whose run started this one, or `None` when the top-level run did.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### depth

The delegation level the task runs at, counting the top-level run as 1, like `SubAgents.max_depth`.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int) **Default:** `2`

##### can\_ask\_questions

Whether the sub-agent gets an `ask_parent` tool.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `True`

##### forward\_events

Whether the sub-agent’s stream events are forwarded as `TaskProgressEvent`s.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### usage\_limits

The delegating run’s usage limits, which a worker in another process applies to the sub-agent’s own usage.

**Type:** [`UsageLimits`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.UsageLimits) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### trace\_context

W3C trace context of the delegation, so a worker in another process continues the delegating run’s trace.

**Type:** [`dict`](https://docs.python.org/3/reference/expressions.html#dict) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)\] **Default:** `field(default_factory=(dict[str, str]))`

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskStartedEvent

**Bases:** `ChildMessageEvent`

A worker picked the task up and its run is starting.

A remote task that no worker picks up within `TaskControl.accept_timeout` fails.

### TaskBackgroundedEvent

**Bases:** [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

A task now runs in the background: the delegation tool returned a receipt, and its report arrives later.

A `requested` task still running when the delegation tool gets its receipt, but settled before this event is announced, as one replayed under durable execution can be, gets this event after its settle event.

#### Attributes

##### task\_id

The task now running in the background.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### reason

Why it moved to the background.

**Type:** `BackgroundReason`

### TaskProgressEvent

**Bases:** `ChildMessageEvent`

An event from the sub-agent’s own run, forwarded while the task runs, with `TaskControl.forward_events`.

Dispatched at its stream position, like the event it carries.

#### Attributes

##### event

The sub-agent’s stream event.

**Type:** [`AgentStreamEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.AgentStreamEvent)

### TaskQuestionAskedEvent

**Bases:** `ChildMessageEvent`

The task asks its delegating run a question and waits for a `TaskAnsweredEvent`.

A listener can answer it by setting `answer`, and then the delegating model is not asked.

#### Attributes

##### question\_id

Identifies the question, so the answer can name it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### question

The question.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### answer

An answer a listener supplies, sent to the task without involving the delegating model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

### TaskAnsweredEvent

**Bases:** `ParentMessageEvent`

The delegating run answers the question a task is waiting on.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### question\_id

The `TaskQuestionAskedEvent.question_id` this answers.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### answer

The answer. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskSteeredEvent

**Bases:** `ParentMessageEvent`

The delegating run steers a running task, which sees the message at its next model request.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### message

The steering message. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskCancelRequestedEvent

**Bases:** `ParentMessageEvent`

The delegating run asks a running task to stop before its next model request.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskForceCancelRequestedEvent

**Bases:** `ParentMessageEvent`

The delegating run stops a running task immediately, interrupting its current model request or tool calls.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskRetriedEvent

**Bases:** `ChildMessageEvent`

A remote task’s run failed and its worker is running it again, as `SubAgentWorker.retries` allows.

#### Attributes

##### attempt

The attempt about to start; the first retry is attempt 2.

**Type:** [`int`](https://docs.python.org/3/builtins/functions.html#int)

##### error

The error the previous attempt failed with.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

### TaskCompletedEvent

**Bases:** `TaskSettledEvent`

The task finished with an output.

#### Attributes

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### usage

The sub-agent’s usage when a worker in another process counted it separately.

`None` for a sub-agent that ran in the delegating run’s process: its usage was counted the way `SubAgents.forward_usage` and `SubAgent.usage_limits` decide.

**Type:** [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### output

The sub-agent’s output, as text. A listener can rewrite it before the delegating model reads it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskFailedEvent

**Bases:** `TaskSettledEvent`

The task’s run failed, or ended in a way that delivered no output.

#### Attributes

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### usage

The sub-agent’s usage when a worker in another process counted it separately.

`None` for a sub-agent that ran in the delegating run’s process: its usage was counted the way `SubAgents.forward_usage` and `SubAgent.usage_limits` decide.

**Type:** [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### error

What went wrong, as reported to the delegating model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### TaskCancelledEvent

**Bases:** `TaskSettledEvent`

The task stopped because it was cancelled. A resumable task can be followed up on.

#### Attributes

##### task\_id

The task this message belongs to.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### agent\_name

The name of the sub-agent running the task.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### mailbox

The address a transport delivers this message to.

`agent:<agent_name>` for a message that starts a run, `task:<task_id>:worker` for one the running task receives, and `task:<task_id>:parent` for one its parent receives.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### usage

The sub-agent’s usage when a worker in another process counted it separately.

`None` for a sub-agent that ran in the delegating run’s process: its usage was counted the way `SubAgents.forward_usage` and `SubAgent.usage_limits` decide.

**Type:** [`RunUsage`](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### forced

Whether the task was stopped immediately rather than before its next model request.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`

### AgentCreatedEvent

**Bases:** `_Vetoable`, [`CapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.CapabilityEvent)

The model is creating a sub-agent with `create_agent` (`SubAgents.dynamic_agents`).

Dispatched immediately, so a listener can rewrite `description` and `instructions`, or veto the creation.

#### Attributes

##### vetoed

Whether a listener vetoed it.

**Type:** [`bool`](https://docs.python.org/3/builtins/functions.html#bool) **Default:** `False`

##### veto\_reason

Why it was vetoed, reported to the model that asked for it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### agent\_name

The name the model gave the sub-agent, which it delegates to.

Also loads from `name`, the key it was serialized under before the rename.

**Type:** [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) \[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), `Field`(`validation_alias`\=(`AliasChoices`(‘agent\_name’, ‘name’)))\]

##### description

What the sub-agent is for. It reaches only a custom `DynamicAgents.factory`, as `DynamicAgentSpec.description`; the model is never shown it. A listener can rewrite it.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### instructions

The sub-agent’s instructions. A listener can rewrite them.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)

##### model

The `SubAgents.models` key the sub-agent runs on, or `None` for the delegating run’s model.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None)

##### event\_dispatch

When capability and application listeners receive the event.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘stream’, ‘immediate’\] **Default:** `'stream'`

##### kind

The namespaced event kind, injected as the default on registered subclasses.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) **Default:** `''`

##### capability\_id

The run id of the capability that emitted this event.

Stamped at emission when unset; a pre-set value is preserved, so a capability re-emitting an event on behalf of another instance can keep the original attribution.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_call\_id

The associated tool call id, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### tool\_name

The associated tool name, when emitted by a capability-contributed tool.

**Type:** [`str`](https://docs.python.org/3/builtins/stdtypes.html#str) | [`None`](https://docs.python.org/3/builtins/constants.html#None) **Default:** `None`

##### event\_kind

Event type identifier, used as a discriminator.

**Type:** [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) \[‘capability’\] **Default:** `'capability'`

#### Methods

##### veto

```python
def veto(reason: str | None = None) -> None
```

Stop it from taking effect.

###### Returns

[`None`](https://docs.python.org/3/builtins/constants.html#None)

##### \_\_get\_pydantic\_core\_schema\_\_

`@classmethod`

```python
def __get_pydantic_core_schema__(
    cls,
    source: Any,
    handler: pydantic.GetCoreSchemaHandler,
) -> pydantic_core.core_schema.CoreSchema
```

Build this family’s tagged union, instead of the plain dataclass schema pydantic would infer.

The set of event classes isn’t known when this module is imported — applications and capabilities register their own by defining them — so the union can’t be written down as a static `Annotated[... , Field(discriminator=...)]` the way the closed event types are. This override builds it from the registry each time a schema is generated, and routes a tag no class has registered to [`UnknownCapabilityEvent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.UnknownCapabilityEvent), so an event from a process that imported a module this one didn’t still round-trips instead of failing validation.

Only the family base builds the union; a subclass gets its own dataclass schema, so annotating a concrete event type validates just that event.

###### Returns

`pydantic_core.core_schema.CoreSchema`
