---
type: Concept
title: Pydantic AI subagent task control
description: What changes when Harness delegations become managed tasks — background receipts, steering, questions, cancellation and resume, typed task events, remote workers over a transport, model-created agents, and the DelegationTasks owner that persists sessions.
tags: [pydantic-ai, harness, agents, subagents, durability]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:47:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-subagents-docs
    resource: ../raw/harness/subagents/index.md
    scope: ../raw/harness/subagents/
    kind: documentation
    revision: sha256:53a83ad8be94200b67b4414a89df6e179c81b68c3a602f6fc242efd32761a974
    title: "Subagents"
---

By default a [Harness](pydantic-ai-harness.md) delegation finishes inside the `delegate_task` call that started it[^pydantic-subagents-docs] `TaskControl` is the opt-in that changes that contract: delegations become tasks the model manages — backgrounded, steered, cancelled, resumed and asked for approval of their questions — and a `DelegationTasks` owner can make them outlive the run, persist them to disk and expose them to an application[^pydantic-subagents-docs] This page covers what that mode adds; the roster, the delegate tool, budgets and failure handling of the plain capability are in [Harness subagents](pydantic-ai-subagents.md).

## The tools task control adds

With `task_control=TaskControl()` the delegate tool gains `background` and `resume`, and the model gets four more tools[^pydantic-subagents-docs]

| Tool | Purpose |
| --- | --- |
| `delegate_task(agent_name, task, background=False, resume=None)` | Start a task, or resume a finished one by task ID; `background=True` returns a receipt immediately |
| `list_tasks()` | The tasks this run started and the tasks they started, with status and IDs (the 50 most relevant) |
| `check_task(task_id)` | What one task is doing now without waiting: elapsed time, model requests, the last five tool calls, the latest text of its current run, and any pending question; a finished task shows only its outcome |
| `message_task(task_id, message)` | Steer a running task; it reads the message as sent at its next model request |
| `answer_task(task_id, answer)` | Answer the question a task is waiting on |
| `cancel_task(task_id, force=False)` | Stop a task before its next model request, or immediately with `force=True`, together with the tasks it started |

A task's instructions tell it that its delegating agent may send messages[^pydantic-subagents-docs] A finished task resumes through `message_task`, which becomes a `delegate_task(resume=...)` call that the delegate tool's hooks and approvals see and that counts as a second tool call — in the background if it ran there[^pydantic-subagents-docs]

## Reports and questions arrive as messages

A background report and a task question reach the delegating model on the user channel as framed data, `<task_output task_id="..." agent_name="...">` and `<task_question task_id="..." agent_name="...">`, and the task-control instructions tell the model both are untrusted task data[^pydantic-subagents-docs] The framing is deliberate: the output was written by a model, so it never enters system voice; a note in the application's voice says the sub-agent wrote it, not the user or the application, and text inside that looks like the frame's own tag or an application frame such as `<system>` gets a further note naming the sub-agent as its author, so it cannot end the frame early or speak as the application[^pydantic-subagents-docs]

A top-level run whose model ends while its background tasks still run waits for them, so their reports become its next request[^pydantic-subagents-docs] `DelegationReports` delivers settled reports through core's queued-message API as `TaskOutputPart`s on the user channel, with `outcome="..."` added when the task did not succeed, and questions arrive the same way as `TaskQuestionPart`s[^pydantic-subagents-docs] Reports default to `priority='when_idle'` so an active parent finishes its current work first; a host that starts an idle continuation uses `priority='asap'` with `agent.run(None, ...)`, so pending reports enter the first model request with no synthetic user prompt, and the host owns wake-up scheduling[^pydantic-subagents-docs] A report that arrives after a run has read its last queued messages is kept for the conversation's next run[^pydantic-subagents-docs]

Two consumers can be told apart: find reports and questions in history by part type, or with `is_task_report(part)`, which also recognizes the user text an earlier version delivered them as[^pydantic-subagents-docs] The Vercel AI and AG-UI message conversions leave capability parts out, so reports and questions stay in server-side history[^pydantic-subagents-docs]

## Limits and ownership

