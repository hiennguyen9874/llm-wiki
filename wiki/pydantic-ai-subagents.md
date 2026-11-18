---
type: Concept
title: Pydantic AI Harness subagents
description: The Harness SubAgents capability — one delegate_task tool over a named roster, what crosses into the child run, per-delegate budgets, a model menu, soft-versus-hard failure handling, disk-defined agents, and the depth and durability rules.
tags: [pydantic-ai, harness, agents, subagents]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:50:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-subagents-docs
    resource: ../raw/harness/subagents/index.md
    scope: ../raw/harness/subagents/
    kind: documentation
    revision: sha256:53a83ad8be94200b67b4414a89df6e179c81b68c3a602f6fc242efd32761a974
    title: "Subagents"
  - id: pydantic-multi-agent-guide
    resource: ../raw/guides/multi-agent-applications/index.md
    scope: ../raw/guides/multi-agent-applications/
    kind: documentation
    revision: sha256:2439e904aa5b1b1ecacfc0e0dcc1dbb8f5e89062198169f4f9f22304589598c1
    title: "Multi-agent Applications"
---

`SubAgents` is the [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md) that turns delegation into one tool call: it takes a roster of `SubAgent` entries and exposes a single `delegate_task(agent_name, task)` tool, so the parent model names a delegate instead of holding a tool per child[^pydantic-subagents-docs] The vendor's guide presents this as one of two routes to the same level, beside a hand-wired tool that calls the delegate's `run()` directly[^pydantic-multi-agent-guide] Each delegation is a fresh run of the chosen agent with its own message history, so the child never sees the parent conversation and the task must be self-contained; the parent receives `str(result.output)`[^pydantic-subagents-docs] The roster is listed in the system prompt and that listing is cache-stable, which is the design constraint the rest of the capability is built around: a changed roster between runs of one conversation is appended rather than rewritten, so a [prompt-cached](pydantic-ai-prompt-caching.md) prefix survives[^pydantic-subagents-docs] The page names no Pydantic AI or Harness version, so every API below is version-unknown.

## Who can be delegated to

A delegate is a `SubAgent`: a child agent plus its own run controls, exposed as `SubAgents(agents=[...])`[^pydantic-subagents-docs] Its name — how the parent model refers to it and how it is listed in the prompt — is `SubAgent.name` when set, otherwise the agent's own `name`; two delegates resolving to one name is an error, and an agent with neither is rejected[^pydantic-subagents-docs] A delegate with no description is listed by name alone[^pydantic-subagents-docs]

The roster has three sources, and they compose in one capability:

| Source | What it adds |
| --- | --- |
| `agents=[...]` | Explicit `SubAgent` entries; these win over disk-loaded definitions of the same name |
| `agent_folders=...` | Claude-style `*.md` and Codex-style `*.toml` definitions read from the run's workspace at the start of every run |
| `include_self=True` | The running agent itself, under the reserved name `self` |

`include_self` is the "delegate to an agent with everything" route: a delegation to `self` starts a fresh run of `RunContext.agent` — same agent, every capability, toolset and instruction bound to it — so a guardrail, approval gate or audit hook bound beside `SubAgents` also sees the tool calls the delegate makes, not only the `delegate_task` call[^pydantic-subagents-docs] Because the child is the same `Agent`, capabilities bound to it register again: an `AskUser` capability can prompt the user from inside a delegation, and the child returns the agent's own `output_type` rendered with `str()`[^pydantic-subagents-docs] What was passed to the parent's `run()` (capabilities, toolsets, instructions, `model_settings`) is not part of the agent and does not carry over, so passing `SubAgents(include_self=True)` to `run()` instead of binding it raises a `UserError` when the run starts[^pydantic-subagents-docs]

`self` is reserved: an explicit delegate with that name is an error, and a disk definition with it is skipped with a warning[^pydantic-subagents-docs]

