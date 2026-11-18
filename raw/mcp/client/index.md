---
title: "Client"
site: "Pydantic Docs"
source: "https://pydantic.dev/docs/ai/mcp/client/"
domain: "pydantic.dev"
language: "en"
description: "Connect Pydantic AI agents to MCP servers over Streamable HTTP, SSE or stdio, load them from config, and use sampling, elicitation, resources and auth."
word_count: 4654
---

Pydantic AI can act as an [MCP client](https://modelcontextprotocol.io/quickstart/client), connecting to MCP servers to use their tools as part of an agent run. The [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) [toolset](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/) wraps the [FastMCP Client](https://gofastmcp.com/clients/) and works with both local (stdio) and remote (Streamable HTTP, SSE) MCP servers.

## Install

You need to either install [`pydantic-ai`](https://pydantic.dev/docs/ai/overview/install/), or [`pydantic-ai-slim`](https://pydantic.dev/docs/ai/overview/install/#slim-install) with the `mcp` optional group:

Terminal

```bash
pip install "pydantic-ai-slim[mcp]"
```

## Usage

An [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) accepts any of the following as its first positional argument:

- A URL string (Streamable HTTP, or SSE if the path ends in `/sse`)
- A path to a local Python or Node.js script (run via stdio)
- A [FastMCP transport](https://gofastmcp.com/clients/transports) like [`StdioTransport`](https://gofastmcp.com/clients/transports), [`StreamableHttpTransport`](https://gofastmcp.com/clients/transports), or [`SSETransport`](https://gofastmcp.com/clients/transports)
- A pre-built [`fastmcp.Client`](https://gofastmcp.com/clients/client) (for advanced FastMCP-specific configuration like [OAuth](https://gofastmcp.com/clients/auth/oauth) or [tool transformation](https://gofastmcp.com/patterns/tool-transformation))
- An in-process [FastMCP server](https://gofastmcp.com/servers/) (for testing or single-process deployments — no network round trip)

Each `MCPToolset` instance is a [toolset](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/) and can be registered with an [`Agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent) via the `toolsets` argument.

You can use [`async with agent`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.__aenter__) to open and close connections to all registered MCP toolsets (and in the case of stdio servers, start and stop the subprocesses) around the context where they’ll be used in agent runs. You can also use `async with toolset` to manage the lifecycle of a specific toolset directly, for example if you’d like to share it across multiple agents. If you don’t explicitly enter one of these context managers, the toolset will be opened and closed automatically as needed.

Note that a shared `MCPToolset` instance connects to the server as a single identity; if your users have their own credentials for the MCP server, see [per-user authentication](#per-user-authentication).

### Streamable HTTP

The [Streamable HTTP](https://modelcontextprotocol.io/introduction#streamable-http) transport is the recommended way to connect to a remote MCP server.

Before creating the toolset, we need to run a server that supports the Streamable HTTP transport.

streamable\_http\_server.py

```python
from mcp.server.fastmcp import FastMCP

app = FastMCP()

@app.tool()
def add(a: int, b: int) -> int:
    return a + b

if __name__ == '__main__':
    app.run(transport='streamable-http')
```

Then we can create the toolset:

mcp\_streamable\_http\_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset('http://localhost:8000/mcp')  # (1)
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])  # (2)

async def main():
    result = await agent.run('What is 7 plus 5?')
    print(result.output)
    #> The answer is 12.
```

Define the MCP toolset with the URL used to connect.

Create an agent with the MCP toolset attached.

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

**What’s happening here?**

- The model receives the prompt “What is 7 plus 5?”
- The model decides “Oh, I’ve got this `add` tool, that will be a good way to answer this question”
- The model returns a tool call
- Pydantic AI sends the tool call to the MCP server using the Streamable HTTP transport
- The model is called again with the return value of running the `add` tool (12)
- The model returns the final answer

To visualise this clearly and see the tool call, run `uvx logfire-cli wizard --task pydantic-ai` once from your project. It [sets up Logfire](https://pydantic.dev/docs/ai/integrations/logfire/#using-logfire) and has your coding agent add these three lines:

mcp\_streamable\_http\_client\_logfire.py

```python
import logfire

logfire.configure()
logfire.instrument_pydantic_ai()
```

### SSE

The [HTTP + Server-Sent Events](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#http-with-sse) transport is also supported. URLs ending in `/sse` are auto-detected as SSE; for any other path, pass an explicit [`SSETransport`](https://gofastmcp.com/clients/transports).

mcp\_sse\_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset('http://localhost:3001/sse')
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

### Stdio

MCP also offers the [stdio transport](https://modelcontextprotocol.io/specification/2024-11-05/basic/transports#stdio), where the server is run as a subprocess and communicates with the client over `stdin` and `stdout`. Pass a path to a Python or Node.js script, or build a [`StdioTransport`](https://gofastmcp.com/clients/transports) for full control over the command, arguments, and environment.

mcp\_stdio\_client.py

```python
from fastmcp.client.transports import StdioTransport

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(StdioTransport(command='python', args=['mcp_server.py']))
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

### In-process FastMCP server

If you already have a [FastMCP server](https://gofastmcp.com/servers/) in the same Python process as your agent, you can hand it directly to `MCPToolset` and save the network round trip:

mcp\_in\_process\_server.py

```python
from fastmcp import FastMCP

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

fastmcp_server = FastMCP('my_server')

@fastmcp_server.tool()
async def add(a: int, b: int) -> int:
    return a + b

toolset = MCPToolset(fastmcp_server)
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])

async def main():
    result = await agent.run('What is 7 plus 5?')
    print(result.output)
    #> The answer is 12.
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

## Loading MCP toolsets from configuration

Instead of constructing `MCPToolset` instances individually, you can load multiple toolsets from a JSON configuration file using [`load_mcp_toolsets()`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.load_mcp_toolsets).

This is particularly useful when you need to manage multiple MCP servers or want to configure servers externally without modifying code.

### Configuration format

The configuration file should be a JSON file with an `mcpServers` object containing server definitions. Each server is identified by a unique key and contains the configuration for that server:

mcp\_config.json

```json
{
  "mcpServers": {
    "python-runner": {
        "command": "uv",
        "args": ["run", "mcp-run-python", "stdio"]
    },
    "weather": {
      "command": "python",
      "args": ["mcp_server.py"]
    },
    "weather-api": {
      "url": "http://localhost:3001/sse"
    },
    "calculator": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

Each entry supports `command`, `args`, `env` and `cwd` for a stdio server, or `url` and `headers` for an HTTP server. An entry with both runs `command` and ignores `url` and `headers`, as FastMCP does. The configuration is validated as it’s loaded, so a wrongly-typed field is reported straight away instead of failing later at connection time. Unknown keys are ignored, so a file shared with another MCP client still loads — but they are only ignored, never honoured. In particular `disabled` does not skip a server, and `type` does not choose the transport: that is inferred from the URL, as described below.

### Environment variables

The configuration file supports environment variable expansion using the `${VAR}` and `${VAR:-default}` syntax, [like Claude Code](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json). This is useful for keeping sensitive information like API keys or host names out of your configuration files:

mcp\_config\_with\_env.json

```json
{
  "mcpServers": {
    "python-runner": {
      "command": "${PYTHON_CMD:-python3}",
      "args": ["run", "${MCP_MODULE}", "stdio"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    },
    "weather-api": {
      "url": "https://${SERVER_HOST:-localhost}:${SERVER_PORT:-8080}/sse"
    }
  }
}
```

When loading this configuration with [`load_mcp_toolsets()`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.load_mcp_toolsets):

- `${VAR}` references are replaced with the corresponding environment variable values.
- `${VAR:-default}` references use the environment variable value if set, otherwise the default value.

### Usage

mcp\_config\_loader.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import load_mcp_toolsets

# Load all toolsets from the configuration file
toolsets = load_mcp_toolsets('mcp_config.json')

# Create an agent with all loaded toolsets
agent = Agent('openai:gpt-6.1-sol', toolsets=toolsets)

async def main():
    result = await agent.run('What is 7 plus 5?')
    print(result.output)
```

## Tool call customization

`MCPToolset` accepts a `process_tool_call` callback that lets you customize tool call requests and their responses. A common use case is to inject metadata that the server-side handler needs to read:

mcp\_process\_tool\_call.py

```python
from typing import Any

from fastmcp.client.transports import StdioTransport

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import CallToolFunc, MCPToolset, ToolResult
from pydantic_ai.models.test import TestModel

async def process_tool_call(
    ctx: RunContext[int],
    call_tool: CallToolFunc,
    name: str,
    tool_args: dict[str, Any],
) -> ToolResult:
    """A tool call processor that passes along the deps."""
    return await call_tool(name, tool_args, metadata={'deps': ctx.deps})

toolset = MCPToolset(
    StdioTransport(command='python', args=['mcp_server.py']),
    process_tool_call=process_tool_call,
)
agent = Agent(
    model=TestModel(call_tools=['echo_deps']),
    deps_type=int,
    toolsets=[toolset],
)

async def main():
    result = await agent.run('Echo with deps set to 42', deps=42)
    print(result.output)
    #> {"echo_deps":{"echo":"This is an echo message","deps":42}}
```

How the server reads the injected metadata is MCP server SDK specific. For example, with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) it’s accessible via the [`ctx: Context`](https://github.com/modelcontextprotocol/python-sdk#context) argument on tool handlers:

mcp\_server.py

```python
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession

mcp = FastMCP('Pydantic AI MCP Server')

@mcp.tool()
async def echo_deps(ctx: Context[ServerSession, None]) -> dict[str, Any]:
    """Echo the run context.

    Args:
        ctx: Context object containing request and session information.

    Returns:
        Dictionary with an echo message and the deps.
    """
    await ctx.info('This is an info message')

    deps: Any = getattr(ctx.request_context.meta, 'deps')
    return {'echo': 'This is an echo message', 'deps': deps}

if __name__ == '__main__':
    mcp.run()
```

## Tool errors

When an MCP server reports a tool error, [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) lets you choose whether that error should ask the model to retry, appear as a failed tool result, or escape as an exception:

| `tool_error_behavior` | Behavior |
| --- | --- |
| `'retry'` | Default. Raises [`ModelRetry`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ModelRetry), sending the server error back to the model as a retried tool result. Use this when the model may be able to correct the call. |
| `'failed'` | Raises [`ToolFailed`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.ToolFailed), which is recorded as a tool result with `outcome='failed'`. Use this when the tool call is complete but failed, and the model should decide what to do next. |
| `'error'` | Propagates the underlying MCP tool exception and fails the agent run. Use this for errors you want application code to handle outside the model loop. |

Structured error content is serialized as JSON in the model-visible message for both `'retry'` and `'failed'`, so retryability hints and other machine-readable details remain available to the model. Protocol and transport errors are not reported as completed failed tool calls.

This is the MCP equivalent of the [tool retry](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries) vs [failed tool result](https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-failed) distinction in local tool code.

## Tool prefixes to avoid naming conflicts

When connecting to multiple MCP servers that might provide tools with the same name, wrap each `MCPToolset` with [`.prefixed(...)`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.prefixed) to prepend a prefix to its tool names:

mcp\_tool\_prefix.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

weather = MCPToolset('http://localhost:3001/sse').prefixed('weather')   # `weather_*`
calculator = MCPToolset('http://localhost:3002/sse').prefixed('calc')   # `calc_*`

# Both servers may expose a `get_data` tool, but they're disambiguated as
# `weather_get_data` and `calc_get_data`.
agent = Agent('openai:gpt-6.1-sol', toolsets=[weather, calculator])
```

The [`MCP` capability](https://pydantic.dev/docs/ai/capabilities/mcp/#tool-names) does the same with `tool_prefix='weather'`, or with `tool_prefix=True` to use its explicit `id=` as the prefix.

## Server instructions

MCP servers can provide instructions during initialization that give context about how to best interact with the server’s tools. These are accessible via [`MCPToolset.instructions`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.instructions) after the connection is established, and can be added to the agent’s instructions by setting `include_instructions=True`:

mcp\_server\_include\_instructions.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset('http://localhost:8000/mcp', id='docs', include_instructions=True)
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

On `MCPToolset` this is off by default because the server writes this text, and the model receives it with the same authority as the instructions you write yourself. Only enable it for servers you trust. The [`MCP`](https://pydantic.dev/docs/ai/capabilities/mcp/) capability turns it on for the local toolset it builds, so for a server you don’t trust, pass [`include_instructions=False`](https://pydantic.dev/docs/ai/capabilities/mcp/#server-instructions) to the capability.

The instructions are read each time the toolset connects, which by default is once per agent run, and on a toolset with an [`id`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.id) they [append their changes](https://pydantic.dev/docs/ai/core-concepts/agent/#appending-instruction-changes). If the server sends different instructions on a later connection, as when it’s redeployed between turns of a conversation, the new text is appended to the conversation rather than rewriting the instruction prefix that the provider has cached. The model receives them in a `<pyai:context id="toolset:<id>">` element, so it can tell which server they came from.

A toolset for a server URL that you don’t give an `id` takes the URL’s hostname as its `id`, as in `toolset:localhost`, with `-` in place of the `:`s of an IPv6 address. Only an `id` you choose is stamped as the `toolset_id` of the server’s tool definitions, and [durable execution](https://pydantic.dev/docs/ai/capabilities/durable_execution/overview/) doesn’t accept a derived one: name the toolset with `id=` there. If two toolsets would take the same hostname, as for two servers on one host, neither keeps it for its instructions, which then rewrite the prefix as plain text, with a warning suggesting a distinct `id=` for each. A stdio or in-process server without an `id` has nothing to key its instructions by either, so pass `id=` to append them.

## Tool metadata

MCP tools can include metadata that provides additional information about the tool’s characteristics, which can be useful when [filtering tools](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.FilteredToolset). The `meta` and `annotations` fields can be found on the `metadata` dict on the [`ToolDefinition`](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.ToolDefinition) object that’s passed to filter functions, and the tool’s output schema (if any) is available as the `return_schema` field.

[`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) additionally exposes a `task: bool` flag indicating whether the toolset will use [task-augmented execution](#background-tasks) for the tool. For tools where task support is optional, this reflects the `prefer_tasks` setting.

Tools with an [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview) `_meta.ui.visibility` that leaves out `"model"` are not exposed to the model, since the server meant them only for its own UI.

## Background tasks

[`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) supports MCP [task-augmented execution](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks) (SEP-1686). Servers using SEP-1686, including FastMCP 3 servers, can declare per-tool task support via `execution.taskSupport`, and `MCPToolset` routes calls accordingly:

| `execution.taskSupport` | Behavior |
| --- | --- |
| `"required"` | Always calls with `task=True`. The server creates a task and the client awaits the final result via `tasks/result`. |
| `"optional"` | Calls with `task=True` by default. Set [`prefer_tasks=False`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.prefer_tasks) to call normally instead. |
| `"forbidden"` or absent | Calls normally. |

FastMCP 4 uses the newer MCP [Tasks extension](https://tasks.extensions.modelcontextprotocol.io/seps/2663-tasks-extension) (SEP-2663), where the server directs task creation. The `task` metadata and `prefer_tasks` client preference above therefore apply to FastMCP 3, not FastMCP 4. An ordinary call drives a task-only tool to completion with nothing extra installed; explicitly selecting the tasks extension with `use_task=True` requires the separate `fastmcp-tasks` package, available via the `mcp-tasks` optional group: `pip install "pydantic-ai-slim[mcp-tasks]"`.

For [FastMCP 3](https://gofastmcp.com/v3/servers/tasks) servers, install the tasks extra with `pip install "fastmcp[tasks]>=3,<4"` and declare task support per tool with `task=TaskConfig(mode=...)`:

background\_task\_server.py

```python
from fastmcp import FastMCP
from fastmcp.server.tasks import TaskConfig

mcp = FastMCP('long_running_server')

@mcp.tool(task=TaskConfig(mode='optional'))
async def deep_research(topic: str) -> str:
    import asyncio
    await asyncio.sleep(0)
    return f'Researched {topic}'

if __name__ == '__main__':
    mcp.run(transport='streamable-http')
```

By default, [`MCPToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset) uses task-augmented execution when a tool supports it. A client that prefers normal calls for tools where task support is optional can set [`prefer_tasks=False`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.prefer_tasks). This setting does not affect tools where task support is required:

background\_task\_client.py

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset('http://localhost:8000/mcp', prefer_tasks=False)
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

## Resources

MCP servers can provide [resources](https://modelcontextprotocol.io/docs/concepts/resources) — files, data, or content that can be accessed by the client. Resources in MCP are application-driven, with host applications determining how to incorporate context manually based on their needs. They are *not* exposed to the LLM automatically (unless a tool returns a `ResourceLink` or `EmbeddedResource`).

`MCPToolset` exposes methods to discover and read resources:

- [`list_resources()`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.list_resources) — list all available resources on the server
- [`list_resource_templates()`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.list_resource_templates) — list resource templates with parameter placeholders
- [`read_resource(uri)`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.read_resource) — read the contents of a specific resource by URI
- [`read_resource_for_app(uri)`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.read_resource_for_app) — read a resource as the MCP result, keeping each item’s MIME type and `_meta`

Text content is returned as `str`, and binary content as [`BinaryContent`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.BinaryContent).

Before consuming resources, we need to run a server that exposes some:

mcp\_resource\_server.py

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('Pydantic AI MCP Server')

@mcp.resource('resource://user_name.txt', mime_type='text/plain')
async def user_name_resource() -> str:
    return 'Alice'

if __name__ == '__main__':
    mcp.run()
```

Then we can read them from the client:

mcp\_resources.py

```python
import asyncio

from fastmcp.client.transports import StdioTransport

from pydantic_ai.mcp import MCPToolset

async def main():
    toolset = MCPToolset(StdioTransport(command='python', args=['-m', 'mcp_resource_server']))

    async with toolset:
        # List all available resources
        resources = await toolset.list_resources()
        for resource in resources:
            print(f' - {resource.name}: {resource.uri} ({resource.mime_type})')
            #>  - user_name_resource: resource://user_name.txt (text/plain)

        # Read a text resource
        user_name = await toolset.read_resource('resource://user_name.txt')
        print(f'Text content: {user_name}')
        #> Text content: Alice

if __name__ == '__main__':
    asyncio.run(main())
```

*(This example is complete, it can be run “as is”)*

## MCP Apps

An [MCP App](https://modelcontextprotocol.io/extensions/apps/overview) is an HTML page a server attaches to a tool through the tool’s `_meta.ui.resourceUri`. Pydantic AI doesn’t render it; it gives your frontend what it needs to.

When the agent calls such a tool, the [`ToolReturn`](https://pydantic.dev/docs/ai/api/pydantic-ai/messages/#pydantic_ai.messages.ToolReturn) carries an [`MCPAppToolResult`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPAppToolResult) in `metadata['mcp_app']`: the resource URI, the model’s arguments, the full MCP result with `structuredContent` and `_meta`, and the toolset `id`. The model doesn’t see it. The [AG-UI](https://pydantic.dev/docs/ai/integrations/ui/ag-ui/#mcp-apps) and [Vercel AI](https://pydantic.dev/docs/ai/integrations/ui/vercel-ai/#mcp-apps) adapters send it to the frontend. If a [`process_tool_call`](#tool-call-customization) hook changes the result or doesn’t call the tool, it isn’t attached. A [`WrapperToolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.WrapperToolset) around the toolset that edits results gets this `ToolReturn` for app tools, so it should edit `return_value`, and drop `metadata` if the page mustn’t see the original.

Your frontend needs three things from your backend:

- The page: [`read_resource_for_app(uri)`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.read_resource_for_app) returns the MCP result as is, the shape app hosts expect: each item in `contents` has the HTML, its `mimeType` and its `_meta`, where `_meta.ui` holds the CSP and permissions for the iframe.
- Tool calls the page makes: [`call_tool_for_app(name, arguments)`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.call_tool_for_app) returns the MCP result as is, including `isError` results. Only tools whose `_meta.ui.visibility` includes `"app"`, or omits `visibility`, can be called. `process_tool_call` doesn’t apply.
- Resource reads the page makes: the same [`read_resource_for_app(uri)`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.read_resource_for_app). Any resource on the server can be read.

Protocol errors raise [`MCPError`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPError); send its `code`, `message` and `data` back to the page as the JSON-RPC error. Other failures, such as an unreachable server, raise as they are.

mcp\_apps.py

```python
from typing import Any

from mcp.types import INVALID_PARAMS, METHOD_NOT_FOUND

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPError, MCPToolset

weather = MCPToolset('http://localhost:8000/mcp', id='weather')
agent = Agent('openai:gpt-6.1-sol', toolsets=[weather])

async def app_page(resource_uri: str) -> tuple[str, dict[str, Any]]:
    """Return the page's HTML and its `_meta.ui`."""
    [contents] = (await weather.read_resource_for_app(resource_uri))['contents']
    return contents['text'], contents.get('_meta', {}).get('ui', {})

async def app_request(method: str, params: dict[str, Any]) -> dict[str, Any]:
    """Answer a request the page made."""
    match method, params:
        case 'tools/call', {'name': str(name), **rest}:
            return await weather.call_tool_for_app(name, rest.get('arguments'))
        case 'resources/read', {'uri': str(uri)}:
            return await weather.read_resource_for_app(uri)
        case 'tools/call' | 'resources/read', _:
            raise MCPError(message=f'Invalid params for {method!r}', code=INVALID_PARAMS)
        case _:
            raise MCPError(message=f'Method {method!r} is not supported', code=METHOD_NOT_FOUND)
```

Use one `MCPToolset` per server, and keep it entered (`async with weather:`) while pages are open so requests don’t reconnect.

[`capabilities.extensions`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.ServerCapabilities.extensions) lists the extensions a server supports; MCP Apps servers list `'io.modelcontextprotocol/ui'`. Some servers only offer app tools to clients that advertise the matching client extension. `MCPToolset` doesn’t by default. On FastMCP 4, pass a client that does; FastMCP 3 clients can’t:

mcp\_apps\_extension.py

```python
from fastmcp import Client
from mcp.client import advertise

from pydantic_ai.mcp import MCPToolset

ui = advertise('io.modelcontextprotocol/ui', {'mimeTypes': ['text/html;profile=mcp-app']})
weather = MCPToolset(Client('http://localhost:8000/mcp', extensions=[ui]), id='weather')
```

## HTTP authentication

For HTTP transports, `MCPToolset` accepts an `auth` argument: a bearer token string, any [`httpx2.Auth`](https://httpx2.pydantic.dev/advanced/authentication/) (or legacy [`httpx.Auth`](https://www.python-httpx.org/advanced/authentication/) on FastMCP 3), the literal string `'oauth'` to enable [FastMCP’s OAuth flow](https://gofastmcp.com/clients/auth/oauth), or a function that returns the credentials for each agent run (see [per-user authentication](#per-user-authentication)). Static headers like API keys can be passed via the `headers` argument instead.

### Per-user authentication

In a multi-user or multi-tenant application, each user typically has their own credentials for the MCP server, such as a tenant-scoped bearer token, so they can’t be fixed when the toolset is created. Pass a function as `auth` instead: it’s called with the [run context](https://pydantic.dev/docs/ai/api/pydantic-ai/tools/#pydantic_ai.tools.RunContext) at the start of each agent run, so it can read the user’s credentials from the run’s [dependencies](https://pydantic.dev/docs/ai/core-concepts/dependencies/):

mcp\_per\_user\_auth.py

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset

@dataclass
class UserDeps:
    mcp_token: str

def mcp_token(ctx: RunContext[UserDeps]) -> str:
    return ctx.deps.mcp_token

toolset = MCPToolset('http://localhost:8000/mcp', auth=mcp_token)
agent = Agent('openai:gpt-6.1-sol', deps_type=UserDeps, toolsets=[toolset])

async def main():
    result = await agent.run('What is 7 plus 5?', deps=UserDeps(mcp_token='<token>'))
    print(result.output)
    #> The answer is 12.
```

*(To run this example, ensure `asyncio` is imported and add `asyncio.run(main())`; no other changes are needed.)*

Each run then connects to the server in an MCP session of its own, opened with the credentials the function returned, so concurrent runs on behalf of different users never share a session. The function can be sync or async, and can return anything a fixed `auth` accepts except `'oauth'`. `headers` accepts a function in the same way, for credentials the server expects in a different header.

Each session also gets an HTTP client of its own, unless you pass the toolset an [`http_client`](#custom-tls-ssl-configuration): every run’s session then sends its requests through that one client, so they share its cookie jar, and a cookie the server sets in response to one user’s run is sent with the requests of the runs after it, whichever user they’re for. Don’t share an `http_client` between runs on behalf of different users. To configure TLS, pass the toolset’s `verify` argument instead, which accepts an [`ssl.SSLContext`](https://docs.python.org/3/library/ssl.html#ssl.SSLContext) that can also hold a client certificate.

Because the toolset only knows which credentials to use once a run has started, it only connects to the server as part of an agent run: entering it with `async with toolset:` or `async with agent:` doesn’t open a connection, and calling one of its methods like `list_tools()` directly raises a [`UserError`](https://pydantic.dev/docs/ai/api/pydantic-ai/exceptions/#pydantic_ai.exceptions.UserError). Outside of an agent run, use the copy a run would use instead, which you get with [`await toolset.for_run(ctx)`](https://pydantic.dev/docs/ai/api/pydantic-ai/toolsets/#pydantic_ai.toolsets.AbstractToolset.for_run).

With the [`MCP` capability](https://pydantic.dev/docs/ai/capabilities/mcp/), pass the function as its `authorization_token` or `headers` instead; see [per-user credentials](https://pydantic.dev/docs/ai/capabilities/mcp/#per-user-credentials).

If each user needs more than their own credentials, such as a server URL of their own, build the whole toolset for each run with a [dynamic toolset](https://pydantic.dev/docs/ai/tools-toolsets/toolsets/#dynamically-building-a-toolset) instead: an [`@agent.toolset`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.toolset) function with `per_run_step=False` that returns an `MCPToolset` for the run’s user.

## Custom TLS / SSL configuration

In some environments you need to tweak how HTTPS connections are established — for example to trust an internal Certificate Authority, present a client certificate for **mTLS**, or (during local development only!) disable certificate verification altogether. `MCPToolset` exposes an `http_client` parameter so you can pass your own pre-configured [`httpx2.AsyncClient`](https://httpx2.pydantic.dev/async/):

mcp\_custom\_tls\_client.py

```python
import ssl

import httpx2

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

# Trust an internal / self-signed CA
ssl_ctx = ssl.create_default_context(cafile='/etc/ssl/private/my_company_ca.pem')

# Optional: load a client certificate for mutual TLS
ssl_ctx.load_cert_chain(certfile='/etc/ssl/certs/client.crt', keyfile='/etc/ssl/private/client.key')

http_client = httpx2.AsyncClient(verify=ssl_ctx, timeout=httpx2.Timeout(10.0))

toolset = MCPToolset('http://localhost:3001/sse', http_client=http_client)  # (1)
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

When you supply `http_client`, Pydantic AI reuses this client for every request. Anything supported by HTTPX (`verify`, `cert`, custom proxies, timeouts, etc.) therefore applies to all MCP traffic. The toolset never closes the client, so it can be reused across runs and you are responsible for closing it. Every run shares the client's cookie jar, so don't pass one to a toolset whose runs act for [different users](#per-user-authentication). On FastMCP 3, build the client with legacy `httpx` instead.

## Client identification

When connecting to an MCP server, you can optionally specify an [Implementation](https://modelcontextprotocol.io/specification/2025-11-25/schema#implementation) object as client information that will be sent to the server during initialization. This is useful for:

- Identifying your application in server logs
- Allowing servers to provide custom behavior based on the client
- Debugging and monitoring MCP connections
- Version-specific feature negotiation

mcp\_client\_with\_name.py

```python
from mcp import types as mcp_types

from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(
    'http://localhost:3001/sse',
    client_info=mcp_types.Implementation(
        name='MyApplication',
        version='2.1.0',
    ),
)
```

## MCP sampling

Sampling diagram

Here’s a mermaid diagram that may or may not make the data flow clearer:

```
sequenceDiagram
    participant LLM
    participant MCP_Client as MCP client
    participant MCP_Server as MCP server

    MCP_Client->>LLM: LLM call
    LLM->>MCP_Client: LLM tool call response

    MCP_Client->>MCP_Server: tool call
    MCP_Server->>MCP_Client: sampling "create message"

    MCP_Client->>LLM: LLM call
    LLM->>MCP_Client: LLM text response

    MCP_Client->>MCP_Server: sampling response
    MCP_Server->>MCP_Client: tool call response
```

Pydantic AI supports sampling as both a client and server. See the [server](https://pydantic.dev/docs/ai/mcp/server/#mcp-sampling) documentation for details on how to use sampling within a server.

To use sampling as a client, an `MCPToolset` needs to have a [`sampling_model`](https://pydantic.dev/docs/ai/api/pydantic-ai/mcp/#pydantic_ai.mcp.MCPToolset.sampling_model) set. This can be done either directly on the toolset using the `sampling_model=` constructor keyword argument, or by using [`agent.set_mcp_sampling_model()`](https://pydantic.dev/docs/ai/api/pydantic-ai/agent/#pydantic_ai.agent.Agent.set_mcp_sampling_model) to use the agent’s model (or one specified as an argument) as the sampling model on all `MCPToolset`s registered with the agent.

Let’s say we have an MCP server that wants to use sampling (in this case to generate an SVG as per the tool arguments):

Sampling MCP server

generate\_svg.py

```python
import re
from pathlib import Path

from mcp import SamplingMessage
from mcp.server.fastmcp import Context, FastMCP
from mcp.types import TextContent

app = FastMCP()

@app.tool()
async def image_generator(ctx: Context, subject: str, style: str) -> str:
    prompt = f'{subject=} {style=}'
    # `ctx.session.create_message` is the sampling call
    result = await ctx.session.create_message(
        [SamplingMessage(role='user', content=TextContent(type='text', text=prompt))],
        max_tokens=1_024,
        system_prompt='Generate an SVG image as per the user input',
    )
    assert isinstance(result.content, TextContent)

    path = Path(f'{subject}_{style}.svg')
    # remove triple backticks if the svg was returned within markdown
    if m := re.search(r'^```\w*$(.+?)```$', result.content.text, re.S | re.M):
        path.write_text(m.group(1), encoding='utf-8')
    else:
        path.write_text(result.content.text, encoding='utf-8')
    return f'See {path}'

if __name__ == '__main__':
    # run the server via stdio
    app.run()
```

Using this server with an `Agent` will automatically allow sampling:

sampling\_mcp\_client.py

```python
from fastmcp.client.transports import StdioTransport

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

toolset = MCPToolset(StdioTransport(command='python', args=['generate_svg.py']))
agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])

async def main():
    agent.set_mcp_sampling_model()
    result = await agent.run('Create an image of a robot in a punk style.')
    print(result.output)
    #> Image file written to robot_punk.svg.
```

*(This example is complete, it can be run “as is”)*

## Elicitation

In MCP, [elicitation](https://modelcontextprotocol.io/docs/concepts/elicitation) allows a server to request [structured input](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation#supported-schema-types) from the client for missing or additional context during a session.

Elicitation lets models essentially say “Hold on — I need to know X before I can continue”, rather than requiring everything upfront or taking a shot in the dark.

### How elicitation works

Elicitation introduces a protocol message type called [`ElicitRequest`](https://modelcontextprotocol.io/specification/2025-06-18/schema#elicitrequest), which is sent from the server to the client when it needs additional information. The client can then respond with an [`ElicitResult`](https://modelcontextprotocol.io/specification/2025-06-18/schema#elicitresult) or an `ErrorData` message.

A typical interaction looks like this:

- User makes a request to the MCP server (e.g. “Book a table at that Italian place”)
- The server identifies that it needs more information (e.g. “Which Italian place?”, “What date and time?”)
- The server sends an `ElicitRequest` to the client asking for the missing information.
- The client receives the request, presents it to the user (e.g. via a terminal prompt, GUI dialog, or web interface).
- User provides the requested information, declines, or cancels.
- The client sends an `ElicitResult` back to the server with the user’s response.
- With the structured data, the server can continue processing the original request.

This allows for a more interactive and user-friendly experience, especially for multi-stage workflows. Instead of requiring all information upfront, the server can ask for it as needed.

### Setting up elicitation

To enable elicitation, provide an `elicitation_handler` when creating your `MCPToolset`:

restaurant\_server.py

```python
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP(name='Restaurant Booking')

class BookingDetails(BaseModel):
    """Schema for restaurant booking information."""

    restaurant: str = Field(description='Choose a restaurant')
    party_size: int = Field(description='Number of people', ge=1, le=8)
    date: str = Field(description='Reservation date (DD-MM-YYYY)')

@mcp.tool()
async def book_table(ctx: Context) -> str:
    """Book a restaurant table with user input."""
    # Ask user for booking details using Pydantic schema
    result = await ctx.elicit(message='Please provide your booking details:', schema=BookingDetails)

    if result.action == 'accept' and result.data:
        booking = result.data
        return f'✅ Booked table for {booking.party_size} at {booking.restaurant} on {booking.date}'
    elif result.action == 'decline':
        return 'No problem! Maybe another time.'
    else:  # cancel
        return 'Booking cancelled.'

if __name__ == '__main__':
    mcp.run(transport='stdio')
```

This server demonstrates elicitation by requesting structured booking details from the client when the `book_table` tool is called. Here’s how to wire up the matching client:

client\_example.py

```python
import asyncio
from typing import Any

from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.transports import StdioTransport
from mcp.types import ElicitRequestFormParams, ElicitRequestParams

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

async def handle_elicitation(
    message: str,
    response_type: type | None,
    params: ElicitRequestParams,
    context: object,
) -> ElicitResult[dict[str, Any]]:
    """Handle elicitation requests from MCP server."""
    print(f'\n{message}')

    if not isinstance(params, ElicitRequestFormParams) or not params.requestedSchema:
        response = input('Response: ')
        return ElicitResult(action='accept', content={'response': response})

    # Collect data for each field
    properties = params.requestedSchema['properties']
    data: dict[str, Any] = {}

    for field, info in properties.items():
        description = info.get('description', field)

        value = input(f'{description}: ')

        # Convert to proper type based on JSON schema
        if info.get('type') == 'integer':
            data[field] = int(value)
        else:
            data[field] = value

    # Confirm
    confirm = input('\nConfirm booking? (y/n/c): ').lower()

    if confirm == 'y':
        print('Booking details:', data)
        return ElicitResult(action='accept', content=data)
    elif confirm == 'n':
        return ElicitResult(action='decline')
    else:
        return ElicitResult(action='cancel')

toolset = MCPToolset(
    StdioTransport(command='python', args=['restaurant_server.py']),
    elicitation_handler=handle_elicitation,
)

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])

async def main():
    """Run the agent to book a restaurant table."""
    result = await agent.run('Book me a table')
    print(f'\nResult: {result.output}')

if __name__ == '__main__':
    asyncio.run(main())
```

### Supported schema types

MCP elicitation supports string, number, boolean, and enum types with flat object structures only. These limitations ensure reliable cross-client compatibility. See [supported schema types](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation#supported-schema-types) for details.

### Security

MCP elicitation requires careful handling — servers must not request sensitive information, and clients must implement user approval controls with clear explanations. See [security considerations](https://modelcontextprotocol.io/specification/2025-06-18/client/elicitation#security-considerations) for details.
