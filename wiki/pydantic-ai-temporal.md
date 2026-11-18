---
type: Concept
title: Pydantic AI on Temporal
description: What changes when a Pydantic AI agent runs inside a Temporal workflow — the workflow/activity split, the names and ids that must not change after deploy, the limited RunContext that crosses into an activity, payload ceilings, per-tool activity config, child workflows, retry ownership and Logfire wiring.
tags: [ml, pydantic-ai, agents, durability, temporal]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:22:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-temporal-docs
    resource: ../raw/capabilities/durable_execution/temporal/index.md
    scope: ../raw/capabilities/durable_execution/temporal/
    kind: documentation
    revision: sha256:d1d6bdec59bcd1f8230987074ce0d7a28d0a365a38df590e4b5efb7326aead73
    title: "Durable Execution with Temporal"
---

**Reported, Pydantic AI version unspecified:** Temporal is the durability engine with the most explicit boundary. The agent's run loop is workflow code, and everything that touches I/O — model requests, tool calls, MCP communication — becomes an activity, so recovery re-runs the deterministic code and reuses each recorded activity result instead of repeating its side effect.[^pydantic-temporal-docs] Attaching `TemporalDurability()` changes almost nothing in the agent's source, but it changes a lot about what may cross between the two halves: which values are serializable, which names are permanent, how large a payload may be, and which toolset can arrive late.

For the engine's place among the other eight engines and their shipping locations, see [Pydantic AI durable execution](pydantic-ai-durable-execution.md); for the streaming, cancellation and long-run half of this integration, see [Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md).

## The split the engine enforces

Temporal separates repeatable from non-repeatable work. Workflows re-execute identically on replay and may not do I/O; activities may do anything but restart from the beginning when they fail part-way.[^pydantic-temporal-docs] Applied to an agent, the coordinating logic of `agent.run()` stays in the workflow while model requests, I/O-performing tool calls and MCP server communication are offloaded, and the Temporal server — not the worker — holds workflow state in its database, possibly replicated, with data encrypted and processing done on the worker.[^pydantic-temporal-docs]

The consequence that shapes everything below is that workflows and activities usually run in different processes, in different workers, possibly on different hosts. Values passed between them are stored in the workflow event history, so they must be serializable by Pydantic and must fit a payload limit.[^pydantic-temporal-docs]

## Attaching durability

Install with `pip install pydantic-ai[temporal]` (or `pydantic-ai-slim[temporal]`) and attach the capability; outside a workflow the same agent behaves as a normal `Agent`:[^pydantic-temporal-docs]

```python
agent = Agent(
    'openai:gpt-6.1-sol',
    instructions="You're an expert in geography.",
    name='geography',
    capabilities=[TemporalDurability()],
)

@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        return (await agent.run(prompt)).output
```

- The agent's `name` identifies its activities, and the capability discovers the agent's name, model and toolsets when it binds, registering an activity for each.[^pydantic-temporal-docs]
- `PydanticAIPlugin()` passed to `Client.connect()` installs Pydantic serialization and registers the activities and child workflows of every agent listed in `__pydantic_ai_agents__`; `AgentPlugin` does the same for one agent when editing the worker is easier than editing the workflow class.[^pydantic-temporal-docs]
- Subclassing `PydanticAIWorkflow` is optional and buys typing for that class variable.[^pydantic-temporal-docs]
- `run_sync()` inside a workflow raises `UserError`, because it drives its own event loop; `await agent.run()` is the documented replacement.[^pydantic-temporal-docs]
- The capability composes with other capabilities — instrumentation, `SetToolMetadata`, `ProcessEventStream` — without Temporal-specific wrapper variants, because outside a workflow it is transparent.[^pydantic-temporal-docs]

