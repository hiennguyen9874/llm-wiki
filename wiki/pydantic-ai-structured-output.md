---
type: Concept
title: Pydantic AI structured output
description: How output_type decides what a run returns — the accepted types and output functions, the tool, native and prompted output modes with their end strategies, run-time Choices, validation context and output validators, plus BinaryImage and None.
tags: [pydantic-ai, agents, structured-output, output-modes]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T11:22:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-tools-advanced
    resource: ../raw/tools-toolsets/tools-advanced/index.md
    scope: ../raw/tools-toolsets/tools-advanced/
    kind: documentation
    revision: sha256:8ba11efdb429ad3648a9f6d4786a06ffc1bcc1da00c6a6635a5a19b091f9daf8
    title: "Advanced Tool Features"
  - id: pydantic-docs-output
    resource: ../raw/core-concepts/output/index.md
    scope: ../raw/core-concepts/output/
    kind: documentation
    revision: sha256:c70422e8bdd3e28400b6ca8c611c3097e9f9dc1a39a9328fc36e440fa3e1193f
    title: "Output"
  - id: pydantic-anthropic-2026
    resource: ../raw/models/anthropic/index.md
    scope: ../raw/models/anthropic/
    kind: documentation
    revision: sha256:4d8450abe7abd2367f5b9e163764ca396b66cadaf87d31aa5c1b5f08ca03a3ca
    title: "Anthropic"
---

**Reported, Pydantic AI version unspecified:** the value a run returns is plain text, structured data, an image, or the result of an output function called with model-supplied arguments, and it is wrapped in an `AgentRunResult` or `StreamedRunResult` that stays generic in that type so usage and message history travel with it. The `output_type` argument on `Agent` is the single declaration that decides which of those four a run ends with, and its default — tool calling against a Pydantic-built JSON schema — is the path most of this page describes.[^pydantic-docs-output]

A run ends when the model produces one of the output types, when plain text arrives if `str` is allowed or no output type is set, when a usage limit is exceeded, or early through `DeferredToolRequests` or `PendingModelResponse` in the output type — the deferral path covered by [deferred tool approval](pydantic-ai-deferred-approvals.md) and [conversation state](pydantic-ai-conversation-state.md).[^pydantic-docs-output]

## What `output_type` accepts

`output_type` takes one or more types or output functions: simple scalars, list and dict types (including `TypedDict` and `StructuredDict`), dataclasses, Pydantic models, and type unions — generally anything a Pydantic model accepts as a type hint — or a list of several choices.[^pydantic-docs-output]

- **Unions and lists become separate output tools.** Each member is registered with the model as its own output tool, which shrinks each schema and raises the chance of a correct response; the docs report this working well across a wide range of models.[^pydantic-docs-output]
- **Non-object schemas are wrapped.** A schema that is not `"object"` — `int`, `list[int]` — is wrapped in a single-element object so every tool the model sees is an object schema.[^pydantic-docs-output]
- **`str` decides whether text is allowed.** With no output type, or with `str` among the types, any plain text response is accepted as the output; without `str` the model is forced to return structured data or call an output function.[^pydantic-docs-output]
- **Pydantic does both halves.** It builds the JSON schema handed to the model and validates what comes back, exactly as for function tools.[^pydantic-docs-output]

```python
class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('google:gemini-3.8-flash', output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
```

Adding `str` to that declaration instead of forcing one shape produces a box-or-error agent: `output_type=[Box, str]` answers "Please provide the units for the dimensions" when the model cannot fill every field. The docs note that the union form `Box | str` needed explicit generic parameters on `Agent` plus a `# type: ignore` under mypy and older Pyright, which is why the list form appears in the samples.[^pydantic-docs-output]

### Output functions

An output function is called with arguments the model provides, and the run returns **what the function returns**. It differs from a function tool in three ways the docs state outright: the model is forced to call one, the call ends the run, and the result is never passed back to the model.[^pydantic-docs-output]

