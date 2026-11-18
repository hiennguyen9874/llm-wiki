---
title: "Output"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/output/"
domain: "pydantic.dev"
language: "en"
description: "Get structured output from Pydantic AI agents as validated Pydantic models or text, with tool, native or prompted output modes, validators and streaming."
word_count: 8218
---

“Output” refers to the final value returned from [running an agent](https://pydantic.dev/docs/ai/core-concepts/agent/#running-agents). This can be either plain text, [structured data](#structured-output), an [image](#image-output), or the result of a [function](#output-functions) called with arguments provided by the model.

The output is wrapped in [`AgentRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult) or [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult) so that you can access other data, like [usage](https://pydantic.dev/docs/ai/api/pydantic-ai/usage/#pydantic_ai.usage.RunUsage) of the run and [message history](https://pydantic.dev/docs/ai/core-concepts/message-history/#accessing-messages-from-results).

Both `AgentRunResult` and `StreamedRunResult` are generic in the data they wrap, so typing information about the data returned by the agent is preserved.

A run ends when the model responds with one of the output types, or, if no output type is specified or `str` is one of the allowed options, when a plain text response is received. A run can also be cancelled if usage limits are exceeded, see [Usage Limits](https://pydantic.dev/docs/ai/core-concepts/agent/#usage-limits). With [`DeferredToolRequests`](https://pydantic.dev/docs/ai/tools-toolsets/deferred-tools/) or [`PendingModelResponse`](https://pydantic.dev/docs/ai/core-concepts/batch/#ending-a-run-while-it-waits) in the output type, a run can also end early, so you can approve its tools or wait for a model request the provider is still processing, like a batch request, and resume it later.

Here’s an example using a Pydantic model as the `output_type`, forcing the model to respond with data matching our specification:

olympics.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent

class CityLocation(BaseModel):
    city: str
    country: str

agent = Agent('google:gemini-3.8-flash', output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage)
#> RunUsage(cost=Decimal('0.00007275'), input_tokens=57, output_tokens=8, requests=1)
```

*(This example is complete, it can be run “as is”)*

## Structured output data

The [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) class constructor takes an `output_type` argument that takes one or more types or [output functions](#output-functions). It supports simple scalar types, list and dict types (including `TypedDict`s and [`StructuredDict`s](#structured-dict)), dataclasses and Pydantic models, as well as type unions — generally everything supported as type hints in a Pydantic model. You can also pass a list of multiple choices.

By default, Pydantic AI leverages the model’s tool calling capability to make it return structured data. When multiple output types are specified (in a union or list), each member is registered with the model as a separate output tool in order to reduce the complexity of the schema and maximise the chances a model will respond correctly. This has been shown to work well across a wide range of models. If you’d like to change the names of the output tools, use a model’s native structured output feature, or pass the output schema to the model in its [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions), you can use an [output mode](#output-modes) marker class.

When no output type is specified, or when `str` is among the output types, any plain text response from the model will be used as the output data. If `str` is not among the output types, the model is forced to return structured data or call an output function.

If the output type schema is not of type `"object"` (e.g. it’s `int` or `list[int]`), the output type is wrapped in a single element object, so the schema of all tools registered with the model are object schemas.

Structured outputs (like tools) use Pydantic to build the JSON schema used for the tool, and to validate the data returned by the model.

Here’s an example of returning either text or structured data:

box\_or\_error.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent

class Box(BaseModel):
    width: int
    height: int
    depth: int
    units: str

agent = Agent(
    'openai:gpt-6-luna',
    output_type=[Box, str], # (1)
    instructions=(
        "Extract me the dimensions of a box, "
        "if you can't extract all data, ask the user to try again."
    ),
)

result = agent.run_sync('The box is 10x20x30')
print(result.output)
#> Please provide the units for the dimensions (e.g., cm, in, m).

result = agent.run_sync('The box is 10x20x30 cm')
print(result.output)
#> width=10 height=20 depth=30 units='cm'
```

This could also have been a union: `output_type=Box | str`. However, as explained in the "Type checking considerations" section above, with mypy or older Pyright versions that would've required explicitly specifying the generic parameters on the `Agent` constructor and adding `# type: ignore` to this line in order to be type checked correctly.

*(This example is complete, it can be run “as is”)*

Here’s an example of using a union return type, which will register multiple output tools and wrap non-object schemas in an object:

colors\_or\_sizes.py

```python
from pydantic_ai import Agent

agent = Agent[object, list[str] | list[int]](
    'openai:gpt-6-luna',
    output_type=list[str] | list[int],  # (1)
    instructions='Extract either colors or sizes from the shapes provided.',
)

result = agent.run_sync('red square, blue circle, green triangle')
print(result.output)
#> ['red', 'blue', 'green']

result = agent.run_sync('square size 10, circle size 20, triangle size 30')
print(result.output)
#> [10, 20, 30]
```

As explained in the "Type checking considerations" section above, with mypy or older Pyright versions, using a union rather than a list requires explicitly specifying the generic parameters on the `Agent` constructor and adding `# type: ignore` to this line in order to be type checked correctly.

*(This example is complete, it can be run “as is”)*

### Output functions

Instead of plain text or structured data, you may want the output of your agent run to be the result of a function called with arguments provided by the model, for example to further process or validate the data provided through the arguments (with the option to tell the model to try again), or to hand off to another agent.

Output functions are similar to [function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/), but the model is forced to call one of them, the call ends the agent run, and the result is not passed back to the model.

As with tool functions, output function arguments provided by the model are validated using Pydantic (with optional [validation context](#validation-context)), can optionally take [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) as the first argument, and can raise [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) to ask the model to try again with modified arguments (or with a different output type).

Output functions do not support [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed), which is reserved for [function-tool failures](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-failed). Here, `ToolFailed` is treated like any ordinary exception: an [`on_output_process_error` hook](https://pydantic.dev/docs/ai/core-concepts/hooks/#error-hooks) can recover from it, otherwise it aborts the run.

To specify output functions, you set the agent’s `output_type` to either a single function (or bound instance method), or a list of functions. The list can also contain other output types like simple scalars or entire Pydantic models. You typically do not want to also register your output function as a tool (using the `@agent.tool` decorator or `tools` argument), as this could confuse the model about which it should be calling.

Here’s an example of all of these features in action:

output\_functions.py

```python
import re

from pydantic import BaseModel

from pydantic_ai import Agent, ModelRetry, RunContext, UnexpectedModelBehavior

class Row(BaseModel):
    name: str
    country: str

tables = {
    'capital_cities': [
        Row(name='Amsterdam', country='Netherlands'),
        Row(name='Mexico City', country='Mexico'),
    ]
}

class SQLFailure(BaseModel):
    """An unrecoverable failure. Only use this when you can't change the query to make it work."""

    explanation: str

def run_sql_query(query: str) -> list[Row]:
    """Run a SQL query on the database."""

    select_table = re.match(r'SELECT (.+) FROM (\w+)', query)
    if select_table:
        column_names = select_table.group(1)
        if column_names != '*':
            raise ModelRetry("Only 'SELECT *' is supported, you'll have to do column filtering manually.")

        table_name = select_table.group(2)
        if table_name not in tables:
            raise ModelRetry(
                f"Unknown table '{table_name}' in query '{query}'. Available tables: {', '.join(tables.keys())}."
            )

        return tables[table_name]

    raise ModelRetry(f"Unsupported query: '{query}'.")

sql_agent = Agent[object, list[Row] | SQLFailure](
    'openai:gpt-6.1-sol',
    output_type=[run_sql_query, SQLFailure],
    instructions='You are a SQL agent that can run SQL queries on a database.',
)

async def hand_off_to_sql_agent(ctx: RunContext, query: str) -> list[Row]:
    """I take natural language queries, turn them into SQL, and run them on a database."""

    # Drop the final message with the output tool call, as it shouldn't be passed on to the SQL agent
    messages = ctx.messages[:-1]
    try:
        result = await sql_agent.run(query, message_history=messages)
        output = result.output
        if isinstance(output, SQLFailure):
            raise ModelRetry(f'SQL agent failed: {output.explanation}')
        return output
    except UnexpectedModelBehavior as e:
        # Bubble up potentially retryable errors to the router agent
        if (cause := e.__cause__) and isinstance(cause, ModelRetry):
            raise ModelRetry(f'SQL agent failed: {cause.message}') from e
        else:
            raise

class RouterFailure(BaseModel):
    """Use me when no appropriate agent is found or the used agent failed."""

    explanation: str

router_agent = Agent[object, list[Row] | RouterFailure](
    'openai:gpt-6.1-sol',
    output_type=[hand_off_to_sql_agent, RouterFailure],
    instructions='You are a router to other agents. Never try to solve a problem yourself, just pass it on.',
)

result = router_agent.run_sync('Select the names and countries of all capitals')
print(result.output)
"""
[
    Row(name='Amsterdam', country='Netherlands'),
    Row(name='Mexico City', country='Mexico'),
]
"""

result = router_agent.run_sync('Select all pets')
print(repr(result.output))
"""
RouterFailure(explanation="The requested table 'pets' does not exist in the database. The only available table is 'capital_cities', which does not contain data about pets.")
"""

result = router_agent.run_sync('How do I fly from Amsterdam to Mexico City?')
print(repr(result.output))
"""
RouterFailure(explanation='I am not equipped to provide travel information, such as flights from Amsterdam to Mexico City.')
"""
```

#### Text output

If you provide an output function that takes a string, Pydantic AI will by default create an output tool like for any other output function. If instead you’d like the model to provide the string using plain text output, you can wrap the function in the [`TextOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.TextOutput) marker class.

If desired, this marker class can be used alongside one or more [`ToolOutput`](#tool-output) marker classes (or unmarked types or functions) in a list provided to `output_type`.

Like other output functions, text output functions can optionally take [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) as the first argument, and can raise [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) to ask the model to try again with modified arguments (or with a different output type).

The text is passed as a `str`. A function whose argument is a Pydantic model, dataclass or `TypedDict` instead, even one with a single `str` field, raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) when the agent is created. To turn the text into a model, take a `str` and build the model inside the function. An alias on the `str` argument must not be another argument’s name: the text goes to that argument instead, and the run fails when the `str` argument has no default or is positional-only.

Some models cannot write text at all, and say so through [`supports_text_output=False`](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.supports_text_output) on their profile — [decision models](https://pydantic.dev/docs/ai/models/decision/) such as [TypeSafe’s Jev](https://pydantic.dev/docs/ai/models/typesafe/) are. On those, any `output_type` that leaves text output available is a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError) before a request is sent: the default `str`, a `str` among several output types, a `TextOutput` function, and [`PromptedOutput`](#prompted-output), which asks for its structured data as text. Give such a model a structured `output_type`, such as a `BaseModel` or a union of them, instead.

text\_output\_function.py

```python
from pydantic_ai import Agent, TextOutput

def split_into_words(text: str) -> list[str]:
    return text.split()

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=TextOutput(split_into_words),
)
result = agent.run_sync('Who was Albert Einstein?')
print(result.output)
#> ['Albert', 'Einstein', 'was', 'a', 'German-born', 'theoretical', 'physicist.']
```

*(This example is complete, it can be run “as is”)*

#### Handling partial output in output functions

When streaming with `run_stream()` or `run_stream_sync()`, output functions are called **multiple times** — once for each partial output received from the model, and once for the final complete output.

You should check the [`RunContext.partial_output`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.partial_output) flag when your output function has **side effects** (e.g., sending notifications, logging, database updates) that should only execute on the final output.

When streaming, `partial_output` is `True` for each partial output and `False` for the final complete output. For all [other run methods](https://pydantic.dev/docs/ai/core-concepts/agent/#running-agents), `partial_output` is always `False` as the function is only called once with the complete output.

output\_function\_with\_side\_effects.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext

class DatabaseRecord(BaseModel):
    name: str
    value: int | None = None  # Make optional to allow partial output

def save_to_database(ctx: RunContext, record: DatabaseRecord) -> DatabaseRecord:
    """Output function with side effect - only save final output to database."""
    if ctx.partial_output:
        # Skip side effects for partial outputs
        return record

    # Only execute side effect for the final output
    print(f'Saving to database: {record.name} = {record.value}')
    #> Saving to database: test = 42
    return record

agent = Agent('openai:gpt-6.1-sol', output_type=save_to_database)

async def main():
    async with agent.run_stream('Create a record with name "test" and value 42') as result:
        async for output in result.stream_output(debounce_by=None):
            print(output)
            #> name='test' value=None
            #> name='test' value=42
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

### Output modes

Pydantic AI implements three different methods to get a model to output structured data:

#### Tool Output

In the default Tool Output mode, the output JSON schema of each output type (or function) is provided to the model as the parameters schema of a special output tool. This is the default as it’s supported by virtually all models and has been shown to work very well.

If you’d like to change the name of the output tool, pass a custom description to aid the model, or turn on or off [strict mode](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#strict-mode), you can wrap the type(s) in the [`ToolOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.ToolOutput) marker class and provide the appropriate arguments. Note that by default, the description is taken from the docstring specified on a Pydantic model or output function, so specifying it using the marker class is typically not necessary.

Field descriptions reach the model as in [tool schemas](https://pydantic.dev/docs/ai/tools-toolsets/tools/#docstrings), including a Pydantic model’s field docstrings when it sets `use_attribute_docstrings`. An `Enum` that mixes in [`UseEnumMemberDocstrings`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.UseEnumMemberDocstrings) additionally describes each of its options by the docstring written under that member, wherever the enum appears — in an output model, in a tool parameter, or as a bare `Enum` `output_type`. Without the mix-in the docstrings are ignored; see [enum options](https://pydantic.dev/docs/ai/tools-toolsets/tools/#enum-options).

When using output tools, each tool gets its own retry counter — the output side of the agent retry budget (set with [`AgentRetries`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentRetries) via `Agent(retries={'output': N})`, or per-run via `agent.run(retries={'output': N})`) is the *default per-tool limit*. To override the limit for an individual output tool, pass [`max_retries`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.ToolOutput.max_retries) on `ToolOutput`: `ToolOutput(Fruit, max_retries=2)`. See [How output retries are enforced](https://pydantic.dev/docs/ai/core-concepts/agent/#how-output-retries-are-enforced) for the relationship to the text-output path’s global budget.

To dynamically modify or filter the available output tools during an agent run, you can define an agent-wide `prepare_output_tools` function that will be called ahead of each step of a run. This function should be of type [`ToolsPrepareFunc`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolsPrepareFunc), which takes the [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) and a list of [`ToolDefinition`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition), and returns the output tool definitions to expose for that step. Return `[]` to expose no output tools. This is analogous to the [`prepare_tools` function](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#prepare-tools) for non-output tools.

tool\_output.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, ToolOutput

class Fruit(BaseModel):
    name: str
    color: str

class Vehicle(BaseModel):
    name: str
    wheels: int

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=[ # (1)
        ToolOutput(Fruit, name='return_fruit'),
        ToolOutput(Vehicle, name='return_vehicle'),
    ],
)
result = agent.run_sync('What is a banana?')
print(repr(result.output))
#> Fruit(name='banana', color='yellow')
```

If we were passing just `Fruit` and `Vehicle` without custom tool names, we could have used a union: `output_type=Fruit | Vehicle`. However, as `ToolOutput` is an object rather than a type, we have to use a list.

*(This example is complete, it can be run “as is”)*

#### Native Output

Native Output mode uses a model’s native “Structured Outputs” feature (aka “JSON Schema response format”), where the model is forced to only output text matching the provided JSON schema. Note that this is not supported by all models, and sometimes comes with restrictions. For example, [Gemini 3](https://ai.google.dev/gemini-api/docs/structured-output#structured_outputs_with_tools) supports Native Output alongside function and native tools, while earlier Gemini models cannot combine Native Output with function tools. [Groq](https://pydantic.dev/docs/ai/models/groq/#structured-output) also cannot combine Native Output with function tools. On [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/#schema-complexity-limits), the schema is compiled into a grammar with complexity limits that a large schema can exceed, and on a request that thinks, a structured `output_type` uses Native Output even without the marker class, unless its schema is over those limits. On [OpenAI](https://pydantic.dev/docs/ai/models/openai/#structured-output-schemas), a schema over the strict-mode size limits is sent without strict mode.

To use this mode, you can wrap the output type(s) in the [`NativeOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.NativeOutput) marker class that also lets you specify a `name` and `description` if the name and docstring of the type or function are not sufficient.

native\_output.py

```python
from pydantic_ai import Agent, NativeOutput

from tool_output import Fruit, Vehicle

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=NativeOutput(
        [Fruit, Vehicle], # (1)
        name='Fruit_or_vehicle',
        description='Return a fruit or vehicle.'
    ),
)
result = agent.run_sync('What is a Ford Explorer?')
print(repr(result.output))
#> Vehicle(name='Ford Explorer', wheels=4)
```

This could also have been a union: `output_type=Fruit | Vehicle`. However, as explained in the "Type checking considerations" section above, with mypy or older Pyright versions that would've required explicitly specifying the generic parameters on the `Agent` constructor and adding `# type: ignore` to this line in order to be type checked correctly.

*(This example is complete, it can be run “as is”)*

#### Prompted Output

In this mode, the model is prompted to output text matching the provided JSON schema through its [instructions](https://pydantic.dev/docs/ai/core-concepts/agent/#instructions) and it’s up to the model to interpret those instructions correctly. This is usable with all models, but is often the least reliable approach as the model is not forced to match the schema.

While we would generally suggest starting with tool or native output, in some cases this mode may result in higher quality outputs, and for models without native tool calling or structured output support it is the only option for producing structured outputs.

If the model API supports the “JSON Mode” feature (aka “JSON Object response format”) to force the model to output valid JSON, this is enabled, but it’s still up to the model to abide by the schema. Pydantic AI will validate the returned structured data and tell the model to try again if validation fails, but if the model is not intelligent enough this may not be sufficient.

To use this mode, you can wrap the output type(s) in the [`PromptedOutput`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.PromptedOutput) marker class that also lets you specify a `name` and `description` if the name and docstring of the type or function are not sufficient. Additionally, `template` lets you specify a custom instructions template to be used instead of the [default](https://pydantic.dev/docs/ai/api/pydantic-ai/profiles/#pydantic_ai.profiles.ModelProfile.prompted_output_template), or `template=False` to disable the schema prompt entirely.

prompted\_output.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, PromptedOutput

from tool_output import Vehicle

class Device(BaseModel):
    name: str
    kind: str

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=PromptedOutput(
        [Vehicle, Device], # (1)
        name='Vehicle or device',
        description='Return a vehicle or device.'
    ),
)
result = agent.run_sync('What is a MacBook?')
print(repr(result.output))
#> Device(name='MacBook', kind='laptop')

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=PromptedOutput(
        [Vehicle, Device],
        template='Gimme some JSON: {schema}'
    ),
)
result = agent.run_sync('What is a Ford Explorer?')
print(repr(result.output))
#> Vehicle(name='Ford Explorer', wheels=4)
```

This could also have been a union: `output_type=Vehicle | Device`. However, as explained in the "Type checking considerations" section above, with mypy or older Pyright versions that would've required explicitly specifying the generic parameters on the `Agent` constructor and adding `# type: ignore` to this line in order to be type checked correctly.

*(This example is complete, it can be run “as is”)*

#### Tool calls alongside a final result

A run ends when the model produces a final result. That result usually comes from an [output tool](#tool-output) call, but it can also come from [Native Output](#native-output), [Prompted Output](#prompted-output), plain text, or [image output](#image-output). When the model emits *other* tool calls in the same response, the agent’s [`end_strategy`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.end_strategy) decides what happens to them. Most agents never need to think about this, since most responses don’t mix a final result with other tool calls — but when one does, `end_strategy` controls how those calls run and which one becomes the final result.

| Strategy | Output tools | Function tools — output succeeded | Function tools — every output failed |
| --- | --- | --- | --- |
| `'graceful'` (default) | Run in emission order; first success is the final result, later output tools skipped | Run, in parallel where possible, in emission order | Run; the run continues |
| `'early'` | Run in emission order; the run ends at the first success | Skipped | Run; the run continues |
| `'exhaustive'` | All run, in parallel; first valid result by emission order wins | Run, in parallel | Run; the run continues |

`'graceful'` is the default and the right choice for most agents: function tools the model requested alongside an output tool still run, so their side effects happen and their results are available to the model if the run continues. Only the first successful output tool is used; later output tools are skipped so their side effects don’t fire more than once.

Choose `'early'` to end the run the instant an output tool succeeds — function tools requested in the same response are then skipped entirely. This is the fastest option when you never need those function tools to run once you have a result.

Choose `'exhaustive'` to run every tool, including additional output tools whose results won’t be used. This gives the model full visibility that each tool ran, at the cost of executing output-tool side effects that are ultimately discarded.

When *every* output tool fails, function tools run and the run continues under all three strategies: there is no result to end on, so the output failures go back to the model as retries and the function tools the model also asked for are run, letting it react to both on the next round.

##### Retrying after a tool failure

Under the `'graceful'` and `'exhaustive'` [end strategies](#parallel-output-tool-calls), function tools requested alongside an output tool still run. If one of them raises [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) (or its arguments fail validation) in the same response as a successful output tool, the output result is **not** used as the final result. Instead, the retry is sent back to the model so it can correct the problem, since the output may have been based on the failed tool call. This does not apply under `'early'`, where function tools don’t run once an output succeeds, nor when [streaming](#parallel-output-tool-calls), where the first matching output is committed immediately.

##### Controlling output tool parallelism

Like function tools, [output tools](#tool-output) run concurrently. Under the `'exhaustive'` [end strategy](#parallel-output-tool-calls), where multiple output tools can run in parallel, you can make an output tool a barrier with [`ToolOutput(sequential=True)`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.ToolOutput) — useful when you want all of a response’s function tools to finish before the output tool runs. This is the output-tool counterpart of the `sequential=True` flag for function tools; see [Parallel tool calls & concurrency](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#parallel-tool-calls-concurrency) for how the barrier behaves and how to run an entire run’s tools serially.

### Custom JSON schema

If it’s not feasible to define your desired structured output object using a Pydantic `BaseModel`, dataclass, or `TypedDict`, for example when you get a JSON schema from an external source or generate it dynamically, you can use the [`StructuredDict()`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.StructuredDict) helper function to generate a `dict[str, Any]` subclass with a JSON schema attached that Pydantic AI will pass to the model.

Note that Pydantic AI will not perform any validation of the received JSON object and it’s up to the model to correctly interpret the schema and any constraints expressed in it, like required fields or integer value ranges.

The output type will be a `dict[str, Any]` and it’s up to your code to defensively read from it in case the model made a mistake. You can use an [output validator](#output-validator-functions) to reflect validation errors back to the model and get it to try again.

Along with the JSON schema, you can optionally pass `name` and `description` arguments to provide additional context to the model:

```python
from pydantic_ai import Agent, StructuredDict

HumanDict = StructuredDict(
    {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'}
        },
        'required': ['name', 'age']
    },
    name='Human',
    description='A human with a name and age',
)

agent = Agent('openai:gpt-6.1-sol', output_type=HumanDict)
result = agent.run_sync('Create a person')
#> {'name': 'John Doe', 'age': 30}
```

### Choices known only at run time

Sometimes the model has to pick one of a set that doesn’t exist until the run is under way: the actions available on the screen in front of an agent, the records a search returned. A `Literal` or an `Enum` (with [`UseEnumMemberDocstrings`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.UseEnumMemberDocstrings) to describe its members) covers a set you know when you write the code, and gives you exhaustiveness checking that a run-time set cannot. For everything else there is [`Choices()`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.Choices), which takes a mapping from each option to what it means:

choices.py

```python
from pydantic_ai import Agent, Choices

Intent = Choices(
    {
        'refund': 'The customer wants their money back.',
        'replace': 'The customer wants a working unit instead.',
        'escalate': 'Nobody on this tier can resolve it.',
    },
    name='customer_intent',
    description='What the customer is asking for.',
)

agent = Agent('openai:gpt-6.1-sol', output_type=Intent)
result = agent.run_sync('The blender arrived smashed. Just send me another one.')
print(result.output)
#> replace
```

The descriptions are what make this worth a helper: each option carries its meaning into the schema the model receives, and the output is one of the keys, validated, and typed `str`. Passing a sequence of keys instead of a mapping describes nothing and asks the same question with a plain `enum`.

Like [`StructuredDict()`](#structured-dict), `Choices()` returns a type, so the same value works as an `output_type`, as a field of a Pydantic model, and as a [tool](https://pydantic.dev/docs/ai/tools-toolsets/tools/) parameter. A type checker won’t accept a type built at runtime in an annotation, though, so as a field or a parameter, put either one in `Annotated` on the type of the value it gives back: `Annotated[str, Intent]` for choices that don’t [stand for something else](#choices-that-stand-for-something-else), and `Annotated[dict[str, Any], Person]` for a `StructuredDict()`. Pydantic reads the schema and validation from the metadata, and the type checker sees a plain `str` or `dict`:

choices\_annotated.py

```python
from typing import Annotated

from pydantic import BaseModel

from pydantic_ai import Agent, Choices

Intent = Choices(
    {
        'refund': 'The customer wants their money back.',
        'replace': 'The customer wants a working unit instead.',
        'escalate': 'Nobody on this tier can resolve it.',
    }
)

class Triage(BaseModel):
    intent: Annotated[str, Intent]
    summary: str

agent = Agent('openai:gpt-6.1-sol', output_type=Triage)

@agent.tool_plain
def open_ticket(intent: Annotated[str, Intent], summary: str) -> str:
    """Open a ticket with the team that handles this intent."""
    return f'Opened a {intent} ticket.'

result = agent.run_sync('The kettle leaks everywhere. I just want my money back.')
print(result.output)
#> intent='refund' summary='Leaking kettle, customer wants a refund.'
```

#### Choices that stand for something else

An option can stand for a value instead of its own key, by giving [`Choice`](https://pydantic.dev/docs/ai/api/pydantic-ai/output/#pydantic_ai.output.Choice) the value alongside the description. The model still picks a key, and the output is what that key stands for:

choices\_value.py

```python
from dataclasses import dataclass

from pydantic_ai import Agent, Choice, Choices

@dataclass
class Doc:
    id: str
    title: str

docs = [
    Doc(id='rfc-6265', title='HTTP State Management Mechanism'),
    Doc(id='rfc-9110', title='HTTP Semantics'),
]

agent = Agent('openai:gpt-6.1-sol')
result = agent.run_sync(
    'Which one covers cookies?',
    output_type=Choices({doc.id: Choice(doc.title, value=doc) for doc in docs}),
)
print(result.output)
#> Doc(id='rfc-6265', title='HTTP State Management Mechanism')
```

#### Choices that do something

When the value is a callable, picking it *calls* it, the way an [output function](#output-functions) is called, so the run’s output is what the action returned and there is no dispatch table between the model’s answer and the thing it meant:

choices\_action.py

```python
from functools import partial

from pydantic_ai import Agent, Choice, Choices

class Screen:
    def click(self, target: str) -> str:
        return f'clicked {target}'

    async def observe(self) -> str:
        return 'the login page'

screen = Screen()
targets = {'login': 'The Login button, top right.', 'forgot': 'The "forgot password" link.'}

actions = {
    target: Choice(description, value=partial(screen.click, target))
    for target, description in targets.items()
}
actions['reobserve'] = Choice('Look again before deciding.', value=screen.observe)

agent = Agent('openai:gpt-6.1-sol')
result = agent.run_sync(
    'Sign in as the admin.',
    output_type=Choices(actions, description='Which action to take on the screen.'),
)
print(result.output)
#> clicked login
```

The action takes no arguments, so bind what it needs with `functools.partial` or a closure, and it may be `async`. Like an output function it can raise [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) to send the model back for another pick.

### Validation context

Some validation relies on an extra Pydantic [context](https://docs.pydantic.dev/latest/concepts/validators/#validation-context) object. You can pass such an object to an `Agent` at definition-time via its [`validation_context`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__init__) parameter. It will be used in the validation of both structured outputs and [tool arguments](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries).

This validation context can be either:

- the context object itself (`Any`), used as-is to validate outputs, or
- a function that takes the [`RunContext`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) and returns a context object (`Any`). This function will be called automatically before each validation, allowing you to build a dynamic validation context.

validation\_context.py

```python
from dataclasses import dataclass

from pydantic import BaseModel, ValidationInfo, field_validator

from pydantic_ai import Agent

class Value(BaseModel):
    x: int

    @field_validator('x')
    def increment_value(cls, value: int, info: ValidationInfo):
        return value + (info.context or 0)

agent = Agent(
    'google:gemini-3.8-flash',
    output_type=Value,
    validation_context=10,
)
result = agent.run_sync('Give me a value of 5.')
print(repr(result.output))  # 5 from the model + 10 from the validation context
#> Value(x=15)

@dataclass
class Deps:
    increment: int

agent = Agent(
    'google:gemini-3.8-flash',
    output_type=Value,
    deps_type=Deps,
    validation_context=lambda ctx: ctx.deps.increment,
)
result = agent.run_sync('Give me a value of 5.', deps=Deps(increment=10))
print(repr(result.output))  # 5 from the model + 10 from the validation context
#> Value(x=15)
```

*(This example is complete, it can be run “as is”)*

### Output validators

Some validation is inconvenient or impossible to do in Pydantic validators, in particular when the validation requires IO and is asynchronous. Pydantic AI provides a way to add validation functions via the [`agent.output_validator`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.output_validator) decorator.

Each [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) raised here consumes one unit of the run’s output retry budget. The budget defaults to `1` and can be set on the agent with [`AgentRetries`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentRetries) via `Agent(retries={'output': N})`, on a single run via `agent.run(retries={'output': N})`, or per output tool via [`ToolOutput(max_retries=N)`](#tool-output). Inside the validator, [`ctx.max_retries`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.max_retries) reflects the limit that will actually stop you (the global budget on the text path, or the per-tool limit on the tool path) and [`ctx.retry`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.retry) is the global retry counter, so it stays consistent across output-tool switches within a single run. See [How output retries are enforced](https://pydantic.dev/docs/ai/core-concepts/agent/#how-output-retries-are-enforced) for the full enforcement model.

Output validators do not support [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed). Raise `ModelRetry` to ask the model for another output. Here, `ToolFailed` is treated like any ordinary exception: an [`on_output_process_error` hook](https://pydantic.dev/docs/ai/core-concepts/hooks/#error-hooks) can recover from it, otherwise it aborts the run.

If you want to implement separate validation logic for different output types, it’s recommended to use [output functions](#output-functions) instead, to save you from having to do `isinstance` checks inside the output validator. If you want the model to output plain text, do your own processing or validation, and then have the agent’s final output be the result of your function, it’s recommended to use an [output function](#output-functions) with the [`TextOutput` marker class](#text-output).

Here’s a simplified variant of the [SQL Generation example](https://pydantic.dev/docs/ai/examples/data-analytics/sql-gen/):

sql\_gen.py

```python
from fake_database import DatabaseConn, QueryError
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ModelRetry

class Success(BaseModel):
    sql_query: str

class InvalidRequest(BaseModel):
    error_message: str

Output = Success | InvalidRequest
agent = Agent[DatabaseConn, Output](
    'google:gemini-3.8-flash',
    output_type=Output,
    deps_type=DatabaseConn,
    instructions='Generate PostgreSQL flavored SQL queries based on user input.',
)

@agent.output_validator
async def validate_sql(ctx: RunContext[DatabaseConn], output: Output) -> Output:
    if isinstance(output, InvalidRequest):
        return output
    try:
        await ctx.deps.execute(f'EXPLAIN {output.sql_query}')
    except QueryError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    else:
        return output

result = agent.run_sync(
    'get me users who were last active yesterday.', deps=DatabaseConn()
)
print(result.output)
#> sql_query='SELECT * FROM users WHERE last_active::date = today() - interval 1 day'
```

*(This example is complete, it can be run “as is”)*

#### Handling partial output in output validators

When streaming with `run_stream()` or `run_stream_sync()`, output validators are called **multiple times** — once for each partial output received from the model, and once for the final complete output.

You should check the [`RunContext.partial_output`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.partial_output) flag when you want to **validate only the complete result**, not intermediate partial values.

When streaming, `partial_output` is `True` for each partial output and `False` for the final complete output. For all [other run methods](https://pydantic.dev/docs/ai/core-concepts/agent/#running-agents), `partial_output` is always `False` as the validator is only called once with the complete output.

partial\_validation\_streaming.py

```python
from pydantic_ai import Agent, ModelRetry, RunContext

agent = Agent('openai:gpt-6.1-sol')

@agent.output_validator
def validate_output(ctx: RunContext, output: str) -> str:
    if ctx.partial_output:
        return output

    if len(output) < 50:
        raise ModelRetry('Output is too short.')
    return output

async def main():
    async with agent.run_stream('Write a long story about a cat') as result:
        async for message in result.stream_text():
            print(message)
            #> Once upon a
            #> Once upon a time, there was
            #> Once upon a time, there was a curious cat
            #> Once upon a time, there was a curious cat named Whiskers who
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore the world around
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore the world around him...
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Image output

Some models can generate images as part of their response, for example those that support the [Image Generation native tool](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#image-generation-tool) and OpenAI models using the [Code Execution native tool](https://pydantic.dev/docs/ai/tools-toolsets/native-tools/#code-execution-tool) when told to generate a chart.

To use the generated image as the output of the agent run, you can set `output_type` to [`BinaryImage`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryImage). If no image-generating native tool is explicitly specified, the [`ImageGenerationTool`](https://pydantic.dev/docs/ai/api/pydantic-ai/native_tools/#pydantic_ai.native_tools.ImageGenerationTool) will be enabled automatically.

image\_output.py

```python
from pydantic_ai import Agent, BinaryImage

agent = Agent('openai-responses:gpt-6.1-sol', output_type=BinaryImage)

result = agent.run_sync('Generate an image of an axolotl.')
assert isinstance(result.output, BinaryImage)
```

*(This example is complete, it can be run “as is”)*

If an agent does not need to always generate an image, you can use a union of `BinaryImage` and `str`. If the model generates both, the image will take precedence as output and the text will be available on [`ModelResponse.text`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.text):

image\_output\_union.py

```python
from pydantic_ai import Agent, BinaryImage

agent = Agent('openai-responses:gpt-6.1-sol', output_type=BinaryImage | str)

result = agent.run_sync('Tell me a two-sentence story about an axolotl, no image please.')
print(result.output)
"""
Once upon a time, in a hidden underwater cave, lived a curious axolotl named Pip who loved to explore. One day, while venturing further than usual, Pip discovered a shimmering, ancient coin that granted wishes!
"""

result = agent.run_sync('Tell me a two-sentence story about an axolotl with an illustration.')
assert isinstance(result.output, BinaryImage)
print(result.response.text)
"""
Once upon a time, in a hidden underwater cave, lived a curious axolotl named Pip who loved to explore. One day, while venturing further than usual, Pip discovered a shimmering, ancient coin that granted wishes!
"""
```

## Optional output (allowing None)

Some agents perform their work entirely through tool calls and don’t need to produce a final output — for example, an agent that updates a record via a tool and then stops. But with `str` in the `output_type` — including the default — the model is required to end its final turn with text. If it considers its work finished and has nothing left to say, it will return an empty response, or one containing only [thinking](https://pydantic.dev/docs/ai/capabilities/thinking/) content (as [Anthropic](https://pydantic.dev/docs/ai/models/anthropic/) models notably do), and Pydantic AI will ask it to produce text anyway.

Include `None` in the `output_type` when finishing without a final message is a valid outcome for your agent, and you’d rather receive `None` than have the model say something for the sake of saying it:

optional\_output.py

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-opus-5-5', output_type=str | None)

@agent.tool_plain
def mark_task_done(task_id: int) -> str:
    """Mark the task as done."""
    return f'Task {task_id} marked done.'

result = agent.run_sync('Mark task 1 as done, then stop without saying anything.')
print(result.output)
#> None
```

When the model returns an empty response and `None` is an allowed output type, the agent will return `None` instead of retrying. [Output validator functions](#output-validator-functions) still run with `None` as the argument, so you can raise [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry) to reject it if needed.

`output_type=str | None` is the canonical case: it’s handled as regular text output, and the **only** way the model signals `None` is by returning a response with no text output — an empty response, one whose text parts are all empty strings (as some OpenAI-compatible gateways produce), or one containing only [thinking](https://pydantic.dev/docs/ai/capabilities/thinking/) content, which some reasoning models emit after completing their work through a tool call. There’s no output tool or structured schema involved. This mirrors how plain `str` is already treated specially as free-form text output rather than a structured tool call.

`None` is also supported in the other output modes, with an extra structured commit path in addition to (or in place of) the empty-response fallback:

- **Bare unions including `None` that use tool mode** — e.g. `output_type=int | None`, `output_type=[int, float, None]`, or `output_type=[ToolOutput(Foo), None]`: a dedicated `final_result_None` output tool is exposed alongside the other output tools, so the model can commit to `None` through a tool call. An empty, blank-text, or thinking-only model response is still also treated as `None`, as with `str | None`.
- **Explicit output mode markers** — e.g. `output_type=ToolOutput(int | None)`, `output_type=NativeOutput([int, None])`, or `output_type=PromptedOutput([int, None])`: `None` is included as a branch of the structured schema the wrapper generates. The model commits by calling the tool with `null` (for `ToolOutput`) or by selecting the `None` branch of the discriminated schema (for `NativeOutput`/`PromptedOutput`). An empty response is **not** accepted — once you’ve opted into an explicit structured output mode, the model is expected to commit through the schema.

## Output cut off by the token limit

A response that reaches the [`max_tokens`](https://pydantic.dev/docs/ai/api/pydantic-ai/settings/#pydantic_ai.settings.ModelSettings.max_tokens) model setting, or the model’s own output limit, is cut off by the provider, and its [`finish_reason`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse.finish_reason) is `'length'`.

Text output, such as `str` or a [`TextOutput`](#text-output) function, has no shape to check, so text that was cut off is the run’s output like any other. When a complete answer matters, check the finish reason of the response it came from:

truncated\_text\_output.py

```python
from pydantic_ai import Agent, ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

def cut_off(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    # A deterministic stand-in for a model that reaches `max_tokens` mid-sentence.
    return ModelResponse(
        parts=[TextPart('The three largest cities are Tokyo, Delhi and')], finish_reason='length'
    )

agent = Agent(FunctionModel(cut_off))
result = agent.run_sync('Name the three largest cities.', model_settings={'max_tokens': 10})
print(result.output)
#> The three largest cities are Tokyo, Delhi and
if result.response.finish_reason == 'length':
    print('The answer was cut off.')
    #> The answer was cut off.
```

Structured output is validated, so output that was cut off is usually caught:

- With [`NativeOutput`](#native-output) or [`PromptedOutput`](#prompted-output), text that was cut off into JSON that doesn’t parse raises [`OutputTokenLimitExceeded`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.OutputTokenLimitExceeded) with a message naming the token limit, in [`run()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run) and [`run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream) alike. The model isn’t asked to try again, as it would run into the same limit. Text that was cut off but still parses is validated as usual, so it’s the output when it’s valid, and is retried when the schema or an [output validator](#output-validator-functions) rejects it.
- With [tool output](#tool-output), an output tool call whose arguments were cut off into JSON that doesn’t parse raises [`IncompleteToolCall`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.IncompleteToolCall) right away, in `run()` and `run_stream()` alike. Arguments that were cut off but still parse are validated as usual, and are retried when the schema or an output validator rejects them.
- A response that was cut off before it produced any output, say while the model was [thinking](https://pydantic.dev/docs/ai/capabilities/thinking/), raises `OutputTokenLimitExceeded`.

To get the whole answer, raise `max_tokens`, ask for a shorter one, or have [another model take over](https://pydantic.dev/docs/ai/capabilities/model-fallback/#token-limit).

## Streamed Results

There two main challenges with streamed results:

1. Validating structured responses before they’re complete, this is achieved by “partial validation” which was recently added to Pydantic in [pydantic/pydantic#10748](https://github.com/pydantic/pydantic/pull/10748).
2. When receiving a response, we don’t know if it’s the final response without starting to stream it and peeking at the content. Pydantic AI streams just enough of the response to sniff out if it’s a tool call or an output, then streams the whole thing and calls tools, or returns the stream as a [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult).

### Streaming Text

Example of streamed text output:

streamed\_hello\_world.py

```python
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash')  # (1)

async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:  # (2)
        async for message in result.stream_text():  # (3)
            print(message)
            #> The first known
            #> The first known use of "hello,
            #> The first known use of "hello, world" was in
            #> The first known use of "hello, world" was in a 1974 textbook
            #> The first known use of "hello, world" was in a 1974 textbook about the C
            #> The first known use of "hello, world" was in a 1974 textbook about the C programming language.
```

Streaming works with the standard [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) class, and doesn't require any special setup, just a model that supports streaming (currently all models support streaming).

The [`Agent.run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream) method is used to start a streamed run, this method returns a context manager so the connection can be closed when the stream completes.

Each item yield by [`StreamedRunResult.stream_text()`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.stream_text) is the complete text response, extended as new data is received.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

The optional `debounce_by` argument of [`stream_text()`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.stream_text) controls how long Pydantic AI groups incoming chunks before yielding. The default `0.1` groups chunks for up to 0.1 seconds; pass `None` to yield as soon as each chunk arrives. Debouncing is especially helpful for long structured responses, where it reduces the overhead of validating each chunk as it arrives.

We can also stream text as deltas rather than the entire text in each item:

streamed\_delta\_hello\_world.py

```python
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash')

async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:
        async for message in result.stream_text(delta=True):  # (1)
            print(message)
            #> The first known
            #> use of "hello,
            #> world" was in
            #> a 1974 textbook
            #> about the C
            #> programming language.
```

[`stream_text`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.stream_text) will error if the response is not text.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

### Streaming Structured Output

Here’s an example of streaming a user profile as it’s built:

streamed\_user\_profile.py

```python
from datetime import date
from typing import NotRequired

from typing_extensions import TypedDict

from pydantic_ai import Agent

class UserProfile(TypedDict):
    name: str
    dob: NotRequired[date]
    bio: NotRequired[str]

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=UserProfile,
    instructions='Extract a user profile from the input',
)

async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for profile in result.stream_output():
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

If a structured response takes a long time to appear in your application, make sure you stream validated partial output rather than waiting for the full run to finish. [`stream_output()`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.stream_output) yields the accumulated output as the model produces it, with partial validation applied to each snapshot and full validation applied to the final output.

When you also need events from intermediate model requests and tool calls, use [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.iter). Iterate over each `AgentStream` until the model starts producing the final result, then switch to `stream_output()` for validated partial output:

stream\_structured\_output\_and\_events.py

```python
from pydantic import BaseModel

from pydantic_ai import Agent, AgentStreamEvent, FinalResultEvent

class Client(BaseModel):
    id: int
    name: str

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=list[str | Client],
    instructions='Find the requested clients and explain each match.',
)

def record_event(event: AgentStreamEvent) -> None:
    ...

def render_output(output: list[str | Client]) -> None:
    ...

async def main():
    async with agent.iter('Find clients named Jane') as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as stream:
                    final_result_started = False
                    async for event in stream:
                        record_event(event)
                        if isinstance(event, FinalResultEvent):
                            final_result_started = True
                            break

                    if final_result_started:
                        async for output in stream.stream_output():
                            render_output(output)
            elif Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as stream:
                    async for event in stream:
                        record_event(event)
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

Each value from `stream_output()` is an accumulated snapshot, not a delta. An incomplete field or list item may be absent until enough data has arrived for it to pass partial validation, so update the rendered value from each snapshot rather than appending every yield.

`AgentStream` is a single iterator. Once you switch to `stream_output()`, it consumes the remaining final-output events while validating them, so those raw events are not also yielded to the preceding loop. If you need to retain every raw event, use [`run_stream_events()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events) and reconstruct and validate the output yourself.

As setting an `output_type` uses the [Tool Output](#tool-output) mode by default, this will only work if the model supports streaming tool arguments. For models that don’t, try [Native Output](#native-output) or [Prompted Output](#prompted-output) instead. With Gemini 3, use Native Output; with earlier Gemini models that also use function tools, use Prompted Output.

If you want fine-grained control of validation, you can use the following pattern to get the entire partial [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse):

streamed\_user\_profile.py

```python
from datetime import date

from pydantic import ValidationError
from typing_extensions import TypedDict

from pydantic_ai import Agent

class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str

agent = Agent('openai:gpt-6.1-sol', output_type=UserProfile)

async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for message in result.stream_response(debounce_by=0.01):  # (1)
            try:
                profile = await result.validate_response_output(  # (2)
                    message,
                    allow_partial=message.state == 'incomplete',
                )
            except ValidationError:
                continue
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

[`stream_response`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.stream_response) streams the data as [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse) objects, thus iteration can't fail with a `ValidationError`.

[`validate_response_output`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.validate_response_output) validates the data, `allow_partial=True` enables pydantic's [`experimental_allow_partial` flag on `TypeAdapter`](https://docs.pydantic.dev/latest/api/pydantic/type_adapter/#pydantic.type_adapter.TypeAdapter.validate_json).

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

### Cancelling Streams

Sometimes you need to stop a streaming response before it completes: a user clicks “stop generating” in a chat UI, you’ve received enough data to make a decision, or you want to avoid receiving more tokens. [`run_stream()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream) and [`iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter) support explicit cancellation by closing the underlying model stream. [`run_stream_events()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events) is an async context manager, so cleanup runs deterministically when you stop consuming events — leaving the `async with` block cancels the background run task. To stop a non-streaming run, see [Cancelling a Run](https://pydantic.dev/docs/ai/core-concepts/agent/#cancelling-a-run); to bound how long a single step may take, see [Timeouts](https://pydantic.dev/docs/ai/core-concepts/timeouts/).

#### Cleaning up run\_stream\_events

[`run_stream_events()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run_stream_events) is an async context manager that yields an async iterator over events:

stream\_cancel\_stream\_events.py

```python
from pydantic_ai import Agent, FinalResultEvent, PartStartEvent

agent = Agent('openai:gpt-6.1-sol')

async def main():
    async with agent.run_stream_events('Write a long essay about Python') as events:
        async for event in events:
            if isinstance(event, PartStartEvent):
                print(f'Started: {event.part!r}')
                #> Started: TextPart(content='Python is a ')
            elif isinstance(event, FinalResultEvent):
                break  # (1)
```

Breaking out of the loop leaves the `async with` block, which cancels the background run task and closes the HTTP connection.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

The yielded [`AgentRunEvents`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AgentRunEvents) handle exposes `cancel()` to cancel the whole run (see [Cancelling a Run](https://pydantic.dev/docs/ai/core-concepts/agent/#cancelling-a-run)); continued iteration then raises [`RunCancelled`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.RunCancelled). It also provides `all_messages()`, `new_messages()`, `usage`, and the completed `result`. From inside a tool or `event_stream_handler`, use [`RunContext.cancel()`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.cancel) instead. As a response-level alternative, [`StreamedRunResult.cancel()`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult.cancel) from `run_stream()` stops only the current model response.

#### Cancelling run\_stream

Call `cancel()` on the [`StreamedRunResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.StreamedRunResult) to cancel the stream:

stream\_cancel\_stream.py

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')

async def main():
    async with agent.run_stream('Write a long essay about Python') as result:
        text = ''
        async for chunk in result.stream_text(delta=True):
            text += chunk
            if len(text) > 100:  # (1)
                await result.cancel()  # (2)
                break
        print(result.cancelled)  # (3)
        #> True
        print(result.response.state == 'interrupted')  # (4)
        #> True
```

Check a condition during streaming, for example whether enough text has been received.

`cancel()` tells the model provider to stop generating tokens and closes the HTTP connection when the model integration supports it.

The `cancelled` property reflects the cancellation state.

The final [`ModelResponse`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ModelResponse) is marked with `state='interrupted'` so that downstream code can identify incomplete responses.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

If you `break` out of `stream_text()` and then leave the surrounding `async with` block, the stream is cleaned up as the context exits. Use `cancel()` when you want to stop generation immediately instead of only stopping local consumption.

#### Cancelling with iter

When using [`agent.iter()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.iter) for fine-grained control over the agent graph, you can cancel the [`AgentStream`](https://pydantic.dev/docs/ai/api/pydantic-ai/result/#pydantic_ai.result.AgentStream) inside a `ModelRequestNode.stream()` context:

stream\_cancel\_iter.py

```python
from pydantic_ai import Agent, FinalResultEvent

agent = Agent('openai:gpt-6.1-sol')

async def main():
    async with agent.iter('Write a long essay about Python') as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as stream:
                    async for event in stream:
                        if isinstance(event, FinalResultEvent):
                            await stream.cancel()  # (1)
                            break
```

`AgentStream.cancel()` cancels the stream at the model request level.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

To abort the run itself rather than just the current response — and for how cancellation is recorded in message history — see [Cancelling a Run](https://pydantic.dev/docs/ai/core-concepts/agent/#cancelling-a-run).

## Examples

The following examples demonstrate how to use streamed responses in Pydantic AI:

- [Stream markdown](https://pydantic.dev/docs/ai/examples/streaming/stream-markdown/)
- [Stream Whales](https://pydantic.dev/docs/ai/examples/streaming/stream-whales/)
