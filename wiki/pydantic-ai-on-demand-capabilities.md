---
type: Concept
title: Pydantic AI on-demand capabilities
description: How defer_loading turns a Pydantic AI capability into a one-line catalog entry — the load exchange and the history records it leaves, bundle-wide activation, what survives a resume, the cache prefix each kind of reveal costs, and how code loads a capability without the model.
tags: [pydantic-ai, agents, capabilities, context-management]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T10:58:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-on-demand-docs
    resource: ../raw/capabilities/on-demand/index.md
    scope: ../raw/capabilities/on-demand/
    kind: documentation
    revision: sha256:0c2c764eb34c1d2c16548b28683279c36f0dc51cd2f0cd918aba6a401f0ecf0c
    title: "On-Demand Capabilities"
---

An on-demand capability — the docs also say *deferred capability* — is a [capability](pydantic-ai-capability-primitive.md) marked `defer_loading=True` with a stable `id`: instead of sending its instructions and tool schemas on every request, the model sees one catalog line (`id` plus an optional `description`) and pulls the bundle in only when it calls the framework-provided `load_capability` tool[^pydantic-on-demand-docs] The vendor motivates it with cost and tool-selection pressure rather than a new loop: a multi-workflow agent otherwise pays every workflow's instructions and tool schemas on every turn, and model tool selection degrades once the visible set passes roughly 30–50 tools[^pydantic-on-demand-docs] Deferred capabilities are explicitly *not* [deferred tools](pydantic-ai-deferred-approvals.md), which pause individual calls for approval or external execution[^pydantic-on-demand-docs]

The minimal shape is a `Capability` with an `id`, a `description`, `instructions` and `defer_loading=True`, with tools attached by `@refunds.tool_plain` or `@refunds.tool`[^pydantic-on-demand-docs]:

```python
refunds = Capability(
    id='refunds',
    description='Use for refund eligibility, refund status, or processing a refund.',
    instructions='Always confirm the order ID before issuing a refund.',
    defer_loading=True,
)

@refunds.tool_plain
def refund_status(order_id: str) -> str:
    """Look up the refund status for an order."""
    return f'Order {order_id}: refund issued on 2026-05-01.'
```

## The catalog and the load exchange

On the first turn the model receives its base instructions, the `load_capability` tool, and a tagged catalog entry[^pydantic-on-demand-docs]:

```
<pyai:context id="capability:deferred_capabilities">
The following capabilities are deferred and can be loaded using the `load_capability` tool. A capability's tools stay hidden until it is loaded:
- refunds: Use for refund eligibility, refund status, or processing a refund.
</pyai:context>
```

The tag is what lets a changed catalog be appended to the conversation rather than rewriting the cached prompt; a later element with the same `id` replaces the earlier one[^pydantic-on-demand-docs] The load then unfolds across model requests inside one run[^pydantic-on-demand-docs]:

1. The model calls `load_capability` with `id='refunds'`.
2. The tool result only *confirms* the load. Pydantic AI states the capability's instructions immediately after it in a system message and exposes `refund_status` on the next request.
3. The model sees the instructions in history and the tool in its list, calls it, and answers from the result.

Already-loaded capabilities stay loaded for the rest of the run. A `load_capability` call for an active capability returns a success result confirming it is already active and does not restate its instructions; a call for one an earlier call in the same response already loaded gets a retry prompt; an id that is not an on-demand capability gets a retry prompt listing the ids the model may load[^pydantic-on-demand-docs]

Instruction changes after a load are appended, not rewritten: a dynamic `@capability.instructions` function that returns something new, or instructions edited in code between runs of a conversation, appends an update for the block `capability:refunds` — the complete instructions, or a diff against the text the model last received when that is shorter[^pydantic-on-demand-docs] The earlier statement stays in history, so the cached prompt survives. A capability whose instructions become empty, or that the agent no longer has, is withdrawn the same way, and a `before_model_request` hook that leaves a loaded capability's parts out of `instruction_parts` does not affect it, because loaded instructions are delivered as they resolved[^pydantic-on-demand-docs] To withdraw the block, keep its parts with empty content; tracking applies whatever the instructions' `on_change` policy, since a loaded capability's instructions are never in the prefix[^pydantic-on-demand-docs] An instructions function that returns something different on every request — the current time, say — appends an update to every request[^pydantic-on-demand-docs]

