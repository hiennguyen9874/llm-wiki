---
type: Concept
title: Pydantic AI function tools
description: How a Python function becomes a Pydantic AI tool — the two decorators and the tools argument, the schema and docstring text that reach the model, single-object parameter folding, the inlined-$defs size limit, enum member docstrings, and enqueueing follow-up messages.
tags: [pydantic-ai, agents, tools, tool-schema]
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
  - id: pydantic-docs-tools
    resource: ../raw/tools-toolsets/tools/index.md
    scope: ../raw/tools-toolsets/tools/
    kind: documentation
    revision: sha256:1a2869f9497f084e0ba1905f48aa2656dccb7775fabbd2657084e2aca967321c
    title: "Function Tools"
---

**Reported, Pydantic AI version unspecified:** a function tool in Pydantic AI is an ordinary Python function that the model can call, and almost nothing about it is written by hand — the signature becomes the argument schema, the docstring becomes most of the description, and Pydantic validates the arguments and serializes the return value[^pydantic-docs-tools] Registration is either a decorator or the `tools` argument, and the page's starting rule is that all `tools` and `toolsets` are gathered into one combined toolset that is what the model actually sees[^pydantic-docs-tools] Two consequences are easy to miss and are the reason this page earns its own retrieval: which docstrings reach the model depends on configuration rather than on where the docstring is written, and a model that inlines `$defs` counts a schema against a hard size ceiling[^pydantic-docs-tools] The alternative for a function that should *end* the run instead of returning to the model is an output function, covered in [Pydantic AI structured output](pydantic-ai-structured-output.md)[^pydantic-docs-tools]

## Registration

| Route | Use it for | Shape |
| --- | --- | --- |
| `@agent.tool` | The default decorator: the tool needs `RunContext`, so it can read dependencies | `def get_player_name(ctx: RunContext[str]) -> str` |
| `@agent.tool_plain` | A tool that needs no context | `def roll_dice() -> str` |
| `Agent(tools=[...])` | Reusing tools across agents or tuning them | Plain functions, or `Tool(roll_dice, takes_ctx=False)` / `Tool(get_player_name, takes_ctx=True)` |
| `Agent(toolsets=[...])` | Collections built by you, by an MCP server, or by a third party | Managed by the toolsets feature, not here |

`@agent.tool` is called the default because most tools do need the context[^pydantic-docs-tools] The `tools` argument takes plain functions or `Tool` instances, and the two forms of the sample agent are identical: with a plain function the signature is inspected to decide whether it takes `RunContext`, while `Tool` makes that explicit along with the name, the description and a custom `prepare`[^pydantic-docs-tools] A tool may return anything Pydantic can serialize to JSON; multimodal returns and metadata live in the advanced tool features page[^pydantic-docs-tools]

## What the model receives

Every parameter except `RunContext` becomes a schema property, and the docstring is parsed by griffe: the description text becomes the tool description, and parameter descriptions are lifted out of `google`, `numpy` or `sphinx` style docstrings, with the format inferred or pinned by `docstring_format`[^pydantic-docs-tools] Setting `require_parameter_descriptions=True` turns a missing description into a `UserError` instead of a silent omission[^pydantic-docs-tools] The documented sample, printed through `FunctionModel`, shows the result: `additionalProperties: False`, one typed property per parameter with its description, and every parameter in `required`[^pydantic-docs-tools]

Not every docstring section survives that parse. Exactly four things reach the model[^pydantic-docs-tools]:

- the description text;
- parameter descriptions, including entries under `Keyword Args` or `Other Parameters`;
- the **first** entry of the returns section;
- recognized admonition sections — `Warning:`, `Warnings:`, `Note:`, `Important:` — header included.

Everything else griffe can parse is dropped: `Raises`, `Examples`, `Yields`, and `Warns` (which lists the warning classes a function emits, unlike a `Warnings:` admonition). So anything the model has to act on belongs in one of those four places[^pydantic-docs-tools] The returns rule has a wrinkle: with a return annotation, the whole text of a Google-style `Returns:` section — including any `type:` prefix — is the return description and no separate return type is sent; without one, the text before the first colon is read as the return type[^pydantic-docs-tools]

