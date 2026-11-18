---
type: Concept
title: Pydantic AI toolsets
description: What a toolset is in Pydantic AI and where it can be registered — the four attachment sites and the override that replaces rather than adds, FunctionToolset and its four routes to a tool, toolset-level instructions with their append-or-rewrite cache rule, dynamically built toolsets, and the third-party toolsets that ship with the framework.
tags: [pydantic-ai, agents, tools, toolsets]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:03:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-toolsets
    resource: ../raw/tools-toolsets/toolsets/index.md
    scope: ../raw/tools-toolsets/toolsets/
    kind: documentation
    revision: sha256:376fcf77e23d854d7b3adfbd3c7ab51b845516590c4c146bd4a21e9c8ee55355
    title: "Toolsets"
---

**Reported, Pydantic AI version unspecified:** a toolset is a collection of tools that can be registered with an agent in one go, and the page's framing is reusability rather than convenience — the same collection is meant to be shared by several agents, swapped at runtime or in a test, and nested inside other toolsets that filter what is available, rewrite the definitions, or change how a call executes[^pydantic-docs-toolsets] A toolset may hold locally defined functions, delegate to an external service that supplies its tools, or implement its own logic to list tools and handle their calls; capabilities can also hand over toolsets, bundling them with hooks, instructions and model settings; and MCP servers are themselves expressed as toolsets[^pydantic-docs-toolsets] The rest of this page is the attachment contract — where a toolset may be passed and what each site does to the others — plus the function-backed toolset, instructions carried on a toolset, toolsets built per run, and the third-party kinds that ship. Composing one toolset out of another is recorded in [toolset composition](pydantic-ai-toolset-composition.md); subclassing the base class is recorded in [custom toolsets](pydantic-ai-custom-toolsets.md).

## The four attachment sites

| Site | Form | What happens to what was already registered |
| --- | --- | --- |
| Agent construction | `Agent(..., toolsets=[...])` | Establishes the base set; accepts toolset instances **and** functions that build one from the `RunContext` |
| Per run | `agent.run(..., toolsets=[...])`, also `run_sync`, `run_stream`, `iter` | Added to the agent's toolsets, not substituted for them |
| Decorator | `@agent.toolset` on a function taking `RunContext` | Builds a toolset per run or per step from run state |
| Override context | `agent.override(toolsets=[...])` | Replaces the agent's and the run's toolsets for the life of the context manager |

The precedence in the samples is sharper than the table suggests: the documented run passes an `extra_toolset` at run time and sees both `agent_tool` and `extra_tool` in `TestModel.last_model_request_parameters.function_tools`, and the same run repeated inside `with agent.override(toolsets=[override_toolset])` sees `override_tool` alone — the per-run toolset is ignored, not merged, because the override sits above both layers[^pydantic-docs-toolsets] `TestModel` is the page's instrument throughout: it needs no provider, and its `last_model_request_parameters.function_tools` is how each sample prints the tool names the model was actually offered[^pydantic-docs-toolsets]

## FunctionToolset: four routes to a tool

`FunctionToolset` is the locally defined-function toolset, and its four registration routes differ only in what they demand of the function and when they can be called[^pydantic-docs-toolsets]:

| Route | Takes | Use it when |
| --- | --- | --- |
| `@toolset.tool` | A function whose first parameter is `RunContext` | The tool needs dependencies or run state |
| `@toolset.tool_plain` | A function with no context parameter | The tool is a pure function of its arguments |
| `tools=[...]` on the constructor | Plain functions or `Tool` instances | The set is known when the toolset is built |
| `add_function()` / `add_tool()` | A plain function or a `Tool` | The set is assembled after construction — including from inside a tool |

The last row is the one with behavioural consequences: the add methods may be called from a tool function, which registers new tools during the run so that they are available in later run steps[^pydantic-docs-toolsets] A tool that joins after the run's first model request is recorded in the message history as a `ToolAvailabilityDeltaPart` — unless no plainly visible earlier tool is still present to keep the shape stable — and a tool added with `defer_loading=True` joins the tool-search corpus instead of the request[^pydantic-docs-toolsets] How each provider delivers that delta is [tool search](pydantic-ai-tool-search.md)'s subject.

## Instructions carried on a toolset