Two `SubAgents` capabilities on one agent would register the same tool name and collide, so the capability carries a fixed `id='sub_agents'`: instances merge instead of colliding, and `SubAgents.combine` unions only `agents`, `models` and `include_self`[^pydantic-subagents-docs] Every other field decides how delegates *run* — what capabilities they are handed, whether they see the parent's tools, what the tool is called, where definitions are loaded from — so composition requires those to already agree and reports when they do not[^pydantic-subagents-docs] Disk definitions are read in `before_run`, after run-level capabilities are combined, so they are not part of the merge[^pydantic-subagents-docs]

## What the child run gets

The capability's defaults are chosen so a delegation is cheap to reason about, and each has an override:

- **Deps are forwarded.** The parent run's `deps` reach every sub-agent, enforced by the type signature (`AbstractAgent[AgentDepsT, Any]`), so an orchestrator and its children share one `AgentDepsT`[^pydantic-subagents-docs]
- **Usage is shared by default.** The parent's `usage` is passed down, so tokens aggregate and a parent `usage_limits` bounds the whole tree; `forward_usage=False` gives each child run its own accounting instead[^pydantic-subagents-docs]
- **The workspace is inherited** unless `workspace_resolver` selects another directory, and parent read-only restrictions still apply[^pydantic-subagents-docs]
- **The parent's tools are not passed on.** A child runs with its own tools; `include_self=True` is the way to delegate to an agent that has all of the parent's tools and capabilities[^pydantic-subagents-docs]
- **Capabilities can be shared** through `shared_capabilities`, applied to every sub-agent run — one guardrail, memory or planning capability for the whole roster without rebuilding each `Agent`[^pydantic-subagents-docs]
- **Streaming can be forwarded** with `event_stream_handler`, which reaches each child run and receives the child's own `RunContext`[^pydantic-subagents-docs]
- **`inherit_tools=True` is deprecated** and emits a `HarnessDeprecationWarning`: it adds the parent agent's own `tools=`/`toolsets=` (minus the delegate tool) but not capabilities' tools, so bind the tools a delegate needs to its `Agent`, use `include_self`, or give disk agents a `tool_resolver`[^pydantic-subagents-docs]

An unknown `agent_name` raises `ModelRetry`, so the model can correct itself, and delegations issued in parallel run as independent sub-agent runs[^pydantic-subagents-docs]

## Per-delegate budgets

Each `SubAgent` carries its own controls, so one delegate's limits do not touch the others; an unset field falls back to the `SubAgents` default[^pydantic-subagents-docs]

| Field | Effect |
| --- | --- |
| `usage_limits` | A request/token budget for one delegation, counted against the child's own accounting (isolated from the parent's and siblings'); reaching it is a soft outcome, not a run-stopping `UsageLimitExceeded`, and with `forward_usage=True` the child's usage is added to the parent's after the delegation |
| `timeout_seconds` | Wall-clock budget for one delegation; the child run is cancelled and the parent gets a steering message instead of hanging |
| `max_calls` | Maximum delegations to this delegate per parent run; later calls return a soft budget-exhausted message without running the child. Counts are scoped to one `Agent.run` (a `run_id`), so each parent run and each level of a nested tree budgets independently |
| `models` | Which menu keys this delegate may run on, the first being its default |
| `on_failure` | Steering message replacing the built-in default for any soft degradation; while `on_model_error` is unset, setting it also makes child failures soft |
| `on_model_error` | `'retry'` raises a parent `ModelRetry`; `'return'` returns the error and the steering message as a normal tool result; unset keeps the earlier coupling (`'return'` when `on_failure` is set, `'retry'` otherwise) |
| `contain_errors` | Contain an unexpected crash as a bounded `ModelRetry` instead of aborting the parent run; unset inherits the `SubAgents` default (off) |
| `keep_partial_output` | Pass the child's last text response on when its timeout or its own budget stops it (off by default) |
| `read_only` | Run the child in a `ReadOnlyWorkspace`; pair it with trusted read-only tools, since arbitrary Python tools bypass the workspace API |
| `resumable`, `can_ask_questions` | Whether a finished task can be resumed, and whether the child gets `ask_parent` under [task control](pydantic-ai-subagent-tasks.md) |