**Single object parameters are folded.** A tool with one parameter that can be represented as an object — a dataclass, a `TypedDict`, a Pydantic model — gets a schema that *is* that object rather than an object wrapping one property, which the page shows through `TestModel.last_model_request_parameters` as a `ToolDefinition` carrying the model's own `title` and `required` list[^pydantic-docs-tools]

**Inlined `$defs` have a ceiling.** A model whose profile inlines `$defs`, such as one configured with `InlineDefsJsonSchemaTransformer`, receives a copy of each referenced definition at every reference site, and Pydantic AI allows up to 250,000 JSON values in those copies per tool or output schema, counting every object, array, string, number, boolean and null once[^pydantic-docs-tools] Past that it raises a `UserError` before sending the request, with a message such as `The JSON schema of tool 'search' is too large`[^pydantic-docs-tools] The three documented remedies are to reference large definitions from fewer places, to leave the tool out of a request through `prepare_tools` or a `FilteredToolset`, or to use a model that keeps `$ref`s[^pydantic-docs-tools]

### Which docstrings reach the model

| Written under | Describes | Sent to the model |
| --- | --- | --- |
| a tool or output function | that tool | always |
| an `Args:` entry in its docstring | that parameter | always |
| a class used as a parameter or output type | that object | always |
| a field of a `dataclass` or `TypedDict` | that field | as a function's parameter |
| a field of a Pydantic model or `pydantic.dataclasses.dataclass` | that field | with `use_attribute_docstrings` on the class |
| an `Enum` member | that option | with `UseEnumMemberDocstrings` |

The asymmetry in the middle two rows is the trap: a schema built from a function signature turns on Pydantic's `use_attribute_docstrings`, and that reaches every type below it that brings no config of its own, at any depth — but a Pydantic model and a `pydantic.dataclasses.dataclass` do bring one, which wins, so they ignore it for their own fields and for anything nested inside them[^pydantic-docs-tools] Setting it on the class opts in wherever that class is used, including as an output type, which is built from the type rather than from a signature and so never inherits the setting[^pydantic-docs-tools] A `Field(description=...)` needs no config and outranks the docstring[^pydantic-docs-tools]

### Enum options

An `Enum` parameter normally reaches the model as its list of values, which says what the choices are and nothing about what they mean[^pydantic-docs-tools] Mixing `UseEnumMemberDocstrings` into the enum sends the docstring under each member as that option's description, and the enum then renders as an `anyOf` of `const` values instead of a plain `enum` list, with the class's own docstring as the enum's description[^pydantic-docs-tools] A mix-in is the only marker available because an enum has no `model_config` to carry a flag and cannot hold a plain class attribute — any assigned value becomes a member[^pydantic-docs-tools]

The boundaries are narrow: members without a docstring keep a bare `const`; a docstring written under an alias describes the option it was written for; a `Literal` is unaffected because it has nowhere to write one; and the descriptions appear wherever Pydantic AI describes the opted-in enum — a tool parameter, an output type, or a field of your own model[^pydantic-docs-tools] Because the docstrings are read from the enum's source, an enum built at run time has none; when the options are only known once the run is under way the documented alternative is `Choices()`, which emits the same `anyOf`-of-`const` schema from a mapping built where you build it[^pydantic-docs-tools]

## Injecting follow-up messages from a tool

A tool can push extra messages into the conversation through `RunContext.enqueue`, for a tool that wants to add follow-up context, redirect the agent's plan, or surface an event the model should react to[^pydantic-docs-tools] The page only names the method and points at the message-history page for the full pattern, so the injection contract — ordering, persistence and how a hook or durability engine sees the enqueued message — is not evidence here.

## Evidence and coverage

The package is a single `index.md` capture (2,412 words as declared, 2,482 by local `wc -w`), inspected as text; `raw/tools-toolsets/tools/` holds no attachments, includes, imports or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, default and behaviour here is version-unknown, and its samples pin `google:gemini-3.8-flash`, which no other capture in this wiki corroborates. Every external link — the `Agent`, `Agent.tool`, `Agent.tool_plain`, `Agent.__init__`, `RunContext`, `RunContext.enqueue`, `Tool`, `UseEnumMemberDocstrings`, `DocstringFormat`, `UserError`, `FunctionModel`, `TestModel`, `InlineDefsJsonSchemaTransformer` and `FilteredToolset` API pages, the output, toolsets, tools-advanced, third-party-tools, MCP client and message-history pages, and the griffe docstring reference — was read as a link, not followed, so the exact signatures, field names and error text behind them are unverified here. Nothing was installed, no tool registered or called, no schema printed and no enum exercised, so every claim is **Reported** and none is **Observed** or **Reproduced**; the page is `draft` under the `pydantic-ai` domain rule, with `stale_after` set because the decorators, the docstring pipeline and the size limit are release-sensitive.

