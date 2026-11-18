---
type: Concept
title: Pydantic AI custom toolsets
description: How to build a Pydantic AI toolset from scratch — the get_tools and call_tool methods to implement, the optional get_instructions and the toolset-id key scheme that addresses its parts, the passthrough rule a wrapper must follow, and the per-run and per-step lifecycle hooks.
tags: [pydantic-ai, agents, tools, toolsets, extension]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:05:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-toolsets
    resource: ../raw/tools-toolsets/toolsets/index.md
    scope: ../raw/tools-toolsets/toolsets/
    kind: documentation
    revision: sha256:376fcf77e23d854d7b3adfbd3c7ab51b845516590c4c146bd4a21e9c8ee55355
    title: "Toolsets"
---

**Reported, Pydantic AI version unspecified:** a toolset with logic of its own — one that lists tools from somewhere and handles their calls itself — is a subclass of `AbstractToolset` implementing `get_tools()` and `call_tool()`[^pydantic-docs-toolsets] That pair is the whole required contract; everything else on this page is optional surface with rules attached: `get_instructions()` to describe the toolset to the model, an `id` that becomes the address of those instructions and must be unique across an agent's toolsets, and three lifecycle hooks that bound per-run and per-step state[^pydantic-docs-toolsets] The reason this earns its own page rather than a section is that the instruction-address and passthrough rules are the part a wrapper author gets wrong, and they are stated only here. Which toolsets the framework ships, and where any toolset can be attached, is [Pydantic AI toolsets](pydantic-ai-toolsets.md); the wrappers that delegate to an existing toolset are [toolset composition](pydantic-ai-toolset-composition.md).

## The two methods to implement

| Method | Role | Detail stated |
| --- | --- | --- |
| `get_tools()` | List the tools this toolset currently offers | Called ahead of each step, so the list may change per step |
| `call_tool(name, tool_args, ctx, tool)` | Execute a named call | The signature is shown in the wrapper sample, with `ctx` a `RunContext` and `tool` a `ToolsetTool` |
| `get_instructions()` | Optional: how to use this toolset's tools | Injected into the agent's instructions; called before each model request |

This is the same surface the built-in composition wrappers are written against: `WrapperToolset` delegates all of it, and its documented override point is `call_tool`[^pydantic-docs-toolsets] The listing side is what makes a custom toolset more than a function collection — an MCP client, a filtered view and a per-run dynamic toolset all decide *per step* what exists, which a `FunctionToolset` does not[^pydantic-docs-toolsets]

## The instruction address

When a toolset has an `id` and contributes instructions, the id must be unique among the toolsets registered with an agent — counting the ones a capability contributes — and it becomes the key those instructions are addressed by: they reach the model as instruction parts identified as `'toolset:<toolset id>'`, so an application can address a block by a key that outlives its wording[^pydantic-docs-toolsets] Every part the toolset returns carries that one key. A part that needs its own address gets a `name` relative to the toolset — `name='limits'` inside a toolset with `id='weather'` arrives as `'toolset:weather:limits'` — and the stated rule is not to spell your own id into the name, because the framework already knows it and a hand-written name could be mistaken for a top-level key[^pydantic-docs-toolsets]

### What a wrapper must not re-key

A wrapper toolset with its own `id` that overrides `get_instructions()` has one way to keep what it wraps intact: return the very part objects `super().get_instructions(ctx)` produced, unchanged, so they keep the ids of the toolsets that wrote them — or no id, if their toolset had none[^pydantic-docs-toolsets] Every other part is keyed by the **wrapper's** id: the ones it adds, the ones it changes in place, and copies — even an unchanged copy such as `replace(part)`, which still carries the id of the part it came from, so copying is not the same as passing through[^pydantic-docs-toolsets] The one structure excluded from this rule is a toolset built by a dynamic toolset: it is not wrapped this way, so everything it says is keyed by the dynamic toolset's id[^pydantic-docs-toolsets]

`get_instructions()` runs before each model request, so a changing return value needs `on_change='append'` on the `InstructionPart` to append rather than rewrite the cached prefix[^pydantic-docs-toolsets] That is the same trade-off the function-toolset decorator exposes as `@toolset.instructions(name=..., on_change='append')`, recorded with its cache cost in [prompt caching](pydantic-ai-prompt-caching.md) and its placement in [mid-run injection and instruction placement](pydantic-ai-mid-run-injection.md).

## Lifecycle: per run, per step, per resource

| Hook | Called | Expected return |
| --- | --- | --- |
| `for_run(ctx)` | Once per agent run, **before** `__aenter__` | A fresh instance for per-run isolation, or `self` (the default) |
| `for_run_step(ctx)` | At the start of each run step | A modified instance for per-step state, or `self` (the default) |
| `__aenter__()` / `__aexit__()` | Around the run | Resources that live for the run's duration, such as connections |

