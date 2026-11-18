---
type: Concept
title: Pydantic AI agent specs
description: How Pydantic AI defines an agent declaratively in YAML or JSON — AgentSpec fields, from_file and from_spec with their override and merge rules, template strings validated against a deps schema, the three capability syntax forms, the serializable capability subset, and the trust boundary a spec file carries.
tags: [pydantic-ai, agents, configuration, agent-spec]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T04:41:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-agent-spec
    resource: ../raw/core-concepts/agent-spec/index.md
    scope: ../raw/core-concepts/agent-spec/
    kind: documentation
    title: "Agent Specs"
  - id: pydantic-e2b-sandbox-docs
    resource: ../raw/harness/e2b-sandbox/index.md
    scope: ../raw/harness/e2b-sandbox/
    kind: documentation
    revision: sha256:18ccb7ad3358aefb277f685880ee331e4f8fa646f9630816bbeaca4103fe3b53
    title: "E2B Sandbox"
---

**Reported, Pydantic AI version unspecified:** an agent spec is a YAML or JSON document that declares a whole agent — model, instructions, model settings, capabilities and the rest — so the agent can be loaded in one line instead of being built in Python. `Agent.from_file('agent.yaml')` returns a constructed agent; `Agent.from_spec()` takes the same structure as a dict or an `AgentSpec` instance plus keyword arguments that supplement or override it. The documentation's four reasons are separation of configuration from application code, letting non-developers such as prompt engineers and domain experts configure agents, storing agent definitions beside other config files, and sharing those definitions across teams or projects.[^pydantic-docs-agent-spec]

## Spec shape and the AgentSpec reference

A minimal spec is just the four things a constructor call would name — model, instructions, model settings and capabilities:[^pydantic-docs-agent-spec]

```yaml
model: anthropic:claude-opus-5-5
instructions: You are a helpful research assistant.
model_settings:
  max_tokens: 8192
capabilities:
  - WebSearch:
      local: duckduckgo
  - Thinking:
      effort: high
```

`AgentSpec` is the model behind that file, and its fields are the full set of things a spec may carry:[^pydantic-docs-agent-spec]

| Field | Type | Description |
| --- | --- | --- |
| `model` | `str \| None` | Model name in the same `<provider>:<model>` form Python uses |
| `name` | `str \| None` | Agent name |
| `description` | `str \| None` | Agent description; supports templates |
| `instructions` | `str \| list[str] \| None` | Instructions; supports templates |
| `model_settings` | `dict \| None` | Model run settings |
| `capabilities` | `list` | Capabilities, in the spec syntax below |
| `deps_schema` | `dict \| None` | JSON Schema used only to validate template variable names |
| `output_schema` | `dict \| None` | JSON Schema for structured output |
| `retries` | `int \| AgentRetries \| None` | Retry budgets for tools and for output validation; an integer applies to both |
| `end_strategy` | `EndStrategy` | When to stop: `'early'`, `'graceful'` or `'exhaustive'` |
| `tool_timeout` | `float \| None` | Default tool timeout in seconds |
| `instrument` | `bool \| None` | Enable Logfire instrumentation |
| `metadata` | `dict \| None` | Agent run metadata |

Two fields deserve separate treatment because they look like validation and are not. `deps_schema` supplies a JSON Schema that checks template variable names at construction time when no Python `deps_type` exists — it does **not** validate the deps object at runtime, only that `{{user_name}}`-style variables correspond to properties the schema declares. `output_schema`, when no `output_type` keyword argument is passed to `from_spec`, builds a `StructuredDict` output type under the hood: the JSON Schema goes to the model API so the model knows the structure, and the response comes back as a `dict[str, Any]`.[^pydantic-docs-agent-spec]

## Loading and override semantics

`Agent.from_spec` accepts a dict or an `AgentSpec` and extra keyword arguments, and the two interact by field, not by wholesale replacement:[^pydantic-docs-agent-spec]

| Keyword argument | Interaction with the spec |
| --- | --- |
| Scalar fields (`model`, `name`, `end_strategy`, `retries`, …) | Keyword value overrides the spec value when provided |
| `instructions` | Merged: spec instructions first, then keyword argument instructions |
| `capabilities` | Merged: spec capabilities first, then keyword argument capabilities |
| `model_settings` | Merged additively, keyword settings overriding matching spec settings |
| `output_type` | Takes precedence over the spec's `output_schema` |

