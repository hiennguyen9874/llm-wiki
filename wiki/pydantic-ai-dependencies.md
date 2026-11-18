---
type: Concept
title: Pydantic AI dependencies
description: How Pydantic AI passes data and services to instructions, tools and output validators — deps_type as a type-only declaration, RunContext access, the thread-pool path for sync dependencies, and agent.override for tests.
tags: [pydantic-ai, agents, dependency-injection]
status: draft
created: 2026-11-18
generated: { by: llm-wiki-agent/1, at: 2026-11-18T10:52:00Z }
stale_after: 2027-02-18
sources:
  - id: pydantic-docs-dependencies
    resource: ../raw/core-concepts/dependencies/index.md
    scope: ../raw/core-concepts/dependencies/
    kind: documentation
    title: "Dependencies"
---

**Reported, Pydantic AI version unspecified:** Pydantic AI ships a dependency injection system so the code that builds a run's prompt and checks its answer receives its data and services as arguments instead of reaching for module-level state. The declaration has two halves that never meet at runtime: `deps_type` on the `Agent` names the type for the type checker only, and the instance itself travels per run, where every consumer reads it from `RunContext.deps`.[^pydantic-docs-dependencies]

## Defining dependencies

Dependencies can be any Python type. When several objects travel together the documentation's recommended container is a dataclass, and its sample holds the two things a tool usually needs — an API key and an HTTP client:[^pydantic-docs-dependencies]

```python
@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent('openai:gpt-6.1-sol', deps_type=MyDeps)

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
```

The split is deliberate. `deps_type` takes the **class, not an instance**, and the documentation states outright that the parameter is not used at runtime — it exists so the agent can be fully type-checked. The instance is supplied at `agent.run(..., deps=deps)`, which is also where a per-request dependency such as the connecting user's client is decided.[^pydantic-docs-dependencies]

## Accessing dependencies through RunContext

`RunContext` is the first parameter of instructions functions "etc.", and it is parameterized with the dependency type. A wrong annotation is caught by static type checkers rather than at runtime, and `.deps` is the attribute every consumer reads:[^pydantic-docs-dependencies]

```python
@agent.instructions
async def get_instructions(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'
```

`RunContext` carries more than the dependencies. `.agent` exposes the running agent so tools, hooks and capabilities can read properties such as `name` or `output_type`; `.realtime` identifies a realtime session without a model type check, and `.realtime_session` exposes the live `RealtimeSession` once connected.[^pydantic-docs-dependencies]

Dependency fields can also reach the prompt without a callable, through template strings: `TemplateStr('Hello {{name}}')` renders `name` from the dependency object at runtime. The documentation calls this especially useful in agent specs, where a callable is not available.[^pydantic-docs-dependencies]

## Synchronous dependencies run in a thread

Instructions functions, function tools and output validators all run in the async context of a run. A function declared with `def` instead of `async def` is called through `run_in_executor` in a thread pool, so a synchronous dependency works — the sample swaps `httpx.AsyncClient` for `httpx.Client` and drops `async def` — but the documentation's guidance is to prefer `async` whenever the dependency performs I/O.[^pydantic-docs-dependencies]

## Where the dependencies reach

| Consumer | How `RunContext` arrives | Sample use |
| --- | --- | --- |
| `@agent.instructions` | First and only parameter, optionally — a plain `-> str` function is also valid | Fetch remote context and authorize it with the dependency's key |
| `@agent.tool` | First parameter, before the tool's own arguments | Pass the dependency's client and key to a lookup |
| `@agent.output_validator` | First parameter, optionally | Call a verification endpoint; raise `ModelRetry` when it answers `400` |

The full example uses the same `MyDeps` in all three places, and the validator's `400` becomes a `ModelRetry` carrying the service's message so the model can try again.[^pydantic-docs-dependencies]

## Overriding dependencies for tests

`agent.override(deps=test_deps)` overrides the dependencies for the duration of a `with` block, which matters when the agent is called from application code rather than directly from the test. Two consequences follow from the sample: dependencies passed by the application code are **not** used while the override is active, and the seam that makes this testable is a **method on the dependency** — the instructions function calls `ctx.deps.instructions_factory()` — so a test subclass can replace the behaviour without a network call:[^pydantic-docs-dependencies]

```python
class TestMyDeps(MyDeps):
    async def instructions_factory(self) -> str:
        return 'test prompt'

async def test_application_code():
    test_deps = TestMyDeps('test_key', httpx.AsyncClient())
    with joke_agent.override(deps=test_deps):
        joke = await application_code('Tell me a joke.')
    assert joke.startswith('Did you hear about the toothpaste scandal?')
```

