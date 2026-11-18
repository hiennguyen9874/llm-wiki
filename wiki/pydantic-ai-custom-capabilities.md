---
type: Concept
title: Pydantic AI custom capabilities
description: How to author a Pydantic AI capability by subclassing AbstractCapability — configuration methods versus lifecycle hooks, id and combine semantics, agent binding and per-run isolation, ordering constraints, durable operations, and the spec-publishing contract.
tags: [pydantic-ai, capabilities, agents]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:12:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-custom-capabilities
    resource: ../raw/capabilities/custom/index.md
    scope: ../raw/capabilities/custom/
    kind: documentation
    revision: sha256:8266876f368fff0ff3cccd0d01daa125794d6d17a79ba31ecaeb85278603fe84
    title: "Building Custom Capabilities"
  - id: pydantic-docs-tool-search-capability
    resource: ../raw/capabilities/tool-search/index.md
    scope: ../raw/capabilities/tool-search/
    kind: documentation
    revision: sha256:d7e51e0a242bd9c822cd13fd2f6eb207b5cedc8f5f3ce03e1cab958b55c0fe42
    title: "Tool Search"
---

A custom capability is a subclass of [`AbstractCapability`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.AbstractCapability) that overrides whichever of two method categories it needs: **configuration methods**, called at agent construction and re-run at run setup on a replacement instance when `for_run` returns one, and **lifecycle hooks**, which fire during each run[^pydantic-docs-custom-capabilities] The authoring surface this page records is the subclass's half of the [capability primitive](pydantic-ai-capability-primitive.md); the hook families themselves, their decorator names and their retry and persistence semantics belong to [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), which is the same machinery seen from the `Hooks` side. Three of the configuration slots get their own pages, because each answers a question an author arrives with separately: which model serves a request ([capability model control](pydantic-ai-capability-model-control.md)) and how content the capability inserts mid-conversation is declared and attributed ([capability parts and authority](pydantic-ai-capability-parts-and-authority.md)).

## Class shape and metadata

A custom capability may be a plain class or a dataclass; the dataclass form generates constructor parameters for your own configuration fields and for the shared metadata fields[^pydantic-docs-custom-capabilities] If you write a custom `__init__` instead, set only the metadata you want to expose — there is no `super().__init__()` or `__post_init__()` requirement, and the vendor's sample assigns `id`, `description`, `defer_loading` and its own field directly:

```python
class MyCapability(AbstractCapability):
    def __init__(self, label: str, *, id: str | None = None,
                 description: str | None = None, defer_loading: bool = False) -> None:
        self.id = id
        self.description = description
        self.defer_loading = defer_loading
        self.label = label
```

The three shared attributes are `id`, `description` and `defer_loading`. They are optional declarations for always-on capabilities: an omitted `id` is derived from the class name and disambiguated run-locally when two instances collide. A deferred capability — `defer_loading=True` — must carry a stable explicit `id`, because history replay keys the catalog entry by it and Pydantic AI rejects a deferred capability without one[^pydantic-docs-custom-capabilities]

`AbstractCapability` is generic in the agent's dependency type, so `AbstractCapability[MyDeps]` types every hook's `RunContext[MyDeps]` while `AbstractCapability[Any]` works with any deps[^pydantic-docs-custom-capabilities]

## Identity, merging and combining

A capability that covers one fixed concern declares a stable default `id` — `WebSearch` uses `'web_search'`, `Thinking` uses `'thinking'`, and [tool search](pydantic-ai-tool-search.md)'s `ToolSearch` uses `'tool_search'`[^pydantic-docs-tool-search-capability] — so [durable execution](pydantic-ai-durable-execution.md) can identify what it contributes without the author naming an instance[^pydantic-docs-custom-capabilities] Because that id is fixed, two of them can meet:

| Situation | Behaviour |
| --- | --- |
| Two instances on one agent | One configuration stated twice: merged field by field, a value only one states is kept, a value both state takes the later one — which is how two packaged capabilities each bring a `WebSearch` and the agent reaches both domain sets |
| Two identities (two accounts, two credentials) | A fixed default id is the wrong shape: derive the id from what distinguishes them, so two identities get two ids and two under one id are reported as a mistake |
| Composition that is more than a field merge | Override `combine` — a budget that should take the *smaller* of two values, say |
| A plain class with a fixed id and instance configuration | Must override `combine`: the default merge enumerates dataclass fields only, so repeated instances raise rather than silently dropping the configuration; a leading underscore does not change that, since what matters is whether the merge can enumerate the attribute |
| State derived from fields | Declare it a `cached_property`. Merging discards the cached value so the next read recomputes against the merged fields; merging deliberately does not re-run `__post_init__`. State that has to be a field is recomputed in your own `combine` |

`MCP` derives its id from the server host and last path segment, which is why two MCP servers differing only in port or in an earlier path segment still need distinct explicit ids[^pydantic-docs-custom-capabilities]

A **capability supplied for a run** overrides its agent-level namesake outright: `agent.run(capabilities=[Thinking(effort='high')])` replaces the agent's `Thinking` rather than merging with it, because a run states what this run does and merging would let an agent-level allow-list widen a restriction the run was passed to impose[^pydantic-docs-custom-capabilities] `combine` is not consulted across layers, unrelated classes cannot share an id across layers, and a transparent wrapper that retains its wrapped capability's id — `prefix_tools()` — can replace that capability across layers, though different wrapper classes still cannot merge within one layer. To keep two rather than resolve them, pass a distinct `id` to each or `id=None` to opt back into the derived, disambiguated ids; an id passed to a capability that declares no default is a name you chose, so passing it twice is reported as a collision rather than merged. One limit survives all of these escapes: for a capability that contributes a [native tool](pydantic-ai-native-or-local-capabilities.md), two differently configured duplicates such as `WebSearch` still raise the native-tool-id conflict, and only identical configurations avoid it[^pydantic-docs-custom-capabilities]

## The configuration methods

| Method | Returns | Purpose |
| --- | --- | --- |
| `get_toolset()` | `AgentToolset \| None` | A pre-built toolset, or a callable receiving `RunContext` that returns one per run |
| `get_native_tools()` | `Sequence[AgentNativeTool]` | Provider-native tools, including callables receiving `RunContext` |
| `get_wrapper_toolset()` | `AbstractToolset \| None` | Wraps the agent's whole assembled toolset; always called per run |
| `get_wrapper_model()` | `Model \| None` | Wraps the model serving an attempt; called per attempt |
| `get_instructions()` | `AgentInstructions \| None` | Static instructions, or a callable for dynamic ones |
| `get_model_settings()` | `AgentModelSettings \| None` | Settings, or a callable resolved per step |
| `get_workspace()` | `WorkspaceBackend \| None` | Supplies the run's environment |
| `get_model()` | `AgentModel \| None` | Selects the model |
| `resolve_model_id()` | `Model \| None` | Builds a model from an application-specific string |
| `get_default_run_id()`, `get_default_conversation_id()` | `str \| None` | Durable identity |
| `get_run_clock()`, `get_run_start_time()` | `Callable[[], datetime] \| None`, `datetime \| None` | Durable deadline |

The last four exist for durable-execution engines, whose runs replay and must get the same identity and deadline each time; when several capabilities return a value, the one listed last wins[^pydantic-docs-custom-capabilities]

`get_wrapper_toolset` receives the combined **non-output** toolset, after the `prepare_tools` hook has wrapped it; output tools are added separately and are unaffected[^pydantic-docs-custom-capabilities] Instructions returned by `get_instructions` are read once at construction, so a callable is how a capability varies them; when the capability has an `id`, its instructions reach the model as instruction parts keyed `'capability:<id>'`, and `@capability.instructions(name=...)` keys one as `'capability:<id>:<name>'` — a capability without an id has no key for either. Changing instruction text mid-conversation should append rather than rewrite, which is what `InstructionPart(..., on_change='append')` states and what keeps the cached prefix reusable; the text must come from state you control[^pydantic-docs-custom-capabilities]

## Binding to an agent

`for_agent()` runs once during `Agent` construction, after the agent's own model, name and toolsets exist and before capability contributions are extracted[^pydantic-docs-custom-capabilities] It is synchronous because it binds configuration before run dependencies or a lifecycle context exist, so it must stay I/O-free. It receives an `AbstractAgent` — the portable agent interface — so a reusable capability stays compatible with custom agent implementations. Three rules follow:

- Return a **new bound copy** rather than mutating the original when the same capability may be attached to several agents.
- `CombinedCapability` and `WrapperCapability` propagate binding to their children, and the bound copy participates in every configuration hook including `get_model()` and `resolve_model_id()`.
- Runs through a `WrapperAgent` are delegated to the wrapped agent, so the built-in wrappers do not rebind a capability to the outer wrapper.

The hook sees the constructor model exactly as the caller wrote it: a model ID stays a string while binding runs, so a bound capability can install `resolve_model_id()` without default inference first constructing a provider with the wrong credentials. Capabilities passed to `run()` or through a run spec are bound once for that run before bootstrap model selection; a `CapabilityFunc` is bound before the run and its returned value again before that value's own `for_run()`, while a run-bound replacement returned by an ordinary capability's `for_run()` is not passed through `for_agent()` a second time[^pydantic-docs-custom-capabilities]

## Per-run state isolation

After binding, the capability instance is shared across all runs of an agent, so mutable state accumulates unless `for_run()` returns a fresh instance[^pydantic-docs-custom-capabilities] The replacement is not just a container for state — configuration is re-extracted from it at run setup: `get_instructions`, `get_toolset`, `get_native_tools` and `get_model_settings` are re-invoked on it, `get_wrapper_toolset`, `get_description` and every lifecycle hook run on it, and a model or workspace selected before the run is reused unless the replacement changes the model contribution. The exceptions are `get_model()`, bootstrap `resolve_model_id()` and `get_workspace()`, which run *before* `for_run` on the original instance, which is why a `for_run` implementation can already read `ctx.workspace`; it cannot change the workspace, and a run that needs a different one passes `workspace=`.

Never mutate `self` inside `for_run()`. When `for_run()` returns the original unchanged the configuration cached at construction is reused, so mutations would not be picked up[^pydantic-docs-custom-capabilities]

## The lifecycle order

Binding establishes which capability participates; lifecycle hooks intercept the work it does. The documented order is `for_agent()` → bootstrap model selection and resolution → `get_workspace()` → `for_run()` → per-step selection and preparation → model request → tool and output processing → run completion[^pydantic-docs-custom-capabilities] The per-phase availability differs in a way an author has to plan around: agent binding sees the agent name, raw constructor model and toolsets but no dependencies; bootstrap sees dependencies, history, usage and the lower-precedence model but `get_workspace()` gets a `RunContext` with the bootstrap model and no tools; `for_run()` gets a complete `RunContext`; each model step has the selected model installed in `RunContext` before its settings, profile-sensitive tools and model-specific message preparation are evaluated; and `wrap_run` closes the run body, `on_run_error` gets its recovery chance, then `after_run` runs[^pydantic-docs-custom-capabilities]

## Dynamic capabilities

A factory function taking `RunContext` and returning a capability or `None` may be passed to the `capabilities` argument of `Agent` or `agent.run()`, sync or async[^pydantic-docs-custom-capabilities] It is called once per run and the returned capability replaces it for the rest of the run, so its instructions, model settings, toolsets, native tools and hooks all flow through the normal path — the documented use is a capability chosen from the run's dependencies, such as a per-user skill row. A factory that needs to return several capabilities wraps them in `CombinedCapability`.

## Composition and ordering

Several capabilities compose into one `CombinedCapability` under middleware semantics: configuration is merged (instructions concatenate, model settings merge additively with later capabilities overriding earlier, toolsets combine, native tools collect), `before_*` hooks fire in list order, `after_*` and `on_*_error` in reverse order, and `wrap_*` hooks nest with the first capability outermost[^pydantic-docs-custom-capabilities] The families do not interleave:

```
cap1.wrap enter → cap2.wrap enter → cap3.wrap enter
  → cap1.before → cap2.before → cap3.before
  → core / on_error
  → cap3.after → cap2.after → cap1.after
→ cap3.wrap exit → cap2.wrap exit → cap1.wrap exit
```