- `TaskControl(auto_background_after=...)` moves a task still running after that many seconds to the background, and `TaskControl(max_running_tasks=...)` caps how many tasks a conversation runs at once across its whole delegation tree; both are off by default[^pydantic-subagents-docs]
- `SubAgent(resumable=False)` makes one delegate one-shot; `SubAgent(can_ask_questions=False)` drops its `ask_parent` tool, and a task that cannot run in the background (a run-owned workspace that is not local) gets no `ask_parent` at all[^pydantic-subagents-docs]
- Every run gets a `DelegationTasks` owner when none is bound, and that owner cancels still-running tasks when the run ends; binding your own keeps tasks across runs, persists them and lets an application observe them[^pydantic-subagents-docs]
- Only the run that started a task can message, answer or resume it; any run above it can cancel it[^pydantic-subagents-docs]
- Only one `SubAgents` on an agent can set `task_control`, and the deprecated wrapper agents such as `TemporalAgent` give a run no durability capability, so their checks cannot catch a misuse — task control and `dynamic_agents` should not be used with them[^pydantic-subagents-docs]
- Task control and `DelegationTasks` run tasks as asyncio tasks, so they need the asyncio event loop: AnyIO's Trio backend is not supported[^pydantic-subagents-docs]

## Task events

Every step of a task is a typed capability event in the `sub_agents` namespace, published into the event stream of the run that started it, so a nested task's events reach its own parent's run[^pydantic-subagents-docs] A bound `DelegationTasks` observer receives them as `DelegationTaskEvent(event=...)` — including those of a task that settles after its delegating run ended — and receives the task run's own events in place of `TaskProgressEvent`[^pydantic-subagents-docs]

| Event | When | A listener can |
| --- | --- | --- |
| `TaskAssignedEvent`, `TaskResumedEvent` (`TaskRequestEvent` matches both) | a task is about to start or resume | rewrite `prompt`, or `veto()` |
| `TaskStartedEvent` | the task's run is starting, locally or on a worker | — |
| `TaskBackgroundedEvent` | the task moved to the background; `reason` is `requested`, `auto` or `question` | — |
| `TaskProgressEvent` | an event of the task's own run, with `TaskControl(forward_events=True)` | — |
| `TaskQuestionAskedEvent` | the task asked a question | set `answer`, so the model is not asked |
| `TaskAnsweredEvent` | an answer is about to reach the task | rewrite `answer`, or `veto()` |
| `TaskSteeredEvent` | a steering message is about to reach the task | rewrite `message`, or `veto()` |
| `TaskCancelRequestedEvent`, `TaskForceCancelRequestedEvent` | a cancellation is about to reach the task | `veto()` |
| `TaskRetriedEvent` | a worker is running a failed remote task again | — |
| `TaskCompletedEvent`, `TaskFailedEvent`, `TaskCancelledEvent` | the task settled | rewrite `output` of a completed one |

Events a listener can change are dispatched immediately so the decision takes effect; a vetoed message is not sent and the model is told why[^pydantic-subagents-docs] Unlike the two delegation events, these are not cut at `MAX_EVENT_TEXT_CHARS`, because each is the message a transport carries to the other side — a listener that persists or forwards them bounds them itself[^pydantic-subagents-docs] With a bound `DelegationTasks`, `DelegationStartedEvent` and `DelegationFinishedEvent` go to its observer only; with the run's own owner they reach the run as before[^pydantic-subagents-docs]

Earlier releases used different names, and the old ones still import from the deprecated `pydantic_ai_harness.subagents` path with a `HarnessDeprecationWarning`[^pydantic-subagents-docs]

| Old | Current |
| --- | --- |
| `SubAgentMessage`, `ParentMessage`, `ChildMessage` | the `...Event` names |
| `TaskFollowUpEvent` / `TaskMessageEvent` / `TaskAnswerEvent` | `TaskResumedEvent` / `TaskSteeredEvent` / `TaskAnsweredEvent` |
| `TaskCancelRequestEvent` / `TaskForceCancelEvent` | `TaskCancelRequestedEvent` / `TaskForceCancelRequestedEvent` |
| `TaskQuestionEvent` / `TaskRetryEvent` | `TaskQuestionAskedEvent` / `TaskRetriedEvent` |
| `AgentCreatedEvent.name`, `parent_id` | `agent_name`, `parent_task_id` |

