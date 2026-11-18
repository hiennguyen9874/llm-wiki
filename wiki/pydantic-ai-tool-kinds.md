---
type: Concept
title: Pydantic AI tool kinds and typed parts
description: How a Pydantic AI tool declares what it is instead of relying on its name — ToolKind namespaces, the typed call and return parts promoted from history, the shape checks that fail a run, and unless_tool_kind plus tool_name_for_kind for capability tools that must step aside.
tags: [pydantic-ai, agents, tools, message-history]
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
---

**Reported, Pydantic AI version unspecified:** a tool's name is not a stable identifier — a toolset can prefix or rename it, `PrefixTools` rewrites it, and the name is therefore the wrong thing for a hook to match on[^pydantic-docs-tools-advanced] A `ToolKind` is the stable identifier instead: a namespaced name that is written into every message, promoted to typed `ToolCallPart` and `ToolReturnPart` subclasses, and usable to make one capability's tool step aside for a better tool on the agent[^pydantic-docs-tools-advanced] The same idea covers the opposite direction — `tool_name_for_kind` lets instructions name whichever tool currently has the kind, so text and tools do not drift apart when the toolset changes[^pydantic-docs-tools-advanced]

## What a kind is

A `ToolKind` has a namespace and a name, and optionally the shapes of the tool's arguments (`args`) and result (`content`), typically `TypedDict`s[^pydantic-docs-tools-advanced] Its id is `'{namespace}.{name}'`, and the namespace exists because that id is stored in every message history — it keeps kinds from different packages apart[^pydantic-docs-tools-advanced]

A tool declares its kind with `tool_kind` on `Tool` and the decorators, or by setting `ToolDefinition.tool_kind` — in a toolset's `get_tools` or a `prepare` function, say — and either surface accepts the `ToolKind` or its id string[^pydantic-docs-tools-advanced]

### Typed parts

Typed parts are registered for a kind with the `kind` class argument, the way [capability events](pydantic-ai-capability-events.md) are defined, and need no `@dataclass` decorator[^pydantic-docs-tools-advanced] Their base class is parameterized with the kind's shape, which is what types `typed_args` and `typed_content`[^pydantic-docs-tools-advanced] The documented sample declares an inventory kind and two parts[^pydantic-docs-tools-advanced]:

```python
lookup = ToolKind('inventory', 'lookup', args=LookupArgs, content=LookupResult)

class LookupCallPart(ToolCallPart[LookupArgs], kind=lookup): ...
class LookupReturnPart(ToolReturnPart[LookupResult], kind=lookup): ...
```

Attaching `tool_kind=lookup` to the tool then makes the run's parts come back as `LookupCallPart` and `LookupReturnPart`, with `call.tool_kind` printing `inventory.lookup`, `call.typed_args` the validated `{'sku': 'a'}`, and `tool_return.typed_content` the validated `{'in_stock': False}`[^pydantic-docs-tools-advanced]

A tool function may take the kind's arguments as its single parameter — the model still sees the shape's fields as the parameters, while the function receives them validated as one object — or as separate parameters[^pydantic-docs-tools-advanced] Type checkers check the function's return type against the kind's `content`, and the parameters are checked when the agent collects its tools, because a type checker cannot tell one parameter of the wrong shape from separate parameters[^pydantic-docs-tools-advanced]

### What `typed_` returns

| Accessor | Value |
| --- | --- |
| `typed_args` | The arguments validated against the kind's `args`, or `None` while they are still streaming in or do not validate |
| `args` | Always the base type, which may still hold the raw JSON string |
| `typed_content` | The content validated against `content`, or `None` if it does not fit |
| `content` | Always as sent, even when it is a JSON string, so a stored history and what goes back to the model do not change |

Promotion is conditional in two ways: a part is promoted only when its arguments, once they are a dictionary, fit the shape, and a return part only when its `outcome` is `'success'` **and** its content fits — the content of any other return is an error rather than the typed result[^pydantic-docs-tools-advanced] A kind may declare no shape at all, in which case anything is promoted and the typed part's base class is left unparameterized; a base class parameterized with a shape other than the kind's is an error both for type checkers and when the class is defined[^pydantic-docs-tools-advanced]

Promotion happens wherever a message is constructed — by a model, by loading stored history, or by hand — so a hand-built `ToolCallPart(..., tool_kind='inventory.lookup')` comes back as the typed part too[^pydantic-docs-tools-advanced] Core's own kinds (`'tool-search'`, `'capability-load'`) work the same way[^pydantic-docs-tools-advanced] Under [Temporal](pydantic-ai-temporal.md), whose workflow sandbox re-imports your modules, a part promoted in workflow code is an instance of the class workflow code imported, so `isinstance` checks still hold[^pydantic-docs-tools-advanced]

### What fails, and what loads anyway

Collecting a run's tools raises `UserError` for a kind that is not defined — so the module defining it must be imported — while a stored `ToolDefinition` carrying such a kind, from durable-execution history for instance, still loads[^pydantic-docs-tools-advanced] It also raises `UserError` when the tool's parameters do not fit the kind's `args` or its return type does not fit the kind's `content`: every field the shape requires must be a required field of the tool's, and where both give a field a JSON type, those types must overlap. A return type that cannot be compared field by field, such as a union, is accepted[^pydantic-docs-tools-advanced] The page calls this a sanity check rather than a full JSON Schema comparison[^pydantic-docs-tools-advanced]

Two leniencies preserve history[^pydantic-docs-tools-advanced]:

- A typed subclass may add properties but not fields; adding a field raises `UserError` when the class is defined. That restriction is what lets a part fall back to its base class without losing anything.
- A history recorded with a kind the current process does not define — module not imported, or removed — still loads: the part stays a plain `ToolCallPart`/`ToolReturnPart` that keeps its `tool_kind`, and becomes typed again wherever the kind is defined.

## Superseding a tool by kind

`ToolDefinition.unless_tool_kind` makes a tool step aside whenever another tool in the same step has the named kind — whatever that tool is called[^pydantic-docs-tools-advanced] It is the counterpart of `unless_native`, which does the same for a native tool the model supports[^pydantic-docs-tools-advanced] The motivating case is a capability offering its own reader for something a more general tool already does — a notes-tool when the agent can read files anyway[^pydantic-docs-tools-advanced]

The documented sample sets the flag from a `prepare` function with `dataclasses.replace(tool_def, unless_tool_kind=file_read)`, then builds instructions from `ctx.tool_name_for_kind(file_read)`: without a file tool the instructions say `Read your notes with \`read_notes\``, and with a `FunctionToolset` holding a `file_read` tool they say ``Read them with `read_file` `` — and the two runs call different tools[^pydantic-docs-tools-advanced]

The resolution rules are precise, and several are counter-intuitive[^pydantic-docs-tools-advanced]:

- The decision is made when the step's tools are collected, **after** any `prepare_tools` function, so a tool left out is neither sent to the model nor callable, and `tool_name_for_kind` does not return it.
- A tool hidden by [deferred loading](pydantic-ai-tool-search.md) counts as present: the answer, and instructions built from it, stay the same once that tool is revealed, which keeps the prompt cacheable.
- A tool is only left out in favour of a tool that stays, so if a third tool supersedes the general one the capability's tool comes back.
- When two tools would each step aside for the other, the one listed first stays and every tool naming its kind steps aside.
- A cycle (A unless B, B unless C, C unless A) cannot satisfy every rule at once, so a tool can stay beside one whose kind it names; the result is still deterministic for the same tools in the same order.
- Unlike `tool_kind`, `unless_tool_kind` needs no definition: only ids are compared, so a capability can yield to another package's tool without importing it, and a kind no tool carries means there is nothing to yield to.

When several tools carry the kind, `tool_name_for_kind` returns the first in `RunContext.tools` order — the order the step's toolsets list them — and iterating `ctx.tools` shows them all[^pydantic-docs-tools-advanced] Instruction functions, model-request hooks and tools see the current step's tools, including a tool running in a Temporal activity, which answers from a snapshot taken when the activity was dispatched; a toolset's `get_tools` and `prepare_tools` run while collection is still in progress, so there they answer from the previous step[^pydantic-docs-tools-advanced]

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, `UserError` condition and ordering rule here is version-unknown. Every external link — the `ToolKind`, `ToolKind.id`, `BaseToolCallPart.tool_kind`, `ToolCallPart`, `ToolReturnPart`, `Tool`, `Agent.tool_plain`, `ToolDefinition.tool_kind`, `ToolDefinition.unless_tool_kind`, `ToolDefinition.unless_native`, `RunContext.tool_name_for_kind`, `RunContext.tools`, `PrefixTools`, `UserError`, `FunctionToolset` and capability-events pages — was read as a link, not followed. Nothing was installed, no kind defined, no tool registered, no part promoted and no run executed, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because the promotion rules and the `unless_tool_kind` resolver are release-sensitive.

## Relationships

- **Extends** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md): a kind is the identity half of a definition, settable on `Tool` or on `ToolDefinition` from `get_tools` and `prepare`, and resolved after `prepare_tools` has run.
- **Types the parts defined by** [Pydantic AI message history](pydantic-ai-message-history.md): `ToolCallPart` and `ToolReturnPart` are promoted to a kind's subclasses when a message is built, and a stored part that cannot be promoted keeps its `tool_kind` until the kind is defined again.
- **Lets a tool yield to** [Pydantic AI tool search](pydantic-ai-tool-search.md)'s revealed tools without name matching, and works the same way for a tool an on-demand capability reveals.
- **Mirrors** [Pydantic AI capability events](pydantic-ai-capability-events.md): both are registered with a `kind=` class argument, both use a namespaced id stored in history, and both are matched with `isinstance` rather than by name.
- **Is the mechanism behind** [Pydantic AI structured output](pydantic-ai-structured-output.md)'s output-tool handling and behind `PrefixTools`, since a prefixed or renamed tool keeps its kind while its name changes.
- **Survives** [Pydantic AI durable execution](pydantic-ai-durable-execution.md)'s Temporal sandbox, which re-imports modules but still promotes parts to the classes workflow code imported.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Typed Tool Parts" (raw lines 1028–1083) for the renaming problem, `ToolKind` fields and namespaced id, the `kind=` registration, the `lookup` sample and its printed output, the single-parameter versus separate-parameter forms, the `typed_args`/`typed_content` table, the promotion and success conditions, shapeless kinds, construction-time promotion, core kinds, the Temporal note, the `UserError` conditions, the properties-only subclass rule and the undefined-kind history fallback; §"Superseding a tool by kind" (1084–1141) for `unless_tool_kind` and its `unless_native` counterpart, the `unless_file_reader` sample, the after-`prepare_tools` timing, the deferred-counts-as-present and third-tool rules, the cycles, the id-only comparison, `tool_name_for_kind` ordering and the `get_tools`/`prepare_tools` previous-step answer. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