## What activates together

Loading is bundle-level disclosure, not an instructions-only fetch: every part of the capability comes live as one unit[^pydantic-on-demand-docs]

| Part | Before load | After load |
| --- | --- | --- |
| Instructions (static or dynamic) | Not sent | Stated in a system message after the tool result, then in subsequent requests |
| Function tools | Not exposed | Exposed on the next request |
| Model settings (static or per-step) | Not applied | Merged into the run's settings for subsequent requests |
| Lifecycle hooks | Do not fire | Fire after the capability loads |
| Native tools | Not exposed | Exposed on the next request |

The docs' worked example is a support agent with two deferred workflows: `orders` (instructions plus a function tool via `Capability`) and `account-security` (instructions, a destructive tool, `reasoning_effort: 'high'` and an approval hook via `AbstractCapability`)[^pydantic-on-demand-docs] Loading `account-security` activates all four together, and from then on every tool call in the run passes the approval hook and runs under the raised effort, while a request that never touched that workflow saw none of it[^pydantic-on-demand-docs] Per-tool `defer_loading` is a no-op on a deferred capability — the capability gates its tools as a unit — and only means something on a non-deferred `Capability`, where it opts an individual tool into [tool search](pydantic-ai-capability-primitive.md)[^pydantic-on-demand-docs]

## When to defer, and what it is not

The vendor's criteria are narrow[^pydantic-on-demand-docs]:

- **Reach for it** when the agent serves several distinct workflows where most turns need one; when a workflow needs more than instructions — its own tools, raised reasoning effort, an approval hook — and those should travel together; or when skills-style progressive disclosure should also bring tools and settings.
- **Skip it** when the capability is used on most turns, because the discovery round-trip costs more than the tokens it saves, or when the catalog is a flat set of individually discoverable tools with no shared instructions — that is tool search's job, which finds tools by name rather than loading bundles.

A capability-owned tool is never searchable: it stays hidden until its capability loads, and no search query can surface it[^pydantic-on-demand-docs] When a run also has searchable deferred tools the catalog steers the model to load the capability rather than search for its tools, and in a capability-only run the catalog omits any mention of searching[^pydantic-on-demand-docs] The docs position the feature against Anthropic's Agent Skills: the same "pull in a Markdown skill on demand" idea, generalised to carry typed function tools, per-step model settings and lifecycle hooks[^pydantic-on-demand-docs]

## Retrofitting and grouping

`defer_loading`, `id` and `description` are not specific to the `Capability` convenience class: they live on `AbstractCapability`, and built-in capabilities expose them at construction[^pydantic-on-demand-docs] So an existing MCP capability can be deferred with `MCP(url=..., native=True, id='analytics-mcp', description=..., defer_loading=True)`, and the same flag works on `WebSearch`, `WebFetch`, `Hooks` and any custom `AbstractCapability` subclass[^pydantic-on-demand-docs]

Several capabilities can be loaded as one by wrapping them in a `CombinedCapability` with its own `id`[^pydantic-on-demand-docs]:

```python
web_research = CombinedCapability(
    [WebSearch(), WebFetch()],
    id='web-research',
    description='Use when the question requires up-to-date information from the web.',
    defer_loading=True,
)
```

Loading `web-research` activates both members' tools, instructions and hooks; each member keeps its own ordering position among the agent's capabilities, as if passed directly, and a member cannot be deferred on its own — pass it separately if the model should load it independently[^pydantic-on-demand-docs]

## State lives in history, not the agent

Loaded-capability and tool-availability state are recorded in message history, so a persisted conversation resumed on another process, machine or model reconstructs the loaded ids and the revealed tool names; capabilities the model loaded stay loaded and the rest stay collapsed, with no second discovery round-trip[^pydantic-on-demand-docs] A model load's record is its `load_capability` exchange; a load from code, which has no exchange, records a `CapabilityLoadDeltaPart`, and revealed tools are recorded in a `ToolAvailabilityDeltaPart`[^pydantic-on-demand-docs]

