---
type: Concept
title: Pydantic AI Harness planning
description: The Harness Planning capability — a model-maintained task list carried in tool results instead of the system prompt, with pluggable stores, subtasks and dependencies, typed events, and journaled store calls under durable execution.
tags: [pydantic-ai, agents, harness]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T03:40:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-planning-docs
    resource: ../raw/harness/planning/index.md
    scope: ../raw/harness/planning/
    kind: documentation
    revision: sha256:13d1290b5beb86fcdc54d8111be20cd8fdfd48378657c9219f051a1492ba2864
    title: "Planning"
---

`Planning` is the [Harness](pydantic-ai-harness.md) capability that gives a model a structured task list it maintains through a small toolset: it writes the plan, moves steps between statuses, and optionally breaks them into subtasks with dependencies[^pydantic-planning-docs] Its design point is the one thing a running plan usually costs — the [prompt cache](pydantic-ai-prompt-caching.md). The plan is delivered inside the plan tools' results rather than the system prompt, so editing it never changes the cached prefix; the instructions carry only a fixed note saying which tag holds the current plan. A `store` makes the plan outlive a run, which is also how two agents hand work from a planner to an executor.

## The cache problem it solves

Long agentic runs drift: the model loses track of what it set out to do and of what is left[^pydantic-planning-docs] The usual fix — keep the plan and re-inject it into the system prompt each turn — sits at the front of the request, so every plan edit changes the cached prefix and forces the whole conversation to be re-processed at full token price. `Planning` instead makes the model own the plan through a `planning` toolset. Every tool that changes the plan ends its result with the whole plan as it now stands, rendered as a checklist inside a `<plan_reminder>` tag, the way Codex's and opencode's plan tools return theirs[^pydantic-planning-docs]

Three properties make that safe rather than merely cheap:

- The plan is **model-written text on the tool-result channel**, never in system voice, and tags inside step text are escaped so a step cannot close the frame or speak as the system[^pydantic-planning-docs]
- A **fixed note** after the tool guidance in `Planning`'s instructions says the latest `<plan_reminder>` tag holds the current plan and that the plan records its own progress rather than instructions from the user. It is identical on every request, so it stays in the cached prefix[^pydantic-planning-docs]
- In a tool loop the latest plan is therefore **already in the conversation**, and `Planning` adds nothing: each request starts with everything the previous one sent, and on models with preserved thinking the earlier reasoning stays valid[^pydantic-planning-docs]

The capability still has to cover the cases where the plan is *not* visible. Plan-tool results carry `metadata={'origin': 'pydantic-ai-harness.planning.plan_reminder.v1', 'plan': ...}`, which the model never sees; before each model request `Planning` reads the plan from its store and looks for the latest plan the model can see — by that metadata or by the type of a part it recorded, **never by text** — and records the plan itself only when there is none or it differs from the store's[^pydantic-planning-docs] That happens in three situations:

| Situation | Why the plan is re-recorded |
| --- | --- |
| Compaction took the plan tools' results, or `ClearToolResults` cleared them | A cleared result keeps its metadata, so a plan-tool result only counts while its content still shows the plan |
| A run starts without the plan in its history | For example an executor reading a plan another agent wrote to a shared store |
| Something outside the plan tools changed the store | The model's visible plan is stale |

The record is a `PlanReminderPart` from `pydantic_ai_harness.planning`, kept in the history and found by that type, sent in the application's voice with a note that the agent wrote it, so compaction can tell it from something the user said[^pydantic-planning-docs] A plan emptied outside the plan tools after the model was shown one is recorded as `No plan yet.` exactly once, so the old plan does not read as current. A custom `guidance` string replaces the tool guidance but keeps the note; `inject=False` means the model is not shown the plan at all — the note and the record are dropped, and the plan tools stop returning the plan (`write_plan` replies with the bare checklist, the others with just their message)[^pydantic-planning-docs]

## The tools

