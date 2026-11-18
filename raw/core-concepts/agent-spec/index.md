---
title: "Agent Specs"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/agent-spec/"
domain: "pydantic.dev"
language: "en"
description: "Define Pydantic AI agents declaratively in YAML or JSON (model, instructions, capabilities) and load them with one line, without agent construction code."
word_count: 1098
---

Agent specs let you define agents declaratively in YAML or JSON — [model](https://pydantic.dev/docs/ai/models/overview/), [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), [capabilities](https://pydantic.dev/docs/ai/capabilities/overview/), and all. One line to load, no Python agent construction code required.

This is useful for:

- Separating agent configuration from application code
- Letting non-developers (prompt engineers, domain experts) configure agents
- Storing agent definitions alongside other config files
- Sharing agent configurations across teams or projects

## Defining a spec

A spec file defines the agent’s configuration in YAML or JSON:

agent.yaml

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

## Loading specs

[`Agent.from_file`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.from_file) loads a spec from a YAML or JSON file and constructs an agent:

from\_file\_example.py

```python
from pydantic_ai import Agent

agent = Agent.from_file('agent.yaml')
```

[`Agent.from_spec`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.from_spec) accepts a dict or [`AgentSpec`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentSpec) instance and supports additional keyword arguments that supplement or override the spec:

from\_spec\_example.py

```python
from dataclasses import dataclass

from pydantic_ai import Agent

@dataclass
class UserContext:
    user_name: str

agent = Agent.from_spec(
    {
        'model': 'anthropic:claude-opus-5-5',
        'instructions': 'You are helping {{user_name}}.',
        'capabilities': [{'WebSearch': {'local': 'duckduckgo'}}],
    },
    deps_type=UserContext,
)
```

Keyword arguments interact with spec fields as follows:

- **Scalar fields** (`model`, `name`, `end_strategy`, etc.) — the keyword argument overrides the spec value when provided. For retry budgets, the `retries` keyword argument overrides the spec’s `retries` value.
- **`instructions`** — merged: spec instructions come first, then keyword argument instructions.
- **`capabilities`** — merged: spec capabilities come first, then keyword argument capabilities.
- **`model_settings`** — merged additively: keyword argument settings override matching spec settings.
- **`output_type`** — takes precedence over `output_schema` from the spec.

The spec may omit `model`; it can instead be supplied to `Agent.from_spec` or when running the agent.

When `deps_type` is passed, [template strings](#template-strings) in the spec’s `instructions`, `description`, and capability arguments are compiled and validated against the deps type at construction time.

For more control over spec loading, use [`AgentSpec.from_file`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentSpec.from_file) to load the spec separately before passing it to `Agent.from_spec`.

### Where specs come from

A spec has the same authority as the code that builds the agent. It chooses the model and provider, the instructions, and every capability with its arguments, including the endpoints the agent connects to. For example, an [`MCP`](https://pydantic.dev/docs/ai/capabilities/mcp/) capability connects to the server URL the spec names, `localhost` and private addresses included, with the network access of the machine the agent runs on.

Load specs only from sources you trust. If your application accepts specs from its users, load each one with [`AgentSpec.from_file`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentSpec.from_file) or `AgentSpec.model_validate`, and check every entry in `spec.capabilities` (its `name`, and its `kwargs` such as an `MCP` `url`) against what that user may use before passing it to `Agent.from_spec`.

## Template strings

[`TemplateStr`](https://pydantic.dev/docs/ai/api/pydantic-ai/template/#pydantic_ai.template.TemplateStr) provides Handlebars-style templates (`{{variable}}`) that are rendered against the agent’s [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/) at runtime. In spec files, strings containing `{{` are automatically converted to template strings:

```yaml
instructions: "You are assisting {{name}}, who is a {{role}}."
```

Template variables are resolved from the fields of the `deps` object. When a `deps_type` (or [`deps_schema`](#deps_schema)) is provided, template variable names are validated at construction time.

In Python code, [`TemplateStr`](https://pydantic.dev/docs/ai/api/pydantic-ai/template/#pydantic_ai.template.TemplateStr) can be used explicitly, but a callable with [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) is generally preferred for IDE autocomplete and type checking:

template\_instructions.py

```python
from dataclasses import dataclass

from pydantic_ai import Agent, TemplateStr

@dataclass
class UserProfile:
    name: str
    role: str

agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=UserProfile,
    instructions=TemplateStr('You are assisting {{name}}, who is a {{role}}.'),
)
result = agent.run_sync('hello', deps=UserProfile(name='Alice', role='engineer'))
print(result.output)
#> Hello! How can I help you today?
```

## Capability spec syntax

Capabilities in specs support three forms:

- `'MyCapability'` — no arguments, calls `MyCapability.from_spec()`
- `{'MyCapability': value}` — single positional argument, calls `MyCapability.from_spec(value)`. A mapping with string keys is read as keyword arguments instead, so a single argument that is such a mapping uses the keyword arguments form below.
- `{'MyCapability': {key: value, ...}}` — keyword arguments, calls `MyCapability.from_spec(**kwargs)`

These built-in capabilities can be declared in specs: [`Thinking`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Thinking), [`Caching`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Caching), [`Instrumentation`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.Instrumentation), [`WebSearch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.WebSearch), [`WebFetch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.WebFetch), [`ImageGeneration`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ImageGeneration), [`XSearch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.XSearch), [`MCP`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.MCP), [`ToolSearch`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ToolSearch), [`PrefixTools`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.PrefixTools), [`NativeTool`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.NativeTool), [`IncludeToolReturnSchemas`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.IncludeToolReturnSchemas), [`SetToolMetadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.SetToolMetadata), [`RaiseContentFilterError`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.RaiseContentFilterError), [`ReinjectSystemPrompt`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ReinjectSystemPrompt), [`LocalWorkspace`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.LocalWorkspace), [`WindowsWorkspace`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.WindowsWorkspace), [`ModelFallback`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.ModelFallback) (see [Model Fallback](https://pydantic.dev/docs/ai/capabilities/model-fallback/#agent-specs)), [`RetryOnModelErrors`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.RetryOnModelErrors) (see [Retry On Model Errors](https://pydantic.dev/docs/ai/capabilities/retry-on-model-errors/#agent-specs)), and [`BatchModelRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.BatchModelRequests) (see [Batch processing](https://pydantic.dev/docs/ai/core-concepts/batch/#agent-specs)). The other [built-in capabilities](https://pydantic.dev/docs/ai/capabilities/overview/#available-capabilities) take non-serializable arguments (callables, toolset objects) and can only be used in Python code.

## Custom capabilities in specs

See [Publishing capabilities](https://pydantic.dev/docs/ai/capabilities/custom/#publishing-capabilities) for how to make custom capabilities work with agent specs.

## AgentSpec reference

The [`AgentSpec`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentSpec) model represents the full spec structure:

| Field | Type | Description |
| --- | --- | --- |
| `model` | `str \| None` | [Model](https://pydantic.dev/docs/ai/models/overview/) name |
| `name` | `str \| None` | Agent name |
| `description` | `str \| None` | Agent description (supports [templates](#template-strings)) |
| `instructions` | `str \| list[str] \| None` | [Instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions) (supports [templates](#template-strings)) |
| `model_settings` | `dict \| None` | [Model settings](https://pydantic.dev/docs/ai/core-concepts/agent/#model-run-settings) |
| `capabilities` | `list` | [Capabilities](https://pydantic.dev/docs/ai/capabilities/overview/) (see [spec syntax](#capability-spec-syntax)) |
| `deps_schema` | `dict \| None` | JSON Schema for [template string](#template-strings) validation (see below) |
| `output_schema` | `dict \| None` | JSON Schema for [structured output](https://pydantic.dev/docs/ai/core-concepts/output/) (see below) |
| `retries` | `int \| AgentRetries \| None` | Retry budgets for [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries) and [output validation](https://pydantic.dev/docs/ai/core-concepts/output/#output-validator-functions). Pass an integer to use the same budget for both, or [`AgentRetries`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentRetries) to configure them separately. |
| `end_strategy` | `EndStrategy` | When to stop (`'early'`, `'graceful'`, or `'exhaustive'`) |
| `tool_timeout` | `float \| None` | Default [tool](https://pydantic.dev/docs/ai/tools-toolsets/tools/) timeout in seconds |
| `instrument` | `bool \| None` | Enable [Logfire](https://pydantic.dev/docs/ai/integrations/logfire/) instrumentation |
| `metadata` | `dict \| None` | Agent [metadata](https://pydantic.dev/docs/ai/core-concepts/agent/#run-metadata) |

### deps\_schema

When loading a spec file without a Python `deps_type`, `deps_schema` provides a JSON Schema that validates [template string](#template-strings) variable names at construction time. It does **not** validate the actual deps object at runtime — it only ensures that template variables like `{{user_name}}` correspond to properties defined in the schema.

### output\_schema

When provided (and no `output_type` keyword argument is passed to `from_spec`), `output_schema` defines the structure the model should produce as its final output. Under the hood, it creates a [`StructuredDict`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.StructuredDict) output type: the JSON Schema is sent to the model API so the model knows what structure to produce, and the response is returned as a `dict[str, Any]`.

agent\_with\_schema.yaml

```yaml
model: anthropic:claude-opus-5-5
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
capabilities:
  - WebSearch:
      local: duckduckgo
```

## Saving specs

[`AgentSpec.to_file`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentSpec.to_file) saves a spec to YAML or JSON and optionally generates a companion JSON Schema file for editor autocompletion:

save\_spec\_example.py

```python
from pydantic_ai import AgentSpec

spec = AgentSpec.model_validate(
    {
        'model': 'anthropic:claude-opus-5-5',
        'instructions': 'You are a helpful assistant.',
        'capabilities': [{'WebSearch': {'local': 'duckduckgo'}}],
    }
)
spec.to_file('agent.yaml')
# Also generates ./agent_schema.json for editor autocompletion
```

The generated JSON Schema file enables autocompletion and validation in editors that support the [YAML Language Server](https://github.com/redhat-developer/yaml-language-server) protocol. Pass `schema_path=None` to skip schema generation.