Non-retryable exceptions are preconfigured rather than left to the retry policy: `UserError`, `PydanticUserError`, `UnexpectedModelBehavior` and `FallbackExceptionGroup` are non-retryable, along with Temporal's own over-limit payload failures (`PayloadsTooLarge`, and `PayloadSizeError` before `temporalio` 1.31) and the workspace errors `WorkspaceTimeoutError`, `WorkspaceOutputLimitError`, `WorkspaceReadOnlyError` and `WorkspaceUnavailableError`.[^pydantic-temporal-docs] A retry policy's `non_retryable_error_types` matches exact class names, so a subclass such as `ContentFilterError` or your own `UserError` subclass would slip through; the activity marks those non-retryable itself.[^pydantic-temporal-docs] The worker separately registers `UserError`, `PydanticUserError`, `AgentRunError`, `FallbackExceptionGroup`, `UnsupportedEventLoopError` and `WorkspaceError` as `workflow_failure_exception_types`.[^pydantic-temporal-docs]

### The deprecated wrapper

`TemporalAgent(agent)` still exists as the older path: it freezes the model and toolsets at wrap time, creates activities for each, and the original agent stays usable outside workflows but later changes to its model or toolsets are never reflected.[^pydantic-temporal-docs] It is documented as deprecated, and it is also looser in three later sections: it forbids `run_stream()` inside workflows, rejects `timeout=`, and does not reject toolsets registered after wrapping, so a toolset added late is silently left out of the run.[^pydantic-temporal-docs]

## Names and ids are permanent

Temporal needs to know which code to run when an activity is restarted, potentially after a deploy, so each activity's name must be stable and unique. Pydantic AI derives the name from the agent's `name` and the toolsets' `id`s — normally optional fields that become required here, and changing either after deploying breaks in-flight workflows.[^pydantic-temporal-docs]

| Wrapped unit | Where its id comes from | Trap |
| --- | --- | --- |
| Model requests | Agent `name` | Renaming the agent breaks active workflows |
| `FunctionToolset`, `MCPToolset` | Toolset `id` | The hostname a URL-based `MCPToolset` would take as its `id` does not count |
| `DynamicToolset` | Explicit `id=` | `per_run_step=False` is not respected: the toolset is rebuilt in the activity |
| `DynamicCapability` | Stable capability `id` | Its factory must be deterministic given the run's deps |
| Capability-owned toolset | The capability's `id` | `Capability(id=..., tools=[...])`, `MCP(id=..., url=...)`; `MCP` falls back to the URL hostname |

Two upgrade hazards sit beside the naming rule. A release that changes the activity sequence for tools with an `args_validator` requires Temporal worker versioning or a `workflow.patched()` marker for workflows already in flight, and a `FunctionToolset`'s `sequential=True` and `defer_loading=True` are now applied to the `Tool` instances it holds — workflows started earlier keep listing those tools without them so their history replays unchanged.[^pydantic-temporal-docs]

MCP sessions do not survive the boundary in either direction. An attached `MCPToolset` connects inside every activity that lists or calls its tools, because an activity cannot use a session the workflow holds and may not even run in that process; each session closes when the activity returns, so `cache_tools` only covers the activity that filled it.[^pydantic-temporal-docs] The workflow does keep the definitions its `get_tools` activity recorded, so discovery costs one activity per run rather than one per model request.[^pydantic-temporal-docs]

Tool argument validation runs in a `validate_args` activity, so a validator may do I/O and dynamic-tool validators survive the boundary. A tool without one schedules no extra activity. Validation runs before approval and deferral, so rejected arguments never reach an approver, and resuming an approved call re-runs validation with `tool_call_approved` set; because each activity derives its typed arguments independently, schema validators must be idempotent.[^pydantic-temporal-docs]

## What crosses into an activity

The `RunContext` a tool sees inside an activity is a limited, rebuilt copy, not the workflow's object.[^pydantic-temporal-docs]