A timeout or a reached `usage_limits` is a soft outcome, so the child's stream handler stops receiving events without a terminal event[^pydantic-subagents-docs] `keep_partial_output=True` appends the child's last text after the steering message in a `<partial_output>` frame, and the same text appears in `DelegationFinishedEvent.output`[^pydantic-subagents-docs] It is deliberately framed as unvalidated: the text has not passed the child's output validation and can be content its output validator or `OutputGuardrail` rejected, so it should stay off for a child whose guardrails keep content from its parent[^pydantic-subagents-docs] Text from a response the child answered with a retry is skipped, as is a final response the run stopped before acting on[^pydantic-subagents-docs]

## Per-delegation model selection

The orchestrator knows how hard a task is when it writes the brief, so routing belongs there rather than in each child agent[^pydantic-subagents-docs] A `models` menu adds a `model` argument to the delegate tool:

- **Off by default.** With no menu the argument is not in the tool schema at all and every delegation behaves as before[^pydantic-subagents-docs]
- **The keys are the interface.** They are listed in the system prompt with each entry's model and description and offered as an enum in the tool schema, so the model picks from the menu instead of inventing a model name; name them for the job (`'fast'`, `'deep'`) rather than for the vendor[^pydantic-subagents-docs]
- **An entry is a model string, a `Model`, or a `ModelOption(model, description=..., settings=...)`.** Option settings merge over the sub-agent's own `model_settings`, keeping whatever the option does not set, so one key can mean "same model, more thinking"[^pydantic-subagents-docs]
- **Resolution order** is the key the parent passed, else the delegate's first allowed key, else the delegate's own model, else the parent run's model[^pydantic-subagents-docs]
- **A delegate can be restricted** with `SubAgent(models=['fast'])`: the first key is its default and the others are refused with a `ModelRetry`, rendered in the prompt listing as `(models: fast)`; restricting to a key the menu does not define is a `ValueError` at construction[^pydantic-subagents-docs]
- **A rejected key costs nothing**: an unknown or unavailable key returns a `ModelRetry` listing the valid options before the delegate's `max_calls` budget is charged[^pydantic-subagents-docs]

## Per-delegation working directory

`workspace_resolver` opts into `delegate_task(working_directory=...)`: an async callback receives the parent `RunContext` and a `DelegationWorkspaceRequest` (delegate name and requested directory) and returns a `Workspace`, so the host validates paths and decides which delegates may move[^pydantic-subagents-docs] The child's relative paths and repository instructions then use that directory, while parent and `SubAgent(read_only=True)` restrictions still apply[^pydantic-subagents-docs]

Three rules keep that safe and resumable: the caller owns the returned workspace and must keep its resources alive until background children finish; a managed task records the resolved directory in `DelegationTask.working_directory`, resume re-resolves that saved directory, and changing it is rejected, so the resolver must accept its own resolved spelling; and older tasks without the field inherit the parent workspace, while remote and durable delegations reject directory overrides[^pydantic-subagents-docs] This option does not change where disk definitions are discovered — `SubAgents.workspace` does that separately[^pydantic-subagents-docs]

## Failure handling

The capability separates outcomes the parent model should read from failures that should stop the run[^pydantic-subagents-docs]

**Soft outcomes** return a steering message as a normal tool result, so the parent's model reads it and decides what to do next rather than immediately re-delegating the way a `ModelRetry` invites[^pydantic-subagents-docs] Timeout, a reached per-delegate budget and an exhausted `max_calls` are always soft, and `on_failure` replaces only the message text[^pydantic-subagents-docs] Two more cases join them: a child run ending with `DeferredToolRequests` (its output type includes the marker and a tool needed approval) returns a steering message naming the sub-agent and why it stopped, because the parent can neither approve the child's calls nor resume it; a child ending with `PendingModelResponse` returns one too, and the waiting request is cancelled as best effort, a batch only once nothing else in it still waits[^pydantic-subagents-docs] A child that handles its own deferred calls, for example with `HandleDeferredToolCalls`, never ends this way[^pydantic-subagents-docs]