A consequence the page states outright is that even `cap3.wrap` runs before `cap1.before` — a wrapper cannot assume any `before_*` hook has run yet[^pydantic-docs-custom-capabilities] `get_wrapper_toolset` and `get_wrapper_model` nest the same way.

When a capability needs a position regardless of where the user lists it, `get_ordering()` returns a `CapabilityOrdering`[^pydantic-docs-custom-capabilities]:

| Constraint | Meaning |
| --- | --- |
| `position` | `'outermost'` or `'innermost'`: a tier before (or after) every capability without one; several may share a tier and list order breaks ties inside it |
| `wraps` | Capabilities this one is outside of, matched by type (`issubclass`) or by instance identity |
| `wrapped_by` | The inverse of `wraps` |
| `requires` | Capability types that must be present; a missing one raises `UserError` and implies no ordering |

`CombinedCapability` topologically sorts its children at construction time, preserving the user's order as a tiebreaker, and `Hooks` accepts the same constraints through its `ordering=` parameter so ordering can be declared without a subclass[^pydantic-docs-custom-capabilities]

## Sharing state between capabilities

Capabilities have no direct access to each other[^pydantic-docs-custom-capabilities] To announce that something happened, publish a [capability event](pydantic-ai-capability-events.md) with `ctx.emit()` and let interested capabilities react with `@on_event` — no shared object and no ordering requirement. To share a *value*, use a `contextvars.ContextVar` set from an async function: one capability sets it in `wrap_run` or `before_run` and another reads it from its hooks. Within a `before_*` family, list the writer before the reader; because every wrapper is entered before any `before_*` hook runs, a value a wrapper sets before calling its handler is visible to all `before_*` hooks, while a wrapper can only read what `before_*` hooks set after its handler returns. A synchronous `Hooks` function cannot be the writer, because it runs on a separate thread. Under `run_stream()`, values set by an async `before_model_request` hook are available to later tool, output and run hooks, but values set later in that model request may not be — mutable dependencies are the route for state that must last the whole run.

## Where a capability's own I/O runs

A capability can move its own I/O or other non-deterministic work into a durable activity, step or task with `durable_operation`[^pydantic-docs-custom-capabilities] The capability needs a stable `id`, because engines recover persisted work by capability id plus operation name, and each operation method is marked `@durable_operation(name='...')` — the name becomes part of persisted unit names and must stay stable, while the Python method may be renamed freely. Without a durability capability the same call awaits the method directly.

| Condition | Where the operation runs |
| --- | --- |
| Durability capability bound, called from a hook or from `for_run`'s instance | Through the engine, dispatched by capability id and operation name |
| Called inside `for_run()` itself | Directly: dispatch is established only after `for_run()` returned |
| Called from a capability tool the engine already runs as its own unit (Temporal, Prefect, AWS Lambda) | Directly inside that unit, under its timeout, retry and cache configuration |
| Called from a capability tool that runs in workflow code (function tools under DBOS) | As its own durable unit |

A `for_run()` replacement must keep the capability's id; Pydantic AI raises `UserError` at the start of the run if a bound capability's id is no longer present[^pydantic-docs-custom-capabilities] A `prepare_model_request`, `after_model_request` or `on_model_request_error` hook that runs as a durable operation can still raise `RetryModelRequest`, but the target model has to be named by string, because a model instance cannot cross the durable boundary. Arguments and results follow the durable-tool serialization rules — Temporal's data converter, JSON-compatible values for a JSON-journal engine — and operation names are scoped by capability id, so changing either identity creates a different persisted operation (and on Prefect a different cache key). Temporal and DBOS match a recorded operation by its position in workflow history while Prefect identifies a recorded task by its arguments, so an operation whose arguments are measured in flow code — a duration, a timestamp, a random value — runs again on a flow retry; measure the changing value inside the operation instead.