- `deps` must be Pydantic-serializable, and so must `model_settings`, the context's `metadata` and `tool_call_metadata`, and tool metadata; an unserializable value raises `UserError` naming the type. `model_settings['timeout']` must be a number of seconds, not an `httpx.Timeout`.[^pydantic-temporal-docs]
- Fields carried as untyped dictionaries arrive as JSON shapes: a `set` or `tuple` becomes a `list`, a dataclass or model becomes a `dict`, UTF-8 `bytes` become `str`, and non-string keys become strings. Binary content does not cross at all unless base64-encoded first.[^pydantic-temporal-docs]
- Everything with a declared type round-trips faithfully — the rest of each message, `ToolDefinition`, `ModelRequestParameters`, and the context's `usage`, `usage_limits`, `loaded_capability_ids` and `discovered_tool_names`.[^pydantic-temporal-docs]
- By default only `deps`, `run_id`, `conversation_id`, `metadata`, `retries`, the tool-call fields, `retry`, `max_retries`, `run_step`, `partial_output`, `usage`, `usage_limits`, `trace_include_content`, `instrumentation_version`, `loaded_capability_ids`, `discovered_tool_names` and `capability_active` are present.[^pydantic-temporal-docs]
- `agent` and `root_capability` are re-attached from the worker's instance and `tracer` resolves through that agent's instrumentation — `Instrumentation`, `agent.instrument` or `Agent.instrument_all()` — so a tool that opens spans works as it does in-process, while an `Instrumentation` passed to a single `run()` is invisible to the worker.[^pydantic-temporal-docs]
- `tool_manager` is `None`: `available_tool_names` returns the snapshot taken when the activity was dispatched, and `active_capability_ids` is carried the same way so `is_tool_available` still answers for a capability-owned tool.[^pydantic-temporal-docs]
- `ctx.enqueue()`, `ctx.dequeue()`, `ctx.set_enqueue_priority()` and `ctx.load_capability()` raise inside an activity, because the recorded result is replayed without re-running the code and a queued message would be dropped.[^pydantic-temporal-docs]
- Any other attribute — `model`, `prompt`, `messages`, `model_settings`, `capabilities` — raises `UserError` instead of returning a default, so missing state cannot be mistaken for real state. `validation_context` is rebuilt rather than serialized.[^pydantic-temporal-docs]

A `TemporalRunContext` subclass with custom `serialize_run_context`/`deserialize_run_context` class methods, passed as `run_context_type`, is the documented way to carry more — including `prompt`, which a subclass may opt into if its prompts are text-only. The reason not to by default is payload cost: a multi-modal prompt would put its `BinaryContent` in every activity payload.[^pydantic-temporal-docs]

Copies, not references, have an accounting consequence. Mutation inside an activity never reaches the run, so a tool that delegates to another agent with `usage=ctx.usage` loses the delegate's tokens: they are absent from `result.usage` and never charged against the run's usage limits. Return the delegate's usage from the tool or record it in a store the `deps` can reach.[^pydantic-temporal-docs] DBOS and Prefect pass the live context into in-process units so mutations accrue while the body runs, but lose them whenever a recorded result is replayed or a task cache hits, which is why the docs advise against relying on that; a general return channel is tracked in pydantic-ai#6886.[^pydantic-temporal-docs]

Two derived values are deliberately deterministic: when `run_id` or `conversation_id` is not passed, the defaults come from the workflow run rather than from randomness, so they are identical when the workflow replays on another worker and every activity sees the same ids as the result.[^pydantic-temporal-docs] A tool's `prepare` function is not cut down at all — for `FunctionToolset` tools, including the agent's own, it runs in workflow code with the full context once per step and its returned definition is what the activity runs — except for `DynamicToolset` tools, whose `prepare` runs in the activity with the limited context.[^pydantic-temporal-docs] A `native=` factory on `XSearch` or `ImageGeneration` is resolved twice, on either side of the boundary, and the second call sees only the limited context, so it must read `ctx.deps` rather than `ctx.messages`.[^pydantic-temporal-docs]

## Workspaces and Harness workspace capabilities

Attach the workspace capability when constructing the agent, as usual. Inside a tool, `ctx.workspace` is rebuilt in the activity and calls the provider directly; in workflow code — capability hooks, output functions, `result.workspace` — each call becomes an activity of its own.[^pydantic-temporal-docs] Because that activity can run on any worker: construct every worker's agent with the same workspace capabilities, let a custom `get_workspace` read only `deps` and the context fields above, move large files inside a tool rather than passing them as workflow-side arguments, and give every worker the same absolute directory when using `LocalWorkspace`, on storage they share.[^pydantic-temporal-docs]