This is why a deferred capability needs a **stable explicit `id`**: replay matches calls to capabilities by id, so a class-derived id would break silently when the class is renamed[^pydantic-on-demand-docs] The same property gives cross-provider replay — a run that loaded `refunds` on Anthropic and continued on OpenAI Responses keeps it loaded[^pydantic-on-demand-docs] History carries *which* ids were loaded, not the capabilities: the resuming agent must be constructed with the same capabilities and ids, just as with tools — state in history, definitions in code[^pydantic-on-demand-docs]

## What tools and hooks can observe

Progressive-disclosure state is exposed on `RunContext`[^pydantic-on-demand-docs]:

| Field | Meaning |
| --- | --- |
| `ctx.loaded_capability_ids` | Capability IDs explicitly loaded by the model or by `ctx.load_capability()`, rebuilt from history before each model request |
| `ctx.active_capability_ids` | Always-on capability IDs plus `ctx.loaded_capability_ids` |
| `ctx.capability_active` | Whether the capability owning the running hook or callback is active — scoped to that capability, and `True` for an always-on one that was never loaded |
| `ctx.discovered_tool_names` | Deferred function tools revealed through tool search, `ToolReturn.tools`, or a capability load |
| `ctx.available_tool_names` | Function tools currently known as available: the step's assembled tool manager plus history-revealed names |
| `ctx.is_tool_available(tool)` | Whether a function tool is visible; pass the `ToolDefinition` you hold from a wrapping toolset, or a name from `ctx.tools` from a request hook or tool execution |
| `ctx.usage_limits` | The `UsageLimits` the run is enforcing (defaults to `UsageLimits()`, `None` only outside a run), beside `ctx.usage` — read-only, because it is the live object enforcing the budget |

A load takes effect on the model request that follows it: the next request for a model or tool load, the run's first request for a `before_run` load, and the request being prepared for a `before_model_request` load[^pydantic-on-demand-docs] A capability loaded during a step appears in `ctx.loaded_capability_ids` from the next step, which is also the first step whose model sees its instructions and tools; one loaded from `before_run` or `before_model_request` appears once that step's hooks have run, so the step's tool calls and `after_model_request` see it[^pydantic-on-demand-docs] Early hooks such as `before_run` may see only history-derived tool names, or none, before tool definitions are prepared[^pydantic-on-demand-docs]

## Per-provider wire behavior and the cache bill

On-demand capabilities work on every model, and where the provider can express an availability change natively the prompt prefix survives the load[^pydantic-on-demand-docs] A capability-owned tool stays off the wire while a search surface is present, which keeps search native, and each provider reveals it differently[^pydantic-on-demand-docs]

| Provider case | Wire representation |
| --- | --- |
| Anthropic `tool_addition_mode='by_reference'` | The revealed name in a `tool_addition` block; a capability-only run pre-advertises the definition with `defer_loading=True`, a mixed run appends the definition in the same request as the reveal |
| OpenAI Responses `tool_addition_mode='with_definitions'` | The full definition in an appended `additional_tools` input item, left out of `tools` |
| No native reveal item (`tool_addition_mode=None`) | Announces `The following tool(s) are now available: {names}` when the schema is visible; a remote MCP server's own tool names are still sent but not named if they carry a framing tag such as `</system>`; synthesizes a `search_tools` exchange only when a withheld schema must be revealed |
| Decision models | Cannot fill a free-form `id`, so each capability becomes a route described by its `description`, and the catalog is left out of the question framing; ids travel on `ModelRequestParameters.deferred_capabilities` |

Adding a standalone `defer_loading=True` *tool* to the same run brings tool search back, because that tool genuinely is searchable[^pydantic-on-demand-docs]

What was revealed decides the cache cost[^pydantic-on-demand-docs]:

| What loads | Cache prefix |
| --- | --- |
| Instructions only | **Stable** — instructions land in message history, and later changes are appended there too |
| Function tools with native reveal support (`by_reference` or `with_definitions`) | **Stable on Anthropic and OpenAI Responses** |
| Function tools without native reveal support (for example OpenAI Chat Completions) | **Breaks once per load** — the tools join `tools[]`, ahead of messages already sent, then holds |
| Native tools | **Always breaks the prefix on load**, on every provider |
| Function tools that appear without a load (dynamic toolset, MCP server adding one mid-run) | **Stable on first-party OpenAI Responses and on Anthropic models with tool search**, except that some Anthropic models add a one-time preamble when a run's first deferred tool is a newcomer |