Each event's `kind` is unchanged, the old attributes still read with the same warning, and an event serialized under an old key still loads — but constructing one takes the new keyword only, and events now serialize under the new keys, so a reader keyed on serialized fields must move and any process loading events this release writes must upgrade[^pydantic-subagents-docs]

## Remote sub-agents

A `SubAgentWorker` serves agents to delegating agents in other processes; the delegating side lists them as `RemoteSubAgent`s by name and reaches them over a `SubAgentTransport`[^pydantic-subagents-docs]

- **A transport is a set of mailboxes.** Implement `send`, `receive` and optionally `release` over a WebSocket, a Redis list or anything that moves bytes, using `serialize_message`/`deserialize_message` at the boundary; every message is one of the `SubAgentMessageEvent`s above, and `InMemoryTransport` serves a worker in the same process by passing messages by reference[^pydantic-subagents-docs]
- **The transport is the trust boundary.** Anyone who can send to it can run the served agents, with their tools and `deps`, and read what they return, so authentication, authorization and network binding belong in the transport[^pydantic-subagents-docs] The worker's output and errors reach the delegating model like a local delegate's: foreground results as tool results, background ones as framed reports[^pydantic-subagents-docs]
- **Mailbox addressing is stable**: `agent:<agent_name>` starts a run, `task:<task_id>:worker` reaches a running task, and `task:<task_id>:parent` reaches its parent, with `Recipient` naming the side (`'worker'`, `'task'`, `'parent'`)[^pydantic-subagents-docs]
- **A lost worker has two failure modes.** A worker that stops sends `TaskFailedEvent` for the tasks it was running; one that dies without doing so leaves the delegating run waiting until it is cancelled, unless `receive` raises when the worker is gone — heartbeats are not part of the protocol[^pydantic-subagents-docs]
- **The worker owns the run.** It runs the agent with its own model, tools and `deps`, which never cross the transport, takes its agents by name without per-delegate run controls (those belong to the delegating side's `SubAgents`), applies the delegating run's usage limits to the task's own usage, and continues its trace through the W3C context carried on the request[^pydantic-subagents-docs] The usage it reports on the settled event is added to the delegating run's usage unless `forward_usage=False`[^pydantic-subagents-docs]
- **Unpicked and orphaned tasks are bounded.** A remote task nobody picks up within `TaskControl.accept_timeout` (default `30` seconds) fails, and a remote task that stops without its worker's report — for example because its delegating run ended — is force-cancelled on the worker[^pydantic-subagents-docs]
- **The worker retries and remembers.** `SubAgentWorker(retries=...)` reruns a failed task from its prompt with a `TaskRetriedEvent`, and the worker keeps up to `max_conversations` task conversations (default `1000`) for resuming, least-recently-used first out[^pydantic-subagents-docs] The conversation stays in the worker that ran it, so each remote agent name must be served by one worker; a follow-up reaching another worker has no conversation and fails[^pydantic-subagents-docs]
- **A remote agent runs on its worker's model**, so `delegate_task` refuses a `model` for it, and its delegations emit no `DelegationStartedEvent` or `DelegationFinishedEvent`[^pydantic-subagents-docs]

A transport that serves many tasks should expire late messages: `release` discards a mailbox when no one will receive from it again, and a message sent afterwards restarts the mailbox with nobody to receive it, so a time to live is the transport's job[^pydantic-subagents-docs]

## Agents the model creates

`dynamic_agents` gives the model a `create_agent(name, description, instructions, model=None)` tool and lets it delegate to the agents it creates until the run ends, with or without task control[^pydantic-subagents-docs]

- A created agent is an `Agent` with the model-written instructions and no tools, running on the `models` key it was created with or on the delegating run's model when `DynamicAgents.models` is empty[^pydantic-subagents-docs]
- It has no `name` or `description` of its own, because tracing records those even without content, and it is *not* added to the cache-stable roster — the model delegates by the name it gave, and the description reaches only a custom `DynamicAgents.factory` as `DynamicAgentSpec.description`[^pydantic-subagents-docs]
- An `AgentCreatedEvent` is dispatched immediately before creation, so a listener can rewrite `instructions` (and `description`, which only a custom factory reads) or veto it[^pydantic-subagents-docs]
- `max_agents` (default `5`) caps how many agents one run creates, and only one `SubAgents` on an agent can set `dynamic_agents`[^pydantic-subagents-docs]

`factory` must be deterministic under durable execution: on Temporal and DBOS the roster lives in the workflow and each delegation other than to `self` runs in a durable unit of its own, so recovery rebuilds the created agents and replays the factory[^pydantic-subagents-docs] Engines that record each tool call in a unit of its own would lose the roster on replay and therefore raise `UserError`[^pydantic-subagents-docs]

## Managed delegation sessions

`SubAgents` delegates in the foreground only unless a caller opens and binds a `DelegationTasks` owner; the owner adds `background` and `resume` to the delegate tool's schema, gives every child a stable conversation ID, and owns every worker — an asyncio task — until shutdown[^pydantic-subagents-docs] No extra agent loop is implemented[^pydantic-subagents-docs]

The lifecycle is `async with tasks.opened():` around `with tasks.bind():`, and the owner is meant to stay open across the parent's turns[^pydantic-subagents-docs] `opened()` cancels and drains workers on exit, raising `RuntimeError` if a child has not released its resources within ten seconds — or only logging it when an error is already closing the owner, so that error is not masked[^pydantic-subagents-docs] Workspace and plugin resources must stay alive outside that scope, and detached execution is refused for run-owned non-local workspaces while foreground delegation still works[^pydantic-subagents-docs] The owner's own `max_depth=4` counts the main run and allows three child layers, and an explicitly configured non-default `SubAgents.max_depth` still takes precedence[^pydantic-subagents-docs]

| Operation | Effect |
| --- | --- |
| `restore(task)` | Add a finished `DelegationTask` made elsewhere so the parent can resume it by ID; works before `opened()`, and a same-ID task that has run since under a different `run_id` is kept rather than replaced, with `restore` returning `False` |
| `background(task_id)` | Release a foreground waiter without restarting the child |
| `await cancel(task_id)` | Stop and drain that child and its descendants |
| `await allow_resume(task_id)` | Re-enable model-requested resume after a user stop; `one_shot` names never resume |
| `steer(task_id, text)` | Send a running child a user message on its own queue with `priority='asap'`; returns `False` when the child is not running, so an application can offer to resume it |
| `history(task_id)` | Read a settled task's history from its file (in async code, via `anyio.to_thread.run_sync`) |
| `snapshot(task_id)` | A `DelegationSnapshot` of a running task read from live history: status, `elapsed_seconds`, the current run's `usage`, `recent_tool_calls`, `latest_text`, `pending_question` |
| `DelegationTasks.discover(directory)` | Load a saved task tree without opening an owner or resuming anything, returning `SavedTasks` and the same `problems` |

A resume uses the same child ID and its independent history, a new run ID, and the current direct parent; a child waits for its own descendants and consumes their reports before its final output settles, reports route to the direct parent, and an idle parent receives pending reports on its next explicitly started run[^pydantic-subagents-docs] Enqueue delivery is acknowledged only when core emits `EnqueuedMessagesEvent`, and acknowledgements are persisted[^pydantic-subagents-docs] With task control a child's `ask_parent` question is routed the same way, `questions(conversation_id=...)` lists the children waiting on an answer, and the observer is notified when one starts waiting so an application can start its idle parent's next run[^pydantic-subagents-docs]

The snapshot deliberately leaves out the child's final result, so a snapshot cannot show a result before `TaskCompletedEvent` listeners process it[^pydantic-subagents-docs] Its `usage` is `None` with no tool calls or text when the owner cannot see the run's history as it streams — before the first model request, for a remote or durable task, and after the task settles[^pydantic-subagents-docs] `check_task` gives the model the same view[^pydantic-subagents-docs]

`step_store` checkpoints through `StepPersistence` so a process-killed child's latest frontier can be recovered; loading an interrupted record never executes its tools, partial effects should be inspected before an explicit resume, and a resume closes unanswered tool calls with an `interrupted` tool return so the child sees they did not complete[^pydantic-subagents-docs]

Persistence is per task file: metadata and final or interrupted histories are saved atomically under `directory`, and once a task settles its history lives only in that file, so the in-memory record keeps empty `messages` and a directory of long-finished tasks does not fill memory[^pydantic-subagents-docs] `replace(task, messages=owner.history(task.id))` copies a settled task with its history[^pydantic-subagents-docs] A file that cannot be read or validated, whose name does not match its task ID, or whose saved ancestry loops is skipped and left on disk: `opened()` logs a warning and lists it in `problems` as a `SavedTaskProblem`, while the other tasks still load, and `discover()` writes nothing and returns a task saved as `running` unchanged[^pydantic-subagents-docs] A task still running when its process exited loads as cancelled when the owner next opens, and one that was waiting for an answer has its question named in its output so the parent can resume with the answer[^pydantic-subagents-docs]

Usage accounting changes in two ways under an owner. Managed children with `forward_usage=True` share live accounting and inherit parent ceilings; a per-child budget becomes an absolute ceiling at launch, so concurrent sibling spend can reach that ceiling earlier but cannot bypass the parent's budget[^pydantic-subagents-docs] A locally run child that inherits `count_tokens_before_request=True` from the run's limits checks each request against the token and cost ceilings before sending when its model implements `count_tokens`; if the child raises `NotImplementedError` before its first request, the delegation starts it once more without the up-front count (under a new run ID when the task is recorded), and there is no second start once the usage the child counts into has counted a request since it started — with `forward_usage=True` a sibling's request in that window also rules it out[^pydantic-subagents-docs] A per-child `usage_limits` that sets `count_tokens_before_request=True` itself is kept, so on such a model the child fails as a top-level run would, and a remote worker applies the announced limits as received, so on a model without `count_tokens` the remote task fails[^pydantic-subagents-docs]

`agents`, `aliases` and `instructions` extend the roster and guidance only inside the bound scope and do not add delegation to an agent that has no `SubAgents`; `SubAgent(read_only=True)` wraps the child's workspace in `ReadOnlyWorkspace`, which still needs trusted read-only tools because arbitrary Python tools bypass the workspace API[^pydantic-subagents-docs] Core's agent, model and tool spans provide the execution telemetry, with task IDs, parent IDs and child run IDs as correlation; this owner adds no logging exporter[^pydantic-subagents-docs]

## Under durable execution

Task control on Temporal and DBOS keeps tasks in the workflow and runs each in a durable unit of its own, so recovery replays a background task's events and reuses its result[^pydantic-subagents-docs] The mode's interactivity is what a durable engine cannot carry: a durable task cannot ask questions, take messages or be resumed, `cancel_task` stops it immediately, its report reaches the model when the run would otherwise end rather than at its next request, a replayed `list_tasks` can show a status as of a different moment, and its history is not updated while it runs so `check_task` shows only status and elapsed time[^pydantic-subagents-docs] A task backgrounded on request can also receive its `TaskBackgroundedEvent` *after* it settles, as one replayed under durable execution can[^pydantic-subagents-docs]

These raise `UserError` under durable execution[^pydantic-subagents-docs]:

- task control with `include_self`, `remote_agents` or `forward_events`
- task control with `auto_background_after` or `max_running_tasks` outside Temporal
- task control or `dynamic_agents` on another durable engine, or within a bound `DelegationTasks` owner

A delegate's own durability does nothing unless the delegate tool runs as a child workflow; that opt-in and its restrictions are compiled in [Harness subagents](pydantic-ai-subagents.md) and [durable tool placement](pydantic-ai-durable-tool-placement.md)[^pydantic-subagents-docs]

## Limits

- The source is one vendor documentation page — "Subagents", Pydantic Docs, 18,887 words as declared and 19,277 by local `wc -w`, **no publication date, author, licence or Pydantic AI/Harness version** — so this page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown[^pydantic-subagents-docs]
- Nothing was executed: no package installed, no task backgrounded, steered, cancelled or resumed, no worker served, no transport implemented, no saved file opened or discovered, no durable replay performed. Every claim is **Reported**[^pydantic-subagents-docs]
- The reference's own API section documents `TaskControl`, `RemoteSubAgent`, `SubAgentWorker`, `SubAgentTransport`, `InMemoryTransport`, `DynamicAgents` and every task event, but not the `DelegationTasks` owner's or `DelegationReports`' method signatures in that section — those appear only as prose and as the printed examples.
- Unstated by the source: what `DelegationTasks` uses as its on-disk schema or how it is versioned, what `Snapshot.usage` counts across several model requests, how a `max_running_tasks` refusal is reported to the model beyond the span, and whether `TaskProgressEvent` forwarding can be filtered per task.
- The page pins `anthropic:claude-opus-5-5` and `claude-sonnet-5-5` in its examples; no other capture here corroborates those aliases.
- External links — the capability-events overview, the Vstorm `subagents-pydantic-ai` repository, the batch and deferred-tools pages, the Temporal and DBOS child-workflow sections, the UI-adapter pages — were read as links, not followed.
- Concurrent operations were writing this checkout during this ingest; the structural check's only failures at completion were concepts another operation had created and not yet indexed, none written or edited here.

## Relationships

- **Extends** [Harness subagents](pydantic-ai-subagents.md): it is the same `SubAgents` capability with `task_control` and/or `dynamic_agents` set, and it inherits that page's roster, budgets and failure-handling rules[^pydantic-subagents-docs]
- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md) surface that publishes events in the `sub_agents` namespace, consumed per [capability events](pydantic-ai-capability-events.md) — immediate dispatch for rewritable messages, stream dispatch for notifications.
- **Depends on** [conversation state](pydantic-ai-conversation-state.md): reports and questions are parts in server-side history, found by part type, and the UI adapters that omit capability parts keep them there rather than in the client's transcript.
- **Accumulates usage into** [run controls](pydantic-ai-run-controls.md): managed children inherit parent ceilings, a per-child budget becomes an absolute ceiling at launch, and `count_tokens_before_request` reaches child requests with one documented restart exception.
- **Is constrained by** [durable execution](pydantic-ai-durable-execution.md) and [Pydantic AI on Temporal](pydantic-ai-temporal.md): durable tasks cannot ask, take messages or resume, and several task-control options raise `UserError` there.
- **Runs its children in** the [workspace](pydantic-ai-workspaces-and-sandboxes.md) the run has or the one `workspace_resolver` returned, and `SubAgent(read_only=True)` wraps that workspace per delegate.
- **Persists sessions via** `StepPersistence` checkpoints and per-task files, which is the same substrate [self-improving agent loops](self-improving-agent-loops.md) use to search past runs.
- **Ports** `subagents-pydantic-ai`, a Vstorm community package (MIT), for task control, remote agents and model-created agents[^pydantic-subagents-docs]
- **Delivers reports through** the queued-message API described in [mid-run injection](pydantic-ai-mid-run-injection.md): `DelegationReports` enqueues `TaskOutputPart`s at `'when_idle'` by default, which is why an active parent finishes its current work before they land, and a report that misses the last drain waits for the conversation's next run.

