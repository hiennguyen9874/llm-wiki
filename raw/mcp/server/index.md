---
title: "Server"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/mcp/server/"
domain: "pydantic.dev"
language: "en"
description: "Use Pydantic AI agents inside the tools of your own MCP server, and route their LLM calls back through the connected client with MCP sampling."
word_count: 569
---

Pydantic AI models can also be used within MCP Servers.

## MCP Server

Here’s a simple example of a [Python MCP server](https://github.com/modelcontextprotocol/python-sdk) using Pydantic AI within a tool call:

mcp\_server.py

```python
from mcp.server.fastmcp import FastMCP

from pydantic_ai import Agent

server = FastMCP('Pydantic AI Server')
server_agent = Agent(
    'anthropic:claude-haiku-5-5', instructions='always reply in rhyme'
)

@server.tool()
async def poet(theme: str) -> str:
    """Poem generator"""
    r = await server_agent.run(f'write a poem about {theme}')
    return r.output

if __name__ == '__main__':
    server.run()
```

## Simple client

This server can be queried with any MCP client. Here is an example using the Python SDK directly:

mcp\_client.py

```
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

async def client():
    server_params = StdioServerParameters(
        command='python', args=['mcp_server.py'], env=dict(os.environ)
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool('poet', {'theme': 'socks'})
            content = result.content[0]
            assert isinstance(content, TextContent)
            print(content.text)
            """
            Oh, socks, those garments soft and sweet,
            That nestle softly 'round our feet,
            From cotton, wool, or blended thread,
            They keep our toes from feeling dread.
            """

if __name__ == '__main__':
    asyncio.run(client())
```

## MCP Sampling

When Pydantic AI agents are used within MCP servers, they can use sampling via [`MCPSamplingModel`](https://pydantic.dev/docs/ai/api/models/mcp-sampling/#pydantic_ai.models.mcp_sampling.MCPSamplingModel).

You can continue a conversation from another model by passing its `message_history` to the sampling agent. Function tool calls, results, and retry feedback in that history are preserved using MCP’s native tool content blocks, which require a client supporting the 2025-11-25 sampling format or later. Multimodal tool results are not yet supported. Replaying tool history does not enable the sampling agent to call new tools.

We can extend the above example to use sampling so instead of connecting directly to the LLM, the agent calls back through the MCP client to make LLM calls.

mcp\_server\_sampling.py

```
from mcp.server.fastmcp import Context, FastMCP

from pydantic_ai import Agent
from pydantic_ai.models.mcp_sampling import MCPSamplingModel

server = FastMCP('Pydantic AI Server with sampling')
server_agent = Agent(instructions='always reply in rhyme')

@server.tool()
async def poet(ctx: Context, theme: str) -> str:
    """Poem generator"""
    r = await server_agent.run(f'write a poem about {theme}', model=MCPSamplingModel(session=ctx.session))
    return r.output

if __name__ == '__main__':
    server.run()  # run the server over stdio
```

The [above](#simple-client) client does not support sampling, so if you tried to use it with this server you’d get an error.

The simplest way to support sampling in an MCP client is to [use](https://pydantic.dev/docs/ai/mcp/client/#mcp-sampling) a Pydantic AI agent as the client, but if you wanted to support sampling with the vanilla MCP SDK, you could do so like this:

mcp\_client\_sampling.py

```
import asyncio
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    ErrorData,
    TextContent,
)

async def sampling_callback(
    context: RequestContext[ClientSession, Any], params: CreateMessageRequestParams
) -> CreateMessageResult | ErrorData:
    print('sampling system prompt:', params.systemPrompt)
    #> sampling system prompt: always reply in rhyme
    print('sampling messages:', params.messages)
    """
    sampling messages:
    [
        SamplingMessage(
            role='user',
            content=TextContent(
                type='text',
                text='write a poem about socks',
                annotations=None,
                meta=None,
            ),
            meta=None,
        )
    ]
    """

    # TODO get the response content by calling an LLM...
    response_content = 'Socks for a fox.'

    return CreateMessageResult(
        role='assistant',
        content=TextContent(type='text', text=response_content),
        model='fictional-llm',
    )

async def client():
    server_params = StdioServerParameters(command='python', args=['mcp_server_sampling.py'])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write, sampling_callback=sampling_callback) as session:
            await session.initialize()
            result = await session.call_tool('poet', {'theme': 'socks'})
            content = result.content[0]
            assert isinstance(content, TextContent)
            print(content.text)
            #> Socks for a fox.

if __name__ == '__main__':
    asyncio.run(client())
```

*(This example is complete, it can be run “as is”)*