The live-value hooks cannot be decorated at all: `get_toolset`, `get_wrapper_toolset`, `get_wrapper_model`, `wrap_run`, `wrap_node_run`, `wrap_model_request`, `wrap_tool_validate`, `wrap_tool_execute`, `wrap_output_validate`, `wrap_output_process` and `wrap_run_event_stream`, because their handlers or values cannot cross a durable boundary; Pydantic AI raises `UserError` naming the incompatible hook during agent construction[^pydantic-docs-custom-capabilities] To branch on the environment instead, read `ctx.in_durable_context`: `True` inside a durable workflow or flow when the agent has a durability capability (and inside a Prefect task, which inherits its flow's context), `False` outside durable execution and inside the Temporal activities and DBOS steps where tools and model requests run.

## Publishing for a spec

A custom capability becomes usable in an [agent spec](pydantic-ai-agent-specs.md) when it has a `get_serialization_name` — the class name by default — and a constructor accepting serializable arguments[^pydantic-docs-custom-capabilities] The default `from_spec` calls `cls(*args, **kwargs)`, so a simple dataclass needs no override; override it when the constructor takes types YAML or JSON cannot express, and let the spec fields mirror the dataclass fields with serializable types. Users register the type through `custom_capability_types` on `Agent.from_spec` or `Agent.from_file`.

## Testing

Custom capabilities are tested the way agents are: build an agent with the capability under `TestModel` or `FunctionModel` and assert on the run result, the messages, or any observable side effect of the hooks[^pydantic-docs-custom-capabilities] The page's two worked shapes are a guardrail that rewrites a `ModelResponse` in `after_model_request` to redact PII, and logging middleware that brackets `wrap_model_request` and `wrap_tool_execute` to see each operation's input and output.

## Limits

- The capture names **no Pydantic AI version, publication date, author or licence**, so every API name and default here is version-unknown and the page is `draft` under the `pydantic-ai` domain rule[^pydantic-docs-custom-capabilities] The indirect anchor is that the wrapper semantics and the `wrap_*`-encloses-the-stage lifecycle match what [the v2 release](pydantic-ai-v2-release.md) records for v2.54.0, though the source never says so.
- The configuration-method table and hook signatures are prose rather than reference text; the `AgentToolset`, `AgentModel` and `AgentInstructions` unions, the `Handler` protocols, the `get_description` contract and the exact `UserError`/collision messages are named where an example touches them and not enumerated.
- Its samples pin `openai:gpt-6.1-sol`, `openai:gpt-6-luna` and `user:openai:gpt-6.1-sol`, aliases no other capture in this wiki corroborates; the "current date" sample prints January 2032 and is illustrative only.
- Unstated: how a `combine`-declared error surfaces to the caller versus at construction, whether capability ordering constraints are validated for cycles, what `in_durable_context` reports inside a capability tool on an engine not named here, and the cost of per-attempt wrapping on a hot retry path.
- Nothing was installed, subclassed, bound, run, replayed or published to a spec, so every claim is **Reported** and none **Observed** or **Reproduced**. One reading is **Synthesis**: since `for_run` re-extraction covers `get_instructions` but not `get_description`'s configuration, a per-run description change is the one configuration slot this page leaves unclear — the source lists `get_description` among methods that "always run on" the replacement without saying whether its return value is re-cached.

## Relationships

- **Extends** the [capability primitive](pydantic-ai-capability-primitive.md): the primitive names what a capability bundles; this page is the subclass contract for building one.
- **Is the subclass half of** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md), which records the hook families, their registration routes, retry budgets and error recovery — the same stages this page's lifecycle order sequences.
- **Depends on** [capability parts and authority](pydantic-ai-capability-parts-and-authority.md) for the one behaviour that is not a method: how content a capability inserts mid-conversation is declared, framed and attributed.
- **Pair with** [capability model control](pydantic-ai-capability-model-control.md), which owns `get_model()`, `resolve_model_id()` and `get_wrapper_model()`.
- **Supplies identity to** [durable execution](pydantic-ai-durable-execution.md): `@durable_operation` dispatches by capability id plus operation name, and the last-wins run identity and clock slots feed the same engines.
- **Is catalogued by** the [capability catalog](pydantic-ai-capability-catalog.md) and **deferred by** [on-demand capabilities](pydantic-ai-on-demand-capabilities.md), which is where the stable-`id` requirement comes from.
- **Coordinates through** [capability events](pydantic-ai-capability-events.md) rather than direct access to another capability.
- **Is published to** [agent specs](pydantic-ai-agent-specs.md) through `get_serialization_name`, `from_spec` and `custom_capability_types`.
- **Constrains** [prompt caching](pydantic-ai-prompt-caching.md) indirectly: appended instruction changes and the frozen rendering of inserted parts are what keep a capability's contribution out of the cached prefix's way.

