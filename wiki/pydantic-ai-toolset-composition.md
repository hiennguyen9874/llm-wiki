---
type: Concept
title: Pydantic AI toolset composition
description: The ten wrappers that turn a Pydantic AI toolset into a different one — combining, filtering, prefixing, renaming, rewriting definitions ahead of each step, gating calls on approval, deferring loading, adding return schemas and metadata, and subclassing WrapperToolset to change execution.
tags: [pydantic-ai, agents, tools, toolsets]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:04:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-toolsets
    resource: ../raw/tools-toolsets/toolsets/index.md
    scope: ../raw/tools-toolsets/toolsets/
    kind: documentation
    revision: sha256:376fcf77e23d854d7b3adfbd3c7ab51b845516590c4c146bd4a21e9c8ee55355
    title: "Toolsets"
---

**Reported, Pydantic AI version unspecified:** toolsets compose, in the narrow sense that each wrapper takes a toolset and returns a toolset, so the three jobs the page names — filtering which tools are available, modifying tool definitions, and changing tool execution behaviour — are done by stacking rather than by rewriting the toolset underneath[^pydantic-docs-toolsets] Most wrappers also exist as a method on `AbstractToolset` (`filtered()`, `prefixed()`, `renamed()`, `prepared()`, `approval_required()`, `defer_loading()`, `include_return_schemas()`, `with_metadata()`), which is what makes a chain readable; `CombinedToolset` and `WrapperToolset` are classes without a chaining method of their own[^pydantic-docs-toolsets] The catalog below is the whole set the source describes, with the constraint each one carries — several are explicit about what they cannot do, and those negatives are the part worth retrieving.

## The catalog

| Wrapper | Chained as | Changes | Constraint the page states |
| --- | --- | --- | --- |
| `CombinedToolset([...])` | — | Several toolsets become one | No constraint stated; name conflicts are what the renaming and prefixing wrappers address |
| `FilteredToolset` | `.filtered(fn)` | Which tools are visible, ahead of each step | The predicate sees `RunContext` and each `ToolDefinition` |
| `PrefixedToolset` | `.prefixed('weather')` | Every tool name gains a prefix | Long or confusing names are the cost it accepts |
| `RenamedToolset` | `.renamed({...})` | Specific tool names | Only the tools listed in the mapping |
| `PreparedToolset` | `.prepared(fn)` | The whole definition list, ahead of each step | Cannot add or rename a tool |
| `ApprovalRequiredToolset` | `.approval_required(fn)` | Which calls pause for approval | Runs land in `DeferredToolRequests` |
| `DeferredLoadingToolset` | `.defer_loading(names=None)` | Visibility until discovered by search | Needs tool search to be usable |
| `IncludeReturnSchemasToolset` | `.include_return_schemas()` | `include_return_schema=True` on every tool | Native field where supported, otherwise JSON in the description |
| `SetMetadataToolset` | `.with_metadata(k=v)` | Merges metadata onto every tool | Metadata only — no behaviour |
| `WrapperToolset` | — | Tool execution, by subclassing | Doing nothing is its default |

## Combining and naming

`CombinedToolset` takes a list of toolsets and lets them be used as one; the page's sample runs the combined result through `TestModel` and prints all four tool names from the two source toolsets[^pydantic-docs-toolsets] Names are the hazard it hands to the next two wrappers. `PrefixedToolset` prevents conflicts by adding a prefix to each tool name, and its own stated limitation is that a prefix can make a name unnecessarily long or confusing to the model[^pydantic-docs-toolsets] `RenamedToolset` is the finer tool for that case, renaming only the tools a dictionary lists — the documented motivation is a name that is ambiguous or collides with another toolset's, where prefixing would overcorrect[^pydantic-docs-toolsets] Prefixing also reaches further than a definition: the [MCP client](pydantic-ai-mcp-client.md) records that `allowed_tools` and durable-execution identity are untouched by a prefix while the visible name is not.

## Rewriting definitions ahead of each step

`PreparedToolset` takes a function of `RunContext` and the full list of `ToolDefinition`s and returns the definitions to expose for that step, so descriptions, schemas and which tools survive can change every step[^pydantic-docs-toolsets] The page's sample rewrites only descriptions, via `dataclasses.replace`, keeping everything else[^pydantic-docs-toolsets] Two boundaries are stated: it **cannot add or rename** tools — adding is `FunctionToolset.add_function()`'s job and renaming is `RenamedToolset`'s — and it is the toolset-scoped equivalent of the `prepare_tools` hook that sees an agent's whole assembled set[^pydantic-docs-toolsets] Per-tool `prepare` and the hook are compiled in [tool definitions](pydantic-ai-tool-definitions.md).

## Gating a call on approval