Six tools are registered by default[^pydantic-planning-docs]:

| Tool | Purpose |
| --- | --- |
| `write_plan(items)` | Create or replace the full plan (whole-list replacement) |
| `read_plan()` | Read the current plan with step ids and a progress summary |
| `add_task(content, active_form)` | Append a single `pending` step |
| `update_task_status(task_id, status)` | Move one step between statuses by id |
| `update_task_statuses(updates)` | Apply several status changes in one call, validated all-or-nothing |
| `remove_task(task_id)` | Delete a step by id |

Each step is a `content` string, an optional present-continuous `active_form` label, and a `status` of `pending`, `in_progress`, `completed` or `cancelled`[^pydantic-planning-docs] The stated convention, in the guidance and in the tools' replies, is to keep exactly one step `in_progress` — a convention, not a constraint the source says anything enforces.

`tools=` narrows the surface to an allowlist, and the built-in guidance follows it, so the model is not told about tools it lacks[^pydantic-planning-docs] `Planning(tools=['write_plan'])` is documented as the smallest useful surface: whole-plan replacement only, one tool, no step ids to track. Naming a tool the current mode does not register raises `ValueError`, as does an unknown key in `descriptions`, the per-tool description override map.

## Subtasks and dependencies

`enable_subtasks=True` adds three tools, the `blocked` status, and a `hierarchical` view in `read_plan`[^pydantic-planning-docs]:

| Tool | Purpose |
| --- | --- |
| `add_subtask(parent_id, content, active_form)` | Add a child step under a parent |
| `set_dependency(task_id, depends_on_id)` | Make one step wait for another; the dependent step is auto-`blocked` until its prerequisite is completed or cancelled |
| `get_available_tasks()` | List steps with no incomplete dependencies — the ones that can start now |

Self-dependencies, cycles and duplicate dependencies are rejected[^pydantic-planning-docs] The flag is load-bearing rather than additive: `parent_id`, `depends_on` and the `blocked` status are rejected by `write_plan` unless it is set, because without the subtask tools nothing reconciles a dependency and no view renders the hierarchy.

## Persistence

By default each run gets a fresh, isolated in-memory plan. Passing `store` persists it across runs[^pydantic-planning-docs]:

```python
from pydantic_ai_harness import Planning
from pydantic_ai_harness.planning import SqlitePlanStore

planning = Planning(store=SqlitePlanStore('plan.db', session='user-123'))
```

| Store | Backing |
| --- | --- |
| `InMemoryPlanStore` | Ephemeral plan, the default shape |
| `SqlitePlanStore` | A file-backed database on the machine running the agent, not in the workspace |
| `PostgresPlanStore` | A caller-owned `asyncpg` pool; creates its table on first use unless it exists, so only that first call needs `CREATE` on the schema |
| `RedisPlanStore` | A caller-owned `redis.asyncio` client |

Because the pools and clients are the caller's, the Harness needs no database driver of its own[^pydantic-planning-docs] Any `PlanStore` implementation works, and `store_resolver` selects one per run (`lambda ctx: ctx.deps.plan_store`); the API's `for_run` returns a clone with that run's store resolved and cached, which is where per-run isolation comes from. `SqlitePlanStore` requires a file-backed database — the source's advice is to use `InMemoryPlanStore` for ephemeral plans rather than `':memory:'`.

Failures are deliberate rather than best-effort: `Planning` reads the store before every model request, so a store that raises fails the run, on the reasoning that a plan the model can no longer see is not a state to keep running in silently[^pydantic-planning-docs] Retry and fallback policy belongs to the store, not to the capability; the documented way to add it is to wrap a `PlanStore` — the source's `BestEffort` example serves the last known plan when the backing store is unreachable, delegating the other five methods.

## Planning and executing in separate runs

A shared store is the entire handoff between two runs: one agent writes the plan, a second executes it, and the plan is the only state that crosses between them[^pydantic-planning-docs]