## Relationships

- **Depends on** [Pydantic AI dependencies](pydantic-ai-dependencies.md): whether a tool takes `RunContext` is exactly what separates `@agent.tool` from `@agent.tool_plain`, and it is where `deps_type` reaches tool code.
- **Shares its schema rules with, and is contrasted against, an output function in** [Pydantic AI structured output](pydantic-ai-structured-output.md): an output function is described by the same signature, docstring, `use_attribute_docstrings` and `UseEnumMemberDocstrings` rules, but its result ends the run instead of returning to the model.
- **Is bundled by** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): tools are one half of what a capability carries, so the same signature-and-docstring contract applies whether a tool is attached to the agent or to a capability.
- **Is extended by** [Pydantic AI tool definitions](pydantic-ai-tool-definitions.md), which covers the definition this page's signature-and-docstring derivation cannot produce (`Tool.from_schema`), cannot constrain (`strict`), or must change between steps (`prepare`, `prepare_tools`)[^pydantic-docs-tools-advanced].
- **Routes its returns through** [Pydantic AI tool results and returned files](pydantic-ai-tool-results.md): the JSON, image and document values this page's tools return are placed by model and media type, framed when demoted to the user channel, or replaced by a note[^pydantic-docs-tools-advanced].
- **Is supplied remotely by** [Pydantic AI MCP client](pydantic-ai-mcp-client.md): an MCP tool arrives as a `ToolDefinition` with `meta`, `annotations` and a `return_schema`, served through a toolset rather than declared as a Python function.

[^pydantic-docs-tools]: Pydantic Docs, "Function Tools" (`https://pydantic.dev/docs/ai/tools-toolsets/tools/`, 2,412 words as declared and 2,482 by local `wc -w`, `domain: pydantic.dev`, `language: en`); local capture `raw/tools-toolsets/tools/index.md`, 481 lines, content digest sha256:1a2869f9. Opening paragraphs (raw lines 11–23) for what a function tool is for, the output-function alternative, the three registration routes and the combined toolset the model sees; §"Registering via Decorator" (25–205) for `@agent.tool_plain` versus `@agent.tool`, the `RunContext` dependency read, the `dice_game.py` sample and its printed `ModelMessage` sequence; §"Registering via Agent Argument" (206–261) for the `tools` kwarg, signature-based `takes_ctx` inference and the `Tool(...)` form with `prepare`; §"Tool Output" (262–265) for JSON-serializable returns; §"Tool Schema" (266–380) for parameters minus `RunContext`, griffe docstring extraction, the three docstring formats and `docstring_format`, `require_parameter_descriptions` and its `UserError`, the four kinds of text that reach the model with the dropped-sections list and the returns-section rule, the `FunctionModel` schema print, the single-object-parameter folding through `TestModel.last_model_request_parameters`, and the inlined-`$defs` limit with its `UserError` and remedies; §"Docstrings" (381–409) for the reach table, `use_attribute_docstrings` inheritance and the config that wins, and `Field(description=...)` precedence; §"Enum options" (410–478) for `UseEnumMemberDocstrings`, the `anyOf`-of-`const` rendering, the mix-in rationale, aliases, `Literal`, run-time enums and `Choices()`; §"Injecting Follow-up Messages from a Tool" (479–481) for `RunContext.enqueue`. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Custom Tool Schema" (raw lines 152–188), §"Strict Mode" (189–233), §"Dynamic Tools" and §"Agent-wide Dynamic Tools" (234–418) for `Tool.from_schema`, the `strict` flag and its provider matrix, and the `prepare`/`prepare_tools` hooks that extend the definition this page derives; §"Where a returned file is sent" (70–99) for the three routes a returned file takes and the note that replaces an unreadable one. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