Two deployment notes follow. Adding a workspace to an agent changes its workflows' history, so drain in-flight workflows first or deploy with worker versioning or on a new task queue. And because workflow-side workspace arguments — commands, `env=`, file contents — are stored in history, secrets belong in the workspace capability's `env=` or inside a tool, or behind a payload codec.[^pydantic-temporal-docs]

Harness workspace capabilities (`Coder`, `Shell`, `FileSystem`) work, with three Temporal-specific behaviours:[^pydantic-temporal-docs]

- **Event delivery is split.** Tools that write files ask for approval and report the write from workflow code, so `FileChangeRequestedEvent`, `FileWrittenEvent`, `FileEditedEvent` and `DirectoryCreatedEvent` reach listeners live. Read and shell events — `FileReadEvent`, `DirectoryListedEvent`, `FilesSearchedEvent`, and `CommandStartedEvent`/`CommandOutputEvent`/`CommandFinishedEvent` — come from tools running in activities and are not delivered (pydantic-ai#7971); the tools still return their results. Approval listeners re-run on replay, so their external effects must be idempotent, and a write tool moved into an activity raises `UserError` rather than writing unobserved.[^pydantic-temporal-docs]
- **Delegation placement follows the delegate.** `Coder`'s `self` delegate runs in the workflow, so the child's model requests and tools become activities of the same agent; a `SubAgents` whose only delegate is `self` behaves the same, with a `models` menu registered through `TemporalDurability(models=...)`. Any other delegate runs in an activity, where the parent's model is unavailable, so each delegate needs its own model or a `models` entry. Sub-agents read from `agent_folders` are unsupported, because reading folders at run start adds a toolset at run time; compose `SubAgents(include_self=True, agent_folders=None)` instead.[^pydantic-temporal-docs]
- **Command timeouts need raising by hand.** Activities default to 60 seconds; `run_command` and `shell` get 300, covering the shell's 270-second foreground wait. A longer timeout, from `Shell(default_timeout=...)` or the model's `timeout_seconds`, needs a matching `SetToolMetadata(tools=['run_command'], temporal=ActivityConfig(start_to_close_timeout=...))`, or `start_command`/`shell(mode='background')` for work that outlives a call.[^pydantic-temporal-docs]

## The 2MB payload ceiling

Every payload the engine records — activity arguments as well as results — is stored in the workflow history and capped at 2MB by default.[^pydantic-temporal-docs] Two things breach it:

- **Binary content.** Base64 encoding on the way in leaves about three quarters of the cap, roughly 1.5MB of raw bytes, so an image that reads as comfortably under 2MB can still be rejected. A tool returning a `BinaryImage` — the direct generator, the `ImageGeneration` subagent fallback, or your own `local=` tool — and a model returning an image both surface as `UserError`, naming the tool or the model respectively. The fix is to keep bytes out of history: write to object storage and return an `ImageUrl` or a key.[^pydantic-temporal-docs]
- **A wide `deps` object.** It is copied into history every time a model, tool, MCP or event-handler activity is scheduled, so a wide fan-out both bloats history permanently and can breach the per-payload limit.[^pydantic-temporal-docs]

Temporal's general answer is external storage: an `ExternalStorage(drivers=[...])` on a `DataConverter` offloads any payload above a threshold (256 KiB by default) and puts a reference in history instead. `PydanticAIPlugin` replaces only the payload converter, so `external_storage`, a custom `payload_codec` and `failure_converter_class` all survive.[^pydantic-temporal-docs] It is in public preview, it offloads per payload so a fan-out of N activities still emits N references, and it does not deduplicate identical deps within one workflow-task completion. A hand-written claim-check codec is the non-preview alternative, and raising `limit.blobSize.error` is the last resort — it raises the ceiling without removing it, because Temporal's gRPC message limit still applies.[^pydantic-temporal-docs]

## Activity configuration

Four `ActivityConfig` keys are accepted by `TemporalDurability`; each specialised one merges over the base:[^pydantic-temporal-docs]

| Key | Applies to |
| --- | --- |
| `activity_config` | Everything; `start_to_close_timeout` defaults to 60 seconds |
| `model_activity_config` | Model request activities |
| `event_stream_handler_activity_config` | Event stream handler activities |
| `toolset_activity_config` | Get-tools and call-tool activities, keyed by toolset id |

Because `ActivityConfig` is a `TypedDict`, a misspelled key would otherwise fail only once the config reached Temporal inside the workflow — where the failure is retried indefinitely — so keys are validated when `TemporalDurability` is constructed and an unknown key raises `UserError` up front.[^pydantic-temporal-docs] Model request activities start from Temporal's default `RetryPolicy.maximum_attempts` of `0`, which means unbounded re-execution; the retry multiplication that stacks with SDK and transport retries is worked out in [retry layers and multiplication](pydantic-ai-retry-layers.md), and the categories it classifies on are in [model API errors](pydantic-ai-model-api-errors.md).[^pydantic-temporal-docs]

Every registered activity heartbeats in the background while it runs, so a long-but-healthy activity is not mistaken for a dead worker and workflow cancellation can reach it. Only model request activities get a `heartbeat_timeout` by default — 30 seconds — and setting one elsewhere is the application's job.[^pydantic-temporal-docs]

### Per-tool activity config

Per-tool configuration lives on the tool's `metadata` under a `'temporal'` key, either inline or applied across a selection with the `SetToolMetadata` capability, and it merges on top of the toolset and base configs. The value is an `ActivityConfig`, or `False` to skip activity wrapping entirely — valid only for async tools, since sync tools always need an activity and MCP tools always run in theirs, where `False` raises `UserError`.[^pydantic-temporal-docs] The engine-neutral `durable=False` from [durable tool placement](pydantic-ai-durable-tool-placement.md) is the portable way to express the same opt-out, and a `'temporal'` key on the same tool wins over it.[^pydantic-temporal-docs]

### Child workflows

An async function tool can run as a Temporal child workflow instead of an activity by setting `metadata={'temporal': {'child_workflow': ChildWorkflowConfig(...)}}`; the value accepts the same options as `workflow.start_child_workflow()`.[^pydantic-temporal-docs] The documented use is a nested agent with its own `TemporalDurability`: the nested model requests and tool calls stay durable, recorded in the child's history rather than growing the parent's.[^pydantic-temporal-docs]

- Both agents must be registered — in `__pydantic_ai_agents__` or through an `AgentPlugin` each — so the worker knows the nested agent's activities and the child workflow definition.[^pydantic-temporal-docs]
- With no `id`, the child workflow id is the parent's workflow id followed by a UUID the workflow generates deterministically; `task_queue`, the three timeouts, `id_reuse_policy`, `retry_policy`, `cron_schedule`, `cancellation_type`, `parent_close_policy`, `memo`, `search_attributes`, `versioning_intent`, `static_summary`, `static_details` and `priority` pass through to Temporal.[^pydantic-temporal-docs]
- The tool body runs as deterministic workflow code, so it must delegate I/O to durable operations; child workflows are not supported for sync, dynamic or MCP tools.[^pydantic-temporal-docs]
- An exception in the tool body fails the child and reaches the parent like a failed activity, retried per the child's `retry_policy` except for errors a retry cannot fix, such as `UserError`.[^pydantic-temporal-docs]
- A toolset's child workflow is registered when the plugin configures it, if `child_workflow` metadata exists by then — including tools added with `@agent.tool` or metadata applied by `SetToolMetadata`. Metadata that only appears later, from a capability that rewrites tool definitions during a run, fails the tool call with `UserError`, and registering only `TemporalDurability.temporal_activities` is rejected outright because it would omit the workflow definitions.[^pydantic-temporal-docs]
- `AgentPlugin` registers an agent's child workflows on every worker it is given, including an activities-only worker created without `workflows`, which then also polls for workflow tasks; `AgentPlugin(agent, register_workflows=False)` limits a worker to activities.[^pydantic-temporal-docs]

## Retries: one owner

Pydantic AI's transport retries and the provider SDK's client retries stack on top of Temporal's activity retries, so the recommendation is to turn the inner two off with `ModelSettings['max_retries'] = 0` and let the engine be the single retry owner, customising Temporal's policy through activity configuration.[^pydantic-temporal-docs]

Error delivery differs by origin:

- A tool exception reaches workflow code as Temporal's `ActivityError`, with the original class name in `cause.type`.[^pydantic-temporal-docs]
- A model error does not. `ModelAPIError`/`ModelHTTPError` raised by a model request reaches workflow code as itself with its fields — non-JSON-serializable values crossing as their string form — so `on_model_request_error` hooks and `ModelFallback` behave as they do without Temporal, with the original `ActivityError` as `__cause__`. Only Pydantic AI's own classes get this treatment; a subclass you define still arrives as an `ActivityError`.[^pydantic-temporal-docs]
- Workflow code and capabilities see the error *category* (`except ModelTimeoutError`, `except ModelRateLimitError`), while a retry policy's `non_retryable_error_types` only sees the `ApplicationError` type — `ModelHTTPError` when the error carries an HTTP status, otherwise `ModelAPIError`. A policy naming a category matches nothing.[^pydantic-temporal-docs]

`non_retryable_model_errors` defaults to `ModelRequestRejectedError` (covering context-window, authentication and model-not-found failures), `ModelQuotaExceededError` and `ModelRequestTimeout` — the errors another attempt cannot fix — and a listed error fails the model activity on its first attempt whatever the policy says, still arriving as its own class so a fallback can act on it.[^pydantic-temporal-docs] Matching is `isinstance`, so listing `ModelUnavailableError` also covers `ModelOverloadedError`. A list you pass replaces the default, so include the defaults you still want, or pass `()` to retry everything.[^pydantic-temporal-docs]

When a model error carries a `retry_after`, Temporal waits that long instead of using the policy's backoff, capped at the policy's `maximum_interval` — 100× `initial_interval`, so 100 seconds by default — with `maximum_attempts` and `schedule_to_close_timeout` still applying. Listing `ModelRateLimitError` as non-retryable is the way to fail or fall back instead of waiting.[^pydantic-temporal-docs]

## Choosing a model or toolset at runtime

Model-name strings work unchanged and never need registering: a string is rebuilt on the worker, and `ResolveModelId` can take over that construction — for a custom provider, injected keys, or per-user credentials carried on `deps` — placed before `TemporalDurability` so it gets first crack at every string, including inside the activity where it re-runs with the real deps. It must be deterministic for a given `(model_id, deps)` and must not perform I/O.[^pydantic-temporal-docs]

A model *instance* cannot be serialized, and rebuilding one from its `model_id` would build a different model — the same name on whatever provider the worker's environment implies, with other credentials — so an unregistered instance raises `UserError`. Pre-register instances in `TemporalDurability(models={...})` and select them by name or pass the registered instance; the same rule governs a `ModelFallback`'s fallback models. The agent's own construction-time model is always available, so an agent needs a model at construction or a capability that supplies one, such as `ModelFallback` or `SelectModel`.[^pydantic-temporal-docs]

Toolsets are stricter, because their activities must exist before the workflow runs:[^pydantic-temporal-docs]

| Arrival | Executing toolset (e.g. `FunctionToolset`, `MCPToolset`, `DynamicToolset`) | Non-executing toolset (`ExternalToolset`, opted-out tools) |
| --- | --- | --- |
| `Agent(toolsets=[...])` | Supported; give a `DynamicToolset` an explicit `id` | Supported |
| `agent.run(toolsets=...)` | `UserError` | Supported |
| `agent.override(toolsets=...)` inside a workflow | `UserError` | Supported |
| `@agent.toolset` decorator inside a workflow | `UserError` — it registers after the durable units exist | — |

A runtime toolset also may not reuse the `id` of one the agent was constructed with, since the `id` is what routes a tool call to a registered activity.[^pydantic-temporal-docs] Capabilities are held to the same rule: `agent.run(capabilities=[...])` inside a workflow raises `UserError`, with `Instrumentation` exempt because it only observes the run. Pydantic AI concedes the restriction is conservative — third-party capabilities cannot yet declare that they only observe — and tracking it in pydantic-ai#5477.[^pydantic-temporal-docs]

## Logfire wiring

`LogfirePlugin()` beside `PydanticAIPlugin()` on `Client.connect()` instruments Temporal, including its metrics, and Pydantic AI, sending everything to Logfire.[^pydantic-temporal-docs] Its tracing is replay-safe, so replaying history emits no duplicate spans, with span and trace ids coming from Temporal's deterministic generator. That safety is installed when a client, worker or replayer is created, so Logfire must be configured first: calling `logfire.configure()` afterwards turns replay-safety off until the next client, worker or replayer is created.[^pydantic-temporal-docs]

- Metrics export every 60 seconds; `metric_periodicity` accepts a `timedelta`.[^pydantic-temporal-docs]
- An existing `logfire.configure()` is kept rather than replaced, so scrubbing, exporters, sampling and console settings survive. A `setup_logfire` function passed to the plugin can return a custom `Logfire` instance; it is called once, and owning it means owning Pydantic AI instrumentation too.[^pydantic-temporal-docs]
- `replay_safe=False` falls back to Logfire's regular tracer provider, which duplicates agent and Temporal spans on replay; `metrics=False` stops the metrics export and lets you supply your own Temporal `Runtime`.[^pydantic-temporal-docs]
- Independently of the plugin, Pydantic AI records a model request's or tool call's span and a model request's token and cost metrics only when the activity runs, so replay adds nothing, with Logfire or any other OTel backend.[^pydantic-temporal-docs]
- A decision model's `decide` spans need the agent's instrumentation visible to the worker — `Agent.instrument_all()` (which the plugin sets up), `agent.instrument`, or an `Instrumentation` capability; a run instrumented only per-run gets none.[^pydantic-temporal-docs]

## Known issue: pandas in the sandbox

`logfire.info` inside an activity can fail with `AttributeError: partially initialized module 'pandas' has no attribute '_pandas_parser_CAPI'` when `pandas` is a dependency — an import race — and the fix is to import it in `workflow.unsafe.imports_passed_through()` so the workflow sandbox does not reload it.[^pydantic-temporal-docs]

## Coverage and limits

The sole artifact is the Pydantic documentation capture `index.md` (10,968 words as declared, 10,860 by local `wc -w` including frontmatter), inspected as text; there are no attachments, includes, imports, downloads or supporting files in the package.[^pydantic-temporal-docs]

- The page names no Pydantic AI or Temporal release version, author, publication date or licence, so every API and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule.[^pydantic-temporal-docs]
- Every external link — Temporal's workflow, activity, signal, versioning, external-storage, dynamic-configuration, blob-size and Python SDK pages; the Pydantic AI API references for `TemporalDurability`, `TemporalRunContext`, `AgentEventStream`, `AgentPlugin`, `PydanticAIPlugin` and `LogfirePlugin`; the MCP, workspace, harness, capabilities, toolsets and dependencies docs; and the two issue threads (#7971, #6886) — was read as a link, not followed.[^pydantic-temporal-docs]
- Nothing was installed, no Temporal server started, no worker or workflow run, no activity scheduled, retried, cancelled or replayed, no payload offloaded and no span opened, so every claim is **Reported** and none **Observed** or **Reproduced**. Prices are absent from the source entirely.
- Evidence class: **Reported**.

## Relationships

- **Instance of** [Pydantic AI durable execution](pydantic-ai-durable-execution.md), the engine table and shipping-location decision this page assumes.
- **Supplies one retry owner to** [retry layers and multiplication](pydantic-ai-retry-layers.md): an activity re-runs the whole model request, so its `maximum_attempts` re-enters the SDK and transport attempts beneath it unless those are set to one attempt.
- **Constrains** [Pydantic AI durable tool placement](pydantic-ai-durable-tool-placement.md): Temporal's `metadata={'temporal': ...}` key and its child-workflow route are the engine-specific settings that beat the portable `durable=False` flag.[^pydantic-temporal-docs]
- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for attachment, and on construction-time registration for every executing capability.[^pydantic-temporal-docs]
- **Bound by** [Pydantic AI dependencies](pydantic-ai-dependencies.md): anything crossing into an activity must be Pydantic-serializable, and a wide deps object is a payload cost.[^pydantic-temporal-docs]
- **Moves** [workspaces and sandboxes](pydantic-ai-workspaces-and-sandboxes.md) off the workflow process, with per-worker parity and history-visible arguments as the cost.[^pydantic-temporal-docs]
- **Changes** [MCP integration](pydantic-ai-mcp-integration.md) behaviour: one session per activity, `cache_tools` scoped to that activity, discovery recorded once per run.[^pydantic-temporal-docs]
- **Specialises** [Pydantic AI Harness](pydantic-ai-harness.md) workspace capabilities: split event delivery, delegate model requirements and raised command timeouts.[^pydantic-temporal-docs]
- **Feeds** [Pydantic AI observability](pydantic-ai-observability.md) through `LogfirePlugin`'s replay-safe Temporal instrumentation.[^pydantic-temporal-docs]
- **Splits its long-run behaviour into** [Temporal streaming and cancellation](pydantic-ai-temporal-streaming.md): buffered streams, Workflow Streams, cancellation, run timeouts, suspended turns and continue-as-new.[^pydantic-temporal-docs]
- **Interacts with** [model fallback](pydantic-ai-model-fallback.md): each fallback attempt gets its own durable model operation, and a model instance must be registered by name.[^pydantic-temporal-docs]
- **Makes** [Conversation state](pydantic-ai-conversation-state.md) ids replay-deterministic, because an unset `conversation_id` derives from the workflow run.[^pydantic-temporal-docs]

[^pydantic-temporal-docs]: Pydantic, "Durable Execution with Temporal" (pydantic.dev docs, `/docs/ai/capabilities/durable_execution/temporal/`), 10,968 words as declared, 10,860 by local `wc -w`, no version, date or author stated; local capture `raw/capabilities/durable_execution/temporal/index.md`, content digest sha256:d1d6bdec. §"Durable Execution" (lines 13–60) for the workflow/activity split, the replay mechanism, the server/worker data boundary and the architecture diagram; §"Durable Agent" (61–180) for the install extras, the `geography` sample, the name-discovery sentence, `PydanticAIPlugin`, the `PydanticAIWorkflow` subclass, `run_sync` refusal, capability composition, the non-retryable exception list and the `workflow_failure_exception_types` registration; §"Wrapper-agent path (deprecated)" (181–196) for `TemporalAgent`'s frozen model and toolsets; §"Agent Names and Toolset IDs" (201–218) for the derived names, the `args_validator` upgrade hazard, the `sequential`/`defer_loading` history rule, `DynamicToolset`/`DynamicCapability` re-resolution and ids, MCP sessions per activity, `cache_tools` scope, `get_tools` recording, and capability-derived ids; §"Tool Argument Validation" (219–224); §"Agent Run Context and Dependencies" (225–246) for the serialization rules, JSON-shape loss, the field allowlist, the re-attached attributes, the guards, `TemporalRunContext`, the usage-loss and DBOS/Prefect caveat, the deterministic ids and `prepare` behaviour; §"Workspaces" (247–259); §"Harness Workspace Capabilities" (260–295) including the live-event split, delegation rules and "Command timeouts"; §"Capabilities at Runtime" (296–301); §"Large Payloads" (302–352) including external storage and the claim-check and blob-size fallbacks; §"Model Selection at Runtime" (749–821) and §"Toolsets at Runtime" (822–829); §"Activity Configuration" (830–894) including the four config keys, the `TypedDict` validation, heartbeats, "Per-tool activity config" and "Child workflows"; §"Activity Retries" (960–1015) for retry ownership, `ActivityError` versus model errors, application types, the default non-retryable list, `retry_after`; §"Observability with Logfire" (1016–1047); §"Known Issues" (1048–1067). Evidence class: **Reported** — vendor reference page naming no version; nothing was installed or executed.