Because the test subclass returns a canned prompt, its `http_client` goes unused — the dependency can carry objects a given test never touches.[^pydantic-docs-dependencies]

## Evidence and coverage

The sole artifact is the Pydantic documentation capture `index.md`, inspected as text; there are no attachments, includes, downloads or supporting files. It names no Pydantic AI version, author, publication date or licence, and all five `Agent` constructions in it pin the model string `openai:gpt-6.1-sol`, which no other capture in this wiki uses. The linked API reference pages (`Agent.__init__`, `RunContext`, `.deps`, `.agent`, `.realtime_session`, `Agent.override`), the agent, tools, output-validator, hooks, capability, agent-spec and template-string pages, and the three worked examples (weather agent, SQL generation, RAG) were read as links, not followed, so the signature, defaults and error behaviour of each are unverified here. The agent-spec template-string route is compiled from its own capture in [agent specs](pydantic-ai-agent-specs.md), and the hooks entry in particular still has a local sibling capture under `raw/core-concepts/` that this ingest did not read. Nothing was installed, no agent was constructed, no instructions function or validator ran, no dependency was overridden and no example was executed, so every claim is **Reported**; the page is `draft` under the `pydantic-ai` domain rule, and `stale_after` is set because `deps_type`, `RunContext` and `override` are release-sensitive surface.

## Relationships

- **Used by** [Pydantic AI capability primitive](pydantic-ai-capability-primitive.md): a capability's instructions, tools and hooks receive the same `RunContext[SupportDeps]`, so the dependency type declared on the agent is what those signatures must match.[^pydantic-docs-dependencies]
- **Used by** [Pydantic AI MCP integration](pydantic-ai-mcp-integration.md): per-user MCP credentials are read from the run's dependencies inside a function called with the `RunContext` at run start.[^pydantic-docs-dependencies]
- **Constrained by** [Pydantic AI v2 release](pydantic-ai-v2-release.md): the generic default moved to `object`, so an agent declared without `deps_type` is typed accordingly and `RunContext[None]` no longer matches it.[^pydantic-docs-dependencies]
- **Related to** [Pydantic AI durable execution](pydantic-ai-durable-execution.md): a dependency object is supplied per run, so whether it survives a replay is a question for the durability engine, not for this page.
- **Is consumed by** [Pydantic AI function tools](pydantic-ai-function-tools.md): whether a tool takes `RunContext` is what separates `@agent.tool` from `@agent.tool_plain`, and what `Tool(..., takes_ctx=...)` declares outright.[^pydantic-docs-dependencies]
- **Is rendered into prompts by** [agent specs](pydantic-ai-agent-specs.md): a spec string containing `{{` becomes a template resolved against these same dependency fields, with the variable names checked against `deps_type` or a `deps_schema` at construction time.

[^pydantic-docs-dependencies]: Pydantic Docs, "Dependencies" (`https://pydantic.dev/docs/ai/core-concepts/dependencies/`, 1,256 words as declared); local capture `raw/core-concepts/dependencies/index.md`, content digest sha256:08aaf82d. Opening paragraphs (lines 10–13) for the injection system's three consumers and the "established Python practices" framing; "Defining Dependencies" (lines 15–59) for any-Python-type, the dataclass container, `unused_dependencies.py` and the three numbered notes — class-not-instance, not used at runtime, `deps=` at `agent.run`; "Accessing Dependencies" (lines 61–113) for `RunContext` as first parameter, the optional single-argument form, the parameterized type and static-checker failure, `.deps`, the `.agent`/`.realtime`/`.realtime_session` properties and their stated uses, and the `TemplateStr('Hello {{name}}')` template-string route for agent specs; "Asynchronous vs. Synchronous dependencies" (lines 115–164) for `run_in_executor` thread-pool dispatch, the `httpx.Client` sample and the prefer-async guidance; "Full Example" (lines 166–229) for `@agent.tool` and `@agent.output_validator` taking `RunContext` first and the `ModelRetry` on `400`; "Overriding Dependencies" (lines 231–308) for the instructions-factory method, `application_code`, the note that `app_deps` is not used under override, the `TestMyDeps` subclass, the `with joke_agent.override(deps=test_deps)` block and its assertion; "Examples" (lines 310–316) for the three linked examples. Evidence class: **Reported** — vendor documentation naming no release version; no package, agent or dependency was exercised.
