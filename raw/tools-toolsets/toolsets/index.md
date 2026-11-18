---
title: "Toolsets"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/tools-toolsets/toolsets/"
domain: "pydantic.dev"
language: "en"
description: "Group tools into reusable Pydantic AI toolsets that you can register in one go, swap at runtime or in tests, and compose to filter, rename or wrap tool calls."
word_count: 5125
---

A toolset represents a collection of [tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/) that can be registered with an agent in one go. They can be reused by different agents, swapped out at runtime or during testing, and composed in order to dynamically filter which tools are available, modify tool definitions, or change tool execution behavior. A toolset can contain locally defined functions, depend on an external service to provide them, or implement custom logic to list available tools and handle them being called. Toolsets can also be provided via [capabilities](https://pydantic.dev/docs/ai/capabilities/overview/), which bundle tools with hooks, instructions, and model settings.

Toolsets are used (among many other things) to define [MCP servers](https://pydantic.dev/docs/ai/mcp/client/) available to an agent. Pydantic AI includes many kinds of toolsets which are described below, and you can define a [custom toolset](#building-a-custom-toolset) by inheriting from the [`AbstractToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset) class.

The toolsets that will be available during an agent run can be specified in four different ways:

- at agent construction time, via the [`toolsets`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__) keyword argument to `Agent`, which takes toolset instances as well as functions that generate toolsets [dynamically](#dynamically-building-a-toolset) based on the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext)
- at agent run time, via the `toolsets` keyword argument to [`agent.run()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run), [`agent.run_sync()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_sync), [`agent.run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream), or [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter). These toolsets will be additional to those registered on the `Agent`
- [dynamically](#dynamically-building-a-toolset), via the [`@agent.toolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.toolset) decorator which lets you build a toolset based on the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext)
- as a contextual override, via the `toolsets` keyword argument to the [`agent.override()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.override) context manager. These toolsets will replace those provided at agent construction or run time during the life of the context manager

toolsets.py

```python
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel

def agent_tool():
    return "I'm registered directly on the agent"

def extra_tool():
    return "I'm passed as an extra tool for a specific run"

def override_tool():
    return 'I override all other tools'

agent_toolset = FunctionToolset(tools=[agent_tool]) # (1)
extra_toolset = FunctionToolset(tools=[extra_tool])
override_toolset = FunctionToolset(tools=[override_tool])

test_model = TestModel() # (2)
agent = Agent(test_model, toolsets=[agent_toolset])

result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['agent_tool']

result = agent.run_sync('What tools are available?', toolsets=[extra_toolset])
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['agent_tool', 'extra_tool']

with agent.override(toolsets=[override_toolset]):
    result = agent.run_sync('What tools are available?', toolsets=[extra_toolset]) # (3)
    print([t.name for t in test_model.last_model_request_parameters.function_tools])
    #> ['override_tool']
```

The [`FunctionToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset) will be explained in detail in the next section.

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

This `extra_toolset` will be ignored because we're inside an override context.

*(This example is complete, it can be run “as is”)*

## Function Toolset

As the name suggests, a [`FunctionToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset) makes locally defined functions available as tools.

Functions can be added as tools in four different ways:

- via the [`@toolset.tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.tool) decorator — for tools that need access to the agent [context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext)
- via the [`@toolset.tool_plain`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.tool_plain) decorator — for tools that do not need access to the agent [context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext)
- via the [`tools`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.__init__) keyword argument to the constructor which can take either plain functions, or instances of [`Tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.Tool)
- via the [`toolset.add_function()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.add_function) and [`toolset.add_tool()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.add_tool) methods which can take a plain function or an instance of [`Tool`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.Tool) respectively

The `add_function()` and `add_tool()` methods can also be used from a tool function to dynamically register new tools during a run to be available in future run steps.

function\_toolset.py

```python
from datetime import datetime

from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.models.test import TestModel

def temperature_celsius(city: str) -> float:
    return 21.0

def temperature_fahrenheit(city: str) -> float:
    return 69.8

weather_toolset = FunctionToolset(tools=[temperature_celsius, temperature_fahrenheit])

@weather_toolset.tool
def conditions(ctx: RunContext, city: str) -> str:
    if ctx.run_step % 2 == 0:
        return "It's sunny"
    else:
        return "It's raining"

datetime_toolset = FunctionToolset()
datetime_toolset.add_function(lambda: datetime.now(), name='now')

test_model = TestModel()  # (1)
agent = Agent(test_model)

result = agent.run_sync('What tools are available?', toolsets=[weather_toolset])
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['temperature_celsius', 'temperature_fahrenheit', 'conditions']

result = agent.run_sync('What tools are available?', toolsets=[datetime_toolset])
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['now']
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

*(This example is complete, it can be run “as is”)*

A tool that joins the run after its first model request, however it got there, is recorded in the message history as a [`ToolAvailabilityDeltaPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolAvailabilityDeltaPart), unless no plainly visible tool from before is still present to keep stable. A new tool with `defer_loading=True` joins the [tool search](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-search) corpus instead. See [Tools that appear mid-run](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#mid-run-tool-additions) for how each provider delivers it.

### Toolset Instructions

A [`FunctionToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset) can provide instructions that are automatically included in the model request. This lets each toolset carry its own usage guidance alongside its tools, so you don’t need to duplicate instructions on every agent that uses the toolset.

Instructions can be provided as strings, functions (sync or async, with or without [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext)), or a mix of both:

toolset\_instructions.py

```python
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

search_toolset = FunctionToolset(
    instructions='Always use the search tool before answering factual questions.',
)

@search_toolset.tool_plain
def search(query: str) -> str:
    """Search for information."""
    return f'Results for: {query}'

test_model = TestModel()
agent = Agent(test_model, toolsets=[search_toolset])
result = agent.run_sync('What is the capital of France?')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> Always use the search tool before answering factual questions.
```

*(This example is complete, it can be run “as is”)*

You can also use the [`@toolset.instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset.instructions) decorator to register dynamic instruction functions that can access the run context. Like [`@agent.instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.instructions), it takes `name=` and [`on_change='append'`](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes), which keeps the cached prefix when the instructions change mid-conversation:

toolset\_instructions\_decorator.py

```python
from pydantic_ai import Agent, FunctionToolset, ModelRequest, RunContext
from pydantic_ai.models.test import TestModel

math_toolset = FunctionToolset[str]()

@math_toolset.instructions
def math_instructions(ctx: RunContext[str]) -> str:
    return f'You are helping: {ctx.deps}. Always show your work when using the calculator.'

@math_toolset.tool_plain
def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    return '4'

test_model = TestModel()
agent = Agent(test_model, toolsets=[math_toolset], deps_type=str)
result = agent.run_sync('What is 2+2?', deps='Alice')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> You are helping: Alice. Always show your work when using the calculator.
```

*(This example is complete, it can be run “as is”)*

When a toolset with instructions is used alongside agent-level [`instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__), the toolset instructions are appended after the agent instructions:

toolset\_instructions\_combined.py

```python
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

toolset = FunctionToolset(instructions='Use the greeting tool for all greetings.')

@toolset.tool_plain
def greeting(name: str) -> str:
    """Greet someone."""
    return f'Hello, {name}!'

test_model = TestModel()
agent = Agent(
    test_model,
    instructions='You are a friendly assistant.',
    toolsets=[toolset],
)
result = agent.run_sync('Hi there!')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
"""
You are a friendly assistant.

Use the greeting tool for all greetings.
"""
```

*(This example is complete, it can be run “as is”)*

When multiple toolsets with instructions are registered on an agent, all their instructions are combined:

toolset\_instructions\_multiple.py

```python
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

weather_toolset = FunctionToolset(instructions='Use weather tools for forecasts.')

@weather_toolset.tool_plain
def forecast(city: str) -> str:
    """Get weather forecast."""
    return 'Sunny'

calendar_toolset = FunctionToolset(instructions='Use calendar tools for scheduling.')

@calendar_toolset.tool_plain
def schedule(event: str) -> str:
    """Schedule an event."""
    return 'Scheduled'

test_model = TestModel()
agent = Agent(test_model, toolsets=[weather_toolset, calendar_toolset])
result = agent.run_sync('Plan my day')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
"""
Use weather tools for forecasts.

Use calendar tools for scheduling.
"""
```

*(This example is complete, it can be run “as is”)*

#### Toolset instructions that change

Instruction functions run before every model request, so their text can change during a run, for example after a tool updates some state. By default each change rewrites the instruction prefix, which stops the provider from reusing the cached conversation behind it. For instructions that change mid-conversation, we recommend having the changes [appended](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) to the history instead: the prefix stays cached, at the cost of the block’s complete new text being added to the history for each change. Build them only from state you control: [keep untrusted text out of instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#untrusted-instruction-text).

To opt in, give the toolset an [`id`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.id) and register the function with `@toolset.instructions(name=..., on_change='append')`. A [custom toolset](#building-a-custom-toolset) can instead return an [`InstructionPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.InstructionPart) with `on_change='append'` from [`get_instructions()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.get_instructions):

toolset\_instruction\_changes.py

```python
from dataclasses import dataclass, field

from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.messages import InstructionDeltaPart, ModelRequest
from pydantic_ai.models.test import TestModel

@dataclass
class Cart:
    items: list[str] = field(default_factory=list[str])

cart_toolset = FunctionToolset[Cart](id='cart')

@cart_toolset.instructions(name='count', on_change='append')
def cart_count(ctx: RunContext[Cart]) -> str:
    return f'Items in the cart: {len(ctx.deps.items)}.'  # (1)

@cart_toolset.tool
def add_to_cart(ctx: RunContext[Cart], item: str) -> str:
    """Add an item to the cart."""
    ctx.deps.items.append(item)
    return 'Added.'

agent = Agent(TestModel(), deps_type=Cart, toolsets=[cart_toolset])
result = agent.run_sync('Add an apple.', deps=Cart())
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> Items in the cart: 0.
print(
    [
        part.content
        for message in result.all_messages()
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, InstructionDeltaPart)
    ]
)
#> ['Items in the cart: 1.']
```

Only the count goes into the instructions, not the item names, which come from the model's tool arguments: [keep untrusted text out of instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#untrusted-instruction-text).

*(This example is complete, it can be run “as is”)*

## Toolset Composition

Toolsets can be composed to dynamically filter which tools are available, modify tool definitions, or change tool execution behavior. Multiple toolsets can also be combined into one.

### Combining Toolsets

[`CombinedToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.CombinedToolset) takes a list of toolsets and lets them be used as one.

combined\_toolset.py

```python
from pydantic_ai import Agent, CombinedToolset
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset

combined_toolset = CombinedToolset([weather_toolset, datetime_toolset])

test_model = TestModel() # (1)
agent = Agent(test_model, toolsets=[combined_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['temperature_celsius', 'temperature_fahrenheit', 'conditions', 'now']
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

*(This example is complete, it can be run “as is”)*

### Filtering Tools

[`FilteredToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FilteredToolset) wraps a toolset and filters available tools ahead of each step of the run based on a user-defined function that is passed the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) and each tool’s [`ToolDefinition`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition) and returns a boolean to indicate whether or not a given tool should be available.