Two responsibilities sit with the author rather than the framework[^pydantic-docs-toolsets] Returning a new instance from `for_run()` is how state is isolated between runs — a reset counter, a new session — and the framework enters and exits the instance that comes back, so the returned object is the one whose `__aenter__` runs. And when a toolset manages an inner toolset's transitions, for example swapping one toolset for another at a step boundary, the inner lifecycle is the outer toolset's job: exiting the old one and entering the new one are not done for you.

## Evidence and coverage

The relevant material is one section of the vendor's Toolsets page — §"Building a Custom Toolset" and its §"Per-run and per-step lifecycle" subsection, raw lines 956–980 — inside a single `index.md` capture of 5,125 declared words (5,192 by local `wc -w`, 1,023 lines) with no attachments, includes, downloads or supporting files[^pydantic-docs-toolsets] The capture names **no Pydantic AI version, date, author or licence**, so the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set. The `AbstractToolset`, `get_tools`, `call_tool`, `get_instructions`, `id`, `for_run`, `for_run_step` and `InstructionPart` API links were read as links, not followed, so nothing here is checked against a signature the source did not print. Nothing was installed, no subclass written, no toolset entered, no instruction part emitted and no lifecycle hook observed, so every claim is **Reported**, none **Observed** or **Reproduced**. The limits worth naming: `get_tools()`'s return type and `call_tool()`'s full signature are unstated except where the `LoggingToolset` sample shows four parameters; error handling inside `call_tool`, whether `get_tools()` may raise, how a custom toolset declares `defer_loading` or `sequential` per tool, and what `ToolsetTool` actually carries are all outside the source, and the `id`-uniqueness error's exact type and message are not given.

## Relationships

- **Is implemented by every built-in kind** in [Pydantic AI toolsets](pydantic-ai-toolsets.md): `FunctionToolset` is one such subclass, and the page's own framing is that a custom toolset is the third source of tools beside local functions and external services.
- **Shares `call_tool` with** [Pydantic AI toolset composition](pydantic-ai-toolset-composition.md)'s `WrapperToolset`, which delegates to an inner toolset instead of implementing the call from scratch — and is therefore where the passthrough rule above is most likely to be broken.
- **Publishes parts into** [Pydantic AI mid-run injection and instruction placement](pydantic-ai-mid-run-injection.md): the `'toolset:<id>'` key and a relative `name` are what make an instruction block addressable across rewording.
- **Chooses between rewrite and append for** [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md): `on_change='append'` keeps the prefix cached at the cost of repeated text in history.
- **Is one of the two toolset verbs in** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md), where `Toolset` wraps an `AbstractToolset` and `get_wrapper_toolset()` wraps the agent's whole assembled set — the same contract seen from the capability side.
- **Supply identity to a durable run** per [Pydantic AI temporal](pydantic-ai-temporal.md): a toolset id is part of the activity naming rule, which is why the uniqueness rule here has consequences beyond the prompt.
- **Expose their per-step listing through** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md): what `get_tools()` returns is what a `prepare` function and `prepare_tools` then get to rewrite.
- **Are enumerated, with the execution side, in** [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md), which records that timeouts are enforced by `FunctionToolset` alone — so a custom `call_tool` owns its own deadline.

[^pydantic-docs-toolsets]: Pydantic Docs, "Toolsets" (<https://pydantic.dev/docs/ai/tools-toolsets/toolsets/>, `domain: pydantic.dev`, `language: en`, 5,125 words as declared and 5,192 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/toolsets/index.md`, 1,023 lines, content digest sha256:376fcf77. §"Building a Custom Toolset" (raw lines 956–973) for the `AbstractToolset` subclass requirement, `get_tools()` and `call_tool()`, the optional `get_instructions()` and its injection into the agent's instructions, the `id`-uniqueness rule across an agent's toolsets including capability-contributed ones, the `'toolset:<toolset id>'` part key, the relative-`name` qualification to `'toolset:weather:limits'` and the don't-spell-your-own-id rule, the wrapper passthrough rule with the `replace(part)` example, the dynamic-toolset exception, and the per-request `get_instructions()` call with `on_change='append'`; §"Per-run and per-step lifecycle" (974–980) for `for_run(ctx)` before `__aenter__` with its `self` default and framework-entered return value, `for_run_step(ctx)` at each step start, the inner-lifecycle responsibility and `__aenter__`/`__aexit__` for resources; §"Changing Tool Execution" (677–734) for the `call_tool(name, tool_args, ctx, tool)` signature and its `ToolsetTool` parameter as shown in the `LoggingToolset` sample; §"Toolset instructions that change" (258–310) for the `InstructionPart`-with-`on_change='append'` route available to a custom toolset and the untrusted-text rule. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.