Two caveats sit on the OpenAI Responses half: before GPT-5.6, a request whose `tool_choice` names a revealed tool declares it in `tools` and misses the cache, and with `openai_previous_response_id` or `openai_conversation_id` set the tool stays out of `tools` and the API rejects the request[^pydantic-on-demand-docs] Where the prefix matters, the vendor's advice is instruction-only or function-tool-only capabilities on a model that expresses availability changes natively[^pydantic-on-demand-docs]

## Loading from code

When the application knows first — a tool just classified the request, or the ticket names the workflow — call `ctx.load_capability(id_or_capability)` instead of waiting for the model[^pydantic-on-demand-docs] It is a plain method, not a coroutine, and works from a tool (sync or async) or a tool hook such as `after_tool_execute`, from `before_run` or `before_model_request`, and from `after_model_request` on a response with tool calls the run executes[^pydantic-on-demand-docs]

The behaviour is narrow and has consequences[^pydantic-on-demand-docs]:

- **It takes effect on the following model request** — the next request from a tool or tool hook, the run's first from `before_run`, and the request being prepared from `before_model_request`, except that a `before_model_request` load gives that request only its tools and instructions: its model settings, native tools and hooks apply from the next request.
- **It never causes a model request.** The load rides the run's next request, so if the step ends the run instead — an approval-needed or deferred call, or output — the load is discarded. Resuming does not re-run that tool, so after an approval, load from the tool that needed approval or from a tool hook such as `after_tool_execute`, which runs on resume. A load made by a tool attempt that then raises `ModelRetry` still counts.
- **It is recorded without a `load_capability` call** — a `CapabilityLoadDeltaPart` naming the capability and the loading tool call, followed by the `ToolAvailabilityDeltaPart` that reveals its tools. The model sees the instructions and tools, never the delta part. Loads before one request, including from parallel tool calls, each get their own record in order, and `ctx.enqueue()` content goes right after the tool result, ahead of the records.
- **It loads once.** The return is `True` when the load was queued and `False` when the capability is already active or already being loaded by an earlier call or by the model in the same response — in that last case the capability loads only if the model's call succeeds.

`ctx.load_capability()` raises `UserError` when the capability is not registered, when it is an unloaded non-deferred member of a deferred group (load the group), when no model request follows (for example `after_model_request` on a response without tool calls, or `after_node_run`/`after_run`), and when it is called from an output tool or output function, which ends the run[^pydantic-on-demand-docs] It is also unsupported in a realtime session, where it raises `UserError` and ends the session, while the model can still load an instructions-only on-demand capability there through `load_capability`[^pydantic-on-demand-docs]

Older versions without `CapabilityLoadDeltaPart` cannot load a history containing one, and any load ends at a compaction that removes its record; the Harness's compaction strategies re-record every removed load as a `CapabilityLoadDeltaPart` after the summary[^pydantic-on-demand-docs]

## Durable execution changes what may load

A durable engine that runs a tool in its own activity, step or task replays the recorded result instead of re-running the code, so a load made there would be lost; where Pydantic AI can detect it, `ctx.load_capability()` raises `UserError`[^pydantic-on-demand-docs] Temporal tools run in activities and Prefect tools in tasks, so neither can load; DBOS runs plain function tools in workflow code, so those can, while MCP-server and dynamic-toolset tools run in steps and cannot, and a load from a function you decorated `@DBOS.step` is undetectable — it succeeds and is lost on recovery[^pydantic-on-demand-docs] Capability hooks and tool hooks run in workflow or flow code on all three engines, so loading from `before_run`, `before_model_request`, `after_model_request` or `after_tool_execute` works there[^pydantic-on-demand-docs] The tool-hook route is the documented workaround when the tool itself cannot load, and the hook runs for every call including the model's own `load_capability` calls, so it must check `tool_def.name`[^pydantic-on-demand-docs] This is consistent with the per-engine notes in [Pydantic AI on Temporal](pydantic-ai-temporal.md) and [Pydantic AI on DBOS](pydantic-ai-dbos.md).

## Skills from Markdown and runbooks from a database