Because instructions and capabilities are merged rather than replaced, the Python side of an application can append its own prompt or register runtime-only capabilities on top of a shared spec without editing the file. The spec may also omit `model` entirely and leave it to `from_spec` or to the run. When `deps_type` is passed, template strings in the spec's `instructions`, `description` and capability arguments are compiled and validated against that type at construction time. For control over loading, `AgentSpec.from_file` parses the spec separately, so it can be inspected before it reaches `Agent.from_spec`.[^pydantic-docs-agent-spec]

## Where specs come from

The documentation is explicit that a spec has the same authority as the code that builds the agent: it chooses the model and provider, the instructions, and every capability with its arguments, including the endpoints the agent connects to. An `MCP` capability connects to whatever server URL the spec names, `localhost` and private addresses included, with the network access of the machine the agent runs on. So specs are loaded only from trusted sources, and an application that accepts specs from its users loads each one with `AgentSpec.from_file` or `AgentSpec.model_validate` and checks every entry in `spec.capabilities` — its `name` and its `kwargs`, such as an `MCP` `url` — against what that user may use before passing it to `Agent.from_spec`.[^pydantic-docs-agent-spec]

That is a client-side authorisation requirement rather than a sandbox: the check is the caller's, and the trusted-spec path performs no checking at all. It sits with the same reasoning recorded for [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md), where server instructions are treated as a trust surface.

## Template strings and dependencies

Any spec string containing `{{` is converted to a [`TemplateStr`](pydantic-ai-dependencies.md) automatically, with variables resolved from the fields of the `deps` object at runtime:[^pydantic-docs-agent-spec]

```yaml
deps_schema:
  type: object
  properties:
    user_name:
      type: string
  required: [user_name]
output_schema:
  type: object
  properties:
    answer:
      type: string
    confidence:
      type: number
  required: [answer, confidence]
instructions: "You are helping {{user_name}}. Always include a confidence score."
```

This is the spec-side counterpart of the dependency-injection route compiled in [Pydantic AI dependencies](pydantic-ai-dependencies.md): in Python code `TemplateStr` can be used explicitly, but the documentation prefers a callable taking `RunContext` there, because a callable gives IDE autocomplete and type checking — an advantage a spec file cannot have, which is why templates exist in specs at all.[^pydantic-docs-agent-spec]

## Capability spec syntax

Capabilities appear in a spec in three forms, each lowering to a `from_spec()` call on the capability class:[^pydantic-docs-agent-spec]

| Form | Call |
| --- | --- |
| `'MyCapability'` | `MyCapability.from_spec()` — no arguments |
| `{'MyCapability': value}` | `MyCapability.from_spec(value)` — one positional argument |
| `{'MyCapability': {key: value, ...}}` | `MyCapability.from_spec(**kwargs)` — keyword arguments |

The middle form has an ambiguity the documentation resolves explicitly: a mapping with string keys is read as keyword arguments, so a single positional argument that happens to be such a mapping must be written in the keyword form instead.[^pydantic-docs-agent-spec]

Not every capability is reachable from a spec. The serializable ones the documentation names are `Thinking`, `Caching`, `Instrumentation`, `WebSearch`, `WebFetch`, `ImageGeneration`, `XSearch`, `MCP`, `ToolSearch`, `PrefixTools`, `NativeTool`, `IncludeToolReturnSchemas`, `SetToolMetadata`, `RaiseContentFilterError`, `ReinjectSystemPrompt`, `LocalWorkspace`, `WindowsWorkspace`, `ModelFallback`, `RetryOnModelErrors` and `BatchModelRequests`; the remaining built-in capabilities take non-serializable arguments — callables, toolset objects — and exist only in Python code. Custom capabilities opt in by publishing themselves for spec use, which is the `from_spec` side of the [capability primitive](pydantic-ai-capability-primitive.md).[^pydantic-docs-agent-spec]