Instructions may sit on the toolset instead of on every agent that uses it, and they are included in the model request automatically[^pydantic-docs-toolsets] The accepted forms are a string, a function — sync or async, with or without `RunContext` — or a mixture of both, with `@toolset.instructions` as the decorator form for a function that needs the run context[^pydantic-docs-toolsets] Two ordering rules are stated: when an agent also has agent-level `instructions`, the toolset's instructions are **appended after** them, and when several toolsets with instructions are registered, all their instruction blocks are combined in the order the toolsets are listed[^pydantic-docs-toolsets] The decorator also takes `name=` and `on_change='append'`, the same pair `@agent.instructions` takes[^pydantic-docs-toolsets]

### When the instructions change mid-run

Instruction functions run before every model request, so their text may change during a run — after a tool mutates state, for instance[^pydantic-docs-toolsets] The default is to rewrite the instruction prefix, which costs the provider's cached conversation; the documented alternative is to append the change, which keeps the prefix cached but adds the block's complete new text to the history once per change[^pydantic-docs-toolsets] Opting in needs both halves: the toolset gets an `id`, and the function is registered with `@toolset.instructions(name=..., on_change='append')`, which is what identifies the part across restatements[^pydantic-docs-toolsets] The rule that matters for safety is separate from the cache: build the instruction text only from state you control, because a value taken from a model tool argument would put untrusted text in the instruction channel — the documented sample prints the cart's item **count** and not the item names for exactly that reason[^pydantic-docs-toolsets] [Prompt caching](pydantic-ai-prompt-caching.md) owns the prefix economics; [mid-run injection and instruction placement](pydantic-ai-mid-run-injection.md) owns the placement of appended blocks.

## Toolsets built per run or per step

A function taking `RunContext` and returning a toolset — or `None` — may be passed in the `toolsets` argument or wrapped in `@agent.toolset`, and its motivating case is a toolset that depends on run-specific information such as dependencies, for example connecting to an MCP server with per-user credentials[^pydantic-docs-toolsets] By default the function runs again ahead of each run step; `per_run_step=False` on the decorator builds it once for the whole run[^pydantic-docs-toolsets] Instructions from the returned toolset are attributed to the dynamic toolset rather than to the toolset it returned, so `on_change='append'` on them requires the decorator to be given an `id`[^pydantic-docs-toolsets] The documented sample toggles between two toolsets through a dependency field and shows the change landing on the *following* request, because the last model request of a run is the one that returns the toggle tool's result[^pydantic-docs-toolsets]

## Third-party toolsets that ship

`MCPToolset` connects to local and remote MCP servers, with the `MCP` capability named as the recommended higher-level entry point[^pydantic-docs-toolsets] Its own surface is compiled in [MCP client](pydantic-ai-mcp-client.md). Two further kinds are recorded as third-party adapters:

- **LangChain tools** — `LangChainToolset` from `pydantic_ai.ext.langchain` takes a list of LangChain tools, including a LangChain toolkit such as `SlackToolkit().get_tools()`, and needs `langchain-community` plus whatever the individual tools import. The stated caveat is a contract change, not an install detail: Pydantic AI does **not** validate the arguments, so matching the LangChain schema is the model's job and rejecting bad arguments is the LangChain tool's[^pydantic-docs-toolsets] The vendor's own third-party-tools page adds the single-tool form, `tool_from_langchain`, and the install list, compiled in [third-party tool bridges](pydantic-ai-third-party-tools.md).
- **`pydantic-ai-ejentum`** — `EjentumToolset` subclasses `FunctionToolset` and registers four tools (`harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`). The agent is expected to call one before generating, and each call returns a structured cognitive scaffold — named failure pattern, executable procedure, suppression vectors, falsification test — that the model reads rather than shows. It authenticates with `EJENTUM_API_KEY` or `api_key=`, and emits instructions that nudge the agent toward the matching tool; `add_instructions=False` suppresses them so routing guidance can come from your own system prompt[^pydantic-docs-toolsets]

## Evidence and coverage