**Soft model errors** — `ModelRetry`, `UnexpectedModelBehavior` after the child exhausts its own retries — become a parent `ModelRetry` by default, so the parent's model sees `Sub-agent '<name>' failed: ...` and can re-delegate[^pydantic-subagents-docs] The delegate tool defaults to `tool_retries=2` rather than core's per-tool default of `1`, so a repeated flaky sub-agent does not abort the parent on its first repeat; the counter resets after any successful delegation, so it bounds consecutive failures rather than total ones[^pydantic-subagents-docs] `on_model_error='return'` makes failures soft instead, and with `on_model_error` unset the presence of `on_failure` switches to `'return'` with the custom message alone, error text omitted[^pydantic-subagents-docs]

**Hard errors propagate.** A `UsageLimitExceeded` from a child that has *no* per-delegate `usage_limits` means the shared tree is out of budget and stops the run, while a child reaching its *own* budget is soft[^pydantic-subagents-docs] Any other exception — a provider `ModelAPIError`/`FallbackExceptionGroup`, a `ValueError` from a bad tool argument — aborts the parent unless `contain_errors=True`, per delegate or as the `SubAgents` default[^pydantic-subagents-docs]

Containment stays loud by design: the exception rides the retry message (`Sub-agent '<name>' crashed: ...`), it is logged through the standard `logging` module, and `tool_retries` still bounds consecutive crashes into an abort, so a genuine bug is never masked as success[^pydantic-subagents-docs] Containment is orthogonal to `on_failure` (a contained crash always raises the loud retry) and is bypassed by cancellation, a shared usage limit, the pydantic-ai control-flow signals (`CallDeferred`, `ApprovalRequired`, the `Skip*` signals) and `UserError`[^pydantic-subagents-docs] A child's own first-party cancellation (`RunContext.cancel()` inside it, raising `RunCancelled`) leaves the delegate tool uncontained and surfaces as a failed `delegate_task` return the parent model can react to, not a crash retry that invites re-delegation[^pydantic-subagents-docs]

## Delegation events and spans

Plain delegation emits two typed capability events in the `sub_agents` namespace, both notified at stream dispatch[^pydantic-subagents-docs]

| Event | When | Payload |
| --- | --- | --- |
| `DelegationStartedEvent` | the delegation passed every refusing check, immediately before the child run starts | `agent_name`, `task`, `truncated`, `model` (menu key or `None`), `inherits_tools`, `parent_task_id` |
| `DelegationFinishedEvent` | the delegation settled into what the parent receives | `agent_name`, `outcome`, `output`, `truncated`, `usage`, `duration_ms`, `parent_task_id` |

One delegation is one `delegate_task` call, so a start and its end share the `tool_call_id` core stamps on every event — which is how a subscriber pairs them when the model delegates in parallel[^pydantic-subagents-docs] `outcome` is `ok`, `timeout`, `budget`, `failed` (a soft model error, or a run that ended with `DeferredToolRequests`/`PendingModelResponse`) or `contained`; `output` is exactly what the tool hands back in that case[^pydantic-subagents-docs] `usage` is the child's own `RunUsage` only when it has separate accounting (`usage_limits` set or `forward_usage=False`), and `None` when its share accrues inseparably into the parent's[^pydantic-subagents-docs]