- Arguments are validated by Pydantic, with the optional validation context; the function may take `RunContext` first and may raise `ModelRetry` to ask for different arguments or a different output type.[^pydantic-docs-output]
- `ToolFailed` is **not** supported here — it is reserved for function-tool failures — so it behaves like any other exception: an `on_output_process_error` hook can recover from it, otherwise the run aborts.[^pydantic-docs-output]
- Registering the same callable as a tool as well is discouraged, since the model may then be unsure which one to call; a list can still mix functions with scalars and models.[^pydantic-docs-output]

The docs' `output_functions.py` sample routes a natural-language query to a SQL agent: the router's output function keeps `ctx.messages[:-1]` so the output-tool call is not replayed into the sub-agent, maps a `SQLFailure` output to a `ModelRetry`, and unwraps an `UnexpectedModelBehavior` whose `__cause__` is a `ModelRetry` so the router's model sees the sub-agent's complaint rather than a hard failure.[^pydantic-docs-output]

#### Text output and models that cannot write text

A function taking a string gets an output tool like any other function; wrapping it in `TextOutput(...)` makes the model supply that string as plain text instead, and the marker can sit in a list beside `ToolOutput` markers or unmarked types. The argument must be a `str` — a Pydantic model, dataclass or `TypedDict` argument, even with one `str` field, raises `UserError` when the agent is created — and an alias on that argument must not collide with another argument's name.[^pydantic-docs-output]

Some models have `supports_text_output=False` in their [profile](pydantic-ai-models-and-providers.md), decision models such as TypeSafe's Jev among them. For those, **any** output type that leaves text output available fails with `UserError` before a request is sent: the default `str`, a `str` among several types, a `TextOutput` function, and `PromptedOutput`, which asks for its structured data as text. Such a model needs a structured output type — a `BaseModel` or a union of them.[^pydantic-docs-output]

## The three output modes

Pydantic AI implements three ways to get structured data out of a model, selected by wrapping the output types in a marker class:[^pydantic-docs-output]

| Mode | How the schema reaches the model | Availability and limits |
| --- | --- | --- |
| Tool Output — the default | Each output type's JSON schema becomes the parameter schema of a special output tool | Supported by virtually all models; `ToolOutput(...)` renames the tool, adds a description, or toggles strict mode |
| Native Output | The provider's own structured-output feature, a JSON Schema response format the model is forced to match | Not universal, and often restricted: Gemini 3 can pair it with function tools, earlier Gemini cannot; Groq cannot; Anthropic compiles the schema into a grammar with complexity limits; OpenAI sends an oversized schema without strict mode |
| Prompted Output | The schema is written into the instructions and the model is trusted to follow it | Usable with every model, the least reliable, and the only option when a model lacks tool calling and native structured output |

Details that change behaviour inside those modes:[^pydantic-docs-output]

- **Descriptions default to docstrings.** `ToolOutput`'s description falls back to the model's or function's docstring, so the marker is usually unnecessary; field docstrings reach the model when `use_attribute_docstrings` is set, and an `Enum` mixing in `UseEnumMemberDocstrings` describes each member wherever the enum appears.[^pydantic-docs-output]
- **Retries are per output tool.** Each tool has its own counter, and the output side of the retry budget (`Agent(retries={'output': N})`, or per run) is the default per-tool limit, overridable per tool with `ToolOutput(Fruit, max_retries=2)`. The text-output path instead shares one global budget.[^pydantic-docs-output]
- **Output tools can be filtered per step.** An agent-wide `prepare_output_tools` of type `ToolsPrepareFunc` receives the `RunContext` and the `ToolDefinition` list ahead of each step and returns the definitions to expose; `[]` exposes none. It is the output counterpart of `prepare_tools`.[^pydantic-docs-output]
- **`PromptedOutput` carries a template.** `template=` replaces the default schema prompt and `template=False` disables it entirely, while a model API's JSON Mode is enabled automatically when it exists — but the model still has to obey the schema, and validation retries may not be enough.[^pydantic-docs-output]
- **Native Output on a thinking request.** On Anthropic, a structured `output_type` uses Native Output even without the marker class when the request thinks, unless the schema is over the grammar limits.[^pydantic-docs-output]