`ApprovalRequiredToolset` decides per **call**, not per tool: the predicate receives `RunContext`, the `ToolDefinition` and the validated arguments, and with no predicate every call requires approval[^pydantic-docs-toolsets] The sample gates the two temperature tools, runs with `output_type=[str, DeferredToolRequests]`, and then approves one and denies the other by tool-call id in `DeferredToolResults`; the denied call comes back to the model as the string `The tool call was denied.`[^pydantic-docs-toolsets] The pause-and-resume machinery itself belongs to [deferred tool approval](pydantic-ai-deferred-approvals.md); what this wrapper adds is the site of the decision, which is a predicate over arguments rather than a flag on a tool.

## Deferring loading

`DeferredLoadingToolset` hides its tools from the model until tool search discovers them, and the page names the case it exists for: a large toolset, an MCP server with many endpoints, where every definition in context is waste[^pydantic-docs-toolsets] Three declaration routes reach the same mark: the wrapper's `.defer_loading()`, which takes a list of tool names to hide only those or `None` to hide all; `FunctionToolset(defer_loading=True)`, which applies to `Tool` instances it holds as well, with a function added `defer_loading=False` as the only opt-out; and the per-tool declaration[^pydantic-docs-toolsets] The choice between the two hiding mechanisms is stated as a rule: use tool search for a large catalog of independent tools, and an [on-demand capability](pydantic-ai-on-demand-capabilities.md) when the tools belong to a workflow the model opts into as a unit with its instructions[^pydantic-docs-toolsets] [Tool search](pydantic-ai-tool-search.md) owns the discovery mechanics and their cache cost.

## Two provider-facing annotations

`IncludeReturnSchemasToolset` sets `include_return_schema=True` on every tool in the set, which tells the model the return type; for models that natively support return schemas, such as Google Gemini, it is sent as a structured API field, and for every other model it is injected into the tool description as JSON text[^pydantic-docs-toolsets] `SetMetadataToolset` merges key-value pairs onto every tool's metadata, for configuration other capabilities or your own logic can inspect[^pydantic-docs-toolsets] Both are documented as the toolset-level equivalents of capabilities that apply across all toolsets or a selected subset — `IncludeToolReturnSchemas` and `SetToolMetadata` — so the same effect is reachable from either layer[^pydantic-docs-toolsets] A concrete consumer exists elsewhere in this wiki: the [Harness background tools](pydantic-ai-harness-background-tools.md) selector matches the metadata `with_metadata(background=True)` writes.

## Changing how a call executes

`WrapperToolset` wraps a toolset and delegates everything, and is a no-op until subclassed; overriding `call_tool(name, tool_args, ctx, tool)` is the single hook the page describes, which is enough to log, time, retry or alter a call around `super().call_tool(...)`[^pydantic-docs-toolsets] The sample is a `LoggingToolset` that appends before and after entries and an error entry on exception, and its comment is a caution about the sample rather than about the feature: the docs' examples are tested in CI with verified output, so the sleep whose length grows with the log length exists to force a deterministic finishing order under parallel calls[^pydantic-docs-toolsets] The same class is the seam the [MCP client](pydantic-ai-mcp-client.md) records for MCP Apps, where a wrapper around a toolset should edit `ToolReturn.return_value` and drop metadata when the frontend must not see the original. Subclassing `AbstractToolset` itself, rather than wrapping one, is [custom toolsets](pydantic-ai-custom-toolsets.md).

## Contradictions

Two samples in the source disagree with their own prose, and neither side is chosen here:

- **Rename direction.** §"Renaming Tools" describes the dictionary as "mapping new names to original names", but its sample passes `{'current_time': 'datetime_now', …}` and then prints `current_time` as one of the resulting names, which reads as original-to-new[^pydantic-docs-toolsets]
- **Filtered names.** §"Filtering Tools" filters a combined toolset imported without prefixes, yet the printed result is prefixed (`weather_temperature_celsius`, `weather_conditions`, `datetime_now`), which only follows if the filtered object were the prefixed combination from the previous section[^pydantic-docs-toolsets]

Neither affects the mechanism — a wrapper takes a toolset and returns one — but the exact dictionary orientation and the exact sample wiring stay unresolved until a release-pinned source or a run settles them.

## Evidence and coverage