Three asymmetries matter for a host. The event is emitted from inside the tool *before* any `ToolGuardrail` result guard screens the text for the model, so a host that needs the screened version reads the `ToolReturnPart` in core's `FunctionToolResultEvent`[^pydantic-subagents-docs] `task` and `output` are cut at `MAX_EVENT_TEXT_CHARS` (4096) with a `truncated` flag, while task-control events and `AgentCreatedEvent` are not cut because each is itself the message a transport carries[^pydantic-subagents-docs] A delegation refused before the child runs (unknown sub-agent, model key off the menu, exhausted `max_calls`) emits nothing and only answers in the tool result, and an exception that propagates out of the tool ends without an end event; a `SubAgentToolset` registered directly in `Agent(toolsets=[...])` has no owning capability and emits nothing[^pydantic-subagents-docs] As with any capability event, a listener that raises aborts the parent run[^pydantic-subagents-docs]

Plain delegation opens no span of its own: the child is a core agent run whose spans nest under the parent's tool-call span[^pydantic-subagents-docs] Task control does add zero-duration decision spans on the delegating run's tracer, with `sub_agents.`-prefixed attributes, for things core's spans would only show as an exception or a tool result — `sub_agents vetoed`, `sub_agents task backgrounded`, `sub_agents question answered`, `sub_agents task refused`, `sub_agents task not accepted`, `sub_agents remote task stopped`, plus `sub_agents wait for tasks` while a top-level run waits on its background tasks[^pydantic-subagents-docs] Veto reasons, questions, answers and the name a vetoed `create_agent` asked for are attached only when the run's instrumentation includes content[^pydantic-subagents-docs]

## Agents defined on disk

`agent_folders` turns a repository's agent definitions into delegates without writing `Agent` code: every `*.md` and `*.toml` file under the configured folders is loaded alongside `agents`, in sorted filename order, at the start of every run, through the run's [workspace](pydantic-ai-workspaces-and-sandboxes.md)[^pydantic-subagents-docs] Nothing is read from the home directory, so a sandbox's agent files are found; `workspace=LocalWorkspaceBackend('/app')` reads definitions that ship with the application instead[^pydantic-subagents-docs]

- A folder-name string (`'agents'` is conventional) loads from `.agents/<name>/`, `.claude/<name>/` and `.codex/<name>/` under the workspace's working directory, in that order, so a workspace that uses `.agents/` for something else still loads agents from the others; a run without a workspace skips them[^pydantic-subagents-docs]
- A sequence of workspace paths loads from exactly those folders, in order; a run without a workspace fails at its start when given a sequence[^pydantic-subagents-docs]
- `None`, the default, disables disk loading[^pydantic-subagents-docs]
- Convention discovery warns once when it skips a `.agents/` or `.claude/` folder in the current or home directory that the workspace does not reach, naming the folder and the `workspace=` that reads it[^pydantic-subagents-docs]

**Claude-style Markdown** has optional frontmatter: `name` (falling back to the filename stem), `description` (drives the prompt listing), `tools`/`allowed-tools` (comma-separated string or YAML block list), and the body becomes the instructions[^pydantic-subagents-docs] `model` and `color` are ignored — the model is inherited — and frontmatter is read by a small dependency-free parser limited to those keys, because `pyyaml` is not a Harness dependency[^pydantic-subagents-docs]

**Codex-style TOML** requires nonempty `name`, `description` and `developer_instructions`; `tools`/`allowed-tools` is optional but not both[^pydantic-subagents-docs] `model`, `effort`, `model_reasoning_effort` and `color` are ignored with a warning in favour of `agent_overrides`, any other key (including sandbox or permission settings) skips that file with a warning rather than silently granting broader tools, and the older `[agents.<name>] config_file` layout is unsupported[^pydantic-subagents-docs]

Nothing in a definition file is executed, and a malformed or invalid file is skipped with a warning without blocking the others[^pydantic-subagents-docs] Without a `tool_resolver`, a disk agent gets no tools and its `tools` frontmatter is ignored; the resolver receives each tool name — so it can honor entries like `Bash(git:*)` — and returns the toolsets providing it, or `None`, which skips that name with a warning[^pydantic-subagents-docs] `agent_overrides` is keyed by agent name and sets `model` and/or `effort`; an unset `effort` adds no thinking setting, while an explicit value including `False` or `'minimal'` passes through unchanged as `ModelSettings.thinking`[^pydantic-subagents-docs]