Anthropic is where that mode choice meets a size constraint, and the constraint counts across the whole request: every strict schema in a request — the Native Output schema, which is always strict, plus any function or output tool with `strict=True` — is compiled into a grammar whose limits cover strict tools, optional parameters and union-typed parameters together.[^pydantic-anthropic-2026] A bare structured `output_type` that would exceed them falls back to Tool Output, whose tool is not strict; an explicit `NativeOutput(...)` or `strict=True` raises `ModelRequestRejectedError` before anything is sent; and a schema within the explicit limits can still fail Anthropic's internal grammar-size limit with a 400 that may take up to 180 seconds to arrive.[^pydantic-anthropic-2026] The full rules, the first-request output-mode lock and the remedies — required fields, flatter models, `strict=True` only where needed, `ToolOutput` or `PromptedOutput` for a large schema — are in [Anthropic request constraints](anthropic-request-constraints.md).

### Tool calls that arrive alongside a final result

When one response carries both a final result and other tool calls, `end_strategy` decides what runs:[^pydantic-docs-output]

| Strategy | Output tools | Function tools — output succeeded | Function tools — every output failed |
| --- | --- | --- | --- |
| `'graceful'` (default) | Run in emission order; first success wins, later output tools skipped | Run, in parallel where possible, in emission order | Run; the run continues |
| `'early'` | Run in emission order; the run ends at the first success | Skipped | Run; the run continues |
| `'exhaustive'` | All run in parallel; first valid result by emission order wins | Run, in parallel | Run; the run continues |

`'graceful'` is the documented default because the function tools the model asked for still execute — their side effects happen and their results are available if the run continues — while later output tools are skipped so their side effects fire once. `'early'` skips those function tools for the fastest end, and `'exhaustive'` runs everything including output tools whose results are discarded. Two rules sit on top:[^pydantic-docs-output]

- **A failing function tool vetoes the output.** Under `'graceful'` and `'exhaustive'`, a function tool that raises `ModelRetry` or fails validation in the same response as a successful output tool means the output is **not** used; the retry goes back to the model, because the output may have been built on the failed call. This does not apply under `'early'`, where function tools did not run, or when [streaming](pydantic-ai-streamed-output.md), where the first matching output is committed immediately.[^pydantic-docs-output]
- **`ToolOutput(sequential=True)` is a barrier.** Under `'exhaustive'`, it makes the output tool wait until the response's other function tools finish — the output-side counterpart of the function-tool flag.[^pydantic-docs-output]

## Custom schemas and run-time choices

Two helpers cover shapes a Pydantic model cannot express:[^pydantic-docs-output]

- **`StructuredDict(schema, name=..., description=...)`** returns a `dict[str, Any]` subclass carrying a JSON schema from an external or generated source. Pydantic AI performs **no validation** of the returned object — constraints such as required fields and integer ranges are the model's to honour — so defensive reads and an output validator are the documented mitigation.[^pydantic-docs-output]
- **`Choices({option: meaning, ...}, name=..., description=...)`** covers a set that does not exist until the run is under way, such as on-screen actions or search results. `Literal` and `Enum` are for sets known at authoring time and give exhaustiveness checking; `Choices` carries each option's meaning into the schema and validates the answer against the keys, typed `str`. A sequence of keys instead of a mapping asks the same question with a plain `enum` and describes nothing.[^pydantic-docs-output]

```python
Intent = Choices(
    {'refund': 'The customer wants their money back.',
     'replace': 'The customer wants a working unit instead.',
     'escalate': 'Nobody on this tier can resolve it.'},
    name='customer_intent',
)

class Triage(BaseModel):
    intent: Annotated[str, Intent]     # a type checker sees str
    summary: str
```

Because a run-time type fails in an annotation, the field or tool parameter takes `Annotated`: `Annotated[str, Intent]` for `Choices`, `Annotated[dict[str, Any], Person]` for a `StructuredDict`, with Pydantic reading schema and validation from the metadata.[^pydantic-docs-output]