The source is the vendor's Toolsets page, one `index.md` capture, 5,125 words as declared and 5,192 by local `wc -w`, 1,023 lines, no attachments, includes, downloads or supporting files; it names **no Pydantic AI version, date, author or licence**, so the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set[^pydantic-docs-toolsets] The composition sections were inspected in full (raw lines 311–734) and their samples were read rather than executed; the `ToolDefinition`, `ToolsPrepareFunc`, `MCPToolset`, `DeferredToolRequests`/`DeferredToolResults`, `RunContext`, `TestModel` and `Agent.toolsets` links they reference were read as links, not followed, and the deferred-tools page they point to for approval handling is a separate un-ingested capture[^pydantic-docs-toolsets] Nothing was installed, no wrapper constructed, no predicate run, no approval requested, no schema sent and no tool call intercepted, so every claim is **Reported** and the two contradictions above are **Reported** disagreements rather than verified defects. A second limit is scope: the vendor lists `FilteredToolset`, `PrefixedToolset`, `RenamedToolset`, `PreparedToolset`, `ApprovalRequiredToolset`, `DeferredLoadingToolset`, `IncludeReturnSchemasToolset`, `SetMetadataToolset`, `CombinedToolset` and `WrapperToolset`, and this page records those ten only — whether other wrappers exist is unstated, and the API reference that would enumerate them was not followed.

## Relationships

- **Wraps** [Pydantic AI toolsets](pydantic-ai-toolsets.md): every entry takes one and returns one, and the chained forms are `AbstractToolset` methods.
- **Is the toolset-scoped form of** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md)'s `prepare`/`prepare_tools` hooks — `PreparedToolset` rewrites definitions per step, one layer up from `Tool.prepare`.
- **Gates through** [Pydantic AI deferred tool approval](pydantic-ai-deferred-approvals.md): `ApprovalRequiredToolset` decides per call and the run ends in `DeferredToolRequests` instead of blocking.
- **Feeds** [Pydantic AI tool search](pydantic-ai-tool-search.md) by marking tools `defer_loading`, and defers *bundles* rather than tools through [Pydantic AI on-demand capabilities](pydantic-ai-on-demand-capabilities.md).
- **Duplicates two capabilities at a smaller scope**, as recorded in [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): `IncludeReturnSchemasToolset` against `IncludeToolReturnSchemas`, and `SetMetadataToolset` against `SetToolMetadata`.
- **Is the seam where** [Pydantic AI MCP client](pydantic-ai-mcp-client.md) records MCP Apps result rewriting, and where [Pydantic AI lifecycle hooks](pydantic-ai-lifecycle-hooks.md) records `PreparedToolset` among the tool-preparation deferral points.
- **Shares `call_tool` with** [custom toolsets](pydantic-ai-custom-toolsets.md): `WrapperToolset` is the delegating subclass of `AbstractToolset`, so both pages describe the same method from different sides.
- **Interacts with a durable run's step identity**, per [Pydantic AI temporal](pydantic-ai-temporal.md), which records that a `FunctionToolset`'s `sequential` and `defer_loading` are now applied to the `Tool` instances it holds — a change that shifts what an in-flight workflow replays.

[^pydantic-docs-toolsets]: Pydantic Docs, "Toolsets" (<https://pydantic.dev/docs/ai/tools-toolsets/toolsets/>, `domain: pydantic.dev`, `language: en`, 5,125 words as declared and 5,192 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/toolsets/index.md`, 1,023 lines, content digest sha256:376fcf77. §"Toolset Composition" (raw lines 311–314) for the three jobs composition covers and combining several toolsets into one; §"Combining Toolsets" (315–340) for `CombinedToolset` and the four-name printed result; §"Filtering Tools" (341–368) for the `(ctx, tool_def) -> bool` predicate, its per-step timing, `filtered()` and the printed prefixed names; §"Prefixing Tool Names" (369–408) for `PrefixedToolset`, `prefixed()` and the long-name limitation; §"Renaming Tools" (409–444) for the new-to-original description, `renamed()`, the sample mapping and its printed names; §"Dynamic Tool Definitions" (445–534) for `PreparedToolset`, the `(ctx, tool_defs) -> list[ToolDefinition]` signature, the `dataclasses.replace` sample, the cannot-add-or-rename rule and the `prepare_tools` equivalence; §"Requiring Tool Approval" (535–597) for the `(ctx, tool_def, tool_args)` predicate, the no-predicate default, `output_type=[str, DeferredToolRequests]`, the approve/deny sample and the denial text; §"Deferred Loading" (598–615) for `DeferredLoadingToolset`, the `names`/`None` argument, `FunctionToolset(defer_loading=True)` with its `Tool`-instance reach and `defer_loading=False` opt-out, and the tool-search-versus-on-demand-capability rule; §"Including Return Schemas" (616–645) for `include_return_schema=True`, the native-field-versus-JSON-in-description split and the `IncludeToolReturnSchemas` equivalence; §"Setting Tool Metadata" (646–676) for the merge semantics, `with_metadata()` and the `SetToolMetadata` equivalence; §"Changing Tool Execution" (677–734) for `WrapperToolset`, the `call_tool` override, the `LoggingToolset` sample and the CI-determinism sleep. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date; the two recorded contradictions are the page disagreeing with itself.