Precedence is: explicitly passed `agents` first, then convention discovery's `.agents/`, `.claude/`, `.codex/`, and for an explicit path sequence earlier folders before later ones; the loser is skipped with a warning, but a duplicate name *within* the explicit `agents` list is still an error[^pydantic-subagents-docs]

`MINIMUM_EFFORT_FLOOR` and `clamp_effort(level, floor=...)` remain importable from the deprecated `pydantic_ai_harness.subagents` path with a `HarnessDeprecationWarning`, but `SubAgents` no longer uses them: an explicit `AgentOverride(effort=...)` or an application-level floor outside the capability is the current route[^pydantic-subagents-docs]

## Depth, durability and serialization

Delegation forms a tree, and each `SubAgents` stops offering delegation at its own `max_depth` — `3` by default, counting the top-level run, so the top-level run delegates and its delegates delegate once more[^pydantic-subagents-docs] The level is tracked per task tree across every `SubAgents` capability, a run at the limit gets neither the delegate tool nor the listing, and a delegate with a higher limit can go deeper than its parent's[^pydantic-subagents-docs] That bound is what contains `include_self`, whose delegate carries the delegate tool again, and a roster that reaches the same agent by another path[^pydantic-subagents-docs]

Under [durable execution](pydantic-ai-durable-execution.md) the defaults are deliberately modest: on Temporal a delegation to anything but `self` runs in an activity, and on DBOS it runs inline in the parent workflow, so a delegate's own durability buys nothing[^pydantic-subagents-docs] Running the delegate tool as a child workflow is opt-in through `SetToolMetadata(tools=['delegate_task'], temporal={'child_workflow': {}})` (or `dbos=...`), which records the delegate's model requests and tool calls in the child's history[^pydantic-subagents-docs] Four consequences follow: every delegate must be durable on the parent's engine because the tool body becomes workflow code; on Temporal each delegate must also be registered with the worker; `include_self`, `inherit_tools`, `models`, `shared_capabilities`, `event_stream_handler`, `dynamic_agents`, `task_control` and a delegate's `max_calls` all rely on parent-run state the child workflow does not receive, so a delegation using any of them raises `UserError`; and the child's usage is not reliably counted in the parent's, its usage limits do not bound it, and `max_depth` restarts from each child workflow[^pydantic-subagents-docs]

Two Temporal-specific rules sit outside child workflows: `agent_folders` is unsupported because it adds a toolset at run time, which Temporal refuses, and when `self` is the only delegate it runs in the workflow, so a `Model` instance from `models` must be registered with `TemporalDurability(models=...)`[^pydantic-subagents-docs] Under any durability capability `SubAgents` needs an `id` — it has the default `'sub_agents'` — and `id=None` raises `UserError`[^pydantic-subagents-docs]

`SubAgents` is not serializable through the agent spec because it holds live `Agent` instances, so `get_serialization_name()` returns `None`[^pydantic-subagents-docs]

## Configuration

The capability's own surface, with the per-delegate defaults shown by the second block, is[^pydantic-subagents-docs]:

```python
SubAgents(
    agents=(), models={}, agent_folders=None, agent_overrides={}, tool_resolver=None,
    forward_usage=True, inherit_tools=False, shared_capabilities=(), event_stream_handler=None,
    tool_name='delegate_task', tool_retries=2, contain_errors=False,
    workspace=None, workspace_resolver=None, include_self=False, max_depth=3,
    task_control=None, dynamic_agents=None,
)
```

```python
SubAgent(
    agent, name=None, description=None, models=None, usage_limits=None, timeout_seconds=None,
    max_calls=None, on_failure=None, contain_errors=None, on_model_error=None,
    resumable=True, can_ask_questions=True, keep_partial_output=False, read_only=False,
)
```