[^pydantic-docs-custom-capabilities]: Pydantic Docs, "Building Custom Capabilities" (https://pydantic.dev/docs/ai/capabilities/custom/; 13,581 words as declared, 13,832 by local `wc -w`; language `en`; no publication date, author, licence or Pydantic AI version), §intro (raw lines 10–94) for the two method categories, the per-run re-extraction rule, the always-per-run `get_wrapper_toolset` and per-attempt `get_wrapper_model`, the plain-class/dataclass/custom-`__init__` shapes, the optional `id`/`description`/`defer_loading` metadata, derived run-local ids, and the full identity/merge/`combine`/`cached_property`/native-tool-id rules including the run-supplied-overrides-agent-level layer rule; §"Typing dependencies" (96–142) for `AbstractCapability[Deps]`; §"Providing tools" and "Toolset wrapping" (143–228) for `get_toolset`'s instance-or-callable form, `get_native_tools`, and `get_wrapper_toolset` receiving the post-`prepare_tools` non-output toolset; §"Providing instructions" and "Instructions that change during a conversation" (229–321) for the called-once/return-a-callable rule, the `capability:<id>` and `capability:<id>:<name>` instruction keys, and `on_change='append'`; §"Providing model settings" (526–559) for the per-step callable and the `ctx.model_settings` merge; §"Configuration methods reference" (721–740) for the thirteen-row table, the durable-engine purpose of the last four and last-listed-wins; §"Binding to an agent" (741–781) for `for_agent` timing, the `AbstractAgent` parameter, the new-bound-copy rule, propagation through `CombinedCapability`/`WrapperCapability`, `WrapperAgent` delegation, the string-stays-a-string guarantee, and the binding rules for run and factory capabilities; §"Capability lifecycle" (782–798) for the phase order and per-phase availability; §"Durable capability operations" (1247–1289) for `@durable_operation`, id stability, the dispatch-timing and engine-unit table, the string-model `RetryModelRequest`, serialization, the Prefect argument-identity rule, the eleven undecoratable hooks and `ctx.in_durable_context`; §"Wrapping capabilities" (1290–1315) for `WrapperCapability`; §"Per-run state isolation" (1316–1357) for the shared-instance hazard, the re-extraction list, the model/workspace exceptions and the never-mutate-`self` rule; §"Dynamically building a capability" (1358–1405) for the sync-or-async factory, once-per-run replacement and `CombinedCapability`; §"Composition and middleware semantics" (1406–1427) for configuration merging, the hook-family order, and the non-interleaving consequence; §"Ordering" (1428–1484) for `CapabilityOrdering`'s four constraints, the topological sort and `Hooks(ordering=)`; §"Sharing state between capabilities" (1485–1492) for events versus `ContextVar`, the wrapper-visibility rule, the sync-thread exclusion and the `run_stream()` caveat; §"Testing custom capabilities" (1493–1496) and §"Examples" (1497–1602) for `TestModel`/`FunctionModel` testing, the PII-redaction guardrail and the logging middleware; §"Publishing capabilities" (1603–1671) for `get_serialization_name`, the default `from_spec`, the override case and `custom_capability_types`. Local capture: `raw/capabilities/custom/index.md`, content digest sha256:8266876f. Evidence class: **Reported** — vendor documentation naming no release version; nothing was installed, constructed, bound, executed or replayed.

[^pydantic-docs-tool-search-capability]: Pydantic Docs, "Tool Search" (<https://pydantic.dev/docs/ai/capabilities/tool-search/>; 213 words as declared, 252 by local `wc -w`; no publication date, author or Pydantic AI version); local capture `raw/capabilities/tool-search/index.md`, content digest sha256:d7e51e0a. Line 13 only, for `ToolSearch`'s declared default `id` of `'tool_search'` and the resulting merge-instead-of-collision behaviour; the rest of that capture duplicates the tools-advanced material compiled in [tool search](pydantic-ai-tool-search.md). Evidence class: **Reported** — vendor documentation naming no version or date; no capability was constructed.