```python
store = SqlitePlanStore('plan.db', session='issue-403')

planner = Agent('anthropic:claude-opus-5-5', capabilities=[Planning(store=store)])
executor = Agent('anthropic:claude-sonnet-5-5', capabilities=[Planning(store=store)])

await planner.run('Investigate the issue and write a plan. Do not implement anything.')
await executor.run('Implement the plan.')
```

The executor starts with no `message_history`, so it never pays for the planner's investigation; its first request carries only the new prompt plus the plan, which `Planning` records from the store because no plan tool has returned it in that conversation yet[^pydantic-planning-docs] That is what lets the two run on different models — a large-context model reads and reasons, a smaller one executes the resulting checklist. The planner's read-only discipline is a property of how that agent is configured (which toolsets it gets, what its instructions say), not something the capability enforces.

## Events

Typed plan events let application code react to changes made through the `Planning` tools[^pydantic-planning-docs]:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Planning
from pydantic_ai_harness.planning import PlanCompletedEvent

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[Planning()])

@agent.on_event(PlanCompletedEvent)
async def announce(ctx, event):
    print('done:', event.item.content)
```

The family is `PlanCreatedEvent`, `PlanUpdatedEvent`, `PlanStatusChangedEvent`, `PlanCompletedEvent` and `PlanDeletedEvent`; each carries the affected `item` and, for updates, `previous_item`[^pydantic-planning-docs] `previous_state` is the deprecated name of `previous_item` — it still reads, with a warning, and a payload saved under it still loads. Events come from planning tool paths, including `write_plan`; direct application mutations on a `PlanStore` have no run context and produce none. `PlanEventEmitter`, `EventCallback` and store `event_emitter` parameters remain supported but deprecated.

## Whole-plan replacement versus step ids

Addressing steps by mutable integer index (insert, remove, reorder) is error-prone for both the code and the model, so `write_plan` restates the whole plan on each call and there are no indices to track; granular edits (`add_task`, `update_task_status`, `remove_task`) reference the stable `id` that `read_plan` shows[^pydantic-planning-docs] The API reference repeats the same split as a design statement rather than an implementation detail.

## Prompt caching

The system prompt and instructions carry only the static guidance and the note on the plan's tag; the plan reaches the model through tool results or through a recorded part, both appended to the history, so the cached prefix stays valid[^pydantic-planning-docs] `Planning` places no cache breakpoint of its own — caching is a model setting (`anthropic_cache`, `anthropic_cache_messages`, `bedrock_cache_messages`, `openrouter_cache_messages`), and those breakpoints cover the plan tools' results with the rest of the history.

Two compatibility consequences travel with that design:

- `cache_ttl` is **deprecated and has no effect**; setting `'5m'` or `'1h'` warns that it is ignored, and a warning is the whole outcome[^pydantic-planning-docs]
- The tag was `<plan-reminder>` in earlier releases, so any prompt, parser or saved payload that names the old spelling has to be updated[^pydantic-planning-docs]

With a UI adapter, history that goes through the client may lose the metadata marking a plan tool's result (AG-UI drops it) and leaves out the `PlanReminderPart` records, which are capability parts; when the client sends that history back, `Planning` records the plan again on the next request[^pydantic-planning-docs] The source's advice is to keep history on the server when that matters — the same conclusion [file understanding](pydantic-ai-file-understanding.md) reaches for a different reason.

## Durable execution

Under a [durable-execution](pydantic-ai-durable-execution.md) capability every plan store call is a journaled capability operation: the plan read before each model request that decides whether to record it, and each read and write the plan tools make[^pydantic-planning-docs] Replay reuses the recorded result instead of calling the store again, so recovering a run does not append a step to a persistent store a second time.

The engine shape changes two things[^pydantic-planning-docs]:

| Engine shape | Effect on `Planning` |
| --- | --- |
| Function tools run in workflow code (DBOS) | A plan tool call runs alone, without overlapping other tool calls, and emits its run events after its last store call, so recorded store calls keep their order on replay — including relative to the steps an `event_stream_handler` runs for those events |
| Tools and capability operations run in a separate worker (Temporal) | The run's in-memory plan does not cross; each call resolves its store from the run context, so a persistent `store` or `store_resolver` is required to keep the plan across steps |

`Planning` carries the stable default `id='planning'`, so durable recovery works without configuration[^pydantic-planning-docs] That is the same naming rule [durable tool placement](pydantic-ai-durable-tool-placement.md) describes for every durable unit: change the id after deploy and in-flight runs no longer match.

## Configuration

```python
Planning(
    guidance=None,           # static tool guidance; None = default, '' = omit (the plan note stays)
    store=None,              # None = fresh in-memory plan per run; or a PlanStore to persist
    enable_subtasks=False,   # add subtask/dependency tools and the 'blocked' status
    inject=True,             # show the model the plan: in the plan tools' results, the note, and a record
    tools=None,              # None = every tool the mode registers; or an allowlist of names
    descriptions=None,       # optional per-tool description overrides, keyed by tool name
)
```

`Planning` works with Pydantic AI's agent spec: `capabilities: [{Planning: {}}]` in YAML, loaded with `Agent.from_file(..., custom_capability_types=[Planning])`[^pydantic-planning-docs] The `from_spec` classmethod takes the serializable subset — `backend` (`'memory'` or `'sqlite'`), `database` (default `.agent-plan.db`), `session` (default `'default'`), `enable_subtasks`, `inject`, `guidance`, the deprecated `cache_ttl`, `tools`, `id`, `description` and `defer_loading` — so a spec can persist a plan but cannot name a Postgres pool or Redis client.

## Relationship to pydantic-ai-todo

`Planning` incorporates the task-list features of [`pydantic-ai-todo`](https://github.com/vstorm-co/pydantic-ai-todo), a community package by [Vstorm](https://vstorm.co/) — persistent stores, subtasks, dependencies and events — and supersedes it[^pydantic-planning-docs] Migration is a rename, not a rewrite:

| `pydantic-ai-todo` | `Planning` |
| --- | --- |
| `write_todos` | `write_plan` |
| `read_todos` | `read_plan` |
| `add_todo` | `add_task` |
| `update_todo_status` / `update_todo_statuses` | `update_task_status` / `update_task_statuses` |
| `remove_todo` | `remove_task` |
| `add_subtask`, `set_dependency`, `get_available_tasks` | unchanged |

Two conveniences are deliberately gone: `create_storage(backend=...)` (you construct your own asyncpg pool or Redis client) and a `timestamp` on `PlanEvent`, so a consumer that ordered or logged by it supplies its own clock[^pydantic-planning-docs] This is the community-to-core path [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md) describes from the ecosystem side, with a Vstorm package's feature set landing in the first-party Harness.

## Limits

- The source is a single vendor documentation page — "Planning", Pydantic Docs, 3,176 words as declared and 3,260 by local `wc -w`, **no publication date, no author and no Pydantic AI or Harness version**. Under the `pydantic-ai` domain rule the page is `draft` and every API name is version-unknown[^pydantic-planning-docs]
- Nothing was executed: no package installed, no `Planning` constructed, no plan written or migrated between stores, no event received, no durable run replayed, no cache hit measured. Every behavioural claim is **Reported**[^pydantic-planning-docs]
- The examples pin model aliases (`anthropic:claude-sonnet-5-5`, `claude-opus-5-5`, `claude-sonnet-4-6`) that no other capture here corroborates, so the planner/executor pairing is illustrative rather than tested.
- Unstated by the source: the tool JSON schemas and whether `active_form` is required, how the "one `in_progress` step" convention is signalled, the `PlanStore` protocol's other five methods, the store schema or migration path, concurrent writers on one store, retention, and whether `Planning` surfaces its own spans in [traces](pydantic-ai-observability.md).
- External links — the Harness version policy, the capability overview, Anthropic prompt caching, Code Mode, the UI-adapter trust model, the agent-spec page and the `pydantic-ai-todo` repository — were read as links, not followed.

## Relationships

- **Is a** [Harness](pydantic-ai-harness.md) [capability](pydantic-ai-capability-primitive.md), attached through `capabilities=[Planning()]` and shipping under the Harness's 0.x version policy.
- **Protects** [prompt caching](pydantic-ai-prompt-caching.md) by keeping the plan off the system prompt and appending every change; it places no breakpoint itself and deprecates `cache_ttl`.
- **Becomes durable under** [Pydantic AI durable execution](pydantic-ai-durable-execution.md): store reads and writes are journaled capability operations, with `id='planning'` as the stable default the placement rules require.
- **Supersedes** Vstorm's `pydantic-ai-todo` feature set, whose ecosystem context is recorded in [Vstorm Pydantic AI capabilities](vstorm-pydantic-ai-capabilities.md).
- **Shares the server-history argument with** [file understanding](pydantic-ai-file-understanding.md): a client-held history loses framework metadata and forces re-recording.
- **Composes with** [Harness subagents](pydantic-ai-subagents.md) in a planning orchestrator: the plan travels in tool results while delegates do the work, and both design choices exist for the same reason — a change must append to the prompt rather than rewrite the cached prefix.
- **Depends on** [conversation state](pydantic-ai-conversation-state.md) in practice — the plan lives in persisted history as a capability part, so state that survives a run is what makes the same plan visible to a later one.

[^pydantic-planning-docs]: Pydantic Docs, "Planning", <https://pydantic.dev/docs/ai/harness/planning/>; local capture `raw/harness/planning/index.md`, content digest sha256:13d1290b, 3,176 words as declared (3,260 by `wc -w`), no publication date, author or framework version. Lines 16–32 for the capability diagram (tools, `PlanStore`, `plan_reminder`, and the before-each-request fallback); lines 34–36 for the drift problem and the cache-invalidation cost of system-prompt re-injection; lines 38–50 for the `<plan_reminder>` tool-result design, tag escaping, the fixed instructions note, the `origin`/`plan` metadata, the three re-record cases, `ClearToolResults`, the `PlanReminderPart` user-channel record, `No plan yet.`, and the `guidance`/`inject=False` behaviour; lines 52–64 for the `Planning()` usage example; lines 66–87 for the six default tools, the step shape and statuses, the one-`in_progress` convention, the `tools=` allowlist, `ValueError` cases and `descriptions`; lines 89–99 for `enable_subtasks`, the three subtask tools, `blocked`, cycle rejection and the `write_plan` rejections; lines 101–131 for default in-memory plans, the four stores, caller-owned pools and clients, first-use table creation, the SQLite-on-the-machine rule, `store_resolver`, the fail-the-run store read and the `BestEffort` wrapper; lines 133–149 for the shared-store planner/executor handoff and the unenforced read-only discipline; lines 151–169 for the five events, `previous_item`/`previous_state`, run-versus-direct mutation and the deprecated emitter parameters; lines 171–173 for whole-plan replacement versus stable ids; lines 175–183 for no-own-breakpoint caching, the deprecated `cache_ttl`, the `<plan-reminder>` tag rename, the AG-UI metadata loss and server-side history, and journaled store calls with the DBOS ordering and Temporal store-resolution rules plus `id='planning'`; lines 185–198 for the configuration block; lines 200–217 for the agent-spec YAML and `custom_capability_types`; lines 219–236 for `pydantic-ai-todo` incorporation, the rename table, the removed `create_storage` and the absent `timestamp`; lines 238–436 for the API reference (attributes, `for_run`/`resolve_store`/`get_toolset`/`get_instructions`/`before_model_request`, and `from_spec`). Evidence class: **Reported** — vendor documentation with no execution behind it.