This subset boundary is why several pages in this wiki have an agent-spec section and a Python-only remainder: [image generation](pydantic-ai-image-generation.md) keeps a direct model name through `ImageGeneration.from_spec()` but leaves `ImageGenerator` objects in Python, and [Harness planning](pydantic-ai-harness-planning.md) persists a plan through a spec while leaving a database pool or Redis client to code. The boundary cuts through the Harness sandboxes too: [Modal sandbox](pydantic-ai-harness-modal-sandbox.md) compiles its own `from_spec`, so a spec can set the sandbox's timeouts, image registry tag, `working_dir`, `env` and file authority, but not its `client`; [E2B sandbox](pydantic-ai-harness-e2b-sandbox.md) does the same with a ten-field `from_spec` (`id`, `description`, `defer_loading`, `template`, `allow_internet_access`, `sandbox_timeout`, `working_dir`, `env`, `authority`, `path_authority`) and adds a second exclusion, `network`; a subclass that inherits the signature instead falls back to the variadic base and publishes only the bare capability name[^pydantic-e2b-sandbox-docs] — and the twenty-name list above, which is what the agent-spec page enumerates, does not name either sandbox (**Synthesis**: neither capture claims that list is exhaustive).

## Saving specs

`AgentSpec.to_file` writes a spec back out as YAML or JSON and, by default, also generates a companion JSON Schema file — `agent.yaml` next to `agent_schema.json` in the documentation's example. The schema enables autocompletion and validation in editors that speak the YAML Language Server protocol; `schema_path=None` skips it. Round-tripping is therefore not lossless for everything a Python `Agent` can hold: only what `AgentSpec` models survives, which is the same serializable subset the capability table above bounds.[^pydantic-docs-agent-spec]

## Evidence and coverage

The source is a single `index.md` capture under `raw/core-concepts/agent-spec/` with no attachments, includes, downloads or supporting files; it declares 1,098 words, measured 1,186 by `wc -w` including frontmatter and markup, and carries content digest sha256:e5758e97. It names no Pydantic AI version, author, publication date or licence. Every external link — `Agent.from_file`, `Agent.from_spec`, `AgentSpec.from_file`, `AgentSpec.to_file`, `AgentRetries`, `TemplateStr`, the `Thinking`/`Caching`/`WebSearch`/`MCP` capability API entries, the models, instructions, dependencies, output, template, capability-overview and publishing-capabilities pages, and the model-fallback, retry-on-model-errors and batch agent-spec sections — was read as a link, not followed, so signatures, defaults and error text for each are unverified here. The sibling captures under `raw/core-concepts/` were left to their own ingests; three of them (`dependencies`, `output`, `hooks`) are already compiled elsewhere in this wiki and are linked rather than restated.

## Limits