`task_control` and `dynamic_agents` are compiled in [subagent task control](pydantic-ai-subagent-tasks.md), together with the background, remote-worker and managed-session behaviour they unlock[^pydantic-subagents-docs] The behavioural contract for a capability of this kind — hooks, per-run copies, `get_instructions`/`get_toolset` — is in [the capability primitive](pydantic-ai-capability-primitive.md): `for_run` returns a per-run copy when folders are read, `before_run` rebuilds the roster from the workspace, and `after_output_process` keeps a top-level run alive while its background tasks work[^pydantic-subagents-docs]

## Limits

- The source is one vendor documentation page — "Subagents", Pydantic Docs, 18,887 words as declared and 19,277 by local `wc -w`, **no publication date, author, licence or Pydantic AI/Harness version**. Under the `pydantic-ai` domain rule the page is `draft` and every API name is version-unknown[^pydantic-subagents-docs]
- Nothing was executed: no package installed, no `SubAgents` constructed, no delegation run, cancelled, timed out or contained, no model menu resolved, no disk definition parsed, no cache hit measured. Every behavioural claim is **Reported**[^pydantic-subagents-docs]
- The page states the intended behaviour of the built-in steering messages, the prompt listing and the frontmatter parser but not their exact text or grammar; the exception messages are illustrative snippets.
- The examples pin `anthropic:claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5` and `claude-sonnet-4-6`; the API reference samples elsewhere pin `claude-opus-4-7`, `claude-sonnet-4-6` and `claude-haiku-4-5`. No other capture here corroborates any of them, and the page does not say which release the older aliases target.
- Unstated by the source: how the roster listing renders a delegate with no description beyond "by name alone", whether `tool_retries` counts per delegate or across a parallel batch, how a task tree's depth is recorded, whether `SubAgents` emits its own spans beyond the task-control ones, and what a `shared_capabilities` capability sees of the child's run.
- External links — the Harness version policy, `Coder`, `Researcher`, dynamic workflow, `SubAgentMessageEvent` API pages, the capability and prompt-caching pages, the multi-agent guide — were read as links, not followed. The sibling captures under `raw/harness/` were left untouched as separate sources.
- Concurrent operations were writing this checkout during this ingest; the structural check's only failures at completion were concepts another operation had created and not yet indexed, none written or edited here.

## Relationships

- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md), attached through `capabilities=[SubAgents(...)]` and shipping under the Harness's 0.x version policy[^pydantic-subagents-docs]
- **Extends into** [subagent task control](pydantic-ai-subagent-tasks.md): `task_control` turns a delegation into a task the model can background, steer, cancel, resume and ask questions of, and `dynamic_agents` lets the model write new delegates mid-run.
- **Protects** [prompt caching](pydantic-ai-prompt-caching.md): the roster listing and model menu live in the cached prefix and a change is appended, which is why created agents are deliberately kept out of the listing.
- **Shares deps and usage accounting with** [Pydantic AI dependencies](pydantic-ai-dependencies.md) and [run controls](pydantic-ai-run-controls.md): `deps` are forwarded by type, usage is shared unless `forward_usage=False`, and a per-delegate budget is an isolated, soft ceiling.
- **Delegates inside** the [workspace](pydantic-ai-workspaces-and-sandboxes.md) the run has, or one `workspace_resolver` returns, with parent read-only restrictions preserved.
- **Becomes durable through** [durable execution](pydantic-ai-durable-execution.md) and [durable tool placement](pydantic-ai-durable-tool-placement.md): a delegate is an activity or inline call by default, a child workflow only when `SetToolMetadata` opts in.
- **Is what** the [Harness](pydantic-ai-harness.md)'s `Coder` uses by default, through `include_self=True`, so the coding agent's delegation is this capability configured rather than a separate mechanism[^pydantic-subagents-docs]
- **Ports** `subagents-pydantic-ai`, a Vstorm community package (MIT), for task control, remote agents and model-created agents — the community-to-core path also recorded in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md)[^pydantic-subagents-docs]
- **Publishes events consumed per** [capability events](pydantic-ai-capability-events.md): the `sub_agents` namespace, immediate dispatch for rewritable messages, and `tool_call_id` pairing.
- **Composes with** [Pydantic AI Harness planning](pydantic-ai-harness-planning.md) in a planning orchestrator: the plan stays in tool results while delegates do the work, and both rely on append-only prompt changes.
- **Has the hand-wired alternative** described in [multi-agent patterns](pydantic-ai-multi-agent-patterns.md): a tool that calls `delegate.run(..., usage=ctx.usage, deps=ctx.deps)` itself, which is this capability's contract minus the roster, budgets, failure handling and prompt listing[^pydantic-multi-agent-guide]
- **Sits beside** [dynamic workflows](pydantic-ai-dynamic-workflow.md) as the other delegation capability: one `delegate_task` per turn here, one script of fan-out, chaining, voting and retry there, over sub-agents that need not change to move between them; the budgets differ in scope (`max_calls` per delegate against `max_agent_calls` across a catalog) for the same reason.