The source is a single `index.md` capture of the vendor's Toolsets page — 5,125 words as declared, 5,192 by local `wc -w`, 1,023 lines — inspected as text; `raw/tools-toolsets/toolsets/` holds that file alone, with no attachments, includes, downloads or supporting assets, and the samples it embeds are code blocks rather than separate files[^pydantic-docs-toolsets] It names **no Pydantic AI version, author, publication date or licence**, so every API name, default and ordering rule here is version-unknown, which is why the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set. Every external link — the `AbstractToolset`, `FunctionToolset`, `Agent.__init__`, `AbstractAgent.run`/`run_sync`/`run_stream`/`iter`, `Agent.toolset`, `Agent.override`, `RunContext`, `TestModel`, `ToolAvailabilityDeltaPart`, `MCPToolset`, `LangChainToolset` and Ejentum pages, and the capabilities, tools, MCP, deferred-tools, on-demand and tool-search pages — was read as a link, not followed. Nothing was installed, no agent constructed, no tool registered mid-run, no instruction change observed and no trace opened, so every claim is **Reported** and none **Observed** or **Reproduced**. Two limits are worth stating rather than hiding: the four-site table's precedence is read off three prints from one sample, so what a per-run `toolsets` argument does to an agent's own toolset in a case the sample does not show stays unstated; and the sample model names are aliases (`openai:gpt-6.1-sol`) that no release-pinned capture here corroborates.

## Relationships

- **Is the collection layer over** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md) and [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md): this page decides where tools are gathered and which set the model sees, while those own the `ToolDefinition` a tool carries and what happens after a call.
- **Is extended to foreign libraries by** [Pydantic AI third-party tool bridges](pydantic-ai-third-party-tools.md), which owns the LangChain single-tool adapter and the argument-validation handover this page only mentions.
- **Is how a capability delivers tools**, per [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): a capability bundles a toolset with hooks, instructions and settings, and its own `get_wrapper_toolset()` wraps the agent's assembled set.
- **Is transformed by** [Pydantic AI toolset composition](pydantic-ai-toolset-composition.md), which catalogs the wrappers that filter, rename, prefix, prepare, gate, defer, annotate and intercept a toolset.
- **Is subclassed according to** [custom toolsets](pydantic-ai-custom-toolsets.md), which owns the `AbstractToolset` contract, the instruction-part key scheme and the run and step lifecycle hooks.
- **Contains** [Pydantic AI MCP client](pydantic-ai-mcp-client.md)'s `MCPToolset` as one kind, and [external toolsets](pydantic-ai-external-toolsets.md)' `ExternalToolset` as another — the latter executes nothing itself.
- **Defers individual tools through** [Pydantic AI tool search](pydantic-ai-tool-search.md): `defer_loading=True` on a toolset or a tool decides what enters the searchable corpus, and a tool added mid-run joins it rather than the request.
- **Chooses an append over a rewrite for changing instructions**, which is the trade-off recorded in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md) and placed in the conversation by [mid-run injection and instruction placement](pydantic-ai-mid-run-injection.md).
- **Is carried into a durable run as identity**, per [Pydantic AI temporal](pydantic-ai-temporal.md) and [Pydantic AI on DBOS](pydantic-ai-dbos.md), where a toolset `id` becomes part of the step or activity name.

[^pydantic-docs-toolsets]: Pydantic Docs, "Toolsets" (<https://pydantic.dev/docs/ai/tools-toolsets/toolsets/>, `domain: pydantic.dev`, `language: en`, 5,125 words as declared and 5,192 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/toolsets/index.md`, 1,023 lines, content digest sha256:376fcf77. Intro, raw lines 13–65, for the definition and the reuse/swap/compose framing, the three kinds of content, toolsets arriving through capabilities, MCP servers as toolsets, the four attachment sites, the `toolsets.py` sample and its three prints (agent-level, run-level additive, override replacing and ignoring the run-level set), and the `TestModel.last_model_request_parameters.function_tools` instrument; §"Function Toolset" (67–124) for the four routes, `add_function()`/`add_tool()` from inside a tool, the `ToolAvailabilityDeltaPart` record, the `defer_loading=True` corpus rule and the `conditions` sample reading `ctx.run_step`; §"Toolset Instructions" (125–257) for the string/function/mix forms, the decorator with `name=` and `on_change='append'`, the append-after-agent-instructions order and the multi-toolset combination; §"Toolset instructions that change" (258–310) for the per-request evaluation, the rewrite-versus-append prefix trade-off, the `id` requirement, the `InstructionPart` route for a custom toolset, and the untrusted-text rule with the cart-count sample; §"Dynamically Building a Toolset" (888–955) for the `RunContext`-to-toolset function, the decorator form, the per-step default, `per_run_step=False`, the instruction attribution and id rule, and the toggle sample's ordering note; §"Third-Party Toolsets" (981–1023) for the MCP pointer and capability recommendation, `LangChainToolset` with the no-validation caveat, and `EjentumToolset` with its four tools, scaffold payload, key variable and `add_instructions=False`. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version or date.