- Vendor documentation naming no Pydantic AI version, so the page is `draft` under the `pydantic-ai` domain rule and `stale_after` is set: `AgentSpec` fields, the merge rules and the serializable capability list are release-sensitive surface.
- The capture states no YAML-parser or JSON-Schema-validator identity, so where a malformed spec fails, and with which exception, is unstated.
- The `{{` auto-conversion rule is given without a stated escape mechanism, so how a literal `{{` is written in a spec is unknown here.
- The capability forms are documented with `from_spec`, and the base contract a custom capability must implement to be spec-loadable — a `get_serialization_name` (the class name by default) and a constructor taking serializable arguments, with `from_spec` defaulting to `cls(*args, **kwargs)` and `custom_capability_types` registering the type — is now compiled in [custom capabilities](pydantic-ai-custom-capabilities.md); the publishing-capabilities page itself was still not read.
- `deps_schema`'s checking is described as construction-time only; whether a missing runtime deps field then fails during a run, and how, is unstated.
- The examples pin `anthropic:claude-opus-5-5` and `openai:gpt-6.1-sol`-era aliases; `claude-opus-5-5` is not corroborated by any other capture in this wiki.
- Evidence class: **Reported** throughout, and **Synthesis** only for the two readings explicitly marked as such in prose (the merge rules' effect on shared specs, and the client-side-authorisation framing). Nothing was installed, no spec file parsed, no agent constructed and no capability loaded from `from_spec`.

## Relationships

- **Depends on** the [capability primitive](pydantic-ai-capability-primitive.md) for the `from_spec` serialization contract that decides which capabilities a spec may name.
- **Is extended by** [custom capabilities](pydantic-ai-custom-capabilities.md), which owns `get_serialization_name`, the `from_spec` override rule for non-serializable constructor arguments, and the `custom_capability_types` registration this page's custom-capability paragraph points at.
- **Uses** [Pydantic AI dependencies](pydantic-ai-dependencies.md) for the deps object that template strings resolve against, and for `TemplateStr` itself.
- **Produces** the [structured output](pydantic-ai-structured-output.md) contract through `output_schema`, lowered to `StructuredDict`.
- **Names** [same-model retries](pydantic-ai-retry-on-model-errors.md) among the serializable capabilities: `RetryOnModelErrors` takes no callable arguments, so a spec configures it by name while [provider SDK retries](pydantic-ai-provider-sdk-retries.md) stay a model setting.
- **Bounds** what [image generation](pydantic-ai-image-generation.md), [Harness planning](pydantic-ai-harness-planning.md) and the [Modal](pydantic-ai-harness-modal-sandbox.md) and [E2B](pydantic-ai-harness-e2b-sandbox.md) sandboxes may declare outside Python — a spec's fields without an image generator, a store without a pool, a sandbox without a client or a network proxy.
- **Contrasts with** the code-built agent: a spec carries the building authority of code, and the trusted-versus-user-supplied split here is the declarative analogue of the configuration surface described in [Pydantic AI models and providers](pydantic-ai-models-and-providers.md).

[^pydantic-docs-agent-spec]: Pydantic Docs, "Agent Specs" (`https://pydantic.dev/docs/ai/core-concepts/agent-spec/`, 1,098 words as declared, 1,186 by local `wc -w` including frontmatter and markup, language `en`, no publication date, author, licence or Pydantic AI version); local capture `raw/core-concepts/agent-spec/index.md`, content digest sha256:e5758e97. §intro (lines 9–18) for the one-line declarative definition and the four stated uses; §"Defining a spec" (lines 20–37) for the `agent.yaml` sample; §"Loading specs" (lines 38–86) for `Agent.from_file`, the `Agent.from_spec` `UserContext` sample, the five-row keyword-versus-spec interaction list, the omittable `model`, the `deps_type` compile-and-validate rule, and `AgentSpec.from_file`; §"Where specs come from" (lines 87–92) for the code-equivalent authority, the MCP `url` and `localhost` example, and the `AgentSpec.from_file`/`model_validate` plus per-capability `name`/`kwargs` check; §"Template strings" (lines 93–126) for automatic `{{` conversion, deps-field resolution, construction-time validation and the callable-over-`TemplateStr` advice; §"Capability spec syntax" (lines 127–136) for the three forms, the string-keyed-mapping rule, the twenty-name serializable list and the non-serializable remainder; §"Custom capabilities in specs" (lines 137–140) for the publishing pointer; §"AgentSpec reference" (lines 141–160) for the thirteen field rows; §"deps_schema" (lines 161–164) for the construction-time-only scope; §"output_schema" (lines 165–192) for `StructuredDict`, the schema sent to the model API and the `dict[str, Any]` result plus the `agent_with_schema.yaml` sample; §"Saving specs" (lines 193–213) for `AgentSpec.to_file`, the companion `agent_schema.json`, the YAML Language Server reference and `schema_path=None`. Evidence class: **Reported** — vendor documentation naming no release version; no package installed, no spec parsed, no agent constructed.

[^pydantic-e2b-sandbox-docs]: Pydantic Docs, "E2B Sandbox", <https://pydantic.dev/docs/ai/harness/e2b-sandbox/>; local capture `raw/harness/e2b-sandbox/index.md`, content digest sha256:18ccb7ad, 4,125 words as declared (4,194 by `wc -w`), 644 lines, no release version, date, author or licence. Locators: 383–391 for "this capability supplies execution only"; 461–484 for the `from_spec` signature with its ten named fields and the `TYPE_CHECKING` fallback that leaves a subclass publishing only `'E2BSandbox'`; 302–316 for the configuration table that the field list mirrors; 451–458 for `network`'s attribute and its "a spec cannot set them" rule. Evidence class: **Reported** — vendor documentation for its own package, with no spec parsed or sandbox created.