Options can stand for values or actions instead of being the answer:[^pydantic-docs-output]

- **`Choice(description, value=doc)`** makes the model pick the key while the output is the value — the sample maps `'rfc-6265'` to a `Doc` and returns the dataclass.[^pydantic-docs-output]
- **A callable value is called**, the way an output function is, so the run's output is the action's return and no dispatch table sits between the model's pick and the effect (the sample returns `'clicked login'`). The action takes no arguments, so bind them with `functools.partial` or a closure; it may be `async` and may raise `ModelRetry`.[^pydantic-docs-output]

## Validation context and output validators

Two hooks let validation see more than the output itself — both are where this page meets [dependencies](pydantic-ai-dependencies.md):[^pydantic-docs-output]

- **`validation_context`** on `Agent` accepts either a Pydantic context object, used as-is, or a **callable taking the `RunContext`** that is invoked before each validation, so the context can be rebuilt per run. It applies to structured outputs **and** tool arguments. The docs' sample validator adds the context number to the model's value (`Value(x=15)` for a model answer of 5 plus `10`), the second variant reading `10` from `ctx.deps.increment`.[^pydantic-docs-output]
- **`@agent.output_validator`** adds a function the Pydantic validators cannot express, notably asynchronous validation requiring IO. Each `ModelRetry` it raises consumes one unit of the output retry budget, which defaults to `1` and is set by `Agent(retries={'output': N})`, per run, or per output tool. Inside the validator `ctx.max_retries` is the limit that will actually stop the run — the global budget on the text path, the per-tool limit on the tool path — and `ctx.retry` is the global counter, so it stays consistent across output-tool switches in one run.[^pydantic-docs-output]
- **Same `ToolFailed` exclusion**: an output validator cannot use it, and an `on_output_process_error` hook is the recovery point.[^pydantic-docs-output]
- **Per-type logic belongs in output functions.** The docs recommend an output function instead of `isinstance` branches inside a validator, and `TextOutput` when raw text needs processing before it becomes the answer.[^pydantic-docs-output]

The `sql_gen.py` sample validates by asking the database: `EXPLAIN` on the generated query raises `ModelRetry('Invalid query: …')` on `QueryError`, and an `InvalidRequest` output passes through untouched.[^pydantic-docs-output]

## Image output and `None`

Setting `output_type=BinaryImage` makes a generated image the run's output; image-generation native tools — `ImageGenerationTool`, or OpenAI's code-execution tool drawing a chart — enable it, and `ImageGenerationTool` is turned on automatically when none is named. `BinaryImage` is the same value type the [image generation](pydantic-ai-image-generation.md) entry points return.[^pydantic-docs-output]

An agent that only sometimes draws declares `BinaryImage | str`: when the model produces both, the **image** wins and the text stays reachable on `result.response.text`. An agent whose work happens entirely in tools — update a record, then stop — declares `str | None`, which is the canonical optional output: the only signal for `None` is a response with no text at all, including one whose text parts are empty strings (as some OpenAI-compatible gateways send) or one carrying only thinking content as Anthropic and reasoning models do. Output validators still run with `None`, so a validator can reject it.[^pydantic-docs-output]

`None` elsewhere in the declaration follows two paths:[^pydantic-docs-output]

- **Bare unions in tool mode** — `int | None`, `[int, float, None]`, `[ToolOutput(Foo), None]` — get a dedicated `final_result_None` output tool so the model can commit through a call, while an empty, blank-text or thinking-only response is still also read as `None`.
- **Explicit mode markers** — `ToolOutput(int | None)`, `NativeOutput([int, None])`, `PromptedOutput([int, None])` — put `None` into the generated schema as a branch; the model commits by calling with `null` or selecting the `None` branch, and an empty response is **not** accepted once a structured mode is chosen.

## Evidence and coverage

