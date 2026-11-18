---
type: Concept
title: Pydantic AI tool definitions
description: How the ToolDefinition a Pydantic AI model sees is built and changed — a hand-written JSON schema through Tool.from_schema, the strict flag and the four providers that enforce it, the Gemini VALIDATED request-wide rule, and the prepare and prepare_tools hooks that rewrite or withhold a definition every step.
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
---

**Reported, Pydantic AI version unspecified:** the third thing a tool carries besides its function and its schema is a `ToolDefinition`, and Pydantic AI gives three levers over it — you can hand-write the schema when introspection cannot produce one, you can ask the provider to enforce the schema during generation with `strict`, and you can rewrite or withhold the definition at every step with a `prepare` function[^pydantic-docs-tools-advanced] Each lever has a different kind of guarantee, and the page is explicit that the strongest-sounding one is the weakest: `strict=True` is a request to force strict mode "wherever the provider can honour it", because not every schema is representable under strict generation[^pydantic-docs-tools-advanced]

## Tool.from_schema

`Tool.from_schema` turns a function into a tool by supplying what introspection would have read: `function`, `name`, `description`, the JSON schema and `takes_ctx`[^pydantic-docs-tools-advanced] It exists for the functions the schema pipeline cannot describe — poorly named, untyped, badly documented, or built from `*args`/`**kwargs`[^pydantic-docs-tools-advanced] The documented sample wraps `def foobar(**kwargs)` with a hand-written two-integer object schema and `takes_ctx=False`, and the `TestModel` run prints `{"sum":0}`[^pydantic-docs-tools-advanced]

One rule matters more than the rest: **Pydantic AI does not validate tool arguments for a `from_schema` tool — it passes them as keyword arguments**[^pydantic-docs-tools-advanced] The schema constrains the model's generation and the function receives whatever arrives, so the `ValidationError`-to-retried-result loop described in [tool execution](pydantic-ai-tool-execution.md) is not a backstop here.

## Strict mode

Strict mode moves schema conformance from after-the-fact validation into generation: instead of letting the model emit arguments and validating them, the provider restricts generation so out-of-schema arguments are not produced in the first place[^pydantic-docs-tools-advanced] Its motivating case is a structured argument — the documented `Reservation` booking tool, where without strictness the model "might emit `party_size` as a string, omit `outdoor_seating`, or invent an extra property"[^pydantic-docs-tools-advanced]

The flag is available on every registration mechanism — `@agent.tool`, `@agent.tool_plain`, `Tool`, `FunctionToolset.add_function` — and on `ToolDefinition` itself[^pydantic-docs-tools-advanced]

### What each provider does with it

| Provider | Enforcement | Default |
| --- | --- | --- |
| OpenAI | Strict tool definitions | On automatically when the tool's schema is strict-compatible; `strict=True` forces it |
| Anthropic | Strict tool definitions | Off unless you opt in with `strict=True` |
| Bedrock | Strict tool spec, on supported models | Off unless you opt in with `strict=True` |
| Google (Gemini) | Gemini's `VALIDATED` function-calling mode | On for Gemini 2.5 and newer, because `VALIDATED` needs no schema changes; opt out with `strict=False` |

Other providers ignore the flag[^pydantic-docs-tools-advanced] Two asymmetries follow. Anthropic and Bedrock make strictness opt-in while OpenAI and Gemini make it the default, so the same agent is stricter on two providers than the other two without any code difference. And Gemini's choice is **request-wide**: any function or output tool with `strict=False` keeps the whole request on `AUTO`, so one loose tool relaxes every tool in that call[^pydantic-docs-tools-advanced] The page also flags `VALIDATED` as a preview Gemini feature[^pydantic-docs-tools-advanced]

### Strictness values

`strict` is `bool | None`, and `None` is the default that lets each provider decide[^pydantic-docs-tools-advanced]

- `True` — force strict mode wherever the provider supports it for this tool's schema.
- `False` — never use strict mode for this tool; on Google this keeps the whole request on `AUTO`.
- `None` — per-provider default: OpenAI enables it when the schema is compatible, Google uses `VALIDATED` on supported models, Anthropic and Bedrock stay off.

### The representability ceiling

Because strict generation guarantees the arguments match the schema exactly, not every schema can be expressed under it: some providers require every property in `required` and `additionalProperties: false`[^pydantic-docs-tools-advanced] A schema that cannot be represented may be transformed lossily for that tool, or the flag may simply be ignored — which is why the page recommends reading `strict=True` as "force strict mode wherever the provider can honour it" rather than as a guarantee[^pydantic-docs-tools-advanced]

To turn it on for many tools at once, the documented route is the agent-wide hook below, replacing each `ToolDefinition` with `strict=True`[^pydantic-docs-tools-advanced]

## Dynamic tools: prepare

A tool may be defined partly by a second function, `prepare`, which runs at each step of a run and either customizes the definition passed to the model or omits the tool from that step entirely[^pydantic-docs-tools-advanced] It is registered through the `prepare` keyword on `@agent.tool`, `@agent.tool_plain` or the `Tool` dataclass, and typed as `ToolPrepareFunc`: it receives `RunContext` and a pre-built `ToolDefinition`, and returns that definition, a modified copy made with `dataclasses.replace`, or `None`[^pydantic-docs-tools-advanced]

The two documented samples split the two uses[^pydantic-docs-tools-advanced]:

- **Withholding.** `only_if_42` returns `tool_def` only when `ctx.deps == 42`, so a run with `deps=41` prints `success (no tool calls)` and a run with `deps=42` calls the tool.
- **Rewriting.** `prepare_greet` edits `tool_def.parameters_json_schema['properties']['name']['description']` from `ctx.deps`, and the printed `TestModel.last_model_request_parameters.function_tools` shows the modified description on the wire.

## Agent-wide dynamic tools: prepare_tools

`prepare_tools` is the same idea over the whole tool list for a step: it takes `RunContext` and a list of `ToolDefinition` and returns the list to expose — the argument itself to keep everything, `[]` to expose nothing[^pydantic-docs-tools-advanced] It is typed as `ToolsPrepareFunc`, and the page's guidance is to modify the definitions given or copy them with `dataclasses.replace` rather than construct new ones[^pydantic-docs-tools-advanced] A separate `prepare_output_tools` function does the same for output tools[^pydantic-docs-tools-advanced]

The samples are attached as a capability, `capabilities=[PrepareTools(fn)]`[^pydantic-docs-tools-advanced]:

- **Bulk strictness.** `turn_on_strict_if_supported` replaces every definition with `strict=True` when the model's profile reports `supports_json_schema_output`. The page is careful about that flag: it describes native structured output, **not** strict tool definitions, and stands in here only "because there's no provider-agnostic strict-tools flag"[^pydantic-docs-tools-advanced] The assertions show the contrast — `strict is None` on a plain `TestModel`, truthy on a profile that claims JSON-schema output.
- **Filtering.** `filter_out_tools_by_name` drops `launch_potato` when `ctx.deps` is `True`, so the second run prints `success (no tool calls)`.

The documented uses are enabling or disabling tools by model, dependencies or other context, and modifying definitions globally — setting every tool strict, changing descriptions[^pydantic-docs-tools-advanced]

### Ordering

When both hooks exist, the per-tool `prepare` is applied to each tool first, and `prepare_tools` is then called with the resulting list[^pydantic-docs-tools-advanced] That order is what makes the agent-wide hook a genuine last word, and it is also why the `unless_tool_kind` decision recorded in [tool kinds](pydantic-ai-tool-kinds.md) is taken after `prepare_tools` has run[^pydantic-docs-tools-advanced]

## Evidence and coverage

The package is a single `index.md` capture (11,651 words as declared, 11,888 by local `wc -w`, 1,141 lines), inspected as text; `raw/tools-toolsets/tools-advanced/` holds no attachments, includes, downloads or supporting files. The capture names **no Pydantic AI version, author, publication date or licence**, so every API name, default and behaviour here is version-unknown, and its samples pin `openai:gpt-6.1-sol`, which no other capture here corroborates. Every external link — the `Tool.from_schema`, `Tool`, `Agent.tool`, `Agent.tool_plain`, `FunctionToolset.add_function`, `ToolDefinition`, `ToolPrepareFunc`, `ToolsPrepareFunc`, `RunContext`, `TestModel`, `ModelProfile`, `supports_json_schema_output`, `PrepareTools` and Gemini function-calling pages — was read as a link, not followed. Nothing was installed, no tool registered, no `prepare` hook run, no schema printed and no provider asked to enforce strictness, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule with `stale_after` set because the flag, the per-provider matrix and the hook signatures are release-sensitive.

## Relationships

- **Extends** [Pydantic AI function tools](pydantic-ai-function-tools.md): that page derives the definition from a signature and docstring, and this one covers the definition that derivation cannot produce, cannot constrain, or must change between steps.
- **Is one half of the tool contract with** [Pydantic AI tool execution](pydantic-ai-tool-execution.md): a `from_schema` tool has no argument validation there, and a `strict` tool is the only way to fail a schema violation before the call.
- **Is where** [Pydantic AI structured output](pydantic-ai-structured-output.md)'s `prepare_output_tools` and output-tool `strict` sit: output tools take the same `ToolDefinition` and the same agent-wide hook family.
- **Sits inside** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): `PrepareTools` and `UseThreadExecutor` are framework features expressed as capabilities, which is how an agent-wide tool hook is attached.
- **Shapes the cache** described in [Pydantic AI prompt caching](pydantic-ai-prompt-caching.md): tool definitions sit at the front of the prefix, so a `prepare` that rewrites one invalidates the cache from that point on.
- **Hands its deferred tools to** [Pydantic AI tool search](pydantic-ai-tool-search.md), which decides visibility by `defer_loading` and by reveal history rather than by a per-step hook.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>, `domain: pydantic.dev`, `language: en`, 11,651 words as declared and 11,888 by local `wc -w`; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, 1,141 lines, content digest sha256:8ba11efd. §"Custom Tool Schema" (raw lines 152–188) for `Tool.from_schema` and its fields, the poorly-documented-function motivation, the `foobar`/`sum` sample and the no-argument-validation rule; §"Strict Mode" (189–223) for the generation-time restriction, the `Reservation` sample, the registration surfaces, the provider table and the representability ceiling; §"Strictness values" (224–233) for `bool | None` and the Gemini request-wide `VALIDATED` rule; §"Dynamic Tools" (234–329) for `prepare`, `ToolPrepareFunc`, the `only_if_42.py` and `customize_name.py` samples and the printed `function_tools`; §"Agent-wide Dynamic Tools" (330–418) for `prepare_tools`, `ToolsPrepareFunc`, `prepare_output_tools`, the `PrepareTools` capability, the two samples, the `supports_json_schema_output` caveat and the ordering rule. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