An Agent Skills Markdown file can be wrapped in a `Capability` with a few lines of glue: split the frontmatter, read `id` and `description` from it, pass the stripped body as `instructions`, and set `defer_loading=True`[^pydantic-on-demand-docs] Each file then appears in the catalog as its `id` plus `description`, and the body is sent only after a `load_capability` call[^pydantic-on-demand-docs] A skill that needs tools passes them to the same `Capability` through `toolsets=` or `tools=`, so they stay hidden until the skill loads and arrive on the next request as a `ToolAvailabilityDeltaPart`; the docs' scripted `FunctionModel` prints the per-request tool list as `['load_capability']`, then `['load_capability', 'stage_release']`, then the same again[^pydantic-on-demand-docs] Model settings or hooks on a skill still require subclassing `AbstractCapability`[^pydantic-on-demand-docs] The Harness `Skills` capability delivers instructions only; a skill that needs tools is defined this way instead, and both share one catalog and the `load_capability` tool[^pydantic-on-demand-docs]

Runbooks kept in a database follow the same shape with a dynamic instructions function: build one deferred `Capability` per row when the agent is created — so the catalog is identical on every run and stays in the cached prefix, and a new row appears when the agent is rebuilt — and read the body inside a `@capability.instructions` function that queries through `ctx.deps.db`[^pydantic-on-demand-docs] The body is read only after a load and again on each later request, so an edited runbook reaches the next run without a redeploy, and an edit after the model loaded it is appended to the conversation as an update[^pydantic-on-demand-docs] The trust boundary is explicit: a loaded body is stated in the system voice, so anyone who can write the table can instruct the model with the agent's authority, and write access should be limited to people allowed to edit the agent's instructions[^pydantic-on-demand-docs]

## Enforcing read-before-act

The loaded set being ordinary `RunContext` data makes a runbook gate cheap: register the runbook as a deferred capability, then bounce a tool call back with `ModelRetry` until `required in ctx.loaded_capability_ids`[^pydantic-on-demand-docs] The docs' `RunbookRequired` hook maps tool names to capability ids and raises `ModelRetry` with the exact `load_capability` call to make; `issue_refund` stays visible from turn 1, the refund only runs after `refund-policy` is loaded, and the same pattern generalises to warnings when a risky pair of workflows is open, audit hooks that tag traces with the loaded set, or an extra confirmation when two workflows are both active[^pydantic-on-demand-docs]

## Limits

- The source is a single vendor reference page naming **no Pydantic AI version, publication date, author or licence**, so the page is `draft` under the `pydantic-ai` domain rule and every API name is version-unknown[^pydantic-on-demand-docs]
- Its samples pin `openai-responses:gpt-6.1-sol`, `anthropic:claude-sonnet-5-5` and `openai:gpt-6.1-sol`-class aliases that appear in sibling captures but are not corroborated by an installed package here[^pydantic-on-demand-docs]
- `tool_addition_mode` is described per provider but its model profiles, the `local=` callable contracts, the exact retry-prompt text, and the per-provider feature tables are named rather than enumerated; the catalog element's text is captured as printed, not generated by a run[^pydantic-on-demand-docs]
- Nothing was installed, no agent constructed, no capability loaded, no cache measured, no durable workflow replayed and no realtime session opened, so every claim here is **Reported** and none is **Observed** or **Reproduced**.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for the bundle, its `id`/`description` fields and attachment to an agent.
- **Is qualified by** [prompt caching](pydantic-ai-prompt-caching.md): instructions are appended to history, native tools always move the prefix, and function tools depend on the provider's reveal mode.
- **Persists through** [conversation state](pydantic-ai-conversation-state.md) and plain message history: the loaded ids and revealed tools are rebuilt from recorded parts, not from the agent.
- **Delays** [lifecycle hooks](pydantic-ai-lifecycle-hooks.md) owned by a deferred capability, which do not fire until it loads.
- **Is worked around inside** [durable execution](pydantic-ai-durable-execution.md) and its engines: a load from an activity, task or step is refused or lost, while capability and tool hooks can still load.
- **Narrows** the blanket limitation in [realtime voice](pydantic-ai-realtime-voice.md) that deferred capabilities are rejected at connect: only a tool-contributing one is, and the model may still load an instructions-only capability there.
- **Extends** [MCP integration](pydantic-ai-mcp-integration.md): a deferred `MCP` capability keeps every server tool definition out of the prompt until the model loads it.
- **Excludes model selection from what a load brings**: [capability model control](pydantic-ai-capability-model-control.md) records that `get_model()` and `resolve_model_id()` are eager, so a deferred capability contributes neither even after it is loaded — a load can bring instructions, tools, settings, hooks and native tools, but not a model.
- **Is the bundle counterpart of** [tool search](pydantic-ai-tool-search.md), which finds individual tools by name instead of loading a capability; the vendor's selection rule is shared instructions and tools-together versus a flat searchable catalog. Tool search also owns the reveal mechanics this page's cache rows depend on — native search, `additional_tools`, `tool_addition`, and the local `search_tools` fallback that moves the tools array[^pydantic-docs-tools-advanced].