[^pydantic-subagents-docs]: Pydantic Docs, "Subagents", <https://pydantic.dev/docs/ai/harness/subagents/>; local capture `raw/harness/subagents/index.md`, content digest sha256:53a83ad8, 18,887 words as declared (19,277 by `wc -w`), no publication date, author, licence or framework version. Locators are line ranges in that capture: 15–33 for the single-tool contract, the fresh run and its own history, the cache-stable roster and the appended change; 34–58 for the context-bloat problem and the roster/name rules; 60–69 for the tool table, `ModelRetry` on an unknown name, `str(result.output)` and the parallel-delegation note; 71–80 for forwarded deps, workspace inheritance, shared usage, `shared_capabilities`, `event_stream_handler` and the deprecated `inherit_tools`; 82–99 for `include_self`, the `self` run, what does not carry over from `run()`, the depth cap, inherited capabilities and the Temporal notes; 101–135 for the per-delegate control table and its semantics; 137–173 for the model menu, `ModelOption`, resolution order and delegate restrictions; 175–202 for `workspace_resolver`, `DelegationWorkspaceRequest` and the resume rules; 204–216 for soft outcomes, partial output, deferred and pending endings, `on_model_error`, `tool_retries` and containment; 218–269 for the two delegation events, `MAX_EVENT_TEXT_CHARS`, the outcome set, the un-emitted cases and the span table; 497–599 for workspace-based discovery, the Claude Markdown and Codex TOML formats, `agent_overrides`, `tool_resolver`, precedence and the deprecated effort helpers; 601–662 for the configuration blocks and the serialization limit; 664–669 for the nesting, parallel and `max_depth` notes; 671–976 for the `SubAgents` attribute and method reference including the fixed `id`, `combine` and `get_serialization_name`; 986–1080 for the `SubAgent` fields; 1102–1140 for `ModelOption` and `AgentOverride`; 1142–1204 for the delegation events; 464–495 for the child-workflow opt-in and its restrictions. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.

[^pydantic-multi-agent-guide]: Pydantic Docs, "Multi-agent Applications", <https://pydantic.dev/docs/ai/guides/multi-agent-applications/>; local capture `raw/guides/multi-agent-applications/index.md`, content digest sha256:2439e904, 2,082 words as declared (2,144 by `wc -w`), no publication date, author, licence or framework version. Lines 11–16 for delegation as level 2 of five, available "either wired up by hand or with the Harness's `SubAgents` capability"; §"Agent delegation" (21–103) for the hand-wired tool that calls the delegate's run and returns its output, `usage=ctx.usage` and the dependency rules. Evidence class: **Reported** — vendor guide; nothing was delegated here.