[^pydantic-subagents-docs]: Pydantic Docs, "Subagents", <https://pydantic.dev/docs/ai/harness/subagents/>; local capture `raw/harness/subagents/index.md`, content digest sha256:53a83ad8, 18,887 words as declared (19,277 by `wc -w`), no publication date, author, licence or framework version. Locators are line ranges in that capture: 271–308 for the task-control contract, the five task tools, reports and questions as framed messages, the limits and ownership rules, the per-run owner and the durable and event-loop exclusions; 310–347 for the task-event table, immediate dispatch, the no-truncation rule, the observer routing and the rename table; 349–383 for `SubAgentWorker`, the transport and mailbox protocol, the trust boundary, lost workers, `accept_timeout`, retries, conversation retention, the model refusal and the trace context; 385–398 for `dynamic_agents`, the created agent's shape, the factory and `max_agents`; 400–462 for `DelegationReports`, `DelegationTasks` lifecycle and operations, snapshots, persistence, `discover`, interrupted tasks, usage accounting and `count_tokens` behaviour; 466–495 for the child-workflow opt-in; 1204–1250 for `TaskControl`; 1248–1340 for `RemoteSubAgent` and `SubAgentWorker`; 1344–1500 for the transport, `InMemoryTransport` and message serialization; 1504–1560 for `DynamicAgents` and `DynamicAgentSpec`; 1570–1660 for the message-event families, `Recipient`, settlement and `BackgroundReason`; 1808–3126 for the individual task events and their fields. Evidence class: **Reported** — vendor documentation for its own package, with no execution behind it.