[^pydantic-on-demand-docs]: Pydantic Docs, "On-Demand Capabilities" (https://pydantic.dev/docs/ai/capabilities/on-demand/; 6,278 words as declared and 6,379 by local `wc -w`; language `en`; no publication date, author, licence or Pydantic AI version). Locators: §intro (raw lines 11–13) for the per-turn cost, the 30–50-tool pressure, `defer_loading=True` with a stable `id` and the deferred-tool distinction; lines 40–50 for the first-turn catalog and its `<pyai:context id="capability:deferred_capabilities">` element, the replacement rule and the change-append behaviour; lines 52–56 for the three-step request sequence; line 58 for appended instruction updates, the `capability:refunds` block, diff-versus-complete selection, withdrawal, the `instruction_parts` non-effect and the every-request dynamic case; line 60 for repeat loads, the same-response retry prompt and the unknown-id retry prompt; line 62 for the never-searchable capability tool and the catalog's search steering; line 64 for bundle-level activation; §"What you can defer" (68–78) for the five-row activation table; §"When to use it" (80–93) for the reach-for/skip criteria, the Agent Skills comparison and the tool-search alternative; §"Retrofitting an existing capability" (95–119) for the `AbstractCapability` fields, the deferred `MCP` sample and the `WebSearch`/`WebFetch`/`Hooks` reach; §"Deferring several capabilities as one" (121–141) for `CombinedCapability`, member ordering and the no-nested-deferral rule; §"Resumable across runs" (143–149) for history-held state, `ToolAvailabilityDeltaPart`, `CapabilityLoadDeltaPart`, the stable-id requirement and cross-provider replay; §"Runtime state in RunContext" (151–163) for the seven `ctx` fields and the load-timing rules; §"Cross-provider behavior" (165–176) for the four wire cases, the search-surface rule and `deferred_capabilities`; §"Cache implications" (178–194) for the five cache rows and the two OpenAI Responses caveats; §"The Capability convenience class" (196–223) for the decorators, `tools=`/`toolsets=`, dynamic instructions and the per-tool `defer_loading` no-op; §"Beyond instructions" (225–308) for the deferred model-settings, hook and native-tool samples; §"Putting it together" (310–382) for the two-workflow support agent and bundle-level disclosure; §"Enforcing read-before-act" (384–437) for the `RunbookRequired` hook and its generalisations; §"Loading a capability from code" (439–505) for the call sites, the three timing bullets, the once-only return, the `UserError` list, the realtime limitation and the compaction rule; §"Durable execution" (507–536) for the Temporal/Prefect/DBOS split and the tool-hook sample; §"Loading skills from Markdown files" (538–584) for the frontmatter glue and catalog behaviour; §"Hide a skill's tools until the skill is loaded" (586–654) for `toolsets=` and the printed per-request tool lists; §"Loading runbooks from a database" (656–726) for construction-time catalog building, read-on-load-and-each-request, the append-on-edit behaviour and the write-access trust warning. Evidence class: **Reported** — vendor documentation naming no release version; nothing was installed, constructed, loaded, replayed or measured.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Tool Search" (raw lines 836–919) for the three execution modes and their reveal surfaces, the append-only native search exchange and the local `search_tools` fallback; §"Stored history and portability" (968–985) for the distinction between a model-driven search and an application-driven `ToolAvailabilityDeltaPart`; §"Tool search and prompt caching" (986–993) for which reveal modes leave `tools[]` untouched and which keep a capability-only load free on every provider. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
