---
title: "Direct Model Requests"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/core-concepts/direct/"
domain: "pydantic.dev"
language: "en"
description: "Make low-level requests to any LLM with the Pydantic AI direct API when you only need input and output schema translation, not the full Agent machinery."
word_count: 539
---

The `direct` module provides low-level methods for making imperative requests to LLMs where the only abstraction is input and output schema translation, enabling you to use all models with the same API.

These methods are thin wrappers around the [`Model`](https://pydantic.dev/docs/ai/api/models/base/#pydantic_ai.models.Model) implementations, offering a simpler interface when you don’t need the full functionality of an [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent).

The following functions are available:

- [`model_request`](https://pydantic.dev/docs/ai/api/pydantic-ai/direct/#pydantic_ai.direct.model_request): Make a non-streamed async request to a model
- [`model_request_sync`](https://pydantic.dev/docs/ai/api/pydantic-ai/direct/#pydantic_ai.direct.model_request_sync): Make a non-streamed synchronous request to a model
- [`model_request_stream`](https://pydantic.dev/docs/ai/api/pydantic-ai/direct/#pydantic_ai.direct.model_request_stream): Make a streamed async request to a model
- [`model_request_stream_sync`](https://pydantic.dev/docs/ai/api/pydantic-ai/direct/#pydantic_ai.direct.model_request_stream_sync): Make a streamed sync request to a model
- [`model_request_batch`](https://pydantic.dev/docs/ai/api/pydantic-ai/direct/#pydantic_ai.direct.model_request_batch): Make several requests through a model’s batch API at a lower cost; see [Batch processing](https://pydantic.dev/docs/ai/core-concepts/batch/#direct-batch-requests)

## Basic Example

Here’s a simple example demonstrating how to use the direct API to make a basic request:

direct\_basic.py

```python
from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')]
)

print(model_response.text)
#> The capital of France is Paris.
print(model_response.usage)
#> RequestUsage(input_tokens=56, output_tokens=7)
```

*(This example is complete, it can be run “as is”)*

## Advanced Example with Tool Calling

You can also use the direct API to work with function/tool calling.

Even here we can use Pydantic to generate the JSON schema for the tool:

```python
from typing import Literal

from pydantic import BaseModel

from pydantic_ai import ModelRequest, ToolDefinition
from pydantic_ai.direct import model_request
from pydantic_ai.models import ModelRequestParameters

class Divide(BaseModel):
    """Divide two numbers."""

    numerator: float
    denominator: float
    on_inf: Literal['error', 'infinity'] = 'infinity'

async def main():
    # Make a request to the model with tool access
    model_response = await model_request(
        'openai:gpt-6-luna',
        [ModelRequest.user_text_prompt('What is 123 / 456?')],
        model_request_parameters=ModelRequestParameters(
            function_tools=[
                ToolDefinition(
                    name=Divide.__name__.lower(),
                    description=Divide.__doc__,
                    parameters_json_schema=Divide.model_json_schema(),
                )
            ],
            allow_text_output=True,  # Allow model to either use tools or respond directly
        ),
    )
    print(model_response)
    """
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='divide',
                args={'numerator': '123', 'denominator': '456'},
                tool_call_id='pyd_ai_2e0e396768a14fe482df90a29a78dc7b',
            )
        ],
        usage=RequestUsage(input_tokens=55, output_tokens=7),
        model_name='gpt-6-luna',
        timestamp=datetime.datetime(...),
    )
    """
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## When to Use the direct API vs Agent

The direct API is ideal when:

1. You need more direct control over model interactions
2. You want to implement custom behavior around model requests
3. You’re building your own abstractions on top of model interactions

For most application use cases, the higher-level [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) API provides a more convenient interface with additional features such as native tool execution, retrying, structured output parsing, and more.

## OpenTelemetry or Logfire Instrumentation

As with [agents](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent), you can enable OpenTelemetry/Logfire instrumentation with just a few extra lines

direct\_instrumented.py

```python
import logfire

from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

logfire.configure()
logfire.instrument_pydantic_ai()

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')],
)

print(model_response.text)
#> The capital of France is Paris.
```

*(This example is complete, it can be run “as is”)*

You can also enable OpenTelemetry on a per call basis:

direct\_instrumented.py

```python
import logfire

from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

logfire.configure()

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')],
    instrument=True
)

print(model_response.text)
#> The capital of France is Paris.
```

See [Debugging and Monitoring](https://pydantic.dev/docs/ai/integrations/logfire/#using-logfire) for Logfire setup and more details, including how to instrument with plain OpenTelemetry without Logfire.
