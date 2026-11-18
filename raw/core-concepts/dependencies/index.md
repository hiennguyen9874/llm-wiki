---
title: "Dependencies"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/dependencies/"
domain: "pydantic.dev"
language: "en"
description: "Pass data and services to a Pydantic AI agent's instructions, tools and output validators with type-safe dependency injection, and override them in tests."
word_count: 1256
---

Pydantic AI uses a dependency injection system to provide data and services to your agent’s [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/) and [output validators](https://pydantic.dev/docs/ai/core-concepts/output/#output-validator-functions).

Pydantic AI’s dependency system follows established Python practices, making dependencies type-safe, understandable, easy to test, and easy to deploy in production.

## Defining Dependencies

Dependencies can be any python type. While in simple cases you might be able to pass a single object as a dependency (e.g. an HTTP connection), [dataclasses](https://docs.python.org/3/library/dataclasses.html#module-dataclasses) are generally a convenient container when your dependencies include multiple objects.

Here’s an example of defining an agent that requires dependencies.

(**Note:** dependencies aren’t actually used in this example, see [Accessing Dependencies](#accessing-dependencies) below)

unused\_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent

@dataclass
class MyDeps:  # (1)
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=MyDeps,  # (2)
)

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run(
            'Tell me a joke.',
            deps=deps,  # (3)
        )
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.
```

Define a dataclass to hold dependencies.

Pass the dataclass type to the `deps_type` argument of the [`Agent` constructor](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__). **Note**: we're passing the type here, NOT an instance, this parameter is not actually used at runtime, it's here so we can get full type checking of the agent.

When running the agent, pass an instance of the dataclass to the `deps` parameter.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Accessing Dependencies

Dependencies are accessed through the [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) type, this should be the first parameter of instructions functions etc.

instructions\_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=MyDeps,
)

@agent.instructions  # (1)
async def get_instructions(ctx: RunContext[MyDeps]) -> str:  # (2)
    response = await ctx.deps.http_client.get(  # (3)
        'https://example.com',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},  # (4)
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.
```

[`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) may optionally be passed to an [`instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.instructions) function as the only argument.

[`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) is parameterized with the type of the dependencies, if this type is incorrect, static type checkers will raise an error.

Access the HTTP client through the [`.deps`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.deps) attribute.

Access the API key through the same attribute.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

In addition to [`.deps`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.deps), [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) provides access to the running agent via [`.agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.agent), which is useful when [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), [hooks](https://pydantic.dev/docs/ai/core-concepts/hooks/), or [capabilities](https://pydantic.dev/docs/ai/capabilities/overview/) need to read agent properties like [`name`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.name) or [`output_type`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.output_type). The [`.realtime`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.realtime) property identifies realtime sessions without requiring a model type check, and [`.realtime_session`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.realtime_session) exposes the live [`RealtimeSession`](https://pydantic.dev/docs/ai/api/pydantic-ai/realtime/#pydantic_ai.realtime.RealtimeSession) to tools and hooks once it is connected.

Dependency fields can also be referenced in instructions and descriptions via [template strings](https://pydantic.dev/docs/ai/core-concepts/agent-spec/#template-strings) — for example, [`TemplateStr('Hello {{name}}')`](https://pydantic.dev/docs/ai/api/pydantic-ai/template/#pydantic_ai.template.TemplateStr) renders `name` from the deps object at runtime. This is especially useful in [agent specs](https://pydantic.dev/docs/ai/core-concepts/agent-spec/) where callables aren’t available.

### Asynchronous vs. Synchronous dependencies

[Instructions functions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), [function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/) and [output validators](https://pydantic.dev/docs/ai/core-concepts/output/#output-validator-functions) are all run in the async context of an agent run.

If these functions are synchronous, defined with `def` rather than `async def`, Pydantic AI calls them with [`run_in_executor`](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor) in a thread pool. Prefer `async` functions when dependencies perform I/O, although synchronous dependencies also work.

Here’s the same example as above, but with a synchronous dependency:

sync\_dependencies.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.Client  # (1)

agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=MyDeps,
)

@agent.instructions
def get_instructions(ctx: RunContext[MyDeps]) -> str:  # (2)
    response = ctx.deps.http_client.get(
        'https://example.com', headers={'Authorization': f'Bearer {ctx.deps.api_key}'}
    )
    response.raise_for_status()
    return f'Prompt: {response.text}'

async def main():
    deps = MyDeps('foobar', httpx.Client())
    result = await agent.run(
        'Tell me a joke.',
        deps=deps,
    )
    print(result.output)
    #> Did you hear about the toothpaste scandal? They called it Colgate.
```

Here we use a synchronous `httpx.Client` instead of an asynchronous `httpx.AsyncClient`.

To match the synchronous dependency, the instructions function is now a plain function, not a coroutine.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Full Example

As well as instructions, dependencies can be used in [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/) and [output validators](https://pydantic.dev/docs/ai/core-concepts/output/#output-validator-functions).

full\_example.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, ModelRetry, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=MyDeps,
)

@agent.instructions
async def get_instructions(ctx: RunContext[MyDeps]) -> str:
    response = await ctx.deps.http_client.get('https://example.com')
    response.raise_for_status()
    return f'Prompt: {response.text}'

@agent.tool  # (1)
async def get_joke_material(ctx: RunContext[MyDeps], subject: str) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com#jokes',
        params={'subject': subject},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text

@agent.output_validator  # (2)
async def validate_output(ctx: RunContext[MyDeps], output: str) -> str:
    response = await ctx.deps.http_client.post(
        'https://example.com#validate',
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
        params={'query': output},
    )
    if response.status_code == 400:
        raise ModelRetry(f'invalid response: {response.text}')
    response.raise_for_status()
    return output

async def main():
    async with httpx.AsyncClient() as client:
        deps = MyDeps('foobar', client)
        result = await agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.
```

To pass `RunContext` to a tool, use the [`tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.tool) decorator.

`RunContext` may optionally be passed to a [`output_validator`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.output_validator) function as the first argument.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Overriding Dependencies

When testing agents, it’s useful to be able to customise dependencies.

While this can sometimes be done by calling the agent directly within unit tests, we can also override dependencies while calling application code which in turn calls the agent.

This is done via the [`override`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.override) method on the agent.

joke\_app.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

    async def instructions_factory(self) -> str:  # (1)
        response = await self.http_client.get('https://example.com')
        response.raise_for_status()
        return f'Prompt: {response.text}'

joke_agent = Agent('openai:gpt-6.1-sol', deps_type=MyDeps)

@joke_agent.instructions
async def get_instructions(ctx: RunContext[MyDeps]) -> str:
    return await ctx.deps.instructions_factory()  # (2)

async def application_code(prompt: str) -> str:  # (3)
    ...
    ...
    # now deep within application code we call our agent
    async with httpx.AsyncClient() as client:
        app_deps = MyDeps('foobar', client)
        result = await joke_agent.run(prompt, deps=app_deps)  # (4)
    return result.output
```

Define a method on the dependency to make the instructions easier to customise.

Call the instructions factory from within the instructions function.

Application code that calls the agent, in a real application this might be an API endpoint.

Call the agent from within the application code, in a real application this call might be deep within a call stack. Note `app_deps` here will NOT be used when deps are overridden.

*(This example is complete, it can be run “as is”)*

test\_joke\_app.py

```python
import httpx

from joke_app import MyDeps, application_code, joke_agent

class TestMyDeps(MyDeps):  # (1)
    async def instructions_factory(self) -> str:
        return 'test prompt'

async def test_application_code():
    test_deps = TestMyDeps('test_key', httpx.AsyncClient())  # (2)
    with joke_agent.override(deps=test_deps):  # (3)
        joke = await application_code('Tell me a joke.')  # (4)
    assert joke.startswith('Did you hear about the toothpaste scandal?')
```

Define a subclass of `MyDeps` in tests to customise the instructions factory.

Create an instance of the test dependency. Its `http_client` goes unused, as the test instructions factory makes no requests.

Override the dependencies of the agent for the duration of the `with` block, `test_deps` will be used when the agent is run.

Now we can safely call our application code, the agent will use the overridden dependencies.

## Examples

The following examples demonstrate how to use dependencies in Pydantic AI:

- [Weather Agent](https://pydantic.dev/docs/ai/examples/getting-started/weather-agent/)
- [SQL Generation](https://pydantic.dev/docs/ai/examples/data-analytics/sql-gen/)
- [RAG](https://pydantic.dev/docs/ai/examples/data-analytics/rag/)