The sole artifact is the Pydantic documentation capture `index.md` (8,218 words as declared), inspected as text; there are no attachments, includes, downloads or supporting files in the package. It states no Pydantic AI version, author, publication date or licence, so every API name here is version-unknown, and its samples pin model names (`google:gemini-3.8-flash`, `openai:gpt-6-luna`, `openai:gpt-6.1-sol`, `openai-responses:gpt-6.1-sol`, `anthropic:claude-opus-5-5`, `google:gemini-3.8-flash`) that no other capture in this wiki corroborates. Every external link — the `Agent`, `RunContext`, `ToolDefinition`, `ToolsPrepareFunc`, `AgentRetries`, `output`, `result`, `messages`, `exceptions`, `profiles` and `native_tools` API pages, the agent, tools, tools-advanced, hooks, batch, message-history, usage and native-tools pages, the model pages for Anthropic, OpenAI, Groq and Gemini structured output, and the SQL-generation example — was read as a link, not followed, so each signature, default and error's exact behaviour is unverified here. Nothing was installed, no agent was constructed, no run executed and no validator or output function called, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule, and `stale_after` is set because `output_type`, the marker classes and the retry surface are release-sensitive.

## Relationships

- **Depends on** [Pydantic AI dependencies](pydantic-ai-dependencies.md): `validation_context` may be a callable over `RunContext`, and output validators take `RunContext` as their first parameter, so a run's dependencies can seed validation.
- **Uses** [models and providers](pydantic-ai-models-and-providers.md): a mode is only available when the model and its profile support it, and `supports_text_output=False` is what turns a text-capable `output_type` into `UserError`.
- **Constrained on Anthropic by** [Anthropic request constraints](anthropic-request-constraints.md), which records the strict-schema grammar limits, the silent Native-Output-to-Tool-Output fallback for a bare `output_type`, and the pre-send `ModelRequestRejectedError` an explicit `strict=True` gets instead.
- **Detailed by** [Pydantic AI streamed output](pydantic-ai-streamed-output.md): streaming calls output functions and validators repeatedly and yields validated partial snapshots of the same schemas.
- **Shares its description pipeline with** [Pydantic AI function tools](pydantic-ai-function-tools.md): the same signature-and-docstring derivation, `use_attribute_docstrings` inheritance and `UseEnumMemberDocstrings` mix-in decide what the model reads for a tool and for an output type, and the inlined-`$defs` ceiling counts both alike.
- **See also** [Pydantic AI output truncation](pydantic-ai-output-truncation.md): a response cut off at the token limit is validated like any other, so the mode decides whether it surfaces as `OutputTokenLimitExceeded`, `IncompleteToolCall`, or plain truncated text.
- **Related to** [Pydantic AI image generation](pydantic-ai-image-generation.md): `BinaryImage` is one legal `output_type`, so an agent can return a generated image without a separate generator call.
- **Renders through** [retry records in message history](pydantic-ai-retry-history.md), which owns how a text-path retry becomes a `RetryFeedbackPart` with no stored wording and how each provider is then sent it.
- **Shares its output-tool mechanics with** [Pydantic AI tool execution, retries and failures](pydantic-ai-tool-execution.md), which owns the tool-versus-output retry precedence, the `ToolFailed`-is-fatal rule at output validators, and the `end_strategy` consequences for output calls made in parallel with a final result[^pydantic-docs-tools-advanced].
- **Excludes provider** [citations](pydantic-ai-citations.md): citations attach to text, so a structured `output_type` — including `[str, Answer]` — returns tool-call arguments that cannot carry them, and on Anthropic with `Citations()` attached a structured output gets no document citations while a forced `tool_choice` with a document in the request raises `UserError` before sending.
- **Ends early through** [Pydantic AI deferred tool approval](pydantic-ai-deferred-approvals.md): `DeferredToolRequests` in the output type makes a run stop for approval instead of producing a final value.

