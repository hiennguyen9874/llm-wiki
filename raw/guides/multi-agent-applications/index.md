---
title: "Multi-agent Applications"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/guides/multi-agent-applications/"
domain: "pydantic.dev"
language: "en"
description: "Build multi-agent systems with Pydantic AI: delegate to sub-agents through tools, hand off between agents in your code, or orchestrate them with graphs."
word_count: 2082
---

There are roughly five levels of complexity when building applications with Pydantic AI:

1. Single agent workflows — what most of the `pydantic_ai` documentation covers
2. [Agent delegation](#agent-delegation) — agents using another agent via tools, either wired up by hand or with the Harness’s [`SubAgents`](https://pydantic.dev/docs/ai/harness/subagents/) capability
3. [Programmatic agent hand-off](#programmatic-agent-hand-off) — one agent runs, then application code calls another agent
4. [Graph based control flow](https://pydantic.dev/docs/ai/graph/graph/) — for the most complex cases, a graph-based state machine can be used to control the execution of multiple agents
5. [Deep Agents](#deep-agents) — autonomous agents with planning, file operations, task delegation, and sandboxed code execution

Of course, you can combine multiple strategies in a single application.

## Agent delegation

“Agent delegation” refers to the scenario where an agent delegates work to another agent, then takes back control when the delegate agent (the agent called from within a tool) finishes. If you want to hand off control to another agent completely, without coming back to the first agent, you can use an [output function](https://pydantic.dev/docs/ai/core-concepts/output/#output-functions).

Since agents are stateless and designed to be global, you do not need to include the agent itself in agent [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/).

You’ll generally want to pass [`ctx.usage`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext.usage) to the [`usage`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.AbstractAgent.run) keyword argument of the delegate agent run so usage within that run counts towards the total usage of the parent agent run.

[Cancellation](https://pydantic.dev/docs/ai/core-concepts/agent/#cancellation-and-sub-agents) is run-scoped: a delegate agent cancelling itself surfaces to the parent as a failed tool return rather than cancelling the parent, and a shared [`CancellationToken`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.CancellationToken) cancels a whole tree of runs at once.

agent\_delegation\_simple.py

```python
from pydantic_ai import Agent, RunContext, UsageLimits

joke_selection_agent = Agent(  # (1)
    'openai:gpt-6.1-sol',
    name='joke_selection_agent',  # (2)
    instructions=(
        'Use the `joke_factory` to generate some jokes, then choose the best. '
        'You must return just a single joke.'
    ),
)
joke_generation_agent = Agent(  # (3)
    'google:gemini-3.8-flash', name='joke_generation_agent', output_type=list[str]
)

@joke_selection_agent.tool
async def joke_factory(ctx: RunContext, count: int) -> list[str]:
    r = await joke_generation_agent.run(  # (4)
        f'Please generate {count} jokes.',
        usage=ctx.usage,  # (5)
    )
    return r.output  # (6)

result = joke_selection_agent.run_sync(
    'Tell me a joke.',
    usage_limits=UsageLimits(request_limit=5, total_tokens_limit=500),
)
print(result.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.
print(result.usage)
"""
RunUsage(
    cost=Decimal('0.00047625'),
    input_tokens=165,
    output_tokens=24,
    requests=3,
    tool_calls=1,
)
"""
```

The "parent" or controlling agent.

Passing `name` is optional but recommended when you run more than one agent: it labels each agent's run span, so naming both lets you tell the parent and delegate apart in [Logfire](https://pydantic.dev/docs/ai/integrations/logfire/). When omitted, the name is inferred from the variable the agent is assigned to and falls back to `'agent'` when it can't be (e.g. agents kept in a list or dict).

The "delegate" agent, which is called from within a tool of the parent agent.

Call the delegate agent from within a tool of the parent agent.

Pass the usage from the parent agent to the delegate agent so the final [`result.usage`](https://pydantic.dev/docs/ai/api/pydantic-ai/run/#pydantic_ai.run.AgentRunResult.usage) includes the usage from both agents.

Since the function returns `list[str]`, and the `output_type` of `joke_generation_agent` is also `list[str]`, we can simply return `r.output` from the tool.

*(This example is complete, it can be run “as is”)*

The control flow for this example is pretty simple and can be summarised as follows:

```
graph TD
  START --> joke_selection_agent
  joke_selection_agent --> joke_factory["joke_factory (tool)"]
  joke_factory --> joke_generation_agent
  joke_generation_agent --> joke_factory
  joke_factory --> joke_selection_agent
  joke_selection_agent --> END
```

### Agent delegation and dependencies

Generally the delegate agent needs to either have the same [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/) as the calling agent, or dependencies which are a subset of the calling agent’s dependencies.

agent\_delegation\_deps.py

```python
from dataclasses import dataclass

import httpx

from pydantic_ai import Agent, RunContext

@dataclass
class ClientAndKey:  # (1)
    http_client: httpx.AsyncClient
    api_key: str

joke_selection_agent = Agent(
    'openai:gpt-6.1-sol',
    name='joke_selection_agent',
    deps_type=ClientAndKey,  # (2)
    instructions=(
        'Use the `joke_factory` tool to generate some jokes on the given subject, '
        'then choose the best. You must return just a single joke.'
    ),
)
joke_generation_agent = Agent(
    'google:gemini-3.8-flash',
    name='joke_generation_agent',
    deps_type=ClientAndKey,  # (4)
    output_type=list[str],
    instructions=(
        'Use the "get_jokes" tool to get some jokes on the given subject, '
        'then extract each joke into a list.'
    ),
)

@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[ClientAndKey], count: int) -> list[str]:
    r = await joke_generation_agent.run(
        f'Please generate {count} jokes.',
        deps=ctx.deps,  # (3)
        usage=ctx.usage,
    )
    return r.output

@joke_generation_agent.tool  # (5)
async def get_jokes(ctx: RunContext[ClientAndKey], count: int) -> str:
    response = await ctx.deps.http_client.get(
        'https://example.com',
        params={'count': count},
        headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
    )
    response.raise_for_status()
    return response.text

async def main():
    async with httpx.AsyncClient() as client:
        deps = ClientAndKey(client, 'foobar')
        result = await joke_selection_agent.run('Tell me a joke.', deps=deps)
        print(result.output)
        #> Did you hear about the toothpaste scandal? They called it Colgate.
        print(result.usage)  # (6)
        """
        RunUsage(
            cost=Decimal('0.00054750'),
            input_tokens=220,
            output_tokens=32,
            requests=4,
            tool_calls=2,
        )
        """
```

Define a dataclass to hold the client and API key dependencies.

Set the `deps_type` of the calling agent — `joke_selection_agent` here.

Pass the dependencies to the delegate agent's run method within the tool call.

Also set the `deps_type` of the delegate agent — `joke_generation_agent` here.

Define a tool on the delegate agent that uses the dependencies to make an HTTP request.

Usage now includes 4 requests — 2 from the calling agent and 2 from the delegate agent.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

This example shows how even a fairly simple agent delegation can lead to a complex control flow:

```
graph TD
  START --> joke_selection_agent
  joke_selection_agent --> joke_factory["joke_factory (tool)"]
  joke_factory --> joke_generation_agent
  joke_generation_agent --> get_jokes["get_jokes (tool)"]
  get_jokes --> http_request["HTTP request"]
  http_request --> get_jokes
  get_jokes --> joke_generation_agent
  joke_generation_agent --> joke_factory
  joke_factory --> joke_selection_agent
  joke_selection_agent --> END
```

## Programmatic agent hand-off

“Programmatic agent hand-off” refers to the scenario where multiple agents are called in succession, with application code and/or a human in the loop responsible for deciding which agent to call next.

Here agents don’t need to use the same deps.

Here we show two agents used in succession, the first to find a flight and the second to extract the user’s seat preference.

programmatic\_handoff.py

```python
from typing import Literal

from pydantic import BaseModel, Field
from rich.prompt import Prompt

from pydantic_ai import Agent, ModelMessage, RunContext, RunUsage, UsageLimits

class FlightDetails(BaseModel):
    flight_number: str

class Failed(BaseModel):
    """Unable to find a satisfactory choice."""

flight_search_agent = Agent[object, FlightDetails | Failed](  # (1)
    'openai:gpt-6.1-sol',
    name='flight_search_agent',
    output_type=FlightDetails | Failed,
    instructions=(
        'Use the "flight_search" tool to find a flight '
        'from the given origin to the given destination.'
    ),
)

@flight_search_agent.tool  # (2)
async def flight_search(
    ctx: RunContext, origin: str, destination: str
) -> FlightDetails | None:
    # in reality, this would call a flight search API or
    # use a browser to scrape a flight search website
    return FlightDetails(flight_number='AK456')

usage_limits = UsageLimits(request_limit=15)  # (3)

async def find_flight(usage: RunUsage) -> FlightDetails | None:  # (4)
    message_history: list[ModelMessage] | None = None
    for _ in range(3):
        prompt = Prompt.ask(
            'Where would you like to fly from and to?',
        )
        result = await flight_search_agent.run(
            prompt,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, FlightDetails):
            return result.output
        else:
            message_history = result.all_messages(
                output_tool_return_content='Please try again.'
            )

class SeatPreference(BaseModel):
    row: int = Field(ge=1, le=30)
    seat: Literal['A', 'B', 'C', 'D', 'E', 'F']

# This agent is responsible for extracting the user's seat selection
seat_preference_agent = Agent[object, SeatPreference | Failed](  # (5)
    'openai:gpt-6.1-sol',
    name='seat_preference_agent',
    output_type=SeatPreference | Failed,
    instructions=(
        "Extract the user's seat preference. "
        'Seats A and F are window seats. '
        'Row 1 is the front row and has extra leg room. '
        'Rows 14, and 20 also have extra leg room. '
    ),
)

async def find_seat(usage: RunUsage) -> SeatPreference:  # (6)
    message_history: list[ModelMessage] | None = None
    while True:
        answer = Prompt.ask('What seat would you like?')

        result = await seat_preference_agent.run(
            answer,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        if isinstance(result.output, SeatPreference):
            return result.output
        else:
            print('Could not understand seat preference. Please try again.')
            message_history = result.all_messages()

async def main():  # (7)
    usage: RunUsage = RunUsage()

    opt_flight_details = await find_flight(usage)
    if opt_flight_details is not None:
        print(f'Flight found: {opt_flight_details.flight_number}')
        #> Flight found: AK456
        seat_preference = await find_seat(usage)
        print(f'Seat preference: {seat_preference}')
        #> Seat preference: row=1 seat='A'
```

Define the first agent, which finds a flight. We use an explicit type annotation until [PEP-747](https://peps.python.org/pep-0747/) lands, see [structured output](https://pydantic.dev/docs/ai/core-concepts/output/#structured-output). We use a union as the output type so the model can communicate if it's unable to find a satisfactory choice; internally, each member of the union will be registered as a separate tool.

Define a tool on the agent to find a flight. In this simple case we could dispense with the tool and just define the agent to return structured data, then search for a flight, but in more complex scenarios the tool would be necessary.

Define usage limits for the entire app.

Define a function to find a flight, which asks the user for their preferences and then calls the agent to find a flight.

As with `flight_search_agent` above, we use an explicit type annotation to define the agent.

Define a function to find the user's seat preference, which asks the user for their seat preference and then calls the agent to extract the seat preference.

Now that we've put our logic for running each agent into separate functions, our main app becomes very simple.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

The control flow for this example can be summarised as follows:

```
graph TB
  START --> ask_user_flight["ask user for flight"]

  subgraph find_flight
    flight_search_agent --> ask_user_flight
    ask_user_flight --> flight_search_agent
  end

  flight_search_agent --> ask_user_seat["ask user for seat"]
  flight_search_agent --> END

  subgraph find_seat
    seat_preference_agent --> ask_user_seat
    ask_user_seat --> seat_preference_agent
  end

  seat_preference_agent --> END
```

## Pydantic Graphs

See the [graph](https://pydantic.dev/docs/ai/graph/graph/) documentation on when and how to use graphs.

## Deep Agents

Deep agents are autonomous agents that combine multiple architectural patterns and capabilities to handle complex, multi-step tasks reliably. [Pydantic AI Harness](https://pydantic.dev/docs/ai/harness/) ships each of these patterns as a capability you can compose with Pydantic AI’s built-in features:

- **Planning and progress tracking** — agents break down complex tasks into steps and track their progress, giving users visibility into what the agent is working on. See [`Planning`](https://pydantic.dev/docs/ai/harness/planning/).
- **File system operations** — reading, writing, and editing files in the run’s workspace, on the local machine or in a sandboxed container. See [`FileSystem`](https://pydantic.dev/docs/ai/harness/filesystem/) and [`Shell`](https://pydantic.dev/docs/ai/harness/shell/).
- **Task delegation** — spawning specialized sub-agents for specific tasks, with isolated context to prevent recursive delegation issues. See [`SubAgents`](https://pydantic.dev/docs/ai/harness/subagents/) and [Agent Delegation](#agent-delegation) above.
- **Sandboxed code execution** — running AI-generated code in isolated environments to prevent accidents. See [`Shell`](https://pydantic.dev/docs/ai/harness/shell/) with a workspace backend such as [`DockerContainer`](https://pydantic.dev/docs/ai/harness/docker-container/), and [`CodeMode`](https://pydantic.dev/docs/ai/harness/code-mode/).
- **Context management** — automatic conversation compaction to handle long sessions that would otherwise exceed token limits. See [Compaction](https://pydantic.dev/docs/ai/capabilities/compaction/) and the Harness [compaction strategies](https://pydantic.dev/docs/ai/harness/compaction/).
- **Human-in-the-loop** — approval workflows for dangerous operations like code execution or file deletion. See [Requiring Tool Approval](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#requiring-tool-approval).
- **Durable execution** — preserving agent state across transient API failures and application errors or restarts. See [Durable Execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/).

For a ready-made assembly of these pieces, [`Coder`](https://pydantic.dev/docs/ai/harness/coder/) combines file system, shell, delegation, and context management capabilities into a coding agent you can use whole or take apart.

## Observing Multi-Agent Systems

Multi-agent systems can be challenging to debug due to their complexity; when multiple agents interact, understanding the flow of execution becomes essential.

### Tracing Agent Delegation

Run `uvx logfire-cli wizard --task pydantic-ai` once from your project to [set up Logfire](https://pydantic.dev/docs/ai/integrations/logfire/#using-logfire) and trace the entire flow across multiple agents. It has your coding agent add this instrumentation:

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()

# Your multi-agent code here...
```

Logfire shows you:

- **Which agent handled which part** of the request
- **Delegation decisions**—when and why one agent called another
- **End-to-end latency** broken down by agent
- **Token usage and costs** per agent
- **What triggered the agent run**—the HTTP request, scheduled job, or user action that started it all
- **What happened inside tool calls**—database queries, HTTP requests, file operations, and any other instrumented code that tools execute

This is essential for understanding and optimizing complex agent workflows. When something goes wrong in a multi-agent system, you’ll see exactly which agent failed and what it was trying to do, and whether the problem was in the agent’s reasoning or in the backend systems it called.

### Full-Stack Visibility

If your Pydantic AI application includes a TypeScript frontend, API gateway, or services in other languages, Logfire can trace them too—Logfire provides SDKs for Python, JavaScript/TypeScript, and Rust, plus compatibility with any OpenTelemetry-instrumented application. See traces from your entire stack in a unified view. For details on sending data from other languages using standard OpenTelemetry, see the [alternative clients guide](https://logfire.pydantic.dev/docs/how-to-guides/alternative-clients/).

Pydantic AI’s instrumentation is built on [OpenTelemetry](https://opentelemetry.io/), so you can also use any OTel-compatible backend. See the [Logfire integration guide](https://pydantic.dev/docs/ai/integrations/logfire/#using-logfire) for details.

## Examples

The following examples demonstrate how to use multi-agent patterns in Pydantic AI:

- [Flight booking](https://pydantic.dev/docs/ai/examples/complex-workflows/flight-booking/)