To chain transformations, call [`filtered()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.filtered) on any toolset.

filtered\_toolset.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from combined_toolset import combined_toolset

filtered_toolset = combined_toolset.filtered(lambda ctx, tool_def: 'fahrenheit' not in tool_def.name)

test_model = TestModel() # (1)
agent = Agent(test_model, toolsets=[filtered_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['weather_temperature_celsius', 'weather_conditions', 'datetime_now']
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

*(This example is complete, it can be run “as is”)*

### Prefixing Tool Names

[`PrefixedToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.PrefixedToolset) wraps a toolset and adds a prefix to each tool name to prevent tool name conflicts between different toolsets.

To chain transformations, call [`prefixed()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.prefixed) on any toolset.

combined\_toolset.py

```python
from pydantic_ai import Agent, CombinedToolset
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset

combined_toolset = CombinedToolset(
    [
        weather_toolset.prefixed('weather'),
        datetime_toolset.prefixed('datetime')
    ]
)

test_model = TestModel() # (1)
agent = Agent(test_model, toolsets=[combined_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
"""
[
    'weather_temperature_celsius',
    'weather_temperature_fahrenheit',
    'weather_conditions',
    'datetime_now',
]
"""
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

*(This example is complete, it can be run “as is”)*

### Renaming Tools

[`RenamedToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.RenamedToolset) wraps a toolset and lets you rename tools using a dictionary mapping new names to original names. This is useful when the names provided by a toolset are ambiguous or would conflict with tools defined by other toolsets, but [prefixing them](#prefixing-tool-names) creates a name that is unnecessarily long or could be confusing to the model.

To chain transformations, call [`renamed()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.renamed) on any toolset.

renamed\_toolset.py

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from combined_toolset import combined_toolset

renamed_toolset = combined_toolset.renamed(
    {
        'current_time': 'datetime_now',
        'temperature_celsius': 'weather_temperature_celsius',
        'temperature_fahrenheit': 'weather_temperature_fahrenheit'
    }
)

test_model = TestModel() # (1)
agent = Agent(test_model, toolsets=[renamed_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
"""
['temperature_celsius', 'temperature_fahrenheit', 'weather_conditions', 'current_time']
"""
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

*(This example is complete, it can be run “as is”)*

### Dynamic Tool Definitions

[`PreparedToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.PreparedToolset) lets you modify the entire list of available tools ahead of each step of the agent run using a user-defined function that takes the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) and a list of [`ToolDefinition`s](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition) and returns the tool definitions to expose for that step.

This is the toolset-specific equivalent of the [`prepare_tools`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#prepare-tools) capability hook that prepares all tool definitions registered on an agent across toolsets.

Note that it is not possible to add or rename tools using `PreparedToolset`. Instead, you can use [`FunctionToolset.add_function()`](#function-toolset) or [`RenamedToolset`](#renaming-tools).

To chain transformations, call [`prepared()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.prepared) on any toolset.

prepared\_toolset.py

```python
from dataclasses import replace

from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.models.test import TestModel

from renamed_toolset import renamed_toolset

descriptions = {
    'temperature_celsius': 'Get the temperature in degrees Celsius',
    'temperature_fahrenheit': 'Get the temperature in degrees Fahrenheit',
    'weather_conditions': 'Get the current weather conditions',
    'current_time': 'Get the current time',
}

async def add_descriptions(ctx: RunContext, tool_defs: list[ToolDefinition]) -> list[ToolDefinition]:
    return [
        replace(tool_def, description=description)
        if (description := descriptions.get(tool_def.name, None))
        else tool_def
        for tool_def
        in tool_defs
    ]

prepared_toolset = renamed_toolset.prepared(add_descriptions)

test_model = TestModel() # (1)
agent = Agent(test_model, toolsets=[prepared_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print(test_model.last_model_request_parameters.function_tools)
"""
[
    ToolDefinition(
        name='temperature_celsius',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the temperature in degrees Celsius',
    ),
    ToolDefinition(
        name='temperature_fahrenheit',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the temperature in degrees Fahrenheit',
    ),
    ToolDefinition(
        name='weather_conditions',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the current weather conditions',
    ),
    ToolDefinition(
        name='current_time',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {},
            'type': 'object',
        },
        description='Get the current time',
    ),
]
"""
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

### Requiring Tool Approval

[`ApprovalRequiredToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.ApprovalRequiredToolset) wraps a toolset and lets you dynamically [require approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) for a given tool call based on a user-defined function that is passed the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext), the tool’s [`ToolDefinition`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition), and the validated tool call arguments. If no function is provided, all tool calls will require approval.

To chain transformations, call [`approval_required()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.approval_required) on any toolset.

See the [Human-in-the-Loop Tool Approval](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#human-in-the-loop-tool-approval) documentation for more information on how to handle agent runs that call tools that require approval and how to pass in the results.

approval\_required\_toolset.py

```python
from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults
from pydantic_ai.models.test import TestModel

from prepared_toolset import prepared_toolset

approval_required_toolset = prepared_toolset.approval_required(lambda ctx, tool_def, tool_args: tool_def.name.startswith('temperature'))

test_model = TestModel(call_tools=['temperature_celsius', 'temperature_fahrenheit']) # (1)
agent = Agent(
    test_model,
    toolsets=[approval_required_toolset],
    output_type=[str, DeferredToolRequests],
)
result = agent.run_sync('Call the temperature tools')
messages = result.all_messages()
print(result.output)
"""
DeferredToolRequests(
    calls=[],
    approvals=[
        ToolCallPart(
            tool_name='temperature_celsius',
            args={'city': 'a'},
            tool_call_id='pyd_ai_tool_call_id__temperature_celsius',
        ),
        ToolCallPart(
            tool_name='temperature_fahrenheit',
            args={'city': 'a'},
            tool_call_id='pyd_ai_tool_call_id__temperature_fahrenheit',
        ),
    ],
    metadata={},
)
"""

result = agent.run_sync(
    message_history=messages,
    deferred_tool_results=DeferredToolResults(
        approvals={
            'pyd_ai_tool_call_id__temperature_celsius': True,
            'pyd_ai_tool_call_id__temperature_fahrenheit': False,
        }
    )
)
print(result.output)
#> {"temperature_celsius":21.0,"temperature_fahrenheit":"The tool call was denied."}
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to specify which tools to call.

*(This example is complete, it can be run “as is”)*

### Deferred Loading

[`DeferredLoadingToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.DeferredLoadingToolset) wraps a toolset and marks its tools for deferred loading, hiding them from the model until discovered via [tool search](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-search). This is useful for large toolsets (e.g. MCP servers with many endpoints) where loading all tool definitions into the model’s context would be wasteful.

[`FunctionToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FunctionToolset) also accepts `defer_loading=True` in its constructor to mark all tools for deferred loading. It applies to `Tool` instances too; only a function added with `defer_loading=False` opts out. For other toolsets, call [`.defer_loading()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.defer_loading) — pass a list of tool names to hide only specific tools, or `None` (the default) to hide all.

deferred\_loading\_toolset.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

mcp = MCPToolset('http://localhost:8000/mcp')
agent = Agent('openai:gpt-6.1-sol', toolsets=[mcp.defer_loading()])
```

Deferred loading hides each tool individually, and the model searches for the ones it needs. To instead hide a group of tools behind a workflow or skill, so they only appear once the model loads it along with its instructions, pass the toolset to an [on-demand capability](https://pydantic.dev/docs/ai/capabilities/on-demand/#hide-tools-until-loaded). Use tool search for a large catalog of independent tools; use an on-demand capability when tools belong to a workflow that the model opts into as a unit.

### Including Return Schemas

[`IncludeReturnSchemasToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.IncludeReturnSchemasToolset) wraps a toolset and sets `include_return_schema=True` on all its tools, causing the model to receive return type information. For models that natively support return schemas (e.g. Google Gemini), the schema is passed as a structured API field. For other models, it is injected into the tool description as JSON text.

To chain transformations, call [`.include_return_schemas()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.include_return_schemas) on any toolset.

include\_return\_schemas\_toolset.py

```python
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel

def get_temperature(city: str) -> float:
    """Get the temperature for a city."""
    return 21.0

toolset = FunctionToolset(tools=[get_temperature])

test_model = TestModel()
agent = Agent(test_model, toolsets=[toolset.include_return_schemas()])
result = agent.run_sync('What is the temperature?')
params = test_model.last_model_request_parameters
assert params is not None
assert params.function_tools[0].include_return_schema is True
```

*(This example is complete, it can be run “as is”)*

This is the toolset-level equivalent of the [`IncludeToolReturnSchemas`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.IncludeToolReturnSchemas) capability, which applies across all toolsets or a selected subset.

### Setting Tool Metadata

[`SetMetadataToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.SetMetadataToolset) wraps a toolset and merges metadata key-value pairs onto all its tools. This is useful for tagging tools with configuration that other capabilities or custom logic can inspect.

To chain transformations, call [`.with_metadata()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.with_metadata) on any toolset.

set\_metadata\_toolset.py

```python
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel

def search(query: str) -> str:
    """Search for information."""
    return f'Results for: {query}'

toolset = FunctionToolset(tools=[search])

test_model = TestModel()
agent = Agent(test_model, toolsets=[toolset.with_metadata(sensitive=True)])
result = agent.run_sync('Search for something')
params = test_model.last_model_request_parameters
assert params is not None
assert params.function_tools[0].metadata is not None
assert params.function_tools[0].metadata['sensitive'] is True
```

*(This example is complete, it can be run “as is”)*

This is the toolset-level equivalent of the [`SetToolMetadata`](https://pydantic.dev/docs/ai/api/pydantic-ai/capabilities/#pydantic_ai.capabilities.SetToolMetadata) capability, which applies across all toolsets or a selected subset.

### Changing Tool Execution

[`WrapperToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.WrapperToolset) wraps another toolset and delegates all responsibility to it.

It is a no-op by default, but you can subclass `WrapperToolset` to change the wrapped toolset’s tool execution behavior by overriding the [`call_tool()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.call_tool) method.

logging\_toolset.py

```python
import asyncio
from typing import Any

from pydantic_ai import Agent, RunContext, ToolsetTool, WrapperToolset
from pydantic_ai.models.test import TestModel

from prepared_toolset import prepared_toolset

LOG = []

class LoggingToolset(WrapperToolset):
    async def call_tool(self, name: str, tool_args: dict[str, Any], ctx: RunContext, tool: ToolsetTool) -> Any:
        LOG.append(f'Calling tool {name!r} with args: {tool_args!r}')
        try:
            await asyncio.sleep(0.1 * len(LOG)) # (1)

            result = await super().call_tool(name, tool_args, ctx, tool)
            LOG.append(f'Finished calling tool {name!r} with result: {result!r}')
        except Exception as e:
            LOG.append(f'Error calling tool {name!r}: {e}')
            raise e
        else:
            return result

logging_toolset = LoggingToolset(prepared_toolset)

agent = Agent(TestModel(), toolsets=[logging_toolset]) # (2)
result = agent.run_sync('Call all the tools')
print(LOG)
"""
[
    "Calling tool 'temperature_celsius' with args: {'city': 'a'}",
    "Calling tool 'temperature_fahrenheit' with args: {'city': 'a'}",
    "Calling tool 'weather_conditions' with args: {'city': 'a'}",
    "Calling tool 'current_time' with args: {}",
    "Finished calling tool 'temperature_celsius' with result: 21.0",
    "Finished calling tool 'temperature_fahrenheit' with result: 69.8",
    'Finished calling tool \'weather_conditions\' with result: "It\'s raining"',
    "Finished calling tool 'current_time' with result: datetime.datetime(...)",
]
"""
```

All docs examples are tested in CI and their output is verified, so we need `LOG` to always have the same order whenever this code is run. Since the tools could finish in any order, we sleep an increasing amount of time based on which number tool call we are to ensure that they finish (and log) in the same order they were called in.

We use [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here as it will automatically call each tool.

*(This example is complete, it can be run “as is”)*

## External Toolset

If your agent needs to be able to call [external tools](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#external-tool-execution) that are provided and executed by an upstream service or frontend, you can build an [`ExternalToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.ExternalToolset) from a list of [`ToolDefinition`s](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition) containing the tool names, arguments JSON schemas, and descriptions.

When the model calls an external tool, the call is considered to be [“deferred”](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#deferred-tools), and the agent run will end with a [`DeferredToolRequests`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolRequests) output object with a `calls` list holding [`ToolCallPart`s](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolCallPart) containing the tool name, validated arguments, and a unique tool call ID, which are expected to be passed to the upstream service or frontend that will produce the results.

When the tool call results are received from the upstream service or frontend, you can build a [`DeferredToolResults`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.DeferredToolResults) object with a `calls` dictionary that maps each tool call ID to an arbitrary value to be returned to the model, a [`ToolReturn`](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#advanced-tool-returns) object, or an exception in case the tool call failed: a [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) if the model should [try again](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries), or a [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed) if the failure should be reported to the model as a [failed result](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-failed) (without consuming the tool’s retry budget) so it can decide how to proceed. This `DeferredToolResults` object can then be provided to one of the agent run methods as `deferred_tool_results`, alongside the original run’s [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/).

Note that you need to add `DeferredToolRequests` to the `Agent`’s or `agent.run()`’s [`output_type`](https://pydantic.dev/docs/ai/core-concepts/output/#structured-output) so that the possible types of the agent run output are correctly inferred. For more information, see the [Deferred Tools](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#deferred-tools) documentation.

To demonstrate, let us first define a simple agent *without* deferred tools:

deferred\_toolset\_agent.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, FunctionToolset

toolset = FunctionToolset()

@toolset.tool_plain
def get_default_language():
    return 'en-US'

@toolset.tool_plain
def get_user_name():
    return 'David'

class PersonalizedGreeting(BaseModel):
    greeting: str
    language_code: str

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset], output_type=PersonalizedGreeting)

result = agent.run_sync('Greet the user in a personalized way')
print(repr(result.output))
#> PersonalizedGreeting(greeting='Hello, David!', language_code='en-US')
```

Next, let’s define a function that represents a hypothetical “run agent” API endpoint that can be called by the frontend and takes a list of messages to send to the model, a list of frontend tool definitions, and optional deferred tool results. This is where `ExternalToolset`, `DeferredToolRequests`, and `DeferredToolResults` come in:

deferred\_toolset\_api.py

```python
from pydantic_ai import (
    DeferredToolRequests,
    DeferredToolResults,
    ExternalToolset,
    ModelMessage,
    ToolDefinition,
)

from deferred_toolset_agent import PersonalizedGreeting, agent

def run_agent(
    messages: list[ModelMessage] = [],
    frontend_tools: list[ToolDefinition] = [],
    deferred_tool_results: DeferredToolResults | None = None,
) -> tuple[PersonalizedGreeting | DeferredToolRequests, list[ModelMessage]]:
    deferred_toolset = ExternalToolset(frontend_tools)
    result = agent.run_sync(
        toolsets=[deferred_toolset], # (1)
        output_type=[agent.output_type, DeferredToolRequests], # (2)
        message_history=messages, # (3)
        deferred_tool_results=deferred_tool_results,
    )
    return result.output, result.new_messages()
```

As mentioned in the [Deferred Tools](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#deferred-tools) documentation, these `toolsets` are additional to those provided to the `Agent` constructor

As mentioned in the [Deferred Tools](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/#deferred-tools) documentation, this `output_type` overrides the one provided to the `Agent` constructor, so we have to make sure to not lose it

We don't include an `user_prompt` keyword argument as we expect the frontend to provide it via `messages`

Now, imagine that the code below is implemented on the frontend, and `run_agent` stands in for an API call to the backend that runs the agent. This is where we actually execute the deferred tool calls and start a new run with the new result included:

deferred\_tools.py

```python
from pydantic_ai import (
    DeferredToolRequests,
    DeferredToolResults,
    ModelMessage,
    ModelRequest,
    ModelRetry,
    ToolDefinition,
    UserPromptPart,
)

from deferred_toolset_api import run_agent

frontend_tool_definitions = [
    ToolDefinition(
        name='get_preferred_language',
        parameters_json_schema={'type': 'object', 'properties': {'default_language': {'type': 'string'}}},
        description="Get the user's preferred language from their browser",
    )
]

def get_preferred_language(default_language: str) -> str:
    return 'es-MX' # (1)

frontend_tool_functions = {'get_preferred_language': get_preferred_language}

messages: list[ModelMessage] = [
    ModelRequest(
        parts=[
            UserPromptPart(content='Greet the user in a personalized way')
        ]
    )
]

deferred_tool_results: DeferredToolResults | None = None

final_output = None
while True:
    output, new_messages = run_agent(messages, frontend_tool_definitions, deferred_tool_results)
    messages += new_messages

    if not isinstance(output, DeferredToolRequests):
        final_output = output
        break

    print(output.calls)
    """
    [
        ToolCallPart(
            tool_name='get_preferred_language',
            args={'default_language': 'en-US'},
            tool_call_id='pyd_ai_tool_call_id',
        )
    ]
    """
    deferred_tool_results = DeferredToolResults()
    for tool_call in output.calls:
        if function := frontend_tool_functions.get(tool_call.tool_name):
            result = function(**tool_call.args_as_dict())
        else:
            result = ModelRetry(f'Unknown tool {tool_call.tool_name!r}')
        deferred_tool_results.calls[tool_call.tool_call_id] = result

print(repr(final_output))
"""
PersonalizedGreeting(greeting='Hola, David! Espero que tengas un gran día!', language_code='es-MX')
"""
```

Imagine that this returns the frontend [`navigator.language`](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language).

*(This example is complete, it can be run “as is”)*

## Dynamically Building a Toolset

Toolsets can be built dynamically ahead of each agent run or run step using a function that takes the agent [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) and returns a toolset or `None`. This is useful when a toolset (like an MCP server) depends on information specific to an agent run, like its [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/) — for example to [connect to an MCP server with per-user credentials](https://pydantic.dev/docs/ai/mcp/client/#per-user-authentication).

To register a dynamic toolset, you can pass a function that takes [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) to the `toolsets` argument of the `Agent` constructor, or you can wrap a compliant function in the [`@agent.toolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.toolset) decorator.

By default, the function will be called again ahead of each agent run step. If you are using the decorator, you can optionally provide a `per_run_step=False` argument to indicate that the toolset only needs to be built once for the entire run.

Instructions from the toolset the function returns are attributed to the dynamic toolset, so for them to use `on_change='append'`, give the decorator an `id`: `@agent.toolset(id='orders')`.

dynamic\_toolset.py

```python
from dataclasses import dataclass
from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset

@dataclass
class ToggleableDeps:
    active: Literal['weather', 'datetime']

    def toggle(self):
        if self.active == 'weather':
            self.active = 'datetime'
        else:
            self.active = 'weather'

test_model = TestModel()  # (1)
agent = Agent(
    test_model,
    deps_type=ToggleableDeps  # (2)
)

@agent.toolset
def toggleable_toolset(ctx: RunContext[ToggleableDeps]):
    if ctx.deps.active == 'weather':
        return weather_toolset
    else:
        return datetime_toolset

@agent.tool
def toggle(ctx: RunContext[ToggleableDeps]):
    ctx.deps.toggle()

deps = ToggleableDeps('weather')

result = agent.run_sync('Toggle the toolset', deps=deps)
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])  # (3)
#> ['toggle', 'now']

result = agent.run_sync('Toggle the toolset', deps=deps)
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['toggle', 'temperature_celsius', 'temperature_fahrenheit', 'conditions']
```

We're using [`TestModel`](https://pydantic.dev/docs/ai/api/models/test/#pydantic_ai.models.test.TestModel) here because it makes it easy to see which tools were available on each run.

We're using the agent's dependencies to give the `toggle` tool access to the `active` via the `RunContext` argument.

This shows the available tools *after* the `toggle` tool was executed, as the "last model request" was the one that returned the `toggle` tool result to the model.

*(This example is complete, it can be run “as is”)*

## Building a Custom Toolset

To define a fully custom toolset with its own logic to list available tools and handle them being called, you can subclass [`AbstractToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset) and implement the [`get_tools()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.get_tools) and [`call_tool()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.call_tool) methods.

You can also override the [`get_instructions()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.get_instructions) method to provide a description of how to use the toolset’s tools. This will be injected into the agent’s instructions and is useful for helping the model understand how to effectively use your toolset’s tools.

If the toolset has an [`id`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.id) and contributes instructions, that id must be unique among the toolsets registered with an agent, counting the ones a [capability](https://pydantic.dev/docs/ai/capabilities/overview/) contributes. Its instructions reach the model as [instruction parts](https://pydantic.dev/docs/ai/core-concepts/agent/#instruction-parts) identified by `'toolset:<toolset id>'`, so an application can address them by a key that outlives their wording. Every part the toolset returns carries that one key; if you want a part to be addressable on its own, return an [`InstructionPart`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.InstructionPart) with a `name` relative to your toolset (`'limits'`), which the framework qualifies to `'toolset:weather:limits'`. Don’t spell out your own id — you’d be repeating what the framework already knows, and a name of your own can’t be mistaken for a top-level key.

A [wrapper toolset](#changing-tool-execution) with an `id` that overrides `get_instructions()` can pass on what it wraps by returning the very part objects `super().get_instructions(ctx)` gave it, unchanged: those keep the ids of the toolsets that wrote them, or no id if their toolset has none. Every other part is keyed by the wrapper’s own id: the ones it adds, the ones it changes in place, and copies, even an unchanged copy such as `replace(part)` that still carries the id of the part it came from. A toolset that a [dynamic toolset](#dynamically-building-a-toolset) builds isn’t wrapped this way, so everything it says is keyed by the dynamic toolset’s id.

`get_instructions()` is called before each model request. If what it returns can change during a conversation, set `on_change='append'` on the `InstructionPart` so changes are [appended](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes) to the history instead of rewriting the cached prefix; see [Toolset instructions that change](#toolset-instructions-that-change).

The toolset lifecycle provides hooks for managing state at different scopes:

- [`for_run()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.for_run): Called once before each agent run. Return a fresh instance for per-run state isolation (e.g. resetting counters, creating a new session). The framework enters and exits the returned instance.
- [`for_run_step()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.for_run_step): Called at the start of each run step. Return a modified instance for per-step state transitions. If managing inner toolset transitions (e.g. swapping one toolset for another), you are responsible for the inner lifecycle (exiting the old, entering the new).
- [`__aenter__()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.__aenter__) and [`__aexit__()`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.__aexit__): Set up and tear down resources (e.g. network connections) that should live for the duration of the agent run.

### Per-run and per-step lifecycle

Toolsets support lifecycle hooks for per-run isolation and per-step state management:

- [`for_run(ctx)`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.for_run) — called once per agent run, before `__aenter__`. Return a fresh instance to isolate state between runs. Default: returns `self`.
- [`for_run_step(ctx)`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.for_run_step) — called at the start of each run step. Manage internal transitions (e.g. refreshing tool availability) in-place. Default: returns `self`.

## Third-Party Toolsets

Third-party toolsets can also be wrapped as [capabilities](https://pydantic.dev/docs/ai/capabilities/overview/), which bundle tools with hooks, instructions, and model settings. See [Extensibility](https://pydantic.dev/docs/ai/guides/extensibility/) for the full ecosystem. For skills, planning, file system and shell access, sandboxed code execution, and more, see the [capability index](https://pydantic.dev/docs/ai/capabilities/overview/#available-capabilities), which covers Pydantic AI and [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/).

### MCP Servers

Pydantic AI provides [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) for connecting to and calling tools on local and remote MCP servers, with the [`MCP` capability](https://pydantic.dev/docs/ai/capabilities/mcp/) as the recommended higher-level entry point. See the [MCP overview](https://pydantic.dev/docs/ai/mcp/overview/) and [MCP client](https://pydantic.dev/docs/ai/mcp/client/) documentation for details.

### LangChain Tools

If you’d like to use tools or a [toolkit](https://python.langchain.com/docs/concepts/tools/#toolkits) from LangChain’s [community tool library](https://python.langchain.com/docs/integrations/tools/) with Pydantic AI, you can use the [`LangChainToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/ext/#pydantic_ai.ext.langchain.LangChainToolset) which takes a list of LangChain tools. Note that Pydantic AI will not validate the arguments in this case — it’s up to the model to provide arguments matching the schema specified by the LangChain tool, and up to the LangChain tool to raise an error if the arguments are invalid.

You will need to install the `langchain-community` package and any others required by the tools in question.

```python
from langchain_community.agent_toolkits import SlackToolkit

from pydantic_ai import Agent
from pydantic_ai.ext.langchain import LangChainToolset

toolkit = SlackToolkit()
toolset = LangChainToolset(toolkit.get_tools())

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
# ...
```

### pydantic-ai-ejentum

[`pydantic-ai-ejentum`](https://pypi.org/project/pydantic-ai-ejentum/) wraps the [Ejentum Reasoning Harness](https://ejentum.com/) as a `FunctionToolset` subclass. `EjentumToolset` registers four agent-callable tools (`harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`). The agent calls one before generating; each call returns a structured cognitive scaffold (named failure pattern, executable procedure, suppression vectors, falsification test) that the model reads internally to shape its next response.

You will need to install the `pydantic-ai-ejentum` package and set your Ejentum API key in the `EJENTUM_API_KEY` environment variable (free and paid tiers at [https://ejentum.com/pricing](https://ejentum.com/pricing)), or pass `api_key=` to the constructor.

```python
from pydantic_ai import Agent
from pydantic_ai_ejentum import EjentumToolset

toolset = EjentumToolset()

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

The toolset emits Pydantic AI `instructions` that nudge the agent to call the matching `harness_*` tool before generating. Pass `add_instructions=False` to suppress and supply routing guidance from your own system prompt.