[^pydantic-docs-output]: Pydantic Docs, "Output" (`https://pydantic.dev/docs/ai/core-concepts/output/`, 8,218 words as declared); local capture `raw/core-concepts/output/index.md`, content digest sha256:c70422e8. Opening paragraphs (lines 10–17) for the four output kinds, the `AgentRunResult`/`StreamedRunResult` wrappers, the run-end conditions and the early ends through `DeferredToolRequests` and `PendingModelResponse`; "Structured output data" (lines 42–116) for the accepted types, separate output tools per union member, object wrapping, the `str` rule, Pydantic schema and validation, and the two typed samples; "Output functions" (lines 117–231) for forced call, run end, no result fed back, argument validation, `RunContext` and `ModelRetry`, the `ToolFailed` exclusion and the `on_output_process_error` recovery, the tool-registration warning, and the SQL-router sample; "Text output" (lines 232–262) for `TextOutput`, mixed lists, the `str`-argument `UserError` and alias rule; "Handling partial output in output functions" (lines 263–304) for the repeated calls and `partial_output`; "Output modes" (lines 305–432) for the three modes, `ToolOutput` naming and strict mode, docstring-derived descriptions, `use_attribute_docstrings`, `UseEnumMemberDocstrings`, per-tool retry counters and `ToolOutput(max_retries=...)`, `prepare_output_tools`, and the Native and Prompted restrictions per provider including Anthropic's thinking-request behaviour and `template`/`template=False`; "Tool calls alongside a final result" (lines 433–458) for the three end strategies, the function-tool veto and `sequential=True`; "Custom JSON schema" (lines 459–489) for `StructuredDict` and the absent validation; "Choices known only at run time" (lines 490–619) for `Choices`, the `Literal`/`Enum` comparison, the `Annotated` pattern, `Choice(value=...)` and callable actions; "Validation context" (lines 620–670) for the context object and the `RunContext` callable over outputs and tool arguments, and the `increment_value` samples; "Output validators" (lines 671–724) for the decorator, the retry budget and its three set points, `ctx.max_retries`/`ctx.retry`, the `ToolFailed` exclusion and the per-type guidance, plus the `sql_gen.py` sample; "Image output" (lines 764–805) for `BinaryImage`, the automatic native tool and the union precedence with `ModelResponse.text`; "Optional output" (lines 806–837) for `str | None`, the empty/blank/thinking-only signals, validators running with `None`, and the tool-mode `final_result_None` versus explicit-marker paths. Excerpted samples were read, not executed. Evidence class: **Reported** — vendor documentation naming no release version.

[^pydantic-anthropic-2026]: Pydantic Docs, "Anthropic", <https://pydantic.dev/docs/ai/models/anthropic/>, 8,470 words as declared and 8,506 by local `wc -w`, no publication date and no Pydantic AI version named; local capture `raw/models/anthropic/index.md`, 995 lines, content digest sha256:4d8450ab. §"Forced tool choice" (raw lines 670–684) for the bare `output_type` selecting Native Output on a thinking request, the model list that thinks by default, and the first-request mode lock; §"Schema complexity limits" (685–706) for the compiled-grammar limits counted across all strict schemas, the always-strict Native Output schema, the `strict=True` tool scope, Prompted Output's exemption, the bare-`output_type` fallback to Tool Output, the pre-send `ModelRequestRejectedError` for explicit strictness, the 180-second compilation ceiling with its `ModelHTTPError` and `hint`, and the remedies. Evidence class: **Reported** — vendor documentation; no schema was compiled and no request sent.

[^pydantic-docs-tools-advanced]: Pydantic Docs, "Advanced Tool Features" (<https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/>; no publication date, author, licence or Pydantic AI version); local capture `raw/tools-toolsets/tools-advanced/index.md`, content digest sha256:8ba11efd. §"Tool Execution, Retries, and Failures" (raw lines 556–566) and §"Which retry limit wins" (586–601) for the tool-versus-output retry budgets and their seven precedence layers; §"Reporting a Failed Tool Result" (602–627) for `ToolFailed` being an ordinary, run-aborting exception at output functions and output validators; §"Output Tool Calls" (830–835) for the `'graceful'`/`'exhaustive'` end strategies. Evidence class: **Reported** — vendor documentation naming no version, date, author or licence.
